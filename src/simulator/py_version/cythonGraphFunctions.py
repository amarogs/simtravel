
from heapq import heappop, heappush

#GLOBAL ATTRIBUTES OF THIS CLASS

CITY, LATTICE_SIZE = None, None



def configure_lattice_size( lattice_size, city_map):
    global CITY, LATTICE_SIZE
    CITY = city_map
    LATTICE_SIZE = lattice_size


def  lattice_distance( x1,  y1,  x2,  y2):
    return c_lattice_distance(x1, y1, x2, y2)

def  c_lattice_distance( x1,  y1,  x2,  y2):
    global LATTICE_SIZE
    
    dx = abs(x1-x2)
    if dx > int(LATTICE_SIZE/2):
        dx = LATTICE_SIZE - dx
    dy = abs(y1-y2)
    if dy > int(LATTICE_SIZE/2):
        dy = LATTICE_SIZE - dy
    
    return (dx + dy)


class PriorityMinHeap(object):
    """This class has been made using the example in https://docs.python.org/2/library/heapq.html """


    def __init__(self):
        self.pq = [] #List arranged as a min heap
        self.entry_finder = {} #mapping of items to enties
        self.REMOVED = (99999,99999) #placeholder for a removed task
        self.counter = 0 #Number of elements that are not removed in the heap

    def insert(self,  item,  priority):
        if item in self.entry_finder:
            self.remove_item(item)
        
        entry = [priority, item]
        self.entry_finder[item] = entry
        heappush(self.pq, entry)
        
        self.counter += 1

    def remove_item(self,  item):
        "Mark an existing task as REMOVED"
        entry = self.entry_finder.pop(item)
        entry[-1] = self.REMOVED
        self.counter -= 1

    def pop(self):
        "Remove and return the lowest priority item that is not REMOVED"
        

        while self.pq:
            entry = heappop(self.pq)
            item = entry[1]
            if item is not self.REMOVED:
                self.counter -= 1
                del self.entry_finder[item]
                return item
    def is_empty(self):
        return self.counter == 0




def  reconstruct_path( came_from, start, current):
    
    total = [current]
    while True:
        current = came_from[current]
        if current==start:
            break
        else:
            total.append(current)
    return total


class AStar():
    
    def __init__(self, max_length):
        self.max_length = max_length

    def  new_path(self,  start,  goal):
        global CITY
        
        closed_set = set() #Set of positions already visited
        open_set = PriorityMinHeap() #Min heap of posible positions available for expansion

        #Dictionary containing (position:distance), which is the distance to
        #the goal from the position
        g_score = {start:0}

        #Dictionary containing the relationship between posititions
        came_from = {start:start}
        

        
        open_set.insert(start, c_lattice_distance(start.pos[0],start.pos[1], goal.pos[0], goal.pos[1]))


        while not open_set.is_empty():
            #If there are available nodos, take the most promising one (lowest f_score)
            current = open_set.pop()
            
            # Check for a end condition
            if current == goal:
                #If the node is the goal, we have finished
                return reconstruct_path(came_from,start, current)
            else:
                #Otherwise we need to explore the current node
                closed_set.add(current)

            road_type = current.cell_type
            successors = current.successors
            g_score_current = g_score[current]

            for successor in successors:
                
                if successor not in closed_set:
                    #If the neighbour hasn't been visited
                    #Compute the possible g_score
                    if successor not in current.prio_successors:
                        new_g_score = g_score_current + road_type + 1
                    else:
                        new_g_score = g_score_current + road_type

                    if successor not in g_score or new_g_score < g_score[successor]:
                        #Add the neighbour with the g_score to the heap
                        
                        open_set.insert(successor, new_g_score + c_lattice_distance(successor.pos[0], successor.pos[1], goal.pos[0], goal.pos[1]))
                        g_score[successor] = new_g_score
                        came_from[successor] = current
                

    def  recompute_path(self,  current_path,  current_cell,  target):
        
        

        if len(current_path) > 1:
            extension_path = self.new_path(current_cell, current_path[-2])
            del current_path[-1]
            for next_step in extension_path[1:]:
                current_path.append(next_step) 
        else:
            current_path = self.new_path(current_cell, target)
        return current_path




