from simtravel.models.vehicle import Vehicle, ElectricVehicle
from simtravel.models.station import Station
from simtravel.models.states import States


class Simulator:

    def __init__(self, city_map, avenues, STR_RATE, SIZE):
        """
        :param city_map: is the graph of the city, given a position returns the list of
            neighboring cells.
        :param avenues: is a set of cell that are avenues

         """
        super().__init__()
        # Set the constants
        self.STR_RATE = STR_RATE
        self.SIZE = SIZE

        # Set attributes
        self.city_map = city_map
        self.city_state = {(pos: 1) for pos in self.city_map}
        self.city_positions = list(city_map.keys())
        self.avenues = avenues
        self.vehicles = None  # List of vehicles
        self.ev_vehicles = None  # Set of ev vehicles
        self.stations = None  # List of stations

        # Dictionary where the key is a state and the value the function
        # associated with that state
        self.next_function = {States.AT_DEST: self.at_destination,
                              States.TOWARDS_DEST: self.towards_destination,
                              States.TOWARDS_ST: self.towards_station,
                              States.QUEUEING: self.queueing, States.CHARGING, self.charging}

    def place_vehicles(self, EV_DEN, TF_DEN):
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
        ev_vehicles = set()
        vehicles = []

        for _ in range(self.TOTAL_EV):
            v = ElectricVehicle(city_positions_copy.pop(),
                                self.compute_idle(), self.compute_battery())
            vehicles.append(v)
            ev_vehicles.add(v)
        for _ in range(self.TOTAL_VEHICLES-TOTAL_EV):
            v = Vehicle(city_positions_copy.pop(), self.compute_idle())
            vehicles.append(v)

        self.vehicles = vehicles
        self.ev_vehicles = ev_vehicles

        return self.vehicles

    def place_stations(num_stations, LAYOUT):
        """Sets the stations around the city given the LAYOUT."""
        pass

    def next_step(self):
        """For each vehicle, computes the next step in their algorithm."""
        for vehicle in vehicles:
            self.next_function[vehicle.state]

    def towards_destination(self, vehicle):
        """Function called when a vehicle has State.TOWARDS_DEST."""
        electric = False
        if v in self.ev_vehicles:
            electric = True

        if self.compute_next_position(vehicle, electric):
            # If we have reached the destination:
            # set the position as a free position
            self.city_state[vehicle.pos] = 1
            # set the vehicles' state to at destination
            vehicle.state = States.AT_DEST
            # set the amount of time the vehicle must
            # stay idle at destination
            vehicle.wait_time = self.compute_idle()
        elif electric:
            if vehicle.battery <= self.BATTERY_LOWER:
                # The vehicle is running out of battery and needs to recharge
                vehicle.state = States.TOWARDS_ST  # Set the state to "towards station"
                vehicle.station = self.choose_station(
                    vehicle.pos)  # Choose the station
                # vehicle.path = FALTA POR ESCRIBIR
                vehicle.seeking = 0  # Start the seeking counter
            elif vehicle.battery == 0:
                # The vehicle has run out of battery
                # Set the vehicle's position as free.
                self.no_battery_vehicle(vehicle)

    def no_battery_vehicle(self, vehicle):
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
            # vehicle.path = FALTA POR ESCRIBIR

            # vehicle.path = FALTA POR ESCRIBIR

    def towards_station(self, vehicle):
        """Function called when a vehicle has State.TOWARDS_ST."""
        vehicle.seeking += 1

        if self.compute_next_position(vehicle):
            # Store the seeking time
            vehicle.seeking_history.append(vehicle.seeking)
            # Start the counter for queueing
            vehicle.queueing = 0
            if not self.check_for_a_charger(vehicle):
                vehicle.state = States.QUEUEING
        elif vehicle.battery == 0:
            self.no_battery_vehicle(vehicle)

            self.no_battery_vehicle(vehicle)

    def check_for_a_charger(vehicle):
        """Checks if the vehicle's station has availables chargers, if so
        computes the goal charge and the waiting time that the vehicle must
        stay on the station."""
        charger_available = False
        if vehicle.station.charger_available():
            charger_available = True.append(vehicle.queueing)
            # Set the next state to charging
            vehicle.state = States.CHARGING
            # Set the goal charge
            vehicle.desired_charge = self.compute_battery()
            # Compute the charge time
            vehicle.wait_time = self.CHARGING_RATE * \
                (vehicle.desired_charge-vehicle.battery)
        return charger_available

        return charger_available

    def queueing(self, vehicle):
        """Function called when a vehicle has State.Queueing."""
        vehicle.queueing += 1
        self.check_for_a_charger(vehicle)

    def charging(self, vehicle):
        """Function called when a vehicle has State.CHARGING."""
        vehicle.wait_time -= 1
        if vehicle.wait_time == 0:
            # The vehicle has waited long enough for
            vehicle.station.vehicle_leaving()
            vehicle.station = None
            vehicle.state = States.TOWARDS_DEST
            # vehicle.path = FALTA POR ESCRIBIR

    def set_idle_distribution(self, upper, lower, std):
        """Sets the parameters of the normal distribution of the time the
        vehicles spend at idle."""
        self.IDLE_UPPER = upper
        self.IDLE_LOWER = lower
        self.IDLE_STD = std

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
        self.BATTERY_LOWER = lower + upper) // 2

    def compute_battery(self):
        """Returns the amount of charge that an EV has in its battery.

        This follows a normal distribution.
        """
        r=int(np.random.normal(self.BATTERY_MEAN, self.BATTERY_STD))

        # Truncate the maximum and minimum values of the distribution.
        while r < BATTERY_THRS or r > MAX_BATTERY:
            r=int(np.random.normal(self.BATTERY_MEAN, self.BATTERY_STD))

        CHARGE_SERIES.append(r)

        return r


    def compute_next_position(destination_pos, electric = True):
        """Given a."""
        pass
