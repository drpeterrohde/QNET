import QNET
import networkx as nx

class Qnode:
    
########## MAGICS ##########
    def __init__(self, name = 'Qnode', coords = [None]*3, costVec = None):
        self.name = name
        self.coords = coords
        self.costVec = QNET.CostVector()
        
    def __str__(self):
        return('Node: ' + self.name)
    

########## SUB CLASSES ##########

class Ground(Qnode):
    def __init__(self, name = 'ground', coords = [None]*3):
        super().__init__(name, coords)
        

class Satellite(Qnode):   
    # self, height, vx, vy, name, coords
    def __init__(self,
                 name = 'satellite',
                 coords = [None]*3,
                 velocity = [None]*2,
                 satRange = 100):
        
        super().__init__(name, coords)
        self.satRange = satRange
        self.velocity = velocity
    
    def posUpdate(self, dt):
        
        # MAX MAP DISTANCE:
        MAX = 10000
        
        i = 0
        while i < 2:
            self.coords[i] = self.coords[i] + self.velocity[i] * dt
            if (self.coords[i] > MAX):
                self.coords[i] = self.coords[i] - MAX
            elif (self.coords[i] < 0):
                self.coords[i] = self.coords[i] + MAX
            i += 1
        return
    
    
    # OUTDATED
    def nodesInRange(self, network):
        nodesInRange = []
        for node in network.nodes:
            if (self.distance(node) < self.satRange):
                nodesInRange.append(node)
        return nodesInRange
    
  
class Swapper(Qnode):   
    # prob is probability of succesful swapping between nodes
    def __init__(self,
                 name = 'swapper',
                 coords = [None]*3,
                 prob = 0.5):
        super().__init__(name, coords)
        self.prob = prob
        self.nodeType = 'swapper'
    
    # TODO
    def distribute(self, costType):
        swapperLoss = 1/self.prob
        
        for channel in self.channels:
            oldCost = channel.cost.costs[costType]
            newCost = oldCost + swapperLoss / 2
            channel.cost.costs[costType] = newCost    


class PBS(Swapper):
    def __init__(self,
                 coords = [None]*3,
                 prob = 0.5):
        super().__init__(coords)


class CNOT(Swapper):
    def __init__(self,
                 coords = [None]*3,
                 prob = 1):
        super().__init__(coords)
    