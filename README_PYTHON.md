# EGAGP - Python Implementation

An **optimized Python implementation** of the Enhanced Genetic Algorithm for Producing Efficient Graph Partitions.

## Optimizations

This Python version includes several optimizations over the original Java implementation:

1. **NumPy for Performance**: Uses NumPy arrays for efficient numerical operations
2. **Vectorized Operations**: Replaces loops with vectorized NumPy operations where possible
3. **Type Hints**: Modern Python type hints for better code clarity and IDE support
4. **Pythonic Code**: Follows PEP 8 and Python best practices
5. **Modular Design**: Clean separation of concerns across modules
6. **Memory Efficiency**: Efficient array operations and data structures

## Installation

```bash
# Install dependencies
pip install -r requirements.txt
```

## Usage

```bash
# Run with data files in current directory
python egagp.py

# Run with data files in specific directory
python egagp.py /path/to/data/directory
```

## File Structure

- `fitness_calc.py` - Data extraction and fitness calculation
- `individual.py` - Individual (solution) representation
- `population.py` - Population management
- `algorithm.py` - GA operators (selection, crossover, mutation)
- `egagp.py` - Main driver program
- `requirements.txt` - Python dependencies

## Input Data Format

The program expects data files with the following format:

```
<number_of_vertices>
<number_of_edges>
<edge_data: vertex1 vertex2 cost>
...
<component_weights: w1 w2 ... wn>
<number_of_machines>
<number_of_machine_connections>
<machine_connection_data: machine1 machine2 cost>
...
<machine_capacities: m1 m2 ... mn>
```

## Algorithm Parameters

- **Population Size**: 20
- **Iterations**: 20 per data file
- **Max Generations**: 3000
- **Tournament Size**: 5
- **Elitism**: Enabled
- **Twin Removal**: Every 50 generations
- **Random Restart**: Every 100 generations if stuck

## Performance

The Python implementation with NumPy provides:
- Faster array operations through vectorization
- Lower memory footprint
- More readable and maintainable code
- Easy integration with scientific Python ecosystem

## Citation

If you use this code, please cite:

```
Shahriar, Fahim, Aakib Bin Nesar, Naweed Mohammad Mahbub, and Swakkhar Shatabda.
"EGAGP: An enhanced genetic algorithm for producing efficient graph partitions."
In 2017 4th International Conference on Networking, Systems and Security (NSysS),
pp. 1-9. IEEE, 2017.
```

## License

See the main repository for license information.
