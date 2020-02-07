cimport graphFunctions
from libc.stdlib cimport malloc, free
from cpython.mem cimport PyMem_Malloc, PyMem_Free



# Global variables 
cdef int LATTICE_SIZE


cdef class Graph:


    def __cinit__(self, dict city_map):
        self.create_graph(city_map)
        
    cdef void create_graph(self, dict city_map):
        cdef int x_src, y_src, type_src
        cdef int x_dest, y_dest

        for ((x_src, y_src), type_src) in city_map.keys():
            graphFunctions.addNode(x_src,y_src,type_src)

        for (((x_src, y_src), _), neighbors) in city_map.items():
            for ((x_dest, y_dest), _ ) in neighbors:
                graphFunctions.addNeighbor(x_src, y_src, x_dest, y_dest)

        

    cpdef void visualize(self):
        graphFunctions.printGraph()
    

cdef class AStar():
    cdef int* x_arr
    cdef int* y_arr

    def __cinit__(self, size_t path_size):
        # Allocate some memory
        self.x_arr = <int *> PyMem_Malloc(path_size * sizeof(int))
        self.y_arr = <int *> PyMem_Malloc(path_size * sizeof(int))

    cdef list path_to_python(self, int length):
        cdef int i
        ppath=[]
        for i in range(length):
            ppath.append( (self.x_arr[i], self.y_arr[i]))
        return ppath

    cpdef list new_path(self,tuple start, tuple end):
        cdef int x_src, y_src, x_dest, y_dest, length

        x_src, y_src = start
        x_dest, y_dest = end
        
        graphFunctions.restartAStar()

        length = graphFunctions.computeAStarPath(x_src, y_src,x_dest, y_dest, self.x_arr, self.y_arr)
        ppath = self.path_to_python(length)   

        return  ppath

    cpdef list recompute_path(self,list current_path, tuple pos, tuple target):
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


    def __dealloc__(self):
        PyMem_Free(self.x_arr)
        PyMem_Free(self.y_arr)

    
cpdef void configure_lattice_size(size_t lattice_size, city_map=None):
    
    # Set the internal parameters of the C functions.
    graphFunctions.setLatticeSize(lattice_size)

cpdef int lattice_distance(tuple start, tuple end):
    cdef int x_src, y_src, x_dest, y_dest
    x_src, y_src = start
    x_dest, y_dest = end
    return graphFunctions.latticeDistance(x_src, y_src, x_dest, y_dest)