import QNET

class Node:
    allNodes = []

    def __init__(self):
        self.name = ''
        self.channels = []
        self.costs = QNET.CostVector()
        QNET.Node.allNodes.append(self)

    def __str__(self):
        return('Node: ' + self.name)