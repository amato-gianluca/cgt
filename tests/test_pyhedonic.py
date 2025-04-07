from .context import pyhedonic

from pyhedonic.HedonicGame import *

import numpy as np


def test1():
    valuations = np.array([
        [0, 0, 2],
        [1, 0, 3],
        [2, 0, 0]
    ])
    game = Game(valuations, is_symmetric=True, is_fractional=True)
    cs1 = np.array([1, 0, 1])
    cs1_sizes = np.array([1, 2])
    cs2 = np.array([0, 0, 0])
    cs2_sizes = np.array([3])
    assert is_improving_deviation(game, cs1, True, 1, 1)
    assert not is_improving_deviation(game, cs1, True, 0, 0)
    assert next_improving_deviation_agent(game, cs1, cs1_sizes, True, 1) == 1
    assert improving_deviations_agent(game, cs1, cs1_sizes, True, 1) == [1]
    assert next_improving_deviation(game, cs1, cs1_sizes, True) is not None
    assert next_improving_deviation(game, cs1, cs1_sizes, True, 2) is None
    assert next_improving_deviation(game, cs2, cs2_sizes, True) is None
    assert np.all(nash_equilibrium(game, True) == np.array([0, 0, 0]))
    assert np.all(nash_equilibrium(game, True, k=1) == np.array([0, 1, 2]))


def test2():
    valuations = np.array([
        [0, 9, 9, 4],
        [9, 0, 1, 7],
        [9, 1, 0, 7],
        [4, 7, 7, 0]
    ])
    game = Game(valuations, is_symmetric=True, is_fractional=True, k=3)
    assert nash_equilibrium(game, True, 3) is None


def test3():
    valuations = np.array([
        [0, 1, 1],
        [1, 0, 1],
        [1, 1, 0]
    ])
    game = Game(valuations, is_symmetric=True, is_fractional=True)
    cs = np.array([0, 1, 2])
    cs_sizes = np.array([3, 3, 3])
    assert improving_deviations_agent(game, cs, cs_sizes, True, 0) == [1, 2]
    assert improving_deviations(game, cs, cs_sizes, True) == [
        (0, 1), (0, 2), (1, 0), (1, 2), (2, 0), (2, 1)]


def test4():
    valuations = np.array([
        [0, 1, 1],
        [1, 0, 1],
        [1, 1, 0]
    ])
    game = Game(valuations, is_symmetric=True, is_fractional=True)
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
               for a1, a2 in zip(games(2, True, 0, 2), resnp))
    assert all(np.array_equal(a1, a2)
               for a1, a2 in zip(games(2, True, 2, 2), resnp[-1:]))
