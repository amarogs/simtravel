import random

from OpenGL.GL import *
from PyQt5 import Qt, QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import *

import src.visual.colors as c
from src.models.states import States
from src.models.cities import SquareCity

class Animation(QOpenGLWidget):

    def __init__(self):
        super(Animation, self).__init__()

        # This attributes are set when resizeGL is called.
        self.WIN_WIDTH = None
        self.WIN_HEIGTH = None
        self.SIZE = None
        self.cell_size = None

        #Flags that control what is being displayed
        self.displaying_city = False
        self.displaying_stations = False
        

    def set_cell_size(self, width, size):
        self.cell_size = width/(size*1.0)

        
    def paintGL(self):
        """Renders the OpenGL scene. Gets called whenever the widget needs to be updated."""
        self.draw()

    def display_new_city(self, size, city):
        """Renders the a city that has a certain size. """
        self.SIZE = size
        self.city = city
        self.set_cell_size(self.WIN_WIDTH, size)
        self.compile_city_drawing(size, city)
        self.displaying_city = True
        self.update()
        
    def draw(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)  # clear the screen
        glLoadIdentity()                                   # reset position
        self.refresh2d()   # set mode to 2d
        
        if self.displaying_city:
            glCallList(self.city_drawing)   
            if self.displaying_stations:
                glCallList(self.stations_drawing)

    def resizeGL(self, width, heigth):
        """Sets up the OpenGL viewport, projection, etc. Gets called whenever the 
        widget has been resized (and also when it is shown for the first time 
        because all newly created widgets get a resize event automatically) """
        print("He resizado")
        
        if width > heigth:
            side = heigth
        else:
            side = width

        
        
        side = int(self.devicePixelRatio()*side)
        
        self.WIN_HEIGTH, self.WIN_WIDTH = side, side
        
        
    def compile_stations_drawing(self, stations):
        self.displaying_stations = True

        index = glGenLists(1)
        glNewList(index, GL_COMPILE)
        glLineWidth(3)
        for st in stations:
            i, j = st.cell.pos
            glColor3f(0.000, 0.502, 0.000)
            
            self.draw_outline(i*self.cell_size, j*self.cell_size,self.cell_size, self.cell_size)
        glLineWidth(1)
        glEndList()
        
        self.stations_drawing = index

    def compile_city_drawing(self, size, city):
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


# enable highdpi scaling
QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)  
app = QApplication([])
app.setApplicationName("SIMTRAVEL")
main_window = QMainWindow()
city_visualization = Animation()

window = QWidget()
main_window.setCentralWidget(window)
def show_city():
    city = SquareCity(RB_LENGTH=random.choice([6,8,10]), AV_LENGTH=4*random.choice([5,7,9,11]), SCALE=2)
    city_visualization.display_new_city(city.SIZE, city.city_matrix)
            
button = QPushButton("Ciudad")
button.clicked.connect(show_city)
layout = QVBoxLayout()
layout.addWidget(city_visualization)
layout.addWidget(button)
window.setLayout(layout)
main_window.show()
app.exec_()