"""
This is a minimalistic program that checks whether a fractional game has a Nash stable coalition
structure.
"""

import numpy as np
from more_itertools import set_partitions

type Agent = int
type Coalition = list[Agent]
type CoalitionStructure = list[Coalition]
type Graph = np.ndarray


def is_improving_deviation(
    graph: Graph, source_coalition: Coalition, target_coalition: Coalition, agent: Agent
) -> bool:
    """
    Check whether an agent has an improving deviation from a source coalition to a target coalition.
    """
    target_coalition = target_coalition + [agent]
    source_utility = sum(graph[agent, a] for a in source_coalition)
    target_utility = sum(graph[agent, a] for a in target_coalition)
    if source_utility == 0 == target_utility:
        return len(target_coalition) > len(source_coalition)
    else:
        return target_utility * len(source_coalition) > source_utility * len(target_coalition)


def is_nash_stable(graph: Graph, coalition_structure: CoalitionStructure, k: int) -> bool:
    """
    Check whether a coalition structure has an improving deviation.
    """
    for source_coalition in coalition_structure:
        for target_coalition in coalition_structure + [[]]:
            if len(target_coalition) == k:
                continue
            for agent in source_coalition:
                if is_improving_deviation(graph, source_coalition, target_coalition, agent):
                    return False
    return True


def nash_stable_coalition_structure(graph, k: int) -> CoalitionStructure | None:
    """
    Check whether the game has a Nash stable equilibrium.
    """
    n = graph.shape[0]
    for coalition_structure in set_partitions(range(n), max_size=k):
        if is_nash_stable(graph, coalition_structure, k):
            return coalition_structure
    return None


def main():
    K = 7
    GRAPH = np.array(
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
    )
    print(nash_stable_coalition_structure(GRAPH, K))


main()


# def nash_stable_coalition_structure_pyhedonic(graph, k: int) -> CoalitionStructure | None:
#     """
#     Check whether the game has a Nash stable equilibrium.
#     """
#     from pyhedonic import hedonicgame as hg
#     game = hg.HedonicGame(graph, k=k)
#     csit = game.nash_stable_coalition_structures()
#     cs = next(csit, None)
#     if cs is not None:
#         cs = [ list(c) for c in cs.to_list() ]
#     return cs
