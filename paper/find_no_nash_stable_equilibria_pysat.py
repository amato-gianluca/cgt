"""
This script looks for games with no Nash stable coalition structures using propositional satisfiability.
It uses the PySAT library.
"""

import argparse
from functools import cache
from math import comb
from typing import Any

import numpy as np
from more_itertools import set_partitions
from pysat.formula import Atom, IDPool
from pysat.pb import PBEnc
from pysat.solvers import Kissat404

type Agent = int
type Coalition = tuple[Agent, ...]
type CoalitionStructure = tuple[Coalition, ...]
type Graph = tuple[tuple[Any, ...], ...]
type Solver = Kissat404

vpool = IDPool()


@cache
def count_partitions(n, max_size):
    """
    Count the number of partitions of n elements into groups of size at most max_size.
    """
    if n == 0:
        return 1
    total = 0
    for s in range(1, min(max_size, n) + 1):
        total += comb(n - 1, s - 1) * count_partitions(n - s, max_size)

    return total


@cache
def is_improving_deviation(
    solver: Solver,
    graph: Graph,
    source_coalition: Coalition,
    target_coalition: Coalition,
    agent: Agent,
) -> list[int]:
    """
    Add clauses for an improving deviation from a source coalition to a target coalition.

    The returned literals are deviation indicators.  At least one of them must be true for this
    deviation to be available.
    """
    target_coalition = target_coalition + (agent,)
    target_vars = [graph[agent][a] for a in target_coalition if a != agent]
    source_vars = [graph[agent][a] for a in source_coalition if a != agent]
    target_lits = [v.name for v in target_vars]
    source_lits = [v.name for v in source_vars]
    s = len(source_coalition)
    t = len(target_coalition)
    b = vpool.id(f"id_{source_coalition}_{target_coalition}_{agent}")
    # PBEnc expects non-negative weights.  Rewrite
    #   s * target_utility - t * source_utility >= 1
    # as
    #   s * target_utility + t * (1 - source_edges) >= 1 + t * |source_edges|.
    pb = PBEnc.geq(
        lits=target_lits + [-lit for lit in source_lits],
        weights=[s] * len(target_lits) + [t] * len(source_lits),
        bound=1 + t * len(source_lits),
        vpool=vpool,
        conditionals=[b],
    )
    assert not pb.atmosts
    solver.append_formula(pb.clauses)
    if len(target_coalition) < len(source_coalition):
        z = vpool.id(f"id_zero_{source_coalition}_{target_coalition}_{agent}")
        for var in target_lits + source_lits:
            solver.add_clause([-z, -var])
        return [b, z]
    else:
        return [b]


def is_not_nash_stable(
    solver: Solver, graph: Graph, coalition_structure: CoalitionStructure, k: int
):
    """
    Check whether a coalition structure has an improving deviation.
    """
    deviation_lits = []
    for source_coalition in coalition_structure:
        for target_coalition in coalition_structure + ((),):
            if len(target_coalition) == k:
                continue
            if len(source_coalition) == 1 and len(target_coalition) == 0:
                continue
            if source_coalition == target_coalition:
                continue
            for agent in source_coalition:
                deviation_lits += is_improving_deviation(
                    solver, graph, source_coalition, target_coalition, agent
                )
    solver.add_clause(deviation_lits)


def has_no_nash_stable_coalition_structure(solver: Solver, graph: Graph, k: int):
    """
    Check whether the game has a Nash stable equilibrium.
    """
    num_constraints = count_partitions(len(graph), k)
    print(f"Generating constraints for all {num_constraints} coalition structures")
    for i, coalition_structure in enumerate(set_partitions(range(len(graph)), max_size=k)):
        if i % 1000 == 0:
            print(f"Coalition structure {i}/{num_constraints}", end="\r")
        coalition_structure = tuple(tuple(c) for c in coalition_structure)
        is_not_nash_stable(solver, graph, coalition_structure, k)
    print(f"Coalition structure {num_constraints}/{num_constraints}")


def base_constraints(solver: Solver, graph: Graph, is_symmetric: bool = True):
    """
    Base constraints for the graph.
    """
    for i in range(len(graph)):
        solver.append_formula(~graph[i][i])
        for j in range(i):
            if is_symmetric:
                solver.append_formula(graph[i][j] @ graph[j][i])


def model_to_graph(model, graph: Graph) -> np.ndarray:
    """
    Convert a solved model to a graph.
    """
    n = len(graph)
    g = np.zeros((n, n), dtype=np.int_)
    for i in range(n):
        for j in range(n):
            g[i, j] = 1 if graph[i][j].name in model else 0
    return g


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("k", type=int, help="upper bound on the size of coalitions")
    parser.add_argument("n", type=int, help="number of agents in the game")
    args = parser.parse_args()

    K = args.k
    N = args.n

    graph = [[Atom(vpool.id(f"v{i, j}")) for j in range(N)] for i in range(N)]
    graph = tuple(map(tuple, graph))

    print("Solving...")
    with Kissat404() as solver:
        base_constraints(solver, graph)
        has_no_nash_stable_coalition_structure(solver, graph, K)

        print(is_improving_deviation.cache_info())

        if solver.solve():
            model = solver.get_model()
            g = model_to_graph(model, graph)
            print(g)
        else:
            print("No graph with no Nash stable coalition structure found.")


main()
