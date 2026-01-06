import os
import re
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
import shutil
from matplotlib import rcParams
from matplotlib import font_manager

def set_custom_font():
    """设置Times New Roman字体，优先使用提供的字体文件"""
    font_path = "/public1/home/sch9516/ZG/MTD_3_database_trained_post_result/reaction_energy_diff/reaction_all/times-new-roman/times.ttf"
    
    try:
        # 添加字体文件到字体管理器
        if os.path.exists(font_path):
            font_manager.fontManager.addfont(font_path)
            plt.rcParams['font.family'] = 'Times New Roman'
            # 设置数学字体也使用Times New Roman
            plt.rcParams['mathtext.fontset'] = 'custom'
            plt.rcParams['mathtext.rm'] = 'Times New Roman'
            plt.rcParams['mathtext.it'] = 'Times New Roman:italic'
            plt.rcParams['mathtext.bf'] = 'Times New Roman:bold'
            print("成功加载Times New Roman字体")
        else:
            print(f"字体文件 {font_path} 不存在，使用备用字体")
            plt.rcParams['font.family'] = 'serif'
            plt.rcParams['font.serif'] = ['Times New Roman', 'DejaVu Serif']
            plt.rcParams['mathtext.fontset'] = 'serif'
    except Exception as e:
        print(f"字体设置错误: {e}, 使用默认字体")
        plt.rcParams['font.family'] = 'serif'
        plt.rcParams['font.serif'] = ['Times New Roman', 'DejaVu Serif']
        plt.rcParams['mathtext.fontset'] = 'serif'

# 设置字体
set_custom_font()

# 设置默认字体大小 - 增大字体
rcParams['font.size'] = 30
rcParams['axes.labelsize'] = 35
rcParams['axes.titlesize'] = 40
rcParams['xtick.labelsize'] = 30
rcParams['ytick.labelsize'] = 30
rcParams['legend.fontsize'] = 25

def setup_directories():
    """创建输出目录"""
    output_dir = './RDF_combine'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    return output_dir

def get_method_mapping():
    """获取方法名称映射"""
    return {
        'dft_PBE': 'PBE',
        'dp_20241109_clean_2': 'DeePMD',
        'lmp_2015': 'ReaxFF',
        'lmp_bks': 'BKS'
    }

def get_color_mapping():
    """获取方法颜色映射"""
    return {
        'PBE': 'red',
        'DeePMD': 'blue',
        'ReaxFF': 'green',
        'BKS': 'orange'
    }

def get_linestyle_mapping():
    """获取RDF类型线型映射"""
    return {
        'O_O': '-',      # 实线
        'Si_O': '--',    # 虚线
        'Si_Si': '-.'    # 点画线
    }

def find_rdf_files(base_dir):
    """查找所有RDF文件"""
    rdf_files = []
    method_mapping = get_method_mapping()
    # 同时查找大写和小写的温度文件夹
    temperature_variants = {
        '500k': ['500k', '500K'],
        '1000k': ['1000k', '1000K'],
        '1500k': ['1500k', '1500K'],
        '2000k': ['2000k', '2000K']
    }
    rdf_types = ['rdf_O_O.dat', 'rdf_Si_O.dat', 'rdf_Si_Si.dat']
    
    for method_folder, method_name in method_mapping.items():
        for temp_standard, temp_variants in temperature_variants.items():
            # 尝试不同的温度文件夹名称
            for temp_folder in temp_variants:
                # 构建路径
                if method_folder == 'dft_PBE':
                    analysis_dir = f"{base_dir}/{method_folder}/{temp_folder}/cp2k_analysis_results"
                else:
                    analysis_dir = f"{base_dir}/{method_folder}/{temp_folder}/lammps_analysis_results"
                
                # 如果目录存在，查找RDF文件
                if os.path.exists(analysis_dir):
                    for rdf_file in rdf_types:
                        file_path = os.path.join(analysis_dir, rdf_file)
                        if os.path.exists(file_path):
                            rdf_files.append({
                                'original_path': file_path,
                                'method': method_name,
                                'temperature': temp_standard.upper(),  # 统一使用大写格式
                                'rdf_type': rdf_file.replace('rdf_', '').replace('.dat', ''),
                                'filename': rdf_file
                            })
                    break  # 找到一个有效的温度文件夹就停止
    
    return rdf_files

def copy_and_rename_files(rdf_files, output_dir):
    """复制并重命名RDF文件"""
    for file_info in rdf_files:
        # 构建新文件名
        new_filename = f"{file_info['method']}_{file_info['temperature']}_{file_info['filename']}"
        new_path = os.path.join(output_dir, new_filename)
        
        # 复制文件
        shutil.copy2(file_info['original_path'], new_path)
        file_info['new_path'] = new_path
        print(f"Copied: {file_info['original_path']} -> {new_path}")

def read_rdf_data(file_path):
    """读取RDF数据文件"""
    try:
        data = np.loadtxt(file_path)
        if data.shape[1] >= 2:
            return data[:, 0], data[:, 1]  # r, g(r)
        else:
            print(f"Warning: Invalid data format in {file_path}")
            return None, None
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return None, None

def find_first_peak(r, g_r, skip_points=10):
    """找到RDF的第一个峰"""
    if r is None or g_r is None or len(r) < skip_points + 1:
        return None, None
    
    # 跳过前面的点，找到最大值
    peak_idx = np.argmax(g_r[skip_points:]) + skip_points
    if peak_idx < len(r):
        return r[peak_idx], g_r[peak_idx]
    return None, None

def create_temperature_dataframe(rdf_files, temperature):
    """为特定温度创建数据框"""
    temp_files = [f for f in rdf_files if f['temperature'] == temperature]
    
    # 收集所有数据
    all_data = []
    for file_info in temp_files:
        r, g_r = read_rdf_data(file_info['new_path'])
        if r is not None:
            peak_r, peak_g = find_first_peak(r, g_r)
            all_data.append({
                'Method': file_info['method'],
                'RDF_Type': file_info['rdf_type'],
                'Peak_r': peak_r,
                'Peak_g': peak_g,
                'r_data': r,
                'g_data': g_r
            })
    
    return pd.DataFrame(all_data)

def plot_temperature_comparison(df, temperature, output_dir):
    """为特定温度创建对比图"""
    fig, ax = plt.subplots(figsize=(16, 10))  # 增大图形尺寸
    
    color_map = get_color_mapping()
    linestyle_map = get_linestyle_mapping()
    
    # 用于存储峰值信息，只保存PBE的
    pbe_peaks = []
    
    # 绘制所有曲线
    for _, row in df.iterrows():
        method = row['Method']
        rdf_type = row['RDF_Type']
        r = row['r_data']
        g_r = row['g_data']
        
        if r is not None and g_r is not None:
            # 确定颜色和线型
            color = color_map.get(method, 'black')
            linestyle = linestyle_map.get(rdf_type, '-')
            
            # 绘制曲线
            label = f"{method} - {rdf_type.replace('_', '-')}"
            ax.plot(r, g_r, color=color, linestyle=linestyle, linewidth=3,
                   label=label, alpha=0.9)
            
            # 只为PBE标记峰值
            if method == 'PBE' and row['Peak_r'] is not None:
                ax.plot(row['Peak_r'], row['Peak_g'], 'o', color=color, 
                       markersize=12, markeredgecolor='black', markeredgewidth=2)
                
                # 存储峰位置信息
                pbe_peaks.append({
                    'method': method,
                    'rdf_type': rdf_type,
                    'r': row['Peak_r'],
                    'g': row['Peak_g'],
                    'color': color
                })
    
    # 只标注PBE的峰值
    add_peak_annotations(ax, pbe_peaks)
    
    # 设置图形属性
    ax.set_xlabel('r (Å)', fontsize=35, fontweight='bold')
    ax.set_ylabel('g(r)', fontsize=35, fontweight='bold')
    ax.set_title(f'Radial Distribution Functions at {temperature}', fontsize=40, 
                fontweight='bold', pad=20)
    
    # 设置图例在图外，一列显示
    ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=25, 
             ncol=1, framealpha=0.9)
    
    # 设置轴范围
    ax.set_xlim(0, 6)  # 横坐标范围0-6
    ax.set_ylim(0, None)
    
    # 调整刻度标签大小
    ax.tick_params(axis='both', which='major', labelsize=30)
    
    # 设置刻度
    ax.set_xticks(np.arange(0, 7, 1))
    
    # 保存图片
    plt.tight_layout()
    output_path = os.path.join(output_dir, f'RDF_comparison_{temperature}.png')
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    
    # 同时保存PDF版本
    pdf_path = os.path.join(output_dir, f'RDF_comparison_{temperature}.pdf')
    plt.savefig(pdf_path, dpi=300, bbox_inches='tight', format='pdf')
    
    plt.close()
    print(f"Saved plot: {output_path}")
    print(f"Saved plot: {pdf_path}")

def add_peak_annotations(ax, peak_positions):
    """智能添加峰值标注，避免与曲线重叠"""
    if not peak_positions:
        return
        
    # 按r值排序
    peak_positions.sort(key=lambda x: x['r'])
    
    # 预定义标注位置，参考用户要求
    annotation_positions = {
        'Si_O': {'offset_x': -0.4, 'offset_y': -0.8, 'va': 'top', 'ha': 'right'},     # Si-O 左下方
        'O_O': {'offset_x': 0.2, 'offset_y': 2.2, 'va': 'bottom', 'ha': 'right'},    # O-O 左上角
        'Si_Si': {'offset_x': 0.3, 'offset_y': 0.8, 'va': 'bottom', 'ha': 'left'}     # Si-Si 右上角
    }
    
    for peak in peak_positions:
        rdf_type = peak['rdf_type']
        
        # 获取预定义的偏移位置
        pos_config = annotation_positions.get(rdf_type, 
                                             {'offset_x': 0.2, 'offset_y': 0.5, 'va': 'bottom', 'ha': 'center'})
        
        text_x = peak['r'] + pos_config['offset_x']
        text_y = peak['g'] + pos_config['offset_y']
        
        # 创建标注文本，包含类型、r值和g(r)值
        label_lines = [
            f"{rdf_type.replace('_', '-')}",
            f"r={peak['r']:.2f}Å",
            f"g(r)={peak['g']:.2f}"
        ]
        label = '\n'.join(label_lines)
        
        # 添加标注
        ax.annotate(label, 
                   xy=(peak['r'], peak['g']),
                   xytext=(text_x, text_y),
                   fontsize=25,  # 增大标注字体
                   fontweight='bold',
                   color='red',  # 使用红色文字
                   bbox=dict(boxstyle='round,pad=0.5', 
                           facecolor='white', 
                           edgecolor=peak['color'], 
                           alpha=0.95, 
                           linewidth=2.5),
                   arrowprops=dict(arrowstyle='->', 
                                 color=peak['color'], 
                                 alpha=0.8, 
                                 linewidth=2.5,
                                 connectionstyle="arc3,rad=0.2"),
                   ha=pos_config.get('ha', 'center'),
                   va=pos_config['va'])

                   
def save_temperature_table(df, temperature, output_dir):
    """保存特定温度的数据表"""
    # 创建简化的表格
    table_data = []
    for _, row in df.iterrows():
        table_data.append({
            'Method': row['Method'],
            'RDF_Type': row['RDF_Type'],
            'Peak_r (Å)': f"{row['Peak_r']:.3f}" if row['Peak_r'] else 'N/A',
            'Peak_g(r)': f"{row['Peak_g']:.3f}" if row['Peak_g'] else 'N/A'
        })
    
    table_df = pd.DataFrame(table_data)
    output_path = os.path.join(output_dir, f'RDF_peaks_{temperature}.csv')
    table_df.to_csv(output_path, index=False)
    print(f"Saved table: {output_path}")

def main():
    # 设置基础目录
    base_dir = "/public1/home/sch9516/ZG/MTD_3_database_trained_post_result/crystal_parameters_a_b_c"
    
    # 创建输出目录
    output_dir = setup_directories()
    
    # 查找所有RDF文件
    print("Finding RDF files...")
    rdf_files = find_rdf_files(base_dir)
    print(f"Found {len(rdf_files)} RDF files")
    
    # 复制并重命名文件
    print("\nCopying and renaming files...")
    copy_and_rename_files(rdf_files, output_dir)
    
    # 为每个温度创建数据表和图
    temperatures = ['500K', '1000K', '1500K', '2000K']
    
    for temp in temperatures:
        print(f"\nProcessing temperature: {temp}")
        
        # 创建数据框
        df = create_temperature_dataframe(rdf_files, temp)
        
        if not df.empty:
            # 保存数据表
            save_temperature_table(df, temp, output_dir)
            
            # 创建对比图
            plot_temperature_comparison(df, temp, output_dir)
        else:
            print(f"No data found for temperature {temp}")
    
    print("\nAll processing completed!")

if __name__ == "__main__":
    main()
