from src.models.cities import SquareCity
from src.simulator.simulation import Simulation

from src.visual.visualOGL import VisualRepresentation
from src.analysis.analysis import SimulationAnalysis, GlobalAnalysis
import sys



# Create a Simulation
simulation = Simulation(1, 0.7, "four")
# Set the physical units
simulation.set_simulation_units(
    speed=10, cell_length=5, simulation_speed=1, battery=24, cs_power=1)
# Set the battery distribution
simulation.set_battery_distribution(lower=0.25, std=0.25)
simulation.set_idle_distribution(upper=5, lower=0, std=0.25)
# Create the city
simulation.create_city(SquareCity, RB_LENGTH=6, AV_LENGTH=4*9, INTERSEC_LENGTH=3, SCALE=2) 
# Place the stations around the city
simulation.stations_placement(min_plugs_per_station=2, min_num_stations=10)
# And finally create a simulator
simulation.create_simulator()

# Now, create a visual representation of the simulatoin and add the vehicles.
vs = VisualRepresentation(simulation.SIZE, 800,800, 1, simulation.city_matrix)
vs.add_vehicles(simulation.vehicles)
vs.add_stations(simulation.stations)

# Finally run the simulation with visual object.
simulation.run(total_time=4, measure_period=0, repetitions=2, visual=vs)

    



