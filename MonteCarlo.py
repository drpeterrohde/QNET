#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May 19 18:59:10 2020

@author: deepeshsingh
"""
import networkx as nx
import QNET
import numpy as np
import Percolation as Pc
import copy

def iterations(Q, nTurns = 100, nSteps = 11, toCompute = "pathProbability"):
    '''
    Monte-Carlo iterations on a graph. 
    
    Calculates the probability of the existence of a path, efficiency of the shortest path, and fidelity of 
    the shortest path in a given graph for different percolation thresholds. 
    
    Parameters
    ----------
    Q : QNET Graph
        Input graph.
    nTurns : int
        Number of Monte-Carlo iterations. The default is 100.
    nSteps : int
        Number of data points to be plotted. The default is 11.
    toCompute : String
        Describes the type of data point for which the computation is performed: ["pathProbability","efficiency", "fidelity"]. 
        The default is "pathProbability".

    Returns
    -------
    avg : Array of float
        Average value of toCompute i.e. "pathProbability", "efficiency", or "fidelity".
    var : Array of float
        Variance value of toCompute i.e. "pathProbability","efficiency", or "fidelity".

    '''
    
        
    B = copy.deepcopy(Q)
    
    DefectProb = np.linspace(0,1,nSteps)
    
    avg = []
    var = []
       
    for probThresh in DefectProb:
        
        totalSum = 0
        sumOfSquare = 0
        
        if toCompute == "pathProbability":
            # Monte-carlo Implementation to calculate probability of path existing
            for i in range(nTurns): 
                pathProb = 0
                G  = Pc.defectedGraph(B, probThresh)
                
                if nx.has_path(G, list(G.nodes)[0], list(G.nodes)[-1]):
                    pathProb = pathProb + 1 
                
                totalSum = totalSum + pathProb            
                sumOfSquare = sumOfSquare + pathProb**2        
            avg.append(totalSum/nTurns)      
            var.append(np.sqrt((sumOfSquare/nTurns) - np.power((totalSum/nTurns), 2)))
        
        elif toCompute == "efficiency":
            # Monte-carlo Implementation to calculate efficiency  
            for i in range(nTurns): 
                lossValue = 1
                G  = Pc.defectedGraph(B, probThresh)
                
                try:
                    # Returns the efficiency of the shortest path in the percolated graph
                    # HUDSON'S TEST:
                    lossValue = QNET.shortest_path_length(G, list(G.nodes)[0], list(G.nodes)[-1], 'e')
                    # lossValue = nx.shortest_path_length(G, list(G.nodes)[0], list(G.nodes)[-1], weight='e', method='dijkstra')
                except:
                    pass
                
                totalSum = totalSum + lossValue            
                sumOfSquare = sumOfSquare + lossValue**2        
            avg.append(totalSum/nTurns)      
            var.append(np.sqrt((sumOfSquare/nTurns) - np.power((totalSum/nTurns), 2)))
        
        elif toCompute == "fidelity":
            # Monte-carlo Implementation to calculate fidelity
            for i in range(nTurns):  
                fidValue = 1
                G  = Pc.defectedGraph(B, probThresh)
                
                try:
                    # Returns the fidelity of the shortest path in the percolated graph
                    # fidValue = nx.shortest_path_length(G, list(G.nodes)[0], list(G.nodes)[-1], weight='pz', method='dijkstra')
                    fidValue = QNET.shortest_path_length(G, list(G.nodes)[0], list(G.nodes)[-1], costType = 'p')
                except:
                    pass
                
                #totalSum = totalSum + (1 + (-1 + 2*pz)**fidValue)/2.0                    
                totalSum = totalSum + fidValue            
                sumOfSquare = sumOfSquare + fidValue**2        
            avg.append(totalSum/nTurns)      
            var.append(np.sqrt((sumOfSquare/nTurns) - np.power((totalSum/nTurns), 2)))
            
        else:
            print("Enter valid data type to be computed: pathProbability, efficiency, or fidelity")
            
            
    return avg, var
        
        
    
