#!/bin/bash
#SBATCH --gpus=1
#SBATCH -x paraai-n32-h-01-agent-[1,4,7-8,16-17,25,27,28-31]
export OMP_PROC_BIND=spread #这里已经有绑核的意思了，如果不放心可以加上强制绑核命令，见下面。
export OMP_PLACES=threads
export OMP_NUM_THREADS=1
export LAMMPS_PLUGIN_PATH=/home/bingxing2/home/scx7113/soft/deepmd-kit-3.1.0/install
export PATH=/home/bingxing2/home/scx7113/soft/lammps-12Jun2025/src:$PATH
source /home/bingxing2/home/scx7113/soft/deepmd-kit-3.1.0/install/env.sh
mpirun -n 1 lmp_mpi -h


mpirun -n 1 lmp_mpi -in in.flux_beta_long_box_abs_gcmc_temperature1000 >log.lammps_beta_long_box_abs_gcmc_temperature1000

