# 设置输出格式为PNG
set terminal png size 800,600

# 设置输出文件名
#set output 'output.png'

# 设置图表标题
# set title 'SiO2 surface reconstruction'

# 设置轴标签
set xlabel 'Time/ps'
set ylabel 'CV-distance/Å'
#set xrange [0:2.5]
#set yrange [1.0:4.0]
# 绘制折线图，指定使用文件的第二列作为X轴，第四列作为Y轴

#set output 'output1.png'
#plot 'colvar' using 1:19 skip 1 w lp pt 7 ps 1 lc 'red'  title 'time vs zdis_surf_down.max'
#plot 'colvar' u ($1):(($3+$4+$5+$6+$7+$8+$9+$10+$11+$12+$13+$14+$15+$16+$17+$18)/16) w lp pt 7 ps 1 lc 'red' title 'time vs zdis-surf-down.max'
#set output 'output0.png'
#plot 'fes-rew.dat' using 1:2 skip 9 w points pt 7 ps 1 lc 'red'  title 'CN vs ENERGY'
set output 'output1.png'
plot 'COLVAR' using 1:7 skip 1 w lp pt 7 ps 1 lc 'red'  title 'time vs energy'
set output 'output2.png'
plot 'COLVAR' using 1:2 skip 1 w lp pt 7 ps 1 lc 'red'  title 'time vs refcv.mean',\
'COLVAR' using 1:3 skip 1 w lp pt 7 ps 1 lc 'blue'  title 'time vs refcv.morethan'
set output 'output3.png'
plot 'COLVAR' using 1:4 skip 1 w lp pt 7 ps 1 lc 'red'  title 'time vs sf3d_1',\
'COLVAR' using 1:5 skip 1 w lp pt 7 ps 1 lc 'blue'  title 'time vs sf3d_2'
set output 'output4.png'
plot 'COLVAR' using 1:6 skip 1 w lp pt 7 ps 1 lc 'red'  title 'time vs q6.vmean'
set output 'output5.png'
plot 'COLVAR' using 1:8 skip 1 w lp pt 7 ps 1 lc 'red'  title 'time vs vol'
set output 'output6.png'
plot 'COLVAR' using 1:9 skip 1 w lp pt 7 ps 1 lc 'red'  title 'time vs opes1.bias'
set output 'output7.png'
plot 'SiO2_crystallisation_melt_3DSF_pbe-1.ener' using 1:4 skip 1 w lp pt 7 ps 1 lc 'red'  title 'time vs temp'
set output 'output8.png'
plot 'SiO2_crystallisation_melt_3DSF_pbe-1.ener' using 4:5 skip 1 w lp pt 7 ps 1 lc 'blue'  title 'temp vs pot'

#plot 'colvar' u ($1):(($3+$4+$5+$6+$7+$8+$9+$10+$11+$12+$13+$14+$15+$16+$17+$18)/16) w points pt 7 ps 1 lc 'blue' title 'time vs CV'

