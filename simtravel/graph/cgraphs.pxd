# This file redefines the C API to be used in Cython

cdef extern from "graphs.h":
    ctypedef struct Graph:
        pass
    
    ctypedef struct Edge:
        pass

    
    Graph *createGraph(Edge *edges, int n_edges)
    Edge createEdge(int src, int dest)

    void printGraph(Graph *graph)