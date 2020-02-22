# -*- coding: utf-8 -*-
import os
import random
import time

import h5py

from src.metrics.metrics import SimulationMetric, SimulationSnapshot
from src.metrics.units import Units
from src.models.station import Station
from src.models.vehicle import ElectricVehicle, Vehicle
from src.simulator.simulator import Simulator

# from src.graphlib.pygraphFunctions import Graph


class Simulation():
    def __init__(self, EV_DEN, TF_DEN, ST_LAYOUT):
        """Creates a Simulation object receiving:

        :param TF_DEN: traffic density of the simulation, it is expressed
        as a percentage of the total drivable cells. A TF_DEN of 1 means
        that every possible cell in the city is occupied by a vehicle.

        :param EV_DEN: electric vehicle dendisty, it's the proportion
        of EVs relative to the total amount of vehicles.

        :param ST_LAYOUT: is the layout of the stations, can either be
        'distributed', 'central' or 'four'.

        In order for the simulation to work, once the Simulation object
        is created, the following methods must be called:

        Simulation.set_simulation_units()
        Simulation.set_battery_distribution()
        Simulation.set_idle_distribution()
        Simulation.create_city()
        Simulation.stations_placement()
        Simulation.create_simulator()

        """
        super().__init__()

        # Attributes that define a simulation
        self.EV_DEN = EV_DEN
        self.TF_DEN = TF_DEN
        self.ST_LAYOUT = ST_LAYOUT
        self.filename = "results/{}#{}#{}".format(
            self.EV_DEN, self.TF_DEN, self.ST_LAYOUT)
        # Attributes filled in the method set_simulation_units()
        self.units = None

        # Attributes filled in the method create_city()
        self.city_builder = None
        self.SCALE = None
        self.BLOCK_SCALE = None
        self.city_map = None
        self.city_matrix = None
        self.avenues = None
        self.SIZE = None
        self.STR_RATE = None
        

        # Attributes filled in the method stations_placement()
        self.TOTAL_PLUGS = None  # Total number of plugs in the city
        self.TOTAL_D_ST = None  # Total number of distributed stations
        self.stations = None
        self.stations_map = None

    def set_simulation_units(self, speed=10, cell_length=5, simulation_speed=1, battery=24, cs_power=7, autonomy=135):
        self.units = Units(speed, cell_length, simulation_speed,
                           battery, cs_power, autonomy)

        # Write the attributes in orde to save them in the HDF5 file.
        self.SPEED = speed
        self.CELL_LENGTH = cell_length
        self.SIMULATION_SPEED = simulation_speed
        self.BATTERY = battery
        self.CS_POWER = cs_power
        self.AUTONOMY = autonomy

    def create_city(self, Builder, scale=1, block_scale=1):
        """Builder is a CityBuilder class, scale and block_scale control
        the final size of the city. """

        # Create the city builder
        self.city_builder = Builder(scale, block_scale)
        self.city_map = self.city_builder.city_map
        self.city_map_graph = self.city_builder.city_map_graph
        #self.graph = Graph(self.city_map_graph)
        
        self.city_matrix = self.city_builder.city_matrix
        self.avenues = self.city_builder.avenues
        self.SCALE = scale
        self.BLOCK_SCALE = block_scale
        self.SIZE = self.city_builder.SIZE
        self.STR_RATE = self.city_builder.STR_RATE

        # Create the city districts
        self.districts = self.city_builder.create_districts(self.ST_LAYOUT)

    def stations_placement(self, min_plugs_per_station, min_num_stations):
        """This method computes the number total number of distributed stations
        that are needed in order to make the city symmetrical and compatible 
        between different stations layour, for example the total number of distributed stations
        need to be a divisor of 4. Then computes the placement of the stations
        for this simulation and creates the simulation objects with the correct
        amount of chargers.

        :param min_plugs_per_station: is the minimum number of plugs that we 
        want each distrbuted station to have.
        :param min_num_stations: is the minimum number of distributed stations
        that we want to have in a simulation with the ST_LAYOUT = "distributed"
        """

        # Compute the amount of plugs and the number of distributed stations
        self.TOTAL_PLUGS, self.TOTAL_D_ST = self.city_builder.set_max_chargers_stations(
            min_plugs_per_station, min_num_stations)

        # Place the stations around the city based on the layout
        self.stations_pos = self.city_builder.place_stations(
            self.ST_LAYOUT, self.districts, self.TOTAL_D_ST)
        # Based on the layout, compute the number of plugs that each station
        # will have.
        plugs_per_station = min_plugs_per_station
        if self.ST_LAYOUT == "central":
            plugs_per_station = self.TOTAL_PLUGS
        elif self.ST_LAYOUT == "four":
            plugs_per_station = self.TOTAL_PLUGS/4

        # Create the stations and the stations map
        self.stations, self.stations_map = self.create_stations(
            self.stations_pos, plugs_per_station)

    def create_stations(self, stations_pos, plugs_per_station):
        """:param stations_pos: a dictionary where the
        keys are tuple of 4 elements defining a district and the value is
        a list of positions where a station must be placed.
        :param plugs_per_station: is the number of plugs that a station can have.
         """
        stations = []
        stations_map = {}
        for district, positions in stations_pos.items():
            # For each station position in the district, create a Station object
            district_stations = [Station(pos, plugs_per_station)
                                 for pos in positions]
            # For each position inside the district, if it is a drivable cell
            # reference the list of stations.
            (C1, C2, R1, R2) = district
            for i in range(C1, C2):
                for j in range(R1, R2):
                    if (i, j) in self.city_map:
                        stations_map[(i, j)] = district_stations
            # Add the stations to the list of stations
            stations.extend(district_stations)

        return stations, stations_map

    def set_battery_distribution(self, lower, std):
        """This method sets the parameters of the normal distribution used
        to set the goal charge of a vehicle when it wants to recharge.
        :param lower: Is the minimum amount to recharge. 1 sets the lower 
        limit to 100% of the vehicle's autonomy while 0 sets the lower
        limit to 0% of the vehicle's autonomy.
        :param std: is the deviation of the distribution with respect
        to the mean. A value of 1 means a deviation equal to 100% of the mean
        while a value of 0 means no deviation at all.

        Internally the battery values are expressed as autonomy in simulation cells.
        """

        self.BATTERY_UPPER = int(self.units.autonomy)
        self.BATTERY_LOWER = int(lower * self.units.autonomy)
        self.BATTERY_MEAN = (lower + self.BATTERY_UPPER) // 2
        self.BATTERY_STD = std * self.BATTERY_MEAN

    def set_idle_distribution(self, upper, lower, std):
        """This method sets the parameters of the normal distribution used
        to compute the amount of time a vehicle is idle at a destination.
        :param upper: Is the maximum time, in minutes, that a vehicle can
        stay idle.
        :param lower: Is the minimum time, in minutes, that a vehicle can 
        stay idle.
        :param std: controls the deviation with respect to the mean. A value
        of 1 means a deviation equal to 100% while a deviation of 0 no deviation
        at all.

        Internally the idle times are expressed as simulation time steps.
        """
        self.IDLE_UPPER = int(self.units.minutes_to_steps(upper))
        self.IDLE_LOWER = int(self.units.minutes_to_steps(lower))
        self.IDLE_MEAN = (self.IDLE_UPPER + self.IDLE_LOWER) // 2
        self.IDLE_STD = std * self.IDLE_MEAN

    def create_vehicles(self):
        """Creates the vehicles and places them around the city.
        Initially all the vehicles are in the AT_DEST state waiting to be released.
        The realeasing follows the same distribution as the idle time spent at a destination."""

        # Add constants to the simulation object
        self.TOTAL_VEHICLES = int(
            self.STR_RATE * self.SIZE * self.SIZE * self.TF_DEN)

        self.TOTAL_EV = int(self.EV_DEN * self.TOTAL_VEHICLES)

        # Create the vehicles, place them on the city.
        # Initially all the vehicles are in a AT_DEST
        # state and so they don't occupy a place.
        city_positions = list(self.city_map.keys())
        random.shuffle(city_positions)

        ev_vehicles = set()
        vehicles = []
        for _ in range(self.TOTAL_EV):
            v = ElectricVehicle(city_positions.pop(),
                                self.simulator.compute_idle(), self.simulator.compute_battery())
            vehicles.append(v)
            ev_vehicles.add(v)
        for _ in range(self.TOTAL_VEHICLES-self.TOTAL_EV):
            v = Vehicle(city_positions.pop(), self.simulator.compute_idle())
            vehicles.append(v)

        self.vehicles = vehicles
        self.ev_vehicles = ev_vehicles

    def create_simulator(self):
        """Creates the simulator object.
        Then it also creates the vehicles calling Simulation.create_vehicles() """
        self.simulator = Simulator(self)
        self.create_vehicles()

    def print_summary(self):
        msg = """*******************************************************\
            \nInitializing the simulation: {}\
            \nThe size of the city is: {} \
            \nThis will run for {} tsteps, taking measures every {} tsteps.\
            \nThe battery distribution has a mean of {} steps and std of {} steps.\
            \nThe idle distribution has a mean of {} steps and std of {} steps.\
            \nIn total there is {} vehicles being electric {} """\
            .format(self.filename,self.SIZE ,self.TOTAL_TSTEPS, self.DELTA_TSTEPS, self.BATTERY_MEAN,
                    self.BATTERY_STD, self.IDLE_MEAN, self.IDLE_STD, self.TOTAL_VEHICLES, self.TOTAL_EV)
        print(msg)

    def set_progress_message(self, num_progress_msg):
        """Computes a list of tsteps that will prompt a message displaying
        the progress of the simulation. """

        self.progress_tsteps = [int(((i+1)*self.TOTAL_TSTEPS)/(num_progress_msg*self.DELTA_TSTEPS))*self.DELTA_TSTEPS
                                for i in range(num_progress_msg)]

    def print_progress(self, tstep):
        progress = int(100*(tstep/self.TOTAL_TSTEPS))
        msg = """Simulation: {} Repetition: {} Progress: {}% """.format(
            self.filename, self.repetition, progress)
        print(msg)

    def prepare_results_file(self):
        """Checks if the results folder exists and truncates the destination
        file."""

        # Check if the results folder exists.
        if not os.path.exists("results"):
            os.makedirs("results")
        else:
            with open(self.filename + ".hdf5", "w"):
                pass

    def write_header_attr(self):
        """This method writes the global attributes of the simulation as HDF5
        attributes of the root group. """

        # Write the attributes
        with h5py.File(self.filename + ".hdf5", "a") as f:
            for key, value in self.__dict__.items():
                if key.isupper():
                    f.attrs[key] = value

    def write_results(self, repetition, metrics):
        """Once the simulation is over, the results are written to a HDF5 file.
        The name of the file is made with the attributes EV_DEN#TF_DEN#ST_LAYOUT that
        identify a simulation. For each repetion a group is made with the index of
        the repetition and the data is saved into datasets."""

        with h5py.File(self.filename+".hdf5", "a") as f:
            metrics.write_results(
                f, "/"+str(repetition)+"/", self.simulator.seeking_history, self.simulator.queueing_history)

    def run(self, total_time, measure_period, repetitions, visual=None):
        """ Method to execute the simulation. The attributes are given
        in the SI, time (hours) and measure_period (minutes).

        :param time: total time to simulate in hours
        :param measure_period: time between two consecutive snapshots of the system.
        :param repetitions: number of times the simulation is run.
         """
        # Convert the time to simulation steps
        total_tsteps = int(self.units.minutes_to_steps(total_time*60))
        delta_tsteps = int(self.units.minutes_to_steps(measure_period))

        if delta_tsteps == 0:
            delta_tsteps = 1

        self.TOTAL_TSTEPS = total_tsteps
        self.DELTA_TSTEPS = delta_tsteps
        self.REPETITIONS = repetitions
        
        # Set the list of tsetps for displaying a message
        self.set_progress_message(10)

        # Prepare the HDF5 file
        self.prepare_results_file()

        self.print_summary()

        elapsed = time.time()
        for i in range(repetitions):
            self.repetition = i

            # Restart the vehicles, the stations and the simulator
            for v in self.vehicles:
                v.restart()
            for st in self.stations:
                st.restart()
            self.simulator.restart()

            # Create a metrics object and initilize it
            metrics = SimulationMetric(
                self.city_map, self.stations, 3, total_tsteps, delta_tsteps, self.SIZE)
            metrics.initialize(
                self.vehicles, self.ev_vehicles, self.stations)

            # Run the simulation using the simulator object
            if visual == None:
                self.run_simulator(metrics)
            else:
                self.run_simulator_visual(metrics, visual)
                
                

            # Store the data into an HDF5 file.
            self.write_results(i, metrics)

        self.ELAPSED = round((time.time() - elapsed) / repetitions, 3)

        self.write_header_attr()

    def run_simulator(self, metrics):
        """This method controls the flow of the simulator, saving the
        data and displaying a progress message. """

        previous_snapshot = SimulationSnapshot(self.vehicles)

        for current_tstep in range(1, self.TOTAL_TSTEPS+1):
            
            # Compute next step of the simulation
            self.simulator.next_step()

            # Check if we have to update the data collection
            if current_tstep % self.DELTA_TSTEPS == 0:
                current_snapshot = SimulationSnapshot(self.vehicles)
                metrics.update_data(self.vehicles, self.ev_vehicles, self.stations,
                                    current_snapshot, previous_snapshot, current_tstep)
                previous_snapshot = current_snapshot

            # Check if we have to display a progress message
            if current_tstep in self.progress_tsteps:
                self.print_progress(current_tstep)

    def run_simulator_visual(self, metrics, visual):
        """This method controls the flow of the simulator, saving the
        data and displaying a progress message. """

        
        self.previous_snapshot = SimulationSnapshot(self.vehicles)
        def next_frame():

            # Compute next step of the simulation
            self.simulator.next_step()
            visual.update()
            current_tstep = visual.current_tstep
            # Check if we have to update the data collection
            if current_tstep % self.DELTA_TSTEPS == 0:
                current_snapshot = SimulationSnapshot(self.vehicles)
                metrics.update_data(self.vehicles, self.ev_vehicles, self.stations, current_snapshot, self.previous_snapshot, current_tstep)
                self.previous_snapshot = current_snapshot

            # Check if we have to display a progress message
            if current_tstep in self.progress_tsteps:
                self.print_progress(current_tstep)

            # Increment the steps counter
            visual.current_tstep += 1

            # Check for termination
            if visual.current_tstep == self.TOTAL_TSTEPS:
                "Terminar la visualizacion"
                pass


            
        visual.beginRepresentation(next_frame)
            

