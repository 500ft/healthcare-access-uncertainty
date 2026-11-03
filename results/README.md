# Results

Executed results verify deterministic travel-time bounds on toy graphs and
software scaling on a current Sofala OSM fixture with synthetic weights.
The historical Idai baseline has not been reproduced. WFP observation timing,
vehicle scope and independence remain unresolved, so no WFP evaluation was run.
[ROADMAP.md](../ROADMAP.md) remains the active plan.

[Current-network timing table](sofala-scaling.md) and
[executed source, scaling and upstream compatibility record](../evidence/sofala-scaling/README.md)
cover software behavior only. Historical replication still needs the author's
input identities and reuse rights; evaluation needs independently collected,
matchable observations.

![Toy travel-time intervals for nodes A to Clinic in two panels, original and widened, with the access threshold as a dotted vertical line. Colour and fill give the decision: filled blue is access, filled orange is exclusion, hollow dark grey is unresolved.](access-stability/bounds.png)

Deterministic shortest-time bounds on a toy graph, in minutes to the fixed
destination Clinic, for the 6 nodes A, B, C, D, E and Clinic. Panel (a):
original assumptions. Panel (b): widened assumptions, same axes. Each horizontal
line is one node's interval between its lower and upper travel time. Colour and
fill give the decision, which is also written at the right of each row: a filled
blue circle means definite access, a filled orange square means definite
exclusion, and a hollow dark grey diamond means unresolved. The dotted grey
vertical line is the 10-minute access threshold; equality counts as access. No
finite upper time exists for D in either panel; that line runs to the right edge
without an end marker. No path exists for E in either panel, so that row carries
only the words no path; the decision is definite exclusion. Original: access for
A, exclusion for B and E, unresolved for C and D. Widened: unresolved now also
for A and B; a definite decision remains only for E and Clinic. The bounds are
deterministic assumptions, not confidence intervals; no geography or observed
travel time is involved. Exact endpoints: README.md and bounds.csv beside this
figure. Source: evidence/access-stability-20261006/result.json.
[Caption file](access-stability/bounds.caption.md).

- [Accessible bounds and qualification tables](access-stability/README.md)
- [Bounds CSV](access-stability/bounds.csv) and [qualification CSV](access-stability/qualification.csv)
- [PDF figure](access-stability/bounds.pdf) and [render provenance](access-stability/provenance.json)
- [Original result and scientific reproduction](../evidence/access-stability-20261006/README.md)

Rebuild these views with `python analysis/plot_access_bounds.py`, then draw them with
[MATLAB](../analysis/matlab/README.md).
The [figure guide](../docs/data-and-figures.md) explains scales, encodings and retention.

The [development input record](../evidence/idai-development-inputs/README.md)
lists acquired files and missing historical identities. Its
[sensor-date check](../evidence/idai-development-inputs/flood-sensor-dates.json)
and [source review](../evidence/idai-development-inputs/source-review.json)
show why the current files cannot reproduce the published baseline.

The detector JSON records, exports and figures in this directory are retained
history. Their [previous results index and reproduction runbook](../docs/history/detector-results.md)
remain available. No detector evaluation or holdout inspection is authorized by
the software pivot. The [history index](../docs/history/README.md) explains scope.
