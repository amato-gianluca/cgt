"""
This file contains unit tests for the pyhedonic library. In particular, it tests the
HedonicGame module, which contain pythonic wrapper for the HedonicGameImpl module.

The notation [PAPER] refers to the paper "Nash Stability in Fractional Hedonic Games
with Bounded Size Coalitions".
"""

from collections.abc import Iterator, Iterable
import networkx as nx
import numpy as np
import numpy.typing as npt
import pytest

import pyhedonic.HedonicGame as hg

VALUATIONS1 = np.array([
    [0, 0, 2],
    [1, 0, 3],
    [2, 0, 0]
])
GAME1_FRAC = hg.HedonicGame(VALUATIONS1)
GAME1_NOFRAC = hg.HedonicGame(VALUATIONS1, is_fractional=False)
GAME1_FRAC_K1 = hg.HedonicGame(VALUATIONS1, k=1)
GAME1_FRAC_K2 = hg.HedonicGame(VALUATIONS1, k=2)
GAME1_FRAC_K3 = hg.HedonicGame(VALUATIONS1, k=3)

VALUATIONS2 = np.array([
    [0, 9, 9, 4],
    [9, 0, 1, 7],
    [9, 1, 0, 7],
    [4, 7, 7, 0]
])
GAME2 = hg.Graph(VALUATIONS2)

GAME1_FRAC_CS1 = hg.CoalitionStructure(GAME1_FRAC, np.array([0, 1, 0]))
GAME1_FRAC_CS2 = hg.CoalitionStructure(GAME1_FRAC, np.array([0, 0, 0]))
GAME1_NOFRAC_CS1 = hg.CoalitionStructure(GAME1_NOFRAC, np.array([0, 1, 0]))


def compare_iterable_nparray(value: Iterable[hg.CoalitionStructure], expected: Iterable[list[int]]):
    l1 = list(value)
    l2 = list(expected)
    assert (len(l1) == len(l2))
    for cs1, cs2 in zip(l1, l2):
        assert np.array_equal(cs1.cs, cs2)


def test_CoalitionStructure_size():
    assert GAME1_FRAC_CS1.size == 2
    assert GAME1_FRAC_CS2.size == 1


def test_CoalitionStructure_coalition_size():
    assert GAME1_FRAC_CS1.coalition_size(0) == 2
    assert GAME1_FRAC_CS2.coalition_size(0) == 3


def test_CoalitionStructure_agent_utility():
    assert GAME1_FRAC_CS1.agent_utility(0) == 1.0
    assert GAME1_FRAC_CS1.agent_utility(1) == 0.0
    assert GAME1_FRAC_CS1.agent_utility(2) == 1.0
    assert GAME1_NOFRAC_CS1.agent_utility(0) == 2
    assert GAME1_NOFRAC_CS1.agent_utility(1) == 0


def test_CoalitionStructure_coalition_social_welfare():
    assert GAME1_FRAC_CS1.coalition_social_welfare(0) == 2.0
    assert GAME1_FRAC_CS1.coalition_social_welfare(1) == 0.0


def test_CoalitionStructure_social_welfare():
    assert GAME1_FRAC_CS1.social_welfare() == 2.0
    assert GAME1_NOFRAC_CS1.social_welfare() == 4


def test_CoalitionStructure_is_improving_deviation():
    assert GAME1_FRAC_CS1.is_improving_deviation(1, 0)
    assert GAME1_FRAC_CS1.is_improving_deviation(1, 0)
    assert not GAME1_FRAC_CS1.is_improving_deviation(0, 0)


def test_CoalitionStructure_equality():
    assert GAME1_FRAC_CS1 == GAME1_FRAC_CS1
    assert GAME1_FRAC_CS1 != GAME1_NOFRAC_CS1


def test_HedonicGame_coalition_structures_1():
    compare_iterable_nparray(GAME1_FRAC.coalition_structures(cs_size=1), [[0, 0, 0]])
    compare_iterable_nparray(GAME1_FRAC_K2.coalition_structures(cs_size=1), [])
    compare_iterable_nparray(GAME1_FRAC.coalition_structures(cs_size=2), [[0, 0, 1], [0, 1, 0], [0, 1, 1]])
    compare_iterable_nparray(GAME1_FRAC_K2.coalition_structures(cs_size=2), [[0, 0, 1], [0, 1, 0], [0, 1, 1]])
    compare_iterable_nparray(GAME1_FRAC_K3.coalition_structures(cs_size=3), [[0, 1, 2]])
    compare_iterable_nparray(GAME1_FRAC_K2.coalition_structures(cs_size=3), [[0, 1, 2]])


def test_HedonicGame_coalition_structures_2():
    compare_iterable_nparray(GAME1_FRAC.coalition_structures(),
                             [[0, 0, 0], [0, 0, 1], [0, 1, 0], [0, 1, 1], [0, 1, 2]])
    compare_iterable_nparray(GAME1_FRAC_K1.coalition_structures(), [[0, 1, 2]])
    compare_iterable_nparray(GAME1_FRAC_K2.coalition_structures(), [[0, 0, 1], [0, 1, 0], [0, 1, 1], [0, 1, 2]])
    compare_iterable_nparray(GAME1_FRAC_K3.coalition_structures(),
                             [[0, 0, 0], [0, 0, 1], [0, 1, 0], [0, 1, 1], [0, 1, 2]])


def test_HedonicGame_nash_stable_coalition_structures():
    compare_iterable_nparray(GAME1_FRAC.nash_stable_coalition_structures(), [[0, 0, 0]])
    compare_iterable_nparray(GAME1_FRAC_K1.nash_stable_coalition_structures(), [[0, 1, 2]])


def test_HedonicGame_has_nash_stable_coalition_structure():
    assert not hg.GAME_K3_NOEQUILIBRIUM_PAPER.has_nash_stable_coalition_structure()
    assert not hg.GAME_K3_NOEQUILIBRIUM.has_nash_stable_coalition_structure()
    assert not hg.GAME_K4_NOEQUILIBRIUM.has_nash_stable_coalition_structure()
    assert not hg.GAME_K5_NOEQUILIBRIUM.has_nash_stable_coalition_structure()
    assert not hg.GAME_K6_NOEQUILIBRIUM.has_nash_stable_coalition_structure()
    assert not hg.GAME_K7_NOEQUILIBRIUM.has_nash_stable_coalition_structure()
    assert not hg.GAME_K7_NOEQUILIBRIUM_SIMPLE.has_nash_stable_coalition_structure()
    assert not hg.GAME_K8_NOEQUILIBRIUM.has_nash_stable_coalition_structure()


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


def test_HedonicGame_optimal_coalition_structure1():
    game = hg.HedonicGame(np.array([
        [0, 1, 0, 1, 0],
        [1, 0, 1, 1, 0],
        [0, 1, 0, 0, 1],
        [1, 1, 0, 0, 1],
        [0, 0, 1, 1, 0]]), k=2)
    _, v = game.optimal_coalition_structure()
    assert v == 2.0


def test_HedonicGame_optimal_coalition_structure2():
    game = hg.HedonicGame(np.array(
        [[0, 0, 0, 0, 1, 1],
         [0, 0, 0, 1, 0, 1],
         [0, 0, 0, 1, 1, 0],
         [0, 1, 1, 0, 0, 0],
         [1, 0, 1, 0, 0, 0],
         [1, 1, 0, 0, 0, 0]]), k=2, is_fractional=True)
    _, opt = game.optimal_coalition_structure()
    assert opt == 3.0


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


def test_CoalitionStructure_move_to():
    csa = GAME1_FRAC_CS1.move_to(2, 2)
    assert csa == hg.CoalitionStructure(GAME1_FRAC, np.array([0, 1, 2]))
    csa = csa.move_to(0, 2)
    assert csa == hg.CoalitionStructure(GAME1_FRAC, np.array([0, 1, 0]))
    csa = csa.move_to(2, 1)
    assert csa == hg.CoalitionStructure(GAME1_FRAC, np.array([0, 1, 1]))
