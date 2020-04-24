import random
import colorsys
import numpy as np

from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

from PyQt5 import Qt, QtCore, QtGui
from PyQt5.QtCore import QSettings
from PyQt5.QtWidgets import *
from PIL import Image

import src.app.colors as c
from src.models.states import States
from src.models.cities import CellType

class Animation(QOpenGLWidget):

    def __init__(self, parent=None, flags=QtCore.Qt.WindowFlags()):
        super(Animation, self).__init__(parent=parent, flags=flags)

        # This attributes are set when resizeGL is called.
        self.WIN_WIDTH = None
        self.WIN_HEIGTH = None
        self.SIZE = None
        self.cell_size = None

        # Flags that control what is being displayed
        self.displaying_city = False
        self.displaying_stations = False
        self.displaying_vehicles = False

        # Colors that can be used with the vehicles.
        self.colors = [val for n, val in c.__dict__.items() if not n.startswith("__") and sum(val) <= 2.0]
        self.colors.remove((0.0, 0.0, 0.0))

        # Special colors used in the painting of the city or stations
        self.avenue_color = (201/255, 88/255, 19/255)
        self.street_color = (47/255, 72/255, 53/255)
        self.street_color = (244/255, 202/255, 159/255)
        self.roundabout_color = (62/255, 141/255, 126/255)
        self.cluster_colors = None

        self.moving_states = set(States.moving_states())

    def paintGL(self):
        """Renders the OpenGL scene. Gets called whenever the widget needs to be updated."""
        
        # clear the screen
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)  
        # reset position
        glLoadIdentity()  
        # set mode to 2d                                 
        self.refresh2d()   

        # Paint new opengl drawings
        if self.displaying_city:
            glCallList(self.city_drawing)   
            if self.displaying_stations:
                glCallList(self.stations_drawing)

        if self.displaying_vehicles:
            self.draw_vehicles()

        self.save_buffer_to_image()
    def resizeGL(self, width, heigth):
        """Sets up the OpenGL viewport, projection, etc. Gets called whenever the 
        widget has been resized (and also when it is shown for the first time 
        because all newly created widgets get a resize event automatically) """
        
        
        if width > heigth:
            side = heigth
        else:
            side = width

        
        side = int(self.devicePixelRatio()*side)
        
        self.WIN_HEIGTH, self.WIN_WIDTH = side, side
        if self.displaying_city:
            self.display_new_city(self.SIZE, self.city, self.city_map, self.stations_pos, self.stations_influence)
            if self.displaying_stations:
                self.display_stations(self.stations)
        
        self.update()

    def save_buffer_to_image(self):
        """Reads the content of the current buffer and stores it in a PIL image.
        Returns the image. """

        data = glReadPixels(0,0,self.WIN_WIDTH,self.WIN_HEIGTH, GL_RGBA, GL_UNSIGNED_BYTE)
        if data != None:
            image = Image.frombytes("RGBA", (self.WIN_WIDTH, self.WIN_HEIGTH), data)
            return image
        else:
            return

    def generate_two_colors(self):
        # Generate the primary hue
        hue = random.randint(0, 360)
        # Generate secondary hue
        hue_secondary = (hue-35)%360
        saturation = 0.55
        lightness = 0.45
        return colorsys.hls_to_rgb(hue/360, 1, saturation), colorsys.hls_to_rgb(hue_secondary/360, lightness, saturation)

    def display_new_city(self, size, city, city_map=None, stations_pos=None, stations_influence=None):
        """Compiles a new city with a certain total size.
        If the function receives a city_map it colors the city based on properties of the cell, 
        If the funtion receives stations_pos the function displays the stations and 
        If the function receives stations_influence, paints the influence. """
        
        self.SIZE = size
        self.city = city
        self.city_map = city_map
        self.stations_pos = stations_pos
        self.stations_influence = stations_influence

        self.set_cell_size(self.WIN_WIDTH, size)

        if city_map != None:
            self.compile_color_city(city, city_map)
        elif stations_pos != None and stations_influence != None:
            if self.cluster_colors == None:
                self.cluster_colors = [self.generate_two_colors() for _ in range(len(stations_pos))]
            self.compile_stations_influence(city, stations_pos, stations_influence)
        else:
            self.compile_city_drawing(city)

        self.displaying_city = True

    def set_cell_size(self, width, size):
        self.cell_size = width/(size*1.0)


    def display_vehicles(self, vehicles):
        """Sets the current list of vehicles.
        Gives a color to each vehicle. """
        
        self.vehicles = vehicles
        for v in self.vehicles:
            v.color = random.choice(self.colors)
        self.displaying_vehicles = True

    def display_stations(self, stations):
        """Compiles the graphic elements that represent th stations. """
        self.stations = stations
        self.displaying_stations = True
        self.compile_stations_drawing(stations)


    def compile_stations_drawing(self, stations):
        
        index = glGenLists(1)
        glNewList(index, GL_COMPILE)
        glLineWidth(6)
        for st in stations:
            i, j = st.cell.pos
            glColor3f(0.000, 0.502, 0.000)
            
            self.draw_outline(i*self.cell_size, j*self.cell_size,self.cell_size, self.cell_size)
        glLineWidth(1)
        glEndList()
        
        self.stations_drawing = index
    def compile_stations_influence(self, city, stations_pos, stations_influence):
        
        index = glGenLists(1)
        glNewList(index, GL_COMPILE)

        # Draw the background.

        for i in range(self.SIZE):
            for j in range(self.SIZE):
                if city[(i,j)] == 0:
                    glColor3f(0.0, 0.0, 0.0)
                    self.draw_rect(i*self.cell_size, j*self.cell_size,self.cell_size, self.cell_size)

                    
        # Draw the influence and the staions
        for colors, stations, influence in zip(self.cluster_colors, stations_pos, stations_influence):
            

            for pos in influence:
                (i,j) = pos
                glColor3f(*colors[1])
                # Draw a rectangle where the influenced position is
                self.draw_rect(i*self.cell_size, j*self.cell_size,self.cell_size, self.cell_size)
                # Draw a black outline of the station.
                glColor3f(0.0, 0.0, 0.0)
                self.draw_outline( i*self.cell_size, j*self.cell_size, self.cell_size, self.cell_size)

            for pos in stations:
                (i,j) = pos
                glColor3f(*colors[0])
                # Draw four white rectangles where the station is.
                glColor3f(*colors[0])
                self.draw_four_rect(i, j,self.cell_size, self.cell_size)
                
                # Draw a rectangle at the center of the station and create an outline.
                self.draw_rect(i*self.cell_size, j*self.cell_size,self.cell_size, self.cell_size)

                glColor3f(0.0, 0.0, 0.0)
                self.draw_outline( i*self.cell_size, j*self.cell_size, self.cell_size, self.cell_size)

        glEndList()
        self.city_drawing = index                               
    def compile_color_city(self, city, city_map):
        """Show the city with each cell type colored """
        index = glGenLists(1)
        glNewList(index, GL_COMPILE)
        
        for i in range(self.SIZE):
            for j in range(self.SIZE):
                if city[(i,j)] == 1:
                    # The cell belongs to the drivable set
                    cell = city_map[(i,j)]
                    if cell.cell_type == CellType.STREET:
                        glColor3f(*self.street_color)
                    elif cell.cell_type == CellType.AVENUE:
                        glColor3f(*self.avenue_color)
                    elif cell.cell_type == CellType.ROUNDABOUT:
                        glColor3f(*self.roundabout_color)

                    self.draw_rect(i*self.cell_size, j*self.cell_size,self.cell_size, self.cell_size)
                    glColor3f(0.0, 0.0, 0.0)
                    self.draw_outline( i*self.cell_size, j*self.cell_size, self.cell_size, self.cell_size)
                 


                else:
                    # Draw a black cell without outline
                    glColor3f(0.0, 0.0, 0.0)
                    self.draw_rect(i*self.cell_size, j*self.cell_size,self.cell_size, self.cell_size)

        glEndList()
        self.city_drawing = index  

    def compile_city_drawing(self, city):
        """For each cell in the city, if it is a house paint it black, else paint it white. """
        
        index = glGenLists(1)
        glNewList(index, GL_COMPILE)
        
        for i in range(self.SIZE):
            for j in range(self.SIZE):
                if city[(i,j)] == 1:
                    # Draw a white cell withe the outline in black
                    glColor3f(1.0, 1.0, 1.0)
                    self.draw_rect(i*self.cell_size, j*self.cell_size,self.cell_size, self.cell_size)
                    glColor3f(0.0, 0.0, 0.0)
                    self.draw_outline( i*self.cell_size, j*self.cell_size, self.cell_size, self.cell_size)
                else:
                    # Draw a black cell without outline
                    glColor3f(0.0, 0.0, 0.0)
                    self.draw_rect(i*self.cell_size, j*self.cell_size,self.cell_size, self.cell_size)

        glEndList()
        self.city_drawing = index  

    def draw_vehicles(self):
        """Draws the vehicles present in next_vehicles. The color of each is set when add_vehicles is
        called.  """
        for v in self.vehicles:
            
            glColor3f(*v.color) # Set the color to the vehicle's
            x, y = v.cell.pos # Retrieve the vehicle's position
            if v.state in self.moving_states:
                # If the vehicle is moving, paint a rectangle at the position of the vehicle with the vehicle's 
                # given color. It also adds a black outline around the rectangle to better identification.

                self.draw_rect(x*self.cell_size, y*self.cell_size,self.cell_size, self.cell_size) 
                glColor3f(0.0, 0.0, 0.0) # Draw the outline of the rectangle in black
                self.draw_outline(x*self.cell_size, y*self.cell_size, self.cell_size, self.cell_size)
            else:
                # If the vehicle is not moving just draw an outline with the vehicle's color and position.
                pass
                #self.draw_outline(x*self.cell_size, y*self.cell_size, self.cell_size, self.cell_size)

    def draw_four_rect(self, x, y, width, height):
        self.draw_rect((x+1)*self.cell_size, y*self.cell_size, width, height)
        self.draw_rect((x-1)*self.cell_size, y*self.cell_size, width, height)
        self.draw_rect(x*self.cell_size, (y+1)*self.cell_size, width, height)
        self.draw_rect(x*self.cell_size, (y-1)*self.cell_size, width, height)
    def draw_circle(self, x,y, r, sides):
        glBegin(GL_POLYGON)
        for s in range(0, sides):
            angle = float(s)*2*np.pi/sides
            p1 = r * np.cos(angle) + x
            p2 = r * np.sin(angle) + y
            glColor3f(1.0, 1.0, 1.0)
            glVertex2f(p1, p2)    
        
        glEnd()
    def draw_rect(self,x, y, width, height):
        """Draws a new rectangle """
        # start drawing a rectangle
        glBegin(GL_QUADS)
        glVertex2f(x, y)                                   # bottom left point
        glVertex2f(x + width, y)                           # bottom right point
        glVertex2f(x + width, y + height)                  # top right point
        glVertex2f(x, y + height)                          # top left point
    
        glEnd()

    def draw_outline(self, x, y, width, height):
        """Draws the outline of a rectangle  """
        # start drawing a rectangle
        glBegin(GL_LINE_STRIP)
        
        glVertex2f(x, y)                                   # bottom left point
        glVertex2f(x + width, y)                           # bottom right point
        glVertex2f(x + width, y + height)                  # top right point
        glVertex2f(x, y + height)                          # top left point
        glVertex2f(x, y)                                   # bottom left point
        
        glEnd()

    def refresh2d(self):
        """Sets the view to a 2D mode. """
        glViewport(0, 0, self.WIN_WIDTH, self.WIN_HEIGTH)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(0.0, self.WIN_WIDTH, 0.0, self.WIN_HEIGTH, 0.0, 1.0)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()


class VisualizationWindow(QMainWindow):
    def __init__(self, parent=None, flags=QtCore.Qt.WindowFlags()):
        super(VisualizationWindow, self).__init__(parent=parent, flags=flags)

        # Create a PyQT-GL object.
        self.opengl_animation = Animation()
        self.setCentralWidget(self.opengl_animation)


        self.setWindowTitle("Representación de la ciudad")
        self.live_analysis_window = None

        self.is_over_function = None
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.update_animation)

        # Restore the size
        self.settings = QSettings("MyCompany", "MyApp")
        if not self.settings.value("geometry") == None:
            self.restoreGeometry(self.settings.value("geometry"))
        if not self.settings.value("windowState") == None:
            self.restoreState(self.settings.value("windowState"))

    def show_new_city(self, size, city, city_map=None, stations_pos=None, stations_influence=None):
        self.opengl_animation.cluster_colors = None
        self.opengl_animation.display_new_city(size, city,city_map,stations_pos,stations_influence)
        self.opengl_animation.update()

    def start_animation(self, simulation, is_over_function):
        """Creates a QTimer that triggers the update of the animation. """
        self.simulation = simulation
        # Starting state of the simulation:
        # current_repetition, current_tstep, metrics, snapshot
        self.sim_data = (0, 0, None, None)
        self.is_over_function = is_over_function

        self.opengl_animation.display_new_city(self.simulation.SIZE, self.simulation.city_matrix)
        self.opengl_animation.display_stations(self.simulation.stations)
        self.opengl_animation.display_vehicles(self.simulation.vehicles)
        
        self.opengl_animation.update()

    def update_animation(self):

        self.sim_data = self.simulation.run_simulator_application(*self.sim_data)

        if self.sim_data == None:
            # The simulation is over
            self.is_over_function()
            
        self.opengl_animation.update()
        if self.live_analysis_window != None:
            self.live_analysis_window.update_values()

        
    def save_image(self):
        return self.opengl_animation.save_buffer_to_image()

    def closeEvent(self,cls):
        
        if self.live_analysis_window != None:
            self.live_analysis_window.destroy()

        if self.is_over_function:
            self.is_over_function()

        self.settings.setValue("geometry", self.saveGeometry())
        self.settings.setValue("windowState", self.saveState())
        return super().closeEvent(cls)
