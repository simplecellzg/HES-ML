import numpy as np
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from ase.io import read
from ase import Atoms
from ase.neighborlist import NeighborList
from scipy.spatial.distance import cdist
from tqdm import tqdm
import os
from concurrent.futures import ProcessPoolExecutor, as_completed
import multiprocessing as mp
from functools import partial

# 修改字体设置，与LAMMPS代码保持一致
try:
    # 首先尝试指定的Times New Roman字体文件
    font_path = '/public1/home/sch9516/ZG/MTD_3_database_trained_post_result/crystal_parameters_a_b_c/times-new-roman/times.ttf'
    if os.path.exists(font_path):
        prop = fm.FontProperties(fname=font_path)
        plt.rcParams['font.family'] = prop.get_name()
    else:
        # 如果找不到指定字体文件，使用系统默认的serif字体
        plt.rcParams['font.family'] = 'serif'
        plt.rcParams['font.serif'] = ['DejaVu Serif', 'Times', 'Times New Roman']
except:
    # 如果出错，使用默认字体
    plt.rcParams['font.family'] = 'serif'
    prop = None

# 全局字体放大设置（与LAMMPS代码一致）
plt.rcParams['font.size'] = 24  # 基础字体大小
plt.rcParams['axes.titlesize'] = 32  # 标题字体
plt.rcParams['axes.labelsize'] = 28  # 轴标签字体
plt.rcParams['xtick.labelsize'] = 20  # x轴刻度字体大小
plt.rcParams['ytick.labelsize'] = 20  # y轴刻度字体大小
plt.rcParams['legend.fontsize'] = 20  # 图例字体大小

# 创建输出文件夹
output_dir = 'cp2k_analysis_results'
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

def read_cp2k_trajectory(xyz_file, cell_file):
    """Read CP2K xyz and cell files"""
    # 读取所有的xyz帧
    try:
        frames = read(xyz_file, index=':')
        if not isinstance(frames, list):
            frames = [frames]
    except:
        print(f"Error: Cannot read XYZ file {xyz_file}")
        return []
    
    # 读取cell文件
    cells = []
    with open(cell_file, 'r') as f:
        lines = f.readlines()
    
    for line in lines[1:]:  # 跳过header
        if line.strip():
            parts = line.split()
            if len(parts) >= 11:
                # 提取晶胞参数 Ax, By, Cz（对角元素）
                ax = float(parts[2])
                by = float(parts[6])
                cz = float(parts[10])
                cells.append([ax, by, cz])
    
    # 将cell信息添加到frames
    for i, frame in enumerate(frames):
        if i < len(cells):
            frame.cell = [[cells[i][0], 0, 0],
                         [0, cells[i][1], 0],
                         [0, 0, cells[i][2]]]
            frame.pbc = True
    
    return frames

def get_safe_rmax(frames):
    """Calculate safe r_max value based on cell size"""
    min_cell_length = float('inf')
    
    for frame in frames:
        cell_lengths = frame.cell.cellpar()[:3]  # a, b, c
        min_cell_length = min(min_cell_length, min(cell_lengths))
    
    # r_max应该小于最小晶胞长度的一半，留一些余量
    safe_rmax = min_cell_length * 0.45
    return safe_rmax

def calculate_distances_vectorized(positions1, positions2, cell, pbc=True):
    """Vectorized calculation of distances between all atom pairs"""
    if pbc:
        # 使用最小镜像约定
        cell_inv = np.linalg.inv(cell)
        
        # 计算所有对之间的向量
        n1 = len(positions1)
        n2 = len(positions2)
        
        # 扩展positions以计算所有对
        pos1_exp = positions1[:, np.newaxis, :]  # (n1, 1, 3)
        pos2_exp = positions2[np.newaxis, :, :]  # (1, n2, 3)
        
        # 计算差向量
        delta = pos1_exp - pos2_exp  # (n1, n2, 3)
        
        # 转换到分数坐标
        delta_frac = np.dot(delta, cell_inv)
        
        # 应用最小镜像约定
        delta_frac = delta_frac - np.round(delta_frac)
        
        # 转换回笛卡尔坐标
        delta_cart = np.dot(delta_frac, cell)
        
        # 计算距离
        distances = np.linalg.norm(delta_cart, axis=2)
    else:
        distances = cdist(positions1, positions2)
    
    return distances

def process_frame_rdf(frame_data, el1, el2, r_max, n_bins):
    """Process single frame RDF calculation (for parallel processing)"""
    frame = frame_data
    
    # 获取原子索引和位置
    symbols = frame.get_chemical_symbols()
    indices1 = np.array([i for i, sym in enumerate(symbols) if sym == el1])
    indices2 = np.array([i for i, sym in enumerate(symbols) if sym == el2])
    
    if len(indices1) == 0 or len(indices2) == 0:
        return None
    
    positions = frame.get_positions()
    pos1 = positions[indices1]
    pos2 = positions[indices2]
    cell = frame.get_cell()
    
    # 向量化计算所有距离
    distances = calculate_distances_vectorized(pos1, pos2, cell, pbc=True)
    
    # 如果是同种元素，去除对角线（自身距离）
    if el1 == el2:
        np.fill_diagonal(distances, np.inf)
    
    # 计算直方图
    dr = r_max / n_bins
    hist, _ = np.histogram(distances.flatten(), bins=n_bins, range=(0, r_max))
    
    # 归一化
    volume = frame.get_volume()
    if el1 == el2:
        rho = len(indices1) * (len(indices1) - 1) / volume
    else:
        rho = len(indices1) * len(indices2) / volume
    
    # 归一化到g(r)
    r_centers = np.linspace(dr/2, r_max - dr/2, n_bins)
    shell_volumes = 4 * np.pi * r_centers**2 * dr
    
    if rho > 0:
        g_r = hist / (rho * shell_volumes)
    else:
        g_r = np.zeros(n_bins)
    
    return g_r

def calculate_rdf_parallel(frames, r_max=None, n_bins=200, n_workers=None):
    """Parallel RDF calculation"""
    # 如果没有指定r_max，自动计算
    if r_max is None:
        r_max = get_safe_rmax(frames)
        print(f"Auto-set r_max = {r_max:.2f} Angstrom")
    
    # 获取元素类型
    elements = list(set(frames[0].get_chemical_symbols()))
    print(f"Elements in system: {elements}")
    
    # 设置并行工作器数量
    if n_workers is None:
        n_workers = min(mp.cpu_count() - 1, 8)
    
    print(f"Using {n_workers} parallel workers")
    
    # 初始化RDF字典
    rdf_data = {}
    dr = r_max / n_bins
    r_values = np.linspace(dr/2, r_max - dr/2, n_bins)
    
    # 按照指定顺序计算RDF（O-O, Si-O, Si-Si），与LAMMPS代码保持一致
    pairs_order = [('O', 'O'), ('Si', 'O'), ('Si', 'Si')]
    
    # 对每个原子对计算RDF
    for el1, el2 in pairs_order:
        if el1 in elements and el2 in elements:
            print(f"\nCalculating {el1}-{el2} RDF...")
            
            # 准备并行计算
            process_func = partial(process_frame_rdf, 
                                 el1=el1, el2=el2, 
                                 r_max=r_max, n_bins=n_bins)
            
            g_r_sum = np.zeros(n_bins)
            count = 0
            
            # 使用进程池并行计算
            with ProcessPoolExecutor(max_workers=n_workers) as executor:
                # 提交所有任务
                futures = {executor.submit(process_func, frame): i 
                          for i, frame in enumerate(frames)}
                
                # 收集结果
                for future in tqdm(as_completed(futures), 
                                 total=len(futures), 
                                 desc=f"Processing {el1}-{el2}"):
                    result = future.result()
                    if result is not None:
                        g_r_sum += result
                        count += 1
            
            # 平均化
            if count > 0:
                g_r_avg = g_r_sum / count
            else:
                g_r_avg = np.zeros(n_bins)
            
            rdf_data[(el1, el2)] = {
                'r': r_values,
                'g_r': g_r_avg
            }
            
            print(f"  Successfully calculated {count} frames")
    
    return rdf_data, r_max

def calculate_bonds_and_angles(frames, cutoffs={'Si-O': 1.85, 'Si-Si': 3.3, 'O-O': 2.8}):
    """Calculate bond length and angle distributions"""
    print("\nCalculating bond length and angle distributions...")
    
    bond_data = {pair: [] for pair in cutoffs.keys()}
    angle_data = {
        'O-Si-O': [],  # Si中心的键角
        'Si-O-Si': []  # O桥接的键角
    }
    
    for frame_idx, frame in enumerate(tqdm(frames, desc="Analyzing bonds and angles")):
        # 使用ASE的邻居列表加速
        symbols = frame.get_chemical_symbols()
        
        # 创建邻居列表
        max_cutoff = max(cutoffs.values())
        nl = NeighborList([max_cutoff/2]*len(frame), self_interaction=False, bothways=True)
        nl.update(frame)
        
        # 收集键长
        for i in range(len(frame)):
            indices, offsets = nl.get_neighbors(i)
            for j, offset in zip(indices, offsets):
                if i < j:  # 避免重复计数
                    el1 = symbols[i]
                    el2 = symbols[j]
                    key = f"{el1}-{el2}" if f"{el1}-{el2}" in cutoffs else f"{el2}-{el1}"
                    
                    if key in cutoffs:
                        dist = frame.get_distance(i, j, mic=True)
                        if dist < cutoffs[key]:
                            bond_data[key].append(dist)
        
        # 计算键角
        # O-Si-O angles
        Si_indices = [i for i, sym in enumerate(symbols) if sym == 'Si']
        for Si_idx in Si_indices:
            O_neighbors = []
            indices, offsets = nl.get_neighbors(Si_idx)
            
            for j in indices:
                if symbols[j] == 'O':
                    dist = frame.get_distance(Si_idx, j, mic=True)
                    if dist < cutoffs['Si-O']:
                        O_neighbors.append(j)
            
            # 计算所有O-Si-O角度
            for i in range(len(O_neighbors)):
                for j in range(i+1, len(O_neighbors)):
                    angle = frame.get_angle(O_neighbors[i], Si_idx, O_neighbors[j], mic=True)
                    angle_data['O-Si-O'].append(angle)
        
        # Si-O-Si angles
        O_indices = [i for i, sym in enumerate(symbols) if sym == 'O']
        for O_idx in O_indices:
            Si_neighbors = []
            indices, offsets = nl.get_neighbors(O_idx)
            
            for j in indices:
                if symbols[j] == 'Si':
                    dist = frame.get_distance(O_idx, j, mic=True)
                    if dist < cutoffs['Si-O']:
                        Si_neighbors.append(j)
            
            # 计算所有Si-O-Si角度
            for i in range(len(Si_neighbors)):
                for j in range(i+1, len(Si_neighbors)):
                    angle = frame.get_angle(Si_neighbors[i], O_idx, Si_neighbors[j], mic=True)
                    angle_data['Si-O-Si'].append(angle)
    
    # 保存原始数据
    save_raw_bond_angle_data(bond_data, angle_data)
    
    return bond_data, angle_data

def save_raw_bond_angle_data(bond_data, angle_data):
    """Save raw bond length and angle data to files"""
    # 保存键长数据
    for pair, distances in bond_data.items():
        if distances:
            filename = os.path.join(output_dir, f'bond_lengths_{pair}.dat')
            np.savetxt(filename, distances, fmt='%.6f', 
                      header=f'{pair} bond lengths (Angstrom)\nTotal count: {len(distances)}')
            print(f"Saved {len(distances)} {pair} bond lengths to {filename}")
    
    # 保存键角数据
    for angle_type, angles in angle_data.items():
        if angles:
            filename = os.path.join(output_dir, f'bond_angles_{angle_type}.dat')
            np.savetxt(filename, angles, fmt='%.6f', 
                      header=f'{angle_type} bond angles (degrees)\nTotal count: {len(angles)}')
            print(f"Saved {len(angles)} {angle_type} bond angles to {filename}")

def plot_bond_angle_distributions(bond_data, angle_data):
    """Plot bond length and angle distributions in a single figure with 5 subplots"""
    # 创建 2x3 的子图布局，用于5个图
    fig, axes = plt.subplots(2, 3, figsize=(24, 16))  # 增大图片尺寸
    axes = axes.flatten()  # 将2D数组展平为1D
    
    plot_idx = 0
    
    # 绘制键长分布（3个图）
    bond_pairs = ['Si-O', 'Si-Si', 'O-O']  # 指定顺序
    for pair in bond_pairs:
        if pair in bond_data and bond_data[pair]:
            distances = bond_data[pair]
            ax = axes[plot_idx]
            
            # 绘制直方图
            n, bins, patches = ax.hist(distances, bins=50, alpha=0.7, density=True, 
                                      color='steelblue', edgecolor='black', linewidth=0.5)
            
            # 计算统计信息
            mean_val = np.mean(distances)
            std_val = np.std(distances)
            
            # 添加均值线
            ax.axvline(mean_val, color='red', linestyle='--', linewidth=3, label=f'Mean = {mean_val:.3f}')
            
            # 设置标签和标题
            if prop:
                ax.set_xlabel(f'Bond Length (Å)', fontproperties=prop, fontsize=28)
                ax.set_ylabel('Probability Density', fontproperties=prop, fontsize=28)
                ax.set_title(f'{pair} Bond Length Distribution\n'
                            f'Mean: {mean_val:.3f} Å, Std: {std_val:.3f} Å, N: {len(distances)}', 
                            fontproperties=prop, fontsize=32)
            else:
                ax.set_xlabel(f'Bond Length (Å)', fontsize=28)
                ax.set_ylabel('Probability Density', fontsize=28)
                ax.set_title(f'{pair} Bond Length Distribution\n'
                            f'Mean: {mean_val:.3f} Å, Std: {std_val:.3f} Å, N: {len(distances)}', 
                            fontsize=32)
            ax.legend()
            ax.grid(False)
            
            plot_idx += 1
    
    # 绘制键角分布（2个图）
    angle_types = ['O-Si-O', 'Si-O-Si']  # 指定顺序
    for angle_type in angle_types:
        if angle_type in angle_data and angle_data[angle_type]:
            angles = angle_data[angle_type]
            ax = axes[plot_idx]
            
            # 绘制直方图
            n, bins, patches = ax.hist(angles, bins=50, alpha=0.7, density=True, 
                                      range=(60, 180), color='coral', edgecolor='black', linewidth=0.5)
            
            # 计算统计信息
            mean_val = np.mean(angles)
            std_val = np.std(angles)
            
            # 添加均值线
            ax.axvline(mean_val, color='darkgreen', linestyle='--', linewidth=3, label=f'Mean = {mean_val:.1f}°')
            
            # 设置标签和标题
            if prop:
                ax.set_xlabel(f'Bond Angle (degrees)', fontproperties=prop, fontsize=28)
                ax.set_ylabel('Probability Density', fontproperties=prop, fontsize=28)
                ax.set_title(f'{angle_type} Bond Angle Distribution\n'
                            f'Mean: {mean_val:.1f}°, Std: {std_val:.1f}°, N: {len(angles)}', 
                            fontproperties=prop, fontsize=32)
            else:
                ax.set_xlabel(f'Bond Angle (degrees)', fontsize=28)
                ax.set_ylabel('Probability Density', fontsize=28)
                ax.set_title(f'{angle_type} Bond Angle Distribution\n'
                            f'Mean: {mean_val:.1f}°, Std: {std_val:.1f}°, N: {len(angles)}', 
                            fontsize=32)
            ax.legend()
            ax.grid(False)
            
            plot_idx += 1
    
    # 隐藏多余的子图（第6个）
    if plot_idx < len(axes):
        axes[-1].set_visible(False)
    
    # 调整布局
    plt.tight_layout()
    
    # 保存图片
    plt.savefig(os.path.join(output_dir, 'bond_angle_distributions_combined.png'), 
                dpi=300, bbox_inches='tight')
    plt.close()
    
    # 同时保存单独的图片（如果需要）
    save_individual_plots(bond_data, angle_data)
    
    # 保存统计数据
    with open(os.path.join(output_dir, 'bond_angle_statistics.txt'), 'w') as f:
        f.write("Bond Length Statistics:\n")
        for pair in bond_pairs:
            if pair in bond_data and bond_data[pair]:
                distances = bond_data[pair]
                f.write(f"{pair}: Mean = {np.mean(distances):.3f} Angstrom, "
                       f"Std = {np.std(distances):.3f} Angstrom, "
                       f"Count = {len(distances)}\n")
        
        f.write("\nBond Angle Statistics:\n")
        for angle_type in angle_types:
            if angle_type in angle_data and angle_data[angle_type]:
                angles = angle_data[angle_type]
                f.write(f"{angle_type}: Mean = {np.mean(angles):.1f} degrees, "
                       f"Std = {np.std(angles):.1f} degrees, "
                       f"Count = {len(angles)}\n")

def save_individual_plots(bond_data, angle_data):
    """Save individual plots for each bond length and angle distribution"""
    # 保存单独的键长分布图
    for pair, distances in bond_data.items():
        if distances:
            plt.figure(figsize=(10, 8))  # 增大单独图片尺寸
            plt.hist(distances, bins=50, alpha=0.7, density=True, 
                    color='steelblue', edgecolor='black', linewidth=0.5)
            
            mean_val = np.mean(distances)
            plt.axvline(mean_val, color='red', linestyle='--', linewidth=3, 
                       label=f'Mean = {mean_val:.3f} Å')
            
            if prop:
                plt.xlabel(f'Bond Length (Å)', fontproperties=prop, fontsize=28)
                plt.ylabel('Probability Density', fontproperties=prop, fontsize=28)
                plt.title(f'{pair} Bond Length Distribution', fontproperties=prop, fontsize=32)
            else:
                plt.xlabel(f'Bond Length (Å)', fontsize=28)
                plt.ylabel('Probability Density', fontsize=28)
                plt.title(f'{pair} Bond Length Distribution', fontsize=32)
            plt.legend()
            plt.grid(False)
            
            plt.savefig(os.path.join(output_dir, f'bond_length_{pair}.png'), 
                       dpi=300, bbox_inches='tight')
            plt.close()
    
    # 保存单独的键角分布图
    for angle_type, angles in angle_data.items():
        if angles:
            plt.figure(figsize=(10, 8))  # 增大单独图片尺寸
            plt.hist(angles, bins=50, alpha=0.7, density=True, range=(60, 180),
                    color='coral', edgecolor='black', linewidth=0.5)
            
            mean_val = np.mean(angles)
            plt.axvline(mean_val, color='darkgreen', linestyle='--', linewidth=3, 
                       label=f'Mean = {mean_val:.1f}°')
            
            if prop:
                plt.xlabel(f'Bond Angle (degrees)', fontproperties=prop, fontsize=28)
                plt.ylabel('Probability Density', fontproperties=prop, fontsize=28)
                plt.title(f'{angle_type} Bond Angle Distribution', fontproperties=prop, fontsize=32)
            else:
                plt.xlabel(f'Bond Angle (degrees)', fontsize=28)
                plt.ylabel('Probability Density', fontsize=28)
                plt.title(f'{angle_type} Bond Angle Distribution', fontsize=32)
            plt.legend()
            plt.grid(False)
            
            plt.savefig(os.path.join(output_dir, f'bond_angle_{angle_type}.png'), 
                       dpi=300, bbox_inches='tight')
            plt.close()

def plot_and_save_rdf(rdf_data, r_max, output_prefix='rdf'):
    """Plot and save RDF with peak annotations (LAMMPS style)"""
    # 绘制所有RDF在一张图上，并标注每个RDF的第一个峰
    plt.figure(figsize=(14, 10))  # 增大图片尺寸
    
    # 定义颜色
    colors = {'O-O': 'blue', 'Si-O': 'red', 'Si-Si': 'green'}
    
    # 用于存储峰信息
    peak_info = {}
    
    # 先绘制所有曲线
    for pair, data in rdf_data.items():
        if data['r'] is not None and data['g_r'] is not None:
            label = f"{pair[0]}-{pair[1]}"
            color = colors.get(label, 'black')
            plt.plot(data['r'], data['g_r'], label=label, linewidth=3, color=color)
            
            # 找到第一个峰
            peak_idx = np.argmax(data['g_r'][10:]) + 10  # 跳过前面的点
            if peak_idx < len(data['r']):
                peak_r = data['r'][peak_idx]
                peak_g = data['g_r'][peak_idx]
                peak_info[label] = (peak_r, peak_g)
                
                # 在图上标注峰位置
                plt.plot(peak_r, peak_g, 'o', color=color, markersize=10)
                plt.axvline(x=peak_r, color=color, linestyle='--', alpha=0.3, linewidth=2)
    
    # 调整标注位置，避免重叠（与LAMMPS代码一致）
    # O-O标注放左边
    if 'O-O' in peak_info:
        peak_r, peak_g = peak_info['O-O']
        plt.text(peak_r - 0.1, peak_g + 0.1,  # 放到左边
                f'O-O\nr={peak_r:.2f} Å\ng(r)={peak_g:.2f}', 
                fontsize=18, color=colors['O-O'], 
                bbox=dict(boxstyle='round', facecolor='white', alpha=0.8),
                ha='right')  # 右对齐文本
    
    # Si-O标注向下调整
    if 'Si-O' in peak_info:
        peak_r, peak_g = peak_info['Si-O']
        # 获取y轴范围
        y_min, y_max = plt.ylim()
        # 将标注放在图内，向下调整
        text_y = min(peak_g - 0.2, y_max * 0.85)  # 确保在图框内
        plt.text(peak_r - 0.15, text_y,  # 向下调整
                f'Si-O\nr={peak_r:.2f} Å\ng(r)={peak_g:.2f}', 
                fontsize=18, color=colors['Si-O'], 
                bbox=dict(boxstyle='round', facecolor='white', alpha=0.8),ha='right')
    
    # Si-Si标注保持原位
    if 'Si-Si' in peak_info:
        peak_r, peak_g = peak_info['Si-Si']
        plt.text(peak_r + 0.1, peak_g + 0.1, 
                f'Si-Si\nr={peak_r:.2f} Å\ng(r)={peak_g:.2f}', 
                fontsize=18, color=colors['Si-Si'], 
                bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
    
    # 确保标题和轴标签字体大小正确
    if prop:
        plt.xlabel('r (Å)', fontproperties=prop, fontsize=28)
        plt.ylabel('g(r)', fontproperties=prop, fontsize=28)
        plt.title('Radial Distribution Functions', fontproperties=prop, fontsize=32)
    else:
        plt.xlabel('r (Å)', fontsize=28)
        plt.ylabel('g(r)', fontsize=28)
        plt.title('Radial Distribution Functions', fontsize=32)
    
    plt.legend(loc='upper right')
    plt.grid(False)
    plt.xlim(0, r_max)
    plt.ylim(0, None)
    
    # 保存图片
    plt.savefig(os.path.join(output_dir, f'{output_prefix}_all.png'), dpi=300, bbox_inches='tight')
    plt.close()
    
    # 为每个原子对单独绘图
    for pair, data in rdf_data.items():
        if data['r'] is not None and data['g_r'] is not None:
            plt.figure(figsize=(10, 8))  # 增大单独图片尺寸
            label = f"{pair[0]}-{pair[1]}"
            color = colors.get(label, 'black')
            plt.plot(data['r'], data['g_r'], linewidth=3, color=color)
            
            # 确保单独图的标题和轴标签字体大小正确
            if prop:
                plt.xlabel('r (Å)', fontproperties=prop, fontsize=28)
                plt.ylabel('g(r)', fontproperties=prop, fontsize=28)
                plt.title(f'RDF: {pair[0]}-{pair[1]}', fontproperties=prop, fontsize=32)
            else:
                plt.xlabel('r (Å)', fontsize=28)
                plt.ylabel('g(r)', fontsize=28)
                plt.title(f'RDF: {pair[0]}-{pair[1]}', fontsize=32)
            
            plt.grid(False)
            plt.xlim(0, r_max)
            plt.ylim(0, None)
            
            # 标注第一个峰的位置和值
            peak_idx = np.argmax(data['g_r'][10:]) + 10  # 跳过前面的点
            if peak_idx < len(data['r']):
                peak_r = data['r'][peak_idx]
                peak_g = data['g_r'][peak_idx]
                plt.axvline(x=peak_r, color='red', linestyle='--', alpha=0.5, linewidth=2)
                plt.plot(peak_r, peak_g, 'ro', markersize=10)
                
                # 调整单独图中的标注位置，避免与曲线重叠
                # 检查峰后的曲线趋势，选择合适的标注位置
                if peak_idx + 20 < len(data['g_r']):
                    # 如果峰后曲线下降，将标注放在右上方
                    if data['g_r'][peak_idx + 10] < peak_g * 0.8:
                        text_x = peak_r + 0.2
                        text_y = peak_g * 0.9
                    else:
                        # 否则放在右下方
                        text_x = peak_r + 0.1
                        text_y = peak_g * 0.7
                else:
                    text_x = peak_r + 0.1
                    text_y = peak_g * 0.9
                
                plt.text(text_x, text_y, 
                        f'r={peak_r:.2f} Å\ng(r)={peak_g:.2f}', 
                        fontsize=22, color='red', 
                        bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
            
            # 保存单独的图片
            plt.savefig(os.path.join(output_dir, f'{output_prefix}_{pair[0]}_{pair[1]}.png'), dpi=300, bbox_inches='tight')
            plt.close()
            
            # 保存数据到文本文件
            np.savetxt(os.path.join(output_dir, f'{output_prefix}_{pair[0]}_{pair[1]}.dat'), 
                      np.column_stack((data['r'], data['g_r'])),
                      header='r(Angstrom) g(r)',
                      fmt='%.6f')

def main():
    # 文件路径
    xyz_file = 'SiO2_crystallisation_melt_3DSF_pbe-pos-1.xyz'
    cell_file = 'SiO2_crystallisation_melt_3DSF_pbe-1.cell'
    
    print("Reading CP2K trajectory files...")
    frames = read_cp2k_trajectory(xyz_file, cell_file)
    
    if not frames:
        print("Error: Cannot read trajectory file")
        return
    
    print(f"Total frames: {len(frames)}")
    
    # 打印晶胞信息
    cell_params = frames[-1].cell.cellpar()
    print(f"Last frame cell parameters: a={cell_params[0]:.3f}, b={cell_params[1]:.3f}, c={cell_params[2]:.3f} Angstrom")
    
    # 选择最后的1000帧
    n_frames_to_use = min(1000, len(frames))  # 使用最后1000帧
    if n_frames_to_use < 1000:
        print(f"Warning: Only {len(frames)} frames available, less than requested 1000 frames")
    
    frames_to_analyze = frames[-n_frames_to_use:]
    print(f"Using last {n_frames_to_use} frames for analysis")
    
    # 计算RDF
    print("\nStarting RDF calculation...")
    import time
    start_time = time.time()
    
    # 使用并行计算，根据CPU核心数设置工作器数量
    n_workers = min(mp.cpu_count() - 1, 8)
    rdf_data, r_max = calculate_rdf_parallel(frames_to_analyze, n_workers=n_workers)
    
    rdf_time = time.time() - start_time
    print(f"RDF calculation completed in {rdf_time:.1f} seconds")
    
    # 绘图并保存RDF
    print("\nSaving RDF results...")
    plot_and_save_rdf(rdf_data, r_max)
    
    # 打印第一个峰的位置
    print("\nFirst peak positions:")
    peak_info = {}
    for pair, data in rdf_data.items():
        if data['r'] is not None and data['g_r'] is not None:
            # 找到第一个峰
            peak_idx = np.argmax(data['g_r'][10:]) + 10  # 跳过前面的点
            if peak_idx < len(data['r']):
                peak_r = data['r'][peak_idx]
                peak_g = data['g_r'][peak_idx]
                print(f"{pair[0]}-{pair[1]}: {peak_r:.2f} Angstrom (g(r)={peak_g:.2f})")
                
                # 根据峰位置确定截断距离
                # 找峰后的第一个谷
                if peak_idx + 20 < len(data['g_r']):
                    valley_idx = peak_idx + np.argmin(data['g_r'][peak_idx:peak_idx+50])
                    cutoff = data['r'][valley_idx]
                else:
                    cutoff = peak_r * 1.2  # 默认使用峰位置的1.2倍
                
                peak_info[f"{pair[0]}-{pair[1]}"] = cutoff
    
    # 设置键的截断距离
    cutoffs = {
        'Si-O': peak_info.get('Si-O', 1.85),
        'Si-Si': peak_info.get('Si-Si', 3.3),
        'O-O': peak_info.get('O-O', 2.8)
    }
    
    print(f"\nUsing bond cutoff distances:")
    for bond, cutoff in cutoffs.items():
        print(f"{bond}: {cutoff:.2f} Angstrom")
    
    # 计算键长和键角
    start_time = time.time()
    bond_data, angle_data = calculate_bonds_and_angles(frames_to_analyze, cutoffs)
    bond_angle_time = time.time() - start_time
    print(f"Bond length and angle analysis completed in {bond_angle_time:.1f} seconds")
    
    # 绘制分布图
    plot_bond_angle_distributions(bond_data, angle_data)
    
    # 计算配位数
    print("\nCoordination number analysis:")
    
    # 获取原子数量信息
    symbols = frames[0].get_chemical_symbols()
    n_Si = symbols.count('Si')
    n_O = symbols.count('O')
    total_atoms = len(symbols)
    
    print(f"System composition: {n_Si} Si atoms, {n_O} O atoms, total {total_atoms} atoms")
    print(f"Chemical formula ratio Si:O = 1:{n_O/n_Si:.2f}")
    
    # 计算平均配位数
    if bond_data.get('Si-O'):
        si_o_bonds = len(bond_data['Si-O']) / n_frames_to_use
        avg_si_coordination = si_o_bonds * 2 / n_Si  # 每个Si-O键涉及1个Si原子
        avg_o_coordination = si_o_bonds * 2 / n_O   # 每个Si-O键涉及1个O原子
        print(f"\nAverage Si coordination number (O neighbors): {avg_si_coordination:.2f}")
        print(f"Average O coordination number (Si neighbors): {avg_o_coordination:.2f}")
    
    # 保存综合分析报告
    with open(os.path.join(output_dir, 'comprehensive_analysis_report.txt'), 'w') as f:
        f.write("SiO2 System Structure Analysis Report (CP2K)\n")
        f.write("="*50 + "\n\n")
        
        f.write(f"Analysis Parameters:\n")
        f.write(f"- Total frames: {len(frames)}\n")
        f.write(f"- Analyzed frames: {n_frames_to_use}\n")
        f.write(f"- RDF r_max: {r_max:.2f} Angstrom\n")
        f.write(f"- Cell parameters: a={cell_params[0]:.3f}, b={cell_params[1]:.3f}, c={cell_params[2]:.3f} Angstrom\n")
        f.write(f"- Computation time: RDF {rdf_time:.1f}s, bonds and angles {bond_angle_time:.1f}s\n")
        
        f.write(f"\nSystem Composition:\n")
        f.write(f"- Si atoms: {n_Si}\n")
        f.write(f"- O atoms: {n_O}\n")
        f.write(f"- Total atoms: {total_atoms}\n")
        f.write(f"- Chemical formula ratio Si:O = 1:{n_O/n_Si:.2f}\n")
        
        f.write(f"\nRDF First Peak Positions:\n")
        for pair, data in rdf_data.items():
            if data['r'] is not None and data['g_r'] is not None:
                peak_idx = np.argmax(data['g_r'][10:]) + 10
                if peak_idx < len(data['r']):
                    f.write(f"- {pair[0]}-{pair[1]}: {data['r'][peak_idx]:.2f} Angstrom\n")
        
        f.write(f"\nBond Length Statistics:\n")
        for pair, distances in bond_data.items():
            if distances:
                f.write(f"- {pair}:\n")
                f.write(f"  * Mean: {np.mean(distances):.3f} ± {np.std(distances):.3f} Angstrom\n")
                f.write(f"  * Range: {np.min(distances):.3f} - {np.max(distances):.3f} Angstrom\n")
                f.write(f"  * Bonds/frame: {len(distances)/n_frames_to_use:.1f}\n")
        
        f.write(f"\nBond Angle Statistics:\n")
        for angle_type, angles in angle_data.items():
            if angles:
                f.write(f"- {angle_type}:\n")
                f.write(f"  * Mean: {np.mean(angles):.1f} ± {np.std(angles):.1f} degrees\n")
                f.write(f"  * Range: {np.min(angles):.1f} - {np.max(angles):.1f} degrees\n")
                f.write(f"  * Angles/frame: {len(angles)/n_frames_to_use:.1f}\n")
        
        if bond_data.get('Si-O'):
            si_o_bonds = len(bond_data['Si-O']) / n_frames_to_use
            avg_si_coordination = si_o_bonds * 2 / n_Si
            avg_o_coordination = si_o_bonds * 2 / n_O
            f.write(f"\nCoordination Numbers:\n")
            f.write(f"- Average Si coordination number (O neighbors): {avg_si_coordination:.2f}\n")
            f.write(f"- Average O coordination number (Si neighbors): {avg_o_coordination:.2f}\n")
    
    print("\nAnalysis complete!")
    print("Generated files in cp2k_analysis_results folder:")
    print("- RDF plots: rdf_all.png (with peak annotations), rdf_O_O.png, rdf_Si_O.png, rdf_Si_Si.png")
    print("- RDF data: rdf_O_O.dat, rdf_Si_O.dat, rdf_Si_Si.dat")
    print("- Combined bond/angle plot: bond_angle_distributions_combined.png")
    print("- Individual plots: bond_length_*.png, bond_angle_*.png")
    print("- Raw data files: bond_lengths_*.dat, bond_angles_*.dat")
    print("- Statistical reports: bond_angle_statistics.txt, comprehensive_analysis_report.txt")

if __name__ == "__main__":
    # 设置多进程启动方法（Windows系统需要）
    mp.set_start_method('spawn', force=True)
    main()
