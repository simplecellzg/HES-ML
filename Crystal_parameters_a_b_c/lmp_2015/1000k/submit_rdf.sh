#!/bin/bash
#SBATCH -N 1
#SBATCH -n 24
#SBATCH -p v6_384
#source /public1/soft/modules/module.sh
#module load cp2k/2024.1-para
#source /public1/home/sch9516/software/new-cp2k-2024.1/cp2k-2024.1/setup
#export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/public1/home/sch9516/software/new-cp2k-2024.1/plumed2/pytorch-v2.0.0/build/lib
#export PATH=/public1/home/sch9516/software/new-cp2k-2024.1/cp2k-2024.1/exe/local:$PATH

#conda activate python_311_rdf

python rdf.py 
#mpirun -np 36 cp2k.popt -i xtb_test.inp -o xtb_test.out
