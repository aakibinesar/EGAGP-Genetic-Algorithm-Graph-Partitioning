"""
Population class for managing a collection of individuals in the genetic algorithm.
"""

from typing import List, Optional
from individual import Individual


class Population:
    """Manages a collection of individuals (solutions) in the GA."""

    def __init__(self, population_size: int, initialize: bool = False):
        """
        Initialize a population.

        Args:
            population_size: Number of individuals in the population
            initialize: If True, generate random valid individuals
        """
        self.individuals: List[Optional[Individual]] = [None] * population_size

        if initialize:
            for i in range(population_size):
                new_individual = Individual()
                new_individual.generate_valid_individual()
                self.save_individual(i, new_individual)

    def get_individual(self, index: int) -> Individual:
        """
        Get individual at index.

        Args:
            index: Population index

        Returns:
            Individual at the given index
        """
        return self.individuals[index]

    def get_fittest(self) -> Optional[Individual]:
        """
        Find and return the fittest individual in the population.

        Returns:
            The fittest valid individual, or None if no valid individuals exist
        """
        fittest = None

        # Find first valid individual
        for individual in self.individuals:
            if individual.is_valid() == Individual.VALID:
                fittest = individual
                break

        if fittest is None:
            return None

        # Find the fittest among valid individuals
        for individual in self.individuals:
            if individual.is_valid() == Individual.VALID:
                if fittest.get_fitness() > individual.get_fitness():
                    fittest = individual

        return fittest

    def size(self) -> int:
        """
        Get population size.

        Returns:
            Number of individuals in the population
        """
        return len(self.individuals)

    def save_individual(self, index: int, individual: Individual) -> None:
        """
        Save an individual at the given index.

        Args:
            index: Population index
            individual: Individual to save
        """
        self.individuals[index] = individual
