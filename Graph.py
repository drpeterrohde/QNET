import QNET
import scipy
import numpy

class Graph:
    def __init__(self, nodes, attributeKey = 'loss'):
        self.adjacencyMatrix = numpy.zeros((len(nodes), len(nodes)))

        for i in range(0,len(nodes)-1):
            neighbours = nodes[i].channels
            for nchan in neighbours:
                destIndex = nodes.index(nchan.dest)
                cost = nchan.cost
                self.adjacencyMatrix[i, destIndex] = cost[attributeKey]

    def shortestPath(self, Alice, Bob, method = ''):
        return 0