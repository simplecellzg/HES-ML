mkdir -p logs  # 创建日志目录
cd frames  # 进入frame目录处理xyz文件

for xyz in *.xyz; do
    base="${xyz%.*}"
    atomsk "$xyz" lmp 
    ../lmp_atom2charge.sh "$base".lmp
done

cd ..  # 返回上级目录