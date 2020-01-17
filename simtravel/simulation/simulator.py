from simtravel.models.vehicle import Vehicle, ElectricVehicle
from simtravel.models.station import Station
from simtravel.models.states import States


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

        self.next_function = {States.AT_DEST: self.at_destination,
                              States.TOWARDS_DEST: self.towards_destination,
                              States.TOWARDS_ST: self.towards_station,
                              States.QUEUEING: self.queueing, States.CHARGING, self.charging}

        

    def place_vehicles(self, EV_DEN, TF_DEN):
        """Creates the vehicles and places them around the city."""
        pass

    def place_stations(num_stations, LAYOUT):
        """Sets the stations around the city given the LAYOUT."""
        pass

    def next_step(self):
        """For each vehicle, computes the next step in their algorithm."""

    def towards_destination(self, vehicle):
        """Function called when a vehicle has State.TOWARDS_DEST """
        pass

    def at_destination(self, vehicle):
        """Function called when a vehicle is idle at a destination
        has so has the State.AT_DEST"""
        pass

    def towards_station(self, vehicle):
        """Function called when a vehicle has State.TOWARDS_ST """
        pass

    def queueing(self, vehicle):
        """Function called when a vehicle has State.Queueing """
        pass

    def charging(self, vehicle):
        """Function called when a vehicle has State.CHARGING """
        pass
    def set_idle_distribution(self, upper, lower, std):
        """Sets the parameters of the normal distribution
        of the time the vehicles spend at idle """
        self.IDLE_UPPER = upper
        self.IDLE_LOWER = lower
        self.IDLE_STD = std
        self.IDLE_MEAN = (lower + upper) // 2

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
        """Sets the parameters of the normal distribution
        of the charge the vehicle's have/recharge.
        The battery is expressed as simulation time.  """

        self.BATTERY_UPPER = upper
        self.BATTERY_LOWER = lower
        self.BATTERY_STD = std
        self.BATTERY_MEAN = (lower + upper) // 2

    def compute_battery(self):
        """Returns the amount of charge that an EV has in its battery.

        This follows a normal distribution
        """
        r = int(np.random.normal(self.BATTERY_MEAN, self.BATTERY_STD))

        # Truncate the maximum and minimum values of the distribution.
        while r < BATTERY_THRS or r > MAX_BATTERY:
            r = int(np.random.normal(self.BATTERY_MEAN, self.BATTERY_STD))

        CHARGE_SERIES.append(r)

        return r
