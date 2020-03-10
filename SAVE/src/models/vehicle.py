# -*- coding: utf-8 -*-
from .states import States


class Vehicle(object):


    def __init__(self, initial_cell, initial_wait_time):
        """pos is the vehicle's original position and wait_time is the amount of
        time a vehicle must spent before taking the first destination """
        self.cell = None  # Current cell of the vehicle
        self.id = hash(str(initial_cell))
        self.destination = None  # Position where the vehicle is heading
        self.path = []  # List of positions to take
        # If True computes a path from the current position to a position in the previous path
        self.recompute_path = False
        # State of the vehicle. Initially they are waiting at a destination.
        self.state = None
        # Time left waiting at the destination or reacharging if applied to an EV.
        self.wait_time = None
        
        # Attributes to restart the vehicle
        self.initial_wait_time = initial_wait_time
        self.initial_cell = initial_cell
        
        self.restart()

    def restart(self):
        """Sets the vehicle to it's original place with all the attributes as
        the start of the simulation."""
        self.cell = self.initial_cell
        self.destination = self.initial_cell
        self.wait_time = self.initial_wait_time
        self.state = States.AT_DEST
        


class ElectricVehicle(Vehicle):
    def __init__(self, initial_cell, initial_wait_time, initial_battery):
        
        # Total battery in time steps that the vehicle has
        self.battery = None
        self.initial_battery = initial_battery

        # Last time spent seeking or queueing
        self.seeking = None
        self.queueing = None

        # Station that the vehicle is headed to.
        self.station = None

        super(ElectricVehicle, self).__init__(initial_cell, initial_wait_time)
        self.restart()

    def restart(self):
        self.battery = self.initial_battery

        self.seeking = None
        self.queueing = None

        self.station = None
        super(ElectricVehicle, self).restart()
