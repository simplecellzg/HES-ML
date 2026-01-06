import pandas as pd
import matplotlib.pyplot as plt
import re
import os
import matplotlib
from matplotlib import font_manager

def process_reaction(input_path, reaction_name, output_dir='./output'):
    # 定义文件夹缩写映射和显示名称
    folder_abbr = {
        'dft_PBE': 'PBE',
        'dp_20241109_clean_2': 'DeePMD',
        'lmp_2015': 'ReaxFF',
        'lmp_bks': 'BKS'
    }
    
    # 读取 CSV 文件
    df_raw = pd.read_csv(input_path)
    
    # 处理数据列
    df = pd.DataFrame()
    df['Frame'] = df_raw['Frame'].apply(lambda x: int(re.findall(r'\d+', x)[-1]) + 1)
    df['Source'] = df_raw['Source'].apply(
        lambda x: folder_abbr.get(x.split('/')[2], x.split('/')[2])
    )
    df['Energy (kcal/mol)'] = df_raw['Energy(kcal/mol)']
    
    # 转换为宽格式二维表
    table = df.pivot(index='Frame', columns='Source', values='Energy (kcal/mol)').sort_index()
    
    # 为reaction1进行特殊处理
    if 'reaction1' in reaction_name:
        table = table.iloc[::-1]
        new_indices = list(range(1, len(table) + 1))
        table.index = new_indices
    
    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)
    
    # 保存二维表到 CSV
    table_csv_path = f"{output_dir}/{reaction_name}_table.csv"
    table.to_csv(table_csv_path)
    print(f"二维表已保存到: {table_csv_path}")
    
    # 设置字体 - 修改部分开始
    font_path = "/public1/home/sch9516/ZG/MTD_3_database_trained_post_result/reaction_energy_diff/reaction_all/times-new-roman/times.ttf"
    
    try:
        # 添加字体文件到字体管理器
        if os.path.exists(font_path):
            font_manager.fontManager.addfont(font_path)
            plt.rcParams['font.family'] = 'Times New Roman'
            print("成功加载Times New Roman字体")
        else:
            print(f"字体文件 {font_path} 不存在，使用备用字体")
            plt.rcParams['font.family'] = 'serif'
        
        # 清除可能的字体权重设置（不再使用_rebuild）
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
    # 设置字体 - 修改部分结束
    
    # 绘图配置
    color_map = {
        'PBE': 'red',
        'DeePMD': 'blue',
        'ReaxFF': 'green',
        'BKS': 'purple'
    }
    
    # 创建图形
    plt.figure(figsize=(10, 6))
    for source in table.columns:
        plt.plot(
            table.index, 
            table[source], 
            marker='o', 
            label=source,
            color=color_map.get(source, 'black')
        )
    
    # 设置字体属性（修正后的写法）
    title_font = {'family': plt.rcParams['font.family'], 'size': 18, 'weight': 'bold'}
    axis_font = {'family': plt.rcParams['font.family'], 'size': 18}
    tick_font = {'family': plt.rcParams['font.family'], 'size': 15}
    
    if 'reaction1' in reaction_name:
        plt.title(f'Energy Comparison: {reaction_name} (Reversed Order)', **title_font)
    else:
        plt.title(f'Energy Comparison: {reaction_name}', **title_font)
        
    plt.xlabel('Frame', **axis_font)
    plt.ylabel('Energy (kcal/mol)', **axis_font)
    
    # 修正刻度字体设置
    plt.xticks(range(1, 8), fontsize=15)
    plt.yticks(fontsize=15)
    
    plt.legend(
        bbox_to_anchor=(1.05, 1),
        loc='upper left',
        frameon=True,
        prop={'family': plt.rcParams['font.family'], 'size': 15}
    )
    plt.grid(False)
    
    # 保存图像
    plot_png_path = f"{output_dir}/{reaction_name}_plot.png"
    plt.savefig(plot_png_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"图表已保存到: {plot_png_path}")

if __name__ == '__main__':
    base_dir = "/public1/home/sch9516/ZG/MTD_3_database_trained_post_result/reaction_energy_diff/reaction_all/diff_energies"
    for reaction_id in [1, 2, 3]:
        input_csv = f"{base_dir}/reaction{reaction_id}_diff_merged.csv"
        output_dir = "./output_reactions"
        process_reaction(input_csv, f"reaction{reaction_id}", output_dir)
    print("All reactions processed!")
