import os
import argparse
import numpy as np
from pathlib import Path

COMMENT_LINE = 'Lattice="19.6230000000 0.0000000000 0.0000000000 0.0000000000 16.9480000000 0.0000000000 0.0000000000 0.0000000000 22.0000000000" Properties=species:S:1:pos:R:3 pbc="T T T"'

def read_single_xyz(filename):
    """读取单个包含多个结构的xyz文件"""
    with open(filename) as f:
        content = f.read().splitlines()
    
    structures = []
    i = 0
    while i < len(content):
        # 跳过空行
        while i < len(content) and not content[i].strip():
            i += 1
        if i >= len(content):
            break
            
        natoms = int(content[i])
        comment = content[i+1]
        atoms = []
        for j in range(i+2, i+2+natoms):
            parts = content[j].split()
            elem = parts[0]
            coords = list(map(float, parts[1:4]))
            atoms.append( (elem, coords) )
        structures.append( (natoms, comment, atoms) )
        i += 2 + natoms
        
    if len(structures) != 2:
        raise ValueError("输入文件必须包含2个结构（反应物和产物）")
    return structures

def validate_structures(rct, prod):
    """校验结构一致性"""
    if rct[0] != prod[0]:
        raise ValueError("原子数量不匹配")
    
    for (relem, _), (pelem, _) in zip(rct[2], prod[2]):
        if relem != pelem:
            raise ValueError("原子类型顺序不匹配")

def generate_interpolations(rct, prod, nsteps):
    """生成线性插值轨迹""" 
    # 创建注释替换的首尾结构
    rct_modified = (rct[0], COMMENT_LINE, rct[2])
    prod_modified = (prod[0], COMMENT_LINE, prod[2])
    trajectory = [rct_modified]
    
    # 参数化插值
    for step in range(1, nsteps+1):
        alpha = step / (nsteps + 1)
        interp_atoms = []
        for (elem, r_coord), (_, p_coord) in zip(rct[2], prod[2]):
            new_coord = (
                r_coord[0] + (p_coord[0] - r_coord[0]) * alpha,
                r_coord[1] + (p_coord[1] - r_coord[1]) * alpha,
                r_coord[2] + (p_coord[2] - r_coord[2]) * alpha
            )
            interp_atoms.append( (elem, new_coord) )
        trajectory.append( (rct[0], COMMENT_LINE, interp_atoms) )
    
    trajectory.append(prod_modified)
    return trajectory


def write_output(trajectory, combined_path, frame_dir):
    """写入输出文件"""
    # 写入合并文件
    with open(combined_path, 'w') as f:
        for natoms, comment, atoms in trajectory:
            f.write(f"{natoms}\n{comment}\n")
            for elem, (x,y,z) in atoms:
                f.write(f"{elem:5s} {x:15.10f} {y:15.10f} {z:15.10f}\n")
    
    # 写入单帧文件
    os.makedirs(frame_dir, exist_ok=True)
    for i, (natoms, comment, atoms) in enumerate(trajectory):
        with open(f"{frame_dir}/frame_{i:03d}.xyz", 'w') as f:
            f.write(f"{natoms}\n{comment}\n") 
            for elem, (x,y,z) in atoms:
                f.write(f"{elem:5s} {x:15.10f} {y:15.10f} {z:15.10f}\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='分子结构插值工具')
    parser.add_argument('-i', '--input', required=True, help='包含反应物和產物的XYZ文件')
    parser.add_argument('-n', '--steps', type=int, required=True, help='插值步骤数量')
    parser.add_argument('-o', '--output', default='trajectory.xyz', help='合并输出文件名')
    parser.add_argument('-d', '--directory', default='frames', help='单帧文件输出目录')
    
    args = parser.parse_args()
    
    # 读取并校验结构
    structures = read_single_xyz(args.input)
    reactant, product = structures
    validate_structures(reactant, product)
    
    # 生成插值轨迹
    trajectory = generate_interpolations(reactant, product, args.steps)
    
    # 输出结果
    write_output(trajectory, args.output, args.directory)
    print(f"生成成功！总结构数：{len(trajectory)}")
    print(f"合并文件保存在：{args.output}")
    print(f"单帧文件保存在：{args.directory}/ 目录")
    
