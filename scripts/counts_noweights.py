"""
This script reads data for the counts.json file and produces a table in markdown format
with the results of the experiments relative to counting the number of games without Nash stable
coalition structures, with varying values for k and n (number of agents) and prefixes of
natural numbers as valuations.
"""

import argparse
import json
from pathlib import Path

import pandas as pd


def are_power2(weights: list[int]) -> bool:
    return weights is not None and weights == [2**i for i in range(len(weights))]


def are_power2_biased(weights: list[int]) -> bool:
    return weights is not None and weights == [0] + [2**i for i in range(len(weights)-1)]

def are_initial_naturals(weights: list[int]) -> bool:
    return weights is None

def total_games(df):
    pivot = df.pivot_table(index="m", columns="n", values="total_game_count",
                           aggfunc=max, fill_value=-2).astype(int).astype(str)
    pivot = pivot.replace("-1", "(to)")
    pivot = pivot.replace("-2", "")
    print(pivot.to_markdown())

def load_data(args) -> list:
    data = []
    with open(Path(__file__).parent / "data/dataout.txt", "r") as f:
        for line in f:
            row = json.loads(line)
            weights = row["weights"]
            valid = are_power2(weights) if args.wp2 else \
                    are_power2_biased(weights) if args.wzerop2 else \
                    are_initial_naturals(weights)
            if valid:
                data.append(row)
    return data

def main():

    parser = argparse.ArgumentParser(
        prog='report_counts.py',
        description='''
        Reports the counts collected by the counting program count.py.
        ''')

    parser.add_argument('--wp2', help='select counts weights are power of twos', action='store_true')
    parser.add_argument('--wzerop2', help='select counts weights are power of twos with an initial zero', action='store_true')
    parser.add_argument('-t', '--totals', help='report about total games instead of unstable ones', action='store_true')
    args = parser.parse_args()

    data = load_data(args)
    df = pd.DataFrame(data)
    df = df.drop(columns=["example", "weights"])

    if args.totals:
        total_games(df)
    else:
        ks = df["k"].unique()
        ks.sort()
        for k in ks:
            dfk = df[df["k"] == k]
            pivot = dfk.pivot_table(index="m", columns="n", values="unstable_game_count",
                                    fill_value=-2).astype(int).astype(str)
            pivot = pivot.replace("-1", "(to)")
            pivot = pivot.replace("-2", "")
            print("\n\nk =", k)
            print(pivot.to_markdown())


if __name__ == "__main__":
    main()
