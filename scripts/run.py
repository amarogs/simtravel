# -*- coding: utf-8 -*-
from src.models.cities import SquareCity
from src.simulator.simulation import Simulation
import sys
from multiprocessing import Pool
import multiprocessing
import yaml



parameters =None
with open("scripts/parameters.yaml", "r") as f:
    parameters = yaml.load(f, Loader=yaml.FullLoader)
    for k, v in parameters.items():
        globals()[k] = v

# Read the number of cores to use from the command line.
if len(sys.argv) == 2:
    NUM_PROCESS = int(sys.argv[1])
else:
    NUM_PROCESS = 1


# Create the combination of values we want to try.
ST_LAYOUT_VALUES = []
if ST_CENTRAL:
    ST_LAYOUT_VALUES.append("central")

if ST_DISTRIBUTED:
    ST_LAYOUT_VALUES.append("distributed")
if ST_FOUR:
    ST_LAYOUT_VALUES.append("four")


sim_args = []
for ev in EV_DENSITY_VALUES:
    for tf in TF_DENSITY_VALUES:
        for ly in ST_LAYOUT_VALUES:
            sim_args.append((ev, tf, ly, PATH))


def run_simulation_with(args):

    # Create the simulation object
    simulation = Simulation(*args)
    # Set the simulation units.
    simulation.set_simulation_units(speed=SPEED, cell_length=CELL_LENGTH,
                                    simulation_speed=SIMULATION_SPEED,
                                    battery=BATTERY, cs_power=CS_POWER, autonomy=AUTONOMY)
    # Set the battery and idle distribution
    simulation.set_battery_distribution(lower=BATTERY_THRESHOLD,
                                        std=BATTERY_STD)
    simulation.set_idle_distribution(upper=IDLE_UPPER,
                                    lower=IDLE_LOWER, std=IDLE_STD)
    # Create the city
    simulation.create_city(SquareCity, RB_LENGTH, AV_LENGTH, INTERSEC_LENGTH, SCALE) 

    simulation.stations_placement(min_plugs_per_station=MIN_PLUGS_PER_STATION,
                                min_num_stations=MIN_D_STATIONS)
    # Create the simulator
    simulation.create_simulator()

    # Run the simulation
    simulation.run(total_time=TOTAL_TIME,
                measure_period=MEASURE_PERIOD, repetitions=REPETITIONS)

if __name__ == "__main__":

    multiprocessing.freeze_support()

    if NUM_PROCESS == 1:
        for args in sim_args:
            run_simulation_with(args)
    else:
        pool = Pool(NUM_PROCESS)
        results = pool.map_async(run_simulation_with, sim_args)
        results.get()

    if pool:
        pool.close()