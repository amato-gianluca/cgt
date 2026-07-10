"""
This script looks for games with no Nash stable coalition structures using propositional satisfiability.
It uses the Z3 SMT solver.
"""

from functools import cache
from math import comb

from more_itertools import set_partitions
import numpy as np
from z3 import Int, ArithRef, BoolRef, BoolVal, And, Or, Solver, SolverFor, sat

type Agent = int
type Coalition = tuple[int, ...]
type CoalitionStructure = tuple[Coalition, ...]
type Graph = tuple[tuple[ArithRef, ...], ...]


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
    graph: Graph, source_coalition: Coalition, target_coalition: Coalition, agent: Agent
) -> BoolRef:
    """
    Check whether an agent has an improving deviation from a source coalition to a target coalition.
    """
    target_coalition = target_coalition + (agent,)
    source_utility: ArithRef = sum(graph[agent][a] for a in source_coalition)  # type: ignore
    target_utility: ArithRef = sum(graph[agent][a] for a in target_coalition)  # type: ignore
    condition = len(source_coalition) * target_utility > len(target_coalition) * source_utility
    if len(target_coalition) < len(source_coalition):
        condition = Or(condition, (And(source_utility == 0, target_utility == 0)))
    return condition  # type: ignore


def is_not_nash_stable(graph: Graph, coalition_structure: CoalitionStructure, k: int) -> BoolRef:
    """
    Check whether a coalition structure has an improving deviation.
    """
    condition: BoolRef = BoolVal(False)  # type: ignore
    for source_coalition in coalition_structure:
        for target_coalition in coalition_structure + ((),):
            if len(target_coalition) == k:
                continue
            if len(source_coalition) == 1 and len(target_coalition) == 0:
                continue
            for agent in source_coalition:
                condition = Or(
                    condition,
                    is_improving_deviation(graph, source_coalition, target_coalition, agent),
                )  # type: ignore
    return condition


def has_no_nash_stable_coalition_structure(graph: Graph, k: int) -> list[BoolRef]:
    """
    Check whether the game has a Nash stable equilibrium.
    """
    constraints: list[BoolRef] = []
    num_constraints = count_partitions(len(graph), k)
    print(f"Generating constraints for all {num_constraints} coalition structures")
    for i, coalition_structure in enumerate(set_partitions(range(len(graph)), max_size=k)):
        if i % 1000 == 999:
            print(f"Coalition structure {i + 1}/{num_constraints}", end="\r")
        coalition_structure = tuple(tuple(c) for c in coalition_structure)
        constraints.append(is_not_nash_stable(graph, coalition_structure, k))
    print(f"Coalition structure {num_constraints}/{num_constraints}")
    return constraints


def base_constraints(graph: Graph, m: int, is_symmetric: bool = True) -> list[BoolRef]:
    """
    Base constraints for the graph.
    """
    constraints: list[BoolRef] = []
    for i in range(len(graph)):
        constraints.append(graph[i][i] == 0)  # type: ignore
        for j in range(i):
            constraints.append(graph[i][j] >= 0)
            constraints.append(graph[i][j] <= m)
            if is_symmetric:
                constraints.append(graph[i][j] == graph[j][i])  # type: ignore
    return constraints


def model_to_graph(model, graph: Graph) -> np.ndarray:
    """
    Convert a Z3 model to a graph.
    """
    n = len(graph)
    g = np.zeros((n, n), dtype=np.int_)
    for i in range(n):
        for j in range(n):
            g[i, j] = model[graph[i][j]].as_long()
    return g


def save_model(s: Solver, filename: str = "constraints.smt2"):
    """
    Save the Z3 model to a file.
    """
    with open(filename, "w") as f:
        f.write("(set-option :produce-models true)\n")
        f.write("(set-logic QF_LIA)\n")
        f.write(s.to_smt2())
        f.write("\n(get-model)\n")


def main():
    # K = 6
    # N = 7
    # M = 1

    K = 4
    N = 8
    M = 1

    graph = [[Int(f"v{i, j}") for j in range(N)] for i in range(N)]
    graph = tuple(map(tuple, graph))
    constraints = base_constraints(graph, M)
    constraints += has_no_nash_stable_coalition_structure(graph, K)

    print(is_improving_deviation.cache_info())

    print("Solving...")
    s = SolverFor("QF_LIA")
    s.add(constraints)
    save_model(s)

    result = s.check()

    if result == sat:
        m = s.model()
        g = model_to_graph(m, graph)
        print(g)
    else:
        print("No graph with no Nash stable coalition structure found.")


main()
