#!/usr/bin/env python3
"""
Simple test to verify the Python implementation works correctly.
"""

import sys
from fitness_calc import FitnessCalc
from population import Population
from individual import Individual
from algorithm import Algorithm


def test_basic_functionality():
    """Test basic functionality without full GA run."""
    print("=" * 60)
    print("Testing EGAGP Python Implementation")
    print("=" * 60)

    # Test 1: Data loading
    print("\n1. Testing data loading...")
    try:
        FitnessCalc.extract_data("test_data.txt")
        print(f"   ✓ Data loaded successfully")
        print(f"   - Vertices: {FitnessCalc.number_of_vertices}")
        print(f"   - Machines: {FitnessCalc.number_of_machines}")
        print(f"   - Component weights: {FitnessCalc.W}")
        print(f"   - Machine capacities: {FitnessCalc.M}")
    except Exception as e:
        print(f"   ✗ Failed: {e}")
        return False

    # Test 2: Individual creation
    print("\n2. Testing individual generation...")
    try:
        ind = Individual()
        ind.generate_valid_individual()
        print(f"   ✓ Valid individual generated")
        print(f"   - Genes: {ind.genes}")
        print(f"   - Valid: {ind.is_valid() == Individual.VALID}")
    except Exception as e:
        print(f"   ✗ Failed: {e}")
        return False

    # Test 3: Fitness calculation
    print("\n3. Testing fitness calculation...")
    try:
        fitness = ind.get_fitness()
        graph_cut = ind.get_graph_cut_cost()
        print(f"   ✓ Fitness calculated")
        print(f"   - Fitness: {fitness:.2f}")
        print(f"   - Graph cut cost: {graph_cut:.2f}")
    except Exception as e:
        print(f"   ✗ Failed: {e}")
        return False

    # Test 4: Population creation
    print("\n4. Testing population creation...")
    try:
        pop = Population(5, initialize=True)
        print(f"   ✓ Population created with {pop.size()} individuals")
        fittest = pop.get_fittest()
        if fittest:
            print(f"   - Fittest fitness: {fittest.get_fitness():.2f}")
    except Exception as e:
        print(f"   ✗ Failed: {e}")
        return False

    # Test 5: Crossover
    print("\n5. Testing crossover...")
    try:
        parent1 = Individual()
        parent1.generate_valid_individual()
        parent2 = Individual()
        parent2.generate_valid_individual()

        offspring = Individual()
        offspring.one_point_crossover(parent1, parent2)
        print(f"   ✓ Crossover performed")
        print(f"   - Offspring genes: {offspring.genes}")
    except Exception as e:
        print(f"   ✗ Failed: {e}")
        return False

    # Test 6: Evolution
    print("\n6. Testing evolution (1 generation)...")
    try:
        new_pop = Algorithm.evolve_population(pop)
        new_fittest = new_pop.get_fittest()
        print(f"   ✓ Population evolved")
        if new_fittest:
            print(f"   - New fittest fitness: {new_fittest.get_fitness():.2f}")
    except Exception as e:
        print(f"   ✗ Failed: {e}")
        return False

    # Test 7: Quick GA run
    print("\n7. Running mini GA (10 generations)...")
    try:
        pop = Population(10, initialize=True)
        initial_fitness = pop.get_fittest().get_fitness()

        for gen in range(10):
            pop = Algorithm.evolve_population(pop)

        final_fitness = pop.get_fittest().get_fitness()
        final_cut = pop.get_fittest().get_graph_cut_cost()

        print(f"   ✓ GA completed")
        print(f"   - Initial fitness: {initial_fitness:.2f}")
        print(f"   - Final fitness: {final_fitness:.2f}")
        print(f"   - Final graph cut: {final_cut:.2f}")
        print(f"   - Improvement: {initial_fitness - final_fitness:.2f}")
    except Exception as e:
        print(f"   ✗ Failed: {e}")
        return False

    print("\n" + "=" * 60)
    print("All tests passed! ✓")
    print("=" * 60)
    return True


if __name__ == "__main__":
    success = test_basic_functionality()
    sys.exit(0 if success else 1)
