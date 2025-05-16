"""
This file contains unit tests for the pyhedonic library.

The notation [PAPER] refers to the paper "Nash Stability in Fractional Hedonic Games
with Bounded Size Coalitions".
"""
import networkx as nx
import numpy as np
import pytest

import pyhedonic.HedonicGame as hg

valuations1 = np.array([
    [0, 0, 2],
    [1, 0, 3],
    [2, 0, 0]
])
game1 = hg.HedonicGame(valuations1)

valuations2 = np.array([
    [0, 9, 9, 4],
    [9, 0, 1, 7],
    [9, 1, 0, 7],
    [4, 7, 7, 0]
])
game2 = hg.HedonicGame(valuations2)

cs11 = hg.CoalitionStructure(game1, np.array([1, 0, 1]))
cs12 = hg.CoalitionStructure(game1, np.array([0, 0, 0]))
cs21 = hg.CoalitionStructure(game1, np.array([1, 0, 1]), is_fractional=False)


def compare_coalition_structures(cs_iterator, csdata_iterator):
    l1 = list(cs_iterator)
    l2 = list(csdata_iterator)
    assert (len(l1) == len(l2))
    for cs1, cs2 in zip(list(cs_iterator), list(csdata_iterator)):
        assert (cs1.cs == cs2).all()


def test_size():
    assert cs11.size == 2
    assert cs12.size == 1


def test_coalition_size():
    assert cs11.coalition_size(1) == 2
    assert cs12.coalition_size(0) == 3


def test_agent_utility():
    assert cs11.agent_utility(0) == 1.0
    assert cs11.agent_utility(1) == 0.0
    assert cs11.agent_utility(2) == 1.0
    assert cs21.agent_utility(0) == 2
    assert cs21.agent_utility(1) == 0


def test_coalition_social_welfare():
    assert cs11.coalition_social_welfare(0) == 0.0
    assert cs11.coalition_social_welfare(1) == 2.0


def test_social_welfare():
    assert cs11.social_welfare() == 2.0
    assert cs21.social_welfare() == 4


def test_is_improving_deviation():
    assert cs11.is_improving_deviation(1, 1)
    assert cs11.is_improving_deviation(1, 1)
    assert not cs11.is_improving_deviation(0, 0)


def test_coalition_structures1():
    cs_list = game1.coalition_structures()
    cs_datas = [[0, 0, 0], [0, 0, 1], [0, 1, 0], [0, 1, 1], [0, 1, 2]]
    compare_coalition_structures(cs_list, cs_datas)


def test_coalition_structures2():
    compare_coalition_structures(game1.coalition_structures(k=1), [[0, 1, 2]])
    compare_coalition_structures(game1.coalition_structures(
        k=2), [[0, 0, 1], [0, 1, 0], [0, 1, 1], [0, 1, 2]])
    compare_coalition_structures(game1.coalition_structures(
        k=3), [[0, 0, 0], [0, 0, 1], [0, 1, 0], [0, 1, 1], [0, 1, 2]])


def test_coalition_structures3():
    compare_coalition_structures(
        game1.coalition_structures(cs_size=1), [[0, 0, 0]])
    compare_coalition_structures(game1.coalition_structures(k=2, cs_size=1), [])
    compare_coalition_structures(game1.coalition_structures(
        cs_size=2), [[0, 0, 1], [0, 1, 0], [0, 1, 1], ])
    compare_coalition_structures(game1.coalition_structures(
        cs_size=2, k=2), [[0, 0, 1], [0, 1, 0], [0, 1, 1], ])
    compare_coalition_structures(
        game1.coalition_structures(cs_size=3), [[0, 1, 2]])
    compare_coalition_structures(game1.coalition_structures(
        cs_size=3, k=2), [[0, 1, 2]])


def test_Nash_stability():
    compare_coalition_structures(game1.nash_stable_coalition_structures(), [[0, 0, 0]])
    compare_coalition_structures(game1.nash_stable_coalition_structures(k=1), [[0, 1, 2]])


def test_has_nash_equilibrium():
    assert not hg.GAME_K3_NOEQUILIBRIUM_PAPER.has_nash_stable_coalition_structure(k=3)
    assert not hg.GAME_K3_NOEQUILIBRIUM.has_nash_stable_coalition_structure(k=3)
    assert not hg.GAME_K4_NOEQUILIBRIUM.has_nash_stable_coalition_structure(k=4)
    assert not hg.GAME_K5_NOEQUILIBRIUM.has_nash_stable_coalition_structure(k=5)
    assert not hg.GAME_K6_NOEQUILIBRIUM.has_nash_stable_coalition_structure(k=6)
    assert not hg.GAME_K7_NOEQUILIBRIUM.has_nash_stable_coalition_structure(k=7)


def test_to_nx_graph():
    graph = nx.Graph()
    graph.add_edges_from([
        (0, 1, {'weight': 9}),
        (0, 2, {'weight': 9}),
        (0, 3, {'weight': 4}),
        (1, 2, {'weight': 1}),
        (1, 3, {'weight': 7}),
        (2, 3, {'weight': 7})
    ])
    assert nx.utils.graphs_equal(hg.GAME_K3_NOEQUILIBRIUM_PAPER.to_nx_graph(), graph)


def test_from_nx_graph():
    graph = nx.Graph()
    graph.add_edges_from([
        (0, 1, {'weight': 9}),
        (0, 2, {'weight': 9}),
        (0, 3, {'weight': 4}),
        (1, 2, {'weight': 1}),
        (1, 3, {'weight': 7}),
        (2, 3, {'weight': 7})
    ])
    assert hg.HedonicGame.from_nx_graph(graph) == hg.GAME_K3_NOEQUILIBRIUM_PAPER

def test_optimal_coalition_structure():
    game = hg.HedonicGame(np.array([
        [0, 1, 0, 1, 0],
        [1, 0, 1, 1, 0],
        [0, 1, 0, 0, 1],
        [1, 1, 0, 0, 1],
        [0, 0, 1, 1, 0]
    ]))
    _, v = game.optimal_coalition_structure(k=2)
    assert v == 2

@pytest.mark.parametrize("k", [2, 3])
def test_no_nash_for_asymmetric_games(k: int):
    """
    Test inspired by Proposition 1 in [PAPER].
    """
    g = nx.DiGraph()
    for i in range(k+1):
        g.add_edge(i, (i + 1) % (k+1))
    graph = hg.HedonicGame.from_nx_graph(g)
    assert not graph.has_nash_stable_coalition_structure(k=k)

@pytest.mark.parametrize("m", [10, 20])
def test_unbound_poa_for_non_simple_games(m: int):
    """
    Test inspired by Proposition 2 in [PAPER].
    """
    g = nx.Graph()
    g.add_edge(0, 1, weight=1)
    g.add_edge(1, 2, weight=2*m)
    g.add_edge(2, 3, weight=1)
    graph = hg.HedonicGame.from_nx_graph(g)
    prices = graph.prices(k=2)
    cs, opt = graph.optimal_coalition_structure(k=2)
    assert opt == 2*m
    assert prices is not None
    assert prices.poa == m

def test_prices_for_2SSFHG():
    """
    Test inspired by Proposition 4 in [PAPER].
    """
    g = nx.Graph()
    g.add_edges_from([(0, 1), (1,2), (2,3)])
    game = hg.HedonicGame.from_nx_graph(g)
    pr = game.prices(k=2)
    assert pr is not None
    assert pr.poa == 2.0
    assert pr.pos == 1.0
