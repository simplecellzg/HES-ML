import glob
import os

# Hartree到kcal/mol的转换因子
HARTREE_TO_KCALMOL = 627.509474

# 查找并排序文件
files = sorted(glob.glob("frame*.out"), 
              key=lambda x: int(x.split("_")[1].split(".")[0]))

# 处理每个文件并收集数据
results = []
for file in files:
    # 获取frame名称（不带扩展名）
    frame_name = os.path.splitext(file)[0]
    
    # 读取能量值
    energy_hartree = None
    with open(file, "r") as f:
        for line in f:
            if "ENERGY| Total FORCE_EVAL ( QS ) energy [a.u.]:" in line:
                energy_hartree = float(line.strip().split()[-1])
                break
    
    # 转换单位（保留5位小数）
    if energy_hartree is not None:
        energy_kcal = round(energy_hartree * HARTREE_TO_KCALMOL, 5)
        results.append(f"{frame_name}  {energy_kcal:.5f}")

# 写入CSV文件（使用两个空格分隔）
with open("energies.csv", "w") as f:
    f.write("Frame  Energy(kcal/mol)\n")
    f.write("\n".join(results))
    