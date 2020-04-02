"""
Created on Fri Mar  6 13:02:25 2020

WORK IN PROGRESS

@author: hudson
"""

import newtworkx as nx
import QNET
import numpy as np

# Returns a linear networkx graph of size n with qnode objects according to specified parameters
def linGen(n, spacing = 0, ground_ratio = None, swapper_ratio = None):
    assert(n > 2)
    if ground_ratio != None and swapper_ratio != None:
        
        assert 1 >= ground_ratio + swapper_ratio
        assert 0.5 >= swapper_ratio, "swapper_ratio cannot be greater than 0.5"
        
        # Get max numbers of each node type
        max_ground = np.floor(n * ground_ratio)
        max_swapper = np.floor(n * swapper_ratio)
        max_normal = n - (max_ground - max_swapper)

    else:
        # Ask for equal number of grounds and swappers
        max_ground = np.floor(n/2)
        max_swapper = np.floor(n/2)
        max_normal = n - (max_ground + max_swapper)
        
    G = nx.graph()
    
    # initialise counters for node types:
    normal_count = 0
    ground_count = 0
    swapper_count = 0
    
    # Add head node
    node = QNET.node('Head', coords = [0,0,0])
    G.add_node(node)
    normal_count += 1
        
    # Add nodes between head and tail:
    i = 1
    while i < n - 1:
        # Check the type of the previous node
        previous_type = type(node)
        if previous_type == type(QNET.Swapper()):
            # generate either a ground node or a plain node
            normalizer = (max_swapper - swapper_count) + (max_ground - ground_count) + (max_normal - normal_count)
            
            prob_swapper = (max_swapper - swapper_count) / normalizer
            prob_ground = (max_ground - ground_count) / normalizer
            prob_normal = (max_normal - normal_count) / normalizer
            
            # Make new node according to probability distribution
            
            newNode = np.random.choice([QNET.node('i'), QNET.ground('i'), QNET.swapper('i')],
                             [prob_normal, prob_ground, prob_normal])
            
            # Add node to graph
            G.add_node(newNode)
            
            # Update counter
            if type(newNode) == type(QNET.Ground):
                ground_count += 1
            elif type(newNode) == type(QNET.Swapper):
                swapper_count += 1
            else:
                normal_count += 1
            