import math
import os

import h5py
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_pdf import PdfPages

import simtravel.analysis.parameters_analysis as params
from simtravel.application.simulation import Simulation
from simtravel.metrics.units import Units
from simtravel.models.states import States

# Configure the matplotlib backend
plt.rc('font', family='serif')
plt.rc('xtick', labelsize='x-small')
plt.rc('ytick', labelsize='x-small')
plt.rc('text', usetex=False)


class SimulationAnalysis(Simulation):
    def __init__(self, EV_DEN, TF_DEN, ST_LAYOUT):
        super().__init__(EV_DEN, TF_DEN, ST_LAYOUT)

        self.sim_name = "EV_DEN: {} TF_DEN: {} LAYOUT: {}".format(
            EV_DEN, TF_DEN, ST_LAYOUT)

        path = "results/analyzed"
        if not os.path.exists(path):
            os.makedirs(path)

    def load_data(self, filename):
        """Takes the attributes of the root folder of the
        HDF5 file and stores them as class attributes. It also
        loads the datasets from different groups and repetitions
        and place them together in numpy arrays creating
        two dictionaries per group: one containing the mean 
        of the different repetitions and other containing the std. """

        with h5py.File(filename, "r") as file:

            # Save the simulation attributes
            for key, val in file.attrs.items():
                self.__setattr__(key, val)

            # Retrieve the data from the groups
            for group in list(file['0'].keys()):

                data_mean, data_std = self.get_data_from_group(file, group)

                self.__setattr__(group+"_mean", data_mean)
                self.__setattr__(group+"_std", data_std)

        # Once we have loaded the datasets, we have to create a
        # units objects
        self.units = Units(self.SPEED, self.CELL_LENGTH, self.SIMULATION_SPEED,
                           self.BATTERY, self.CS_POWER, self.AUTONOMY)

    def get_array_shape(self, ds_shape):
        """Returns a shape that can hold the datasets
        for all the repetitions """

        arr_shape = None

        if len(ds_shape) == 1:
            arr_shape = (self.REPETITIONS, ds_shape[0])
        elif len(ds_shape) == 2:
            arr_shape = [self.REPETITIONS]+list(ds_shape)
        else:
            print("No se entiende el dato")

        return arr_shape

    def get_data_from_group(self, file, group_name):
        # Every group has more than one element that we
        # want to save, each one must be saved onto a dictionary.

        data_mean = {}
        data_std = {}
        for element in file['0/'+group_name].keys():

            dest_shape = file['0/'+group_name+"/"+element].shape
            # Create the numpy array that will hold the data
            dest_arr = np.zeros(self.get_array_shape(dest_shape))

            # Fullfill the numpy array
            for i in range(self.REPETITIONS):
                dset = file[str(i)+'/'+group_name+"/"+element]
                dset.read_direct(dest_arr, dest_sel=np.s_[i])

            data_std[element] = np.std(dest_arr, axis=0)
            data_mean[element] = np.mean(dest_arr, axis=0)

        return data_mean, data_std

    def steps_to_minutes(self, length):
        return self.units.steps_to_minutes(np.arange(length)*self.DELTA_TSTEPS)

    def graph_states_evolution(self):

        fig = plt.figure(figsize=params.FIGSIZE)
        x = self.steps_to_minutes(len(self.states_mean['States.AT_DEST']))

        for s in States:
            plt.errorbar(x, self.states_mean[str(s)], yerr=self.states_std[str(s)], color=params.COLORS[s],
                         label=params.STATE_NAMES[s], linewidth=2)

        plt.xlabel("Time (minutes)")
        plt.ylabel("Number of EVs at each state (EVs)")
        plt.title("Evolution of states.")
        plt.legend()

        return fig

    def graph_occupation_evolution(self):
        """Creates figures of 4 subplots with the occupation of the stations """
        super_title = self.sim_name + " {}/{}"

        def plot_four_stations(plot_i, total_plots, stations, occupation):
            """Creates a figure to plot 4 stations occupation """

            fig = plt.figure(figsize=params.FIGSIZE)  # Create the figure

            plt.suptitle(super_title.format(plot_i+1, total_plots))
            plt.subplots_adjust(hspace=0.4)  # Adjust the space

            for i in range(4):  # Creates the subplots
                index = plot_i + i
                if index >= len(stations):
                    continue  # The last figure may contain less than 4 stations
                else:
                    pos = stations[plot_i + i]
                    plt.subplot(2, 2, i+1)
                    y = occupation[pos]
                    x = self.steps_to_minutes(len(y))
                    plt.plot(x, y, color='k')
                    plt.xlabel("Time (minutes)")
                    plt.ylabel("Station occupation (EVs)")
                    plt.title("Station at {} ".format(pos))

            return fig

        stations = sorted(list(self.occupation_mean.keys()))
        if len(stations) == 1:
            total_plots, plot_i = 1, 0  # We have only one plot

            fig = plt.figure(figsize=params.FIGSIZE)  # Create the figure
            plt.suptitle(super_title.format(
                plot_i+1, total_plots))  # Add the suptitle
            # Plot the data
            y = self.occupation_mean[stations[0]]
            x = self.steps_to_minutes(len(y))
            plt.plot(x, y, color='k')
            plt.xlabel("Simulation evolution (steps)")
            plt.ylabel("Station occupation (EVs)")
            plt.title("Station at {} ".format(stations[0]))

            occupation_plots = [fig]  # Create the list of plots

        elif len(stations) == 4:
            occupation_plots = [plot_four_stations(
                0, 1, stations, self.occupation_mean)]
        else:
            total_plots = math.ceil(len(stations)/4)
            occupation_plots = [plot_four_stations(plot_i, total_plots, stations, self.occupation_mean)
                                for plot_i in range(total_plots)]

        return occupation_plots

    def graph_heat_map_evolution(self):
        super_title = self.sim_name + " - Snapshot {}/{}"
        figures = []
        for (i, hmap) in self.heat_map_mean.items():

            # Create a subplot for this snapshot
            fig = plt.figure(figsize=params.FIGSIZE)
            plt.suptitle(super_title.format(
                eval(i)+1, len(self.heat_map_mean)))
            norm = 1.0/(np.max(hmap))
            # Plot the heat map
            ax = plt.imshow(norm*hmap, cmap='hot',
                            interpolation='nearest', origin='upper')
            # Show the leyend
            cbar = plt.colorbar(ax, label="Probability of finding a vehicle")
            figures.append(fig)

        return figures

    def graph_velocities_evolution(self):
        """Code to plot the mean speed of the vehicles and mean mobility"""
        # Create a figure
        fig = plt.figure(figsize=params.FIGSIZE)
        plt.suptitle(self.sim_name)

        # Create a subplot
        plt.subplot(1, 2, 1)

        plt.xlabel("Simulation evolution (minutes)")
        plt.ylabel("Mean speed (km/h)")

        # Plot the data
        y = self.units.simulation_speed_to_kmh(
            self.velocities_mean['speed'])

        yerr = self.units.simulation_speed_to_kmh(
            self.velocities_std['speed'])
        x = self.steps_to_minutes(len(y))

        plt.errorbar(x, y, yerr=yerr, color="k", label="Mean speed evolution")

        plt.legend()

        # Create a subplot
        plt.subplot(1, 2, 2)

        plt.xlabel("Simulation evolution (minutes)")
        plt.ylabel("Mean mobility (km/h)")
        y = self.units.simulation_speed_to_kmh(
            self.velocities_mean['mobility'])
        yerr = self.units.simulation_speed_to_kmh(
            self.velocities_std['mobility'])
        x = self.steps_to_minutes(len(y))

        plt.errorbar(x, y, yerr=yerr, color="k",
                     label="Mean mobility evolution")

        plt.legend()

        return fig

    def generate_report(self):

        # Create the folder where the images are going to be stored.
        base_name = "{}_{}_{}".format(self.EV_DEN, self.TF_DEN, self.ST_LAYOUT)
        path = "results/analyzed/" + base_name
        if not os.path.exists(path):
            os.makedirs(path)

        # Create the figures
        figures, names = self.create_figures(base_name)

        # Save the figures into a file and a PDF
        pp = PdfPages(path+"/ev{}tf{}ly{}.pdf".format(self.EV_DEN,
                                                      self.TF_DEN, self.ST_LAYOUT))

        for (fig, name) in zip(figures, names):
            pp.savefig(fig)
            fig.savefig(path+"/" + name+".eps", format="eps", dpi=100)
            fig.clear()
            plt.close(fig)
        pp.close()

    def create_figures(self,base_name):
        """Based on the configuration file,create the figures of the simulation. """
        figures, names = [], []

        if params.STATES:
            figures.append(self.graph_states_evolution())
            names.append("states_"+base_name)

        if params.OCCUPATION:
            aux = self.graph_occupation_evolution()
            for (i, fig) in enumerate(aux):
                figures.append(fig)
                names.append("occupation"+str(i)+"_"+base_name)

        if params.HEAT_MAP:
            aux = self.graph_heat_map_evolution()
            for (i, fig) in enumerate(aux):
                figures.append(fig)
                names.append("heat"+str(i)+"_"+base_name)

        if params.VELOCITIES:
            figures.append(self.graph_velocities_evolution())
            names.append("velocity_"+base_name)

        # if params.DISTRIBUTION:
        #     figures.append(self.distribution("charge_d"))
        #     names.append("charge_distr_"+base_name)
        #     figures.append(self.distribution("wait_d"))
        #     names.append("wait_distr_"+base_name)
        return figures, names

# Por cada string de arhivo HDF5, leer los atributos del nombre y crear el objeto
# SimuationAnalysis
