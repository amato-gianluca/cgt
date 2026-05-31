"""
This script reads data for the prices.yaml file and produces tables in markdown format
with the results of the experiments relative to counting the prices of anarchy and
stability, with varying values for k and n (number of agents) and prefixes of
natural numbers as valuations.
"""

import argparse
from pathlib import Path
from typing import Any

import pandas as pd
import yaml

type GCILike = dict[str, Any]
type InputData = list[GCILike]


def yaml_load(filename: str) -> InputData:
    """
    Loads the data from a yaml file, which is expected to contain a list of documents, each
    being a dictionary with informations serialized from a `GameCollectionInfo` object.
    """
    with open(filename, "r") as f:
        data = list(yaml.load_all(f, Loader=yaml.FullLoader))
    return data


def generate_df(data: InputData) -> pd.DataFrame:
    """
    Generates a pandas DataFrame from the list of dictionaries, filtering the rows based on the
    compatibility of their weights with the specified weights.
    """
    data_clean = [
        row
        for row in data
        if row["payload"] is not None and row["payload"].get("prices") is not None
    ]
    df = pd.json_normalize(data_clean)
    return df


def main():

    parser = argparse.ArgumentParser(
        prog="report_prices.py",
        description="""
        Reports on prices of anarchy and stability collected by the counting program count.py.
        """,
    )
    parser.add_argument(
        "-i",
        "--input",
        help="file containing data points to report about",
        default=Path(__file__).parent / "data/prices.yaml",
    )
    parser.add_argument("-k", help="specify the required valued of k to report about")
    parser.add_argument("-m", help="specify the required valued of m to report about")
    parser.add_argument("-n", help="specify the required valued of n to report about")
    args = parser.parse_args()

    data = yaml_load(args.input)
    df = generate_df(data)
    if df.empty:
        print("No data to report about.")
        return

    columns = ["k", "n", "m"]
    for price in ["poa", "pos"]:
        for value in ["highest"]:
            columns += [f"{price}_{value}", f"{price}_{value}_count"]
            df[f"{price}_{value}"] = (
                df[f"payload.prices.{price}_{value}.numerator"]
                / df[f"payload.prices.{price}_{value}.denominator"]
            )
            df[f"{price}_{value}_count"] = df[
                f"payload.prices.{price}_{value}_count"
            ].astype(str)
    prices = df[columns].copy()
    if args.k is not None:
        prices = prices[prices["k"] == int(args.k)]
        prices.drop(columns=["k"], inplace=True)
    if args.m is not None:
        prices = prices[prices["m"] == int(args.m)]
        prices.drop(columns=["m"], inplace=True)
    if args.n is not None:
        prices = prices[prices["n"] == int(args.n)]
        prices.drop(columns=["n"], inplace=True)
    print(prices.to_markdown(index=False, floatfmt=".2f"))


if __name__ == "__main__":
    main()
