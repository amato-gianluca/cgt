"""
This script reads data for the counts.yaml (or similar) file and produces a table in markdown format
with the results of the experiments relative to counting the number of games without Nash stable
coalition structures, with varying values for k and n (number of agents) and prefixes of natural
numbers as valuations.
"""

import argparse
import json
from pathlib import Path
from typing import Any

import pandas as pd
import yaml

type GCILike = dict[str, Any]
type InputData = list[GCILike]

args: argparse.Namespace


def yaml_load(filename: str) -> InputData:
    """
    Loads the data from a yaml file, which is expected to contain a list of documents, each being a
    dictionary with informations serialized from a `GameCollectionInfo` object.
    """
    with open(filename, "r") as f:
        data = list(yaml.load_all(f, Loader=yaml.FullLoader))
    return data


def has_compatible_weights(gci: GCILike, weights: list[int] | None) -> bool:
    """
    Determines if the weights of a given row are compatible with the specified weights.
    """
    if weights is None and gci["weights"] is None:
        return True
    elif weights is None or gci["weights"] is None:
        return False
    elif gci["m"] > len(weights):
        return False
    else:
        return weights[: gci["m"] + 1] == gci["weights"][: gci["m"] + 1]


def generate_df(data: InputData, weights: list[int] | None) -> pd.DataFrame:
    """
    Generates a pandas DataFrame from the list of dictionaries, filtering the rows based on the
    compatibility of their weights with the specified weights.
    """
    data_clean = [row for row in data if has_compatible_weights(row, weights)]
    df = pd.json_normalize(data_clean).convert_dtypes()
    df.fillna(-1, inplace=True)
    return df


def total_games(df: pd.DataFrame):
    """
    Prints a table in markdown format with the total number of games for each combination of m and
    n.
    """
    pivot = df.pivot_table(
        index="m",
        columns="n",
        values="payload.counts.count_total",
        aggfunc=max,
        fill_value=-2,
    )
    pivot = pivot.astype(object)
    pivot = pivot.replace(-1, "(to)")
    pivot = pivot.replace(-2, "")
    if args.latex:
        print(pivot.to_latex(escape=False))
    else:
        print(pivot.to_markdown())


def format_number(x: int) -> str:
    """
    Formats a number for display, either in parts per million or as an absolute count, and
    optionally in LaTeX format.
    """
    x_str = f"{x * 1_000_000:.3f}" if args.ppm else str(x)
    return x_str if args.latex else f"**{x_str}**"


def noequilibrium_games(df: pd.DataFrame):
    """
    Prints a table in markdown or LaTeX format with the number of games without Nash stable
    coalition structures for each combination of m and n.
    """
    for k in df["k"].sort_values().unique():
        dfk = df[df["k"] == k]
        if args.ppm:
            dfk["target"] = dfk["payload.counts.count_noequilibrium"] / abs(
                dfk["payload.counts.count_total"]
            )
        else:
            dfk["target"] = dfk["payload.counts.count_noequilibrium"]
        pivot = dfk.pivot_table(
            index="m",
            columns="n",
            values="target",
            aggfunc="max",
            fill_value=-2,  # do not use NaN, because NaN forces a float type
        )
        pivot = pivot.astype(object)
        pivot.iloc[:, :] = pivot.iloc[:, :].map(
            lambda x: "" if x == -2 else "(to)" if x == -1 else format_number(x) if x > 0 else "0"
        )
        pivot.index.name = "m\\n"
        print(f"\n\n### k={k}\n")
        if args.latex:
            column_format = "l|" + "c" * len(pivot.columns)
            print(pivot.to_latex(column_format=column_format, escape=False))
        else:
            print(pivot.to_markdown())


def main():
    global args

    parser = argparse.ArgumentParser(
        prog="report_counts.py",
        description="Reports the counts collected by the counting program count.py.",
    )

    weights_group = parser.add_mutually_exclusive_group()

    parser.add_argument(
        "-i",
        "--input",
        help="file containing data points to report about",
        default=Path(__file__).parent / "data/counts.yaml",
    )
    weights_group.add_argument(
        "--wp2",
        help="select counts whose weights are power of twos",
        action="store_true",
    )
    weights_group.add_argument(
        "--wzerop2",
        help="select counts whose weights are power of twos with an initial zero",
        action="store_true",
    )
    weights_group.add_argument(
        "-w",
        "--weights",
        help="select counts whose weights are specified in this parameter",
    )

    totals_group = parser.add_mutually_exclusive_group()

    totals_group.add_argument(
        "-t",
        "--totals",
        help="report about total games instead of unstable ones",
        action="store_true",
    )
    totals_group.add_argument(
        "--ppm",
        help="parts per million instead of absolute counts",
        action="store_true",
    )

    parser.add_argument(
        "--latex",
        help="output the tables in LaTeX format instead of markdown",
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

    data = yaml_load(args.input)
    df = generate_df(data, weights)

    if args.totals:
        total_games(df)
    else:
        noequilibrium_games(df)


if __name__ == "__main__":
    main()
