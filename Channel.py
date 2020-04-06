import QNET
import numpy as np

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
        
