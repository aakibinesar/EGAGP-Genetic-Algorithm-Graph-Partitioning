#!/usr/bin/env python3
"""
Synthetic dataset generator for EGAGP, standing in for the original
(unavailable) G200_*.txt files.

The paper (Section V-A) states the real datasets were "generated using the
Eppstein power law generator", following the methodology of the FGPGA paper
[Islam et al., 2015] and Verbelen et al. [2013]. Those exact instance files
were never published and are not recoverable, and the "Eppstein power law
generator" itself isn't precisely specified beyond that citation, so this
generator does NOT reproduce them. Instead it approximates the described
properties with a well-documented substitute:

  - Application graph: sparse, non-uniform-degree graph built via
    Barabasi-Albert preferential attachment (a standard, well-known way to
    produce power-law-ish degree distributions), matching the paper's
    "sparse graphs" characterization.
  - Machine graph: sparse "geographically neighboring machines" structure
    (a randomly-ordered ring plus a few extra links), matching the paper's
    justification for sparse machine connectivity.
  - Component weights / machine capacities: randomized but scaled so a
    feasible assignment always exists (required by Individual.generate_valid_individual).

Output format matches FitnessCalc.extract_data() exactly:

    n_vertices
    n_edges
    <n_edges lines of "x y cost">
    <n_vertices component weights, space-separated>
    n_machines
    n_machine_edges
    <n_machine_edges lines of "x y cost">
    <n_machines machine capacities, space-separated>

Use --replicate-name G200 --vertices 200 --instances 10 to reproduce the
file set GA.java/egagp.py expect (G200_0.txt .. G200_9.txt).
"""

import argparse
import os
import numpy as np


def barabasi_albert_edges(n_vertices, m_attach, rng):
    """Sparse power-law-ish graph via Barabasi-Albert preferential attachment."""
    m_attach = max(1, min(m_attach, n_vertices - 1))
    edges = set()
    degree = np.zeros(n_vertices, dtype=np.int64)

    # Seed a small connected core so preferential attachment has something
    # to attach to.
    core_size = m_attach + 1
    for i in range(core_size):
        for j in range(i + 1, core_size):
            edges.add((i, j))
            degree[i] += 1
            degree[j] += 1

    for new_node in range(core_size, n_vertices):
        candidates = np.arange(new_node)
        weights = degree[:new_node].astype(np.float64) + 1.0  # +1 avoids all-zero degree
        probs = weights / weights.sum()
        targets = rng.choice(candidates, size=min(m_attach, new_node), replace=False, p=probs)
        for t in targets:
            edge = (min(new_node, t), max(new_node, t))
            if edge not in edges:
                edges.add(edge)
                degree[new_node] += 1
                degree[t] += 1

    return edges


def sparse_ring_edges(n_machines, extra_link_prob, rng):
    """Sparse 'geographically neighboring machines' graph: a shuffled ring
    plus a few random long-range links."""
    order = rng.permutation(n_machines)
    edges = set()
    for i in range(n_machines):
        a, b = order[i], order[(i + 1) % n_machines]
        edges.add((min(a, b), max(a, b)))

    for i in range(n_machines):
        for j in range(i + 1, n_machines):
            if (i, j) not in edges and rng.random() < extra_link_prob:
                edges.add((i, j))

    return edges


def generate_instance(n_vertices, n_machines, seed,
                       m_attach=2, machine_extra_link_prob=0.15,
                       vertex_weight_range=(5.0, 25.0),
                       component_cost_range=(1.0, 20.0),
                       machine_cost_range=(1.0, 10.0),
                       capacity_load_factor=1.6):
    rng = np.random.default_rng(seed)

    # --- Application graph (components) ---
    app_edges = barabasi_albert_edges(n_vertices, m_attach, rng)
    component_edges = [
        (i, j, float(rng.uniform(*component_cost_range)))
        for (i, j) in sorted(app_edges)
    ]
    weights = rng.uniform(*vertex_weight_range, size=n_vertices)

    # --- Machine graph ---
    machine_edges_set = sparse_ring_edges(n_machines, machine_extra_link_prob, rng)
    machine_edges = [
        (i, j, float(rng.uniform(*machine_cost_range)))
        for (i, j) in sorted(machine_edges_set)
    ]

    # --- Capacities: guarantee a feasible packing exists ---
    total_weight = weights.sum()
    base_capacity = total_weight * capacity_load_factor / n_machines
    heterogeneity = rng.uniform(0.6, 1.4, size=n_machines)
    capacities = base_capacity * heterogeneity
    # Make sure every single component still fits somewhere.
    max_weight = weights.max()
    capacities = np.maximum(capacities, max_weight * 1.05)

    return component_edges, weights, machine_edges, capacities


def write_instance(path, component_edges, weights, machine_edges, capacities):
    n_vertices = len(weights)
    n_machines = len(capacities)

    with open(path, "w") as f:
        f.write(f"{n_vertices}\n")
        f.write(f"{len(component_edges)}\n")
        for x, y, cost in component_edges:
            f.write(f"{x} {y} {cost:.6f}\n")
        f.write(" ".join(f"{w:.6f}" for w in weights) + "\n")

        f.write(f"{n_machines}\n")
        f.write(f"{len(machine_edges)}\n")
        for x, y, cost in machine_edges:
            f.write(f"{x} {y} {cost:.6f}\n")
        f.write(" ".join(f"{c:.6f}" for c in capacities) + "\n")


def main():
    parser = argparse.ArgumentParser(description="Generate synthetic EGAGP datasets")
    parser.add_argument("--vertices", type=int, default=200, help="number of component vertices")
    parser.add_argument("--machines", type=int, default=None,
                         help="number of machines (default: max(4, vertices // 15))")
    parser.add_argument("--instances", type=int, default=10, help="number of replicate files to generate")
    parser.add_argument("--replicate-name", type=str, default="G200",
                         help="filename prefix, files are named <prefix>_<index>.txt")
    parser.add_argument("--output-dir", type=str, default="data", help="output directory")
    parser.add_argument("--seed", type=int, default=42, help="base random seed")
    args = parser.parse_args()

    n_machines = args.machines or max(4, args.vertices // 15)
    os.makedirs(args.output_dir, exist_ok=True)

    for idx in range(args.instances):
        component_edges, weights, machine_edges, capacities = generate_instance(
            n_vertices=args.vertices, n_machines=n_machines, seed=args.seed + idx
        )
        out_path = os.path.join(args.output_dir, f"{args.replicate_name}_{idx}.txt")
        write_instance(out_path, component_edges, weights, machine_edges, capacities)
        print(f"Wrote {out_path}: {args.vertices} vertices, {len(component_edges)} edges, "
              f"{n_machines} machines, {len(machine_edges)} machine-links")


if __name__ == "__main__":
    main()
