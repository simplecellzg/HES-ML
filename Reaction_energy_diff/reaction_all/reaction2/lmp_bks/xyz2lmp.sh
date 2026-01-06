mkdir -p logs  # 创建日志目录
cd frames  # 进入frame目录处理xyz文件
module load atomsk/11.2
for xyz in *.xyz; do
    base="${xyz%.*}"
    atomsk "$xyz" lmp 
    ../lmp_atom2charge.sh "$base".lmp
    
    # 修改z轴边界值从"0.000000000000 22.000000000000 zlo zhi"为"-20.0 40.000000000000 zlo zhi"
    sed -i 's/\s*0\.0*\s\+22\.0*\s\+zlo zhi/      -20.0      40.000000000000  zlo zhi/' "$base".lmp
done

cd ..  # 返回上级目录
