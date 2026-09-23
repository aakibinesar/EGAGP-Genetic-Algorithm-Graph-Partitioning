# Implementation Notes

This repo contains two implementations of the algorithm described in the paper
below: the **original Java implementation** from the thesis, and a **Python
port** with NumPy optimizations. Both are kept for reference; the Java code is
unmodified from the original thesis submission.

> Shahriar, Fahim, Aakib Bin Nesar, Naweed Mohammad Mahbub, and Swakkhar
> Shatabda. "EGAGP: An enhanced genetic algorithm for producing efficient
> graph partitions." In *2017 4th International Conference on Networking,
> Systems and Security (NSysS)*, pp. 1-9. IEEE, 2017. ([paper PDF](./EGAGP.pdf))

## Repo layout

```
java/     original Java implementation (unmodified)
python/   Python port + tooling
EGAGP.pdf the published paper
```

## `java/`

The five original classes (`GA`, `Algorithm`, `FitnessCalc`, `Individual`,
`Population`). `GA.main()` points at a hardcoded Windows path
(`C:\GAThesis\Data\DataSet\...`) from the original author's machine and is not
runnable as-is without adjusting that path and supplying data files.

## `python/`

A NumPy-optimized port of the same algorithm:

- `fitness_calc.py`, `individual.py`, `population.py`, `algorithm.py` — core
  GA (mirrors the Java classes 1:1)
- `egagp.py` — CLI driver (`python3 egagp.py <data_dir>`)
- `requirements.txt` — just `numpy`

Run it:

```bash
cd python
pip install -r requirements.txt
python3 egagp.py data
```

### Dataset: why it's synthetic

The paper states (Section V-A) the real datasets were generated with the
"Eppstein power law generator" per the methodology in Islam et al. (2015) and
Verbelen et al. (2013) — but those exact instance files were never published
and no longer exist. `generate_dataset.py` is a documented substitute, **not**
a reproduction:

- Application graph: Barabási–Albert preferential attachment (a standard way
  to get sparse, power-law-ish degree distributions)
- Machine graph: a shuffled ring + a few extra random links, matching the
  paper's "geographically neighboring machines" rationale
- Weights/capacities scaled so a feasible partition always exists

```bash
python3 generate_dataset.py --vertices 200 --instances 10 --replicate-name G200 --output-dir data
```

`data/` already contains 10 replicate instances for every vertex count in the
paper's Table II (100–900), 90 files total.

**Results on this synthetic data are not comparable to the paper's published
Table II numbers** — different graphs entirely. They validate that the port
runs correctly and behaves like a genetic algorithm should, not that it
reproduces the published results.

### Testing

- `test_runner.py` — functional smoke test (data loading, individual
  generation, fitness calc, population, crossover, evolution)
- `test_incremental_fitness.py` — correctness check for the trickiest part of
  the port: `Individual.set_gene()`'s O(1) incremental fitness update vs. a
  full O(n²) recomputation, across 2000 randomized mutations. This directly
  validates the logic the original Java author left a commented-out debug
  assertion for but never actually verified.

```bash
cd python
python3 test_runner.py
python3 test_incremental_fitness.py
```

### Experiment: full run on G200

`run_g200_experiment.py` runs the real algorithm (pop=20, 3000 generations,
twin removal every 50 generations, random restart every 100) on all 10
`data/G200_*.txt` instances, one run per file — matching `GA.java`'s original
per-file protocol (reduced from 20 iterations/file to 1, for runtime). It's
resumable: re-running it after an interruption skips files already recorded
in `experiment_results.json`.

```bash
cd python
python3 run_g200_experiment.py
```

Full results from the completed run:

| File | Graph cut cost | Time |
|---|---|---|
| G200_0.txt | 383,783,200.31 | 569.3s |
| G200_1.txt | 334,441,900.18 | 563.8s |
| G200_2.txt | 169,335,744.66 | 579.8s |
| G200_3.txt | 237,892,425.48 | 546.7s |
| G200_4.txt | 307,623,611.68 | 539.0s |
| G200_5.txt | 365,780,523.91 | 536.8s |
| G200_6.txt | 288,253,805.13 | 548.2s |
| G200_7.txt | 26,959,488.08 | 528.1s |
| G200_8.txt | 265,730,762.08 | 556.6s |
| G200_9.txt | 286,924,825.87 | 557.0s |

**Avg graph cut cost: 266,672,628.74**
**Min graph cut cost: 26,959,488.08**
**Total time: 5525.1s (~92 minutes)**

This confirms the port runs the full algorithm (evolution, twin removal,
random restart, greedy mutation, elitism) correctly and stably across a
realistic multi-hour, multi-instance run with no crashes or degradation.
