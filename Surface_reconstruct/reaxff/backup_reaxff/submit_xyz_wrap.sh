#!/bin/bash
#SBATCH -N 1 
#SBATCH -n 20
#SBATCH -p v6_384

source /public1/soft/modules/module.sh
# module load cp2k/2024.1-para
# mpirun -np 288 cp2k.popt -i sio2_2000k.inp -o sio2_2000k.out

module load atomsk/11.2
bash xyz_wrap.sh sio2_surf_o_reconstruct_xtb
#bash xyz_wrap.sh sio2_surf_o_reconstruct_pbe
