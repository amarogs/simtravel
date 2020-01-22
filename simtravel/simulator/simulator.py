# -*- coding: utf-8 -*-
import copy
import numpy as np
import random

from simtravel.models.states import States
from simtravel.models.station import Station
from simtravel.models.vehicle import ElectricVehicle, Vehicle
from simtravel.simulator import graphs


class Simulator:

    def __init__(self, city_map, avenues, CHAR_RATE):
        """
        :param city_map: is the graph of the city, given a position returns the list of
            neighboring cells.
        :param avenues: is a set of cell that are avenues

         """
        super().__init__()

        # Set attributes
        self.city_map = city_map
        self.city_state = {pos: 1 for pos in self.city_map}
        self.city_positions = list(city_map.keys())
        self.avenues = avenues
        self.CHARGING_RATE = CHAR_RATE
        self.vehicles = None  # List of vehicles
        self.ev_vehicles = None  # Set of ev vehicles
        self.stations = None  # List of stations
        self.stations_map = None #Dictionary where each position of the city has a list of stations

        # Dictionary where the key is a state and the value the function
        # associated with that state
        self.next_function = {States.AT_DEST: self.at_destination,
                              States.TOWARDS_DEST: self.towards_destination,
                              States.TOWARDS_ST: self.towards_station,
                              States.QUEUEING: self.queueing, States.CHARGING: self.charging,
                              States.NO_BATTERY: self.no_battery}

    def create_vehicles(self, EV_DEN, TF_DEN, SIZE, STR_RATE):
        """Creates the vehicles and places them around the city.
        Initially all the vehicles are in the AT_DEST
        state waiting to be released. The realeasing follows the
        same distribution as the idle time spent at a destination."""

        # Add constants to the simulator object
        self.EV_DEN = EV_DEN
        self.TF_DEN = TF_DEN
        self.TOTAL_VEHICLES = int(STR_RATE * SIZE * SIZE * TF_DEN)
        self.TOTAL_EV = int(EV_DEN * self.TOTAL_VEHICLES)

        # Create the vehicles, place them on the city.
        # Initially all the vehicles are in a AT_DEST
        # state and so they don't occupy a place.

        city_positions_copy = copy.copy(self.city_positions)
        random.shuffle(city_positions_copy)
        ev_vehicles = set()
        vehicles = []

        for _ in range(self.TOTAL_EV):
            v = ElectricVehicle(city_positions_copy.pop(),
                                self.compute_idle(), self.compute_battery())
            vehicles.append(v)
            ev_vehicles.add(v)
        for _ in range(self.TOTAL_VEHICLES-self.TOTAL_EV):
            v = Vehicle(city_positions_copy.pop(), self.compute_idle())
            vehicles.append(v)

        self.vehicles = vehicles
        self.ev_vehicles = ev_vehicles

        return self.vehicles

    def create_stations(self,stations_per_district, num_plugs):
        """:param stations_per_district: a dictionary where the
        keys are tuple of 4 elements defining a district and the value is
        a list of positions where a station must be placed.
        :param num_plugs: is the number of plugs that a station can have.
         """
        stations = []
        stations_map = {}
        for district, positions in stations_per_district.items():
            # For each station position in the district, create a Station object
            district_stations = [Station(pos, num_plugs) for pos in positions]
            # For each position inside the district, if it is a drivable cell
            # reference the list of stations.
            (C1, C2, R1, R2) = district
            for i in range(C1, C2):
                for j in range(R1, R2):
                    if (i, j) in self.city_map:
                        stations_map[(i, j)] = district_stations
            # Add the stations to the list of stations
            stations.extend(district_stations)

        # Save the data as class attributes
        self.stations = stations
        self.stations_map = stations_map
        return self.stations
    def choose_station(self, pos):
        return random.choice(self.stations_map[pos])
    def next_step(self):
        """For each vehicle, computes the next step in their algorithm."""
        for vehicle in self.vehicles:
            self.next_function[vehicle.state](vehicle)

    def towards_destination(self, vehicle):
        """Function called when a vehicle has State.TOWARDS_DEST."""
        electric = False
        if vehicle in self.ev_vehicles:
            electric = True

        if self.compute_next_position(vehicle, vehicle.destination, electric):
            # If we have reached the destination:
            # set the position as a free position
            self.city_state[vehicle.pos] = 1
            # set the vehicles' state to at destination
            vehicle.state = States.AT_DEST
            # set the amount of time the vehicle must
            # stay idle at destination
            vehicle.wait_time = self.compute_idle()
            vehicle.idle_history.append(vehicle.wait_time)
        elif electric:
            if vehicle.battery <= self.BATTERY_LOWER:
                # The vehicle is running out of battery and needs to recharge
                vehicle.state = States.TOWARDS_ST  # Set the state to "towards station"
                vehicle.station = self.choose_station(
                    vehicle.pos)  # Choose the station
                vehicle.path = graphs.a_star(vehicle.pos, vehicle.station.pos)
                vehicle.seeking = 0  # Start the seeking counter
            elif vehicle.battery == 0:
                # The vehicle has run out of battery
                # Set the vehicle's position as free.
                self.no_battery(vehicle)
    
    def no_battery(self, vehicle):
        """Operations made when a vehicle runs out of battery.

        It makes the vehicle invisible to the traffic.
        """
        self.city_state[vehicle.pos] = 1
        vehicle.state = States.NO_BATTERY

    def at_destination(self, vehicle):
        """Function called when a vehicle is idle at a destination has so has
        the State.AT_DEST."""
        vehicle.wait_time -= 1

        if vehicle.wait_time == 0:
            # The waiting is over, choose a new destination
            vehicle.state = States.TOWARDS_DEST
            vehicle.destination = random.choice(self.city_positions)
            vehicle.path = graphs.a_star(vehicle.pos, vehicle.destination)

    def towards_station(self, vehicle):
        """Function called when a vehicle has State.TOWARDS_ST."""
        vehicle.seeking += 1

        if self.compute_next_position(vehicle, vehicle.station.pos):
            # Store the seeking time
            vehicle.seeking_history.append(vehicle.seeking)
            # Start the counter for queueing
            vehicle.queueing = 0
            # Increase the occupation counter
            vehicle.station.occupation += 1
            if not self.check_for_a_charger(vehicle):
                vehicle.state = States.QUEUEING
        elif vehicle.battery == 0:
            self.no_battery(vehicle)

    def check_for_a_charger(self, vehicle):
        """Checks if the vehicle's station has availables chargers, if so
        computes the goal charge and the waiting time that the vehicle must
        stay on the station."""
        charger_available = False
        if vehicle.station.charger_available():
            charger_available = True
            vehicle.queueing_history.append(vehicle.queueing)
            # Set the next state to charging
            vehicle.state = States.CHARGING
            # Set the goal charge
            vehicle.desired_charge = self.compute_battery()
            vehicle.charging_history.append(vehicle.desired_charge)
            # Compute the charge time
            vehicle.wait_time = int(self.CHARGING_RATE * \
                (vehicle.desired_charge-vehicle.battery))

        return charger_available

    def queueing(self, vehicle):
        """Function called when a vehicle has State.Queueing."""
        vehicle.queueing += 1
        self.check_for_a_charger(vehicle)

    def charging(self, vehicle):
        """Function called when a vehicle has State.CHARGING."""
        vehicle.wait_time -= 1
        if vehicle.wait_time == 0:
            # The vehicle has waited long enough
            vehicle.station.vehicle_leaving()
            vehicle.station = None
            vehicle.battery = vehicle.desired_charge
            vehicle.state = States.TOWARDS_DEST
            vehicle.path = graphs.a_star(vehicle.pos, vehicle.destination)

    def set_idle_distribution(self, upper, lower, std):
        """Sets the parameters of the normal distribution of the time the
        vehicles spend at idle."""
        self.IDLE_UPPER = upper
        self.IDLE_LOWER = lower
        self.IDLE_STD = std
        self.IDLE_MEAN = (upper + lower) // 2

    def compute_idle(self):
        """Returns the time a vehicle must spent idle when it reaches a
        destination.

        This follows a normal distribution
        """

        # Compute a normal random number
        r = int(np.random.normal(self.IDLE_MEAN, self.IDLE_STD))

        # Truncate the maximum and minimum values of the distribution.
        while r < self.IDLE_LOWER or r > self.IDLE_UPPER:
            r = int(np.random.normal(self.IDLE_MEAN, self.IDLE_STD))

        return r

    def set_battery_distribution(self, upper, lower, std):
        """Sets the parameters of the normal distribution of the charge the
        vehicle's have/recharge.

        The battery is expressed as simulation time.
        """

        self.BATTERY_UPPER = upper
        self.BATTERY_LOWER = lower
        self.BATTERY_STD = std
        self.BATTERY_MEAN = (lower + upper) // 2

    def compute_battery(self):
        """Returns the amount of charge that an EV has in its battery.

        This follows a normal distribution.
        """
        r=int(np.random.normal(self.BATTERY_MEAN, self.BATTERY_STD))

        # Truncate the maximum and minimum values of the distribution.
        while r < self.BATTERY_LOWER or r > self.BATTERY_UPPER:
            r=int(np.random.normal(self.BATTERY_MEAN, self.BATTERY_STD))

        return r


    def compute_next_position(self, vehicle,  target, electric = True):
        """Given a."""

        # Recompute the path if we have moved to a random position in the previous step
        if vehicle.recompute_path:
            vehicle.path=graphs.recompute_path(vehicle.path, vehicle.pos, target)
            vehicle.recompute_path=False

        # Get the next step in the path to our goal
        choice=vehicle.path.pop(-1)

        vehicle_moved=False

        if self.city_state[choice]:
            # If the position of the next step in the path is available, move to it
            self.update_city_and_vehicle(vehicle, choice)
            vehicle_moved=True
        else:
            # With a 20% chance we move to a random position if any is available
            if random.random() >= 0.65:
                vehicle_moved=self.move_to_random(vehicle)


        if not vehicle_moved:
            # The vehicle's position is the same as before entering this function.
                vehicle.path.append(choice)  # restore the path
        else:
            # The vehicle did move. If the path is changed then it must be recomputed in the next step.
            if electric:
                vehicle.battery -= 1


        return vehicle.pos == target

    def move_to_random(self, vehicle):
        """Move the vehicle to an available position in the neighbourhood. Returns True if there is
        at least one position available, False otherwise."""
        candidates = [
            pos for (pos, tp) in self.city_map[vehicle.pos] if self.city_state[pos]]

        if len(candidates):
            self.update_city_and_vehicle(vehicle, random.choice(candidates))
            vehicle.recompute_path = True
            return True
        else:
            return False

    def update_city_and_vehicle(self, vehicle, choice):
        """Function that updates the city state and the vehicle position """
        self.city_state[vehicle.pos] = 1  # Set the current position as free
        self.city_state[choice] = 0  # Set the chosen position as occuppied
        # vehicle.ppos = vehicle.pos  # Record the previous position
        vehicle.pos = choice  # Update the vehicle position
