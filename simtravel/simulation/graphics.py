from parameters import *
import random

try:
    from tkinter import Canvas, Tk
except:
    from Tkinter import Canvas, Tk


class VisualRepresentation(object):
    def __init__(self, city, SIZE, vehicles, stations):
        # Constant attributes
        self.SIZE = SIZE
        self.WIN_WIDTH = WIDTH
        self.WIN_HEIGHT = HEIGHT
        self.cell_size = self.WIN_WIDTH/(self.SIZE*1.0)

        # Visual Objects
        self.master = Tk()
        self.master.minsize(width=self.WIN_WIDTH+50,
                            height=self.WIN_HEIGHT+50)
        self.master.maxsize(width=self.WIN_WIDTH+50,
                            height=self.WIN_HEIGHT+50)
        self.canvas = Canvas(self.master, width=self.WIN_WIDTH,
                             height=self.WIN_HEIGHT, highlightthickness=0)
        self.canvas.pack()

        # Simualtion elements
        self.city = city
        self.vehicles = vehicles
        self.stations = stations

        self.rect_vehicles = []
        self.old_position = []
        self.rect_destination = []
        self.old_destinations = []

    def show_city(self, show_type=False):
        for i in range(self.SIZE):
            for j in range(self.SIZE):

                # Compute the coordinates of the square
                p1 = (j*self.cell_size, i*self.cell_size)
                p2 = ((j+1)*self.cell_size, (i+1)*self.cell_size)
                # Paint the rectangle according to the type of cell.
                if self.city[(i, j)][4] == 0:
                    # this is a house
                    self.canvas.create_rectangle(
                        p1[0], p1[1], p2[0], p2[1], fill='black')

                elif show_type:
                    # if show_type is enabled, each cell type will be painted
                    # on a different color
                    if self.city[(i, j)][4] == 1:
                        self.canvas.create_rectangle(
                            p1[0], p1[1], p2[0], p2[1], fill='yellow')
                    elif self.city[(i, j)][4] == 2:
                        self.canvas.create_rectangle(
                            p1[0], p1[1], p2[0], p2[1], fill = 'red')
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
        color=["red", "green", "blue", "yellow",
                 "orange", "gray", "pink", "black"]

        for i in range(self.SIZE):
            for j in range(self.SIZE):
                p1=(j*self.cell_size, i*self.cell_size)
                p2=((j+1)*self.cell_size, (i+1)*self.cell_size)
                in_segment=-1
                for (k, segment) in enumerate(segments):
                    if (i, j) in segment:
                        in_segment=k
                        break

                if in_segment != -1:
                    self.canvas.create_rectangle(
                        p1[0], p1[1], p2[0], p2[1], fill=color[k % len(color)])
                else:
                    self.canvas.create_rectangle(
                        p1[0], p1[1], p2[0], p2[1], fill='white')

    def place_vehicles(self):
        colors=["green", "blue", "orange", "purple"]
        for vehicle in self.vehicles:
            x, y=vehicle.pos
            p1=(y*self.cell_size, x*self.cell_size)
            p2=((y+1)*self.cell_size, (x+1)*self.cell_size)
            choice=random.choice(colors)
            r=self.canvas.create_rectangle(p1[0], p1[1], p2[0], p2[1],
                                             fill=choice)
            self.rect_vehicles.append(r)
            self.old_position.append(vehicle.pos)

            (i, j)=vehicle.destination
            p1=(j*self.cell_size, i*self.cell_size)
            p2=((j+1)*self.cell_size, (i+1)*self.cell_size)
            d=self.canvas.create_rectangle(
                p1[0], p1[1], p2[0], p2[1], fill='white', outline=choice, width=3)

            self.rect_destination.append(d)
            self.old_destinations.append(vehicle.destination)
            self.canvas.update_idletasks()

    def show_intensity(self, points):
        for point in points:
            (x, y)=point.int_point
            p1=(y*self.cell_size, x*self.cell_size)
            p2=((y+1)*self.cell_size, (x+1)*self.cell_size)
            r=self.canvas.create_rectangle(p1[0], p1[1], p2[0], p2[1],
                                             outline="yellow", width=3,   fill='white')
            (x, y)=point.ext_point
            p1=(y*self.cell_size, x*self.cell_size)
            p2=((y+1)*self.cell_size, (x+1)*self.cell_size)
            r=self.canvas.create_rectangle(p1[0], p1[1], p2[0], p2[1],
                                             outline="green", width=3,   fill='white')
            self.canvas.update_idletasks()

    def show_points(self, points):
        for (x, y) in points:

            p1=(y*self.cell_size, x*self.cell_size)
            p2=((y+1)*self.cell_size, (x+1)*self.cell_size)
            r=self.canvas.create_rectangle(p1[0], p1[1], p2[0], p2[1],
                                             outline="purple", width=5, fill="white")

            self.canvas.update_idletasks()

    def update_vehicles(self, vehicles):
        for (rect, old_pos, vehicle, dest, old_dest) in zip(self.rect_vehicles, self.old_position, vehicles, self.rect_destination, self.old_destinations):
            if vehicle.state in [1, 3, 4]:
                self.canvas.itemconfigure(rect, state='hidden')
                dy=(vehicle.pos[0] - old_pos[0]) * self.cell_size
                dx=(vehicle.pos[1] - old_pos[1]) * self.cell_size
                self.canvas.move(rect, dx, dy)

            else:
                if old_dest != vehicle.destination:
                    dy=(vehicle.destination[0] -
                          old_dest[0]) * self.cell_size
                    dx=(vehicle.destination[1] -
                          old_dest[1]) * self.cell_size

                    self.canvas.move(dest, dx, dy)
                if vehicle.state in [2, 3, 4]:
                    # Hide the destination when the vehicle is dealing with a station
                    self.canvas.itemconfigure(dest, state='hidden')
                else:
                    self.canvas.itemconfigure(dest, state='normal')

                # Move the vehicle to a new position
                self.canvas.itemconfigure(rect, state='normal')
                dy=(vehicle.pos[0] - old_pos[0]) * self.cell_size
                dx=(vehicle.pos[1] - old_pos[1]) * self.cell_size
                self.canvas.move(rect, dx, dy)

        self.old_position=[v.pos for v in vehicles]
        self.old_destinations=[v.destination for v in vehicles]

        self.canvas.after(DELAY)
        self.canvas.update()

    def show_stations(self):
        for s in self.stations:
            (i, j)=s.pos
            p1=(j*self.cell_size, i*self.cell_size)
            p2=((j+1)*self.cell_size, (i+1)*self.cell_size)
            self.canvas.create_rectangle(
                p1[0], p1[1], p2[0], p2[1], fill='white', outline="red", width=3)

    def freeze(self):
        self.master.mainloop()
