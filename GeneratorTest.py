#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Mar  6 16:59:06 2020

Test file, please ignore
- The management

@author: hudson
"""
import networkx as nx
import QNET
import numpy as np
import matplotlib.pyplot as plt

def linGenTest():
    # Test half half case
    n = 100
    G = QNET.linGen(n, spacing = [5, 0, 0], loss = 10)
    for node in G:
        print(node)
    print('\n')
    QNET.print_qchans(G)
    

def linGen_withSat():
    n = 5
    G = QNET.linGen(n, spacing = [5, 0, 0], loss = 7)
    
    # Add satellites to graph
    S = QNET.Satellite(name = 'S', coords = [0,0,100], velocity = [5, 0])
    G.add_node(S)
    
    # S2 = QNET.Satellite(name = 'S2', coords = [100, 0, 100], velocity = [1,0])
    # G.add_node(S2)
    
    nodeList = G.nodes()
    for node in nodeList:
        if type(node) != QNET.Ground and type(node) != QNET.Satellite:
            G.add_edge(node, S, loss = QNET.airCost(S, node))
            # G.add_edge(node, S2, loss = QNET.airCost(S2, node))
    
    # Debug
    for node in G:
        print(node)
    print('\n')
    
    # Debug
    QNET.print_qchans(G)
    
    # Simulate
    tMax = 20
    dt = 0.05
    
    timeArr = QNET.getTimeArr(tMax, dt)
    lossArrs, stringDict = QNET.getLossArrays(G, 'Head', 'Tail', 'loss', tMax, dt)
    minArr = QNET.getOptimalLossArray(G, 'Head', 'Tail', 'loss', tMax, dt)
    purArr = QNET.getPurifiedArray(G, 'Head', 'Tail', 'loss', tMax, dt)
    # TODO GET PATH COST FROM ENTANGLEMENT PURIFICATION
    
    
    # Plot arrays over time
    i = 0
    while i < len(lossArrs):
        plt.plot(timeArr, lossArrs[i], label = f'{stringDict[i]}')
        i += 1
    
    # plot purified path cost
    plt.plot(timeArr, purArr, linestyle = '-.', label = 'Purified path cost')

    # Plot optimal path cost
    line = plt.plot(timeArr, minArr, linestyle = ':', c = 'k', label = 'Optimal Path Cost')
    plt.setp(line, linewidth = 3)
    
    plt.xlabel('time')
    plt.ylabel('cost')
    plt.title('Path Costs from Head to Tail')
    plt.legend()
    
    plt.show()
    
def ValidGenTest():
    i = 10
    while i < 100:
        print(f"Testing linGen({i})")
        QNET.linGen(i)
        i += 1

def pathStringTest():
    n = 5
    G = QNET.linGen(n)
    QNET.print_qchans(G)
    shortPath = nx.dijkstra_path(G, QNET.getNode(G,'Head'), QNET.getNode(G, 'Tail'), weight = 'loss')
    pathString = QNET.pathString(shortPath)
    print(pathString)

# linGenTest()
# linGen_withSat()
# pathStringTest()
    
def altTest():
    n = 5
    X = QNET.alternatingLinGen(n, spacing = [5,0,0], loss = 1)
    for node in X.nodes():
        print(node)

# This is a cool demo concept: Keep this.
def passTest():
    def parent(x, y, z):
        def child(w, **parentArgs):
            return w + x + y + z
        return child(w = 1, **locals())
    
    print(parent(1,2,3))
    
    
altTest()
# passTest()