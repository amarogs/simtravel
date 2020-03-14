from src.analysis.analysis import SimulationAnalysis, GlobalAnalysis
from src.visual.visualOGL import VisualRepresentation
from src.simulator.simulation import Simulation
from src.models.cities import SquareCity
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import QApplication, QLabel, QWidget, QMainWindow
from src.app.animation import VisualRepresentation
import sys

QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)  # enable highdpi scaling



# Create a Simulation
simulation = Simulation(0.3, 0.2, "central")
# Set the physical units
simulation.set_simulation_units(speed=10, cell_length=5, simulation_speed=1, battery=0.1, cs_power=7)
# Set the battery distribution
simulation.set_battery_distribution(lower=0.2, std=0.25)
simulation.set_idle_distribution(upper=2, lower=1, std=0.25)
# Create the city
simulation.create_city(SquareCity, RB_LENGTH=6, AV_LENGTH=4*15, INTERSEC_LENGTH=3, SCALE=2) 
# Place the stations around the city
simulation.stations_placement(min_plugs_per_station=2, min_num_stations=10)
# And finally create a simulator
simulation.create_simulator()

# Create the application.
app = QApplication(sys.argv)
window = QWidget()
window.setMinimumHeight(500)
window.setMinimumWidth(500)

layout = QtWidgets.QGridLayout()
start = QtWidgets.QPushButton("Start simulation")
layout.addWidget(start, 0, 0,)




# Now, create a visual representation of the simulatoin and add the vehicles.
vs = VisualRepresentation(simulation.SIZE, 70, simulation.city_matrix, window, hdpi=True)
vs.add_vehicles(simulation.vehicles)

layout.addWidget(vs, 1, 1, 4, 4)
def run_simulation():
    # Finally run the simulation with visual object.
    simulation.run(total_time=1, measure_period=0, repetitions=2, visual=vs)


start.clicked.connect(run_simulation)

window.setLayout(layout)

window.show()
sys.exit(app.exec_())
# http: // trevorius.com/scrapbook/uncategorized/part-1-drawing-with-pyopengl-using-moden-opengl-buffers/
