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


def linear_swap_reduce(Q, source, dest):
    """
    Given a linear graph or subgraph, this function calculates the efficiency from head to tail if all valid swapper
    nodes are used. Currently, both this quantity and the normal efficiency of the path are returned

    In the future, if it's more efficient not to use any swappers, the normal efficiency of the path
    will be returned.

    :param Q: Linear Qnet Graph
    :return float: no_swap and swap efficiencies of the graph

    Example:

    A - G1 - T - G2 - T - G3 - B
    net_eff = min ( e[A-G1-T], e[T-G2], e[T-G3-B] ) * e[T]**2

    Where e[A-G-T] is taken to mean the efficiency of the path [A-G-T]
    and e[T] is taken to mean the efficiency cost of performing a swap with the node T.

    """
    # Check that path exists from A to B
    assert(nx.has_path(Q, source, dest))

    # Create generator of paths from A to B. If no generator exists raise exception
    path_gen = nx.all_simple_paths(Q, source, dest)
    assert (path_gen != None), f"No valid path exists between {source.name} and {dest.name}."

    #  Unpack generator. If more than one path exists, raise exception
    path_count = 0
    for obj in path_gen:
        path = QNET.Path(Q, obj)
        path_count += 1

    assert(path_count == 1), "More than one path exists, linear reduction cannot be done."

    # Does a Swapper with swapping potential exist?
    swap_candidate = None
    # Does ground exist before a swapper?
    front_ground = False
    # Local efficiency of a Ground - Swapper - Ground configuration (or equivalent)
    local_eff = 1
    # list of swapper nodes used in the swapping process
    swap_list = []
    # Total efficiency of path
    net_eff = 1

    # Current node
    cur = source
    # Counter
    i = 0

    while cur != dest:
        # If current node is a Ground and we haven't seen a Swapper yet, set front_ground to True
        if isinstance(cur, QNET.Ground) and swap_candidate is None:
            # Add node eff to local
            local_eff *= cur.costs['e']
            front_ground = True

        # If Current node is a Swapper and we've seen a ground node previously, we now have a candidate for a swapper
        # that could be used.
        elif isinstance(cur, QNET.Swapper) and front_ground is True:
            swap_switch = True
            if swap_candidate == None:
                swap_candidate = cur
            # If we had another swap candidate previously, update swap_candidate to be cheaper option
            elif swap_candidate.costs['e'] < cur.costs['e']:
                swap_candidate = cur

        # If current node is a Ground and we've seen a Swapper, we perform a swap with the local resources
        # (Front-Ground, Swapper, Back-Ground) and update net_eff.
        elif isinstance(cur, QNET.Ground) and swap_candidate is not None:
            # Add node eff to local
            local_eff *= cur.costs['e']

            # Update net_eff to local_eff if net_eff is smaller
            if local_eff < net_eff:
                 net_eff = local_eff

            # Add the swapper we were considering to the list of swappers used
            swap_list.append(swap_candidate)

            # Reset parameters to prepare for the next swap
            local_eff = 1
            swap_candidate = None
            front_ground = False

        # Otherwise include the node cost in the local efficiency
        else:
            local_eff *= cur.costs['e']

        # Increment counter and get the edge efficiency
        i += 1
        edge_costs = Q.get_edge_data(cur, path.node_array[i])

        # Update local_eff with edge efficiency
        local_eff *= edge_costs['e']
        # Move to next node
        cur = path.node_array[i]

        # If the new node is the destination
        if cur == dest:
            # Append node costs from dest
            local_eff *= cur.costs['e']
            # Update net_eff to local_eff if net_eff is smaller
            # This also handles the case where no valid swapper was encountered
            if local_eff < net_eff:
                 net_eff = local_eff

    # Multiply net_eff with the costs of all swappers used.
    for swapper in swap_list:
        net_eff *= swapper.costs['e']

    """Calculate cost of path without any swapping"""
    # Cost of path without swapping
    no_swap = 1
    # Length of path
    path_len = len(path.node_array)
    i = 0

    # Sum all edge efficiencies
    while (i < path_len - 1):
        cur = path.node_array[i]
        nxt = path.node_array[i + 1]
        edgeData = path.G.get_edge_data(cur, nxt)
        no_swap *= edgeData['e']
        i += 1

    # Sum all node efficiencies except for swappers
    for node in path.node_array:
        if not isinstance(node, QNET.Swapper):
            no_swap *= node.costs['e']

    # DEBUG: For now, return both swap and no swap:
    return(no_swap, net_eff)

    """
    # Return whatever cost is better
    if net_eff > no_swap:
        return net_eff
    else:
        return no_swap
    """

