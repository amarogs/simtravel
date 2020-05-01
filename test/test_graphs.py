import unittest

from src.simulator.cythonGraphFunctions import lattice_distance, AStar
import src.models.cities as cities


class TestLatticeDistance(unittest.TestCase):

    def test_lattice_distance(self):
        sq = cities.SquareCity(6, 7*4, 2)
        # With this city the SIZE = 72

        self.assertEqual(lattice_distance(0,0,0,0 ), 0, "Lattice distance for zero distance not working")
        self.assertEqual(lattice_distance(0,0, 10,10), 20, "Lattice distance same cuadrant not working")
        self.assertEqual(lattice_distance(0,0, 71, 71), 2), "Lattice distance different cuadrants not working"
        self.assertEqual(lattice_distance(10,10, 50, 50), 64), "Lattice distance different cuadrants not working"
    
class TestAStar(unittest.TestCase):
    
    def test_path_length(self):
        sq = cities.SquareCity(6, 7*4, 2)
    