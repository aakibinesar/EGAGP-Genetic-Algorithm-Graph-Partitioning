#!/usr/bin/env python3
"""
Enhanced Genetic Algorithm for Graph Partitioning (EGAGP)
Main driver program - optimized Python implementation.

Usage:
    python egagp.py [data_directory]
"""

import time
import sys
import os
from pathlib import Path
from typing import List

from fitness_calc import FitnessCalc
from population import Population
from individual import Individual
from algorithm import Algorithm


class EGAGP:
    """Main class for running the genetic algorithm."""

    def __init__(self, data_dir: str = ".", population_size: int = 20,
                 iterations: int = 20, max_generations: int = 3000):
        """
        Initialize EGAGP.

        Args:
            data_dir: Directory containing data files
            population_size: Size of the population
            iterations: Number of iterations per file
            max_generations: Maximum generations per iteration
        """
        self.data_dir = Path(data_dir)
        self.population_size = population_size
        self.iterations = iterations
        self.max_generations = max_generations

    def run_single_iteration(self, data_file: str) -> tuple[float, float]:
        """
        Run a single GA iteration.

        Args:
            data_file: Path to data file

        Returns:
            Tuple of (best_fitness, graph_cut_cost)
        """
        # Load data
        FitnessCalc.extract_data(data_file)

        # Initialize population
        population = Population(self.population_size, initialize=True)

        generation_count = 0
        current_best = -1.0
        prev_best = -1.0

        while generation_count < self.max_generations:
            generation_count += 1

            # Remove twins every 50 generations
            if generation_count % 50 == 0:
                population = Algorithm.remove_twins(population)

            best_fitness = population.get_fittest().get_fitness()

            # Evolve population
            population = Algorithm.evolve_population(population)

            # Random restart every 100 generations if stuck
            if generation_count % 100 == 0:
                if current_best == -1.0:
                    current_best = best_fitness
                else:
                    prev_best = current_best
                    current_best = best_fitness
                    if current_best == prev_best:
                        population = Algorithm.random_restart(population)

            # Early stopping if optimal solution found
            if best_fitness <= 0.0:
                break

        fittest = population.get_fittest()
        return fittest.get_fitness(), fittest.get_graph_cut_cost()

    def run_experiment(self, file_pattern: str = "G200_*.txt") -> None:
        """
        Run complete experiment on multiple data files.

        Args:
            file_pattern: Glob pattern for data files
        """
        start_time = time.time()

        # Find all matching data files
        data_files = sorted(self.data_dir.glob(file_pattern))

        if not data_files:
            print(f"No files matching '{file_pattern}' found in {self.data_dir}")
            return

        total_avg = 0.0
        total_min = 0.0

        for data_file in data_files:
            print(f"\n{data_file.name}")
            print("Iterations: ", end="")

            avg_cost = 0.0
            min_cost = float('inf')

            for iteration in range(self.iterations):
                print(f"{iteration} ", end="", flush=True)

                _, graph_cut_cost = self.run_single_iteration(str(data_file))

                if graph_cut_cost < min_cost:
                    min_cost = graph_cut_cost

                avg_cost += graph_cut_cost

            avg_cost /= self.iterations
            print()
            print(f"Avg Graph Cut Cost: {avg_cost:.2f}")
            print(f"Min Graph Cut Cost: {min_cost:.2f}")

            total_avg += avg_cost
            total_min += min_cost

        # Print summary
        print("\n" + "=" * 60)
        print(f"Summation of Avg Graph Cut Cost: {total_avg:.2f}")
        print(f"Summation of Min Graph Cut Cost: {total_min:.2f}")

        elapsed_time = time.time() - start_time
        print(f"Time: {elapsed_time:.2f}s ({elapsed_time / 60:.2f} minutes)")
        print("=" * 60)


def main():
    """Main entry point."""
    # Parse command line arguments
    if len(sys.argv) > 1:
        data_dir = sys.argv[1]
    else:
        # Default to current directory
        data_dir = "."

    # Check if data directory exists
    if not os.path.isdir(data_dir):
        print(f"Error: Directory '{data_dir}' not found")
        print("\nUsage: python egagp.py [data_directory]")
        sys.exit(1)

    print("=" * 60)
    print("Enhanced Genetic Algorithm for Graph Partitioning (EGAGP)")
    print("=" * 60)
    print(f"Data directory: {data_dir}")
    print(f"Population size: 20")
    print(f"Iterations per file: 20")
    print(f"Max generations: 3000")
    print("=" * 60)

    # Run experiment
    egagp = EGAGP(data_dir=data_dir)
    egagp.run_experiment()


if __name__ == "__main__":
    main()
