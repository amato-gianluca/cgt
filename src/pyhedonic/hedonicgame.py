"""
Python interface.

This is a pythonic wrapper around functions implemented in the pyhedonicgame_impl
module.
"""

from collections.abc import Iterable, Iterator
from dataclasses import dataclass
from fractions import Fraction
from functools import total_ordering
from typing import NamedTuple

import networkx as nx
import numpy as np
import pydot

from . import hedonicgame_impl as hgimpl
from .hedonicgame_impl import Agent, Coalition, IntArray1D, IntArray2D


class PriceResult(NamedTuple):
    """
    A named tuple to store the price of anarchy, the price of stability and the
    corresponding coalition structures.
    """

    poa: Fraction
    """Price of anarchy"""

    pos: Fraction
    """Price of stability"""

    sw_best_equilibrium: Fraction
    """Social welfare of the best Nash stable coalition structure."""

    cs_best_equilibrium: "CoalitionStructure"
    """Nash stable coalition structure with the best social welfare."""

    sw_worst_equilibrium: Fraction
    """Social welfare of the worst Nash stable coalition structure."""

    cs_worst_equilibrium: "CoalitionStructure"
    """Nash stable coalition structure with the worst social welfare."""

    sw_best: Fraction
    """Social welfare of the optimal coalition structure."""

    cs_best: "CoalitionStructure"
    """Optimal coalition structure with the best social welfare"""


@total_ordering
@dataclass(frozen=True)
class FractionalAgentUtility:
    """
    A dataclass to store the utility of an agent in a fractional game. It contains
    the sum of the valuations and the size of the coalition of the agent.
    """

    value: int
    """The sum of the valuations."""

    size: int
    """The size of the coalition of the agent."""

    def to_fraction(self) -> Fraction:
        """
        Convert the utility to a fraction.
        """
        return Fraction(self.value, self.size)

    def __lt__(self, other) -> bool:
        """
        Compare the utility with another utility.

        The comparison is done by comparing the values of the utilities, after converting
        them to fractions.
        """
        if self.value == other.value == 0:
            return self.size > other.size
        else:
            return self.value * other.size < other.value * self.size

    def __str__(self) -> str:
        return f"{self.value}/{self.size}"


class Graph:
    """
    The class represents a weighted directed or undirected graph, according to the
    value of the field _is_directed.
    """

    weights: IntArray2D
    """
    The weight matrix of the graph. Its values should be non-negative integers.
    """

    _is_directed: bool
    """
    Whether the graph is directed or not. If True, the matrix weights should be
    symmetric.
    """

    def __init__(self, weights: IntArray2D, is_directed: bool | None = None):
        """
        Creates a graph from the given weights.

        The weights matrix should be square and its values should be non-negative
        integers. If the graph is undirected the matrix should be symmetric, while the
        opposite is not generally required.  However, if the parameter is_directed is
        not provided, its value is inferred from the weights matrix. If the matrix is
        symmetric, the graph is undirected, otherwise it is directed.
        """
        assert weights.ndim == 2 and weights.shape[0] == weights.shape[1], (
            "The weights matrix should be square."
        )
        assert np.all(weights >= 0), (
            "The weights matrix should contain only non-negative integers."
        )
        assert is_directed is not False or np.array_equal(weights, weights.T), (
            "The graph is undirected, but the weights matrix is not symmetric."
        )
        self.weights = weights
        self._is_directed = (
            is_directed
            if is_directed is not None
            else not np.array_equal(weights, weights.T)
        )

    def __eq__(self, other: object) -> bool:
        """
        Compare the graph with another object.

        The graph is equal to another object if the latter is a graph with the same
        weights and the same directedness.
        """
        if not isinstance(other, Graph):
            return NotImplemented
        return (
            np.array_equal(self.weights, other.weights)
            and self.is_directed() == other.is_directed()
        )

    @property
    def node_count(self) -> int:
        return len(self.weights)

    def nodes(self) -> Iterable[int]:
        """
        Return the nodes of the graph.
        """
        return range(len(self.weights))

    def edges(self) -> Iterable[tuple[int, int, int]]:
        """
        Iterates over the edges of the graph.

        For each edge, the tuple (i, j, w) is returned where w is the weight of the
        edge (i, j).
        """
        return ((i, j, int(w)) for (i, j), w in np.ndenumerate(self.weights) if w > 0)

    def is_simple(self) -> bool:
        """
        Return whether the game is simple.

        A game is simple if the weights are all 0 or 1.
        """
        return bool(np.all(self.weights <= 1))

    def is_directed(self) -> bool:
        """
        Return whether the game is directed.
        """
        return self._is_directed

    def to_dot(self) -> pydot.Dot:
        """
        Convert the game in the dot format.
        """
        graph_type = "digraph" if self.is_directed() else "graph"
        graph = pydot.Dot("hedonicgame", graph_type=graph_type, strict=True)
        for i in self.nodes():
            graph.add_node(pydot.Node(str(i)))
        for i, j, w in self.edges():
            edge = (
                pydot.Edge(str(i), str(j))
                if self.is_simple()
                else pydot.Edge(str(i), str(j), label=str(w))
            )
            graph.add_edge(edge)
        return graph

    @classmethod
    def from_nx_graph(cls, graph: nx.Graph | nx.DiGraph) -> "Graph":
        """
        Convert a networkx graph to the `Graph` class.

        It expect weights to be non-negative integers and node labels to be integers
        from 0 to n-1, where n is the number of nodes in the graph.
        """
        assert all(
            isinstance(weight, int) or weight is None
            for _, _, weight in graph.edges(data="weight")  # type: ignore[arg-type]
        ), "The weights of the edges should be non-negative integers."

        weights = np.zeros((len(graph.nodes), len(graph.nodes)), dtype=np.int_)
        for i, j, weight in graph.edges(data="weight"):  # type: ignore[arg-type]
            weights[i, j] = weight if weight is not None else 1
            if not graph.is_directed():
                weights[j, i] = weights[i, j]
        return cls(weights, graph.is_directed())

    def to_nx_graph(self) -> nx.Graph | nx.DiGraph:
        """
        Convert the game in the networkx format.

        All the edges in the resulting graph have the weight attribute.
        """
        graph = nx.DiGraph() if self.is_directed() else nx.Graph()
        graph.add_nodes_from(self.nodes())
        graph.add_weighted_edges_from(self.edges())
        return graph

    def __repr__(self) -> str:
        return f"Graph({repr(self.weights)}, is_directed={self.is_directed()})"

    def __str__(self) -> str:
        return f"{repr(self.weights)}, is_directed={self.is_directed()}"

    @classmethod
    def enumerate(
        cls, n: int, is_directed: bool, m_min: int, m_max: int
    ) -> Iterator["Graph"]:
        """
        Iterates over all the graphs with n nodes, with the given directedness. The
        values m_min and m_max are the minimum and maximum value of m, where m is the
        maximum weight of the edges. For example, if one wants to generate only simple
        graphs, m_max should be set to 1 and m_min to 0.

        The graphs are generated in a lexicographic order. Some attempt is made to
        generate the graphs in a canonical form, avoiding isomorphism variants of the
        same graph. However, isomophic variants of the same graph are almost always
        generated.
        """
        for weights in hgimpl.games(n, not is_directed, m_min, m_max):
            yield cls(weights, is_directed)


class HedonicGame:
    graph: Graph
    """
    The graph encoding the agents and their valuations.
    """

    _k: int | None
    """
    The maximum size of the coalitions.

    If None, there is no limit on the size of the coalitions. If it is an integer, it
    should be non-negative.
    """

    _is_fractional: bool
    """
    Whether the game is fractional or additively separable.
    """

    @property
    def agent_count(self) -> int:
        return self.graph.node_count

    @property
    def valuations(self) -> IntArray2D:
        """
        Return the valuations of the game. The valuations are represented as a matrix,
        where the i-th row contains the valuations of the i-th agent for all the other
        agents.
        """
        return self.graph.weights

    @property
    def k(self) -> int | None:
        """
        Return the maximum size of the coalitions. If None, there is no limit on the
        size of the coalitions.
        """
        return self._k

    def agents(self) -> Iterable[Agent]:
        """
        Return the agents of the game.
        """
        return self.graph.nodes()

    def is_fractional(self) -> bool:
        """
        Return whether the game is fractional or additively separable.
        """
        return self._is_fractional

    def is_directed(self) -> bool:
        """
        Return whether the game is directed or not.
        """
        return self.graph.is_directed()

    def is_simple(self) -> bool:
        """
        Return whether the game is simple or not. A game is simple if weights are all
        0 or 1.
        """
        return self.graph.is_simple()

    def __init__(
        self,
        graph: Graph | IntArray2D,
        k: int | None = None,
        is_fractional: bool = True,
    ):
        """
        Creates a hedonic game from the given graph.
        """
        assert k is None or k >= 0, (
            "The maximum size of the coalitions should be non-negative."
        )
        assert not isinstance(graph, Graph) or (
            graph.is_directed() != np.array_equal(graph.weights, graph.weights.T)
        ), "The graph is directed, but the weights matrix is symmetric."
        self.graph = graph if isinstance(graph, Graph) else Graph(graph)
        self._k = k
        self._is_fractional = is_fractional

    def __eq__(self, other: object) -> bool:
        """
        Compare the game with another object.

        A game is equal to another object if the latter is a game with the same weights
        and same values of k and is_fractional.
        """
        if not isinstance(other, HedonicGame):
            return NotImplemented
        return (
            self.graph == other.graph
            and self._k == other._k
            and self.is_fractional() == other.is_fractional()
        )

    def coalition_structures(
        self, cs_size: int | None = None
    ) -> Iterator["CoalitionStructure"]:
        """
        Iterates over the coalition structures of the game.

        If provided, `cs_size` restrict the coalitions structures to those with the
        specified number of coalitions.
        """
        assert cs_size is None or cs_size >= 0, (
            "The number of coalitions should be non-negative."
        )
        if cs_size is not None:
            for cs in hgimpl.css_givensize(self.agent_count, cs_size, self._k):
                yield CoalitionStructure(self, cs)
        else:
            for cs in hgimpl.css(self.agent_count, self._k):
                yield CoalitionStructure(self, cs)

    def coalition_structures_as_nx(
        self, cs_size: int | None = None
    ) -> tuple[nx.DiGraph["CoalitionStructure"], set["CoalitionStructure"]]:
        equilibria = set()
        graph = nx.DiGraph()
        graph.add_nodes_from(self.coalition_structures())
        for cs in self.coalition_structures():
            equilibrium = True
            for ag, co in cs.improving_deviations():
                equilibrium = False
                cs_new = cs.move_to(ag, co)
                graph.add_edge(cs, cs_new)
            if equilibrium:
                equilibria.add(cs)
        return graph, equilibria

    def isolated_coalition_structure(self) -> "CoalitionStructure":
        """
        Return the isolated coalition structure of the game.

        The isolated coalition structure is the one where each agent is in its own
        coalition.
        """
        return CoalitionStructure(self, np.arange(self.agent_count))

    def big_coalition_structure(self) -> "CoalitionStructure | None":
        """
        Return the big coalition structure of the game, or None if it is not valid.

        The big coalition structure is the one where all agents are in the same
        coalition. If this is not a valid coalition structure, None is retuned.
        """
        if self._k is not None and self._k < self.agent_count:
            return None
        else:
            return CoalitionStructure(self, np.zeros(self.agent_count, dtype=np.int_))

    def nash_stable_coalition_structures(self) -> Iterator["CoalitionStructure"]:
        """
        Iterates over the Nash stable coalition structures of the game.
        """
        for cs in hgimpl.nash_equilibria(
            self.valuations, self.is_fractional(), self._k
        ):
            yield CoalitionStructure(self, cs)

    def has_nash_stable_coalition_structure(self) -> bool:
        """
        Return whether the game has a Nash stable coalition structure.
        """
        return (
            hgimpl.nash_equilibrium(self.valuations, self.is_fractional(), self._k)
            is not None
        )

    def _optimal_coalition_structure_fast(
        self,
    ) -> tuple["CoalitionStructure", int | Fraction]:
        """
        Return one of the optimal coalition structures of the game and the
        corresponding social welfare. Currently, this function only works fo
        undirected games with k=2, where the optimal coalition structure can be found
        by computing a maximum weight matching in the graph.
        """
        if self.is_directed():
            raise ValueError(
                "The game is directed, cannot compute optimal coalition structure."
            )
        if self._k != 2:
            raise ValueError(
                "k is different from 2, cannot compute the optimal coalition structure."
            )

        g = self.graph.to_nx_graph()
        matching = nx.max_weight_matching(g)
        welfare = sum(g[u][v]["weight"] for u, v in matching)
        if not self.is_fractional():
            welfare *= 2
        cs = np.full(self.agent_count, -1, dtype=np.int_)
        next_coalition = 0
        for i, j in matching:
            cs[i] = next_coalition
            cs[j] = next_coalition
            next_coalition += 1
        for i in range(self.agent_count):
            if cs[i] == -1:
                cs[i] = next_coalition
                next_coalition += 1
        CoalitionStructure._normalize(cs)
        return CoalitionStructure(self, cs), welfare

    def optimal_coalition_social_welfare(self) -> int | Fraction:
        """
        Return the social welfare of an optimal coalition structure of the game.
        """
        if not self.is_directed() and self._k == 2:
            _, opt = self._optimal_coalition_structure_fast()
            return opt
        else:
            return max(cs.social_welfare() for cs in self.coalition_structures())

    def optimal_coalition_structures(self) -> Iterator["CoalitionStructure"]:
        """
        Return all the optimal coalition structures of the game, in lexicographic order.
        """
        opt = self.optimal_coalition_social_welfare()
        yield from (
            cs for cs in self.coalition_structures() if cs.social_welfare() == opt
        )

    def optimal_coalition_structure(
        self,
    ) -> tuple["CoalitionStructure", int | Fraction]:
        """
        Return one of the optimal coalition structures of the game and the corresponding social welfare.
        """
        if not self.is_directed() and self._k == 2:
            return self._optimal_coalition_structure_fast()
        else:
            cs = next(self.optimal_coalition_structures())
            return cs, cs.social_welfare()

    def prices(self) -> PriceResult | None:
        """
        Return the prices of anarchy and the price of stability for the game.

        It also returns examples of the coalition structures that achieve them. If the
        game has no Nash stable coalition structure, the result is None.
        """
        denominator = (
            1
            if not self.is_fractional()
            else hgimpl.lcm_upto(self.k)
            if self.k is not None
            else hgimpl.lcm_upto(self.agent_count)
        )
        weights = self.valuations * denominator
        res = hgimpl.game_prices_compute(weights, self.is_fractional(), self._k)
        if res is None:
            return None
        else:
            poa = Fraction(res.sw_best, res.sw_worst_equilibrium)
            pos = Fraction(res.sw_best, res.sw_best_equilibrium)
            return PriceResult(
                poa,
                pos,
                Fraction(res.sw_best_equilibrium, denominator),
                CoalitionStructure(self, res.cs_best_equilibrium),
                Fraction(res.sw_worst_equilibrium, denominator),
                CoalitionStructure(self, res.cs_worst_equilibrium),
                Fraction(res.sw_best, denominator),
                CoalitionStructure(self, res.cs_best),
            )

    def __repr__(self) -> str:
        return f"HedonicGame({repr(self.valuations)}, k={self._k}, is_fractional={self.is_fractional()}))"

    def __str__(self) -> str:
        return (
            f"{str(self.valuations)}, k={self._k}, is_fractional={self.is_fractional()}"
        )


class CoalitionStructure:
    """
    This is a coalition structure for an hedonic game.
    """

    game: HedonicGame
    """
    The game for which this coalition structure is defined.
    """

    cs: IntArray1D
    """
    The coalition structure.

    The i-th element is the coalition number of the i-th agent. Elements of cs are all
    and only the integers in the range [0, max(cs)].
    """

    _sizes: IntArray1D
    """
    The sizes of the coalitions in the coalition structure.
    """

    @staticmethod
    def _normalize(cs: IntArray1D) -> None:
        """
        Normalize the coalition structure.

        The coalition numbers are shifted to be in the range [0, size-1] and they
        appear in increasing order.
        """
        current = 0
        map = np.full(len(cs), -1)
        for i in range(len(cs)):
            tgt = map[cs[i]]
            if tgt == -1:
                map[cs[i]] = current
                tgt = current
                current += 1
            cs[i] = tgt

    def __init__(self, game: HedonicGame, cs: IntArray1D):
        """
        Creates a coalition structure for a given game.

        The coalition structure is represented as an array of integers, where the i-th
        element is the coalition number of the i-th agent. Elements of cs are all and
        only the integers in the range [0, max(cs)]. New coalitions indexes should
        appear for the first time in the order of their number. Therefore `[0, 2, 0, 1]`
        is not a valid coalition structure, because the coalition `1` appears for the
        first time before the coalition `2`. However, `[0, 1, 0, 2]` is a valid
        coalition structure.
        """
        assert len(cs) == game.agent_count, (
            "The coalition structure should have the same size as the number of agents."
        )
        assert np.all(cs >= 0), (
            "The coalition structure should contain only non-negative integers."
        )
        assert max(cs) + 1 == len(np.unique(cs)), (
            "The coalition structure should contain all integers from `0` to `max(cs)`."
        )

        self.game = game
        self.cs = cs
        self._sizes = np.bincount(cs, minlength=len(cs))

    def __eq__(self, value: object) -> bool:
        """
        Compare the coalition structure with another object.

        The coalition structure is equal to another object if the latter is a coalition
        structure for the same game with the same coalitions.
        """
        if not isinstance(value, CoalitionStructure):
            return False
        return self.game == value.game and np.array_equal(self.cs, value.cs)

    def __hash__(self):
        return hash(self.cs.tobytes())

    @property
    def size(self) -> int:
        """
        Return the number of coalitions in the coalition structure.
        """
        return max(self.cs) + 1

    def coalitions(self) -> Iterable[Coalition]:
        """
        Returns the coalitions of the coalition structure.
        """
        return range(self.size)

    def coalition_size(self, co: Coalition) -> int:
        """
        Return the size of coalition `co`.
        """
        assert 0 <= co < self.size, "Coalition number out of range."
        return self._sizes[co]

    def agent_coalition(self, ag: Agent) -> Coalition:
        """
        Returns the coalition of the given agent.
        """
        assert 0 <= ag < len(self.cs), "Agent number out of range."
        return self.cs[ag]

    def agent_utility(
        self, ag: Agent, co: Coalition | None = None
    ) -> int | FractionalAgentUtility:
        """
        Returns the utility of the given agent. If co is provided, the utility is computed as if the agent were in coalition co.
        """
        assert 0 <= ag < len(self.cs), "Agent number out of range."
        assert co is None or (0 <= co < self.size + 1 and co < self.game.agent_count), (
            "Coalition number out of range."
        )
        val, size = (
            hgimpl.agent_utility(self.game.valuations, self.cs, ag)
            if co is None
            else hgimpl.agent_utility_co(self.game.valuations, self.cs, ag, co)
        )
        return FractionalAgentUtility(val, size) if self.game.is_fractional() else val

    def coalition_social_welfare(self, co: Coalition) -> int | Fraction:
        """
        Returns the social welfare of the given coalition.
        """
        assert 0 <= co < self.size, "Coalition number out of range."
        ut, size = hgimpl.coalition_social_welfare(self.game.valuations, self.cs, co)
        return Fraction(ut, size) if self.game.is_fractional() else ut

    def social_welfare(self) -> int | Fraction:
        """
        Returns the social welfare of the coalition structure.
        """
        return sum(self.coalition_social_welfare(co) for co in self.coalitions())

    def is_improving_deviation(self, ag: Agent, co_new: Coalition) -> bool:
        """
        Determine if the given agent can improve its utility by moving to the new
        coalition.

        Note that co_new may be one larger than the current coalition structure size.
        This means that the agent ag is moving its current coalition to form a new
        coalition alone. In all cases, co_new should be smaller than the number of
        agents in the game.
        """
        assert 0 <= ag < len(self.cs), "Agent number out of range."
        assert 0 <= co_new <= self.size and co_new < self.game.agent_count, (
            "Coalition number out of range."
        )

        if self.game.k is not None and self._sizes[co_new] == self.game.k:
            return False
        co_old = self.cs[ag]
        if co_old == co_new:
            return False
        ut_old, size_old = hgimpl.agent_utility(self.game.valuations, self.cs, ag)
        ut_new, size_new = hgimpl.agent_utility_co(
            self.game.valuations, self.cs, ag, co_new
        )
        if not self.game.is_fractional():
            return ut_new > ut_old
        elif ut_old == ut_new == 0:
            return size_new < size_old
        else:
            return ut_new * size_old > ut_old * size_new

    def improving_deviations_for_agents(self, ag: Agent) -> Iterable[Coalition]:
        """
        Iterates over the improving deviations of the given agent.

        The improving deviations are the coalitions to which the agent can move to
        improve its utility.
        """
        assert 0 <= ag < len(self.cs), "Agent number out of range."
        for co_new in range(min(self.size + 1, self.game.agent_count)):
            if self.is_improving_deviation(ag, co_new):
                yield co_new

    def improving_deviations(self) -> Iterable[tuple[Agent, Coalition]]:
        """
        Iterates over the improving deviations of the coalition structure.

        The improving deviations are the pairs (agent, coalition) such that the agent
        can move to the coalition to improve its utility.
        """
        for ag in self.game.agents():
            for co_new in self.improving_deviations_for_agents(ag):
                yield ag, co_new

    def move_to(self, ag: Agent, co_new: Coalition) -> "CoalitionStructure":
        """
        Move the given agent to the new coalition and return the new coalition structure
        we obtain in this way.
        """
        assert 0 <= ag < len(self.cs), "Agent number out of range."
        assert 0 <= co_new <= self.size and co_new < self.game.agent_count, (
            "Coalition number out of range."
        )
        assert self.game.k is None or self._sizes[co_new] < self.game.k, (
            "The target coalition size is too large."
        )
        # If the agent is moving to a new coalition, we need to update the coalition sizes.
        co_old = self.cs[ag]
        if co_old == co_new:
            return self
        if self._sizes[co_old] == 1 and co_new == self.size:
            return self
        cs_new = np.copy(self.cs)
        cs_new[ag] = co_new
        self._normalize(cs_new)
        return CoalitionStructure(self.game, cs_new)

    def is_agent_nash_stable(self, ag: Agent) -> bool:
        """
        Determine if the given agent has no improving deviations.
        """
        assert 0 <= ag < len(self.cs), "Agent number out of range."
        return all(
            not self.is_improving_deviation(ag, co_new)
            for co_new in range(self.size + 1)
            if co_new != self.cs[ag]
        )

    def is_nash_stable(self) -> bool:
        """
        Determine if the coalition structure is Nash stable.
        """
        return all(self.is_agent_nash_stable(ag) for ag in (self.game.agents()))

    def to_list(self) -> list[set[int]]:
        """
        Return the coalition structure as a list of sets. Each set contains the agents
        in the corresponding coalition.
        """
        s = [set[int]() for _ in range(self.size)]
        for ag in self.game.agents():
            s[self.cs[ag]].add(ag)
        return s

    def __repr__(self) -> str:
        return f"CoalitionStructure({repr(self.game)},{repr(self.cs)})"

    def __str__(self) -> str:
        return str(self.to_list())


GAME_K3_NOEQUILIBRIUM_PAPER = HedonicGame(
    np.array([[0, 9, 9, 4], [9, 0, 1, 7], [9, 1, 0, 7], [4, 7, 7, 0]]),
    is_fractional=True,
    k=3,
)

GAME_K3_NOEQUILIBRIUM = HedonicGame(
    np.array([[0, 0, 5, 7], [0, 0, 5, 7], [5, 5, 0, 3], [7, 7, 3, 0]]),
    is_fractional=True,
    k=3,
)

GAME_K4_NOEQUILIBRIUM = HedonicGame(
    np.array(
        [
            [0, 0, 0, 5, 10],
            [0, 0, 6, 4, 9],
            [0, 6, 0, 10, 0],
            [5, 4, 10, 0, 10],
            [10, 9, 0, 10, 0],
        ]
    ),
    is_fractional=True,
    k=4,
)

GAME_K5_NOEQUILIBRIUM = HedonicGame(
    np.array(
        [
            [0, 0, 0, 0, 2, 2],
            [0, 0, 0, 2, 0, 2],
            [0, 0, 0, 2, 2, 1],
            [0, 2, 2, 0, 0, 2],
            [2, 0, 2, 0, 0, 2],
            [2, 2, 1, 2, 2, 0],
        ]
    ),
    is_fractional=True,
    k=5,
)

GAME_K6_NOEQUILIBRIUM = HedonicGame(
    np.array(
        [
            [0, 0, 0, 0, 1, 1, 3],
            [0, 0, 1, 3, 0, 1, 2],
            [0, 1, 0, 3, 0, 3, 3],
            [0, 3, 3, 0, 0, 3, 2],
            [1, 0, 0, 0, 0, 3, 1],
            [1, 1, 3, 3, 3, 0, 0],
            [3, 2, 3, 2, 1, 0, 0],
        ]
    ),
    is_fractional=True,
    k=6,
)

GAME_K7_NOEQUILIBRIUM = HedonicGame(
    np.array(
        [
            [0, 0, 0, 0, 0, 0, 1, 2],
            [0, 0, 0, 0, 0, 0, 2, 2],
            [0, 0, 0, 0, 0, 2, 1, 2],
            [0, 0, 0, 0, 1, 2, 1, 0],
            [0, 0, 0, 1, 0, 2, 2, 0],
            [0, 0, 2, 2, 2, 0, 2, 0],
            [1, 2, 1, 1, 2, 2, 0, 2],
            [2, 2, 2, 0, 0, 0, 2, 0],
        ]
    ),
    is_fractional=True,
    k=7,
)

GAME_K7_NOEQUILIBRIUM_SIMPLE = HedonicGame(
    np.array(
        [
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [0, 0, 0, 0, 0, 0, 1, 1, 1, 0],
            [0, 0, 0, 0, 0, 1, 0, 1, 1, 1],
            [0, 0, 0, 0, 1, 1, 0, 0, 1, 0],
            [0, 0, 0, 1, 0, 1, 0, 0, 1, 1],
            [0, 0, 1, 1, 1, 0, 0, 0, 1, 1],
            [0, 1, 0, 0, 0, 0, 0, 1, 1, 1],
            [0, 1, 1, 0, 0, 0, 1, 0, 1, 1],
            [0, 1, 1, 1, 1, 1, 1, 1, 0, 1],
            [1, 0, 1, 0, 1, 1, 1, 1, 1, 0],
        ]
    ),
    is_fractional=True,
    k=7,
)

GAME_K8_NOEQUILIBRIUM = HedonicGame(
    np.array(
        [
            [0, 0, 0, 0, 0, 0, 0, 1, 2],
            [0, 0, 0, 0, 0, 0, 1, 2, 0],
            [0, 0, 0, 0, 1, 1, 0, 2, 2],
            [0, 0, 0, 0, 1, 1, 1, 1, 0],
            [0, 0, 1, 1, 0, 1, 0, 2, 2],
            [0, 0, 1, 1, 1, 0, 0, 2, 2],
            [0, 1, 0, 1, 0, 0, 0, 2, 0],
            [1, 2, 2, 1, 2, 2, 2, 0, 1],
            [2, 0, 2, 0, 2, 2, 0, 1, 0],
        ]
    ),
    is_fractional=True,
    k=8,
)
