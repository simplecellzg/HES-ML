#!/bin/bash

inp_template="energy_force_pbe.inp"
sbatch_template="submit_template.sh"
xyz_file="pos-1.xyz"

steps=$1
frame_number=0

# 计算xyz文件中的总帧数
atom_num=$(awk 'NR==1 {print $1}' $xyz_file)
total_lines=$(wc -l < "$xyz_file")
total_frames=$((total_lines / (atom_num + 2)))

while (( frame_number < total_frames )); do
    # 检查当前sbatch任务数量
    task_count=$(squeue -u $USER | wc -l)
    if (( task_count < 45 )); then
        frame_number=$((frame_number+steps))
        if (( frame_number >= total_frames )); then
            echo "Reached the end of the xyz file at frame $frame_number."
            break
        fi
        # 提取.xyz文件的一帧
        awk -v frame=${frame_number} -v num=${atom_num} 'NR==frame*(num+2)+1,NR==frame*(num+2)+num+2 {print}' ${xyz_file} > frame_${frame_number}.xyz
        # 提取出晶格参数
        lattice=$(head -n 2 frame_${frame_number}.xyz | tail -n 1 | awk -F'"' '{print $2}')
        # 生成新的cp2k输入文件

        # 将lattice参数分解为数组
        IFS=' ' read -ra ADDR <<< "$lattice"

        # 创建新的CELL参数
        new_cell="    &CELL\n      A    ${ADDR[0]}     ${ADDR[1]}     ${ADDR[2]}\n      B     ${ADDR[3]}    ${ADDR[4]}     ${ADDR[5]}\n      C     ${ADDR[6]}     ${ADDR[7]}    ${ADDR[8]}\n      PERIODIC XYZ #Direction(s) of applied PBC (geometry aspect)\n    &END CELL"

        # 替换inp文件中的CELL参数
        sed "/&CELL/,/&END CELL/c$new_cell" ${inp_template} > frame_${frame_number}.inp
        sed -i "s/       COORD_FILE_NAME frame.xyz/       COORD_FILE_NAME frame_${frame_number}.xyz/g" frame_${frame_number}.inp
        sed -i "s/PROJECT frame_number/PROJECT frame_${frame_number}/g" frame_${frame_number}.inp
        # 生成新的sbatch文件
        sed "s/frame_number/frame_${frame_number}/g" ${sbatch_template} > frame_sub_${frame_number}.sh
        # 提交任务
        sbatch frame_sub_${frame_number}.sh
    else
        # 等待
        sleep 10
    fi
done


