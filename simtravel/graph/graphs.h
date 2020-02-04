// This file is the header file for the graphs C library.

// Define maximum number of vertices in the graph
#define N 6

// Data structure to store graph
typedef struct Graph
{
    // An array of pointers to Node to represent adjacency list
    struct Node *head[N];
}Graph;

// A data structure to store adjacency list nodes of the graph
typedef struct Node
{
    int dest;
    struct Node *next;
}Node;

// data structure to store graph edges
typedef struct Edge
{
    int src, dest;
}Edge;

// Function to create an adjacency list from specified edges
struct Graph *createGraph(struct Edge edges[], int n);

// Function to create an Edge
struct Edge createEdge(int src, int dest);

// Function to print adjacency list representation of graph
void printGraph(struct Graph *graph);