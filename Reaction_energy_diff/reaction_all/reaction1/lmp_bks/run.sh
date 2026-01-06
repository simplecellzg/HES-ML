module purge
source ~/software/deepmd-kit/bin/activate
module load mpi/oneAPI/2022.1
export PATH=/public1/home/sch9516/software/0703/lammps-patch_27Jun2024/src:$PATH
export LD_LIBRARY_PATH=/public1/home/sch9516/software/deepmd-kit/lib:$LD_LIBRARY_PATH
export LD_LIBRARY_PATH=/public1/home/sch9516/software/0703/lammps-patch_27Jun2024/lib/plumed/plumed-new/plumed2-2.9.1/install/lib:$LD_LIBRARY_PATH


echo "Frame  Energy(kcal/mol)" > energies.csv

cd frames  # 进入frame目录处理lmp文件

for lmp in *.lmp; do
    base="${lmp%.*}"
    log="../logs/$base.log"
    
    # 运行LAMMPS计算能量
    lmp -var datafile "$lmp" -in ../compute_energy.in -log "$log"
    
    # 提取势能（严格匹配步数0对应的PotEng）
    energy_ev=$(grep -E '^[[:space:]]*0[[:space:]]+' "$log" | awk '{print $2}')
    
    # 转换单位：eV 到 kcal/mol (1 eV = 23.8 kcal/mol)
    energy_kcal=$(echo "$energy_ev / 0.042" | bc -l)
    
    # 保留4位小数
    energy_kcal=$(printf "%.4f" $energy_kcal)
    
    echo "$base  $energy_kcal" >> ../energies.csv
done

cd ..
