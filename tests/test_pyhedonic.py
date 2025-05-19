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
game1_frac = hg.HedonicGame(valuations1)
game1_nofrac = hg.HedonicGame(valuations1, is_fractional=False)
game1_frac_k1 = hg.HedonicGame(valuations1, k=1)
game1_frac_k2 = hg.HedonicGame(valuations1, k=2)
game1_frac_k3 = hg.HedonicGame(valuations1, k=3)

valuations2 = np.array([
    [0, 9, 9, 4],
    [9, 0, 1, 7],
    [9, 1, 0, 7],
    [4, 7, 7, 0]
])
game2 = hg.Graph(valuations2)

game1_frac_cs1 = hg.CoalitionStructure(game1_frac, np.array([0, 1, 0]))
game1_frac_cs2 = hg.CoalitionStructure(game1_frac, np.array([0, 0, 0]))
game1_nofrac_cs1 = hg.CoalitionStructure(game1_nofrac, np.array([0, 1, 0]))


def compare_coalition_structures(cs_iterator, csdata_iterator):
    l1 = list(cs_iterator)
    l2 = list(csdata_iterator)
    assert (len(l1) == len(l2))
    for cs1, cs2 in zip(list(cs_iterator), list(csdata_iterator)):
        assert np.array_equal(cs1.cs, cs2)


def test_CoalitionStructure_size():
    assert game1_frac_cs1.size == 2
    assert game1_frac_cs2.size == 1


def test_CoalitionStructure_coalition_size():
    assert game1_frac_cs1.coalition_size(0) == 2
    assert game1_frac_cs2.coalition_size(0) == 3


def test_CoalitionStructure_agent_utility():
    assert game1_frac_cs1.agent_utility(0) == 1.0
    assert game1_frac_cs1.agent_utility(1) == 0.0
    assert game1_frac_cs1.agent_utility(2) == 1.0
    assert game1_nofrac_cs1.agent_utility(0) == 2
    assert game1_nofrac_cs1.agent_utility(1) == 0


def test_CoalitionStructure_coalition_social_welfare():
    assert game1_frac_cs1.coalition_social_welfare(0) == 2.0
    assert game1_frac_cs1.coalition_social_welfare(1) == 0.0


def test_CoalitionStructure_social_welfare():
    assert game1_frac_cs1.social_welfare() == 2.0
    assert game1_nofrac_cs1.social_welfare() == 4


def test_CoalitionStructure_is_improving_deviation():
    assert game1_frac_cs1.is_improving_deviation(1, 0)
    assert game1_frac_cs1.is_improving_deviation(1, 0)
    assert not game1_frac_cs1.is_improving_deviation(0, 0)


def test_CoalitionStructure_equality():
    assert game1_frac_cs1 == game1_frac_cs1
    assert game1_frac_cs1 != game1_nofrac_cs1


def test_HedonicGame_coalition_structures_1():
    compare_coalition_structures(game1_frac.coalition_structures(cs_size=1), [[0, 0, 0]])
    compare_coalition_structures(game1_frac_k2.coalition_structures(cs_size=1), [])
    compare_coalition_structures(game1_frac.coalition_structures(cs_size=2), [[0, 0, 1], [0, 1, 0], [0, 1, 1]])
    compare_coalition_structures(game1_frac_k2.coalition_structures(cs_size=2), [[0, 0, 1], [0, 1, 0], [0, 1, 1]])
    compare_coalition_structures(game1_frac_k3.coalition_structures(cs_size=3), [[0, 1, 2]])
    compare_coalition_structures(game1_frac_k2.coalition_structures(cs_size=3), [[0, 1, 2]])


def test_HedonicGame_coalition_structures_2():
    compare_coalition_structures(game1_frac.coalition_structures(), [
                                 [0, 0, 0], [0, 0, 1], [0, 1, 0], [0, 1, 1], [0, 1, 2]])
    compare_coalition_structures(game1_frac_k1.coalition_structures(), [[0, 1, 2]])
    compare_coalition_structures(game1_frac_k2.coalition_structures(), [[0, 0, 1], [0, 1, 0], [0, 1, 1], [0, 1, 2]])
    compare_coalition_structures(game1_frac_k3.coalition_structures(), [
                                 [0, 0, 0], [0, 0, 1], [0, 1, 0], [0, 1, 1], [0, 1, 2]])


def test_HedonicGame_nash_stable_coalition_structures():
    compare_coalition_structures(game1_frac.nash_stable_coalition_structures(), [[0, 0, 0]])
    compare_coalition_structures(game1_frac_k1.nash_stable_coalition_structures(), [[0, 1, 2]])


def test_HedonicGame_has_nash_stable_coalition_structure():
    assert not hg.GAME_K3_NOEQUILIBRIUM_PAPER.has_nash_stable_coalition_structure()
    assert not hg.GAME_K3_NOEQUILIBRIUM.has_nash_stable_coalition_structure()
    assert not hg.GAME_K4_NOEQUILIBRIUM.has_nash_stable_coalition_structure()
    assert not hg.GAME_K5_NOEQUILIBRIUM.has_nash_stable_coalition_structure()
    assert not hg.GAME_K6_NOEQUILIBRIUM.has_nash_stable_coalition_structure()
    assert not hg.GAME_K7_NOEQUILIBRIUM.has_nash_stable_coalition_structure()
    assert not hg.GAME_K7_NOEQUILIBRIUM_SIMPLE.has_nash_stable_coalition_structure()
    assert not hg.GAME_K8_NOEQUILIBRIUM.has_nash_stable_coalition_structure()


def test_HedonicGame_optimal_coalition_structure():
    game = hg.HedonicGame(np.array([
        [0, 1, 0, 1, 0],
        [1, 0, 1, 1, 0],
        [0, 1, 0, 0, 1],
        [1, 1, 0, 0, 1],
        [0, 0, 1, 1, 0]
    ]), k=2)
    _, v = game.optimal_coalition_structure()
    assert v == 2


@pytest.mark.parametrize("k", [2, 3])
def test_HedonicGamee_no_nash_for_asymmetric_games(k: int):
    """
    Test inspired by Proposition 1 in [PAPER].
    """
    graph = nx.DiGraph()
    for i in range(k+1):
        graph.add_edge(i, (i + 1) % (k+1))
    game = hg.HedonicGame(hg.Graph.from_nx_graph(graph), k=k)
    assert not game.has_nash_stable_coalition_structure()


@pytest.mark.parametrize("m", [10, 20])
def test_HedonicGame_unbound_poa_for_non_simple_games(m: int):
    """
    Test inspired by Proposition 2 in [PAPER].
    """
    graph = nx.Graph()
    graph.add_edge(0, 1, weight=1)
    graph.add_edge(1, 2, weight=2*m)
    graph.add_edge(2, 3, weight=1)
    game = hg.HedonicGame(hg.Graph.from_nx_graph(graph), k=2)
    cs, opt = game.optimal_coalition_structure()
    prices = game.prices()
    assert opt == 2*m
    assert prices is not None
    assert prices.poa == m


def test_HedonicGame_prices_for_2SSFHG():
    """
    Test inspired by Proposition 4 in [PAPER].
    """
    graph = nx.Graph()
    graph.add_edges_from([(0, 1), (1, 2), (2, 3)])
    game = hg.HedonicGame(hg.Graph.from_nx_graph(graph), k=2)
    pr = game.prices()
    assert pr is not None
    assert pr.poa == 2.0
    assert pr.pos == 1.0


def test_Graph_to_nx_graph():
    graph = nx.Graph()
    graph.add_weighted_edges_from([
        (0, 1, 9), (0, 2, 9), (0, 3, 4), (1, 2, 1), (1, 3, 7), (2, 3, 7)
    ])
    assert nx.utils.graphs_equal(hg.GAME_K3_NOEQUILIBRIUM_PAPER.graph.to_nx_graph(), graph)


def test_Graph_from_nx_graph():
    graph = nx.Graph()
    graph.add_weighted_edges_from([
        (0, 1, 9), (0, 2, 9), (0, 3, 4), (1, 2, 1), (1, 3, 7), (2, 3, 7)
    ])
    print(hg.Graph.from_nx_graph(graph))
    print(hg.GAME_K3_NOEQUILIBRIUM_PAPER.graph)
    assert hg.Graph.from_nx_graph(graph) == hg.GAME_K3_NOEQUILIBRIUM_PAPER.graph
