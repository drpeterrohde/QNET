import QNET
from CostVector import CostVector
import numpy as np

# TODO:
# Tidy up so we only have to import QNET

class Qchan:
    pass

########## CHANNEL CLASSES ##########

def Fiber(Channel):
    def __init__(self, 
                 attenuation = 0.0):
        self.attenuation = attenuation
        
    def getLoss(self):
        # Calculate of fiber
        dist = self.distance()
        dBLoss = dist * self.attenuation
        return dBLoss
        
