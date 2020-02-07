# -*- coding: utf-8 -*-
import copy
import numpy as np
import random

from src.models.states import States


from libc.math cimport abs as cabs


import heapq

#GLOBAL ATTRIBUTES OF THIS CLASS
#A dictionary to use as a c type

cdef dict CITY
cdef int SIZE


class Simulator:

    def __init__(self, simulation):
        """
        :param simulation: A simulation object
         """
        super().__init__()

        # Set attributes
        self.simulation = simulation
        self.city_state = {pos: 1 for pos in self.simulation.city_map}
        self.city_positions = list(simulation.city_map.keys())

        # Dictionary where the key is a state and the value the function
        # associated with that state
        self.next_function = {States.AT_DEST: self.at_destination,
                              States.TOWARDS_DEST: self.towards_destination,
                              States.TOWARDS_ST: self.towards_station,
                              States.QUEUEING: self.queueing, States.CHARGING: self.charging,
                              States.NO_BATTERY: self.no_battery}

    def restart(self):
        self.city_state = {pos: 1 for pos in self.simulation.city_map}
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
            self.city_state[vehicle.pos] = 1
            # set the vehicles' state to at destination
            vehicle.state = States.AT_DEST
            # set the amount of time the vehicle must
            # stay idle at destination
            vehicle.wait_time = self.compute_idle()
            vehicle.idle_history.append(vehicle.wait_time)
        elif electric:
            if vehicle.battery <= self.simulation.BATTERY_LOWER:
                # The vehicle is running out of battery and needs to recharge
                vehicle.state = States.TOWARDS_ST  # Set the state to "towards station"
                vehicle.station = self.choose_station(
                    vehicle.pos)  # Choose the station
                vehicle.path = a_star(vehicle.pos, vehicle.station.pos)
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
            vehicle.path = a_star(vehicle.pos, vehicle.destination)

    def towards_station(self, vehicle):
        """Function called when a vehicle has State.TOWARDS_ST."""
        vehicle.seeking += 1

        if self.compute_next_position(vehicle, vehicle.station.pos):
            # Free up the position
            self.city_state[vehicle.pos] = 1
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
            vehicle.wait_time = int(self.simulation.units.steps_to_recharge(
                vehicle.desired_charge-vehicle.battery))
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
            vehicle.path = a_star(vehicle.pos, vehicle.destination)

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
            vehicle.path = recompute_path(
                vehicle.path, vehicle.pos, target)
            vehicle.recompute_path = False

        # Get the next step in the path to our goal
        choice = vehicle.path.pop(-1)

        vehicle_moved = False

        if self.city_state[choice]:
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
            pos for (pos, tp) in self.simulation.city_map[vehicle.pos] if self.city_state[pos]]

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

    def next_step(self):
        """For each vehicle, computes the next step in their algorithm."""
        for vehicle in self.simulation.vehicles:
            self.next_function[vehicle.state](vehicle)







cpdef configure_a_star(dict city_map, int city_size):
    global CITY, SIZE
    CITY = city_map
    SIZE = city_size

cdef class PriorityMinHeap(object):
    """This class has been made using the example in https://docs.python.org/2/library/heapq.html """
    cdef list pq
    cdef dict entry_finder
    cdef tuple REMOVED
    cdef int counter

    def __init__(self):
        self.pq = [] #List arranged as a min heap
        self.entry_finder = {} #mapping of items to enties
        self.REMOVED = (99999,99999) #placeholder for a removed task
        self.counter = 0 #Number of elements that are not removed in the heap

    cdef insert(self, tuple item, int priority):
        if item in self.entry_finder:
            self.remove_item(item)
        
        cdef list entry = [priority, item]
       
        self.entry_finder[item] = entry
        heapq.heappush(self.pq, entry)
        self.counter += 1

    cdef remove_item(self, tuple item):
        "Mark an existing task as REMOVED"
        cdef list entry = self.entry_finder.pop(item)
        entry[-1] = self.REMOVED
        self.counter -= 1

    cdef pop(self):
        "Remove and return the lowest priority item that is not REMOVED"
        cdef tuple item

        while self.pq:
            _ , item = heapq.heappop(self.pq)
            if item is not self.REMOVED:
                self.counter -= 1
                del self.entry_finder[item]
                return item
    cdef is_empty(self):
        return self.counter == 0


cdef list reconstruct_path(dict came_from, tuple start, tuple current):
    cdef list total = [current]

    while True:
        current = came_from[current]
        if current==start:
            break
        else:
            total.append(current)
    return total



cpdef list a_star(tuple start, tuple goal):
    global CITY
    cdef set closed_set = set() #Set of positions already visited
    cdef PriorityMinHeap open_set = PriorityMinHeap() #Min heap of posible positions available for expansion

    #Dictionary containing (position:distance), which is the distance to
    #the goal from the position
    cdef dict g_score = {start:0}

    #Dictionary containing the relationship between posititions
    cdef dict came_from = {start:start}

    cdef int depth = 0 #Controls the number of entries in the path we want to compute
    cdef tuple neighbour, current
    
    open_set.insert(start, lattice_distance(start, goal))


    while not open_set.is_empty():
        #If there are available nodos, take the most promising one (lowest f_score)
        current = open_set.pop()
        depth += 1
        
        
        if current == goal: #or depth==MAX_DEPTH:
            #If the nodo is the goal, we have finished
            return reconstruct_path(came_from,start, current)
        else:
            #Otherwise we need to explore the current node
            closed_set.add(current)
        
        for (neighbour,road_type) in CITY[current]:

            if neighbour not in closed_set:
                #If the neighbour hasn't been visited
                #Compute the possible g_score
                new_g_score = g_score[current] + road_type

                if neighbour not in g_score or new_g_score < g_score[neighbour]:
                    #Add the neighbour with the g_score to the heap
                    open_set.insert(neighbour, new_g_score + lattice_distance(neighbour, goal))
                    g_score[neighbour] = new_g_score
                    came_from[neighbour] = current
              

cpdef list recompute_path(list current_path, tuple pos, tuple target):
    cdef list extension_path
    cdef tuple n_step

    if len(current_path) > 1:
        extension_path = a_star(pos, current_path[-2])
        del current_path[-1]
        for n_step in extension_path[1:]:
            current_path.append(n_step) 
    else:
        current_path = a_star(pos, target)
    return current_path

cpdef int lattice_distance(pos1, pos2):
    global SIZE
    cdef int dx, dy
    dx = cabs(pos1[0] - pos2[0])
    if dx > int(SIZE/2):
        dx = SIZE - dx
    dy = cabs(pos1[1] - pos2[1])
    if dy > int(SIZE/2):
        dy = SIZE - dy
    return (dx + dy)



