"""
This script looks for games with no Nash stable coalition structures using propositional satisfiability.
It uses the PySAT library.
"""

from functools import cache, reduce
from math import comb
from operator import and_, or_
from typing import Any

from more_itertools import set_partitions

from pysat.solvers import Kissat404
from pysat.formula import Atom, Formula, IDPool, PYSAT_FALSE
from pysat.pb import PBEnc

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
) -> Formula:
    """
    Check whether an agent has an improving deviation from a source coalition to a target coalition.
    """
    target_coalition = target_coalition + (agent,)
    target_vars = [graph[agent][a] for a in target_coalition if a != agent]
    source_vars = [graph[agent][a] for a in source_coalition if a != agent]
    target_lits = [v.name for v in target_vars]
    source_lits = [v.name for v in source_vars]
    s = len(source_coalition)
    t = len(target_coalition)
    b = Atom(vpool.id(f"id_{source_coalition}_{target_coalition}_{agent}"))
    pb = PBEnc.geq(
        lits=target_lits + source_lits,
        weights=[s] * len(target_lits) + [-t] * len(source_lits),
        bound=1,
        vpool=vpool,
        conditionals=[b.name],
    )
    assert not pb.atmosts
    solver.append_formula(pb.clauses)
    if len(target_coalition) < len(source_coalition):
        formula2 = reduce(and_, [~v for v in target_vars + source_vars])
        return b | formula2
    else:
        return b


def is_not_nash_stable(
    solver: Solver, graph: Graph, coalition_structure: CoalitionStructure, k: int
):
    """
    Check whether a coalition structure has an improving deviation.
    """
    formulas = []
    for source_coalition in coalition_structure:
        for target_coalition in coalition_structure + ((),):
            if len(target_coalition) == k:
                continue
            if len(source_coalition) == 1 and len(target_coalition) == 0:
                continue
            if source_coalition == target_coalition:
                continue
            for agent in source_coalition:
                # print(source_coalition, target_coalition, agent)
                dev = is_improving_deviation(
                    solver, graph, source_coalition, target_coalition, agent
                )
                # print(dev)
                # print(list(dev))
                formulas.append(dev)
    formula = reduce(or_, formulas) if formulas else PYSAT_FALSE
    solver.append_formula(formula)


def has_no_nash_stable_coalition_structure(solver: Solver, graph: Graph, k: int):
    """
    Check whether the game has a Nash stable equilibrium.
    """
    num_constraints = count_partitions(len(graph), k)
    print(f"Generating constraints for all {num_constraints} coalition structures")
    for i, coalition_structure in enumerate(set_partitions(range(len(graph)), max_size=k)):
        if i % 1000 == 999:
            print(f"Coalition structure {i + 1}/{num_constraints}", end="\r")
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


def main():
    K = 6
    N = 11

    graph = [[Atom(vpool.id(f"v{i, j}")) for j in range(N)] for i in range(N)]
    graph = tuple(map(tuple, graph))

    print("Solving...")
    with Kissat404() as solver:
        base_constraints(solver, graph)
        has_no_nash_stable_coalition_structure(solver, graph, K)

        print(is_improving_deviation.cache_info())

        if solver.solve():
            model = solver.get_model()
            print(model)
        else:
            print("No graph with no Nash stable coalition structure found.")


main()
