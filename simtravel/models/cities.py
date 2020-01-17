import numpy as np
import random


class IntensityMeasure():
    def __init__(self, int_point, ext_point):
        self.int_point = int_point
        self.ext_point = ext_point
        self.vehicle_count_int = 0
        self.vehicle_count_ext = 0
        
    def restart(self):
        self.vehicle_count_int = 0
        self.vehicle_count_ext = 0

class SquareCity():
    
    def __init__(self, sqrt_roundabouts=1, block_scale=4):
        """Builds a city that is made trough tiles. The block_scale controls how big the blocks
        are, the sqrt_roundabouts is the square root of the total number of
        roundabouts in the city.
        
        Each cell in the city is represented as an array of 5 elements (tile):
        [North, South, West, East, Type]. The first four can take: 0 means following that
        direction is the wrong way, 1 following that direction is allowed, 2 following
        that direction you hit a house. The type is either 0 (house), 1 (avenue),
        2 (roundabout) 3 (street)"""

        self.block_scale = block_scale
        self.sqrt_roundabouts = sqrt_roundabouts
        if sqrt_roundabouts >= 2:
            self.block_size = 2*(6*block_scale + 1)
        else:
            self.block_size = 6*block_scale + 1


        #*******BULDING BLOCKS*******
        house = [2,2,2,2,0,0]
        av_S_int, av_S_house  = [0,1,1,0,1,1], [0,1,2,1,1,1]
        av_S_exit, av_S_entr = [0,1,1,1,1,1], [0,1,0,1,1,1]

        av_N_int, av_N_house = [1,0,0,1,1,1],[1,0,1,2,1,1]
        av_N_exit,av_N_entr = [1,0,1,1,1,1],[1,0,1,0,1,1]


        av_E_int, av_E_house = [0,1,0,1,1,1], [1,2,0,1,1,1]
        av_E_exit,av_E_entr = [1,1,0,1,1,1],[1,0,0,1,1,1]

        av_W_int, av_W_house = [1,0,1,0,1,1], [2,1,1,0,1,1]
        av_W_exit,av_W_entr = [1,1,1,0,1,1],[0,1,1,0,1,1]


        street_E, street_W = [2,2,0,1,3,1], [2,2,1,0,3,1]
        street_N, street_S = [1,0,2,2,3,1], [0,1,2,2,3,1]

        RB_E, RB_W = [2,2,0,1,2,1], [2,2,1,0,2,1]
        RB_N, RB_S = [1,0,2,2,2,1], [0,1,2,2,2,1]

        RB_inter_S_E,RB_inter_S_W = [0,1,0,1,2,1],[0,1,1,0,2,1]
        RB_inter_N_E,RB_inter_N_W = [1,0,0,1,2,1],[1,0,1,0,2,1]

        inter_S_E,inter_S_W = [0,1,0,1,3,1],[0,1,1,0,3,1]
        inter_N_E,inter_N_W = [1,0,0,1,3,1],[1,0,1,0,3,1]


        #*******SMALL TILES************
        self.tile_AV_NS =np.array([  [house,    av_S_house, av_S_int, av_N_int, av_N_house, house],
                                     [street_E, av_S_entr,  av_S_int, av_N_int, av_N_exit,  street_E ],
                                     [house,    av_S_house, av_S_int, av_N_int, av_N_house, house],
                                     [house,    av_S_house, av_S_int, av_N_int, av_N_house, house],
                                     [street_W, av_S_exit,  av_S_int, av_N_int, av_N_entr,  street_W],
                                     [house,    av_S_house, av_S_int, av_N_int, av_N_house, house]
                            ],dtype='int8')

        self.tile_AV_EW = np.array([ [house,   street_S   ,  house,      house,  street_N    ,   house],
                                   [av_W_house, av_W_entr , av_W_house, av_W_house, av_W_exit ,  av_W_house ],
                                   [av_W_int,   av_W_int,  av_W_int,   av_W_int,   av_W_int,   av_W_int],
                                   [av_E_int,   av_E_int,  av_E_int,   av_E_int,   av_E_int,   av_E_int],
                                   [av_E_house, av_E_exit, av_E_house, av_E_house,  av_E_entr,  av_E_house],
                                   [house,      street_S ,  house,      house,   street_N   ,   house]
                                   ], dtype='int8')

        self.tile_NG = np.array([    [house,    street_S,  house,    house,    street_N,  house],
                                [street_E, inter_S_E, street_E, street_E, inter_N_E, street_E],
                                [house,    street_S,  house,    house,    street_N,  house],
                                [house,    street_S,  house,    house,    street_N,  house],
                                [street_W, inter_S_W, street_W, street_W, inter_N_W, street_W],
                                [house,    street_S,  house,    house,     street_N, house] ],dtype='int8')

        self.tile_RB = np.array([[house,      av_S_house,   av_S_int,      av_N_int,      av_N_house,    house],
                                [av_W_house, RB_inter_S_W,  RB_W,          RB_inter_N_W,  RB_inter_N_W,  av_W_house],
                                [av_W_int,   RB_inter_S_W,  house,         house,         RB_N,          av_W_int],
                                [av_E_int,   RB_S,          house,         house,         RB_inter_N_E,  av_E_int],
                                [av_E_house, RB_inter_S_E,  RB_inter_S_E,  RB_E,          RB_inter_N_E,  av_E_house],
                                [house,      av_S_house,    av_S_int,      av_N_int,      av_N_house,    house]
                            ],dtype='int8')
        
        self.N = [(0,0), (0,-1), (-1,-1), (-1,0)]
        self.S = [(0,0), (0, 1), (1 , 1), ( 1, 0)]
        self.E = [(0,0), (-1,0), (-1, 1), ( 0, 1)]
        self.W = [(0,0), ( 1,0), ( 1, 1), ( 0,-1)]

        

        #First create the city
        self.city = self.create_city()

        #Then create the city map, that is a dictionary where keys are legal positions on the city and returns the list of 
        #cells where a vehicle can move to from the current position.
        self.city_map = self.create_city_map()

        #Split the matrix into sets, one for each kind of road
        self.avenues_set, self.roundabouts_set, self.streets_set = self.split_by_type()
        self.cells_sets = [self.avenues_set, self.roundabouts_set, self.streets_set]

        #Segment the city into different components based on the type
        #self.segments_type = self.segment_by_type()

        #Add direction changers at the midpoint of avenues.
        # self.add_direction_changers(self.mid_point_av_segments())

    def combine_tiles(self):
        side_list = [self.tile_NG for _ in range(self.block_scale)] + [self.tile_AV_EW] \
            + [self.tile_NG for _ in range(self.block_scale)]
        side_array = [np.concatenate(side_list, axis=0) for _ in range(self.block_scale) ]

        central_list =[self.tile_AV_NS for _ in range(self.block_scale)] + [self.tile_RB] \
            + [self.tile_AV_NS for _ in range(self.block_scale)]
        total = side_array + [np.concatenate(central_list, axis=0)] + side_array
        total = np.concatenate(total, axis=1)
        base = [np.concatenate([total, total], axis=1),
                np.concatenate([total, total], axis=1)]
        
        
        return np.concatenate(base, axis=0)

    def create_city(self):
        base_array = self.combine_tiles()
        matrix = []
        for _ in range(self.sqrt_roundabouts):
            row = [base_array for _ in range(self.sqrt_roundabouts)]
            matrix.append(np.concatenate(row, axis=1))
        city = np.concatenate(matrix, axis=0)
        self.SIZE = city.shape[0]
        self.STREET_P = round(1.0*sum((1 for i in range(self.SIZE) \
            for j in range(self.SIZE) if city[i,j][5]!=0))/(city.shape[0]**2),2)

        return city
    def select_intensity_points(self, total):
        intensity_points = [] #List to store the Intensity objects

        #Obtain the list of avenues and shuffle it
        avenues_list = list(self.avenues_set)
        random.shuffle(avenues_list)

        for _ in range(total):
            interior, exterior = self.avenue_pair(avenues_list.pop())
            intensity_points.append(IntensityMeasure(interior, exterior))
     
        return intensity_points
    def avenue_pair(self, pos):
        """Given a position inside an avenue, returns a tuple containing the inner lane and exterior lane. """
        (x_1, y_1) = pos

        #Select the avenue cell next to the random selected previously
        for (pos,t) in self.city_map[(x_1, y_1)]: 
            if t == 1 and ((x_1, y_1),1) in self.city_map[pos]:
                x_2,y_2 = pos[0], pos[1]
                break
        #The inner lane is surrounded by avenues and the exterior lane is next to regular streets or houses
        #Based on this difference sort the positions accordinly
 
        y_diff = y_1 - y_2
        if y_diff != 0:
            #We are dealing wih an avenue that goes N or S
            if y_diff > 0:
                check_next = (x_1, y_1+1)
            else:
                check_next = (x_1, y_1-1)
        else:
            #We are dealing with an avenue that goes E or W
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
        """Method that creates a class atributte called city_map which is a dictionary 
        where keys are the road cells and the attribute is a list of adjacent roads. """
        n_hood = {}
        for i in range(self.SIZE):
            for j in range(self.SIZE):
                #Check if the position is not a house:
                if self.city[(i,j)][-2] != 0:
                    movements = self.city[(i,j)][0:4] == 1
                    allowed = self.get_neigh(i,j)[movements]
                    n_hood[(i,j)] = [(pos, self.city[pos][-2]) for pos in allowed]
  
        return n_hood
    def segment_by_type(self):
        types = [1,2,3]
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
            #Compute the sum of distances from one element to the rest
            segment_list = list(segment)
            segment_dist = []
            for s in segment_list:
                s_distance = 0
                for t in segment_list:
                    if s != t:
                        s_distance += graphs.lattice_distance(s, t)

                segment_dist.append(s_distance/len(segment_list))
            mid_points.append(segment_list[segment_dist.index(min(segment_dist))])

        return mid_points
    def add_direction_changers(self, points):
        def add_mask(pos, mask):
            return ((pos[0] + mask[0])%self.SIZE, (pos[1] + mask[1])%self.SIZE)

        avenues_masks = [self.N, self.E, self.S, self.W]

        for point in points:
            (inner, outer) = self.avenue_pair(point)

        dx = inner[0] - outer[0]
        dy = inner[1] - outer[1]

        # (0,1,2,3)
        # (N,E,S,W)
        direction = None
        if dx > 0:
            #Road that goes E
            direction = 1
        elif dx <0:
            #Road that goes W
            direction = 3
        elif dy>0:
            #Road that goes S
            direction = 2
        elif dy <0:
            #Road that goes N
            direction = 0
        else:
            raise Exception("The points are the same")
        self.city_map[inner].append( (add_mask(inner, avenues_masks[direction][1]), 1) )
        self.city_map[add_mask(inner, avenues_masks[direction][3])].append( \
            (add_mask(inner, avenues_masks[direction][2]),1))

    def depth_first_search(self, cell_set):
        visited = set()

        stack = [cell_set.pop()]

        while stack:
            current = stack.pop() #Take the last element of the list
            visited.add(current) #Add it to the set of visited nodes

            for neigh in self.get_neigh(current[0], current[1], True):
                if neigh not in visited and neigh in cell_set:
                    #For each neigbour, if it hasn't been visited yet and it is in the set, 
                    #add it to the stack.
                    stack.append(neigh)
            #In the visited set I have all the cells reachable from the starting one
        return visited  

    def split_by_type(self):
        """Returs three sets, 1 avenues, 2 roundabouts, 3 streets"""

        avenues, roundabouts, streets  = set(),set(),set()
        for i in range(self.SIZE):
            for j in range(self.SIZE):
                if self.city[(i,j)][-2] == 1:
                    avenues.add((i, j))
                elif self.city[(i,j)][-2] == 2:
                    roundabouts.add((i, j))
                elif self.city[(i, j)][-2] == 3:
                    streets.add((i,j))
        return (avenues, roundabouts, streets)

    def get_neigh(self,x,y, as_list=False):
        "Returns a np array containing 4 [x,y] directions. (N, S,W,E)"
        N,S = ((x-1)%self.SIZE, y), ((x+1)%self.SIZE, y)
        W,E = (x, (y-1)%self.SIZE), (x, (y+1)%self.SIZE)
        if not as_list:
            n = np.empty( (4,), dtype='object')
            n[:] = list([N,S,W,E])
        else:
            n = [N,S,W,E]
        return n    
    

def set_max_chargers_stations(min_chargers, min_d_stations):
    """Given the minimum number of chargers and minimum number of total distributed stations, 
    compute the total number of distributed stations so that it is a perfect square number and 
    divisible by 4. Return the total number of chargers and distributed stations in a tuple """

    while min_d_stations % 4 != 0 or not (min_d_stations**0.5).is_integer():
        min_d_stations += 1

    return (min_chargers*min_d_stations, min_d_stations)
