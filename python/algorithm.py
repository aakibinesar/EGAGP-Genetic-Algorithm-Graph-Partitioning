"""
Genetic Algorithm operations including selection, crossover, and mutation.
Optimized for performance and code clarity.
"""

import numpy as np
from typing import List
from individual import Individual
from population import Population
from fitness_calc import FitnessCalc


class Algorithm:
    """Implements GA operators: selection, crossover, mutation."""

    # Algorithm parameters
    TOURNAMENT_SIZE = 5
    TABOO_LIMIT = 25
    ELITISM = True
    TABOO_FLAG = False

    @classmethod
    def evolve_population(cls, pop: Population) -> Population:
        """
        Evolve population to create next generation.

        Args:
            pop: Current population

        Returns:
            New evolved population
        """
        new_population = Population(pop.size(), initialize=False)

        # Preserve best individual if elitism is enabled
        elitism_offset = 0
        if cls.ELITISM:
            new_population.save_individual(0, pop.get_fittest())
            elitism_offset = 1

        # Create new individuals through crossover
        for i in range(elitism_offset, pop.size()):
            j = 0
            while j < FitnessCalc.number_of_vertices:
                parent1 = cls._tournament_selection(pop)
                parent2 = cls._tournament_selection(pop)
                offspring = cls._one_point_crossover(parent1, parent2)

                if offspring.is_valid() == Individual.VALID:
                    new_population.save_individual(i, offspring)
                    break

                j += 1

            # If no valid offspring created, keep old individual
            if j == FitnessCalc.number_of_vertices:
                new_population.save_individual(i, pop.get_individual(i))

        # Apply greedy mutation to all non-elite individuals
        for i in range(elitism_offset, new_population.size()):
            cls._greedy_mutate(new_population.get_individual(i))

        return new_population

    @classmethod
    def random_restart(cls, pop: Population) -> Population:
        """
        Perform random restart to escape local optima.

        Args:
            pop: Current population

        Returns:
            New population with partial restart
        """
        new_population = Population(pop.size(), initialize=False)

        # Preserve best individual if elitism is enabled
        elitism_offset = 0
        if cls.ELITISM:
            new_population.save_individual(0, pop.get_fittest())
            elitism_offset = 1

        # Keep top 20% through tournament selection
        i = elitism_offset
        for i in range(elitism_offset, pop.size() // 5):
            individual = cls._tournament_selection(pop)
            new_population.save_individual(i, individual)

        # Fill rest with random valid individuals
        for i in range(i, new_population.size()):
            individual = Individual()
            individual.generate_valid_individual()
            new_population.save_individual(i, individual)

        return new_population

    @classmethod
    def remove_twins(cls, pop: Population) -> Population:
        """
        Remove duplicate/similar individuals from population.

        Args:
            pop: Current population

        Returns:
            Population with duplicates replaced
        """
        count = 0
        for i in range(pop.size()):
            for j in range(i + 1, pop.size()):
                if cls._is_twins(pop.get_individual(i), pop.get_individual(j)):
                    individual = Individual()
                    individual.generate_valid_individual()
                    pop.save_individual(j, individual)
                    count += 1

        return pop

    @classmethod
    def _one_point_crossover(cls, parent1: Individual, parent2: Individual) -> Individual:
        """
        Perform one-point crossover between two parents.

        Args:
            parent1: First parent
            parent2: Second parent

        Returns:
            Offspring individual
        """
        offspring = Individual()
        offspring.one_point_crossover(parent1, parent2)
        return offspring

    @classmethod
    def _greedy_mutate(cls, individual: Individual) -> None:
        """
        Apply greedy mutation to an individual.

        Args:
            individual: Individual to mutate
        """
        temp = Individual(copy_from=individual)
        greedy_mutation_values = FitnessCalc.number_of_machines

        k = 0
        taboo_count = Individual.get_taboo_count()

        while k < FitnessCalc.number_of_vertices:
            gene_index = np.random.randint(FitnessCalc.number_of_vertices)

            # Check taboo list
            if cls.TABOO_FLAG and (taboo_count - Individual.get_taboo_of_index(gene_index) < cls.TABOO_LIMIT):
                k += 1
                continue

            # Generate random machine assignments to try
            values = np.random.randint(0, FitnessCalc.number_of_machines, greedy_mutation_values)

            min_fitness = float('inf')
            min_index = -1
            min_gene_value = -1

            # Try each value and find the best
            for i, value in enumerate(values):
                individual.set_gene(gene_index, value)

                if individual.is_valid() == Individual.VALID:
                    fitness = individual.get_fitness()
                    if fitness < min_fitness:
                        min_fitness = fitness
                        min_index = i
                        min_gene_value = value

            # Apply best mutation found
            if min_index != -1:
                individual.set_gene(gene_index, min_gene_value)
                individual.best_gene_index = gene_index
                Individual.set_taboo_of_index(gene_index)
                break
            else:
                # Restore original value if no improvement
                individual.set_gene(gene_index, temp.get_gene(gene_index))

            k += 1

    @classmethod
    def _tournament_selection(cls, pop: Population) -> Individual:
        """
        Select individual using tournament selection.

        Args:
            pop: Population to select from

        Returns:
            Selected individual
        """
        tournament = Population(cls.TOURNAMENT_SIZE, initialize=False)

        for i in range(cls.TOURNAMENT_SIZE):
            random_id = np.random.randint(pop.size())
            tournament.save_individual(i, pop.get_individual(random_id))

        return tournament.get_fittest()

    @classmethod
    def _is_twins(cls, ind1: Individual, ind2: Individual) -> bool:
        """
        Check if two individuals are too similar (twins).

        Args:
            ind1: First individual
            ind2: Second individual

        Returns:
            True if hamming distance is <= 2.5%
        """
        # Calculate hamming distance efficiently
        hamming_distance = np.sum(ind1.genes != ind2.genes)
        similarity_percent = (hamming_distance * 100.0) / ind1.size()

        return similarity_percent <= 2.50
