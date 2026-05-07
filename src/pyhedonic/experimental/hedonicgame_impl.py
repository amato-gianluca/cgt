"""
This is an experimental version of the HedonicGameImpl module with an alternative implementation
of nash_equilibrium and nash_equilibria functions. This implementation, instead of building a
complete coalition structure and determine if there are improving deviations, tries to combine
these two things together, so that improving deviations are found as soon as possible even for
a partial coalition structure.

Unfortunately, this seems to improve efficiency only for very small values of k.
"""

from typing import Iterator, NamedTuple

import numpy as np
from numba import njit

from pyhedonic.hedonicgame_impl import (
    CoalitionStructure,
    Deviation,
    Game,
    IntArray1D,
    Weights,
    game_begin,
    game_next,
    is_improving_deviation,
)


@njit
def cs_partial_next(
    cs: CoalitionStructure, cs_sizes: IntArray1D, co: int, ag: int, k: int | None
) -> bool:
    """
    Update the partial coalition structure cs by enumerating all possible ways to add a new partition co.

    All successive calls of cs_partial_next with the same values for cs and ag are logically
    related.

    The first time the function is called with a given combination (co, ag), agent ag should be
    the first non-assigned agent in the partial coalition structure, all coalitions from 0 to
    co-1 should already exist and no other coalition should exist. The function creates the coalition
    co by assigning to it the agent ag.

    Successive calls of cs_partial_next with the same combination (co, ag) assume that cs and cs_sizes
    contain the same value of the original call. The function tries to enumerate all possible ways to
    define the coalition co, respecting the value of k and the fact that ag should be the first element
    of the coalition.

    The function returns True if a new partial coalition structure has been obtained, otherwise it removes
    coalition co and returns False.
    """
    if cs[ag] == -1:
        cs[ag] = co
        cs_sizes[co] += 1
        return True
    co_size = cs_sizes[co]
    for i in range(ag + 1, len(cs)):
        if cs[i] == -1 and (k is None or co_size < k):
            cs[i] = co
            cs_sizes[co] = co_size + 1
            return True
        elif cs[i] == co:
            cs[i] = -1
            co_size -= 1
    # clean coalition co before returning
    for i in range(ag, len(cs)):
        if cs[i] == co:
            cs[i] = -1
    cs_sizes[co] = 0
    return False


@njit
def has_improving_deviation_partial(
    game: Game,
    is_fractional: bool,
    cs: CoalitionStructure,
    cs_sizes: IntArray1D,
    co: int,
    k: int | None,
    weights: Weights | None = None,
) -> bool:
    """
    Determines whether the partial coalition structure cs has an improving deviation involving coalition co.

    The function tries deviations where agents in coalitions different from co are moved to co, and deviations where
    agents in coalition co are moved to a different coalition or even out of any coalition. If any of these deviations
    is improving, the function returns True, otherwise returns False.
    """
    for ag in range(len(game)):
        if cs[ag] == -1:
            pass
        elif cs[ag] != co:
            if (k is None or cs_sizes[co] < k) and is_improving_deviation(
                game, is_fractional, cs, cs_sizes, Deviation(ag, co), weights
            ):
                return True
        else:
            for co_other in range(co):
                if k is None or cs_sizes[co_other] < k:
                    if is_improving_deviation(
                        game,
                        is_fractional,
                        cs,
                        cs_sizes,
                        Deviation(ag, co_other),
                        weights,
                    ):
                        return True
            if cs_sizes[co] > 1 and co < len(game):
                if is_improving_deviation(
                    game, is_fractional, cs, cs_sizes, Deviation(ag, co + 1), weights
                ):
                    return True
    return False


class StableCoalitionStructureIterator(NamedTuple):
    """An iterator for Nash stable coalition structures."""

    cs: CoalitionStructure
    """
    The last coalition structure computed by the iterator.
    """

    cs_sizes: IntArray1D
    """
    The vector of sizes of the coalitions.
    """

    data: IntArray1D
    """
    Additional data for the iterator, i.e., a list whose first (and only) element is the number of coalitions.
    We put this information in an array because we need to modify it during the iterations.
    """


@njit
def cs_stable_begin1(game: Game) -> StableCoalitionStructureIterator:
    """
    Build an iterator for Nash stable coalition structures.
    """
    return StableCoalitionStructureIterator(
        np.full(len(game), -1), np.zeros(len(game), dtype=np.int_), np.array([0])
    )


@njit
def cs_stable_next1(
    cit: StableCoalitionStructureIterator,
    game: Game,
    k: int | None,
    is_fractional: bool,
    weights: Weights | None = None,
) -> bool:
    """
    Update the iterator with a new Nash stable coalition structure.

    The function returns False when the iterator has not been updated since there are no more coalition
    structures, otherwise it returns True.
    """
    # If you want to get sensible performance improvements, we should first consider partitions with
    # fewer coalitions.
    cs, cs_sizes, data = cit
    co = data[0]
    while co >= 0:
        # find either first unallocated agent in coalition structure or first agent in the coalition co
        ag = 0
        while ag < len(cs):
            if cs[ag] == co or cs[ag] == -1:
                break
            ag += 1
        # coalition is complete
        if ag == len(cs):
            data[0] = co - 1
            return True
        res = cs_partial_next(cs, cs_sizes, co, ag, k)
        while res and has_improving_deviation_partial(
            game, is_fractional, cs, cs_sizes, co, k, weights
        ):
            res = cs_partial_next(cs, cs_sizes, co, ag, k)
        co += 1 if res else -1
    return False


@njit
def nash_equilibria(
    game: Game,
    is_fractional: bool = True,
    k: int | None = None,
    weights: Weights | None = None,
) -> Iterator[CoalitionStructure]:
    """
    Iterate over all Nash equilibria of the given game.
    """
    cit = cs_stable_begin1(game)
    while cs_stable_next1(cit, game, k, is_fractional, weights=weights):
        yield np.copy(cit.cs)


@njit
def nash_equilibrium(
    game: Game,
    is_fractional: bool = True,
    k: int | None = None,
    weights: Weights | None = None,
) -> CoalitionStructure | None:
    """
    Return the first Nash equilibrium of the given game.
    """
    cit = cs_stable_begin1(game)
    res = cs_stable_next1(cit, game, k, is_fractional, weights=weights)
    return cit.cs if res else None


@njit
def count_unstable_games(
    num_agents: int,
    is_symmetric: bool = True,
    m_begin: int = 0,
    m_end: int = 1,
    k: int | None = None,
    is_fractional: bool = True,
    weights: Weights | None = None,
    debug: int = 0,
) -> tuple[int, int]:
    """
    Count the number of games without a Nash stable coalition structure.

    The first returned value is the number of games without a Nash stable coalition structure, while the second value
    is the total number of games considered.
    """
    git = game_begin(num_agents, is_symmetric, m_begin, m_end, debug)
    count_total = 0
    count_noequilibrium = 0
    first = True
    while game_next(git):
        count_total += 1
        if nash_equilibrium(git.game_internal, is_fractional, k, weights) is None:
            if debug > 0 and first:
                first = False
                print(git.game)
            count_noequilibrium += 1
    return count_noequilibrium, count_total


@njit
def count_games(
    num_agents: int,
    is_symmetric: bool = True,
    m_begin: int = 0,
    m_end: int = 1,
    debug: int = 0,
) -> int:
    """
    Count the number of games generated by our procedure.

    This is the same value as the second element of the tuple returned by count_unstable_games.
    """
    git = game_begin(num_agents, is_symmetric, m_begin, m_end, debug)
    count_total = 0
    while game_next(git):
        count_total += 1
    return count_total
