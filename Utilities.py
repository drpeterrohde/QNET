#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Mar 25 10:59:46 2020
@author: hudson

Definitions:
    p: 
        Probability of a bell pair being distributed between A and B 
        for a given path without the state changing
    
    e:
        Efficiency. The proportion of photons that make it through a channel
        
    pz:
        Dephasing probability.
    px: 
        Bitflip probability
    py:
        yflip probability
        
    d**:
        Logarithmic form
    
    Note for bell pairs, fidelity = P
"""

import copy
import numpy as np
import QNET

"""
Old conversion functions
"""
def P2Q(p):
    return 1 - p

def P2L(p):
    return -1 * np.log(p)

def L2P(l):
    return np.exp(-l)

"""
Option 1:
    Keep track of units yourself with simple formula
"""

def convert(x, typ = None):
    valid_types = ['log', 'linear']
    assert(typ in valid_types), "Invalid type"
    if typ == 'log':
        assert(0 < x and x <= 1)
        return(-1 * np.log(x))
    elif typ == 'linear':
        assert(0 < x)
        return(np.exp(-x))
    else:
        assert(False), "An exception has occoured"
        

## OPTION 2 ##
"""
Option 2:
    Unit class that automatically keeps track of units for you
"""

class unit():
    def __init__(self, val, unit):
        
        self.valid_units = ['p', 'e', 'px', 'py', 'pz',
                   'dp', 'de', 'dpx', 'dpy', 'dpz']
        
        self.valid_conversions = {'p':'dp', 'e':'de', 'px':'dpx', 'py':'dpy', 
                                  'pz':'dpz','dp':'p', 'de':'e', 'dpx':'px', 
                                  'dpy':'dy', 'dpz':'pz'}
        
        assert(unit in self.valid_units)
        self.unit = unit
        self.val = val
        
        # TODO: Assert that units are in a correct range
        
    def check_valid(self):
        pass
    
    def __str__(self):
        return (str(self.val) + " " + str(self.unit))
      
    def convert(self, typ = None):
        
        # TODO: assert that type is different
        
        valid_types = ['log', 'linear']
        
        assert(typ in self.valid_units), "Invalid type"
        
        if typ == 'log':
            # change unit type
            self.unit = self.valid_conversions[self.unit]
            self.val = -1 * np.log(self.val)
            return(self.val)
        
        elif typ == 'linear':
            self.unit = self.valid_conversions[self.unit]
            self.val = np.exp(-self.val)
            return(self.val)
        else:
            assert(False), "An exception has occoured"
            
        
# Weight functions:
def weight(u, v, d):
    if type(u) == QNET.Swapper:
        return d['loss'] + QNET.P2L(u.prob)/2
    elif type(v) == QNET.Swapper:
        return d['loss'] + QNET.P2L(v.prob)/2
    else:
        return d['loss']
        
    
    