
#!/usr/bin/env python3
import subprocess
import re
import os
# --- 配置 ---
# 你要运行的可执行文件的名字
EXECUTABLE_NAME = "build/main/ctidh-2047m1l226_normal.main"
# 运行的总次数
NUM_RUNS = 50

# --- 脚本主体 ---

# 确保可执行文件存在且在当前目录下
executable_path = os.path.join(".", EXECUTABLE_NAME)
if not os.path.exists(executable_path):
    print(f"错误: 可执行文件 '{EXECUTABLE_NAME}' 不在当前目录中。")
    print("请确保你在 'build' 目录下运行此脚本。")
    exit(1)

# 用于存储每次运行结果的列表
results = {
    "alice_keygen": [],
    "bob_keygen": [],
    "alice_share": [],
    "bob_share": [],
}

print(f"将要运行 '{EXECUTABLE_NAME}' {NUM_RUNS} 次，请稍候...")
print("-" * 40)

for i in range(1, NUM_RUNS + 1):
    print(f"--> 正在进行第 {i}/{NUM_RUNS} 次测试...", end='\r', flush=True)
    
    try:
        # 运行你的C程序并捕获其输出
        process = subprocess.run(
            [executable_path], 
            capture_output=True, 
            text=True, 
            check=True
        )
        output = process.stdout

        # 使用正则表达式从输出中提取时钟周期数
        # findall 会按顺序找到所有匹配项
        keygen_cycles = re.findall(r"Clock cycles \(millions\):.*?(\d+\.\d+)", output)
        share_cycles = re.findall(r"Clock cycles \(millions\) \[including validation\]:.*?(\d+\.\d+)", output)

        if len(keygen_cycles) == 2 and len(share_cycles) == 2:
            results["alice_keygen"].append(float(keygen_cycles[0]))
            results["bob_keygen"].append(float(keygen_cycles[1]))
            results["alice_share"].append(float(share_cycles[0]))
            results["bob_share"].append(float(share_cycles[1]))
        else:
            print(f"\n警告: 第 {i} 次运行时未能解析出所有数据，已跳过。")

    except subprocess.CalledProcessError as e:
        print(f"\n错误: 第 {i} 次运行时程序崩溃。")
        print(e.stderr)
        # 如果程序崩溃，可以选择停止或继续
        # break 
        
    except Exception as e:
        print(f"\n发生未知错误: {e}")
        break

print("\n\n测试完成！正在计算平均结果...")
print("=" * 40)

# 计算并打印平均值、最小值和最大值
print(f"{'测量项':<25} | {'平均耗时':^15} | {'最快一次':^15} | {'最慢一次':^15}")
print(f"{'-'*25: <25} | {'-'*15:^15} | {'-'*15:^15} | {'-'*15:^15}")

for name, times in results.items():
    if times: # 确保列表不为空
        avg_time = sum(times) / len(times)
        min_time = min(times)
        max_time = max(times)
        print(f"{name:<25} | {avg_time:^15.3f} | {min_time:^15.3f} | {max_time:^15.3f}")

print("=" * 40)
print("提示: 所有时间的单位都是 '百万时钟周期'。")
