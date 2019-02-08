import QNET

class Network:
    def __init__(self):
        self.name = ''
        self.nodes = []
        self.channels = []

    def __str__(self):
        return('Network: ' + self.name + '\n Nodes: ' + len(self.nodes) + ', Channels: ' + len(self.channels))

    def addNode(self, node):
        self.nodes.append(node)
       
    def addChannel(self, channel):
        self.channels.append(channel)