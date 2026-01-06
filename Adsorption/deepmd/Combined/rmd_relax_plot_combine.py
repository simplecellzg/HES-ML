#!/usr/bin/env python
import numpy as np
import os
import matplotlib.pyplot as plt
from matplotlib import rcParams
from matplotlib import font_manager
from matplotlib import gridspec
import warnings
import glob
import re
from collections import defaultdict
from scipy.interpolate import griddata
from scipy.optimize import curve_fit
from scipy.stats import linregress
from matplotlib.colors import LinearSegmentedColormap

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

    # 设置绘图参数 - 字体都大幅放大
    rcParams.update({
        'font.family': font_family,
        'font.serif': ['Times New Roman', 'Times', 'DejaVu Serif'],
        'font.size': 28,  # 基础字体从20增加到28
        'axes.linewidth': 2.5,
        'axes.labelsize': 32,  # 轴标签从24增加到32
        'axes.titlesize': 34,  # 标题从26增加到34
        'xtick.labelsize': 26,  # 刻度标签从20增加到26
        'ytick.labelsize': 26,  # 刻度标签从20增加到26
        'legend.fontsize': 20,  # 图例字体从16增加到20
        'legend.frameon': True,
        'legend.fancybox': False,
        'legend.shadow': False,
        'legend.framealpha': 0.95,
        'legend.edgecolor': 'black',
        'lines.linewidth': 3.0,  # 线宽增加
        'lines.markersize': 10,  # 标记大小增加
        'savefig.dpi': 1200,
        'savefig.bbox': 'tight',
        'figure.figsize': [40, 28],
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
        'axes.titlepad': 18,
        'xtick.major.pad': 8,
        'ytick.major.pad': 8,
        'text.usetex': False,
        'mathtext.fontset': 'custom',
        'mathtext.rm': font_family,
    })

# 扩展的JoJo风格配色方案
nature_colors = [
    '#FFD700',  # 金色 (Golden Experience)
    '#FF69B4',  # 亮粉色 (Giorno's hair)
    '#9932CC',  # 紫色 (Golden Experience Requiem)
    '#1E90FF',  # 蓝色 (Mista's outfit)
    '#32CD32',  # 绿色 (Fugo's outfit)
    '#FF6347',  # 橙红色 (Narancia's outfit)
    '#FF1493',  # 深粉色 (Trish's hair)
    '#00CED1',  # 青色 (Abbacchio's lipstick)
    '#B8860B',  # 深金色 (shadow effects)
    '#DC143C',  # 深红色 (Diavolo's hair)
    '#4169E1',  # 皇家蓝 (Star Platinum)
    '#FF8C00',  # 深橙色 (DIO's outfit)
    '#9370DB',  # 中紫色 (Crazy Diamond)
    '#20B2AA',  # 浅海蓝色 (Josuke's outfit)
    '#DAA520',  # 金棒色 (The World)
    '#FF6B6B',  # 珊瑚粉 (Jolyne's outfit)
    '#4ECDC4',  # 青绿色 (Stone Free)
    '#45B7D1',  # 天蓝色 (Weather Report)
    '#96CEB4',  # 薄荷绿 (Emporio's outfit)
    '#8A2BE2'   # 蓝紫色 (Bruno's outfit)
]

# 线型定义
line_styles = ['-', '--', '-.', ':', (0, (3, 1, 1, 1)), (0, (5, 1)), (0, (3, 5, 1, 5)), (0, (1, 1))]

# 点线样式定义
marker_styles = ['o', 's', '^', 'D', 'v', '<', '>', 'p', '*', 'h']

def extract_pressure_value(pressure_str):
    """从压力字符串中提取数值，支持科学记数法和小数"""
    # 移除'atm'或'bar'后缀
    pressure_str = pressure_str.replace('atm', '').strip()
    pressure_str = pressure_str.replace(' bar', '').strip()
    # pressure_str = pressure_str.replace('bar', '').strip()  # 也处理单数形式
    try:
        # 直接尝试转换为浮点数（处理0.001, 0.1, 1e-07等形式）
        return float(pressure_str)
    except ValueError:
        # 如果转换失败，尝试匹配数字
        match = re.match(r'([\d.e\-+]+)', pressure_str, re.IGNORECASE)
        if match:
            try:
                return float(match.group(1))
            except ValueError:
                pass
        # 如果都失败了，返回一个很小的正数以避免log(0)
        return 1e-20

# 在 pressure_to_log10 函数中修改注释（约第106行）：
def pressure_to_log10(pressure_str):
    """将压力字符串转换为log10(p/1bar)"""  # 注释从1bar改为1bar
    pressure_value = extract_pressure_value(pressure_str)
    # 确保不会取log(0)，设置一个最小值
    if pressure_value <= 0:
        pressure_value = 1e-20
    # 计算log10，并处理非常小的值
    log_value = np.log10(pressure_value)
    # 避免返回-inf
    if np.isinf(log_value):
        log_value = -20  # 设置一个合理的最小值
    return log_value

def parse_folder_name(folder_name):
    """解析文件夹名称，提取温度和压强信息"""
    pattern = r'RMD_Relax_(\d+)k_(.+)'
    match = re.match(pattern, folder_name)
    if match:
        temperature = int(match.group(1))  # 温度（K）
        pressure = match.group(2)  # 压强
        return temperature, pressure
    else:
        return None, None

def convert_pressure_unit(pressure_str):
    """将压力字符串从atm转换为bar用于显示"""
    return pressure_str.replace('atm', ' bar')

def read_adsorption_data(filename):
    """读取吸附数据，处理重复的step"""
    try:
        data = np.loadtxt(filename, comments='#')
        steps = data[:, 0]
        
        # 处理重复的step，选择第二个
        unique_steps = []
        selected_indices = []
        i = 0
        while i < len(steps):
            current_step = steps[i]
            same_step_indices = []
            j = i
            while j < len(steps) and steps[j] == current_step:
                same_step_indices.append(j)
                j += 1
            
            if len(same_step_indices) >= 2:
                selected_indices.append(same_step_indices[1])
            else:
                selected_indices.append(same_step_indices[0])
            unique_steps.append(current_step)
            i = j
        
        selected_data = data[selected_indices]
        return {
            'time': selected_data[:, 0] * 0.0002,  # 转换为ps
            'step': selected_data[:, 0],
            'temperature': selected_data[:, 1],
            'coverage': selected_data[:, 11] * 100,  # 转换为 atom/nm²
            'e_ads_per_o': selected_data[:, 16] * (-1)  # 乘以-1
        }
    except Exception as e:
        print(f"Error reading {filename}: {e}")
        return None

def calculate_desorption_rate(time, coverage):
    """计算解吸附速率 - 通过覆盖度对时间的负导数"""
    try:
        # 使用后80%的数据来计算解吸附速率，避免初始平衡阶段的影响
        start_idx = int(0.2 * len(time))
        time_subset = time[start_idx:]
        coverage_subset = coverage[start_idx:]
        
        # 计算覆盖度对时间的导数
        dt = np.diff(time_subset)
        dcov_dt = np.diff(coverage_subset) / dt
        
        # 解吸附速率为负的覆盖度变化率的平均值
        desorption_rates = -dcov_dt[dcov_dt < 0]  # 只考虑覆盖度下降的部分
        
        if len(desorption_rates) > 0:
            return np.mean(desorption_rates)
        else:
            # 如果没有明显的解吸附，使用整体的平均变化率
            total_rate = -(coverage_subset[-1] - coverage_subset[0]) / (time_subset[-1] - time_subset[0])
            return max(total_rate, 1e-6)  # 确保返回正值
    except:
        return 1e-6  # 默认很小的值

def find_rmd_relax_folders():
    """寻找三个指定文件夹中的RMD_Relax文件夹"""
    folders = []
    # 定义要查找的三个父文件夹
    parent_folders = [
        "../workdir_reaxff_1",
        "../workdir_reaxff_2",
        "../workdir_reaxff_3",
        "../workdir_reaxff_4",
        "../workdir_reaxff_5"
    ]
    
    print("Searching in parent folders:")
    for parent in parent_folders:
        print(f"  - {parent}")
    print()
    
    # 存储所有找到的数据，按温度和压力分组
    grouped_data = defaultdict(list)
    
    for parent_folder in parent_folders:
        if not os.path.exists(parent_folder):
            print(f"Warning: Parent folder {parent_folder} does not exist!")
            continue
            
        # 在每个父文件夹中查找RMD_Relax文件夹
        pattern = os.path.join(parent_folder, "RMD_Relax*")
        for folder in glob.glob(pattern):
            if os.path.isdir(folder):
                # 获取相对路径的文件夹名称
                folder_name = os.path.basename(folder)
                data_file = os.path.join(folder, "energy_data", "energy_adsorption.dat")
                
                if os.path.exists(data_file):
                    temperature, pressure = parse_folder_name(folder_name)
                    if temperature is not None and pressure is not None:
                        # 按温度和压力分组
                        key = (temperature, pressure)
                        grouped_data[key].append({
                            'parent': parent_folder,
                            'folder': folder,
                            'data_file': data_file
                        })
                        print(f"Found: {parent_folder}/{folder_name} -> T={temperature} K, P={pressure}")
    
    # 整理分组数据
    for (temperature, pressure), data_list in grouped_data.items():
        folders.append({
            'temperature': temperature,
            'pressure': pressure,
            'data_files': data_list,  # 包含多个文件的列表
            'folder': f"RMD_Relax_{temperature}k_{pressure}"  # 用于显示的文件夹名
        })
        print(f"\nCondition T={temperature} K, P={pressure}: found {len(data_list)} datasets")
    
    return folders

def read_and_average_data(data_files):
    """读取多个数据文件并计算平均值"""
    all_data = []
    for file_info in data_files:
        data = read_adsorption_data(file_info['data_file'])
        if data is not None:
            all_data.append(data)
    
    if not all_data:
        return None
    
    # 如果只有一个文件，直接返回
    if len(all_data) == 1:
        return all_data[0]
    
    # 找到所有数据集中最短的时间序列长度
    min_length = min(len(data['time']) for data in all_data)
    
    # 创建平均数据
    averaged_data = {
        'time': all_data[0]['time'][:min_length],  # 使用第一个数据集的时间轴
        'step': all_data[0]['step'][:min_length],
        'temperature': all_data[0]['temperature'][:min_length],
        'coverage': np.zeros(min_length),
        'e_ads_per_o': np.zeros(min_length)
    }
    
    # 计算平均值
    for i in range(min_length):
        coverages = [data['coverage'][i] for data in all_data]
        e_ads = [data['e_ads_per_o'][i] for data in all_data]
        averaged_data['coverage'][i] = np.mean(coverages)
        averaged_data['e_ads_per_o'][i] = np.mean(e_ads)
    
    print(f"  Averaged {len(all_data)} datasets, using {min_length} time points")
    return averaged_data

def read_all_individual_data(data_files):
    """读取所有个别数据文件，返回所有数据点"""
    all_individual_data = []
    for file_info in data_files:
        data = read_adsorption_data(file_info['data_file'])
        if data is not None:
            all_individual_data.append(data)
    
    return all_individual_data

def calculate_statistics(folder_data):
    """计算统计数据，包括解吸附速率"""
    statistics_averaged = []
    all_individual_data = []
    
    for item in folder_data:
        folder = item['folder']
        temperature = item['temperature']
        pressure = item['pressure']  # 保持为字符串，不要转换为set
        data_files = item['data_files']
        
        # 排除压力为0.05的数据
        pressure_value = extract_pressure_value(pressure)
        if abs(pressure_value - 0.05) < 1e-6:  # 考虑浮点数精度
            print(f"Skipping {folder} with pressure 0.05")
            continue
        
        print(f"\nCalculating statistics for {folder}...")
        
        # 读取并平均数据（用于子图1和2）
        averaged_data = read_and_average_data(data_files)
        if averaged_data is None:
            continue
        
        # 读取所有个别数据（用于子图3）
        individual_datasets = read_all_individual_data(data_files)
        
        # 计算后50%的平均值（基于平均数据）
        half_idx = len(averaged_data['time']) // 2
        coverage_last_half = averaged_data['coverage'][half_idx:]
        e_ads_last_half = averaged_data['e_ads_per_o'][half_idx:]
        coverage_avg = np.mean(coverage_last_half)
        e_ads_avg = np.mean(e_ads_last_half)
        
        # 计算解吸附速率（基于平均数据）
        desorption_rate = calculate_desorption_rate(averaged_data['time'], averaged_data['coverage'])
        
        # 压力转换为log10(p/1bar)
        pressure_log10 = pressure_to_log10(pressure)  # 现在pressure是字符串
        
        statistics_averaged.append({
            'folder': folder,
            'temperature': temperature,
            'pressure': pressure,  # 保持为字符串
            'pressure_log10': pressure_log10,
            'coverage_avg': coverage_avg,
            'e_ads_avg': e_ads_avg,
            'desorption_rate': desorption_rate,
            'data': averaged_data  # 保存平均后的时间序列数据
        })
        
        # 收集所有个别数据点（用于子图3）
        for dataset in individual_datasets:
            # 对每个个别数据集计算后50%的平均值
            half_idx = len(dataset['time']) // 2
            coverage_last_half = dataset['coverage'][half_idx:]
            e_ads_last_half = dataset['e_ads_per_o'][half_idx:]
            coverage_individual = np.mean(coverage_last_half)
            e_ads_individual = np.mean(e_ads_last_half)
            
            all_individual_data.append({
                'temperature': temperature,
                'pressure': pressure,  # 保持为字符串
                'pressure_log10': pressure_log10,
                'coverage': coverage_individual,
                'e_ads': e_ads_individual,
                'folder': folder
            })
    
    return statistics_averaged, all_individual_data



def create_combined_plots(folder_data, statistics_averaged, all_individual_data):
    """创建包含3个子图的组合图，使用新的布局"""
    # 设置Nature风格
    set_nature_style()
    
    # 创建一个更紧凑的布局
    fig = plt.figure(figsize=(36, 26))
    
    # 使用GridSpec创建布局
    gs = gridspec.GridSpec(2, 2, figure=fig, hspace=0.35, wspace=0.25, height_ratios=[1, 1])
    
    # 第一个子图占据整个第一行（两列）
    ax1 = fig.add_subplot(gs[0, :])
    # 第二行的两个子图
    ax2 = fig.add_subplot(gs[1, 0])  # 温度倒数-性能关系图
    ax3 = fig.add_subplot(gs[1, 1])  # 覆盖度-吸附能散点图
    
    # 子图1：时间-吸附能关系图（横占两列）
    plot_time_adsorption_energy_subplot(ax1, statistics_averaged)
    
    # 子图2：1000/T-性能关系图（双Y轴版本）
    plot_temperature_performance_dual_y_axis(ax2, statistics_averaged)
    
    # 子图3：覆盖度-吸附能散点图（使用所有个别数据）
    plot_coverage_adsorption_scatter_subplot_all_data(ax3, all_individual_data)
    
    return fig

def plot_time_adsorption_energy_subplot(ax, statistics):
    """绘制时间-单个氧原子吸附能关系图（子图）"""
    # 获取所有唯一的温度和压强，并排序
    temperatures = sorted(list(set([item['temperature'] for item in statistics])))
    pressures = sorted(list(set([convert_pressure_unit(item['pressure']) for item in statistics])), key=extract_pressure_value, reverse=True)
    
    # 为每个温度分配颜色
    temp_colors = {}
    for i, temp in enumerate(temperatures):
        temp_colors[temp] = nature_colors[i % len(nature_colors)]
    
    # 为每个压强分配线型
    pressure_styles = {}
    for i, pressure in enumerate(pressures):
        pressure_styles[convert_pressure_unit(pressure)] = line_styles[i % len(line_styles)]
    
    # 重新排序statistics
    statistics_sorted = []
    for temp in temperatures:
        temp_data = [item for item in statistics if item['temperature'] == temp]
        temp_data.sort(key=lambda x: extract_pressure_value(x['pressure']), reverse=True)
        statistics_sorted.extend(temp_data)
    
    # 绘制每个数据集
    for item in statistics_sorted:
        data = item['data']  # 使用已经平均的数据
        if data is None:
            continue
        
        time = data['time']
        e_ads_per_o = data['e_ads_per_o']
        
        # 获取颜色和线型
        color = temp_colors[item['temperature']]
        linestyle = pressure_styles[convert_pressure_unit(item['pressure'])]
        
        # 设置标签
        label = f"{item['temperature']} K, {convert_pressure_unit(item['pressure'])}"
        
        # 绘制线条
        ax.plot(time, e_ads_per_o, color=color, linestyle=linestyle,
                linewidth=3.0, label=label, alpha=0.85)
    
    # 设置轴标签
    ax.set_xlabel('Time (ps)', fontsize=32, fontweight='bold')
    ax.set_ylabel('Adsorption Energy per O Atom (eV)', fontsize=32, fontweight='bold')
    ax.set_title('(a) Time vs Adsorption Energy per O Atom (Averaged)', fontweight='bold', fontsize=34)
    
    # 设置刻度标签大小
    ax.tick_params(axis='both', labelsize=26, width=2.5, length=8)
    
    # 创建图例并放在右下角，4列，以适应两列布局
    legend_labels = []
    legend_handles = []
    for temp in temperatures:
        temp_items = [item for item in statistics_sorted if item['temperature'] == temp]
        for item in temp_items:
            label = f"{item['temperature']} K, {convert_pressure_unit(item['pressure'])}"
            color = temp_colors[item['temperature']]
            linestyle = pressure_styles[convert_pressure_unit(item['pressure'])]
            line = plt.Line2D([0], [0], color=color, linestyle=linestyle, linewidth=3.0, alpha=0.85)
            legend_handles.append(line)
            legend_labels.append(label)
    
    # 图例放在右下角，4列（从6列改为4列）
    legend = ax.legend(legend_handles, legend_labels, loc='lower right', fontsize=22, frameon=True,
                      fancybox=False, shadow=False, framealpha=0.95, edgecolor='black', ncol=6,
                      columnspacing=0.8, handlelength=1.2, handletextpad=0.8)
    legend.get_frame().set_linewidth(2.0)

def plot_temperature_performance_dual_y_axis(ax, statistics):
    """绘制1000/T-性能关系图（双Y轴版本）"""
    # 获取唯一的压力，按数值排序
    pressures = sorted(list(set([convert_pressure_unit(item['pressure']) for item in statistics])), key=extract_pressure_value, reverse=True)
    
    # 为每个压力分配颜色
    pressure_colors = {}
    for i, pressure in enumerate(pressures):
        pressure_colors[pressure] = nature_colors[i % len(nature_colors)]
    
    # 创建第二个Y轴
    ax2 = ax.twinx()
    
    # 存储所有的拟合线信息，用于后续标注
    energy_fits = []
    coverage_fits = []
    
    # 绘制吸附能（左Y轴）- 使用实心方形
    for pressure in pressures:
        # 修正：移除花括号，正确比较字符串
        pressure_data = [item for item in statistics if convert_pressure_unit(item['pressure']) == pressure]
        pressure_data.sort(key=lambda x: x['temperature'])
        
        if len(pressure_data) < 2:
            continue
        
        temperatures = [item['temperature'] for item in pressure_data]
        e_ads = [item['e_ads_avg'] for item in pressure_data]
        inverse_temps = [1000.0/temp for temp in temperatures]
        
        # 绘制数据点（散点，实心方形）
        ax.scatter(inverse_temps, e_ads, color=pressure_colors[pressure], marker='s',  # 实心方形
                  s=100, alpha=0.85, label=f'{pressure} (E)')
        
        # 对数拟合: y = a * ln(x) + b
        if len(inverse_temps) >= 2:
            # 对数变换
            log_inverse_temps = np.log(inverse_temps)
            slope, intercept, r_value, p_value, std_err = linregress(log_inverse_temps, e_ads)
            
            # 生成拟合曲线的点
            fit_x = np.linspace(min(inverse_temps), max(inverse_temps), 100)
            fit_y = slope * np.log(fit_x) + intercept
            
            # 绘制拟合线（虚线）
            ax.plot(fit_x, fit_y, '--', color=pressure_colors[pressure], linewidth=2.0, alpha=0.7)
            
            # 保存拟合信息
            energy_fits.append({
                'pressure': pressure,
                'color': pressure_colors[pressure],
                'slope': slope,
                'intercept': intercept,
                'left_x': fit_x[0],  # 拟合线左端点
                'left_y': fit_y[0],  # 拟合线左端点的y值
                'right_x': fit_x[-1],
                'right_y': fit_y[-1]
            })
    
    # 绘制覆盖度（右Y轴）- 使用实心三角形
    for pressure in pressures:
        # 修正：移除花括号，正确比较字符串
        pressure_data = [item for item in statistics if convert_pressure_unit(item['pressure']) == pressure]
        pressure_data.sort(key=lambda x: x['temperature'])
        
        if len(pressure_data) < 2:
            continue
        
        temperatures = [item['temperature'] for item in pressure_data]
        coverages = [item['coverage_avg'] for item in pressure_data]
        inverse_temps = [1000.0/temp for temp in temperatures]
        
        # 绘制数据点（散点，实心三角形）
        ax2.scatter(inverse_temps, coverages, color=pressure_colors[pressure], marker='^',  # 实心三角形
                   s=100, alpha=0.85, label=f'{pressure} (C)')

        
        # 对数拟合: y = a * ln(x) + b
        if len(inverse_temps) >= 2:
            # 对数变换
            log_inverse_temps = np.log(inverse_temps)
            slope, intercept, r_value, p_value, std_err = linregress(log_inverse_temps, coverages)
            
            # 生成拟合曲线的点
            fit_x = np.linspace(min(inverse_temps), max(inverse_temps), 100)
            fit_y = slope * np.log(fit_x) + intercept
            
            # 绘制拟合线（实线）
            ax2.plot(fit_x, fit_y, '-', color=pressure_colors[pressure], linewidth=2.0, alpha=0.7)
            
            # 保存拟合信息
            coverage_fits.append({
                'pressure': pressure,
                'color': pressure_colors[pressure],
                'slope': slope,
                'intercept': intercept,
                'left_x': fit_x[0],
                'left_y': fit_y[0],
                'right_x': fit_x[-1],  # 拟合线右端点
                'right_y': fit_y[-1]   # 拟合线右端点的y值
            })
    
    # 设置轴范围
    ax.set_xlim(0.6, 2.6)  # 横坐标范围
    ax.set_ylim(2.0, 3.4)  # 能量范围
    ax2.set_ylim(1.0, 9.0)  # 覆盖度范围
    
    # 准备分组的标注信息
    # 能量拟合按y值排序
    energy_fits.sort(key=lambda x: x['left_y'], reverse=True)
    # 覆盖度拟合按y值排序
    coverage_fits.sort(key=lambda x: x['left_y'], reverse=True)
    
    # 在图的左侧内部添加能量拟合方程
    x_position = 0.65  # 在图内左侧的x坐标
    y_spacing = 0.045  # 减小垂直间距（相对于能量轴范围）
    energy_range = ax.get_ylim()[1] - ax.get_ylim()[0]
    
    # 从图的上部开始标注能量方程
    start_y_energy = ax.get_ylim()[1] - 0.05 * energy_range  # 从顶部稍微往下一点开始
    for i, fit in enumerate(energy_fits):
        # 对数拟合方程: y = a*ln(x) + b
        equation = f'E: y = {fit["slope"]:.2f}ln(x) + {fit["intercept"]:.2f}'
        # 计算标注位置
        y_pos = start_y_energy - i * y_spacing * energy_range
        # 添加标注（虚线框）
        ax.text(x_position, y_pos, equation, fontsize=13,  # 稍微减小字体
               color=fit['color'], ha='left', va='center', transform=ax.transData,
               bbox=dict(boxstyle='round,pad=0.2',  # 减小内边距
                        facecolor='white', edgecolor=fit['color'],
                        alpha=0.9, linewidth=1.2, linestyle='--'))  # 虚线框
    
    # 在能量方程下方添加覆盖度拟合方程
    # 计算能量方程组的底部位置
    energy_bottom = start_y_energy - len(energy_fits) * y_spacing * energy_range
    start_y_coverage = energy_bottom - 0.15 * energy_range  # 留一点间隔
    
    for i, fit in enumerate(coverage_fits):
        # 对数拟合方程: y = a*ln(x) + b
        equation = f'C: y = {fit["slope"]:.2f}ln(x) + {fit["intercept"]:.2f}'
        # 计算标注位置
        y_pos = start_y_coverage - i * y_spacing * energy_range
        # 添加标注（实线框）
        ax.text(x_position, y_pos, equation, fontsize=13,  # 稍微减小字体
               color=fit['color'], ha='left', va='center', transform=ax.transData,
               bbox=dict(boxstyle='round,pad=0.2',  # 减小内边距
                        facecolor='white', edgecolor=fit['color'],
                        alpha=0.9, linewidth=1.2, linestyle='-'))  # 实线框
    
    # 设置轴标签
    ax.set_xlabel('1000/T (K$^{-1}$)', fontsize=32, fontweight='bold')
    ax.set_ylabel('Adsorption Energy per O (eV)', fontsize=32, fontweight='bold', color='black')
    ax2.set_ylabel('Coverage (atom/nm$^{2}$)', fontsize=32, fontweight='bold', color='black')
    ax.set_title('(b) Temperature Dependence (Averaged)', fontweight='bold', fontsize=34)
    
    # 设置刻度标签
    ax.tick_params(axis='both', labelsize=26, width=2.5, length=8)
    ax2.tick_params(axis='y', labelsize=26, width=2.5, length=8)
    
    # 设置Y轴颜色
    ax.tick_params(axis='y', colors='black')
    ax2.tick_params(axis='y', colors='black')
    
    # 添加网格
    ax.grid(True, alpha=0.3, linestyle='--')
    
    # 创建组合图例（横排，放置于图内右下角）
    legend_elements = []
    for pressure in pressures:
        # 添加能量散点（实心方形）
        legend_elements.append(plt.Line2D([0], [0], color=pressure_colors[pressure], linestyle='none',
                                        marker='s', markersize=10, label=f'{pressure} Energy'))
        # 添加覆盖度散点（实心三角形）
        legend_elements.append(plt.Line2D([0], [0], color=pressure_colors[pressure], linestyle='none',
                                        marker='^', markersize=10, label=f'{pressure} Coverage'))
    
    # 创建图例，放在图内右下角
    legend = ax.legend(handles=legend_elements, loc='center right',  # 右下角
                      fontsize=20, frameon=True, fancybox=False, shadow=False,
                      framealpha=0.95, edgecolor='black', ncol=1,  # 单列显示
                      columnspacing=1.0, handletextpad=0.5)
    legend.get_frame().set_linewidth(2.0)



def plot_coverage_adsorption_scatter_subplot_all_data(ax, all_individual_data):
    """绘制覆盖度-吸附能散点图（子图），强调数据分布特征而非线性关系"""
    from scipy import stats
    from matplotlib.patches import Ellipse
    from matplotlib.ticker import FormatStrFormatter
    
    # 提取数据
    coverages = np.array([item['coverage'] for item in all_individual_data])
    e_ads_values = np.array([item['e_ads'] for item in all_individual_data])
    temperatures = [item['temperature'] for item in all_individual_data]
    
    # 为不同温度分配颜色（使用原JoJo配色）
    temp_unique = sorted(list(set(temperatures)))
    temp_colors = {}
    for i, temp in enumerate(temp_unique):
        temp_colors[temp] = nature_colors[i % len(nature_colors)]
    
    # 绘制每个温度的数据点
    for temp in temp_unique:
        temp_data = [item for item in all_individual_data if item['temperature'] == temp]
        temp_coverages = np.array([item['coverage'] for item in temp_data])
        temp_e_ads = np.array([item['e_ads'] for item in temp_data])
        
        # 使用原代码的散点样式（去掉edgecolors）
        ax.scatter(temp_coverages, temp_e_ads, color=temp_colors[temp],
                  s=120, alpha=0.7, label=f'{temp} K')

       # 计算每个温度的统计信息
        mean_coverage = np.mean(temp_coverages)
        mean_e_ads = np.mean(temp_e_ads)
        std_e_ads = np.std(temp_e_ads)
        
        # 添加误差条
        ax.errorbar(mean_coverage, mean_e_ads, yerr=std_e_ads, 
                fmt='none', color=temp_colors[temp], capsize=12, 
                capthick=4.5, alpha=0.8)
    
    # 计算统计信息
    mean_e_ads = np.mean(e_ads_values)
    std_e_ads = np.std(e_ads_values)
    median_e_ads = np.median(e_ads_values)
    
    # 绘制平均值和标准差范围
    ax.axhline(y=mean_e_ads, color='black', linestyle='-', linewidth=3.0, 
               alpha=0.9, label=f'Mean: {mean_e_ads:.3f} eV')
    ax.axhspan(mean_e_ads - std_e_ads, mean_e_ads + std_e_ads, 
               alpha=0.30, color='gray', label=f'±1σ: {std_e_ads:.3f} eV')
    #ax.axhspan(mean_e_ads - 2*std_e_ads, mean_e_ads + 2*std_e_ads, 
    #           alpha=0.15, color='gray')
    
    # 添加Kim & Boudart (1991) 实验数据
    exp_value = 3.004
    exp_error = 0.311
    ax.axhspan(exp_value - exp_error, exp_value + exp_error, 
               alpha=0.1, color='red', zorder=0)
    ax.axhline(y=exp_value, color='red', linestyle=':', linewidth=3.0, alpha=0.9)
    
    # 设置主图的y轴范围
    x_margin = (coverages.max() - coverages.min()) * 0.2
    ax.set_xlim(coverages.min() - x_margin, coverages.max() + x_margin)
    y_margin_up = (e_ads_values.max() - e_ads_values.min()) * 0.6
    y_margin_down = (e_ads_values.max() - e_ads_values.min()) * 0.6
    y_min = e_ads_values.min() - y_margin_down
    y_max = e_ads_values.max() + y_margin_up
    ax.set_ylim(y_min, y_max)
    
    # 设置x轴格式为小数点后一位
    ax.xaxis.set_major_formatter(FormatStrFormatter('%.1f'))
    
    # 在右侧添加垂直的核密度图 - 使用fig.add_axes方式
    pos = ax.get_position()
    kde_width = 0.10  # 核密度图宽度（相对于主图宽度的比例）
    fig = ax.get_figure()
    ax_kde = fig.add_axes([pos.x1, pos.y0, kde_width * pos.width, pos.height])
    
    # 计算核密度估计
    kde = stats.gaussian_kde(e_ads_values)
    e_ads_range = np.linspace(e_ads_values.min(), e_ads_values.max(), 200)
    kde_values = kde(e_ads_range)
    
    # 绘制垂直的核密度图（旋转90度）
    ax_kde.fill_betweenx(e_ads_range, kde_values, alpha=0.6, color='skyblue')
    #ax_kde.plot(kde_values, e_ads_range, color='navy', linewidth=3.0)
    ax_kde.axhline(y=mean_e_ads, color='black', linestyle='-', linewidth=2.5)
    ax_kde.axhline(y=exp_value, color='red', linestyle=':', linewidth=2.5)
    
    # 设置核密度图的范围和样式 - 使用与主图相同的y轴范围
    ax_kde.set_ylim(y_min, y_max)
    ax_kde.set_xlabel('Density', fontsize=32, fontweight='bold')
    ax_kde.tick_params(axis='x', labelsize=26, width=2.5, length=8)
    
    # 完全隐藏y轴
    ax_kde.yaxis.set_visible(False)
    
    # 移除左侧的脊线（spine）
    ax_kde.spines['left'].set_visible(False)
    
    # 调整x轴范围，让图形充满整个区域
    ax_kde.set_xlim(0, kde_values.max() * 1.1)
    
    # 调整统计信息文本框的位置 - 放到左上角，但保持一定距离
    stats_text = (f'Mean: {mean_e_ads:.3f} eV\n'
                  f'Std:  {std_e_ads:.3f} eV\n'
                  f'n =   {len(all_individual_data)}')
    
    
    
    ax.text(0.04, 0.95, stats_text, transform=ax.transAxes, fontsize=24,
            verticalalignment='top',  # 改为bottom对齐
            linespacing=1.2,  # 增加行距（默认是1.2）
            bbox=dict(boxstyle='round,pad=0.5', facecolor='white', 
                     edgecolor='black', linewidth=1.5, alpha=0.9))

    
    # 调整实验值标注位置 - 箭头指向更右侧，文本高于实验值上限
    ax.annotate('Kim & Boudart (1991)\n3.00±0.31 eV', 
                xy=(coverages.mean() + 1.5, exp_value),
                xytext=(coverages.mean() + 0.8, exp_value + exp_error + 0.05),
                fontsize=24, color='red',
                ha='center', va='bottom',
                arrowprops=dict(arrowstyle='->', color='red', lw=2.0, alpha=0.9))
    
    # 设置轴标签和标题（保持原代码的字体设置）
    ax.set_xlabel('Coverage (atom/nm$^{2}$)', fontsize=32, fontweight='bold')
    ax.set_ylabel('Adsorption Energy per O (eV)', fontsize=32, fontweight='bold')
    ax.set_title('(c) Coverage vs Adsorption Energy Distribution', fontweight='bold', fontsize=34)
    ax.tick_params(axis='both', labelsize=26, width=2.5, length=8)
    
    # 温度图例放在右下角
    temp_handles = []
    temp_labels = []
    for temp in temp_unique:
        temp_handles.append(plt.scatter([], [], color=temp_colors[temp], s=120, alpha=0.7))
        temp_labels.append(f'{temp} K')
    
    temp_legend = ax.legend(temp_handles, temp_labels, loc='lower right', fontsize=22,
                          frameon=True, fancybox=False, shadow=False, framealpha=0.95,
                          edgecolor='black', ncol=2, title='Temperature')
    temp_legend.get_frame().set_linewidth(2.0)
    temp_legend.get_title().set_fontsize(24)
    temp_legend.get_title().set_fontweight('bold')
    
    # 数据聚集区域的椭圆标注
    # cov_std = np.std(coverages)
    # ellipse = Ellipse((np.mean(coverages), mean_e_ads), 
    #                   width=1.5*cov_std,  
    #                   height=1.5*std_e_ads,  
    #                   angle=0, facecolor='none', 
    #                   edgecolor='blue', linewidth=2.0, 
    #                   linestyle='--', alpha=0.5)
    # ax.add_patch(ellipse)
    
    # 添加网格
    ax.grid(True, alpha=0.3, linestyle='--')



def save_data_to_dat_files(folder_data, statistics_averaged, all_individual_data, output_dir):
    """将数据保存为dat文件"""
    # 保存平均时间序列数据
    time_series_file = os.path.join(output_dir, "averaged_time_series_data.dat")
    with open(time_series_file, 'w') as f:
        f.write("# Averaged time series data from multiple datasets\n")
        f.write("# Note: Adsorption energy has been multiplied by -1\n")
        f.write("# Temperature(K)\tPressure\tTime(ps)\tCoverage(atom/nm²)\tE_ads_per_O(eV)\n")
        
        for item in statistics_averaged:
            temperature = item['temperature']
            pressure = convert_pressure_unit(item['pressure'])
            data = item['data']
            if data is None:
                continue
            
            for i in range(len(data['time'])):
                f.write(f"{temperature}\t{pressure}\t{data['time'][i]:.4f}\t"
                       f"{data['coverage'][i]:.6f}\t{data['e_ads_per_o'][i]:.6f}\n")
    
    print(f"Averaged time series data saved to: {time_series_file}")
    
    # 保存平均统计数据
    statistics_file = os.path.join(output_dir, "averaged_statistics_data.dat")
    with open(statistics_file, 'w') as f:
        f.write("# Statistical summary of averaged data\n")
        f.write("# Note: Adsorption energy has been multiplied by -1\n")
        f.write("# Temp(K)\tPressure\tlog10(P/1bar)\t1000/T(K^-1)\tCoverage_avg(atom/nm²)\tE_ads_avg(eV)\tDesorption_rate(atom/(nm²·ps))\n")
        
        for item in sorted(statistics_averaged, key=lambda x: (x['temperature'], x['pressure_log10'])):
            inverse_temp = 1000.0 / item['temperature']
            f.write(f"{item['temperature']}\t{convert_pressure_unit(item['pressure'])}\t"
                   f"{item['pressure_log10']:.4f}\t{inverse_temp:.4f}\t"
                   f"{item['coverage_avg']:.6f}\t{item['e_ads_avg']:.6f}\t{item['desorption_rate']:.6f}\n")
    
    print(f"Averaged statistics data saved to: {statistics_file}")
    
    # 保存所有个别数据点
    individual_file = os.path.join(output_dir, "all_individual_data_points.dat")
    with open(individual_file, 'w') as f:
        f.write("# All individual data points from all datasets\n")
        f.write("# Note: Adsorption energy has been multiplied by -1\n")
        f.write("# Temp(K)\tPressure\tlog10(P/1bar)\t1000/T(K^-1)\tCoverage(atom/nm²)\tE_ads(eV)\tFolder\n")
        
        for item in sorted(all_individual_data, key=lambda x: (x['temperature'], x['pressure_log10'])):
            inverse_temp = 1000.0 / item['temperature']
            f.write(f"{item['temperature']}\t{convert_pressure_unit(item['pressure'])}\t"
                   f"{item['pressure_log10']:.4f}\t{inverse_temp:.4f}\t"
                   f"{item['coverage']:.6f}\t{item['e_ads']:.6f}\t{item['folder']}\n")
    
    print(f"All individual data points saved to: {individual_file}")

def save_statistics_to_file(statistics_averaged, all_individual_data, output_dir):
    """将统计数据保存到文件"""
    filename = os.path.join(output_dir, "combined_statistics_summary.txt")
    with open(filename, 'w') as f:
        f.write("COMBINED RMD_Relax Analysis Statistics Summary\n")
        f.write("="*60 + "\n")
        f.write("Data from 3 datasets:\n")
        f.write("  - yxb_test_20241109_clean_2_20250921\n")
        f.write("  - yxb_test_20241109_clean_2_20250922\n")
        f.write("  - yxb_test_20241109_clean_2_20250923\n")
        f.write("="*60 + "\n")
        f.write("Note: Adsorption energy has been multiplied by -1\n")
        f.write("="*60 + "\n\n")
        
        f.write("AVERAGED DATA (for subplots a and b):\n")
        f.write("-"*50 + "\n")
        f.write("Temp(K)\tPressure\tlog10(P/1bar)\t1000/T(K^-1)\tCoverage(atom/nm²)\tE_ads(eV)\tDesorption_rate(atom/(nm²·ps))\n")
        f.write("-"*100 + "\n")
        for item in sorted(statistics_averaged, key=lambda x: (x['temperature'], x['pressure_log10'])):
            inverse_temp = 1000.0 / item['temperature']
            f.write(f"{item['temperature']}\t{convert_pressure_unit(item['pressure'])}\t"
                   f"{item['pressure_log10']:.2f}\t{inverse_temp:.4f}\t"
                   f"{item['coverage_avg']:.4f}\t{item['e_ads_avg']:.4f}\t{item['desorption_rate']:.6f}\n")
        
        f.write(f"\n\nINDIVIDUAL DATA POINTS (for subplot c): {len(all_individual_data)} points\n")
        f.write("-"*50 + "\n")
        f.write("Temp(K)\tPressure\tlog10(P/1bar)\t1000/T(K^-1)\tCoverage(atom/nm²)\tE_ads(eV)\tFolder\n")
        f.write("-"*100 + "\n")
        for item in sorted(all_individual_data, key=lambda x: (x['temperature'], x['pressure_log10'])):
            inverse_temp = 1000.0 / item['temperature']
            f.write(f"{item['temperature']}\t{convert_pressure_unit(item['pressure'])}\t"
                   f"{item['pressure_log10']:.2f}\t{inverse_temp:.4f}\t"
                   f"{item['coverage']:.4f}\t{item['e_ads']:.4f}\t{item['folder']}\n")
    
    print(f"Combined statistics saved to: {filename}")

def main():
    print("\n" + "="*80)
    print("COMBINED RMD_RELAX ANALYSIS (AVERAGED + INDIVIDUAL DATA)")
    print("="*80 + "\n")
    
    # 寻找所有RMD_Relax文件夹
    print("Searching for RMD_Relax folders in multiple datasets...")
    folder_data = find_rmd_relax_folders()
    
    if not folder_data:
        print("No valid RMD_Relax folders found!")
        return
    
    print(f"\nFound {len(folder_data)} unique conditions")
    
    # 创建输出文件夹
    output_dir = "Combined_RMD_Relax_plot"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    print(f"Created output directory: {output_dir}")
    
    # 计算统计数据（包括平均数据和所有个别数据）
    print("\nCalculating statistics (both averaged and individual data)...")
    statistics_averaged, all_individual_data = calculate_statistics(folder_data)
    
    print(f"Generated {len(statistics_averaged)} averaged statistics")
    print(f"Collected {len(all_individual_data)} individual data points")
    
    # 保存统计数据到文件
    save_statistics_to_file(statistics_averaged, all_individual_data, output_dir)
    
    # 保存数据到dat文件
    print("\nSaving data to dat files...")
    save_data_to_dat_files(folder_data, statistics_averaged, all_individual_data, output_dir)
    
    # 创建组合图
    print("\nCreating combined plots (averaged + individual data)...")
    fig = create_combined_plots(folder_data, statistics_averaged, all_individual_data)
    
    # 保存组合图
    filename_base = os.path.join(output_dir, "Combined_RMD_Relax_analysis")
    fig.savefig(f'{filename_base}.png', dpi=800, bbox_inches='tight', 
               facecolor='white', edgecolor='none')
    fig.savefig(f'{filename_base}.pdf', dpi=300, bbox_inches='tight',
               facecolor='white', edgecolor='none')
    plt.close()
    
    print(f"Saved: {filename_base}.[png/pdf]")
    
    # 输出统计信息
    print("\n" + "="*80)
    print("ANALYSIS SUMMARY")
    print("="*80)
    
    temperatures = sorted(list(set([item['temperature'] for item in folder_data])))
    pressures = sorted(list(set([convert_pressure_unit(item['pressure']) for item in folder_data])), 
                      key=extract_pressure_value, reverse=True)
    
    print(f"Number of unique conditions: {len(folder_data)}")
    print(f"Temperature range: {min(temperatures)} - {max(temperatures)} K")
    print(f"Pressure conditions (descending): {', '.join(pressures)}")
    print(f"Output saved to: {output_dir}/")
    print(f"Averaged data points: {len(statistics_averaged)}")
    print(f"Individual data points: {len(all_individual_data)}")
    print("NOTE: All adsorption energies have been multiplied by -1")
    print("Coverage unit: atom/nm² (converted from atom/Å² by multiplying by 100)")
    print("Statistics include last 50% averages for coverage and adsorption energy")
    print("Desorption rates calculated from coverage derivatives")
    
    print("\nPlots generated:")
    print("(a) Time vs Adsorption Energy per O Atom (Averaged) - spans 2 columns")
    print("(b) 1000/T vs Performance (Averaged, dual Y-axis with linear fits)")
    print("(c) Coverage vs Adsorption Energy scatter plot (ALL INDIVIDUAL DATA)")
    
    print("="*80)
    print("Combined analysis completed successfully!")

if __name__ == "__main__":
    main()
