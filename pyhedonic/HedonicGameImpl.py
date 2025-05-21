"""
Highly optimized code for brute-forcing hedonic game explorations.

Parameters mostly have the same meaning in all functions, namely:
- `game`: a game, that is, a matrix of valuations. `game[i,j]` is the valuation of agent `j` for agent `i`;
- `k`: the maximum size of coalitions. If `None`, there is no restriction on the size of coalitions;
- `is_fractional`: if `True`, the game is fractional, otherwise it is additively separable;
- `weights`: maps evaluations in `game` to a different scale. If `None`, the original valuations are used.
- `m_begin`: the starting value of m for the game iterator. `m` is the maximum valuation of the game.
- `m_end`: the ending value of m for the game iterator. `m` is the maximum valuation of the game.
- `cs`: a coalition structure, that is, a vector of integers mapping agents to coalitions numbers.
        `cs[i]` is the coalition of agent `i`;
- `cs_sizes`: a vector of integers mapping coalition numbers to their sizes. `cs_sizes[i]` is the size of coalition `i`;
- `debug`: debug verbosity. Zero or negative is no debug.

"""

from typing import Iterator, NamedTuple

import numpy as np
import numpy.typing as npt
from numba import config, njit

# pyright: reportAttributeAccessIssue=false
config.DISABLE_JIT = False

# Unfortunately, specifying the shape of the array in the type hint does not work well
type IntArray2D = npt.NDArray[np.integer]

# Unfortunately, specifying the shape of the array in the type hint does not work well
type IntArray1D = npt.NDArray[np.integer]

type Game = IntArray2D

type CoalitionStructure = IntArray1D


class Deviation(NamedTuple):
    """A deviation in a coalition structure"""

    ag: int
    """Agent performing the deviation"""

    co: int
    """New coalition of the agent"""


@njit
def agent_utility_co(game: Game, cs: CoalitionStructure, ag: int, co: int,
                     weights: list[int] | None = None) -> tuple[int, int]:
    """
    Compute the utility of the agent `ag` in the given `game` w.r.t. the coalition structure `cs`. It actually returns
    two values: the sum of the valuations of the agent `ag` w.r.t. the agents in the coalition `co`, and the
    number of agents in `co`.
    """
    num_agents = len(game)
    ut = 0
    size = 0
    for j in range(num_agents):
        if cs[j] == co:
            x = game[ag, j]
            ut += game[ag, j] if weights is None else weights[game[ag, j]]
            size += 1
    return ut, size


@njit
def agent_utility(game: Game, cs: CoalitionStructure, ag: int,
                  weights: list[int] | None = None) -> tuple[int, int]:
    """
    Compute the utility of the agent `ag` in the given `game`. It actually returns two values: the sum of the valuations of
    the agent `ag` with the other agents in the same coalition, and the number of agents in the same coalition as `ag`.
    """
    return agent_utility_co(game, cs, ag, cs[ag], weights)


@njit
def coalition_social_welfare(game: Game, cs: CoalitionStructure, co: int,
                             weights: list[int] | None = None) -> tuple[int, int]:
    """
    Compute the social welfare of the coalition `co` in the given game and coalition structure.
    """
    num_agents = len(game)
    ut = 0
    size = 0
    for i in range(num_agents):
        if cs[i] == co:
            size += 1
            for j in range(num_agents):
                if cs[j] == co:
                    ut += game[i, j] if weights is None else weights[game[i, j]]
    return ut, size


@njit
def is_improving_deviation(game: Game, is_fractional: bool, cs: CoalitionStructure, cs_sizes: IntArray1D, dev: Deviation,
                           weights: list[int] | None = None) -> bool:
    """
    Determine if `dev` is an improving deviation for the given game and coalition structure.
    """
    num_agents = len(game)
    ag, co_new = dev
    co_old = cs[ag]
    if co_old == co_new:
        return False
    ut_old = 0
    ut_new = 0
    for j in range(num_agents):
        if cs[j] == co_old:
            ut_old += game[ag, j] if weights is None else weights[game[ag, j]]
        elif cs[j] == co_new:
            ut_new += game[ag, j] if weights is None else weights[game[ag, j]]

    if not is_fractional:
        return ut_new > ut_old
    elif ut_old == ut_new == 0:
        return cs_sizes[co_new]+1 < cs_sizes[co_old]
    else:
        return ut_new * cs_sizes[co_old] > ut_old * (cs_sizes[co_new]+1)


@njit
def next_improving_deviation(game: Game, is_fractional: bool, cs: CoalitionStructure, cs_sizes: IntArray1D,
                             num_coalitions: int, k: int | None, weights: list[int] | None = None,
                             dev: Deviation = Deviation(0, -1)) -> Deviation | None:
    """
    Return the next improving deviation in the given game and coalition structure. The parameter `dev` is the
    last found improving deviation (use default value if you need to find the first deviation).
    """
    ag, co = dev
    ag = max(ag, 0)
    while ag < len(game):
        co += 1
        while co <= num_coalitions and co < len(cs_sizes):
            if k is None or cs_sizes[co] < k:
                if is_improving_deviation(game, is_fractional, cs, cs_sizes, Deviation(ag, co), weights):
                    return Deviation(ag, co)
            co += 1
        ag += 1
        co = -1
    return None


@njit
def improving_deviations(game: Game, is_fractional: bool, cs: CoalitionStructure, cs_sizes: IntArray1D,
                         num_coalitions: int, k: int | None, weights: list[int] | None = None) -> list[Deviation]:
    """
    Return a list of improving deviations for the given game and coalition structure.
    """
    res = []
    dev = next_improving_deviation(game, is_fractional, cs, cs_sizes, num_coalitions, k, weights)
    while dev is not None:
        res.append(dev)
        dev = next_improving_deviation(
            game, is_fractional, cs, cs_sizes, num_coalitions, k, weights, dev)
    return res


type CoalitionStructureIterator = tuple[CoalitionStructure, IntArray1D, IntArray1D, IntArray1D]
"""
An iterator over coalition structures:
- the first element (`cs`) is the current coalition structure;
- the second element (`cs_sizes`) is the vector of sizes of the coalitions;
- the third element (`cs_nums`) is the vector of cumulative maximum coalition numbers for each agent, i.e.,
  `cs_nums[i]` is equal to `max(cs[i] for i in range(i)`);
- the last element is the sought number of coalitions.
"""

@njit
def cs_givensize_begin(game: Game, num_coalitions: int, k: int | None = None) -> CoalitionStructureIterator:
    """
    Build an iterator for coalition structures with `num_coalitions` coalitions.
    """
    num_agents = len(game)
    return np.full((num_agents), -1), np.zeros((num_agents), dtype=np.int_), np.full((num_agents + 1), -1), np.array([num_coalitions])


@njit
def cs_givensize_next(cs_data: CoalitionStructureIterator, game: Game, k: int | None = None, ) -> bool:
    """
    Update the iterator with a new coalition structure. Return `False` if there are no more coalition structures
    to iterate.
    """
    num_agents = len(game)
    cs, cs_sizes, cs_nums, num_coalitions = cs_data
    ag = 0 if cs[0] == -1 else num_agents - 1
    while True:
        if ag == num_agents:
            return True
        if ag == -1:
            return False
        # `coalitions_potential` is the number of coalitions that can be formed with the remaining agents.
        coalitions_potential = cs_nums[ag] + 1 + (num_agents - ag)
        bot = 0 if coalitions_potential > num_coalitions[0] else cs_nums[ag] + 1
        top = cs_nums[ag] + 1 if cs_nums[ag] + 1 < num_coalitions[0] else cs_nums[ag]
        co = cs[ag]
        if co > -1:
            cs_sizes[co] -= 1
        co_new = max(co+1, bot)
        while co_new <= top:
            if k is None or cs_sizes[co_new] < k:
                break
            co_new += 1
        if co_new <= top:
            cs[ag] = co_new
            cs_sizes[co_new] += 1
            cs_nums[ag+1] = max(cs_nums[ag], co_new)
            ag += 1
        else:
            cs[ag] = -1
            ag -= 1


@njit
def cs_begin(game: Game, k: int | None = None) -> CoalitionStructureIterator:
    """
    Build an iterator for coalition structures with `num_coalitions` coalitions.
    """
    return cs_givensize_begin(game, 1, k)


@njit
def cs_next(cs_data: CoalitionStructureIterator, game: Game, k: int | None) -> bool:
    """
    Update the iterator with a new coalition structure. Return `False` if there are no more coalition structures
    to iterate.
    """
    num_agents = len(game)
    cs, cs_sizes, cs_nums, num_coalitions = cs_data
    while num_coalitions[0] <= num_agents:
        res = cs_givensize_next(cs_data, game, k)
        if res:
            return True
        num_coalitions[0] += 1
        cs.fill(-1)
        cs_nums.fill(-1)
        cs_sizes.fill(0)
    return False


@njit
def css_givensize(game: Game, num_coalitions: int, k: int | None = None) -> Iterator[CoalitionStructure]:
    """
    Return a valid list of coalition structures for the given parameters.
    """
    cs_data = cs_givensize_begin(game, num_coalitions, k)
    while cs_givensize_next(cs_data, game,  k):
        yield np.copy(cs_data[0])


@njit
def css(game: Game, k: int | None = None) -> Iterator[CoalitionStructure]:
    """
    Return a valid list of coalition structures for the given parameters.
    """
    cs_data = cs_begin(game, k)
    while cs_next(cs_data, game, k):
        yield np.copy(cs_data[0])


@njit
def nash_equilibria(game: Game, is_fractional: bool = True, k: int | None = None, weights: list[int] | None = None) -> Iterator[CoalitionStructure]:
    """
    Iterate over all Nash equilibria of the given game.
    """
    cs_data: CoalitionStructureIterator = cs_begin(game, k)
    while cs_next(cs_data, game, k):
        cs, cs_sizes, _, num_coalitions = cs_data
        res = next_improving_deviation(game, is_fractional, cs, cs_sizes, num_coalitions[0], k, weights)
        if res is None:
            yield np.copy(cs)


@njit
def nash_equilibrium(game: Game, is_fractional: bool = True, k: int | None = None, weights: list[int] | None = None) -> CoalitionStructure | None:
    """
    Return the first Nash equilibrium of the given game.
    """
    cs_data: CoalitionStructureIterator = cs_begin(game, k)
    while cs_next(cs_data, game, k):
        cs, cs_sizes, _, num_coalitions = cs_data
        res = next_improving_deviation(game, is_fractional, cs, cs_sizes, num_coalitions[0], k, weights)
        if res is None:
            return cs


# Note the use of the "data" field to store additional information. This is the best solution we have found so far allowing the
# [game_next] function to change the value of these variables. The problem is that numba does not allow dataclasses to be used.
# Other solutions we tried where:
# - Using a @jitclass, but this is quite slower than the current solution.
# - Using a structref, but this is not supported when JIT is disabled, and it seriously hinder debugging.
# - Using a structured scalar, but this is annoying since these scalars can be used but not generated inside JITTED code.

class GameIterator(NamedTuple):
    """
    An internal iterator over games.
    """

    game: Game
    """
    The last game computed by the iterator.
    """

    data: IntArray1D
    """
    Further search parameters, i.e. current value of `m` and position where it has been reached.
    """

    is_symmetric: bool
    """
    Restrict to symmetric games.
    """

    m_end: int
    """
    Max valued of `m` to be considered.
    """

    debug: int
    """
    Debug verbosity. Zero or negative is no debug.
    """

# Constants for the data field of the GameIterator

_SOUGHT_MAX_VALUATION = 0
_REACHED_MAX_VALUATION = 1

@njit
def game_begin(num_agents: int, is_symmetric: bool = True, m_begin: int = 0, m_end: int = 1, debug: int = 0) -> GameIterator:
    """
    Build an iterator over games.
    """
    game = np.zeros((num_agents, num_agents), dtype=np.int_)
    game[num_agents-1, num_agents-1] = -1
    if debug > 0:
        print("sought_reward:", m_begin)
        for col in range(1, min(debug, num_agents)+1):
            print(f"{"  " * col}[{col}] v: 0")
    return GameIterator(game, np.array([m_begin, -1]), is_symmetric, m_end, debug)


@njit
def game_next(git: GameIterator) -> bool:
    """
    Update the iterator with a new game. Return `False` if there are no more games.
    """

    def next_pos(row, col, num_agents: int) -> tuple[int, int]:
        return (row, col+1) if col < num_agents - 1 else (row+1, 0)

    def prev_pos(row, col, num_agents: int) -> tuple[int, int]:
        return (row, col-1) if col > 0 else (row-1, num_agents-1)

    game, data, is_symmetric, max_valuation, debug = git
    num_agents = len(game)
    pos_final = num_agents * num_agents - 1
    row = num_agents - 1
    col = num_agents - 1
    pos = pos_final
    while data[_SOUGHT_MAX_VALUATION] <= max_valuation:
        while row >= 0:
            # Checks in line 2 and 3 of the following code are used to remove graphs that are isomorphic
            # to other graphs found in other iterations. They are actuall not needed, since the check later
            # on the code will subsume them, but they are kept because they make the execution faster.

            bot = game[col][row] if is_symmetric and row > col else \
                game[row][col-1] if row == 0 and col > 0 else \
                game[0][1] if row > 0 and row != col else \
                0
            top = 0 if row == col else  \
                game[col][row] if is_symmetric and row > col else \
                data[_SOUGHT_MAX_VALUATION]

            v = game[row][col]
            v_new = max(v+1, bot)

            if v_new <= top:
                game[row][col] = v_new

                # ISOMORPHISM CHECK
                # Codish et al, Constraints for symmetry breaking in graph representation, Constraints 24 (2019)
                is_invalid_graph = False
                if row > 0 and col == num_agents-1:
                    for i in range(0, row):
                        if i == row-2:
                            continue
                        for j in range(0, num_agents):
                            if j == i or j == row:
                                continue
                            if game[i, j] == game[row, j]:
                                continue
                            if game[i, j] > game[row, j]:
                                is_invalid_graph = True
                            break
                        if is_invalid_graph:
                            break

                if not is_invalid_graph:
                    if debug > 0 and row == 0 and 0 < col <= debug:
                        print(f"{"  " * col}[{col}] v: {v_new}")
                    if v_new == data[_SOUGHT_MAX_VALUATION] and data[_REACHED_MAX_VALUATION] == -1:
                        data[_REACHED_MAX_VALUATION] = pos
                    if pos == pos_final:
                        if data[_REACHED_MAX_VALUATION] != -1:
                            return True
                    else:
                        row, col = next_pos(row, col, num_agents)
                        pos += 1
            elif v_new > top:
                game[row][col] = -1
                if data[_REACHED_MAX_VALUATION] == pos:
                    data[_REACHED_MAX_VALUATION] = -1
                row, col = prev_pos(row, col, num_agents)
                pos -= 1

        data[_SOUGHT_MAX_VALUATION] += 1
        if debug > 0 and data[_SOUGHT_MAX_VALUATION] <= max_valuation:
            print("sought_reward:", data[_SOUGHT_MAX_VALUATION])
        row = 0
        pos = 0
        col = 0
    return False


@njit
def game_next_unstable(git: GameIterator, is_fractional: bool = True, k: int | None = None, weights: list[int] | None = None) -> bool:
    """
    Update the iterator with a new **Nash stable** coalition structure. Return `False` if there are no more coalition structures
    """
    while game_next(git):
        if nash_equilibrium(git.game, is_fractional, k) is None:
            return True
    return False


@njit
def games(num_agents: int, is_symmetric: bool = True, m_begin: int = 0, m_end: int = 1) -> Iterator[Game]:
    """
    Iterate over games.
    """
    git = game_begin(num_agents, is_symmetric, m_begin, m_end)
    while game_next(git):
        yield np.copy(git.game)


@njit
def unstable_game(num_agents: int, is_symmetric: bool = True, m_begin: int = 0, m_end: int = 1, k: int | None = None,
                  is_fractional: bool = True, weights: list[int] | None = None, debug: int = 0) -> Iterator[Game]:
    """
    Iterates over games without a Nash stable coalition structure.
    """
    git = game_begin(num_agents, is_symmetric, m_begin, m_end, debug)
    while game_next_unstable(git, is_fractional, k, weights):
        yield np.copy(git.game)


@njit
def count_unstable_games(num_agents: int, is_symmetric: bool = True, m_begin: int = 0, m_end: int = 1, k: int | None = None,
                         is_fractional: bool = True, weights: list[int] | None = None, debug: int = 0) -> tuple[int, int]:
    """
    Count the number of games without a Nash stable coalition structure. The first returned value is the number of games
    without a Nash stable coalition structure, while the second value is the total number of games considered.
    """
    git = game_begin(num_agents, is_symmetric, m_begin, m_end, debug)
    count_total = 0
    count_noequilibrium = 0
    first = True
    while game_next(git):
        count_total += 1
        if nash_equilibrium(git.game, is_fractional, k, weights) is None:
            if debug > 0 and first:
                first = False
                print(git.game)
            count_noequilibrium += 1
    return count_noequilibrium, count_total


@njit
def count_games(num_agents: int, is_symmetric: bool = True, m_begin: int = 0, m_end: int = 1, debug: int = 0) -> int:
    """
    Count the number of games we generate. This is the same value of the second value of the tuple returned by
    `count_unstable_games`.
    """
    git = game_begin(num_agents, is_symmetric, m_begin, m_end, debug)
    count_total = 0
    while game_next(git):
        count_total += 1
    return count_total
