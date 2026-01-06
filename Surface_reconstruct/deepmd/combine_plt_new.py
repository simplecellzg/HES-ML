import os
import pandas as pd
import matplotlib.pyplot as plt
import re
import matplotlib
from matplotlib import font_manager
import sys

# 设置字体并显示进度
print("步骤 1/6: 正在设置字体...")
font_path = "/public1/home/sch9516/ZG/MTD_3_database_trained_post_result/MTD_3_database_2_surf_reconstruct_trained_post_lmp_bks_result/times-new-roman/times.ttf"

try:
    # 添加字体文件到字体管理器
    if os.path.exists(font_path):
        font_manager.fontManager.addfont(font_path)
        plt.rcParams['font.family'] = 'Times New Roman'
        print("✓ 成功加载Times New Roman字体")
    else:
        print(f"⚠ 字体文件 {font_path} 不存在，使用备用字体")
        plt.rcParams['font.family'] = 'serif'
    
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
    print(f"⚠ 字体设置错误: {e}, 使用默认字体")
    plt.rcParams['font.family'] = 'serif'

# 创建图形
print("步骤 2/6: 创建新的图形...")
fig, ax = plt.subplots(figsize=(20, 10))
print("✓ 图形创建完成")

# 自定义排序函数
def sort_key(s):
    temperature_match = re.findall(r"(\d+\.?\d*)K", s)
    temperature = float(temperature_match[0]) if temperature_match else 0.0

    distance_match = re.findall(r"(\d+\.?\d*)A", s)
    distance = float(distance_match[0]) if distance_match else 0.0

    return (temperature, distance)

# 获取当前目录
current_dir = os.getcwd()
print(f"步骤 3/6: 当前工作目录: {current_dir}")

# 检查combine_plt目录是否存在
if not os.path.exists('combine_plt'):
    print("⚠ combine_plt目录不存在，将创建此目录")
    os.makedirs('combine_plt', exist_ok=True)
else:
    print("✓ combine_plt目录已存在")

# 处理每个colvar文件
print("步骤 4/6: 开始处理colvar文件...")
colvar_files = [f for f in os.listdir('combine_plt') if f.endswith('_colvar')]

if not colvar_files:
    print("⚠ 没有找到colvar文件，请确保combine_plt目录中有*_colvar文件")
    sys.exit(1)

print(f"✓ 找到 {len(colvar_files)} 个colvar文件")

# 按排序处理文件
sorted_files = sorted(colvar_files, key=sort_key)
print(f"处理的文件顺序: {', '.join(sorted_files[:5])}" + ("..." if len(sorted_files) > 5 else ""))

for i, colvar_file in enumerate(sorted_files):
    # 显示处理进度
    progress = (i + 1) / len(sorted_files) * 100
    print(f"处理文件 {i+1}/{len(sorted_files)} ({progress:.1f}%): {colvar_file}", end="\r")
    
    # 从colvar文件名提取文件夹名
    folder = colvar_file[:-7]  # 移除'_colvar'后缀
    
    # 读取colvar文件
    df = pd.read_csv(os.path.join('combine_plt', colvar_file), sep='\s+')
    
    # 使用第一列作为x，计算第3列到第18列的平均值作为y
    x = df.iloc[:, 0]
    y = df.iloc[:, 2:18].mean(axis=1)
    
    # 绘制数据，不使用图例
    ax.plot(x, y, 'o', markersize=1, markerfacecolor='none')

print("\n✓ 所有文件处理完成")

# 设置坐标轴标签
print("步骤 5/6: 设置图表属性...")
ax.set_xlabel('Time /ps', fontsize=36)
ax.set_ylabel('CV-Distance /Å', fontsize=36)

# 设置刻度参数
ax.tick_params(axis='both', which='major', labelsize=30)

# 设置坐标轴范围
ax.set_xlim(left=0, right=50)  # x轴从0开始
ax.set_ylim(bottom=1.4)  # y轴从1.4开始

# 移除网格
ax.grid(False)
print("✓ 图表属性设置完成")

# 保存图像
print("步骤 6/6: 保存图像...")
output_path = './combine_plt/combine_plt_new.png'
plt.savefig(output_path, bbox_inches='tight', dpi=300)
print(f"✓ 图像已保存到: {output_path}")

# 显示图像
print("图像处理完成，正在显示...")
plt.show()
