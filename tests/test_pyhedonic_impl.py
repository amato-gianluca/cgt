
"""
This file contains unit tests for the pyhedonic library. In particular, it tests the
HedonicGameImpl module, which implements the core functionality of the library using Numba.
"""

from pyhedonic.hedonicgame_impl import *

import numpy as np

GAME1 = np.array([
    [0, 0, 2],
    [1, 0, 3],
    [2, 0, 0]
])
GAME1_CS1 = np.array([1, 0, 1])
GAME1_CS1_SIZES = np.array([1, 2, 0])
GAME1_CS2 = np.array([0, 0, 0])
GAME1_CS2_SIZES = np.array([3, 0, 0])


GAME2 = np.array([
    [0, 1],
    [0, 0]
])
GAME2_CS1 = np.array([0, 0])
GAME2_CS1_SIZES = np.array([2, 0])

GAME3 = np.array([
    [0, 0, 1],
    [0, 0, 0],
    [0, 0, 0]
])
GAME3_CS1 = np.array([0, 0, 0])
GAME3_CS1_SIZES = np.array([3, 0, 0])

GAME4 = np.array([
    [0, 0, 2],
    [1, 0, 3],
    [2, 0, 0]
])
GAME4_CS1 = np.array([1, 0, 1])
GAME4_CS1_SIZES = np.array([1, 2, 0])
GAME4_CS2 = np.array([0, 0, 0])
GAME4_CS2_SIZES = np.array([3, 0, 0])

GAME5 = np.array([
    [0, 1, 1],
    [1, 0, 1],
    [1, 1, 0]
])
GAME5_CS1 = np.array([0, 1, 2])
GAME5_CS1_SIZES = np.array([1, 1, 1])

GAME6 = np.array([
    [0, 9, 9, 4],
    [9, 0, 1, 7],
    [9, 1, 0, 7],
    [4, 7, 7, 0]
])


def compare_nparray_list(list1, list2):
    return all(np.array_equal(a1, a2) for a1, a2 in zip(list1, list2))


def test_agent_utility_co():
    assert agent_utility_co(GAME1, GAME1_CS1, ag=0, co=0) == (0, 1)
    assert agent_utility_co(GAME1, GAME1_CS1, ag=0, co=1) == (2, 2)
    assert agent_utility_co(GAME1, GAME1_CS1, ag=1, co=0) == (0, 1)
    assert agent_utility_co(GAME1, GAME1_CS1, ag=1, co=1) == (4, 2)
    # non existent coalition
    assert agent_utility_co(GAME1, GAME1_CS1, ag=0, co=2) == (0, 0)
    assert agent_utility_co(GAME1, GAME1_CS1, ag=1, co=2) == (0, 0)


def test_agent_utility():
    assert agent_utility(GAME1, GAME1_CS1, ag=0) == (2, 2)
    assert agent_utility(GAME1, GAME1_CS1, ag=1) == (0, 1)
    assert agent_utility(GAME1, GAME1_CS2, ag=1) == (4, 3)


def test_coalition_social_welfare():
    assert coalition_social_welfare(GAME1, GAME1_CS1, co=0) == (0, 1)
    assert coalition_social_welfare(GAME1, GAME1_CS1, co=1) == (4, 2)
    assert coalition_social_welfare(GAME1, GAME1_CS2, co=0) == (8, 3)
    # non-existent coalition
    assert coalition_social_welfare(GAME1, GAME1_CS2, co=1) == (0, 0)


def test_is_improving_deviation():
    assert is_improving_deviation(GAME1, True, GAME1_CS1, GAME1_CS1_SIZES, Deviation(1, 1))
    assert not is_improving_deviation(GAME1, True, GAME1_CS1, GAME1_CS1_SIZES, Deviation(0, 0))
    assert not is_improving_deviation(GAME2, True, GAME2_CS1, GAME2_CS1_SIZES, Deviation(0, 1))
    # moving to a coalition with fewer agents and the same (null) utility for fractional games
    assert is_improving_deviation(GAME2, True, GAME2_CS1, GAME2_CS1_SIZES, Deviation(1, 1))
    # moving to a coalition with fewer agents and the same (null) utility for additive games
    assert not is_improving_deviation(GAME2, False, GAME2_CS1, GAME2_CS1_SIZES, Deviation(1, 1))


def test_improving_deviations():
    assert list(improving_deviations(GAME1, True, GAME1_CS1, GAME1_CS1_SIZES, co_max=len(GAME1_CS1_SIZES), k=None)) \
        == [(1, 1)]
    assert list(improving_deviations(GAME1, True, GAME1_CS2, GAME1_CS2_SIZES, co_max=len(GAME1_CS2_SIZES), k=None)) \
        == []
    assert list(improving_deviations(GAME2, True, GAME2_CS1, GAME2_CS1_SIZES, co_max=len(GAME2_CS1_SIZES), k=None)) \
        == [(1, 1)]
    assert list(improving_deviations(GAME2, False, GAME2_CS1, GAME2_CS1_SIZES, co_max=len(GAME2_CS1_SIZES), k=None)) \
        == []
    assert list(improving_deviations(GAME3, True, GAME3_CS1, GAME3_CS1_SIZES, co_max=len(GAME3_CS1_SIZES), k=None)) \
        == [(1, 1), (1, 2), (2, 1), (2, 2)]
    assert list(improving_deviations(GAME3, True, GAME3_CS1, GAME3_CS1_SIZES, co_max=len(GAME3_CS1_SIZES), k=None)) \
        == [(1, 1), (1, 2), (2, 1), (2, 2)]
    assert list(improving_deviations(GAME3, True, GAME3_CS1, GAME3_CS1_SIZES, co_max=1, k=None)) \
        == [(1, 1),  (2, 1)]
    assert list(improving_deviations(GAME5, True, GAME5_CS1, GAME5_CS1_SIZES, 3, None)) \
        == [(0, 1), (0, 2), (1, 0), (1, 2), (2, 0), (2, 1)]


def test_css_givensize():
    assert compare_nparray_list(css_givensize(3, 1), [[0, 0, 0]])
    assert compare_nparray_list(css_givensize(3, 2),  [[0, 0, 1], [0, 1, 0], [0, 1, 1]])
    assert compare_nparray_list(css_givensize(3, 2, k=2), [[0, 0, 1], [0, 1, 0], [0, 1, 1]])
    assert compare_nparray_list(css_givensize(3, 2, k=1), [])
    assert compare_nparray_list(css_givensize(3, 3), [[0, 1, 2]])
    assert compare_nparray_list(css_givensize(4, 2, 2), [[0, 0, 1, 1], [0, 1, 0, 1], [0, 1, 1, 0]])


def test_css():
    assert compare_nparray_list(css(3), [[0, 0, 0], [0, 0, 1], [0, 1, 0], [0, 1, 1], [0, 1, 2]])
    assert compare_nparray_list(css(3, k=2), [[0, 0, 1], [0, 1, 0], [0, 1, 1], [0, 1, 2]])
    assert compare_nparray_list(css(3, k=1), [[0, 1, 2]])
    assert compare_nparray_list(css(4, k=2),
                                [[0, 0, 1, 1], [0, 1, 0, 1], [0, 1, 1, 0],
                                 [0, 0, 1, 2], [0, 1, 0, 2], [0, 1, 1, 2], [0, 1, 2, 0],  [0, 1, 2, 1], [0, 1, 2, 2],
                                 [0, 1, 2, 3]])


def test_bash_equilibria():
    assert compare_nparray_list(nash_equilibria(GAME4), [[0, 0, 0]])
    assert compare_nparray_list(nash_equilibria(GAME4, k=1), [[0, 1, 2]])
    assert compare_nparray_list(nash_equilibria(GAME6, k=3), [])


def test_bash_equilibrium():
    assert np.all(nash_equilibrium(GAME4) == [0, 0, 0])
    assert np.all(nash_equilibrium(GAME4, k=1) == [0, 1, 2])
    assert nash_equilibrium(GAME6, k=3) is None


def test_games():
    res = [
        [[0, 0], [0, 0]],
        [[0, 1], [1, 0]],
        [[0, 2], [2, 0]],
    ]
    assert compare_nparray_list(games(2, m_end=2), res)
    assert compare_nparray_list(games(2, m_begin=2, m_end=2), res[-1:])

def test_unstable_games():
    res = [
        [[0, 0], [0, 0]],
        [[0, 1], [1, 0]],
        [[0, 2], [2, 0]],
    ]
    assert compare_nparray_list(unstable_games(2, m_end=2), [])
    assert compare_nparray_list(unstable_games(2, m_begin=2, m_end=2), [])


def test_count_games():
    assert count_games(agent_count=4, m_end=2) == 72
    assert count_games(agent_count=4, m_begin=2, m_end=2) == 61


def test_count_unstable_games():
    assert count_unstable_games(agent_count=6, m_begin=2, m_end=2, k=4) \
        == (9, 66515)
    assert count_unstable_games(agent_count=4, m_begin=4, m_end=4, k=3, weights=np.array([0, 1, 4, 7, 9])) \
        == (2, 775)
