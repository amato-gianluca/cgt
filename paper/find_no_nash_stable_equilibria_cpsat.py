"""
This script looks for games with no Nash stable coalition structures using constraint programming.
It uses the OR-Tools CP-SAT.
"""

from functools import cache
from math import comb

from more_itertools import set_partitions
import numpy as np

from ortools.sat.python import cp_model
from ortools.sat.python.cp_model import IntVar, CpModel, CpSolver, LiteralT

type Agent = int
type Coalition = tuple[Agent, ...]
type CoalitionStructure = tuple[Coalition, ...]
type Graph = tuple[tuple[IntVar, ...], ...]


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
    model: CpModel,
    graph: Graph,
    source_coalition: Coalition,
    target_coalition: Coalition,
    agent: Agent,
) -> list[LiteralT]:
    """
    Check whether an agent has an improving deviation from a source coalition to a target coalition.
    """
    target_coalition = target_coalition + (agent,)
    source_utility = sum(graph[agent][a] for a in source_coalition if a != agent)
    target_utility = sum(graph[agent][a] for a in target_coalition if a != agent)
    b1 = model.new_bool_var(f"id_base_{source_coalition}_{target_coalition}_{agent}")
    model.add(
        len(source_coalition) * target_utility > len(target_coalition) * source_utility
    ).only_enforce_if(b1)
    if len(target_coalition) < len(source_coalition):
        b2 = model.new_bool_var(f"id_zero_{source_coalition}_{target_coalition}_{agent}")
        model.add(source_utility == 0).only_enforce_if(b2)
        model.add(target_utility == 0).only_enforce_if(b2)
        return [b1, b2]
    else:
        return [b1]


def is_not_nash_stable(
    model: CpModel, graph: Graph, coalition_structure: CoalitionStructure, k: int
):
    """
    Check whether a coalition structure has an improving deviation.
    """
    deviations: list[LiteralT] = []
    for source_coalition in coalition_structure:
        for target_coalition in coalition_structure + ((),):
            if len(target_coalition) == k:
                continue
            if len(source_coalition) == 1 and len(target_coalition) == 0:
                continue
            for agent in source_coalition:
                deviations += is_improving_deviation(
                    model, graph, source_coalition, target_coalition, agent
                )
    model.add_bool_or(deviations)


def has_no_nash_stable_coalition_structure(model: CpModel, graph: Graph, k: int):
    """
    Check whether the game has a Nash stable equilibrium.
    """
    num_constraints = count_partitions(len(graph), k)
    print(f"Generating constraints for all {num_constraints} coalition structures")
    for i, coalition_structure in enumerate(set_partitions(range(len(graph)), max_size=k)):
        if i % 1000 == 999:
            print(f"Coalition structure {i + 1}/{num_constraints}", end="\r")
        coalition_structure = tuple(tuple(c) for c in coalition_structure)
        is_not_nash_stable(model, graph, coalition_structure, k)
    print(f"Coalition structure {num_constraints}/{num_constraints}")


def base_constraints(model: CpModel, graph: Graph, m: int, is_symmetric: bool = True):
    """
    Base constraints for the graph.
    """
    for i in range(len(graph)):
        model.add(graph[i][i] == 0)
        for j in range(i):
            if is_symmetric:
                model.add(graph[i][j] == graph[j][i])


def model_to_graph(solver: CpSolver, graph: Graph) -> np.ndarray:
    """
    Convert a solved model to a graph.
    """
    n = len(graph)
    g = np.zeros((n, n), dtype=np.int_)
    for i in range(n):
        for j in range(n):
            g[i, j] = solver.value(graph[i][j])
    return g


def main():
    # K = 6
    # N = 7
    # M = 2

    K = 4
    N = 8
    M = 1

    model = cp_model.CpModel()
    graph = [[model.new_int_var(0, M, f"v{i, j}") for j in range(N)] for i in range(N)]
    graph = tuple(map(tuple, graph))

    base_constraints(model, graph, M)
    has_no_nash_stable_coalition_structure(model, graph, K)
    print(model.model_stats())

    print(is_improving_deviation.cache_info())

    print("Solving the model...")
    solver = cp_model.CpSolver()
    status = solver.solve(model)

    if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
        g = model_to_graph(solver, graph)
        print(g)
    else:
        print("No graph with no Nash stable coalition structure found.")


main()
