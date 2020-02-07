from src.analysis.analysis import SimulationAnalysis, GlobalAnalysis
from src.visual.graphics import VisualRepresentation
import time
import numpy as np
import matplotlib.pyplot as plt
import h5py
from src.simulator.simulation import Simulation
from src.models.cities import SquareCity
import pyximport
pyximport.install()

from src.graphlib.pygraphFunctions import Graph
simulation = Simulation(0.5, 0.3, "four")

simulation.set_simulation_units(
    speed=10, cell_length=5, simulation_speed=1, battery=24, cs_power=7)
simulation.set_battery_distribution(lower=0.25, std=0.2)
simulation.set_idle_distribution(upper=2, lower=1, std=0.3)
simulation.create_city(SquareCity, scale=1, block_scale=1)
simulation.stations_placement(min_plugs_per_station=2, min_num_stations=10)
simulation.create_simulator()

start, end = (35,34),(1,29)
g = Graph(simulation.city_map_graph,2)
