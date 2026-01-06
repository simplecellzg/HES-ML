import numpy as np
import matplotlib.pyplot as plt

# 读取数据
data = np.loadtxt('fes-rew.dat')


# 提取x, y, z
x = data[:, 0]
y = data[:, 1]
z = data[:, 2]
# 减去最小值
#z -= np.min(z)

# 转换为网格
# 转换为网格
x_unique = np.unique(x)
y_unique = np.unique(y)
Y, X = np.meshgrid(x_unique, y_unique)

# 将z值调整为网格形状
Z = z.reshape(len(y_unique), len(x_unique))

# 创建等值面图，设置颜色映射为'bwr'
plt.figure(figsize=(24, 6))
cp = plt.contourf(X, Y, Z, levels=100, cmap='coolwarm')
contours = plt.contour(X, Y, Z, levels=50, colors='black', linestyles='dashed', linewidths=0.5)  # 绘制灰色虚线等值线


# 添加等值线标签
plt.clabel(contours, inline=True, fontsize=8)

# 添加色标
cbar = plt.colorbar(cp, pad=0.01)
cbar.set_label('Energy Difference (KJ/mol) ')

# 添加标题和坐标轴标签
plt.title('Contour Plot')
plt.xlabel('X')
plt.ylabel('Y')
# 使用tight_layout自动调整布局
plt.tight_layout()


# 保存图像
plt.savefig('output1_2d2.png', bbox_inches='tight')
