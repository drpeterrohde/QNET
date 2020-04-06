#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Mar 25 10:59:46 2020

@author: hudson
"""

import copy
import numpy as np
import QNET

# Definitions:
# p: Probability of successful transmission
# q: Probability of dephasing
# l: Loss, decebelic form of p
# g: Gain, decebelic form of q
# f: Fidelity, equal to 1-q = p for bell states

def P2Q(p):
    return 1 - p

def P2L(p):
    return -1 * np.log(p)

def L2P(l):
    return np.exp(-l)

def weight(u, v, d):
    if type(u) == QNET.Swapper:
        return d['loss'] + QNET.P2L(u.prob)/2
    elif type(v) == QNET.Swapper:
        return d['loss'] + QNET.P2L(v.prob)/2
    else:
        return d['loss']