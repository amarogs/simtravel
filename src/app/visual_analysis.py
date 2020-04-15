import copy
import os
import numpy as np

from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtGui import QKeySequence
from PyQt5.QtWidgets import *
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT
import pyqtgraph as pg

from src.analysis.analysis import SimulationAnalysis, GraphFunctions, GlobalAnalysis
from src.models.states import States
import src.analysis.parameters_analysis as params

class LiveAnalysisPyG(QMainWindow):
    def __init__(self, simulation, main_window, parent=None, flags=QtCore.Qt.WindowFlags()):
        super().__init__(parent=parent, flags=flags)

        # Store a reference to the current simulation
        self.main_window = main_window
        self.simulation = simulation
        
        # Create the grapher
        self.grapher = GraphFunctions(simulation.sim_name, simulation.units, 1, simulation.DELTA_TSTEPS, 1)
        
        # Retrieve the initial data from the metrics object
        states_mean = self.simulation.metrics.states_evolution
        states_std = {k:np.repeat(0, len(states_mean[k])) for k in states_mean}
        
        self.keys = list(states_mean.keys())

        x = self.grapher.steps_to_minutes(len(states_mean[self.keys[0]]))

        # Create the plot widget
        self.graphWidget = pg.PlotWidget()
        self.setCentralWidget(self.graphWidget)


        # Give styling to the graphWidget
        self.graphWidget.setBackground("w")
        self.graphWidget.setTitle("Evolución de estados para EVs")
        self.graphWidget.setLabel('left', 'Número de vehículos')
        self.graphWidget.setLabel("bottom", "Tiempo simulación (minutos)")
        self.graphWidget.addLegend()

        # Plot the data
        self.lines = {}
        for s in States:
            pen = pg.mkPen(color=params.COLORS_PG[s], width=10, style=QtCore.Qt.SolidLine)
            y = states_mean[s]
            line = self.graphWidget.plot(x, y, name=params.STATE_NAMES[s], pen=pen)
            self.lines[s] = line

    def update_values(self):
        len_data = len(self.simulation.metrics.states_evolution[self.keys[0]])
        x = self.grapher.steps_to_minutes(len_data)
        y_data = self.simulation.metrics.states_evolution
        for s in States:
            self.lines[s].setData(x,y_data[s])

    def closeEvent(self,cls):
        
        self.main_window.live_analysis_window = None
        
        return super().closeEvent(cls)
class LiveAnalysisWindow(QMainWindow):
    def __init__(self, simulation, parent=None, flags=QtCore.Qt.WindowFlags()):
        super().__init__(parent=parent, flags=flags)
        self.simulation = simulation
        # Create the grapher
        self.grapher = GraphFunctions(simulation.sim_name, simulation.units, 1, simulation.DELTA_TSTEPS, 1)
        
        # Retrieve the initial data from the metrics object
        states_mean = self.simulation.metrics.states_evolution
        states_std = {k:np.repeat(0, len(states_mean[k])) for k in states_mean}
        
        self.keys = list(states_mean.keys())

        x = self.grapher.steps_to_minutes(len(states_mean[self.keys[0]]))

        # Plot the data into a canvas
        self.states_graph = self.grapher.graph_states_evolution_live(states_mean, x, live=True)
        
        # And set the graph as the main widget.
        self.setCentralWidget(self.states_graph)

    def update_values(self):
        len_data = len(self.simulation.metrics.states_evolution[self.keys[0]])
        self.grapher.update_states_canvas(self.states_graph, len_data, self.simulation.metrics.states_evolution)
        self.states_graph.draw()
        

class AnalysisWindow(QMainWindow):
    def __init__(self,ev, tf, ly, attributes, non_individual=False, parent=None, flags=QtCore.Qt.WindowFlags()):
        super(AnalysisWindow, self).__init__(parent=parent, flags=flags)
        if non_individual:
            title = "Análisis global de distintas simulaciones"
        else:
            title = "Análisis para Densidad EV={}, Densidad TF={}, Layout={}".format(ev, tf, ly)

        self.setWindowTitle(title)
        # Create the analysis and set up the gallery
        if non_individual:
            
            all_sim_analysis = [SimulationAnalysis(*attr) for attr in attributes]
            # Create a global analysis object and feed it with the simulations.
            g_analysis = GlobalAnalysis(attributes, 'seeking', 'queueing','total', 'speed','mobility', 'elapsed')
            g_analysis.load_matrices(all_sim_analysis)
            g_analysis.load_single_attribute(all_sim_analysis, 'TOTAL_VEHICLES')
            g_analysis.compute_all()
            self.sim_analysis = g_analysis
        else:
            self.sim_analysis = SimulationAnalysis(*attributes)

        self.canvas_index = 0
        
        # Create the gallery with a vertical layout and a stack as the main widget.
        gallery = QWidget()
        layout = QVBoxLayout()
        self.current_canvas = QStackedWidget()
        
        button_row = QWidget()
        button_layout = QHBoxLayout()

        self.next_button = QPushButton("Siguiente")
        self.previous_button = QPushButton("Anterior")
        self.next_button.clicked.connect(self.on_click_next_gallery)
        self.previous_button.clicked.connect(self.on_click_previous_gallery)
        self.previous_button.hide()
        button_layout.addWidget(self.previous_button)
        button_layout.addWidget(self.next_button)
        button_row.setLayout(button_layout)


        layout.addWidget(self.current_canvas)
        layout.addWidget(button_row)
  
        gallery.setLayout(layout)

        # Create the first canvas.
        self.show_current_canvas()

        # Set the gallery widget as the central widget of this window.
        self.setCentralWidget(gallery)

    def on_click_next_gallery(self):
        
        self.canvas_index += 1
        self.show_current_canvas()
        
        if self.canvas_index == self.sim_analysis.total_plots - 1:
            self.next_button.hide()
            self.previous_button.show()
        else:
            self.next_button.show()
            self.previous_button.show()    
        
    def on_click_previous_gallery(self):
        self.canvas_index -= 1
        self.show_current_canvas()

        if self.canvas_index == 0:
            self.previous_button.hide()
            self.next_button.show()
        else:
            self.previous_button.show()
            self.next_button.show()
    def show_current_canvas(self):
        """Given the current canvas index, displays this canvas onto the stack.
        If this canvas has already been computed and is already in the stack, it just
        set it as the current widget. """
        
        if self.current_canvas.widget(self.canvas_index) == None:
            # Create a new widget and store it in the stack
            content = QWidget()
            layout = QVBoxLayout()

            canvas = self.sim_analysis.get_canvas(self.canvas_index)
            canvas.setParent(content)
            toolbar = NavigationToolbar2QT(canvas,content)

            layout.addWidget(toolbar)
            layout.addWidget(canvas)
            content.setLayout(layout)
            
            # Store the widget in the stack
            self.current_canvas.addWidget(content)
            self.current_canvas.setCurrentWidget(content)
        else:
            # The canvas already exists
            self.current_canvas.setCurrentIndex(self.canvas_index)
        


class SingleAnalysis(QWidget):
    def __init__(self, BASEDIR_PATH, parent=None, flags=QtCore.Qt.WindowFlags()):
        super(SingleAnalysis, self).__init__(parent=parent, flags=flags)
        self.BASEDIR_PATH = BASEDIR_PATH
        self.combo_widgets = {}
        self.attributes_by_filename = {}
        

        # Create the layout to visualize this menu
        self.selection_form = QWidget()


        self.layout = QVBoxLayout()
        self.layout.addWidget(self.selection_form)
        
        self.setLayout(self.layout)

    def update_values(self, BASEDIR_PATH):
        self.BASEDIR_PATH = BASEDIR_PATH
        new_selection_form = self.create_selection_form()
        
        self.layout.replaceWidget(self.selection_form,new_selection_form, QtCore.Qt.FindChildrenRecursively)
        self.selection_form.setParent(None)
        self.selection_form = new_selection_form
    
    def read_path(self):
        """Given a path were the HDF5 files from simulations are stored, 
        returns a tuple with the attributes needed for the object SimulationAnalysis
        to be built.  
        EV_DEN, TF_DEN, ST_LAYOUT, BASEDIR_PATH, filepath """
        path = os.path.join(self.BASEDIR_PATH, "results")
        
        

        self.attributes_by_filename, self.ev_values_per_tf, self.st_values_per_tf_ev  = {}, {}, {}

        ev_den, tf_den, st_layout = [], [], []
        if not os.path.exists(path):
            return

        filepath = [f for f in os.listdir(path) if f[-5:] == ".hdf5"]
        for f in filepath:
       
            config = f[0:-5].split("#")
            # Retrieve the simulation attribute from the filename.
            ev, tf, st = config[0], config[1], config[2]

            # Order the data forming the different combinations
            if tf not in self.ev_values_per_tf:
                self.ev_values_per_tf[tf] = set()

            ev_tf_key = tf + "#" + ev
            if ev_tf_key not in self.st_values_per_tf_ev:
                self.st_values_per_tf_ev[ev_tf_key] = set()
            
            self.ev_values_per_tf[tf].add(ev)
            self.st_values_per_tf_ev[ev_tf_key].add(st)

            ev_den.append(ev)
            tf_den.append(tf)
            st_layout.append(st)

            # Complete the attribute tuple for the SimulationAnalysis object.
            config.append(self.BASEDIR_PATH)
            config.append(os.path.join(path,  str(f)))
            self.attributes_by_filename[f[0:-5]] = tuple(config)
            

    def on_change_tf_combo(self):
        """Clears the combo boxes for selecting EV and ST. Sets the new values on EV. """
        
        tf = self.combo_widgets['TF_DENSITY_VALUES'].currentText()
        
        self.combo_widgets['EV_DENSITY_VALUES'].clear()
        self.combo_widgets['ST_LAYOUT_VALUES'].clear()

        if tf != "":
            self.combo_widgets['EV_DENSITY_VALUES'].addItems(sorted(self.ev_values_per_tf[tf]))

    def on_change_ev_combo(self):

        tf = self.combo_widgets['TF_DENSITY_VALUES'].currentText()
        ev = self.combo_widgets['EV_DENSITY_VALUES'].currentText()

        self.combo_widgets['ST_LAYOUT_VALUES'].clear()
        if tf != "" and ev != "":
            self.combo_widgets['ST_LAYOUT_VALUES'].addItems(sorted(self.st_values_per_tf_ev[tf+"#"+ev]))
   
    def fulfill_combo_widget(self, key, values):
        combo = QComboBox()
        ordered_values = set(values)
        for val in sorted(ordered_values):
            combo.addItem(str(val))
        self.combo_widgets[key] = combo
        return combo
    
    def on_click_button_change_path(self):
        """Selects a new path to read the results """
        path = QFileDialog.getExistingDirectory(caption="Seleccionar directorio de resultados")
        
        if path:
            self.update_values(path)
            
        return 
    
    def get_selected_simulation(self):
        """Based on the values of the combo widgets, returns ev, tf, ly.
        If any of the combo is not selected, then returns None. """
        ev =  self.combo_widgets['EV_DENSITY_VALUES'].currentText()
        tf =  self.combo_widgets['TF_DENSITY_VALUES'].currentText()
        ly =  self.combo_widgets['ST_LAYOUT_VALUES'].currentText()
        if any([x=="" for x in [ev, tf, ly]]):
            return
        else:
            return ev, tf, ly

    def on_click_analyze(self):
        params = self.get_selected_simulation()
        if params:
            ev, tf, ly = params
            filename = "{}#{}#{}".format(ev, tf, ly)

            # Create a analysis of the simulation
            self.sim_analysis = SimulationAnalysis(*self.attributes_by_filename[filename])

            # Add the window as an attribute so that the window stays on the screen.
            window_name = "WINDOW_{}_{}_{}".format(ev, tf, ly)
            self.__dict__[window_name] = AnalysisWindow(ev, tf, ly, self.attributes_by_filename[filename])
            self.__dict__[window_name].show()


    def on_click_report(self):
        params = self.get_selected_simulation()
        if params:
            ev, tf, ly = params
            filename = "{}#{}#{}".format(ev, tf, ly)

            # Create a analysis of the simulation
            sim_analysis = SimulationAnalysis(*self.attributes_by_filename[filename])
            # Generate the report
            sim_analysis.generate_report()
            
    def create_selection_form(self):
        selection_form = QGroupBox("Selecciona la simulación")

        layout = QFormLayout()
        layout.setSizeConstraint(QLayout.SetMinimumSize)

        # Select the BASEDIR_PATH where the simulations results are

        layout.addRow(QLabel("Seleccione el directorio donde se encuentran la carpeta de resultados"))
        if self.BASEDIR_PATH== ".":
            self.BASEDIR_PATH = QtCore.QDir.currentPath()
            
        self.current_directory_label = QLabel("Directorio actual: " + self.BASEDIR_PATH)
        layout.addRow(self.current_directory_label)
        button_change_path = QPushButton("Seleccionar nuevo directorio")
        button_change_path.clicked.connect(self.on_click_button_change_path)
        layout.addRow(button_change_path)

        # Create three combo boxes that select the simulation based on the files stored in BASEDIR_PATH.
        layout.addRow(QLabel("Selecciona la simulación: "))
        selectors = QWidget()
        selectors_layout = QGridLayout()

        # Read the different documents inside the path
        self.read_path()

        combo = self.fulfill_combo_widget("TF_DENSITY_VALUES", self.ev_values_per_tf.keys())
        combo.currentTextChanged.connect(self.on_change_tf_combo)
        selectors_layout.addWidget(QLabel("Densidad de tráfico: "), 0,0)
        selectors_layout.addWidget(combo, 1, 0) 
        

        combo = self.fulfill_combo_widget("EV_DENSITY_VALUES", [])
        combo.currentTextChanged.connect(self.on_change_ev_combo)
        selectors_layout.addWidget(QLabel("Densidad de EV: "), 0, 3)
        selectors_layout.addWidget(combo, 1, 3)



        combo = self.fulfill_combo_widget("ST_LAYOUT_VALUES", [])
        selectors_layout.addWidget(QLabel("Colocación de estaciones: "), 0, 6)
        selectors_layout.addWidget(combo, 1, 6)

        self.on_change_tf_combo()
        self.on_change_ev_combo()
        # Add the selector having the three combo boxes to the form layout.
        selectors.setLayout(selectors_layout)
        layout.addRow(selectors)       

        # Add a button to analize the simulation selected.
        self.analyze = QPushButton("Mostrar análisis visual")
        self.analyze.clicked.connect(self.on_click_analyze)
        layout.addRow(self.analyze)
        
        self.report = QPushButton("Guardar informe PDF")
        self.report.clicked.connect(self.on_click_report)
        layout.addRow(self.report)
        # Finally set the layout of the top-form for selecting the simulation
        selection_form.setLayout(layout)

        return selection_form

    def closeEvent(self, cls):
       
        for key, window in self.__dict__.items():
            if key.startswith("WINDOW"):
                window.close()
        return super().closeEvent(cls)


class GlobalAnalysisForm(SingleAnalysis):
    def __init__(self, BASEDIR_PATH, parent=None, flags=QtCore.Qt.WindowFlags()):
        super().__init__(BASEDIR_PATH, parent=parent, flags=flags)
    
    def on_click_analyze(self, report=False):
        """Create a global analysis of the results folder. """
        # Read the names of the files and extract their basic info.
        attrs = list(self.attributes_by_filename.values())
        # Create and individual simulation that reads the HDF5 files

        if report:
            all_sim_analysis = [SimulationAnalysis(*attr) for attr in attrs]
            # Create a global analysis object and feed it with the simulations.
            g_analysis = GlobalAnalysis(attrs, 'seeking', 'queueing','total', 'speed','mobility', 'elapsed')
            g_analysis.load_matrices(all_sim_analysis)
            g_analysis.load_single_attribute(all_sim_analysis, 'TOTAL_VEHICLES')
            # Create the report.
            g_analysis.create_report()
        else:
            # Add the window as an attribute so that the window stays on the screen.
            window_name = "WINDOW_{}".format(self.BASEDIR_PATH)
            self.__dict__[window_name] = AnalysisWindow(None, None, None, attrs, non_individual=True)
            self.__dict__[window_name].show()

    def on_click_report(self):
        self.on_click_analyze(report=True)
    def create_selection_form(self):
        selection_form = QGroupBox("Selección directorio resultados")

        layout = QFormLayout()
        layout.setSizeConstraint(QLayout.SetMinimumSize)

        # Select the BASEDIR_PATH where the simulations results are

        layout.addRow(QLabel("Seleccione el directorio donde se encuentran la carpeta de resultados"))
        if self.BASEDIR_PATH== ".":
            self.BASEDIR_PATH = QtCore.QDir.currentPath()
            
        self.current_directory_label = QLabel("Directorio actual: " + self.BASEDIR_PATH)
        layout.addRow(self.current_directory_label)
        button_change_path = QPushButton("Seleccionar nuevo directorio")
        button_change_path.clicked.connect(self.on_click_button_change_path)
        layout.addRow(button_change_path)

        # Create three combo boxes that select the simulation based on the files stored in BASEDIR_PATH.
        layout.addRow(QLabel("Selecciona la simulación: "))
        selectors = QWidget()
        selectors_layout = QGridLayout()

        # Read the different documents inside the path, this changes the class attribute: 
        self.read_path()

        # Add a button to analize the simulation selected.
        self.analyze = QPushButton("Mostrar análisis visual")
        self.analyze.clicked.connect(self.on_click_analyze)
        layout.addRow(self.analyze)
        
        self.report = QPushButton("Guardar informe PDF")
        self.report.clicked.connect(self.on_click_report)
        layout.addRow(self.report)
        # Finally set the layout of the top-form for selecting the simulation
        selection_form.setLayout(layout)

        return selection_form
