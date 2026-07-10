"""
This script is an attempt to find a potential function for the dynamics of a 6-SSFH games.

The potential is based on the entire data for a coalition, instead of syntetic data such as size
and utility.

Unfortunately, the potential is still based on single coalitions, and this approach cannot work
since we know there are cyclces in the dynamics of 6-SSFH games. We should write a potential
function that is based on the entire coalition structure, so that we can filter out part of the
dynamics, for example limiting ourselves to best responses. However, this does not seem to be
feasible.
"""

import sys
from itertools import combinations_with_replacement, product
import networkx as nx

from z3 import Int, solve, ArithRef

k = 5

type CoalitionData = tuple[int, ...]

vars: dict[CoalitionData, ArithRef] = {}

alpha = [Int(f"a{i}") for i in range(k + 1)]
beta = [Int(f"b{i}") for i in range(k + 1)]


def graphical_degree_sequences(n):
    for degrees in combinations_with_replacement(range(n), n):
        if nx.is_graphical(degrees):
            yield degrees


def sum_utilities(coalition: CoalitionData, additional_utilities: tuple[int, ...]) -> CoalitionData:
    """
    Add a new agent with additional utilities to the coalition and return the new coalition as a sorted tuple.
    """
    newtuple = [coalition[i] + additional_utilities[i] for i in range(len(coalition))]
    return tuple(sorted(newtuple + [sum(additional_utilities)]))


def phi1(coalition: CoalitionData) -> ArithRef:
    """
    The generic potential function.
    """
    if len(coalition) > k:
        raise ValueError(f"Coalition size {len(coalition)} exceeds maximum size {k}.")
    if coalition not in vars:
        vars[coalition] = Int(f"phi_{'_'.join(map(str, coalition))}")
    return vars[coalition]


def phi2(coalition: CoalitionData) -> ArithRef:
    """
    The simplified potential function.
    """
    if len(coalition) > k:
        raise ValueError(f"Coalition size {len(coalition)} exceeds maximum size {k}.")
    co_size = len(coalition)
    utility = sum(coalition)
    return utility * alpha[co_size] + beta[co_size]


phi = phi1

constraints = []
for source_size in range(k):
    for target_size in range(k):
        print(
            f"Generating constraints for source size {source_size} and target size {target_size}...\r",
            file=sys.stderr,
            end="",
        )
        for source_utilities in graphical_degree_sequences(source_size):
            for agent_source_utilities in product((0, 1), repeat=source_size):
                for target_utilities in graphical_degree_sequences(target_size):
                    for agent_target_utilities in product((0, 1), repeat=target_size):
                        source_utility = sum(source_utilities)
                        target_utility = sum(target_utilities)
                        agent_source_utility = sum(agent_source_utilities)
                        agent_target_utility = sum(agent_target_utilities)

                        # fmt: off
                        if (
                            agent_target_utility * (source_size + 1) > agent_source_utility * (target_size + 1) or
                            agent_source_utility == agent_target_utility == 0 and target_size < source_size
                        ):
                            before_source_utilities = sum_utilities(source_utilities, agent_source_utilities)
                            after_target_utilities = sum_utilities(target_utilities, agent_target_utilities)
                            phi_before = phi(before_source_utilities) + phi(target_utilities)
                            phi_after = phi(source_utilities) + phi(after_target_utilities)
                            constraints.append(phi_after > phi_before)
                        # fmt: on
print()

# for v in vars.values():
#    constraints.append(v >= 0)
# for v in alpha:
#     constraints.append(v >= 0)
# for v in beta:
#     constraints.append(v >= 0)

print(f"Generated {len(constraints)} constraints for {len(vars)} variables")
print("Solving...")
print(solve(constraints))
