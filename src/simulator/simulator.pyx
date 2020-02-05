# -*- coding: utf-8 -*-
import copy
import numpy as np
import random

from src.models.states import States
from src.simulator.cythonGraphFunctions import AStar

class Simulator:

    def __init__(self, simulation):
        """
        :param simulation: A simulation object
         """
        super().__init__()

        # Set attributes
        self.simulation = simulation
        self.avenues = self.simulation.avenues
        # Controls the update.
        self.current_city_state = {pos: 1 for pos in self.simulation.city_map}
        self.new_occupations = []
        self.new_releases = []

        # A list of positions to take random destinations.
        self.city_positions = list(simulation.city_map.keys())
        # Object that models the A* path algorithm 
        self.astar = AStar(200)
        # Global data from the simulation
        self.seeking_history = None
        self.queueing_history = None
        # Dictionary where the key is a state and the value the function
        # associated with that state
        self.next_function = {States.AT_DEST: self.at_destination,
                              States.TOWARDS_DEST: self.towards_destination,
                              States.TOWARDS_ST: self.towards_station,
                              States.QUEUEING: self.queueing, States.CHARGING: self.charging,
                              States.NO_BATTERY: self.no_battery}

    def restart(self):
        self.current_city_state = {pos: 1 for pos in self.simulation.city_map}
        self.new_occupations = []
        self.new_releases = []
        
        self.seeking_history = {v.id:[] for v in self.simulation.ev_vehicles}
        self.queueing_history = {v.id: [] for v in self.simulation.ev_vehicles}

    def choose_station(self, pos):
        return random.choice(self.simulation.stations_map[pos])

    def towards_destination(self, vehicle):
        """Function called when a vehicle has State.TOWARDS_DEST."""
        electric = False
        if vehicle in self.simulation.ev_vehicles:
            electric = True

        if self.compute_next_position(vehicle, vehicle.destination, electric):
            # If we have reached the destination:
            # set the position as a free position
            self.new_releases.append(vehicle.pos)
            # set the vehicles' state to at destination
            vehicle.state = States.AT_DEST
            # set the amount of time the vehicle must
            # stay idle at destination
            vehicle.wait_time = self.compute_idle()
            
        elif electric:
            if vehicle.battery <= self.simulation.BATTERY_LOWER:
                # The vehicle is running out of battery and needs to recharge
                vehicle.state = States.TOWARDS_ST  # Set the state to "towards station"
                vehicle.station = self.choose_station(
                    vehicle.pos)  # Choose the station
                vehicle.path = self.astar.new_path(vehicle.pos, vehicle.station.pos)
                vehicle.seeking = 0  # Start the seeking counter
            elif vehicle.battery == 0:
                # The vehicle has run out of battery
                # Set the vehicle's position as free.
                self.no_battery(vehicle)

    def no_battery(self, vehicle):
        """Operations made when a vehicle runs out of battery.

        It makes the vehicle invisible to the traffic.
        """
        self.new_releases.append(vehicle.pos) 
        
        vehicle.state = States.NO_BATTERY

    def at_destination(self, vehicle):
        """Function called when a vehicle is idle at a destination has so has
        the State.AT_DEST."""
        vehicle.wait_time -= 1

        if vehicle.wait_time == 0:
            # The waiting is over, choose a new destination
            vehicle.state = States.TOWARDS_DEST
            vehicle.destination = random.choice(self.city_positions)
            vehicle.path = self.astar.new_path(vehicle.pos, vehicle.destination)

    def towards_station(self, vehicle):
        """Function called when a vehicle has State.TOWARDS_ST."""
        vehicle.seeking += 1

        if self.compute_next_position(vehicle, vehicle.station.pos):
            # Free up the position
            self.new_releases.append(vehicle.pos)
            # Store the seeking time
            self.seeking_history[vehicle.id].append(vehicle.seeking)
            
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
            self.queueing_history[vehicle.id].append(vehicle.queueing)
            
            # Set the next state to charging
            vehicle.state = States.CHARGING
            # Set the goal charge
            goal_charge = self.compute_battery()
            
            # Compute the charge time
            vehicle.wait_time = int(self.simulation.units.steps_to_recharge(
                goal_charge-vehicle.battery))
            # Update the battery of the vehicle
            vehicle.battery = goal_charge
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
            vehicle.state = States.TOWARDS_DEST
            vehicle.path = self.astar.new_path(vehicle.pos, vehicle.destination)

    def compute_idle(self):
        """Returns the time a vehicle must spent idle when it reaches a
        destination.

        This follows a normal distribution
        """

        # Compute a normal random number
        r = int(np.random.normal(
            self.simulation.IDLE_MEAN, self.simulation.IDLE_STD))

        # Truncate the maximum and minimum values of the distribution.
        while r < self.simulation.IDLE_LOWER or r > self.simulation.IDLE_UPPER:
            r = int(np.random.normal(
                self.simulation.IDLE_MEAN, self.simulation.IDLE_STD))

        return r

    def compute_battery(self):
        """Returns the amount of charge that an EV has in its battery.

        This follows a normal distribution.
        """
        r = int(np.random.normal(self.simulation.BATTERY_MEAN,
                                 self.simulation.BATTERY_STD))

        # Truncate the maximum and minimum values of the distribution.
        while r < self.simulation.BATTERY_LOWER or r > self.simulation.BATTERY_UPPER:
            r = int(np.random.normal(self.simulation.BATTERY_MEAN,
                                     self.simulation.BATTERY_STD))

        return r

    def compute_next_position(self, vehicle,  target, electric=True):
        """Given a."""

        # Recompute the path if we have moved to a random position in the previous step
        if vehicle.recompute_path:
            vehicle.path = self.astar.recompute_path(
                vehicle.path, vehicle.pos, target)
            vehicle.recompute_path = False
            

        # Get the next step in the path to our goal
        choice = vehicle.path.pop(-1)

        vehicle_moved = False

        if self.current_city_state[choice]:
            # If the position of the next step in the path is available, move to it
            self.update_city_and_vehicle(vehicle, choice)
            vehicle_moved = True
        else:
            # With a 20% chance we move to a random position if any is available
            if random.random() >= 0.65:
                vehicle_moved = self.move_to_random(vehicle)

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
            pos for (pos, tp) in self.simulation.city_map[vehicle.pos] if self.current_city_state[pos]]

        if len(candidates):
            self.update_city_and_vehicle(vehicle, random.choice(candidates))
            vehicle.recompute_path = True
            return True
        else:
            return False

    def update_city_and_vehicle(self, vehicle, choice):
        """Function that updates the city state and the vehicle position """
        self.new_releases.append(vehicle.pos) # Set the current position as free
        self.new_occupations.append(choice) # Set the chosen position as occuppied
        vehicle.pos = choice  # Update the vehicle position
    def update_city_state(self):
        """Based on the cells marked by the vehicles, update the dictionary of the
        state of the city accordingly."""

        for pos in self.new_occupations:
            self.current_city_state[pos] = 0
        for pos in self.new_releases:
            self.current_city_state[pos] = 1

        self.new_releases, self.new_occupations = [], []

    def next_step(self):
        """For each vehicle, computes the next step in their algorithm."""
        
        # Advance only the vehicles in the avenues
        for vehicle in self.simulation.vehicles:
            if vehicle.pos in self.avenues:
                self.next_function[vehicle.state](vehicle)
            
        # Update the city state
        self.update_city_state()

        # Now advance all the vehicles
        for vehicle in self.simulation.vehicles:
            self.next_function[vehicle.state](vehicle)

        # Set the current city state to the new one
        self.update_city_state()

        
 





