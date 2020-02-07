# -*- coding: utf-8 -*-
import copy
import numpy as np
import random
from .states import States


class Vehicle(object):
    def __init__(self, initial_pos, initial_wait_time):
        """pos is the vehicle's original position and wait_time is the amount of
        time a vehicle must spent before taking the first destination """
        self.pos = None  # Current position of the vehicle
        self.id = hash(str(initial_pos))
        self.destination = None  # Position where the vehicle is heading
        self.path = []  # List of positions to take
        # If True computes a path from the current position to a position in the previous path
        self.recompute_path = False
        # State of the vehicle. Initially they are waiting at a destination.
        self.state = None
        # Time left waiting at the destination or reacharging if applied to an EV.
        self.wait_time = None
        self.idle_history = None
        # Attributes to restart the vehicle
        self.initial_wait_time = initial_wait_time
        self.initial_pos = initial_pos
        
        self.restart()

    def restart(self):
        """Sets the vehicle to it's original place with all the attributes as
        the start of the simulation."""
        self.pos = self.initial_pos
        self.destination = self.initial_pos
        self.wait_time = self.initial_wait_time
        self.state = States.AT_DEST
        self.idle_history = []


class ElectricVehicle(Vehicle):
    def __init__(self, initial_pos, initial_wait_time, initial_battery):
        

        self.battery = None
        self.initial_battery = initial_battery

        self.desired_charge = None  # Desired charge that the vehicle will top up

        # Metrics we want to store
        self.seeking_history = []
        self.queueing_history = []
        self.charging_history = []

        # Station that the vehicle is headed to.
        self.station = None


        super(ElectricVehicle, self).__init__(initial_pos, initial_wait_time)
        self.restart()
    def restart(self):
        self.battery = self.initial_battery
        self.seeking_history = []
        self.queueing_history = []
        self.charging_history = []
        self.station = None
        super(ElectricVehicle, self).restart()
