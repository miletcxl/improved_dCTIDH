#!/usr/bin/env python3
import subprocess
import os
import time  # 引入 time 模块

# --- 配置 ---
# 你要运行的可执行文件的名字
EXECUTABLE_NAME = "build/main/ctidh-2047m1l226.main"
# 运行的总次数
NUM_RUNS = 50

# --- 脚本主体 ---

# 确保可执行文件存在且在当前目录下
executable_path = os.path.join(".", EXECUTABLE_NAME)
if not os.path.exists(executable_path):
    print(f"错误: 可执行文件 '{EXECUTABLE_NAME}' 不在当前目录中。")
    print("请确保你在 'build' 目录下运行此脚本。")
    exit(1)

# 用于存储每次运行时间的列表
execution_times = []

print(f"将要运行 '{EXECUTABLE_NAME}' {NUM_RUNS} 次，并测量其执行时间...")
print("-" * 50)

for i in range(1, NUM_RUNS + 1):
    print(f"--> 正在进行第 {i}/{NUM_RUNS} 次测试...", end='\r', flush=True)
    
    try:
        # 记录开始时间
        start_time = time.perf_counter()

        # 运行你的C程序
        # capture_output=True 会阻止程序输出打印到控制台，如果想看到可以设为False
        subprocess.run(
            [executable_path], 
            capture_output=True, 
            text=True, 
            check=True
        )
        
        # 记录结束时间
        end_time = time.perf_counter()

        # 计算经过的时间并添加到列表中
        elapsed_time = end_time - start_time
        execution_times.append(elapsed_time)

    except subprocess.CalledProcessError as e:
        print(f"\n错误: 第 {i} 次运行时程序崩溃。")
        print(e.stderr)
        # 如果程序崩溃，可以选择停止或继续
        # break 
        
    except Exception as e:
        print(f"\n发生未知错误: {e}")
        break

print("\n\n测试完成！正在计算平均结果...")
print("=" * 50)

# 计算并打印平均值、最小值和最大值
if execution_times: # 确保列表不为空
    avg_time = sum(execution_times) / len(execution_times)
    min_time = min(execution_times)
    max_time = max(execution_times)
    
    print(f"对 '{EXECUTABLE_NAME}' 的性能测试结果:")
    print(f"{'统计项':<15} | {'执行时间 (秒)':^20}")
    print(f"{'-'*15: <15} | {'-'*20:^20}")
    print(f"{'平均耗时':<15} | {avg_time:^20.6f}")
    print(f"{'最快一次':<15} | {min_time:^20.6f}")
    print(f"{'最慢一次':<15} | {max_time:^20.6f}")

else:
    print("没有成功的运行记录，无法计算结果。")

print("=" * 50)