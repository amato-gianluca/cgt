"""
This script counts the number of games with no Nash stable coalition structures.
"""

import argparse
import datetime
import json
import sys
import time
from typing import Collection

from pyhedonic.hedonicgame_impl import *


def result_log(k: int, n: int, m: int, weights: IntArray1D | None,  total_game_count: int,
               unstable_game_count: int, elapsed_time: float, example: IntArray2D | None) -> str:
    data = {
        "k": k,
        "n": n,
        "m": m,
        "weights": weights,
        "total_game_count": total_game_count,
        "unstable_game_count": unstable_game_count,
        "elapsed_time": elapsed_time,
        "elapsed_time_human": str(datetime.timedelta(seconds=int(elapsed_time))),
        "example": example.tolist() if example is not None else None,
    }
    return json.dumps(data)


def parse_range(s: str) -> Collection[int]:
    s_split = s.split("-")
    val_min = int(s_split[0])
    val_max = int(s_split[1]) if len(s_split) > 1 else val_min
    return range(val_min, val_max+1)


parser = argparse.ArgumentParser(
    prog='count.py',
    description='''
    Count games without Nash table coalition structures.
    Arguments n, k and m may be either a natural number or a range min-max of natural numbers.
    ''')
parser.add_argument('k', nargs='?', help='upper bound on the size of coalitions')
parser.add_argument('n', nargs='?', help='number of agents in the game')
parser.add_argument('m', nargs='?', help='maximum valuation in the game')
parser.add_argument('-o', '--output', help='output file')
parser.add_argument('-w', '--weights', help='weights to use instead of consecutive numbers')
args = parser.parse_args()

n_range = parse_range(args.n) if args.n else None
k_range = parse_range(args.k) if args.k else None
m_range = parse_range(args.m) if args.m else None

f = open(args.output, "a") if args.output else None
weights = json.loads(args.weights) if args.weights else None

# warmup jit
count_unstable_games(agent_count=1, m_begin=1, m_end=1, debug=0)

if k_range is None:
    k_range = range(3, 8)

for k in k_range:
    if n_range is None:
        n_range = range(k+1, 11)

    for n in n_range:
        if m_range is None:
            match n:
                case 0 | 1 | 2 | 3 | 4: m_range = range(1, 31)
                case 5: m_range = range(1, 11)
                case 6: m_range = range(1, 7)
                case 7: m_range = range(1, 4)
                case 8: m_range = range(1, 3)
                case _: m_range = range(1, 2)

        for m in m_range:
            print("k:", k, "n:", n, "m: ", m, file=sys.stderr)
            start_time = time.time()
            unstable_game_count, total_game_count, example = count_unstable_games(
                agent_count=n, k=k, m_begin=m, m_end=m, weights=weights, debug=1)
            elapsed_time = time.time() - start_time
            log_msg = result_log(n, k, m, weights, total_game_count, unstable_game_count, elapsed_time, example)
            print(log_msg)
            if f:
                print(log_msg, file=f)
                f.flush()

if f:
    f.close()
