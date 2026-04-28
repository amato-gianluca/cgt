<!-- ltex: enabled=false-->

# Fractional Hedonic Games

## Notation

In the following:
  - $n$ is the number of vertices in a graph;
  - $m$ is the maximum weight of the edges;
  - $k$ is the maximum size of a partition.

Note that $m$ is intended as the maximum value of all the weights in the graph, not as an upper bound for all the weights. Therefore, sets of graphs corresponding to different values of $m$ are disjoint. Simple graphs are those where $m$ is either $0$ (graph without edges) or $1$ (graph with at least one edge).

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
  21 | 253 | 1561120
  22 | 276 | 1957231
  23 | 300 | 2430020
  24 | 325 | 2990125
  25 | 351 | 3649126
  26 | 378 | 4419585
  27 | 406 | 5315086
  28 | 435 | 6350275
  29 | 465 | 7540900
  30 | 496 | 8903851

## Simple games without Nash stable coalition structure.

* No cases for $k=3$ and $k=4$ (known from theory).
* No cases for $2 \leq n \leq 9$, and $k < n$.
* No cases for $n=10$ and $k<n$ with the **only exception** of $n=10$ and $k=7$.

## Games without Nash stable coalition structure

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

There is no direct relationship between numbers with different values of $k$ since increasing $k$ on the one hand increases the number of coalition structures, but on the other hand increases the number of allowed deviations.

## Number of games with no Nash stable coalition structures

For each value of $k$, $m$ and $n$ we count the number of games without Nash stable coalition structures.
The value we find is to compare with the total number of games in the first table above. We recall that the method we use for enumerating graphs may contain many isomorphic variants of the same graph.

Note that numbers increase monotonically when $n$ increase, for the same reason already outlined in the observations relative to the table above.

The value `(to)` means execution took more than 24h and was interrupted. Values in italic have been computed without enforcing a well-defined timeout, and we don't know how much time it took to find them.

### k=3

 m\n | 4       | 5           | 6         | 7         | 8         | 9    | 10   |
----:|--------:|------------:|----------:|----------:|----------:|-----:|:----:|
   0 |  0      | 0           | 0         | 0         | 0         | 0    | 0    |
   1 |  0      | 0           | 0         | 0         | 0         | 0    | 0    |
   2 |  0      | 0           | 0         | 0         | 0         | (to) | (to) |
   3 |  0      | 0           | 0         | 0         | (to)      |
   4 |  0      | 0           | 0         | (to)      |
   5 |  0      | **45**      | **50**    |
   6 |  0      | **147**     | **160**   |
   7 |  **1**  | **728**     | **913**   |
   8 |  0      | **1654**    | (to)      |
   9 |  **2**  | **4831**    |
  10 |  **1**  | **9747**    |
  11 |  **4**  | **22222**   |
  12 |  **2**  | **39401**   |
  13 |  **9**  | **78724**   |
  14 |  **5**  | **128584**  |
  15 |  **14** | **231730**  |
  16 |  **11** | **357631**  |
  17 |  **23** | **598369**  |
  18 |  **18** | **879507**  |
  19 |  **38** | **1395591** |
  20 |  **31** | (to)
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

 m\n | 5          | 6            | 7         | 8         | 9      | 10   |
----:|-----------:|-------------:|----------:|----------:|-------:|:----:|
   0 | 0          | 0            | 0         | 0         | 0      | 0    |
   1 | 0          | 0            | 0         | 0         | 0      | 0    |
   2 | 0          | **9**        | **9**     | **9**     | (to)   | (to) |
   3 | 0          | **1033**     | **1084**  | (to)      |
   4 | 0          | **29759**    | (to)      |
   5 | 0          | **336527**   |
   6 | 0          | **2660652**  |
   7 | 0          | *18055411*   |
   8 | 0          |
   9 | 0          |
  10 | **423**    |
  11 | **759**    |
  12 | **4089**   |
  13 | **7946**   |
  14 | **24905**  |
  15 | **45650**  |
  16 | **109369** |
  17 | **188589** |
  18 | **391237** |
  19 | **634022** |
  20 | (to)       |

### k=5

 m\n | 6          | 7         | 8         | 9     |  10  |
----:|-----------:|----------:|----------:|------:|-----:|
   0 | 0          | 0         | 0         | 0     | 0    |
   1 | 0          | 0         | 0         | 0     | 0    |
   2 | **5**      | **5**     | **36109** | (to)  | (to) |
   3 | **41**     | **41259** | (to)      |
   4 | **2098**   | (to)
   5 | **64388**  |
   6 | **500786** |
   7 | (to)       |

### k=6

 m\n | 7          | 8         | 9         | 10    |
----:|-----------:|----------:|----------:|------:|
   0 | 0          | 0         | 0         | 0     |
   1 | 0          | 0         | 0         | 0     |
   2 | 0          | **17915** | (to)      | (to)
   3 | **146**    | (to)      |
   4 | *66743*    |

### k=7

 m\n | 8         | 9    | 10     |
----:|----------:|-----:|-------:|
   0 | 0         | 0    | 0      |
   1 | 0         | 0    | **13** |
   2 | **11736** | (to) | (to)   |
   3 | (to)      |

### k=8

| m\n | 9    | 10   |
|----:|:-----|:-----|
|   0 | 0    | 0    |
|   1 | 0    | 0    |
|   2 | (to) | (to) |

## Powers of two

The following tables are similar to the ones before, but the real valuations of the edges is are not initial segments of natural numbers like $0, 1, 2, \ldots, m$, but powers of two, from $1$ up to $2^m$. Timeout is set to one hour.

The fact that weight zero is missing (i.e., the graph of the game is always connected) seriously reduces the number of games without Nash stable coalition structures.

### k=3

|   m |   4 |   5 | 6   | 7   | 8   | 9    | 10   |
|----:|----:|----:|:----|:----|:----|:-----|:-----|
|   0 |   0 |   0 | 0   | 0   | 0   | 0    | 0    |
|   1 |   0 |   0 | 0   | 0   | 0   | 0    | 0    |
|   2 |   0 |   0 | 0   | 0   | 0   | (to) |      |
|   3 |   0 |   0 | 0   | 0   |     |      |      |
|   4 |   0 |   0 | 0   |     |     |      |      |
|   5 |   0 |   0 | 0   |     |     |      |      |
|   6 |   0 |   0 | 0   |     |     |      |      |
|   7 |   0 |   0 |     |     |     |      |      |
|   8 |   0 |   0 |     |     |     |      |      |
|   9 |   0 |   0 |     |     |     |      |      |
|  10 |   0 |   0 |     |     |     |      |      |
|  11 |   0 |   0 |     |     |     |      |      |
|  12 |   0 |   0 |     |     |     |      |      |


### k=4

|   m |   5 | 6            | 7   | 8   | 9    | 10   |
|----:|----:|:-------------|:----|:----|:-----|:-----|
|   0 |   0 | 0            | 0   | 0   | 0    | 0    |
|   1 |   0 | 0            | 0   | 0   | 0    | 0    |
|   2 |   0 | 0            | 0   | 0   | (to) |      |
|   3 |   0 | **39**       | 0   |     |      |      |
|   4 |   0 | **12915**    |     |     |      |      |
|   5 |   0 | **752663**   |     |     |      |      |
|   6 |   0 | **11864989** |     |     |      |      |
|   7 |   0 |              |     |     |      |      |
|   8 |   0 |              |     |     |      |      |
|   9 |   0 |              |     |     |      |      |
|  10 |   0 |              |     |     |      |      |
|  11 |   0 |              |     |     |      |      |
|  12 |   0 |              |     |     |      |      |


### k=5

|   m |          6 | 7       | 8   | 9    | 10   |
|----:|-----------:|:--------|:----|:-----|:-----|
|   0 |          0 |       0 | 0   | 0    | 0    |
|   1 |          0 |       0 | 0   | 0    | 0    |
|   2 |          0 |       0 | 0   | (to) |      |
|   3 |          0 |  **11** |     |      |      |
|   4 |    **197** |         |     |      |      |
|   5 |   **9567** |         |     |      |      |
|   6 | **252106** |         |     |      |      |


### k=6

|   m |   7 | 8   | 9    | 10   |
|----:|----:|:----|:-----|:-----|
|   0 |   0 | 0   | 0    | 0    |
|   1 |   0 | 0   | 0    | 0    |
|   2 |   0 | 0   | (to) |      |
|   3 |   0 |     |      |      |


### k=7

|   m |   8 | 9    | 10   |
|----:|----:|:-----|:-----|
|   0 |   0 | 0    | 0    |
|   1 |   0 | 0    | 0    |
|   2 |   0 | (to) |      |

### k=8

|   m | 9    | 10   |
|----:|:-----|:-----|
|   0 | 0    | 0    |
|   1 | 0    | 0    |
|   2 | (to) |      |

## Powers of two with zero

The following tables are similar to the ones before, but the first value of the weights is not one but zero, i.e., weights are $0, 1, 2, 4, 8, \ldots, 2^{m-1}$. Timeout is 1 hour.

### k=3

|   m |   4 |          5 | 6       | 7   | 8   | 9    | 10   |
|----:|----:|-----------:|:--------|:----|:----|:-----|:-----|
|   0 |   0 |          0 |      0  | 0   | 0   | 0    | 0    |
|   1 |   0 |          0 |      0  | 0   | 0   | 0    | 0    |
|   2 |   0 |          0 |      0  | 0   | 0   | (to) |      |
|   3 |   0 |          0 |      0  | 0   |     |      |      |
|   4 |   0 |     **16** | **17**  |     |     |      |      |
|   5 |   0 |    **124** | **140** |     |     |      |      |
|   6 |   0 |    **583** | **660** |     |     |      |      |
|   7 |   0 |   **2153** |         |     |     |      |      |
|   8 |   0 |   **6666** |         |     |     |      |      |
|   9 |   0 |  **17929** |         |     |     |      |      |
|  10 |   0 |  **43035** |         |     |     |      |      |
|  11 |   0 |  **94158** |         |     |     |      |      |
|  12 |   0 | **190908** |         |     |     |      |      |


### k=4

|   m |   5 | 6        | 7    | 8   | 9    | 10   |
|----:|----:|:---------|:-----|:----|:-----|:-----|
|   0 |   0 | 0        | 0    | 0   | 0    | 0    |
|   1 |   0 | 0        | 0    | 0   | 0    | 0    |
|   2 |   0 | 9        | 9    | 9   | (to) |      |
|   3 |   0 | 3456     | 6555 |     |      |      |
|   4 |   0 | 82672    |      |     |      |      |
|   5 |   0 | 1617525  |      |     |      |      |
|   6 |   0 | 16952943 |      |     |      |      |
|   7 |   0 |          |      |     |      |      |
|   8 |   0 |          |      |     |      |      |
|   9 |   0 |          |      |     |      |      |
|  10 |   0 |          |      |     |      |      |
|  11 |   0 |          |      |     |      |      |
|  12 |   0 |          |      |     |      |      |


### k=5

|   m |      6 | 7     | 8     | 9    | 10   |
|----:|-------:|:------|:------|:-----|:-----|
|   0 |      0 | 0     | 0     | 0    | 0    |
|   1 |      0 | 0     | 0     | 0    | 0    |
|   2 |      5 | 5     | 36109 | (to) |      |
|   3 |    137 | 69896 |       |      |      |
|   4 |   1576 |       |       |      |      |
|   5 |  23368 |       |       |      |      |
|   6 | 282374 |       |       |      |      |


### k=6

|   m |   7 | 8     | 9    | 10   |
|----:|----:|:------|:-----|:-----|
|   0 |   0 | 0     | 0    | 0    |
|   1 |   0 | 0     | 0    | 0    |
|   2 |   0 | 17915 | (to) |      |
|   3 |  64 |       |      |      |


### k=7

|   m |     8 | 9    | 10   |
|----:|------:|:-----|:-----|
|   0 |     0 | 0    | 0    |
|   1 |     0 | 0    | 13   |
|   2 | 11736 | (to) |      |


### k=8

|   m | 9    | 10   |
|----:|:-----|:-----|
|   0 | 0    | 0    |
|   1 | 0    | 0    |
|   2 | (to) |      |

## Prime numbers

In the following experiments we are using 0 and prime numbers 2, 3, 5, ... as weights. Timeout is 1 hour.

### k=3

| m\n |   4 |      5 | 6    | 7    | 8    | 9    | 10   |
|----:|----:|-------:|:-----|:-----|:-----|:-----|:-----|
|   0 |   0 |      0 | 0    | 0    | 0    | 0    | 0    |
|   1 |   0 |      0 | 0    | 0    | 0    | 0    | (to) |
|   2 |   0 |      0 | 0    | 0    | (to) | (to) |      |
|   3 |   0 |      0 | 0    | (to) |      |      |      |
|   4 |   1 |     30 | 50   |      |      |      |      |
|   5 |   0 |    138 | 151  |      |      |      |      |
|   6 |   0 |    748 | (to) |      |      |      |      |
|   7 |   2 |   2283 |      |      |      |      |      |
|   8 |   1 |   6422 |      |      |      |      |      |
|   9 |   6 |  15995 |      |      |      |      |      |
|  10 |   4 |  33651 |      |      |      |      |      |
|  11 |   3 |  73186 |      |      |      |      |      |
|  12 |   9 | 138569 |      |      |      |      |      |


### k=4

| m\n |     5 | 6     | 7    | 8    | 9    | 10   |
|----:|------:|:------|:-----|:-----|:-----|:-----|
|   0 |     0 | 0     | 0    | 0    | 0    | 0    |
|   1 |     0 | 0     | 0    | 0    | 0    | (to) |
|   2 |     0 | 0     | 0    | (to) | (to) |      |
|   3 |     0 | 1755  | (to) |      |      |      |
|   4 |     0 | 59975 |      |      |      |      |
|   5 |     0 | (to)  |      |      |      |      |
|   6 |    15 | (to)  |      |      |      |      |
|   7 |   102 |       |      |      |      |      |
|   8 |   407 |       |      |      |      |      |
|   9 |   726 |       |      |      |      |      |
|  10 |  2427 |       |      |      |      |      |
|  11 | 14662 |       |      |      |      |      |
|  12 | 24941 |       |      |      |      |      |


### k=5

| m\n | 6     | 7    | 8    | 9    | 10   |
|----:|:------|:-----|:-----|:-----|:-----|
|   0 | 0     | 0    | 0    | 0    | 0    |
|   1 | 0     | 0    | 0    | 0    | (to) |
|   2 | 0     | 10   | (to) | (to) |      |
|   3 | 987   | (to) |      |      |      |
|   4 | 21577 |      |      |      |      |
|   5 | (to)  |      |      |      |      |
|   6 | (to)  |      |      |      |      |


### k=6

| m\n | 7    | 8    | 9    | 10   |
|----:|:-----|:-----|:-----|:-----|
|   0 | 0    | 0    | 0    | 0    |
|   1 | 0    | 0    | 0    | (to) |
|   2 | 0    | (to) | (to) |      |
|   3 | (to) |      |      |      |


### k=7
| m\n | 8    | 9    | 10   |
|----:|:-----|:-----|:-----|
|   0 | 0    | 0    | 0    |
|   1 | 0    | 0    | (to) |
|   2 | (to) | (to) |      |


### k=8

| m\n | 9    | 10   |
|----:|:-----|:-----|
|   0 | 0    | 0    |
|   1 | 0    | (to) |
|   2 | (to) |      |

## Odd prime numbers

In the following experiments we are using 0 and odd prime numbers 3, 5, ... as weights.  Timeout is 1 hour. It seems that skipping the number 2 makes it possible to obtain games without Nash stable coalition structure with a smaller value of m.


### k=3

| m\n |   4 |      5 | 6    | 7    | 8    | 9    | 10   |
|----:|----:|-------:|:-----|:-----|:-----|:-----|:-----|
|   0 |   0 |      0 | 0    | 0    | 0    | 0    | 0    |
|   1 |   0 |      0 | 0    | 0    | 0    | 0    | (to) |
|   2 |   0 |      0 | 0    | 0    | (to) | (to) |      |
|   3 |   1 |      2 | 14   | (to) |      |      |      |
|   4 |   0 |     14 | 19   |      |      |      |      |
|   5 |   0 |     95 | 106  |      |      |      |      |
|   6 |   1 |    402 | (to) |      |      |      |      |
|   7 |   1 |   1500 |      |      |      |      |      |
|   8 |   4 |   4182 |      |      |      |      |      |
|   9 |   3 |  10069 |      |      |      |      |      |
|  10 |   2 |  24997 |      |      |      |      |      |
|  11 |   7 |  50944 |      |      |      |      |      |
|  12 |  17 | 110900 |      |      |      |      |      |


### k=4

| m\n |     5 | 6     | 7    | 8    | 9    | 10   |
|----:|------:|:------|:-----|:-----|:-----|:-----|
|   0 |     0 | 0     | 0    | 0    | 0    | 0    |
|   1 |     0 | 0     | 0    | 0    | 0    | (to) |
|   2 |     0 | 17    | 20   | (to) | (to) |      |
|   3 |     0 | 2271  | (to) |      |      |      |
|   4 |     0 | 52164 |      |      |      |      |
|   5 |    15 | (to)  |      |      |      |      |
|   6 |    58 |       |      |      |      |      |
|   7 |   216 |       |      |      |      |      |
|   8 |   282 |       |      |      |      |      |
|   9 |  1175 |       |      |      |      |      |
|  10 |  7615 |       |      |      |      |      |
|  11 | 14513 |       |      |      |      |      |
|  12 | 34157 |       |      |      |      |      |


### k=5

| m\n | 6     | 7    | 8    | 9    | 10   |
|----:|:------|:-----|:-----|:-----|:-----|
|   0 | 0     | 0    | 0    | 0    | 0    |
|   1 | 0     | 0    | 0    | 0    | (to) |
|   2 | 5     | 67   | (to) | (to) |      |
|   3 | 1022  | (to) |      |      |      |
|   4 | 15799 |      |      |      |      |
|   5 | (to)  |      |      |      |      |


### k=6

| m\n | 7    | 8    | 9    | 10   |
|----:|:-----|:-----|:-----|:-----|
|   0 | 0    | 0    | 0    | 0    |
|   1 | 0    | 0    | 0    | (to) |
|   2 | 13   | (to) | (to) |      |
|   3 | (to) |      |      |      |


### k=7

| m\n | 8    | 9    | 10   |
|----:|:-----|:-----|:-----|
|   0 | 0    | 0    | 0    |
|   1 | 0    | 0    | (to) |
|   2 | (to) | (to) |      |


### k=8

| m\n | 9    | 10   |
|----:|:-----|:-----|
|   0 | 0    | 0    |
|   1 | 0    | (to) |
|   2 | (to) |      |

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
