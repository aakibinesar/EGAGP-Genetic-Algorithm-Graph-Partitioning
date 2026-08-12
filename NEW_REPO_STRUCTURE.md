# Proposed New Repository Structure

Based on: *"EGAGP: An enhanced genetic algorithm for producing efficient graph
partitions"* (NSysS 2017, Best Student Paper).

Suggested repo name: `egagp` (or `egagp-graph-partitioning` if `egagp` is taken).

```
egagp/
├── README.md                      # Paper citation, abstract, usage, results
├── LICENSE
├── requirements.txt                # numpy>=1.21.0
├── .gitignore
│
├── src/
│   └── egagp/
│       ├── __init__.py
│       ├── fitness.py              # was fitness_calc.py — data loading, cost matrices
│       ├── individual.py           # chromosome representation, crossover, mutation ops
│       ├── population.py           # population management, fittest selection
│       ├── algorithm.py            # GA operators: tournament, greedy mutation, twins, restart
│       └── runner.py               # was egagp.py — experiment driver / CLI entrypoint
│
├── legacy/
│   └── java/                       # original reference implementation, kept for provenance
│       ├── GA.java
│       ├── Algorithm.java
│       ├── FitnessCalc.java
│       ├── Individual.java
│       └── Population.java
│
├── data/
│   ├── README.md                   # input file format spec
│   └── sample/
│       └── test_data.txt           # small synthetic instance for smoke-testing
│
├── tests/
│   └── test_runner.py              # unit/smoke tests (rename to test_egagp.py)
│
├── docs/
│   └── EGAGP.pdf                   # published paper
│
└── scripts/
    └── run_experiment.sh           # convenience wrapper around runner.py
```

## Notes on the reorganization

- **`src/egagp/` package layout** — makes the project `pip install -e .`-able later
  and gives imports a proper namespace (`from egagp.algorithm import Algorithm`)
  instead of flat top-level modules.
- **`legacy/java/`** — preserves the original Java reference implementation for
  provenance/citation purposes without cluttering the Python source tree.
- **`data/sample/`** — separates test fixtures from source code; add real
  `G200_*.txt` datasets here (or link externally if large).
- **`docs/`** — houses the paper PDF instead of sitting at repo root.
- Root `README.md` should lead with the paper citation and a one-line abstract,
  then installation/usage — this is what most visitors from the citation link
  will actually want to see first.
