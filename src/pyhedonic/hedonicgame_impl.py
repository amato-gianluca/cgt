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
    - it should be at most max(cs)+1, where max(cs) is the maximum coalition number in cs
- dev -- a deviation, i.e., a pair `(ag, co)`
- weights -- a vector mapping evaluations in `game` to a different scale;
    - None means that the original valuations are used
- m_begin -- the initial maximum valuation when enumerating games
- m_end -- the final maximum valuation when enumerating games
- debug -- debug verbosity: zero or negative is no debug
"""

from typing import Iterator, NamedTuple

import numpy as np
from numba import config, njit, prange

# pyright: reportAttributeAccessIssue=false
config.DISABLE_JIT = False

# Unfortunately, specifying the shape of the array in the type hint does not work well
type IntArray2D = np.typing.NDArray[np.int_]

# Unfortunately, specifying the shape of the array in the type hint does not work well
type IntArray1D = np.typing.NDArray[np.int_]

type Game = IntArray2D

type Agent = int

type Coalition = int

type CoalitionStructure = IntArray1D

type Weights = IntArray1D


@njit
def lcm_upto(m: int) -> int:
    """
    Compute the least common multiple of the natural numbers from 1 to m.

    This is used when converting fractional games to integer games.
    """
    lcm = 1
    for i in range(2, m + 1):
        lcm = np.lcm(lcm, i)
    return lcm


class Rational(NamedTuple):
    """
    A rational number, represented as a pair of integers (numerator and denominator).

    Positive and negative infinity may be represented as a positive or negative numerator and a zero
    denominator. However, NaN's are not supported.
    """

    numerator: int
    """
    Numerator of the rational number.
    """

    denominator: int
    """
    Denominator of the rational number.
    """


@njit
def rational_compare(self: Rational, other: Rational) -> int:
    """
    Compare two rational numbers.

    Return a positive value if self > other, a negative value if self < other, and zero if self ==
    other.
    """
    v1 = self.numerator * other.denominator
    v2 = other.numerator * self.denominator
    return int(v1 > v2) - int(v1 < v2)


@njit
def rational_to_float(self: Rational) -> float:
    """
    Convert a rational number to a float.

    Rounding errors may occur.
    """
    return self.numerator / self.denominator


class AgentUtility(NamedTuple):
    """
    A dataclass to store the utility of an agent in a fractional game.

    It contains the sum of the valuations and the size of the coalition of the agent.
    """

    value: int
    """
    The sum of the valuations.
    """

    size: int
    """
    The size of the coalition of the agent.
    """


@njit
def fau_lt(ut1: AgentUtility, ut2: AgentUtility, is_fractional: bool) -> bool:
    """
    Compare the utility with another utility.

    The comparison is done by comparing the values of the utilities, after converting them to
    fractions.
    """
    if is_fractional:
        return ut1.value < ut2.value
    elif ut1.value == ut2.value == 0:
        return ut1.size > ut2.size
    else:
        return ut1.value * ut2.size < ut2.value * ut1.size


class Deviation(NamedTuple):
    """
    A deviation in a coalition structure.
    """

    ag: Agent
    """
    Agent performing the deviation.
    """

    co: Coalition
    """
    New coalition of the agent.
    """


@njit
def agent_utility_co(
    game: Game,
    cs: CoalitionStructure,
    ag: Agent,
    co: Coalition,
) -> AgentUtility:
    """
    Compute the utility of the agent ag w.r.t.

    the coalition co in the given game and coalition structure.

    It returns two values: the sum of the valuations of ag w.r.t. the agents in co and
    the number of agents in co (including ag if not already in co).
    """
    ut = 0
    size = 0
    for j in range(len(game)):
        if cs[j] == co:
            ut += game[ag, j]
            size += 1
    if cs[ag] != co:
        size += 1
    return AgentUtility(ut, size)


@njit
def agent_utility(game: Game, cs: CoalitionStructure, ag: Agent) -> AgentUtility:
    """
    Compute the utility of the agent ag in the given game.

    It returns two values: the sum of the valuations of ag with the other agents in the
    same coalition and the number of agents in the same coalition as ag.
    """
    return agent_utility_co(game, cs, ag, cs[ag])


@njit
def coalition_social_welfare(game: Game, cs: CoalitionStructure, co: Coalition) -> Rational:
    """
    Compute the social welfare of the coalition co in the given game and coalition structure.

    It returns two values: the sum of the valuations between agents in co and the
    number of agents in co.
    """
    agent_count = len(game)
    ut = 0
    size = 0
    for i in range(agent_count):
        if cs[i] == co:
            size += 1
            for j in range(agent_count):
                if cs[j] == co:
                    ut += game[i, j]
    return Rational(ut, size)


@njit
def social_welfare(
    game: Game, is_fractional: bool, cs: CoalitionStructure, cs_sizes: IntArray1D
) -> float:
    """
    Compute the social welfare of the given coalition structure in the given game.
    """
    agent_count = len(game)
    sw = 0.0
    for i in range(agent_count):
        ut = 0
        co: int = cs[i]
        for j in range(agent_count):
            if cs[j] == co:
                ut += game[i, j]
        sw += ut / cs_sizes[co] if is_fractional else ut
    return sw


@njit
def social_welfare_integer(
    game: Game,
    is_fractional: bool,
    cs: CoalitionStructure,
    cs_sizes: IntArray1D,
) -> int:
    """
    Compute the social welfare of the given coalition structure in the given game, rounded to an
    integer value.
    """
    agent_count = len(game)
    sw = 0
    for i in range(agent_count):
        ut = 0
        co: int = cs[i]
        for j in range(agent_count):
            if cs[j] == co:
                ut += game[j, i]
        sw += ut // cs_sizes[co] if is_fractional else ut
    return sw


@njit
def is_improving_deviation(
    game: Game,
    is_fractional: bool,
    cs: CoalitionStructure,
    cs_sizes: IntArray1D,
    dev: Deviation,
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
            ut_old += game[ag, j]
        elif cs[j] == co_new:
            ut_new += game[ag, j]

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
    co_max: int,
    k: int | None,
    dev: Deviation = Deviation(0, -1),
) -> Deviation | None:
    """
    Return the next improving deviation in the given game and coalition structure, None if there are
    no more deviations.

    The parameter dev is the last found improving deviation (use default value if you need to find
    the first deviation). Normally, the maximum target coalition in an improving deviation is equal
    to max(cs)+1. However, the parameter max_coalition may be used to further restrict this value.
    """
    ag, co = dev
    while ag < len(game):
        co += 1
        while co <= co_max and co < len(cs_sizes):
            if k is None or cs_sizes[co] < k:
                dev = Deviation(ag, co)
                if is_improving_deviation(game, is_fractional, cs, cs_sizes, dev):
                    return dev
            co += 1
        ag += 1
        co = -1
    return None


def improving_deviations(
    game: Game,
    is_fractional: bool,
    cs: CoalitionStructure,
    *,
    k: int | None = None,
    cs_sizes: IntArray1D | None = None,
    co_max: int | None = None,
) -> Iterator[Deviation]:
    """
    Return a Python iterator of improving deviations for the given game and coalition structure.

    Normally, the maximum target coalition in an improving deviation is equal to max(cs_sizes)+1.
    However, the parameter co_max may be used to further restrict this value.
    """
    cs_sizes_real = cs_sizes if cs_sizes is not None else np.bincount(cs, minlength=len(cs))
    co_max_real = co_max if co_max is not None else max(cs) + 1
    dev = next_improving_deviation(game, is_fractional, cs, cs_sizes_real, co_max_real, k)
    while dev is not None:
        # cannot directly yield dev due to limitations of Numba
        yield Deviation(dev.ag, dev.co)
        dev = next_improving_deviation(game, is_fractional, cs, cs_sizes_real, co_max_real, k, dev)


@njit
def next_best_improving_deviation(
    game: Game,
    is_fractional: bool,
    cs: CoalitionStructure,
    cs_sizes: IntArray1D,
    co_max: int,
    k: int | None,
    dev: Deviation = Deviation(0, -1),
    maxut: AgentUtility = AgentUtility(-1, 1),
) -> tuple[Deviation, AgentUtility] | None:
    """
    Return the next best improving deviation in the given game and coalition structure, None if
    there are no more deviations.

    Normally, the maximum target coalition in an improving deviation is equal to max(cs_sizes)+1.
    However, the parameter co_max may be used to further restrict this value.
    """
    ag, co = dev
    while ag < len(game):
        if maxut == AgentUtility(-1, 1):
            for candidate_co in range(co + 1, min(co_max + 1, len(cs_sizes))):
                if is_improving_deviation(
                    game, is_fractional, cs, cs_sizes, Deviation(ag, candidate_co)
                ):
                    ut = agent_utility_co(game, cs, ag, candidate_co)
                    if fau_lt(maxut, ut, is_fractional):
                        maxut = ut
        co += 1
        while co <= co_max and co < len(cs_sizes):
            if k is None or cs_sizes[co] < k:
                dev = Deviation(ag, co)
                if is_improving_deviation(game, is_fractional, cs, cs_sizes, dev):
                    ut = agent_utility_co(game, cs, ag, co)
                    if ut == maxut:
                        return dev, ut
            co += 1
        ag += 1
        maxut = AgentUtility(-1, 1)
        co = -1
    return None


def best_improving_deviations(
    game: Game,
    is_fractional: bool,
    cs: CoalitionStructure,
    *,
    k: int | None = None,
    cs_sizes: IntArray1D | None = None,
    co_max: int | None = None,
) -> Iterator[Deviation]:
    """
    Return a Python iterator of improving deviations for the given game and coalition structure.

    Normally, the maximum target coalition in an improving deviation is equal to max(cs_sizes)+1.
    However, the parameter co_max may be used to further restrict this value.
    """
    cs_sizes_real = cs_sizes if cs_sizes is not None else np.bincount(cs, minlength=len(cs))
    co_max_real = co_max if co_max is not None else max(cs) + 1
    res = next_best_improving_deviation(game, is_fractional, cs, cs_sizes_real, co_max_real, k)
    while res is not None:
        dev, ut = res
        # cannot directly yield dev due to limitations of Numba
        yield Deviation(dev.ag, dev.co)
        res = next_best_improving_deviation(
            game, is_fractional, cs, cs_sizes_real, co_max_real, k, dev, ut
        )


class CoalitionStructureIterator(NamedTuple):
    """
    An iterator over coalition structures.
    """

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
    The vector of cumulative maximum coalition numbers for each agent, i.e., cs_nums[i]
    is equal to `max(cs[a] for a in range(i))` for i > 1, with the special value
    `cs_nums[0] = -1`.
    """

    cs_data: IntArray1D
    """
    Additional data for the iterator, i.e., a list whose first (and only) element is the sought
    number of coalitions.

    We put this information in an array because we need to modify it during the iterations.
    """


# Note the use of the "data" field to store additional information. This is the best
# solution we have found so far allowing functions to change the value of these
# variables. The problem is that numba does not allow dataclasses to be used. Other
# solutions we tried where:
# - Using a @jitclass, but this is quite slower than the current solution.
# - Using a structref, but this is not supported when JIT is disabled, and it seriously
#   hinders debugging.
# - Using a structured scalar, but this is annoying since these scalars can be used but
#   not generated inside jitted code.


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

    The function returns False when the iterator has not been updated since there are no more
    coalition structures, otherwise it returns True.
    """
    cs, cs_sizes, cs_nums, cs_data = cit
    agent_count = len(cs)
    ag = 0 if cs[0] == -1 else agent_count - 1
    while True:
        if ag == agent_count:
            return True
        if ag == -1:
            return False
        # `coalitions_potential` is the number of coalitions that can be formed with
        # the remaining agents.
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

    The function returns False when the iterator has not been updated since there are no more
    coalition structures, otherwise it returns True.
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
    game: Game, is_fractional: bool = True, k: int | None = None
) -> Iterator[CoalitionStructure]:
    """
    Return a Python iterator for all Nash equilibria of the given game.
    """
    cit = cs_begin(len(game))
    while cs_next(cit, k):
        cs, cs_sizes, _, cs_data = cit
        res = next_improving_deviation(game, is_fractional, cs, cs_sizes, cs_data[0], k)
        if res is None:
            yield np.copy(cs)


@njit
def nash_equilibrium(
    game: Game,
    is_fractional: bool = True,
    k: int | None = None,
) -> CoalitionStructure | None:
    """
    Return the first Nash equilibrium of the given game, if it exists.
    """
    cit = cs_begin(len(game))
    while cs_next(cit, k):
        cs, cs_sizes, _, cs_data = cit
        res = next_improving_deviation(game, is_fractional, cs, cs_sizes, cs_data[0], k)
        if res is None:
            return cs


class GamePrices(NamedTuple):
    """
    A named tuple which holds the best social welfare, the best social welfare of a Nash
    equilibrium, and the worst social welfare of a Nash equilibrium, together with examples of
    coalition structures where such values are achieved.

    The social welfare values are assumed to be integer values, even for fractional games. This can
    be achieved by multiplying the valuations in the game by an appropriate factor.
    """

    sw_best: int
    """
    Social welfare of the best coalition structure.
    """

    cs_best: CoalitionStructure
    """
    Coalition structure with best social welfare.
    """

    sw_best_equilibrium: int
    """
    Social welfare of the best Nash stable coalition structure.
    """

    cs_best_equilibrium: CoalitionStructure
    """
    Nash stable coalition structure with best social welfare.
    """

    sw_worst_equilibrium: int
    """
    Social welfare of the worst Nash stable coalition structure.
    """

    cs_worst_equilibrium: CoalitionStructure
    """
    Nash stable coalition structure with worst social welfare.
    """


@njit
def game_prices_copy(gi: GamePrices) -> GamePrices:
    """
    Copy a GameInfo named tuple.
    """
    return GamePrices(
        gi.sw_best,
        gi.cs_best,
        gi.sw_best_equilibrium,
        gi.cs_best_equilibrium,
        gi.sw_worst_equilibrium,
        gi.cs_worst_equilibrium,
    )


@njit
def game_prices_dummy() -> GamePrices:
    """
    A dummy GameInfo structure to accomodate Numba typing inference.

    The values in this structure are not meaningful.
    """
    return GamePrices(
        -1,
        np.zeros(0, dtype=np.int_),
        np.iinfo(np.int64).max,
        np.zeros(0, dtype=np.int_),
        -1,
        np.zeros(0, dtype=np.int_),
    )


@njit
def game_prices_compute(
    game: Game, is_fractional: bool = True, k: int | None = None
) -> GamePrices | None:
    """
    Return information on the prices for the given game, or None if the game as no Nash stable
    coalition structure.

    An error may occur if the social welfare computed for some coalition structure exceeds the
    maximum value of an np.int64.
    """
    cit = cs_begin(len(game))
    sw_best_equilibrium = -1
    cs_best_equilibrium = np.zeros_like(cit.cs)
    sw_worst_equilibrium = np.iinfo(np.int64).max
    cs_worst_equilibrium = np.zeros_like(cit.cs)
    sw_best = -1
    cs_best = np.zeros_like(cit.cs)
    valid = False
    while cs_next(cit, k):
        cs, cs_sizes, _, cs_data = cit
        sw = social_welfare_integer(game, is_fractional, cs, cs_sizes)
        if sw > sw_best:
            sw_best = sw
            cs_best[:] = cs
        res = next_improving_deviation(game, is_fractional, cs, cs_sizes, cs_data[0], k)
        if res is None:
            valid = True
            if sw > sw_best_equilibrium:
                sw_best_equilibrium = sw
                cs_best_equilibrium[:] = cs
            if sw < sw_worst_equilibrium:
                sw_worst_equilibrium = sw
                cs_worst_equilibrium[:] = cs
    return (
        GamePrices(
            sw_best,
            cs_best,
            sw_best_equilibrium,
            cs_best_equilibrium,
            sw_worst_equilibrium,
            cs_worst_equilibrium,
        )
        if valid
        else None
    )


class GameIterator(NamedTuple):
    """
    An internal iterator over games.
    """

    game_internal: Game
    """
    The last game computed by the iterator, without considering weights.
    """

    game: Game
    """
    The last game computed by the iterator, considering weights.
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

    weights: Weights
    """
    Weights for the valuations in the game.

    An empty array means that the original valuations are used and that game is an alias for
    game_internal. We cannot use Weights | None as type for limitations of the numba type checker.
    """

    debug: int
    """
    Debug verbosity.

    Zero or negative is no debug.
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
    weights: Weights | None = None,
    debug: int = 0,
) -> GameIterator:
    """
    Build an iterator over games.
    """
    if weights is not None and len(weights) < m_end + 1:
        raise ValueError("Weights should have length at least m_end + 1")
    game_internal = np.zeros((agent_count, agent_count), dtype=np.int_)
    game_internal[agent_count - 1, agent_count - 1] = -1
    game = game_internal if weights is None else np.zeros_like(game_internal)
    if debug > 0:
        print("sought_reward:", m_begin)
        for col in range(1, min(debug, agent_count) + 1):
            print(f"{'  ' * col}[{col}] v: 0")
    return GameIterator(
        game_internal,
        game,
        np.array([m_begin, -1]),
        is_symmetric,
        m_end,
        weights if weights is not None else np.zeros(0, dtype=np.int_),
        debug,
    )


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

    game_internal, game, data, is_symmetric, max_valuation, weights, debug = git
    agent_count = len(game_internal)
    pos_final = agent_count * agent_count - 1
    row = agent_count - 1
    col = agent_count - 1
    pos = pos_final
    while data[_SOUGHT_MAX_VALUATION] <= max_valuation:
        while row >= 0:
            # Checks in line 2 and 3 of the following code are used to remove graphs
            # that are isomorphic to other graphs found in other iterations. They are
            # actually not needed, since the check later on the code will subsume them,
            # but they are kept because they make the execution faster.

            bot = (
                game_internal[col][row]
                if is_symmetric and row > col
                else game_internal[row][col - 1]
                if row == 0 and col > 0
                else game_internal[0][1]
                if row > 0 and row != col
                else 0
            )
            top = (
                0
                if row == col
                else game_internal[col][row]
                if is_symmetric and row > col
                else data[_SOUGHT_MAX_VALUATION]
            )

            v = game_internal[row][col]
            v_new = max(v + 1, bot)

            if v_new <= top:
                game_internal[row][col] = v_new

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
                            if game_internal[i, j] == game_internal[row, j]:
                                continue
                            if game_internal[i, j] > game_internal[row, j]:
                                is_invalid_graph = True
                            break
                        if is_invalid_graph:
                            break

                if not is_invalid_graph:
                    if debug > 0 and row == 0 and 0 < col <= debug:
                        print(f"{'  ' * col}[{col}] v: {v_new}")
                    if v_new == data[_SOUGHT_MAX_VALUATION] and data[_REACHED_MAX_VALUATION] == -1:
                        data[_REACHED_MAX_VALUATION] = pos
                    if pos == pos_final:
                        if data[_REACHED_MAX_VALUATION] != -1:
                            if len(weights) > 0:
                                for i in range(agent_count):
                                    for j in range(agent_count):
                                        game[i, j] = weights[game_internal[i, j]]
                            return True
                    else:
                        row, col = next_pos(row, col, agent_count)
                        pos += 1
            elif v_new > top:
                game_internal[row][col] = -1
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
) -> bool:
    """
    Update the iterator with a new game with no Nash stable coalition structures.

    The function returns False when the iterator has not been updated since there are no more games,
    otherwise it returns True.
    """
    while game_next(git):
        if nash_equilibrium(git.game, is_fractional, k) is None:
            return True
    return False


@njit
def games(
    agent_count: int,
    is_symmetric: bool = True,
    m_begin: int = 0,
    m_end: int = 1,
    weights: Weights | None = None,
    debug: int = 0,
) -> Iterator[Game]:
    """
    Return a Python iterator over games.
    """
    git = game_begin(agent_count, is_symmetric, m_begin, m_end, weights, debug)
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
    git = game_begin(agent_count, is_symmetric, m_begin, m_end, weights, debug)
    while game_next_unstable(git, is_fractional, k):
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

    This is the same value as the count_total field returned by count_unstable_games.
    """
    git = game_begin(agent_count, is_symmetric, m_begin, m_end, None, debug)
    count_total = 0
    while game_next(git):
        count_total += 1
    return count_total


class GameCollectionCounts(NamedTuple):
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
    An example of a game without a Nash stable coalition structure.

    This is only meaningful if count_noequilibrium is greater than zero, otherwise it is a dummy
    value. We cannot use None as type for limitations of the numba type checker.
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
) -> GameCollectionCounts:
    """
    Count the number of games without a Nash stable coalition structure.

    The returned named tuple contains the total number of games considered, the number of games
    without a Nash stable coalition structure, and an example of such a game when one exists.
    """
    git = game_begin(agent_count, is_symmetric, m_begin, m_end, weights, debug)
    count_total = 0
    count_noequilibrium = 0
    example_noequilibrium = np.zeros_like(git.game)
    while game_next(git):
        count_total += 1
        if nash_equilibrium(git.game, is_fractional, k) is None:
            if count_noequilibrium == 0:
                example_noequilibrium[:] = git.game
                if debug > 0:
                    print(example_noequilibrium)
            count_noequilibrium += 1
    return GameCollectionCounts(count_total, count_noequilibrium, example_noequilibrium)


@njit(parallel=True, cache=True)
def count_unstable_games_from_collection(
    games: list[Game],
    k: int | None = None,
    is_fractional: bool = True,
) -> GameCollectionCounts:
    """
    Count the number of games without a Nash stable coalition structure from a given collection of games.

    The returned named tuple contains the total number of games considered, the number of games
    without a Nash stable coalition structure, and an example of such a game when one exists.
    """
    count_noequilibrium = 0
    n = len(games)
    mask = np.zeros(n, dtype=np.bool_)
    for i in prange(n):
        if nash_equilibrium(games[i], is_fractional, k) is None:
            mask[i] = True

    count_noequilibrium = 0
    example_noequilibrium = np.zeros((0, 0), dtype=np.int_)
    for i in range(n):
        if mask[i]:
            count_noequilibrium += 1
            if example_noequilibrium.size == 0:
                example_noequilibrium = games[i]

    return GameCollectionCounts(n, count_noequilibrium, example_noequilibrium)


class GameCollectionPrices(NamedTuple):
    """
    A named tuple to hold the extremal values for the prices of anarchy and stability in a set of
    games.
    """

    poa_highest: Rational
    """
    The highest price of anarchy across all games.
    """

    poa_highest_count: int
    """
    Number of games with the highest price of anarchy.
    """

    poa_highest_game: Game
    """
    A game with the highest price of anarchy.
    """

    poa_highest_info: GamePrices
    """
    Price of anarchy and related coalition structures for the game with the highest price of
    anarchy.
    """

    poa_lowest: Rational
    """
    The lowest price of anarchy across all games.
    """

    poa_lowest_count: int
    """
    Number of games with the lowest price of anarchy.
    """

    poa_lowest_game: Game
    """
    A game with the lowest price of anarchy.
    """

    poa_lowest_info: GamePrices
    """
    Price of anarchy and related coalition structures for the game with the lowest price of anarchy.
    """

    pos_highest: Rational
    """
    The highest price of stability across all games.
    """

    pos_highest_count: int
    """
    Number of games with the highest price of stability.
    """

    pos_highest_game: Game
    """
    A game with the highest price of stability.
    """

    pos_highest_info: GamePrices
    """
    Price of stability and related coalition structures for the game with the highest price of
    stability.
    """

    pos_lowest: Rational
    """
    The lowest price of stability across all games.
    """

    pos_lowest_count: int
    """
    Number of games with the lowest price of stability.
    """

    pos_lowest_game: Game
    """
    A game with the lowest price of stability.
    """

    pos_lowest_info: GamePrices
    """
    Price of stability and related coalition structures for the game with the lowest price of
    stability.
    """

    poa_avg: float
    """
    The average price of anarchy across all games.
    """

    pos_avg: float
    """
    The average price of stability across all games.
    """


class GameCollectionInfo(NamedTuple):
    """
    A named tuple to hold informations on a set of games.
    """

    counts: GameCollectionCounts | None
    """
    Information on the number of games withtout Nash stable coalition structures.
    """

    prices: GameCollectionPrices | None
    """
    Information on the extremal values for the prices of anarchy and stability.
    """


@njit(cache=True)
def game_collection_info(
    agent_count: int,
    is_symmetric: bool = True,
    m_begin: int = 0,
    m_end: int = 1,
    k: int | None = None,
    is_fractional: bool = True,
    weights: Weights | None = None,
    debug: int = 0,
) -> GameCollectionInfo:
    """
    Count the number of games without a Nash stable coalition structure, together with the extremal
    values of the price of anarchy and price of stability.
    """
    denominator = (
        1 if not is_fractional else lcm_upto(k) if k is not None else lcm_upto(agent_count)
    )
    git = game_begin(agent_count, is_symmetric, m_begin, m_end, weights, debug)
    game = git.game
    scaled_game = game if denominator == 1 else np.zeros_like(game)
    # data for counting information on the collection of games
    total_count = 0
    noequilibrium_count = 0
    noequilibrium_game = np.zeros_like(game)
    # data for pricining information on the collection of games
    poa_highest = Rational(-1, 1)
    poa_lowest = Rational(1, 0)
    pos_highest = Rational(-1, 1)
    pos_lowest = Rational(1, 0)
    pos_lowest_count = pos_highest_count = poa_lowest_count = poa_highest_count = 0
    poa_lowest_game = np.zeros_like(game)
    poa_highest_game = np.zeros_like(game)
    pos_lowest_game = np.zeros_like(game)
    pos_highest_game = np.zeros_like(game)
    poa_lowest_info = poa_highest_info = pos_lowest_info = pos_highest_info = game_prices_dummy()
    poa_sum_val = pos_sum_val = 0.0
    valid_count = 0
    while game_next(git):
        total_count += 1
        if denominator != 1:
            scaled_game[:] = game * denominator
        game_prices = game_prices_compute(scaled_game, is_fractional, k)
        # game with no Nash stable coalition structure
        if game_prices is None:
            noequilibrium_count += 1
            noequilibrium_game[:] = game
            continue
        # game with no valid price of anarchy or price of stability (i.e., best social welfare is zero)
        if game_prices.sw_best == 0:
            continue
        valid_count += 1
        poa = Rational(game_prices.sw_best, game_prices.sw_worst_equilibrium)
        pos = Rational(game_prices.sw_best, game_prices.sw_best_equilibrium)
        poa_sum_val += rational_to_float(poa)
        pos_sum_val += rational_to_float(pos)
        compare_poa = rational_compare(poa, poa_highest)
        if compare_poa > 0:
            poa_highest = poa
            poa_highest_count = 1
            poa_highest_game[:] = game
            # for some reason, the copy of the GameInfoEquilibria named tuple is needed in numba
            poa_highest_info = game_prices_copy(game_prices)
        elif compare_poa == 0:
            poa_highest_count += 1
        compare_poa = rational_compare(poa, poa_lowest)
        if compare_poa < 0:
            poa_lowest = poa
            poa_lowest_count = 1
            poa_lowest_info = game_prices_copy(game_prices)
            poa_lowest_game[:] = game
        elif compare_poa == 0:
            poa_lowest_count += 1
        compare_pos = rational_compare(pos, pos_highest)
        if compare_pos > 0:
            pos_highest = pos
            pos_highest_count = 1
            pos_highest_info = game_prices_copy(game_prices)
            pos_highest_game[:] = game
        elif compare_pos == 0:
            pos_highest_count += 1
        compare_pos = rational_compare(pos, pos_lowest)
        if compare_pos < 0:
            pos_lowest = pos
            pos_lowest_count = 1
            pos_lowest_info = game_prices_copy(game_prices)
            pos_lowest_game[:] = game
        elif compare_pos == 0:
            pos_lowest_count += 1
    game_collection_count = GameCollectionCounts(
        total_count, noequilibrium_count, noequilibrium_game
    )
    game_collection_prices = (
        GameCollectionPrices(
            poa_highest,
            poa_highest_count,
            poa_highest_game,
            poa_highest_info,
            poa_lowest,
            poa_lowest_count,
            poa_lowest_game,
            poa_lowest_info,
            pos_highest,
            pos_highest_count,
            pos_highest_game,
            pos_highest_info,
            pos_lowest,
            pos_lowest_count,
            pos_lowest_game,
            pos_lowest_info,
            poa_sum_val / valid_count,
            pos_sum_val / valid_count,
        )
        if valid_count > 0
        else None
    )
    return GameCollectionInfo(game_collection_count, game_collection_prices)


@njit
def graph6_to_weight_matrix(g6: bytes) -> IntArray2D:
    """
    Parse a graph6 string/bytes object with n <= 62 and return a dense NumPy adjacency matrix
    with weights 0 / 1.
    """
    # Remove trailing newline if present
    length = len(g6)
    if length > 0 and g6[length - 1] == 10:
        length -= 1

    # This simple version supports graph6 with n <= 62
    n = g6[0] - 63

    A = np.zeros((n, n), dtype=np.int_)

    bit_index = 0

    # graph6 encodes upper-triangular adjacency bits:
    # (0,1), (0,2), (1,2), (0,3), (1,3), (2,3), ...
    for j in range(1, n):
        for i in range(j):
            byte_pos = 1 + bit_index // 6
            offset = bit_index % 6

            value = g6[byte_pos] - 63
            bit = (value >> (5 - offset)) & 1

            if bit == 1:
                A[i, j] = 1
                A[j, i] = 1

            bit_index += 1

    return A
