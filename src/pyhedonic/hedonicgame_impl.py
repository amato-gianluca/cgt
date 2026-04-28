"""
Highly optimized code for brute-forcing hedonic game explorations.

Parameters mostly have the same meaning in all functions, namely:
- game -- a game, that is, a matrix of valuations:
    - game[i,j] is the valuation of agent j for agent i
- cs -- a coalition structure, that is, a vector of integers mapping each agent to its coalition number:
    - cs[i] is the coalition number of agent i
    - in some cases we work with partial coalition structures, i.e., coalition structures where some
      agents are not assigned to any coalition, and its corresponding value in cs is -1
- cs_sizes -- a vector of integers mapping coalition numbers to their sizes:
    - cs_sizes[i] is the size of coalition i
    - the length of cs_sizes should be equal to the number of agents in game
- k -- the maximum size of coalitions (None in case of no limits)
- is_fractional -- if True, the game is fractional, otherwise it is additively separable
- ag -- an agent number
- co -- a coalition number:
    - it is generally allowed for this parameter to refer to a non-existent coalition
    - if a cs_sizes parameter is also provided, co should be in range(len(cs_sizes))
- dev -- a deviation, i.e., a pair `(ag, co)`
- weights -- a vector mapping evaluations in `game` to a different scale;
    - None means that the original valuations are used
- m_begin -- the minimum valuation for edges in a game
- m_end -- the maximum valuation for edges in a game
- debug -- debug verbosity: zero or negative is no debug
"""

from typing import Iterator, NamedTuple

import numpy as np
import numpy.typing as npt
from numba import config, njit

# pyright: reportAttributeAccessIssue=false
config.DISABLE_JIT = False

# Unfortunately, specifying the shape of the array in the type hint does not work well
type IntArray2D = npt.NDArray[np.int_]

# Unfortunately, specifying the shape of the array in the type hint does not work well
type IntArray1D = npt.NDArray[np.int_]

type Game = IntArray2D

type Agent = int

type Coalition = int

type CoalitionStructure = IntArray1D

type Weights = IntArray1D

@njit
def lcm_upto(m: int) -> int:
    lcm = 1
    for i in range(2, m + 1):
        lcm = np.lcm(lcm, i)
    return lcm

class Rational(NamedTuple):
    numerator: int
    """Numerator of the rational number"""

    denominator: int
    """Denominator of the rational number"""

@njit
def rational_compare(self: Rational, other: Rational) -> int:
    v1 = self.numerator * other.denominator
    v2 = other.numerator * self.denominator
    return (v1 > v2) - (v1 < v2)

@njit
def rational_to_float(self: Rational) -> float:
    return self.numerator / self.denominator

class Deviation(NamedTuple):
    """A deviation in a coalition structure"""

    ag: Agent
    """Agent performing the deviation"""

    co: Coalition
    """New coalition of the agent"""


@njit
def agent_utility_co(
    game: Game,
    cs: CoalitionStructure,
    ag: Agent,
    co: Coalition,
    weights: Weights | None = None,
) -> tuple[int, int]:
    """
    Compute the utility of the agent ag w.r.t. the coalition co in the given game and coalition structure.

    It returns two values: the sum of the valuations of ag w.r.t. the agents in co and the number of agents in co.
    """
    ut = 0
    size = 0
    for j in range(len(game)):
        if cs[j] == co:
            ut += game[ag, j] if weights is None else weights[int(game[ag, j])]
            size += 1
    return ut, size


@njit
def agent_utility(
    game: Game, cs: CoalitionStructure, ag: Agent, weights: Weights | None = None
) -> tuple[int, int]:
    """
    Compute the utility of the agent ag in the given game.

    It returns two values: the sum of the valuations of ag with the other agents in the same coalition
    and the number of agents in the same coalition as ag.
    """
    return agent_utility_co(game, cs, ag, cs[ag], weights)


@njit
def coalition_social_welfare(
    game: Game, cs: CoalitionStructure, co: Coalition, weights: Weights | None = None
) -> tuple[int, int]:
    """
    Compute the social welfare of the coalition co in the given game and coalition structure.

    It returns two values: the sum of the valuations between agents in co and the number of agents in co.
    """
    agent_count = len(game)
    ut = 0
    size = 0
    for i in range(agent_count):
        if cs[i] == co:
            size += 1
            for j in range(agent_count):
                if cs[j] == co:
                    ut += game[i, j] if weights is None else weights[int(game[i, j])]
    return ut, size


@njit
def social_welfare(
    game: Game, is_fractional: bool, cs: CoalitionStructure, cs_sizes: IntArray1D
) -> float:
    agent_count = len(game)
    sw: float = 0.0
    for i in range(agent_count):
        ut = 0
        co = cs[i]
        for j in range(agent_count):
            if cs[j] == co:
                ut += game[j, i]
        sw += ut / cs_sizes[co] if is_fractional else ut  # type: ignore
    return sw

@njit
def social_welfare_rational(
    game: Game, is_fractional: bool, cs: CoalitionStructure, cs_sizes: IntArray1D, denominator: int
) -> int:
    """
    Compute the social welfare of the given coalition structure in the given game, multiplied by the denominator.
    This should be high enough to avoid eror due to rounding, but low enough to avoid overflow.
    """
    agent_count = len(game)
    sw: int = 0
    for i in range(agent_count):
        ut = 0
        co = cs[i]
        for j in range(agent_count):
            if cs[j] == co:
                ut += game[j, i]
        sw += (ut * denominator) // cs_sizes[co] if is_fractional else ut  # type: ignore
    return sw


@njit
def is_improving_deviation(
    game: Game,
    is_fractional: bool,
    cs: CoalitionStructure,
    cs_sizes: IntArray1D,
    dev: Deviation,
    weights: Weights | None = None,
) -> bool:
    """
    Determine if dev is an improving deviation for the given game and coalition structure.
    """
    ag, co_new = dev
    co_old = cs[ag]
    if co_old == co_new:
        return False
    ut_old = 0
    ut_new = 0
    for j in range(len(game)):
        if cs[j] == co_old:
            ut_old += game[ag, j] if weights is None else weights[int(game[ag, j])]
        elif cs[j] == co_new:
            ut_new += game[ag, j] if weights is None else weights[int(game[ag, j])]

    if not is_fractional:
        return ut_new > ut_old
    elif ut_old == ut_new == 0:
        return cs_sizes[co_new] + 1 < cs_sizes[co_old]
    else:
        return ut_new * cs_sizes[co_old] > ut_old * (cs_sizes[co_new] + 1)


# I tried to rewrite next_improving_deviation in the style of the other iterators (see cs_begin, cs_next)
# but every time this has caused a noticeable decrease in performance.


@njit
def next_improving_deviation(
    game: Game,
    is_fractional: bool,
    cs: CoalitionStructure,
    cs_sizes: IntArray1D,
    max_coalition: int,
    k: int | None,
    weights: Weights | None = None,
    dev: Deviation = Deviation(0, -1),
) -> Deviation | None:
    """
    Return the next improving deviation in the given game and coalition structure, None if there are no more deviations.

    The parameter dev is the last found improving deviation (use default value if you need to find the first
    deviation). Normally, the maximum target coalition in an improving deviation is equal to len(cs_sizes).
    However, the parameter max_coalition may be used to further restrict this value.
    """
    ag, co = dev
    while ag < len(game):
        co += 1
        while co <= max_coalition and co < len(cs_sizes):
            if k is None or cs_sizes[co] < k:
                dev = Deviation(ag, co)
                if is_improving_deviation(
                    game, is_fractional, cs, cs_sizes, dev, weights
                ):
                    return dev
            co += 1
        ag += 1
        co = -1
    return None


@njit
def improving_deviations(
    game: Game,
    is_fractional: bool,
    cs: CoalitionStructure,
    cs_sizes: IntArray1D,
    co_max: int,
    k: int | None,
    weights: Weights | None = None,
) -> Iterator[Deviation]:
    """
    Return a Python iterator of improving deviations for the given game and coalition structure.

    Normally, the maximum target coalition in an improving deviation is equal to len(cs_sizes).
    However, the parameter co_max may be used to further restrict this value.
    """
    dev = next_improving_deviation(
        game, is_fractional, cs, cs_sizes, co_max, k, weights
    )
    while dev is not None:
        # cannot directly yield dev due to limitations of Numba
        yield Deviation(dev.ag, dev.co)
        dev = next_improving_deviation(
            game, is_fractional, cs, cs_sizes, co_max, k, weights, dev
        )


class CoalitionStructureIterator(NamedTuple):
    """An iterator over coalition structures."""

    cs: CoalitionStructure
    """
    The last coalition structure computed by the iterator.
    """

    cs_size: IntArray1D
    """
    The vector of sizes of the coalitions.
    """

    cs_nums: IntArray1D
    """
    The vector of cumulative maximum coalition numbers for each agent, i.e., cs_nums[i] is equal to
    `max(cs[a] for a in range(i))` for i > 1, with the special value `cs_nums[0] = -1`.
    """

    cs_data: IntArray1D
    """
    Additional data for the iterator, i.e., a list whose first (and only) element is the sought number
    of coalitions. We put this information in an array because we need to modify it during the iterations.
    """


# Note the use of the "data" field to store additional information. This is the best solution we have found so far allowing
# functions to change the value of these variables. The problem is that numba does not allow dataclasses to be used.
# Other solutions we tried where:
# - Using a @jitclass, but this is quite slower than the current solution.
# - Using a structref, but this is not supported when JIT is disabled, and it seriously hinders debugging.
# - Using a structured scalar, but this is annoying since these scalars can be used but not generated inside JITTED code.


@njit
def cs_givensize_begin(agent_count: int, size: int) -> CoalitionStructureIterator:
    """
    Build an iterator for coalition structures of a given size.
    """
    return CoalitionStructureIterator(
        np.full(agent_count, -1),
        np.zeros(agent_count, dtype=np.int_),
        np.full(agent_count + 1, -1),
        np.array([size]),
    )


@njit
def cs_givensize_next(cit: CoalitionStructureIterator, k: int | None = None) -> bool:
    """
    Update the iterator with a new coalition structure.

    The function returns False when the iterator has not been updated since there are no more coalition
    structures, otherwise it returns True.
    """
    cs, cs_sizes, cs_nums, cs_data = cit
    agent_count = len(cs)
    ag = 0 if cs[0] == -1 else agent_count - 1
    while True:
        if ag == agent_count:
            return True
        if ag == -1:
            return False
        # `coalitions_potential` is the number of coalitions that can be formed with the remaining agents.
        coalitions_potential = cs_nums[ag] + 1 + (agent_count - ag)
        bot = 0 if coalitions_potential > cs_data[0] else cs_nums[ag] + 1
        top = cs_nums[ag] + 1 if cs_nums[ag] + 1 < cs_data[0] else cs_nums[ag]
        co = cs[ag]
        if co > -1:
            cs_sizes[co] -= 1
        co_new = max(co + 1, bot)
        while co_new <= top:
            if k is None or cs_sizes[co_new] < k:
                break
            co_new += 1
        if co_new <= top:
            cs[ag] = co_new
            cs_sizes[co_new] += 1
            cs_nums[ag + 1] = max(cs_nums[ag], co_new)
            ag += 1
        else:
            cs[ag] = -1
            ag -= 1


@njit
def cs_begin(agent_count: int) -> CoalitionStructureIterator:
    """
    Build an iterator for coalition structures.
    """
    return cs_givensize_begin(agent_count, 1)


@njit
def cs_next(cit: CoalitionStructureIterator, k: int | None) -> bool:
    """
    Update the iterator with a new coalition structure.

    The function returns False when the iterator has not been updated since there are no more coalition
    structures, otherwise it returns True.
    """
    cs, cs_sizes, cs_nums, cs_data = cit
    while cs_data[0] <= len(cs):
        res = cs_givensize_next(cit, k)
        if res:
            return True
        cs_data[0] += 1
        cs.fill(-1)
        cs_nums.fill(-1)
        cs_sizes.fill(0)
    return False


@njit
def css_givensize(
    agent_count: int, size: int, k: int | None = None
) -> Iterator[CoalitionStructure]:
    """
    Return a Python iterator for the coalition structures of the given name and specified size.
    """
    cit = cs_givensize_begin(agent_count, size)
    while cs_givensize_next(cit, k):
        yield np.copy(cit.cs)


@njit
def css(agent_count: int, k: int | None = None) -> Iterator[CoalitionStructure]:
    """
    Return a Python iterator for coalition structures of the given game.
    """
    cit = cs_begin(agent_count)
    while cs_next(cit, k):
        yield np.copy(cit.cs)


@njit
def nash_equilibria(
    game: Game,
    is_fractional: bool = True,
    k: int | None = None,
    weights: Weights | None = None,
) -> Iterator[CoalitionStructure]:
    """
    Return a Python iterator for all Nash equilibria of the given game.
    """
    cit = cs_begin(len(game))
    while cs_next(cit, k):
        cs, cs_sizes, _, cs_data = cit
        res = next_improving_deviation(
            game, is_fractional, cs, cs_sizes, cs_data[0], k, weights
        )
        if res is None:
            yield np.copy(cs)


@njit
def nash_equilibrium(
    game: Game,
    is_fractional: bool = True,
    k: int | None = None,
    weights: Weights | None = None,
) -> CoalitionStructure | None:
    """
    Return the first Nash equilibrium of the given game, if it exists.
    """
    cit = cs_begin(len(game))
    while cs_next(cit, k):
        cs, cs_sizes, _, cs_data = cit
        res = next_improving_deviation(
            game, is_fractional, cs, cs_sizes, cs_data[0], k, weights
        )
        if res is None:
            return cs


class Prices(NamedTuple):
    poa: Rational
    """Price of anarchy"""

    pos: Rational
    """Price of stability"""

    sw_best: int
    """Social welfare of the best coalition structure"""

    cs_best: CoalitionStructure
    """Coalition structure with best social welfare"""

    sw_best_equilibrium: int
    """Social welfare of the best Nash stable coalition structure"""

    cs_best_equilibrium: CoalitionStructure
    """Nash stable coalition structure with best social welfare"""

    sw_worst_equilibrium: int
    """Social welfare of the worst Nash stable coalition structure"""

    cs_worst_equilibrium: CoalitionStructure
    """Nash stable coalition structure with worst social welfare"""


@njit(error_model="numpy")
def poa_pos_rational(
    game: Game, is_fractional: bool = True, k: int | None = None, denominator: int = 1
) -> Prices | None:
    """
    Return the PoA (price of anarchy) and PoS (price of stability) for the given game, and related coalition structures.
    The social welfare is computed with rational numbers, i.e., it is multiplied by the given denominator to avoid errors due to rounding.
    """
    cit = cs_begin(len(game))
    sw_best_equilibrium = -1
    cs_best_equilibrium = np.zeros(0, dtype=np.int_)
    sw_worst_equilibrium = np.iinfo(np.int64).max
    cs_worst_equilibrium = np.zeros(0, dtype=np.int_)
    sw_best = -1
    cs_best = np.zeros(0, dtype=np.int_)
    valid = False
    while cs_next(cit, k):
        cs, cs_sizes, _, cs_data = cit
        sw = social_welfare_rational(game, is_fractional, cs, cs_sizes, denominator)
        if sw > sw_best:
            sw_best = sw
            cs_best = np.copy(cs)
        res = next_improving_deviation(game, is_fractional, cs, cs_sizes, cs_data[0], k)
        if res is None:
            valid = True
            if sw > sw_best_equilibrium:
                sw_best_equilibrium = sw
                cs_best_equilibrium = np.copy(cs)
            if sw < sw_worst_equilibrium:
                sw_worst_equilibrium = sw
                cs_worst_equilibrium = np.copy(cs)
    if valid and sw_worst_equilibrium > 0:
        poa = Rational(sw_best, sw_worst_equilibrium)
        pos = Rational(sw_best, sw_best_equilibrium)
        return Prices(poa, pos, sw_best, cs_best, sw_best_equilibrium, cs_best_equilibrium, sw_worst_equilibrium, cs_worst_equilibrium)
    else:
        return None


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
    Further data, i.e. current value of `m` and position where it has been reached.
    """

    is_symmetric: bool
    """
    Determine whether to restrict the search to symmetric games.
    """

    m_end: int
    """
    Max value of `m` to be considered.
    """

    debug: int
    """
    Debug verbosity. Zero or negative is no debug.
    """


# Constants for the data field of the GameIterator

_SOUGHT_MAX_VALUATION = 0
_REACHED_MAX_VALUATION = 1


@njit
def game_begin(
    agent_count: int,
    is_symmetric: bool = True,
    m_begin: int = 0,
    m_end: int = 1,
    debug: int = 0,
) -> GameIterator:
    """
    Build an iterator over games.
    """
    game = np.zeros((agent_count, agent_count), dtype=np.int_)
    game[agent_count - 1, agent_count - 1] = -1
    if debug > 0:
        print("sought_reward:", m_begin)
        for col in range(1, min(debug, agent_count) + 1):
            print(f"{'  ' * col}[{col}] v: 0")
    return GameIterator(game, np.array([m_begin, -1]), is_symmetric, m_end, debug)


@njit
def game_next(git: GameIterator) -> bool:
    """
    Update the iterator with a new game.

    The function returns False when the iterator has not been updated since there are no more games,
    otherwise it returns True.
    """

    def next_pos(row: int, col: int, agent_count: int) -> tuple[int, int]:
        return (row, col + 1) if col < agent_count - 1 else (row + 1, 0)

    def prev_pos(row: int, col: int, agent_count: int) -> tuple[int, int]:
        return (row, col - 1) if col > 0 else (row - 1, agent_count - 1)

    game, data, is_symmetric, max_valuation, debug = git
    agent_count = len(game)
    pos_final = agent_count * agent_count - 1
    row = agent_count - 1
    col = agent_count - 1
    pos = pos_final
    while data[_SOUGHT_MAX_VALUATION] <= max_valuation:
        while row >= 0:
            # Checks in line 2 and 3 of the following code are used to remove graphs that are isomorphic
            # to other graphs found in other iterations. They are actually not needed, since the check later
            # on the code will subsume them, but they are kept because they make the execution faster.

            bot = (
                game[col][row]
                if is_symmetric and row > col
                else game[row][col - 1]
                if row == 0 and col > 0
                else game[0][1]
                if row > 0 and row != col
                else 0
            )
            top = (
                0
                if row == col
                else game[col][row]
                if is_symmetric and row > col
                else data[_SOUGHT_MAX_VALUATION]
            )

            v = game[row][col]
            v_new = max(v + 1, bot)

            if v_new <= top:
                game[row][col] = v_new

                # ISOMORPHISM CHECK
                # Codish et al, Constraints for symmetry breaking in graph representation, Constraints 24 (2019)
                is_invalid_graph = False
                if row > 0 and col == agent_count - 1:
                    for i in range(0, row):
                        if i == row - 2:
                            continue
                        for j in range(0, agent_count):
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
                        print(f"{'  ' * col}[{col}] v: {v_new}")
                    if (
                        v_new == data[_SOUGHT_MAX_VALUATION]
                        and data[_REACHED_MAX_VALUATION] == -1
                    ):
                        data[_REACHED_MAX_VALUATION] = pos
                    if pos == pos_final:
                        if data[_REACHED_MAX_VALUATION] != -1:
                            return True
                    else:
                        row, col = next_pos(row, col, agent_count)
                        pos += 1
            elif v_new > top:
                game[row][col] = -1
                if data[_REACHED_MAX_VALUATION] == pos:
                    data[_REACHED_MAX_VALUATION] = -1
                row, col = prev_pos(row, col, agent_count)
                pos -= 1

        data[_SOUGHT_MAX_VALUATION] += 1
        if debug > 0 and data[_SOUGHT_MAX_VALUATION] <= max_valuation:
            print("sought_reward:", data[_SOUGHT_MAX_VALUATION])
        row = 0
        pos = 0
        col = 0
    return False


@njit
def game_next_unstable(
    git: GameIterator,
    is_fractional: bool = True,
    k: int | None = None,
    weights: Weights | None = None,
) -> bool:
    """
    Update the iterator with a new game with no Nash stable coalition structures.

    The function returns False when the iterator has not been updated since there are no more games,
    otherwise it returns True.
    """
    while game_next(git):
        if nash_equilibrium(git.game, is_fractional, k, weights) is None:
            return True
    return False


@njit
def games(
    agent_count: int, is_symmetric: bool = True, m_begin: int = 0, m_end: int = 1
) -> Iterator[Game]:
    """
    Return a Python iterator over games.
    """
    git = game_begin(agent_count, is_symmetric, m_begin, m_end)
    while game_next(git):
        yield np.copy(git.game)


@njit
def unstable_games(
    agent_count: int,
    is_symmetric: bool = True,
    m_begin: int = 0,
    m_end: int = 1,
    k: int | None = None,
    is_fractional: bool = True,
    weights: Weights | None = None,
    debug: int = 0,
) -> Iterator[Game]:
    """
    Return a Python iterator over games without a Nash stable coalition structure.
    """
    git = game_begin(agent_count, is_symmetric, m_begin, m_end, debug)
    while game_next_unstable(git, is_fractional, k, weights):
        yield np.copy(git.game)


@njit
def count_games(
    agent_count: int,
    is_symmetric: bool = True,
    m_begin: int = 0,
    m_end: int = 1,
    debug: int = 0,
) -> int:
    """
    Count the number of games generated by our procedure.

    This is the same value as the second element of the tuple returned by count_unstable_games.
    """
    git = game_begin(agent_count, is_symmetric, m_begin, m_end, debug)
    count_total = 0
    while game_next(git):
        count_total += 1
    return count_total


class GameCounts(NamedTuple):
    """
    A named tuple to hold the counts of games.
    """

    count_total: int
    """
    Number of games generated by our procedure.
    """
    count_noequilibrium: int
    """
    Number of games without a Nash stable coalition structure.
    """
    example_noequilibrium: Game
    """
    An example of a game without a Nash stable coalition structure, or None if there are no such games.
    """


@njit(cache=True)
def count_unstable_games(
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
    Count the number of games without a Nash stable coalition structure.

    The first returned value is the number of games without a Nash stable coalition structure, while the second value
    is the total number of games considered.
    """
    git = game_begin(agent_count, is_symmetric, m_begin, m_end, debug)
    count_total = 0
    count_noequilibrium = 0
    example_noequilibrium = np.zeros((0, 0), dtype=np.int_)
    while game_next(git):
        count_total += 1
        if nash_equilibrium(git.game, is_fractional, k, weights) is None:
            if count_noequilibrium == 0:
                example_noequilibrium = np.copy(git.game)
                if debug > 0:
                    print(example_noequilibrium)
            count_noequilibrium += 1
    return GameCounts(count_total, count_noequilibrium, example_noequilibrium)


class GamePrices(NamedTuple):
    """A named tuple to hold the prices of anarchy and stability for a game, and related information."""

    total_game_count: int
    """Total number of games considered."""
    poa_highest: Prices
    """Price of anarchy and related coalition structures for the game with the highest price of anarchy."""
    poa_highest_count: int
    """Number of games with the highest price of anarchy."""
    poa_highest_game: Game
    """A game with the highest price of anarchy."""
    poa_lowest: Prices
    """Price of anarchy and related coalition structures for the game with the lowest price of anarchy."""
    poa_lowest_count: int
    """Number of games with the lowest price of anarchy."""
    poa_lowest_game: Game
    """A game with the lowest price of anarchy."""
    pos_highest: Prices
    """Price of stability and related coalition structures for the game with the highest price of stability."""
    pos_highest_count: int
    """Number of games with the highest price of stability."""
    pos_highest_game: Game
    """A game with the highest price of stability."""
    pos_lowest: Prices
    """Price of stability and related coalition structures for the game with the lowest price of stability."""
    pos_lowest_count: int
    pos_lowest_game: Game
    """A game with the lowest price of stability."""
    poa_avg: float
    """The average price of anarchy across all games."""
    pos_avg: float
    """The average price of stability across all games."""


@njit(cache=True)
def compute_poa_pos(
    agent_count: int,
    is_symmetric: bool = True,
    m_begin: int = 0,
    m_end: int = 1,
    k: int | None = None,
    is_fractional: bool = True,
    weights: Weights | None = None,
    debug: int = 0,
) -> GamePrices | None:
    if weights is not None:
        raise NotImplementedError(
            "The function compute_poa_pos does not support weights yet."
        )
    denominator = lcm_upto(agent_count) if is_fractional else 1
    maxint = np.iinfo(np.int64).max
    git = game_begin(agent_count, is_symmetric, m_begin, m_end, debug)
    poa_lowest_val = Rational(maxint // denominator, 1)
    poa_sum_val = 0.0
    poa_highest_val = Rational(-1, 1)
    pos_lowest_val = Rational(maxint // denominator, 1)
    pos_sum_val = 0.0
    pos_highest_val = Rational(-1, 1)
    poa_lowest_game = poa_highest_game = pos_lowest_game = pos_highest_game = np.zeros(
        (0, 0), dtype=np.int_
    )
    poa_lowest = poa_highest = pos_lowest = pos_highest = Prices(
        Rational(0, 1),
        Rational(0, 1),
        -1,
        np.zeros(0, dtype=np.int_),
        np.iinfo(np.int64).max,
        np.zeros(0, dtype=np.int_),
        -1,
        np.zeros(0, dtype=np.int_),
    )
    pos_lowest_count = pos_highest_count = poa_lowest_count = poa_highest_count = 0
    count = 0
    valid_count = 0
    while game_next(git):
        count += 1
        prices = poa_pos_rational(git.game, is_fractional, k, denominator)
        if prices is None:
            continue
        valid_count += 1
        poa = prices.poa
        pos = prices.pos
        poa_sum_val += rational_to_float(poa)
        pos_sum_val += rational_to_float(pos)
        compare_poa = rational_compare(poa, poa_highest_val)
        if compare_poa > 0:
            poa_highest_val = poa
            poa_highest_count = 1
            # Need to rebuild prices due to limitations of Numba
            poa_highest = Prices(
                poa,
                pos,
                prices.sw_best,
                prices.cs_best,
                prices.sw_best_equilibrium,
                prices.cs_best_equilibrium,
                prices.sw_worst_equilibrium,
                prices.cs_worst_equilibrium,
            )
            poa_highest_game = np.copy(git.game)
        elif compare_poa == 0:
            poa_highest_count += 1
        compare_poa = rational_compare(poa, poa_lowest_val)
        if compare_poa < 0:
            poa_lowest_val = poa
            poa_lowest_count = 1
            poa_lowest = Prices(
                poa,
                pos,
                prices.sw_best,
                prices.cs_best,
                prices.sw_best_equilibrium,
                prices.cs_best_equilibrium,
                prices.sw_worst_equilibrium,
                prices.cs_worst_equilibrium,
            )
            poa_lowest_game = np.copy(git.game)
        elif compare_poa == 0:
            poa_lowest_count += 1
        compare_pos = rational_compare(pos, pos_highest_val)
        if compare_pos > 0:
            pos_highest_val = pos
            pos_highest_count = 1
            pos_highest = Prices(
                poa,
                pos,
                prices.sw_best,
                prices.cs_best,
                prices.sw_best_equilibrium,
                prices.cs_best_equilibrium,
                prices.sw_worst_equilibrium,
                prices.cs_worst_equilibrium,

            )
            pos_highest_game = np.copy(git.game)
        elif compare_pos == 0:
            pos_highest_count += 1
        compare_pos = rational_compare(pos, pos_lowest_val)
        if compare_pos < 0:
            pos_lowest_val = pos
            pos_lowest_count = 1
            pos_lowest = Prices(
                poa,
                pos,
                prices.sw_best,
                prices.cs_best,
                prices.sw_best_equilibrium,
                prices.cs_best_equilibrium,
                prices.sw_worst_equilibrium,
                prices.cs_worst_equilibrium,
            )
            pos_lowest_game = np.copy(git.game)
        elif compare_pos == 0:
            pos_lowest_count += 1
    return (
        GamePrices(
            count,
            poa_highest,
            poa_highest_count,
            poa_highest_game,
            poa_lowest,
            poa_lowest_count,
            poa_lowest_game,
            pos_highest,
            pos_highest_count,
            pos_highest_game,
            pos_lowest,
            pos_lowest_count,
            pos_lowest_game,
            poa_sum_val / valid_count,
            pos_sum_val / valid_count,
        )
        if valid_count > 0
        else None
    )
