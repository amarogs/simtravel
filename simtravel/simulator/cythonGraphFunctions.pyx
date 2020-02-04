from libc.math cimport abs as cabs

import heapq

#GLOBAL ATTRIBUTES OF THIS CLASS

cdef dict CITY
cdef int LATTICE_SIZE



cpdef void configure_lattice_size(int lattice_size,dict city_map):
    global CITY, LATTICE_SIZE
    CITY = city_map
    LATTICE_SIZE = lattice_size

cpdef int lattice_distance(tuple pos1, tuple pos2):
    global LATTICE_SIZE
    cdef int dx, dy
    dx = cabs(pos1[0] - pos2[0])
    if dx > int(LATTICE_SIZE/2):
        dx = LATTICE_SIZE - dx
    dy = cabs(pos1[1] - pos2[1])
    if dy > int(LATTICE_SIZE/2):
        dy = LATTICE_SIZE - dy
    return (dx + dy)



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

    cdef remove_item(self, tuple item):
        "Mark an existing task as REMOVED"
        cdef list entry = self.entry_finder.pop(item)
        entry[-1] = self.REMOVED
        self.counter -= 1

    cdef pop(self):
        "Remove and return the lowest priority item that is not REMOVED"
        cdef tuple item

        while self.pq:
            _ , item = heapq.heappop(self.pq)
            if item is not self.REMOVED:
                self.counter -= 1
                del self.entry_finder[item]
                return item
    cdef is_empty(self):
        return self.counter == 0




cdef list reconstruct_path(dict came_from, tuple start, tuple current):
    cdef list total = [current]

    while True:
        current = came_from[current]
        if current==start:
            break
        else:
            total.append(current)
    return total


cdef class AStar():
    cdef int max_length
    def __init__(self, max_length):
        self.max_length = max_length
    cpdef list new_path(self, tuple start, tuple goal):
        global CITY
        cdef set closed_set = set() #Set of positions already visited
        cdef PriorityMinHeap open_set = PriorityMinHeap() #Min heap of posible positions available for expansion

        #Dictionary containing (position:distance), which is the distance to
        #the goal from the position
        cdef dict g_score = {start:0}

        #Dictionary containing the relationship between posititions
        cdef dict came_from = {start:start}

        cdef int depth = 0 #Controls the number of entries in the path we want to compute
        cdef tuple neighbour, current
        
        open_set.insert(start, lattice_distance(start, goal))


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
                

    cpdef list recompute_path(self, list current_path, tuple pos, tuple target):
        cdef list extension_path
        cdef tuple n_step

        if len(current_path) > 1:
            extension_path = self.new_path(pos, current_path[-2])
            del current_path[-1]
            for n_step in extension_path[1:]:
                current_path.append(n_step) 
        else:
            current_path = self.new_path(pos, target)
        return current_path




