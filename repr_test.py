#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Apr 25 17:54:04 2020

@author: hudson
"""

import QNET

Q = QNET.Qnet()
my_node = QNET.Qnode(name = 'A')
Q.add_node(my_node)
double = QNET.Qnode(name = 'A')
print(my_node.__repr__() == double.__repr__())

print(Q)