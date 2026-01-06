#!/bin/bash

# 定义源文件目录和文件列表
src_dir="/public1/home/sch9516/ZG/MTD_3_database_trained_post_result/backup_bks"
#files_to_copy=("sio2_surf_o_reconstruct_pbe.inp" "sio2_surf_o_slab_240_addH_opt.xyz" "sio2_surf_o_reconstruct_xtb.inp" "submit_pbe.sh" "submit_xtb.sh" "xyz_wrap.sh" "submit_xyz_wrap.sh" "plt_reconstruct.gp" "plumed_SiO_surf_reconstruct.dat")
files_to_copy=("input.lammps" "potential_SiO2.TPF" "sio2_surf_o_slab_240_addH_opt_modified_charges.lmp" "get_last_xyz.sh" "submit_lmp_bks.sh" "submit_xtb.sh" "xyz_wrap.sh" "submit_xyz_wrap.sh" "plt_reconstruct.gp" "plumed_SiO_surf_reconstruct.dat")

# 循环遍历温度和上界
for temp in $(seq 300 50 1500); do
  for upper_bound in $(seq 8.2 0.1 9.8); do
#for temp in $(seq 300 50 350); do
#  for upper_bound in $(seq 8.2 0.1 8.5); do
    # 创建新的文件夹
    new_dir="MTD_2_database_2_surf_reconstruct_${temp}K_${upper_bound}A"
    mkdir -p "$new_dir"

    # 复制文件
    for file in "${files_to_copy[@]}"; do
      cp "${src_dir}/${file}" "${new_dir}"
    done

    # 修改sio2_surf_o_reconstruct_nvt.inp和xtb_test.inp中的温度
    sed -i "s/variable        TEMP            equal 500/variable        TEMP            equal ${temp}/g" "${new_dir}/input.lammps"
    #sed -i "s/TEMPERATURE 500/TEMPERATURE ${temp}/g" "${new_dir}/sio2_surf_o_reconstruct_xtb.inp"

    # 修改plumed_SiO_surf_reconstruct.dat中的上界
    sed -i "s/AT=up-wall/AT=${upper_bound}/g" "${new_dir}/plumed_SiO_surf_reconstruct.dat"

    # 提交任务，限制最大运行任务数量为5
    while true; do
      num_jobs=$(squeue -u $USER | wc -l)
      if [ "$num_jobs" -lt 40 ]; then
        cd "${new_dir}"
#        sbatch submit_xtb.sh
         sbatch submit_lmp_bks.sh
        cd ..
        break
      else
        sleep 1m
      fi
    done
  done
done
