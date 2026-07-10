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
from pysat.formula import Atom, Formula, IDPool, CNF, CNFPlus, And
from pysat.pb import PBEnc

type Agent = int
type Coalition = tuple[Agent, ...]
type CoalitionStructure = tuple[Coalition, ...]
type Graph = tuple[tuple[Any, ...], ...]


vpool = IDPool()
true_var = vpool.id("__true__")
false_var = vpool.id("__false__")
PYSAT_TRUE = Atom(true_var) | ~Atom(true_var)
PYSAT_FALSE = Atom(false_var) & ~Atom(false_var)


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

def cnf_to_formula(cnf: CNFPlus) -> Formula:
    assert not cnf.atmosts
    clauses = cnf.clauses
    if len(clauses) == 0:
        return PYSAT_TRUE
    if any(len(c) == 0 for c in clauses):
        return PYSAT_FALSE
    return CNF(from_clauses=clauses)


@cache
def is_improving_deviation(
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
    pb = PBEnc.geq(
        lits=target_lits + source_lits,
        weights=[s] * len(target_lits) + [-t] * len(source_lits),
        bound=1,
        vpool=vpool,
    )
    formula1 = cnf_to_formula(pb)
    if len(target_coalition) < len(source_coalition):
        formula2 = reduce(and_, (~v for v in target_vars + source_vars))
        return formula1 | formula2
    else:
        return formula1


def is_not_nash_stable(graph: Graph, coalition_structure: CoalitionStructure, k: int) -> Formula:
    """
    Check whether a coalition structure has an improving deviation.
    """
    constraints: list[Formula] = []
    for source_coalition in coalition_structure:
        for target_coalition in coalition_structure + ((),):
            if len(target_coalition) == k:
                continue
            if len(source_coalition) == 1 and len(target_coalition) == 0:
                continue
            if source_coalition == target_coalition:
                continue
            for agent in source_coalition:
                #print(source_coalition, target_coalition, agent)
                dev = is_improving_deviation(graph, source_coalition, target_coalition, agent)
                #dev.clausify()
                #print(dev)
                #print(dev.clauses)
                constraints.append(dev)
    return reduce(or_, constraints) if constraints else PYSAT_FALSE


def has_no_nash_stable_coalition_structure(graph: Graph, k: int) -> list[Formula]:
    """
    Check whether the game has a Nash stable equilibrium.
    """
    constraints: list[Formula] = []
    num_constraints = count_partitions(len(graph), k)
    print(f"Generating constraints for all {num_constraints} coalition structures")
    for i, coalition_structure in enumerate(set_partitions(range(len(graph)), max_size=k)):
        if i % 1000 == 999:
            print(f"Coalition structure {i + 1}/{num_constraints}", end="\r")
        coalition_structure = tuple(tuple(c) for c in coalition_structure)
        constraints.append(is_not_nash_stable(graph, coalition_structure, k))
    print(f"Coalition structure {num_constraints}/{num_constraints}")
    return constraints


def base_constraints(graph: Graph, is_symmetric: bool = True) -> list[Formula]:
    """
    Base constraints for the graph.
    """
    constraints: list[Formula] = []
    for i in range(len(graph)):
        constraints.append(~graph[i][i])
        for j in range(i):
            if is_symmetric:
                constraints.append(graph[i][j] @ graph[j][i])
    return constraints


def main():
    K = 4
    N = 8

    graph = [[Atom(vpool.id(f"v{i, j}")) for j in range(N)] for i in range(N)]
    graph = tuple(map(tuple, graph))

    formulas = base_constraints(graph)
    formulas += has_no_nash_stable_coalition_structure(graph, K)

    print(is_improving_deviation.cache_info())

    big_formula = And(*formulas)
    big_formula.clausify()
    clauses = list(big_formula)

    print(f"Generated {len(clauses)} clauses and {vpool.top} variables.")
    print("Solving...")
    with Kissat404(bootstrap_with=clauses) as solver:
        if solver.solve():
            model = solver.get_model()
            print(model)
        else:
            print("No graph with no Nash stable coalition structure found.")

main()
