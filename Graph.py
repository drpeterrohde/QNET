import QNET
import numpy as np
from scipy.sparse.csgraph._validation import validate_graph
from scipy.sparse.csgraph import shortest_path
from scipy.sparse.csgraph import reconstruct_path

class Graph:
    def __init__(self, nodes, attributeKey = 'loss'):
        # make inifinity \comment
        self.adjacencyMatrix = np.zeros((len(nodes), len(nodes)))

        for node in nodes:
            for channel in node.channels:
                sourceIndex = nodes.index(channel.source)
                destIndex = nodes.index(channel.dest)

                if attributeKey in channel.cost.costs:
                    cost = channel.cost.costs[attributeKey]
                else:
                    cost = 0

                self.adjacencyMatrix[sourceIndex, destIndex] = cost

        self.adjacencyMatrix = validate_graph(self.adjacencyMatrix, True)

    def shortestPath(self, Alice, Bob, method = 'auto'):
        solution = shortest_path(self.adjacencyMatrix, method, return_predecessors = True)#, indices = [Alice, Bob])
        return(solution)