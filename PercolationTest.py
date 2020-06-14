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
import MonteCarlo as MC
   

def PercolationPlots(x,y, e, pz, nTurns = 100, nSteps = 10):
    """
    Plots probability of path existing, efficiency and fidelity of the shortest path in a graph.

    Constructs a regular lattice and then makes defects in it for different probability thresholds.
    Calculates the probability of path exisiting, efficiency and fidelity of the shortest path in
    these defected graphs using Monte-Carlo iteration.

    Parameters
    ----------
    x : int
        Number of columns in the regular lattice.
    y : int
        Number of rows in the regular lattice.
    e : float
        Efficiency of a single channel in the regular lattice.
    pz : float
        Probability of state not undergoing dephasing in the regular lattice.
    nTurns: int
        Number of iterations for each data point in the Monte Carlo loop
    nSteps: int
        Number of percolation densities considered

    Returns
    -------
    None.

    """
    ## Create a Regular Lattice ##
    B = RL.RegLat(x,y, xspacing = [50,0,0], yspacing = [0,50,0], eVal = e, pzVal = pz)
    
    ## Monte-Carlo Iterations logistics ##
    DefectProb = np.linspace(0,1,nSteps) # Range over which Monte-Carlo Iterations runs
    
    ## Call Monte-Carlo iterator ##
    pathProbAvg, pathProbVar = MC.iterations(B, nTurns, nSteps, "pathProbability")
    effAvg, effVar = MC.iterations(B, nTurns, nSteps, "efficiency")
    fidAvg, fidVar = MC.iterations(B, nTurns, nSteps, "fidelity")
    purAvg, purVar = MC.iterations(B, nTurns, nSteps, "purFidelity")

    # Plotting Data
    # plt.errorbar(DefectProb, pathProbAvg, label = "Prob of path existing")
    plt.errorbar(DefectProb, pathProbAvg, yerr = pathProbVar, label = "Probability of path existing")

    # plt.errorbar(DefectProb, effAvg, fmt = 'g-o', label = "Net Efficiency (\u03B7 = "+str(e)+ ")")
    plt.errorbar(DefectProb, effAvg, yerr = effVar, fmt = 'g-o', label = "Net Efficiency (\u03B7 = "+str(e)+ ")")

    # plt.errorbar(DefectProb, fidAvg, fmt = 'r--', label = "Net Fidelity (Pz = "+str(pz)+ ")")
    plt.errorbar(DefectProb, fidAvg, yerr = fidVar, fmt = 'r--', label = "Net Fidelity (Pz = "+str(pz)+ ")")

    # plt.errorbar(DefectProb, purAvg, fmt='c--', label="Purified Fidelity")
    plt.errorbar(DefectProb, purAvg, yerr = purVar, fmt = 'c--', label = "Purified Fidelity")
    
    #plt.ylabel('Probability of path existing b/w A and B')
    plt.xlabel('Probability For A Given Node To Be Present')
    plt.title(str(x)+" x "+str(y)+" Lattice; averaged "+str(nTurns)+" times")
    plt.legend(loc='best')
    plt.show()
    
PercolationPlots(3, 3, e = 1, pz = 0.1, nTurns = 100, nSteps = 20)
# B = RL.RegLat(x=3,y=3, xspacing = [50,0,0], yspacing = [0,50,0], eVal = 1, pzVal = 0.2)
# purAvg, purVar = MC.iterations(B, nTurns=5, nSteps=3, toCompute="purFidelity")
