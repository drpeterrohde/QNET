import QNET

class Channel:
    allChannels = []

    def __init__(self, source = False, dest = False):
        self.name = ''
        self.source = source
        self.dest = dest
        self.costs = QNET.CostVector()
        QNET.Channel.allChannels.append(self)

    def __str__(self):
        return('Channel: ' + self.name)