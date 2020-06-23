"""
Created on Fri Mar 6 13:02:25 2020
@author: hudson
"""

import networkx as nx
import QNET
import numpy as np


def multidim_lattice(dim, size, e, p, periodic=False):
    dim = [size]*dim
    print(dim)
    G = nx.grid_graph(dim, periodic)

    Q = QNET.Qnet()
    for edge in G.edges():
        u = edge[0]
        v = edge[1]
        Q.add_qchan(edge=[u, v], e=e, p=p)
    return Q


def altLinGen(n, spacing, eVal=1, pxVal=0, pyVal=0, pzVal=0):
    '''
    Constructs a linear chain with end Qnodes A and B, and alternating Swapper and Ground nodes in the middle.

    Parameters
    ----------
    n : int
        Total number of nodes in the chain, including end nodes A and B.
    spacing : Array of float
        Distance between two consecutive nodes in [x,y,z] format.
    eVal : float
        Efficiency of a single channel in the regular lattice. The default is 1.
    pxVal : float
        Probability of state not undergoing X-flip in the regular lattice. The default is 0.
    pyVal : float
        Probability of state not undergoing Y-flip in the regular lattice. The default is 0.
    pzVal : float
        Probability of state not undergoing Z-flip in the regular lattice. The default is 0.

    Returns
    -------
    Q : QNET Graph
        A linear chain of length n consisting of alternating Bell pair generator and swappers.

    '''

    Q = QNET.Qnet()

    if n > 0:
        firstNode = QNET.Qnode(name='A', coords=spacing)
        Q.add_node(firstNode)

    previousNode = QNET.Qnode()
    currentNode = QNET.Qnode()

    ChannelList = []

    if n > 2:
        for i in range(n - 2):
            GroundNode = QNET.Ground(name=('G' + str(i + 1)), coords=np.multiply(i + 2, spacing))
            SwapNode = QNET.Swapper(name=('T' + str(i + 1)), coords=np.multiply(i + 2, spacing))

            if n > 3:
                if (i) % 2 == 0:
                    currentNode = SwapNode
                else:
                    currentNode = GroundNode
            else:
                currentNode = GroundNode

            Q.add_node(currentNode)

            if i > 0:
                ChannelList.append(
                    {'edge': (previousNode.name, currentNode.name), 'e': eVal, 'px': pxVal, 'py': pyVal, 'pz': pzVal})

            previousNode = currentNode

    if n > 1:
        lastNode = QNET.Qnode(name='B', coords=np.multiply(n, spacing))
        Q.add_node(lastNode)

        ChannelList.append(
            {'edge': (firstNode.name, list(Q.nodes)[1].name), 'e': eVal, 'px': pxVal, 'py': pyVal, 'pz': pzVal})
        ChannelList.append(
            {'edge': (list(Q.nodes)[n - 2].name, lastNode.name), 'e': eVal, 'px': pxVal, 'py': pyVal, 'pz': pzVal})

    Q.add_qchans_from(ChannelList)

    return Q


def altLinSatGen(n, spacing, eVal=1, pxVal=0, pyVal=0, pzVal=0, startTime=0, Line1='', Line2='', *args):
    '''
    Constructs a linear chain with end Qnodes A and B, and alternating Swapper and Ground nodes in the middle.

    A satellite is connected to end nodes A and B, and all swapper nodes.

    Parameters
    ----------
    n : int
        Total number of nodes in the chain, including end nodes A and B.
    spacing : Array of float
        Distance between two consecutive nodes in [x,y,z] format.
    eVal : float
        Efficiency of a single channel in the regular lattice. The default is 1.
    pxVal : float
        Probability of state not undergoing X-flip in the regular lattice. The default is 0.
    pyVal : float
        Probability of state not undergoing Y-flip in the regular lattice. The default is 0.
    pzVal : float
        Probability of state not undergoing Z-flip in the regular lattice. The default is 0.
    startTime : int
        Time in seconds from now (current time) starting which the satellite should be tracked. The default is 0.
    Line1 : String
        Line 1 of satellite TLE. The deault is ''.
    Line2 : String
        Line 2 of satellite TLE. The deault is ''.

    Returns
    -------
    Q : QNET Graph
        A linear chain of length n consisting of alternating Bell pair generator and swappers.
        End nodes A and B, and all swapper nodes are connected to a satellite.

    '''

    Q = QNET.Qnet()

    if n > 0:
        firstNode = QNET.Qnode(name='A', coords=spacing)
        Q.add_node(firstNode)

    previousNode = QNET.Qnode()
    currentNode = QNET.Qnode()

    ChannelList = []

    if n > 2:
        for i in range(n - 2):
            GroundNode = QNET.Ground(name=('G' + str(i + 1)), coords=np.multiply(i + 2, spacing))
            SwapNode = QNET.Swapper(name=('T' + str(i + 1)), coords=np.multiply(i + 2, spacing))

            if n > 3:
                if (i) % 2 == 0:
                    currentNode = SwapNode
                else:
                    currentNode = GroundNode
            else:
                currentNode = GroundNode

            Q.add_node(currentNode)

            if i > 0:
                ChannelList.append(
                    {'edge': (previousNode.name, currentNode.name), 'e': eVal, 'px': pxVal, 'py': pyVal, 'pz': pzVal})

            previousNode = currentNode

    if n > 1:
        lastNode = QNET.Qnode(name='B', coords=np.multiply(n, spacing))
        Q.add_node(lastNode)

        ChannelList.append(
            {'edge': (firstNode.name, list(Q.nodes)[1].name), 'e': eVal, 'px': pxVal, 'py': pyVal, 'pz': pzVal})
        ChannelList.append(
            {'edge': (list(Q.nodes)[n - 2].name, lastNode.name), 'e': eVal, 'px': pxVal, 'py': pyVal, 'pz': pzVal})

    S = QNET.Satellite(name='S', t=startTime, line1=Line1, line2=Line2)
    Q.add_node(S)

    nodeList = Q.nodes()
    for node in nodeList:
        if type(node) != QNET.Ground and type(node) != QNET.Satellite:
            ChannelList.append({'edge': (node.name, S.name)})

    Q.add_qchans_from(ChannelList)

    return Q


def RegLat(x, y, xspacing, yspacing=[0, 0, 0], eVal=1, pVal=1, pxVal=0, pyVal=0, pzVal=0):
    '''
    Constructs a 2D Regular Lattice with end Qnodes A and B, and alternating Swapper and Ground nodes in the middle.


    Parameters
    ----------
    x : int
        Number of columns in the regular lattice.
    y : int
        Number of rows in the regular lattice.
    xspacing : 3x1 Array of float
        Distance between two consecutive columns in 2D regular lattice in [x,0,0] format.
    yspacing : 3x1 Array of float
        Distance between two consecutive rows in 2D regular lattice in [0,y,0] format. The default is [0,0,0].
    eVal : float
        Efficiency of a single channel in the regular lattice. The default is 1.
    pxVal : float
        Probability of state not undergoing X-flip in the regular lattice. The default is 0.
    pyVal : float
        Probability of state not undergoing Y-flip in the regular lattice. The default is 0.
    pzVal : float
        Probability of state not undergoing Z-flip in the regular lattice. The default is 0.

    Returns
    -------
    Q : QNET Graph
        A y*x 2D regular lattice.

    '''

    assert (x > 0)
    assert (y > 0)

    if yspacing == [0, 0, 0]:
        yspacing[1] = xspacing[0]

    Q = QNET.Qnet()

    firstNode = QNET.Qnode(name='A', coords=[0, 0, 0])
    lastNode = QNET.Qnode(name='B', coords=np.add(np.multiply(x - 1, xspacing), np.multiply(y - 1, yspacing)))

    previousNode = QNET.Qnode()
    currentNode = QNET.Qnode()

    ChannelList = []

    # Constructing the nodes in the Regular Lattice
    for i in range(x):
        for j in range(y):

            GroundNode = QNET.Ground(name=('G(' + str(i + 1) + ',' + str(j + 1) + ')'),
                                     coords=np.add(np.multiply(i, xspacing), np.multiply(j, yspacing)))
            SwapNode = QNET.Swapper(name=('T(' + str(i + 1) + ',' + str(j + 1) + ')'),
                                    coords=np.add(np.multiply(i, xspacing), np.multiply(j, yspacing)))

            # Swap nodes at odd positions and Ground nodes at even positions in a Regular Lattice
            if x >= 1 and y >= 1:
                if (i + j) % 2 == 0:
                    currentNode = GroundNode
                else:
                    currentNode = SwapNode

                    # Linear chain of length 3 exception
            if (x == 3 and y == 1) or (x == 1 and y == 3):
                currentNode = GroundNode

            # 2*2 2D lattice exception
            if x == 2 and y == 2:
                currentNode = GroundNode

            # Initialising the first node as A
            if i == 0 and j == 0:
                currentNode = firstNode

            # Initialising the last node as B
            if i == (x - 1) and j == (y - 1):
                currentNode = lastNode

            Q.add_node(currentNode)

            previousNode = currentNode

    # Constructing the vertical edges in the Regular Lattice
    for i in range(x):
        previousNode = list(Q.nodes)[i * y]
        for j in range(y - 1):
            currentNode = list(Q.nodes)[j + 1 + (i * y)]
            ChannelList.append(
                {'edge': (previousNode.name, currentNode.name), 'e': eVal, 'p': pVal, 'px': pxVal, 'py': pyVal,
                 'pz': pzVal})
            previousNode = currentNode

    # Constructing the horizontal edges in the Regular Lattice
    for j in range(y):
        previousNode = list(Q.nodes)[j]
        for i in range(x - 1):
            currentNode = list(Q.nodes)[j + (i + 1) * y]
            ChannelList.append(
                {'edge': (previousNode.name, currentNode.name), 'e': eVal, 'p': pVal, 'px': pxVal, 'py': pyVal,
                 'pz': pzVal})
            previousNode = currentNode

    Q.add_qchans_from(ChannelList)
    # Q.print_qchans()

    return Q
    
    