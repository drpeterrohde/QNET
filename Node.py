import QNET
import numpy as np
import scipy
from pvlib import atmosphere

class Node:
    
    # nodeAtrDict = {'name':name}
    
    def __init__(self, name = 'QNET Node', coords = [None]*3):
        self.name = name
        self.coords = coords
        self.channels = []
        self.cost = QNET.CostVector()
        self.nodeType = 'NA'
        

    def __str__(self):
        return('Node: ' + self.name)

    def connectTo(self, dest, costs = {'loss': 0}):
        channel = QNET.Channel('QNET Channel', self, dest)
        channel.setCosts(costs)
        self.channels.append(channel)
        dest.channels.append(channel)
        return(channel)

    def setCosts(self, costs):
        self.cost.costs = costs

    def setCost(self, attributeKey, value):
        self.cost.costs[attributeKey] = value
        
    def printChannels(self):
        print(f"List of channels Connecting to {self.name}:")
        for channel in self.channels:
            sourceNode = channel.source
            if (sourceNode.name == self.name):
                print(channel.dest)
            else:
                print(channel.source)
    

    # Input: self, target node
    # Returns distance
    def distance(self, target):
        
        sx = self.coords[0]
        sy = self.coords[1]
        sz = self.coords[2]
        
        tx = target.coords[0]
        ty = target.coords[1]
        tz = target.coords[2]
        
        return np.sqrt((sx - tx)**2 + (sy - ty)**2 + (sz - tz)**2)
    

class Ground(Node):
    def __init__(self, name = 'QNET Ground', coords = [None]*3):
        super().__init__(name, coords)
        self.nodeType = 'ground'


class Satellite(Node):   
    # self, height, vx, vy, name, coords
    def __init__(self, 
                 vx, 
                 vy, 
                 name = 'QNET Satellite',
                 coords = [None]*3,
                 satRange = 100):
        
        super().__init__(name, coords)
        self.velocity = [vx, vy]
        self.satRange = satRange
        self.nodeType = 'satellite'
        
    
    def costFunc(self, target):
        
        alt = self.coords[2]
        
        # Calculate ground distance from source to target:
        dist = self.distance(target)
        
        # Calculate azimuthal angle 
        theta = np.arcsin(alt / dist)
        
        
        """
        Line integral for effective density
        
          / L'
         |     rho(L * sin(theta)) dL
        /   0
        """
        
        def rho(L, theta):
            # From altitude, calculate pressure
            # Assume T = 288.15K and 0% humidity
            P = atmosphere.alt2pres(L * np.sin(theta))
            T = 288.15
            R = 287.058 # Specific gas constant of air
            return P / (R * T)
        
        # Perform numerical integreation to get effective density (?)
        result = scipy.integrate.quad(rho, 0, dist, args = (theta))[0]
        
        return result * 0.1
        
        # Original toy loss function
        # return dist * 0.1
    
    
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
    
    
    # Inputs: self, network
    # Returns List of nodes in satellite's range
    def nodesInRange(self, network):
        nodesInRange = []
        for node in network.nodes:
            if (self.distance(node) < self.satRange):
                nodesInRange.append(node)
        return nodesInRange
    
    
    def updateChannels(self):
        for channel in self.channels:
            #cost = channel.cost.costs
            
            # Update weight
            if (channel.source.name == self.name):
                channel.cost.costs['loss'] = self.costFunc(channel.dest)
            else:
                channel.cost.costs['loss'] = self.costFunc(channel.source)


  
class Swapper(Node):   
    # prob is probability of succesful swapping between nodes
    def __init__(self, 
                 name = 'QNET Swappper',
                 coords = [None]*3,
                 prob = 0.5):
        super().__init__(name, coords)
        self.prob = prob
        self.nodeType = 'swapper'
    
    def distribute(self, costType):
        swapperLoss = 1/self.prob
        for channel in self.channels:
            oldCost = channel.cost.costs[costType]
            newCost = oldCost + swapperLoss / 2
            channel.cost.costs[costType] = newCost    
    
class PBS(Swapper):
    def __init__(self,
                 name = 'PBS Swapper',
                 coords = [None]*3,
                 prob = 0.5):
        super().__init__(name, coords)
        
class CNOT(Swapper):
    def __init__(self,
                 name = 'PBS Swapper',
                 coords = [None]*3,
                 prob = 1):
        super().__init__(name, coords)
    