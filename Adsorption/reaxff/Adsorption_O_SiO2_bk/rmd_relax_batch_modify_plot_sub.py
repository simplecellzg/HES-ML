#!/usr/bin/env python3

import os
import re
import subprocess
import time
from pathlib import Path

def get_user_total_jobs():
    """获取当前用户所有正在运行和排队的作业总数"""
    try:
        # 使用squeue命令查询当前用户的所有作业
        user = os.environ.get('USER', '')
        result = subprocess.run(
            ["squeue", "-u", user, "-h", "-o", "%i %t"],
            capture_output=True,
            text=True,
            check=True
        )
        
        # 统计所有状态的作业（R=running, PD=pending, CG=completing等）
        jobs = result.stdout.strip().split('\n')
        active_jobs = 0
        for job in jobs:
            if job.strip():
                parts = job.split()
                if len(parts) >= 2:
                    status = parts[1]
                    # 统计运行中、等待中的作业
                    if status in ['R', 'PD', 'CG', 'CF']:
                        active_jobs += 1
        
        return active_jobs
    except Exception as e:
        print(f"  警告: 无法获取作业信息 - {e}")
        return 0

def show_job_details():
    """显示当前用户的作业详情"""
    try:
        user = os.environ.get('USER', '')
        result = subprocess.run(
            ["squeue", "-u", user, "-o", "%.10i %.30j %.8T %.10M %.6D %R"],
            capture_output=True,
            text=True,
            check=True
        )
        print("  当前作业详情:")
        lines = result.stdout.strip().split('\n')
        if len(lines) > 1:  # 有标题行和数据
            print(f"    {lines[0]}")  # 标题
            for line in lines[1:6]:  # 显示前5个作业
                print(f"    {line}")
            if len(lines) > 6:
                print(f"    ... 还有 {len(lines)-6} 个作业")
    except:
        pass

def wait_for_job_slot(max_total_jobs=16, check_interval=10, verbose=True):
    """等待直到总作业数小于限制"""
    wait_count = 0
    while True:
        total_jobs = get_user_total_jobs()
        
        if total_jobs < max_total_jobs:
            if wait_count > 0:
                print(f"  ✓ 作业槽位可用 (当前总任务: {total_jobs}/{max_total_jobs})")
            return total_jobs
        else:
            wait_count += 1
            timestamp = time.strftime("%H:%M:%S")
            print(f"  [{timestamp}] 总任务数已达上限: {total_jobs}/{max_total_jobs}, 等待 {check_interval} 秒...")
            
            # 每等待3次显示一次作业详情
            if verbose and wait_count % 3 == 1:
                show_job_details()
            
            time.sleep(check_interval)

def main():
    # 配置参数
    MAX_TOTAL_JOBS = 20    # 用户总作业数上限
    CHECK_INTERVAL = 10    # 检查间隔（秒）
    
    # 获取当前目录
    current_dir = Path.cwd()
    
    # 获取当前用户名
    username = os.environ.get('USER', 'unknown')
    print(f"当前用户: {username}")
    
    # 显示初始作业状态
    initial_jobs = get_user_total_jobs()
    print(f"初始总作业数: {initial_jobs}/{MAX_TOTAL_JOBS}")
    if initial_jobs > 0:
        show_job_details()
    
    # 查找所有RMD_Relax开头的文件夹
    rmd_dirs = sorted([d for d in current_dir.iterdir() 
                      if d.is_dir() and d.name.startswith("RMD_Relax")])
    
    if not rmd_dirs:
        print("\n没有找到以RMD_Relax开头的文件夹")
        return
    
    print(f"\n找到 {len(rmd_dirs)} 个RMD_Relax文件夹")
    print(f"最大总任务数限制: {MAX_TOTAL_JOBS}")
    print(f"检查间隔: {CHECK_INTERVAL} 秒")
    print("-" * 60)
    
    # 记录处理结果
    submitted_jobs = []
    failed_dirs = []
    skipped_dirs = []
    
    # 处理每个文件夹
    for idx, rmd_dir in enumerate(rmd_dirs, 1):
        print(f"\n[{idx}/{len(rmd_dirs)}] 处理文件夹: {rmd_dir.name}")
        
        # 检查提交脚本
        submit_script = rmd_dir / "submit_reaction_gpu_nature_plot.sh"
        
        if not submit_script.exists():
            print(f"  ⚠ 提交脚本不存在，跳过")
            skipped_dirs.append(rmd_dir.name)
            continue
        
        # 等待直到总作业数低于限制
        print(f"  检查作业队列...")
        current_total = wait_for_job_slot(MAX_TOTAL_JOBS, CHECK_INTERVAL, verbose=False)
        
        # 提交作业
        try:
            os.chdir(rmd_dir)
            print(f"  正在提交作业...")
            result = subprocess.run(
                ["sbatch", "--gpus=1", "submit_reaction_gpu_nature_plot.sh"],
                capture_output=True,
                text=True,
                check=True
            )
            job_output = result.stdout.strip()
            
            # 提取作业ID
            job_id_match = re.search(r'(\d+)', job_output)
            job_id = job_id_match.group(1) if job_id_match else "unknown"
            
            submitted_jobs.append((rmd_dir.name, job_id))
            print(f"  ✓ 成功提交作业 ID: {job_id}")
            print(f"  当前总任务数: {current_total + 1}/{MAX_TOTAL_JOBS}")
            
            # 短暂延迟，避免提交过快
            time.sleep(0.5)
            
        except subprocess.CalledProcessError as e:
            print(f"  ✗ sbatch提交失败: {e.stderr}")
            failed_dirs.append((rmd_dir.name, "sbatch失败"))
        except Exception as e:
            print(f"  ✗ 提交错误: {e}")
            failed_dirs.append((rmd_dir.name, str(e)))
        finally:
            os.chdir(current_dir)
    
    # 打印总结
    print(f"\n{'='*60}")
    print("处理总结:")
    print(f"  总文件夹数: {len(rmd_dirs)}")
    print(f"  ✓ 成功提交: {len(submitted_jobs)} 个")
    print(f"  ✗ 失败: {len(failed_dirs)} 个")
    print(f"  ⚠ 跳过: {len(skipped_dirs)} 个")
    
    if submitted_jobs:
        print(f"\n成功提交的作业:")
        for dir_name, job_id in submitted_jobs[:10]:  # 显示前10个
            print(f"  {dir_name:<30} Job ID: {job_id}")
        if len(submitted_jobs) > 10:
            print(f"  ... 还有 {len(submitted_jobs)-10} 个作业")
    
    if failed_dirs:
        print(f"\n失败的目录:")
        for dir_name, reason in failed_dirs:
            print(f"  {dir_name}: {reason}")
    
    # 最终状态
    print(f"\n最终作业队列状态:")
    final_jobs = get_user_total_jobs()
    print(f"用户 {username} 的总作业数: {final_jobs}")
    if final_jobs > 0:
        show_job_details()
    
    print("\n✓ 批处理完成！")

if __name__ == "__main__":
    main()
