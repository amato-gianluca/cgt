"""
Python interface.

This is a pythonic wrapper around functions implemented in the HedonicGameImpl package.
"""

from collections.abc import Iterator, Iterable
from typing import NamedTuple

import networkx as nx
import numpy as np
import pydot

from . import hedonicgame_impl as hgimpl
from .hedonicgame_impl import IntArray1D, IntArray2D, Agent, Coalition


class PriceResult(NamedTuple):
    """
    A named tuple to store the price of anarchy, the price of stability and the corresponding coalition structures.
    """

    poa: float
    """Price of anarchy"""

    pos: float
    """Price of stability"""

    pom: float
    """Average price of the Nash equilibria"""

    cs_worst: 'CoalitionStructure'
    """Coalition structure with the worst price"""

    cs_best: 'CoalitionStructure'
    """Coalition structure with the best price"""

    cs_count: int
    """Number of Nash equilibria found"""


class Graph:
    """
    The class represents a weighted directed or undirected graph, according to the value of the field is_directed.
    """

    weights: IntArray2D
    """
    The weight matrix of the graph. Its values should be non-negative integers.
    """

    _is_directed: bool
    """
    Whether the graph is directed or not. If True, the matrix weights should be symmetric.
    """

    def __init__(self, weights: IntArray2D, is_directed: bool | None = None):
        """
        Creates a graph from the given weights.

        The weights matrix should be square and its values should be non-negative integers. If the graph is
        undirected the matrix should be symmetric, while the opposite is not generally required.  However,
        if the parameter is_directed is not provided, its value is inferred from the weights matrix. If the
        matrix is symmetric, the graph is undirected, otherwise it is directed.
        """
        assert weights.ndim == 2 and weights.shape[0] == weights.shape[1], "The weights matrix should be square."
        assert np.all(weights >= 0), "The weights matrix should contain only non-negative integers."
        assert is_directed is not False or np.array_equal(weights, weights.T), (
            "The graph is undirected, but the weights matrix is not symmetric."
        )
        self.weights = weights
        self._is_directed = is_directed if is_directed is not None else not np.array_equal(weights, weights.T)

    def __eq__(self, value: object) -> bool:
        """
        Compare the graph with another object.

        The graph is equal to another object if the latter is a graph with the same weights and the
        same directedness.
        """
        if not isinstance(value, Graph):
            return False
        return np.array_equal(self.weights, value.weights) and self.is_directed() == value.is_directed()

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

        For each edge, the tuple (i, j, w) is returned where w is the weight of the edge (i, j).
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
            edge = pydot.Edge(str(i), str(j)) if self.is_simple() else pydot.Edge(str(i), str(j), label=str(w))
            graph.add_edge(edge)
        return graph

    @classmethod
    def from_nx_graph(cls, graph: nx.Graph | nx.DiGraph) -> 'Graph':
        """
        Convert a networkx graph to the `Graph` class.

        All weights should be non-negative integers.
        """
        assert all(
            isinstance(weight, int) or weight is None
            for _, _, weight in graph.edges(data="weight")  # type: ignore[arg-type]
        ), "The weights of the edges should be non-negative integers."

        weights = np.zeros((len(graph.nodes), len(graph.nodes)), dtype=np.int_)
        for i, j, weight in graph.edges(data='weight'):  # type: ignore[arg-type]
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
    def enumerate(cls, n: int, is_directed: bool, m_min: int, m_max: int) -> Iterator['Graph']:
        """
        Iterates over all the graphs with n nodes, with the given directedness. The values m_min and m_max
        are the minimum and maximum value of m, where m is the maximum weight of the edges. For example,
        if one wants to generate only simple graphs, m_max should be set to 1 and m_min to 0.

        The graphs are generated in a lexicographic order. Some attempt is made to generate the graphs in a canonical
        form, avoiding isomorphism variants of the same graph. However, isomophic variants of the same graph are
        almost always generated.
        """
        for weights in hgimpl.games(n, not is_directed, m_min, m_max):
            yield cls(weights, is_directed)


class HedonicGame:

    graph: Graph
    """
    The graph encoding the agents and their valuations.
    """

    k: int | None
    """
    The maximum size of the coalitions.

    If None, there is no limit on the size of the coalitions. If it is an integer, it should be non-negative.
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
        Return the valuations of the game. The valuations are represented as a matrix, where the i-th row
        contains the valuations of the i-th agent for all the other agents.
        """
        return self.graph.weights

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
        Return whether the game is simple or not. A game is simple if weights are all 0 or 1.
        """
        return self.graph.is_simple()

    def __init__(self, graph: Graph | IntArray2D, k: int | None = None, is_fractional: bool = True):
        """
        Creates a hedonic game from the given graph.
        """
        assert k is None or k >= 0, "The maximum size of the coalitions should be non-negative."
        assert not isinstance(graph, Graph) or (graph.is_directed != np.array_equal(graph.weights, graph.weights.T)), (
            "The graph is directed, but the weights matrix is symmetric."
        )
        self.graph = graph if isinstance(graph, Graph) else Graph(graph)
        self.k = k
        self._is_fractional = is_fractional

    def __eq__(self, value: object) -> bool:
        """
        Compare the game with another object.

        A game is equal to another object if the latter is a game with the same weights and same
        values of k and is_fractional.
        """
        if not isinstance(value, HedonicGame):
            return False
        return self.graph == value.graph and self.k == value.k and self.is_fractional() == value.is_fractional()

    def coalition_structures(self, cs_size: int | None = None) -> Iterator['CoalitionStructure']:
        """
        Iterates over the coalition structures of the game.

        If provided, `cs_size` restrict the coalitions structures to those with the specified number of coalitions.
        """
        assert cs_size is None or cs_size >= 0, "The number of coalitions should be non-negative."
        if cs_size is not None:
            for cs in hgimpl.css_givensize(self.agent_count, cs_size, self.k):
                yield CoalitionStructure(self, cs)
        else:
            for cs in hgimpl.css(self.agent_count, self.k):
                yield CoalitionStructure(self, cs)

    def isolated_coalition_structure(self) -> 'CoalitionStructure':
        """
        Return the isolated coalition structure of the game.

        The isolated coalition structure is the one where each agent is in its own coalition.
        """
        return CoalitionStructure(self, np.arange(self.agent_count))

    def big_coalition_structure(self) -> 'CoalitionStructure':
        """
        Return the big coalition structure of the game.

        The big coalition structure is the one where all agents are in the same coalition. If this is not a valid
        coalition structure, an exception is raised.
        """
        if self.k is not None and self.k < self.agent_count:
            raise ValueError("The big coalition structure is not valid.")
        return CoalitionStructure(self, np.zeros(self.agent_count, dtype=np.int_))

    def nash_stable_coalition_structures(self) -> Iterator['CoalitionStructure']:
        """
        Iterates over the Nash stable coalition structures of the game.
        """
        for cs in hgimpl.nash_equilibria(self.valuations, self.is_fractional(), self.k):
            yield CoalitionStructure(self, cs)

    def has_nash_stable_coalition_structure(self) -> bool:
        """
        Return whether the game has a Nash stable coalition structure.
        """
        return hgimpl.nash_equilibrium(self.valuations, self.is_fractional(), self.k) is not None

    def optimal_coalition_structure(self) -> tuple['CoalitionStructure', int]:
        """
        Return one of the optimal coalition structures of the game and the corresponding social welfare.
        """
        if self.is_directed():
            raise ValueError("The game is directed, cannot compute optimal coalition structure.")
        if self.k != 2:
            raise ValueError("k is different from 2, cannot compute the optimal coalition structure.")

        g = self.graph.to_nx_graph()
        matching = nx.max_weight_matching(g)
        welfare = sum(g[u][v]['weight'] for u, v in matching)
        if not self.is_fractional():
            welfare *= 2
        cs = np.zeros(self.agent_count, dtype=np.int_)
        for n, (i, j) in enumerate(matching):
            cs[i] = n
            cs[j] = n
        return CoalitionStructure(self, cs), welfare

    def prices(self) -> PriceResult | None:
        """
        Return the prices of anarchy and the price of stability for the game.

        It also returns examples of the coalition structures that achieve them. If the game has no Nash
        stable coalition structure, the result is None.
        """
        poa = float('-inf')
        cs_worst = None
        pos = float('inf')
        cs_best = None
        _, opt = self.optimal_coalition_structure()
        cs_count = 0
        pom = 0.0
        for cs in self.nash_stable_coalition_structures():
            cs_count += 1
            price = opt / cs.social_welfare()
            pom += price
            if price > poa:
                poa = price
                cs_worst = cs
            if price < pos:
                pos = price
                cs_best = cs
        return None if cs_worst is None or cs_best is None \
            else PriceResult(poa, pos, pom / cs_count, cs_worst, cs_best, cs_count)

    def __repr__(self) -> str:
        return f"HedonicGame({repr(self.valuations)}, k={self.k}, is_fractional={self.is_fractional()}))"

    def __str__(self) -> str:
        return f"{str(self.valuations)}, k={self.k}, is_fractional={self.is_fractional()}"


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

    The i-th element is the coalition number of the i-th agent. Elements of cs are all and only the
    integers in the range [0, max(cs)].
    """

    _sizes: IntArray1D
    """
    The sizes of the coalitions in the coalition structure.
    """

    @staticmethod
    def _normalize(cs: IntArray1D) -> None:
        """
        Normalize the coalition structure.

        The coalition numbers are shifted to be in the range [0, size-1] and they appear in increasing order.
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

        The coalition structure is represented as an array of integers, where the i-th element is the coalition
        number of the i-th agent. Elements of cs are all and only the integers in the range [0, max(cs)].
        New coalitions indexes should appear for the first time in the order of their number. Therefore
        `[0, 2, 0, 1]` is not a valid coalition structure, because the coalition `1` appears for the first time
        before the coalition `2`. However, `[0, 1, 0, 2]` is a valid coalition structure.
        """
        assert len(cs) == game.agent_count, "The coalition structure should have the same size as the number of agents."
        assert np.all(cs >= 0), "The coalition structure should contain only non-negative integers."
        assert max(cs)+1 == len(np.unique(cs)), "The coalition structure should contain all integers from `0` to `max(cs)`."

        self.game = game
        self.cs = cs
        self._sizes = np.bincount(cs, minlength=len(cs))

    def __eq__(self, value: object) -> bool:
        """
        Compare the coalition structure with another object.

        The coalition structure is equal to another object if the latter is a coalition structure with the same
        game and the same coalitions.
        """
        if not isinstance(value, CoalitionStructure):
            return False
        return self.game == value.game and np.array_equal(self.cs, value.cs)

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

    def agent_utility(self, ag: Agent) -> int | float:
        """
        Returns the utility of the given agent.
        """
        assert 0 <= ag < len(self.cs), "Agent number out of range."
        val, size = hgimpl.agent_utility(self.game.valuations, self.cs, ag)
        return val / size if self.game.is_fractional() else val

    def coalition_social_welfare(self, co: Coalition) -> int | float:
        """
        Returns the social welfare of the given coalition.
        """
        assert 0 <= co < self.size, "Coalition number out of range."
        ut, size = hgimpl.coalition_social_welfare(self.game.valuations, self.cs, co)
        return ut / size if self.game.is_fractional() else ut

    def social_welfare(self) -> int | float:
        """

        Returns the social welfare of the coalition structure.
        """
        return sum(self.coalition_social_welfare(co) for co in self.coalitions())

    def is_improving_deviation(self, ag: Agent, co_new: Coalition) -> bool:
        """
        Determine if the given agent can improve its utility by moving to the new coalition.

        Note that co_new may be one larger than the current coalition structure size. This means that
        the agent ag is moving its current coalition to form a new coalition alone.
        """
        assert 0 <= ag < len(self.cs), "Agent number out of range."
        assert 0 <= co_new <= self.size, "Coalition number out of range."
        if self.game.k is not None and self._sizes[co_new] == self.game.k:
            return False
        co_old = self.cs[ag]
        if co_old == co_new:
            return False
        ut_old, size_old = hgimpl.agent_utility(self.game.valuations, self.cs, ag)
        ut_new, size_new = hgimpl.agent_utility_co(
            self.game.valuations, self.cs, ag, co_new)
        if not self.game.is_fractional:
            return ut_new > ut_old
        elif ut_old == ut_new == 0:
            return size_new+1 < size_old
        else:
            return ut_new * size_old > ut_old * (size_new + 1)

    def improving_deviations_for_agents(self, ag: Agent) -> Iterable[Coalition]:
        """
        Iterates over the improving deviations of the given agent.

        The improving deviations are the coalitions to which the agent can move to improve its utility.
        """
        assert 0 <= ag < len(self.cs), "Agent number out of range."
        for co_new in range(self.size+1):
            if self.is_improving_deviation(ag, co_new):
                yield co_new

    def improving_deviations(self) -> Iterable[tuple[Agent, Coalition]]:
        """
        Iterates over the improving deviations of the coalition structure.

        The improving deviations are the pairs (agent, coalition) such that the agent can move to the coalition
        to improve its utility.
        """
        for ag in self.game.agents():
            for co_new in self.improving_deviations_for_agents(ag):
                yield ag, co_new

    def move_to(self, ag: Agent, co_new: Coalition) -> 'CoalitionStructure':
        """
        Move the given agent to the new coalition and return the new coalition structure we obtain in this way.
        """
        assert 0 <= ag < len(self.cs), "Agent number out of range."
        assert 0 <= co_new <= self.size, "Coalition number out of range."
        assert self.game.k is None or self._sizes[co_new] < self.game.k, "The target coalition size is too large."
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
            for co_new in range(self.size+1) if co_new != self.cs[ag]
        )

    def is_nash_stable(self) -> bool:
        """
        Determine if the coalition structure is Nash stable.
        """
        return all(self.is_agent_nash_stable(ag) for ag in (self.game.agents()))

    def to_list(self) -> list[set[int]]:
        """
        Return the coalition structure as a list of sets. Each set contains the agents in the corresponding coalition.
        """
        s = [set[int]() for _ in range(self.size)]
        for ag in self.game.agents():
            s[self.cs[ag]].add(ag)
        return s

    def __repr__(self) -> str:
        return f"CoalitionStructure({repr(self.game)},{repr(self.cs)})"

    def __str__(self) -> str:
        return str(self.to_list())


GAME_K3_NOEQUILIBRIUM_PAPER = HedonicGame(np.array([
    [0, 9, 9, 4],
    [9, 0, 1, 7],
    [9, 1, 0, 7],
    [4, 7, 7, 0]
]), is_fractional=True, k=3)

GAME_K3_NOEQUILIBRIUM = HedonicGame(np.array([
    [0, 0, 5, 7],
    [0, 0, 5, 7],
    [5, 5, 0, 3],
    [7, 7, 3, 0]
]), is_fractional=True, k=3)

GAME_K4_NOEQUILIBRIUM = HedonicGame(np.array([
    [0, 0, 0, 5, 10],
    [0, 0, 6, 4, 9],
    [0, 6, 0, 10, 0],
    [5, 4, 10, 0, 10],
    [10, 9, 0, 10, 0]
]), is_fractional=True, k=4)

GAME_K5_NOEQUILIBRIUM = HedonicGame(np.array([
    [0, 0, 0, 0, 2, 2],
    [0, 0, 0, 2, 0, 2],
    [0, 0, 0, 2, 2, 1],
    [0, 2, 2, 0, 0, 2],
    [2, 0, 2, 0, 0, 2],
    [2, 2, 1, 2, 2, 0]
]), is_fractional=True, k=5)

GAME_K6_NOEQUILIBRIUM = HedonicGame(np.array([
    [0, 0, 0, 0, 1, 1, 3],
    [0, 0, 1, 3, 0, 1, 2],
    [0, 1, 0, 3, 0, 3, 3],
    [0, 3, 3, 0, 0, 3, 2],
    [1, 0, 0, 0, 0, 3, 1],
    [1, 1, 3, 3, 3, 0, 0],
    [3, 2, 3, 2, 1, 0, 0]
]), is_fractional=True, k=6)

GAME_K7_NOEQUILIBRIUM = HedonicGame(np.array([
    [0, 0, 0, 0, 0, 0, 1, 2],
    [0, 0, 0, 0, 0, 0, 2, 2],
    [0, 0, 0, 0, 0, 2, 1, 2],
    [0, 0, 0, 0, 1, 2, 1, 0],
    [0, 0, 0, 1, 0, 2, 2, 0],
    [0, 0, 2, 2, 2, 0, 2, 0],
    [1, 2, 1, 1, 2, 2, 0, 2],
    [2, 2, 2, 0, 0, 0, 2, 0]
]), is_fractional=True, k=7)

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
]), is_fractional=True, k=7)

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
]), is_fractional=True, k=8)
