"""
Fitness calculation and data extraction module for EGAGP.
Optimized using NumPy for efficient array operations.
"""

import numpy as np
from typing import Tuple


class FitnessCalc:
    """Handles data extraction and storage for the genetic algorithm."""

    # Component communication cost matrix
    C: np.ndarray = None
    # Weight of each component
    W: np.ndarray = None
    # Machine communication cost matrix
    B: np.ndarray = None
    # Machine capacity array
    M: np.ndarray = None

    number_of_machines: int = 0
    number_of_vertices: int = 0

    @classmethod
    def extract_data(cls, path: str) -> None:
        """
        Extract graph and machine data from file.

        Args:
            path: Path to the data file
        """
        with open(path, 'r') as file:
            lines = [line.strip() for line in file.readlines()]

        idx = 0

        # Read graph (components) data
        n = int(lines[idx])
        idx += 1
        m = int(lines[idx])
        idx += 1

        cls.number_of_vertices = n
        cls.C = np.zeros((n, n), dtype=np.float64)

        # Read edges
        for _ in range(m):
            parts = lines[idx].split()
            x, y, cost = int(parts[0]), int(parts[1]), float(parts[2])
            cls.C[x, y] = cost
            cls.C[y, x] = cost  # Symmetric
            idx += 1

        # Read component weights
        cls.W = np.array([float(x) for x in lines[idx].split()], dtype=np.float64)
        idx += 1

        # Read machine data
        n = int(lines[idx])
        idx += 1
        m = int(lines[idx])
        idx += 1

        cls.number_of_machines = n
        cls.B = np.full((n, n), 1000000.0, dtype=np.float64)

        # Read machine connections
        for _ in range(m):
            parts = lines[idx].split()
            x, y, cost = int(parts[0]), int(parts[1]), float(parts[2])
            cls.B[x, y] = cost
            cls.B[y, x] = cost  # Symmetric
            idx += 1

        # Read machine capacities
        cls.M = np.array([float(x) for x in lines[idx].split()], dtype=np.float64)
