"""CITY PARAMETERS"""
CITY_TYPE = "square"
RB_LENGTH=6 # Is the length of the side of the roundabout. Each side has at least 4(avenues)+2 cells.
AV_LENGTH=4*9 # Is the legnth of the avenue from one roundabout to the next roundabout.
INTERSEC_LENGTH=3 # Is the length of the side of the intersection
SCALE=2 # Is the 2D scale of the city.

"""STATIONS PARAMETERS """
MIN_PLUGS_PER_STATION = 2 #Minimum number of outlets that each station must have
MIN_D_STATIONS = 36 #Minimum number of stations that must be placed when choosing the distributed layout

"""PHYSICAL UNITS """
SPEED = 10 # km/h
CELL_LENGTH = 5 # meters
SIMULATION_SPEED = 1 #cell/tstep
BATTERY = 24 #kWh
CS_POWER = 7 #kW

"""BATTERY DISTRIBUTION """
BATTERY_THRESHOLD = 0.25 # lower limit of the charge
BATTERY_STD = 0.2 # percentage of deviation from the mean.

"""IDLE DISTRIBUTION """
IDLE_UPPER = 10 # minutes
IDLE_LOWER = 2 # minutes
IDLE_STD = 0.25 #percentage of deviation from the mean


"""VALUES TO TRY """
#For each combination of ev_density, tf_density and st_layout we run a different simulation
EV_DENSITY_VALUES = [0.1]#, 0.4, 1]
TF_DENSITY_VALUES = [0.1, 0.3, 0.5]
ST_LAYOUT_VALUES = ["central"]#, "distributed", "four"]

"""GRAPHICS PARAMETERS """
WIDTH = 700 #Window width
HEIGHT = 700 #Window height
DELAY = 0 #Number of ms between different frames

"""GENERAL PARAMETERS """
REPETITIONS = 2 #Number of times each simulation is run
TOTAL_TIME = 5  # Number of hours to simulate
MEASURE_PERIOD = 0 # Number of minutes between two consecutive snapshots of the system.


