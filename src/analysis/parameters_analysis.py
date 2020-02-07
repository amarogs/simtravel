from src.models.states import States

"""Plot configuration """
FIGSIZE = (8, 6)  # Size of the figure to be produced

STATE_NAMES = {States.TOWARDS_DEST: 'towards destination', States.AT_DEST: 'at destination',
               States.TOWARDS_ST: 'towards station', States.QUEUEING: 'queuing', States.CHARGING: 'recharging', States.NO_BATTERY: 'no battery'}

COLORS = {States.TOWARDS_DEST: 'blue', States.AT_DEST: 'purple', States.TOWARDS_ST: 'red',
          States.QUEUEING: 'orange', States.CHARGING: 'green', States.NO_BATTERY: 'black'}


# To make the graphs look better we can perform a moving average.
WINDOW_SIZE = 201 # This value must be odd
# This is the size of the window of the moving average.

"""RUN configuration """
NUM_PROC = 1  # Number of processors

SHOW = True  # If True shows the plot that are about to be build

"PDF creation per simulation"
# If True creates the individual analysis of each simulation and stores it in a PDF
PDF_INDIVIDUAL = False
# If True the values from individual simulations must be saved and global graphs are created
PLOT_GLOBAL = True

STATES = True
OCCUPATION = True
HEAT_MAP = True
VELOCITIES = True
DISTRIBUTION = True


"PDF creation using global data"
GROUPS = ["seeking", "queueing", "total_time", "mean_speed", "mean_mobility"]
SINGLE = ["seeking", "queueing", "total_time", "mean_speed", "mean_mobility"]
PROPERTY_1 = "EV_DENSITY"
PROPERTY_2 = "LAYOUT"
