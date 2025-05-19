"""
This script counts the number of games with no stable coalition structures.
You can pass the maximum size of coalitions `k` as a command line argument.
The script will iterate over the number of agents and the maximum valuation,
trying to keep them low enough that the computation is actually feasible.
"""

from context import pyhedonic

from sys import argv
from pyhedonic.HedonicGameImpl import *

k = int(argv[1])

n_min = int(argv[2]) if len(argv) >= 3 else k+1
n_max = 11

m_min = int(argv[3]) if len(argv) >= 4 else 0
m_max_k0 = [20, 20, 20, 20, 20, 10, 7, 3, 2, 1, 1]
m_max_k4 = [20, 20, 20, 20, 20, 10, 6, 3, 2, 1, 1]
m_max = m_max_k0 if k <= 3 else m_max_k4

for n in range(n_min, n_max+1):
    for m in range(m_min, m_max[n]+1):
        m_min = 0
        print("num_agents:", n, "k:", k, "maxval: ", m)
        count_noequilibrium, count_total = count_unstable_games(
            num_agents=n, k=k, min_valuation=m, max_valuation=m, debug=1)
        print("num_agents:", n, "k:", k, "maxval: ", m, "count:", count_noequilibrium, "/", count_total)
