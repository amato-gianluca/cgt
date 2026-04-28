"""
This script tries to find simple games which have no Nash stable coalition structure.
It tries all n (number of agents) from 2 to 20 and all k (maximal coalition size) from 1 to n-1.
"""

from pyhedonic.hedonicgame_impl import unstable_games

for n in range(2, 20):
    for k in range(1, n):
        print("n:", n, "k:", k)
        for g in unstable_games(agent_count=n, k=k, m_end=1, debug=1):
            print(g)
            break
