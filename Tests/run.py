# -*- coding: utf-8 -*-
import sys
from multiprocessing import Pool

import pyximport
pyximport.install()

import parameters as params
from simtravel.simulator.simulation import Simulation
from simtravel.models.cities import SquareCity



# Read the number of cores to use from the command line.
if len(sys.argv) == 2:
    NUM_PROCESS = int(sys.argv[1])
else:
    NUM_PROCESS = 1


# Create the combination of values we want to try.
sim_args = []
for ev in params.EV_DENSITY_VALUES:
    for tf in params.TF_DENSITY_VALUES:
        for ly in params.ST_LAYOUT_VALUES:
            sim_args.append((ev, tf, ly))


def run_simulation_with(args):
    
    # Create the simulation object
    simulation = Simulation(*args)
    # Set the simulation units.
    simulation.set_simulation_units(speed=params.SPEED, cell_length=params.CELL_LENGTH,
                                    simulation_speed=params.SIMULATION_SPEED,
                                    battery=params.BATTERY, cs_power=params.CS_POWER)
    # Set the battery and idle distribution
    simulation.set_battery_distribution(lower=params.BATTERY_THRESHOLD,
                                        std=params.BATTERY_STD)
    simulation.set_idle_distribution(upper=params.IDLE_UPPER,
                                     lower=params.IDLE_LOWER, std=params.IDLE_STD)
    # Create the city
    simulation.create_city(SquareCity, scale=params.SCALE,
                           block_scale=params.BLOCK_SCALE)
    simulation.stations_placement(min_plugs_per_station=params.MIN_PLUGS_PER_STATION,
                                  min_num_stations=params.MIN_D_STATIONS)
    # Create the simulator
    simulation.create_simulator()

    # Run the simulation
    simulation.run(total_time=params.TOTAL_TIME,
                   measure_period=params.MEASURE_PERIOD, repetitions=params.REPETITIONS)

if NUM_PROCESS == 1:
    for args in sim_args:
        run_simulation_with(args)
else:
    pool = Pool(NUM_PROCESS)
    results = pool.map_async(run_simulation_with, sim_args)
    results.get()
