<<<<<<< HEAD
import time

import h5py
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np

from src.analysis.analysis import SimulationAnalysis
from src.simulator.simulation import Simulation

from src.models.cities import SquareCity
from src.simulator.simulator import *
from src.visual.graphics import VisualRepresentation

start = time.time()
simulation = Simulation(0.5, 0.3, "four")

simulation.set_simulation_units(
    speed=10, cell_length=5, simulation_speed=1, battery=24, cs_power=7)
simulation.set_battery_distribution(lower=0.25, std=0.2)
simulation.set_idle_distribution(upper=2, lower=1, std=0.3)
simulation.create_city(SquareCity, scale=4, block_scale=2)
simulation.stations_placement(min_plugs_per_station=2, min_num_stations=10)

edges = []
for pos in simulation.city_map:
    edges += [(pos, v[0], v[1]) for v in simulation.city_map[pos]]
g = nx.DiGraph()
g.add_weighted_edges_from(edges)


path = nx.astar_path(g, (16,29), (19,31), lattice_distance);
del path[0];
path = list(reversed(path))

# print(path)

# path = a_star((16,29), (19,31))
=======
import time

import h5py
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np

from src.analysis.analysis import SimulationAnalysis
from src.simulator.simulation import Simulation

from src.models.cities import SquareCity
from src.simulator.simulator import *
from src.visual.graphics import VisualRepresentation

start = time.time()
simulation = Simulation(0.5, 0.3, "four")

simulation.set_simulation_units(
    speed=10, cell_length=5, simulation_speed=1, battery=24, cs_power=7)
simulation.set_battery_distribution(lower=0.25, std=0.2)
simulation.set_idle_distribution(upper=2, lower=1, std=0.3)
simulation.create_city(SquareCity, scale=4, block_scale=2)
simulation.stations_placement(min_plugs_per_station=2, min_num_stations=10)

edges = []
for pos in simulation.city_map:
    edges += [(pos, v[0], v[1]) for v in simulation.city_map[pos]]
g = nx.DiGraph()
g.add_weighted_edges_from(edges)


path = nx.astar_path(g, (16,29), (19,31), lattice_distance);
del path[0];
path = list(reversed(path))

# print(path)

# path = a_star((16,29), (19,31))
>>>>>>> e837e38783576096c1b556938763b3c2038d2860
# print(path)