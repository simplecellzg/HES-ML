#!/usr/bin/env python3
"""
计算氧原子的化学势 (chemical potential)
输入参数：
  第一个参数：温度 (K)
  第二个参数：压力 (bar)
"""

import sys
import math

def calculate_mu(T, P_bar):
    """
    计算氧原子的化学势
    
    参数:
        T: 温度 (K)
        P_bar: 压力 (bar)
    
    返回:
        mu: 化学势 (eV)
    """
    
    # 物理常数
    k_B = 1.380649e-23  # 玻尔兹曼常数 (J/K)
    h = 6.62607015e-34  # 普朗克常数 (J·s)
    N_A = 6.02214076e23  # 阿伏伽德罗常数 (mol^-1)
    eV_to_J = 1.602176634e-19  # eV到J的转换因子
    
    # 氧原子参数
    m_O = 15.999 / N_A / 1000  # 氧原子质量 (kg)
    
    # 单位转换
    P = P_bar * 1e5  # bar转换为Pa
    
    # 计算热德布罗意波长
    lambda_dB = h / math.sqrt(2 * math.pi * m_O * k_B * T)
    
    # 计算理想气体化学势
    # μ_id = k_B * T * ln(P * λ^3 / (k_B * T))
    mu_id_J = k_B * T * math.log(P * lambda_dB**3 / (k_B * T))
    
    # 转换为eV
    mu_id_eV = mu_id_J / eV_to_J
    
    # 对于理想气体，μ_ex = 0
    mu_ex_eV = 0.0
    
    # 总化学势
    mu = mu_id_eV + mu_ex_eV
    
    return mu, lambda_dB

def main():
    # 检查命令行参数
    if len(sys.argv) != 3:
        print("用法: python calculate_mu.py <温度(K)> <压力(bar)>")
        print("示例: python calculate_mu.py 298 1.0")
        sys.exit(1)
    
    try:
        # 读取输入参数
        T = float(sys.argv[1])
        P_bar = float(sys.argv[2])
        
        # 验证输入
        if T <= 0:
            print("错误：温度必须大于0 K")
            sys.exit(1)
        if P_bar <= 0:
            print("错误：压力必须大于0 bar")
            sys.exit(1)
        
        # 计算化学势
        mu, lambda_dB = calculate_mu(T, P_bar)
        
        # 输出结果
        print(f"\n计算结果：")
        print(f"温度: {T:.2f} K")
        print(f"压力: {P_bar:.2f} bar")
        print(f"热德布罗意波长: {lambda_dB:.3e} m")
        print(f"化学势 (μ): {mu:.6f} eV")
        
        # 额外信息
        print(f"\n参考信息：")
        print(f"在标准条件下 (298 K, 1 bar):")
        mu_std, lambda_std = calculate_mu(298, 1.0)
        print(f"化学势: {mu_std:.6f} eV")
        
    except ValueError:
        print("错误：请输入有效的数字")
        sys.exit(1)
    except Exception as e:
        print(f"错误：{str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
