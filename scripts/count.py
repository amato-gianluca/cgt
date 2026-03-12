"""
This script counts the number of games with no Nash stable coalition structures.
"""

import argparse
import datetime
import json
import multiprocessing as mp
import time
from typing import Any, Callable, cast

import numpy
import yaml

from pyhedonic.hedonicgame_impl import *


def yaml_serialize(obj: Any) -> Any:
    """
    Serialize an object to a YAML-compatible format.

    This is needed to serialize numpy arrays and other non-serializable objects.
    """
    if isinstance(obj, numpy.ndarray):
        return obj.tolist()
    if isinstance(obj, dict):
        return {key: yaml_serialize(value) for key, value in obj.items()}
    if isinstance(obj, tuple) and hasattr(obj, "_asdict"):
        return {key: yaml_serialize(value) for key, value in obj._asdict().items()}  # type: ignore
    if isinstance(obj, (list, tuple)):
        return [yaml_serialize(value) for value in obj]
    return obj


def yaml_log(k: int, n: int, m: int, weights: IntArray1D | None,  payload: Any,  elapsed_time: float) -> str:
    """
    Log the result of a computation in YAML format.
    """
    data = {
        "k": k,
        "n": n,
        "m": m,
        "weights": weights,
        "elapsed_time": elapsed_time,
        "elapsed_time_human": str(datetime.timedelta(seconds=int(elapsed_time))),
        "payload": payload,
    }
    return yaml.dump(yaml_serialize(data), default_flow_style=None, sort_keys=False)


def parse_range(s: str) -> range:
    """
    Parse a string representing a range of integers.
    """
    s_split = s.split("-")
    val_min = int(s_split[0])
    val_max = int(s_split[1]) if len(s_split) > 1 else val_min
    return range(val_min, val_max+1)


def _runner(q: mp.Queue, fn: Callable, args: tuple, kwargs: dict):
    try:
        q.put((True, fn(*args, **kwargs)))
    except BaseException as e:
        q.put((False, e))


def run_with_timeout(fn: Callable, timeout: float | None, *args, **kwargs) -> Any:
    ctx = mp.get_context("spawn")  # cross-platform, safe with numba too
    q = ctx.Queue()
    p = ctx.Process(target=_runner, args=(q, fn, args, kwargs))

    p.start()
    p.join(timeout)

    if p.is_alive():
        p.terminate()
        p.join()
        raise TimeoutError(f"Timed out after {timeout} seconds")

    status, payload = q.get()
    if not status:
        raise payload
    else:
        return payload


def yaml_load(filename: str) -> list[dict[str, Any]]:
    with open(filename, "r") as f:
        data = list(yaml.load_all(f, Loader=yaml.FullLoader))
    return data


def skip_processing(data: list[dict[str, Any]], k: int, n: int, m: int, weights: Any, timeout: float | None) -> bool:
    for ex in data:
        if ex["k"] == k and ex["n"] == n and ex["m"] == m and ex["weights"] == weights and \
                (ex["payload"] is not None or timeout is None or ex["elapsed_time"] > timeout):
            return True
    return False


def count_with_timing(**kwargs) -> tuple[tuple[int, int, Game | None], float]:
    # I tried to generalize count_with_timing to make it works with any function, but this
    # interferes with numba caching.
    start_time = time.time()
    res = count_unstable_games(**kwargs)
    elapsed_time = time.time() - start_time
    return (res, elapsed_time)


def prices_with_timing(**kwargs) -> tuple[GamePrices | None, float]:
    start_time = time.time()
    res = compute_poa_pos(**kwargs)
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
    parser.add_argument('-t', '--timeout', type=int, help='timeout for a single game count')
    parser.add_argument('--prices', help='compute price of anarchy and stability instead of counting games', action='store_true')

    args = parser.parse_args()

    n_range = None if args.n is None else parse_range(args.n)
    k_range = None if args.k is None else parse_range(args.k)
    m_range = None if args.m is None else parse_range(args.m)

    f = None if args.output is None else open(args.output, "a")
    weights: IntArray1D | None = None if args.weights is None else json.loads(args.weights)
    timeout: float | None = args.timeout

    old_data = yaml_load(args.input) if args.input else []
    print(old_data)


    # warmup jit
    if args.prices:
        compute_poa_pos(agent_count=2, k=1, m_begin=1, m_end=1, weights=weights, debug=0)
    else:
        count_unstable_games(agent_count=2, k=1, m_begin=1, m_end=1, weights=weights, debug=0)

    local_k_range = range(3, 9) if k_range is None else k_range

    for k in local_k_range:
        local_n_range = range(k+1, 11) if n_range is None else n_range

        for n in local_n_range:
            local_m_range = range(0, 31) if m_range is None else m_range

            if weights is not None:
                local_m_range = range(local_m_range.start, min(local_m_range.stop, len(weights)))

            for m in local_m_range:
                timeout_occured = False
                if skip_processing(old_data, k, n, m, weights, timeout):
                    print("k:", k, "n:", n, "m: ", m, "------ SKIPPED")
                    continue
                print("k:", k, "n:", n, "m: ", m)
                fn = prices_with_timing if args.prices else count_with_timing
                result = None
                try:
                    result, elapsed_time = run_with_timeout(fn, timeout, agent_count=n, k=k,
                                                            m_begin=m, m_end=m, weights=weights, debug=1)
                except TimeoutError:
                    timeout_occured = True
                    elapsed_time = cast(float, timeout)
                log_msg = yaml_log(k, n, m, weights, result, elapsed_time)
                print(log_msg)
                if f:
                    print('---', file=f, flush=True)
                    print(log_msg, file=f, flush=True, end="")

                if timeout_occured:
                    # do not try greater values for m if the current has timed out
                    break

    if f:
        f.close()


if __name__ == '__main__':
    main()
