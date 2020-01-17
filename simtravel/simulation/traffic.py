import parameters as params
from parameters import *
import random
from simulation_objects import *
import traffic_simulation.graphs as graphs


class TrafficSimulator():

    def __init__(self):

        #Based on the CITY_TYPE parameter, create the city
        if CITY_TYPE == "square":
            self.city_builder = SquareCity(sqrt_roundabouts=SQRT_ROUNDABOUTS, block_scale=BLOCK_SCALE)
        
        #Set the total number of distributed stations.
        self.N_PLUGS, self.TOTAL_D_CS = set_max_chargers_stations(MIN_CHARGERS_STATION, MIN_D_STATIONS)

        #Set the constants to use in the simulation
        self.SIZE = self.city_builder.SIZE
        self.HSIZE = self.SIZE/2.0
        self.STREET_P = self.city_builder.STREET_P

        #Copy the global values inside parameters:
        for key in params.__dict__.keys():
            if key[0] != "_":
                #If the key is not from a Python class object, it is a global attribute.
                self.__dict__[key] = params.__dict__[key] #Add the attribute to the class.
                
        #Create the city map so that we can place vehicles and stations easily
        self.city_map = self.city_builder.city_map
        self.city_pos = list(self.city_map.keys())
        random.shuffle(self.city_pos)  # Shuffle the positions
        self.avenues_set = self.city_builder.avenues_set
        self.streets_set = self.city_builder.streets_set
        self.intensity_points = self.city_builder.select_intensity_points(MAX_INTENSITY_POINTS)

        #Now we are going to change the values of the type of road in other to use it as a score
        for pos in self.city_map:
            for i in range(len(self.city_map[pos])):
                old = self.city_map[pos][i]
                if old[1] == 1:
                    t = 1
                elif old[1] == 2:
                    t = 4
                else:
                    t = 2

                self.city_map[pos][i] = (old[0], t)
                
        # Configure the global parameters of the a_star
        graphs.configure_a_star(self.city_map, self.SIZE)

        #Attributes that are initilize when 'initialize()' is called
        # Dictionary where keys are positions of the city and values are either True (free) or False (occupied)
        self.city_state = None
        self.total_ev = None  # Total number of ev veh
        self.total_gas = None  # Total number of gas vehicles
        self.vehicles = None  # List with all the vehicles
        self.ev_vehicles = None  # List that contains the ev vehicles only.
        

        #Attributes to restart the simulation for a repetition
        self.city_initial_state = None
        self.vehicles_initial_data = None

        #Attributes that are initialize when 'place_stations()' is called
        self.stations = None  # List of stations of the city
        # Dictinary binding each position of the city with its list of stations
        self.stations_map = None
        self.LAYOUT = None

        #Dictionary containing the functions that must be called when computing next step
        self.states = {0: self.towards_destination, 1: self.in_destination,
                       2: self.towards_station, 3: self.in_station,
                       4: self.recharging, 5: self.no_battery}
        self.path_times = 0 #Count the number of times a_star is called 


    def update_intensity(self):
        for ip in self.intensity_points:
            if self.city_state[ip.int_point]:
                ip.vehicle_count_int += 1

            if self.city_state[ip.ext_point]:
                ip.vehicle_count_ext += 1
                     
    def position_in_district(self, pos, C1, C2, R1, R2):
        """"Given a positon (x,y) return True if the position is inside the area defined by 
        the district between the column C1, C2 and rows R1, R2 """
        (x, y) = pos
        return x >= C1 and x < C2 and y >= R1 and y < R2

    
    def place_stations(self, layout):
        def nearest_cell_type(reference, type_set):
            nearest = reference
            if reference not in type_set:
                candidates = [(i, j) for (i, j) in type_set
                              if i == reference[0] or j == reference[1]]
                if not candidates:
                    reference = (reference[0]+2, reference[1]+2)
                    candidates = [(i, j) for (i, j) in type_set
                                  if i == reference[0] or j == reference[1]]

                nearest = min(candidates, key=lambda p: graphs.lattice_distance(
                    p, reference))

            return nearest
        self.LAYOUT = layout

        if layout == 'central':
            L_STEP = self.SIZE
            PLUGS = self.N_PLUGS
        elif layout == 'four':
            L_STEP = int(self.HSIZE)
            PLUGS = int(self.N_PLUGS/4)
        elif layout == 'distributed':
            L_STEP = int(self.SIZE/SQRT_ROUNDABOUTS)
            PLUGS = MIN_CHARGERS_STATION
        #Create the districs
        districts = [(i, i+L_STEP, j, j+L_STEP) for i in range(0, self.SIZE, L_STEP)
                     for j in range(0, self.SIZE, L_STEP)]

        #Create the list of stations that each district has
        stations_per_district = {}
        stations = []
        if layout == 'central' or layout == 'four':
            for d in districts:
                (C1, C2, R1, R2) = d
                mid_point = (int((C1+C2)/2), int((R1 + R2)/2))
                stations_per_district[d] = [Station(nearest_cell_type(
                    mid_point, self.avenues_set), PLUGS)]
                stations.extend(stations_per_district[d])
        else:
            #First place all the stations in the city and add it into the stations list
            sq_maximum_cs = self.TOTAL_D_CS**0.5
            distance_appart = float(self.SIZE/sq_maximum_cs*1.0)
            for i in range(int(sq_maximum_cs)):
                for j in range(int(sq_maximum_cs)):
                    cell = (int(i*distance_appart), int(j*distance_appart))
                    stations.append(Station(nearest_cell_type(
                        cell, self.streets_set), PLUGS))

            #Each station is in a position of the city that we have to map to the districts
            # Initialize the districts as empty lists
            stations_per_district = {d: [] for d in districts}
            for st in stations:
                for district in districts:
                    if self.position_in_district(st.pos, district[0], district[1], district[2], district[3]):
                        stations_per_district[district].append(st)
                        break
        #Nowe we have produced a dictionary that maps districts with a list of stations, now
        #for each position in the city, point to the list of stations of its district
        stations_map = {}

        for pos in self.city_pos:
            for district, st in stations_per_district.items():
                if self.position_in_district(pos, district[0], district[1], district[2], district[3]):
                    stations_map[pos] = st
                    break

        self.stations_map = stations_map
        for d, st in self.stations_map.items():
            if len(st) == 0:
                print("El distrito: ", d, " no tiene estacion")
        self.stations = stations
        return stations


    def compute_next(self, vehicle, target, electric=False):
        """Computes the next step in the path of the vehicle towards its targer. If the vehicle's path is broken (the vehicle 
        did not follow the path at the previous step) then it must be fixed first, the algorithm then follows normally. """

        #Recompute the path if we have moved to a random position in the previous step
        if vehicle.recompute_path:
            vehicle.path = graphs.recompute_path(vehicle.path, vehicle.pos, target)
            vehicle.recompute_path = False
        
        #Get the next step in the path to our goal
        choice = vehicle.path.pop(-1)

        vehicle_moved = False

        if self.city_state[choice]:
            #If the position of the next step in the path is available, move to it
            self.update_city_and_vehicle(vehicle, choice)
            vehicle_moved = True
        else:
            #With a 20% chance we move to a random position if any is available
            if random.random() >= 0.65:
                vehicle_moved = self.move_to_random(vehicle)


        if not vehicle_moved:
            #The vehicle's position is the same as before entering this function.
                vehicle.path.append(choice) #restore the path
        else:
            #The vehicle did move. If the path is changed then it must be recomputed in the next step.
            if electric:
                vehicle.battery -= 1


        return vehicle.pos == target

    def move_to_random(self, vehicle):
        """Move the vehicle to an available position in the neighbourhood. Returns True if there is
        at least one position available, False otherwise."""
        candidates = [
            pos for (pos, tp) in self.city_map[vehicle.pos] if self.city_state[pos]]
        
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

    ####States that control the behaviour of the vehicles #####

    def towards_destination(self, v):
        """Computes the next position and if the vehicle is the destination position
        then changes to state 1, in destination """
        electric = False
        if v in self.ev_vehicles:
            electric = True

        if self.compute_next(v, v.destination, electric=electric):
            #If we have reached the destination, then:
            # Free the position making the vehicle invisible
            self.city_state[v.pos] = 1
            v.state = 1  # Set state to 'In a destination'
            # Set the wait time at the destination
            v.wait_time = v.wait_normal_d()
            
        elif electric and v.battery <= BATTERY_THRS:
            #If we haven't reached the destination and we dont have enough battery
            v.station = self.choose_station(v.pos)  # Choose our future station
            v.towards_station()  # Set the state variables
            v.path = graphs.a_star(v.pos, v.station.pos) #Compute the path to the new destination
            self.path_times += 1
    def towards_station(self, v):
        """The vehicle is driving towards a station, if if reaches it changes state
        to in station """
        v.seeking += 1  # Increase the seeking counter
        if self.compute_next(v, v.station.pos):
            #If the vehicle reaches the destination
            self.city_state[v.pos] = 1 # Free the position making the vehicle invisible
            v.arriving_station() # Update the corresponding vehicle variables
        elif v.battery == 0:
            v.state = 5

    def in_destination(self, v):
        """We have arrived at the destination, we just need to decrease the wait time
        until we are ready to a new destination"""

        v.wait_time = v.wait_time - 1

        if v.wait_time == 0:
            #If the vehicle has waited long enough it sets route to a new dest.
            v.destination = random.choice(self.city_pos)
            v.towards_destination()  # Set the state variables accordingly
            v.path = graphs.a_star(v.pos, v.destination) #Compute the path to the new destination
            self.path_times += 1
            

    def in_station(self, v):
        """The vehicle has reached the station and is waiting for a charger """
        v.queueing += 1
        if v.station.check_for_charger():
            #We have an available charger and are ready to charge
            # Change the vehicle's internal variables
            v.available_charger()
            

    def recharging(self, v):
        v.wait_time = v.wait_time - 1

        #If the vehicle has waited long enough it sets route to a new dest.
        if v.wait_time == 0:
            v.path = graphs.a_star(v.pos, v.destination) #Resume the course to the destination.
            self.path_times += 1
            v.battery = v.desired_charge  # Recharge the battery
            v.towards_destination()  # Change state variables
            v.station.exiting_station()  # Free the station charger

    def no_battery(self, v):
        # Free the position making the vehicle invisible
        self.city_state[v.pos] = 1

    def choose_station(self, pos):
        return random.choice(self.stations_map[pos])

    def initialize(self, EV_DENSITY, TF_DENSITY):
        #Store this attributes in the object to analyse the data later when the simuations are over
        self.EV_DENSITY = EV_DENSITY
        self.TF_DENSITY = TF_DENSITY

        #Start initilizing attributes related to the traffic simulator
        # First of all set each position as available
        self.city_state = {pos: 1 for pos in self.city_map}
        total_vehicles = self.SIZE*self.SIZE*self.STREET_P * \
            TF_DENSITY  # Compute the total number of vehicles

        # Set attributes for the class
        self.total_ev = int(total_vehicles*EV_DENSITY)
        self.total_gas = int(total_vehicles - self.total_ev)

        #Create the vehicles, place them in the city and set the destination
        vehicles = [] #list of vehicles
        positions_copy = copy.copy(self.city_pos) #Stack of positions
        ev_vehicles = set()
        for _ in range(self.total_ev):
            #Get the last position of the list of shuffled positions
            pos = positions_copy.pop()
            #Create the electric vehicle waiting at a position, 
            # the self.city_state[pos] value is not updated and so the position is free.
            vehicle = ElectricVehicle(pos)
            
            vehicles.append(vehicle)
            ev_vehicles.add(vehicle)

        for _ in range(self.total_gas):
            #Get the last position of the list of shuffled positions
            pos = positions_copy.pop()
            #Create the vehicle
            vehicle = Vehicle(pos)
            vehicles.append(vehicle)

        #Set the vehicles attribute
        self.vehicles = vehicles
        self.ev_vehicles = ev_vehicles
        #Set the attributes for another repetition
        self.vehicles_initial_data = self.create_map_state_pos()
        self.city_initial_state = copy.copy(self.city_state)

        return self.vehicles

    def restart(self):
        #Restore the city's state
        self.city_state = copy.copy(self.city_initial_state)

        #Restore the vehicles' state, position, charge and rest of attributes
        for v in self.vehicles:
            v.restart(self.vehicles_initial_data[v.id])

        #Restore the stations' attributes
        for s in self.stations:
            s.restart()

        for ip in self.intensity_points:
            ip.restart()
        #Restore the global values of distribution of charge and time
        CHARGE_SERIES = []
        WAIT_SERIES = []
        
    def create_map_state_pos(self):
        previous_data = {}
        for v in self.vehicles:
            previous_data[v.id] = (v.state, v.pos)

        return previous_data
