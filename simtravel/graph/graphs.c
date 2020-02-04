#include <stdio.h>
#include <stdlib.h>
#include "graphs.h"

struct Graph *createGraph(struct Edge edges[], int n)
{
    unsigned i;
    struct Edge *edge;
    // allocate memory for graph data structure
    struct Graph *graph = (struct Graph *)malloc(sizeof(struct Graph));
    
    // initialize head pointer for all vertices
    for (i = 0; i < N; i++)
        graph->head[i] = NULL;

    // add edges to the directed graph one by one

    for (i = 0; i < n; i++)
    {
        edge = &edges[i];
        
        // get source and destination vertex
        int src = edge->src;
        int dest = edges->dest;

        // allocate new node of Adjacency List from src to dest
        struct Node *newNode = (struct Node *)malloc(sizeof(struct Node));
        newNode->dest = dest;

        // point new node to current head
        newNode->next = graph->head[src];

        // point head pointer to new node
        graph->head[src] = newNode;
    }

    return graph;
}

struct Edge createEdge(int src, int dest)
{
    struct Edge *edge = (struct Edge*)malloc(sizeof(struct Edge));
    edge->src = src;
    edge->dest = dest;
    
    return *edge;
}

// Function to print adjacency list representation of graph
void printGraph(struct Graph *graph)
{
    int i;
    for (i = 0; i < N; i++)
    {
        // print current vertex and all ts neighbors
        struct Node *ptr = graph->head[i];
        while (ptr != NULL)
        {
            printf("(%d -> %d)\t", i, ptr->dest);
            ptr = ptr->next;
        }

        printf("\n");
    }
}

int main(int argc, char *argv[])
{
    // input array containing edges of the graph (as per above diagram)
    // (x, y) pair in the array represents an edge from x to y
    
    struct Edge edges[] =
        {
            {0, 1}, {1, 2}, {2, 0}, {2, 1}, {3, 2}, {4, 5}, {5, 4}};
    
    // calculate number of edges
    int n = sizeof(edges) / sizeof(edges[0]);

    // construct graph from given edges
    struct Graph *graph = createGraph(edges, n);

    // print adjacency list representation of graph
    printGraph(graph);

    return 0;
}