"""
This file contains unit tests for the pyhedonic library.

In particular, it tests the HedonicGameImpl module, which implements the core functionality of the
library using Numba.
"""

from fractions import Fraction

import numpy as np

from pyhedonic import hedonicgame_impl as hgimpl

GAME1 = np.array(
    [
        [0, 0, 2],
        [1, 0, 3],
        [2, 0, 0],
    ]
)
GAME1_CS1 = np.array([1, 0, 1])
GAME1_CS1_SIZES = np.array([1, 2, 0])
GAME1_CS2 = np.array([0, 0, 0])
GAME1_CS3 = np.array([0, 1, 2])

GAME2 = np.array(
    [
        [0, 1],
        [0, 0],
    ]
)
GAME2_CS1 = np.array([0, 0])
GAME2_CS1_SIZES = np.array([2, 0])

GAME3 = np.array(
    [
        [0, 0, 1],
        [0, 0, 0],
        [0, 0, 0],
    ]
)
GAME3_CS1 = np.array([0, 0, 0])

GAME4 = np.array(
    [
        [0, 0, 2],
        [1, 0, 3],
        [2, 0, 0],
    ]
)
GAME4_CS1 = np.array([1, 0, 1])
GAME4_CS2 = np.array([0, 0, 0])

GAME5 = np.array(
    [
        [0, 1, 1],
        [1, 0, 1],
        [1, 1, 0],
    ]
)
GAME5_CS1 = np.array([0, 1, 2])

GAME6 = np.array(
    [
        [0, 9, 9, 4],
        [9, 0, 1, 7],
        [9, 1, 0, 7],
        [4, 7, 7, 0],
    ]
)


def compare_nparray_list(list1, list2):
    return all(np.array_equal(a1, a2) for a1, a2 in zip(list1, list2))


def assert_rational_equal(res: hgimpl.Rational, expected: hgimpl.Rational):
    assert Fraction(res.numerator, res.denominator) == Fraction(
        expected.numerator, expected.denominator
    )


def assert_game_collection_counts(
    res: hgimpl.GameCollectionCounts, gcc: hgimpl.GameCollectionCounts
):
    assert res.count_total == gcc.count_total
    assert res.count_noequilibrium == gcc.count_noequilibrium
    if res.count_noequilibrium > 0:
        assert np.array_equal(res.example_noequilibrium, np.array(gcc.example_noequilibrium))


def assert_game_prices(res: hgimpl.GamePrices, expected: hgimpl.GamePrices):
    assert res.sw_best == expected.sw_best
    assert np.array_equal(res.cs_best, np.array(expected.cs_best))
    assert res.sw_best_equilibrium == expected.sw_best_equilibrium
    assert np.array_equal(res.cs_best_equilibrium, np.array(expected.cs_best_equilibrium))
    assert res.sw_worst_equilibrium == expected.sw_worst_equilibrium
    assert np.array_equal(res.cs_worst_equilibrium, np.array(expected.cs_worst_equilibrium))


def assert_game_collection_prices(
    res: hgimpl.GameCollectionPrices, expected: hgimpl.GameCollectionPrices
):
    assert_rational_equal(res.poa_highest, expected.poa_highest)
    assert res.poa_highest_count == expected.poa_highest_count
    assert np.array_equal(res.poa_highest_game, np.array(expected.poa_highest_game))
    assert_game_prices(res.poa_highest_info, expected.poa_highest_info)
    assert_rational_equal(res.poa_lowest, expected.poa_lowest)
    assert res.poa_lowest_count == expected.poa_lowest_count
    assert np.array_equal(res.poa_lowest_game, np.array(expected.poa_lowest_game))
    assert_game_prices(res.poa_lowest_info, expected.poa_lowest_info)
    assert_rational_equal(res.pos_highest, expected.pos_highest)
    assert res.pos_highest_count == expected.pos_highest_count
    assert np.array_equal(res.pos_highest_game, np.array(expected.pos_highest_game))
    assert_game_prices(res.pos_highest_info, expected.pos_highest_info)
    assert_rational_equal(res.pos_lowest, expected.pos_lowest)
    assert res.pos_lowest_count == expected.pos_lowest_count
    assert np.array_equal(res.pos_lowest_game, np.array(expected.pos_lowest_game))
    assert_game_prices(res.pos_lowest_info, expected.pos_lowest_info)
    assert np.isclose(res.poa_avg, expected.poa_avg)
    assert np.isclose(res.pos_avg, expected.pos_avg)


def assert_game_collection_info(
    res: hgimpl.GameCollectionInfo, expected: hgimpl.GameCollectionInfo
):
    assert res.counts is not None
    assert expected.counts is not None
    assert_game_collection_counts(res.counts, expected.counts)
    assert res.prices is not None
    assert expected.prices is not None
    assert_game_collection_prices(res.prices, expected.prices)


def test_agent_utility_co():
    assert hgimpl.agent_utility_co(GAME1, GAME1_CS1, ag=0, co=0) == hgimpl.AgentUtility(0, 2)
    assert hgimpl.agent_utility_co(GAME1, GAME1_CS1, ag=0, co=1) == hgimpl.AgentUtility(2, 2)
    assert hgimpl.agent_utility_co(GAME1, GAME1_CS1, ag=1, co=0) == hgimpl.AgentUtility(0, 1)
    assert hgimpl.agent_utility_co(GAME1, GAME1_CS1, ag=1, co=1) == hgimpl.AgentUtility(4, 3)
    # non existent coalition
    assert hgimpl.agent_utility_co(GAME1, GAME1_CS1, ag=0, co=2) == hgimpl.AgentUtility(0, 1)
    assert hgimpl.agent_utility_co(GAME1, GAME1_CS1, ag=1, co=2) == hgimpl.AgentUtility(0, 1)


def test_agent_utility():
    assert hgimpl.agent_utility(GAME1, GAME1_CS1, ag=0) == hgimpl.AgentUtility(2, 2)
    assert hgimpl.agent_utility(GAME1, GAME1_CS1, ag=1) == hgimpl.AgentUtility(0, 1)
    assert hgimpl.agent_utility(GAME1, GAME1_CS2, ag=1) == hgimpl.AgentUtility(4, 3)


def test_coalition_social_welfare():
    assert hgimpl.coalition_social_welfare(GAME1, GAME1_CS1, co=0) == hgimpl.Rational(0, 1)
    assert hgimpl.coalition_social_welfare(GAME1, GAME1_CS1, co=1) == hgimpl.Rational(4, 2)
    assert hgimpl.coalition_social_welfare(GAME1, GAME1_CS2, co=0) == hgimpl.Rational(8, 3)
    # non-existent coalition
    assert hgimpl.coalition_social_welfare(GAME1, GAME1_CS2, co=1) == hgimpl.Rational(0, 0)


def test_is_improving_deviation():
    assert hgimpl.is_improving_deviation(
        GAME1, True, GAME1_CS1, GAME1_CS1_SIZES, hgimpl.Deviation(1, 1)
    )
    assert not hgimpl.is_improving_deviation(
        GAME1, True, GAME1_CS1, GAME1_CS1_SIZES, hgimpl.Deviation(0, 0)
    )
    assert not hgimpl.is_improving_deviation(
        GAME2, True, GAME2_CS1, GAME2_CS1_SIZES, hgimpl.Deviation(0, 1)
    )
    # moving to a coalition with fewer agents and the same (null) utility for fractional games
    assert hgimpl.is_improving_deviation(
        GAME2, True, GAME2_CS1, GAME2_CS1_SIZES, hgimpl.Deviation(1, 1)
    )
    # moving to a coalition with fewer agents and the same (null) utility for additive games
    assert not hgimpl.is_improving_deviation(
        GAME2, False, GAME2_CS1, GAME2_CS1_SIZES, hgimpl.Deviation(1, 1)
    )


def test_improving_deviations():
    assert list(hgimpl.improving_deviations(GAME1, True, GAME1_CS1)) == [(1, 1)]
    assert (
        list(
            hgimpl.improving_deviations(
                GAME1,
                True,
                GAME1_CS2,
            )
        )
        == []
    )
    assert list(hgimpl.improving_deviations(GAME1, True, GAME1_CS3)) == [
        (0, 2),
        (1, 0),
        (1, 2),
        (2, 0),
    ]
    assert list(hgimpl.improving_deviations(GAME2, True, GAME2_CS1)) == [(1, 1)]
    assert list(hgimpl.improving_deviations(GAME2, False, GAME2_CS1)) == []
    assert list(hgimpl.improving_deviations(GAME3, True, GAME3_CS1)) == [
        (1, 1),
        (2, 1),
    ]
    assert list(hgimpl.improving_deviations(GAME5, True, GAME5_CS1)) == [
        (0, 1),
        (0, 2),
        (1, 0),
        (1, 2),
        (2, 0),
        (2, 1),
    ]


def test_best_improving_deviations():
    assert list(hgimpl.best_improving_deviations(GAME1, True, GAME1_CS1)) == [(1, 1)]
    assert list(hgimpl.best_improving_deviations(GAME1, True, GAME1_CS2)) == []
    assert list(hgimpl.best_improving_deviations(GAME1, True, GAME1_CS3)) == [
        (0, 2),
        (1, 2),
        (2, 0),
    ]
    assert list(hgimpl.best_improving_deviations(GAME2, True, GAME2_CS1)) == [(1, 1)]
    assert list(hgimpl.best_improving_deviations(GAME2, False, GAME2_CS1)) == []
    assert list(hgimpl.best_improving_deviations(GAME3, True, GAME3_CS1)) == [
        (1, 1),
        (2, 1),
    ]
    assert list(hgimpl.best_improving_deviations(GAME5, True, GAME5_CS1)) == [
        (0, 1),
        (0, 2),
        (1, 0),
        (1, 2),
        (2, 0),
        (2, 1),
    ]


def test_css_givensize():
    assert compare_nparray_list(hgimpl.css_givensize(3, 1), [[0, 0, 0]])
    assert compare_nparray_list(hgimpl.css_givensize(3, 2), [[0, 0, 1], [0, 1, 0], [0, 1, 1]])
    assert compare_nparray_list(hgimpl.css_givensize(3, 2, k=2), [[0, 0, 1], [0, 1, 0], [0, 1, 1]])
    assert compare_nparray_list(hgimpl.css_givensize(3, 2, k=1), [])
    assert compare_nparray_list(hgimpl.css_givensize(3, 3), [[0, 1, 2]])
    assert compare_nparray_list(
        hgimpl.css_givensize(4, 2, 2),
        [[0, 0, 1, 1], [0, 1, 0, 1], [0, 1, 1, 0]],
    )


def test_css():
    assert compare_nparray_list(
        hgimpl.css(3), [[0, 0, 0], [0, 0, 1], [0, 1, 0], [0, 1, 1], [0, 1, 2]]
    )
    assert compare_nparray_list(hgimpl.css(3, k=2), [[0, 0, 1], [0, 1, 0], [0, 1, 1], [0, 1, 2]])
    assert compare_nparray_list(hgimpl.css(3, k=1), [[0, 1, 2]])
    assert compare_nparray_list(
        hgimpl.css(4, k=2),
        [
            [0, 0, 1, 1],
            [0, 1, 0, 1],
            [0, 1, 1, 0],
            [0, 0, 1, 2],
            [0, 1, 0, 2],
            [0, 1, 1, 2],
            [0, 1, 2, 0],
            [0, 1, 2, 1],
            [0, 1, 2, 2],
            [0, 1, 2, 3],
        ],
    )


def test_bash_equilibria():
    assert compare_nparray_list(hgimpl.nash_equilibria(GAME4), [[0, 0, 0]])
    assert compare_nparray_list(hgimpl.nash_equilibria(GAME4, k=1), [[0, 1, 2]])
    assert compare_nparray_list(hgimpl.nash_equilibria(GAME6, k=3), [])


def test_bash_equilibrium():
    assert np.all(hgimpl.nash_equilibrium(GAME4) == [0, 0, 0])
    assert np.all(hgimpl.nash_equilibrium(GAME4, k=1) == [0, 1, 2])
    assert hgimpl.nash_equilibrium(GAME6, k=3) is None


def test_games():
    res = [
        [[0, 0], [0, 0]],
        [[0, 1], [1, 0]],
        [[0, 2], [2, 0]],
    ]
    assert compare_nparray_list(hgimpl.games(2, m_end=2), res)
    assert compare_nparray_list(hgimpl.games(2, m_begin=2, m_end=2), res[-1:])


def test_unstable_games():
    assert compare_nparray_list(hgimpl.unstable_games(2, m_end=2), [])
    assert compare_nparray_list(hgimpl.unstable_games(2, m_begin=2, m_end=2), [])


def test_count_games():
    assert hgimpl.count_games(agent_count=4, m_end=2) == 72
    assert hgimpl.count_games(agent_count=4, m_begin=2, m_end=2) == 61


def test_count_unstable_games():
    res = hgimpl.count_unstable_games(agent_count=6, m_begin=2, m_end=2, k=4)
    gcc = hgimpl.GameCollectionCounts(
        count_total=66515,
        count_noequilibrium=9,
        example_noequilibrium=np.array(
            [
                [0, 0, 0, 0, 0, 1],
                [0, 0, 0, 0, 2, 2],
                [0, 0, 0, 2, 0, 2],
                [0, 0, 2, 0, 0, 2],
                [0, 2, 0, 0, 0, 2],
                [1, 2, 2, 2, 2, 0],
            ]
        ),
    )
    assert_game_collection_counts(res, gcc)

    res = hgimpl.count_unstable_games(
        agent_count=4,
        m_begin=4,
        m_end=4,
        k=3,
        weights=np.array([0, 1, 4, 7, 9]),
    )
    gcc = hgimpl.GameCollectionCounts(
        count_total=775,
        count_noequilibrium=2,
        example_noequilibrium=np.array(
            [
                [0, 0, 7, 9],
                [0, 0, 7, 9],
                [7, 7, 0, 4],
                [9, 9, 4, 0],
            ]
        ),
    )
    assert_game_collection_counts(res, gcc)


def test_game_collection_info():
    res = hgimpl.game_collection_info(agent_count=6, m_begin=2, m_end=2, k=4)
    expected = hgimpl.GameCollectionInfo(
        counts=hgimpl.GameCollectionCounts(
            count_total=66515,
            count_noequilibrium=9,
            example_noequilibrium=np.array(
                [
                    [0, 0, 1, 1, 2, 2],
                    [0, 0, 1, 2, 1, 2],
                    [1, 1, 0, 1, 1, 1],
                    [1, 2, 1, 0, 0, 2],
                    [2, 1, 1, 0, 0, 2],
                    [2, 2, 1, 2, 2, 0],
                ]
            ),
        ),
        prices=hgimpl.GameCollectionPrices(
            poa_highest=hgimpl.Rational(48, 18),
            poa_highest_count=15,
            poa_highest_game=np.array(
                [
                    [0, 0, 0, 0, 0, 1],
                    [0, 0, 0, 1, 1, 0],
                    [0, 0, 0, 1, 1, 0],
                    [0, 1, 1, 0, 2, 0],
                    [0, 1, 1, 2, 0, 0],
                    [1, 0, 0, 0, 0, 0],
                ]
            ),
            poa_highest_info=hgimpl.GamePrices(
                sw_best=48,
                cs_best=np.array([0, 1, 1, 1, 1, 0]),
                sw_best_equilibrium=48,
                cs_best_equilibrium=np.array([0, 1, 1, 1, 1, 0]),
                sw_worst_equilibrium=18,
                cs_worst_equilibrium=np.array([0, 1, 2, 0, 0, 0]),
            ),
            poa_lowest=hgimpl.Rational(1, 1),
            poa_lowest_count=11442,
            poa_lowest_game=np.array(
                [
                    [0, 0, 0, 0, 0, 0],
                    [0, 0, 0, 0, 0, 0],
                    [0, 0, 0, 0, 0, 0],
                    [0, 0, 0, 0, 0, 0],
                    [0, 0, 0, 0, 0, 2],
                    [0, 0, 0, 0, 2, 0],
                ]
            ),
            poa_lowest_info=hgimpl.GamePrices(
                sw_best=24,
                cs_best=np.array([0, 0, 0, 0, 1, 1]),
                sw_best_equilibrium=24,
                cs_best_equilibrium=np.array([0, 1, 2, 3, 4, 4]),
                sw_worst_equilibrium=24,
                cs_worst_equilibrium=np.array([0, 1, 2, 3, 4, 4]),
            ),
            pos_highest=hgimpl.Rational(80, 48),
            pos_highest_count=1,
            pos_highest_game=np.array(
                [
                    [0, 0, 0, 1, 2, 2],
                    [0, 0, 2, 1, 0, 2],
                    [0, 2, 0, 1, 1, 2],
                    [1, 1, 1, 0, 1, 1],
                    [2, 0, 1, 1, 0, 2],
                    [2, 2, 2, 1, 2, 0],
                ]
            ),
            pos_highest_info=hgimpl.GamePrices(
                sw_best=80,
                cs_best=np.array([0, 1, 1, 0, 0, 1]),
                sw_best_equilibrium=48,
                cs_best_equilibrium=np.array([0, 1, 2, 2, 2, 2]),
                sw_worst_equilibrium=48,
                cs_worst_equilibrium=np.array([0, 1, 2, 2, 2, 2]),
            ),
            pos_lowest=hgimpl.Rational(1, 1),
            pos_lowest_count=58789,
            pos_lowest_game=np.array(
                [
                    [0, 0, 0, 0, 0, 0],
                    [0, 0, 0, 0, 0, 0],
                    [0, 0, 0, 0, 0, 0],
                    [0, 0, 0, 0, 0, 0],
                    [0, 0, 0, 0, 0, 2],
                    [0, 0, 0, 0, 2, 0],
                ]
            ),
            pos_lowest_info=hgimpl.GamePrices(
                sw_best=24,
                cs_best=np.array([0, 0, 0, 0, 1, 1]),
                sw_best_equilibrium=24,
                cs_best_equilibrium=np.array([0, 1, 2, 3, 4, 4]),
                sw_worst_equilibrium=24,
                cs_worst_equilibrium=np.array([0, 1, 2, 3, 4, 4]),
            ),
            poa_avg=1.299399060751563,
            pos_avg=1.0072630585901752,
        ),
    )
    assert_game_collection_info(res, expected)


def test_game_collection_info2():
    res = hgimpl.game_collection_info(
        agent_count=4, m_begin=4, m_end=4, k=3, weights=np.array([0, 1, 4, 7, 9])
    )
    expected = hgimpl.GameCollectionInfo(
        counts=hgimpl.GameCollectionCounts(
            count_total=775,
            count_noequilibrium=2,
            example_noequilibrium=np.array(
                [
                    [0, 1, 7, 9],
                    [1, 0, 7, 9],
                    [7, 7, 0, 4],
                    [9, 9, 4, 0],
                ]
            ),
        ),
        prices=hgimpl.GameCollectionPrices(
            poa_highest=hgimpl.Rational(68, 40),
            poa_highest_count=1,
            poa_highest_game=np.array(
                [
                    [0, 0, 0, 1],
                    [0, 0, 4, 4],
                    [0, 4, 0, 9],
                    [1, 4, 9, 0],
                ]
            ),
            poa_highest_info=hgimpl.GamePrices(
                sw_best=68,
                cs_best=np.array([0, 1, 1, 1]),
                sw_best_equilibrium=68,
                cs_best_equilibrium=np.array([0, 1, 1, 1]),
                sw_worst_equilibrium=40,
                cs_worst_equilibrium=np.array([0, 1, 0, 0]),
            ),
            poa_lowest=hgimpl.Rational(1, 1),
            poa_lowest_count=442,
            poa_lowest_game=np.array(
                [
                    [0, 0, 0, 0],
                    [0, 0, 0, 0],
                    [0, 0, 0, 9],
                    [0, 0, 9, 0],
                ]
            ),
            poa_lowest_info=hgimpl.GamePrices(
                sw_best=54,
                cs_best=np.array([0, 0, 1, 1]),
                sw_best_equilibrium=54,
                cs_best_equilibrium=np.array([0, 1, 2, 2]),
                sw_worst_equilibrium=54,
                cs_worst_equilibrium=np.array([0, 1, 2, 2]),
            ),
            pos_highest=hgimpl.Rational(60, 44),
            pos_highest_count=3,
            pos_highest_game=np.array(
                [
                    [0, 0, 0, 1],
                    [0, 0, 9, 1],
                    [0, 9, 0, 1],
                    [1, 1, 1, 0],
                ]
            ),
            pos_highest_info=hgimpl.GamePrices(
                sw_best=60,
                cs_best=np.array([0, 1, 1, 0]),
                sw_best_equilibrium=44,
                cs_best_equilibrium=np.array([0, 1, 1, 1]),
                sw_worst_equilibrium=44,
                cs_worst_equilibrium=np.array([0, 1, 1, 1]),
            ),
            pos_lowest=hgimpl.Rational(1, 1),
            pos_lowest_count=554,
            pos_lowest_game=np.array(
                [
                    [0, 0, 0, 0],
                    [0, 0, 0, 0],
                    [0, 0, 0, 9],
                    [0, 0, 9, 0],
                ]
            ),
            pos_lowest_info=hgimpl.GamePrices(
                sw_best=54,
                cs_best=np.array([0, 0, 1, 1]),
                sw_best_equilibrium=54,
                cs_best_equilibrium=np.array([0, 1, 2, 2]),
                sw_worst_equilibrium=54,
                cs_worst_equilibrium=np.array([0, 1, 2, 2]),
            ),
            poa_avg=1.0696687276647048,
            pos_avg=1.032287279340795,
        ),
    )
    assert_game_collection_info(res, expected)
