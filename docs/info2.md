<!-- ltex: enabled=false-->

# Fractional Hedonic Games

**These results are similar to those in `info.md`, but are computed using a slightly different definiton of
fractional game, in which an agent has no reason to move out of a coalition and stay alone when its utility is
zero.**

## Notation

In the following:
  - $n$ is the number of vertices in a graph;
  - $m$ is the maximum weight of the edges (intended as the maximum value of all the weights in the graph, not as an upper bound of all the weights);
  - $k$ is the maximum size of a partition.

Simple graphs are those where $m$ is either $0$ (graph withouth edges) or $1$ (graph with at least one edge).

## Exhaustive game generation procedure

Games are generated using the heuristics in  _[Codish et al, Constraints for symmetry breaking in graph representation, Constraints 24 (2019)](https://doi.org/10.1007/s10601-018-9294-5)_. Using these heuristics, it is possible to avoid the generation of many (but not all) isomorphic copies of the same graph.

The following table show the number of games we generate for each combination given by the number of nodes *n* and the maximum valuation *m*. The first line shows the number of non-isomorphic graphs in the case when m=1, taken from https://users.cecs.anu.edu.au/~bdm/data/graphs.html. Note that we subtract one unit from the values from the web page in order to account for the graph without edges (m=0) that we do not count in our procedure.

 m\n | 3   | 4      | 5        | 6            | 7          | 8          | 9       | 10        | 11         |
----:|----:|-------:|---------:|-------------:|-----------:|-----------:|--------:|----------:|-----------:|
  \* | 3   |     10 | 33       | 155          | 1043       | 12345      |  274667 |  12005168 | 1018997864 |
   1 | 3   |     10 | 42       | 275          | 3157       | 66594      | 2587487 | 184192328
   2 | 6   |     61 | 1264     | 66515        | 9219851    | 3366883033 |
   3 | 10  |    250 | 17972    | 4256478      | 3380330967 |
   4 | 15  |    775 | 146016   | 109376621    |
   5 | 21  |   1976 | 809840   | 1541858582   |
   6 | 28  |   4375 | 3432849  | 14324050578  |
   7 | 36  |   8716 | 11943408 | 98118616940  |
   8 | 45  |  16005 | 35741811 | 533002333113 |
   9 | 55  |  27550 | 95011942 |
  10 |     |  45001
  11 |     |  70390
  12 |     | 106171
  13 |     | 155260
  14 |     | 221075
  15 |     | 307576
  16 |     | 419305
  17 |     | 561426
  18 |     | 739765
  19 |     | 960850


## Simple games without Nash equilibrium

* No cases for $k=3$ and $k=4$ (known from theory).
* No cases for $n \leq 10$, and $k < n$.

## Games without Nash equilibrium

For each $k$ and $n$, this table shows the maximum weight of the lexicographically minimum graph with no Nash equilibrium.

 k\n | 4 |  5  | 6  | 7  | 8  | 9  | 10 |
-----|---|-----|----|----|----|----|----|
  3  | 7 | >20 | >9 | >3 | >2 | >1 | >1 |
  4  | - |  10 |  2 | >4 | >2 | >1 | >1 |
  5  | - |  -  |  2 |  3 |  2 | >1 | >1 |
  6  | - |  -  |  - |  3 |  2 |  2 | >1 |
  7  | - |  -  |  - |  - |  2 | >1 | >1 |
  8  | - |  -  |  - |  - |  - |  2 | >1 |
  9  | - |  -  |  - |  - |  - |  - | >1 |

## Number of games with no equilibrium w.r.t. total games considered

### k=3

 m\n | 4      | 5          | 6              | 7            | 8            |
----:|-------:|-----------:|---------------:|-------------:|-------------:|
   1 | 0      | 0/42       | 0/275          | 0/3157       | 0/66594      |
   2 | 0      | 0/1264     | 0/66515        | 0/9219851    | 0/3366883033 |
   3 | 0      | 0/17972    | 0/4256478      | 0/3380330967 |
   4 | 0      | 0/146016   | 0/109376621    |              |
   5 | 0      | 0/809840   | 0/1541858582   |
   6 | 0      | 0/3432849  | 0/14324050578  |
   7 | **1**  | 0/11943408 | 0/98118616940  |
   8 | 0      | 0/35741811 | 0/533002333113 |
   9 | **2**  | 0/95011942 |


### k=4

 m\n | 5          | 6               | 7            | 8            |
-----|------------|-----------------|--------------|--------------|
   1 | 0/42       | 0/275           | 0/3157       | 0/66594      |
   2 | 0/1264     | **8/66515**     | 0/9219851    | 0/3366883033 |
   3 | 0/17972    | **855/4256478** | 0/3380330967 |              |
   4 | 0/146016   |                 |
   5 | 0/809840   |                 |
   6 | 0/3432849  |                 |
   7 | 0/11943408 |                 |
   8 | 0/35741811 |                 |
   9 | 0/95011942 |                 |

### k=5

 m\n | 6                  | 7                       | 8                    |
-----|--------------------|-------------------------|----------------------|
   1 | 0/275              | 0/3157                  | 0/66594              |
   2 | **5/66515**        | 0/9219851               | **21413/3366883033** |
   3 | **41/4256478**     | **3402/3380330967**     |                      |
   4 | **2098/109376621** | **780714/334171364470** |                      |

### k=6

 m\n | 7                    | 8                   |
-----|----------------------|---------------------|
   1 | 0/3157               | 0/ 66594            |
   2 | 0/9219851            | **7136/3366883033** |
   3 | 146/3380330967       |                     |

### k=7

 m\n | 8                     | 9                |
-----|-----------------------|------------------|
   1 | 0/66594               |                  |
   2 | **11736/3366883033**  |                  |

### k=8

 m\n | 9         | 10            |
-----|-----------|---------------|
   1 | 0/2587487 | 0/184192328   |

## Powers of two

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

 ## The case m=3

 We now make experiments like the ones above, but where weights are only 0, 1 and *v* for a variable *v*. We consider the following possible values for *v*: 2, 3, ..., 127, 128, 256, ..., 2**31. We only recoport here the combination which have given a non-zero count.

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
