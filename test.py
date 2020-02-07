# import pyximport
# pyximport.install()

from src.models.cities import SquareCity
from src.simulator.simulation import Simulation
import h5py
import matplotlib.pyplot as plt
import numpy as np

import time

from src.visual.graphics import VisualRepresentation
from src.analysis.analysis import SimulationAnalysis, GlobalAnalysis

times = []
for _ in range(10):
    start = time.time()
    simulation = Simulation(0.5, 0.1, "four")

    simulation.set_simulation_units(speed=10, cell_length=5, simulation_speed=1, battery=24,cs_power=7)
    simulation.set_battery_distribution(lower=0.25, std=0.2)
    simulation.set_idle_distribution(upper=2, lower=1, std=0.3)
    simulation.create_city(SquareCity, scale=1, block_scale=2) 
    simulation.stations_placement(min_plugs_per_station=2, min_num_stations=10) 
    simulation.create_simulator()

    # vs = VisualRepresentation(simulation.SIZE, 700, 700, 70)
    # vs.show_city(simulation.city_matrix)
    # vs.show_stations(simulation.stations)
    # vs.show_vehicles(simulation.vehicles, False)
    # vs.freeze()
    simulation.run(total_time=1, measure_period=1, repetitions=2)#, visual=vs)
    times.append(time.time()-start)
print("Media: ", np.mean(times))

# with h5py.File(simulation.filename + ".hdf5", "r") as f:
#     for k, vl in f.attrs.items():
#         print(k,vl)
#     direct = "/0/heat_map/2"
#     dst = f[direct]
#     a = np.zeros(dst.shape)
#     dst.read_direct(a)
#     plt.imshow(a, cmap="hot")
#     plt.show()



# import pyximport
# pyximport.install()
# from src.analysis.analysis import *
# import numpy as np

# attrs = get_attributes_results("results")
# simulations = [analize_simulation(attr) for attr in attrs]
# g = GlobalAnalysis(attrs, 'seeking', 'queueing', 'speed', 'mobility', 'total', 'elapsed')
# g.load_matrices(simulations)
# g.load_single_attribute(simulations, 'TOTAL_VEHICLES')
# g.create_report()

# analysis = SimulationAnalysis(0.5, 0.3, 'four')
# analysis.load_data("results/0.5#0.3#four.hdf5")
# analysis.generate_report()
# analysis.graph_states_evolution()

# analysis.graph_occupation_evolution()
# analysis.heat_map_graph()
# analysis.graph_velocities()

