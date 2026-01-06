import os
import pandas as pd
import matplotlib.pyplot as plt
import re
import shutil

# Base directory for the project
base_path = "/public1/home/sch9516/ZG/MTD_3_database_trained_post_result/reaction_energy_diff/reaction_all"
reactions = ['reaction1', 'reaction2', 'reaction3']

# 定义文件夹缩写映射 (updated to include lmp_bks)
folder_abbr = {
    'dft_PBE': 'pbe',
    'dp_20241109_clean_2': 'dp',
    'lmp_2015': 'lmp',
    'lmp_bks': 'lmp_bks'  # Added new data source
}

# Color mappings for visualization
color_map = {
    'pbe': 'red',      # 红色
    'dp': 'blue',      # 蓝色
    'lmp': 'green',    # 绿色
    'lmp_bks': 'purple'  # Added new color for lmp_bks
}

def process_energy_file(src_path, reaction_name):
    """增强型文件处理方法"""
    try:
        # 使用正则表达式分隔符读取
        df = pd.read_csv(src_path, sep=r'\s{2,}', engine='python')  # 两个以上空格作为分隔符
        df.columns = df.columns.str.strip()
        
        # 列名校验
        if not df.columns.tolist() == ['Frame', 'Energy(kcal/mol)']:
            print(f"发现非常规列名{df.columns}在文件{src_path}")
            return None, None

        # 为reaction1进行特殊处理
        if reaction_name == 'reaction1':
            # 将数据帧倒序排列
            df = df.iloc[::-1].reset_index(drop=True)
            # 以第一个能量为基准（之前是最后一个，但现在已经倒序了）
            base_energy = df.iloc[0]['Energy(kcal/mol)']
        else:
            # 其他反应以第一个能量为基准
            base_energy = df.iloc[0]['Energy(kcal/mol)']
            
        df['Source'] = src_path  # 添加源文件路径记录
        df_diff = df.copy()
        df_diff['Energy(kcal/mol)'] = df_diff['Energy(kcal/mol)'] - base_energy
        
        return df, df_diff

    except Exception as e:
        print(f"文件处理失败: {src_path} | 错误: {str(e)}")
        return None, None

def process_files():
    collected_dir = os.path.join(base_path, 'collected_energies')
    diff_dir = os.path.join(base_path, 'diff_energies')
    os.makedirs(collected_dir, exist_ok=True)
    os.makedirs(diff_dir, exist_ok=True)

    error_log_path = os.path.join(base_path, 'error_analysis.log')
    with open(error_log_path, 'w') as log_file:
        log_file.write("Error Log - 详细字段解析:\n")

    for reaction in reactions:
        reaction_path = os.path.join(base_path, reaction)
        with open(error_log_path, 'a') as log_file:
            log_file.write(f"\n==== {reaction} ====\n")

        # 初始化数据收集器
        collected_dfs = []
        diff_dfs = []

        for root, _, files in os.walk(reaction_path):
            if 'energies.csv' not in files:
                continue

            src_file = os.path.join(root, 'energies.csv')
            relative_path = os.path.relpath(root, reaction_path)

            # 处理文件
            df_collect, df_diff = process_energy_file(src_file, reaction)
            
            # 处理失败时记录原始内容
            if df_collect is None:
                with open(error_log_path, 'a') as log_file:
                    with open(src_file, 'r') as f:
                        content = f.read(200)  # 记录前200字符分析
                        log_file.write(f"失败文件内容片段:\n{content}\n{'='*40}\n")
                continue

            # 保存文件
            for df, target_dir, prefix in zip([df_collect, df_diff],
                                           [collected_dir, diff_dir],
                                           ['orig', 'diff']):
                save_path = os.path.join(
                    target_dir, reaction, f"{prefix}_{os.path.basename(root)}.csv")
                os.makedirs(os.path.dirname(save_path), exist_ok=True)
                df.to_csv(save_path, index=False)

            # 收集数据
            collected_dfs.append(df_collect)
            diff_dfs.append(df_diff)

        # 生成合并文件
        if collected_dfs:
            pd.concat(collected_dfs).to_csv(
                os.path.join(collected_dir, f"{reaction}_merged.csv"), index=False)
            
        if diff_dfs:
            pd.concat(diff_dfs).to_csv(
                os.path.join(diff_dir, f"{reaction}_diff_merged.csv"), index=False)

def process_reaction(input_path, reaction_name, output_dir='./output'):
    """处理反应数据并生成可视化"""
    # 读取 CSV 文件（确保路径存在）
    df_raw = pd.read_csv(input_path)
    
    # 处理数据列（应用文件夹缩写）
    df = pd.DataFrame()
    # 修改此行：将提取的帧号加1，使得Frame从1开始
    df['Frame'] = df_raw['Frame'].apply(lambda x: int(re.findall(r'\d+', x)[-1]) + 1)
    
    # 处理Source列，应用文件夹缩写
    df['Source'] = df_raw['Source'].apply(
        lambda x: folder_abbr.get(x.split('/')[2], x.split('/')[2])
    )
    df['Energy (kcal/mol)'] = df_raw['Energy(kcal/mol)']
    
    # 检查并处理重复项 - 对于相同Frame和Source的行，取平均值
    print(f"处理前的记录数: {len(df)}")
    df_grouped = df.groupby(['Frame', 'Source'])['Energy (kcal/mol)'].mean().reset_index()
    print(f"处理后的记录数: {len(df_grouped)}")
    
    # 检查是否还有重复项
    duplicates = df_grouped.duplicated(subset=['Frame', 'Source'], keep=False)
    if duplicates.any():
        print(f"警告: 仍然存在 {duplicates.sum()} 个重复条目")
        print(df_grouped[duplicates])
    
    # 转换为宽格式二维表
    table = df_grouped.pivot(index='Frame', columns='Source', values='Energy (kcal/mol)').sort_index()
    
    # 为reaction1进行特殊处理：倒序排列
    if 'reaction1' in reaction_name:
        table = table.iloc[::-1]  # 倒序排列行
        # 重新为索引赋值，保持从1开始递增
        new_indices = list(range(1, len(table) + 1))
        table.index = new_indices
    
    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)
    
    # 保存二维表到 CSV
    table_csv_path = f"{output_dir}/{reaction_name}_table.csv"
    table.to_csv(table_csv_path)
    print(f"二维表已保存到: {table_csv_path}")
    
    # 绘图并保存为 PNG
    plt.figure(figsize=(10, 6))
    for source in table.columns:
        plt.plot(
            table.index, 
            table[source], 
            marker='o', 
            label=source,
            color=color_map.get(source, 'black')  # 用预定义颜色，默认黑色兜底
        )
    
    # 设置标题，根据反应类型调整
    if 'reaction1' in reaction_name:
        plt.title(f'Energy Comparison: {reaction_name} (Reversed Order)', fontsize=18)
    else:
        plt.title(f'Energy Comparison: {reaction_name}', fontsize=18)
        
    plt.xlabel('Frame', fontsize=18)
    plt.ylabel('Energy (kcal/mol)', fontsize=18)
    # X轴刻度范围
    plt.xticks(range(1, 8), fontsize=15)
    plt.yticks(fontsize=15)
    plt.legend(
        bbox_to_anchor=(1.05, 1),
        loc='upper left',
        frameon=True,
        fontsize=15
        )
    plt.grid(False)
    plot_png_path = f"{output_dir}/{reaction_name}_plot.png"
    plt.savefig(plot_png_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"图表已保存到: {plot_png_path}")

if __name__ == '__main__':
    # 第一步：收集和处理所有反应数据，包括lmp_bks
    process_files()
    
    # 第二步：为每个反应生成可视化
    diff_dir = os.path.join(base_path, 'diff_energies')
    output_dir = "./output_reactions"
    
    for reaction_id in [1, 2, 3]:
        reaction_name = f"reaction{reaction_id}"
        input_csv = os.path.join(diff_dir, f"{reaction_name}_diff_merged.csv")
        process_reaction(input_csv, reaction_name, output_dir)
    
    print("All reactions processed and visualized!")
