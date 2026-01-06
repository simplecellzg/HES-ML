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
    '#96CEB4',   # 薄荷绿 (Emporio's outfit)
    '#8A2BE2'   # 蓝紫色 (Bruno's outfit)
]

# 线型定义
line_styles = ['-', '--', '-.', ':', (0, (3, 1, 1, 1)), (0, (5, 1)), (0, (3, 5, 1, 5)), (0, (1, 1))]

# 点线样式定义
marker_styles = ['o', 's', '^', 'D', 'v', '<', '>', 'p', '*', 'h']

def extract_pressure_value(pressure_str):
    """从压力字符串中提取数值，支持科学记数法和小数"""
    # 移除'atm'后缀
    pressure_str = pressure_str.replace('atm', '').strip()
    
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

def pressure_to_log10(pressure_str):
    """将压力字符串转换为log10(p/1atm)"""
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
    """寻找所有以RMD_Relax开头的文件夹"""
    folders = []
    pattern = "RMD_Relax*"
    
    for folder in glob.glob(pattern):
        if os.path.isdir(folder):
            data_file = os.path.join(folder, "energy_data", "energy_adsorption.dat")
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

def calculate_statistics(folder_data):
    """计算统计数据，包括解吸附速率"""
    statistics = []
    
    for item in folder_data:
        folder = item['folder']
        data_file = item['data_file']
        temperature = item['temperature']
        pressure = item['pressure']
        
        print(f"Calculating statistics for {folder}...")
        data = read_adsorption_data(data_file)
        
        if data is None:
            continue
        
        # 计算后25%的平均值
        half_idx = len(data['time']) // 2
        coverage_last_half = data['coverage'][half_idx:]
        e_ads_last_half = data['e_ads_per_o'][half_idx:]
        
        coverage_avg = np.mean(coverage_last_half)
        e_ads_avg = np.mean(e_ads_last_half)
        
        # 计算解吸附速率
        desorption_rate = calculate_desorption_rate(data['time'], data['coverage'])
        
        # 压力转换为log10(p/1atm)
        pressure_log10 = pressure_to_log10(pressure)
        
        statistics.append({
            'folder': folder,
            'temperature': temperature,
            'pressure': pressure,
            'pressure_log10': pressure_log10,
            'coverage_avg': coverage_avg,
            'e_ads_avg': e_ads_avg,
            'desorption_rate': desorption_rate
        })
    
    return statistics

def create_combined_plots(folder_data, statistics):
    """创建包含3个子图的组合图，使用新的布局"""
    
    # 设置Nature风格
    set_nature_style()
    
    # 创建一个更紧凑的布局
    fig = plt.figure(figsize=(36, 26))
    
    # 使用GridSpec创建布局
    gs = gridspec.GridSpec(2, 2, figure=fig, hspace=0.35, wspace=0.25,
                          height_ratios=[1, 1])
    
    # 第一个子图占据整个第一行（两列）
    ax1 = fig.add_subplot(gs[0, :])
    
    # 第二行的两个子图
    ax2 = fig.add_subplot(gs[1, 0])  # 温度倒数-性能关系图
    ax3 = fig.add_subplot(gs[1, 1])  # 覆盖度-吸附能散点图
    
    # 子图1：时间-吸附能关系图（横占两列）
    plot_time_adsorption_energy_subplot(ax1, folder_data)
    
    # 子图2：1000/T-性能关系图（双Y轴版本）
    plot_temperature_performance_dual_y_axis(ax2, statistics)
    
    # 子图3：覆盖度-吸附能散点图
    plot_coverage_adsorption_scatter_subplot(ax3, statistics)
    
    return fig

def plot_time_adsorption_energy_subplot(ax, folder_data):
    """绘制时间-单个氧原子吸附能关系图（子图）"""
    
    # 获取所有唯一的温度和压强，并排序
    temperatures = sorted(list(set([item['temperature'] for item in folder_data])))
    pressures = sorted(list(set([item['pressure'] for item in folder_data])), 
                      key=extract_pressure_value, reverse=True)
    
    # 为每个温度分配颜色
    temp_colors = {}
    for i, temp in enumerate(temperatures):
        temp_colors[temp] = nature_colors[i % len(nature_colors)]
    
    # 为每个压强分配线型
    pressure_styles = {}
    for i, pressure in enumerate(pressures):
        pressure_styles[pressure] = line_styles[i % len(line_styles)]
    
    # 重新排序folder_data
    folder_data_sorted = []
    for temp in temperatures:
        temp_data = [item for item in folder_data if item['temperature'] == temp]
        temp_data.sort(key=lambda x: extract_pressure_value(x['pressure']), reverse=True)
        folder_data_sorted.extend(temp_data)
    
    # 绘制每个数据集
    for item in folder_data_sorted:
        data = read_adsorption_data(item['data_file'])
        
        if data is None:
            continue
        
        time = data['time']
        e_ads_per_o = data['e_ads_per_o']
        
        # 获取颜色和线型
        color = temp_colors[item['temperature']]
        linestyle = pressure_styles[item['pressure']]
        
        # 设置标签
        label = f"{item['temperature']}K, {item['pressure']}"
        
        # 绘制线条
        ax.plot(time, e_ads_per_o, color=color, linestyle=linestyle, 
                linewidth=3.0, label=label, alpha=0.85)
    
    # 设置轴标签
    ax.set_xlabel('Time (ps)', fontsize=32, fontweight='bold')
    ax.set_ylabel('Adsorption Energy per O Atom (eV)', fontsize=32, fontweight='bold')
    ax.set_title('(a) Time vs Adsorption Energy per O Atom', fontweight='bold', fontsize=34)
    
    # 设置刻度标签大小
    ax.tick_params(axis='both', labelsize=26, width=2.5, length=8)
    
    # 创建图例并放在右下角，4列，以适应两列布局
    legend_labels = []
    legend_handles = []
    
    for temp in temperatures:
        temp_items = [item for item in folder_data_sorted if item['temperature'] == temp]
        for item in temp_items:
            label = f"{item['temperature']}K, {item['pressure']}"
            color = temp_colors[item['temperature']]
            linestyle = pressure_styles[item['pressure']]
            
            line = plt.Line2D([0], [0], color=color, linestyle=linestyle, 
                             linewidth=3.0, alpha=0.85)
            legend_handles.append(line)
            legend_labels.append(label)
    
    # 图例放在右下角，4列（从6列改为4列）
    legend = ax.legend(legend_handles, legend_labels, 
                      loc='lower right', 
                      fontsize=22,
                      frameon=True, fancybox=False, shadow=False, 
                      framealpha=0.95, edgecolor='black',
                      ncol=6, columnspacing=0.8, handlelength=1.2,
                      handletextpad=0.8)
    
    legend.get_frame().set_linewidth(2.0)

def plot_temperature_performance_dual_y_axis(ax, statistics):
    """绘制1000/T-性能关系图（双Y轴版本）"""
    
    # 获取唯一的压力，按数值排序
    pressures = sorted(list(set([item['pressure'] for item in statistics])), 
                      key=extract_pressure_value, reverse=True)
    
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
        pressure_data = [item for item in statistics if item['pressure'] == pressure]
        pressure_data.sort(key=lambda x: x['temperature'])
        
        if len(pressure_data) < 2:
            continue
            
        temperatures = [item['temperature'] for item in pressure_data]
        e_ads = [item['e_ads_avg'] for item in pressure_data]
        inverse_temps = [1000.0/temp for temp in temperatures]
        
        # 绘制数据点（散点，实心方形）
        ax.scatter(inverse_temps, e_ads, 
                   color=pressure_colors[pressure], 
                   marker='s',  # 实心方形
                   s=100,       # 散点大小
                   alpha=0.85,
                   label=f'{pressure} (E)')
        
        # 线性拟合
        if len(inverse_temps) >= 2:
            slope, intercept, r_value, p_value, std_err = linregress(inverse_temps, e_ads)
            fit_x = np.array([min(inverse_temps), max(inverse_temps)])
            fit_y = slope * fit_x + intercept
            
            # 绘制拟合线（虚线）
            ax.plot(fit_x, fit_y, '--', 
                   color=pressure_colors[pressure], 
                   linewidth=2.0,
                   alpha=0.7)
            
            # 保存拟合信息
            energy_fits.append({
                'pressure': pressure,
                'color': pressure_colors[pressure],
                'slope': slope,
                'intercept': intercept,
                'left_x': fit_x[0],  # 拟合线左端点
                'left_y': fit_y[0],  # 拟合线左端点的y值
                'right_x': fit_x[1],
                'right_y': fit_y[1]
            })
    
    # 绘制覆盖度（右Y轴）- 使用实心三角形
    for pressure in pressures:
        pressure_data = [item for item in statistics if item['pressure'] == pressure]
        pressure_data.sort(key=lambda x: x['temperature'])
        
        if len(pressure_data) < 2:
            continue
            
        temperatures = [item['temperature'] for item in pressure_data]
        coverages = [item['coverage_avg'] for item in pressure_data]
        inverse_temps = [1000.0/temp for temp in temperatures]
        
        # 绘制数据点（散点，实心三角形）
        ax2.scatter(inverse_temps, coverages, 
                    color=pressure_colors[pressure], 
                    marker='^',  # 实心三角形
                    s=100,       # 散点大小
                    alpha=0.85,
                    label=f'{pressure} (C)')
        
        # 线性拟合
        if len(inverse_temps) >= 2:
            slope, intercept, r_value, p_value, std_err = linregress(inverse_temps, coverages)
            fit_x = np.array([min(inverse_temps), max(inverse_temps)])
            fit_y = slope * fit_x + intercept
            
            # 绘制拟合线（虚线）
            ax2.plot(fit_x, fit_y, '--', 
                    color=pressure_colors[pressure], 
                    linewidth=2.0,
                    alpha=0.7)
            
            # 保存拟合信息
            coverage_fits.append({
                'pressure': pressure,
                'color': pressure_colors[pressure],
                'slope': slope,
                'intercept': intercept,
                'left_x': fit_x[0],
                'left_y': fit_y[0],
                'right_x': fit_x[1],  # 拟合线右端点
                'right_y': fit_y[1]  # 拟合线右端点的y值
            })
    
    # 设置轴范围
    ax.set_xlim(0.6, 2.6)  # 横坐标范围
    ax.set_ylim(2.0, 3.4)  # 能量范围
    ax2.set_ylim(1.0, 8.0) # 覆盖度范围
    
    # 准备分组的标注信息
    # 能量拟合按y值排序
    energy_fits.sort(key=lambda x: x['left_y'], reverse=True)
    # 覆盖度拟合按y值排序
    coverage_fits.sort(key=lambda x: x['left_y'], reverse=True)
    
    # 在图的左侧内部添加能量拟合方程
    x_position = 0.7  # 在图内左侧的x坐标
    y_spacing = 0.045  # 减小垂直间距（相对于能量轴范围）
    energy_range = ax.get_ylim()[1] - ax.get_ylim()[0]
    
    # 从图的上部开始标注能量方程
    start_y_energy = ax.get_ylim()[1] - 0.05 * energy_range  # 从顶部稍微往下一点开始
    
    for i, fit in enumerate(energy_fits):
        equation = f'E: y = {fit["slope"]:.2f}x + {fit["intercept"]:.2f}'
        # 计算标注位置
        y_pos = start_y_energy - i * y_spacing * energy_range
        
        # 添加标注
        ax.text(x_position, y_pos, equation,
                fontsize=13,  # 稍微减小字体
                color=fit['color'],
                ha='left',
                va='center',
                transform=ax.transData,
                bbox=dict(boxstyle='round,pad=0.2',  # 减小内边距
                         facecolor='white', 
                         edgecolor=fit['color'],
                         alpha=0.9,
                         linewidth=1.2))
    
    # 在能量方程下方添加覆盖度拟合方程
    # 计算能量方程组的底部位置
    energy_bottom = start_y_energy - len(energy_fits) * y_spacing * energy_range
    start_y_coverage = energy_bottom - 0.05 * energy_range  # 留一点间隔
    
    for i, fit in enumerate(coverage_fits):
        equation = f'C: y = {fit["slope"]:.2f}x + {fit["intercept"]:.2f}'
        # 计算标注位置
        y_pos = start_y_coverage - i * y_spacing * energy_range
        
        # 添加标注
        ax.text(x_position, y_pos, equation,
                fontsize=13,  # 稍微减小字体
                color=fit['color'],
                ha='left',
                va='center',
                transform=ax.transData,
                bbox=dict(boxstyle='round,pad=0.2',  # 减小内边距
                         facecolor='white', 
                         edgecolor=fit['color'],
                         alpha=0.9,
                         linewidth=1.2))
    
    # 设置轴标签
    ax.set_xlabel('1000/T (K$^{-1}$)', fontsize=32, fontweight='bold')
    ax.set_ylabel('Adsorption Energy per O (eV)', fontsize=32, fontweight='bold', color='black')
    ax2.set_ylabel('Coverage (atom/nm$^{2}$)', fontsize=32, fontweight='bold', color='black')
    ax.set_title('(b) Temperature Dependence', fontweight='bold', fontsize=34)
    
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
        legend_elements.append(plt.Line2D([0], [0], color=pressure_colors[pressure], 
                                        linestyle='none', marker='s', markersize=10,
                                        label=f'{pressure} Energy'))
        # 添加覆盖度散点（实心三角形）
        legend_elements.append(plt.Line2D([0], [0], color=pressure_colors[pressure], 
                                        linestyle='none', marker='^', markersize=10,
                                        label=f'{pressure} Coverage'))
    
    # 创建图例，放在图内右下角
    legend = ax.legend(handles=legend_elements, 
                      loc='lower right',  # 右下角
                      fontsize=20,
                      frameon=True, 
                      fancybox=False, 
                      shadow=False, 
                      framealpha=0.95, 
                      edgecolor='black',
                      ncol=1,  # 单列显示
                      columnspacing=1.0,  # 列间距
                      handletextpad=0.5)  # 图标与文字间距
    legend.get_frame().set_linewidth(2.0)





def plot_coverage_adsorption_scatter_subplot(ax, statistics):
    """绘制覆盖度-吸附能散点图（子图），包含线性拟合和离散程度分析"""
    
    # 提取数据
    coverages = np.array([item['coverage_avg'] for item in statistics])
    e_ads_values = np.array([item['e_ads_avg'] for item in statistics])
    temperatures = [item['temperature'] for item in statistics]
    
    # 为不同温度分配颜色
    temp_unique = sorted(list(set(temperatures)))
    temp_colors = {}
    for i, temp in enumerate(temp_unique):
        temp_colors[temp] = nature_colors[i % len(nature_colors)]
    
    # 计算每个温度的统计数据
    temp_stats = {}
    for temp in temp_unique:
        temp_data = [item for item in statistics if item['temperature'] == temp]
        temp_coverages = np.array([item['coverage_avg'] for item in temp_data])
        temp_e_ads = np.array([item['e_ads_avg'] for item in temp_data])
        
        # 计算均值和标准差
        mean_coverage = np.mean(temp_coverages)
        mean_e_ads = np.mean(temp_e_ads)
        std_e_ads = np.std(temp_e_ads)
        
        temp_stats[temp] = {
            'coverages': temp_coverages,
            'e_ads': temp_e_ads,
            'mean_coverage': mean_coverage,
            'mean_e_ads': mean_e_ads,
            'std_e_ads': std_e_ads
        }
        
        # 绘制散点图
        ax.scatter(temp_coverages, temp_e_ads, 
                  color=temp_colors[temp], s=150, alpha=0.7, 
                  edgecolors='black', linewidths=1.5)
        
        # 添加误差条
        ax.errorbar(mean_coverage, mean_e_ads, yerr=std_e_ads, 
                   fmt='none', color=temp_colors[temp], capsize=8, 
                   capthick=2.5, alpha=0.6)
    
    # 进行线性拟合
    slope, intercept, r_value, p_value, std_err = linregress(coverages, e_ads_values)
    r_squared = r_value**2
    
    # 计算残差和拟合优度指标
    predicted = slope * coverages + intercept
    residuals = e_ads_values - predicted
    
    # 计算各种离散度指标
    rmse = np.sqrt(np.mean(residuals**2))
    mae = np.mean(np.abs(residuals))
    std_residuals = np.std(residuals)
    
    # 计算整体数据的离散度
    overall_std = np.std(e_ads_values)
    overall_cv = overall_std / np.mean(e_ads_values) * 100
    
    # 创建拟合线
    coverage_range = np.linspace(coverages.min(), coverages.max(), 100)
    fit_line = slope * coverage_range + intercept
    
    # 绘制拟合线
    ax.plot(coverage_range, fit_line, 'k--', linewidth=2.5, alpha=0.8)
    
    # 添加置信区间
    n = len(coverages)
    t_val = 1.96
    
    # 计算置信区间
    se_y_est = np.sqrt(np.sum(residuals**2) / (n - 2))
    mean_x = np.mean(coverages)
    
    confidence_interval = []
    for x in coverage_range:
        se_pred = se_y_est * np.sqrt(1/n + (x - mean_x)**2 / np.sum((coverages - mean_x)**2))
        confidence_interval.append(t_val * se_pred)
    
    confidence_interval = np.array(confidence_interval)
    
    # 绘制置信区间
    ax.fill_between(coverage_range, 
                   fit_line - confidence_interval, 
                   fit_line + confidence_interval, 
                   alpha=0.2, color='gray')
    
    # 在图上添加拟合信息和离散度分析
    fit_text = (f'Linear fit: y = {slope:.3f}x + {intercept:.3f}\n'
                f'$R^2$ = {r_squared:.3f}, SE = {std_err:.3f}\n'
                f'RMSE = {rmse:.3f}, MAE = {mae:.3f}\n'
                f'Overall STD = {overall_std:.3f}\n'
                f'CV = {overall_cv:.1f}%')
    
    ax.text(0.05, 0.95, fit_text, transform=ax.transAxes, fontsize=20,
            verticalalignment='top', 
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.9))
    
    # 添加残差子图
    from mpl_toolkits.axes_grid1.inset_locator import inset_axes
    axins = inset_axes(ax, width="35%", height="35%", loc='lower right', 
                      bbox_to_anchor=(0, 0.08, 1, 1), bbox_transform=ax.transAxes)
    
    # 绘制残差散点图
    for temp in temp_unique:
        temp_coverages = temp_stats[temp]['coverages']
        temp_e_ads = temp_stats[temp]['e_ads']
        temp_predicted = slope * temp_coverages + intercept
        temp_residuals = temp_e_ads - temp_predicted
        
        axins.scatter(temp_coverages, temp_residuals, 
                     color=temp_colors[temp], s=30, alpha=0.7)
    
    axins.axhline(y=0, color='k', linestyle='-', linewidth=1)
    axins.axhline(y=rmse, color='r', linestyle='--', linewidth=1, alpha=0.5)
    axins.axhline(y=-rmse, color='r', linestyle='--', linewidth=1, alpha=0.5)
    
    axins.set_xlabel('Coverage', fontsize=16)
    axins.set_ylabel('Residuals', fontsize=16)
    axins.tick_params(labelsize=14)
    axins.grid(True, alpha=0.3)
    
    # 调整y轴范围
    y_range = e_ads_values.max() - e_ads_values.min()
    y_margin_up = y_range * 2.0
    y_margin_down = y_range * 3.0
    ax.set_ylim(e_ads_values.min() - y_margin_down, e_ads_values.max() + y_margin_up)
    
    # 设置轴标签
    ax.set_xlabel('Coverage (atom/nm$^{2}$)', fontsize=32, fontweight='bold')
    ax.set_ylabel('Adsorption Energy per O (eV)', fontsize=32, fontweight='bold')
    ax.set_title('(c) Coverage vs Adsorption Energy', fontweight='bold', fontsize=34)
    ax.tick_params(axis='both', labelsize=26, width=2.5, length=8)
    
    # 创建温度图例
    temp_handles = []
    temp_labels = []
    for temp in temp_unique:
        temp_handles.append(plt.scatter([], [], color=temp_colors[temp], s=150, 
                                       edgecolors='black', linewidths=1.5))
        temp_labels.append(f'{temp}K')
    
    temp_legend = ax.legend(temp_handles, temp_labels, loc='lower left', 
                           fontsize=24, frameon=True, fancybox=False, 
                           shadow=False, framealpha=0.95, edgecolor='black')
    temp_legend.get_frame().set_linewidth(2.0)
    temp_legend.set_title('Temperature', prop={'size': 24, 'weight': 'bold'})
    
    # 保存第一个图例
    ax.add_artist(temp_legend)
    
    # 创建拟合线和置信区间的图例
    from matplotlib.lines import Line2D
    from matplotlib.patches import Patch
    
    legend_elements = [
        Line2D([0], [0], color='k', linewidth=2.5, linestyle='--', 
               label='Linear fit'),
        Patch(facecolor='gray', alpha=0.2, edgecolor='none', 
              label='95% CI')
    ]
    
    fit_legend = ax.legend(handles=legend_elements, loc='upper right', 
                          fontsize=24, frameon=True, fancybox=False, 
                          shadow=False, framealpha=0.95, edgecolor='black')
    fit_legend.get_frame().set_linewidth(2.0)
    
    # 添加网格
    ax.grid(True, alpha=0.3, linestyle='--')

def save_data_to_dat_files(folder_data, statistics, output_dir):
    """将数据保存为dat文件"""
    
    # 保存时间序列数据
    time_series_file = os.path.join(output_dir, "time_series_data.dat")
    with open(time_series_file, 'w') as f:
        f.write("# Time series data for all conditions\n")
        f.write("# Note: Adsorption energy has been multiplied by -1\n")
        f.write("# Folder\tTemperature(K)\tPressure\tTime(ps)\tCoverage(atom/nm$^{2}$)\tE_ads_per_O(eV)\n")
        
        for item in folder_data:
            folder = item['folder']
            temperature = item['temperature']
            pressure = item['pressure']
            
            data = read_adsorption_data(item['data_file'])
            if data is None:
                continue
            
            for i in range(len(data['time'])):
                f.write(f"{folder}\t{temperature}\t{pressure}\t{data['time'][i]:.4f}\t"
                       f"{data['coverage'][i]:.6f}\t{data['e_ads_per_o'][i]:.6f}\n")
    
    print(f"Time series data saved to: {time_series_file}")
    
    # 保存统计数据
    statistics_file = os.path.join(output_dir, "statistics_data.dat")
    with open(statistics_file, 'w') as f:
        f.write("# Statistical summary data\n")
        f.write("# Note: Adsorption energy has been multiplied by -1\n")
        f.write("# Folder\tTemp(K)\tPressure\tlog10(P/1atm)\t1000/T(K^-1)\tCoverage_avg(atom/nm²)\tE_ads_avg(eV)\tDesorption_rate(atom/(nm²·ps))\n")
        
        for item in sorted(statistics, key=lambda x: (x['temperature'], x['pressure_log10'])):
            inverse_temp = 1000.0 / item['temperature']
            f.write(f"{item['folder']}\t{item['temperature']}\t{item['pressure']}\t"
                   f"{item['pressure_log10']:.4f}\t{inverse_temp:.4f}\t"
                   f"{item['coverage_avg']:.6f}\t{item['e_ads_avg']:.6f}\t{item['desorption_rate']:.6f}\n")
    
    print(f"Statistics data saved to: {statistics_file}")

def save_statistics_to_file(statistics, output_dir):
    """将统计数据保存到文件"""
    filename = os.path.join(output_dir, "statistics_summary.txt")
    
    with open(filename, 'w') as f:
        f.write("RMD_Relax Analysis Statistics Summary\n")
        f.write("="*60 + "\n")
        f.write("Note: Adsorption energy has been multiplied by -1\n")
        f.write("="*60 + "\n\n")
        f.write("Folder\tTemp(K)\tPressure\tlog10(P/1atm)\t1000/T(K^-1)\tCoverage(atom/nm²)\tE_ads(eV)\tDesorption_rate(atom/(nm²·ps))\n")

        f.write("-"*120 + "\n")
        
        for item in sorted(statistics, key=lambda x: (x['temperature'], x['pressure_log10'])):
            inverse_temp = 1000.0 / item['temperature']
            f.write(f"{item['folder']}\t{item['temperature']}\t{item['pressure']}\t"
                   f"{item['pressure_log10']:.2f}\t{inverse_temp:.4f}\t"
                   f"{item['coverage_avg']:.4f}\t{item['e_ads_avg']:.4f}\t{item['desorption_rate']:.6f}\n")
    
    print(f"Statistics saved to: {filename}")

def main():
    print("\n" + "="*80)
    print("COMBINED RMD_RELAX ANALYSIS")
    print("="*80 + "\n")
    
    # 寻找所有RMD_Relax文件夹
    print("Searching for RMD_Relax folders...")
    folder_data = find_rmd_relax_folders()
    
    if not folder_data:
        print("No valid RMD_Relax folders found!")
        print("Please ensure folders follow the naming pattern: RMD_Relax_<temperature>k_<pressure>")
        return
    
    print(f"\nFound {len(folder_data)} valid folders")
    
    # 创建输出文件夹
    output_dir = "Combine_RMD_Relax_plot"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Created output directory: {output_dir}")
    
    # 计算统计数据
    print("\nCalculating statistics...")
    statistics = calculate_statistics(folder_data)
    
    # 保存统计数据到文件
    save_statistics_to_file(statistics, output_dir)
    
    # 保存数据到dat文件
    print("\nSaving data to dat files...")
    save_data_to_dat_files(folder_data, statistics, output_dir)
    
    # 创建组合图
    print("\nCreating combined plots...")
    fig = create_combined_plots(folder_data, statistics)
    
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
    pressures = sorted(list(set([item['pressure'] for item in folder_data])), 
                      key=extract_pressure_value, reverse=True)
    print(f"Number of datasets: {len(folder_data)}")
    print(f"Temperature range: {min(temperatures)} - {max(temperatures)} K")
    print(f"Pressure conditions (descending): {', '.join(pressures)}")
    print(f"Output saved to: {output_dir}/")
    print("NOTE: All adsorption energies have been multiplied by -1")
    print("Coverage unit: atom/nm² (converted from atom/Å² by multiplying by 100)")
    print("Statistics include last 50% averages for coverage and adsorption energy")
    print("Desorption rates calculated from coverage derivatives")
    
    print("\nPlots generated:")
    print("(a) Time vs Adsorption Energy per O Atom - spans 2 columns")
    print("(b) 1000/T vs Performance (dual Y-axis with linear fits)")
    print("(c) Coverage vs Adsorption Energy scatter plot")
    
    print("="*80)
    print("Combined analysis completed successfully!")

if __name__ == "__main__":
    main()
