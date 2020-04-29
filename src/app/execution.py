import copy
import os
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtGui import QKeySequence

from PyQt5.QtWidgets import *
from src.simulator.simulation import Simulation
from src.models.cities import SquareCity
from src.app.animation import VisualizationWindow
from src.app.visual_analysis  import LiveAnalysisPyG as LiveAnalysisWindow
from src.app.param import LY_ENG_TO_SP, LY_SP_TO_ENG


class ExecutionVisualizationForm(QWidget):
    def __init__(self, params, visualization_window, parent=None, flags=QtCore.Qt.WindowFlags()):
        super(ExecutionVisualizationForm, self).__init__(parent=parent, flags=flags)
        
        # global parameters to be used
        self.params_text = params
        self.combo_widgets = {}

        # Visualizatoin related widgets
        self.simulation_directory = None
        self.visualization_window = visualization_window
        self.fps = QSpinBox()
        self.fps.valueChanged.connect(self.fps_change)
        self.analyse_button = QPushButton("Analizar")
        self.analyse_button.clicked.connect(self.on_click_analyse_button)
        

        # Button tool on the bottom part of the main window
        self.button_tool = QWidget()
        self.button_layout = QHBoxLayout()
        self.button_layout.setSizeConstraint(QLayout.SetMinimumSize)

        self.execute = QPushButton("Ejecutar")
        self.execute.clicked.connect(self.on_click_execute_button)
        
        self.pause = QPushButton("Parar")
        self.pause.hide()
        self.pause.clicked.connect(self.on_click_pause_button)

        self.resume = QPushButton("Reanudar")
        self.resume.hide()
        self.resume.clicked.connect(self.on_click_resume_button)

        self.terminate = QPushButton("Terminar")
        self.terminate.hide()
        self.terminate.clicked.connect(self.on_click_terminate_button)

        
        self.button_layout.addWidget(self.execute)
        self.button_layout.addWidget(self.resume)
        self.button_layout.addWidget(self.pause)
        self.button_layout.addWidget(self.terminate)

        self.button_tool.setLayout(self.button_layout)

        # Main content is the form area to choose the simulation to run.
        self.main_content = QWidget()

        # Create the layout of the view
        self.layout = QVBoxLayout()
        self.layout.setSizeConstraint(QLayout.SetMinimumSize)
        self.layout.addWidget(self.main_content)
        self.layout.addWidget(self.button_tool)

        self.setLayout(self.layout)

    def update_values(self, parameters):
        self.params_text = parameters
        new_main_content = self.create_main_content()
        self.layout.replaceWidget(self.main_content, new_main_content, QtCore.Qt.FindChildrenRecursively)
        self.main_content.setParent(None)

        self.main_content = new_main_content
        

    def create_simulation(self):
        ev = str(self.combo_widgets['EV_DENSITY_VALUES'].currentText())
        tf = str(self.combo_widgets['TF_DENSITY_VALUES'].currentText())
        ly = LY_SP_TO_ENG[str(self.combo_widgets['ST_LAYOUT_VALUES'].currentText())]
        path = self.params_text["PATH"]
        self.simulation_directory =  os.path.join(path, "results","{}#{}#{}.hdf5".format(ev, tf, ly))
        # Create the simulation object
        simulation = Simulation(float(ev), float(tf), ly,path)
        # Set the simulation units.
        simulation.set_simulation_units(speed=self.params_text['SPEED'], cell_length=self.params_text['CELL_LENGTH'],
                                        simulation_speed=self.params_text['SIMULATION_SPEED'],
                                        battery=self.params_text['BATTERY'], cs_power=self.params_text['CS_POWER'], autonomy=self.params_text['AUTONOMY'])
        # Set the battery and idle distribution
        simulation.set_battery_distribution(lower=self.params_text['BATTERY_THRESHOLD'],
                                            std=self.params_text['BATTERY_STD'])
        simulation.set_idle_distribution(upper=self.params_text['IDLE_UPPER'],
                                        lower=self.params_text['IDLE_LOWER'], std=self.params_text['IDLE_STD'])
        # Create the city
        simulation.create_city(SquareCity, self.params_text['RB_LENGTH'], self.params_text['AV_LENGTH'], self.params_text['SCALE']) 

        simulation.stations_placement(min_plugs_per_station=self.params_text['MIN_PLUGS_PER_STATION'],
                                    min_num_stations=self.params_text['MIN_D_STATIONS'])
        # Create the simulator
        simulation.create_simulator()

        return simulation

    def on_click_terminate_button(self, all_done=False):
        # Hide the buttons that control the execution
        self.execute.show()
        self.pause.hide()
        self.resume.hide()
        self.terminate.hide()
        self.analyse_button.hide()

        # Stop the execution and close the visualization window
        self.visualization_window.timer.stop()
        if not all_done and self.simulation_directory != None:
            # Destroy the file that was created.
            if os.path.exists(self.simulation_directory):
                os.remove(self.simulation_directory)

        self.visualization_window.close()

    def on_click_pause_button(self):
        self.resume.show()
        self.pause.hide()
        self.visualization_window.timer.stop()

    def on_click_resume_button(self):
        self.pause.show()
        self.resume.hide()
        self.visualization_window.timer.start()

    def simulation_is_over(self):
        """Function called when the simulation has finished executing """
        self.on_click_terminate_button(all_done=True)

    def on_click_execute_button(self):

        # Update the view of the buttons
        self.execute.hide()
        self.pause.show()
        self.terminate.show()

        self.analyse_button.show()

        # Create a new simulation
        self.simulation = self.create_simulation()
        self.simulation.prepare_simulation(self.params_text['TOTAL_TIME'], \
            self.params_text['MEASURE_PERIOD'], self.params_text['REPETITIONS'])

        # Open the visualization window
        self.visualization_window.show()
        self.visualization_window.start_animation(self.simulation, self.simulation_is_over)

        # Start the timer
        self.fps_change()
        self.visualization_window.timer.start()

    def on_click_analyse_button(self):
        self.visualization_window.live_analysis_window = LiveAnalysisWindow(self.simulation, self.visualization_window)
        self.visualization_window.live_analysis_window.show()
    def fps_change(self):
        """Setes the timer of the visualization to the new interval based on the 
        fps count. """

        self.visualization_window.timer.setInterval(int(1000/self.fps.value()))

    def list_of_stations_layout(self):
        """For each layout selected in the parameters file, creates
        a string representing that selection. The new list is stored in 
        the parameters dictionary with the key:  ST_LAYOUT_VALUES"""

        ST_LAYOUT_VALUES = []
        if self.params_text['ST_CENTRAL']:
            ST_LAYOUT_VALUES.append("grande")

        if self.params_text['ST_DISTRIBUTED']:
            ST_LAYOUT_VALUES.append("pequeñas")
        if self.params_text['ST_FOUR']:
            ST_LAYOUT_VALUES.append("medianas")
        self.params_text['ST_LAYOUT_VALUES'] = ST_LAYOUT_VALUES

    def fulfill_combo_widget(self, key):
        combo = QComboBox()
        ordered_values = sorted(self.params_text[key])
        for val in ordered_values:
            combo.addItem(str(val))
        self.combo_widgets[key] = combo
        return combo

    def create_main_content(self):
        main_content = QWidget()
        trafico = QGroupBox("Densidad de tráfico")
        evs = QGroupBox("Densidad de vehículos eléctricos")
        st = QGroupBox("Colocación de las estaciones")
        vs = QGroupBox("Parámetros de la visualización")

        # Fulfill each category
        layout = QFormLayout()
        
        combo = self.fulfill_combo_widget("TF_DENSITY_VALUES")
        layout.addRow(QLabel("Selecciona la densidad de tráfico:"), combo)
        trafico.setLayout(layout)

        layout = QFormLayout()
        combo = self.fulfill_combo_widget("EV_DENSITY_VALUES")
        layout.addRow(QLabel("Selecciona la densidad de EVs:"), combo)
        evs.setLayout(layout)

        layout = QFormLayout()
        self.list_of_stations_layout()
        combo = self.fulfill_combo_widget("ST_LAYOUT_VALUES")
        layout.addRow(QLabel("Selecciona el modelo de colocación de estaciones:"), combo)
        st.setLayout(layout)

        layout = QFormLayout()
        
        self.fps.setValue(24)
        self.fps.setMaximum(10800)
        self.fps.setMinimum(1)
        layout.addRow(QLabel("Selecciona los FPS de la visualización (más frames, más rápido):"), self.fps)
        vs.setLayout(layout)
        
        self.analyse_button.hide()
        # Configure the main_content widget with a layout
        layout = QVBoxLayout()
        layout.addWidget(trafico)
        layout.addWidget(evs)
        layout.addWidget(st)
        layout.addWidget(vs)
        layout.addWidget(self.analyse_button)
        main_content.setLayout(layout)

        return main_content    

    def closeEvent(self, cls):        
        self.on_click_terminate_button()

        return super().closeEvent(cls)