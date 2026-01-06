import os
import shutil
import pandas as pd

#base_path = "/public1/home/sch9516/ZG/MTD_3_database_trained_post_result/reaction_energy_diff/reaction_all"
base_path = "./"
reactions = ['reaction1', 'reaction2', 'reaction3']

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

if __name__ == "__main__":
    process_files()
