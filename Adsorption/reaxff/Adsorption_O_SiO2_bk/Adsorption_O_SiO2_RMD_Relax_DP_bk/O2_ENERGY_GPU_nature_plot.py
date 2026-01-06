#!/usr/bin/env python
import numpy as np
import os
import matplotlib.pyplot as plt
from matplotlib import rcParams
from matplotlib import font_manager
import warnings
warnings.filterwarnings('ignore')

# Nature期刊风格设置
def set_nature_style():
    """设置Nature期刊的绘图风格"""
    
    # 设置字体 - Times New Roman
    font_path = "/home/bingxing2/home/scx7113/DEEPMD_PROJECT/yxb_test_20241109_clean_2_20250910/times-new-roman/times.ttf"
    
    try:
        # 添加字体文件到字体管理器
        if os.path.exists(font_path):
            font_manager.fontManager.addfont(font_path)
            font_family = 'Times New Roman'
            print("成功加载Times New Roman字体")
        else:
            print(f"字体文件 {font_path} 不存在，使用备用字体")
            font_family = 'serif'
    except Exception as e:
        print(f"加载字体时出错: {e}，使用备用字体")
        font_family = 'serif'
    
    # 设置绘图参数
    rcParams.update({
        'font.family': font_family,
        'font.serif': ['Times New Roman', 'Times', 'DejaVu Serif'],
        'font.size': 26,
        'axes.linewidth': 2.0,
        'axes.labelsize': 31,
        'axes.titlesize': 35,
        'xtick.labelsize': 26,
        'ytick.labelsize': 26,
        'legend.fontsize': 24,
        'legend.frameon': True,
        'legend.fancybox': False,
        'legend.shadow': False,
        'legend.framealpha': 1.0,
        'legend.edgecolor': 'black',
        'lines.linewidth': 3.0,
        'lines.markersize': 10,
        'savefig.dpi': 1200,
        'savefig.bbox': 'tight',
        'figure.figsize': [20, 14],
        'axes.grid': False,
        'axes.spines.top': True,
        'axes.spines.right': True,
        'axes.spines.left': True,
        'axes.spines.bottom': True,
        'xtick.direction': 'out',
        'ytick.direction': 'out',
        'pdf.fonttype': 42,
        'ps.fonttype': 42,
        'axes.labelpad': 8,
        'axes.titlepad': 15,
        'xtick.major.pad': 6,
        'ytick.major.pad': 6,
        'text.usetex': False,
        'mathtext.fontset': 'custom',
        'mathtext.rm': font_family,
    })

# Nature推荐的配色方案
nature_colors = {
    'blue': '#0173B2',
    'green': '#029E73',
    'red': '#D55E00',
    'orange': '#E69F00',
    'purple': '#CC79A7',
    'grey': '#999999',
    'black': '#000000'
}

def read_adsorption_data(filename):
    """读取吸附数据，处理重复的step"""
    try:
        # 读取数据
        data = np.loadtxt(filename, comments='#')
        
        # 新的列索引（根据LAMMPS脚本的输出格式）
        # 0: Step, 1: Temp, 2: PE, 3: KE, 4: Etotal, 5: E_deepmd, 6: E_soft, 
        # 7: E_total, 8: Atoms, 9: Type3_O, 10: Type3_O_added, 11: Coverage, 
        # 12: Coverage_added, 13: Delta_E, 14: E_O_contrib, 15: E_ads, 16: E_ads_per_O
        
        steps = data[:, 0]
        
        # 处理重复的step，选择第二个
        unique_steps = []
        selected_indices = []
        
        i = 0
        while i < len(steps):
            current_step = steps[i]
            # 查找相同step的所有索引
            same_step_indices = []
            j = i
            while j < len(steps) and steps[j] == current_step:
                same_step_indices.append(j)
                j += 1
            
            # 如果有重复，选择第二个；否则选择唯一的一个
            if len(same_step_indices) >= 2:
                selected_indices.append(same_step_indices[1])
            else:
                selected_indices.append(same_step_indices[0])
            
            unique_steps.append(current_step)
            i = j
        
        # 提取选定的数据
        selected_data = data[selected_indices]
        
        return {
            'time': selected_data[:, 0] * 0.0002,  # 转换为ps
            'step': selected_data[:, 0],
            'Type3_O': selected_data[:, 9],      # 更新：从第7列改为第9列
            'Coverage': selected_data[:, 11],     # 更新：从第9列改为第11列
            'E_ads_per_O': selected_data[:, 16]  # 更新：从第14列改为第16列
        }
    
    except Exception as e:
        print(f"Error reading {filename}: {e}")
        return None

def plot_adsorption_analysis(data):
    """绘制吸附分析图"""
    
    # 设置Nature风格
    set_nature_style()
    
    # 创建图形
    fig, ax1 = plt.subplots(figsize=(16, 12))
    
    time = data['time']
    coverage = data['Coverage']
    e_ads_per_o = data['E_ads_per_O']
    
    # 绘制Coverage（使用左y轴）
    color1 = nature_colors['green']
    ax1.plot(time, coverage, color=color1, linewidth=3, label='Coverage')
    ax1.set_xlabel('Time (ps)', fontsize=31)
    ax1.set_ylabel('Coverage (atom/Å²)', color='black', fontsize=31)  # 改为黑色，添加单位
    ax1.tick_params(axis='y', labelcolor='black', labelsize=26)  # 改为黑色
    ax1.tick_params(axis='x', labelsize=26)
    
    # 创建第二个y轴用于E_ads_per_O
    ax2 = ax1.twinx()
    color2 = nature_colors['red']
    ax2.plot(time, e_ads_per_o, color=color2, linewidth=3, label='E$_{ads}$ per O')
    ax2.set_ylabel('Adsorption energy per O (eV)', color='black', fontsize=31)  # 改为黑色
    ax2.tick_params(axis='y', labelcolor='black', labelsize=26)  # 改为黑色
    
    # 计算后50%时间的E_ads_per_O平均值
    half_idx = len(time) // 2
    e_ads_last_half = e_ads_per_o[half_idx:]
    e_ads_avg = np.mean(e_ads_last_half)
    time_mid = time[half_idx]
    
    # 绘制后50%时间的平均值虚线
    ax2.axhline(y=e_ads_avg, xmin=0.5, xmax=1.0, 
               color=color2, linewidth=3.0, linestyle='--', alpha=0.8,
               label=f'E$_{{ads}}$ avg (last 50%): {e_ads_avg:.3f} eV')
    
    # 添加文本标注
    # 找一个合适的位置放置标注
    text_x = time[-1] * 0.75  # 在75%的时间位置
    text_y = e_ads_avg + 0.1  # 更高于平均线（从0.05改为0.15）
    
    ax2.text(text_x, text_y, 
            f'{e_ads_avg:.3f} eV', 
            color=color2, fontsize=26, fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.5', facecolor='white', 
                     edgecolor=color2, linewidth=2, alpha=0.9))
    
    # 添加垂直线标记50%时间点
    ax1.axvline(x=time_mid, color='gray', linewidth=2.0, linestyle=':', alpha=0.5)
    
    # 计算y轴20%的位置
    y_range = ax1.get_ylim()[1] - ax1.get_ylim()[0]
    y_20_percent = ax1.get_ylim()[0] + 0.35 * y_range
    
    ax1.text(time_mid, y_20_percent, '50%', 
           horizontalalignment='center', verticalalignment='center', 
           color='gray', fontsize=22)
   
   
    # 设置标题
    ax1.set_title('Adsorption Analysis at 1000 K', fontweight='bold', fontsize=35, pad=20)
    
    # 调整x轴范围
    ax1.set_xlim(time[0], time[-1])
    
    # 创建图例
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    
    # 合并图例
    ax1.legend(lines1 + lines2, labels1 + labels2, 
               loc='best', fontsize=24, frameon=True, fancybox=False, shadow=False)
    
    # 调整布局
    plt.tight_layout()
    
    # 保存图形
    filename = 'adsorption_analysis_nature'
    plt.savefig(f'{filename}.png', dpi=1200, bbox_inches='tight')
    plt.savefig(f'{filename}.pdf', dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"\nSaved: {filename}.[png/pdf]")
    
    # 打印统计信息
    print("\n" + "="*70)
    print("ADSORPTION ANALYSIS STATISTICS")
    print("="*70)
    print(f"Time range: {time[0]:.2f} - {time[-1]:.2f} ps")
    print(f"Coverage range: {np.min(coverage):.4f} - {np.max(coverage):.4f} atom/Å²")  # 添加单位
    print(f"E_ads_per_O range: {np.min(e_ads_per_o):.2f} - {np.max(e_ads_per_o):.2f} eV")
    print(f"\nLast 50% statistics:")
    print(f"  Time range: {time_mid:.2f} - {time[-1]:.2f} ps")
    print(f"  E_ads_per_O average: {e_ads_avg:.3f} eV")
    print(f"  E_ads_per_O std: {np.std(e_ads_last_half):.3f} eV")
    print(f"\nOverall statistics:")
    print(f"  E_ads_per_O average: {np.mean(e_ads_per_o):.3f} ± {np.std(e_ads_per_o):.3f} eV")
    print("="*70)

def main():
    print("\n" + "="*70)
    print("NATURE-STYLE ADSORPTION DATA ANALYSIS")
    print("="*70 + "\n")
    
    # 数据文件路径
    data_file = "energy_data/energy_adsorption.dat"
    
    # 检查文件是否存在
    if not os.path.exists(data_file):
        print(f"Error: File '{data_file}' not found!")
        return
    
    # 读取数据
    print("Reading adsorption data...")
    data = read_adsorption_data(data_file)
    
    if data is None:
        print("Error: Failed to read data!")
        return
    
    # 绘制分析图
    print("\nPlotting analysis...")
    plot_adsorption_analysis(data)
    
    print("\nAnalysis completed successfully!")

if __name__ == "__main__":
    main()
