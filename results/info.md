<!-- ltex: enabled=false-->

# Fractional Hedonic Games

## Notation

In the following:
  - $n$ is the number of vertices in a graph;
  - $m$ is the maximum weight of the edges;
  - $k$ is the maximum size of a partition.

Notate that $m$ is intended as the maximum value of all the weights in the graph, not as an upper bound of all the weights. Therefore, set of graphs corresponding to different values of $m$ are disjoint. Simple graphs are those where $m$ is either $0$ (graph without edges) or $1$ (graph with at least one edge).

## Exhaustive game generation procedure

Games are generated using the heuristics in _[Codish et al, Constraints for symmetry breaking in graph representation, Constraints 24 (2019)](https://doi.org/10.1007/s10601-018-9294-5)_. Using these heuristics, it is possible to avoid the generation of many (but not all) isomorphic copies of the same graph.

The following table shows the number of games we generate for each combination given by the number of nodes *n* and the maximum valuation *m*. The first line shows the number of non-isomorphic graphs in the case when m=1, taken from https://users.cecs.anu.edu.au/~bdm/data/graphs.html. Note that we subtract one unit from the values taken from this web page in order to account for the only graph without edges (m=0) that we do not count in our procedure.

 m\n | 3   | 4       | 5         | 6            | 7          | 8          | 9       | 10        | 11         |
----:|----:|--------:|----------:|-------------:|-----------:|-----------:|--------:|----------:|-----------:|
  \* | 3   | 10      | 33        | 155          | 1043       | 12345      | 274667  | 12005168  | 1018997864 |
   1 | 3   | 10      | 42        | 275          | 3157       | 66594      | 2587487 | 184192328
   2 | 6   | 61      | 1264      | 66515        | 9219851    | 3366883033 |
   3 | 10  | 250     | 17972     | 4256478      | 3380330967 |
   4 | 15  | 775     | 146016    | 109376621    |
   5 | 21  | 1976    | 809840    | 1541858582   |
   6 | 28  | 4375    | 3432849   | 14324050578  |
   7 | 36  | 8716    | 11943408  | 98118616940  |
   8 | 45  | 16005   | 35741811  | 533002333113 |
   9 | 55  | 27550   | 95011942  |
  10 | 66  | 45001   | 229565094 |
  11 | 78  | 70390   | 512752516 |
  12 | 91  | 106171
  13 | 105 | 155260
  14 | 120 | 221075
  15 | 136 | 307576
  16 | 153 | 419305
  17 | 171 | 561426
  18 | 190 | 739765
  19 | 210 | 960850
  20 | 231 | 1231951
  21 |     | 1561120
  22 |     | 1957231
  23 |     | 2430020
  24 |     | 2990125
  25 |     | 3649126
  26 |     | 4419585
  27 |     | 5315086
  28 |     | 6350275
  29 |     | 7540900
  30 |     | 8903851

## Simple games without Nash stable coalition structure.

* No cases for $k=3$ and $k=4$ (known from theory).
* No cases for $2 \leq n \leq 9$, and $k < n$.
* No cases for $n=10$ and $k<n$ with the **only exception** of $n=10$ and $k=7$.

## Games without Nash stable coalition structure.

For each $k$ and $n$, this table shows the maximum weight ($m$) of the lexicographically minimum graph with no Nash stable coalition structure.

 k\n | 4 |  5  | 6 | 7  | 8  | 9  | 10    |
----:|--:|----:|--:|---:|---:|---:|------:|
  3  | 7 |   5 | 5 | >2 | >1 | >1 | >1    |
  4  | - |  10 | 2 | 2  | 2  | 2  |  2    |
  5  | - |  -  | 2 | >1 | >1 | >1 | >1    |
  6  | - |  -  | - | 3  | >1 | >1 | >1    |
  7  | - |  -  | - | -  |  2 | >1 | **1** |
  8  | - |  -  | - | -  |  - | >1 | >1    |
  9  | - |  -  | - | -  |  - |  - | >1    |

Note that these numbers decrease monotonically with $n$. This is because if a game with $n$ agents has no Nash stable coalition structure, the node with $n+1$ agents obtained by adding a new disconnected node also has no stable coalition structure for the same value of $k$.

There is no direct relationship between numbers with different values of $k$ since increasing $k$ from the one side increase the number of coalition structures, but other side increase the number of allowed deviations.

## Number of games with no Nash stable coalition structures

For each value of $k$, $m$ and $n$ we count the number of games without Nash stable coalition structures.
The value we find is to compare with the total number of games in the first table above. We recall that the method we use for enumerating graphs may contain many isomorphic variants of the same graph.

Note that numbers increase monotonically when $n$ increase, for the same reason already outlined in the observations relative to the table above.

### k=3

 m\n | 4       | 5         | 6         | 7         | 8         | 9         | 10 |
----:|--------:|----------:|----------:|----------:|----------:|----------:|:--:|
   1 |  0      | 0         | 0         | 0         | 0         | 0         | 0  |
   2 |  0      | 0         | 0         | 0         | 0         | (timeout) |
   3 |  0      | 0         | 0         | 0         | (timeout) |
   4 |  0      | 0         | 0         | (timeout) |
   5 |  0      | **45**    | **50**    |
   6 |  0      | **147**   | **160**   |
   7 |  **1**  | **728**   | **913**   |
   8 |  0      | **1654**  |
   9 |  **2**  | **4831**  |
  10 |  **1**  | **9747**  |
  11 |  **4**  | **22222** |
  12 |  **2**  | (timeout) |
  13 |  **9**  |
  14 |  **5**  |
  15 |  **14** |
  16 |  **11** |
  17 |  **23** |
  18 |  **18** |
  19 |  **38** |
  20 |  **31** |
  21 |  **55** |
  22 |  **52** |
  23 |  **82** |
  24 |  **76** |
  25 | **121** |
  26 | **115** |
  27 | **165** |
  28 | **169** |
  29 | **230** |
  30 | **231** |

### k=4

 m\n | 5         | 6            | 7         | 8         | 9         | 10 |
----:|----------:|-------------:|----------:|----------:|----------:|:--:|
   1 | 0         | 0            | 0         | 0         | 0         | 0  |
   2 | 0         | **9**        | **9**     | **9**     | (timeout) |
   3 | 0         | **1033**     | **1084**  | (timeout) |
   4 | 0         | **29759**    | (timeout) |
   5 | 0         | **336527**   |
   6 | 0         | **2660652**  |
   7 | 0         | **18055411** |
   8 | 0         |
   9 | 0         |
  10 | **423**   |
  11 | **759**   |
  12 | (timeout) |

### k=5

 m\n | 6          | 7         | 8         | 9         | 10 |
----:|-----------:|----------:|----------:|:---------:|:--:|
   1 | 0          | 0         | 0         | 0         | 0  |
   2 | **5**      | **5**     | **36109** | (timeout) |
   3 | **41**     | **41259** | (timeout) |
   4 | **2098**   | (timeout) |
   5 | **64388**  |
   6 | **500786** |
   7 | (timeout)  |

### k=6

 m\n | 7          | 8         | 9         | 10       |
----:|-----------:|----------:|----------:|---------:|
   1 | 0          | 0         | 0         | 0        |
   2 | 0          | **17915** | (timeout) |
   3 | **146**    | (timeout) |
   4 | **66743**  |

### k=7

 m\n | 8         | 9 | 10     |
----:|----------:|--:|-------:|
   1 | 0         | 0 | **13** |
   2 | **11736** |

### k=8

 m\n | 9 | 10 |
----:|--:|---:|
   1 | 0 | 0  |

## Powers of two (need to recompute values)

The following tables are similar to the ones before, but the real valuations of the edges is are no 0, 1, 2, ... m
but 1, 2, 4, 8, ... 2^m.

### k=3

 m\n | 4 | 5 | 6 | 7 |
----:|--:|--:|--:|--:|
   1 | 0 | 0 | 0 | 0 |
   2 | 0 | 0 | 0 | 0 |
   3 | 0 | 0 | 0 |
   4 | 0 | 0 | 0 |
   5 | 0 | 0 | 0 |
   6 | 0 | 0 | 0 |
   7 | 0 | 0 |
   8 | 0 | 0 |
   9 | 0 | 0 |
 <20 | 0

 ### k=4

 m\n | 5 | 6       | 7 |
----:|---|--------:|---|
   1 | 0 | 0       | 0 |
   2 | 0 | 0       | 0 |
   3 | 0 | 39      |
   4 | 0 | 12915   |
   5 | 0 | 752663  |
   6 | 0 |11864989 |
   7 | 0 |
   8 | 0 |
   9 | 0 |
 <20 |

 ### k=5

| m\n |      6 | 7   |
|----:|-------:|-----|
|   1 |      0 | 0   |
|   2 |      0 | 0   |
|   3 |      0 |     |
|   4 |    197 |     |
|   5 |   9567 |     |
|   6 | 252106 |     |

 ## The case m=3 (need to recompute values)

 We now make experiments like the ones above, but where weights are only 0, 1 and *v* for a variable *v*. We consider the following possible values for *v*: 2, 3, ..., 127, 128, 256, ..., 2**31. Furthermore, we only report here the combination which have given a non-zero count.

|   k |   n | val       |   count |
|----:|----:|:----------|--------:|
|   3 |   4 | 2 - 2**30 |       0 |
|   3 |   5 | 2 - 2**30 |       0 |
|   3 |   6 | 2 - 2**30 |       0 |
|   3 |   7 | 2 - 2**30 |       0 |
|   4 |   5 | 2 - 2**30 |       0 |
|   4 |   6 | 2 - 2     |       8 |
|   4 |   6 | 3 - 3     |      59 |
|   4 |   6 | 4 - 6     |     292 |
|   4 |   6 | 7 - 2**30 |     723 |
|   4 |   7 | 2 - 2**30 |       0 |
|   5 |   6 | 3 - 2**30 |       0 |
|   5 |   6 | 2 - 2     |       5 |
|   5 |   7 | 2 - 2     |       0 |
|   5 |   7 | 3 - 3     |       6 |
|   5 |   7 | 4 - 4     |     137 |
|   5 |   7 | 5 - 5     |    1122 |
|   5 |   7 | 6 - 2**30 |    1169 |
