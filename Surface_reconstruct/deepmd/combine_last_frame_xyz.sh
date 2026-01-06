#!/bin/bash

# 创建目标文件夹，如果不存在
mkdir -p ./combine_last_frame_xyz
rm ./combine_last_frame_xyz/*

# 遍历所有符合条件的文件夹
for dir in MTD_2_database_2_surf_reconstruct_*/ ; do
    # 获取文件夹名称
    dir_name=${dir%*/}
    
    # 获取需要复制的文件的路径
    file_path=${dir}dump.lastframe.xyz-last-frame.xyz
    
    # 获取新的文件名，去掉前缀
    new_file_name=${dir_name#MTD_2_database_2_surf_reconstruct_}_xyz
    
    # 如果文件存在，复制并重命名
    if [ -f "${file_path}" ]; then
        cp "${file_path}" "./combine_last_frame_xyz/${new_file_name}"
        
        # 替换第二行
        sed -i "2s/.*/temp_height_${dir_name#MTD_2_database_2_surf_reconstruct_}/" "./combine_last_frame_xyz/${new_file_name}"
    fi
done

cat ./combine_last_frame_xyz/*_xyz > ./combine_last_frame_xyz/all_last_frame.xyz