#!/bin/bash
#SBATCH -N 1 
#SBATCH -n 4
#SBATCH -p v6_384

source /public1/soft/modules/module.sh
# module load cp2k/2024.1-para
# mpirun -np 288 cp2k.popt -i sio2_2000k.inp -o sio2_2000k.out
# bash batch_sub.sh
python combine_plt_new20241024.py