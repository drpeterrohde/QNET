import QNET
from CostVector import CostVector

# TODO:
# Tidy up so we only have to import QNET

class Channel:
    allChannels = []

    def __init__(self, name = 'QNET Channel', source = False, dest = False):
        self.name = name
        self.source = source
        self.dest = dest
        
        # Initialise cost vector
        initialD = {'loss': 0.0}
        self.cost = CostVector(initialD)
        
        QNET.Channel.allChannels.append(self)
        
        # For each node, add to node.channels
        source.channels.append(self)
        dest.channels.append(self)

    def __str__(self):
        return('Channel: ' + self.name + '\n ' + str(self.cost))

    # costs is a dictionary
    def setCosts(self, costs):
        self.cost.costs = costs

    # Add a cost to the dictionary?
    def setCost(self, attributeKey, value):
        self.cost.costs[attributeKey] = value
        
    # print cost attributes of the channel
    def printCost(self):
        print(self.cost.costs)
