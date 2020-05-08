#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Apr 23 12:12:10 2020

@author: hudson
"""

import QNET
from Graph1 import X
from Graph2 import X as X2

# Check graph __str__
print(X2)

# Test Path initialization / path check
array = ['A', 'G1', 'T', 'G2', 'B']
my_path = QNET.Path(X2, array)
print(my_path)
print('\n')

# Check new __repr__ method
for edge in X2.edges():
    print(edge)
    
print(my_path.head())
print(my_path.tail())

path1 = ['A', 'G1', 'T', 'G2', 'B']
path2 = ['A', 'S', 'B']
result = X2.low_purify(path1, path2, return_as = 'loss')
print(result)




