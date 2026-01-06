#!/bin/bash
mkdir -p Combine_GCMC_RMD_traj
mkdir -p Combine_GCMC_RMD_lmp
mkdir -p Combine_GCMC_RMD_plot

cp GCMC_RMD*/zz_gcmc_*.lammpstrj Combine_GCMC_RMD_traj/
cp GCMC_RMD*/final_gcmc*.lmp Combine_GCMC_RMD_lmp/
for dir in GCMC_RMD*/; do
    [ -f "$dir/ads_gcmc_md_time_coverage_analysis_nature.png" ] && \
    cp "$dir/ads_gcmc_md_time_coverage_analysis_nature.png" "Combine_GCMC_RMD_plot/${dir%/}.png"
done

mkdir -p Combine_RMD_Relax_traj
mkdir -p Combine_RMD_Relax_lmp
mkdir -p Combine_RMD_Relax_plot


for dir in RMD_Relax*/; do
    [ -f "$dir/adsorption_analysis_nature.png" ] && \
    cp "$dir/adsorption_analysis_nature.png" "Combine_RMD_Relax_plot/${dir%/}.png"
    [ -f "$dir/target_final.lmp" ] && \
    cp "$dir/target_final.lmp" "Combine_RMD_Relax_lmp/${dir%/}_target_final.lmp"
    [ -f "$dir/zz_target_trajectory.lammpstrj" ] && \
    cp "$dir/zz_target_trajectory.lammpstrj" "Combine_RMD_Relax_traj/${dir%/}_zz_target_trajectory.lammpstrj"
done

