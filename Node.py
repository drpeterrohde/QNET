import QNET

class Node:
    allNodes = []

    def __init__(self, name = 'QNET Node'):
        self.name = name
        self.channels = []
        self.cost = QNET.CostVector()
        QNET.Node.allNodes.append(self)

    def __str__(self):
        return('Node: ' + self.name)

    def connectTo(self, dest):
        channel = QNET.Channel('QNET Channel', self, dest)
        self.channels.append(channel)
        return(channel)

    def setCosts(self, costs):
        self.cost.costs = costs

    def setCost(self, attributeKey, value):
        self.cost.costs[attributeKey] = value