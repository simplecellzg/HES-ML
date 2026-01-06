import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors


step = 5
# 读取文件并解析数据
x_coords = []
y_coords = []
x_widths = []
y_widths = []
colors = []

with open('KERNELS_LDA', 'r') as file:
    for i, line in enumerate(file):
        if i >= 6:  # 跳过前六行
            parts = line.split()  # 以空格分隔
            if len(parts) >= 7:  # 确保有足够的数据列
                y_coords.append(float(parts[1]))
                x_coords.append(float(parts[2]))
                y_widths.append(float(parts[3]))
                x_widths.append(float(parts[4]))
                colors.append(-1 * float(parts[6]))  # 乘以-1


x_sampled = x_coords[::step]
y_sampled = y_coords[::step]
x_widths_sampled = x_widths[::step]
y_widths_sampled = y_widths[::step]
colors_sampled = colors[::step]

# 将椭圆宽度转换为点的大小（这里需要一个合适的转换因子，这取决于你的具体需求）
sizes = [500 * (xw + yw) for xw, yw in zip(x_widths_sampled, y_widths_sampled)]  # 示例转换因子为200
# 使用颜色映射和归一化
norm = mcolors.Normalize(vmin=min(colors_sampled), vmax=max(colors_sampled))
cmap = plt.get_cmap('coolwarm')

# 绘制散点图
fig, ax = plt.subplots(figsize=(24, 6))
sc = ax.scatter(x_sampled, y_sampled, s=sizes, c=colors_sampled, cmap=cmap, norm=norm, alpha=0.6, edgecolors='w', linewidths=0.5)

# 添加颜色条
plt.colorbar(sc, label='Value', pad=0.01)

# 设置标题和坐标轴标签
ax.set_title('Ellipse Sampling Distribution')
ax.set_xlabel('X')
ax.set_ylabel('Y')

# 调整坐标轴的范围，使内容更紧凑
ax.set_xlim(min(x_sampled), max(x_sampled))
ax.set_ylim(min(y_sampled), max(y_sampled))

# 使用tight_layout自动调整布局
plt.tight_layout()

# 保存为PNG图片，自动裁剪空白边缘
plt.savefig('output_ellipse_sampling_distribution_tight.png', dpi=100, bbox_inches='tight')

# 显示图表
plt.show()
