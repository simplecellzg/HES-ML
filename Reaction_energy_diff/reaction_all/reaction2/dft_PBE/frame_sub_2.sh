#!/bin/bash
#SBATCH -N 2
#SBATCH -n 192
#SBATCH -p v6_384
#source /public1/soft/modules/module.sh
#module load cp2k/2024.1-para
#source /public1/home/sch9516/software/new-cp2k-2024.1/cp2k-2024.1/setup
#export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/public1/home/sch9516/software/new-cp2k-2024.1/plumed2/pytorch-v2.0.0/build/lib
#export PATH=/public1/home/sch9516/software/new-cp2k-2024.1/cp2k-2024.1/exe/local:$PATH

module unload anaconda/3-Python-3.8.3-phonopy-phono3py
module load gcc/9.3.0-new
source /public1/home/sch9516/software/new-cp2k-2024.1/pro/cp2k-2024.1-new/tools/toolchain/install/setup
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/public1/home/sch9516/software/new-cp2k-2024.1/pro/torch200/lib
export PATH=/public1/home/sch9516/software/new-cp2k-2024.1/pro/cp2k-2024.1-new/exe/local:$PATH


mpirun -np 192 cp2k.popt -i frame_2.inp -o frame_2.out
#mpirun -np 36 cp2k.popt -i xtb_test.inp -o xtb_test.out
