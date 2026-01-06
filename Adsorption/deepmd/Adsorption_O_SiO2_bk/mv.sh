#!/bin/bash

# 创建目标文件夹（如果不存在）
mkdir -p unused_bk

# 查找并移动同时包含 RMD_Relax 和指定气压值的文件夹
find . -maxdepth 1 -type d -name "*RMD_Relax*" | while read dir; do
    # 检查是否包含指定的气压值
    if [[ "$dir" =~ (10atm|7\.5atm|0\.05atm) ]]; then
        echo "Moving $dir to unused_bk/"
        mv "$dir" unused_bk/
    fi
done
