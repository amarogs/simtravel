# -*- coding: utf-8 -*-
from collections import deque

class Station(object):
    def __init__(self, cell, N_CHARGERS):
        self.id = hash(str(cell))
        self.cell = cell # Cell where the station is at.
        self.N_CHARGERS = N_CHARGERS # Total number of plugs
        self.available = None # Number of available chargers 
        self.queue = None # Current queue of vehicles.
        
        self.restart()

    def occupation(self):
        return len(self.queue) + (self.N_CHARGERS - self.available)

    def charger_available(self):
        """Returns True if the station has an available charger and reserves it. """
        r = False
        if self.available > 0:
            self.available -= 1
            r = True
        return r

    def vehicle_leaving(self):
        """Sets free the charger that was previously occuppied. """
        self.available += 1
        

    def restart(self):
        self.available = self.N_CHARGERS
        self.queue = deque()
