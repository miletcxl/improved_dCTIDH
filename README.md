# dCTIDH: Fast & Deterministic CTIDH
This repository contains auxiliary material for the paper ["dCTIDH: Fast & Deterministic CTIDH"](https://eprint.iacr.org/2025/107).

Authors:
- [Fabio Campos](https://www.sopmac.org/) `<campos@sopmac.de>`
- [Andreas Hellenbrand](https://www.andhell.de/) `<andreas.hellenbrand@hs-rm.de>`
- [Michael Meyer](https://www.uni-regensburg.de/informatics-data-science/qpc/team/dr-michael-meyer/index.html) `<michael@random-oracles.org>`
- [Krijn Reijnders](https://krijnreijnders.com/) `<krijn@q1q1.nl>`

# Overview

## Building

```sh
# Only necessary first time (generally)
mkdir build && cd build
cmake ..

# If you want with instrumentation for constant-time behavior testing, the default value is OFF.
# Valgrind development files are used for this build option.
cmake -DENABLE_CT_TESTING=ON ..

# Building
make
```
This builds the executables for 3 versions:

- 2047m1l226 
- 2047m4l205
- 2047m6l194

## benchmarking

### Automated Benchmarking

The project includes automated benchmark targets that make it easy to run and analyze benchmarks for all enabled parameter sets:

```sh
# Run benchmarks for a specific parameter set
make benchmark-ctidh-2047m1l226

# Run all benchmarks and display a summary
make benchmark

# Show just the summary of previously run benchmarks 
make benchmark-summary
```

By default, benchmarks run with 100 iterations. You can change this by setting the `SECSIDH_BENCHMARK_RUNS` option:

```sh
# Configure with 500 benchmark runs
cmake -DSECSIDH_BENCHMARK_RUNS=500 ..

```

The benchmark results are:
1. Displayed in the console with formatted tables
2. Saved to files in the build directory:
   - Raw logs: `benchmark-ctidh-<param_set>.log`
   - Analysis results: `benchmark-ctidh-<param_set>-analysis.log`

### Manual Benchmarking

You can also run benchmarks manually using the executable options:
when in `build`:
```sh
usage: 	
    ./main/ctidh-2047m1l226.main				            // for a quick test
	./main//ctidh-2047m1l226.main -bact [number of runs]	// run benchmark for the action
	./main//ctidh-2047m1l226.main -bfp [number of runs]		// run benchmark for fp arithmetic
```

Each version contains benchmarking tools for the action, as well as the finite-field arithmetic,
which can be used with `-bact`, resp. `-bfp`.

The benchmarks can be analyzed using the `analyze_bench.py` script:
```sh
./main/ctidh-2047m1l226.main -bact 500 > bench_action.out
python3 ../analyze_bench.py < bench_action.out 
```

The analyze_bench.py script supports different output formats:
```sh
# Default grid format for terminal viewing
python3 ../analyze_bench.py < bench_action.out

# CSV format for importing into spreadsheets
python3 ../analyze_bench.py --format=csv < bench_action.out

# LaTeX format for academic papers
python3 ../analyze_bench.py --format=latex < bench_action.out
```
## Constant-time Check
If `DENABLE_CT_TESTING=ON`, `checkct` versions of the executable are created for all versions, which can be validated with `valgrind`.

For example, to validate that ctidh-2047m6l194 is constant-time:
```sh 
valgrind ./main/checkct-2047m6l194.main
```


## Parameter Search
We use greedy to find optimal configurations. The script explores the key space for primes with 151 to 226 ell_i and 1 to 18 batches.
We recommend to split up the search, as this will take a while (up to a month using 4 jobs with 48 threads each).

```sh
cd scripts
./greedywombats.py
```

## Licenses
See [LICENSE](https://github.com/PaZeZeVaAt/dCTIDH/blob/main/LICENSE) for the license concerning the code in this repository.

For the third-party code see their licenses:
- [CTIDH](http://ctidh.isogeny.org/): [http://ctidh.isogeny.org/high-ctidh-20210523/AUTHORS.md.html](http://ctidh.isogeny.org/high-ctidh-20210523/AUTHORS.md.html)
- [dCSIDH](https://github.com/kemtls-secsidh/code): [https://github.com/kemtls-secsidh/code/blob/main/LICENSE.md](https://github.com/kemtls-secsidh/code/blob/main/LICENSE.md)
- [sibc](https://github.com/JJChiDguez/sibc): [https://github.com/JJChiDguez/sibc/blob/master/LICENSE](https://github.com/JJChiDguez/sibc/blob/master/LICENSE)
