"""
Highly optimized code for brute-forcing hedonic game explorations.
"""

from numba import njit, config, intp
from numba.experimental import jitclass

import numpy as np

# pyright: reportAttributeAccessIssue=false
config.DISABLE_JIT = False

type IntArray1D = np.ndarray[tuple[int], np.dtype[np.integer]]

type IntArray2D = np.ndarray[tuple[int, int], np.dtype[np.integer]]

type Game = IntArray2D

type CoalitionStructure = IntArray1D

type Deviation = tuple[int, int]

@njit
def is_improving_deviation(game: Game, is_fractional: bool, cs: CoalitionStructure, cs_sizes: IntArray1D, dev: Deviation) -> bool:
    """
    Determine if the agent "ag" moving to coalition "co_new" is an improving deviation for the given game
    and coalition structure.
    """
    num_agents = len(game)
    ag, co_new = dev
    co_old = cs[ag]
    if co_old == co_new:
        return False
    ut_old = 0
    ut_new = 0
    # starting from 1 compensates the fact that ag is a member of co_old
    for j in range(num_agents):
        if cs[j] == co_old:
            ut_old += game[ag,j]
        elif cs[j] == co_new:
            ut_new += game[ag,j]

    if not is_fractional:
        return ut_new > ut_old
    elif ut_old == ut_new == 0:
        return cs_sizes[co_new]+1 < cs_sizes[co_old]
    else:
        return ut_new * cs_sizes[co_old] > ut_old * (cs_sizes[co_new]+1)

@njit
def next_improving_deviation(game: Game, is_fractional: bool, cs: CoalitionStructure, cs_sizes: IntArray1D, num_coalitions: int, k: int | None, min_agent: int, max_agent: int, dev_actual: Deviation = (0, -1)) -> Deviation | None:
    """
    Return the next improving deviation in the given game and coalition structure.  The parameter "k" is the maximum size of
    allowed coalitions, while "dev_actual" is the last found  improving deviation (-1 if we need to find the first deviation).
    """
    ag, co = dev_actual
    ag = max(ag, min_agent)
    while ag < max_agent:
        co += 1
        while co < num_coalitions:
            if k is None or cs_sizes[co] < k:
                if is_improving_deviation(game, is_fractional, cs, cs_sizes, (ag, co)):
                    return (ag, co)
            co += 1
        ag += 1
        co = -1
    return None

@njit
def improving_deviations(game: Game, is_fractional: bool, cs: CoalitionStructure, cs_sizes: IntArray1D, num_coalitions: int, k: int | None, min_agent: int, max_agent: int) -> list[Deviation]:
    """
    Return a list of improving deviations for the given game and coalition structure.
    """
    res = []
    dev = next_improving_deviation(game, is_fractional, cs, cs_sizes, num_coalitions, k, min_agent, max_agent)
    while dev is not None:
        res.append(dev)
        dev = next_improving_deviation(game, is_fractional, cs, cs_sizes, num_coalitions, k, min_agent, max_agent, dev)
    return res

type CoalitionStructureIterator = tuple[CoalitionStructure, IntArray1D, IntArray1D, IntArray1D]

@njit
def cs_givensize_begin(game: Game, num_coalitions: int, k: int | None = None) -> CoalitionStructureIterator:
    """
    Build an iterator for coalistion structures.
    """
    num_agents = len(game)
    return (np.full((num_agents), -1), np.zeros((num_agents), dtype=np.int_), np.full((num_agents + 1), -1), np.array([num_coalitions]))


@njit
def cs_givensize_next(cs_data: CoalitionStructureIterator, game: Game, k: int | None = None, ) -> bool:
    """
    Update the iterator with a new colation structure. Returns False if there are no moreo coalitions structures
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
    return cs_givensize_begin(game, 1, k)


@njit
def cs_next(cs_data: CoalitionStructureIterator, game: Game, k: int | None) -> bool:
    num_agents = len(game)
    cs, cs_sizes, cs_nums, num_coalitions = cs_data
    while num_coalitions[0] <= num_agents:
        res = cs_givensize_next(cs_data, game, k)
        if res: return True
        num_coalitions[0] += 1
        cs.fill(-1)
        cs_nums.fill(-1)
        cs_sizes.fill(0)
    return False


@njit
def css_givensize(game: Game, coalitions_max: int, k: int | None = None) -> list[CoalitionStructure]:
    """
    Return a valid list of coalistion structures for the given parameters.
    """
    res = []
    cs_data = cs_givensize_begin(game, coalitions_max, k)
    while cs_givensize_next(cs_data, game,  k):
        res.append(np.copy(cs_data[0]))
    return res


@njit
def css(game: Game, k: int | None = None) -> list[CoalitionStructure]:
    """
    Return a valid list of coalistion structures for the given parameters.
    """
    res = []
    cs_data = cs_begin(game, k)
    while cs_next(cs_data, game, k):
        res.append(np.copy(cs_data[0]))
    return res


@njit
def nash_equilibrium(game: Game, is_fractional: bool, k: int | None = None) -> CoalitionStructure | None:
    cs_data: CoalitionStructureIterator = cs_begin(game, k)
    while cs_next(cs_data, game, k):
        cs, cs_sizes, _, num_coalitions = cs_data
        res = next_improving_deviation(game, is_fractional, cs, cs_sizes, num_coalitions[0], k, 0, len(game))
        if res is None:
            return cs

type GameIterator = tuple[Game, IntArray1D]

@njit
def game_begin(num_agents: int,  min_reward: int, max_valuation: int) -> GameIterator:
    game = np.full((num_agents, num_agents), -1)
    return (game, np.array([-1, min_reward]))


@njit
def game_next(git: GameIterator, is_symmetric: bool, max_valuation: int) -> bool:

    def next_pos(row, col, num_agents: int) -> tuple[int, int]:
        if col < num_agents - 1:
            col += 1
        else:
            row += 1
            col = 0
        return row, col

    game, data = git
    num_agents = len(game)
    pos_final = num_agents * num_agents - 1
    if game[0][0] == -1:
        row = 0
        col = 0
        pos = 0
    else:
        row = num_agents - 1
        col = num_agents - 1
        pos = pos_final
    while data[1] <= max_valuation:
        while row >= 0:
            bot = game[col][row] if (is_symmetric and row > col) else 0
            top = 0 if row == col else game[col][row] if (is_symmetric and row > col) else data[1]
            v = game[row][col]
            v_new = max(v+1, bot)
            if v_new <= top:
                game[row][col] = v_new
                if row == 0 and col == 1:
                    print("    v:", v)
                if v_new == data[1] and data[0] == -1:
                    data[0] = pos
                if pos == pos_final:
                    if data[0] != -1:
                        return True
                else:
                    row, col = next_pos(row, col, num_agents)
                    pos += 1
            else:
                game[row][col] = -1
                if data[0] == pos:
                    data[0] = -1
                pos -= 1
                if col > 0:
                    col -= 1
                else:
                    col = num_agents - 1
                    row -= 1
        data[1] += 1
        print("sought_reward:", data[1])
        data[0] = -1
        row = 0
        pos = 0
        col = 0
    return False


@njit
def games(num_agents: int, is_symmetric: bool, min_reward: int, max_valuation: int) -> list[Game]:
    res = []
    git = game_begin(num_agents, min_reward, max_valuation)
    while game_next(git, is_symmetric, max_valuation):
        res.append(np.copy(git[0]))
    return res


@njit
def unstable_game(num_agents: int, is_symmetric: bool, is_fractional: bool, max_valuation: int, k: int | None = None) -> Game | None:
    git = game_begin(num_agents, 0, max_valuation)
    while game_next(git, is_symmetric, max_valuation):
        if nash_equilibrium(git[0], is_fractional, k) is None:
            return git[0]
    return None
