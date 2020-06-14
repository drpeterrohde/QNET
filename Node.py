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


# SUB CLASSES

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
    def __init__(self, name=None, coords=[0,0,0], e=1, p=1, px=0, py=0, pz=0, t=0, v_cart=[0, 0], line1=None,
                 line2=None, cartesian=True, **kwargs):
        """
        Intialises the satellite class. If cartesian == True, satellite coordinates will be cartesian and  it will
        travel in a fixed plane.
        Else the satellite will be initalised with the given TLEs with geodesic coordinates.
        If either TLE is invalid or None, the satellite defaults to ISS Zarya with geodesic coordinates

        Parameters
        ----------
        name : String
            Name of the satellite. The default is None.
        coords : Array of floats
            Coords of satellite, usage [x,y,z]. The default is [0,0,0].
        e : float
            Efficiancy. The default is 1.
        p : float
            Proportion of surviving photons that haven't changed state. The default is 1.
        px : float
            Probability of x-flip (Bitflip). The default is 0.
        py : float
            Probability of y-flip. The default is 0.
        pz : float
            Probability of z-flip (Dephasing). The default is 0.
        t : float
            Time (in seconds) ahead of the current time from which the satellite is started being tracked. The default is 0.
        v_cart: Array of floats
            Cartesian velocity of Satellite.
        line1 : String
            Line 1 of TLE of the satellite to be added in the network. The default is ''.
        line2 : String
            Line 2 of TLE of the satellite to be added in the network. The default is ''.
        **kwargs : TYPE
            Other costs or qualifying attributes.

        Returns
        -------
        None.

        """
        # Initialise coordinate type
        self.cartesian = cartesian

        if cartesian is True:
            self.velocity = v_cart
            super().__init__(name, coords, e, p, px, py, pz, **kwargs)

        else:
            # TODO: Figure out where globals should go?
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
                geometry = satellite.at(t_new)
                subpoint = geometry.subpoint()
                self.coords = [int(subpoint.latitude.degrees), int(subpoint.longitude.degrees), int(subpoint.elevation.km)]
            except:
                # Add ISS Zarya to the network by default if the given TLE is invalid
                # l1 and l2 are TLE of ISS Zarya
                l1 = '1 25544U 98067A   20154.85125762  .00002004  00000-0  43906-4 0  9990'
                l2 = '2 25544  51.6443  59.4222 0002071  22.0017  92.6243 15.49416742229799'
                satellite = EarthSatellite(l1, l2, self.name, ts)
                geometry = satellite.at(t_new)
                subpoint = geometry.subpoint()
                geo_coords = [int(subpoint.latitude.degrees), int(subpoint.longitude.degrees), int(subpoint.elevation.km)]
                super().__init__(name, geo_coords, e, p, px, py, pz, **kwargs)

            print(t_now.utc)

    def posUpdate(self, dt):
        if self.cartesian is True:
            vx = self.velocity[0]
            vy = self.velocity[1]
            self.coords = [self.coords[0] + vx * dt, self.coords[1] + vy * dt, self.coords[2]]

        else:
            # TODO: Figure out where globals should go?
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

    def cart_distance(self, node):
        sx, sy, sz = self.coords
        x, y, z = node.coords
        return np.sqrt((x-sx)**2 + (y-sy)**2 + (z-sz)**2)
    
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
        if self.cartesian is True:
            # Straight line distance between nodes
            dist = self.cart_distance(node)
            # Difference in altitude
            dz = self.coords[2] - node.coords[2]
            assert(dz > 0), f"Satellite altitude [{self.coords[2]}] must be greater than node altitude. [{node.coords[2]}]"
            # Altitude angle
            theta = np.arcsin(dz/dist)

        else:
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
        

        ## Check if satellite is above the horizon before making an edge ##
        '''
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
    
