

class Simulator:

    def __init__(self, city_map, avenues):
        """
        :param city_map: is the graph of the city, given a position returns the list of 
            neighboring cells.
        :param avenues: is a set of cell that are avenues

         """
        super().__init__()

        self.city_map = city_map
        self.city_state = {(pos: False) for pos in self.city_map}
        self.avenues = avenues
        self.city_state = None
        self.vehicles = None
        self.stations = None

    def place_vehicles(self, EV_DEN, TF_DEN):
        """Creates the vehicles and places them around the city."""
        pass

    def place_stations(num_stations, LAYOUT):
        """Sets the stations around the city given the LAYOUT."""
        pass

    def next_step(self):
        """For each vehicle, computes the next step in their algorithm."""

    def towards_destination(self):
        """Function called when a vehicle has State.TOWARDS_DEST """
        pass

    def at_destination(self):
        """Function called when a vehicle is idle at a destination
        has so has the State.AT_DEST"""
        pass

    def towards_station(self):
        """Function called when a vehicle has State.TOWARDS_ST """
        pass

    def queueing(self):
        """Function called when a vehicle has State.Queueing """
        pass

    def charging(self):
        """Function called when a vehicle has State.CHARGING """

    def compute_idle_time(self):
        """Returns the time a vehicle must spent idle when it reaches a
        destination.

        This follows a normal distribution
        """
        pass

    def compute_battery(self):
        """Returns the amount of charge that an EV has in its battery.

        This follows a normal distribution
        """
        pass
