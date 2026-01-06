#!/bin/bash
for dir in ./*/
do
    dir=${dir%*/}
    cd "$dir"
    gnuplot plt_reconstruct.gp
    cp output1.png "../combine_plt/${dir##*/}.png"
    echo ${dir##*/}.png
    cd ..
done

echo "完成"
