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
        self.city_map = simulation.city_map
        self.avenues = self.simulation.avenues
        self.roundabouts = self.simulation.roundabouts
        self.SEARCH_ALTERNATIVE_PRIO = 0.1
        # Control the updating of the cell's occupation state.
        self.new_occupations = []
        self.new_releases = []

        # Control the lists for updating
        self.general_update = []
        self.new_general_update = []

        # A list of cells to take random destinations.
        self.city_cells = list(simulation.city_map.values())
        
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
                              States.CHARGING: self.charging,
                              States.NO_BATTERY: self.no_battery}

    def restart(self):
        self.new_occupations = []
        self.new_releases = []

        self.general_update = self.simulation.vehicles
        self.new_general_update = []
        
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
            # If we have reached the destination, set the position as a free position
            self.new_releases.append(vehicle.cell)

            # set the vehicles' state to at destination
            vehicle.state = States.AT_DEST
            # set the amount of time the vehicle must stay idle at destination
            vehicle.wait_time = self.compute_idle()
            
        elif electric:
            if vehicle.battery <= self.simulation.BATTERY_LOWER:
                # The vehicle is running out of battery and needs to recharge
                vehicle.state = States.TOWARDS_ST  # Set the state to "towards station"
                vehicle.station = self.choose_station(vehicle.cell.pos)  # Choose the station
                vehicle.path = self.astar.new_path(vehicle.cell, vehicle.station.cell)
                vehicle.seeking = 0  # Start the seeking counter

            elif vehicle.battery == 0:
                # The vehicle has run out of battery
                vehicle.state = States.NO_BATTERY

        # Add the vehicle to the general update cycle.
        self.new_general_update.append(vehicle)
        return 

    def no_battery(self, vehicle):
        """Operations made when a vehicle runs out of battery.

        It makes the vehicle invisible to the traffic.
        """
        self.new_releases.append(vehicle.cell) 

        # The vehicle is no longer part of the general update list

    def at_destination(self, vehicle):
        """Function called when a vehicle is idle at a destination has so has
        the State.AT_DEST."""
        vehicle.wait_time -= 1

        if vehicle.wait_time == 0:
            # The waiting is over, choose a new destination
            vehicle.state = States.TOWARDS_DEST
            vehicle.destination = random.choice(self.city_cells)
            
            vehicle.path = self.astar.new_path(vehicle.cell, vehicle.destination)

        # Add the vehicle to the general update cycle.
        self.new_general_update.append(vehicle)
        return 

    def towards_station(self, vehicle):
        """Function called when a vehicle has State.TOWARDS_ST."""
        vehicle.seeking += 1

        if self.compute_next_position(vehicle, vehicle.station.cell):
            # Free up the position
            self.new_releases.append(vehicle.cell)

            # Store the seeking time
            self.seeking_history[vehicle.id].append(vehicle.seeking)
            vehicle.state = States.QUEUEING

            # Start the counter for queueing
            vehicle.queueing = 0
            vehicle.station.queue.append(vehicle)

        else:
            if vehicle.battery == 0:
                # The vehicle has run out of battery
                vehicle.state = States.NO_BATTERY

            # Add the vehicle to the general update list only if it hasn't reached
            # the station.
            self.new_general_update.append(vehicle)

    def update_at_station(self, station):
        """Update the vehicles that are inside the station queueing"""

        if len(station.queue):
            # Increase the queueing counter of each vehicle.
            for vehicle in station.queue:
                vehicle.queueing += 1

            # Assign a new charger to the first vehicle in the queue
            if station.charger_available():
                vehicle = station.queue.popleft() # Retrieve the first vehicle.
                self.queueing_history[vehicle.id].append(vehicle.queueing) 

                vehicle.state = States.CHARGING # Set the state to charging
                goal_charge = self.compute_battery() # Compute the goal charge and wait time.
                vehicle.wait_time = int(self.simulation.units.steps_to_recharge(goal_charge-vehicle.battery))
                vehicle.battery = goal_charge

                # Add the vehicle to the general update list.
                self.new_general_update.append(vehicle)


    def charging(self, vehicle):
        """Function called when a vehicle has State.CHARGING."""
        vehicle.wait_time -= 1
        if vehicle.wait_time == 0:
            # The vehicle has waited long enough
            vehicle.station.vehicle_leaving()
            vehicle.station = None
            vehicle.state = States.TOWARDS_DEST
            
            vehicle.path = self.astar.new_path(vehicle.cell, vehicle.destination)

        # Add the vehicle to the general update list
        self.new_general_update.append(vehicle)

    def compute_idle(self):
        """Returns the time a vehicle must spent idle when it reaches a
        destination.

        This follows a normal distribution
        """

        # Compute a normal random number
        r = int(np.random.normal(self.simulation.IDLE_MEAN, self.simulation.IDLE_STD))

        # Truncate the maximum and minimum values of the distribution.
        while r < self.simulation.IDLE_LOWER or r > self.simulation.IDLE_UPPER:
            r = int(np.random.normal(self.simulation.IDLE_MEAN, self.simulation.IDLE_STD))

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

        # A flag to know whether the vehicle moved to a new position.
        vehicle_moved = False

        def keep_in_lane_is_possible(next_prio_cell):
            """Given a priority cell next to the current cell, returns True
            if we can keep in lane and occupy the next cell. """

            return not next_prio_cell.occupied
        
        def lane_change_is_possible(choice):
            """ Given a cell, checks if it is possible to move to that cell provided
            that we dont have priority.  """
            is_possible = not choice.occupied

            for cell in choice.prio_predecessors:
                # For each cell leading to the choice, check if it's clear.
                if not is_possible or cell.occupied:
                    is_possible = False
                    break
                # For each previous cell leading to cell, check if that's also clear.
                #for p_cell in cell.prio_predecessors:
                #    if p_cell.occupied:
                #        is_possible = False
                #        break
                    
            return is_possible

        def follow_path(vehicle, next_cell):
            self.assign_new_cell(vehicle, next_cell)
            

        def divert_from_path(vehicle, next_cell):
            
            self.assign_new_cell(vehicle, next_cell)
            vehicle.recompute_path = True

        # Recompute the path if we have diverted from the path in the previous step.
        if vehicle.recompute_path:
            vehicle.path = self.astar.recompute_path(vehicle.path, vehicle.cell, target)
            vehicle.recompute_path = False
            

        # Get the next step in the path to our goal
        
        next_cell = vehicle.path.pop(-1)
        
        if next_cell in vehicle.cell.prio_successors:
            # The vehicle tries to keep in lane and move to the forward position.
            if keep_in_lane_is_possible(next_cell):
                follow_path(vehicle, next_cell)
                vehicle_moved = True
            elif random.random() < self.SEARCH_ALTERNATIVE_PRIO:
                # The vehicle tries to change lane with a certain probability
                for n_cell in vehicle.cell.successors:
                    
                    if n_cell in vehicle.cell.prio_successors:
                        # The vehicle tries to change the direction an enter another priority street.
                        if keep_in_lane_is_possible(n_cell):
                            divert_from_path(vehicle, n_cell)
                            vehicle_moved = True
                            break
                    else:
                        # The vehicle tries to change lane
                        if lane_change_is_possible(n_cell):
                            divert_from_path(vehicle, n_cell)
                            vehicle_moved = True
                            break
                
        else:
            # Case when the next position is not a priority, the vehicle must give way.
            if lane_change_is_possible(next_cell):
                follow_path(vehicle, next_cell)
                vehicle_moved = True
                
            elif vehicle.cell.prio_successors and keep_in_lane_is_possible(vehicle.cell.prio_successors[0]):
                # There is no safe way to change lane, so the vehicle must stay in his lane.
                divert_from_path(vehicle, vehicle.cell.prio_successors[0])
                vehicle_moved = True
   

        if not vehicle_moved:
            # The vehicle's position is the same as before entering this function.
            vehicle.path.append(next_cell)  # restore the path
        else:
            # The vehicle did move. If the path is changed then it must be recomputed in the next step.
            if electric:
                vehicle.battery -= 1

        return vehicle.cell == target

    def move_to_random(self, vehicle):
        """Move the vehicle to an available position in the neighbourhood. Returns True if there is
        at least one position available, False otherwise."""
        candidates = [pos for (pos, tp) in self.simulation.city_map[vehicle.pos] if self.current_city_state[pos]]
        # DEPRECATED
        if len(candidates):
            self.update_city_and_vehicle(vehicle, random.choice(candidates))
            vehicle.recompute_path = True
            return True
        else:
            return False

    def assign_new_cell(self, vehicle, choice):
        """Function that updates the city state and the vehicle position """
        self.new_releases.append(vehicle.cell) # Set the current position as free
        self.new_occupations.append(choice) # Set the chosen position as occupied
        vehicle.cell = choice  # Update the vehicle position

    def update_city_state(self):
        """Based on the cells marked by the vehicles, update the dictionary of the
        state of the city accordingly."""

        for cell in self.new_occupations:
            cell.occupied = True
        for cell in self.new_releases:
            cell.occupied = False
        
        # Prepare the simulation for the next step.
        self.general_update = self.new_general_update
        self.new_general_update = []
        
        self.new_releases, self.new_occupations = [], []

    def next_step(self):
        """For each vehicle, computes the next step in their algorithm."""
        
        # Advance only the vehicles in the avenues
        for vehicle in self.general_update:
            if vehicle.cell in self.avenues or vehicle.cell in self.roundabouts:
                self.next_function[vehicle.state](vehicle)
            else:
                self.new_general_update.append(vehicle)
        # Update the city state
        self.update_city_state()

        # Now advance all the vehicles
        for vehicle in self.general_update:
            self.next_function[vehicle.state](vehicle)
            
        for st in self.simulation.stations:
            self.update_at_station(st)

        # Set the current city state to the new one
        self.update_city_state()


 





