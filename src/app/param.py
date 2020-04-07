from PyQt5.QtWidgets import QSpinBox, QDoubleSpinBox, QLineEdit, QCheckBox
class Param():
    def __init__(self, widget, minimum, single_step, key, label ):
        self.widget = widget
        self.minimum = minimum
        self.single_step = single_step
        self.key = key
        self.label = label

""" City creation parameters"""
roundabout = Param(QSpinBox, 6, 2, "RB_LENGTH", "Tamaño del lado de las rotondas:")
av_segment = Param(QSpinBox, 20, 8, "AV_LENGTH", "Longitud de una avenida")
scale = Param(QSpinBox, 1, 1, "SCALE", "Factor de escala del patrón base:")

plugs_per_station = Param(QSpinBox, 1, 1, "MIN_PLUGS_PER_STATION", "Número mínimo de enchufes por estacion:")
d_stations = Param(QSpinBox, 1,1,"MIN_D_STATIONS", "Número mínimo de estaciones distribuidas: ")

city_creation = [roundabout, av_segment, scale, plugs_per_station, d_stations]


"""Speed parameters """
speed = Param(QSpinBox, 1, 1, "SPEED", "Velocidad media en las calles (km/h):")
cell_length = Param(QSpinBox, 1, 1, "CELL_LENGTH", "Longitud de una celda (m):")
simulation_speed = Param(QSpinBox, 1, 1, "SIMULATION_SPEED", "Velocidad de la simulación (cell/timestep):")

speed_creation = [speed, cell_length,simulation_speed]

"""Battery parameters """
battery_capacity = Param(QSpinBox, 1, 1, "BATTERY", "Capacidad de la batería (kWh):")
station_power = Param(QSpinBox, 1, 1, "CS_POWER", "Potencia de las estaciones (kW):")

battery_creation = [battery_capacity, station_power]

"""Distribución de la batería y el tiempo en espera """
battery_thresh = Param(QDoubleSpinBox, 0.01, 0.01, "BATTERY_THRESHOLD", "Umbral mínimo de batería (tanto por uno):")
battery_std = Param(QDoubleSpinBox, 0.01, 0.01, "BATTERY_STD", "Desviación estándar de la batería (tanto por uno):")
idle_upper = Param(QSpinBox, 1, 1, "IDLE_UPPER", "Máximo tiempo en espera (min):")
idle_lower = Param(QSpinBox, 1, 1, "IDLE_LOWER", "Mínimo tiempo en espera (min):")
idle_std = Param(QDoubleSpinBox, 0.01, 0.01, "IDLE_STD", "Desviación estándar del tiempo en espera (tanto por uno):")

distribution_creation = [battery_thresh,battery_std, idle_upper, idle_lower,idle_std]

"""Configuracion de las simulaciones """
repetitions =Param(QSpinBox, 1, 1, "REPETITIONS", "Número de repeticiones de cada simulación:")
total_time = Param(QSpinBox, 1, 1, "TOTAL_TIME", "Tiempo total de simulación (h):")
measure_period = Param(QSpinBox,0, 1, "MEASURE_PERIOD", "Tiempo entre cada medición del sistema (min):")

sim_configuration_creation = [repetitions, total_time, measure_period]

ev_density = Param(QLineEdit, None, None, "EV_DENSITY_VALUES", "Valores de densidad de EV:")
tf_density = Param(QLineEdit, None, None, "TF_DENSITY_VALUES", "Valores de densidad de tráfico:")

st_central = Param(QCheckBox, None, None, "ST_CENTRAL", "Una estación centrada en una avenida")
st_distributed = Param(QCheckBox, None, None, "ST_DISTRIBUTED", "Pequeñas estaciones en las calles")
st_four = Param(QCheckBox, None, None, "ST_FOUR", "Cuatro estaciones medianas en las avenidas")

instances_configuration_creation = [tf_density, ev_density]
stations_configuration_creation = [st_central, st_distributed, st_four]