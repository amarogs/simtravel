"""Plot configuration """
FIGSIZE = (8,6) #Size of the figure to be produced

STATE_NAMES = {0: 'towards destination', 1: 'at destination',
               2: 'towards station', 3: 'at station', 4: 'recharging', 5: 'no battery'}

COLORS = {0: 'blue', 1: 'purple', 2: 'red',
          3: 'orange', 4: 'green', 5: 'black'}


WINDOW_SIZE = 10 #To make the graphs look better we can perform a moving average.
#This is the size of the window of the moving average.

"""RUN configuration """
NUM_PROC = 1 #Number of processors

SHOW = False #If True shows the plot that are about to be build

"PDF creation per simulation"
PDF_INDIVIDUAL = False  #If True creates the individual analysis of each simulation and stores it in a PDF
PLOT_GLOBAL = True #If True the values from individual simulations must be saved and global graphs are created

STATES = True
OCCUPATION = True
HEAT_MAP = True
VELOCITIES = True
DISTRIBUTION = True


"PDF creation using global data"
GROUPS = ["seeking", "queueing","total_time", "mean_speed", "mean_mobility"]
SINGLE = ["seeking", "queueing", "total_time", "mean_speed", "mean_mobility"]
PROPERTY_1 = "EV_DENSITY"
PROPERTY_2 = "LAYOUT"