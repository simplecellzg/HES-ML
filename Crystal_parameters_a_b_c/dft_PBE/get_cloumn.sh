#!/bin/bash

# 读取列数作为参数
#col_num=$1
#awk -v col=$col_num -F' ' 'NR==1{print $col; exit}' colvar

title=$1
awk -v title="$title" -F' ' 'NR==1{for(i=1;i<=NF;i++){if($i==title){print i-2; exit}}}' COLVAR
