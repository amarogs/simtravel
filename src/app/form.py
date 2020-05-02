import copy

from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtGui import QKeySequence

from PyQt5.QtWidgets import *
from src.app.animation import Animation, VisualizationWindow
from src.models.cities import SquareCity
from src.app.param import city_creation,stations_creation, speed_creation, battery_creation, \
    distribution_creation, sim_configuration_creation, instances_configuration_creation, stations_configuration_creation, LY_SP_TO_ENG, LY_ENG_TO_SP
from src.app.visual_analysis import AnalysisDistribucion


class ParamsCreationForm(QWidget):


    def __init__(self, params,callback, parent=None, flags=QtCore.Qt.WindowFlags()):
        super(ParamsCreationForm, self).__init__(parent=parent, flags=flags)
        # Function that must be called right after closing the form
        self.callback = callback
        # Points to the next view that must be rendered
        self.current_view = None 
        # List of function that create the views. The current_view can point to any view to draw it.
        self.views = [self.create_city_form, self.create_physical_units_form, \
            self.create_distribution_form, self.create_sim_configuration_form, self.create_results_form]
        # List of arguments that are used in the creation functions. Each index matches a function
        # in the list of functions.
        self.args = [{"title1":"Creación de la ciudad", "button1":"Mostrar ciudad",\
                    "title2":"Configuración de la distribución de estaciones", "button2":"Mostras estaciones"},\

                     {"title1": "Unidades físicas - velocidad", "title2": "Unidades físicas - energía"},
                     {"title1": "Distribución de la batería", "title2": "Distribución del tiempo de espera"},
                     {"title1": "Configuración general de las simulaciones", "title2": "Configuración de las instancias",
                     "title3": "Configuración de las estaciones"},{"title1":"Configuración de los resultados"}]

        # Attribute that points to the global params
        self.global_params = params
        # Attribute used througout the form to store a internal copy.
        self.params_text = copy.deepcopy(params)
        # Attribute that holds each widget with a KEY that matches those in the simulation parameters.
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

        # Create a distribution visualization widget
        self.distribution_visualization = AnalysisDistribucion()

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
        self.distribution_visualization.close()
        self.hide()
        self.callback()

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
        
    def save_new_image(self):
        """Read the current buffer and stores it in a PNG image. """
        self.city_visualization.update()
        image = self.city_visualization.save_image()
        if image != None:
            path = QFileDialog.getSaveFileName(self, "Guardar imagen como")[0]
            if path and image:
                image.save(path+".png", "png", quality=95)
        
    def show_city(self):
        # Update the parameters
        self.update_params_txt(reset_widgets=False)
        
        # Create the city
        city = SquareCity(RB_LENGTH=self.params_text["RB_LENGTH"],\
             AV_LENGTH=self.params_text["AV_LENGTH"], SCALE=self.params_text["SCALE"])
        self.city_visualization.show()
    
        # Display the newly created city
        self.city_visualization.show_new_city(city.SIZE, city.city_matrix, city.city_map)

    def show_stations(self):
        # Update the parameters
        self.update_params_txt(reset_widgets=False)
        
        # Create the city
        city = SquareCity(RB_LENGTH=self.params_text["RB_LENGTH"],\
             AV_LENGTH=self.params_text["AV_LENGTH"], SCALE=self.params_text["SCALE"])
        self.city_visualization.show()
        # Place the stations in the city based on the parameters chosen.
        min_plugs_per_station, min_num_stations = self.params_text["MIN_PLUGS_PER_STATION"], self.params_text["MIN_D_STATIONS"]
        _, TOTAL_D_ST = city.set_max_chargers_stations(min_plugs_per_station, min_num_stations)
        stations_pos, stations_influence = city.place_stations_new(LY_SP_TO_ENG[self.station_layout.currentText()], TOTAL_D_ST)
        
        # Display the newly created city with the stations.
        self.city_visualization.show_new_city(city.SIZE, city.city_matrix, stations_pos=stations_pos, stations_influence=stations_influence)        

    def add_params_to_layout(self, params, layout):
        """For each param in the list params creates a widget and add it to layout. """
        widgets = []
        for param in params:
            if param.widget == QSpinBox or param.widget == QDoubleSpinBox:
                widget = param.widget()
                widget.setMinimum(param.minimum)
                widget.setMaximum(100000000)
                widget.setSingleStep(param.single_step)
                widget.setValue(self.params_text[param.key])
                self.params_widget[param.key] = widget
                layout.addRow(QLabel(param.label), widget)
                widgets.append(widget)

            elif param.widget == QLineEdit:
                widget = param.widget()
                widget.setText(self.write_density_params(self.params_text[param.key]))
                self.params_widget[param.key] = widget
                layout.addRow(QLabel(param.label), widget)
                widgets.append(widget)
            elif param.widget == QCheckBox: 
                widget = param.widget()
                widget.setChecked(self.params_text[param.key])
                self.params_widget[param.key] = widget
                layout.addRow(QLabel(param.label), widget)
                widgets.append(widget)

        return widgets
    def create_city_form(self, *args, **kwargs):
        """Creates a form to fullfill the parameters related to the city creation. """

        # Create the form that will be displayed in the scrollable area
        self.current_form = QWidget()
        form_layout = QVBoxLayout() 

        # Form to show the configure the city and show it wih colors
        cities_form = QGroupBox(kwargs["title1"])
        layout = QFormLayout()
        layout.setSizeConstraint(QLayout.SetMinimumSize)
        layout.addRow(QLabel("Configuración de la ciudad sintética con rotondas, calles y avenidas."))
        # For each parameter, add it to the layout
        self.add_params_to_layout(city_creation, layout)

        # Button for displaying the city.
        show_city_button = QPushButton(kwargs["button1"])
        show_city_button.clicked.connect(self.show_city)
        layout.addRow(show_city_button)
        cities_form.setLayout(layout)

        # Add the form to the general layout
        form_layout.addWidget(cities_form)

        # Form to show the configuration of the stations and show the influence areas
        stations_form = QGroupBox(kwargs["title2"])
        layout = QFormLayout()
        layout.setSizeConstraint(QLayout.SetMinimumSize)
        layout.addRow(QLabel("El número de estaciones pequeñas total será el siguiente número múltiplo de cuatro y\n cuadrado perfecto del número mínimo indicado "))
        # For each parameter, add it to the layout
        self.add_params_to_layout(stations_creation, layout)
        
        # Button for displaying the city stations.
        show_city_button = QPushButton(kwargs["button2"])
        show_city_button.clicked.connect(self.show_stations)
        self.station_layout = QComboBox()
        self.station_layout.addItems(LY_SP_TO_ENG.keys())
        line_layout = QHBoxLayout()
        line_layout.addWidget(show_city_button)
        line_layout.addWidget(self.station_layout)

        layout.addRow(line_layout)
        stations_form.setLayout(layout)
        # Add the form to the general layout
        form_layout.addWidget(stations_form)
        save_button = QPushButton("Guardar imagen")
        save_button.clicked.connect(self.save_new_image)
        form_layout.addWidget(save_button)
        # Set the layout
        self.current_form.setLayout(form_layout)
        
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

    def update_battery_distribution(self):
        self.update_params_txt(reset_widgets=False)
        mean = int(self.params_text["AUTONOMY"])/2
        std = float(self.params_text["BATTERY_STD"])*mean
        low = float(self.params_text["BATTERY_THRESHOLD"]) * int(self.params_text["AUTONOMY"])
        upper= int(self.params_text["AUTONOMY"])
        if upper > low:

            self.distribution_visualization.update_canvas(mean, std, low, upper, "Autonomía (km)" )
            self.distribution_visualization.show()

    def update_wait_distribution(self):
        self.update_params_txt(reset_widgets=False)
        low = int(self.params_text['IDLE_LOWER'])
        upper = int(self.params_text['IDLE_UPPER'])
        std = float(self.params_text['IDLE_STD'])
        mean = (low + upper) /2
        if upper > low:
            
            self.distribution_visualization.update_canvas(mean, std, low, upper, "Tiempo en espera (min)")
            self.distribution_visualization.show()

    def create_distribution_form(self, *args, **kwargs):

        # Create the form that will be displayed in the scrollable area
        self.current_form = QWidget()
        total_layout = QVBoxLayout()

        # First QGgroupBox for the battery distribution 
        battery = QGroupBox(kwargs["title1"])
        layout = QFormLayout()
        layout.setSizeConstraint(QLayout.SetMinimumSize)
        # For each parameter, add it to the layout
        

        widgets = self.add_params_to_layout(distribution_creation[0:2], layout)
        for w in widgets:
            w.valueChanged.connect(self.update_battery_distribution)

        self.update_battery_distribution()
 

        battery.setLayout(layout)
        total_layout.addWidget(battery)


        # Second QGroupBox for the wait time.
        wait = QGroupBox(kwargs["title2"])
        layout = QFormLayout()
        layout.setSizeConstraint(QLayout.SetMinimumSize)

        widgets = self.add_params_to_layout(distribution_creation[2:], layout)
        for w in widgets:
            w.valueChanged.connect(self.update_wait_distribution)


        wait.setLayout(layout)
        total_layout.addWidget(wait)


        # Add the layout to the current_form
        self.current_form.setLayout(total_layout)
    def create_results_form(self, *args, **kwargs):
        def on_click_button_change_path():
            """Selects a new path to stre the results """
            path = QFileDialog.getExistingDirectory(caption="Seleccionar directorio de resultados")
          
            if path:
                self.params_text['PATH'] = path
                self.current_directory_text.setText(self.params_text['PATH'])
        def update_path():
            self.params_text['PATH'] = self.current_directory_text.text()
            
        # Create a subform about the path where the results are going to be stored.
        self.current_form = QGroupBox(kwargs['title1'])
        layout = QFormLayout()
        layout.setSizeConstraint(QLayout.SetMinimumSize)
        msg = """Seleccione el directorio donde se van a guardar los resultados de las simulaciones.\nPuede seleccionar uno del sistema haciendo click en el botón o bien escribir manualmente el directorio."""
        layout.addRow(QLabel(msg))

        
        self.current_directory_text = QLineEdit() 
        self.current_directory_text.textChanged.connect(update_path)
        self.current_directory_text.setText(self.params_text['PATH'])
        layout.addRow(QLabel("Directorio seleccionado:"),self.current_directory_text)
        button_change_path = QPushButton("Seleccionar directorio del sistema")
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

    def closeEvent(self, cls):
        self.city_visualization.close()
        self.distribution_visualization.close()
        
        return super().closeEvent(cls)