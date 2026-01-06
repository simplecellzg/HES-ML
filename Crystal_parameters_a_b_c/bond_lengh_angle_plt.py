import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
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

def get_color_mapping():
    """获取方法颜色映射"""
    return {
        'PBE': 'red',
        'DeePMD': 'blue',
        'ReaxFF': 'green',
        'BKS': 'orange'
    }

def load_bond_data():
    """加载键长键角数据"""
    # 数据定义
    data = {
        'Method': ['expt', 'PBE', 'PBE', 'PBE', 'PBE', 'DeePMD', 'DeePMD', 'DeePMD', 'DeePMD',
                   'ReaxFF', 'ReaxFF', 'ReaxFF', 'ReaxFF', 'BKS', 'BKS', 'BKS', 'BKS'],
        'Temperature': ['', '500K', '1000K', '1500K', '2000K', '500K', '1000K', '1500K', '2000K',
                        '500K', '1000K', '1500K', '2000K', '500K', '1000K', '1500K', '2000K'],
        'Si-O (Å)': [1.614, 1.635, 1.640, 1.646, 1.655, 1.636, 1.642, 1.647, 1.654,
                     1.580, 1.591, 1.602, 1.612, 1.607, 1.610, 1.616, 1.621],
        'Si-O_std': [0, 0.038, 0.055, 0.070, 0.083, 0.039, 0.056, 0.071, 0.084,
                     0.038, 0.053, 0.068, 0.079, 0.036, 0.052, 0.066, 0.077],
        'O-Si-O (degree)': [109.2, 109.4, 109.3, 109.2, 109.2, 109.4, 109.3, 109.2, 109.2,
                            109.3, 109.1, 108.9, 108.8, 109.4, 109.4, 109.3, 109.3],
        'O-Si-O_std': [0, 4.9, 6.8, 8.4, 9.7, 4.7, 6.7, 8.4, 9.6,
                        5.5, 8.2, 10.0, 11.4, 4.6, 6.1, 7.2, 8.1],
        'Si-O-Si (degree)': [143.7, 138.7, 141.2, 143.9, 144.3, 136.9, 138.6, 142.7, 143.1,
                             154.6, 152.7, 150.9, 149.3, 154.0, 154.5, 153.6, 152.9],
        'Si-O-Si_std': [0, 6.6, 10.6, 13.0, 13.9, 5.9, 9.3, 12.8, 14.0,
                         7.9, 10.3, 12.0, 13.1, 7.4, 10.0, 11.1, 11.8]
    }
    
    df = pd.DataFrame(data)
    
    # 分离实验数据和模拟数据
    expt_data = df[df['Method'] == 'expt'].iloc[0]
    sim_data = df[df['Method'] != 'expt']
    
    return expt_data, sim_data

def plot_si_o_bond_length(expt_data, sim_data, output_dir):
    """绘制Si-O键长随温度变化图"""
    fig, ax = plt.subplots(figsize=(16, 10))
    
    color_map = get_color_mapping()
    temperatures = [500, 1000, 1500, 2000]
    
    # 绘制各方法的曲线
    for method in ['PBE', 'DeePMD', 'ReaxFF', 'BKS']:
        method_data = sim_data[sim_data['Method'] == method]
        
        # 提取数据
        bond_lengths = method_data['Si-O (Å)'].values
        bond_stds = method_data['Si-O_std'].values
        
        # 绘制数据点和误差棒，大幅加粗误差线
        ax.errorbar(temperatures, bond_lengths, yerr=bond_stds,
                   marker='o', markersize=12, linewidth=4, capsize=10, capthick=6,
                   color=color_map[method], label=method,
                   markeredgecolor='black', markeredgewidth=2, elinewidth=6)
    
    # 添加实验值参考线并标注
    expt_value = expt_data['Si-O (Å)']
    ax.axhline(y=expt_value, color='black', linestyle='--', 
               linewidth=3, label='Experiment')
    
    # 标注实验值，放在线的上方
    ax.text(2100, expt_value + 0.005, f'Expt: {expt_value:.3f} Å', 
            fontsize=25, fontweight='bold', 
            va='top', ha='left',
            bbox=dict(boxstyle='round,pad=0.5', facecolor='white', 
                     edgecolor='black', alpha=0.8))
    
    # 设置图形属性
    ax.set_xlabel('Temperature (K)', fontsize=35, fontweight='bold')
    ax.set_ylabel('Si-O Bond Length (Å)', fontsize=35, fontweight='bold')
    ax.set_title('Si-O Bond Length vs Temperature', fontsize=40, 
                fontweight='bold', pad=20)
    
    # 计算y轴范围，确保误差棒完全在图内
    all_values = []
    for method in ['PBE', 'DeePMD', 'ReaxFF', 'BKS']:
        method_data = sim_data[sim_data['Method'] == method]
        values = method_data['Si-O (Å)'].values
        stds = method_data['Si-O_std'].values
        all_values.extend(values - stds)
        all_values.extend(values + stds)
    
    y_min = min(all_values) - 0.01
    y_max = max(all_values) + 0.02  # 增加上边界空间
    
    # 扩展x轴范围，让标注完全在框内
    ax.set_xlim(300, 2600)
    ax.set_ylim(y_min, y_max)
    
    # 设置刻度
    ax.set_xticks(temperatures)
    ax.tick_params(axis='both', which='major', labelsize=30)
    
    # 添加网格
    # ax.grid(True, alpha=0.3, linestyle='--')
    
    # 设置图例在图框外
    ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=25, framealpha=0.9)
    
    # 保存图片
    plt.tight_layout()
    output_path = os.path.join(output_dir, 'Si-O_bond_length_vs_temperature.png')
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    
    pdf_path = os.path.join(output_dir, 'Si-O_bond_length_vs_temperature.pdf')
    plt.savefig(pdf_path, dpi=300, bbox_inches='tight', format='pdf')
    
    plt.close()
    print(f"Saved Si-O bond length plot: {output_path}")

def plot_o_si_o_angle(expt_data, sim_data, output_dir):
    """绘制O-Si-O键角随温度变化图"""
    fig, ax = plt.subplots(figsize=(16, 10))
    
    color_map = get_color_mapping()
    temperatures = [500, 1000, 1500, 2000]
    
    # 绘制各方法的曲线
    for method in ['PBE', 'DeePMD', 'ReaxFF', 'BKS']:
        method_data = sim_data[sim_data['Method'] == method]
        
        angles = method_data['O-Si-O (degree)'].values
        angle_stds = method_data['O-Si-O_std'].values
        
        # 大幅加粗误差线
        ax.errorbar(temperatures, angles, yerr=angle_stds,
                   marker='o', markersize=12, linewidth=4, capsize=10, capthick=6,
                   color=color_map[method], label=method,
                   markeredgecolor='black', markeredgewidth=2, elinewidth=6)
    
    # 添加实验值参考线并标注
    expt_value = expt_data['O-Si-O (degree)']
    ax.axhline(y=expt_value, color='black', linestyle='--', 
               linewidth=3, label='Experiment')
    
    # 标注实验值，放在线的上方
    ax.text(2100, expt_value + 0.5, f'Expt: {expt_value:.1f}°', 
            fontsize=25, fontweight='bold', 
            va='top', ha='left',
            bbox=dict(boxstyle='round,pad=0.5', facecolor='white', 
                     edgecolor='black', alpha=0.8))
    
    ax.set_xlabel('Temperature (K)', fontsize=35, fontweight='bold')
    ax.set_ylabel('O-Si-O Bond Angle (degree)', fontsize=35, fontweight='bold')
    ax.set_title('O-Si-O Bond Angle vs Temperature', fontsize=40, 
                 fontweight='bold', pad=20)
    
    # 计算y轴范围，确保误差棒完全在图内
    all_values = []
    for method in ['PBE', 'DeePMD', 'ReaxFF', 'BKS']:
        method_data = sim_data[sim_data['Method'] == method]
        values = method_data['O-Si-O (degree)'].values
        stds = method_data['O-Si-O_std'].values
        all_values.extend(values - stds)
        all_values.extend(values + stds)
    
    y_min = min(all_values) - 1
    y_max = max(all_values) + 2  # 增加上边界空间
    
    # 扩展x轴范围
    ax.set_xlim(300, 2600)
    ax.set_ylim(y_min, y_max)
    ax.set_xticks(temperatures)
    ax.tick_params(axis='both', which='major', labelsize=30)
    ax.grid(True, alpha=0.3, linestyle='--')
    
    # 设置图例在图框外
    ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=25, framealpha=0.9)
    
    # 保存图片
    plt.tight_layout()
    output_path = os.path.join(output_dir, 'O-Si-O_bond_angle_vs_temperature.png')
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    
    pdf_path = os.path.join(output_dir, 'O-Si-O_bond_angle_vs_temperature.pdf')
    plt.savefig(pdf_path, dpi=300, bbox_inches='tight', format='pdf')
    
    plt.close()
    print(f"Saved O-Si-O bond angle plot: {output_path}")

def plot_si_o_si_angle(expt_data, sim_data, output_dir):
    """绘制Si-O-Si键角随温度变化图"""
    fig, ax = plt.subplots(figsize=(16, 10))
    
    color_map = get_color_mapping()
    temperatures = [500, 1000, 1500, 2000]
    
    # 绘制各方法的曲线
    for method in ['PBE', 'DeePMD', 'ReaxFF', 'BKS']:
        method_data = sim_data[sim_data['Method'] == method]
        
        angles = method_data['Si-O-Si (degree)'].values
        angle_stds = method_data['Si-O-Si_std'].values
        
        # 大幅加粗误差线
        ax.errorbar(temperatures, angles, yerr=angle_stds,
                   marker='o', markersize=12, linewidth=4, capsize=10, capthick=6,
                   color=color_map[method], label=method,
                   markeredgecolor='black', markeredgewidth=2, elinewidth=6)
    
    # 添加实验值参考线并标注
    expt_value = expt_data['Si-O-Si (degree)']
    ax.axhline(y=expt_value, color='black', linestyle='--', 
               linewidth=3, label='Experiment')
    
    # 标注实验值，放在线的上方
    ax.text(2100, expt_value + 1, f'Expt: {expt_value:.1f}°', 
            fontsize=25, fontweight='bold', 
            va='top', ha='left',
            bbox=dict(boxstyle='round,pad=0.5', facecolor='white', 
                     edgecolor='black', alpha=0.8))
    
    ax.set_xlabel('Temperature (K)', fontsize=35, fontweight='bold')
    ax.set_ylabel('Si-O-Si Bond Angle (degree)', fontsize=35, fontweight='bold')
    ax.set_title('Si-O-Si Bond Angle vs Temperature', fontsize=40, 
                 fontweight='bold', pad=20)
    
    # 计算y轴范围，确保误差棒完全在图内
    all_values = []
    for method in ['PBE', 'DeePMD', 'ReaxFF', 'BKS']:
        method_data = sim_data[sim_data['Method'] == method]
        values = method_data['Si-O-Si (degree)'].values
        stds = method_data['Si-O-Si_std'].values
        all_values.extend(values - stds)
        all_values.extend(values + stds)
    
    y_min = min(all_values) - 2
    y_max = max(all_values) + 3  # 增加上边界空间
    
    # 扩展x轴范围
    ax.set_xlim(300, 2600)
    ax.set_ylim(y_min, y_max)
    ax.set_xticks(temperatures)
    ax.tick_params(axis='both', which='major', labelsize=30)
    ax.grid(True, alpha=0.3, linestyle='--')
    
    # 设置图例在图框外
    ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=25, framealpha=0.9)
    
    # 保存图片
    plt.tight_layout()
    output_path = os.path.join(output_dir, 'Si-O-Si_bond_angle_vs_temperature.png')
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    
    pdf_path = os.path.join(output_dir, 'Si-O-Si_bond_angle_vs_temperature.pdf')
    plt.savefig(pdf_path, dpi=300, bbox_inches='tight', format='pdf')
    
    plt.close()
    print(f"Saved Si-O-Si bond angle plot: {output_path}")

def save_data_table(expt_data, sim_data, output_dir):
    """保存整理后的数据表"""
    # 整理数据，只包含需要的列
    columns_to_keep = ['Method', 'Temperature', 'Si-O (Å)', 'O-Si-O (degree)', 'Si-O-Si (degree)']
    
    # 准备实验数据行
    expt_row = pd.DataFrame({
        'Method': ['Experiment'],
        'Temperature': [''],
        'Si-O (Å)': [f"{expt_data['Si-O (Å)']:.3f}"],
        'O-Si-O (degree)': [f"{expt_data['O-Si-O (degree)']:.1f}"],
        'Si-O-Si (degree)': [f"{expt_data['Si-O-Si (degree)']:.1f}"]
    })
    
    # 准备模拟数据
    sim_table = sim_data.copy()
    for col in ['Si-O (Å)', 'O-Si-O (degree)', 'Si-O-Si (degree)']:
        std_col = col.replace(' (Å)', '_std').replace(' (degree)', '_std')
        sim_table[col] = sim_table.apply(lambda row: f"{row[col]:.3f} ± {row[std_col]:.3f}" 
                                         if '(Å)' in col else f"{row[col]:.1f} ± {row[std_col]:.1f}", axis=1)
    
    # 选择需要的列
    sim_table = sim_table[columns_to_keep]
    
    # 合并数据
    final_table = pd.concat([expt_row, sim_table], ignore_index=True)
    
    # 保存CSV文件
    output_path = os.path.join(output_dir, 'bond_length_angle_statistics.csv')
    final_table.to_csv(output_path, index=False)
    print(f"Saved data table: {output_path}")

def main():
    # 创建输出目录
    output_dir = './bond_analysis'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # 加载数据
    print("Loading bond length and angle data...")
    expt_data, sim_data = load_bond_data()
    
    # 绘制三个独立的图
    print("Plotting Si-O bond length...")
    plot_si_o_bond_length(expt_data, sim_data, output_dir)
    
    print("Plotting O-Si-O bond angle...")
    plot_o_si_o_angle(expt_data, sim_data, output_dir)
    
    print("Plotting Si-O-Si bond angle...")
    plot_si_o_si_angle(expt_data, sim_data, output_dir)
    
    # 保存数据表
    print("Saving data table...")
    save_data_table(expt_data, sim_data, output_dir)
    
    print("\nAll processing completed!")

if __name__ == "__main__":
    main()
