from OpenGL.GL import *
from PyQt5.QtWidgets import QApplication, QHBoxLayout, QOpenGLWidget, QSlider, QWidget
import random

import src.visual.colors as c
from src.models.states import States


import sys


def enable_vsync():
    if sys.platform != 'darwin':
        return
    try:
        import ctypes
        import ctypes.util
        ogl = ctypes.cdll.LoadLibrary(ctypes.util.find_library("OpenGL"))
        v = ctypes.c_int(1)

        ogl.CGLGetCurrentContext.argtypes = []
        ogl.CGLGetCurrentContext.restype = ctypes.c_void_p

        ogl.CGLSetParameter.argtypes = [
            ctypes.c_void_p, ctypes.c_int, ctypes.c_void_p]
        ogl.CGLSetParameter.restype = ctypes.c_int

        context = ogl.CGLGetCurrentContext()

        ogl.CGLSetParameter(context, 222, ctypes.pointer(v))
    except Exception as e:
        print("Unable to set vsync mode, using driver defaults: {}".format(e))



class VisualRepresentation(QOpenGLWidget):
    def __init__(self, SIZE, DELAY, city, parent, hdpi):
        super().__init__(parent)
        # Constant attributes
        self.SIZE = SIZE
        self.hdpi = hdpi
        self.DELAY = DELAY
        self.current_tstep = 0

        # Attributes set by the resizeGL() method
        self.WIN_WIDTH = None
        self.WIN_HEIGTH = None
        self.cell_size = None

             
        # Attributes to create the city and vehicles.
        self.city = city
        self.colors = [c.red, c.green, c.blue, c.magenta, c.gold]
        self.vehicles = []
        self.next_vehicles = []
        

    def initializeGL(self):
        """Sets up the OpenGL resources and state"""
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)  # clear the screen
        
    def paintGL(self):
        """Renders the OpenGL scene. Gets called whenever the widget needs to be updated."""
        # Select the vehicles we want to draw
        self.next_vehicles = [ v for v in self.vehicles if v.state in States.moving_states()]
        self.draw()

    def resizeGL(self, width, heigth):
        """Sets up the OpenGL viewport, projection, etc. Gets called whenever the 
        widget has been resized (and also when it is shown for the first time 
        because all newly created widgets get a resize event automatically) """
        magnification = 1
        if self.hdpi:
            magnification = 2

        self.WIN_WIDTH = int((10/10)*magnification*width)
        self.WIN_HEIGTH = int((10/10)*magnification*heigth)
        self.cell_size = self.WIN_WIDTH/(self.SIZE*1.0)
        self.refresh2d()
        self.cityVertexList = self.compile_city_drawing()
        

    def add_vehicles(self, vehicles):
        """Set the list of vehicles  """
        self.vehicles = vehicles
        for v in self.vehicles:
            # v.state = States.TOWARDS_DEST
            v.color = random.choice(self.colors)

    def compile_city_drawing(self):
        """For each cell in the city, if it is a house paint it black, else paint it white. """
        index = glGenLists(1)
        glNewList(index, GL_COMPILE)

        for i in range(self.SIZE):
            for j in range(self.SIZE):
                
                if self.city[(i,j)][4] == 0:
                    
                    # Draw a black cells
                    glColor3f(0.0, 0.0, 0.0)
                    self.draw_rect(i*self.cell_size, j*self.cell_size, self.cell_size, self.cell_size)
                else:
                    # Draw a white cell
                    glColor3f(1.0, 1.0, 1.0)
                    self.draw_rect(i*self.cell_size, j*self.cell_size,self.cell_size, self.cell_size)
                    # Draw the outline of the rectangle in black
                    glColor3f(0.0, 0.0, 0.0)
                    self.draw_outline(i*self.cell_size, j*self.cell_size, self.cell_size, self.cell_size)

        glEndList()
        return index

    def draw_vehicles(self):
        """Draws the vehicles present in next_vehicles. The color of each is set when add_vehicles is
        called.  """
        for v in self.next_vehicles:

            glColor3f(*v.color)  # Set the color to the vehicle's
            x, y = v.pos  # Retrieve the vehicle's position
            # Paint a rectangle in the vehicle's position.
            self.draw_rect(x*self.cell_size, y*self.cell_size,
                           self.cell_size, self.cell_size)
            # Draw the outline of the rectangle in black
            glColor3f(0.0, 0.0, 0.0)
            self.draw_outline(x*self.cell_size, y*self.cell_size,
                              self.cell_size, self.cell_size)

    def draw_rect(self, x, y, width, height):
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

    def draw(self):
        """Function called when we want to draw a new frame. """

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)  # clear the screen
        glLoadIdentity()                                   # reset position
        self.refresh2d()                           # set mode to 2d

        glCallList(self.cityVertexList)   # Always draw the city
        self.draw_vehicles()
        return

    def refresh2d(self):
        """Sets the view to a 2D mode. """
        glViewport(0, 0, self.WIN_WIDTH, self.WIN_HEIGTH)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(0.0, self.WIN_WIDTH, 0.0, self.WIN_HEIGTH, 0.0, 1.0)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()


        
        
    

        
        

