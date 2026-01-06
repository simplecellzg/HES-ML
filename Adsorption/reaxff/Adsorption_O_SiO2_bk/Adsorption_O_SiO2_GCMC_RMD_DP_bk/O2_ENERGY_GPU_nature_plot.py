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

def read_gcmc_data(filename):
    """读取GCMC吸附数据"""
    try:
        # 读取数据
        data = np.loadtxt(filename, comments='#')
        
        # 列索引
        # 0: Time(ps), 1: Cycle, 2: Delta_N_O, 3: Delta_E_total, 4: Ads_E_per_O,
        # 5: Delta_PE_total, 6: Ads_PE_per_O, 7: N_O_ads, 8: Coverage,
        # 9: N_isolated, 10: N_bridging, 11: N_strong, 12: N_weak,
        # 13: N_O2_pairs, 14: N_surface_OO
        
        return {
            'time': data[:, 0],  # 时间已经是ps单位
            'cycle': data[:, 1],
            'coverage': data[:, 8],
            'n_o_ads': data[:, 7],
            'ads_e_per_o': data[:, 4],
            'n_isolated': data[:, 9],
            'n_bridging': data[:, 10]
        }
    
    except Exception as e:
        print(f"Error reading {filename}: {e}")
        return None

def plot_time_coverage(data):
    """绘制时间-覆盖度关系图"""
    
    # 设置Nature风格
    set_nature_style()
    
    # 创建图形
    fig, ax = plt.subplots(figsize=(16, 12))
    
    time = data['time']
    coverage = data['coverage']
    
    # 绘制Coverage vs Time
    color = nature_colors['blue']
    ax.plot(time, coverage, color=color, linewidth=3, label='Coverage')
    
    # 设置轴标签
    ax.set_xlabel('Time (ps)', fontsize=31)
    ax.set_ylabel('Coverage (atom/Å²)', fontsize=31)
    
    # 设置刻度标签大小
    ax.tick_params(axis='both', labelsize=26)
    
    # 计算后50%时间的Coverage平均值
    half_idx = len(time) // 2
    coverage_last_half = coverage[half_idx:]
    coverage_avg = np.mean(coverage_last_half)
    time_mid = time[half_idx]
    
    # 绘制后50%时间的平均值虚线
    ax.axhline(y=coverage_avg, xmin=0.5, xmax=1.0, 
               color=nature_colors['red'], linewidth=3.0, linestyle='--', alpha=0.8,
               label=f'Coverage avg (last 50%): {coverage_avg:.4f} atom/Å²')
    
    # 添加文本标注
    text_x = time[-1] * 0.75  # 在75%的时间位置
    text_y = coverage_avg -0.002  # 略高于平均线
    
    ax.text(text_x, text_y, 
            f'{coverage_avg:.4f} atom/Å²', 
            color=nature_colors['red'], fontsize=26, fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.5', facecolor='white', 
                     edgecolor=nature_colors['red'], linewidth=2, alpha=0.9))
    
    # 添加垂直线标记50%时间点
    ax.axvline(x=time_mid, color='gray', linewidth=2.0, linestyle=':', alpha=0.5)
    
    # 计算y轴20%的位置
    y_range = ax.get_ylim()[1] - ax.get_ylim()[0]
    y_20_percent = ax.get_ylim()[0] + 0.75 * y_range
    
    ax.text(time_mid, y_20_percent, '50%', 
           horizontalalignment='center', verticalalignment='center', 
           color='gray', fontsize=22)
    
    # 设置标题
    ax.set_title('Time-Coverage Relationship at 1000 K', fontweight='bold', fontsize=35, pad=20)
    
    # 调整x轴和y轴范围
    ax.set_xlim(time[0], time[-1])
    ax.set_ylim(0, max(coverage) * 1.1)  # 留出一些顶部空间
    
    # 添加图例
    ax.legend(loc='best', fontsize=24, frameon=True, fancybox=False, shadow=False)
    
    # 调整布局
    plt.tight_layout()
    
    # 保存图形
    filename = 'ads_gcmc_md_time_coverage_analysis_nature'
    plt.savefig(f'{filename}.png', dpi=1200, bbox_inches='tight')
    plt.savefig(f'{filename}.pdf', dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"\nSaved: {filename}.[png/pdf]")
    
    # 打印统计信息
    print("\n" + "="*70)
    print("TIME-COVERAGE ANALYSIS STATISTICS")
    print("="*70)
    print(f"Time range: {time[0]:.2f} - {time[-1]:.2f} ps")
    print(f"Coverage range: {np.min(coverage):.6f} - {np.max(coverage):.6f} atom/Å²")
    print(f"Final coverage: {coverage[-1]:.6f} atom/Å²")
    print(f"\nLast 50% statistics:")
    print(f"  Time range: {time_mid:.2f} - {time[-1]:.2f} ps")
    print(f"  Coverage average: {coverage_avg:.6f} atom/Å²")
    print(f"  Coverage std: {np.std(coverage_last_half):.6f} atom/Å²")
    print(f"\nOverall statistics:")
    print(f"  Coverage average: {np.mean(coverage):.6f} ± {np.std(coverage):.6f} atom/Å²")
    print(f"  Total O atoms adsorbed: {data['n_o_ads'][-1]}")
    print("="*70)

def main():
    print("\n" + "="*70)
    print("NATURE-STYLE TIME-COVERAGE ANALYSIS")
    print("="*70 + "\n")
    
    # 数据文件路径
    data_file = "energy_data/gcmc_adsorption.dat"
    
    # 检查文件是否存在
    if not os.path.exists(data_file):
        print(f"Error: File '{data_file}' not found!")
        return
    
    # 读取数据
    print("Reading GCMC adsorption data...")
    data = read_gcmc_data(data_file)
    
    if data is None:
        print("Error: Failed to read data!")
        return
    
    # 绘制时间-覆盖度关系图
    print("\nPlotting time-coverage relationship...")
    plot_time_coverage(data)
    
    print("\nAnalysis completed successfully!")

if __name__ == "__main__":
    main()
