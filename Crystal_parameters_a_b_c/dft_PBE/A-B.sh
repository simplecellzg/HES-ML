#!/bin/bash

# 定义两个字符串
strA="cv.Sk-[0_0_1],cv.Sk-[0_1_0],cv.Sk-[1_0_0],cv.Sk-[0_1_-1],cv.Sk-[0_1_1],cv.Sk-[1_-1_0],cv.Sk-[1_0_-1],cv.Sk-[1_0_1],cv.Sk-[1_1_0],cv.Sk-[1_-1_-1],cv.Sk-[1_-1_1],cv.Sk-[1_1_-1],cv.Sk-[1_1_1],cv.Sk-[0_0_2],cv.Sk-[0_2_0],cv.Sk-[2_0_0],cv.Sk-[0_1_-2],cv.Sk-[0_1_2],cv.Sk-[0_2_-1],cv.Sk-[0_2_1],cv.Sk-[1_-2_0],cv.Sk-[1_0_-2],cv.Sk-[1_0_2],cv.Sk-[1_2_0],cv.Sk-[2_-1_0],cv.Sk-[2_0_-1],cv.Sk-[2_0_1],cv.Sk-[2_1_0],cv.Sk-[1_-2_-1],cv.Sk-[1_-2_1],cv.Sk-[1_-1_-2],cv.Sk-[1_-1_2],cv.Sk-[1_1_-2],cv.Sk-[1_1_2],cv.Sk-[1_2_-1],cv.Sk-[1_2_1],cv.Sk-[2_-1_-1],cv.Sk-[2_-1_1],cv.Sk-[2_1_-1],cv.Sk-[2_1_1],cv.Sk-[0_2_-2],cv.Sk-[0_2_2],cv.Sk-[2_-2_0],cv.Sk-[2_0_-2],cv.Sk-[2_0_2],cv.Sk-[2_2_0],cv.Sk-[0_0_3],cv.Sk-[0_3_0],cv.Sk-[1_-2_-2],cv.Sk-[1_-2_2],cv.Sk-[1_2_-2],cv.Sk-[1_2_2],cv.Sk-[2_-2_-1],cv.Sk-[2_-2_1],cv.Sk-[2_-1_-2],cv.Sk-[2_-1_2],cv.Sk-[2_1_-2],cv.Sk-[2_1_2],cv.Sk-[2_2_-1],cv.Sk-[2_2_1],cv.Sk-[3_0_0],cv.Sk-[0_1_-3],cv.Sk-[0_1_3],cv.Sk-[0_3_-1],cv.Sk-[0_3_1],cv.Sk-[1_-3_0],cv.Sk-[1_0_-3],cv.Sk-[1_0_3],cv.Sk-[1_3_0],cv.Sk-[3_-1_0],cv.Sk-[3_0_-1],cv.Sk-[3_0_1],cv.Sk-[3_1_0],cv.Sk-[1_-3_-1],cv.Sk-[1_-3_1],cv.Sk-[1_-1_-3],cv.Sk-[1_-1_3],cv.Sk-[1_1_-3],cv.Sk-[1_1_3],cv.Sk-[1_3_-1],cv.Sk-[1_3_1],cv.Sk-[3_-1_-1],cv.Sk-[3_-1_1],cv.Sk-[3_1_-1],cv.Sk-[3_1_1],cv.Sk-[2_-2_-2],cv.Sk-[2_-2_2],cv.Sk-[2_2_-2],cv.Sk-[2_2_2],cv.Sk-[0_2_-3],cv.Sk-[0_2_3],cv.Sk-[0_3_-2],cv.Sk-[0_3_2],cv.Sk-[2_-3_0],cv.Sk-[2_0_-3],cv.Sk-[2_0_3],cv.Sk-[2_3_0],cv.Sk-[3_-2_0],cv.Sk-[3_0_-2],cv.Sk-[3_0_2],cv.Sk-[3_2_0],cv.Sk-[1_-3_-2],cv.Sk-[1_-3_2],cv.Sk-[1_-2_-3],cv.Sk-[1_-2_3],cv.Sk-[1_2_-3],cv.Sk-[1_2_3],cv.Sk-[1_3_-2],cv.Sk-[1_3_2],cv.Sk-[2_-3_-1],cv.Sk-[2_-3_1],cv.Sk-[2_-1_-3],cv.Sk-[2_-1_3],cv.Sk-[2_1_-3],cv.Sk-[2_1_3],cv.Sk-[2_3_-1],cv.Sk-[2_3_1],cv.Sk-[3_-2_-1],cv.Sk-[3_-2_1],cv.Sk-[3_-1_-2],cv.Sk-[3_-1_2],cv.Sk-[3_1_-2],cv.Sk-[3_1_2],cv.Sk-[3_2_-1],cv.Sk-[3_2_1],cv.Sk-[0_0_4],cv.Sk-[0_4_0],cv.Sk-[4_0_0],cv.Sk-[0_1_-4],cv.Sk-[0_1_4],cv.Sk-[0_4_-1],cv.Sk-[0_4_1],cv.Sk-[1_-4_0],cv.Sk-[1_0_-4],cv.Sk-[1_0_4],cv.Sk-[1_4_0],cv.Sk-[2_-3_-2],cv.Sk-[2_-3_2],cv.Sk-[2_-2_-3],cv.Sk-[2_-2_3],cv.Sk-[2_2_-3],cv.Sk-[2_2_3],cv.Sk-[2_3_-2],cv.Sk-[2_3_2],cv.Sk-[3_-2_-2],cv.Sk-[3_-2_2],cv.Sk-[3_2_-2],cv.Sk-[3_2_2],cv.Sk-[4_-1_0],cv.Sk-[4_0_-1],cv.Sk-[4_0_1],cv.Sk-[4_1_0],cv.Sk-[0_3_-3],cv.Sk-[0_3_3],cv.Sk-[1_-4_-1],cv.Sk-[1_-4_1],cv.Sk-[1_-1_-4],cv.Sk-[1_-1_4],cv.Sk-[1_1_-4],cv.Sk-[1_1_4],cv.Sk-[1_4_-1],cv.Sk-[1_4_1],cv.Sk-[3_-3_0],cv.Sk-[3_0_-3],cv.Sk-[3_0_3],cv.Sk-[3_3_0],cv.Sk-[4_-1_-1],cv.Sk-[4_-1_1],cv.Sk-[4_1_-1],cv.Sk-[4_1_1],cv.Sk-[1_-3_-3],cv.Sk-[1_-3_3],cv.Sk-[1_3_-3],cv.Sk-[1_3_3],cv.Sk-[3_-3_-1],cv.Sk-[3_-3_1],cv.Sk-[3_-1_-3],cv.Sk-[3_-1_3],cv.Sk-[3_1_-3],cv.Sk-[3_1_3],cv.Sk-[3_3_-1],cv.Sk-[3_3_1],cv.Sk-[0_2_-4],cv.Sk-[0_2_4],cv.Sk-[0_4_-2],cv.Sk-[0_4_2],cv.Sk-[2_-4_0],cv.Sk-[2_0_-4],cv.Sk-[2_0_4],cv.Sk-[2_4_0],cv.Sk-[4_-2_0],cv.Sk-[4_0_-2],cv.Sk-[4_0_2],cv.Sk-[4_2_0],cv.Sk-[1_-4_-2],cv.Sk-[1_-4_2],cv.Sk-[1_-2_-4],cv.Sk-[1_-2_4],cv.Sk-[1_2_-4],cv.Sk-[1_2_4],cv.Sk-[1_4_-2],cv.Sk-[1_4_2],cv.Sk-[2_-4_-1],cv.Sk-[2_-4_1],cv.Sk-[2_-1_-4],cv.Sk-[2_-1_4],cv.Sk-[2_1_-4],cv.Sk-[2_1_4],cv.Sk-[2_4_-1],cv.Sk-[2_4_1],cv.Sk-[4_-2_-1],cv.Sk-[4_-2_1],cv.Sk-[4_-1_-2],cv.Sk-[4_-1_2],cv.Sk-[4_1_-2],cv.Sk-[4_1_2],cv.Sk-[4_2_-1],cv.Sk-[4_2_1],cv.Sk-[2_-3_-3],cv.Sk-[2_-3_3],cv.Sk-[2_3_-3],cv.Sk-[2_3_3],cv.Sk-[3_-3_-2],cv.Sk-[3_-3_2],cv.Sk-[3_-2_-3],cv.Sk-[3_-2_3],cv.Sk-[3_2_-3],cv.Sk-[3_2_3],cv.Sk-[3_3_-2],cv.Sk-[3_3_2],cv.Sk-[2_-4_-2],cv.Sk-[2_-4_2],cv.Sk-[2_-2_-4],cv.Sk-[2_-2_4],cv.Sk-[2_2_-4],cv.Sk-[2_2_4],cv.Sk-[2_4_-2],cv.Sk-[2_4_2],cv.Sk-[4_-2_-2],cv.Sk-[4_-2_2],cv.Sk-[4_2_-2],cv.Sk-[4_2_2],cv.Sk-[0_0_5],cv.Sk-[0_3_-4],cv.Sk-[0_3_4],cv.Sk-[0_4_-3],cv.Sk-[0_4_3],cv.Sk-[0_5_0],cv.Sk-[3_-4_0],cv.Sk-[3_0_-4],cv.Sk-[3_0_4],cv.Sk-[3_4_0],cv.Sk-[4_-3_0],cv.Sk-[4_0_-3],cv.Sk-[4_0_3],cv.Sk-[4_3_0],cv.Sk-[5_0_0],cv.Sk-[0_1_-5],cv.Sk-[0_1_5],cv.Sk-[0_5_-1],cv.Sk-[0_5_1],cv.Sk-[1_-5_0],cv.Sk-[1_-4_-3],cv.Sk-[1_-4_3],cv.Sk-[1_-3_-4],cv.Sk-[1_-3_4],cv.Sk-[1_0_-5],cv.Sk-[1_0_5],cv.Sk-[1_3_-4],cv.Sk-[1_3_4],cv.Sk-[1_4_-3],cv.Sk-[1_4_3],cv.Sk-[1_5_0],cv.Sk-[3_-4_-1],cv.Sk-[3_-4_1],cv.Sk-[3_-1_-4],cv.Sk-[3_-1_4],cv.Sk-[3_1_-4],cv.Sk-[3_1_4],cv.Sk-[3_4_-1],cv.Sk-[3_4_1],cv.Sk-[4_-3_-1],cv.Sk-[4_-3_1],cv.Sk-[4_-1_-3],cv.Sk-[4_-1_3],cv.Sk-[4_1_-3],cv.Sk-[4_1_3],cv.Sk-[4_3_-1],cv.Sk-[4_3_1],cv.Sk-[5_-1_0],cv.Sk-[5_0_-1],cv.Sk-[5_0_1],cv.Sk-[5_1_0],cv.Sk-[1_-5_-1],cv.Sk-[1_-5_1],cv.Sk-[1_-1_-5],cv.Sk-[1_-1_5],cv.Sk-[1_1_-5],cv.Sk-[1_1_5],cv.Sk-[1_5_-1],cv.Sk-[1_5_1],cv.Sk-[3_-3_-3],cv.Sk-[3_-3_3],cv.Sk-[3_3_-3],cv.Sk-[3_3_3],cv.Sk-[5_-1_-1],cv.Sk-[5_-1_1],cv.Sk-[5_1_-1],cv.Sk-[5_1_1],cv.Sk-[0_2_-5],cv.Sk-[0_2_5],cv.Sk-[0_5_-2],cv.Sk-[0_5_2],cv.Sk-[2_-5_0],cv.Sk-[2_-4_-3],cv.Sk-[2_-4_3],cv.Sk-[2_-3_-4],cv.Sk-[2_-3_4],cv.Sk-[2_0_-5],cv.Sk-[2_0_5],cv.Sk-[2_3_-4],cv.Sk-[2_3_4],cv.Sk-[2_4_-3],cv.Sk-[2_4_3],cv.Sk-[2_5_0],cv.Sk-[3_-4_-2],cv.Sk-[3_-4_2],cv.Sk-[3_-2_-4],cv.Sk-[3_-2_4],cv.Sk-[3_2_-4],cv.Sk-[3_2_4],cv.Sk-[3_4_-2],cv.Sk-[3_4_2],cv.Sk-[4_-3_-2],cv.Sk-[4_-3_2],cv.Sk-[4_-2_-3],cv.Sk-[4_-2_3],cv.Sk-[4_2_-3],cv.Sk-[4_2_3],cv.Sk-[4_3_-2],cv.Sk-[4_3_2],cv.Sk-[5_-2_0],cv.Sk-[5_0_-2],cv.Sk-[5_0_2],cv.Sk-[5_2_0],cv.Sk-[1_-5_-2],cv.Sk-[1_-5_2],cv.Sk-[1_-2_-5],cv.Sk-[1_-2_5],cv.Sk-[1_2_-5],cv.Sk-[1_2_5],cv.Sk-[1_5_-2],cv.Sk-[1_5_2],cv.Sk-[2_-5_-1],cv.Sk-[2_-5_1],cv.Sk-[2_-1_-5],cv.Sk-[2_-1_5],cv.Sk-[2_1_-5],cv.Sk-[2_1_5],cv.Sk-[2_5_-1],cv.Sk-[2_5_1],cv.Sk-[5_-2_-1],cv.Sk-[5_-2_1],cv.Sk-[5_-1_-2],cv.Sk-[5_-1_2],cv.Sk-[5_1_-2],cv.Sk-[5_1_2],cv.Sk-[5_2_-1],cv.Sk-[5_2_1]"
strB="cv.Sk-[3_-2_0],cv.Sk-[3_2_0],cv.Sk-[0_4_0],cv.Sk-[3_-2_-3],cv.Sk-[3_-2_3],cv.Sk-[3_2_-3],cv.Sk-[3_2_3],cv.Sk-[0_4_-3],cv.Sk-[0_4_3]"

# 使用IFS将字符串转换为数组
IFS=',' read -ra arrA <<< "$strA"
IFS=',' read -ra arrB <<< "$strB"

# 使用关联数组存储B数组中的元素
declare -A mapB
for elem in "${arrB[@]}"; do
  mapB[$elem]=1
done

# 创建一个空的结果数组
declare -a result

# 遍历A数组，检查每个元素是否在B数组中
for elem in "${arrA[@]}"; do
  if [[ -z ${mapB[$elem]} ]]; then
    # 如果元素不在B数组中，将其添加到结果数组中
    result+=($elem)
  fi
done

# 获取result数组的长度
len=${#result[@]}
len2=${#arrB[@]}

{
echo -n "uwall1: UPPER_WALLS ARG="
for ((i=0; i<len; i++))
do
  printf "%s" "${result[$i]}"
  if [ $i -ne $((len-1)) ]; then
    printf ","
  fi
done

printf " AT="
for ((i=0; i<len; i++))
do
  printf "2.0"
  if [ $i -ne $((len-1)) ]; then
    printf ","
  fi
done

printf " KAPPA="
for ((i=0; i<len; i++))
do
  printf "1000"
  if [ $i -ne $((len-1)) ]; then
    printf ","
  fi
done

printf " EXP="
for ((i=0; i<len; i++))
do
  printf "2"
  if [ $i -ne $((len-1)) ]; then
    printf ","
  fi
done

printf "\n"
printf "\n"

echo -n "uwall2: UPPER_WALLS ARG="
for ((i=0; i<len2; i++))
do
  printf "%s" "${arrB[$i]}"
  if [ $i -ne $((len2-1)) ]; then
    printf ","
  fi
done

printf " AT="
for ((i=0; i<len2; i++))
do
  printf "2.0"
  if [ $i -ne $((len2-1)) ]; then
    printf ","
  fi
done

printf " KAPPA="
for ((i=0; i<len2; i++))
do
  printf "1000"
  if [ $i -ne $((len2-1)) ]; then
    printf ","
  fi
done

printf " EXP="
for ((i=0; i<len2; i++))
do
  printf "2"
  if [ $i -ne $((len2-1)) ]; then
    printf ","
  fi
done
printf "\n"
printf "\n"
} > A-B_output
