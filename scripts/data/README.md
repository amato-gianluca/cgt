# Experiment data

This folder contains the raw results produced by `scripts/count.py`.  The files are used to
generate the tables in `docs/info.md`; they are not intended to be hand-edited.  The experiments
concern the number of games without Nash-stable coalition structures and the prices of anarchy and
stability.

The files are:

- `counts.yaml`: counts obtained with the repository's game-generation procedure;
- `geng_counts.yaml`: counts for simple games generated with nauty's `geng` procedure;
- `prices.yaml`: counts together with detailed price-of-anarchy and price-of-stability results;
- `geng_prices.yaml`: the corresponding results for simple games generated with `geng`;
- `counts_old.json`: legacy count data.  Its format and semantics are not documented here.

## YAML file format

Each YAML file is a stream of documents, one document for every combination of experiment
parameters.  Documents are separated by `---`, so the files must be read with a YAML
multi-document reader (as in `scripts/report_counts.py` and `scripts/report_prices.py`), rather
than as one large mapping.

Every document has the following top-level fields:

```yaml
k: 2
n: 3
m: 1
weights: null
elapsed_time: 0.0589
elapsed_time_human: 0:00:00
payload: ...
```

- `k` is the maximum size of a coalition considered by the experiment.
- `n` is the number of agents (vertices) in each game.
- `m` identifies the maximum valuation used for this data point.  With the default valuation
  sequence, the generated weights are the relevant prefix of the consecutive values up to `m`.
  In particular, different `m` values describe disjoint sets of games because `m` is the maximum
  value actually present, not merely an upper bound.
- `weights` is either `null`, meaning that the default valuation sequence is used, or a list of
  integer weights supplied with `--weights`.  The list can be longer than the prefix used for a
  particular value of `m`.
- `elapsed_time` is the computation time in seconds, and `elapsed_time_human` is the same value
  formatted for display.
- `payload` contains the computed result.  It is `null` when the computation was interrupted by a
  timeout.  In that case `elapsed_time` is the timeout value; count files use `-1` placeholders in
  the `counts` fields when such a result is serialized.

The `payload` is a serialized `GameCollectionInfo` object.  It always contains `counts` in the
count files and in the price files.  Price files also contain `prices`, which may be `null` when no
game has a valid price to aggregate (for example, when no Nash-stable coalition structure exists
for any game in the collection, or when the best social welfare is zero for every game).

## Counts

The `counts` object has this form:

```yaml
counts:
  count_total: 3
  count_noequilibrium: 0
  example_noequilibrium: null
```

- `count_total` is the number of generated or supplied games examined.
- `count_noequilibrium` is the number of those games with no Nash-stable coalition structure.
- `example_noequilibrium` is one such game, represented as a square matrix of integer valuations,
  when `count_noequilibrium > 0`.  It is `null` when the game-generation procedure stores a
  dummy value, and can be an empty matrix/list in results obtained from `geng`; it should not be
  interpreted as an additional count.

The matrix representation uses one row and column per agent.  Entry `[i][j]` is the valuation of
agent `i` for agent `j`; the diagonal is normally zero.  The exact matrix is only an example of an
unstable game, not a list of all unstable games.

## Prices

For price experiments, `payload.prices` has one record for each extremal statistic:
`poa_highest`, `poa_lowest`, `pos_highest`, and `pos_lowest`.  `poa` means price of anarchy and
`pos` means price of stability; `highest` and `lowest` refer to the value across the games in the
collection.

Each statistic is stored as a reduced rational number and a multiplicity:

```yaml
poa_highest: {numerator: 4, denominator: 2}
poa_highest_count: 3
poa_highest_game: [[0, 0], [0, 0]]
poa_highest_info:
  sw_best: 4
  cs_best: [0, 1]
  sw_best_equilibrium: 4
  cs_best_equilibrium: [0, 1]
  sw_worst_equilibrium: 2
  cs_worst_equilibrium: [0, 1]
```

For each `*_highest` or `*_lowest` group:

- the rational value is `numerator / denominator`;
- `*_count` is the number of games attaining that value;
- `*_game` is one game attaining it, in the same valuation-matrix format used by
  `example_noequilibrium`;
- `*_info` describes the social-welfare values and coalition structures for that game.

The fields in `*_info` are:

- `sw_best` and `cs_best`: the maximum social welfare over all coalition structures;
- `sw_best_equilibrium` and `cs_best_equilibrium`: the maximum social welfare among
  Nash-stable coalition structures and one structure attaining it;
- `sw_worst_equilibrium` and `cs_worst_equilibrium`: the minimum social welfare among
  Nash-stable coalition structures and one structure attaining it.

A coalition structure is represented by a list of coalition labels, one per agent.  Equal labels
identify agents in the same coalition; the labels themselves have no meaning beyond that
partition.

The two remaining fields, `poa_avg` and `pos_avg`, are the arithmetic averages of the price of
anarchy and price of stability over games for which the corresponding prices are valid.  Social
welfare is scaled to integer values internally, so the rational extrema are exact; the average
fields are serialized as floating-point numbers.

## Generation variants and reporting

The `counts.yaml` and `prices.yaml` files use the built-in exhaustive game-generation procedure.
The `geng_*` files contain only simple games (`m = 1`) generated by nauty's `geng`, and therefore
have a different set of game representatives and counts.

`scripts/report_counts.py` reads the count files and uses paths such as
`payload.counts.count_total` and `payload.counts.count_noequilibrium`.  `scripts/report_prices.py`
ignores documents whose `prices` value is `null` and reads the rational extrema from paths such as
`payload.prices.poa_highest.numerator` and `payload.prices.poa_highest.denominator`.
