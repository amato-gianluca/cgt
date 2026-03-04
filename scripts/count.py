"""
This script counts the number of games with no Nash stable coalition structures.
"""

import argparse
import datetime
import json
import multiprocessing as mp
import time
from typing import Callable, Any

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


def parse_range(s: str) -> range:
    s_split = s.split("-")
    val_min = int(s_split[0])
    val_max = int(s_split[1]) if len(s_split) > 1 else val_min
    return range(val_min, val_max+1)


def _runner(q: mp.Queue, fn: Callable, args: tuple, kwargs: dict):
    try:
        q.put(("ok", fn(*args, **kwargs)))
    except BaseException as e:
        q.put(("err", repr(e)))


def run_with_timeout(fn: Callable, timeout: float, *args, **kwargs) -> Any:
    ctx = mp.get_context("spawn")  # cross-platform, safe with numba too
    q: mp.Queue = ctx.Queue()
    p = ctx.Process(target=_runner, args=(q, fn, args, kwargs))

    p.start()
    p.join(timeout)

    if p.is_alive():
        p.terminate()
        p.join()
        raise TimeoutError(f"Timed out after {timeout} seconds")

    status, payload = q.get() if not q.empty() else ("err", "No result")
    if status == "ok":
        return payload
    raise RuntimeError(payload)


def load_data(filename: str) -> list[dict[str, Any]]:
    data = []
    with open(filename, "r") as f:
        for line in f:
            data.append(json.loads(line))
    return data


def skip_processing(data: list[dict[str, Any]], k: int, n: int, m: int, weights: Any, timeout: float) -> bool:
    for ex in data:
        if ex["k"] == k and ex["n"] == n and ex["m"] == m and ex["weights"] == weights and \
                (ex["unstable_game_count"] != -1 or timeout is None or ex["elapsed_time"] > timeout):
            return True
    return False


def count_with_timing(**kwargs) -> tuple[tuple[int, int, Game | None], float]:
    # I tried to generalize count_with_timing to make it works with any function, but this
    # interferes with numba caching.
    start_time = time.time()
    res = count_unstable_games(**kwargs)
    elapsed_time = time.time() - start_time
    return (res, elapsed_time)


def main():
    parser = argparse.ArgumentParser(
        prog='count.py',
        description='''
        Count games without Nash table coalition structures.
        Arguments n, k and m may be either a natural number or a range min-max of natural numbers.
        ''')
    parser.add_argument('-k', help='upper bound on the size of coalitions')
    parser.add_argument('-n', help='number of agents in the game')
    parser.add_argument('-m', help='maximum valuation in the game')
    parser.add_argument('-i', '--input', help='input file containing already counted data points')
    parser.add_argument('-o', '--output', help='output file')
    parser.add_argument('-w', '--weights', help='weights to use instead of consecutive numbers')
    parser.add_argument('-t', '--timeout', type=float, help='timeout for a single game count')
    args = parser.parse_args()

    n_range = None if args.n is None else parse_range(args.n)
    k_range = None if args.k is None else parse_range(args.k)
    m_range = None if args.m is None else parse_range(args.m)

    f = None if args.output is None else open(args.output, "a")
    weights = None if args.weights is None else json.loads(args.weights)
    timeout = args.timeout

    old_data = load_data(args.input) if args.input else []

    # warmup jit
    count_unstable_games(agent_count=2, k=1, m_begin=1, m_end=1, weights=weights, debug=0)

    local_k_range = range(3, 9) if k_range is None else k_range

    for k in local_k_range:
        local_n_range = range(k+1, 11) if n_range is None else n_range

        for n in local_n_range:
            local_m_range = m_range
            if local_m_range is None:
                match n:
                    case 0 | 1 | 2 | 3 | 4: local_m_range = range(0, 31)
                    case 5: local_m_range = range(0, 13)
                    case 6: local_m_range = range(0, 7)
                    case 7: local_m_range = range(0, 4)
                    case 8 | 9: local_m_range = range(0, 3)
                    case _: local_m_range = range(0, 2)

            if weights is not None:
                local_m_range = range(local_m_range.start, min(local_m_range.stop, len(weights)))

            for m in local_m_range:
                if skip_processing(old_data, k, n, m, weights, timeout):
                    print("k:", k, "n:", n, "m: ", m, "------ SKIPPED")
                    continue
                print("k:", k, "n:", n, "m: ", m)
                try:
                    (unstable_game_count, total_game_count, example), elapsed_time = run_with_timeout(
                        count_with_timing, timeout, agent_count=n, k=k, m_begin=m, m_end=m, weights=weights, debug=1)
                except TimeoutError:
                    unstable_game_count = total_game_count = -1
                    example = None
                    elapsed_time = timeout
                log_msg = result_log(k, n, m, weights, total_game_count, unstable_game_count, elapsed_time, example)
                print(log_msg)
                if f:
                    print(log_msg, file=f, flush=True)
                if unstable_game_count == -1:
                    # do not try greater values for m if the current has timed out
                    break

    if f:
        f.close()


if __name__ == '__main__':
    main()
