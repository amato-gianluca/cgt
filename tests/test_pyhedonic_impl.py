
"""
This file contains unit tests for the pyhedonic library. In particular, it tests the
HedonicGameImpl module, which implements the core functionality of the library using Numba
"""

from pyhedonic.HedonicGameImpl import *

import numpy as np


def test1():
    game = np.array([
        [0, 0, 2],
        [1, 0, 3],
        [2, 0, 0]
    ])
    cs1 = np.array([1, 0, 1])
    cs1_sizes = np.array([1, 2, 0])
    cs2 = np.array([0, 0, 0])
    cs2_sizes = np.array([3, 0, 0])
    assert is_improving_deviation(game, True, cs1, cs1_sizes, Deviation(1, 1))
    assert not is_improving_deviation(game, True, cs1, cs1_sizes, Deviation(0, 0))
    assert next_improving_deviation(game, True, cs1, cs1_sizes, len(cs1_sizes), None) == (1, 1)
    assert improving_deviations(game, True, cs1, cs1_sizes, len(cs1_sizes), None) == [(1, 1)]
    assert next_improving_deviation(game, True, cs1, cs1_sizes, len(cs1_sizes), None) is not None
    assert next_improving_deviation(game, True, cs1, cs1_sizes, len(cs1_sizes), 2) is None
    assert next_improving_deviation(game, True, cs2, cs2_sizes, len(cs2_sizes), None) is None
    assert np.all(nash_equilibrium(game) == np.array([0, 0, 0]))
    assert np.all(nash_equilibrium(game, k=1) == np.array([0, 1, 2]))


def test2():
    game = np.array([
        [0, 9, 9, 4],
        [9, 0, 1, 7],
        [9, 1, 0, 7],
        [4, 7, 7, 0]
    ])
    assert nash_equilibrium(game, k=3) is None


def test3():
    game = np.array([
        [0, 1, 1],
        [1, 0, 1],
        [1, 1, 0]
    ])
    cs = np.array([0, 1, 2])
    cs_sizes = np.array([1, 1, 1])
    assert improving_deviations(game, True, cs, cs_sizes, 3, None) == [
        (0, 1), (0, 2), (1, 0), (1, 2), (2, 0), (2, 1)]


def test4():
    game = np.array([
        [0, 1, 1],
        [1, 0, 1],
        [1, 1, 0]
    ])
    assert all(np.array_equal(a1, a2)
               for a1, a2 in zip(css_givensize(game, 1), [np.array([0, 0, 0])]))
    assert all(np.array_equal(a1, a2) for a1, a2 in zip(css_givensize(game, 2), [
               np.array([0, 0, 1]), np.array([0, 1, 0]), np.array([0, 1, 1])]))
    assert all(np.array_equal(a1, a2) for a1, a2 in zip(css_givensize(game, 2, k=2), [
               np.array([0, 0, 1]), np.array([0, 1, 0]), np.array([0, 1, 1])]))
    assert all(np.array_equal(a1, a2)
               for a1, a2 in zip(css_givensize(game, 2, k=1), []))
    assert all(np.array_equal(a1, a2)
               for a1, a2 in zip(css(game, k=1), [np.array([0, 1, 2])]))


def test5():
    res1 = [
        [[0, 0], [0, 0]],
        [[0, 1], [1, 0]],
        [[0, 2], [2, 0]],
    ]
    resnp = [np.array(g) for g in res1]
    assert all(np.array_equal(a1, a2)
               for a1, a2 in zip(games(2, m_end=2), resnp))
    assert all(np.array_equal(a1, a2)
               for a1, a2 in zip(games(2, m_begin=2, m_end=2), resnp[-1:]))


def test6():
    assert count_games(num_agents=4, m_end=2) == 72
    assert count_games(num_agents=4, m_begin=2, m_end=2) == 61
    assert count_unstable_games(num_agents=6, m_begin=2, m_end=2, k=4) == (9, 66515)


def test7():
    assert count_unstable_games(num_agents=4, m_begin=4, m_end=4,
                                k=3, weights=[0, 1, 4, 7, 9]) == (2, 775)
