"""
Highly optimized code for brute-forcing hedonic game explorations.
"""

from numba import njit, config, intp, optional
from numba.experimental import jitclass

from typing import Optional

import numpy as np

# pyright: reportAttributeAccessIssue=false
config.DISABLE_JIT = False

type IntArray = np.ndarray[tuple[int], np.dtype[np.integer]]

type IntArray2D = np.ndarray[tuple[int, int], np.dtype[np.integer]]

type CoalitionStructure = IntArray

@jitclass([('valuations', intp[:,:])])
class Game:
    valuations: IntArray2D
    is_symmetric: bool
    is_fractional: bool
    k: Optional[int]

    def __init__(self, valuations: IntArray2D, is_symmetric: bool = True, is_fractional: bool = True, k: Optional[int] = None):
        self.valuations = valuations
        self.is_symmetric = is_symmetric
        self.is_fractional = is_fractional
        self.k = k

@njit
def is_improving_deviation(game: Game, cs: CoalitionStructure, ag: int, co_new: int) -> bool:
    """
    Determine if the agent "ag" moving to coalition "co_new" is an improving deviation for the given game
    and coalition structure.
    """
    valuations = game.valuations
    num_agents = len(valuations)
    co_old = cs[ag]
    if co_old == co_new:
        return False
    ut_old = 0
    ut_new = 0
    co_old_size = 0
    # starting from 1 compensates the fact that ag is a member of co_old
    co_new_size = 1
    for j in range(num_agents):
        if cs[j] == co_old:
            ut_old += valuations[ag][j]
            co_old_size += 1
        elif cs[j] == co_new:
            ut_new += valuations[ag][j]
            co_new_size += 1

    if not game.is_fractional:
        return ut_new > ut_old
    elif ut_old == ut_new == 0:
        return co_new_size < co_old_size
    else:
        return ut_new * co_old_size > ut_old * co_new_size


@njit
def next_improving_deviation_agent(game: Game, cs: CoalitionStructure, cs_sizes: IntArray,  ag: int, co_actual: int = -1) -> int | None:
    """
    Return the next improving deviation, if any, for the agent "ag" in the given game and coalition structure.  The parameter "k" is the maximum size of
    allowed coalitions, while "co_actual" is the last found improving deviation (-1 if we need to find the first deviation).
    """
    num_coalitions = len(cs_sizes)
    co = co_actual + 1
    k = game.k
    while co < num_coalitions:
        if k is None or cs_sizes[co] < k:
            if is_improving_deviation(game, cs, ag, co):
                return co
        co += 1
    return None


@njit
def improving_deviations_agent(game: Game, cs: CoalitionStructure, cs_sizes: IntArray, ag: int) -> list[int]:
    """
    Return a list of improving deviations for agent "ag".
    """
    res = []
    co = next_improving_deviation_agent(game, cs, cs_sizes, ag)
    while co is not None:
        res.append(co)
        co = next_improving_deviation_agent(game, cs, cs_sizes, ag, co)
    return res


@njit
def next_improving_deviation(game: Game, cs: CoalitionStructure, cs_sizes: IntArray, dev_actual: tuple[int, int] = (0, -1)) -> tuple[int, int] | None:
    """
    Return the next improving deviation in the given game and coalition structure.  The parameter "k" is the maximum size of
    allowed coalitions, while "dev_actual" is the last found  improving deviation (-1 if we need to find the first deviation).
    """
    num_agents = len(game.valuations)
    ag, co = dev_actual
    while ag < num_agents:
        co = next_improving_deviation_agent(game, cs, cs_sizes, ag, co)
        if co is not None:
            return (ag, co)
        ag += 1
        co = -1
    return None


@njit
def improving_deviations(game: Game, cs: CoalitionStructure, cs_sizes: IntArray) -> list[tuple[int, int]]:
    """
    Return a list of improving deviations for the given game and coalition structure.
    """
    res = []
    dev = next_improving_deviation(game, cs, cs_sizes)
    while dev is not None:
        res.append(dev)
        dev = next_improving_deviation(game, cs, cs_sizes, dev)
    return res

# pyright: reportCallIssue=false


@jitclass([
    ('cs', intp[:]),
    ('cs_sizes', intp[:]),
    ('cs_nums', intp[:])
])
class CoalitionStructureIterator:
    def __init__(self, cs: CoalitionStructure, cs_sizes: IntArray, cs_nums: IntArray):
        self.cs = cs
        self.cs_sizes = cs_sizes
        self.cs_nums = cs_nums


@njit
def cs_givensize_begin(game: Game, num_coalitions: int) -> CoalitionStructureIterator:
    """
    Build an iterator for coalistion structures.
    """
    num_agents = len(game.valuations)
    return CoalitionStructureIterator(np.full((num_agents), -1), np.zeros((num_coalitions), dtype=np.int_), np.full((num_agents + 1), -1))


@njit
def cs_givensize_next(cs_data: CoalitionStructureIterator, game: Game, num_coalitions: int) -> bool:
    """
    Update the iterator with a new colation structure. Returns False if there are no moreo coalitions structures
    to iterate.
    """
    num_agents = len(game.valuations)
    cs = cs_data.cs
    cs_sizes = cs_data.cs_sizes
    cs_nums = cs_data.cs_nums
    ag = 0 if cs[0] == -1 else num_agents - 1
    k = game.k
    while True:
        if ag == num_agents:
            return True
        if ag == -1:
            return False
        coalitions_potential = cs_nums[ag] + 1 + (num_agents - ag)
        bot = 0 if coalitions_potential > num_coalitions else cs_nums[ag] + 1
        top = cs_nums[ag] + 1 if cs_nums[ag] + \
            1 < num_coalitions else cs_nums[ag]
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
def cs_begin(game: Game) -> CoalitionStructureIterator:
    return cs_givensize_begin(game, 1)


@njit
def cs_next(cs_data: CoalitionStructureIterator, game: Game) -> bool:
    num_agents = len(game.valuations)
    num_coalitions = len(cs_data.cs_sizes)
    while num_coalitions <= num_agents:
        res = cs_givensize_next(cs_data, game, num_coalitions)
        if res:
            return True
        num_coalitions += 1
        cs_data.cs.fill(-1)
        cs_data.cs_nums.fill(-1)
        cs_data.cs_sizes = np.resize(cs_data.cs_sizes, num_coalitions)
    return False


@njit
def css_givensize(game: Game, coalitions_max: int) -> list[CoalitionStructure]:
    """
    Return a valid list of coalistion structures for the given parameters.
    """
    res = []
    cs_data = cs_givensize_begin(game, coalitions_max)
    while cs_givensize_next(cs_data, game, coalitions_max):
        res.append(np.copy(cs_data.cs))
    return res


@njit
def css(game: Game) -> list[CoalitionStructure]:
    """
    Return a valid list of coalistion structures for the given parameters.
    """
    res = []
    cs_data = cs_begin(game)
    while cs_next(cs_data, game):
        res.append(np.copy(cs_data.cs))
    return res


@njit
def nash_equilibrium(game: Game) -> CoalitionStructure | None:
    cs_data = cs_begin(game)
    while cs_next(cs_data, game):
        res = next_improving_deviation(game, cs_data.cs, cs_data.cs_sizes)
        if res is None:
            return cs_data.cs
    return None


@jitclass([
    ('game', intp[:, :]),
    ('first_max_reached', intp),
    ('sought_reward', intp)
])
class GameIterator:
    is_symmetric: bool

    def __init__(self, game: IntArray2D, first_max_reached: int, sought_reward: int, is_symmetric: bool):
        self.game = game
        self.first_max_reached = first_max_reached
        self.sought_reward = sought_reward
        self.is_symmetric = is_symmetric


@njit
def game_begin(num_agents: int,  min_reward: int, max_valuation: int, is_symmetric: bool) -> GameIterator:
    valuations = np.full((num_agents, num_agents), -1)
    return GameIterator(valuations, -1, min_reward, is_symmetric)


@njit
def game_next(git: GameIterator, max_valuation: int) -> bool:

    def next_pos(row, col, num_agents: int) -> tuple[int, int]:
        if col < num_agents - 1:
            col += 1
        else:
            row += 1
            col = 0
        return row, col

    game = git.game
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
    while git.sought_reward <= max_valuation:
        while row >= 0:
            bot = game[col][row] if (git.is_symmetric and row > col) else 0
            top = 0 if row == col else game[col][row] if (
                git.is_symmetric and row > col) else git.sought_reward
            v = game[row][col]
            v_new = max(v+1, bot)
            if v_new <= top:
                game[row][col] = v_new
                if row == 0 and col == 1:
                    print("    v:", v)
                if v_new == git.sought_reward and git.first_max_reached == -1:
                    git.first_max_reached = pos
                if pos == pos_final:
                    if git.first_max_reached != -1:
                        return True
                else:
                    row, col = next_pos(row, col, num_agents)
                    pos += 1
            else:
                game[row][col] = -1
                if git.first_max_reached == pos:
                    git.first_max_reached = -1
                pos -= 1
                if col > 0:
                    col -= 1
                else:
                    col = num_agents - 1
                    row -= 1
        git.sought_reward += 1
        print("sought_reward:", git.sought_reward)
        git.first_max_reached = -1
        row = 0
        pos = 0
        col = 0
    return False


@njit
def games(num_agents: int, is_symmetric: bool, min_reward: int, max_valuation: int, k: int | None = None) -> list[IntArray2D]:
    res = []
    git = game_begin(num_agents, min_reward, max_valuation, is_symmetric)
    while game_next(git, max_valuation):
        res.append(np.copy(git.game))
    return res


@njit
def unstable_game(num_agents: int, is_symmetric: bool, is_fractional: bool, max_valuation: int, k: int | None = None) -> IntArray2D| None:
    git = game_begin(num_agents, 0, max_valuation, is_symmetric)
    game = Game(git.game, is_symmetric, is_fractional, k)
    while game_next(git, max_valuation):
        if nash_equilibrium(game) is None:
            return game.valuations
    return None
