"""
This script reads data for the counts_old.json file and produces a table in markdown format
with the results of the experiment relative to counting the number of games without Nash stable
coalition structures, with varying values for k, n (number of agents) power of twos as valuations.
The column m contains the greatest power of two allowed in the game.
"""

import json
from pathlib import Path

import pandas as pd

col_order = ["k", "n"]
col_count = "count"
col_val = "val"

data = []
with open(Path(__file__).parent / "data/counts_old.json", "r") as f:
    for line in f:
        data.append(json.loads(line))

df_orig = pd.DataFrame(data)
ks = df_orig["k"].unique()

for k in ks:
    df = df_orig[df_orig["k"] == k]
    df = df[df["weights"].apply(lambda x: x == [2**i for i in range(len(x))])]
    df["m"] = df["weights"].apply(lambda x: len(x) - 1)
    pivot = (
        df.pivot_table(index="m", columns="n", values="count", fill_value=-1)
        .astype(int)
        .astype(str)
    )
    pivot = pivot.replace("-1", "")

    print("\n\nk =", k)
    print(pivot.to_markdown())

# grouped = df.groupby(col_order + [col_count])
# grouped = grouped.agg({
#     col_val: lambda x: f"{x.min()} - {x.max()}" if x.max() < 128 else f"{x.min()} - 2**{int(log2(x.max()))}"
# }).reset_index()
# grouped = grouped[col_order + [col_val, col_count]]
# print(grouped.to_markdown(index=False))
