
#define SIZE 300

struct CityNode *graph[SIZE][SIZE];
int LATTICE_SIZE;
int PATH_LENGTH;

typedef struct CityNode
{
    int x;
    int y;
    int roadType;
    struct CityNode *neighbors[4];
    int num_neighbors;

    // Heap and a* variables
    int in_closed_set; //Boolean variable
    int g_score; //Current g_score of the node, a value of -1 means no g_score
    struct CityNode* cameFrom; //Points to the node previous to this.
    int index; //Current index of the node in the Heap, a value of -1 means that it is not in the heap.
    int key; //Value used in the binary heap to sort the nodes 

};

typedef struct Heap{
    int counter;
    struct CityNode *array[SIZE];
};


//Sets the lattice size
void setLatticeSize(int size);

// Adds a new node to the global variable *graph
void addNode(int x, int y, int roadType);
// Adds a new neighbor (x_d, y_d) to the node (x_s, y_x)
void addNeighbor(int x_s, int y_s, int x_d, int y_d);
// Print lines with the content of the graph
void printGraph();



/*Functions to implement the binary heap and A*  */
// Source: https://gist.github.com/sudhanshuptl/d86da25da46aa3d060e7be876bbdb343

void restartAStar();
int computeAStarPath(int x_src, int y_src, int x_dest, int y_dest, int *x_positions, int* y_positions);
int reconstructPath(int *x_positions, int *y_positions, struct CityNode *current, int x_src, int y_src);
void printPath(int *x_positions, int *y_positions); 
void destroyPath(int * x_positions, int *y_positions);
int latticeDistance(int x_src, int y_src, int x_dest, int y_dest);


struct Heap* createHeap();
void insert(struct Heap *heap, int key, struct CityNode * node);
void update(struct Heap *heap, int key, struct CityNode *node);
struct CityNode * popMin(struct Heap *heap);
void heapify_bottom_top(struct Heap *heap, int node_index);
void heapify_top_bottom(struct Heap *heap, int parent_index);
void printHeap(struct Heap *heap);



