from typing import Iterator

from . import HedonicGameImpl as hgimpl
import numpy as np
import pydot

type Agent = int

type IntArray2D = np.ndarray[tuple[int, int], np.dtype[np.integer]]

type IntArray1D = np.ndarray[tuple[int], np.dtype[np.integer]]

type Coalition = int


class HedonicGame:
    """
    The class represents an hedonic game.
    """

    valuations: IntArray2D
    """
    The valuations matrix. The i-th row and j-th column represent the valuation of agent i
    for agent j.
    """

    is_symmetric: bool
    """
    Whether the game is symmetric or not. If `is_symmetric` is `True`, then
    `valuations[i, j]` should be equal to `valuations[j, i]` for all `i` and `j`.
    """

    def __init__(self, valuations: IntArray2D, is_symmetric: bool = True):
        """
        Creates an hedonic game. The parameter `is_symmetric` should be consistent with
        the values in the `valuations` matrix. If `is symmetric` is `True`, then
        `valuations[i, j]` should be equal to `valuations[j, i]` for all `i` and `j`.
        """
        self.valuations = valuations
        self.is_symmetric = is_symmetric

    @property
    def agents_num(self) -> int:
        """
        Return the number of agents in the game.
        """
        return len(self.valuations)

    def to_dot(self) -> str:
        """
        Convert the graph in the dot format. At the moment only works for symmetric games.
        """
        if not self.is_symmetric:
            raise ValueError("The game is not symmetric, cannot generate dot format.")
        graph = pydot.Dot("hedonicgame", graph_type="graph")
        for i in range(self.agents_num):
            node = pydot.Node(str(i), label=str(i))
            graph.add_node(node)
        for i in range(self.agents_num):
            for j in range(i+1, self.agents_num):
                if self.valuations[i, j] > 0:
                    edge = pydot.Edge(str(i), str(j), label=str(self.valuations[i, j]))
                    graph.add_edge(edge)
        return graph.to_string()

    def coalition_structures(self, cs_size: int | None = None,  k: int | None = None) -> Iterator['CoalitionStructure']:
        """
        Iterates over the colation structures for the current game. If provided, `cs_size` is the number of
        coalitions in the coalition structure, while `k` is the maximum size of each coalition.
        """
        if cs_size is not None:
            for cs in hgimpl.css_givensize(self.valuations, cs_size, k):
                yield CoalitionStructure(self, cs)
        else:
            for cs in hgimpl.css(self.valuations, k):
                yield CoalitionStructure(self, cs)

    def nash_equilibria(self, is_fractional: bool = True, k: int | None = None) -> Iterator['CoalitionStructure']:
        """
        Iterates over the the Nash stable coalition structures of the game. If provided, `cs_size` is the number of
        coalitions in the coalition structure, while `k` is the maximum size of each coalition.
        """
        for cs in hgimpl.nash_equilibria(self.valuations, is_fractional, k):
            yield CoalitionStructure(self, cs)

    def has_nash_equilibrium(self, is_fractional: bool = True, k: int | None = None) -> bool:
        """
        Return whether the game as has a Nash stable coalition structure.
        """
        return hgimpl.nash_equilibrium(self.valuations, is_fractional, k) is not None

    def __repr__(self) -> str:
        return f"HedonicGame({repr(self.valuations)}, is_symmetric={self.is_symmetric})"


class CoalitionStructure:
    """
    This is a coalition structure for an hedonic game.
    """

    game: HedonicGame
    """
    The game for which the coalition structure is defined.
    """

    cs: IntArray1D
    """
    The coalition structure. The i-th element is the coalition number of the i-th agent.
    """

    is_fractional: bool
    """
    Whether the utilities should be computed considering the game as a fractional or an
    additively separable one.
    """

    size: int
    """
    The number of coalitions in the coalition structure.
    """

    def __init__(self, game: HedonicGame, cs: IntArray1D, is_fractional: bool = True):
        """
        Creates a coalition structure for a given game. The coalition structure is represented as a
        numpy array of integers, where the i-th element is the coalition number of the i-th agent.
        """
        self.game = game
        self.cs = cs
        self.is_fractional = is_fractional
        self.size = max(self.cs)+1

    def coalition_size(self, co: Coalition) -> int:
        """
        Return the size of coalition `co`.
        """
        return sum(1 for x in self.cs if x == co)

    def agent_coalition(self, ag: Agent) -> Coalition:
        """
        Returns the coalition of the given agent.
        """
        if ag >= self.game.agents_num:
            raise ValueError(f"Agent {ag} is not in the game.")
        return self.cs[ag]

    def agent_utility(self, ag: Agent) -> int | float:
        """
        Returns the utility of the given agent.
        """
        val, size = hgimpl.agent_utility(self.game.valuations, self.cs, ag)
        return val if self.is_fractional else val / size

    def coalition_social_welfare(self, co: Coalition) -> int | float:
        """
        Returns the social welfare of the given coalition.
        """
        ut, size = hgimpl.coalition_social_welfare(self.game.valuations, self.cs, co)
        if size == 0:
            return 0
        else:
            return ut if self.is_fractional else ut / size

    def social_welfare(self) -> int | float:
        """
        Returns the social welfare of the coalition structure.
        """
        return sum(self.coalition_social_welfare(co) for co in np.arange(self.size))

    def move_agent(self, ag: Agent, co_new: Coalition):
        """
        Move the given agent to the new coalition.
        """
        if co_new >= self.size:
            co_new = self.size
            self.size += 1
        self.cs[ag] = co_new

    def is_improving_deviation(self, ag: Agent, co_new: Coalition) -> bool:
        """
        Determine if the given agent can improve its utility by moving to the new coalition.
        """
        co_old = self.cs[ag]
        if co_old == co_new:
            return False
        ut_old, size_old = hgimpl.agent_utility(self.game.valuations, self.cs, ag)
        ut_new, size_new = hgimpl.agent_utility_co(
            self.game.valuations, self.cs, ag, co_new)
        if not self.is_fractional:
            return ut_new > ut_old
        elif ut_old == ut_new == 0:
            return size_new+1 < size_old
        else:
            return ut_new * size_old > ut_old * (size_new + 1)


    def is_agent_stable(self, ag: Agent, k: np.integer | None = None) -> bool:
        """
        Determine if the given agent has no improving deviations.
        """
        return all(
            not self.is_improving_deviation(ag, co_new)
            for co_new in range(self.size+1) if co_new != self.cs[ag]
        )

    def is_nash_stable(self, k: np.integer | None = None) -> bool:
        """
        Determine if the coalition structure is Nash stable.
        """
        return all(self.is_agent_stable(ag, k) for ag in range(self.game.agents_num))

    def __repr__(self) -> str:
        return f"CoalitionStructure({repr(self.game)},{repr(self.cs)})"


GAME_K3_NOEQUILIBRIUM_PAPER = HedonicGame(np.array([
    [0, 9, 9, 4],
    [9, 0, 1, 7],
    [9, 1, 0, 7],
    [4, 7, 7, 0]
]))

GAME_K3_NOEQUILIBRIUM = HedonicGame(np.array([
    [0, 0, 5, 7],
    [0, 0, 5, 7],
    [5, 5, 0, 3],
    [7, 7, 3, 0]
]))

GAME_K4_NOEQUILIBRIUM_ = HedonicGame(np.array([
    [0, 0, 0, 5, 10],
    [0, 0, 6, 4, 9],
    [0, 6, 0, 10, 0],
    [5, 4, 10, 0, 10],
    [10, 9, 0, 10, 0]
]))

GAME_K5_NOEQUILIBRIUM_ = HedonicGame(np.array([
    [0, 0, 0, 0, 2, 2],
    [0, 0, 0, 2, 0, 2],
    [0, 0, 0, 2, 2, 1],
    [0, 2, 2, 0, 0, 2],
    [2, 0, 2, 0, 0, 2],
    [2, 2, 1, 2, 2, 0]
]))

GAME_K6_NOEQUILIBRIUM_= HedonicGame(np.array([
    [0, 0, 0, 0, 1, 1, 3],
    [0, 0, 1, 3, 0, 1, 2],
    [0, 1, 0, 3, 0, 3, 3],
    [0, 3, 3, 0, 0, 3, 2],
    [1, 0, 0, 0, 0, 3, 1],
    [1, 1, 3, 3, 3, 0, 0],
    [3, 2, 3, 2, 1, 0, 0]
]))

GAME_K7_NOEQUILIBRIUM = HedonicGame(np.array([
    [0, 0, 0, 0, 0, 0, 1, 2],
    [0, 0, 0, 0, 0, 0, 2, 2],
    [0, 0, 0, 0, 0, 2, 1, 2],
    [0, 0, 0, 0, 1, 2, 1, 0],
    [0, 0, 0, 1, 0, 2, 2, 0],
    [0, 0, 2, 2, 2, 0, 2, 0],
    [1, 2, 1, 1, 2, 2, 0, 2],
    [2, 2, 2, 0, 0, 0, 2, 0]
]))

GAME_K8_NOEQUILIBRIUM = HedonicGame(np.array([
    [0, 0, 0, 0, 0, 0, 0, 1, 2],
    [0, 0, 0, 0, 0, 0, 1, 2, 0],
    [0, 0, 0, 0, 1, 1, 0, 2, 2],
    [0, 0, 0, 0, 1, 1, 1, 1, 0],
    [0, 0, 1, 1, 0, 1, 0, 2, 2],
    [0, 0, 1, 1, 1, 0, 0, 2, 2],
    [0, 1, 0, 1, 0, 0, 0, 2, 0],
    [1, 2, 2, 1, 2, 2, 2, 0, 1],
    [2, 0, 2, 0, 2, 2, 0, 1, 0]
]))
