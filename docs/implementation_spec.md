# EGAGP Modern Implementation Specification

## 1. Purpose

This document defines the implementation target for the modern Python version of **EGAGP: An Enhanced Genetic Algorithm for Producing Efficient Graph Partitions**.

The implementation is reconstructed from three source layers:

1. The published NSysS 2017 paper, especially the problem formulation, Algorithms 1–7, and Table I.
2. The historical Java source preserved under `legacy/java/`.
3. The later flat Python port, used only as supporting evidence and not as the authoritative algorithm.

When these sources disagree, the published algorithm and its surrounding prose take priority. Historical code is used to resolve implementation details that the paper leaves unspecified, except where the historical behavior is clearly erroneous or contradicts the paper.

The repository must distinguish the **published algorithm**, **historical implementation behavior**, and **modern corrective decisions**.

---

## 2. Problem Model

EGAGP maps an application graph onto a heterogeneous machine graph.

### Application graph

- Vertices represent software components.
- Each component has a resource requirement.
- Edges represent communication between components.
- Edge weights represent component-to-component communication cost.

### Machine graph

- Vertices represent heterogeneous machines.
- Each machine has a maximum resource capacity.
- Edges represent communication links between machines.
- Machine-edge weights represent machine-to-machine communication cost.

### Chromosome

An individual contains one gene per application vertex.

`genes[i] = k` means application component `i` is assigned to machine `k`.

The paper uses machine identifiers in `[1, M]`; the Python implementation will use zero-based machine indices `[0, M-1]`.

### Objective

For every application edge whose endpoints are assigned to different machines, its component communication cost is multiplied by the communication cost between the assigned machines.

The optimization objective is to **minimize graph cut size (GCS)**.

### Feasibility

For every machine, the sum of the resource requirements of components assigned to it must not exceed that machine's capacity.

The modern implementation will treat feasibility as a hard constraint. Invalid chromosomes will not compete on penalized fitness.

---

## 3. Source Priority

Implementation decisions follow this order:

1. Paper equation or unambiguous prose.
2. Paper pseudocode, unless it conflicts with the objective or surrounding prose.
3. Historical Java implementation when the paper is silent.
4. Modern engineering safeguard when neither source safely specifies behavior.

Every nontrivial correction or inference must be documented in `docs/implementation_notes.md`.

---

## 4. Paper-Faithful Core Components

### 4.1 Initialization

For every component, choose uniformly among machines that currently have enough remaining capacity.

This is equivalent to repeatedly sampling machines until a feasible machine is selected, as described in Algorithm 1.

If a partial assignment reaches a state where no machine can accommodate the next component, restart construction of the chromosome.

A bounded number of complete retries will be used. If no feasible chromosome can be constructed, raise an explicit feasibility error instead of silently marking the chromosome valid.

### 4.2 Full Fitness Evaluation

For a valid chromosome:

- iterate over unordered application-vertex pairs;
- when the two genes map to different machines, add the component communication cost multiplied by the assigned machine communication cost;
- lower cost is better.

Feasibility is checked separately.

### 4.3 Partial / Incremental Fitness

The paper's faster fitness calculation is a defining EGAGP feature.

When changing one gene:

`new_cost = old_cost - old_partial_cost + new_partial_cost`

The modern implementation must provide a correctness-first full recomputation and an incremental move calculation.

Tests must verify that incremental updates agree with full recomputation.

### 4.4 Greedy Mutation

For each non-elite offspring:

1. Choose a gene index randomly.
2. Evaluate candidate machine values for that gene.
3. Ignore candidates that violate machine capacity.
4. Choose the feasible candidate producing the lowest graph-cut cost.
5. Commit that value.
6. Record the mutated gene as the individual's `best_gene_index`.

The paper says `r` different values are tried but does not define `r` in the EGAGP paper. The historical Java code sets the number of trials to the number of machines. The modern default will therefore evaluate all machine identifiers exactly once, in randomized order. This is an explicit reconstruction decision.

The historical Java implementation contains a defect in which the running minimum is not updated. The modern implementation will use the actual minimum.

### 4.5 One-Point Crossover with Best-Gene Passing

Create the ordinary one-point child:

- prefix from parent A;
- suffix from parent B.

Then ensure that:

- A's best gene value is copied into the child's corresponding position;
- B's best gene value is copied into the child's corresponding position.

If a parent does not yet have a best gene, that override is skipped.

The paper's Algorithm 5 contains a line that assigns both segments from parent A, but its prose and the historical Java implementation use parent B for the second segment. The modern implementation follows the prose and historical behavior.

The paper states the crossover point lies in `[1, V]`. The modern paper-oriented mode will use a prefix length in that range. This differs slightly from the historical zero-based Java implementation, which allows an empty A prefix and never an all-A ordinary crossover.

### 4.6 Valid Offspring

Algorithm 6 repeats parent selection and crossover until a valid offspring is produced.

To prevent unbounded execution on difficult instances, the modern implementation will use a configurable maximum number of crossover attempts. On exhaustion, it will retain a valid parent copy rather than introduce an invalid child.

This is an engineering safeguard and will be documented.

### 4.7 Elitism

Population size remains fixed.

The best current individual is copied unchanged into the next generation. Only the remaining `N-1` slots are created by crossover and mutation.

The elite is not mutated.

This interpretation is required for elitism to actually preserve the best solution and matches the historical implementation.

### 4.8 Twin Removal

The paper reports a similarity threshold of `0.95`.

The modern implementation will define chromosome similarity as:

`matching_gene_count / chromosome_length`

Two individuals are twins when similarity is at least `0.95`.

One of the twins is retained; the other is replaced by a newly generated feasible individual.

The historical Java code instead uses Hamming distance `<= 2.5%`, equivalent to similarity `>= 0.975`. That historical threshold will be documented but will not be the paper-oriented default.

Twin removal is triggered every 50 generations/non-diverse steps.

### 4.9 Random Restart

The paper requires random restart after a configured number of non-improving generations but does not fully specify the restart population composition.

The historical Java routine supplies the missing detail:

- retain 20% of the population in total, including the elite;
- the elite occupies the first retained slot;
- select the other retained individuals by tournament selection;
- replace the remaining 80% with newly initialized feasible individuals.

The modern implementation will use this behavior.

The later Python port contains an off-by-one error that overwrites the final retained tournament-selected individual. That bug will not be reproduced.

### 4.10 Tournament Selection

Tournament size is 5, as reported in the paper and historical code.

Select five population members uniformly with replacement and return the valid individual with the lowest graph-cut cost.

---

## 5. GeneticAlgorithm Routine (Paper Algorithm 6)

`run_genetic_algorithm(population, generation_limit, restart_interval)` will:

1. Initialize `global_best` from the initial population.
2. Initialize `non_improving_steps = 0`.
3. Initialize `non_diverse_steps = 0`.
4. Repeat until `generation_limit` generations have been produced:
   - copy the elite;
   - generate valid offspring for all remaining population slots;
   - greedily mutate every non-elite offspring;
   - determine the generation best;
   - if generation best improves `global_best`, update `global_best` and reset `non_improving_steps`;
   - otherwise increment `non_improving_steps`;
   - increment `non_diverse_steps`;
   - when `non_diverse_steps >= 50`, perform twin removal and reset it;
   - when `non_improving_steps >= restart_interval`, perform random restart and reset it.
5. Return the final population and best-so-far individual.

### Paper pseudocode correction

Algorithm 6 appears to reverse the comparison used to update `global_best`. Since the objective is minimization, the implementation must update global best when:

`generation_best.cost < global_best.cost`

not the reverse.

---

## 6. Full EGAGP Routine (Paper Algorithm 7)

`run_egagp(instance, generation_limit, config, rng)` will implement the primary/secondary architecture that defines the published EGAGP method.

### Published parameter defaults

- Secondary population size: **20**
- Primary population size: **30**
- Secondary generation limit: **3000**
- Secondary random-restart interval: **100**
- Twin-removal interval: **50**
- Tournament size: **5**
- Similarity threshold: **0.95**

### Secondary phase

Half of the total generation budget is assigned approximately to secondary populations.

The paper defines:

`secondary_population_limit = (generation_limit / 2) / 3000`

The paper does not state how to round this quantity for generation limits that are not exact multiples of 6000.

The modern default will use integer-floor semantics, consistent with a straightforward Java integer implementation:

`secondary_count = floor((generation_limit / 2) / 3000)`

An explicit `secondary_count` override will be supported for reproducibility.

For each secondary population:

1. Generate 20 feasible individuals.
2. Run the genetic algorithm for 3000 generations with restart interval 100.
3. Save that secondary population's best individual.

### Primary phase

1. Create a primary population of size 30.
2. Insert the best individual from each secondary population.
3. Fill all remaining primary slots with newly generated feasible individuals.
4. Set primary generations to `generation_limit / 2`.
5. Set primary random-restart interval to 5% of the primary generation limit.
6. Run the genetic algorithm on the primary population.
7. Return its best-so-far individual.

### Paper pseudocode correction

Algorithm 7 prints the secondary loop as:

`while ite >= secondaryPopulationLimit`

Starting from `ite = 1`, that condition contradicts the surrounding prose and the 90,000-generation example. The modern implementation interprets it as iteration over the calculated number of secondary populations.

---

## 7. Generation-Limit Presets

The paper evaluates EGAGP with total generation limits:

- 30,000
- 50,000
- 70,000
- 90,000

The exact rounding of secondary-population count for 50,000 and 70,000 is not recoverable from the supplied source. The repository must not claim exact reproduction of those experiments unless the original benchmark data and orchestration details are recovered.

For 90,000 generations, the paper explicitly gives 15 secondary populations because:

`15 × 3000 = 45,000 = 90,000 / 2`.

---

## 8. Historical Java Snapshot

Files under `legacy/java/` must remain byte-for-byte unchanged.

They are a historical source snapshot associated with the EGAGP work, but they do **not** implement the complete primary/secondary Algorithm 7 described by the paper.

Repository documentation should not call them the complete reference implementation of the published algorithm.

Recommended wording:

> This directory preserves the historical Java source snapshot associated with the EGAGP project. The published paper describes an additional primary/secondary population orchestration layer that is not present in this snapshot. The modern Python implementation follows the published method while documenting differences from the historical source.

---

## 9. Known Historical Discrepancies

### Java greedy mutation

The Java code compares candidate fitness to `minFitness` but does not assign the newly found minimum back to `minFitness`.

**Modern decision:** correct the running-minimum update.

### Java/Python twin threshold

Historical code: Hamming distance `<= 2.5%`.

Paper parameter: similarity threshold `0.95`.

**Modern decision:** use Hamming similarity `>= 0.95` by default.

### Historical runner

The Java and existing Python runners use one population of 20 and a 3000-generation cap.

**Modern decision:** retain them only as historical behavior; implement Algorithm 7 separately.

### Existing Python random restart

The Python loop begins random filling from the final retained index, overwriting one survivor.

**Modern decision:** retain exactly 20% total and start replacement after the retained block.

### Existing feasible initialization

Historical Java/Python code may finish a component loop without finding a feasible machine and still mark the individual valid.

**Modern decision:** never silently accept incomplete/infeasible initialization.

### Tabu fields

Historical code contains tabu-related state, but the flag is disabled and the EGAGP paper does not describe tabu search as part of the method.

**Modern decision:** omit tabu state from the modern implementation.

---

## 10. Input-Format Convention

The historical text format is:

```text
number_of_vertices
number_of_application_edges
u v application_edge_cost
...
component_resource_requirements
number_of_machines
number_of_machine_edges
u v machine_edge_cost
...
machine_capacities
```

Application and machine edges are treated as symmetric.

The historical loader assigns a cost of `1_000_000` to missing machine links. The paper does not explicitly define this non-edge convention.

**Modern decision:** preserve `1_000_000` as the default legacy-format non-edge cost, expose it as a named constant/configuration value, and document that this detail comes from the historical implementation rather than the paper.

---

## 11. Data-Reproduction Policy

The supplied original benchmark instance files are not available.

The paper states that sparse graphs were generated using an Eppstein power-law generator and refers to prior work for generation details.

The supplied `generate_dataset.py` uses Barabási-Albert application graphs and a ring-based machine topology. It is therefore a **synthetic substitute**, not a reconstruction of the published benchmark data.

The modern repository may retain a generator only under a clearly named path such as:

`scripts/generate_synthetic_data.py`

Documentation must state that generated instances are intended for testing, examples, and demonstrations, not for reproducing the published numerical results.

---

## 12. Reproducibility Design

All stochastic operations in the modern implementation will receive an explicit `numpy.random.Generator`.

No algorithmic function will rely on NumPy's global random state.

This allows:

- deterministic tests;
- reproducible experimental seeds;
- independent secondary-population streams;
- transparent experiment logging.

---

## 13. Proposed Python Package

```text
src/egagp/
├── __init__.py
├── fitness.py
├── individual.py
├── population.py
├── algorithm.py
└── runner.py
```

### `fitness.py`

Contains:

- `ProblemInstance`
- historical-format parser
- feasibility/capacity calculation
- full graph-cut evaluation
- partial/move-cost evaluation

### `individual.py`

Contains:

- chromosome representation
- cached used capacities
- cached graph-cut cost
- `best_gene_index`
- initialization
- safe move application
- one-point crossover support

### `population.py`

Contains:

- fixed-size population abstraction
- fittest selection
- population validation

### `algorithm.py`

Contains:

- configuration dataclass
- tournament selection
- greedy mutation
- best-gene crossover
- twin detection/removal
- random restart
- Algorithm 6 genetic-algorithm loop

### `runner.py`

Contains:

- Algorithm 7 EGAGP orchestration
- primary/secondary population construction
- generation-limit presets
- CLI
- experiment result records

---

## 14. Test Strategy

The new suite must use `pytest` assertions rather than print-only smoke scripts.

Required test groups:

### Fitness

- known exact graph-cut cost;
- capacity calculation;
- valid/invalid assignment;
- incremental move cost equals full recomputation.

### Initialization

- every returned individual is feasible;
- impossible instance fails explicitly;
- deterministic output under a fixed seed.

### Crossover

- prefix/suffix composition;
- best gene from both parents is preserved;
- offspring validity loop behaves correctly.

### Mutation

- only feasible candidate values are accepted;
- selected value has the minimum tested graph-cut cost;
- `best_gene_index` is updated.

### Twins

- exactly 95% similarity is a twin;
- below 95% is not a twin.

### Random restart

- elite is retained;
- exactly 20% of the population is retained in total;
- remaining individuals are newly generated and feasible.

### GeneticAlgorithm

- population size stays constant;
- elite cannot be lost by ordinary evolution;
- stagnation counter triggers restart;
- twin counter triggers twin removal;
- global best is monotonically non-increasing.

### Full EGAGP

Using very small generation limits for CI:

- creates the requested number of secondary populations;
- transfers secondary winners into the primary population;
- fills remaining primary slots;
- runs the primary phase;
- returns a feasible result.

---

## 15. Deterministic Sample Instance

The existing `test_data.txt` allows all components to fit on a single machine and therefore permits a trivial zero-cut solution.

Replace the primary test fixture with a constrained instance where multiple machines must be used and the optimum is analytically known.

A recommended 4-vertex / 2-machine fixture is:

```text
4
6
0 1 10
0 2 1
0 3 1
1 2 1
1 3 1
2 3 10
6 6 6 6
2
1
0 1 1
12 12
```

For assignment `[0, 0, 1, 1]`, the graph-cut cost is 4 and both machine capacities are exactly satisfied.

This fixture is suitable for exact fitness and mutation tests.

---

## 16. Repository Documentation Policy

The repository should make the following distinctions explicit:

- **Paper specification:** what the NSysS 2017 paper defines.
- **Historical snapshot:** what the preserved Java source actually does.
- **Modern implementation:** paper-oriented implementation with documented corrections and safety guards.
- **Synthetic data:** test/demo data that does not reproduce the original benchmark instances.

The README must not claim reproduction of the paper's reported benchmark results until the original datasets and all missing experiment details are available.

The README must not claim Python speed or memory improvements without benchmark evidence.

---

## 17. Implementation Order

The implementation should proceed in this order:

1. Documentation/specification and corrected legacy README.
2. Package metadata and `fitness.py`.
3. Deterministic sample data and fitness tests.
4. `individual.py` and incremental-fitness tests.
5. `population.py`.
6. GA operators in `algorithm.py`.
7. Algorithm 6 tests.
8. Full primary/secondary orchestration in `runner.py`.
9. Synthetic-data generator cleanup.
10. README, citation metadata, examples, and experiment documentation.
11. Only after validation, archive the old repository.

