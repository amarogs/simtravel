import copy

from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import QSpinBox, QDoubleSpinBox, QLineEdit, QCheckBox
from PyQt5.QtGui import QKeySequence

from PyQt5.QtWidgets import *
from src.app.animation import Animation, VisualizationWindow
from src.models.cities import SquareCity
from src.app.visual_analysis import AnalysisDistribution
from src.app.params import LY_ENG_TO_SP, LY_SP_TO_ENG




class PageParam():
    def __init__(self, widget, minimum, single_step, key, label ):
        self.widget = widget
        self.minimum = minimum
        self.single_step = single_step
        self.key = key
        self.label = label


class ParamsCreationForm(QWidget):
    def __init__(self, app_params, callback, parent=None, flags=QtCore.Qt.WindowFlags()):
        super().__init__(parent=parent, flags=flags)

        self.app_params = app_params
        self.internal_params = copy.deepcopy(app_params)
        self.callback = callback

        # Create the layout of the class
        self.layout = QVBoxLayout()

        # Create the stack that will hold the different pages    
        self.stack = QStackedWidget()
        # Add the different pages to the stack
        self.widgets = [CityCreationPage(),PhysicalUnitsPage(), DistributionPage(), GeneralPage(), InstancesPage() ]
        for w in self.widgets:
            self.stack.addWidget(w)
        # Create the button row at the bottom
        self.button_layout = QHBoxLayout()
        self.next_page = QPushButton("Siguiente")
        self.next_page.clicked.connect(self.on_click_next_page)
        self.previous_page = QPushButton("Anterior")
        self.previous_page.clicked.connect(self.on_click_previous_page)
        self.cancel = QPushButton("Cancelar")
        self.cancel.clicked.connect(self.on_click_cancel)
        self.save = QPushButton("Establecer parámeteros")
        self.save.clicked.connect(self.on_click_save)

        button_row = [self.cancel, self.previous_page, self.next_page, self.save]
        for button in button_row:
            self.button_layout.addWidget(button)
        self.button_tool = QWidget()
        self.button_tool.setLayout(self.button_layout)

        # Perform the initial step
        self.update_page_info()
        self.update_button_tool()
        
        # Configure the general layout with the stack and the button tool row.
        self.layout.addWidget(self.stack)
        self.layout.addWidget(self.button_tool)
        self.setLayout(self.layout)
    
    def update_app_params(self, app_params):
        """The internal app_params attribute points to the new ones and also the internal 
        parameters are updated, there is a current page update afterwards. """
        self.app_params = app_params
        self.internal_params = copy.deepcopy(app_params)
        self.update_page_info()
        self.show()

    def update_internal_params(self):
        """For each widget in the current page widgets_dict, updates the corresponding internal value. """
        # Point to the current page
        page = self.stack.currentWidget()
        # For each widget inside the page, update the corresponding internal param.
        for k, w in page.widgets_dict.items():
            if isinstance(w, QSpinBox) or isinstance(w, QDoubleSpinBox):
                self.internal_params[k] = w.value()
            elif isinstance(w, QLineEdit):
                if k in ["EV_DENSITY_VALUES", "TF_DENSITY_VALUES"]:
                    self.internal_params[k] = [float(p) for p in w.text().split(" ") if p != ""]
                else:
                    self.internal_params[k] = w.text()
            elif isinstance(w, QCheckBox):
                self.internal_params[k] = w.isChecked()

    def update_button_tool(self):
        # Check the different cases based on the new page.
        current = self.stack.currentIndex()
        if current == 0:
            self.previous_page.hide()
            self.save.hide()
            self.next_page.show()
            
        elif current == self.stack.count() - 1:
            self.next_page.hide()
            self.save.show()
            self.previous_page.show()
        else:
            self.next_page.show()
            self.previous_page.show()
            self.save.hide()

    def update_page_info(self):
        page = self.stack.currentWidget()
        page.update_values(self.internal_params)

    def on_click_next_page(self):
        # First update the internal values
        self.update_internal_params()
        # Then, move the stack pointer to the next page.
        self.stack.setCurrentIndex(self.stack.currentIndex()+1)
        # Update the values of the page
        self.update_page_info()
        # Then update the button row to show the proper buttons
        self.update_button_tool()
        
    def on_click_previous_page(self):
        # First update the internal values
        self.update_internal_params()
        # Then, move the stack pointer to the previous page.
        self.stack.setCurrentIndex(self.stack.currentIndex()-1)
        # Update the values of the page
        self.update_page_info()
        # Then update the button row to show the proper buttons
        self.update_button_tool()
               
    def on_click_cancel(self):
        self.stack.setCurrentIndex(0)
        for w in self.widgets:
            w.close_external_window()
        self.hide()
        self.callback()

    def on_click_save(self):
        # First, save the parameters from the last page
        self.update_internal_params()
        # Then, override each app_param with the internal one
        for key, value in self.internal_params.items():
            self.app_params[key] = value
        self.on_click_cancel()
    def closeEvent(self, cls):
        for w in self.widgets:
            w.close()
        return super().closeEvent(cls)
class Page(QWidget):
    """Class that controls the logic of a Page through certain functions. Aspects related to the
    desing of the page are left for classes that inherint this one. """
    def __init__(self, parent=None, flags=QtCore.Qt.WindowFlags()):
        super().__init__(parent=parent, flags=flags)
        self.widgets_dict = {}

    def add_page_param_to_layout(self, page_params, layout):
        """For each PageParam in page_params list, creates the corresponding
        widget object and stores it in a dictionary referenced by its key. """

        widgets = []
        for param in page_params:
            widget = param.widget()
            if type(widget) == QSpinBox or type(widget) == QDoubleSpinBox:
                widget.setMinimum(param.minimum)
                widget.setMaximum(100000000)
                widget.setSingleStep(param.single_step)
                
                self.widgets_dict[param.key] = widget
                layout.addRow(QLabel(param.label), widget)
                widgets.append(widget)

            elif type(widget) == QLineEdit:
                self.widgets_dict[param.key] = widget
                layout.addRow(QLabel(param.label), widget)
                widgets.append(widget)

            elif type(widget) == QCheckBox: 
                self.widgets_dict[param.key] = widget
                layout.addRow(QLabel(param.label), widget)
                widgets.append(widget)

        return widgets

    def update_values(self, new_values):
        """Given a dictionary (WIDGET_KEY:VALUE), updates the widgets inside the
        widgets_dict with the proper values. """

        for key, widget in self.widgets_dict.items():
            if type(widget) == QSpinBox or type(widget) == QDoubleSpinBox:
                widget.setValue(new_values[key])
            elif type(widget) == QLineEdit:
                if key == "EV_DENSITY_VALUES" or key == "TF_DENSITY_VALUES":
                    widget.setText("".join([str(f)+" " for f in new_values[key]]))
                else:
                    widget.setText(new_values[key])
            elif type(widget) == QCheckBox:
                widget.setChecked(new_values[key])
            else:
                raise TypeError("The widget inside widgets_dict has an unkwon type")
    def close_external_window(self):
        pass
class CityCreationPage(Page):
    def __init__(self, parent=None, flags=QtCore.Qt.WindowFlags()):
        super().__init__(parent=parent, flags=flags)
        # Create the city visualization window
        self.city_visualization = VisualizationWindow()
        
        # City related parameters
        roundabout = PageParam(QSpinBox, 6, 2, "RB_LENGTH", "Tamaño del lado de las rotondas:")
        av_segment = PageParam(QSpinBox, 20, 8, "AV_LENGTH", "Longitud de una avenida")
        scale = PageParam(QSpinBox, 1, 1, "SCALE", "Factor de escala del patrón base:")

        # Stations related parameters
        plugs_per_station = PageParam(QSpinBox, 1, 1, "MIN_PLUGS_PER_STATION", "Número mínimo de enchufes por estacion:")
        d_stations = PageParam(QSpinBox, 1,1,"MIN_D_STATIONS", "Número mínimo de estaciones pequeñas: ")

        # Create self layout
        layout = QVBoxLayout()
        
        # Add city configuration subpart
        cities_form = QGroupBox("Creación de la ciudad")
        aux_layout = QFormLayout()
        aux_layout.setSizeConstraint(QLayout.SetMinimumSize)
        aux_layout.addRow(QLabel("Configuración de la ciudad sintética con rotondas, calles y avenidas."))
        self.add_page_param_to_layout([roundabout, av_segment,scale], aux_layout)
        show_city_button = QPushButton("Mostrar ciudad")
        show_city_button.clicked.connect(self.show_city)
        aux_layout.addRow(show_city_button)


        cities_form.setLayout(aux_layout)
        # Add the cities_form to the layout and create a new part of the form.
        layout.addWidget(cities_form)

        # Add stations configuration subpart
        stations_form = QGroupBox("Configuración de la distribución de las estaciones")
        aux_layout = QFormLayout()
        aux_layout.setSizeConstraint(QLayout.SetMinimumSize)
        aux_layout.addRow(QLabel("El número de estaciones pequeñas total será el siguiente número múltiplo de cuatro y\n cuadrado perfecto del número mínimo indicado "))
        self.add_page_param_to_layout([plugs_per_station,d_stations ], aux_layout)
        
        show_st_layout_button = QPushButton("Mostrar estaciones")
        show_st_layout_button.clicked.connect(self.show_stations)
        self.choose_st_layout = QComboBox()
        self.choose_st_layout.addItems(LY_SP_TO_ENG.keys())
        aux_line_layout = QHBoxLayout()
        aux_line_layout.addWidget(show_st_layout_button)
        aux_line_layout.addWidget(self.choose_st_layout)
        
        aux_layout.addRow(aux_line_layout)
        stations_form.setLayout(aux_layout)

        # Add the stations_form to the layout
        layout.addWidget(stations_form)
        # Add a save image button to the layout
        save_button = QPushButton("Guardar imagen")
        save_button.clicked.connect(self.save_new_image)
        layout.addWidget(save_button)

        # Set the layout
        self.setLayout(layout)
    def show_city(self):
        """Reads the values of the QSpingBox parameters and creates and new city. Then it opens
        the visualization window and renders a new visualization of the newly created city. """

        # Create the city
        rb_length = self.widgets_dict["RB_LENGTH"].value()
        av_length = self.widgets_dict["AV_LENGTH"].value()
        scale = self.widgets_dict["SCALE"].value()
        city = SquareCity(RB_LENGTH=rb_length, AV_LENGTH=av_length, SCALE=scale)

        # Display the new city
        self.city_visualization.show()
        self.city_visualization.show_new_city(city.SIZE, city.city_matrix, city.city_map)
        

    def show_stations(self):
        # Create the city
        rb_length = self.widgets_dict["RB_LENGTH"].value()
        av_length = self.widgets_dict["AV_LENGTH"].value()
        scale = self.widgets_dict["SCALE"].value()
        city = SquareCity(RB_LENGTH=rb_length, AV_LENGTH=av_length, SCALE=scale)
        self.city_visualization.show()
        # Place the stations in the city based on the parameters chosen.
        min_plugs_per_station = self.widgets_dict["MIN_PLUGS_PER_STATION"].value()
        min_num_stations = self.widgets_dict["MIN_D_STATIONS"].value()
        
        _, TOTAL_D_ST = city.set_max_chargers_stations(min_plugs_per_station, min_num_stations)
        stations_pos, stations_influence = city.place_stations_new(LY_SP_TO_ENG[self.choose_st_layout.currentText()], TOTAL_D_ST)
        
        # Display the newly created city with the stations.
        self.city_visualization.show_new_city(city.SIZE, city.city_matrix, stations_pos=stations_pos, stations_influence=stations_influence)        

    def save_new_image(self):
        self.city_visualization.update()
        image = self.city_visualization.save_image()
        if image != None:
            path = QFileDialog.getSaveFileName(self, "Guardar imagen como")[0]
            if path and image:
                image.save(path+".png", "png", quality=95)
    def close_external_window(self):
        self.city_visualization.close()
    
    def closeEvent(self, cls):
        self.city_visualization.close()
        return super().closeEvent(cls)
class PhysicalUnitsPage(Page):
    def __init__(self, parent=None, flags=QtCore.Qt.WindowFlags()):
        super().__init__(parent=parent, flags=flags)
        # Create the Params
        # Speed parameters
        speed = PageParam(QSpinBox, 1, 1, "SPEED", "Velocidad media en las calles (km/h):")
        cell_length = PageParam(QSpinBox, 1, 1, "CELL_LENGTH", "Longitud de una celda (m):")
        simulation_speed = PageParam(QSpinBox, 1, 1, "SIMULATION_SPEED", "Velocidad de la simulación (cell/timestep):")

        # Battery parameters
        battery_capacity = PageParam(QSpinBox, 1, 1, "BATTERY", "Capacidad de la batería (kWh):")
        station_power = PageParam(QSpinBox, 1, 1, "CS_POWER", "Potencia de las estaciones (kW):")


        # Set the layout of the (self) widget
        layout = QVBoxLayout()
        layout.setSizeConstraint(QLayout.SetMinimumSize)

        # Subsection about velocity related parameters
        form_speed = QGroupBox("Unidades físicas - Velocidad")
        layout_aux = QFormLayout()
        layout_aux.setSizeConstraint(QLayout.SetMinimumSize)
        self.add_page_param_to_layout([speed, cell_length,simulation_speed], layout_aux)
        form_speed.setLayout(layout_aux)

        # Add the first subform to the general layout
        layout.addWidget(form_speed)

        # Subsection about energy related parameters
        form_battery = QGroupBox("Unidades físicas - energía")
        layout_aux = QFormLayout()
        layout_aux.setSizeConstraint(QLayout.SetMinimumSize)
        self.add_page_param_to_layout([battery_capacity, station_power], layout_aux)
        form_battery.setLayout(layout_aux)

        # Add the second subform to the layout combined and set the general layout.
        layout.addWidget(form_battery)

        self.setLayout(layout)

class DistributionPage(Page):
    def __init__(self, parent=None, flags=QtCore.Qt.WindowFlags()):
        super().__init__(parent=parent, flags=flags)
        # Create the visualization window
        self.distribution_visualization = AnalysisDistribution()
        # Create the PageParam
        battery_autonomy = PageParam(QSpinBox, 1, 1, "AUTONOMY", "Autonomía de una carga completa (km):")
        battery_thresh = PageParam(QDoubleSpinBox, 0.05, 0.01, "BATTERY_THRESHOLD", "Umbral mínimo de batería (tanto por uno):")
        battery_std = PageParam(QDoubleSpinBox, 0.05, 0.01, "BATTERY_STD", "Desviación estándar de la batería (tanto por uno):")
        
        idle_upper = PageParam(QSpinBox, 1, 1, "IDLE_UPPER", "Máximo tiempo en espera (min):")
        idle_lower = PageParam(QSpinBox, 1, 1, "IDLE_LOWER", "Mínimo tiempo en espera (min):")
        idle_std = PageParam(QDoubleSpinBox, 0.05, 0.01, "IDLE_STD", "Desviación estándar del tiempo en espera (tanto por uno):")

        layout = QVBoxLayout()

        # Create first section defined by a GroupBox
        battery_form = QGroupBox("Distribución de la autonomía de batería")
        aux_layout = QFormLayout()
        aux_layout.setSizeConstraint(QLayout.SetMinimumSize)
        widgets = self.add_page_param_to_layout([battery_autonomy,battery_thresh, battery_std], aux_layout)
        for w in widgets:
            w.valueChanged.connect(self.update_battery_distribution)
        battery_form.setLayout(aux_layout)

        # Add the section to the general layout and then create another section
        layout.addWidget(battery_form)

        # Create the second section defined by another Groupbox.
        wait_form = QGroupBox("Distribución del tiempo de espera")
        aux_layout = QFormLayout()
        aux_layout.setSizeConstraint(QLayout.SetMinimumSize)

        widgets = self.add_page_param_to_layout([idle_upper, idle_lower, idle_std], aux_layout)
        for w in widgets:
            w.valueChanged.connect(self.update_wait_distribution)
        wait_form.setLayout(aux_layout)

        # Add the section to the general layout and set the class layout.
        layout.addWidget(wait_form)     
        self.setLayout(layout)

    def update_battery_distribution(self):
        """Creates a new normal distribution sample and opens a window with the corresponding
        normal distribution. Uses the values for a battery distribution."""

        mean = self.widgets_dict["AUTONOMY"].value() // 2
        std = float(self.widgets_dict["BATTERY_STD"].value()) * mean
        low = float(self.widgets_dict["BATTERY_THRESHOLD"].value()) * self.widgets_dict["AUTONOMY"].value()
        
        upper= self.widgets_dict["AUTONOMY"].value()

        if upper > low:
            self.distribution_visualization.update_canvas(mean, std, low, upper, "Autonomía (km)" )
            self.distribution_visualization.show()        

    def update_wait_distribution(self):
        """Creates a new normal distribution sample and opens a window with the corresponding
        normal distribution. Uses the values of the wait time distribution. """
        low = int(self.widgets_dict['IDLE_LOWER'].value())
        upper = int(self.widgets_dict['IDLE_UPPER'].value())
        std = float(self.widgets_dict['IDLE_STD'].value())
        mean = (low + upper) /2

        if upper > low:
            self.distribution_visualization.update_canvas(mean, std, low, upper, "Tiempo en espera (min)")
            self.distribution_visualization.show()
    def close_external_window(self):
        self.distribution_visualization.close()
    def closeEvent(self, cls):
        self.distribution_visualization.close()
        return super().closeEvent(cls)
class GeneralPage(Page):
    def __init__(self, parent=None, flags=QtCore.Qt.WindowFlags()):
        super().__init__(parent=parent, flags=flags)

        # Create the PageParam for this class
        repetitions =PageParam(QSpinBox, 1, 1, "REPETITIONS", "Número de repeticiones de cada simulación:")
        total_time = PageParam(QSpinBox, 1, 1, "TOTAL_TIME", "Tiempo total de simulación (h):")
        measure_period = PageParam(QSpinBox,0, 1, "MEASURE_PERIOD", "Tiempo entre cada medición del sistema (min):")
        directory_path = PageParam(QLineEdit, None, None, "PATH", "Directorio seleccionado:")
        # Create the layout for this class
        layout = QVBoxLayout()

        # First section, general configuration
        configuration_form = QGroupBox("Configuración general de las simulaciones")
        aux_layout = QFormLayout()
        aux_layout.setSizeConstraint(QLayout.SetMinimumSize)
        self.add_page_param_to_layout([repetitions,total_time,measure_period ], aux_layout)
        configuration_form.setLayout(aux_layout)

        # Add the section to the general layout
        layout.addWidget(configuration_form)

        # Second section, PATH input.
        path_form = QGroupBox("Configuarción de los resultados")
        aux_layout = QFormLayout()
        msg = """Seleccione el directorio donde se van a guardar los resultados de las simulaciones.\nPuede seleccionar uno del sistema haciendo click en el botón o bien escribir manualmente el directorio."""
        aux_layout.addRow(QLabel(msg))
        self.add_page_param_to_layout([directory_path], aux_layout)
        change_path_button = QPushButton("Seleccionar directorio del sistema")
        change_path_button.clicked.connect(self.on_click_change_path_button)
        aux_layout.addRow(change_path_button)
        path_form.setLayout(aux_layout)

        # Add the section to the general layout
        layout.addWidget(path_form)

        self.setLayout(layout)
    def on_click_change_path_button(self):
        path = QFileDialog.getExistingDirectory(caption="Seleccionar directorio de resultados")
        if path:
            self.widgets_dict['PATH'].setText(path)


class InstancesPage(Page):
    def __init__(self, parent=None, flags=QtCore.Qt.WindowFlags()):
        super().__init__(parent=parent, flags=flags)
        
        # Create the PageParam for this class
        ev_density = PageParam(QLineEdit, None, None, "EV_DENSITY_VALUES", "Valores de densidad de VE:")
        tf_density = PageParam(QLineEdit, None, None, "TF_DENSITY_VALUES", "Valores de densidad de tráfico:")

        st_central = PageParam(QCheckBox, None, None, "ST_CENTRAL", "Una estación centrada en una avenida")
        st_distributed = PageParam(QCheckBox, None, None, "ST_DISTRIBUTED", "Pequeñas estaciones en las calles")
        st_four = PageParam(QCheckBox, None, None, "ST_FOUR", "Cuatro estaciones medianas en las avenidas")

        # Create the class layout
        layout = QVBoxLayout()

        # Create the first section about the traffic
        vehicles_form = QGroupBox("Configuración de instancias - Vehículos")
        aux_layout = QFormLayout()
        aux_layout.setSizeConstraint(QLayout.SetMinimumSize)
        aux_layout.addRow(QLabel('Introduzca los valores de densidad de VE y densidad de tráfico.\nPara separar cada valor utilizar un espacio en blanco. \n Por ejemplo: 0.1 0.2 0.3 0.4 '))
        self.add_page_param_to_layout([tf_density, ev_density], aux_layout)
        vehicles_form.setLayout(aux_layout)

        layout.addWidget(vehicles_form)

        # Create the second section about the stations
        stations_form = QGroupBox("Configuración de instancias - Estaciones")
        aux_layout = QFormLayout()
        aux_layout.setSizeConstraint(QLayout.SetMinimumSize)
        aux_layout.addRow(QLabel("Marque todas las disposiciones de estaciones que desee probar. Al menos una"))
        self.add_page_param_to_layout([st_central, st_distributed,st_four], aux_layout)
        stations_form.setLayout(aux_layout)

        layout.addWidget(stations_form)

        self.setLayout(layout)
