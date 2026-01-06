import pandas as pd
import matplotlib.pyplot as plt
from adjustText import adjust_text
# 读取数据文件
df = pd.read_csv('COLVAR_LIQUID', sep="\s+")
# 定义平均值的判断条件
average_threshold = 2.0
# 计算从第二列开始的每一列的平均值
averages = df.iloc[:, 1:].mean()
#averages = df.iloc[:, 1:].min()

# 绘制柱状图
plt.bar(range(len(averages)), averages)
plt.xlabel('Column')
plt.ylabel('Average')
plt.title('Average of each column')

# 对于平均值大于2的，标注出列名
texts = []
high_avg_columns = []  # 用于存储平均值大于1.5的列名
for i, avg in enumerate(averages):
    if avg > average_threshold:
        column_name = df.columns[i+3]
        texts.append(plt.text(i, avg, df.columns[i+3], ha='center'))
        high_avg_columns.append(column_name)

# 使用 adjust_text 来自动调整标签的位置
adjust_text(texts, arrowprops=dict(arrowstyle='->', color='red'))
# 输出平均值大于1.5的列名，用逗号分隔
high_avg_columns_str = ",".join(high_avg_columns)
print(f"Number of columns with average > {average_threshold}: {len(high_avg_columns)}")
print(f"Columns with average > {average_threshold}:", high_avg_columns_str)

# 保存图形为 PNG 文件
plt.savefig('output.png', dpi=300)

# 如果还想在屏幕上显示图形，可以调用 plt.show()
# plt.show()