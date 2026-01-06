import numpy as np
from collections import defaultdict

def read_lammps_file(filename):
    """读取LAMMPS输入文件，保留原始格式"""
    with open(filename, 'r') as f:
        lines = f.readlines()
    
    # 保留前17行不变
    header_lines = lines[:17]
    
    # 解析原子数据（从第18行开始）
    atoms = []
    for line in lines[17:]:
        line = line.strip()
        if not line or line.startswith('#'):
            continue
            
        if line[0].isdigit():
            parts = line.split()
            if len(parts) >= 6:  # 确保行有足够的数据
                atom_id = int(parts[0])
                atom_type = int(parts[1])
                charge = float(parts[2])
                x = float(parts[3])
                y = float(parts[4])
                z = float(parts[5])
                atoms.append([atom_id, atom_type, charge, x, y, z])
    
    return header_lines, atoms

def assign_charges(atoms):
    """根据规则分配电荷"""
    # 将原子按类型分组
    atom_types = defaultdict(list)
    for atom in atoms:
        atom_id, atom_type, _, x, y, z = atom
        atom_types[atom_type].append((atom_id, x, y, z))
    
    # 计算周期性边界条件下的距离
    def calc_distance(pos1, pos2, box_dims):
        dx = pos1[0] - pos2[0]
        dy = pos1[1] - pos2[1]
        dz = pos1[2] - pos2[2]
        
        # 考虑周期性边界条件
        dx = dx - box_dims[0] * round(dx / box_dims[0])
        dy = dy - box_dims[1] * round(dy / box_dims[1])
        dz = dz - box_dims[2] * round(dz / box_dims[2])
        
        return np.sqrt(dx**2 + dy**2 + dz**2)
    
    # 先为原子分配默认电荷
    for atom in atoms:
        if atom[1] == 1:  # Si
            atom[2] = 2.4
        elif atom[1] == 2:  # O
            atom[2] = -1.2
        elif atom[1] == 3:  # H
            atom[2] = 1.0
    
    # 找出与H原子最近的O原子
    h_atoms = atom_types.get(3, [])
    o_atoms = atom_types.get(2, [])
    
    # 假设盒子尺寸为文件中提供的尺寸
    box_dims = [19.623, 16.948, 18.000]
    
    o_modified = set()  # 追踪已修改的O原子
    
    for h_id, hx, hy, hz in h_atoms:
        min_dist = float('inf')
        nearest_o_id = None
        
        for o_id, ox, oy, oz in o_atoms:
            dist = calc_distance((hx, hy, hz), (ox, oy, oz), box_dims)
            if dist < min_dist:
                min_dist = dist
                nearest_o_id = o_id
        
        if nearest_o_id is not None:
            o_modified.add(nearest_o_id)
    
    # 修改最近O原子的电荷
    for atom in atoms:
        if atom[1] == 2 and atom[0] in o_modified:  # O最近的
            atom[2] = -1.2
    
    # 检查总电荷
    total_charge = sum(atom[2] for atom in atoms)
    print(f"系统总电荷: {total_charge}")
    
    # 如果需要调整以实现电中性
    if abs(total_charge) > 1e-10:
        print(f"调整电荷以保持电中性")
        # 可以通过微调所有氧原子的电荷来实现电中性
        o_count = sum(1 for atom in atoms if atom[1] == 2)
        if o_count > 0:
            charge_adjustment = total_charge / o_count
            
            for atom in atoms:
                if atom[1] == 2:  # 所有氧原子
                    atom[2] -= charge_adjustment
    
    return atoms

def write_lammps_file(filename, header_lines, atoms):
    """写入更新后的LAMMPS文件，保持原始格式"""
    with open(filename, 'w') as f:
        # 写入前17行不变
        for line in header_lines:
            f.write(line)
        
        # 写入修改后的原子数据
        for atom in atoms:
            f.write(f"{atom[0]}\t{atom[1]}\t{atom[2]:.6f}\t{atom[3]:.12f}\t{atom[4]:.12f}\t{atom[5]:.12f}\n")

def main():
    input_file = "sio2_surf_o_slab_240_addH_opt.lmp"
    output_file = "sio2_surf_o_slab_240_addH_opt_modified_charges.lmp"
    
    # 读取文件
    header_lines, atoms = read_lammps_file(input_file)
    
    # 分配电荷
    atoms = assign_charges(atoms)
    
    # 写入更新后的文件
    write_lammps_file(output_file, header_lines, atoms)
    
    print(f"已成功将更新后的文件写入到 {output_file}")

if __name__ == "__main__":
    main()
