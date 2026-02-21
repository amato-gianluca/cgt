I am trying to find games without Nash equilibrium even for combinations of n and k that the standard brute force
approach was not able to discover. The approach I am following is trying with weights that are not consecutive numbers
but prime numbers.

In particular, using [0] followed by a suffix of prime numbers seem to work somewhat. At least, I am able to get
example of games without Nash equilibrium with a smaller number of different values for edge evaluation w.r.t.
the standard approach. Moreover, it seems that the case in which every prime is around the double of the previous one
generally gives good results.

**Result for n=6 and k=3**

```
[ 0  2  3  5  7 11 13 17 19 23 29 31 37 41 43 47 53 59 61 67 71 73 79 83
 89 97]
********* m: 0
sought_reward: 0
  [1] v: 0
********* m: 1
sought_reward: 1
  [1] v: 0
  [1] v: 1
********* m: 2
sought_reward: 2
  [1] v: 0
  [1] v: 1
  [1] v: 2
********* m: 3
sought_reward: 3
  [1] v: 0
  [1] v: 1
  [1] v: 2
  [1] v: 3
********* m: 4
sought_reward: 4
  [1] v: 0
[[0 0 0 0 0 0]
 [0 0 0 0 0 0]
 [0 0 0 0 3 4]
 [0 0 0 0 3 4]
 [0 0 3 3 0 2]
 [0 0 4 4 2 0]]
  [1] v: 1
  [1] v: 2
  [1] v: 3
  [1] v: 4
[ 0  3  5  7 11 13 17 19 23 29 31 37 41 43 47 53 59 61 67 71 73 79 83 89
 97]
********* m: 0
sought_reward: 0
  [1] v: 0
********* m: 1
sought_reward: 1
  [1] v: 0
  [1] v: 1
********* m: 2
sought_reward: 2
  [1] v: 0
  [1] v: 1
  [1] v: 2
********* m: 3
sought_reward: 3
  [1] v: 0
[[0 0 0 0 0 0]
 [0 0 0 0 0 0]
 [0 0 0 0 2 3]
 [0 0 0 0 2 3]
 [0 0 2 2 0 1]
 [0 0 3 3 1 0]]
  [1] v: 1
  [1] v: 2
  [1] v: 3
********* m: 4
sought_reward: 4
  [1] v: 0
[[0 0 0 0 0 0]
 [0 0 0 0 0 1]
 [0 0 0 0 0 4]
 [0 0 0 0 4 2]
 [0 0 0 4 0 4]
 [0 1 4 2 4 0]]
  [1] v: 1
  [1] v: 2
  [1] v: 3
  [1] v: 4
[ 0  5  7 11 13 17 19 23 29 31 37 41 43 47 53 59 61 67 71 73 79 83 89 97]
********* m: 0
sought_reward: 0
  [1] v: 0
********* m: 1
sought_reward: 1
  [1] v: 0
  [1] v: 1
********* m: 2
sought_reward: 2
  [1] v: 0
  [1] v: 1
  [1] v: 2
********* m: 3
sought_reward: 3
  [1] v: 0
  [1] v: 1
  [1] v: 2
  [1] v: 3
********* m: 4
sought_reward: 4
  [1] v: 0
  [1] v: 1
  [1] v: 2
  [1] v: 3
  [1] v: 4
[ 0  7 11 13 17 19 23 29 31 37 41 43 47 53 59 61 67 71 73 79 83 89 97]
********* m: 0
sought_reward: 0
  [1] v: 0
********* m: 1
sought_reward: 1
  [1] v: 0
  [1] v: 1
********* m: 2
sought_reward: 2
  [1] v: 0
  [1] v: 1
  [1] v: 2
********* m: 3
sought_reward: 3
  [1] v: 0
  [1] v: 1
  [1] v: 2
  [1] v: 3
********* m: 4
sought_reward: 4
  [1] v: 0
[[0 0 0 0 0 0]
 [0 0 0 0 0 0]
 [0 0 0 0 3 4]
 [0 0 0 0 3 4]
 [0 0 3 3 0 1]
 [0 0 4 4 1 0]]
  [1] v: 1
  [1] v: 2
  [1] v: 3
  [1] v: 4
[ 0 11 13 17 19 23 29 31 37 41 43 47 53 59 61 67 71 73 79 83 89 97]
********* m: 0
sought_reward: 0
  [1] v: 0
********* m: 1
sought_reward: 1
  [1] v: 0
  [1] v: 1
********* m: 2
sought_reward: 2
  [1] v: 0
  [1] v: 1
  [1] v: 2
********* m: 3
sought_reward: 3
  [1] v: 0
  [1] v: 1
  [1] v: 2
  [1] v: 3
********* m: 4
sought_reward: 4
  [1] v: 0
  [1] v: 1
  [1] v: 2
  [1] v: 3
  [1] v: 4
[ 0 13 17 19 23 29 31 37 41 43 47 53 59 61 67 71 73 79 83 89 97]
********* m: 0
sought_reward: 0
  [1] v: 0
********* m: 1
sought_reward: 1
  [1] v: 0
  [1] v: 1
********* m: 2
sought_reward: 2
  [1] v: 0
  [1] v: 1
  [1] v: 2
********* m: 3
sought_reward: 3
  [1] v: 0
  [1] v: 1
  [1] v: 2
  [1] v: 3
********* m: 4
sought_reward: 4
  [1] v: 0
  [1] v: 1
  [1] v: 2
  [1] v: 3
  [1] v: 4
[ 0 17 19 23 29 31 37 41 43 47 53 59 61 67 71 73 79 83 89 97]
********* m: 0
sought_reward: 0
  [1] v: 0
********* m: 1
sought_reward: 1
  [1] v: 0
  [1] v: 1
********* m: 2
sought_reward: 2
  [1] v: 0
  [1] v: 1
  [1] v: 2
********* m: 3
sought_reward: 3
  [1] v: 0
  [1] v: 1
  [1] v: 2
  [1] v: 3
********* m: 4
sought_reward: 4
  [1] v: 0
  [1] v: 1
  [1] v: 2
  [1] v: 3
  [1] v: 4
[ 0 19 23 29 31 37 41 43 47 53 59 61 67 71 73 79 83 89 97]
********* m: 0
sought_reward: 0
  [1] v: 0
********* m: 1
sought_reward: 1
  [1] v: 0
  [1] v: 1
********* m: 2
sought_reward: 2
  [1] v: 0
  [1] v: 1
  [1] v: 2
********* m: 3
sought_reward: 3
  [1] v: 0
  [1] v: 1
  [1] v: 2
  [1] v: 3
********* m: 4
sought_reward: 4
  [1] v: 0
  [1] v: 1
  [1] v: 2
  [1] v: 3
  [1] v: 4
[ 0 23 29 31 37 41 43 47 53 59 61 67 71 73 79 83 89 97]
********* m: 0
sought_reward: 0
  [1] v: 0
********* m: 1
sought_reward: 1
  [1] v: 0
  [1] v: 1
********* m: 2
sought_reward: 2
  [1] v: 0
  [1] v: 1
  [1] v: 2
********* m: 3
sought_reward: 3
  [1] v: 0
  [1] v: 1
  [1] v: 2
  [1] v: 3
********* m: 4
sought_reward: 4
  [1] v: 0
  [1] v: 1
  [1] v: 2
  [1] v: 3
  [1] v: 4
[ 0 29 31 37 41 43 47 53 59 61 67 71 73 79 83 89 97]
********* m: 0
sought_reward: 0
  [1] v: 0
********* m: 1
sought_reward: 1
  [1] v: 0
  [1] v: 1
********* m: 2
sought_reward: 2
  [1] v: 0
  [1] v: 1
  [1] v: 2
********* m: 3
sought_reward: 3
  [1] v: 0
  [1] v: 1
  [1] v: 2
  [1] v: 3
********* m: 4
sought_reward: 4
  [1] v: 0
  [1] v: 1
  [1] v: 2
  [1] v: 3
  [1] v: 4
```
and
```
[ 0  3  5  7 11 13 17 19 23 29 31 37 41 43 47 53 59 61 67 71 73 79 83 89
 97]
********* m: 0
sought_reward: 0
  [1] v: 0
Count: 0
********* m: 1
sought_reward: 1
  [1] v: 0
  [1] v: 1
Count: 0
********* m: 2
sought_reward: 2
  [1] v: 0
  [1] v: 1
  [1] v: 2
Count: 0
********* m: 3
sought_reward: 3
  [1] v: 0
[[0 0 0 0 0 0]
 [0 0 0 0 0 0]
 [0 0 0 0 2 3]
 [0 0 0 0 2 3]
 [0 0 2 2 0 1]
 [0 0 3 3 1 0]]
  [1] v: 1
  [1] v: 2
  [1] v: 3
Count: 14
[ 0  5 11 17 23 31 41 47 59 67 73 83 97]
********* m: 0
sought_reward: 0
  [1] v: 0
Count: 0
********* m: 1
sought_reward: 1
  [1] v: 0
  [1] v: 1
Count: 0
********* m: 2
sought_reward: 2
  [1] v: 0
  [1] v: 1
  [1] v: 2
Count: 0
********* m: 3
sought_reward: 3
  [1] v: 0
  [1] v: 1
  [1] v: 2
  [1] v: 3
Count: 0
[ 0  7 17 29 41 53 67 79 97]
********* m: 0
sought_reward: 0
  [1] v: 0
Count: 0
********* m: 1
sought_reward: 1
  [1] v: 0
  [1] v: 1
Count: 0
********* m: 2
sought_reward: 2
  [1] v: 0
  [1] v: 1
  [1] v: 2
Count: 0
********* m: 3
sought_reward: 3
  [1] v: 0
  [1] v: 1
  [1] v: 2
  [1] v: 3
Count: 0
[ 0 11 23 41 59 73 97]
********* m: 0
sought_reward: 0
  [1] v: 0
Count: 0
********* m: 1
sought_reward: 1
  [1] v: 0
  [1] v: 1
Count: 0
********* m: 2
sought_reward: 2
  [1] v: 0
  [1] v: 1
  [1] v: 2
Count: 0
********* m: 3
sought_reward: 3
  [1] v: 0
  [1] v: 1
  [1] v: 2
  [1] v: 3
Count: 0
[ 0 13 31 53 73]
********* m: 0
sought_reward: 0
  [1] v: 0
Count: 0
********* m: 1
sought_reward: 1
  [1] v: 0
  [1] v: 1
Count: 0
********* m: 2
sought_reward: 2
  [1] v: 0
  [1] v: 1
  [1] v: 2
Count: 0
********* m: 3
sought_reward: 3
  [1] v: 0
  [1] v: 1
  [1] v: 2
  [1] v: 3
Count: 0
[ 0 17 41 67 97]
********* m: 0
sought_reward: 0
  [1] v: 0
Count: 0
********* m: 1
sought_reward: 1
  [1] v: 0
  [1] v: 1
Count: 0
********* m: 2
sought_reward: 2
  [1] v: 0
  [1] v: 1
  [1] v: 2
Count: 0
********* m: 3
sought_reward: 3
  [1] v: 0
  [1] v: 1
  [1] v: 2
  [1] v: 3
Count: 0
[ 0 19 47 79]
********* m: 0
sought_reward: 0
  [1] v: 0
Count: 0
********* m: 1
sought_reward: 1
  [1] v: 0
  [1] v: 1
Count: 0
********* m: 2
sought_reward: 2
  [1] v: 0
  [1] v: 1
  [1] v: 2
Count: 0
********* m: 3
sought_reward: 3
  [1] v: 0
  [1] v: 1
  [1] v: 2
  [1] v: 3
Count: 0
[ 0 23 59 97]
********* m: 0
sought_reward: 0
  [1] v: 0
Count: 0
********* m: 1
sought_reward: 1
  [1] v: 0
  [1] v: 1
Count: 0
********* m: 2
sought_reward: 2
  [1] v: 0
  [1] v: 1
  [1] v: 2
Count: 0
********* m: 3
sought_reward: 3
  [1] v: 0
  [1] v: 1
  [1] v: 2
  [1] v: 3
Count: 0
[ 0 29 67]
********* m: 0
sought_reward: 0
  [1] v: 0
Count: 0
********* m: 1
sought_reward: 1
  [1] v: 0
  [1] v: 1
Count: 0
********* m: 2
sought_reward: 2
  [1] v: 0
  [1] v: 1
  [1] v: 2
Count: 0
********* m: 3
sought_reward: 3
  [1] v: 0
[[0 0 0 0 0 0]
 [0 0 0 0 0 1]
 [0 0 0 0 0 3]
 [0 0 0 0 3 2]
 [0 0 0 3 0 3]
 [0 1 3 2 3 0]]
  [1] v: 1
  [1] v: 2
  [1] v: 3
Count: 13
Total: 27
```