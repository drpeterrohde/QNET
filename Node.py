import QNET
import Utilities
import numpy as np
import scipy.integrate
from pvlib import atmosphere
import warnings

# If qnode doesn't have a name, consider having a global counter that
# keeps track of number of nodes and just names it after the number

class Qnode:
    """
    Default Qnode Class
    """

########## MAGICS ##########
    def __init__(self, name = None, coords = [0]*3, e = 1, p = 1, px = 0, py = 0, pz = 0, **kwargs):
        """
        Qnode Initialization
        :param str name: Name of Qnode
        :param list coords: Cartesian coordinates. Usage: [x,y,z]
        :param float e: Efficiancy. Proportion of photons that pass through the Qnode
        :param float p: Proportion of surviving photons that haven't changed state
        :param float px: Probability of x-flip (Bitflip)
        :param float py: Probability of y-flip
        :param float pz: Probability of z-flip (Dephasing)
        :param float kwargs: Other costs or qualifying attributes

        """
        if name == None:
            self.name = "N.A."
        else:
            self.name = name

        assert (len(coords) == 3), "Usage: [x, y, z]"
        self.coords = coords

        # Initialize cost vector
        costs = QNET.make_cost_vector(e, p, px, py, pz, **kwargs)
        self.costs = costs
        
    def __str__(self):
        return self.name
        # Formerly:
        # Qnode.name: ' + self.name + " -- " + "Coords:" + str(self.coords) + " -- " + str(type(self))
    
    def __repr__(self):
        return self.name
        # Possible add on:
        # f'{self.__class__.__name__}('f'{self.color!r}, {self.mileage!r})'

    def get_cost(self, costType):
        try:
            val = self.costs[costType]
        except:
            assert(False), f"\"{costType}\" is not a cost or attribute of \"{self.name}\"."


########## SUB CLASSES ##########

class Ground(Qnode):
    def __init__(self, name = None, coords = [0]*3, e = 1, p = 1, px = 0, py = 0, pz = 0, **kwargs):
        """
        Ground Node initialization
        :param str name: Name of Qnode
        :param list coords: Cartesian coordinates. Usage: [x,y,z]
        :param float e: Efficiancy. Proportion of photons that pass through the Qnode
        :param float p: Proportion of surviving photons that haven't changed state
        :param float px: Probability of x-flip (Bitflip)
        :param float py: Probability of y-flip
        :param float pz: Probability of z-flip (Dephasing)
        :param float kwargs: Other costs or qualifying attributes
        """
        super().__init__(name, coords, e, p, px, py, pz, **kwargs)
        

class Satellite(Qnode):
    def __init__(self, name = None, coords = [0]*3, e = 1, p = 1, px = 0, py = 0, pz = 0,
                 velocity = [0]*2, range = 0, **kwargs):
        """
        Satellite initialization
        :param str name: Name of Qnode
        :param list coords: Cartesian coordinates. Usage: [x,y,z]
        :param float e: Efficiancy. Proportion of photons that pass through the Qnode
        :param float p: Proportion of surviving photons that haven't changed state
        :param float px: Probability of x-flip (Bitflip)
        :param float py: Probability of y-flip
        :param float pz: Probability of z-flip (Dephasing)
        :param list velocity: Cartesian coordinates. Usage [vx, vy]
        :param float satRange: Range of Satellite communication
        :param float kwargs: Other costs or qualifying attributes
        """
        self.velocity = velocity
        self.range = range
        super().__init__(name, coords, e, p, px, py, pz, **kwargs)

        # Warn user if satellite parameters aren't initialized
        if (self.velocity == [0]*2):
            warnings.warn(message = f"Satellite \'{self.name}\' has no velocity")
        if (self.range == 0):
            warnings.warn(message = f"Satellite \'{self.name}\' has no range")
    
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
     
class Swapper(Qnode):   
    # prob is probability of succesful swapping between nodes
    def __init__(self, name = None, coords = [0]*3, e = 0.5, p = 1, px = 0, py = 0, pz = 0, **kwargs):
        """
        Swapper node initialization (Notice that "e" defaults to 0.5)
        :param str name: Name of Qnode
        :param list coords: Cartesian coordinates. Usage: [x,y,z]
        :param float e: Efficiancy. Proportion of photons that pass through the Qnode
        :param float p: Proportion of surviving photons that haven't changed state
        :param float px: Probability of x-flip (Bitflip)
        :param float py: Probability of y-flip
        :param float pz: Probability of z-flip (Dephasing)
        :param float kwargs: Other costs or qualifying attributes
        """
        super().__init__(name, coords, e, p, px, py, pz, **kwargs)

class PBS(Swapper):
    def __init__(self, name = None, coords = [0]*3, e = 0.5, p = 1, px = 0, py = 0, pz = 0, **kwargs):
        """
        Polarizing Beam Splitter Swapper node initialization (Notice that "e" defaults to 0.5)
        :param str name: Name of Qnode
        :param list coords: Cartesian coordinates. Usage: [x,y,z]
        :param float e: Efficiancy. Proportion of photons that pass through the Qnode
        :param float p: Proportion of surviving photons that haven't changed state
        :param float px: Probability of x-flip (Bitflip)
        :param float py: Probability of y-flip
        :param float pz: Probability of z-flip (Dephasing)
        :param float kwargs: Other costs or qualifying attributes
        """
        assert(e <= 0.5), "Type \"PBS\" cannot have \"e\" value greater than 0.5."
        super().__init__(name, coords, e, p, px, py, pz, **kwargs)

class CNOT(Swapper):
    def __init__(self, name = None, coords = [0]*3, e = 0.5, p = 1, px = 0, py = 0, pz = 0, **kwargs):
        """
        Polarizing Beam Splitter Swapper node initialization (Notice that "e" defaults to 0.5)
        :param str name: Name of Qnode
        :param list coords: Cartesian coordinates. Usage: [x,y,z]
        :param float e: Efficiancy. Proportion of photons that pass through the Qnode
        :param float p: Proportion of surviving photons that haven't changed state
        :param float px: Probability of x-flip (Bitflip)
        :param float py: Probability of y-flip
        :param float pz: Probability of z-flip (Dephasing)
        :param float kwargs: Other costs or qualifying attributes
        """
        super().__init__(name, coords, e, p, px, py, pz, **kwargs)
    