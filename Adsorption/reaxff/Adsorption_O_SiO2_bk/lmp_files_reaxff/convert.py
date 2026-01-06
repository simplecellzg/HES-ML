def convert_atomic_to_full(input_file, output_file, default_mol_id=1, default_charge=0.0):
    """
    将LAMMPS atomic style数据文件转换为full style
    
    参数:
    input_file: 输入文件名（atomic style）
    output_file: 输出文件名（full style）
    default_mol_id: 默认分子ID（如果所有原子属于同一分子，使用1）
    default_charge: 默认电荷值
    """
    
    with open(input_file, 'r') as f:
        lines = f.readlines()
    
    # 查找Atoms部分
    atoms_section_start = -1
    for i, line in enumerate(lines):
        if line.strip().startswith('Atoms'):
            atoms_section_start = i + 2  # 跳过标题行和空行
            break
    
    # 修改atom style声明
    new_lines = []
    for i, line in enumerate(lines):
        if i >= atoms_section_start and line.strip() and not line.strip().startswith('#'):
            # 解析atomic格式的原子行
            parts = line.split()
            if len(parts) >= 8:  # atom-ID type x y z ix iy iz
                atom_id = parts[0]
                atom_type = parts[1]
                x, y, z = parts[2], parts[3], parts[4]
                ix, iy, iz = parts[5], parts[6], parts[7]
                
                # 转换为full格式
                new_line = f"{atom_id} {default_mol_id} {atom_type} {default_charge:.6f} {x} {y} {z} {ix} {iy} {iz}\n"
                new_lines.append(new_line)
        elif line.strip().startswith('Atoms'):
            # 修改Atoms标签
            new_lines.append('Atoms # full\n')
        else:
            new_lines.append(line)
    
    # 写入新文件
    with open(output_file, 'w') as f:
        f.writelines(new_lines)
    
    print(f"转换完成！输出文件：{output_file}")

# 使用示例
convert_atomic_to_full('nve.lmp', 'nve_full.lmp', default_mol_id=1, default_charge=0.0)
