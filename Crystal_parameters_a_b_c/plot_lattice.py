import os
import re
import csv
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
from matplotlib import font_manager  # 添加这行导入


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
            plt.rcParams['mathtext.fontset'] = 'serif'
        
        # 清除可能的字体权重设置
        if 'roman' in matplotlib.font_manager.weight_dict:
            del matplotlib.font_manager.weight_dict['roman']
        
        # 重建字体缓存（兼容性写法）
        try:
            matplotlib.font_manager._rebuild()
        except AttributeError:
            # 对于新版本matplotlib，可能不需要rebuild
            pass
        
    except Exception as e:
        print(f"字体设置错误: {e}, 使用默认字体")
        plt.rcParams['font.family'] = 'serif'
        plt.rcParams['font.serif'] = ['Times New Roman', 'DejaVu Serif', 'SimSun']
        plt.rcParams['mathtext.fontset'] = 'serif'
        print("使用备用serif字体设置")


def extract_temp(folder_name):
    """从文件夹名提取温度数值（如500k → 500.0）"""
    match = re.match(r"^(\d+\.?\d*)[kK]$", folder_name)
    return float(match.group(1)) if match else None

def parse_abc(file_path):
    """解析abc_data文件（兼容格式变异）"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = [line.strip() for line in f.readlines()]

        # 模糊匹配关键行
        key_line_pattern = re.compile(r'晶体参数\s*最后1ps\s*平均.*[:：]')
        key_line_idx = None
        for idx, line in enumerate(lines):
            if key_line_pattern.search(line):
                key_line_idx = idx
                break
        if key_line_idx is None:
            print(f"文件 {file_path} 未找到关键行")
            return None, None, None

        # 提取参数a、b、c（允许参数行乱序）
        params = {}
        for line in lines[key_line_idx + 1 : key_line_idx + 4]:
            if 'a(Å)' in line:
                params['a'] = float(line.split(':')[-1].strip())
            elif 'b(Å)' in line:
                params['b'] = float(line.split(':')[-1].strip())
            elif 'c(Å)' in line:
                params['c'] = float(line.split(':')[-1].strip())
        if len(params) != 3:
            print(f"文件 {file_path} 参数缺失: {params}")
            return None, None, None
        return params['a'], params['b'], params['c']
    except Exception as e:
        print(f"解析错误 {file_path}: {str(e)}")
        return None, None, None

def collect_data(main_dirs, output_csv):
    """收集数据并标注来源目录（仅遍历一级子目录）"""
    data = []
    source_map = {
        'dp_20241109_clean_2': 'DeePMD',
        'lmp_2015': 'ReaxFF',
        'dft_PBE': 'PBE',
        'lmp_bks': 'BKS'
    }
    for main_dir in main_dirs:
        if not os.path.isdir(main_dir):
            print(f"警告：主目录 {main_dir} 不存在，跳过")
            continue
        # 获取来源标签
        main_dir_name = os.path.basename(main_dir)
        source = source_map.get(main_dir_name, 'unknown')
        # 遍历主目录的直接子文件夹
        for entry in os.listdir(main_dir):
            subdir = os.path.join(main_dir, entry)
            if not os.path.isdir(subdir):
                continue  # 跳过文件
            # 检查子目录中是否存在abc_data文件
            abc_file = os.path.join(subdir, 'abc_data')
            if not os.path.isfile(abc_file):
                continue  # 跳过无目标文件的子目录
            # 从子目录名提取温度
            temp = extract_temp(entry)
            if not temp:
                print(f"无效温度目录: {subdir}（名称无法解析为温度）")
                continue
            # 解析abc_data文件
            a, b, c = parse_abc(abc_file)
            if a and b and c:
                data.append([temp, a, b, c, source])
    # 保存到CSV
    with open(output_csv, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['temperature', 'a', 'b', 'c', 'source'])
        writer.writerows(sorted(data, key=lambda x: (x[-1], x[0])))

def plot_combined_chart(csv_file):
    """绘制晶体参数图，确保使用Times New Roman字体"""
    # 设置字体（必须在创建图形之前）
    set_custom_font()
    
    # 定义字体属性
    title_font = {'family': plt.rcParams['font.family'], 'size': 30, 'weight': 'bold'}
    axis_font = {'family': plt.rcParams['font.family'], 'size': 30}
    legend_font = {'family': plt.rcParams['font.family'], 'size': 20}
    tick_font = {'family': plt.rcParams['font.family'], 'size': 25}
    
    df = pd.read_csv(csv_file)
    # 配置样式
    source_color = {
        'PBE': 'red',
        'DeePMD': 'blue',
        'ReaxFF': 'green',
        'BKS': 'orange'
    }
    param_style = {
        'a': {'ls': '-', 'marker': 'o'},
        'b': {'ls': '--', 'marker': 's'},
        'c': {'ls': ':', 'marker': '^'}
    }
    
    # 创建图形（必须在字体设置之后）
    plt.figure(figsize=(12, 7))
    
    # 绘制数据
    for source in df['source'].unique():
        df_source = df[df['source'] == source].sort_values('temperature')
        color = source_color[source]
        for param in ['a', 'b', 'c']:
            plt.plot(
                df_source['temperature'], df_source[param],
                color=color,
                linestyle=param_style[param]['ls'],
                marker=param_style[param]['marker'],
                markersize=12,
                linewidth=4,
                label=f'{source} {param}'
            )
    
    # 设置图表元素（显式指定字体）
    plt.title('Lattice Parameters vs Temperature', fontdict=title_font)
    plt.xlabel('Temperature /K', fontdict=axis_font)
    
    # 修改这行以确保Å符号也使用Times New Roman
    plt.ylabel('Lattice Parameter /Å', fontdict=axis_font)  # 不使用mathtext模式
    # 或者保留mathtext但确保使用正确字体:
    # plt.ylabel(r'Lattice Parameter /$\AA$', fontdict=axis_font)
    
    # 设置刻度字体
    plt.xticks(fontsize=25)
    plt.yticks(fontsize=25)
    
    # 设置图例（显式指定字体）
    legend = plt.legend(
        bbox_to_anchor=(1.05, 1),
        loc='upper left',
        frameon=True,
        prop=legend_font
    )
    
    # 确保图例文本使用正确字体
    for text in legend.get_texts():
        text.set_fontfamily(plt.rcParams['font.family'])
        text.set_fontsize(20)
    
    plt.grid(False)
    plt.tight_layout()
    
    # 保存前再次验证字体
    print("最终使用的字体:", plt.rcParams['font.family'])
    
    # 保存图像（建议使用PDF格式保留字体嵌入）
    output_file = 'combined_lattice_parameters.pdf'
    plt.savefig(output_file, dpi=300, bbox_inches='tight', format='pdf')
    print(f"图表已保存为 {output_file} (推荐PDF格式保留字体)")
    
    # 同时保存PNG版本
    png_file = 'combined_lattice_parameters_big_font.png'
    plt.savefig(png_file, dpi=300, bbox_inches='tight')
    print(f"图表已保存为 {png_file}")
    
    plt.close()

if __name__ == "__main__":
    main_dirs = ['dp_20241109_clean_2', 'lmp_2015', 'dft_PBE', 'lmp_bks']
    output_csv = 'summary.csv'
    collect_data(main_dirs, output_csv)
    plot_combined_chart(output_csv)
