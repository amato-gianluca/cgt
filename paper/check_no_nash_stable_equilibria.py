"""
This is a minimalistic program that checks whether a fractional game has a Nash stable coalition
structure.
"""

from more_itertools import set_partitions

type Agent = int
type Coalition = list[Agent]
type CoalitionStructure = list[Coalition]
type Graph = list[list[int]]


def is_improving_deviation(
    graph: Graph, source_coalition: Coalition, target_coalition: Coalition, agent: Agent
) -> bool:
    """
    Check whether an agent has an improving deviation from a source coalition to a target coalition.
    """
    target_coalition = target_coalition + [agent]
    source_utility = sum(graph[agent][a] for a in source_coalition)
    target_utility = sum(graph[agent][a] for a in target_coalition)
    if source_utility == 0 == target_utility:
        return len(target_coalition) < len(source_coalition)
    else:
        return target_utility * len(source_coalition) > source_utility * len(target_coalition)


def is_nash_stable(graph: Graph, coalition_structure: CoalitionStructure, k: int) -> bool:
    """
    Check whether a coalition structure is Nash stable.
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
    Check whether the game has a Nash stable coalition structure. It returns a
    Nash stable coalition structure if it exists, otherwise it returns None.
    """
    for coalition_structure in set_partitions(range(len(graph)), max_size=k):
        if is_nash_stable(graph, coalition_structure, k):
            return coalition_structure
    return None


def check_game(graph: Graph, k: int) -> None:
    cs = nash_stable_coalition_structure(graph, k)
    if cs is None:
        print(f"The game with k={k} has **no** Nash stable coalition structure.")
    else:
        print(f"The game with k={k} has a Nash stable coalition structure.")


def main():
    GRAPH_K3 = [
        [0, 0, 5, 7],
        [0, 0, 5, 7],
        [5, 5, 0, 3],
        [7, 7, 3, 0],
    ]
    check_game(GRAPH_K3, 3)

    GAME_K5 = [
        [0, 0, 0, 0, 2, 2],
        [0, 0, 0, 2, 0, 2],
        [0, 0, 0, 2, 2, 1],
        [0, 2, 2, 0, 0, 2],
        [2, 0, 2, 0, 0, 2],
        [2, 2, 1, 2, 2, 0],
    ]
    check_game(GAME_K5, 5)

    GRAPH_K6 = [
        [0, 0, 0, 0, 1, 1, 3],
        [0, 0, 1, 3, 0, 1, 2],
        [0, 1, 0, 3, 0, 3, 3],
        [0, 3, 3, 0, 0, 3, 2],
        [1, 0, 0, 0, 0, 3, 1],
        [1, 1, 3, 3, 3, 0, 0],
        [3, 2, 3, 2, 1, 0, 0],
    ]
    check_game(GRAPH_K6, 6)

    GRAPH_K7 = [
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
    check_game(GRAPH_K7, 7)

    GRAPH_K8 = [
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
    check_game(GRAPH_K8, 8)


main()
