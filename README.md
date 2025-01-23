# dCTIHD - Deterministic CTIDH from WOMBats

## Building

```sh
# Only necessary first time (generally)
mkdir build && cd build
cmake ..

# If you want with instrumentation for constant-time behavior testing, the default value is OFF. Valgrind development files are used for this build option.
cmake -DENABLE_CT_TESTING=ON ..

# Building
make
```
this builds the executeables for 3 versions:

- 2047m1l226 
- 2047m4l205
- 2047m6l194

## benchmarking
```sh
usage: 	
    ./ctidh-2047m1l226.main				            // for a quick test
	./ctidh-2047m1l226.main -bact [number of runs]	// run benchmark for the action
	./ctidh-2047m1l226.main -bfp [number of runs]	// run benchmark for fp arithmetic
```

Each version contains benchmarking tools for the action, as well as the finite-field arithmetic,
which can be used with `-bact`, resp. `-bfp`.

The benchmarks can be analyzed using the `analyze_bench.py` script:
```sh
./main/ctidh-2047m1l226.main -bact 500 > bench_action.out
./analyze_bench.py < bench_action.out 
```

## constant-time check
If `DENABLE_CT_TESTING=ON`, `checkct` versions of the executable are created for all versions, which can be validated with `valgrind`.

e.G.:
```sh 
valgrind ./main/checkct-2047m6l194.main
```


## parameter search
We use greedy to find optimal configurations. The script explors the keyspace for primes with 151 to 226 ell_i and 1 to 18 batches.
We recomend to split up the search, as this will take a while (up to a month using 4 jobs with 48 threads each).

```sh
cd scripts
./greedywombats.py
```
