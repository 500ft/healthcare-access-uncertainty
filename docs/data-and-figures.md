# Data, figures and tables

## Current access result

The [PNG](../results/access-stability/bounds.png) and
[SVG](../results/access-stability/bounds.svg) show the same committed
[toy result](../evidence/access-stability-20261006/result.json).
Original and widened bounds use coordinated panels with the same node order,
scale and fixed clinic. The [method](ACCESS_STABILITY.md) defines their meaning.

- Horizontal units are minutes. The threshold comes from the result; equality
  counts as access. It is a demonstration choice, not a real-area service target.
- Blue circles and solid lines mean definite access. Red squares and dashed lines
  mean definite exclusion. Purple diamonds and dash-dot lines mean unresolved.
  The key, shapes and styles support reading without color.
- Endpoint labels reproduce the source precision. No probability or confidence
  level is assigned to these deterministic intervals.
- An arrow indicates an infinite upper bound; its displayed endpoint is not a
  finite travel time. The common axis includes zero and all finite endpoints,
  with space beyond the largest endpoint for the arrow. A disconnected node gets
  text instead of a misleading finite mark. Clinic is the fixed destination.

The [generated Markdown tables](../results/access-stability/README.md) preserve
node order and right-align minute intervals. [Bounds CSV](../results/access-stability/bounds.csv)
retains separate lower/upper/threshold columns and literal `infinity` values.
[Qualification CSV](../results/access-stability/qualification.csv) and the text
tables copy the existing qualification findings, including unavailable inputs
and unknown observation scope. Empty optional CSV fields mean unspecified in the
source. Metadata does not establish usable WFP outcomes or real-area replication.

## Reproduce the presentation

After installing `analysis[dev]`, run from the repository root:

```sh
MPLBACKEND=Agg python analysis/plot_access_bounds.py
PYTHONPATH=analysis python -m pytest analysis/tests/test_access_figure.py -q
```

The renderer reads the two committed records, writes only
`results/access-stability/`, and records source and generator hashes in
[provenance.json](../results/access-stability/provenance.json). These tables are
derived views, not additional authoritative result records. No network or model
execution is needed. The [original scientific generator](../analysis/run_access_demo.py)
and its evidence remain unchanged; its reproduction instructions are retained in
[the evidence record](../evidence/access-stability-20261006/README.md).

The visual reference is the owner's pinned enclosure
[steady-state figure](https://github.com/500ft/sensor-enclosure-thermal-design/blob/bad572fc0902437445a5446bb5bc43098cc6211f/analysis/figures/thermal_bias.png),
[transient figure](https://github.com/500ft/sensor-enclosure-thermal-design/blob/bad572fc0902437445a5446bb5bc43098cc6211f/analysis/figures/thermal_transient_prediction.png)
and [generator](https://github.com/500ft/sensor-enclosure-thermal-design/blob/bad572fc0902437445a5446bb5bc43098cc6211f/analysis/thermal_bias.py).
The redesign uses their white scientific background, coordinated panels, readable
sans-serif type, restrained grid, stable colors, redundant markers and visible
evidence status. The interval layout is specific to the access question.

## Inventory and retention

| Visual or table | Use | Disposition |
| :--- | :--- | :--- |
| Toy bounds figure | README and current results | Redesigned as PNG and SVG from the committed result. |
| Bounds and qualification tables | Current results | Generated Markdown and CSV; units and unknowns explicit. |
| Adoption/disposition table | Access method note | Retained as text: it records decisions, not quantitative evidence. |
| Original toy figure and generator | Dated evidence | Retained unchanged to preserve original hashes and reproduction. |
| Detector synthetic figures and result tables | History | Retained unchanged; the detector is inactive and superseded. |
| UCI aggregate tables | Historical parser probe | Retained unchanged; the trajectories are non-Mongolian and supply no field validation. |

The [figure manifest](figure-manifest.json) lists active and retained generators.
The [history index](history/README.md) links scientific corrections and archived
artifacts. No detector imagery, candidate overlay, reserved outcome row or holdout
was opened for this redesign. The roadmap and pending owner decisions are unchanged.
