# Healthcare Access Uncertainty

Which healthcare-access decisions remain stable across credible road-time,
closure and facility uncertainty, and which observations resolve the most
consequential ambiguities per unit cost?

The first executed result verifies shortest-path interval bounds on **toy graphs**.
It does not measure access accuracy in any country. Global applicability is the
research question; geographic validation remains open.

[![CI](https://github.com/500ft/healthcare-access-uncertainty/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/500ft/healthcare-access-uncertainty/actions/workflows/ci.yml)

## Results so far

The [executed record](evidence/access-stability-20261006/result.json) reports
exhaustive small-graph checks, demonstration classifications and widening checks.
The [method](docs/ACCESS_STABILITY.md) states the assumptions and proof.

![Toy travel-time intervals for nodes A to Clinic in two panels, original and widened, with the access threshold as a dotted vertical line. Marker shape and line style give the decision; hollow markers are unresolved.](results/access-stability/bounds.png)

Deterministic shortest-time bounds on a toy graph, in minutes to the fixed
destination Clinic, for the 6 nodes A, B, C, D, E and Clinic. Panel (a):
original assumptions. Panel (b): widened assumptions, same axes. Each horizontal
line is one node's interval between its lower and upper travel time. A filled
circle with a solid line means definite access, a filled square with a dashed
line means definite exclusion, and a hollow diamond with a dash-dot line means
unresolved. The dotted vertical line is the 10-minute access threshold; equality
counts as access. No finite upper time exists for D in either panel; that line
runs to the right edge without an end marker. No path exists for E in either
panel, so nothing is drawn on that row; the decision is definite exclusion.
Original: access for A, exclusion for B and E, unresolved for C and D. Widened:
unresolved now also for A and B; a definite decision remains only for E and
Clinic. The bounds are deterministic assumptions, not confidence intervals; no
geography or observed travel time is involved. Exact endpoints: README.md and
bounds.csv beside this figure. Source:
evidence/access-stability-20261006/result.json.
[Caption file](results/access-stability/bounds.caption.md).

[Bounds and qualification tables](results/access-stability/README.md) ·
[Bounds CSV](results/access-stability/bounds.csv) ·
[Vector figure](results/access-stability/bounds.svg) ·
[Figure guide](docs/data-and-figures.md)

The [Sofala software result](evidence/sofala-scaling/README.md) checks
scaling on a dated OSM road network with synthetic times and closures.
[Timings and memory](results/sofala-scaling.md) accompany independent routing
checks and an isolated upstream compatibility probe. No measured journey times
or clinical outcomes were used to assess accuracy.

The [Idai source record](evidence/idai-development-inputs/README.md) identifies
the published development baseline and the inputs still needed to reproduce it:
the author's historical roads and final facility list, boundary and flood
membership, routing settings, reference output and confirmed reuse rights. No
published baseline has been reproduced here. WFP road-constraint outcomes remain
unopened. Their catalog metadata does not yet establish observation timing,
vehicle scope or independence from the development inputs.

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

The [roadmap](ROADMAP.md) orders the remaining work by dependency. The first
Idai target is the published [60-minute network-driving potential-access
quantity](docs/ACCESS_STABILITY.md#reproduction-target-adopted-by-the-owner),
which describes modeled population coverage by mapped facilities. Reproduction
requires the historical input identities, reuse rights and a numerical comparison
rule derived from the original output. Real-area stability then needs two
independently sourced travel-time bound families. Measurement-policy comparison
and an evaluation against independently collected observations follow. WFP
road-constraint reports cannot enter that evaluation until their dates, vehicle
scope, coverage and source lineage are established.

## Retained history

This repository now studies healthcare access. The earlier detector study is
inactive; its scientific outcome remains unresolved. The [history index](docs/history/README.md)
links its baseline materials, code, dated QA reports, figures and previous
questions. Its candidate layers and holdout remain unopened.

The [UCI trip probe](evidence/route-feasibility-20261004/README.md) is a
non-Mongolian parser demonstration, not field validation. Its reported usable
trips establish neither observed healthcare access nor off-road passability.
No route-planning repository was created or renamed.

## License

Original production code is [MIT](LICENSE). The separate
[upstream compatibility harness](tools/probe_petricola.R) is
[GPL-3.0-only](tools/PETRICOLA_PROBE_LICENSE.md). Third-party inputs retain their
own terms,
including the [baseline packet's ODbL attribution](baseline/20261003/ATTRIBUTION.md).
No Idai GPL code is incorporated into the production implementation. A future
combined derived program must meet
its applicable GPL obligations; placing it in a separate folder is insufficient.
See [qualification](evidence/access-stability-20261006/README.md) and
[contributing](CONTRIBUTING.md).
