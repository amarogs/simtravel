import yaml
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtGui import QKeySequence

from PyQt5.QtWidgets import *

from src.app.form import ParamsCreationForm
from src.app.execution import ExecutionVisualizationForm
from src.app.animation import VisualizationWindow
from src.app.visual_analysis import SingleAnalysis, GlobalAnalysisForm

class SimtravelMainWindow(QMainWindow):
    def __init__(self, parent=None, flags=QtCore.Qt.WindowFlags()):
        super().__init__(parent=parent, flags=flags)


        default_parameters = {'CITY_TYPE': 'square', 'RB_LENGTH': 8, 'AV_LENGTH': 44, 'INTERSEC_LENGTH': 3, \
                            'SCALE': 2, 'MIN_PLUGS_PER_STATION': 2, 'MIN_D_STATIONS': 10, 'SPEED': 10, \
                            'CELL_LENGTH': 5, 'SIMULATION_SPEED': 1, 'BATTERY': 24,'AUTONOMY':135, 'CS_POWER': 7, \
                            'BATTERY_THRESHOLD': 0.25, 'BATTERY_STD': 0.2, 'IDLE_UPPER': 2, 'IDLE_LOWER': 1, \
                            'IDLE_STD': 0.25, 'EV_DENSITY_VALUES': [0.1], 'TF_DENSITY_VALUES': [0.3], \
                            'WIDTH': 700, 'HEIGHT': 700, 'ST_CENTRAL':0, 'ST_DISTRIBUTED': 1, 'ST_FOUR': 0, \
                            'DELAY': 0, 'REPETITIONS': 1, 'TOTAL_TIME': 1, 'MEASURE_PERIOD': 0, 'PATH':QtCore.QDir.homePath()}

        self.parameters = default_parameters

        # Configure the main window
        self.setWindowTitle("SIMTRAVEL - Simulador de tráfico urbano")
        self.setMinimumHeight(600)
        self.setMinimumWidth(600)

        # Create the widgets that the stack will hold.
        self.stack = QStackedWidget()
        self.welcome = QWidget(flags=flags)
        layout = QHBoxLayout()
        msg = """
                <br><br>
                <h1>Bienvenido</h1>
                
                <p>
                <br>(1) Crear nuevos parámetros de simulación o cargar desde un archivo.
                <br>(2) Los parámetros creados o modificados puede ser guardados como archivo.
                <br>(2) Ejecutar la simulación con los parámetros cargados.
                <br>(3) Analizar los resultados obtenido o de otra localización.
                </p>
                <br>
                <a href=https://github.com/amarogs/simtravel>Código fuente <a/>
                 """
        msg_label =QLabel(msg)
        # msg_label.setAlignment(QtCore.Qt.AlignCenter)

        layout.addWidget(msg_label)
        self.welcome.setLayout(layout)
        self.parameters_creation_form = ParamsCreationForm(self.parameters, self.create_new_welcome, flags=flags)
        self.execution_visualization_form = ExecutionVisualizationForm(self.parameters, VisualizationWindow(), flags=flags)
        self.individual_analysis_form = SingleAnalysis(self.parameters['PATH'], flags=flags)
        self.global_analysis_form = GlobalAnalysisForm(self.parameters['PATH'], flags=flags)

        self.stack.addWidget(self.welcome)
        self.stack.addWidget(self.parameters_creation_form)
        self.stack.addWidget(self.execution_visualization_form)
        self.stack.addWidget(self.individual_analysis_form)
        self.stack.addWidget(self.global_analysis_form)

        # Main content of the widget is the stack of forms and the welcome page wich is the first 
        # widget to be displayed.
        self.setCentralWidget(self.stack)


        # Create the top menu of the main window.
        self.top_menu = self.menuBar()
        # Parameters
        self.parameters_menu = self.top_menu.addMenu("Parámetros")

        self.load_params = QAction("Cargar")
        self.load_params.triggered.connect(self.open_file)

        self.create_params = QAction("Crear/Editar")
        self.create_params.triggered.connect(self.create_parameters)

        self.save_params = QAction("Guardar como ")
        self.save_params.triggered.connect(self.save_file_as)

        self.parameters_menu.addAction(self.create_params)
        self.parameters_menu.addAction(self.load_params)
        self.parameters_menu.addAction(self.save_params)


        # Execution
        self.execution_menu = self.top_menu.addMenu("Ejecución")
        self.configure_execution = QAction("Ejecutar con visualización")
        self.configure_execution.triggered.connect(self.create_new_execution_visualization)
        self.execution_menu.addAction(self.configure_execution)


        # Analysis
        self.analysis_menu = self.top_menu.addMenu("Análisis")
        self.individual_analysis = QAction("Nuevo análisis individual")
        self.individual_analysis.triggered.connect(self.create_new_individual_analysis)
        self.analysis_menu.addAction(self.individual_analysis)
        self.global_analysis = QAction("Nuevo análisis grupal")
        self.global_analysis.triggered.connect(self.create_new_global_analysis)
        self.analysis_menu.addAction(self.global_analysis)


    def open_file(self):
        """Opens a yaml file and saves the parameters into the parameters variable. """
        
        path= QFileDialog.getOpenFileName(self, "Abrir archivo de configuración")[0]
        if path:
            with open(path, "r") as f:
                self.parameters = yaml.load(f, Loader=yaml.FullLoader)
            self.parameters_creation_form.current_view = None
            self.create_params.trigger()

    def save_file_as(self):
        """Saves the current parameters dictionary as a yaml parameter file. """
        
        path = QFileDialog.getSaveFileName(self, "Guardar parámetros como")[0]
        if path:
            with open(path+".yaml", "w") as f:
                yaml.dump(self.parameters, f, sort_keys=False)


    def create_parameters(self):
        """Creates a new form to build a parameter file.
        Updates the stack to point to this new widget. """
        
        if self.parameters_creation_form.current_view == None:
            self.parameters_creation_form.initialize_widget(self.parameters)

        self.stack.setCurrentWidget(self.parameters_creation_form)

    def create_new_execution_visualization(self):
        """Creates a new execution form with the ability to show visually the simulation.
        Updates the stack to point to this new widget """

        self.execution_visualization_form.update_values(self.parameters)
        self.stack.setCurrentWidget(self.execution_visualization_form)

    def create_new_individual_analysis(self):
        """Creates a new form to select the individual analysis of the simulations. 
        Updates the stack to point to this new widget. """
        self.individual_analysis_form.update_values(self.parameters['PATH'])
        self.stack.setCurrentWidget(self.individual_analysis_form)

    def create_new_global_analysis(self):
        """Creates a new form to select the global analysis of the simulations. 
        Updates the stack to point to this new widget. """
        self.global_analysis_form.update_values(self.parameters['PATH'])
        self.stack.setCurrentWidget(self.global_analysis_form)

    def create_new_welcome(self):
        """Sets the stack to point to the welcome widget. """
        self.stack.setCurrentWidget(self.welcome)
    def closeEvent(self,cls):
        
        
        self.parameters_creation_form.close()
        self.execution_visualization_form.close() 
        self.individual_analysis_form.close()
        self.welcome.close()

        return super().closeEvent(cls)

