#!/usr/bin/env python
import numpy as np
import os
import matplotlib.pyplot as plt
from matplotlib import rcParams
from matplotlib import font_manager
import warnings
import glob
import re
from collections import defaultdict

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
    
    # 设置绘图参数 - 更长的比例，稍微增加高度
    rcParams.update({
        'font.family': font_family,
        'font.serif': ['Times New Roman', 'Times', 'DejaVu Serif'],
        'font.size': 28,  # 增大基础字体
        'axes.linewidth': 2.5,
        'axes.labelsize': 34,  # 增大轴标签
        'axes.titlesize': 38,  # 增大标题
        'xtick.labelsize': 28,  # 增大刻度标签
        'ytick.labelsize': 28,
        'legend.fontsize': 20,  # 稍微减小图例字体以适应6列
        'legend.frameon': True,
        'legend.fancybox': False,
        'legend.shadow': False,
        'legend.framealpha': 0.95,
        'legend.edgecolor': 'black',
        'lines.linewidth': 3.5,  # 增大线宽
        'lines.markersize': 10,
        'savefig.dpi': 1200,
        'savefig.bbox': 'tight',
        'figure.figsize': [24, 12],  # 增加高度以容纳图例
        'axes.grid': False,
        'axes.spines.top': True,
        'axes.spines.right': True,
        'axes.spines.left': True,
        'axes.spines.bottom': True,
        'xtick.direction': 'out',
        'ytick.direction': 'out',
        'pdf.fonttype': 42,
        'ps.fonttype': 42,
        'axes.labelpad': 10,
        'axes.titlepad': 20,
        'xtick.major.pad': 8,
        'ytick.major.pad': 8,
        'text.usetex': False,
        'mathtext.fontset': 'custom',
        'mathtext.rm': font_family,
    })

# Nature推荐的配色方案
# JOJO黄金之风配色方案
nature_colors = [
    '#FFD700',  # 金色 (Golden Experience)
    '#FF69B4',  # 亮粉色 (Giorno's hair)
    '#9932CC',  # 紫色 (Golden Experience Requiem)
    '#1E90FF',  # 蓝色 (Mista's outfit)
    '#32CD32',  # 绿色 (Fugo's outfit)
    '#FF6347',  # 橙红色 (Narancia's outfit)
    '#8A2BE2',  # 蓝紫色 (Bruno's outfit)
    '#FF1493',  # 深粉色 (Trish's hair)
    '#00CED1',  # 青色 (Abbacchio's lipstick)
    '#B8860B'   # 深金色 (shadow effects)
]

# 线型定义
line_styles = ['-', '--', '-.', ':', (0, (3, 1, 1, 1)), (0, (5, 1)), (0, (3, 5, 1, 5)), (0, (1, 1))]

def extract_pressure_value(pressure_str):
    """从压力字符串中提取数值"""
    # 匹配数字部分，如 "100atm" -> 100, "1atm" -> 1
    match = re.match(r'(\d+)', pressure_str)
    return int(match.group(1)) if match else 0

def parse_folder_name(folder_name):
    """解析文件夹名称，提取温度和压强信息"""
    # 匹配格式如 GCMC_RMD_100k_1atm
    pattern = r'GCMC_RMD_(\d+)k_(.+)'
    match = re.match(pattern, folder_name)
    
    if match:
        temperature = int(match.group(1))  # 温度（K）
        pressure = match.group(2)  # 压强
        return temperature, pressure
    else:
        return None, None

def read_gcmc_data(filename):
    """读取GCMC吸附数据"""
    try:
        # 读取数据
        data = np.loadtxt(filename, comments='#')
        
        return {
            'time': data[:, 0],  # 时间已经是ps单位
            'cycle': data[:, 1],
            'coverage': data[:, 8] * 100,  # 单位转换：atom/Å² -> atom/nm²
            'n_o_ads': data[:, 7],
            'ads_e_per_o': data[:, 4],
            'n_isolated': data[:, 9],
            'n_bridging': data[:, 10]
        }
    
    except Exception as e:
        print(f"Error reading {filename}: {e}")
        return None

def find_gcmc_folders():
    """寻找所有以GCMC_RMD开头的文件夹"""
    folders = []
    pattern = "GCMC_RMD*"
    
    for folder in glob.glob(pattern):
        if os.path.isdir(folder):
            data_file = os.path.join(folder, "energy_data", "gcmc_adsorption.dat")
            if os.path.exists(data_file):
                temperature, pressure = parse_folder_name(folder)
                if temperature is not None and pressure is not None:
                    folders.append({
                        'folder': folder,
                        'data_file': data_file,
                        'temperature': temperature,
                        'pressure': pressure
                    })
                    print(f"Found: {folder} -> T={temperature}K, P={pressure}")
                else:
                    print(f"Warning: Cannot parse folder name: {folder}")
            else:
                print(f"Warning: Data file not found in {folder}")
    
    return folders

def plot_combined_coverage(folder_data):
    """绘制汇总的时间-覆盖度关系图"""
    
    # 设置Nature风格
    set_nature_style()
    
    # 创建图形 - 增加高度以容纳图例
    fig, ax = plt.subplots(figsize=(24, 12))
    
    # 获取所有唯一的温度和压强，并排序
    temperatures = sorted(list(set([item['temperature'] for item in folder_data])))
    pressures = sorted(list(set([item['pressure'] for item in folder_data])), 
                      key=extract_pressure_value, reverse=True)  # 压力从大到小
    
    print(f"Unique temperatures: {temperatures}")
    print(f"Unique pressures (sorted by value, descending): {pressures}")
    
    # 为每个温度分配颜色
    temp_colors = {}
    for i, temp in enumerate(temperatures):
        temp_colors[temp] = nature_colors[i % len(nature_colors)]
    
    # 为每个压强分配线型
    pressure_styles = {}
    for i, pressure in enumerate(pressures):
        pressure_styles[pressure] = line_styles[i % len(line_styles)]
    
    # 打印颜色和线型分配
    print("\nColor assignment for temperatures:")
    for temp in temperatures:
        print(f"  {temp}K: {temp_colors[temp]}")
    
    print("\nLine style assignment for pressures:")
    for pressure in pressures:
        print(f"  {pressure}: {pressure_styles[pressure]}")
    
    # 重新排序folder_data：按温度分组，每组内按压力从大到小
    folder_data_sorted = []
    for temp in temperatures:
        temp_data = [item for item in folder_data if item['temperature'] == temp]
        temp_data.sort(key=lambda x: extract_pressure_value(x['pressure']), reverse=True)
        folder_data_sorted.extend(temp_data)
    
    # 用于存储所有绘制的线条和标签
    lines = []
    labels = []
    
    # 绘制每个数据集
    max_coverage = 0
    min_time = float('inf')
    max_time = 0
    
    for item in folder_data_sorted:
        folder = item['folder']
        data_file = item['data_file']
        temperature = item['temperature']
        pressure = item['pressure']
        
        print(f"Processing {folder}...")
        data = read_gcmc_data(data_file)
        
        if data is None:
            continue
        
        time = data['time']
        coverage = data['coverage']  # 已经转换为 atom/nm²
        
        # 更新数据范围
        max_coverage = max(max_coverage, np.max(coverage))
        min_time = min(min_time, np.min(time))
        max_time = max(max_time, np.max(time))
        
        # 获取颜色和线型
        color = temp_colors[temperature]
        linestyle = pressure_styles[pressure]
        
        # 设置标签
        label = f"{temperature}K, {pressure}"
        
        # 绘制线条 - 不设置label参数，而是返回line对象
        line, = ax.plot(time, coverage, color=color, linestyle=linestyle, 
                       linewidth=3.5, alpha=0.85)
        
        # 存储线条和标签
        lines.append(line)
        labels.append(label)
    
    # 设置轴标签 - 更新单位
    ax.set_xlabel('Time (ps)', fontsize=34, fontweight='bold')
    ax.set_ylabel('Coverage (atom/nm²)', fontsize=34, fontweight='bold')
    
    # 设置刻度标签大小
    ax.tick_params(axis='both', labelsize=28, width=2, length=6)
    
    # 设置标题
    ax.set_title('Combined Time-Coverage Relationship', fontweight='bold', fontsize=38, pad=25)
    
    # 设置坐标轴范围
    ax.set_xlim(min_time, max_time)
    ax.set_ylim(0, max_coverage * 1.05)
    
    # 使用实际绘制的线条创建图例
    legend = ax.legend(lines, labels, 
                      loc='upper center', fontsize=20, 
                      frameon=True, fancybox=False, shadow=False, 
                      framealpha=0.95, edgecolor='black',
                      ncol=6, columnspacing=0.6, handlelength=1.2,
                      bbox_to_anchor=(0.5, -0.18))  # 使用负值将图例放在图下方
    
    # 手动设置图例边框线宽
    legend.get_frame().set_linewidth(1.5)
    
    # 设置图例标题
    legend.set_title('Conditions (Temp, Pressure)', prop={'size': 22, 'weight': 'bold'})
    
    # 调整布局，为图例留出更多空间
    plt.subplots_adjust(bottom=0.3)  # 增加底部空间
    
    return fig


def main():
    print("\n" + "="*80)
    print("COMBINED NATURE-STYLE TIME-COVERAGE ANALYSIS")
    print("="*80 + "\n")
    
    # 寻找所有GCMC_RMD文件夹
    print("Searching for GCMC_RMD folders...")
    folder_data = find_gcmc_folders()
    
    if not folder_data:
        print("No valid GCMC_RMD folders found!")
        print("Please ensure folders follow the naming pattern: GCMC_RMD_<temperature>k_<pressure>")
        return
    
    print(f"\nFound {len(folder_data)} valid folders")
    
    # 创建输出文件夹
    output_dir = "Combine_GCMC_RMD_plot"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Created output directory: {output_dir}")
    
    # 绘制汇总图
    print("\nPlotting combined time-coverage relationship...")
    fig = plot_combined_coverage(folder_data)
    
    # 保存图形
    filename_base = os.path.join(output_dir, "Combine_GCMC_RMD_all")
    fig.savefig(f'{filename_base}.png', dpi=800, bbox_inches='tight', 
                facecolor='white', edgecolor='none')
    fig.savefig(f'{filename_base}.pdf', dpi=300, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    plt.close()
    
    print(f"\nSaved: {filename_base}.[png/pdf]")
    
    # 输出统计信息
    print("\n" + "="*80)
    print("ANALYSIS SUMMARY")
    print("="*80)
    temperatures = sorted(list(set([item['temperature'] for item in folder_data])))
    pressures = sorted(list(set([item['pressure'] for item in folder_data])), 
                      key=extract_pressure_value, reverse=True)
    print(f"Number of datasets: {len(folder_data)}")
    print(f"Temperature range: {min(temperatures)} - {max(temperatures)} K")
    print(f"Pressure conditions (descending): {', '.join(pressures)}")
    print(f"Output saved to: {output_dir}/")
    print("Coverage unit: atom/nm² (converted from atom/Å² by multiplying by 100)")
    print("Legend layout: 6 columns (by temperature), pressures sorted high to low")
    print("="*80)
    
    print("\nCombined analysis completed successfully!")

if __name__ == "__main__":
    main()
