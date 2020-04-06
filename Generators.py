"""
Created on Fri Mar  6 13:02:25 2020

Work in progress, please be nice
-- The management

@author: hudson
"""

import networkx as nx
import QNET
import numpy as np


def linGen(n, spacing = [0, 0, 0], loss = 0):
    assert(n > 2)
    
    G = nx.Graph()
    
    # Add head node
    node = QNET.Qnode('Head', coords = [0,0,0])
    G.add_node(node)
        
    # Add nodes between head and tail:
    i = 1
    while i < n - 1:
        # Make a random node
        newNode = np.random.choice([QNET.Qnode(str(i)), QNET.Ground(str(i)), QNET.Swapper(str(i))],
                             p = [1/3, 1/3, 1/3])
        
        # Update coordinates of newNode:
        newNode.coords = np.add(newNode.coords, np.multiply(i, spacing))
        # Add edge (and implicitly add node)
        G.add_edge(node, newNode, loss = loss)
        node = newNode
        i += 1
            
    # add tail node
    newNode = QNET.Qnode('Tail', coords = np.multiply(n-1, spacing))
    G.add_edge(node, newNode, loss = loss)
    return G

# Todo:
# Write better linear generator


"""
WORK IN PROGRESS
"""
def alternatingLinGen(n, spacing = [0,0,0], loss = 0):
    # locals() brings in all the local attributes intothe function
    
    ### Subfunctions ###
    def add_node(G, curNode, nodeType, **parentArgs):
        
        if curNode.name == 'Head':
            newNode = QNET.nodeType(str(1))
            newNode.coords = np.add(newNode.coords, np.multiply(1, spacing))
        
        else:
            counter = int(curNode.name) + 1
            newNode = QNET.nodeType(str(counter))
            newNode.coords = np.add(newNode.coords, np.multiply(counter, spacing))
            G.add_edge(newNode, curNode, loss = loss)
            
        return newNode
    
    def iterate(G, cur, i, bound, **parentArgs):
        while i < bound:
            if type(cur) == QNET.Swapper or type(cur) == QNET.Qnode:
                cur = add_node(G, cur, QNET.Ground, parentArgs = locals())
                i += 1
            elif type(cur) == QNET.Ground:
                cur = add_node(G, cur, QNET.Swapper, parentArgs = locals())
                i += 1
        return i
    
    assert(n > 2)
    
    # initialise graph
    G = nx.Graph()
    
    # Add head node
    cur = QNET.Qnode('Head', coords = [0,0,0])
    G.add_node(cur)
    
    i = 0
    if n % 2 == 0:
        # add nodes until we reach halfway point
        i = iterate(G, cur, i, n/2, **locals())
        
        # Reaching middle of sequence, repeat whatever previous node was
        if type(cur) == QNET.Swapper:
            cur = add_node(G, cur, QNET.Swapper, **locals())
            i += 1 
        elif type(cur) == QNET.Ground:
            cur = add_node(G, cur, QNET.Ground, **locals())
            i += 1 
        
        # Continue as normal
        i = iterate(G, cur, i, n, **locals())
    
    
    # For an odd numbered pathlen, generate normally
    elif n % 2 == 1:
        
        i = 0
        iterate(G, cur, i, n, parentArgs = locals())
            
    # Add tail node
    node = QNET.Qnode('Tail')
    G.add_node(node)
    
    return G
    
    