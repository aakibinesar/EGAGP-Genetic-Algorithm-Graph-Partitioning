"""
Individual class representing a solution in the genetic algorithm.
Optimized using NumPy for efficient array operations.
"""

import numpy as np
from typing import Optional
from fitness_calc import FitnessCalc


class Individual:
    """Represents a single solution (chromosome) in the genetic algorithm."""

    VALID = 1
    INVALID = 0
    DONT_KNOW = -1

    # Class-level taboo search variables
    _taboo: Optional[np.ndarray] = None
    _taboo_count: int = 100
    _taboo_set: bool = False

    def __init__(self, copy_from: Optional['Individual'] = None):
        """
        Initialize an individual.

        Args:
            copy_from: Optional individual to copy from
        """
        if copy_from is None:
            self.genes = np.zeros(FitnessCalc.number_of_vertices, dtype=np.int32)
            self.used_capacities = np.zeros(FitnessCalc.number_of_machines, dtype=np.float64)
            self.fitness = 0.0
            self.graph_cut_cost = 0.0
            self.validity = self.INVALID
            self.fitness_calculated = False
            self.best_gene_index = -1
        else:
            # Copy constructor
            self.genes = copy_from.genes.copy()
            self.used_capacities = copy_from.used_capacities.copy()
            self.fitness = copy_from.fitness
            self.graph_cut_cost = copy_from.graph_cut_cost
            self.validity = copy_from.validity
            self.fitness_calculated = copy_from.fitness_calculated
            self.best_gene_index = copy_from.best_gene_index

    def is_valid(self) -> int:
        """
        Check if the individual satisfies capacity constraints.

        Returns:
            VALID, INVALID, or DONT_KNOW
        """
        if self.validity != self.DONT_KNOW:
            return self.validity

        # Check if any machine is over capacity
        if np.any(self.used_capacities > FitnessCalc.M):
            self.validity = self.INVALID
        else:
            self.validity = self.VALID

        return self.validity

    def generate_valid_individual(self) -> None:
        """Generate a valid random individual satisfying all constraints."""
        free = FitnessCalc.M.copy()
        machines = np.arange(FitnessCalc.number_of_machines)

        for i in range(len(self.genes)):
            # Shuffle remaining machines
            available = FitnessCalc.number_of_machines
            for j in range(FitnessCalc.number_of_machines):
                value = np.random.randint(available - j)
                gene = machines[value]

                if free[gene] >= FitnessCalc.W[i]:
                    self.genes[i] = gene
                    free[gene] -= FitnessCalc.W[i]
                    self.used_capacities[gene] += FitnessCalc.W[i]
                    break

                # Swap to exclude this machine
                machines[value], machines[available - j - 1] = machines[available - j - 1], machines[value]

        self.validity = self.VALID

    def one_point_crossover(self, parent1: 'Individual', parent2: 'Individual') -> None:
        """
        Perform one-point crossover between two parents.

        Args:
            parent1: First parent
            parent2: Second parent
        """
        index = np.random.randint(parent1.size())
        bgene1 = parent1.best_gene_index
        bgene2 = parent2.best_gene_index

        self.used_capacities.fill(0)

        # First part from parent1
        for i in range(index):
            if i == bgene2:
                self.genes[i] = parent2.genes[bgene2]
            else:
                self.genes[i] = parent1.genes[i]
            self.used_capacities[self.genes[i]] += FitnessCalc.W[i]

        # Second part from parent2
        for i in range(index, parent1.size()):
            if i == bgene1:
                self.genes[i] = parent1.genes[bgene1]
            else:
                self.genes[i] = parent2.genes[i]
            self.used_capacities[self.genes[i]] += FitnessCalc.W[i]

        self.validity = self.DONT_KNOW

    def get_gene(self, index: int) -> int:
        """Get gene value at index."""
        return self.genes[index]

    def set_gene(self, index: int, value: int) -> None:
        """
        Set gene value at index and update fitness incrementally.

        Args:
            index: Gene index
            value: New machine assignment
        """
        prev_value = self.genes[index]
        if value == prev_value:
            return

        self.genes[index] = value
        self.validity = self.DONT_KNOW

        W = FitnessCalc.W
        M = FitnessCalc.M

        if not self.fitness_calculated:
            self.used_capacities[prev_value] -= W[index]
            self.used_capacities[value] += W[index]
            self.get_fitness()
        else:
            # Incremental fitness update
            if self.used_capacities[prev_value] > M[prev_value] and \
               self.used_capacities[prev_value] - W[index] <= M[prev_value]:
                self.fitness -= 1000000.0

            if self.used_capacities[value] <= M[value] and \
               self.used_capacities[value] + W[index] > M[value]:
                self.fitness += 1000000.0

            self.used_capacities[prev_value] -= W[index]
            self.used_capacities[value] += W[index]

            C = FitnessCalc.C
            B = FitnessCalc.B

            # Calculate fitness change
            # Add costs for new assignment
            mask_new = self.genes != value
            fitness_plus = np.sum(C[index, :] * B[self.genes, value] * mask_new)

            # Subtract costs for old assignment
            mask_old = self.genes != prev_value
            fitness_minus = np.sum(C[index, :] * B[self.genes, prev_value] * mask_old)

            self.fitness += fitness_plus - fitness_minus
            self.graph_cut_cost += fitness_plus - fitness_minus

    def size(self) -> int:
        """Return the number of genes."""
        return len(self.genes)

    def get_fitness(self) -> float:
        """
        Calculate and return fitness value.

        Returns:
            Fitness value (lower is better)
        """
        if self.fitness_calculated:
            return self.fitness

        # Penalty for capacity violations
        self.fitness = np.sum(np.maximum(0, self.used_capacities - FitnessCalc.M) > 0) * 1000000.0

        # Calculate graph cut cost using vectorized operations
        C = FitnessCalc.C
        B = FitnessCalc.B
        self.graph_cut_cost = 0.0

        for i in range(FitnessCalc.number_of_vertices):
            for j in range(i + 1, FitnessCalc.number_of_vertices):
                if self.genes[i] != self.genes[j]:
                    cost = C[i, j] * B[self.genes[i], self.genes[j]]
                    self.fitness += cost
                    self.graph_cut_cost += cost

        self.fitness_calculated = True
        return self.fitness

    def get_graph_cut_cost(self) -> float:
        """Get the graph cut cost (without penalties)."""
        if not self.fitness_calculated:
            self.get_fitness()
        return self.graph_cut_cost

    @classmethod
    def get_taboo_of_index(cls, index: int) -> int:
        """Get taboo value for a gene index."""
        if cls._taboo_set:
            return cls._taboo[index]
        else:
            cls._set_taboo()
            cls._taboo_set = True
            return 0

    @classmethod
    def set_taboo_of_index(cls, index: int) -> None:
        """Set taboo value for a gene index."""
        if not cls._taboo_set:
            cls._set_taboo()
            cls._taboo_set = True

        cls._taboo[index] = cls._taboo_count
        cls._taboo_count += 1

    @classmethod
    def _set_taboo(cls) -> None:
        """Initialize taboo array."""
        cls._taboo = np.zeros(FitnessCalc.number_of_vertices, dtype=np.int32)

    @classmethod
    def get_taboo_count(cls) -> int:
        """Get current taboo count."""
        return cls._taboo_count

    def __str__(self) -> str:
        """String representation of the individual."""
        lines = [f"(Vertex {i} ==> Machine {self.genes[i]})" for i in range(self.size())]
        return '\n'.join(lines)
