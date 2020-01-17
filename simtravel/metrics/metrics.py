from parameters import *
import copy
import numpy as np
import numexpr as ne

class SimulationMetrics(object):
    def __init__(self, total_states, stations_pos, intensity_points,previous_data, SIZE, EV_DENSITY, TF_DENSITY, LAYOUT):
        self.SIZE = SIZE
        self.HSIZE = int(self.SIZE/2)
        self.I_TIME_STEP = float(1/DELTA_TIME_STEP)
        self.LAYOUT = LAYOUT
        self.EV_DENSITY = EV_DENSITY
        self.TF_DENSITY = TF_DENSITY
        self.counter = 0 #Count the number of times we have entered the update metrics

        first = int(int(TOTAL_STEPS/3)/DELTA_TIME_STEP)*DELTA_TIME_STEP
        second = int(int(2*TOTAL_STEPS/3)/DELTA_TIME_STEP)*DELTA_TIME_STEP
        last = int(int(TOTAL_STEPS)/DELTA_TIME_STEP)*DELTA_TIME_STEP
        self.snapshot_times = set([first, second, last])

        # Dict: (vehicle: (state, position) )
        self.previous_data = previous_data
        #The attributes with a 'simulation' in the name refer to the attributes that store information
        #of a particular repetition of the simulation

        #Let's create the attributes to store the state
        self.total_states = total_states
        self.states_simulation = None  # A map where the key is a state
        #and the value is a list with the number of times it appears.

        # (pos : [# of vehicles in that station])
        self.occupation_simulation = {i: [0] for i in stations_pos}

        self.intensity_ext_simulation = []
        self.intensity_int_simulation = []

        self.heat_map = None  # (pos : # of vehicles that have passed)
        self.heat_map_simulation = []  # List where the different heat maps are stored

        # List where the different speeds are annotated.
        self.speed_simulation = []
        self.mobility_simulation = []
        
        self.seeking_simulation = None
        self.queueing_simulation = None

        #List where the final values of distribution and wait time are annotated
        self.wait_series = None
        self.charge_series = None

    def lattice_distance(self, pos1, pos2):
        dx = abs(pos1[0] - pos2[0])
        dy = abs(pos1[1] - pos2[1])
        if dx > self.HSIZE:
            dx = self.SIZE - dx
        if dy > self.HSIZE:
            dy = self.SIZE - dy
        return float(dx + dy)

    def init_states(self, ev_vehicles):
        """Function that counts the number of times each state appears at time_step=0
        and returns a list of lists where each state is represented by its index. """

        #Count the number of times each state appears.
        state_count = [0 for k in range(self.total_states)]

        for ev in ev_vehicles:
            state_count[ev.state] += 1

        #Then create the attribute that is going to store the count
        self.states_simulation = [[state_count[k]] for k in range(self.total_states)]
        return

    def update_states(self, ev_vehicles):
        """Count the number of vehicle that are in each state at time_step=n and appends it
        to the corresponding list in states_simulation. """

        #First count the number of vehicles that are in a certain state
        state_count = [0 for k in self.states_simulation]

        for ev in ev_vehicles:
            state_count[ev.state] += 1

        #Then add then to the evolution
        for (i, state) in enumerate(self.states_simulation):
            state.append(state_count[i])
            

    def update_occupation(self, stations):
        """For each station, count the number of vehicles that are inside the 
        station at each snapshot """
        for st in stations:
            self.occupation_simulation[st.pos].append(st.occupation)

    def charge_and_time_distribution(self):
        self.charge_series = CHARGE_SERIES
        self.wait_series = WAIT_SERIES

    def global_points(self, ev_vehicles):
        seeking, queueing = [], []

        for ev in ev_vehicles:
            if len(ev.seeking_history)>0:
                seeking.append(np.average(np.array(ev.seeking_history)))
            if len(ev.queueing_history)>0:
                queueing.append(np.average(np.array(ev.queueing_history)))
        if len(seeking):
            self.seeking_simulation = np.average(np.array(seeking))
        if len(queueing):
            self.queueing_simulation = np.average(np.array(queueing))

    def init_heat_map(self, city_pos):
        # For each position in the city, set the counter to 0
        heat_map = {i: 0 for i in city_pos}

        for _, (st, pos) in self.previous_data.items():
            if st == 0 or st == 2:
                #Increase the counter where there is a vehicle driving
                heat_map[pos] += 1
        self.heat_map = heat_map
        return

    def update_heat_map(self, new_data, step):
        """Record the current position of the vehicles that are currently moving"""
        for _, (st, pos) in new_data.items():
            if st == 0 or st == 2:
                self.heat_map[pos] += 1
        if step in self.snapshot_times:
            #Appends the current heat_map to the list of the evolution
            self.heat_map_simulation.append(copy.copy(self.heat_map))
    def create_matrices(self):
        """Create new np matrices with some attributes like states_simulation and intensity_simulation """
        #State matrix
        self.states_simulation = np.array(self.states_simulation)
        
        #For each placement of intensity create the matrices and multiply by the factor 
        #of time_step
        divisor = self.I_TIME_STEP
        interior = np.array(self.intensity_int_simulation)
        exterior = np.array(self.intensity_ext_simulation)
        
        self.intensity_int_simulation = ne.evaluate("divisor * interior")
        self.intensity_ext_simulation = ne.evaluate("divisor * exterior")
        
        #Mean speead as a numpy array
        self.speed_simulation = np.array(self.speed_simulation)


        #For each snapshot of the heat map create a matrix 
        heat_map_matrix = []
        for hmap in self.heat_map_simulation:
            
            A = np.zeros((self.SIZE, self.SIZE))
            for pos, value in hmap.items():
                A[pos] = value
            heat_map_matrix.append(A)
        self.heat_map_simulation = heat_map_matrix

        
    def update_all(self, ev_vehicles, new_data, stations,intensity_points ,step):
        #Update the state of the ev_vehicles
        self.update_states(ev_vehicles)

        #Loop the stations to update the occupation
        self.update_occupation(stations)

        #Now let's loop over all the vehicle to find the data we need

        #Count the number of vehicles driving in the current time step and the previous one
        new_speed = []
        new_mobility = []
        for v in new_data:
            # Retrieve the data from the vehicles
            (st_0, pos_0) = self.previous_data[v]
            (st_1, pos_1) = new_data[v]

            if st_1 == 0 or st_1 == 2:
                self.heat_map[pos_1] += 1 #There is a  vehicle at pos_1 that is driving
                #We already know that the vehicle is driving, let's find out if the vehicle was driving before too
                if (st_0 == 0 or st_0 == 2):
                    new_speed.append(self.lattice_distance(pos_0, pos_1))

            #Compute the mobility for this vehicle
            new_mobility.append(self.lattice_distance(pos_0, pos_1))
        divisor = self.I_TIME_STEP
        if len(new_speed) > 0:
            new_speed = np.array(new_speed) #Take the distance list and make a new array
            new_speed = np.average(ne.evaluate("divisor * new_speed"))
        else:
            new_speed = 0.0
        new_mobility = np.array(new_mobility) #Create a numpy array with the mobility
        new_mobility = np.average(ne.evaluate("divisor * new_mobility")) #Compute the mean mobility of this snapshot.

        #Update the speed evolution list
        self.speed_simulation.append(new_speed)
        self.mobility_simulation.append(new_mobility)

        #Appends the current heat_map to the list of the evolution if where are on a selected step
        if step in self.snapshot_times:
            self.heat_map_simulation.append(copy.copy(self.heat_map))


        #Update the intensity measure at the points selected
        interior, exterior = [],[]
        for ip in intensity_points:
            interior.append(ip.vehicle_count_int)
            exterior.append(ip.vehicle_count_ext)
            ip.restart()
        
        self.intensity_int_simulation.append(interior)
        self.intensity_ext_simulation.append(exterior)

        self.previous_data = new_data  # Set the previous data as the new data
        self.counter += 1 #Increase the counter
