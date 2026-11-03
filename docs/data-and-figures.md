# Data, figures and tables

## Current access result

The [PNG](../results/access-stability/bounds.png) and
[PDF](../results/access-stability/bounds.pdf) show the same committed
[toy result](../evidence/access-stability-20261006/result.json).
Original and widened bounds use coordinated panels with the same node order,
scale and fixed clinic. The [method](ACCESS_STABILITY.md) defines their meaning.

- Horizontal units are minutes. The threshold comes from the result; equality
  counts as access. It is a demonstration choice, not a real-area service target.
- Colour and fill carry the decision. A filled blue circle is definite access, a
  filled orange square is definite exclusion and a hollow dark grey diamond is
  unresolved. The decision is also written at the right of each row, so the
  figure reads in greyscale.
- Minor ticks are 1 min apart. Exact endpoints at source precision are in the
  typeset table. No probability or confidence level is assigned to these
  deterministic intervals.
- A line that runs to the right edge with a marker only at its left end has no
  finite upper time. A disconnected node carries the words "no path" on its row.
  Clinic is the fixed destination.
- The dotted grey threshold line is labelled once, in panel a. The title, panel
  descriptions and outcomes are in the
  [caption file](../results/access-stability/bounds.caption.md), which the
  Python script writes and the README repeats under the image.

The [results page](../results/access-stability/README.md) shows the bounds and
qualification tables typeset with booktabs and siunitx. Each image sits above the
same table as Markdown text in a collapsed block, so the values stay searchable.
[Bounds CSV](../results/access-stability/bounds.csv) retains separate
lower/upper/threshold columns and literal `infinity` values.
[Qualification CSV](../results/access-stability/qualification.csv) and the text
tables copy the existing qualification findings, including unavailable inputs
and unknown observation scope. Empty optional CSV fields mean unspecified in the
source. Metadata does not establish usable WFP outcomes or real-area replication.

## Reproduce the presentation

Python writes captions, tables and plot data; MATLAB R2025b draws. From the
repository root:

```sh
python analysis/plot_access_bounds.py
python analysis/plot_stress_cases.py
python analysis/demo_synthetic.py
cd analysis/matlab && matlab -batch make_figures
```

The [MATLAB README](../analysis/matlab/README.md) lists what each script reads and
writes and how to typeset the table fragments. `plot_access_bounds.py` reads the
two committed records, writes only `results/access-stability/`, and records
source and generator hashes in
[provenance.json](../results/access-stability/provenance.json). These tables are
derived views, not additional authoritative result records. No network or model
execution is needed. The [original scientific generator](../analysis/run_access_demo.py)
and its evidence remain unchanged; its reproduction instructions are retained in
[the evidence record](../evidence/access-stability-20261006/README.md).

`plot_stress_cases.py` writes one JSON file per synthetic case to
`results/figures/data/`: the displayed part of the disturbance field rounded to
0.01 z units, the reference centerline pixels and each candidate's path and chord.
The demo figure reuses the `demo_reference` file; `demo_synthetic.py` checks that
it matches `make_scene(size=256, seed=1)`.

All figures follow [fig_style.m](../analysis/matlab/fig_style.m): LaTeX text in
Computer Modern, 9 pt axis labels, 8 pt labels and 7 pt ticks, bold 10 pt panel
letters, and 300-dpi PNG plus vector PDF. The canvas holds data, axes, panel
letters, a colour bar where a field is shown, and short labels in the colour of
the series they name. Titles, scores and notes are in a `<stem>.caption.md` file
beside each image. In the detector figures grey is the disturbance field, the
delivered path is blue, the legacy chord is an orange dash-dot line, path
endpoints are hollow blue circles and the reference centerline is a thin line of
dark grey pixels. The style follows the owner's 2026-11-02 request to redraw all
data visuals in MATLAB with LaTeX.

## Inventory and retention

| Visual or table | Use | Disposition |
| :--- | :--- | :--- |
| Toy bounds figure | README and current results | Drawn in MATLAB from `bounds.csv` as PNG and PDF. |
| Bounds and qualification tables | Current results | Typeset by MATLAB and LaTeX from the CSV and qualification record; Markdown text kept below each image. |
| Reserved WFP candidate table | Current results | Retained as Markdown text: its cells are findings with no numeric values. |
| Adoption/disposition table | Access method note | Retained as text: it records decisions, not quantitative evidence. |
| Original toy figure and generator | Dated evidence | Retained unchanged to preserve original hashes and reproduction. |
| Detector stress-case and demo figures | History | Drawn in MATLAB from the exported case data; captions beside each image. |
| Detector result tables | History | Retained unchanged; the detector is inactive and superseded. |
| Parameter register | Detector parameters | Value column right-aligned; values unchanged and still checked by `test_parameter_register.py`. |
| UCI aggregate tables | Historical parser probe | Retained unchanged; the trajectories are non-Mongolian and supply no field validation. |

The [figure manifest](figure-manifest.json) lists active and retained generators.
The [history index](history/README.md) links scientific corrections and archived
artifacts. No detector imagery, candidate overlay, reserved outcome row or holdout
was opened for this redesign. The roadmap and pending owner decisions are unchanged.
