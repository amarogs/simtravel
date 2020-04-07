import copy

from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtGui import QKeySequence

from PyQt5.QtWidgets import *
from src.app.animation import Animation, VisualizationWindow
from src.models.cities import SquareCity
from src.app.param import city_creation, speed_creation, battery_creation, \
    distribution_creation, sim_configuration_creation, instances_configuration_creation, stations_configuration_creation


class ParamsCreationForm(QWidget):


    def __init__(self, params, parent=None, flags=QtCore.Qt.WindowFlags()):
        super(ParamsCreationForm, self).__init__(parent=parent, flags=flags)
        self.current_view = None # Points to the next view that must be rendered
        self.views = [self.create_city_form, self.create_physical_units_form, \
            self.create_distribution_form, self.create_sim_configuration_form, self.create_results_form]

        self.args = [{"title1":"Creación de la ciudad", "button1":"Mostrar ciudad"},\
                     {"title1": "Unidades físicas - velocidad", "title2": "Unidades físicas - energía"},
                     {"title1": "Distribución de la batería y el tiempo de espera"},
                     {"title1": "Configuración general de las simulaciones", "title2": "Configuración de las instancias",
                     "title3": "Configuración de las estaciones"},{"title1":"Configuración de los resultados"}]
        self.global_params = params
        self.params_text = copy.deepcopy(params)

        self.params_widget = {k:None for k in self.params_text}

        # Button tool in the lower part of the main window.
        self.button_tool = QWidget()
        self.button_layout = QHBoxLayout()

        self.next_view = QPushButton("Siguiente")
        self.previous_view = QPushButton("Anterior")
        self.cancel = QPushButton("Cancelar")
        self.save = QPushButton("Establecer parámeteros")
        
        # Connect the buttons with its callback functions
        self.next_view.clicked.connect(self.next_screen)
        self.previous_view.clicked.connect(self.previous_screen)
        self.save.clicked.connect(self.save_and_close)
        self.cancel.clicked.connect(self.close_all)
        
        # Add the buttons to the layout
        self.button_layout.addWidget(self.cancel)
        self.button_layout.addWidget(self.previous_view)
        self.previous_view.hide()
        self.button_layout.addWidget(self.next_view)
        self.button_layout.addWidget(self.save)
        self.save.hide()
        
        # Set the button_tool layout
        self.button_tool.setLayout(self.button_layout)

        # Now we are going to create the main area, the scrolling area.
        self.scroll_area = QScrollArea()

        # Finally create the composition of this view adding the scroll area and the button toolbox at the bottom.
        mainLayout = QVBoxLayout()

        mainLayout.addWidget(self.scroll_area)
        mainLayout.addWidget(self.button_tool)
        self.setLayout(mainLayout)

        # Create a visualization widget
        self.city_visualization = VisualizationWindow()


        # Set the widget as hidden by default
        self.hide()
    def initialize_widget(self, parameters):
        """Restarts the widget with fresh parameters. """
        self.global_params = parameters
        self.params_text = copy.deepcopy(parameters)
        self.current_view = 0
        self.next_screen()
        self.show()

    def save_and_close(self):
        # Update the parameters from the last screen:
        self.update_params_txt()
        
        # Update the global parameters
        for k,v in self.params_text.items():
            self.global_params[k] = v
        
        
        self.close_all()
    def close_all(self):
        self.current_view = None
        self.city_visualization.close()
        self.hide()

    def next_screen(self):
        """Function that draws the next screen """
        self.change_screen()
        self.current_view += 1
    def previous_screen(self):
        """Function that draws the previous screen """
        self.current_view -= 2 
        self.change_screen()
        self.current_view += 1

    def update_params_txt(self, reset_widgets=True):
        """Updates the dictionary of parameters """
        # Record the current values
        for k, w in self.params_widget.items():
            if w != None:
                if isinstance(w, QSpinBox) or isinstance(w, QDoubleSpinBox):
                    self.params_text[k] = w.value()

                elif isinstance(w, QLineEdit):
                    self.params_text[k] = self.read_density_params(w.text())
                elif isinstance(w, QCheckBox):
                    self.params_text[k] = w.isChecked()
           
                if reset_widgets:
                    self.params_widget[k] = None
    def change_screen(self):
        """Function that draws the following/previous screen """
        self.update_params_txt()
        if self.current_view > 0:
            # Show the previous button.
            self.previous_view.show()
            # Check whether we are in the last screen
            if self.current_view == len(self.views) -1:
                self.next_view.hide()
                self.save.show()
            else:
                self.next_view.show()
                self.save.hide()
        else:
            # This is the first view
            self.next_view.show()
            self.save.hide()
            self.previous_view.hide()

        # Draw the corresponding view.
        self.views[self.current_view](**self.args[self.current_view])
        
        # Update the scrolling area to the new current_form
        self.scroll_area.setWidget(self.current_form)
        

    def show_city(self):
        # Update the parameters
        self.update_params_txt(reset_widgets=False)
        
        # Create the city
        city = SquareCity(RB_LENGTH=self.params_text["RB_LENGTH"],\
             AV_LENGTH=self.params_text["AV_LENGTH"], SCALE=self.params_text["SCALE"])
        self.city_visualization.show()
    
        # Display the newly created city
        self.city_visualization.show_new_city(city.SIZE, city.city_matrix)
    

    def add_params_to_layout(self, params, layout):
        """For each param in the list params creates a widget and add it to layout. """
        for param in params:
            if param.widget == QSpinBox or param.widget == QDoubleSpinBox:
                widget = param.widget()
                widget.setMinimum(param.minimum)
                widget.setSingleStep(param.single_step)
                widget.setValue(self.params_text[param.key])
                self.params_widget[param.key] = widget
                layout.addRow(QLabel(param.label), widget)

            elif param.widget == QLineEdit:
                widget = param.widget()
                widget.setText(self.write_density_params(self.params_text[param.key]))
                self.params_widget[param.key] = widget
                layout.addRow(QLabel(param.label), widget)

            elif param.widget == QCheckBox: 
                widget = param.widget()
                widget.setChecked(self.params_text[param.key])
                self.params_widget[param.key] = widget
                layout.addRow(QLabel(param.label), widget)
    def create_city_form(self, *args, **kwargs):
        """Creates a form to fullfill the parameters related to the city creation. """

        # Create the form that will be displayed in the scrollable area
        self.current_form = QGroupBox(kwargs["title1"])
        layout = QFormLayout()
        layout.setSizeConstraint(QLayout.SetMinimumSize)
        # For each parameter, add it to the layout
        self.add_params_to_layout(city_creation, layout)

        # Button for displaying the city.
        show_city_button = QPushButton(kwargs["button1"])
        show_city_button.clicked.connect(self.show_city)
        layout.addRow(show_city_button)
    
        # Add the layout to the current_form
        self.current_form.setLayout(layout)
        
    def create_physical_units_form(self, *args, **kwargs):
        """Form  """
        self.current_form = QWidget()
        layout_combined = QVBoxLayout()
        layout_combined.setSizeConstraint(QLayout.SetMinimumSize)
        # Subsection about velocity related parameters
        form_speed = QGroupBox(kwargs["title1"])
        layout_speed = QFormLayout()
        layout_speed.setSizeConstraint(QLayout.SetMinimumSize)
        self.add_params_to_layout(speed_creation, layout_speed)

        # Add the first subform to the general layout
        form_speed.setLayout(layout_speed)
        layout_combined.addWidget(form_speed)

        # Subsection about energy related parameters
        form_battery = QGroupBox(kwargs["title2"])
        layout_battery = QFormLayout()
        layout_battery.setSizeConstraint(QLayout.SetMinimumSize)
        self.add_params_to_layout(battery_creation, layout_battery)
        
        # Add the second subform to the layout combined and set the general layout.
        form_battery.setLayout(layout_battery)
        layout_combined.addWidget(form_battery)


        self.current_form.setLayout(layout_combined)
    def read_density_params(self, text):
        return [float(p) for p in text.split(";") if p != ""]
    def write_density_params(self, den_list):
        return "".join([str(f) + ";" for f in den_list])


    def create_distribution_form(self, *args, **kwargs):
        # Create the form that will be displayed in the scrollable area
        self.current_form = QGroupBox(kwargs["title1"])
        layout = QFormLayout()
        layout.setSizeConstraint(QLayout.SetMinimumSize)
        # For each parameter, add it to the layout
        self.add_params_to_layout(distribution_creation, layout)

        # Add the layout to the current_form
        self.current_form.setLayout(layout)
    def create_results_form(self, *args, **kwargs):
        def on_click_button_change_path():
            """Selects a new path to stre the results """
            path = QFileDialog.getExistingDirectory(caption="Seleccionar directorio de resultados")
          
            if path:
                self.params_text['PATH'] = path
                self.current_directory_label.setText("Directorio actual: " + self.params_text["PATH"])

        # Create a subform about the path where the results are going to be stored.
        self.current_form = QGroupBox(kwargs['title1'])
        layout = QFormLayout()
        layout.setSizeConstraint(QLayout.SetMinimumSize)
        layout.addRow(QLabel("Seleccione el directorio donde se van a guardar los resultados de las simulaciones."))
        if self.params_text["PATH"] == ".":
            self.params_text["PATH"] = QtCore.QDir.currentPath()
            
        self.current_directory_label = QLabel("Directorio actual: " + self.params_text["PATH"])
        layout.addRow(self.current_directory_label)
        button_change_path = QPushButton("Seleccionar nuevo directorio")
        button_change_path.clicked.connect(on_click_button_change_path)
        layout.addRow(button_change_path)
        self.current_form.setLayout(layout)

    def create_sim_configuration_form(self, *args, **kwargs):

        # Create the form that will be displayed in the scrollable area
        self.current_form = QWidget()
        # Create a subform about the configuration of the simulations
        configuracion_form = QGroupBox(kwargs["title1"])
        layout = QFormLayout()
        layout.setSizeConstraint(QLayout.SetMinimumSize)
        # For each parameter, add it to the layout
        self.add_params_to_layout(sim_configuration_creation, layout)
        configuracion_form.setLayout(layout)


        # Create a subform about the instances of simulations that will be created.
        instances_form = QGroupBox(kwargs["title2"])
        layout = QFormLayout()
        layout.setSizeConstraint(QLayout.SetMinimumSize)
        layout.addRow(QLabel('Introduzca los valores de densidad de EV y tráfico separándolos por ";".\n'\
            'Los valores están expresados en tanto por uno de manera relativa al total de celdas.\nPor ejemplo: 0.1; 0.2; 0.5'))

        self.add_params_to_layout(instances_configuration_creation, layout)
        instances_form.setLayout(layout)

        
        stations_form = QGroupBox(kwargs["title3"])
        layout = QFormLayout()
        layout.setSizeConstraint(QLayout.SetMinimumSize)
        layout.addRow(QLabel("Marque todas las disposiciones de estaciones que desee probar. Al menos una"))
        self.add_params_to_layout(stations_configuration_creation, layout)
        stations_form.setLayout(layout)
        
        

        # Add the layout to the current_form
        layout = QVBoxLayout()
        layout.setSizeConstraint(QLayout.SetMinimumSize)
        layout.addWidget(configuracion_form)
        layout.addWidget(instances_form)
        layout.addWidget(stations_form)

        self.current_form.setLayout(layout)

    