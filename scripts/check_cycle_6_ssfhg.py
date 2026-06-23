# This script checks that the dynamic of a specific 6-SSFH game presented in the paper contains a cycle, by
# verifying that the cycle is indeed a sequence of improving deviations. It also check that some of these
# deviations are not the best possible ones.

from pyhedonic import hedonicgame as hg
import numpy as np

edges = [
    (1, 2),
    (4, 5),
    (7, 8),
    (3, 1),
    (3, 2),
    (3, 4),
    (3, 5),
    (3, 7),
    (3, 8),
    (6, 1),
    (6, 2),
    (6, 4),
    (6, 5),
    (6, 7),
    (6, 8),
    (9, 3),
    (9, 6),
    (10, 11),
] + [(10, i) for i in range(1, 9)]

cycle = [
    {"X": {1, 2, 9}, "Y": {3, 4, 5, 10, 11}, "W": {6, 7, 8}, "c": 3},
    {"X": {4, 5, 9}, "Y": {6, 7, 8, 10, 11}, "W": {1, 2, 3}, "c": 6},
    {"X": {7, 8, 9}, "Y": {1, 2, 3, 10, 11}, "W": {4, 5, 6}, "c": 3},
    {"X": {1, 2, 9}, "Y": {4, 5, 6, 10, 11}, "W": {3, 7, 8}, "c": 6},
    {"X": {4, 5, 9}, "Y": {3, 7, 8, 10, 11}, "W": {1, 2, 6}, "c": 3},
    {"X": {7, 8, 9}, "Y": {1, 2, 6, 10, 11}, "W": {3, 4, 5}, "c": 6},
]

# We add a dummy agent 0, that is alone in its coalition and has no edge with anyone. This is to make agent numbers here
# the same as in the paper.

weights = np.array([[0] * 12] * 12)
for a, b in edges:
    weights[a][b] = 1
    weights[b][a] = 1

g = hg.HedonicGame(weights, k=6)

print("** Equilibra **")
equilibria = g.nash_stable_coalition_structures()
for equilibrium in equilibria:
    print(equilibrium)

def check_best_deviation(state: hg.CoalitionStructure, ag: int, tgt: int) -> bool:
    chosen = state.agent_utility(ag, tgt)
    for co in state.coalitions():
        if state.is_improving_deviation(ag, co):
            ut = state.agent_utility(ag, co)
            if chosen < ut:
                print(
                    f"Agent {ag} has a better deviation to {co} with utility {ut} than to {tgt} with utility {chosen}."
                )
                return False
    return True


print("** Cycle Verification **")
state = g.coalition_structure_from_groups(
    [{0}, cycle[0]["X"], cycle[0]["Y"], cycle[0]["W"]]
)
print(state)
for macro_step in cycle:
    assert state == g.coalition_structure_from_groups(
        [{0}, macro_step["X"], macro_step["Y"], macro_step["W"]]
    )
    tgt = state.cs[next(iter(macro_step["Y"]))]
    assert state.is_improving_deviation(9, tgt)
    check_best_deviation(state, 9, tgt)
    state = state.move_to(9, tgt)
    print(state)
    tgt = state.cs[next(iter(macro_step["W"]))]
    assert state.is_improving_deviation(10, tgt)
    check_best_deviation(state, 10, tgt)
    state = state.move_to(10, tgt)
    print(state)
    tgt = state.cs[next(iter(macro_step["X"] - {9}))]
    assert state.is_improving_deviation(macro_step["c"], tgt)
    check_best_deviation(state, macro_step["c"], tgt)
    state = state.move_to(macro_step["c"], tgt)
    print(state)
    tgt = state.cs[10]
    assert state.is_improving_deviation(11, tgt)
    check_best_deviation(state, 11, tgt)
    state = state.move_to(11, tgt)
    print(state)
