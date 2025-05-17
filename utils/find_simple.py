"""
This script tries to find simple games which have no nash stable coalition structure.
It tries all n (numer of agents) from 2 to 20 and all k (maximal coalition size) from 1 to n-1.
"""
from context import pyhedonic

from pyhedonic.HedonicGameImpl import *

for n in range(2, 20):
    for k in range(1, n):
        print("n:", n, "k:",k)
        for g in unstable_game(num_agents=n, k=k, max_valuation=1, debug=1):
            print(g)
            break
