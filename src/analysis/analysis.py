import math
import os
import h5py
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import scipy.stats as stats
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg


import src.analysis.parameters_analysis as params

from src.metrics.units import Units
from src.models.states import States
from src.simulator.simulation import Simulation

matplotlib.use('Qt5Agg')
plt.style.use('ggplot')
language = params.LANGUAGE


# Configure the matplotlib backend
plt.rc('text', usetex=False)

SMALL_SIZE = 6
MEDIUM_SIZE = 8
BIGGER_SIZE = 10

plt.rc('font', family='serif', size=SMALL_SIZE)          # controls default text sizes
plt.rc('axes', titlesize=BIGGER_SIZE)     # fontsize of the axes title
plt.rc('axes', labelsize=MEDIUM_SIZE)    # fontsize of the x and y labels
plt.rc('xtick', labelsize=SMALL_SIZE)    # fontsize of the tick labels
plt.rc('ytick', labelsize=SMALL_SIZE)    # fontsize of the tick labels
plt.rc('legend', fontsize=SMALL_SIZE)    # legend fontsize
plt.rc('figure', titlesize=BIGGER_SIZE)  # fontsize of the figure title

class GraphFunctions():
    def __init__(self,sim_name, units, n_elements_per_bin, DELTA_TSTEPS, total_measures):
        self.n_elements_per_bin = n_elements_per_bin
        self.units = units
        self.DELTA_TSTEPS = DELTA_TSTEPS
        self.sim_name = sim_name
        self.total_measures = total_measures

        self.x_measures_minutes = self.steps_to_minutes(total_measures)

    def binning_data(self, x, y):
        """Given an x,y series, returns a new x,y series having the elements
        grouped into bins. Each bin is the mean of the elements belonging to it.
        It is a way to reduce the number of points if a plot while mantaining the
        information. """

        indices = np.linspace(0, len(x), self.n_elements_per_bin, dtype='uint32')
    
        new_x, new_y = [], []
        for i in range(0,len(indices)-1,2):
            new_y.append(np.mean(y[indices[i]: indices[i+1]]))
            new_x.append(np.mean(x[indices[i]: indices[i+1]]))
        
        return new_x, new_y
    def steps_to_minutes(self, length):
        return self.units.steps_to_minutes(np.arange(length)*self.DELTA_TSTEPS)

      
    def graph_states_evolution(self, states_mean, states_std, x=None, live=False):
        """Given a dictionary of states{k=states, val=[number of vehicles in that state at that step]}, and
        the dictioanary with the deviation of the steps, returns a canvas with the lines plotted. """
        if x is None:
            x = self.x_measures_minutes
        keys = list(states_mean.keys())
        keys_as_strings = False
        if type(keys[0]) == type(""):
            keys_as_strings = True
        canvas = MplCanvas()
        canvas.axes = canvas.fig.add_subplot(111)


        for s in States:
            if keys_as_strings:
                state_mean, state_std = states_mean[str(s)], states_std[str(s)]
            else:
                state_mean, state_std = states_mean[s], states_std[s]

            new_x, new_y = self.binning_data(x, state_mean)

            _, new_err = self.binning_data(x, state_std)

            err_plot = canvas.axes.errorbar(new_x, new_y, yerr=new_err, color=params.COLORS[s], label=params.STATE_NAMES[language][s], linewidth=2)
        

        canvas.axes.set_xlabel(params.lb_evolution[language])
        canvas.axes.set_ylabel(params.lb_states_y[language])
        canvas.axes.set_title(params.lb_states[language])
        canvas.axes.legend()

        return canvas

    def graph_occupation_evolution(self, plugs_per_station, occupation_mean, x=None, live=False):
        """Receives a dictionary of stations where k=station position and val=[list of occupation]
        Creates canvas of 4 subplots with the occupation of the stations """
        
        super_title =  " {}/{}"

        def plot_four_stations(plot_i, total_plots, stations, occupation):
            nonlocal x
            """Creates a figure to plot 4 stations occupation """

            canvas = MplCanvas()
            canvas.fig.tight_layout()
            # canvas.fig.suptitle(super_title.format(plot_i+1, total_plots))
            canvas.fig.subplots_adjust(hspace=0.4)  # Adjust the space

            for i in range(4):  # Creates the subplots
                index = plot_i + i
                if index >= len(stations):
                    continue  # The last figure may contain less than 4 stations
                else:
                    pos = stations[plot_i + i]
                    canvas.__dict__['axes_'+str(i)] = canvas.fig.add_subplot(2, 2, i+1)
                    y = occupation[pos]

                    if x is None:
                        x = self.x_measures_minutes

                    canvas.__dict__['axes_'+str(i)].plot(x, y, color='k', label=params.lb_occupation_legend[language])
                    canvas.__dict__['axes_'+str(i)].plot(x, np.repeat(plugs_per_station, len(x)), color='green', linestyle="--", label=params.lb_occupation_capacity[language])
                    canvas.__dict__['axes_'+str(i)].legend()
                    canvas.__dict__['axes_'+str(i)].set_xlabel(params.lb_evolution[language])
                    canvas.__dict__['axes_'+str(i)].set_ylabel(params.lb_occupation_y[language])
                    canvas.__dict__['axes_'+str(i)].set_title(params.lb_occupation[language].format(pos))

            return canvas

        stations = sorted(list(occupation_mean.keys()))
        if len(stations) == 1:
            total_plots, plot_i, i = 1, 0,0  # We have only one plot
            pos = stations[plot_i + i]

            canvas = MplCanvas() # Create the canvas
            canvas.fig.tight_layout()
            canvas.__dict__['axes_'+str(i)] = canvas.fig.add_subplot(111)

            # Retrieve the data
            y = occupation_mean[stations[0]]
            if x is None:
                x = self.x_measures_minutes

            # Plot the data
            canvas.__dict__['axes_'+str(i)].plot(x, y, color='k', label=params.lb_occupation_legend[language])
            canvas.__dict__['axes_'+str(i)].plot(x, np.repeat(plugs_per_station, len(x)), color='green', linestyle="--", label=params.lb_occupation_capacity[language])
            canvas.__dict__['axes_'+str(i)].legend()
            canvas.__dict__['axes_'+str(i)].set_xlabel(params.lb_evolution[language])
            canvas.__dict__['axes_'+str(i)].set_ylabel(params.lb_occupation_y[language])
            canvas.__dict__['axes_'+str(i)].set_title(params.lb_occupation[language].format(pos))
            
            # Create the list of plots
            occupation_plots = [canvas]  

        elif len(stations) == 4:
            occupation_plots = [plot_four_stations(0, 1, stations, occupation_mean)]
        else:
            total_plots = math.ceil(len(stations)/4)
            occupation_plots = [plot_four_stations(plot_i, total_plots, stations, occupation_mean)
                                for plot_i in range(total_plots)]

        return occupation_plots

    def graph_heat_map_evolution(self, heat_map_mean,x=None, live=False):
        """Given a dictionary called heat_map_mean = {k=snapshot number, val=matrix of occupation of cells.}
        Returns a list of canvases where each canvas is a matrix image representing the probability of finding
        a vehicle. """

        super_title = params.lb_heat[language]
        canvases = []
        for (i, hmap) in heat_map_mean.items():

            # Create a subplot for this snapshot
            canvas = MplCanvas()
            canvas.axes = canvas.fig.add_subplot(111)
            canvas.axes.grid(False)
            canvas.figure.suptitle(super_title.format(eval(i)+1, len(heat_map_mean)))

            norm = 1.0/((eval(i)+1)*self.total_measures/len(heat_map_mean))
            # Plot the heat map
            img = canvas.axes.imshow(norm*hmap, cmap='hot',interpolation='none', origin='upper')
            
            # Show the leyend
            canvas.fig.colorbar(img, label=params.lb_heat_bar[language])
            canvases.append(canvas)

        return canvases

    def graph_velocities_evolution(self, velocities_mean, velocities_std, x=None, live=False):
        """Given two dictionaries: velocities_mean, velocities_std each having two keys:
        'speed' and 'mobility' and values are time series of those measures, plot in a canvas
        the two graphs side by side."""
        
        # Set the x value
        if x is None:
            x =self.x_measures_minutes
        
        
        # Create a figure
        canvas = MplCanvas()
        # canvas.fig.suptitle(self.sim_name)

        
        # Create a subplot
        canvas.axes_1 = canvas.fig.add_subplot(1,2,1)

        canvas.axes_1.set_xlabel(params.lb_evolution[language])
        canvas.axes_1.set_ylabel(params.lb_speed[language])

        # Plot the data
        y = self.units.simulation_speed_to_kmh(velocities_mean['speed'])
        
        yerr = self.units.simulation_speed_to_kmh(velocities_std['speed'])
        
        new_x, new_y = self.binning_data(x,y)
        _, new_yerr = self.binning_data(x, yerr)

        canvas.axes_1.errorbar(new_x, new_y, yerr=new_yerr, color="k")
        #canvas.axes_1.legend()

        # Create a subplot
        canvas.axes_2 = canvas.fig.add_subplot(1,2,2)

        canvas.axes_2.set_xlabel(params.lb_evolution[language])
        canvas.axes_2.set_ylabel(params.lb_mobility[language])

        y = self.units.simulation_speed_to_kmh(velocities_mean['mobility'])
        
        yerr = self.units.simulation_speed_to_kmh(velocities_std['mobility'])
        
        new_x, new_y = self.binning_data(x, y)
        _, new_yerr = self.binning_data(x, yerr)


        canvas.axes_2.errorbar(new_x, new_y, yerr=new_yerr, color="k")

        #canvas.axes_2.legend()

        return canvas


class MplCanvas(FigureCanvasQTAgg):

    def __init__(self, parent=None, width=params.FIGSIZE[0], height=params.FIGSIZE[1], dpi=100):
        self.fig = plt.Figure(figsize=(width, height), dpi=dpi)
        self.axes = None
        super(MplCanvas, self).__init__(self.fig)

    def create_normal_distribution(self, mu, sigma, inf, sup, unit):
        def get_sample(size):
            nonlocal mu, sigma, inf, sup

            sample = np.random.normal(mu, sigma,size=size )
            mask = (sample > sup) | (sample < inf)

            while np.any(mask):
                
                sample = np.where(mask, np.random.normal(mu, sigma, size=size), sample)
                mask = (sample > sup) | (sample < inf)
            
            return sample


        if self.axes != None:
            self.axes.cla()
        else:
            self.axes = self.fig.add_subplot(111)
        
        n_bins = 1200

        x = np.linspace(mu-5*sigma, mu+5*sigma, n_bins)
        # Plot the theorical normal distribution.
        self.axes.plot(x, stats.norm.pdf(x, mu, sigma), color="#3E8D7E", label="Función de densidad teórica")
        
        # Get a sample of the normal distribucion
        self.axes.hist(get_sample(n_bins),n_bins//30, density=True, color="#F4CA9F" ,label="Muestra aleatoria con límites")

        self.axes.set_xlabel(unit, fontsize=13)
        self.axes.set_ylabel("Densidad", fontsize=13)
        self.axes.legend(fontsize=8)
        self.fig.tight_layout()
        self.draw()
        
class SimulationAnalysis(Simulation):
    def __init__(self, EV_DEN, TF_DEN, ST_LAYOUT, PATH, filepath):
        super().__init__(EV_DEN, TF_DEN, ST_LAYOUT, PATH)

        self.filepath = filepath

        # load the data into the object
        self.load_data()

        # Compute number of plugs per station
        if ST_LAYOUT == "central":
            self.plugs_per_station = self.TOTAL_PLUGS
            self.n_stations = 1
        elif ST_LAYOUT == "distributed":
            self.plugs_per_station = self.TOTAL_PLUGS/self.TOTAL_D_ST
            self.n_stations = self.TOTAL_D_ST
        elif ST_LAYOUT == "four":
            self.plugs_per_station = self.TOTAL_PLUGS/4
            self.n_stations = 4

        # Prepare the data for the global report
        self.prepare_global_data()
        # Total plots
        total_occupation_plots = 1
        if len(self.occupation_mean) > 1:
            total_occupation_plots = len(self.occupation_mean)//4
        
        self.total_plots = 1 + total_occupation_plots +len(self.heat_map_mean) + 1
       
        # Create the grapher object:
        self.grapher = GraphFunctions(self.sim_name, self.units,params.N_BINS, self.DELTA_TSTEPS, len(self.states_mean['States.AT_DEST']))


        # Prepare for the generation of canvases
        # This code should be done directly with lambda functions, given that python can't pickle
        # lambda functions and we need to send this object trough a process, we are going to write
        # each function as a regular named function.

        self.computed_canvases = []

        self.canvas_creator = [self.lambda1, self.lambda2, self.lambda3, self.lambda4]

        # generate the report of the simulation
        # self.generate_report()
    def lambda1(self):
        return self.grapher.graph_states_evolution(self.states_mean, self.states_std)
    def lambda2(self):
        return self.grapher.graph_occupation_evolution(self.plugs_per_station, self.occupation_mean)
    def lambda3(self):
        return self.grapher.graph_heat_map_evolution(self.heat_map_mean)
    def lambda4(self):
        return self.grapher.graph_velocities_evolution(self.velocities_mean, self.velocities_std)
    def prepare_global_data(self):
        """This function takes the attributes that are going
        to be used as a global meter of the simulation. """

        # Convert the time variables to minutes
        to_minutes = ['seeking', 'queueing', 'total']
        for key in to_minutes:
            self.global_mean[key] = self.units.steps_to_minutes(self.global_mean[key])

            self.global_std[key] = self.units.steps_to_minutes(self.global_std[key])

        # Convert the velocities into km/h and compute the std.
        to_kmh = ['speed', 'mobility']
        for key in to_kmh:
            mean = self.units.simulation_speed_to_kmh(np.mean(self.global_mean[key]))
            std = np.std(self.global_mean[key])

            self.global_mean[key] = mean
            
            
            self.global_std[key] =  std

        # Convert the elapsed time to minutes/(vehicles * repetitions)
        self.global_mean['elapsed'] = self.units.steps_to_minutes(
            self.ELAPSED/(self.TOTAL_VEHICLES*self.REPETITIONS))
        self.global_std['elapsed'] = 0

        # Compute the mean occupation across all the stations:
        occupation_array = np.array([arr for pos, arr in self.occupation_mean.items()])
        
        mean_occupation = (np.mean(occupation_array, axis=1))/self.plugs_per_station
        self.global_mean['occupation'] = np.mean(mean_occupation)
        self.global_std['occupation'] = np.std(mean_occupation)

        # Save the total number of stations
        self.global_mean['n_stations'] = self.n_stations
        self.global_std['n_stations'] = 0


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

 
    def generate_report(self):

        # Create the folder where the images are going to be stored.
        base_name = "{}_{}_{}".format(self.EV_DEN, self.TF_DEN, self.ST_LAYOUT)

        path = os.path.join(os.path.dirname(self.filepath), "analyzed", base_name )
        
        if not os.path.exists(path):
            os.makedirs(path)

        # Create the figures
        figures, names = self.create_canvases(base_name)

        # Save the figures into a file and a PDF
        pp = PdfPages(path+"/ev{}tf{}ly{}.pdf".format(self.EV_DEN,
                                                      self.TF_DEN, self.ST_LAYOUT))

        for (fig, name) in zip(figures, names):
            if type(fig) == MplCanvas:
                fig = fig.fig
            pp.savefig(fig)
            fig.savefig(path+"/" + name+".pdf", format="pdf", dpi=100)
            fig.clear()
            plt.close(fig)
        pp.close()

    def create_canvases(self, base_name):
        """Based on the configuration file,create the canvases of the simulation. """
        canvases, names = [], []

        if params.STATES:
            canvases.append(self.canvas_creator[0]())
            names.append("states_"+base_name)

        if params.OCCUPATION:
            aux = self.canvas_creator[1]()
            for (i, fig) in enumerate(aux):
                canvases.append(fig)
                names.append("occupation"+str(i)+"_"+base_name)

        if params.HEAT_MAP:
            aux = self.canvas_creator[2]()
            for (i, fig) in enumerate(aux):
                canvases.append(fig)
                names.append("heat"+str(i)+"_"+base_name)

        if params.VELOCITIES:
            canvases.append(self.canvas_creator[3]())
            names.append("velocity_"+base_name)

        return canvases, names

    def get_canvas(self, canvas_index):
        """Given an index, returns the canvas with that index. If the graph has
        been computed, it is retrieved from memory, else it is computed and stored. """

        
        if canvas_index >= len(self.computed_canvases):
            # Check if the canvas exists in the list of computed canvases
            new_canvas = self.canvas_creator.pop(0)()

            # Create the new canvas and append it to the list of canvases.
            if type(new_canvas) is list:
                self.computed_canvases.extend(new_canvas)
            else:
                self.computed_canvases.append(new_canvas)


        return self.computed_canvases[canvas_index]
        

class GlobalAnalysis():
    def __init__(self, attrs, *global_keys):
        super().__init__()
        # Compute the shape of the matrix that will
        # hold all data from the simulations.
        self.shape = self.global_matrix_shape(attrs)

        # Set the path to store the figures and pdf
        self.path = os.path.join(attrs[0][-2],"results", "analyzed", "global" )
        if not os.path.exists(self.path):
            os.makedirs(self.path)
        # For each key passed as attribute, we must
        # create a matrix to store the data.
        self.global_keys = list(global_keys)

        # Add the key to compute the total number of stations.
        self.global_keys.append("n_stations")
        for key in self.global_keys:
            self.__setattr__(key+"_mean", np.zeros(shape=self.shape))
            self.__setattr__(key+"_std", np.zeros(shape=self.shape))

        # Sort the keys into two categories and generate the suptitles
        self.traffic = ['seeking', 'queueing', 'total', 'elapsed']
        self.velocities = ['speed', 'mobility']
        self.stations = ['occupation']


        self.suptitles_heat = {'seeking': 'Mean time spent seeking',
                    'queueing': 'Mean time spent queueing',
                    'total': "Total time spent recharging",
                    'elapsed': "Time elapsed", 'speed': "Mean speed",
                    'mobility': "Mean mobility", 
                    'occupation': "Mean station occupation"}
         
        self.total_plots = 0
        self.computed_canvases = []
    
    def compute_all(self):
        """Creates all the canvases and sets the number of total plots. """
        self.computed_canvases = self.graph_attributes()[0]
        self.total_plots = len(self.computed_canvases)

    def get_canvas(self,canvas_index):
        """Given an index, returns the canvas at that index. """
        return self.computed_canvases[canvas_index]

    def global_matrix_shape(self, attrs):
        total_evd, total_tfd, total_layout = set(), set(), set()

        for (evd, tfd, layout, _, _) in attrs:
            total_evd.add(evd)
            total_tfd.add(tfd)
            total_layout.add(layout)

        self.evd_index = sorted(list(total_evd))
        self.tfd_index = sorted(list(total_tfd))
        self.layout_index = sorted(list(total_layout))

        shape = (len(self.evd_index),  len(self.layout_index), len(self.tfd_index))
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
        """Generates a pdf with all the canvases produced. """
        # Create the canvases and names for the files
        canvases, names = self.graph_attributes()

        # Create a pdf pages object named: report.pdf
        pp = PdfPages(self.path+"/report.pdf")

        for (canvas, name) in zip(canvases, names):
            pp.savefig(canvas.figure)
            canvas.figure.savefig(self.path+"/" + name+".pdf", format="pdf", dpi=150)
        pp.close()

    def graph_attributes(self):
        """For each attribute passed as a global_key, generate
        the corresponding figures. One figure per EV density and 
        one summary. """

        figures, names = [], []

        for key in self.global_keys:
            if key != "n_stations":
                # Retrieve the matrices from memory
                mean = self.__dict__[key+"_mean"]
                std = self.__dict__[key+"_std"]

                # For each ev density
                for i in range(self.shape[0]):
                    fig, name = self.create_canvas_per_evd(i, key, mean, std)
                    figures.append(fig)
                    names.append(name)

                # For all ev density draw a heat map
                # fig, name = self.create_heat_map(key, mean, std)
                # figures.append(fig)
                # names.append(name)

        return figures, names

    def create_heat_map(self, key, mean, std):
        """Returns a canvas with 3 heat maps, each one representing a layout and the values
        come from evd x tfd. Rememeber that the input matrices are sorted by (evd, ly, tf) """
        
        mean_by_ly =  mean.swapaxes(0,1)
        std_by_ly = std.swapaxes(0,1)
        canvas = MplCanvas()
        canvas.fig.suptitle(self.suptitles_heat[key])
        

        for i, name in enumerate(self.layout_index):
            canvas.__dict__["canvas_".format(i+1)] = canvas.fig.add_subplot(1, 3, i+1)
            axes = canvas.__dict__["canvas_".format(i+1)]
            max_value = np.max(mean[i])
            img = axes.imshow(mean[i]/max_value, origin='upper', vmin=0, vmax=1)

            axes.set_title(name)
            axes.set_xticks(np.arange(len(self.tfd_index)))
            axes.set_xticklabels(self.tfd_index)

            axes.set_yticks(np.arange(len(self.evd_index)))
            axes.set_yticklabels(self.evd_index)

            # for j in range(len(self.evd_index)):
            #     for k in range(len(self.tfd_index)):
            #             text = axes.text(k, j, mean[i][j, k],ha="center", va="center", color="w")
            
            #canvas.fig.colorbar(img, label="Probability of finding a vehicle")

        return canvas, "{}_heatmap".format(key)

    def get_layout_label(self, n_stations):
        if language == "es":
            if n_stations == 1:
                label = "1 estación grande"
            elif n_stations == 4:
                label = "4 estaciones medianas"
            else:
                label = "{} estaciones pequeñas".format(n_stations)
        else:
            if n_stations == 1:
                label ="1 big station"
            elif n_stations == 4:
                label ="4 medium stations"
            else:
                label="{} small stations".format(n_stations)
        return label
    def create_canvas_per_evd(self, i, key, mean, std):

        evd = self.evd_index[i]
        canvas = MplCanvas()
        canvas.axes = canvas.fig.add_subplot(111)

        # For each traffic density, plot each row
        for j in range(self.shape[1]):
            layout = self.layout_index[j]
            n_stations = int(self.__dict__["n_stations_mean"][i, j,0])
            st_label = self.get_layout_label(n_stations)
            y, yerr = mean[i, j, :], std[i, j, :]
     
            x = self.matrix_total_vehicles[i, j, :]

            canvas.axes.errorbar(x, y, yerr=yerr, linewidth=2,marker="o", markersize=3, ls="solid",label=st_label)
            
                
        # Set the axis
        canvas.axes.set_xlabel(params.global_x_label[language])
        if key in self.traffic:
            canvas.axes.set_ylabel(params.global_y_label[language]['traffic'])
        elif key == 'mobility':
            canvas.axes.set_ylabel("Movilidad media (km/h)")
        elif key in self.velocities:
            canvas.axes.set_ylabel(params.global_y_label[language]['velocities'])
        elif key in self.stations:
            label, y_label = params.global_y_label[language]['stations']
            canvas.axes.plot(x, np.repeat(1, len(y)), color='k', linestyle="--", label=label)
            canvas.axes.set_ylabel(y_label)
            
        elif key == 'elapsed':
            canvas.axes.set_ylabel("Time elapsed per repetition (minutes/vehicle)")

        # Set the suptitle
        canvas.figure.suptitle(params.global_suptitles[language][key].format(evd))
        # Set the legend
        canvas.axes.legend(fontsize=8)

        return canvas, key+"_"+str(evd)
