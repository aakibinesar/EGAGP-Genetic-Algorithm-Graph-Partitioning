#!/usr/bin/env python3
"""
Verify that Individual.set_gene()'s incremental fitness/graph-cut update
matches a full from-scratch recomputation. This mirrors the debug check
that was commented out in the original Java Individual.setGene().
"""

import copy
import numpy as np
from fitness_calc import FitnessCalc
from individual import Individual


def make_random_instance(n_vertices=12, n_machines=4, edge_prob=0.5, seed=None):
    rng = np.random.default_rng(seed)
    FitnessCalc.number_of_vertices = n_vertices
    FitnessCalc.number_of_machines = n_machines

    C = np.zeros((n_vertices, n_vertices))
    for i in range(n_vertices):
        for j in range(i + 1, n_vertices):
            if rng.random() < edge_prob:
                w = rng.uniform(1, 20)
                C[i, j] = w
                C[j, i] = w
    FitnessCalc.C = C

    FitnessCalc.W = rng.uniform(5, 25, n_vertices)

    B = np.full((n_machines, n_machines), 1000000.0)
    for i in range(n_machines):
        for j in range(i + 1, n_machines):
            w = rng.uniform(1, 10)
            B[i, j] = w
            B[j, i] = w  # B must be symmetric, matching FitnessCalc.extract_data
    FitnessCalc.B = B

    # Generous capacities so validity churns during mutation
    FitnessCalc.M = np.full(n_machines, FitnessCalc.W.sum() / n_machines * 1.6)


def full_recompute_fitness_and_cut(indiv: Individual):
    """Force a from-scratch recomputation, bypassing the cached/incremental path."""
    fresh = Individual()
    fresh.genes = indiv.genes.copy()
    fresh.used_capacities = np.zeros(FitnessCalc.number_of_machines)
    for i, g in enumerate(fresh.genes):
        fresh.used_capacities[g] += FitnessCalc.W[i]
    fresh.fitness_calculated = False
    return fresh.get_fitness(), fresh.get_graph_cut_cost()


def run_trial(seed, n_vertices=12, n_machines=4, n_mutations=200, tol=1e-6):
    make_random_instance(n_vertices=n_vertices, n_machines=n_machines, seed=seed)

    indiv = Individual()
    indiv.generate_valid_individual()
    indiv.get_fitness()  # populate fitness_calculated=True, seed incremental path

    rng = np.random.default_rng(seed + 1000)
    mismatches = []

    for step in range(n_mutations):
        idx = int(rng.integers(0, n_vertices))
        new_val = int(rng.integers(0, n_machines))

        indiv.set_gene(idx, new_val)

        incremental_fitness = indiv.fitness
        incremental_cut = indiv.graph_cut_cost

        full_fitness, full_cut = full_recompute_fitness_and_cut(indiv)

        if abs(incremental_fitness - full_fitness) > tol or abs(incremental_cut - full_cut) > tol:
            mismatches.append({
                "step": step,
                "gene_index": idx,
                "new_value": new_val,
                "incremental_fitness": incremental_fitness,
                "full_fitness": full_fitness,
                "incremental_cut": incremental_cut,
                "full_cut": full_cut,
            })

    return mismatches


def main():
    print("=" * 60)
    print("Incremental vs. full-recompute fitness consistency check")
    print("=" * 60)

    total_mismatches = 0
    for seed in range(10):
        mismatches = run_trial(seed)
        status = "OK" if not mismatches else f"MISMATCH ({len(mismatches)})"
        print(f"  seed={seed:2d}: {status}")
        if mismatches:
            total_mismatches += len(mismatches)
            for m in mismatches[:3]:
                print(f"    {m}")

    print("=" * 60)
    if total_mismatches == 0:
        print("PASS: incremental set_gene() matches full recomputation in all trials")
        return 0
    else:
        print(f"FAIL: {total_mismatches} mismatches found across trials")
        return 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
