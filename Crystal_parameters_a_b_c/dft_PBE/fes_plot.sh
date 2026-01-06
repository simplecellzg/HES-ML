#python FES_from_Reweighting.py --colvar colvar --sigma 0.02 --temp 500 --cv 218 --bin 200 --blocks 1 --skiprows 10 --bias 219 && gnuplot plt_reconstruct_absorb.gp
#2d
python FES_from_Reweighting.py --colvar COLVAR --sigma 0.02,0.02 --temp 2000 --cv 4,5 --bin 100,100 --blocks 1 --skiprows 1 --bias 9
python plt_3dsf_average.py
python plt_2d.py
gnuplot plt_melt.gp
