import QNET

class Node:
    allNodes = []

    def __init__(self, name = 'QNET Node'):
        self.name = name
        self.channels = []
        self.costs = QNET.CostVector()
        QNET.Node.allNodes.append(self)

    def __str__(self):
        return('Node: ' + self.name)

    def connectTo(self, dest, channel):
        channel.source = self
        channel.dest = dest
        self.channels.append(channel)

        