#!/bin/bash
#SBATCH -N 1 
#SBATCH -n 30
#SBATCH -p v6_384

python data2dp2.py
# source /public1/soft/modules/module.sh
# module load cp2k/2024.1-para
# mpirun -np 288 cp2k.popt -i sio2_5000k.inp -o sio2_5000k.out