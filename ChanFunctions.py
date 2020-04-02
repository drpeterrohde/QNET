#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar  2 15:53:03 2020

@author: hudson
"""

import QNET
import numpy as np
import scipy.integrate
from pvlib import atmosphere

# Given an array of tuples, convert into Qchan objects and add to graph
def add_qchans_from(G, cbunch):
    qchans = []
    
    for chan in cbunch:
        # No dictionary
        if len(chan) == 2:
            
            # Find nodes
            u = QNET.getNode(G, chan[0])
            v = QNET.getNode(G, chan[1])
          
            # define zero'd dict
            d = {'loss': 0}
            
            # Add to graph
            G.add_edge(u, v, attr_dict = d)
        
        else:     
            assert len(chan) == 3, f"Invalid syntax: \"{chan}\" Correct usage: (u, v, d)"
        
            # Check valid dictionary
            assert type(chan[2]) == dict, f"Invalid syntax: {chan[2]} must be a dictionary"
            d = chan[2]
        
            # Find nodes
            u = QNET.getNode(G, chan[0])
            v = QNET.getNode(G, chan[1])
            
            # debug
            print(d)
            print(u)
            print(v)
        
            # Add channel to grapph
            G.add_edge(u, v, attr_dict = d)