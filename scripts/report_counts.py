"""
This script reads data for the counts.json (or similar) file and produces a table in markdown format
with the results of the experiments relative to counting the number of games without Nash stable
coalition structures, with varying values for k and n (number of agents) and prefixes of
natural numbers as valuations.
"""

import argparse
import json
from pathlib import Path

import pandas as pd


def has_valid_weights(row, weights: list[int] | None) -> bool:
    if weights is None and row["weights"] is None:
        return True
    elif weights is None or row["weights"] is None:
        return False
    elif row["m"] > len(weights):
        return False
    else:
        return weights[: row["m"] + 1] == row["weights"][: row["m"] + 1]


def total_games(df):
    pivot = (
        df.pivot_table(
            index="m",
            columns="n",
            values="total_game_count",
            aggfunc=max,
            fill_value=-2,
        )
        .astype(int)
        .astype(str)
    )
    pivot = pivot.replace("-1", "(to)")
    pivot = pivot.replace("-2", "")
    print(pivot.to_markdown())


def load_data(filename: str, weights) -> list:
    with open(filename, "r") as f:
        data = [
            row for line in f if has_valid_weights(row := json.loads(line), weights)
        ]
    return data


def main():

    parser = argparse.ArgumentParser(
        prog="report_counts.py",
        description="""
        Reports the counts collected by the counting program count.py.
        """,
    )

    weights_group = parser.add_mutually_exclusive_group()

    parser.add_argument(
        "-i",
        "--input",
        help="file containing data points to report about",
        default=Path(__file__).parent / "data/counts.json",
    )
    weights_group.add_argument(
        "--wp2",
        help="select counts whose weights are power of twos",
        action="store_true",
    )
    weights_group.add_argument(
        "--wzerop2",
        help="select counts whise weights are power of twos with an initial zero",
        action="store_true",
    )
    weights_group.add_argument(
        "-w",
        "--weights",
        help="select counts whose weights are specified in this parameter",
    )
    parser.add_argument(
        "-t",
        "--totals",
        help="report about total games instead of unstable ones",
        action="store_true",
    )
    args = parser.parse_args()
    weights = (
        [2**i for i in range(20)]
        if args.wp2
        else [0] + [2**i for i in range(20)]
        if args.wzerop2
        else json.loads(args.weights)
        if args.weights is not None
        else None
    )

    data = load_data(args.input, weights)
    df = pd.DataFrame(data)
    df = df.drop(columns=["example", "weights"])

    if args.totals:
        total_games(df)
    else:
        ks = df["k"].unique()
        ks.sort()
        for k in ks:
            dfk = df[df["k"] == k]
            pivot = (
                dfk.pivot_table(
                    index="m",
                    columns="n",
                    values="unstable_game_count",
                    aggfunc="max",
                    fill_value=-2 # do not use NaN, because NaN forces a float type
                )
            )
            pivot = pivot.astype(object)
            pivot.iloc[:, :] = pivot.iloc[:, :].map(
                lambda x: "" if x == -2 else "(to)" if x == -1 else f"**{x}**" if x > 0 else "0"
            )
            pivot.index.name = "m\\n"
            print(f"\n\n### k={k}\n")
            print(pivot.to_markdown())


if __name__ == "__main__":
    main()
