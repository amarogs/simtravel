# -*- coding: utf-8 -*-
from src.models.states import States
from src.simulator.cythonGraphFunctions import lattice_distance

import copy
import numpy as np
import h5py


class SimulationSnapshot(object):

    def __init__(self, vehicles):
        super().__init__()
        # For each vehicle, store its position
        self.v_pos = {v.id: copy.copy(v.pos) for v in vehicles}
        # For each vehicle, store its state
        self.v_state = {v.id: copy.copy(v.state) for v in vehicles}

    def mean_velocities(self, previous, delta_tsteps):
        """Given a previous snapshot, computes the mean speed of
        the vehicles moving (mean_speed) and the mean speed of all
        vehicles (mean_mobility). """

        previous_state = previous.v_state
        previous_pos = previous.v_pos

        moving_distance, total_distance = 0, 0
        moving_counter = 0

        for v, state in self.v_state.items():
            # Compute the distance from the two snapshots
            distance = lattice_distance(self.v_pos[v], previous_pos[v])
            
                
            total_distance += distance

            if state in States.moving_states() and previous_state[v] in States.moving_states():
                # If the vehicle is moving rigth now and was moving before, take it into account
                moving_distance += distance
                moving_counter += 1

        # Compute the aggregated speed and mobility
        moving_distance, total_distance = moving_distance / \
            delta_tsteps, total_distance/delta_tsteps
        
        if moving_counter == 0:
            return (0, total_distance/len(previous_pos))
        else:
            return (moving_distance/moving_counter, total_distance/len(previous_pos))


class SimulationMetric(object):
    def __init__(self, city_map, stations, num_heat_snapshots, total_tsteps, delta_tsteps, SIZE):
        super().__init__()
        self.SIZE = SIZE
        # For each state count the number of EV's in that state
        self.states_evolution = {s: [] for s in States}
        # Compute metrics about the speed and mobility
        self.mean_speed_evolution = []
        self.mean_mobility_evolution = []
        # Compute metrics about the occupation of stations
        self.occupation_history = {st.pos: [] for st in stations}
        # Compute metrics about the placement of vehicles
        self.heat_map = {pos: 0 for pos in city_map}
        self.heat_map_tsteps = [int(((i+1)*total_tsteps)/(num_heat_snapshots*delta_tsteps))*delta_tsteps
                                for i in range(num_heat_snapshots)]
        self.delta_tsteps = delta_tsteps
        self.heat_map_evolution = []

        # Compute the global metrics
        self.mean_seeking = None
        self.mean_queueing = None

        # Save the amount of charge and time spent idle
        self.idle_distribution = None
        self.charging_distribution = None

    def initialize(self, vehicles, ev_vehicles, stations):
        """Method that updates the internal variables with the data
        from the tstep=0 """
        self.update_states(ev_vehicles)
        self.update_heat_map(vehicles, 0)
        self.update_occupation(stations)

    def update_data(self, vehicles, ev_vehicles, stations, current, previous, tstep):
        """Method that updates the internal variables with the
        data from a tstep different from the first one. """
        self.update_states(ev_vehicles)
        self.update_heat_map(vehicles, tstep)
        self.update_occupation(stations)
        self.update_speed_mobility(current, previous)

    def update_states(self, ev_vehicles):
        """Given a set/list of ev_vehicles, computes how many vehicles
        are in each state, then appends that data to the evolution lists.
        This method updates the attribute states_evolution """

        # First count the number of vehicles that are in a certain state
        state_count = {s: 0 for s in States}

        for ev in ev_vehicles:
            state_count[ev.state] += 1
        # Append the count to the lists of evolution
        for s in States:
            self.states_evolution[s].append(state_count[s])

    def update_heat_map(self, vehicles, tstep):
        """Given the list of vehicles and the current time step, 
        if a vehicle is moving, then increase the counter of the cell
        that it's occupying. """

        # First update the global count of the placement of vehicles
        for v in vehicles:
            if v.state in States.moving_states():
                self.heat_map[v.pos] += 1

        # Then, check if we have to make a snapshot of the heat map
        if tstep in self.heat_map_tsteps:
            heat = np.zeros((self.SIZE, self.SIZE), dtype="int32")
            for pos, value in self.heat_map.items():
                heat[pos] = value
            self.heat_map_evolution.append(heat)

    def update_speed_mobility(self, current, previous):
        """Given the current snapshot and the last snapshot, 
        computes the mean_speed and mean_velcities and updates
        the evolution lists for those parameters. """

        speed, mobility = current.mean_velocities(previous, self.delta_tsteps)
        
        self.mean_speed_evolution.append(speed)
        self.mean_mobility_evolution.append(mobility)

    def update_occupation(self, stations):
        """Given the list of stations, count the number of 
        vehicles that they hold and save it to a list. """
        for st in stations:
            self.occupation_history[st.pos].append(st.occupation)

    def compute_seeking_queueing(self, ev_vehicles):
        """Aggregates the data from the vehicles. For each
        vehicle compute the mean number of steps used in seeking
        and the mean number of steps used in queueing, then compute
        a global average mean of the simulation. """
        self.mean_seeking = np.mean([np.sum(ev.seeking_history)
                                     for ev in ev_vehicles])
        self.mean_queueing = np.mean([np.sum(ev.queueing_history)
                                      for ev in ev_vehicles])

    def store_idle_charging(self, ev_vehicles):
        self.idle_distribution = [ev.idle_history for ev in ev_vehicles]
        self.charging_distribution = [
            ev.charging_history for ev in ev_vehicles]


    def write_results(self, file, base_directory, ev_vehicles):
        """Given a openned and writable HDF5 file, and the 
        base directory where we are going to write, takes the
        data from the simulation and stores it in the file. """

        # Write states evolution data
        directory = base_directory + "states/"
        size = len(self.states_evolution[States.AT_DEST])

        for s in States:
            dset = file.create_dataset(
                directory+str(s), (size,), dtype="uint32")
            dset.write_direct(np.array(self.states_evolution[s]))

        # Write mean speed and mobility
        directory = base_directory + "velocities/"
        size = len(self.mean_speed_evolution)

        dset = file.create_dataset(
            directory + "speed", (size,), dtype="float32")
        dset.write_direct(np.array(self.mean_speed_evolution))

        dset = file.create_dataset(
            directory + "mobility", (size,), dtype="float32")
        dset.write_direct(np.array(self.mean_mobility_evolution))

        # Write heat map data
        directory = base_directory + "heat_map/"
        size = self.heat_map_evolution[0].shape

        for (i, heat) in enumerate(self.heat_map_evolution):
            dset = file.create_dataset(directory+str(i), size, dtype="uint32")
            dset.write_direct(heat)

        # Write occupation data
        directory = base_directory + "occupation/"

        for pos, station_occupation in self.occupation_history.items():
            size = len(station_occupation)
            dset = file.create_dataset(
                directory + str(pos), (size,), dtype="uint32")
            dset.write_direct(np.array(station_occupation))

        # Write seeking and queueing
        self.compute_seeking_queueing(ev_vehicles)
        directory = base_directory + "global/"

        dset = file.create_dataset(directory + "seeking", (1,), dtype="float32")
        dset.write_direct(np.array(self.mean_seeking))

        dset = file.create_dataset(directory + "queueing", (1,), dtype="float32")
        dset.write_direct(np.array(self.mean_queueing))

        # # Write idle data
        # directory = base_directory + "idle/"
        # for ev in ev_vehicles:
        #     data = ev.idle_history
        #     if len(data) > 0:
        #         dset = file.create_dataset(directory + str(ev.id), (len(data),), dtype="uint32")
        #         dset.write_direct(np.array(data))
        
        # # Write charging data
        # directory = base_directory + "charging/"
        # for ev in ev_vehicles:
        #     data = ev.charging_history
        #     if len(data) > 0:
        #         dset = file.create_dataset(
        #             directory + str(ev.id), (len(data),), dtype="uint32")
        #         dset.write_direct(np.array(data))
