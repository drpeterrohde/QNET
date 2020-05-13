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
    
    Note for bell pairs, fidelity = p = 1 - px - py - pz

    WARNING:
        Future cost types cannot begin with the letter d. Find some way to assert this.
"""

import copy
import numpy as np
import networkx as nx
import QNET

def make_cost_vector(e = 1, p = 1, px = 0, py = 0, pz = 0, **kwargs):
    """
    Makes a cost vector for a qnode or qchan

    :param float e: Proportion of photons that pass through the channel
    :param float p: Proportion of surviving photons that haven't changed state
    :param float px: Probability of x-flip (Bitflip)
    :param float py: Probability of y-flip
    :param float pz: Probability of z-flip (Dephasing)
    :param float kwargs: Other costs or qualifying attributes

    :return dictionary: Cost vector
    """
    cost_vector = {'e': e, 'p': p, 'px': px, 'py': py, 'pz': pz}

    for cost in cost_vector:
        assert (0 <= cost_vector[cost] and cost_vector[
            cost] <= 1), f"Probability \"{cost} = {cost_vector[cost]}\" out of range"

    # Initialize log probabilities
    log_dict = {}
    for cost in cost_vector:
        x = cost_vector[cost]
        if x == 0:
            log = np.inf
        else:
            log = -1 * np.log(x) + 0
        log_dict["d" + cost] = log

    # Combine dictionaries
    cost_vector.update(log_dict)

    for attr in kwargs:
        cost_vector[attr] = kwargs[attr]

    # Set p and log p
    cost_vector['p'] = 1 - cost_vector['px'] - cost_vector['py'] - cost_vector['pz']
    cost_vector['dp'] = convert(cost_vector['p'], 'log')

    return cost_vector

"""
Old conversion functions 
(DEPRECIATED)

def P2Q(p):
    return 1 - p

def P2L(p):
    return -1 * np.log(p)

def L2P(l):
    return np.exp(-l)
"""

def convert(x, typ = None):
    """
    Convert a value to a linear or logarithmic regime.
    Handles infinities and other exceptions

    :param float x: Value to convert
    :param str typ: Usage: {'log', 'linear}
    :return float: Converted value
    """

    valid_types = ['log', 'linear']
    assert(typ in valid_types), "Invalid type"

    if typ == 'log':
        assert(0 <= x and x <= 1)
        return(-1 * np.log(x))

    elif typ == 'linear':
        assert(0 <= x)
        return(np.exp(-x))

    else:
        assert(False), "A weird exception has occurred."


def shortest_path_length(Q, source, target, costType):
    """
    :param Q: Qnet Graph
    :param str source: Name of source node
    :param str target: Name of target node
    :param str costType: Any of {'e', 'p', 'de', 'dp'}
    :return: float length of shortest path in units of costType
    """

    # Future proof:
    # Make it so that this function only considers valid paths in Q!

    def get_weight_function(costType):
        def weight(u, v, d):
            node_u_wt = u.costs[costType]
            node_v_wt = v.costs[costType]
            edge_wt = d.get(costType, 1)
            return node_u_wt / 2 + node_v_wt / 2 + edge_wt
        return weight

    is_lin = False
    if costType[0] != "d":
        is_lin = True
        costType = "d" + costType

    assert(costType in ['de', 'dp']), "Please use one of the supported cost types: {'e', 'p', 'de', 'dp}"

    u = Q.getNode(source)
    v = Q.getNode(target)
    weight = get_weight_function(costType)
    len = nx.shortest_path_length(Q, u, v, weight)

    if is_lin == True:
        len = convert(len, 'linear')

    return len

# DEPRECIATED
def weight(u, v, d):
    if type(u) == QNET.Swapper:
        return d['loss'] + QNET.P2L(u.prob)/2
    elif type(v) == QNET.Swapper:
        return d['loss'] + QNET.P2L(v.prob)/2
    else:
        return d['loss']



