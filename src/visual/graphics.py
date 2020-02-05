# -*- coding: utf-8 -*-
import random

from src.models.states import States

try:
    from tkinter import Canvas, Tk
except:
    from Tkinter import Canvas, Tk


class VisualObject(object):
    def __init__(self, cell_size):
        super().__init__()
        self.cell_size = cell_size
        self.rectangle = None


class VisualVehicle(VisualObject):
    def __init__(self, cell_size, vehicle, canvas, show_destination):
        super().__init__(cell_size)

        self.vehicle = vehicle
        self.last_position = None
        self.last_destination = None
        self.rectangle = None
        self.destination_rectangle = None
        self.colors = ["green", "blue", "orange", "purple"]
        self.canvas = canvas
        self.show_destination = show_destination

        self.restart()

    def choose_color(self):
        return random.choice(self.colors)

    def visual_destination(self, color):
        (i, j) = self.vehicle.destination
        p1 = (j*self.cell_size, i*self.cell_size)
        p2 = ((j+1)*self.cell_size, (i+1)*self.cell_size)
        visual_d = self.canvas.create_rectangle(
            p1[0], p1[1], p2[0], p2[1], fill='white', outline=color, width=3)
        return visual_d

    def move_vehicle(self, state):
        """Update the vehicle's rectangle placement and
        visibility (visual state) """
        dy = (self.vehicle.pos[0] - self.last_position[0]) * self.cell_size
        dx = (self.vehicle.pos[1] - self.last_position[1]) * self.cell_size
        self.canvas.move(self.rectangle, dx, dy)
        self.canvas.itemconfigure(self.rectangle, state=state)

        # update the attributes
        self.last_position = self.vehicle.pos

    def move_destination(self):
        """When the vehicle's destination changes, it must be updated """
        dy = (self.vehicle.destination[0] -
              self.last_destination[0]) * self.cell_size
        dx = (self.vehicle.destination[1] -
              self.last_destination[1]) * self.cell_size
        self.canvas.move(self.destination_rectangle, dx, dy)

        # Control de visibility of the destination frame
        if self.show_destination:
            self.canvas.itemconfigure(
                self.destination_rectangle, state='normal')
        else:
            self.canvas.itemconfigure(
                self.destination_rectangle, state='hidden')

        # update the attributes
        self.last_destination = self.vehicle.destination

    def restart(self):

        # Attribute to update the rectangle
        # and the visual_destination
        self.last_position = self.vehicle.pos
        self.last_destination = self.vehicle.destination

        # Create the rectangle
        x, y = self.vehicle.pos
        p1 = (y*self.cell_size, x*self.cell_size)
        p2 = ((y+1)*self.cell_size, (x+1)*self.cell_size)
        color = self.choose_color()

        self.rectangle = self.canvas.create_rectangle(
            p1[0], p1[1], p2[0], p2[1], fill=color)

        # Create the visual destination
        self.destination_rectangle = self.visual_destination(color)


class VisualRepresentation(object):
    def __init__(self, SIZE, WIN_WIDTH, WIN_HEIGTH, DELAY):
        # Constant attributes
        self.SIZE = SIZE
        self.WIN_WIDTH = WIN_WIDTH
        self.WIN_HEIGTH = WIN_HEIGTH
        self.cell_size = self.WIN_WIDTH/(self.SIZE*1.0)
        self.DELAY = DELAY
        # Visual Objects
        self.master = Tk()
        self.master.minsize(width=self.WIN_WIDTH+50,
                            height=self.WIN_HEIGTH+50)
        self.master.maxsize(width=self.WIN_WIDTH+50,
                            height=self.WIN_HEIGTH+50)
        self.canvas = Canvas(self.master, width=self.WIN_WIDTH,
                             height=self.WIN_HEIGTH, highlightthickness=0)
        self.canvas.pack()

        # Simualtion elements
        self.visual_vehicles = None

    def show_city(self, city, show_type=False):
        for i in range(self.SIZE):
            for j in range(self.SIZE):

                # Compute the coordinates of the square
                p1 = (j*self.cell_size, i*self.cell_size)
                p2 = ((j+1)*self.cell_size, (i+1)*self.cell_size)
                # Paint the rectangle according to the type of cell.
                if city[(i, j)][4] == 0:
                    # this is a house
                    self.canvas.create_rectangle(
                        p1[0], p1[1], p2[0], p2[1], fill='black')

                elif show_type:
                    # if show_type is enabled, each cell type will be painted
                    # on a different color
                    if city[(i, j)][4] == 1:
                        self.canvas.create_rectangle(
                            p1[0], p1[1], p2[0], p2[1], fill='yellow')
                    elif city[(i, j)][4] == 2:
                        self.canvas.create_rectangle(
                            p1[0], p1[1], p2[0], p2[1], fill='red')
                    else:
                        self.canvas.create_rectangle(
                            p1[0], p1[1], p2[0], p2[1], fill='blue')

                else:
                    # If this option is disabled, then every cell will be white
                    self.canvas.create_rectangle(
                        p1[0], p1[1], p2[0], p2[1], fill='white')
                # To place somenthing in the middle of a cell:
                # px = (p1[0] + (1.0*p2[0]-p1[0])/2, p1[1] + (1.0*p2[1]-p1[1])/2)
                # canvas.create_text(px, text=str(cityMap[(i,j)].distToStation))
        self.canvas.update()
       # ps = self.canvas.postscript(colormode="color")
       # im = Image.open(io.BytesIO(ps.encode('utf-8')))
       # im.save("city.png", quality=100)

    def show_components(self, segments):
        color = ["red", "green", "blue", "yellow",
                 "orange", "gray", "pink", "black"]

        for i in range(self.SIZE):
            for j in range(self.SIZE):
                p1 = (j*self.cell_size, i*self.cell_size)
                p2 = ((j+1)*self.cell_size, (i+1)*self.cell_size)
                in_segment = -1
                for (k, segment) in enumerate(segments):
                    if (i, j) in segment:
                        in_segment = k
                        break

                if in_segment != -1:
                    self.canvas.create_rectangle(
                        p1[0], p1[1], p2[0], p2[1], fill=color[k % len(color)])
                else:
                    self.canvas.create_rectangle(
                        p1[0], p1[1], p2[0], p2[1], fill='white')

    def show_vehicles(self, vehicles, show_destination=True):
        self.visual_vehicles = [VisualVehicle(
            self.cell_size, v, self.canvas, show_destination) for v in vehicles]
        self.canvas.update()

        # Hide the destination rectangle from the canvas
        if not show_destination:
            for visual_vehicle in self.visual_vehicles:
                self.canvas.itemconfigure(
                    visual_vehicle.destination_rectangle, state='hidden')

    def show_intensity(self, points):
        for point in points:
            (x, y) = point.int_point
            p1 = (y*self.cell_size, x*self.cell_size)
            p2 = ((y+1)*self.cell_size, (x+1)*self.cell_size)
            r = self.canvas.create_rectangle(p1[0], p1[1], p2[0], p2[1],
                                             outline="yellow", width=3,   fill='white')
            (x, y) = point.ext_point
            p1 = (y*self.cell_size, x*self.cell_size)
            p2 = ((y+1)*self.cell_size, (x+1)*self.cell_size)
            r = self.canvas.create_rectangle(p1[0], p1[1], p2[0], p2[1],
                                             outline="green", width=3,   fill='white')
            self.canvas.update_idletasks()

    def show_points(self, points):
        for (x, y) in points:

            p1 = (y*self.cell_size, x*self.cell_size)
            p2 = ((y+1)*self.cell_size, (x+1)*self.cell_size)
            r = self.canvas.create_rectangle(p1[0], p1[1], p2[0], p2[1],
                                             outline="purple", width=5, fill="white")

            self.canvas.update_idletasks()

    def update_vehicles(self):
        """For each VisualVehicle in the simulation, updates the vehicle's rectangle
        according to the state. It also updates the destination rectangle. """
        for visual_veh in self.visual_vehicles:
            if visual_veh.vehicle.state in States.idle_states():
                # The vehicle is not moving.
                visual_veh.move_vehicle(state='hidden')
                # Hide the destination rectangle
                self.canvas.itemconfigure(
                    visual_veh.destination_rectangle, state='hidden')
            elif visual_veh.vehicle.state == States.TOWARDS_DEST:

                # The vehicle is on the move
                visual_veh.move_vehicle(state='normal')

                if visual_veh.last_destination != visual_veh.vehicle.destination:
                    # Update the destination rectangle
                    visual_veh.move_destination()
                # else:
                #     # Make it visible
                #     self.canvas.itemconfigure(
                #         visual_veh.destination_rectangle, state='normal')
            elif visual_veh.vehicle.state == States.TOWARDS_ST:
                # The vehicle is on the move
                visual_veh.move_vehicle(state='normal')
                self.canvas.itemconfigure(
                    visual_veh.destination_rectangle, state='hidden')

        self.canvas.after(self.DELAY)
        self.canvas.update()

    def show_stations(self, stations):
        for s in stations:
            (i, j) = s.pos
            p1 = (j*self.cell_size, i*self.cell_size)
            p2 = ((j+1)*self.cell_size, (i+1)*self.cell_size)
            self.canvas.create_rectangle(
                p1[0], p1[1], p2[0], p2[1], fill='white', outline="red", width=3)

    def freeze(self):
        self.master.mainloop()
