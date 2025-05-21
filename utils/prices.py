"""
This script compute prices for games.
"""

from context import pyhedonic

from sys import argv
import pyhedonic.HedonicGame as hg
import pyhedonic.HedonicGameImpl as hgimpl

k = 2
n = 6

poamin = float("inf")
poamax = float("-inf")
posmin = float("inf")
posmax = float("-inf")


cs_count = 0
poasum = 0.0
possum = 0.0
pomsum = 0.0

for g in hg.Graph.enumerate(n, is_directed=False, m_min=1, m_max=1):
    game = hg.HedonicGame(g, k=2)
    gr = game.prices()

    if gr is not None:
        if gr.pos < 1.0:
            print(game)
            raise ValueError("pos < 1.0")
        poamin = min(poamin, gr.poa)
        poamax = max(poamax, gr.poa)
        posmin = min(posmin, gr.pos)
        posmax = max(posmax, gr.pos)
        pomsum += gr.pom * gr.cs_count
        possum += gr.pos * gr.cs_count
        poasum += gr.poa * gr.cs_count
        cs_count += gr.cs_count

print("poamin: ", poamin)
print("poamax: ", poamax)
print("posmin: ", posmin)
print("posmax: ", posmax)
print()
print("pom avg: ", pomsum / cs_count)
print("poa avg: ", poasum / cs_count)
print("pos avg: ", possum / cs_count)