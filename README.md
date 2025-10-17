# Our CTIDH-H
# Overview
主要代码基于[dCTIDH](https://github.com/PaZeZeVaAt/dCTIDH).

## Building
代码需要 ADX (ADOX and ADCX) 指令，请确认您的 cpu 包含上述指令
```sh
# 确认可以使用 ADX 指令
cat /proc/cpuinfo | grep adx

# 仅第一次需要
mkdir build && cd build
cmake ..

# 开启恒定时间测试（默认关闭）
cmake -DENABLE_CT_TESTING=ON ..

# Building
make
```
构建三个可执行文件

- 2047m1l226 
- 2047m4l205
- 2047m6l194

我们主要分析了 2047m1l226 

## benchmarking

### Automated Benchmarking

该项目包含自动化基准测试
```sh
# Run benchmarks for a specific parameter set
make benchmark-ctidh-2047m1l226

# Run all benchmarks and display a summary
make benchmark

# Show just the summary of previously run benchmarks 
make benchmark-summary
```

默认情况下，基准测试会运行 100 次迭代，这将花费几个小时。您可以通过设置 `SECSIDH_BENCHMARK_RUNS` 选项来更改这一点：

```sh
# Configure with 5 benchmark runs
cmake -DSECSIDH_BENCHMARK_RUNS=5 ..

```

基准测试结果已保存到构建目录中的文件：
   - 原始日志: `benchmark-ctidh-<param_set>.log`
   - 分析结果: `benchmark-ctidh-<param_set>-analysis.log`

### Manual Benchmarking

您也可以使用可执行文件选项手动运行基准测试：
在 `build` 目录下:
```sh
usage: 	
    ./main/ctidh-2047m1l226.main                            # for a quick test
	./main//ctidh-2047m1l226.main -bact [number of runs]    # run benchmark for the action
	./main//ctidh-2047m1l226.main -bfp [number of runs]     # run benchmark for fp arithmetic
```

每个版本都包含用于该操作的基准测试工具，以及可与 `-bact` 或 `-bfp` 一起使用的有限域算术。

可以使用 `analyze_bench.py` 脚本来分析动作基准：
```sh
./main/ctidh-2047m1l226.main -bact 100 > bench_action.out
python3 ../analyze_bench.py < bench_action.out 
```

analyze_bench.py 脚本支持不同的输出格式：
```sh
# 默认网格格式
python3 ../analyze_bench.py < bench_action.out

# CSV 格式
python3 ../analyze_bench.py --format=csv < bench_action.out

# LaTeX 格式
python3 ../analyze_bench.py --format=latex < bench_action.out
```

## constant-time check
如果 `DENABLE_CT_TESTING=ON`，则会为所有版本创建可执行文件的 `checkct` 版本，可以使用 `valgrind` 进行验证。

在 `build` 目录下:
```sh 
cmake -DENABLE_CT_TESTING=ON ..

make  # 所有版本

make checkct-2047m1l226.main  # 对于选定的版本
make checkct-2047m4l205.main
make checkct-2047m6l194.main

# 运行 'valgrind' 测试
valgrind ./main/checkct-2047m1l226.main
valgrind ./main/checkct-2047m4l205.main
valgrind ./main/checkct-2047m6l194.main
```

## parameter search and new primes
我们先大步搜索最佳范围，然后使用贪婪算法来寻找最优配置。脚本会探索关键空间，用于 ell_i 在 190 到 226 之间、批次数在 15 到 20 之间的质数。我们建议分批进行搜索，因为这可能需要较长时间。

```sh
# 初步搜索
cd scripts/greedy/
./cxl_greedy.py

#精细搜索
cd scripts/greedy/
./new_wombats.py
```

要为新的参数集添加新素数所需的文件，请使用 `scripts/new_prime` 中的脚本

```sh
cd scripts/new_primes/genFiles
./autogen

cd scripts/new_primes/genSteps
./autogen

# 生成文件移至common
```