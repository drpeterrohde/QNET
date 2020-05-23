#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Mar 25 10:59:46 2020
@author: hudson

Definitions:
    p: 
        Probability of a bell state being distributed without dephasing.
    e:
        Efficiency. The proportion of photons that make it through a channel
    pz:
        Dephasing probability.
    px: 
        Bitflip probability
    py:
        yflip probability
    log_e:
        -log(e)
    d:
        -log(abs(1 - 2p))
"""

import copy
import numpy as np
import networkx as nx
import QNET

def make_cost_vector(e = 1, p = 1, px = 0, py = 0, pz = 0, **kwargs):
    """
    Creates a dictionary of costs for a qnode or qchan.

    NOTE:
        Dephasing probabilities (px, py, pz) are included here for future proofing and do not currently initialize.
        At the moment we assume one axis of dephasing: pz = 1 - p

    :param float e: Proportion of photons that pass through the channel
    :param float p: Proportion of surviving photons that haven't changed state. Range: (0.5, 1)
    :param float px: Probability of x-flip (Bitflip)
    :param float py: Probability of y-flip
    :param float pz: Probability of z-flip (Dephasing)
    :param float kwargs: Other costs or qualifying attributes
    :return dictionary: Cost vector

    Other instantiated costs:
    log_e:
        -log(e)
    d:
        -log(abs(2p - 1))
    """
    cost_vector = {'e': e, 'p': p, 'pz':pz}
    cost_vector.update(kwargs)

    # Assert that costs are within the correct range:
    assert(0 <= e <= 1), "Out of range"
    assert(0 <= p <= 1), "Out of range"

    # Caclulate pz from p or vice versa
    if p == 1:
        p = 1 - pz
        cost_vector['p'] = p
    elif pz == 0:
        pz = 1 - p
        cost_vector['pz'] = pz

    # Calculate log_e
    cost_vector['log_e'] = convert(e, 'log')

    # Calculate d from p
    cost_vector['d'] = fid_convert(p, 'd')

    # Initialize other attributes
    for arg in kwargs:
        cost_vector[arg] = kwargs[arg]

    return cost_vector


def convert(x, typ = None):
    """
    Convert a value to a linear or logarithmic regime.
    Handles infinities and other exceptions

    :param float x: Value to convert
    :param str typ: Type to convert to. Usage: {'log', 'linear}
    :return float: Converted value
    """
    valid_types = ['log', 'linear']
    assert(typ in valid_types), "Invalid type, please choose one from {\'log\', \'linear\'}"

    if typ == 'log':
        assert(0 <= x and x <= 1)
        return(-1 * np.log(x) + 0)

    elif typ == 'linear':
        assert(0 <= x)
        return(np.exp(-x))

    else:
        assert(False), "A weird exception has occurred."


def fid_convert(x, typ = None):
    """
    Convert the fidelity 'p' into its additive form (d = -log(2p - 1)) or vice versa.
    :param float x: Value to convert
    :param str typ: Type to convert to. Usage: {'p', 'd'}
    :return float: Converted value
    """
    valid_types = ['p', 'd']
    assert(typ in valid_types), "Invalid type, please choose one from {\'p\', \'d\'}"

    if typ == 'd':
        return -np.log(np.abs(2 * x - 1)) + 0

    elif typ == 'p':
        return (1 + np.exp(-x))/2

    else:
        assert(False), "A weird exception has occurred."


def shortest_path_length(Q, source, target, costType):
    """
    Get the shortest path cost in a Qnet for a given costType.
    Considers edge weights and node weights
    # TODO Considers only valid paths.

    :param Q: Qnet Graph
    :param Union[str, Qnode] source: Source node
    :param Union[str, Qnode] target: Target node
    :param str costType: Any of {'e', 'p', 'de', 'dp'}
    :return: float length of shortest path in units of costType
    """

    # 1. Create copy of graph
    # 2. Generate all simple paths
    # 3. If path is not valid, remove it
    # 4. Continue on with this modified graph

    def get_weight_function(costType):
        def weight(u, v, d):
            node_u_wt = u.costs[costType]
            node_v_wt = v.costs[costType]
            edge_wt = d.get(costType, 1)
            return node_u_wt / 2 + node_v_wt / 2 + edge_wt
        return weight

    assert costType in ['e', 'p'], "Please use one of the supported cost types: {'e', 'p'}"

    if costType == 'e':
        costType = 'log_e'

    elif costType == 'p':
        costType = 'd'

    # Get node "u"
    if isinstance(source, str):
        u = Q.getNode(source)
    elif isinstance(source, QNET.Qnode):
        u = source
    else:
        assert False, f"Argument must be a string or reference to Qnode"

    # Get node "v"
    if isinstance(target, str):
        v = Q.getNode(target)
    elif isinstance(target, QNET.Qnode):
        v = target
    else:
        assert False, f"Argument must be a string or reference to Qnode"

    # u = Q.getNode(source)
    # v = Q.getNode(target)

    weight = get_weight_function(costType)
    len = nx.shortest_path_length(Q, u, v, weight)

    if costType == 'log_e':
        len = convert(len, 'linear')

    elif costType == 'd':
        len = fid_convert(len, 'p')

    return len



