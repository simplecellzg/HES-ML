#!/usr/bin/env python3
"""
GCMC/RMD批处理脚本
用于批量提交基于深度势deepmd的混合GCMC/RMD任务
支持多文件夹并行处理，GCMC完成后自动提交作图任务
"""

import os
import subprocess
import time
import shutil
from pathlib import Path
import re
from collections import defaultdict
from datetime import datetime

# 配置参数
TEMPERATURES = [500, 600, 700, 800, 900, 1000]  # 温度范围 (K)
# PRESSURES = [1, 2, 5, 10, 20, 50, 100]     # 压力范围 (atm)
# PRESSURES = [10, 5, 1, 0.5, 0.1]     # 压力范围 (bar)
PRESSURES = [10, 7.5, 5, 2.5, 1, 0.75, 0.5, 0.25, 0.1, 0.05]     # 压力范围 (bar)
MAX_JOBS = 20                                   # 最大并行任务数
CHECK_INTERVAL = 30                             # 检查间隔（秒）

# 源文件路径
SOURCE_DIR = "/home/bingxing2/home/scx7113/DEEPMD_PROJECT/yxb_test_20241109_clean_2_20251013_MD_deepmd/Adsorption_O_SiO2_bk/Adsorption_O_SiO2_GCMC_RMD_DP_bk"
LMP_FILES_DIR = "/home/bingxing2/home/scx7113/DEEPMD_PROJECT/yxb_test_20241109_clean_2_20251013_MD_deepmd/Adsorption_O_SiO2_bk/lmp_files_deepmd"

class JobManager:
    """任务管理器"""
    def __init__(self):
        self.gcmc_jobs = {}  # {job_id: {'T': temp, 'P': pressure, 'dir': work_dir}}
        self.plot_jobs = {}  # {job_id: {'T': temp, 'P': pressure, 'dir': work_dir}}
        self.completed_gcmc = set()
        self.completed_plot = set()
        self.failed_jobs = []
        
    def add_gcmc_job(self, job_id, temperature, pressure, work_dir):
        """添加GCMC任务记录"""
        self.gcmc_jobs[job_id] = {
            'T': temperature,
            'P': pressure,
            'dir': work_dir,
            'status': 'running',
            'submit_time': datetime.now()
        }
    
    def add_plot_job(self, job_id, temperature, pressure, work_dir):
        """添加作图任务记录"""
        self.plot_jobs[job_id] = {
            'T': temperature,
            'P': pressure,
            'dir': work_dir,
            'status': 'running',
            'submit_time': datetime.now()
        }
    
    def get_job_status(self, job_id):
        """获取作业状态"""
        try:
            result = subprocess.run(['squeue', '-j', job_id, '-h'], 
                                  capture_output=True, text=True, check=True)
            if result.stdout.strip():
                # 作业仍在运行
                return 'running'
            else:
                # 作业已完成，检查是否成功
                return 'completed'
        except subprocess.CalledProcessError:
            # 作业不在队列中，认为已完成
            return 'completed'
    
    def check_and_submit_plot_jobs(self):
        """检查GCMC任务状态，完成的提交作图任务"""
        newly_completed = []
        
        for job_id, job_info in list(self.gcmc_jobs.items()):
            if job_id in self.completed_gcmc:
                continue
                
            status = self.get_job_status(job_id)
            
            if status == 'completed':
                self.completed_gcmc.add(job_id)
                job_info['status'] = 'completed'
                print(f"\n✓ GCMC任务完成: T={job_info['T']}K, P={job_info['P']}atm (Job ID: {job_id})")
                
                # 提交对应的作图任务
                plot_job_id = submit_plot_job(job_info['dir'], job_info['T'], job_info['P'])
                if plot_job_id:
                    self.add_plot_job(plot_job_id, job_info['T'], job_info['P'], job_info['dir'])
                    newly_completed.append(job_info)
                else:
                    self.failed_jobs.append({**job_info, 'reason': 'plot_submission_failed'})
        
        return newly_completed
    
    def check_plot_jobs(self):
        """检查作图任务状态"""
        for job_id, job_info in list(self.plot_jobs.items()):
            if job_id in self.completed_plot:
                continue
                
            status = self.get_job_status(job_id)
            
            if status == 'completed':
                self.completed_plot.add(job_id)
                job_info['status'] = 'completed'
                print(f"✓ 作图任务完成: T={job_info['T']}K, P={job_info['P']}atm (Job ID: {job_id})")
    
    def get_running_count(self):
        """获取当前运行的任务总数"""
        running_gcmc = len([j for j in self.gcmc_jobs.values() 
                           if j.get('status') == 'running'])
        running_plot = len([j for j in self.plot_jobs.values() 
                          if j.get('status') == 'running'])
        return running_gcmc + running_plot
    
    def all_completed(self):
        """检查是否所有任务都已完成"""
        total_expected = len(TEMPERATURES) * len(PRESSURES)
        return len(self.completed_plot) == total_expected

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
        time.sleep(CHECK_INTERVAL)

def get_job_id(submit_output):
    """从sbatch输出中提取作业ID"""
    match = re.search(r'Submitted batch job (\d+)', submit_output)
    if match:
        return match.group(1)
    return None

def modify_lammps_input(input_file, temperature, pressure, lmp_filename):
    """修改LAMMPS输入文件"""
    with open(input_file, 'r') as f:
        content = f.read()
    
    content = re.sub(r'variable T equal \d+', f'variable T equal {temperature}', content)
    content = re.sub(r'variable P equal \d+', f'variable P equal {pressure}', content)
    content = re.sub(r'read_data nve\.lmp', f'read_data {lmp_filename}', content)
    
    with open(input_file, 'w') as f:
        f.write(content)

def prepare_and_submit_gcmc(temperature, pressure):
    """准备工作目录并提交GCMC任务"""
    work_dir = f"GCMC_RMD_{temperature}k_{pressure}atm"
    
    if os.path.exists(work_dir):
        print(f"警告：目录 {work_dir} 已存在，跳过...")
        return None, None
    
    print(f"准备任务: T={temperature}K, P={pressure}atm")
    
    # 1. 创建工作目录
    os.makedirs(work_dir, exist_ok=True)
    
    # 2. 复制源文件
    for item in os.listdir(SOURCE_DIR):
        src = os.path.join(SOURCE_DIR, item)
        dst = os.path.join(work_dir, item)
        if os.path.isfile(src):
            shutil.copy2(src, dst)
        elif os.path.isdir(src):
            shutil.copytree(src, dst, dirs_exist_ok=True)
    
    # 3. 复制特定温度的lmp文件
    lmp_filename = f"{temperature}k.lmp"
    lmp_source = os.path.join(LMP_FILES_DIR, lmp_filename)
    lmp_dest = os.path.join(work_dir, lmp_filename)
    if os.path.exists(lmp_source):
        shutil.copy2(lmp_source, lmp_dest)
    else:
        print(f"  错误：找不到文件 {lmp_source}")
        return None, None
    
    # 4. 修改LAMMPS输入文件
    input_file = os.path.join(work_dir, "in.flux_beta_long_box_abs_gcmc")
    if os.path.exists(input_file):
        modify_lammps_input(input_file, temperature, pressure, lmp_filename)
    else:
        print(f"  错误：找不到输入文件 {input_file}")
        return None, None
    
    # 5. 提交GCMC任务
    original_dir = os.getcwd()
    os.chdir(work_dir)
    
    try:
        result = subprocess.run(['sbatch', '--gpus=1', 'submit_gpu_lmp25_beta_long_box_abs_gcmc.sh'],
                              capture_output=True, text=True, check=True)
        job_id = get_job_id(result.stdout)
        print(f"  → GCMC任务已提交，作业ID: {job_id}")
        return job_id, work_dir
        
    except subprocess.CalledProcessError as e:
        print(f"  错误：GCMC任务提交失败 - {e}")
        return None, None
    finally:
        os.chdir(original_dir)

def submit_plot_job(work_dir, temperature, pressure):
    """提交作图任务"""
    original_dir = os.getcwd()
    os.chdir(work_dir)
    
    try:
        print(f"  → 提交作图任务: T={temperature}K, P={pressure}atm")
        result = subprocess.run(['sbatch', '--gpus=1', 'submit_reaction_gpu_nature_plot.sh'],
                              capture_output=True, text=True, check=True)
        job_id = get_job_id(result.stdout)
        print(f"    作图任务已提交，作业ID: {job_id}")
        return job_id
        
    except subprocess.CalledProcessError as e:
        print(f"  错误：作图任务提交失败 - {e}")
        return None
    finally:
        os.chdir(original_dir)

def print_progress(job_manager):
    """打印进度信息"""
    total_tasks = len(TEMPERATURES) * len(PRESSURES)
    gcmc_completed = len(job_manager.completed_gcmc)
    plot_completed = len(job_manager.completed_plot)
    
    print(f"\n{'='*60}")
    print(f"进度更新 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"GCMC任务: {gcmc_completed}/{total_tasks} 完成")
    print(f"作图任务: {plot_completed}/{total_tasks} 完成")
    print(f"运行中的任务数: {job_manager.get_running_count()}")
    print(f"{'='*60}")

def main():
    """主函数"""
    print("="*60)
    print("GCMC/RMD并行批处理脚本")
    print(f"温度范围: {TEMPERATURES} K")
    print(f"压力范围: {PRESSURES} atm")
    print(f"总任务数: {len(TEMPERATURES) * len(PRESSURES)}")
    print(f"最大并行任务数: {MAX_JOBS}")
    print("="*60)
    
    job_manager = JobManager()
    
    # 第一阶段：并行提交所有GCMC任务
    print("\n第一阶段：提交GCMC任务")
    print("-"*40)
    
    for temperature in TEMPERATURES:
        for pressure in PRESSURES:
            # 等待有可用槽位
            wait_for_job_slot()
            
            # 准备并提交GCMC任务
            job_id, work_dir = prepare_and_submit_gcmc(temperature, pressure)
            if job_id:
                job_manager.add_gcmc_job(job_id, temperature, pressure, work_dir)
            
            time.sleep(2)  # 短暂延迟
    
    print(f"\n所有GCMC任务已提交，共 {len(job_manager.gcmc_jobs)} 个")
    
    # 第二阶段：监控GCMC任务并提交作图任务
    print("\n第二阶段：监控任务并自动提交作图任务")
    print("-"*40)
    
    check_counter = 0
    while not job_manager.all_completed():
        # 检查GCMC任务状态，完成的自动提交作图任务
        job_manager.check_and_submit_plot_jobs()
        
        # 检查作图任务状态
        job_manager.check_plot_jobs()
        
        # 定期打印进度
        check_counter += 1
        if check_counter % 4 == 0:  # 每4次检查打印一次进度
            print_progress(job_manager)
        
        # 如果还有未完成的任务，等待后继续检查
        if not job_manager.all_completed():
            time.sleep(CHECK_INTERVAL)
    
    # 完成总结
    print("\n" + "="*60)
    print("所有任务已完成！")
    print(f"成功完成的GCMC任务: {len(job_manager.completed_gcmc)}")
    print(f"成功完成的作图任务: {len(job_manager.completed_plot)}")
    if job_manager.failed_jobs:
        print(f"失败的任务: {len(job_manager.failed_jobs)}")
        for job in job_manager.failed_jobs:
            print(f"  - T={job['T']}K, P={job['P']}atm: {job['reason']}")
    print("="*60)
    
    # 保存任务信息
    with open('gcmc_rmd_jobs_log.txt', 'w') as f:
        f.write("Temperature(K)\tPressure(atm)\tWorkDir\tGCMC_JobID\tPlot_JobID\tStatus\n")
        for gcmc_id, gcmc_info in job_manager.gcmc_jobs.items():
            # 找到对应的作图任务
            plot_id = None
            for pid, pinfo in job_manager.plot_jobs.items():
                if pinfo['T'] == gcmc_info['T'] and pinfo['P'] == gcmc_info['P']:
                    plot_id = pid
                    break
            
            status = 'completed' if gcmc_id in job_manager.completed_gcmc else 'unknown'
            f.write(f"{gcmc_info['T']}\t{gcmc_info['P']}\t{gcmc_info['dir']}\t{gcmc_id}\t{plot_id or 'N/A'}\t{status}\n")
    
    print("\n任务日志已保存到 gcmc_rmd_jobs_log.txt")

if __name__ == "__main__":
    main()
