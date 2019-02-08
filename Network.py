import QNET

class Network:
    def __init__(self, name = 'QNET Network'):
        self.name = name
        self.nodes = []
        self.channels = []

    def __str__(self):
        return('Network: ' + self.name +
            '\n Nodes: ' + str(len(self.nodes)) + ', Channels: ' + str(len(self.channels)))

    def addNode(self, node):
        self.nodes.append(node)
       
    def addChannel(self, channel):
        self.channels.append(channel)