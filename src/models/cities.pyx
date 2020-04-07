from enum import Enum

import numpy as np

from src.simulator.cythonGraphFunctions import (configure_lattice_size,lattice_distance)



class CellType(Enum):
    HOUSE = 0
    AVENUE = 4
    STREET = 5
    ROUNDABOUT = 6

    def __eq__(self, other):
        return self.value == other

    def __ne__(self, other):
        return self.value != other

class Cell():
    
    def __init__(self, pos,cell_type,successors, prio_successors, direction, predecessors=None, prio_predecessors=None ):
        self.pos = pos
        self.successors = successors
        self.prio_successors = prio_successors
        self.predecessors = predecessors or []
        self.prio_predecessors = prio_predecessors or []
        self.r = []
        self.cell_type = cell_type.value
        self.direction = direction
        self.occupied = False
        
    def duplicate_cell(self, dx, dy, total_size):
        """Given a displacement (dx, dy) creates a copy of this cell but shifted the amount passed
        as argument.
        Returns a tuple (new position, new cell) """
        
        new_pos = (self.pos[0] + dx)%total_size, (self.pos[1] + dy)%total_size
        new_sucessors = self.move_cell(dx, dy, self.successors, total_size)
        new_prio_sucessors = self.move_cell(dx, dy, self.prio_successors, total_size)
        new_predecessors = self.move_cell(dx, dy, self.predecessors, total_size)
        new_prio_predecessors = self.move_cell(dx, dy, self.prio_predecessors, total_size)
        
        return new_pos, Cell(new_pos, CellType(self.cell_type), new_sucessors, new_prio_sucessors, self.direction, new_predecessors, new_prio_predecessors)

    def move_cell(self, dx, dy, positions, total_size):
        return [ ( (pos[0]+dx)%total_size, (pos[1]+dy)%total_size) for pos in positions]
    def __gt__(self, other):
        return self.pos > other
    def __ge__(self, other):
        return self.pos >= other
    def __lt__(self, other):
        return self.pos < other
    def __le__(self, other):
        return self.pos <= other


    def __str__(self):
        return "C:"+str(self.pos)
    def __repr__(self):
        return self.__str__()

class CityBuilder():
    
    # define the cardinal direction in Z4.
    N,E,S,W = 0,1,2,3

    def __init__(self):
        super().__init__()
        self.cells = []
        self.move_towards = {self.N:self.north_of, self.S:self.south_of, self.E:self.east_of, self.W:self.west_of}
        self.direction_vectors = {self.N:(-1, 0), self.S:(1,0), self.E:(0,1), self.W:(0,-1)}
        self.direction_towards ={(-1,0):self.N, (1,0):self.S, (0,1):self.E, (0,-1):self.W}

    def next_cell_of(self, x, y, *direction):
        """Given a position (x,y) and a variable amount of directions, compute
        those directions and return the cell. """
        for d in direction:
            x , y = self.move_towards[d](x,y)
        return (x,y)

    def north_of(self, x, y):
        """Given a position (x,y) return the following cell in the 
        north direction """
        return (x-1, y)
    def south_of(self, x,y):
        """Given a position (x,y) return the following cell in the 
        south direction """
        return (x+1, y)
    def east_of(self, x, y):
        """Given a position (x,y) return the following cell in the 
        east direction """
        return (x, y+1)
    def west_of(self, x, y):
        """Given a position (x,y) return the following cell in the 
        west direction """
        return (x, y-1)
    def exit_of(self, x, y, direction):
        """"Given a position (x,y) and the direction,
         returns the position of the cell to the right."""
        return self.next_cell_of(x,y, direction, (direction+1)%4)
    def entrance_of(self, x, y, direction):
        """Given a position (x,y) and the direction, returns the 
        position of the cell that enters to (x,y). It is going Back, and Right """
        return self.next_cell_of(x,y, (direction-2)%4, (direction-1)%4 )

    def leads_to(self, x,y, direction, lx, ly):
        """Given a position (x,y) and a direction. Tests, wheter
        following the direction, the next cell is (lx, ly). """
        next_pos = self.next_cell_of(x, y, direction)
        
        return next_pos[0] == lx and next_pos[1] == ly

    def direction_of(self, x_curr,y_curr,x_next, y_next):
        dx = x_next-x_curr
        dy = y_next-y_curr
        return self.direction_towards[(dx,dy)]
    def __str__(self):
        return str(self.cells)

    def __repr__(self):
        return self.__str__()      

class Street(CityBuilder):
    def __init__(self, x, y, direction, length):
        """(x,y) is the position of the first cell in the street.
            Direction is either N, S, E, W (0,1,2,3)
            length is the total number of cells in that street. """
        super().__init__()
        self.cells = []
        for _ in range(length):
            # Compute the position of the next cell
            next_cell_pos = self.next_cell_of(x,y,direction)
            # Create the current cell
            c = Cell((x,y), CellType.STREET, [next_cell_pos], [next_cell_pos], direction)
            self.cells.append(c)
            # Update the (x,y) to point to the new position
            x, y = next_cell_pos

        

        self.start = self.cells[0]
        self.end = self.cells[-1]



class SemiAvenueInt(CityBuilder):
    def __init__(self, x, y,direction,length, change=1):
        """length is the length of the semi-avenue, this means that it must be
        connected with another semi-avenue to form a complete avenue. """
        super().__init__()
        self.cells = []
        
        for _ in range(length):
            # Compute the cell in front of (x,y)
            next_cell_pos = self.next_cell_of(x,y,direction)
            # Compute the cell to the right of (x,y)
            change_cell = self.next_cell_of(*next_cell_pos, (direction+change)%4)
            # Create the cell object 
            c = Cell((x,y), CellType.AVENUE, [next_cell_pos, change_cell], [next_cell_pos], direction)
            self.cells.append(c)
            # update the value of x,y
            x, y = next_cell_pos
        
        # self.cells.append(Cell((x,y), CellType.AVENUE, [], []))

        self.start, self.end = self.cells[0], self.cells[-1]
    

class SemiAvenueExt(SemiAvenueInt):
    def __init__(self, x, y, direction, length):
        super().__init__(x, y, direction, length, change=-1)
        
        midpoint = length//2
        # Set the exit
        avenue_cell = self.cells[midpoint + (midpoint//2) - 1] 
        self.create_exit_of(avenue_cell, direction)

        # Set the entrance
        avenue_cell = self.cells[(midpoint//2)-1]        
        self.create_entrance_of(avenue_cell, direction)

    def create_entrance_of(self, avenue_cell, direction):
        entrance_pos = self.exit_of(*avenue_cell.pos, direction)
        entrance_sucessor = self.exit_of(*entrance_pos, (direction-1)%4)
        c = Cell(entrance_pos, CellType.STREET, [entrance_sucessor], [], (direction-1)%4 )
        self.cells.append(c)
        self.entrance = [c]

    def create_exit_of(self, avenue_cell, direction):
        exit_pos = self.exit_of(*avenue_cell.pos, direction)
        # update its information
        avenue_cell.successors.append(exit_pos)
        avenue_cell.prio_successors.append(exit_pos)

        # Create the exit cell
        next_cell = self.next_cell_of(*exit_pos, (direction+1)%4 ) 
        c = Cell(exit_pos, CellType.STREET,[next_cell],[next_cell], (direction+1)%4)
        self.cells.append(c)
        self.exit = [c]

class Roundabout(CityBuilder):
    """Creates a rotary that has in each side 2 avenue exit lanes and 2 avenue entrance lanes.
    The minimum length for it to work is 6. """
    def __init__(self, x, y, length, special_cell_type=CellType.ROUNDABOUT):
        super().__init__()
        self.special_cell_type = special_cell_type 
        self.exit, self.entrance = [], []
        self.internal_av_entr, self.external_av_entr = [], []
        self.internal_av_exit, self.external_av_exit = [],[]
        self.create_rotary_of(x,y,length)
        
        self.give_way_internal_avenue()


    def give_way_internal_avenue(self):
        """For each pair of avenues entrances, make the cell in the internal avenue give way
        to the external cell. Like any priority list made in the constructor, this is 
        made through a reference to the cell position and not the actual cell. """
 
        for int_av, ext_av in zip(self.internal_av_entr, self.external_av_entr):
 
            successor_pos = int_av.successors[0]
            successor_cell = [c for c in self.cells if c.pos == successor_pos][0]
            successor_cell.prio_predecessors.append(self.exit_of(*int_av.pos, int_av.direction))
            
            

    def rotary_segment_of(self,x,y,direction,length):
        """Creates a side of the rotary. Each side has a number of cells leading one to 
        the next and 4 special cells. 2 avenue exits made at positions 0 and 1,
        2 avenue entrances at positions length -3, and length -2. """

        for i in range(length -1):
            # Compute the sucessor
            next_pos = self.next_cell_of(x,y,direction)
            successors = [next_pos]
            

            # Create a external avenue exit
            if i == 0:
                exit_sucessor = self.create_exit_of(x,y, direction, external=True)
                successors.append(exit_sucessor)
            elif i == 1:
                # Create an internal avenue exit
                exit_sucessor = self.create_exit_of(x,y, direction, external=False)
                successors.append(exit_sucessor)

            elif i ==length-3:
                # Create a rotary entrance
                self.create_entrance_of(x, y, direction, external=False)

            elif i==length-2:
                # Create a rotary entrance
                self.create_entrance_of(x, y, direction, external=True)

            # Create the main rotary cell with all the successors.
            c = Cell((x,y), CellType.ROUNDABOUT, successors, successors, direction)
            self.cells.append(c)
            x, y = next_pos

        return x, y

    def create_entrance_of(self, x, y, direction, external=True):
        entrance_pos = self.next_cell_of(x,y,(direction+1)%4)
        entrance_dir = (direction - 1)% 4 
        if external:
            c = Cell(entrance_pos, self.special_cell_type, [self.exit_of(*entrance_pos, entrance_dir)], [], entrance_dir)
        else:
            c = Cell(entrance_pos, self.special_cell_type, [self.next_cell_of(*entrance_pos, entrance_dir)], [], entrance_dir)
        # Append the cells to the list of entrance cells and total cells of the roundabout
        self.entrance.append(c)
        self.cells.append(c)

        # Sort the cells into external and internal avenues entrances
        if external:
            self.external_av_entr.append(c)
        else:
            self.internal_av_entr.append(c)


        return 

    def create_exit_of(self, x, y, direction, external=True):
        exit_position = self.exit_of(x,y,direction)
        next_cell = self.next_cell_of(*exit_position, (direction+1)%4)
        c = Cell(exit_position, self.special_cell_type, [next_cell], [next_cell], (direction+1)%4)
        # Append the cells to the list of exit cells and total cells of roundabout.
        self.exit.append(c)
        self.cells.append(c)
        # Sort the cell into extenal and internal avenues.
        if external: 
            self.external_av_exit.append(c)
        else:
            self.internal_av_exit.append(c)

        return exit_position

    def create_rotary_of(self, x,y, length):
        """Given a position (x,y), the length  of the rotary and
        if we want ot create exits to the right, creates a rotary and stores it
        in self.cells. """
        for i in range(4):
            x, y = self.rotary_segment_of(x, y, (2-i)%4, length)

class RoadIntersection(CityBuilder):
    def __init__(self, c_x, c_y, directions):
        super().__init__()
        cell_order = [self.W, self.S, self.E, self.N]
        cell_order = [self.direction_vectors[k] for k in cell_order]
        self.exit = []

        # First create the 4 cells N, W, E, S
        for i, v in enumerate(cell_order):
            x, y = c_x + v[0], c_y + v[1]
            
            cell_direction = directions[i]
            sucessors = [self.next_cell_of(x,y, cell_direction)]
            
            if self.is_entrance(x,y,cell_direction, c_x, c_y):
                # This cell is an intersection entrance, now we have to check wheter
                # it has priority or not.   
                index_right = (i+1)%4
                right_vector = cell_order[index_right]
                x_right, y_right = c_x + right_vector[0], c_y + right_vector[1]

                if self.is_entrance(x_right, y_right,directions[index_right], c_x, c_y):
                    # This cell must give way since the cell in its right is an entrance
                    c = Cell((x,y), CellType.STREET,sucessors, [],cell_direction)
                    self.cells.append(c)
                else:
                    # This cell has priority over the right cell.
                    c = Cell((x,y), CellType.STREET,sucessors, sucessors,cell_direction)
                    self.cells.append(c)

            else:
                # This cell is an intersection exit.
                c = Cell((x,y), CellType.STREET,sucessors, sucessors,cell_direction)
                self.cells.append(c)
                self.exit.append(c)
        # Now create the center cell, connecting it with the exits.
        c = Cell((c_x, c_y), CellType.STREET, [c.pos for c in self.exit], [c.pos for c in self.exit], -1)
        self.cells.append(c)

    def is_entrance(self, x,y, direction, center_x, center_y):
        """Returns True if the cell (x,y) following that direction
        leads to (center_x, center_y). """ 
        return self.leads_to(x,y,direction, center_x, center_y)
class Intersection(Roundabout):
    """Creates an intersection wich is made out of a rotary plus 4 special cells. """
    def __init__(self, x, y, length, special_directions ):
        """(x,y) is the position of the center of the rotary
        length is the total length of one side of the rotary.
        special directions is a list of 4 directions, one per special cell starting from the 
        leftmost cell and counter clockwise """
        
        # Create a roundabout 
        
        self.special_directions = special_directions
        self.special_index = 0

        x, y = x - (length//2), y - (length//2) 
        super().__init__(x, y, length=length, special_cell_type=CellType.STREET)

        # Modify some attributes

    def rotary_segment_of(self, x, y,direction, length):
        for i in range(length-1):
            # Compute the sucessor
            next_pos = self.next_cell_of(x,y,direction)
            successors = [next_pos]

            if i == (length//2) - 1:
                # This is a cell that leads to a special one.
                if (direction + 1)%4 == self.special_directions[self.special_index]:
                    exit_sucessor = self.create_exit_of(x,y, direction)
                    successors.append(exit_sucessor)

                    # Increment the index for the next special cell direction
                    self.special_index += 1
                else:
                    
                    self.create_entrance_of(*self.next_cell_of(x,y,direction), direction)
                    # Increment the index for the next special cell direction
                    self.special_index += 1
            # Create the main rotary cell with all the successors.
            c = Cell((x,y), CellType.ROUNDABOUT, successors, successors,direction)
            self.cells.append(c)
            x, y = next_pos   
        return x,y


class SquareCity(CityBuilder):
    def __init__(self, RB_LENGTH, AV_LENGTH, SCALE, INTERSEC_LENGTH=3 ):
        super().__init__()
        """RB_LENGTH: Is the length of the side of the roundabout rotary. The minimum for 
        it to work must be 6, any even number greater that 6 is valid.

        AV_LENGTH: Is the length of a strip of avenue. It is the length from a roundabout to 
        the next roundabout.

        INTERSEC_LENGTH: Is the length of the side of the intersection rotary. The minimum number
        for it to work must be 3, any odd number greater thar 3 is valid.  """
        
        
        
        self.base_size = RB_LENGTH + 2 + AV_LENGTH
        self.SIZE = self.base_size * SCALE
        self.scale = SCALE
        reference = (AV_LENGTH//2 + 1, AV_LENGTH//2 +1)
        
        # Define the attributes for the intersections
        base = np.array([AV_LENGTH/8, AV_LENGTH/8])        
        inter_coord = np.array([ [1, 1], [1, 3], [3, 1], [3, 3] ], dtype="float32") * base
        # Intersections are given by row: first the intersection of the first row, then the second row.
        # Each lists starts with the leftmost cell.
        inter_dirs = np.array([ [3,2,3,2], [3,0,3,0], [1,2,1,2], [1,0,1,0]])
        inter_dirs = (inter_dirs+2)%4

        next_cuadrant = (AV_LENGTH//2) + RB_LENGTH + 2
        inter_offset = np.array([[0,0], [0,next_cuadrant], [next_cuadrant, 0], [next_cuadrant,next_cuadrant]])

        # Define the global attributes.
        self.base_city = {}
        
        

        # Create the external roundabout rotary
        rb = Roundabout(*reference, RB_LENGTH)
        for c in rb.cells:
            self.base_city[c.pos] = c
            

        # Create the exit avenues, internal and external.
        exit_cells = []
        for cell in rb.exit:
            
            if cell in rb.external_av_exit:
                av = SemiAvenueExt(*cell.successors[0], cell.direction, AV_LENGTH//2)
                exit_cells.extend(av.exit)
            else:
                av = SemiAvenueInt(*cell.successors[0], cell.direction, AV_LENGTH//2)

            for c in av.cells:
                self.base_city[c.pos] = c
                
        
        # Create the entrance avenues internal and external.
        for cell in rb.entrance:
            start = tuple( x - i*(AV_LENGTH//2) for x,i in zip(cell.pos, self.direction_vectors[cell.direction]) )

            if cell in rb.external_av_entr:
                av = SemiAvenueExt(*start ,cell.direction, AV_LENGTH//2)
                exit_cells.extend(av.exit)
            else:
                av = SemiAvenueInt(*start,cell.direction, AV_LENGTH//2)

            for c in av.cells:
                self.base_city[c.pos] = c
                
      
        # Create the intersections:
        for offset in inter_offset:
            for coord, dirs in zip(inter_coord, inter_dirs):
                coord = np.array(coord, dtype="int32")
                it = RoadIntersection(*tuple(coord + offset), list(dirs))
                exit_cells.extend(it.exit)
                for c in it.cells:
                    self.base_city[c.pos] = c
                    

        # Extend the exits to fullfill the streets
        for c in exit_cells:
            next_cell = self.next_cell_of(*c.pos, c.direction)
            length = self.compute_street_length(*next_cell, c.direction)
            
            st = Street(*next_cell, c.direction, length)
            for c in st.cells:
                self.base_city[c.pos] = c

 
        # Scale the city to the desired size
        self.city_map, self.city_matrix = self.scale_city(SCALE)

 
        # Configure the global parameters of the simulator module
        configure_lattice_size(self.SIZE, self.city_map)

        # Sort by type
        self.avenues, self.streets, self.roundabouts = self.split_by_type()

        # Compute the street rate
        self.STR_RATE = np.sum(self.city_matrix)/(self.SIZE*self.SIZE)

    def scale_city(self, scale):

        def change_pos_to_references(cell, attribute, dictionary):
            """Given a cell, and a list of keys (attribute), replace the 
            keys for a reference to the object in the dictionary """
            # if attribute == "predecessors":
                
            #     if len(cell.__dict__[attribute]) > 0:
            #         print("Tiene elementos camiando predecessors: ", cell, cell.predecessors, cell.cell_type)

            cell.__dict__[attribute] = [city_map[k] for k in cell.__dict__[attribute]]
        
        def add_predecessors(cell, attribute, successors_of_cell):
            """Given a cell, an attibute we want to fullfill ("prio_predecessors" or "predecessors"), 
            and the list of sucessors of the cell, fulffill the atttribute accordingly."""
            for successor in successors_of_cell:
                successor.__dict__[attribute].append(cell)
        
        # Augment the city by the scale
        city_map = {}
        city_matrix = np.zeros((self.SIZE, self.SIZE))


        for i in range(scale):
            for j in range(scale):
                dx, dy = i*self.base_size, j*self.base_size
                for pos, cell in self.base_city.items():
                    new_pos, new_cell = cell.duplicate_cell(dx, dy, self.SIZE)
                    city_map[new_pos] = new_cell
                    city_matrix[new_pos] = 1


        # Replace the positions by the corresponding pointer to cells.
        for pos, cell in city_map.items():
            change_pos_to_references(cell, "prio_predecessors", city_map)
            change_pos_to_references(cell, "predecessors", city_map)
            change_pos_to_references(cell, "successors", city_map)
            change_pos_to_references(cell, "prio_successors", city_map)
        
        # Complete the 'graph' of the city adding the predecessors and successors.
        for pos, cell in city_map.items():   
            
            add_predecessors(cell, "predecessors", cell.successors)
            add_predecessors(cell, "prio_predecessors", cell.prio_successors)

 
        return city_map, city_matrix
        
    def compute_street_length(self, x, y, direction):
        length = 0
        while (x,y) not in self.base_city:
            length += 1
            x, y = self.next_cell_of(x,y, direction)
            x, y = x%self.base_size, y%self.base_size
        return length

    def split_by_type(self):
        """Returns three sets, 1 avenues, 2 streets, 3 roundabouts"""

        avenues, roundabouts, streets = set(), set(), set()

        for pos, cell in self.city_map.items():
            if cell.cell_type == CellType.STREET:
                streets.add(cell)
            elif cell.cell_type == CellType.AVENUE:
                avenues.add(cell)
            elif cell.cell_type == CellType.ROUNDABOUT:
                roundabouts.add(cell)

        return (avenues, streets, roundabouts)

    def set_max_chargers_stations(self,min_chargers, min_d_stations):
            """Given the minimum number of chargers and minimum number of total distributed stations, 
            compute the total number of distributed stations so that it is a perfect square number and 
            divisible by 4. Return the total number of chargers and distributed stations in a tuple """

            while min_d_stations % 4 != 0 or not (min_d_stations**0.5).is_integer():
                min_d_stations += 1

            return (min_chargers*min_d_stations, min_d_stations)

    def position_in_district(self, pos, C1, C2, R1, R2):
        """"Given a positon (x,y) return True if the position is inside the area defined by 
        the district between the column C1, C2 and rows R1, R2 """
        (x, y) = pos
        return x >= C1 and x < C2 and y >= R1 and y < R2

    def create_districts(self, layout):
        """"Recibes the stations layout and return a list of districts, 
        the districts are tuples of 4 elements that define an area:
        (C1, C2, R1, R2), all the elements between column C1 and C2 and
        rows R1 and R2 belong to that district. """

        # Based on the layout, create the step, the number of rows/cells
        # that are between the beginning and end of a district.

        if layout == 'central':
            step = self.SIZE

        elif layout == 'four':
            step = self.SIZE // 2

        elif layout == 'distributed':
            step = int(self.SIZE/self.scale)

        # Once we have the step, compute the area of each district
        districts = [(i, i+step, j, j+step) for i in range(0, self.SIZE, step)
                        for j in range(0, self.SIZE, step)]

        return districts

    def place_stations(self, layout, districts, total_d_st):
        """Recibes the layout of the stations and the districts
        of the city to return a dictionary where for each 
        district we have a list of positions for the stations."""

        def nearest_cell_type(reference, type_set):
            nearest = reference
            type_set_pos = [c.pos for c in type_set]
            if reference not in type_set_pos:
                candidates = [(i, j) for (i, j) in type_set_pos
                                if i == reference[0] or j == reference[1]]
                if len(candidates)==0:
                    # reference = (reference[0]+2, reference[1]+2)
                    # candidates = [(i, j) for (i, j) in type_set
                    #                 if i == reference[0] or j == reference[1]]
                    return nearest_cell_type((reference[0]+1, reference[1]+1), type_set)
                nearest = min(candidates, key=lambda p: lattice_distance(p[0], p[1], reference[0], reference[1]))

            return nearest

        # Create the list of stations that each district has
        stations_per_district = {}

        if layout == 'central' or layout == 'four':
            # If the layout is central we have only one district,
            # if the layout is four we have four districts. We place
            # a station in each district.
            for d in districts:
                (C1, C2, R1, R2) = d
                mid_point = (C1+C2) // 2, (R1+R2) // 2
                stations_per_district[d] = [
                    nearest_cell_type(mid_point, self.avenues)]

        else:
            # Now we are dealing with the distributed layout and so
            # a district has more than one station. First we are
            # goint to create all the stations evenly distributed
            # across the city.
            sq_maximum_cs = total_d_st**0.5
            
            distance_appart = float(self.SIZE/sq_maximum_cs)
            positions = []
            for i in range(int(sq_maximum_cs)):
                for j in range(int(sq_maximum_cs)):
                    cell = (int(i*distance_appart), int(j*distance_appart))
                    positions.append(
                        nearest_cell_type(cell, self.streets))

            # Now we have to find for each position, in which district
            # does it fall.
            stations_per_district = {d: [] for d in districts}
            for pos in positions:
                for district in districts:
                    if self.position_in_district(pos, district[0], district[1], district[2], district[3]):
                        stations_per_district[district].append(pos)
                        break

        return stations_per_district
