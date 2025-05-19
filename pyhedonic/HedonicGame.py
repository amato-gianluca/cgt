from typing import Iterator, NamedTuple
from functools import cached_property

import networkx as nx
import numpy as np
import numpy.typing as npt
import pydot

from . import HedonicGameImpl as hgimpl

type Agent = int

# Unfortunately, specifying the shape of the array in the type hint does not work well
type IntArray2D = npt.NDArray[np.integer]

# Unfortunately, specifying the shape of the array in the type hint does not work well
type IntArray1D = npt.NDArray[np.integer]

type Coalition = int


class PriceResult(NamedTuple):
    """A named tuple to store the price of anarchy, the price of stability and corresponding coalition structures."""
    poa: float
    """Price of anarchy"""
    pos: float
    """Price of stability"""
    cs_worst: 'CoalitionStructure'
    """Coalition structure with the worst price"""
    cs_best: 'CoalitionStructure'
    """Coalition structure with the best price"""


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
        Create an hedonic game.

        The parameter `is_symmetric` should be consistent with the values in the `valuations` matrix. If
        `is symmetric` is `True`, then `valuations[i, j]` should be equal to `valuations[j, i]`
        for all `i` and `j`.
        """
        self.valuations = valuations
        self.is_symmetric = is_symmetric

    @property
    def agents_num(self) -> int:
        """
        Return the number of agents in the game.
        """
        return len(self.valuations)

    @cached_property
    def is_simple(self) -> bool:
        """
        Return whether the game is simple or not. A game is simple if the valuations are all 0 or 1.
        """
        return np.all(self.valuations <= 1) # type: ignore[no-untyped-call]

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, HedonicGame):
            return False
        return (
            np.array_equal(self.valuations, other.valuations)
            and self.is_symmetric == other.is_symmetric
        )

    def to_dot(self) -> pydot.Dot:
        """
        Convert the game in the dot format.
        """
        graph_type = "graph" if self.is_symmetric else "digraph"
        graph = pydot.Dot("hedonicgame", graph_type=graph_type, strict=True)
        for i in range(self.agents_num):
            node = pydot.Node(str(i))
            graph.add_node(node)
        for i in range(self.agents_num):
            base = i+1 if self.is_symmetric else 0
            for j in range(base, self.agents_num):
                if self.valuations[i, j] > 0:
                    edge = (
                        pydot.Edge(str(i), str(j))
                        if self.is_simple
                        else pydot.Edge(str(i), str(j), label=str(self.valuations[i, j]))
                    )
                    graph.add_edge(edge)
        return graph

    @staticmethod
    def from_nx_graph(graph: nx.Graph | nx.DiGraph) -> 'HedonicGame':
        """
        Convert a networkx graph to an hedonic game.
        """
        is_symmetric = not graph.is_directed()
        if not all(
            isinstance(weight, int) or weight is None
            for _, _, weight in graph.edges(data="weight")  # type: ignore[arg-type]
        ):
            raise ValueError("The weights of the edges are not integers.")
        valuations = np.zeros((len(graph.nodes), len(graph.nodes)), dtype=np.integer)
        for i, j, weight in graph.edges(data='weight'):  # type: ignore[arg-type]
            valuations[i, j] = weight if weight is not None else 1
            if is_symmetric:
                valuations[j, i] = valuations[i, j]
        return HedonicGame(valuations, is_symmetric=is_symmetric)

    def to_nx_graph(self) -> nx.Graph | nx.DiGraph:
        """
        Convert the game in the networkx format. All the edges in the resulting graph have the weight attribute.
        """
        graph = nx.Graph() if self.is_symmetric else nx.DiGraph()
        graph.add_nodes_from(range(self.agents_num))
        graph.add_weighted_edges_from(
            (i, j, weight)
            for i in range(self.agents_num)
            for j in range(self.agents_num)
            if (weight := self.valuations[i, j]) > 0
        )
        return graph

    def coalition_structures(self, is_fractional: bool = True, k: int | None = None, cs_size: int | None = None) -> Iterator['CoalitionStructure']:
        """
        Iterates over the coalition structures of the game.

        If provided, `cs_size` is the number of coalitions in the coalition structure.
        The parameter `is_fractional` tells if we are interested in fractional or additively separable games,
        while `k` is the maximum size of each coalition.
        """
        if cs_size is not None:
            for cs in hgimpl.css_givensize(self.valuations, cs_size, k):
                yield CoalitionStructure(self, cs, is_fractional)
        else:
            for cs in hgimpl.css(self.valuations, k):
                yield CoalitionStructure(self, cs, is_fractional)

    def nash_stable_coalition_structures(self, is_fractional: bool = True, k: int | None = None) -> Iterator['CoalitionStructure']:
        """
        Iterates over the the Nash stable coalition structures of the game.

        The parameter `is_fractional` tells if we are interested in fractional or additively separable games,
        while `k` is the maximum size of each coalition.
        """
        for cs in hgimpl.nash_equilibria(self.valuations, is_fractional, k):
            yield CoalitionStructure(self, cs)

    def has_nash_stable_coalition_structure(self, is_fractional: bool = True, k: int | None = None) -> bool:
        """
        Return whether the game as has a Nash stable coalition structure.

        The parameter `is_fractional` tells if we are interested in fractional or additively separable games,
        while `k` is the maximum size of each coalition.
        """
        return hgimpl.nash_equilibrium(self.valuations, is_fractional, k) is not None

    def optimal_coalition_structure(self, is_fractional: bool = True, k: int | None = None) -> tuple['CoalitionStructure', int]:
        """
        Return one of the optimal coalition structures of the game and the corresponding social welfare.

        The parameter `is_fractional` tells if we are interested in fractional or additively separable games,
        while `k` is the maximum size of each coalition.
        """
        if not self.is_symmetric:
            raise ValueError(
                "The game is not symmetric, cannot compute optimal coalition structure."
            )
        if k != 2:
            raise ValueError(
                "k is different from 2, cannot compute the optimal coalition structure."
            )
        g = self.to_nx_graph()
        matching = (
            nx.maximal_matching(g)
            if np.max(self.valuations) <= 1
            else nx.max_weight_matching(g)
        )
        welfare = sum(g[u][v]['weight'] for u, v in matching)
        if not is_fractional:
            welfare *= 2
        cs = np.zeros(self.agents_num, dtype=np.integer)
        for n, (i, j) in enumerate(matching):
            cs[i] = n
            cs[j] = n
        return CoalitionStructure(self, cs, is_fractional), welfare

    def prices(self, is_fractional: bool = True, k: int | None = None) -> PriceResult | None:
        """
        Return the prics of anarchy and the price of stability for the game, together with an example of the
        coalition structures that achieve them. If the game has no Nash stable coalition structure, the
        result is `None`.

        The parameter `is_fractional` tells if we are interested in fractional or additively separable games,
        while `k` is the maximum size of each coalition.
        """
        poa = float('-inf')
        cs_worst = None
        pos = float('inf')
        cs_best = None
        _, opt = self.optimal_coalition_structure(is_fractional, k)
        for cs in self.nash_stable_coalition_structures(is_fractional, k):
            price = opt / cs.social_welfare()
            if price > poa:
                poa = price
                cs_worst = cs
            if price < pos:
                pos = price
                cs_best = cs
        return None if cs_worst is None or cs_best is None else PriceResult(poa, pos, cs_worst, cs_best)

    def __repr__(self) -> str:
        return f"HedonicGame({repr(self.valuations)}, is_symmetric={self.is_symmetric})"

    def __str__(self) -> str:
        return f"{repr(self.valuations)}, is_symmetric={self.is_symmetric}"


class CoalitionStructure:
    """
    This is a coalition structure for an hedonic game.
    """

    game: HedonicGame
    """
    The game for which the coalition structure is defined.
    """

    size: int
    """
    The number of coalitions in the coalition structure.
    """

    cs: IntArray1D
    """
    The coalition structure. The i-th element is the coalition number of the i-th agent. Elements of `cs` are
    all and only the integers in the range [0, size-1].
    """

    is_fractional: bool
    """
    Whether the utilities should be computed considering the game as a fractional or an
    additively separable one.
    """

    def __init__(self, game: HedonicGame, cs: IntArray1D, is_fractional: bool = True):
        """
        Creates a coalition structure for a given game. The coalition structure is represented as a
        numpy array of integers, where the i-th element is the coalition number of the i-th agent.
        Elements of `cs` are all and only the integers in the range [0, max(self.cs)].
        """
        self.game = game
        self.size = max(cs)+1  # type: ignore[arg-type]
        self.cs = cs
        self.is_fractional = is_fractional

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, CoalitionStructure):
            return False
        return (
            self.game is other.game
            and np.array_equal(self.cs, other.cs)
            and self.is_fractional == other.is_fractional
        )

    def coalition_size(self, co: Coalition) -> int:
        """
        Return the size of coalition `co`.
        """
        return sum(1 for x in self.cs if x == co)

    def agent_coalition(self, ag: Agent) -> Coalition:
        """
        Returns the coalition of the given agent.
        """
        return self.cs[ag]

    def agent_utility(self, ag: Agent) -> int | float:
        """
        Returns the utility of the given agent.
        """
        val, size = hgimpl.agent_utility(self.game.valuations, self.cs, ag)
        return val / size if self.is_fractional else val

    def coalition_social_welfare(self, co: Coalition) -> int | float:
        """
        Returns the social welfare of the given coalition.
        """
        ut, size = hgimpl.coalition_social_welfare(self.game.valuations, self.cs, co)
        return ut / size if self.is_fractional else ut

    def social_welfare(self) -> int | float:
        """
        Returns the social welfare of the coalition structure.
        """
        return sum(self.coalition_social_welfare(co) for co in range(self.size))

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

    def is_agent_nash_stable(self, ag: Agent, k: np.integer | None = None) -> bool:
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
        return all(self.is_agent_nash_stable(ag, k) for ag in range(self.game.agents_num))

    def __repr__(self) -> str:
        return f"CoalitionStructure({repr(self.game)},{repr(self.cs)})"

    def __str__(self) -> str:
        return f"{repr(self.cs)}"


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

GAME_K4_NOEQUILIBRIUM = HedonicGame(np.array([
    [0, 0, 0, 5, 10],
    [0, 0, 6, 4, 9],
    [0, 6, 0, 10, 0],
    [5, 4, 10, 0, 10],
    [10, 9, 0, 10, 0]
]))

GAME_K5_NOEQUILIBRIUM = HedonicGame(np.array([
    [0, 0, 0, 0, 2, 2],
    [0, 0, 0, 2, 0, 2],
    [0, 0, 0, 2, 2, 1],
    [0, 2, 2, 0, 0, 2],
    [2, 0, 2, 0, 0, 2],
    [2, 2, 1, 2, 2, 0]
]))

GAME_K6_NOEQUILIBRIUM = HedonicGame(np.array([
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

GAME_K7_NOEQUILIBRIUM_SIMPLE = HedonicGame(np.array([
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [0, 0, 0, 0, 0, 0, 1, 1, 1, 0],
    [0, 0, 0, 0, 0, 1, 0, 1, 1, 1],
    [0, 0, 0, 0, 1, 1, 0, 0, 1, 0],
    [0, 0, 0, 1, 0, 1, 0, 0, 1, 1],
    [0, 0, 1, 1, 1, 0, 0, 0, 1, 1],
    [0, 1, 0, 0, 0, 0, 0, 1, 1, 1],
    [0, 1, 1, 0, 0, 0, 1, 0, 1, 1],
    [0, 1, 1, 1, 1, 1, 1, 1, 0, 1],
    [1, 0, 1, 0, 1, 1, 1, 1, 1, 0]
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
