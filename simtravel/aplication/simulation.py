# -*- coding: utf-8 -*-
from simtravel.metrics.metrics import SimulationMetric
from simtravel.metrics.units import Units
from simtravel.models.station import Station
from simtravel.models.vehicle import ElectricVehicle, Vehicle
from simtravel.simulator.simulator import Simulator

import h5py
import random


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
        self.filename = "{}#{}#{}".format(
            self.EV_DEN, self.TF_DEN, self.ST_LAYOUT)
        # Attributes filled in the method set_simulation_units()
        self.units = None

        # Attributes filled in the method create_city()
        self.city_builder = None
        self.scale = None
        self.block_scale = None
        self.city_map = None
        self.city_matrix = None
        self.SIZE = None
        self.STR_RATE = None

        # Attributes filled in the method stations_placement()
        self.total_plugs = None  # Total number of plugs in the city
        self.total_d_st = None  # Total number of distributed stations
        self.stations = None
        self.stations_map = None

    def set_simulation_units(self, speed=10, cell_length=5, simulation_speed=1, battery=24, cs_power=7, autonomy=135):
        self.units = Units(speed, cell_length, simulation_speed,
                           battery, cs_power, autonomy)

    def create_city(self, Builder, scale=1, block_scale=1):
        """Builder is a CityBuilder class, scale and block_scale control
        the final size of the city. """

        # Create the city builder
        self.city_builder = Builder(scale, block_scale)
        self.city_map = self.city_builder.city_map
        self.city_matrix = self.city_builder.city_matrix
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
        self.total_plugs, self.total_d_st = self.city_builder.set_max_chargers_stations(
            min_plugs_per_station, min_num_stations)

        # Place the stations around the city based on the layout
        self.stations_pos = self.city_builder.place_stations(
            self.ST_LAYOUT, self.districts, self.total_d_st)
        # Based on the layout, compute the number of plugs that each station
        # will have.
        plugs_per_station = min_plugs_per_station
        if self.ST_LAYOUT == "central":
            plugs_per_station = self.total_plugs
        elif self.ST_LAYOUT == "four":
            plugs_per_station = self.total_plugs/4

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
            \nThis will run for {} tsteps, taking measures every {} tsteps.\
            \nThe battery distribution has a mean of {} steps and std of {} steps.\
            \nThe idle distribution has a mean of {} steps and std of {} steps.\
            \nIn total there is {} vehicles being electric {} """\
            .format(self.filename, self.TOTAL_TSTEPS, self.DELTA_TSTEPS, self.BATTERY_MEAN,\
                    self.BATTERY_STD, self.IDLE_MEAN, self.IDLE_STD, self.TOTAL_VEHICLES, self.TOTAL_EV)
        print(msg)

    def write_header_attr(self):
        """This method writes the global attributes of the simulation as HDF5
        attributes of the root group. """
        with open(self.filename + ".hdf5", "w"):
            pass
    def run(self, time, measure_period, repetitions, visual=None):
        """ Method to execute the simulation. The attributes are given
        in the SI, time (hours) and measure_period (minutes).

        :param time: total time to simulate in hours
        :param measure_period: time between two consecutive snapshots of the system.
        :param repetitions: number of times the simulation is run.
         """

        total_tsteps = int(self.units.minutes_to_steps(time*60))
        delta_tsteps = int(self.units.minutes_to_steps(measure_period))
        self.TOTAL_TSTEPS = total_tsteps
        self.DELTA_TSTEPS = delta_tsteps
        self.write_header_attr()
        self.print_summary()

        # FUNCION QUE ESCRIBE LA CABECERA Y CREA EL ARCHIVO
        for i in range(repetitions):

            # Restart the vehicles, the stations and the simulator
            for v in self.vehicles:
                v.restart()
            for st in self.stations:
                st.restart()
            self.simulator.restart()
            # Create a metrics object and initilize it
            self.metrics = SimulationMetric(
                self.city_map, self.stations, 3, total_tsteps, delta_tsteps, self.SIZE)
            self.metrics.initialize(
                self.vehicles, self.ev_vehicles, self.stations)

            # Run the simulation using the simulator object
            if visual != None:
                self.simulator.run_simulation_visual(
                    total_tsteps, delta_tsteps, visual)
            else:
                self.simulator.run_simulation(
                    total_tsteps, delta_tsteps)

            # Store the data into an HDF5 file.
            self.write_results(i)

    def write_results(self, repetition):
        """Once the simulation is over, the results are written to a HDF5 file.
        The name of the file is made with the attributes EV_DEN#TF_DEN#ST_LAYOUT that
        identify a simulation. For each repetion a group is made with the index of
        the repetition and the data is saved into datasets."""

        with h5py.File(self.filename+".hdf5", "a") as f:
            self.metrics.write_results(
                f, "/"+str(repetition)+"/", self.ev_vehicles)

    def update_data(self, current_snapshot, previous_snapshot, current_tstep):
        """Computes and stores data, it's a direct call to SimulationMetric.update_data() """
        self.metrics.update_data(self.vehicles, self.ev_vehicles, self.stations,
                                 current_snapshot, previous_snapshot, current_tstep)
