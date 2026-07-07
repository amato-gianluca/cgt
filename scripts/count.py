"""
This script counts the number of games with no Nash stable coalition structures.

It can also compute the price of anarchy and stability for games with given parameters. The results
are logged in YAML or JSON format, and the script supports resuming from a previous log file.
"""

import argparse
import datetime
import itertools
import json
import multiprocessing as mp
import subprocess
import sys
import time
from textwrap import dedent
from typing import Any, Callable, Iterator, cast

import numpy as np
import yaml

import pyhedonic.hedonicgame_impl as hgimpl
from pyhedonic.hedonicgame_impl import IntArray1D, Game


def yaml_serialize(obj: Any) -> Any:
    """
    Serialize an object to a YAML-compatible format.

    This is needed to serialize numpy arrays and other non-serializable objects.
    """
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, np.generic):
        return obj.item()
    elif isinstance(obj, dict):
        return {key: yaml_serialize(value) for key, value in obj.items()}
    elif isinstance(obj, tuple) and hasattr(obj, "_asdict"):
        return {key: yaml_serialize(value) for key, value in obj._asdict().items()}  # type: ignore
    elif isinstance(obj, (list, tuple)):
        return [yaml_serialize(value) for value in obj]
    return obj


yaml.add_representer(np.float64, lambda dumper, value: dumper.represent_float(float(value)))


def yaml_log(
    k: int | None,
    n: int | None,
    m: int | None,
    weights: IntArray1D | None,
    payload: Any,
    elapsed_time: float,
) -> str:
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


def json_serialize(obj: Any) -> Any:
    """
    Serialize an object to a JSON-compatible format.

    This is needed to serialize numpy arrays and other non-serializable objects.
    """
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    if isinstance(obj, dict):
        return {key: json_serialize(value) for key, value in obj.items()}
    if isinstance(obj, tuple) and hasattr(obj, "_asdict"):
        return {key: json_serialize(value) for key, value in obj._asdict().items()}  # type: ignore
    if isinstance(obj, (list, tuple)):
        return [json_serialize(value) for value in obj]
    return obj


def json_log(
    k: int | None,
    n: int | None,
    m: int | None,
    weights: IntArray1D | None,
    payload: Any,
    elapsed_time: float,
) -> str:
    """
    Log the result of a computation in JSON format.
    """
    data = {
        "k": k,
        "n": n,
        "m": m,
        "weights": weights,
        "total_game_count": payload.count_total if payload else None,
        "unstable_game_count": payload.count_noequilibrium if payload else None,
        "elapsed_time": elapsed_time,
        "elapsed_time_human": str(datetime.timedelta(seconds=int(elapsed_time))),
        "example": (
            payload.example_noequilibrium
            if payload and payload.example_noequilibrium.size > 0
            else None
        ),
    }
    return json.dumps(json_serialize(data))


def parse_range(s: str) -> range:
    """
    Parse a string representing a range of integers.
    """
    s_split = s.split("-")
    val_min = int(s_split[0])
    val_max = int(s_split[1]) if len(s_split) > 1 else val_min
    return range(val_min, val_max + 1)


def _runner(q: mp.Queue, fn: Callable, args: tuple, kwargs: dict):
    """
    Run a function and put the result in a queue.

    This is used to run a function in a separate process with a timeout.
    """
    try:
        q.put((True, fn(*args, **kwargs)))
    except BaseException as e:
        q.put((False, e))


def run_with_timeout(fn: Callable, timeout: float | None, *args, **kwargs) -> Any:
    """
    Run a function with a timeout.

    If the function does not return within the timeout, it is terminated and a TimeoutError is
    raised.
    """
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
    """
    Loads the data containing the results of previous computations from a yaml file.
    """
    with open(filename, "r") as f:
        data = list(yaml.load_all(f, Loader=yaml.FullLoader))
    return data


def skip_processing(
    data: list[dict[str, Any]],
    k: int,
    n: int,
    m: int,
    weights: Any,
    timeout: float | None,
) -> bool:
    """
    Check if a given processing step should be skipped based on the results of previous
    computations.
    """
    for ex in data:
        if (
            ex["k"] == k
            and ex["n"] == n
            and ex["m"] == m
            and ex["weights"] == weights
            and (ex["payload"] is not None or timeout is None or ex["elapsed_time"] > timeout)
        ):
            return True
    return False


def count_with_timing(**kwargs) -> tuple[tuple[int, int, Game | None], float]:
    """
    Execute the count_unstable_games function and measure the elapsed time.

    Returns a tuple containing the result of the function and the elapsed time in seconds.
    """
    # I tried to generalize count_with_timing to make it works with any function, but this
    # interferes with numba caching.
    start_time = time.time()
    res = hgimpl.count_unstable_games(**kwargs)
    elapsed_time = time.time() - start_time
    return (res, elapsed_time)


def game_collection_info_with_timing(**kwargs) -> tuple[hgimpl.GameCollectionInfo | None, float]:
    """
    Execute the game_collection_info function and measure the elapsed time.

    Returns a tuple containing the result of the function and the elapsed time in seconds.
    """
    start_time = time.time()
    res = hgimpl.game_collection_info(**kwargs)
    elapsed_time = time.time() - start_time
    return (res, elapsed_time)


def generate_graphs(
    n: int, geng_path: str = "geng", geng_args: tuple = (), verbose: bool = True
) -> Iterator[Game]:
    """
    Generate all non-isomorphic simple graphs on n vertices using nauty's geng and return them
    as weight matrices.
    """
    cmd = [geng_path, *geng_args, str(n)]

    # The number of non-isomorphic simple graphs on n vertices is given by the OEIS sequence A000088.
    GRAPH_COUNTS = [
        1,
        1,
        2,
        4,
        11,
        34,
        156,
        1044,
        12346,
        274668,
        12005168,
        1018997864,
        165091172592,
        50502031367952,
        29054155657235488,
        31426485969804308768,
        64001015704527557894928,
        245935864153532932683719776,
        1787577725145611700547878190848,
        24637809253125004524383007491432768,
    ]
    total = GRAPH_COUNTS[n] if n < len(GRAPH_COUNTS) else None

    proc = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    assert proc.stdout is not None

    for i, line in enumerate(proc.stdout):
        if verbose and i % 10000 == 0:
            if total is not None:
                print(f"Processing graph {i/total*100:.3f}%\r", end="", file=sys.stderr)
            else:
                print(f"Processing graph {i}\r", end="", file=sys.stderr)
        graph = hgimpl.graph6_to_weight_matrix(line)
        yield graph
    if verbose:
        print()

    _, stderr = proc.communicate()

    if proc.returncode != 0:
        raise RuntimeError(f"geng failed:\n{stderr}")


def count_unstable_games_from_collection_with_timing(
    agent_count: int,
    k: int,
    is_fractional: bool = True,
    geng_path: str = "geng",
    debug: int = 0,
    **_,
) -> tuple[tuple[int, int, Game | None], float]:
    """
    Execute the count_unstable_games_from_collection function and measure the elapsed time.

    Returns a tuple containing the result of the function and the elapsed time in seconds. The
    functions is called in batches of 1000 graphs to avoid memory issues with large graph
    collections.
    """
    graphs = generate_graphs(agent_count, geng_path)
    batches = itertools.batched(graphs, 10000)
    start_time = time.time()
    count_total = 0
    count_noequilibrium = 0
    example_noequilibrium = np.zeros((0, 0), dtype=np.int_)
    for batch in batches:
        games = list(batch)
        res = hgimpl.count_unstable_games_from_collection(games, k, is_fractional)
        count_total += res.count_total
        count_noequilibrium += res.count_noequilibrium
        if example_noequilibrium.size == 0 and res.example_noequilibrium.size > 0 and debug > 0:
            print()
            print(res.example_noequilibrium)
            example_noequilibrium = res.example_noequilibrium
    elapsed_time = time.time() - start_time
    res = hgimpl.GameCollectionCounts(count_total, count_noequilibrium, example_noequilibrium)
    return (res, elapsed_time)


def main():
    parser = argparse.ArgumentParser(
        prog="count.py",
        description=dedent(
            """
            Count games without Nash table coalition structures.

            Arguments n, k and m may be either a natural number or a range min-max of natural
            numbers.
            """
        ),
    )
    parser.add_argument("-k", help="upper bound on the size of coalitions")
    parser.add_argument("-n", help="number of agents in the game")
    parser.add_argument("-m", help="maximum valuation in the game")
    parser.add_argument("--geng", help="generate graphs using nauty's geng", action="store_true")
    parser.add_argument("--geng-binary", help="name of the geng binary", default="geng")
    parser.add_argument("-i", "--input", help="input file containing already counted data points")
    parser.add_argument("-o", "--output", help="output file")
    parser.add_argument("-w", "--weights", help="weights to use instead of consecutive numbers")
    parser.add_argument("-t", "--timeout", type=int, help="timeout for a single game count")
    parser.add_argument(
        "--prices",
        help="compute price of anarchy and stability instead of counting games",
        action="store_true",
    )
    parser.add_argument(
        "--json",
        help="output results in JSON format instead of YAML (only for counts, not prices)",
        action="store_true",
    )

    args = parser.parse_args()

    n_range = None if args.n is None else parse_range(args.n)
    k_range = None if args.k is None else parse_range(args.k)
    m_range = None if args.m is None else parse_range(args.m)

    old_data = yaml_load(args.input) if args.input else []

    out_file = None if args.output is None else open(args.output, "a")
    timeout = None if args.timeout is None else int(args.timeout)
    weights = None if args.weights is None else np.array(json.loads(args.weights))

    # warmup jit
    if args.prices:
        hgimpl.game_collection_info(
            agent_count=2, k=1, m_begin=1, m_end=1, weights=weights, debug=0
        )
    else:
        hgimpl.count_unstable_games(
            agent_count=2, k=1, m_begin=1, m_end=1, weights=weights, debug=0
        )

    local_k_range = range(2, 9) if k_range is None else k_range

    if args.geng:
        if weights is not None or m_range is not None:
            raise ValueError(
                "Cannot use weights or m range when generating graphs with nauty's geng"
            )

        if args.prices:
            raise ValueError(
                "Cannot compute prices of anarchy and stability with a graph collection"
            )

    for k in local_k_range:
        local_n_range = range(k + 1, 11) if n_range is None else n_range

        for n in local_n_range:
            local_m_range = (
                range(1, 2) if args.geng else range(0, 31) if m_range is None else m_range
            )

            if weights is not None:
                local_m_range = range(local_m_range.start, min(local_m_range.stop, len(weights)))

            for m in local_m_range:
                timeout_occured = False
                if skip_processing(old_data, k, n, m, weights, timeout):
                    print("k:", k, "n:", n, "m:", m, "------ SKIPPED")
                    continue
                print("k:", k, "n:", n, "m:", m)

                fn = (
                    count_unstable_games_from_collection_with_timing
                    if args.geng
                    else game_collection_info_with_timing
                    if args.prices
                    else count_with_timing
                )
                result = None
                try:
                    result, elapsed_time = run_with_timeout(
                        fn,
                        timeout,
                        agent_count=n,
                        k=k,
                        m_begin=m,
                        m_end=m,
                        weights=weights,
                        geng_path=args.geng_binary,
                        debug=1,
                    )
                except TimeoutError:
                    timeout_occured = True
                    elapsed_time = cast(float, timeout)
                log_msg = (
                    yaml_log(k, n, m, weights, result, elapsed_time)
                    if args.prices or not args.json
                    else json_log(k, n, m, weights, result, elapsed_time)
                )
                print(log_msg)
                if out_file:
                    print("---", file=out_file, flush=True)
                    print(log_msg, file=out_file, flush=True, end="")

                if timeout_occured:
                    # do not try greater values for m if the current has timed out
                    break

    if out_file:
        out_file.close()


if __name__ == "__main__":
    main()
