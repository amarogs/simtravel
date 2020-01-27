# -*- coding: utf-8 -*-
import random
from enum import Enum
from simtravel.simulator.simulator import lattice_distance, configure_a_star
import numpy as np


class Direction(Enum):
    WRONG_WAY = 0
    ALLOWED = 1
    FORBIDDEN = 2

    def __add__(self, other):
        return self.value + other.value

    def __eq__(self, other):
        return self.value == other

    def __ne__(self, other):
        return self.value != other


class CellType(Enum):
    HOUSE = 0
    AVENUE = 1
    STREET = 2
    ROUNDABOUT = 3

    def __eq__(self, other):
        return self.value == other

    def __ne__(self, other):
        return self.value != other


class IntensityMeasure():

    def __init__(self, int_point, ext_point):
        self.int_point = int_point
        self.ext_point = ext_point
        self.vehicle_count_int = 0
        self.vehicle_count_ext = 0

    def restart(self):
        self.vehicle_count_int = 0
        self.vehicle_count_ext = 0


class CityBuilder():
    def __init__(self):
        '''BULDING CELLS 
        The smallest controllable element is a cell.
        A cell is an array with 5 element [North, South, West, East, Type].
        The first 4 take a value from Direction, the Type takes a value
        from CellType.
        '''

        self.house = [Direction.FORBIDDEN, Direction.FORBIDDEN,
                      Direction.FORBIDDEN, Direction.FORBIDDEN, CellType.HOUSE]
        self.av_S_int, self.av_S_house = [Direction.WRONG_WAY, Direction.ALLOWED, Direction.ALLOWED, Direction.WRONG_WAY, CellType.AVENUE], [
            Direction.WRONG_WAY, Direction.ALLOWED, Direction.FORBIDDEN, Direction.ALLOWED, CellType.AVENUE]
        self.av_S_exit, self.av_S_entr = [Direction.WRONG_WAY, Direction.ALLOWED, Direction.ALLOWED, Direction.ALLOWED, CellType.AVENUE], [
            Direction.WRONG_WAY, Direction.ALLOWED, Direction.WRONG_WAY, Direction.ALLOWED, CellType.AVENUE]

        self.av_N_int, self.av_N_house = [Direction.ALLOWED, Direction.WRONG_WAY, Direction.WRONG_WAY, Direction.ALLOWED, CellType.AVENUE], [
            Direction.ALLOWED, Direction.WRONG_WAY, Direction.ALLOWED, Direction.FORBIDDEN, CellType.AVENUE]
        self.av_N_exit, self.av_N_entr = [Direction.ALLOWED, Direction.WRONG_WAY, Direction.ALLOWED, Direction.ALLOWED, CellType.AVENUE], [
            Direction.ALLOWED, Direction.WRONG_WAY, Direction.ALLOWED, Direction.WRONG_WAY, CellType.AVENUE]

        self.av_E_int, self.av_E_house = [Direction.WRONG_WAY, Direction.ALLOWED, Direction.WRONG_WAY, Direction.ALLOWED, CellType.AVENUE], [
            Direction.ALLOWED, Direction.FORBIDDEN, Direction.WRONG_WAY, Direction.ALLOWED, CellType.AVENUE]
        self.av_E_exit, self.av_E_entr = [Direction.ALLOWED, Direction.ALLOWED, Direction.WRONG_WAY, Direction.ALLOWED, CellType.AVENUE], [
            Direction.ALLOWED, Direction.WRONG_WAY, Direction.WRONG_WAY, Direction.ALLOWED, CellType.AVENUE]

        self.av_W_int, self.av_W_house = [Direction.ALLOWED, Direction.WRONG_WAY, Direction.ALLOWED, Direction.WRONG_WAY, CellType.AVENUE], [
            Direction.FORBIDDEN, Direction.ALLOWED, Direction.ALLOWED, Direction.WRONG_WAY, CellType.AVENUE]
        self.av_W_exit, self.av_W_entr = [Direction.ALLOWED, Direction.ALLOWED, Direction.ALLOWED, Direction.WRONG_WAY, CellType.AVENUE], [
            Direction.WRONG_WAY, Direction.ALLOWED, Direction.ALLOWED, Direction.WRONG_WAY, CellType.AVENUE]

        self.street_E, self.street_W = [Direction.FORBIDDEN, Direction.FORBIDDEN, Direction.WRONG_WAY, Direction.ALLOWED, CellType.STREET], [
            Direction.FORBIDDEN, Direction.FORBIDDEN, Direction.ALLOWED, Direction.WRONG_WAY, CellType.STREET]
        self.street_N, self.street_S = [Direction.ALLOWED, Direction.WRONG_WAY, Direction.FORBIDDEN, Direction.FORBIDDEN, CellType.STREET], [
            Direction.WRONG_WAY, Direction.ALLOWED, Direction.FORBIDDEN, Direction.FORBIDDEN, CellType.STREET]

        self.RB_E, self.RB_W = [Direction.FORBIDDEN, Direction.FORBIDDEN, Direction.WRONG_WAY, Direction.ALLOWED, CellType.ROUNDABOUT], [
            Direction.FORBIDDEN, Direction.FORBIDDEN, Direction.ALLOWED, Direction.WRONG_WAY, CellType.ROUNDABOUT]
        self.RB_N, self.RB_S = [Direction.ALLOWED, Direction.WRONG_WAY, Direction.FORBIDDEN, Direction.FORBIDDEN, CellType.ROUNDABOUT], [
            Direction.WRONG_WAY, Direction.ALLOWED, Direction.FORBIDDEN, Direction.FORBIDDEN, CellType.ROUNDABOUT]

        self.RB_inter_S_E, self.RB_inter_S_W = [Direction.WRONG_WAY, Direction.ALLOWED, Direction.WRONG_WAY, Direction.ALLOWED, CellType.ROUNDABOUT], [
            Direction.WRONG_WAY, Direction.ALLOWED, Direction.ALLOWED, Direction.WRONG_WAY, CellType.ROUNDABOUT]
        self.RB_inter_N_E, self.RB_inter_N_W = [Direction.ALLOWED, Direction.WRONG_WAY, Direction.WRONG_WAY, Direction.ALLOWED, CellType.ROUNDABOUT], [
            Direction.ALLOWED, Direction.WRONG_WAY, Direction.ALLOWED, Direction.WRONG_WAY, CellType.ROUNDABOUT]

        self.inter_S_E, self.inter_S_W = [Direction.WRONG_WAY, Direction.ALLOWED, Direction.WRONG_WAY, Direction.ALLOWED, CellType.STREET], [
            Direction.WRONG_WAY, Direction.ALLOWED, Direction.ALLOWED, Direction.WRONG_WAY, CellType.STREET]
        self.inter_N_E, self.inter_N_W = [Direction.ALLOWED, Direction.WRONG_WAY, Direction.WRONG_WAY, Direction.ALLOWED, CellType.STREET], [
            Direction.ALLOWED, Direction.WRONG_WAY, Direction.ALLOWED, Direction.WRONG_WAY, CellType.STREET]

    def north_mask(self):
        return [(0, 0), (0, -1), (-1, -1), (-1, 0)]

    def sout_mask(self):
        return [(0, 0), (0, 1), (1, 1), (1, 0)]

    def east_mask(self):
        return [(0, 0), (-1, 0), (-1, 1), (0, 1)]

    def west_mask(self):
        return [(0, 0), (1, 0), (1, 1), (0, -1)]


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
            if reference not in type_set:
                candidates = [(i, j) for (i, j) in type_set
                                if i == reference[0] or j == reference[1]]
                if len(candidates)==0:
                    # reference = (reference[0]+2, reference[1]+2)
                    # candidates = [(i, j) for (i, j) in type_set
                    #                 if i == reference[0] or j == reference[1]]
                    return nearest_cell_type((reference[0]+1, reference[1]+1), type_set)
                nearest = min(candidates, key=lambda p: lattice_distance(
                    p, reference))

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

class SquareCity(CityBuilder):

    def __init__(self, scale=1, block_scale=4):
        """
        Creates a city based on a squre design, it is based on 4 roundabouts
        connected to each other and blocks oh housing between them. 

        :param scale: scales the city in 2D, a scale of 1 is the original set up, 
        a scale of 2 is 4 times the original set up

        :param block_scale: scales the city in 1D, controls the length of the
        avenues as well as the length of the blocks. """

        super().__init__()
        self.scale = scale
        self.block_scale = block_scale
        self.SIZE = None
        self.STR_RATE = None

        if scale >= 2:
            self.block_size = 2*(6*block_scale + 1)
        else:
            self.block_size = 6*block_scale + 1

        # *******SMALL TILES************
        self.tile_AV_NS = np.array([[self.house,    self.av_S_house, self.av_S_int, self.av_N_int, self.av_N_house, self.house],
                                    [self.street_E, self.av_S_entr,  self.av_S_int,
                                        self.av_N_int, self.av_N_exit,  self.street_E],
                                    [self.house,    self.av_S_house, self.av_S_int,
                                     self.av_N_int, self.av_N_house, self.house],
                                    [self.house,    self.av_S_house, self.av_S_int,
                                     self.av_N_int, self.av_N_house, self.house],
                                    [self.street_W, self.av_S_exit,  self.av_S_int,
                                     self.av_N_int, self.av_N_entr,  self.street_W],
                                    [self.house,    self.av_S_house, self.av_S_int,
                                     self.av_N_int, self.av_N_house, self.house]
                                    ])

        self.tile_AV_EW = np.array([[self.house,   self.street_S,  self.house,      self.house,  self.street_N,   self.house],
                                    [self.av_W_house, self.av_W_entr, self.av_W_house,
                                        self.av_W_house, self.av_W_exit,  self.av_W_house],
                                    [self.av_W_int,   self.av_W_int,  self.av_W_int,
                                     self.av_W_int,   self.av_W_int,   self.av_W_int],
                                    [self.av_E_int,   self.av_E_int,  self.av_E_int,
                                     self.av_E_int,   self.av_E_int,   self.av_E_int],
                                    [self.av_E_house, self.av_E_exit, self.av_E_house,
                                     self.av_E_house,  self.av_E_entr,  self.av_E_house],
                                    [self.house,      self.street_S,  self.house,
                                        self.house,   self.street_N,   self.house]
                                    ])

        self.tile_NG = np.array([[self.house,    self.street_S,  self.house,    self.house,    self.street_N,  self.house],
                                 [self.street_E, self.inter_S_E, self.street_E,
                                     self.street_E, self.inter_N_E, self.street_E],
                                 [self.house,    self.street_S,  self.house,
                                  self.house,    self.street_N,  self.house],
                                 [self.house,    self.street_S,  self.house,
                                  self.house,    self.street_N,  self.house],
                                 [self.street_W, self.inter_S_W, self.street_W,
                                  self.street_W, self.inter_N_W, self.street_W],
                                 [self.house,    self.street_S,  self.house,    self.house,     self.street_N, self.house]])

        self.tile_RB = np.array([[self.house,      self.av_S_house,   self.av_S_int,      self.av_N_int,      self.av_N_house,    self.house],
                                 [self.av_W_house, self.RB_inter_S_W,  self.RB_W,
                                     self.RB_inter_N_W,  self.RB_inter_N_W,  self.av_W_house],
                                 [self.av_W_int,   self.RB_inter_S_W,  self.house,
                                     self.house,         self.RB_N,          self.av_W_int],
                                 [self.av_E_int,   self.RB_S,          self.house,
                                     self.house,         self.RB_inter_N_E,  self.av_E_int],
                                 [self.av_E_house, self.RB_inter_S_E,  self.RB_inter_S_E,
                                     self.RB_E,          self.RB_inter_N_E,  self.av_E_house],
                                 [self.house,      self.av_S_house,    self.av_S_int,
                                     self.av_N_int,      self.av_N_house,    self.house]
                                 ])

        # Create the city
        self.city_matrix = self.create_city_matrix()
        self.city_map = self.create_city_map()
        # Once the city map has been create we can use it on the simulator module
        # Configure the global parameters of the a_star
        configure_a_star(self.city_map, self.SIZE)

        # Split the cells by type
        self.avenues, self.streets, self.roundabouts = self.split_by_type()

    def combine_tiles(self):
        """Creates the basic layout combining the tiles. 
        Returns a numpy array."""
        side_list = [self.tile_NG for _ in range(self.block_scale)] + [self.tile_AV_EW] \
            + [self.tile_NG for _ in range(self.block_scale)]
        side_array = [np.concatenate(side_list, axis=0)
                      for _ in range(self.block_scale)]

        central_list = [self.tile_AV_NS for _ in range(self.block_scale)] + [self.tile_RB] \
            + [self.tile_AV_NS for _ in range(self.block_scale)]
        total = side_array + \
            [np.concatenate(central_list, axis=0)] + side_array
        total = np.concatenate(total, axis=1)
        base = [np.concatenate([total, total], axis=1),
                np.concatenate([total, total], axis=1)]

        return np.concatenate(base, axis=0)

    def create_city_matrix(self):
        base_array = self.combine_tiles()
        matrix = []
        for _ in range(self.scale):
            row = [base_array for _ in range(self.scale)]
            matrix.append(np.concatenate(row, axis=1))
        city = np.concatenate(matrix, axis=0)
        self.SIZE = city.shape[0]
        self.STR_RATE = round(1.0*sum((1 for i in range(self.SIZE)
                                       for j in range(self.SIZE) if city[i, j][4] != CellType.HOUSE))/(city.shape[0]**2), 2)

        return city

    def select_intensity_points(self, total):
        intensity_points = []  # List to store the Intensity objects

        # Obtain the list of avenues and shuffle it
        avenues_list = list(self.avenues_set)
        random.shuffle(avenues_list)

        for _ in range(total):
            interior, exterior = self.avenue_pair(avenues_list.pop())
            intensity_points.append(IntensityMeasure(interior, exterior))

        return intensity_points

    def avenue_pair(self, pos):
        """Given a position inside an avenue, returns a tuple containing the inner lane and exterior lane. """
        (x_1, y_1) = pos

        # Select the avenue cell next to the random selected previously
        for (pos, t) in self.city_map[(x_1, y_1)]:
            if t == 1 and ((x_1, y_1), 1) in self.city_map[pos]:
                x_2, y_2 = pos[0], pos[1]
                break
        # The inner lane is surrounded by avenues and the exterior lane is next to regular streets or houses
        # Based on this difference sort the positions accordinly

        y_diff = y_1 - y_2
        if y_diff != 0:
            # We are dealing wih an avenue that goes N or S
            if y_diff > 0:
                check_next = (x_1, y_1+1)
            else:
                check_next = (x_1, y_1-1)
        else:
            # We are dealing with an avenue that goes E or W
            x_diff = x_1 - x_2
            if x_diff > 0:
                check_next = (x_1+1, y_1)
            else:
                check_next = (x_1-1, y_1)

        if check_next in self.avenues_set:
            return ((x_1, y_1), (x_2, y_2))
        else:
            return ((x_2, y_2), (x_1, y_1))

    def create_city_map(self):
        """Method that creates a dictionary where keys are the road
        cells and the attribute is a list of adjacent roads """
        
        city_map = {}
        for i in range(self.SIZE):
            for j in range(self.SIZE):
                # Check if the position is not a house:
                if self.city_matrix[(i, j)][4] != CellType.HOUSE:
                    movements = self.city_matrix[(i, j)][0:4] == Direction.ALLOWED
                    allowed = self.get_neigh(i, j)[movements]
                    city_map[(i, j)] = [(pos, self.city_matrix[pos][4].value)
                                        for pos in allowed]


        return city_map

    def segment_by_type(self):
        types = [1, 2, 3]
        city_segments = {}

        for i in types:
            segments = []
            cell_set = self.cells_sets[i-1]

            while cell_set:
                component = self.depth_first_search(cell_set)
                segments.append(component)
                cell_set = cell_set - component
            city_segments[i] = segments

        return city_segments

    def mid_point_av_segments(self):
        mid_points = []
        for segment in self.segments_type[1]:
            # Compute the sum of distances from one element to the rest
            segment_list = list(segment)
            segment_dist = []
            for s in segment_list:
                s_distance = 0
                for t in segment_list:
                    if s != t:
                        s_distance += lattice_distance(s, t)

                segment_dist.append(s_distance/len(segment_list))
            mid_points.append(
                segment_list[segment_dist.index(min(segment_dist))])

        return mid_points

    def add_direction_changers(self, points):
        def add_mask(pos, mask):
            return ((pos[0] + mask[0]) % self.SIZE, (pos[1] + mask[1]) % self.SIZE)

        avenues_masks = [self.N, self.E, self.S, self.W]

        for point in points:
            (inner, outer) = self.avenue_pair(point)

        dx = inner[0] - outer[0]
        dy = inner[1] - outer[1]

        # (0,1,2,3)
        # (N,E,S,W)
        direction = None
        if dx > 0:
            # Road that goes E
            direction = 1
        elif dx < 0:
            # Road that goes W
            direction = 3
        elif dy > 0:
            # Road that goes S
            direction = 2
        elif dy < 0:
            # Road that goes N
            direction = 0
        else:
            raise Exception("The points are the same")
        self.city_map[inner].append(
            (add_mask(inner, avenues_masks[direction][1]), 1))
        self.city_map[add_mask(inner, avenues_masks[direction][3])].append(
            (add_mask(inner, avenues_masks[direction][2]), 1))

    def depth_first_search(self, cell_set):
        visited = set()

        stack = [cell_set.pop()]

        while stack:
            current = stack.pop()  # Take the last element of the list
            visited.add(current)  # Add it to the set of visited nodes

            for neigh in self.get_neigh(current[0], current[1], True):
                if neigh not in visited and neigh in cell_set:
                    # For each neigbour, if it hasn't been visited yet and it is in the set,
                    # add it to the stack.
                    stack.append(neigh)
            # In the visited set I have all the cells reachable from the starting one
        return visited

    def split_by_type(self):
        """Returs three sets, 1 avenues, 2 streets, 3 roundabouts"""

        avenues, roundabouts, streets = set(), set(), set()
        for i in range(self.SIZE):
            for j in range(self.SIZE):
                if self.city_matrix[(i, j)][-1] == 1:
                    avenues.add((i, j))
                elif self.city_matrix[(i, j)][-1] == 2:
                    streets.add((i, j))
                elif self.city_matrix[(i, j)][-1] == 3:
                    roundabouts.add((i, j))
        
        return (avenues, streets, roundabouts)

    def get_neigh(self, x, y, as_list=False):
        "Returns a np array containing 4 [x,y] directions. (N, S,W,E)"
        N, S = ((x-1) % self.SIZE, y), ((x+1) % self.SIZE, y)
        W, E = (x, (y-1) % self.SIZE), (x, (y+1) % self.SIZE)
        if not as_list:
            n = np.empty((4,), dtype='object')
            n[:] = list([N, S, W, E])
        else:
            n = [N, S, W, E]
        return n

 



