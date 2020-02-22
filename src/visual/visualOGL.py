from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import random
import src.visual.colors as c
from src.models.states import States

#https: // noobtuts.com/python/opengl-introduction
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
class VisualRepresentation():
    def __init__(self, SIZE, WIN_WIDTH, WIN_HEIGTH, DELAY, city):
        super().__init__()

        # Constant attributes
        self.SIZE = SIZE
        self.WIN_WIDTH = WIN_WIDTH
        self.WIN_HEIGTH = WIN_HEIGTH
        self.cell_size = self.WIN_WIDTH/(self.SIZE*1.0)
        self.DELAY = DELAY
        self.current_tstep = 0

        self.create_GLU()
        self.city = city
        self.black_cells = []
        self.white_cells = []

        for i in range(self.SIZE):
            for j in range(self.SIZE):
                if self.city[(i, j)][4] == 0:
                    self.black_cells.append((i,j))
                        
                else:
                    self.white_cells.append((i,j))

        self.cityVertexList = self.compile_city_drawing()

        self.colors = [c.red, c.green, c.blue, c.magenta, c.gold]
        self.vehicles = None
        self.next_vehicles = []
        
        
        
            
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

        # Draw the black cells
        glColor3f(0.0, 0.0, 0.0)
        for (i,j) in self.black_cells:
            self.draw_rect(i*self.cell_size, j*self.cell_size,self.cell_size, self.cell_size)

        # Draw white cells
        glColor3f(1.0, 1.0, 1.0)
        for (i,j) in self.white_cells:
            
            self.draw_rect(i*self.cell_size, j*self.cell_size,self.cell_size, self.cell_size)
        # Draw the outline of the rectangle in black
        for (i,j) in self.white_cells:
            glColor3f(0.0, 0.0, 0.0)
            self.draw_outline( i*self.cell_size, j*self.cell_size, self.cell_size, self.cell_size)

        glEndList()
        return index    

    def draw_vehicles(self):
        """Draws the vehicles present in next_vehicles. The color of each is set when add_vehicles is
        called.  """
        for v in self.next_vehicles:
            
            glColor3f(*v.color) # Set the color to the vehicle's
            x, y = v.pos # Retrieve the vehicle's position
            self.draw_rect(x*self.cell_size, y*self.cell_size,self.cell_size, self.cell_size) # Paint a rectangle in the vehicle's position.
            # Draw the outline of the rectangle in black
            glColor3f(0.0, 0.0, 0.0)
            self.draw_outline(x*self.cell_size, y*self.cell_size, self.cell_size, self.cell_size)

            
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

    def draw(self):     
        """Function called when we want to draw a new frame. """
                                              
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)  # clear the screen
        glLoadIdentity()                                   # reset position
        self.refresh2d()                           # set mode to 2d

        glCallList(self.cityVertexList)   # Always draw the city        
        self.draw_vehicles()

        glutSwapBuffers()  # important for double buffering

        return 

    def refresh2d(self):
        """Sets the view to a 2D mode. """
        glViewport(0, 0, self.WIN_WIDTH, self.WIN_HEIGTH)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(0.0, self.WIN_WIDTH, 0.0, self.WIN_HEIGTH, 0.0, 1.0)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

    def create_GLU(self):
        """Create the OpenGL window, setting the height and width and more properties. """
        enable_vsync()
        window = 0                                             # glut window number
        glutInit()                                             # initialize glut
        glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE | GLUT_ALPHA | GLUT_DEPTH)
        glutInitWindowSize(self.WIN_WIDTH, self.WIN_HEIGTH)                      # set window size
        glutInitWindowPosition(0, 0)                           # set window position
        # create window with title
        window = glutCreateWindow("SIMTRAVEL: visual representation")

    def update(self):
        """"When this function is called, we update the list of vehicles we want to 
        draw and force the drawing of a new frame. """
        # Select the vehicles we want to draw
        self.next_vehicles = [v for v in self.vehicles if v.state in States.moving_states()]
        # Force the update of the display.
        glutPostRedisplay()

    def beginRepresentation(self, nextframe):
        """This function sets the callback functions to draw and update the frames, 
        it also starts the main loop. """
        glutDisplayFunc(self.draw)  # set draw function callback
        glutIdleFunc(nextframe)  # compute the next step of the simulation
        glutMainLoop()
