from PyQt5 import QtCore

# Diccionario de traducción de staciones:
LY_ENG_TO_SP = {"central":"grande", "distributed":"pequeñas", "four":"medianas"}
LY_SP_TO_ENG = {v:k for (k, v) in LY_ENG_TO_SP.items()}


default_parameters = {'CITY_TYPE': 'square', 'RB_LENGTH': 8, 'AV_LENGTH': 44, 'INTERSEC_LENGTH': 3, \
                    'SCALE': 2, 'MIN_PLUGS_PER_STATION': 2, 'MIN_D_STATIONS': 10, 'SPEED': 10, \
                    'CELL_LENGTH': 5, 'SIMULATION_SPEED': 1, 'BATTERY': 24,'AUTONOMY':135, 'CS_POWER': 7, \
                    'BATTERY_THRESHOLD': 0.25, 'BATTERY_STD': 0.2, 'IDLE_UPPER': 2, 'IDLE_LOWER': 1, \
                    'IDLE_STD': 0.25, 'EV_DENSITY_VALUES': [0.1], 'TF_DENSITY_VALUES': [0.1],\
                    'ST_CENTRAL':0, 'ST_DISTRIBUTED': 1, 'ST_FOUR': 0, 'REPETITIONS': 1, \
                    'TOTAL_TIME': 1, 'MEASURE_PERIOD': 0, 'PATH':QtCore.QDir.homePath()}
