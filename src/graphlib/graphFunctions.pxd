
cdef extern from "astarlattice.h":
    
    void setLatticeSize(int size)
    int latticeDistance(int x_src, int y_src, int x_dest, int y_dest)

    void addNode(int x, int y, int roadType)
    void addNeighbor(int x_s, int y_s, int x_d, int y_d);
    void printGraph()

    void restartAStar()
    int computeAStarPath(int x_src, int y_src, int x_dest, int y_dest, int *x_positions, int* y_positions)
    
    void printPath(int *x_positions, int *y_positions)
    void destroyPath(int * x_positions, int *y_positions)

