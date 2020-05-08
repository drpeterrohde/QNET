import QNET
import Utilities
import numpy as np
import scipy.integrate
from pvlib import atmosphere
import warnings

# If qnode doesn't have a name, consider having a global counter that
# keeps track of number of nodes and just names it after the number

class Qnode:

########## MAGICS ##########
    def __init__(self, **kwargs):
        """

        Parameters
        ----------
        **kwargs : dict
            Key word arguements specifying the node
            
            'name': str
                The name of the qnode. 
                "Is everyone with one face called a Milo?"
                - The Dodecahedron
            'qnode_type': str
                The class of qnode. Defaults to none.
                Choose from {'Ground', 'Satellite', 'Swapper'}
            'coords': array
                Spatial cartesian coordinates
                [x,y,z]
            
            Satellite kwargs
            ----------------
            'velocity': array
                Velocity of satellite
                [vx,vy]
            Swapper kwargs
            --------------
            'prob': float
                Probability of a successful swap

        Returns
        -------
        None.

        """        
        # Attempts to pop 'name' from kwarg dict. 
        # If not found, defaults to 'Qnode'
        self.name = kwargs.pop('name', 'Qnode')
        self.coords = kwargs.pop('coords', [0]*3)
        self.kwarg_warning(kwargs)
        
    def __str__(self):
        return self.name
        # Formerly:
        # Qnode.name: ' + self.name + " -- " + "Coords:" + str(self.coords) + " -- " + str(type(self))
    
    def __repr__(self):
        return self.name
        # Possible add on:
        # f'{self.__class__.__name__}('f'{self.color!r}, {self.mileage!r})'
    
    def kwarg_warning(self, kwargs):
        if len(kwargs) > 0:
            warnings.warn(f"The following key word arguments could not be initialised for for \'{self.name}\': {kwargs}")

########## SUB CLASSES ##########

class Ground(Qnode):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # name = 'ground', coords = [0]*3
        

class Satellite(Qnode):   
    # self, height, vx, vy, name, coords
    def __init__(self, **kwargs):
        self.velocity = kwargs.pop('velocity', [0]*2)
        self.satRange = kwargs.pop('satRange', 100)
        super().__init__(**kwargs)
        
        """
        # TODO: Make this warning look cleaner
        if (self.velocity == [0]*2):
            warnings.warn(message = f"Satellite \'{self.name}\' has no velocity")
        """
    
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
    
    def distance(self, node):
        
        x = self.coords[0]
        y = self.coords[1]
        z = self.coords[2]
        
        nx = node.coords[0]
        ny = node.coords[1]
        nz = node.coords[2]
        
        return np.sqrt((x - nx)**2 + (y - ny)**2 + (z - nz)**2)
    
    def airCost(self, node):
        alt = self.coords[2]
        
        # Calculate ground distance from source to target:
        dist = self.distance(node)
            
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
        
        # Attenuation constant:
        K = 0.001
        return result * K
        
    
        # OUTDATED
        def nodesInRange(self, network):
            nodesInRange = []
            for node in network.nodes:
                if (self.distance(node) < self.satRange):
                    nodesInRange.append(node)
            return nodesInRange
     
class Swapper(Qnode):   
    # prob is probability of succesful swapping between nodes
    def __init__(self, **kwargs):
        self.prob = kwargs.pop('prob', 0.5)
        self.loss = QNET.P2L(self.prob)
        super().__init__(**kwargs)

class PBS(Swapper):
    def __init__(self,
                 coords = [0]*3,
                 prob = 0.5):
        super().__init__(coords)

class CNOT(Swapper):
    def __init__(self,
                 coords = [0]*3,
                 prob = 1):
        super().__init__(coords)
    