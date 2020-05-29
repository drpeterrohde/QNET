#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May 25 18:48:05 2020

@author: deepeshsingh
"""

import QNET
import Utilities
import numpy as np
import scipy.integrate
from pvlib import atmosphere
import warnings
from skyfield.api import EarthSatellite
from skyfield.api import Topos, load

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
    def __init__(self, name = None, coords = [0,0,0], e = 1, p = 1, px = 0, py = 0, pz = 0, t  = 0, line1='', line2 ='', **kwargs):
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
        super().__init__(name, coords, e, p, px, py, pz, **kwargs)
        
        global ts
        global t_now
        global t_startTime
        global t_new
        global satellite

        ## Define the time at which the satellite is being tracked ##
        ts = load.timescale()
        t_now = ts.now()
        t_startTime = ts.utc(t_now.utc[0], t_now.utc[1], t_now.utc[2], t_now.utc[3], t_now.utc[4], t_now.utc[5]+t)
        t_new = t_startTime 

        ## Initialise which satellite to track. Default is ISS Zarya ##
        try:
            satellite = EarthSatellite(line1, line2, self.name, ts)
        except:    
            stations_url = 'http://celestrak.com/NORAD/elements/stations.txt'
            satellites = load.tle_file(stations_url)        
            by_name = {sat.name: sat for sat in satellites}
            satellite = by_name['ISS (ZARYA)']
        
        ## find satellite location in topocentric coordinates at given time with boston at center ##
        geometry = satellite.at(t_new)
        subpoint = geometry.subpoint()
        print(t_now.utc)
        

        self.coords = [int(subpoint.latitude.degrees), int(subpoint.longitude.degrees), int(subpoint.elevation.km)]
                     
    def posUpdate(self, dt):   
        global ts
        global t_new
        global sums
        t_new = ts.utc(t_new.utc[0], t_new.utc[1], t_new.utc[2], t_new.utc[3], t_new.utc[4], t_new.utc[5]+dt)
        geometry = satellite.at(t_new)
        subpoint = geometry.subpoint()
        self.coords = [int(subpoint.latitude.degrees), int(subpoint.longitude.degrees), int(subpoint.elevation.km)]
        
        return
    
    def setTime(self):
        '''
        Restart tracking the satellite. 
        
        Reset the time to the start time after function: QNET.update(dt) has been applied in some process

        Returns
        -------
        None.

        '''
        global t_startTime
        global t_new
        t_new = t_startTime
        
        return
    
    def distance(self, node):
        global t_new        
        node_location = Topos(float(node.coords[0]), float(node.coords[1]))
        difference = satellite - node_location
        topocentric = difference.at(t_new)
        alt, az, distMagnitude = topocentric.altaz()
        
        return int(distMagnitude.km/1000)
        
    def airCost(self, node):
        """
        :param Qnode() node: The target node for the satellite communication
        :return list: [e, p] -- [Transmission probability, phasing probability]
        """

        # TODO:
        """
        We want the aircost to be able to return both the efficiency and p,
        but this requires more advanced understanding of how e and p change with
        effective density.
        
        """
        global t_new        
        node_location = Topos(float(node.coords[0]), float(node.coords[1]))
        difference = satellite - node_location
        topocentric = difference.at(t_new)
        alt, az, dist1 = topocentric.altaz()
        theta = alt.degrees
        dist = self.distance(node)
            
            
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
            
        # Perform numerical integration to get effective density (?)
        #d = scipy.integrate.quad(rho, 0, int(dist.km/1000), args = (theta))[0]
        d = scipy.integrate.quad(rho, 0, dist, args = (theta))[0]

        # TODO:
        """
        Given effective distance, write functions for transmission probability
        and phasing probability
        """

        def transmission_probability(d):
            """
            Calculate proportion of photons that survive the transmission given effective density
            :param float d: Effective density
            :return float: "p" Probability of survival
            """

            # Attenuation coefficient
            K = 0.01
            return QNET.convert(d * K, 'linear')

        def phasing_probability(d):
            """
            Calculate proportion of surviving photons that undergo no phase transition given effective density
            :param float d: Effective density
            :return float: "e" probability of no phase flip.
            """

            # Attenuation coefficient
            K = 0.01
            return QNET.convert(d * K, 'linear')
        
        '''
        ## Check if satellite is above the horizon before making an edge ##
        if alt.degrees>0:
            results = [transmission_probability(d), phasing_probability(d)]
        else:
            results = [0,0]
        '''
        
        results = [transmission_probability(d), phasing_probability(d)]
        
        return results

     
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
    
