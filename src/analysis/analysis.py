import math
import os

import h5py
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_pdf import PdfPages

import src.analysis.parameters_analysis as params
from src.simulator.simulation import Simulation
from src.metrics.units import Units
from src.models.states import States

# Configure the matplotlib backend
plt.rc('font', family='serif')
plt.rc('xtick', labelsize='x-small')
plt.rc('ytick', labelsize='x-small')
plt.rc('text', usetex=False)


class SimulationAnalysis(Simulation):
    def __init__(self, EV_DEN, TF_DEN, ST_LAYOUT, filepath):
        super().__init__(EV_DEN, TF_DEN, ST_LAYOUT)

        self.sim_name = "EV_DEN: {} TF_DEN: {} LAYOUT: {}".format(
            EV_DEN, TF_DEN, ST_LAYOUT)

        self.filepath = filepath

        # Check if the analyzed folder exists
        path = "results/analyzed"
        if not os.path.exists(path):
            os.makedirs(path)

        # load the data into the object
        self.load_data()
        # Prepare the data for the global report
        self.prepare_global_data()
        # Create the pulse for the moving average convolution
        self.pulse_ma = np.repeat(1.0, params.WINDOW_SIZE)/params.WINDOW_SIZE
        self.half_window = int(params.WINDOW_SIZE/2)
        # generate the report of the simulation
        self.generate_report()

    def prepare_global_data(self):
        """This function takes the attributes that are going
        to be used as a global meter of the simulation. """

        # Convert the time variables to minutes
        to_minutes = ['seeking', 'queueing', 'total']
        for key in to_minutes:
            self.global_mean[key] = self.units.steps_to_minutes(
                self.global_mean[key])

            self.global_std[key] = self.units.steps_to_minutes(
                self.global_std[key])

        # Convert the velocities into km/h and compute the std.
        to_kmh = ['speed', 'mobility']
        for key in to_kmh:
            self.global_mean[key] = self.units.simulation_speed_to_kmh(
                np.mean(self.global_mean[key]))
            self.global_std[key] = self.units.simulation_speed_to_kmh(
                np.std(self.global_mean[key]))

        # Convert the elapsed time to minutes/(vehicles * repetitions)
        self.global_mean['elapsed'] = self.units.steps_to_minutes(
            self.ELAPSED/(self.TOTAL_VEHICLES*self.REPETITIONS))
        self.global_std['elapsed'] = 0

    def load_data(self):
        """Takes the attributes of the root folder of the
        HDF5 file and stores them as class attributes. It also
        loads the datasets from different groups and repetitions
        and place them together in numpy arrays creating
        two dictionaries per group: one containing the mean 
        of the different repetitions and other containing the std. """

        with h5py.File(self.filepath, "r") as file:

            # Save the simulation attributes
            for key, val in file.attrs.items():
                self.__setattr__(key, val)

            # Retrieve the data from the groups
            for group in list(file['0'].keys()):

                data_mean, data_std = self.get_data_from_group(file, group)

                self.__setattr__(group+"_mean", data_mean)
                self.__setattr__(group+"_std", data_std)

            # Obtain the total time spent charging and insert it
            # in the dictionary of global attributes
            data_mean, data_std = self.get_data_total_group(file, "global")
            self.global_mean['total'] = data_mean
            self.global_std['total'] = data_std

            # Obtain the mean and std of the velocities group by columns.
            data_mean, data_std = self.get_data_from_group(
                file, 'velocities', axis=1)
            for key, val in data_mean.items():
                self.global_mean[key] = val

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

    def get_data_total_group(self, file, group_name):
        """Given a group name, retrieves the data from all
        elements of this group. Each element gives a matrix, so
        we make an nd-array with each element and resumes the data
        by collapsing every element into one. Then compute the mean
        and std of the collapsed matrix. This is made so that we 
        can compute total time spent charging """

        data = []
        for element in file['0/'+group_name].keys():

            dest_shape = file['0/'+group_name+"/"+element].shape
            # Create the numpy array that will hold the data
            dest_arr = np.zeros(self.get_array_shape(dest_shape))

            # Fullfill the numpy array
            for i in range(self.REPETITIONS):
                dset = file[str(i)+'/'+group_name+"/"+element]
                dset.read_direct(dest_arr, dest_sel=np.s_[i])

            data.append(dest_arr)
        data = np.sum(data, axis=0)
        data_mean, data_std = np.mean(data, axis=0), np.std(data, axis=0)

        return data_mean, data_std

    def get_data_from_group(self, file, group_name, axis=0):
        # Every group has more than one element that we
        # want to save, each one must be saved onto a dictionary.

        data_mean, data_std = {}, {}

        for element in file['0/'+group_name].keys():

            dest_shape = file['0/'+group_name+"/"+element].shape
            # Create the numpy array that will hold the data
            dest_arr = np.zeros(self.get_array_shape(dest_shape))

            # Fullfill the numpy array
            for i in range(self.REPETITIONS):
                dset = file[str(i)+'/'+group_name+"/"+element]
                dset.read_direct(dest_arr, dest_sel=np.s_[i])

            data_std[element] = np.std(dest_arr, axis=axis)
            data_mean[element] = np.mean(dest_arr, axis=axis)

        return data_mean, data_std

    def steps_to_minutes(self, length):
        return self.units.steps_to_minutes(np.arange(length)*self.DELTA_TSTEPS)

    def graph_states_evolution(self):

        fig = plt.figure(figsize=params.FIGSIZE)
        x = self.steps_to_minutes(len(self.states_mean['States.AT_DEST']))

        for s in States:
            plt.errorbar(x, self.states_mean[str(s)],
                        yerr=self.states_std[str(s)], color=params.COLORS[s],
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
                    plt.xlabel("Simulation evolution (minutes)")
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
            plt.xlabel("Simulation evolution (minutes)")
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
        y = self.units.simulation_speed_to_kmh(self.velocities_mean['speed'])

        yerr = self.units.simulation_speed_to_kmh(self.velocities_std['speed'])
        x = self.steps_to_minutes(len(y))

        plt.errorbar(x, y, yerr=yerr, color="k", label="Mean speed evolution")

        plt.legend()

        # Create a subplot
        plt.subplot(1, 2, 2)

        plt.xlabel("Simulation evolution (minutes)")
        plt.ylabel("Mean mobility (km/h)")

        y = self.units.simulation_speed_to_kmh(self.velocities_mean['mobility'])

        yerr = self.units.simulation_speed_to_kmh(self.velocities_std['mobility'])
        x = self.steps_to_minutes(len(y))

        plt.errorbar(x, y, yerr=yerr, color="k",label="Mean mobility evolution")

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
            fig.savefig(path+"/" + name+".svg", format="svg", dpi=100)
            fig.clear()
            plt.close(fig)
        pp.close()

    def create_figures(self, base_name):
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


class GlobalAnalysis():
    def __init__(self, attrs, *global_keys):
        super().__init__()
        # Compute the shape of the matrix that will
        # hold all data from the simulations.
        self.shape = self.global_matrix_shape(attrs)

        # For each key passed as attribute, we must
        # create a matrix to store the data.
        self.global_keys = global_keys
        for key in global_keys:
            self.__setattr__(key+"_mean", np.zeros(shape=self.shape))
            self.__setattr__(key+"_std", np.zeros(shape=self.shape))

        # Sort the keys into two categories and generate the suptitles
        self.traffic = ['seeking', 'queueing', 'total', 'elapsed']
        self.velocities = ['speed', 'mobility']
        self.suptitles = {'seeking': 'Mean time spent seeking EV rate = {}',
                          'queueing': 'Mean time spent queueing EV rate = {}',
                          'total': "Total time spent recharging EV rate = {} ",
                          'elapsed': "Time elapsed", 'speed': "Mean speed EV rate = {}",
                          'mobility': "Mean mobility EV rate = {} "}

        # Set the path to store the figures and pdf
        self.path = "results/analyzed/global"
        if not os.path.exists("results/analyzed/global"):
            os.makedirs(self.path)

    def global_matrix_shape(self, attrs):
        total_evd, total_tfd, total_layout = set(), set(), set()

        for (evd, tfd, layout, _) in attrs:
            total_evd.add(evd)
            total_tfd.add(tfd)
            total_layout.add(layout)

        self.evd_index = sorted(total_evd)
        self.tfd_index = sorted(total_tfd)
        self.layout_index = sorted(total_layout)

        shape = (len(self.evd_index),  len(
            self.layout_index), len(self.tfd_index))
        return shape

    def compute_index(self, simulation):
        ev = self.evd_index.index(str(simulation.EV_DEN))
        ly = self.layout_index.index(str(simulation.ST_LAYOUT))
        tf = self.tfd_index.index(str(simulation.TF_DEN))

        return (ev, ly, tf)

    def load_matrices(self, simulations):
        """Given a set of simulations, loads the content
        of the marices with the attributes from the global 
        attributes passed when this object was initialized. """

        for key in self.global_keys:
            matrix_mean = self.__dict__[key + "_mean"]
            matrix_std = self.__dict__[key + "_std"]
            for simulation in simulations:
                index = self.compute_index(simulation)
                matrix_mean[index] = float(simulation.global_mean[key])
                matrix_std[index] = float(simulation.global_std[key])

    def load_single_attribute(self, simulations, attribute):
        """Given a list of simulations and an attribute, extracts
        the attribute from the simulations and saves it into a matrix.
        This matrix will be called matrix_attribute where attribute is the
        value passed in lowercase. """
        matrix = np.zeros(shape=self.shape)
        for simulation in simulations:
            index = self.compute_index(simulation)
            matrix[index] = simulation.__dict__[attribute]
        self.__setattr__("matrix_"+attribute.lower(), matrix)

    def create_report(self):
        """Generates a pdf with all the figures produced. """
        # Create the figures and names for the files
        figures, names = self.graph_attributes()

        # Create a pdf pages object named: global.pdf
        pp = PdfPages(self.path+"/global.pdf")

        for (fig, name) in zip(figures, names):
            pp.savefig(fig)
            fig.savefig(self.path+"/" + name+".svg", format="svg", dpi=150)
            fig.clear()
            plt.close(fig)
        pp.close()

    def graph_attributes(self):
        """For each attribute passed as a global_key, generate
        the corresponding figures. One figure per EV density and 
        one summary. """

        figures, names = [], []

        for key in self.global_keys:
            # Retrieve the matrices from memory
            mean = self.__dict__[key+"_mean"]
            std = self.__dict__[key+"_std"]

            # For each ev density
            for i in range(self.shape[0]):
                fig, name = self.create_figure_per_evd(i, key, mean, std)
                figures.append(fig)
                names.append(name)

        return figures, names

    def create_figure_per_evd(self, i, key, mean, std):

        evd = self.evd_index[i]
        fig = plt.figure(figsize=params.FIGSIZE)

        # For each traffic density, plot each row
        for j in range(self.shape[1]):
            layout = self.layout_index[j]
            y, yerr = mean[i, j, :], std[i, j, :]
            x = self.matrix_total_vehicles[i, j, :]

            plt.errorbar(x, y, yerr=yerr, linewidth=2,
                         label="{} = {}".format("Layout", layout))

        # Set the axis
        plt.xlabel("Total number of vehicles")
        if key in self.traffic:
            plt.ylabel("Time (minutes)")
        elif key in self.velocities:
            plt.ylabel("Mean speed (km/h)")
        elif key == 'elapsed':
            plt.ylabel("Time elapsed per repetition (minutes/vehicle)")

        # Set the suptitle
        plt.suptitle(self.suptitles[key].format(evd))
        # Set the legend
        plt.legend()

        return fig, key+"_"+str(evd)
