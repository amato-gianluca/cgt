# Fractional Hedonic Games

In the following, $n$ is the number of agents and $k$ the maximum size of a partition.

## Simple games without Nash equilibrium

* No cases for $k=3$ and $k=4$.
* No cases for $n \leq 10$, and $k < n$.

## Games without Nash equilibrium

For each $k$ and $n$, this table shows the maximum weight of the lexicographically minimum graph with no Nash equilibrium.

 k\n |  4 |  5  |  6  |  7 |  8 |  9 | 10 |
-----|----|-----|-----|----|----|----|----|
   3 |  7 | >20 |  >8 (run) | >3 (run) | >2 | >1 | >1 |
   4 |  - |  10 |   2 | >4 | >2 | >1 | >1
   5 |  - |   - |   2 |  3 |  2 | >1 (run) | >1 |
   6 |  - |   - |   - |  3 |  2 |    2 | >1 (run) |
   7 |  - |   - |   - |  - |  2 | >1 | >1 |
   8 |  - |   - |   - |  - |  - |  2 | >1 |
   9 |  - |   - |   - |  - |  - |  - | >1 |

## Number of games with no equilibrium w.r.t. total games considered

The total games considered contains many isomorphic copies of the same game, but not all the isomorphic
copies, since the heuristic in _[Codish et al, Constraints for symmetry breaking in graph representation,
Constraints 24 (2019)](https://doi.org/10.1007/s10601-018-9294-5)_ is used to avoid generating some copies.

In the tables below, $m$ is the maximum valuation of the game.

### k=3

 m\n |  4           |  5         |  6            |  7           |  8           |
-----|--------------|------------|---------------|--------------|--------------|
   1 |  0/10        | 0/42       | 0/275         | 0/3157       | 0/66594      |
   2 |  0/61        | 0/1264     | 0/66515       | 0/9219851    | 0/3366883033 |
   3 |  0/250       | 0/17972    | 0/4256478     | 0/3380330967 |
   4 |  0/775       | 0/146016   | 0/109376621   |
   5 |  0/1976      | 0/809840   | 0/1541858582  |
   6 |  0/4375      | 0/3432849  | 0/14324050578 |
   7 |  **1/8716**  | 0/11943408 | 0/98118616940 |
   8 |  0/16005     | 0/35741811 | 0/?? (run)    |
   9 |  **2/27550** | 0/95011942 |

### k=4

 m\n | 5          | 6               |  7           |  8           |
-----|------------|-----------------|--------------|--------------|
   1 | 0/42       | 0/275           | 0/3157       | 0/66594      |
   2 | 0/1264     | **8/66515**     | 0/9219851    | 0/3366883033 |
   3 | 0/17972    | **855/4256478** | 0/3380330967 | (run)        |
   4 | 0/146016   |                 | 0/??
   5 | 0/809840   |                 |
   6 | 0/3432849  |                 |
   7 | 0/11943408 |                 |
   8 | 0/35741811 |                 |
   9 | 0/95011942 |                 |

### k=5

 m\n | 6                  |  7                  |  8           |
-----|--------------------|---------------------|--------------|
   1 | 0/275              | 0/3157              | 0/66594      |
   2 | **5/66515**        | 0/9219851           | ?/3366883033 |
   3 | **41/4256478**     | **3402/3380330967** |
   4 | **2098/109376621** | (run)               |
