# This script finds a cycle in the dynamic of a specific 6-SSFH game presented in the paper. It also
# checks if there is coalition structures from which it is impossible to reach an equilibrium.
# Note that this last check is extremely time consumign (several days are required) and produce
# no results: from every coalition structure it is possible to reach an equilibrium.

from pyhedonic import hedonicgame as hg
import numpy as np
import networkx as nx

edges = [
    (1, 2),
    (4, 5),
    (7, 8),
    (3, 1),
    (3, 2),
    (3, 4),
    (3, 5),
    (3, 7),
    (3, 8),
    (6, 1),
    (6, 2),
    (6, 4),
    (6, 5),
    (6, 7),
    (6, 8),
    (9, 3),
    (9, 6),
    (10, 11),
] + [(10, i) for i in range(1, 9)]

weights = np.array([[0] * 11] * 11)
for a, b in edges:
    weights[a - 1][b - 1] = 1
    weights[b - 1][a - 1] = 1

g = hg.HedonicGame(weights, k=6)

print("** Generating coalition structures **")
css, equilibria = g.coalition_structures_as_nx(best_response_only=True)
for equilibrium in equilibria:
    print(equilibrium)
print("** Equilibria **")
cycle = nx.find_cycle(css)
print("** Cycle **")
for u, _ in cycle:
    print(f"{u} -> ", end="")
print(cycle[0][0])
print("** Unreachable CSs **")
dist = nx.multi_source_dijkstra_path_length(
    css.reverse(copy=False),
    equilibria,
)
first = True
for cs in css.nodes():
    if cs not in dist.keys():
        print(cs)
