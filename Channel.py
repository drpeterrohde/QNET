import QNET

class Channel:
    allChannels = []

    def __init__(self):
        self.name = ''
        self.ports = [QNET.Node(), QNET.Node()]
        self.costs = QNET.CostVector()
        QNET.Channel.allChannels.append(self)

    def __str__(self):
        return('Channel: ' + self.name)