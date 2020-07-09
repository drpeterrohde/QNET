#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Feb 28 17:25:13 2020
@author: Hudson Leone
"""

import networkx as nx
import QNET
import copy
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import art3d


def getTimeArr(tMax, dt):
    """
    Make uniform array from 0 to tMax with interval dt
    Parameters
    ----------
    tMax : float
        Maximum time
    dt : float
        Time increment
    Returns
    -------
    Array
    """
    return np.arange(0, tMax, dt)


def sim_all_simple(G, source, target, tMax, dt, cost_type = None):
    # Get cost arrays for all simple paths over time

    C = copy.deepcopy(G)

    # get source and target from names
    source = C.getNode(source)
    target = C.getNode(target)

    # Create a generator of all simple paths
    simplePathGen = nx.algorithms.simple_paths.all_simple_paths(C, source, target)

    # Unpack paths from generator into array as QNET paths
    path_arr = []
    for path in simplePathGen:
        path_arr.append(QNET.Path(C, path))

    # Assign each path to an empty cost array
    path_dict = {path: [] for path in path_arr}

    # Initialize array size
    size_arr = len(np.arange(0, tMax, dt))
    i = 0
    while i < size_arr:
        j = 0
        while j < len(path_arr):
            # Get the cost of each path and append it to respective array
            if cost_type is None:
                # Fetch all costs in cost vector
                cost = path_arr[j].cost_vector()
            else:
                # Fetch specified cost
                cost = path_arr[j].cost(cost_type)
            path_dict[path_arr[j]].append(cost)
            j += 1

        C.update(dt)
        i += 1

    for path in path_arr:
        for node in path.node_array:
            if isinstance(node, QNET.Satellite):
                if node.cartesian is False:
                    node.setTime()

    return path_dict


def sim_protocol(G, source, target, protocol, tMax, dt,):
    C = copy.deepcopy(G)
    u = C.getNode(source)
    v = C.getNode(target)

    # Initialize cost array
    cost_arr = []
    # Initialize size of array
    size_arr = len(np.arange(0, tMax, dt))
    i = 0
    while i < size_arr:
        # Run protocol to get either scalar cost or cost bector
        cost = protocol(C, u, v)
        cost_arr.append(cost)
        # Update graph
        C.update(dt)
        i += 1
    return cost_arr

def plot_cv(x, cva, label):
    for cost in cva[0].keys():
        a = []
        for d in cva:
            a.append(d[cost])
        plt.plot(x, a, label=f"{label} ({cost})")


def sim_optimal_cost(G, source_name, target_name, cost_type, tMax, dt):
    """
    Calculate the costs of the lowest cost path from "source" to "target" over time.
    :param G: Qnet Graph
    :param string source_name: Name of source node
    :param string target_name: Name of target node
    :param string cost_type: The type of cost to optimise over. Choose from {'loss', 'fid'}
    :param float tMax: Time period
    :param float dt: Time increment
    :return: Optimal loss array
    """
    C = copy.deepcopy(G)

    u = C.getNode(source_name)
    v = C.getNode(target_name)

    assert cost_type in ['e', 'p'], "Please choose a supported cost type from {'e', 'p'}"

    # Initialize arrays
    cost_arr = []
    size = len(np.arange(0, tMax, dt))

    # Get optimal path cost and append it to costArr
    i = 0
    while i < size:
        cost = QNET.best_path_cost(C, source_name, target_name, cost_type)
        cost_arr.append(cost)
        # Update network
        C.update(dt)
        i += 1

    """ 
    simplePathGen = nx.algorithms.simple_paths.all_simple_paths(C, u, v) 
    pathArr = []
    for path in simplePathGen:
        pathArr.append(QNET.Path(C, path))
    for path in pathArr:
        for node in path.node_array:
            if isinstance(node, QNET.Satellite):
                if node.cartesian is False:
                    node.setTime()
    """

    return cost_arr

def posPlot(Q, u, v, tMax, dt):
    """
    Plot the distance between two nodes over time
    :param Q: QNet Graph
    :param u: Name of Qnode
    :param v: Name of Qnode
    :param tMax: Maximum time
    :param dt: Size of timestep
    :return: None
    """
    C = copy.deepcopy(Q)

    u = C.getNode(u)
    v = C.getNode(v)

    posArr = []
    sizeArr = len(np.arange(0,tMax,dt))

    i = 0
    while i < sizeArr:
        if isinstance(u, QNET.Satellite):
            dist = u.distance(v)
        elif isinstance(v, QNET.Satellite):
            dist = v.distance(u)
        else:
            assert(False)
        posArr.append(dist)
        C.update(dt)
        i += 1
    if isinstance(u, QNET.Satellite):
        u.setTime()
    if isinstance(v, QNET.Satellite):
        v.setTime()
    
    timeArr = QNET.getTimeArr(tMax, dt)
    plt.plot(timeArr, posArr)
    plt.xlabel("Time (in s)")
    plt.ylabel("Distance (in 10^3 km)")
    plt.title(f"Distance between {u.name} and {v.name}")
    plt.show()    
    

def plot_2d(Q, node_label = None, edge_label=None, title=None, FOV=('x', 'y')):
    """
    Plots a 2d view of a Qnet graph in spatial coordinates of nodes
    Edge costs listed are rounded to four significant figures

    :param Q: Qnet Graph
    :param string label: Optional. Cost of edge to be labeled
    :param strings FOV: Optional. Field of view orientation
    :return:
    """
    # Dictionary of node positions
    pos_dict = {}
    # Dictionary of node labels
    node_labels = {}
    # Dictionary of node positions but offset for labeling
    offset = {}
    # Offset for node labeling in y direction
    y_off = 5
    # Dictionary of labels for edges
    edge_labels = {}
    # Array of colours for nodes
    node_colours = []
    # Dictionary between colours and node types
    colour_dict = {QNET.Qnode: 'r', QNET.Ground: 'y', QNET.Swapper: 'c', QNET.Satellite: 'b'}

    for axes in FOV:
        assert axes in ('x', 'y', 'z'), "Field of view usage: Two from (\'x\', \'y\', \'z\')."
    axis_to_index = {'x':0, 'y':1, 'z':2}
    u = axis_to_index[FOV[0]]
    v = axis_to_index[FOV[1]]

    for node in Q.nodes():
        pos_dict[node] = [node.coords[u], node.coords[v]]
        node_colours.append(colour_dict[type(node)])

        if node_label is not None:
            cost = round(node.costs[node_label], 4)
            node_labels[node] = str(node_label) + ' = ' + str(cost)

            offset[node] = [node.coords[u], node.coords[v] + y_off]

        if edge_label is not None:
            for nbr in Q.neighbors(node):
                # If there's no key for the reverse direction case, add edge label (Only one direction needed)
                if not (nbr, node) in edge_labels:
                    cost = round(Q.edges[node, nbr][edge_label], 4)
                    edge_labels[(node, nbr)] = str(edge_label) + ' = ' + str(cost)

    nx.draw_networkx(Q, pos=pos_dict, node_color=node_colours)
    nx.draw_networkx_labels(Q, pos=offset, labels=node_labels)
    nx.draw_networkx_edge_labels(Q, pos_dict, edge_labels=edge_labels)

    if title is not None:
        plt.title(title)

    plt.show()


def plot_3d(Q):
    """
    Draws a 3d plot of a Qnet graph
    Parameters
    :param Q: Qnet Graph
    :return:
    """
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    # Note widget requires external packkage jupyter matplotlib
    # %matplotlib widget

    for node in Q.nodes:
        x = node.coords[0]
        y = node.coords[1]
        z = node.coords[2]

        # Dictionary between colours and node types
        qnode_color = {QNET.Qnode: 'r', QNET.Ground: 'y', QNET.Swapper: 'c', QNET.Satellite: 'b'}
        ax.scatter(x, y, z, c=qnode_color[type(node)], marker='o')
        ax.text(x, y, z, '%s' % node.name, size=12, zorder=1)

    for edge in Q.edges:
        xs = [edge[0].coords[0], edge[1].coords[0]]
        ys = [edge[0].coords[1], edge[1].coords[1]]
        zs = [edge[0].coords[2], edge[1].coords[2]]
        if isinstance(edge[0], QNET.Satellite) or isinstance(edge[1], QNET.Satellite):
            line = art3d.Line3D(xs, ys, zs, linestyle='--')
        else:
            line = art3d.Line3D(xs, ys, zs)
        ax.add_line(line)
    plt.show(fig)
    
def satTrajectory(Q, u, tMax, dt):
    '''
    Generate an array of positions occupied by the satellite. 

    Parameters
    ----------
    Q : QNET Graph
        Graph to be plotted.
    u : QNET Satellite
        Name of satellite to be tracked.
    tMax : int
        Total duration of time for which the satellite should be tracked.
    dt : int
        Time step to track satellite position.

    Returns
    -------
    posArr : 2D Array 
        Each array element contains latitude, longitude of satellite at a given time.

    '''
    C = copy.deepcopy(Q)
    u = C.getNode(u)
    
    posArr = []
    sizeArr = len(np.arange(0,tMax,dt))

    i = 0
    while i < sizeArr:
        if isinstance(u, QNET.Satellite):
            pos = [u.coords[0], u.coords[1]]
        else:
            assert(False)
        posArr.append(pos)
        C.update(dt)
        i += 1
    if isinstance(u, QNET.Satellite):
        u.setTime()
    return posArr


def plot_paths(Q, tMax, dt):
    # Get Time Array
    time_arr = QNET.getTimeArr(tMax, dt)

    # Plot the losses of every simple path over time
    path_dict = sim_all_simple(Q, 'A', 'B', tMax, dt)
    for path in path_dict:
        for cost in Q.cost_vector.keys():
            a = []
            for d in path_dict[path]:
                a.append(d[cost])
            plt.plot(time_arr, a, label = f"{str(path)} ({cost})")

    # Purified costs over time:
    pur_arr = sim_protocol(Q, "A", "B", QNET.simple_purify, tMax, dt)
    plot_cv(time_arr, pur_arr, label = "Path Purification")

    plt.xlabel('Time')
    plt.ylabel("Path Costs")
    plt.title("Network Path Costs Over Time Between Nodes \"A\" and \"B\"")

    plt.legend()
    plt.show()


def plotSatTrajectory(Q, u, tMax, dt):
    '''
    Plots trajectory of a given satellite. 

    Parameters
    ----------
    Q : QNET Graph
        Graph to be plotted.
    u : QNET Satellite
        Name of satellite to be tracked.
    tMax : int
        Total duration of time for which the satellite should be tracked.
    dt : int
        Time step to track satellite position.

    Returns
    -------
    None.

    '''
    satPosition = satTrajectory(Q, u, tMax, dt)
    
    # define color maps for water and land
    ocean_map = (plt.get_cmap('ocean'))(210)
    cmap = plt.get_cmap('gist_earth')
    
    fig = plt.figure(num=None, figsize=(12, 8) )
    ax=fig.add_axes([0.1,0.1,0.8,0.8])
    m = Basemap(projection='merc',llcrnrlat=-80,urcrnrlat=80,llcrnrlon=-180,urcrnrlon=180,resolution='c')
    
    # draw parallels and meridians.
    m.drawparallels(np.arange(-90.,91.,30.),labels=[True,True,False,False],dashes=[2,2])
    m.drawmeridians(np.arange(-180.,181.,60.),labels=[False,False,False,True],dashes=[2,2])
    m.drawcoastlines()
    m.drawmapboundary(fill_color=ocean_map)
    m.fillcontinents(color=cmap(200),lake_color=ocean_map)
    m.drawcountries()
    for i in range(1, len(satPosition)-1):
        redColor = i/(len(satPosition)-1)
        oldloclat = satPosition[i][0]
        oldloclon = satPosition[i][1]
        newloclat = satPosition[i+1][0]
        newloclon = satPosition[i+1][1]
        m.drawgreatcircle(oldloclon,oldloclat,newloclon,newloclat,linewidth=2,color=(redColor,0,0))
           
    
    plt.title("Mercator Projection")
    plt.show()

def plotMap(Q, tMax, dt):
    '''
    Plot QNET on a map. 
    
    For static nodes: Treat x-coord as latitude, y-coord as longitude. z-coord is ignored.
    For sateelites: Color of the trajectory progresses from 'black' to 'red' to show the direction of time. 
    
    Parameters
    ----------
    Q : QNET Graph
        Graph to be plotted.
    tMax : int
        Total duration of time for which the satellite should be tracked.
    dt : int
        Time step to track satellite position.

    Returns
    -------
    None.

    '''
    staticNodes = []
    satPosition = []
    
    for node in list(Q.nodes):
        if isinstance(node, QNET.Satellite):
            satPosition.append(satTrajectory(Q, node.name, tMax, dt))
        else:
            staticNodes.append([node.coords[0], node.coords[1], node.name])
            
    
    # define color maps for water and land
    ocean_map = (plt.get_cmap('ocean'))(210)
    cmap = plt.get_cmap('gist_earth')
    
    fig = plt.figure(num=None, figsize=(12, 8) )
    title_font = {'fontname':'Arial', 'size':'20', 'color':'black', 'weight':'bold',
              'verticalalignment':'bottom'}
    m = Basemap(projection='merc',llcrnrlat=-80,urcrnrlat=80,llcrnrlon=-180,urcrnrlon=180,resolution='c')
    
    # Draw sketch map of earth.
    m.drawparallels(np.arange(-90.,91.,30.),labels=[True,True,False,False],dashes=[2,2])
    m.drawmeridians(np.arange(-180.,181.,60.),labels=[False,False,False,True],dashes=[2,2])
    m.drawcoastlines()
    m.drawmapboundary(fill_color=ocean_map)
    m.fillcontinents(color=cmap(200),lake_color=ocean_map)
    m.drawcountries()
    '''
    # Draw real map of earth. Slow. 
    m.bluemarble()
    '''
    plt.title("Mercator Projection")
    for i in range(len(staticNodes)):
        x, y = m(staticNodes[i][1],staticNodes[i][0])
        nodePos = plt.plot(x,y,'wo')
        plt.setp(nodePos,'markersize',10.,'markeredgecolor','g');
        plt.annotate(staticNodes[i][2]+"("+str(staticNodes[i][0])+","+str(staticNodes[i][1])+")", (x, y), **title_font)
    for j in range(len(satPosition)):
        for i in range(len(satPosition[j])-1):
            redColor = i/(len(satPosition[j])-1)
            oldloclat = satPosition[j][i][0]
            oldloclon = satPosition[j][i][1]
            newloclat = satPosition[j][i+1][0]
            newloclon = satPosition[j][i+1][1]
            m.drawgreatcircle(oldloclon,oldloclat,newloclon,newloclat,linewidth=2,color=(redColor,0,0))
           
    plt.show()
        
    
