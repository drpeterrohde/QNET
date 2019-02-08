import QNET
import numpy

class Graph:
    def __init__(self, nodes, attributeKey = ''):
        self.adjacencyMatrix = numpy.zeros((len(nodes), len(nodes)))