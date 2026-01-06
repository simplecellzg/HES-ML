for dir in MTD_2_database_2_surf_reconstruct*; do 
    if [ "$dir" != "MTD_2_database_3_gas_solid_absorb_11_BC_B1" ]; then
        cd $dir
        #rm *out && rm bck*
        #sbatch submit_lmp.sh
        #bash fes_plot.sh 
        rm -r ./resub_e_f
        echo $dir
        cd ../ 
    fi
done
