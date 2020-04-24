
import sys
import time

import numpy as np

from src.models.cities import SquareCity
from src.simulator.simulation import Simulation


size = [1,2,3]

matrix_time = []
for val in size:
    elapsed_time = []
    for _ in range(4):
        start = time.time()
        simulation = Simulation(1, 0.2, "central",".")

        simulation.set_simulation_units(speed=10, cell_length=5, simulation_speed=1, battery=0.1,cs_power=7)
        simulation.set_battery_distribution(lower=0.2, std=0.25)
        simulation.set_idle_distribution(upper=10, lower=2, std=0.25)
        simulation.create_city(SquareCity, RB_LENGTH=6, AV_LENGTH=4*7, INTERSEC_LENGTH=3, SCALE=val) 
        simulation.stations_placement(min_plugs_per_station=2, min_num_stations=10) 
        simulation.create_simulator()
        simulation.run(total_time=3, measure_period=0,repetitions=1)

        elapsed_time.append(time.time()-start)
    matrix_time.append(elapsed_time)

np.save("elapsed_full", np.array(matrix_time))
