#!/bin/bash
module load atomsk/11.2

# 检查是否提供了一个参数
if [ "$#" -ne 1 ]; then
  echo "用法: \\$0 <文件名>"
  exit 1
fi

base_name="$1"
cell_file="${base_name}-1.cell"
xyz_file="${base_name}-pos-1.xyz"
wrapped_file_prefix="${base_name}_wrapped"
final_output_file="${base_name}_final_wrapped.xyz"

# Check if the directory exists
if [ -d "xyz_bk" ]; then
    rm -r xyz_bk/
fi
mkdir xyz_bk

# Check if the backup directory exists, if not create it and copy the original pos file
if [ ! -d "xyz_bk_bak" ]; then
    mkdir xyz_bk_bak
    cp ${xyz_file} xyz_bk_bak/
else
    cp xyz_bk_bak/${xyz_file} ./
fi

read -r atoms_number < "$xyz_file"
total_lines_per_frame=$((atoms_number + 2))

frame=1
> "$final_output_file"

tail -n +2 "$cell_file" | while read -r line; do
  read -ra arr <<< "$line"
  lattice="Lattice=\"${arr[@]:2:9}\" Properties=species:S:1:pos:R:3 pbc=\"T T T\""

  start_line=$(( (frame - 1) * total_lines_per_frame + 1 ))
  end_line=$(( frame * total_lines_per_frame ))

  sed -n "${start_line},${end_line}p" "$xyz_file" | sed "2s/.*/$lattice/" > "${wrapped_file_prefix}_${frame}.xyz"

  atomsk "${wrapped_file_prefix}_${frame}.xyz" -wrap "${wrapped_file_prefix}_temp_${frame}.xyz" >/dev/null 2>&1
  sed -i "2s/.*/$lattice/" "${wrapped_file_prefix}_temp_${frame}.xyz"
  cat "${wrapped_file_prefix}_temp_${frame}.xyz" >> "$final_output_file"

  rm "${wrapped_file_prefix}_${frame}.xyz" "${wrapped_file_prefix}_temp_${frame}.xyz"

  ((frame++))
done

mv "$final_output_file" ./xyz_bk
cp  ./xyz_bk/${final_output_file} "$xyz_file"
echo "转换完成，所有原子坐标已包裹在盒子内部。输出文件为 ./xyz_bk/$final_output_file"
