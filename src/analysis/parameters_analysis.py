from src.models.states import States

"""Plot configuration """
FIGSIZE = (6.4,4.8 )  # Size of the figure to be produced
LANGUAGE = "es"
stations_ly = {"central":"grande", "distributed":"pequeñas", "four":"medianas"}

STATE_NAMES_ENG = {States.TOWARDS_DEST: 'towards destination', States.AT_DEST: 'at destination',
               States.TOWARDS_ST: 'towards station', States.QUEUEING: 'queuing', States.CHARGING: 'recharging', States.NO_BATTERY: 'no battery'}
STATE_NAMES_ES = {States.TOWARDS_DEST: 'hacia destino', States.AT_DEST: 'en destino',
               States.TOWARDS_ST: 'hacia estacion', States.QUEUEING: 'en cola', States.CHARGING: 'recargando', States.NO_BATTERY: 'sin batería'}
STATE_NAMES = {"eng":STATE_NAMES_ENG, "es":STATE_NAMES_ES}

COLORS = {States.TOWARDS_DEST: 'blue', States.AT_DEST: 'purple', States.TOWARDS_ST: 'red',
          States.QUEUEING: 'orange', States.CHARGING: 'green', States.NO_BATTERY: 'black'}
COLORS_PG = {States.TOWARDS_DEST: '#321BD6', States.AT_DEST: '#AE1BD6', States.TOWARDS_ST: '#D61B1B',
          States.QUEUEING: '#D66D1B', States.CHARGING: '#33FF5E', States.NO_BATTERY: '#000000'}



# Labels and artists for the graphs in two languages english and spanish

lb_evolution = {"eng": "Evolution (minutes)", "es":"Evolución (minutos)"}
lb_states = {"eng":"EV states" , "es": "Estados de los VE"}
lb_states_y = {"eng": "Number of EVs at each state", "es": "Número de VE en cada estado"}


lb_occupation = {"eng":"Station at {}", "es": "Estación en {}"}

lb_occupation_legend = {"eng":"Occupation", "es":"Ocupación"}
lb_occupation_capacity = {"eng":"Capacity", "es":"Capacidad"}
lb_occupation_y ={"eng":"Number of EVs", "es":"Número de VE"}

lb_heat = {"eng":"Snapshot at {}/{} of simulation" , "es":"Instantánea al {}/{} de la simulación"} 
lb_heat_bar = {"eng": "Probability of finding a vehicle", "es": "Probabilidad de encontrar un vehículo"}


lb_speed = {"eng": "Mean speed (km/h)", "es": "Velocidad media (km/h)"}
lb_mobility = {"eng": "Mean mobility (km/h)", "es":"Movilidad media (km/h)"}



# Labels and artist for the GLOBAL graphs.
eng_suptitles = {'seeking': 'Mean time spent seeking. EV rate = {}',
                    'queueing': 'Mean time spent queueing. EV rate = {}',
                    'total': "Total time spent recharging. EV rate = {} ",
                    'elapsed': "Time elapsed", 'speed': "Mean speed. EV rate = {}",
                    'mobility': "Mean mobility. EV rate = {} ", 
                    'occupation': "Mean stations use. EV rate = {}"}

es_suptitles = {'seeking': 'Tiempo medio invertido buscando. Proporción de VE = {}',
                    'queueing': 'Tiempo medio invertido esperando. Proporción de VE = {}',
                    'total': "Tiempo medio total invertido en la recarga. Proporción de VE = {} ",
                    'elapsed': "Time elapsed", 'speed': "Velocidad media. Proporción de VE = {}",
                    'mobility': "Movilidad media. Proporción de VE = {} ", 
                    'occupation': "Utilización media de las estaciones. Proporción de VE = {}"}

global_suptitles = {"eng":eng_suptitles , "es":es_suptitles}
global_x_label = {"eng":"Total number of vehicles" , "es":"Número total de vehículos"}

eng_y_label = {'traffic': "Time (minutes)", 'velocities':"Mean speed (km/h)", "stations":["Optimal occupation", "Number of EV per electric charger (EV/charger) "]}
es_y_label = {'traffic':"Tiempo (minutos)", 'velocities':"Velocidad media (km/h)", "stations":["Ocupación óptima", "Número de VE por cargador eléctrico (VE/cargador)"]}
global_y_label = {"eng":eng_y_label, "es":es_y_label}
# To make the graphs look better we can perform a moving average.
WINDOW_SIZE = 201 # This value must be odd
N_BINS = 200
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

