#!/bin/bash
#SBATCH -J lammps_deepmd_plumed
#SBATCH -N 1
#SBATCH -n 24
#SBATCH -p v6_384

module purge
source ~/software/deepmd-kit/bin/activate
module load mpi/oneAPI/2022.1
export PATH=/public1/home/sch9516/software/0703/lammps-patch_27Jun2024/src:$PATH
export LD_LIBRARY_PATH=/public1/home/sch9516/software/deepmd-kit/lib:$LD_LIBRARY_PATH
export LD_LIBRARY_PATH=/public1/home/sch9516/software/0703/lammps-patch_27Jun2024/lib/plumed/plumed-new/plumed2-2.9.1/install/lib:$LD_LIBRARY_PATH
#export OMP_NUM_THREADS=96
#export TF_INTRA_OP_PARALLELISM_THREADS=12
#export TF_INTER_OP_PARALLELISM_THREADS=8
mpirun -np 24  lmp_intel_cpu_intelmpi -in  input.lammps >log.lammps

bash ./get_last_xyz.sh dump.lastframe.xyz
