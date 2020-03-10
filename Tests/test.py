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
import sys

if len(sys.argv) == 2:
    VISUAL = bool(sys.argv[1])
else:
    VISUAL = False



times = []
for _ in range(1):
    start = time.time()
    simulation = Simulation(0.5, 0.2, "central")

    simulation.set_simulation_units(speed=10, cell_length=5, simulation_speed=1, battery=0.1,cs_power=7)
    simulation.set_battery_distribution(lower=0.2, std=0.25)
    simulation.set_idle_distribution(upper=15, lower=5, std=0.25)
    simulation.create_city(SquareCity, RB_LENGTH=12, AV_LENGTH=4*13, INTERSEC_LENGTH=3, SCALE=2) 
    simulation.stations_placement(min_plugs_per_station=2, min_num_stations=10) 
    simulation.create_simulator()
    if VISUAL:
        vs = VisualRepresentation(simulation.SIZE, 700, 700, 70)
        vs.show_city(simulation.city_matrix)
        vs.show_stations(simulation.stations)
        
        vs.show_vehicles(simulation.vehicles, False)
        simulation.run(total_time=1, measure_period=0, repetitions=2, visual=vs)
    else:
        simulation.run(total_time=3, measure_period=0,repetitions=1)
    times.append(time.time()-start)

print("Media: ", np.mean(times))

