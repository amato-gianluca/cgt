"""
This script counts the number of games with no stable coalition structures.
You can pass the maximum size of coalitions `k` as a command line argument.
The script will iterate over the number of agents and the maximum valuation,
trying to keep them low enough that the computation is actually feasible.
"""

import sys

from context import pyhedonic
from pyhedonic import HedonicGameImpl as hgimpl

# Maximum size of coalitions
k = int(sys.argv[1])

# Maximum weight for each number of agents
max_weight = [20, 20, 20, 20, 20, 10, 8, 3, 2, 1, 1, 1, 1]

for n in range(k+1, len(max_weight)):
    for m in range(0, max_weight[n] + 1):
        print("num_agents:", n, "k:", k, "maxval: ", m)
        count_noequilibrium, count_total = hgimpl.count_unstable_games(
            num_agents=n, k=k, min_valuation=m, max_valuation=m, debug=2)
        print("num_agents:", n, "k:", k, "maxval: ", m,
              "count:", count_noequilibrium, "/", count_total)
