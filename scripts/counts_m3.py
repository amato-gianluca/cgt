import json
from math import log2
from pathlib import Path

import pandas as pd

col_order = ["k", "n"]
col_count = "count"
col_val = "v"

data = []
with open(Path(__file__).parent / "data/counts.json", "r") as f:
    for line in f:
        data.append(json.loads(line))

df = pd.DataFrame(data)
df = df[df["weights"].apply(lambda x: len(x) == 3 and x[0] == 0 and x[1] == 1)]
df[col_val] = df["weights"].apply(lambda x: x[2])

grouped = df.groupby(col_order + [col_count])
grouped = grouped.agg({
    col_val: lambda x: f"{x.min()} - {x.max()}" if x.max() < 128 else f"{x.min()} - 2**{int(log2(x.max()))}"
}).reset_index()
grouped = grouped[col_order + [col_val, col_count]]
print(grouped.to_markdown(index=False))
