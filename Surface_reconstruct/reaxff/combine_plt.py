import os
import subprocess
import shutil
import pandas as pd
import matplotlib.pyplot as plt
import re

# 创建一个新的figure，并设置图的大小
fig, ax = plt.subplots(figsize=(20, 10))

# 获取当前工作目录，以便后面返回
current_dir = os.getcwd()

# 自定义排序函数
def sort_key(s):
    temperature_match = re.findall(r"(\d+\.?\d*)K", s)
    temperature = float(temperature_match[0]) if temperature_match else 0.0

    distance_match = re.findall(r"(\d+\.?\d*)A", s)
    distance = float(distance_match[0]) if distance_match else 0.0

    return (temperature, distance)

# 遍历当前目录下的所有文件夹
#for folder in sorted(os.listdir('.'), key=sort_key):
for folder in sorted(os.listdir('.'), key=sort_key):    
    if os.path.isdir(folder) and folder != 'combine_plt' and "3000K" not in folder:

        print(folder)
        # 进入当前文件夹
        os.chdir(folder)
        
        # 执行gnuplot命令并忽略错误
        subprocess.run(['gnuplot', 'plt_reconstruct.gp'], stderr=subprocess.DEVNULL, check=False)

        # 返回到原来的目录
        os.chdir(current_dir)

        # 检查output1.png和colvar文件是否存在
        if not os.path.exists(os.path.join(folder, 'output1.png')) or not os.path.exists(os.path.join(folder, 'colvar')):
            print(f"Skipping {folder} because output1.png or colvar file is missing.")
            continue

        # 复制和重命名output1.png到combine_plt文件夹
        shutil.copy(os.path.join(folder, 'output1.png'), 'combine_plt')
        os.rename(os.path.join('combine_plt', 'output1.png'), os.path.join('combine_plt', folder + '.png'))

        # 复制和重命名colvar文件到combine_plt文件夹
        shutil.copy(os.path.join(folder, 'colvar'), 'combine_plt')
        os.rename(os.path.join('combine_plt', 'colvar'), os.path.join('combine_plt', folder + '_colvar'))

        # 读取colvar文件
        df = pd.read_csv(os.path.join('combine_plt', folder + '_colvar'), sep='\s+')

        # 使用第一列作为x，计算第3列到第18列的平均值作为y
        x = df.iloc[:, 0]
        y = df.iloc[:, 2:18].mean(axis=1)

        #labels = os.path.basename(folder)[-10:]
        # 找到最后一个 "_" 的位置
        last_underscore_position = folder.rfind("_")
        # 找到倒数第二个 "_" 的位置
        second_last_underscore_position = folder.rfind("_", 0, last_underscore_position)
        # 取倒数第二个 "_" 之后的所有字符
        labels = folder[second_last_underscore_position + 1:]

        # 在同一张图上绘制x-y图，使用文件名作为图例，设置线型为点，设置点的大小
        ax.plot(x, y, 'o', label=labels, markersize=1, markerfacecolor='none')

# 显示图例，并设置图例字体大小
ax.legend(fontsize='small', bbox_to_anchor=(1, 1), loc='upper left', ncol=20)

# 保存图像为combine_plt.png
plt.savefig('./combine_plt/combine_plt.png', bbox_inches='tight')

# 显示图像
plt.show()
