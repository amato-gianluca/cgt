"""
This script sorts the lines in counts.json (or similar files) and remove duplicates.
"""

import argparse
import json
from pathlib import Path

import pandas as pd


def load_data(filename: str) -> list:
    with open(filename, "r") as f:
        data = [json.loads(line) for line in f]
    return data


def main():

    parser = argparse.ArgumentParser(
        prog="sort_counts.py",
        description="""
        Sorts the lines in counts.json (or similar files) and remove duplicates.
        """,
    )

    parser.add_argument(
        "-i",
        "--input",
        help="file containing data points to sort and remove duplicates from",
        default=Path(__file__).parent / "data/counts.json",
    )

    args = parser.parse_args()

    data = load_data(args.input)
    df = pd.DataFrame(data)
    df["weights_sort"] = df["weights"].apply(
        lambda x: tuple(x) if type(x) is list else ()
    )

    df = df.sort_values(by=["weights_sort", "k", "n", "m", "elapsed_time"])
    df = df.drop_duplicates(subset=["weights_sort", "k", "n", "m"], keep="last")

    df.drop(columns=["weights_sort"], inplace=True)

    for _, row in df.iterrows():
        print(json.dumps(row.to_dict()))


if __name__ == "__main__":
    main()
