#!/bin/bash
#SBATCH -N 1 
#SBATCH -n 12
#SBATCH -p v6_384

combinedir='/public1/home/sch9516/ZG/MTD_3_database_trained_post/COMBINE_DATA_NEW'
# Navigate to the directory containing the sio2* directories
#cd /public1/home/sch9516/ZG/MTD_2_database/MTD_2_database_1_melt
steps=20
melt_dir='/public1/home/sch9516/ZG/MTD_3_database_trained_post/MTD_3_database_1_melt_trained_post/MTD_3_database_1_melt_no_deeplda_*k_2dim'
surf_re_dir='/public1/home/sch9516/ZG/MTD_3_database_trained_post/MTD_3_database_2_surf_reconstruct_trained_post/MTD_2_database_2_surf_reconstruct_*K_*A'
surf_re_dir2='/public1/home/sch9516/ZG/MTD_3_database_trained_post/MTD_3_database_2_surf_reconstruct_trained_post_no_dipole/MTD_2_database_2_surf_reconstruct_*K_*A'
absorb_dir='/public1/home/sch9516/ZG/MTD_3_database_trained_post/MTD_3_database_3_gas_solid_absorb_trained_post_lmp_*k/MTD_3_database_3_gas_solid_absorb_11_*'
surf_recomposition_dir='/public1/home/sch9516/ZG/MTD_3_database_trained_post/MTD_3_database_4_O_surface_recomposition_trained_post_lmp_*k/MTD_2_database_4_O_surface_recomposition_1_*'
# Loop through each directory starting with 'sio2'
for dir in ${surf_re_dir}; do
        # Check if directory exists
        if [ -d "$dir" ]; then

            echo "Processing directory: $dir"

            cd $dir
            mkdir resub_e_f
            cp ${combinedir}/submit_template.sh "${dir}/resub_e_f"
            cp ${combinedir}/process_frame.sh "${dir}/resub_e_f"
            #surface use
            #cp ${combinedir}/energy_force_pbe_dipole.inp "${dir}/resub_e_f/energy_force_pbe.inp"
            # melt use
            #cp ${combinedir}/energy_force_pbe.inp "${dir}/resub_e_f/energy_force_pbe.inp"
            cp ${dir}/SiO2.lammpstrj_final_wrapped.xyz "${dir}/resub_e_f/pos-1.xyz"
            cp ${combinedir}/data2dp3.py ${dir}/resub_e_f/

            cd resub_e_f

            #单帧e_f计算
            #bash process_frame.sh ${steps}

            #构建deepmd文件
            #rm -r dp_wrap_all
            #python data2dp3.py
            
            #复制汇总dp数据
            mkdir ${dir}/dp_wrap_all
            cp -r ${dir}/resub_e_f/dp_wrap_all/*/* ${dir}/dp_wrap_all

            cd ${combinedir}
        fi
done

#if [ $counter -ne $n ]; then
#    echo "The $n-th directory does not exist."
#fi





