"""
This script looks for games with a cycle in the graph of coalition structures and improving
deviations, or with coalition structures that have no path to Nash equilibria.
"""

from pyhedonic import hedonicgame as hg
from pyhedonic.hedonicgame_impl import game_begin, game_next, Weights
import networkx as nx

from collections import deque
import numpy as np


def game_dynamic_info(game: hg.HedonicGame):
    """
    Compute the distance from Nash equilibria for all coalition structures in the game.
    """
    # build the graph of improving deviations
    dist = {}
    rev = {}
    q = deque()

    for cs in game.coalition_structures():
        cs_tuple = tuple(np.ravel(cs.cs))
        dist[cs_tuple] = None
        rev[cs_tuple] = []

    for cs in game.coalition_structures():
        cs_tuple = tuple(np.ravel(cs.cs))
        equilibrium = True
        for ag, co in cs.improving_deviations():
            equilibrium = False
            cs_new = cs.move_to(ag, co)
            cs_new_tuple = tuple(np.ravel(cs_new.cs))
            rev[cs_new_tuple].append(cs_tuple)
        if equilibrium:
            dist[cs_tuple] = 0
            q.append(cs_tuple)

    if len(q) == 0:
        return None
    # compute the distance from Nash equilibria
    while q:
        v = q.popleft()
        for u in rev[v]:
            if dist[u] is None:
                dist[u] = dist[v] + 1
                q.append(u)
    return dist


def game_collection_dynamic(
    agent_count: int,
    is_symmetric: bool = True,
    m_begin: int = 0,
    m_end: int = 1,
    k: int | None = None,
    is_fractional: bool = True,
    weights: Weights | None = None,
    debug: int = 0,
):
    """
    Search games for coalition structures that have no path to Nash equilibria.

    Print the game and the coalition structures that have no path to Nash equilibria.
    """
    git = game_begin(agent_count, is_symmetric, m_begin, m_end, weights, debug)
    while game_next(git):
        game = hg.HedonicGame(git.game, is_fractional=is_fractional, k=k)
        info = game_dynamic_info(game)
        if info is None:
            continue
        first = True
        for cs, d in info.items():
            if d is None:
                if first:
                    print("**** GAME ****")
                    print(game)
                    print("**** NASH STABLE COALITION STRUCTURES ****")
                    for cseq in game.nash_stable_coalition_structures():
                        print(cseq)
                    print("**** COALITION STRUCTURES WITH NO PATH TO NASH EQUILIBRIA ****")
                    first = False
                print(hg.CoalitionStructure(game, np.array(cs)))


def game_collection_dynamic2(
    agent_count: int,
    is_symmetric: bool = True,
    m_begin: int = 0,
    m_end: int = 1,
    k: int | None = None,
    is_fractional: bool = True,
    weights: Weights | None = None,
    best_response_only=False,
    debug: int = 0,
):
    """
    Search games with a path in the graph of coalition structures and (best) improving deviations.
    """
    git = game_begin(agent_count, is_symmetric, m_begin, m_end, weights, debug)
    while game_next(git):
        game = hg.HedonicGame(git.game, is_fractional=is_fractional, k=k)
        g = game.coalition_structures_as_nx(best_response_only=best_response_only)
        equilibria = [n for n, d in g.out_degree() if d == 0]
        try:
            cycle = nx.find_cycle(g)
            print("**** GAME ****")
            print(game)
            print("**** NASH STABLE COALITION STRUCTURES ****")
            for cs in equilibria:
                print(cs)
            print("**** CYCLE ****")
            for u, _ in cycle:
                print(f"{u} -> ", end="")
            print(cycle[0][0])
        except nx.NetworkXNoCycle:
            pass


def game_collection_dynamic3(
    agent_count: int,
    is_symmetric: bool = True,
    m_begin: int = 0,
    m_end: int = 1,
    k: int | None = None,
    is_fractional: bool = True,
    weights: Weights | None = None,
    debug: int = 0,
):
    """
    Search games for coalition structures that have no path to Nash equilibria.

    Print the game and the coalition structures that have no path to Nash equilibria. It works
    like game_collection_dynamic, but it uses the networkx library to compute the distance from
    Nash equilibria for all coalition structures in the game.
    """
    git = game_begin(agent_count, is_symmetric, m_begin, m_end, weights, debug)
    while game_next(git):
        game = hg.HedonicGame(git.game, is_fractional=is_fractional, k=k)
        g = game.coalition_structures_as_nx()
        equilibria = [n for n, d in g.out_degree() if d == 0]
        if len(equilibria) == 0:
            continue
        dist = nx.multi_source_dijkstra_path_length(
            g.reverse(copy=False),
            equilibria,
        )
        first = True
        for cs in g.nodes():
            if cs not in dist.keys():
                if first:
                    print("**** GAME ****")
                    print(game)
                    print("**** NASH STABLE COALITION STRUCTURES ****")
                    for cseq in equilibria:
                        print(cseq)
                    print("**** COALITION STRUCTURES WITH NO PATH TO NASH EQUILIBRIA ****")
                    first = False
                print(cs)


print("### games with a cycle in the graph of coalition structures and (best) improving deviations")
print(game_collection_dynamic2(4, k=3, best_response_only=True, m_end=3, debug=1))

print()

print("### games with coalition structures that have no path to Nash equilibria")
print(game_collection_dynamic3(4, k=3, m_end=9, debug=1))
# or slower, using game_collection_dynamic3
# print(game_collection_dynamic3(4, k=3, m_end=9, debug=1))


# VALUATIONS1 = np.array([[0, 0, 2], [1, 0, 3], [2, 0, 0]])
# GAME1_FRAC = hg.HedonicGame(VALUATIONS1)
# GAME1_NOFRAC = hg.HedonicGame(VALUATIONS1, is_fractional=False)
# GAME1_FRAC_K1 = hg.HedonicGame(VALUATIONS1, k=1)
# GAME1_FRAC_K2 = hg.HedonicGame(VALUATIONS1, k=2)
# GAME1_FRAC_K3 = hg.HedonicGame(VALUATIONS1, k=3)

# print(game_dynamic_info(GAME1_FRAC_K2))
# game_collection_dynamic(7, k=5, m_end=1, debug=1)
