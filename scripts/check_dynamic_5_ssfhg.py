"""
This script checks that the dynamic of 5-SSFH games always terminates, by computing the minimum
delta of the potential fuction phi for each possible deviation.

The minimum delta should be strictly positive for all deviations.
"""

k = 5


def phi(r, s, ma, mb) -> int:
    """
    The potential function.
    """
    alpha = [0, 0, 36, 35, 30, 30]
    beta = [0, 8, 15, 19, 19, 0]
    return alpha[r] * ma + beta[r] + alpha[s] * mb + beta[s]


for r in range(1, k + 1):
    for a in range(r):
        min_delta = None
        for s in range(1, k + 1):
            for b in range(s):
                for ma in range((r - 2) * (r - 1) // 2 + 1):
                    for mb in range((s - 2) * (s - 1) // 2 + 1):
                        # check if the deviation is increasing
                        if b * r > a * s or (a == b == 0 and s < r):
                            # pontential before applying the deviation
                            phi_a = phi(r, s - 1, ma + a, mb)
                            # potential after applying the deviation
                            phi_b = phi(r - 1, s, ma, mb + b)
                            # updating the minimum delta of the potential function
                            delta = phi_b - phi_a
                            if min_delta is None or delta < min_delta:
                                min_delta = delta
        print(f"r={r}, a={a}, min_delta={min_delta}")
