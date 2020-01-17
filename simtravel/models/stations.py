class Station(object):
    def __init__(self, pos, N_CHARGERS, speed=1):
        self.pos = pos
        self.N_CHARGERS = N_CHARGERS
        self.available = self.N_CHARGERS
        self.occupation = 0

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
        self.occupation -= 1

    def restart(self):
        self.available = self.N_CHARGERS
        self.occupation = 0
