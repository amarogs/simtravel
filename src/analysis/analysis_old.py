import dill as pickle
import matplotlib.pyplot as plt
import math
import numpy as np
import os
import sys
from parameters_analysis import *
from matplotlib.backends.backend_pdf import PdfPages
import multiprocessing

# Set the configuration of pyplot backend
plt.rc('font', family='serif')
plt.rc('xtick', labelsize='x-small')
plt.rc('ytick', labelsize='x-small')
plt.rc('text', usetex=False)


class SimulationResult:

    @staticmethod
    def moving_avg(data, window):
        new_data = []
        if data.ndim == 1:

            for i in range(0, len(data)-window, 1):
                new_data.append(np.mean(data[i:i+window]))
        elif data.ndim == 2:
            for row in data:
                new_row = []
                for i in range(0, len(row)-window, 1):
                    new_row.append(np.mean(row[i:i+window]))
                new_data.append(new_row)
        return np.array(new_data)

    def __init__(self, simulator, data):
        """Class that takes the simulator used (simulator) and the arrays from the different repetitions of the simulation (data)
        and performs useful operations. The data is split into different attributes """
        self.simulator = simulator
        self.states = []
        self.speed = []
        self.mobility = []
        self.occupation = []
        self.intensity_int = []
        self.intensity_ext = []
        self.heat_map = []

        self.seeking = []
        self.std_seeking = None
        self.queueing = []
        self.std_queueing = None

        self.wait_d = []
        self.charge_d = []
        self.elapsed = simulator.elapsed

        self.sim_name = "EV_DEN: {} TF_DEN: {} LAYOUT: {}".format(
            simulator.EV_DENSITY, simulator.TF_DENSITY, simulator.LAYOUT)

        self.EV_DENSITY = simulator.EV_DENSITY
        self.TF_DENSITY = simulator.TF_DENSITY
        self.LAYOUT = simulator.LAYOUT
        self.total_vehicles = simulator.total_ev + simulator.total_gas

        self.MAX_BATTERY = simulator.MAX_BATTERY
        self.STD_CHARGE = simulator.STD_CHARGE
        self.WAIT_TIME_UPPER = simulator.WAIT_TIME_UPPER
        self.WAIT_TIME_LOWER = simulator.WAIT_TIME_LOWER
        self.STD_WAIT = simulator.STD_WAIT

        self.DELTA_TIME_STEP = simulator.DELTA_TIME_STEP
        self.PH_SECONDS_TS_FACTOR = simulator.PH_SECONDS_TS_FACTOR
        self.PH_DISTANCE_CELL_FACTOR = simulator.PH_DISTANCE_CELL_FACTOR
        for d in data:
            self.states.append(d.states_simulation)
            self.speed.append(d.speed_simulation)
            self.mobility.append(d.mobility_simulation)
            self.intensity_int.append(d.intensity_int_simulation)
            self.intensity_ext.append(d.intensity_ext_simulation)
            self.heat_map.append(d.heat_map_simulation)
            self.occupation.append(d.occupation_simulation)

            self.wait_d.append(d.wait_series)
            self.charge_d.append(d.charge_series)

            self.seeking.append(d.seeking_simulation)
            self.queueing.append(d.queueing_simulation)

        # Once the data has been split, combine the diferent repetitions.
        self.combine_repetitions()

        # Remove the simulator object since it is no longer needed
        del self.simulator

    def combine_repetitions(self):
        """Performs an average of the data contained in the initial lists by storing
        the data in a ND array and colapsing axis 0. """
        if PDF_INDIVIDUAL:
            self.states = SimulationResult.moving_avg(
                np.average(np.array(self.states), axis=0), WINDOW_SIZE)
            self.std_speed = SimulationResult.moving_avg(
                np.std(np.array(self.speed), axis=0), WINDOW_SIZE)
            self.std_mobility = SimulationResult.moving_avg(
                np.std(np.array(self.mobility), axis=0), WINDOW_SIZE)

            aux = {}
            for st in self.simulator.stations:
                aux[st.pos] = SimulationResult.moving_avg(np.average(
                    [occupation_dict[st.pos] for occupation_dict in self.occupation], axis=0), WINDOW_SIZE)
            self.occupation = aux

            self.intensity_int = np.average(
                np.array(self.intensity_int), axis=0)
            self.intensity_ext = np.average(
                np.array(self.intensity_ext), axis=0)

            self.heat_map = np.average(np.array(self.heat_map), axis=0)
            aux = []
            for d in self.charge_d:
                aux += d
            self.charge_d = aux

            aux = []
            for d in self.wait_d:
                aux += d
            self.wait_d = aux

        # Retrieve the seeking and queueing data
        self.std_seeking = np.std(self.seeking, axis=0)
        self.seeking = np.average(self.seeking, axis=0)

        self.std_queueing = np.std(self.queueing, axis=0)
        self.queueing = np.average(self.queueing, axis=0)

        self.total_time = self.seeking + self.queueing

        # Retrieve speed measures
        self.speed = SimulationResult.moving_avg(
            np.average(np.array(self.speed), axis=0), WINDOW_SIZE)
        self.mean_speed = np.average(self.speed)
        # Retieve mobility measures
        self.mobility = SimulationResult.moving_avg(
            np.average(np.array(self.mobility), axis=0), WINDOW_SIZE)
        self.mean_mobility = np.average(self.mobility)

    def create_pdf(self):
        """Creates a PDF file with the parameters set on the analysis_parameters."""

        # Create the folder where the images are going to be stored
        sim_name = "{}_{}_{}".format(
            self.EV_DENSITY, self.TF_DENSITY, self.LAYOUT)
        path = "results/analysis/"+sim_name
        if not os.path.exists(path):
            os.makedirs(path)

        # Create the figures and store the names of the files
        figures = []
        names = []
        if STATES:
            figures.append(self.states_graph())
            names.append("states_"+sim_name)
        if OCCUPATION:
            aux = self.occupation_graph()
            for (i, fig) in enumerate(aux):
                figures.append(fig)
                names.append("occupation"+str(i)+"_"+sim_name)
        if HEAT_MAP:
            aux = self.heat_map_graph()
            for (i, fig) in enumerate(aux):
                figures.append(fig)
                names.append("heat"+str(i)+"_"+sim_name)
        if VELOCITIES:
            figures.append(self.velocities_graph())
            names.append("velocity_"+sim_name)
        if DISTRIBUTION:
            figures.append(self.distribution("charge_d"))
            names.append("charge_distr_"+sim_name)
            figures.append(self.distribution("wait_d"))
            names.append("wait_distr_"+sim_name)
        # Create a new PDF creator and save the figures into eps format.
        pp = PdfPages(
            path+"/ev{}tf{}ly{}.pdf".format(self.EV_DENSITY, self.TF_DENSITY, self.LAYOUT))

        for (fig, name) in zip(figures, names):
            pp.savefig(fig)
            fig.savefig(path+"/" + name+".eps", format="eps", dpi=100)
            fig.clear()
            plt.close(fig)
        pp.close()

    def states_graph(self):
        fig = plt.figure(figsize=FIGSIZE)

        for s in range(len(self.states)):
            plt.plot(self.states[s], color=COLORS[s],
                     label=STATE_NAMES[s], linewidth=2)
            x = [int(i*self.DELTA_TIME_STEP*self.PH_SECONDS_TS_FACTOR/60) for i in range(0, len(self.states[s]))]
            
        plt.suptitle(self.sim_name)
        plt.xlabel("Simulation evolution (steps)")
        plt.ylabel("Number of EVs at each state (EVs)")
        plt.title("Evolution of states.")
        plt.legend()

        if SHOW:
            plt.show()
        return fig

    def distribution(self, attribute):
        fig = plt.figure(figsize=FIGSIZE)
        if attribute == "charge_d":
            mu, sigma = self.MAX_BATTERY/2, self.STD_CHARGE
            x_label = "Battery charge values (steps)"
        else:
            mu, sigma = (self.WAIT_TIME_UPPER +
                         self.WAIT_TIME_LOWER)/2, self.STD_WAIT
            x_label = "Time spent waiting at destination (steps)"

        s = self.__dict__[attribute]
        # Compute the histogram
        count, bins, ignored = plt.hist(
            s, density=True, stacked=True, color="0.9", ls="solid")

        x = np.array(range(0, int(1.1*bins[-1])))
        plt.plot(x, 1/(sigma * np.sqrt(2 * np.pi)) * np.exp(- (x - mu)
                                                            ** 2 / (2 * sigma**2)), linewidth=2, color='r')
        plt.xlabel(x_label)
        plt.ylabel("Probability")

        if SHOW:
            plt.show()
        return fig

    def occupation_graph(self):
        """Creates figures of 4 subplots with the occupation of the stations """
        super_title = self.sim_name + " {}/{}"

        def plot_four_stations(plot_i, total_plots, stations, occupation):
            """Creates a figure to plot 4 stations occupation """

            fig = plt.figure(figsize=FIGSIZE)  # Create the figure

            plt.suptitle(super_title.format(plot_i+1, total_plots))
            plt.subplots_adjust(hspace=0.4)  # Adjust the space

            for i in range(4):  # Creates the subplots
                index = plot_i + i
                if index >= len(stations):
                    continue  # The last figure may contain less than 4 stations
                else:
                    pos = stations[plot_i + i]
                    plt.subplot(2, 2, i+1)
                    plt.plot(occupation[pos], color='k')
                    plt.xlabel("Simulation evolution (steps)")
                    plt.ylabel("Station occupation (EVs)")
                    plt.title("Station at {} ".format(pos))
            if SHOW:
                plt.show()
            return fig

        stations = sorted(list(self.occupation))
        if len(stations) == 1:
            total_plots, plot_i = 1, 0  # We have only one plot

            fig = plt.figure(figsize=FIGSIZE)  # Create the figure
            plt.suptitle(super_title.format(
                plot_i+1, total_plots))  # Add the suptitle
            plt.plot(self.occupation[stations[0]], color='k')  # Plot the data
            plt.xlabel("Simulation evolution (steps)")
            plt.ylabel("Station occupation (EVs)")
            plt.title("Station at {} ".format(stations[0]))

            occupation_plots = [fig]  # Create the list of plots
            if SHOW:
                plt.show()

        elif len(stations) == 4:
            occupation_plots = [plot_four_stations(
                0, 1, stations, self.occupation)]
        else:
            total_plots = math.ceil(len(stations)/4)
            occupation_plots = [plot_four_stations(plot_i, total_plots, stations, self.occupation)
                                for plot_i in range(total_plots)]

        return occupation_plots

    def heat_map_graph(self):
        super_title = self.sim_name + " - Snapshot {}/{}"
        figures = []
        for (i, hmap) in enumerate(self.heat_map):

            # Create a subplot for this snapshot
            fig = plt.figure(figsize=FIGSIZE)
            plt.suptitle(super_title.format(i+1, len(self.heat_map)))
            norm = 1.0/(np.max(hmap))
            # Plot the heat map
            ax = plt.imshow(norm*hmap, cmap='hot',
                            interpolation='nearest', origin='upper')
            # Show the leyend
            cbar = plt.colorbar(ax, label="Probability of finding a vehicle")
            figures.append(fig)
            if SHOW:
                plt.show()

        return figures

    def velocities_graph(self):
        """Code to plot the mean speed of the vehicles and mean mobility"""
        # Create a figure
        fig = plt.figure(figsize=FIGSIZE)
        plt.suptitle(self.sim_name)

        # Create a subplot
        plt.subplot(1, 2, 1)

        plt.xlabel("Simulation evolution (steps)")
        plt.ylabel("Mean speed (cells/step)")

        # Plot the data
        plt.plot(range(len(self.speed)), [self.mean_speed for i in range(
            len(self.speed))], color="k", label="Mean speed of simulation")
        plt.scatter(range(len(self.speed)), self.speed, s=1,
                    color="0.5", ls="solid", label="Evolution of mean speed")

        plt.legend()

        # Create a subplot
        plt.subplot(1, 2, 2)

        plt.xlabel("Simulation evolution (steps)")
        plt.ylabel("Mean mobility (cells/step)")

        # Plot the data
        plt.plot(range(len(self.mobility)), [self.mean_mobility for i in range(
            len(self.mobility))], color="k", label="Mean mobility of simulation")
        plt.scatter(range(len(self.mobility)), self.mobility, s=1,
                    color="0.5", ls="solid", label="Evolution of mean mobility")

        plt.legend()

        """Code to plot the intensity of vehicles at different points in avenues """
        # #Create a subplot
        # plt.subplot(1,2,2)

        # #Let's resume the information we've got in the corresponding matrices
        # interior = np.average(self.intensity_int, axis=0)
        # exterior = np.average(self.intensity_ext, axis=0)

        # #Plot the data in the subplots
        # plt.plot(interior, label="interior lane")
        # plt.plot(exterior, label="exterior lane")

        # plt.yticks([0,0.5, 0.75, 0.9, 1])
        # plt.legend()
        # plt.xlabel("Positions where intensity was measured")
        # plt.ylabel("Traffic intensity on avenues (vehicles/step)")

        if SHOW:
            plt.show()
        return fig


def plot_elapsed(result_objects):
    fig = plt.figure(figsize=FIGSIZE)
    color = {"central": "red", "distributed": "blue", "four": "green"}

    marker = {0.1: ">", 0.2: "<", 0.3: "D",
              0.4: "P", 0.5: "o", 0.7: "s", 1: "H"}
    marker = {0.5: "k", 0.7: "0.5"}
    ls = {0.1: "dotted", 0.4: "solid", 0.8: "dashed"}

    for layout, ev_dict in result_objects.items():
        for ev_den, sim in ev_dict.items():
            x, y = [], []
            for s in sim:
                x.append(s.total_vehicles)
                y.append(s.elapsed/(60*s.total_vehicles))

            plt.plot(x, y, color=color[layout], linestyle=ls[ev_den], label="{} {}".format(
                layout, ev_den))
    plt.title("Elapsed time")
    plt.xlabel("Total number of vehicles (vehicles)")
    plt.ylabel("Time spent on a repetition (minutes/vehicle)")
    plt.legend()
    return "elapsed", fig


def global_group_graph(sorted_simulations, attr):
    """sorted_simulations must be sorted being PROPERTY_1='LAYOUT' and PROPERTY_2='EV_DENSITY' """

    fig = plt.figure(figsize=FIGSIZE)
    color = {"central": "red", "distributed": "blue", "four": "green"}

    marker = {0.1: ">", 0.2: "<", 0.3: "D",
              0.4: "P", 0.5: "o", 0.7: "s", 1: "H"}
    marker = {0.5: "k", 0.7: "0.5"}
    ls = {0.1: "dotted", 0.4: "solid", 0.8: "dashed"}
    if attr == "seeking" or attr == "queueing":
        conversion = {"seeking": "buscando", "queueing": "en cola"}
        plt.ylabel("Number of steps {}".format(attr))
    elif attr == "total_time":
        plt.ylabel("Total time spent on recharging (steps)")
    elif attr == "mean_speed":
        plt.ylabel("Mean speed (cells/step)")
    plt.xlabel("Total number of vehícules")

    for layout, ev_dict in sorted_simulations.items():
        for ev_den, sim in ev_dict.items():
            x, y = [], []
            for s in sim:
                x.append(s.total_vehicles)
                y.append(s.__dict__[attr])

            plt.plot(x, y, color=color[layout], linestyle=ls[ev_den], linewidth=2, label="{} {}".format(
                layout, ev_den))
    plt.title(attr[0].upper()+attr[1:])

    plt.legend()

    return attr+"_All", fig


def global_graphs(simulations):
    figures = []

    # Create graphs for each distribution

    for property_1, property_2_dict in graphs_distribution(simulations).items():

        figures.extend([global_single_graph(property_1, property_2_dict, attr)
                        for attr in SINGLE])

    # Create group graphs for all layouts
    result_objects = graphs_distribution(simulations, 'LAYOUT', 'EV_DENSITY')
    figures.extend(global_group_graph(result_objects, attr) for attr in GROUPS)

    figures.append(plot_elapsed(result_objects))

    # Create a new PDF creator
    path = "results/analysis/global/"

    pp = PdfPages(path + "global.pdf")

    for (i, content) in enumerate(figures):
        name, fig = content
        pp.savefig(fig)
        fig.savefig(path + name+".eps", format="eps", dpi=500)
        fig.clear()
        plt.close(fig)
    pp.close()

    return figures


def global_single_graph(property_1, property_2_dict, attr):
    # Create a figure
    fig = plt.figure(figsize=FIGSIZE)
    plt.suptitle("Attribute: {} {}: {}".format(attr, PROPERTY_1, property_1))
    if attr == "seeking" or attr == "queueing":
        plt.ylabel("Time spent {} (steps)".format(attr))
    elif attr == "total_time":
        plt.ylabel("Total time spent (steps)")
    elif attr == "mean_speed":
        plt.ylabel("Mean speed (cells/step)")

    plt.xlabel("Total number of vehicles (vehicles)")

    # Plot a graph with error bars, there is a different plot for every ev_density.
    for property_2, sims in property_2_dict.items():

        x, y, yerr = [], [], []
        if "std_"+attr not in sims[0].__dict__:
            with_error = False
        else:
            with_error = True

        for s in sims:
            y.append(s.__dict__[attr])  # Take the y data from each simulation
            if with_error:
                # Take the standard deviation
                yerr.append(s.__dict__["std_"+attr])
            # Take the x data from each simulation
            x.append(s.__dict__["total_vehicles"])
        if with_error:
            plt.errorbar(x, y, yerr=yerr, linewidth=2,
                         label="{} = {}".format(PROPERTY_2, property_2))
        else:
            plt.plot(x, y, linewidth=2, label="{} = {}".format(
                PROPERTY_2, property_2))
        plt.legend()

    if SHOW:
        plt.show()

    return attr+"_"+str(property_1)+"_"+PROPERTY_2, fig


def perform_individual_analysis(filename):
    with open(filename, "rb") as f:

        metrics_data = pickle.load(f)

        # Create the simulation object
        s = SimulationResult(metrics_data[0], metrics_data[1:])
        if PDF_INDIVIDUAL:
            s.create_pdf()  # Create the PDF
        if PLOT_GLOBAL:
            return s
        else:
            return


def graphs_distribution(simulations, attribute_1=PROPERTY_1, attribute_2=PROPERTY_2):
    """Given a list of simulations, create a dictionary sorted by attribute_1 
    such that each element is another dictionary sorted by attribute_2 """

    def sort_simulations(attribute, simulations):
        """Given a list of simulations, returns a dictionary where keys are the 
        attribute and the value is a list of simulations with that attribute"""
        result = {}
        for sim in simulations:
            key = sim.__dict__[attribute]
            if key in result:
                result[key].append(sim)
            else:
                result[key] = [sim]

        return result

    distribution = sort_simulations(attribute_1, simulations)

    for k, unsorted in distribution.items():
        distribution[k] = sort_simulations(attribute_2, unsorted)

    return distribution


"""********************SCRIPT STARTS*****************"""

# Read the command line for arguments
if len(sys.argv) == 2:
    NUM_PROC = int(sys.argv[1])

if NUM_PROC > 1:
    PARALLEL = True
else:
    PARALLEL = False

# Make the destination directory if it doesn't exist
if not os.path.exists("results/analysis"):
    os.makedirs("results/analysis")
    os.makedirs("results/analysis/global")
else:
    if not os.path.exists("results/analysis/global"):
        os.makedirs("results/analysis/global")


# Start the analysis by sorting how the files are going to be open
files = ["results/" + f for f in os.listdir("results/") if f[-2::] == "pk"]

# Itereate through the files and create a SimulationResult object for each
# simulation. If PDF_INDIVIDUAL is True a PDF is built for each simulation, the
# content of the PDF files is controlled via the parameters_analysis  flags.

individual_analysis = []
if PARALLEL:
    pool = multiprocessing.Pool(NUM_PROC)
    individual_analysis.extend(pool.map(perform_individual_analysis, files))

else:
    individual_analysis.extend(
        [perform_individual_analysis(filename) for filename in files])

# At this step what we have is a list of SimulationResult objects with the data from the simulation,
# now we can sort it and make global graphs.
if PLOT_GLOBAL:
    global_graphs(individual_analysis)
