# This file implements the wrapper class.

cimport cgraphs


cdef class PyGraph:
    cdef cgraphs.Graph* _c_graph
    

    def __cinit__(self, list edges):
        cdef cgraphs.Edge _c_edges[6]

        for (i, (src,dest)) in enumerate(edges):
            
            _c_edges[i] = cgraphs.createEdge(src, dest)

        self._c_graph = cgraphs.createGraph(_c_edges, len(edges))
        

    cpdef void visualize(self):
        cgraphs.printGraph(self._c_graph)