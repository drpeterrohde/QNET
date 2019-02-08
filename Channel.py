import QNET

class Channel:
    allChannels = []

    def __init__(self, name = 'QNET Channel', source = False, dest = False):
        self.name = name
        self.source = source
        self.dest = dest
        self.cost = QNET.CostVector()
        QNET.Channel.allChannels.append(self)

    def __str__(self):
        return('Channel: ' + self.name + '\n ' + str(self.cost))