#include <stdio.h>
#include <stdlib.h>
#include "astarlattice.h"

// Sets the lattice size and reduces the size of the graph to match the lattice.

void setLatticeSize(int size)
{
    LATTICE_SIZE = size;
    for (int i = size; i < SIZE; i++)
    {
        for (int j = size; j < SIZE; j++)
        {
            free(graph[i][j]);
        }
    }
}
void addNode(int x, int y, int roadType)
{

    struct CityNode *node = malloc(sizeof(struct CityNode));

    if (node == NULL)
    {
        printf("Memory error!\n");
        return;
    }

    for (int i = 0; i < 4; i++)
    {
        node->neighbors[i] = NULL;
    }
    node->x = x;
    node->y = y;
    node->roadType = roadType;
    node->num_neighbors = 0;

    
    graph[x][y] = node;
}

void addNeighbor(int x_s, int y_s, int x_d, int y_d)
{
    struct CityNode *source_node = graph[x_s][y_s];
    source_node->neighbors[source_node->num_neighbors] = graph[x_d][y_d];
    source_node->num_neighbors += 1;
}

void printGraph()
{
    struct CityNode *node;
    struct CityNode *neighbor;

    for (int i = 0; i < SIZE; i++)
    {
        for (int j = 0; j < SIZE; j++)
        {

            node = graph[i][j];
            if (node != NULL)
            {
                printf("Nodo en (%d, %d) tipo: %d\n", node->x, node->y, node->roadType);
                for (int k = 0; k < node->num_neighbors; k++)
                {
                    neighbor = node->neighbors[k];
                    printf("Tiene vecino: (%d, %d) ", neighbor->x, neighbor->y);
                }
                printf("\n");
            }
        }
    }
}

void restartAStar()
{
    struct CityNode *node;
    for (int i = 0; i < SIZE; i++)
    {
        for (int j = 0; j < SIZE; j++)
        {
            node = graph[i][j];
            if (node != NULL)
            {
                node->in_closed_set = 0;
                node->g_score = -1;
                node->key = -1;
                node->index = -1;
            }
        }
    }
}

int reconstructPath(int *x_positions, int *y_positions, struct CityNode *current, int x_src, int y_src){
    int i = 0;

    int x = current->x, y = current->y;
    // printf("Before first insertion\n");
    x_positions[i] = x, y_positions[i] = y;

        while (1)
    {
        i += 1;
        current = current->cameFrom;
        x = current->x, y = current->y;
        if (x != x_src || y != y_src){
            x_positions[i] = x, y_positions[i] = y;
        }else{
            break;
        }
    }
    
    return i;

}
int computeAStarPath(int x_src, int y_src, int x_dest, int y_dest, int *x_positions, int *y_positions)
{
    
    struct CityNode *current, *neighbor;
    struct Heap *heap;
    int new_g_score, pathLength;
    


    // Restart the variables.
    restartAStar();

    // Set initial position variables.
    current = graph[x_src][y_src];
    current->g_score = 0;
    current->cameFrom = current;
    // Create a heap
    heap = createHeap();
    // insert(heap, latticeDistance(x_src, y_src, x_dest, y_dest), current);
    // printHeap(heap);
    
    while (current != NULL){

        if (current->x != x_dest || current->y != y_dest){
            //Add this node to the close set.
            current->in_closed_set = 1;

            // For each neighbor, if it is not in the closed set:
            for (int i = 0; i < current->num_neighbors; i++){
                neighbor = current->neighbors[i];

                if (!neighbor->in_closed_set){
                    // Compute the possible g_score.
                    new_g_score = current->g_score + neighbor->roadType;

                    if (neighbor->g_score == -1 || new_g_score < neighbor->g_score){
                        // Insert the neighbor into the heap, updating the key if necesary.
                        insert(heap, new_g_score + latticeDistance(neighbor->x, neighbor->y, x_dest, y_dest), neighbor);
                        neighbor->cameFrom = current;
                        
                    }

                }
            }
        }else{
            
            // We have finished, return the path
            pathLength = reconstructPath(x_positions, y_positions, current, x_src, y_src);
            free(heap);
            return pathLength;
            
        }

        current = popMin(heap);
    }


    
}


int latticeDistance(int x_src, int y_src, int x_dest, int y_dest)
{
    int dx, dy;
    dx = abs(x_src - x_dest);
    if (dx > (SIZE / 2))
        dx = SIZE - dx;

    dy = abs(y_src - y_dest);
    if (dy > (SIZE / 2))
        dy = SIZE - dy;

    return (dx + dy);
}
void destroyPath(int *x_positions, int *y_positions){
    free(x_positions);
    free(y_positions);
}

void printPath(int *x_positions, int *y_positions)
{
    printf("Path: ");
    for (int i = 0; i < PATH_LENGTH; i++)
    {
        printf("-> (%d, %d) ", x_positions[i], y_positions[i]);
    }
    printf("\n");
}
//***********START OF HEAP FUNCTIONS*******************************

// Create an empty heap
struct Heap *createHeap()
{

    struct Heap *heap = malloc(sizeof(struct Heap));
    if (heap == NULL)
    {
        printf("Memory error when creating the heap");
        return NULL;
    }

    heap->counter = 0;

    return heap;
}
void insert(struct Heap *heap, int key, struct CityNode *node)
{

    if (node->index != -1){
        // This node is already in the heap, we have to update its key.
        node->key = key;
        heapify_bottom_top(heap, node->index);

    }else{
        // We have no create a new place in the heap array

        if (heap->counter < SIZE){
            node->key = key;
            node->index = heap->counter;

            heap->array[heap->counter] = node;

            heapify_bottom_top(heap, heap->counter);
            heap->counter += 1;
        }else{
            printf(" Heap max SIZE exceeded\n");
        }
    }


}

void update(struct Heap *heap, int key, struct CityNode *node)
{
    node->key = key;
    // heap->array[node->index]->key = key;
    heapify_bottom_top(heap, node->index);
}
struct CityNode *popMin(struct Heap *heap)
{
    struct CityNode *pop;

    if (heap->counter == 0)
    {
        return NULL;
    }
    else
    {
        pop = heap->array[0];
        heap->array[0] = heap->array[heap->counter - 1];
        heap->counter -= 1;
        heapify_top_bottom(heap, 0);
        return pop;
    }
}
void heapify_bottom_top(struct Heap *heap, int node_index)
{
    int parent_index = (node_index - 1) / 2;
    int tmp_index;

    struct CityNode *tmp_node;

    if (heap->array[parent_index]->key > heap->array[node_index]->key)
    {

        // swap the indices
        heap->array[parent_index]->index = node_index;
        heap->array[node_index]->index = parent_index;

        // swap places in the array
        tmp_node = heap->array[parent_index];
        heap->array[parent_index] = heap->array[node_index];
        heap->array[node_index] = tmp_node;

        // recursive call
        heapify_bottom_top(heap, parent_index);
    }
}
void heapify_top_bottom(struct Heap *heap, int parent_index)
{
    int left_index = (2 * parent_index) + 1;
    int right_index = (2 * parent_index) + 2;
    int min_index = parent_index;
    struct CityNode *tmp;

    // Check for a child.
    if (left_index < 0 || left_index >= heap->counter)
    {
        left_index = -1; // There is no left child
    }

    if (right_index < 0 || right_index >= heap->counter)
    {
        right_index = -1; // There is no right child
    }

    if (left_index != -1 && heap->array[left_index]->key < heap->array[parent_index]->key)
    {
        min_index = left_index;
    }

    if (right_index != -1 && heap->array[right_index]->key < heap->array[min_index]->key)
    {
        min_index = right_index;
    }
    if (min_index != parent_index)
    {

        // Swap indeces
        heap->array[parent_index]->index = min_index;
        heap->array[min_index]->index = parent_index;

        // Swap places
        tmp = heap->array[parent_index];
        heap->array[parent_index] = heap->array[min_index];
        heap->array[min_index] = tmp;

        heapify_top_bottom(heap, min_index);
    }
}
void printHeap(struct Heap *heap)
{
    printf("HEAP: ");
    for (int i = 0; i < heap->counter; i++)
    {
        printf(" -> (%d, %d):%d ", heap->array[i]->x, heap->array[i]->y, heap->array[i]->key);
    }
    printf("\n");
}



//***********END OF HEAP FUNCTIONS*******************************
int main(void)
{
    int *x, *y;
    x = malloc(LATTICE_SIZE * sizeof(int));
    y = malloc(LATTICE_SIZE * sizeof(int));
    setLatticeSize(100);
    addNode(1, 2, 3);
    addNode(1, 3, 2);
    addNode(3, 3, 1);
    addNode(2, 1, 1);
    addNode(2, 3, 1);

    addNeighbor(1,2,1,3);
    addNeighbor(1,3,3,3);
    addNeighbor(3,3,2,1);
    addNeighbor(2, 1, 2, 3);

    printGraph();
    restartAStar();
    printf("ANTES\n");
    PATH_LENGTH = computeAStarPath(1,2,2,3, x, y);
    printPath(x,y);
    // heap = createHeap();
    // insert(heap, 10, graph[1][2]);
    // insert(heap, 7, graph[1][3]);
    // insert(heap, 5, graph[3][3]);
    // update(heap, 1, graph[1][2]);
    // printHeap(heap);

    // printf("Nodo %d\n", graph[1][2]);
    // printf("Nodoh %d\n", heap->array[0]);
    // struct CityNode *min = popMin(heap);
    // printf("Top: (%d, %d)\n", min->x, min->y);
    // printHeap(heap);
}