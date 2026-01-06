#!/bin/bash
#SBATCH -x paraai-n32-h-01-agent-[1,4,7-8,16-17,25,27-31]
module purge
module load miniforge3/24.1 compilers/cuda/12.1 cudnn/8.8.1.3_cuda12.x mpi/4.1.5-gcc11.3.0-cuda12.1-ucx1.14.1  nccl/2.18.3-1_cuda12.1 
source activate dp310


python gcmc_rmd_plot_combine.py > gcmc_rmd_plot_combine.out
