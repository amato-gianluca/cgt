"""
This script reads data for the counts.json file and produces a table in markdown format
with the results of the experiments relative to counting the number of games without Nash stable
coalition structures, with varying values for k and n (number of agents) and prefixes of
natural numbers as valuations.
"""

import json
from pathlib import Path

import pandas as pd

data = []
with open(Path(__file__).parent / "data/dataout.txt", "r") as f:
    for line in f:
        data.append(json.loads(line))

df = pd.DataFrame(data)
df = df[df["weights"].isna()]
df = df.drop(columns=["example", "weights"])

dfk3 =df[df["k"] == 3]
pivot = dfk3.pivot_table(index="m", columns="n", values="total_game_count", fill_value=-2).astype(int).astype(str)
pivot = pivot.replace("-1", "(to)")
pivot = pivot.replace("-2", "")
print("Total game count")
print(pivot.to_markdown())

ks = df["k"].unique()
ks.sort()
for k in ks:
    dfk = df[df["k"] == k]
    pivot = dfk.pivot_table(index="m", columns="n", values="unstable_game_count", fill_value=-2).astype(int).astype(str)
    pivot = pivot.replace("-1", "(to)")
    pivot = pivot.replace("-2", "")
    print("\n\nk =", k)
    print(pivot.to_markdown())
