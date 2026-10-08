# Informal Road Mapping

Which healthcare-access decisions remain stable across credible road-time,
closure and facility uncertainty, and which observations resolve the most
consequential ambiguities per unit cost?

The first executed result verifies shortest-path interval bounds on **toy graphs**.
It does not measure access accuracy in any country. Global applicability is the
research question; geographic validation remains open.

[![CI](https://github.com/500ft/informal-road-mapping/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/500ft/informal-road-mapping/actions/workflows/ci.yml)

## Results so far

The [executed record](evidence/access-stability-20261006/result.json) reports
exhaustive small-graph checks, demonstration classifications and widening checks.
The [method](docs/ACCESS_STABILITY.md) states the assumptions and proof.

![Deterministic toy travel-time bounds in minutes, before and after widening. The 10-minute access threshold is marked in both panels. A and B become unresolved; D may disconnect, E has no path, and Clinic stays at zero. Shapes and line styles distinguish decisions.](results/access-stability/bounds.png)

*Deterministic assumptions on a toy graph. The vertical line marks the recorded
access threshold, including equality. Arrows indicate an unbounded upper time;
no confidence intervals or geographic validation are shown.*

[Bounds and qualification tables](results/access-stability/README.md) ·
[Bounds CSV](results/access-stability/bounds.csv) ·
[Vector figure](results/access-stability/bounds.svg) ·
[Figure guide](docs/data-and-figures.md)

The [Idai qualification record](evidence/access-stability-20261006/qualification.json)
identifies a development baseline, checks its input links and records the
reproduction blockers. No published baseline has been reproduced here.
WFP observed constraints remain an unopened, currently ineligible evaluation
candidate. Metadata and eligibility are hashed before outcome access.

## Getting started

Use Python 3.10+ and the existing analysis dependencies:

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e "analysis[dev]"
MPLBACKEND=Agg python analysis/plot_access_bounds.py
PYTHONPATH=analysis python -m pytest analysis/tests/test_access_bounds.py analysis/tests/test_access_figure.py -q
```

The renderer reads the committed result and qualification metadata, then writes
the active figure and tables. It uses no network or reserved data.
[Start here](docs/START_HERE.md) lists metadata hashes and the optional dependencies
for retained detector checks.

## What's next

The [roadmap](ROADMAP.md) orders prerequisites and completion evidence without
a schedule. Qualified inputs and an estimand precede development replication,
bounds, route-cost measurement selection and independent evaluation.
Real-area claims require licensed,
pinned development inputs and independently sourced bound families. The WFP
candidate also needs observation dates, vehicle scope and independent lineage
before evaluation can be registered at row level.

## Retained history

The owner adopted this software question in this repository. The detector track
is inactive and superseded, with its evidence retained; it was not scientifically
disproved. The [history index](docs/history/README.md) preserves the baseline
packet, code, dated QA reports, figures and previous questions. Its candidate
layers and holdout remain unopened.

The [UCI trip probe](evidence/route-feasibility-20261004/README.md) is a
non-Mongolian parser demonstration, not field validation. Its reported usable
trips establish neither observed healthcare access nor off-road passability.
No route-planning repository was created or renamed.

## License

Original code is [MIT](LICENSE). Third-party inputs retain their own terms,
including the [baseline packet's ODbL attribution](baseline/20261003/ATTRIBUTION.md).
No Idai GPL code is incorporated. A future combined derived program must meet
its applicable GPL obligations; placing it in a separate folder is insufficient.
See [qualification](evidence/access-stability-20261006/README.md) and
[contributing](CONTRIBUTING.md).
