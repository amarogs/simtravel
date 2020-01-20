from libc.math cimport abs as cabs
from libc.math cimport pow as cpow
from libc.math cimport exp as cexp

import heapq
import random


#A dictionary to use as a c type
cdef dict CITY
cdef int SIZE
cpdef configure_a_star(dict city_map, int city_size):
    global CITY, SIZE
    CITY = city_map
    SIZE = city_size

cdef class PriorityMinHeap(object):
    """This class has been made using the example in https://docs.python.org/2/library/heapq.html """
    cdef list pq
    cdef dict entry_finder
    cdef tuple REMOVED
    cdef int counter

    def __init__(self):
        self.pq = [] #List arranged as a min heap
        self.entry_finder = {} #mapping of items to enties
        self.REMOVED = (99999,99999) #placeholder for a removed task
        self.counter = 0 #Number of elements that are not removed in the heap

    cdef insert(self, tuple item, int priority):
        if item in self.entry_finder:
            self.remove_item(item)
        
        cdef list entry = [priority, item]
       
        self.entry_finder[item] = entry
        heapq.heappush(self.pq, entry)
        self.counter += 1

    def remove_item(self, tuple item):
        "Mark an existing task as REMOVED"
        cdef list entry = self.entry_finder.pop(item)
        entry[-1] = self.REMOVED
        self.counter -= 1

    def pop(self):
        "Remove and return the lowest priority item that is not REMOVED"
        cdef tuple item

        while self.pq:
            _ , item = heapq.heappop(self.pq)
            if item is not self.REMOVED:
                self.counter -= 1
                del self.entry_finder[item]
                return item
    def is_empty(self):
        return self.counter == 0


cdef list reconstruct_path(came_from, start, current):
    cdef list total = [current]

    while True:
        current = came_from[current]
        if current==start:
            break
        else:
            total.append(current)
    return total



cpdef list a_star(tuple start, tuple goal):
    global CITY
    cdef set closed_set = set() #Set of positions already visited
    open_set = PriorityMinHeap() #Min heap of posible positions available for expansion
    open_set.insert(start, lattice_distance(start, goal))

    #Dictionary containing (position:distance), which is the distance to
    #the goal from the position
    cdef dict g_score = {start:0}

    #Dictionary containing the relationship between posititions
    cdef dict came_from = {start:start}

    cdef int depth = 0 #Controls the number of entries in the path we want to compute
    cdef tuple neighbour, current


    while not open_set.is_empty():
        #If there are available nodos, take the most promising one (lowest f_score)
        current = open_set.pop()
        depth += 1
        
        
        if current == goal: #or depth==MAX_DEPTH:
            #If the nodo is the goal, we have finished
            return reconstruct_path(came_from,start, current)
        else:
            #Otherwise we need to explore the current node
            closed_set.add(current)
        
        for (neighbour,road_type) in CITY[current]:

            if neighbour not in closed_set:
                #If the neighbour hasn't been visited
                #Compute the possible g_score
                new_g_score = g_score[current] + road_type

                if neighbour not in g_score or new_g_score < g_score[neighbour]:
                    #Add the neighbour with the g_score to the heap
                    open_set.insert(neighbour, new_g_score + lattice_distance(neighbour, goal))
                    g_score[neighbour] = new_g_score
                    came_from[neighbour] = current
              

cpdef list recompute_path(list current_path, tuple pos, tuple target):
    cdef list extension_path
    cdef tuple n_step

    if len(current_path) > 1:
        extension_path = a_star(pos, current_path[-2])
        del current_path[-1]
        for n_step in extension_path[1:]:
            current_path.append(n_step) 
    else:
        current_path = a_star(pos, target)
    return current_path

cpdef int lattice_distance(pos1, pos2):
    global SIZE
    cdef int dx, dy
    dx = cabs(pos1[0] - pos2[0])
    if dx > int(SIZE/2):
        dx = SIZE - dx
    dy = cabs(pos1[1] - pos2[1])
    if dy > int(SIZE/2):
        dy = SIZE - dy
    return (dx + dy)


