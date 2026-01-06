#!/usr/bin/env python3
"""
RMD-Relax批处理脚本
用于对GCMC/RMD的结果进行RMD-Relax处理
"""

import os
import subprocess
import time
import shutil
from pathlib import Path
import re

# 配置参数
TEMPERATURES = [500, 600, 700, 800, 900, 1000]  # 温度范围 (K)
# PRESSURES = [1, 2, 5, 10, 20, 50, 100]     # 压力范围 (atm)
# PRESSURES = [10, 5, 1, 0.5, 0.1]     # 压力范围 (bar)
PRESSURES = [10, 7.5, 5, 2.5, 1, 0.75, 0.5, 0.25, 0.1, 0.05]     # 压力范围 (bar)
MAX_JOBS = 20                                   # 最大并行任务数

# 源文件路径
SOURCE_DIR = "/home/bingxing2/home/scx7113/DEEPMD_PROJECT/yxb_test_20241109_clean_2_20251013_MD_reaxff/Adsorption_O_SiO2_RMD_Relax_DP_bk"
LMP_FILES_DIR = "/home/bingxing2/home/scx7113/DEEPMD_PROJECT/yxb_test_20241109_clean_2_20251013_MD_reaxff/lmp_files_reaxff"

def get_running_jobs():
    """获取当前用户正在运行的SLURM任务数量"""
    try:
        result = subprocess.run(['squeue', '-u', os.environ['USER'], '-h'], 
                              capture_output=True, text=True, check=True)
        jobs = result.stdout.strip().split('\n')
        return len([j for j in jobs if j.strip()])
    except subprocess.CalledProcessError:
        print("警告：无法获取SLURM任务状态")
        return 0

def wait_for_job_slot():
    """等待直到有可用的任务槽位"""
    while True:
        current_jobs = get_running_jobs()
        if current_jobs < MAX_JOBS:
            return
        print(f"当前运行任务数: {current_jobs}/{MAX_JOBS}，等待槽位...")
        time.sleep(30)

def get_job_id(submit_output):
    """从sbatch输出中提取作业ID"""
    match = re.search(r'Submitted batch job (\d+)', submit_output)
    if match:
        return match.group(1)
    return None

def modify_relax_input(input_file, temperature, pressure, lmp_filename):
    """修改RMD-Relax的LAMMPS输入文件"""
    with open(input_file, 'r') as f:
        content = f.read()
    
    # 修改温度变量
    content = re.sub(r'variable T equal \d+', f'variable T equal {temperature}', content)
    
    # 修改第一个read_data命令 (nve.lmp -> {温度}k.lmp)
    content = re.sub(r'read_data nve\.lmp', f'read_data {lmp_filename}', content)
    
    # 修改第二个read_data命令，使用新的文件名格式
    gcmc_filename = f"final_gcmc_{temperature}K_{pressure}atm.lmp"
    content = re.sub(r'read_data gcmc_last\.lmp', f'read_data {gcmc_filename}', content)
    # 也处理可能的gcmc_50.lmp引用
    content = re.sub(r'read_data gcmc_50\.lmp', f'read_data {gcmc_filename}', content)
    
    with open(input_file, 'w') as f:
        f.write(content)

def check_gcmc_output(temperature, pressure):
    """检查GCMC输出文件是否存在"""
    gcmc_dir = f"GCMC_RMD_{temperature}k_{pressure}atm"
    gcmc_filename = f"final_gcmc_{temperature}K_{pressure}atm.lmp"
    gcmc_output = os.path.join(gcmc_dir, gcmc_filename)
    return os.path.exists(gcmc_output)

def submit_rmd_relax_job(temperature, pressure):
    """提交单个RMD-Relax任务"""
    # 检查GCMC输出是否存在
    if not check_gcmc_output(temperature, pressure):
        gcmc_filename = f"final_gcmc_{temperature}K_{pressure}atm.lmp"
        print(f"警告：找不到GCMC输出文件 GCMC_RMD_{temperature}k_{pressure}atm/{gcmc_filename}，跳过...")
        return None
    
    # 创建工作目录名称
    work_dir = f"RMD_Relax_{temperature}k_{pressure}atm"
    
    # 如果目录已存在，询问是否覆盖
    if os.path.exists(work_dir):
        print(f"警告：目录 {work_dir} 已存在，跳过...")
        return None
    
    print(f"\n开始处理RMD-Relax: T={temperature}K, P={pressure}atm")
    
    # 1. 创建工作目录
    os.makedirs(work_dir, exist_ok=True)
    
    # 2. 复制源文件
    print(f"  复制文件到 {work_dir}...")
    for item in os.listdir(SOURCE_DIR):
        src = os.path.join(SOURCE_DIR, item)
        dst = os.path.join(work_dir, item)
        if os.path.isfile(src):
            shutil.copy2(src, dst)
        elif os.path.isdir(src):
            shutil.copytree(src, dst, dirs_exist_ok=True)
    
    # 3. 复制GCMC结果文件
    gcmc_filename = f"final_gcmc_{temperature}K_{pressure}atm.lmp"
    gcmc_output = f"GCMC_RMD_{temperature}k_{pressure}atm/{gcmc_filename}"
    gcmc_dest = os.path.join(work_dir, gcmc_filename)
    if os.path.exists(gcmc_output):
        shutil.copy2(gcmc_output, gcmc_dest)
        print(f"  复制GCMC结果文件 {gcmc_filename}")
    else:
        print(f"  错误：找不到GCMC结果文件 {gcmc_output}")
        return None
    
    # 4. 复制特定温度的lmp文件
    lmp_filename = f"{temperature}k.lmp"
    lmp_source = os.path.join(LMP_FILES_DIR, lmp_filename)
    lmp_dest = os.path.join(work_dir, lmp_filename)
    if os.path.exists(lmp_source):
        shutil.copy2(lmp_source, lmp_dest)
        print(f"  复制 {lmp_filename} 到工作目录")
    else:
        print(f"  警告：找不到文件 {lmp_source}")
        return None
    
    # 5. 修改LAMMPS输入文件
    input_file = os.path.join(work_dir, "in.flux_beta_long_box_abs_gcmc_compare_reaxff")
    if os.path.exists(input_file):
        modify_relax_input(input_file, temperature, pressure, lmp_filename)
        print(f"  修改输入文件参数: T={temperature}K, P={pressure}atm")
    else:
        print(f"  错误：找不到输入文件 {input_file}")
        return None
    
    # 6. 进入工作目录并提交任务
    original_dir = os.getcwd()
    os.chdir(work_dir)
    
    try:
        # 只提交RMD-Relax计算任务，不进行后处理作图
        print(f"  提交RMD-Relax计算任务...")
        result = subprocess.run(['sbatch', '--gpus=1', 'submit_gpu_lmp25_beta_long_box_abs_gcmc_compare.sh'],
                              capture_output=True, text=True, check=True)
        job_id = get_job_id(result.stdout)
        print(f"  RMD-Relax计算任务已提交，作业ID: {job_id}")
        
        return job_id
        
    except subprocess.CalledProcessError as e:
        print(f"  错误：任务提交失败 - {e}")
        return None
    finally:
        os.chdir(original_dir)

def main():
    """主函数"""
    print("="*60)
    print("RMD-Relax批处理脚本")
    print(f"温度范围: {TEMPERATURES} K")
    print(f"压力范围: {PRESSURES} atm")
    print(f"总任务数: {len(TEMPERATURES) * len(PRESSURES)}")
    print(f"最大并行任务数: {MAX_JOBS}")
    print("="*60)
    
    # 检查是否有GCMC结果
    print("\n检查GCMC结果文件...")
    available_jobs = []
    for temperature in TEMPERATURES:
        for pressure in PRESSURES:
            if check_gcmc_output(temperature, pressure):
                available_jobs.append((temperature, pressure))
                gcmc_filename = f"final_gcmc_{temperature}K_{pressure}atm.lmp"
                print(f"  找到: GCMC_RMD_{temperature}k_{pressure}atm/{gcmc_filename}")
    
    print(f"\n找到 {len(available_jobs)} 个可处理的GCMC结果")
    
    if len(available_jobs) == 0:
        print("错误：没有找到任何GCMC结果文件，请先运行GCMC批处理脚本")
        return
    
    # 记录所有任务
    all_jobs = []
    
    # 批量提交任务
    for temperature, pressure in available_jobs:
        # 等待有可用槽位
        wait_for_job_slot()
        
        # 提交任务
        job_info = submit_rmd_relax_job(temperature, pressure)
        if job_info:
            all_jobs.append({
                'temperature': temperature,
                'pressure': pressure,
                'job_id': job_info,
                'work_dir': f"RMD_Relax_{temperature}k_{pressure}atm"
            })
        
        # 短暂延迟
        time.sleep(2)
    
    print("\n="*60)
    print(f"所有RMD-Relax计算任务已提交完成")
    print(f"成功提交的任务数: {len(all_jobs)}")
    print("="*60)
    
    # 保存任务信息
    with open('rmd_relax_jobs.txt', 'w') as f:
        f.write("Temperature(K)\tPressure(atm)\tJobID\tWorkDir\n")
        for job in all_jobs:
            f.write(f"{job['temperature']}\t{job['pressure']}\t{job['job_id']}\t{job['work_dir']}\n")
    
    print("\n任务信息已保存到 rmd_relax_jobs.txt")

if __name__ == "__main__":
    main()
