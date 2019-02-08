import QNET
import scipy
import numpy

class Graph:
    def __init__(self, nodes, attributeKey = ''):
        self.adjacencyMatrix = numpy.zeros((len(nodes), len(nodes)))

        for i in range(1,len(nodes)):
            neighbours = nodes[i].channels
            for j in neighbours:
                destIndex = nodes.index(j.dest)
                cost = j.cost
                if attributeKey == '':
                    self.adjacencyMatrix[i,destIndex] = cost
                else:
                    self.adjacencyMatrix[i,destIndex] = cost[attributeKey]

    def shortestPath(self, Alice, Bob, method = ''):
        return 0