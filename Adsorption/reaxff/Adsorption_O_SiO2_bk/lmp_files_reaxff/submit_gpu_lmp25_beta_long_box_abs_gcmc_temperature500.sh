#!/bin/bash
#SBATCH --gpus=1
#SBATCH -x paraai-n32-h-01-agent-[1,4,7-8,16-17,25,27,28-31]

export LAMMPS_PLUGIN_PATH=/home/bingxing2/home/scx7113/soft/deepmd-kit-3.1.0/install
source /home/bingxing2/home/scx7113/soft/deepmd-kit-3.1.0/install/env.sh
source /home/bingxing2/home/scx7113/soft/lammps-12Jun2025-lxk/install/env.sh

# Use newton off with neigh full
mpirun -n 1 lmp_mpi -h
mpirun -n 1 lmp_mpi -k on g 1 -sf kk -pk kokkos newton on neigh half -in in.flux_beta_long_box_abs_gcmc_temperature500 >log.lammps_beta_long_box_abs_gcmc_temperature500