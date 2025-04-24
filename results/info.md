# SFHG

In the following, $n$ is the number of agents and $k$ the maximum size of a partition.

## Simple games without Nash equilibrium

* No cases for $k=3$ and $k=4$.
* No cases for $n \leq 10$, and $k < n$.

## Non-simple games without Nash equilibrium

For each $k$ and $n$, this table shows the maximum weight of the lexicographically minimum graph with no Nash equilibrium.

 k\n |  4 |  5  |  6  |  7 |  8 |  9 | 10 |
-----|----|-----|-----|----|----|----|----|
   3 |  7 | >20 |  >8 |
   4 |  - |  10 |   2 | >3 |
   5 |  - |   - |   2 |  3 |  2 | >1 |
   6 |  - |   - |   - |  3 |
   7 |  - |   - |   - |  - |  2 |
   8 |  - |   - |   - |  - |  - |  2
   9 |  - |   - |   - |  - |  - |  - | >1 |

## Number of games with no equilibrium w.r.t. total games considered

The total games considered contains many isomorphic copies of the same game, but not all the isomorphic
copy, since the heuristic in _[Codish et al, Constraints for symmetry breaking in graph representation,
Constraints 24 (2019)](https://doi.org/10.1007/s10601-018-9294-5)_ is used to avoid generating some of the
copies.

In the tables below, $m$ is the maximum valuation of the game.

### k=3

 m\n |  4           |  5         |  6          |  7        |
-----|--------------|------------|-------------|-----------|
   1 |  0/10        | 0/42       | 0/275       | 0/3157
   2 |  0/61        | 0/1264     | 0/66515     | 0/9219851
   3 |  0/250       | 0/17972    | 0/4256478   |
   4 |  0/775       | 0/146016   | 0/109376621 |
   5 |  0/1976      | 0/809840   | 0/??
   6 |  0/4375      | 0/3432849  | 0/??
   7 |  **1/8716**  | 0/11943408 | 0/??
   8 |  0/16005     | 0/35741811 | 0/??
   9 |  **2/27550** | 0/95011942 |

### k=4

 m\n | 5          | 6               |  7        |
-----|------------|-----------------|-----------|
   1 | 0/42       | 0/275           | 0/3157
   2 | 0/1264     | **8/66515**     | 0/9219851
   3 | 0/17972    | **855/4256478** |
   4 | 0/146016   | 0/109376621     |
   5 | 0/809840   | 0/??            |
   6 | 0/3432849  | 0/??            |
   7 | 0/11943408 | 0/??            |
   8 | 0/35741811 | 0/??            |
   9 | 0/95011942 |                 |