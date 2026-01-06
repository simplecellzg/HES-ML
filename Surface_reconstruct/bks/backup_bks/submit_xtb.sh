#!/bin/bash
#SBATCH -N 1
#SBATCH -n 96
#SBATCH -p v6_384
#source /public1/soft/modules/module.sh
#module load cp2k/2024.1-para
#source /public1/home/sch9516/software/new-cp2k-2024.1/cp2k-2024.1/setup
#export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/public1/home/sch9516/software/new-cp2k-2024.1/plumed2/pytorch-v2.0.0/build/lib
#export PATH=/public1/home/sch9516/software/new-cp2k-2024.1/cp2k-2024.1/exe/local:$PATH
#mpirun -np 192 cp2k.popt -i sio2_surf_o_reconstruct_nvt_1500k.inp -o sio2_surf_o_reconstruct_nvt_1500k.out

module unload anaconda/3-Python-3.8.3-phonopy-phono3py
module load gcc/9.3.0-new
source /public1/home/sch9516/software/new-cp2k-2024.1/pro/cp2k-2024.1-new/tools/toolchain/install/setup
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/public1/home/sch9516/software/new-cp2k-2024.1/pro/torch200/lib
export PATH=/public1/home/sch9516/software/new-cp2k-2024.1/pro/cp2k-2024.1-new/exe/local:$PATH

mpirun -np 96 cp2k.popt -i sio2_surf_o_reconstruct_xtb.inp -o sio2_surf_o_reconstruct_xtb.out
