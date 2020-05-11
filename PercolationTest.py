#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Apr 24 23:44:13 2020

@author: deepeshsingh
"""


import networkx as nx
import QNET
import numpy as np
import matplotlib.pyplot as plt
import RegularLattice as RL
import Percolation as Pc
   

def RegLatCheck(x,y):
    
    # Create a Regular Lattice
    B = RL.RegLat(x,y, xspacing = [50,0,0], yspacing = [0,50,0], loss = 0.15)
    
    # Number of Monte-Carlo Iterations 
    nTurns = 100
    
    # Range over which Monte-Carlo Iterations runs
    DefectProb = range(0,110,10)
    
    pathProbAvg = []
    lossArrAvg = []
    fidArrAvg = []
    
    for prob in DefectProb:
        probThresh = prob/100 
        pathProbSum = 0
        lossSum = 0
        fidSum = 0
        # Monte-carlo Implementation
        for i in range(nTurns):        
            pathProb, lossValue, fidValue  = Pc.defectedGraph(B, probThresh)
            pathProbSum = pathProbSum + pathProb
            lossSum = lossSum + lossValue
            fidSum = fidSum + fidValue
        pathProbAvg.append(pathProbSum/nTurns)
        lossArrAvg.append(lossSum/nTurns)
        fidArrAvg.append(fidSum/nTurns)
    
    print('\n')
    print("pathProbAvg", pathProbAvg)
    print("lossArrAvg", lossArrAvg)
    print("fidArrAvg", fidArrAvg)
    
    plt.plot(np.divide(DefectProb,100), pathProbAvg, label = "Prob of path existing" )
    plt.plot(np.divide(DefectProb,100), lossArrAvg, 'g-o', label = "Loss probability")
    plt.plot(np.divide(DefectProb,100), fidArrAvg, 'r--', label = "Fidelity probability")    
    
    plt.ylabel('Probability of path existing b/w A and B')
    plt.xlabel('Probability of occupation of a single site')
    plt.title(str(x)+"X"+str(y)+" Lattice; averaged "+str(nTurns)+" times")
    plt.legend(loc='best')
    plt.show()

    
RegLatCheck(3,3)  

