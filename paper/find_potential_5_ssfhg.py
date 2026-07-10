"""
This script finds a potential function for the dynamics of 5-SSFH games.
"""

from z3 import Int, solve, ArithRef
k = 5

alpha = [Int(f'a{i}') for i in range(k + 1)]
beta = [Int(f'b{i}') for i in range(k + 1)]

def phi(co_size, utility: int) -> ArithRef:
    """
    The potential function.
    """
    return  utility * alpha[co_size] + beta[co_size]

constraints = []
for r in range(1, k + 1):
    for a in range(r):
        for s in range(1, k + 1):
            for b in range(s):
                for ma in range((r - 2) * (r - 1) // 2 + 1):
                    for mb in range((s - 2) * (s - 1) // 2 + 1):
                        if b * r > a * s or (a == b == 0 and s < r):
                            # pontential before applying the deviation
                            phi_a = phi(r, ma + a) + phi(s - 1, mb)
                            # potential after applying the deviation
                            phi_b = phi(r - 1, ma) + phi(s, mb + b)
                            # updating the minimum delta of the potential function
                            constraints.append(phi_b > phi_a)
for v in alpha:
    constraints.append(v >= 0)
for v in beta:
    constraints.append(v >= 0)

print(solve(constraints))
