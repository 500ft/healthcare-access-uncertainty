# MATLAB figures and tables

These scripts draw every data figure in the repository and write the two headline
tables as LaTeX. They read committed data only. Python computes and exports; MATLAB
R2025b draws.

Regenerate from the repository root:

```sh
python analysis/plot_access_bounds.py              # captions, CSV, Markdown tables, provenance
python analysis/plot_stress_cases.py               # stress-case plot data and captions
python analysis/demo_synthetic.py                  # demo caption and data check
cd analysis/matlab && matlab -batch make_figures   # PNG (300 dpi) and PDF beside each doc path
```

`make_figures` runs three scripts:

| Script | Reads | Writes |
| :--- | :--- | :--- |
| `make_access_bounds.m` | `results/access-stability/bounds.csv` | `results/access-stability/bounds.png`, `.pdf` |
| `make_access_tables.m` | `bounds.csv`, `evidence/access-stability-20261006/qualification.json` | `bounds_table.tex`, `qualification_table.tex` |
| `make_stress_cases.m` | `results/figures/data/*.json` | `results/figures/0*.png`, `.pdf`; `results/method_demo_synthetic.png`, `.pdf` |

`fig_style.m` sets the shared style: LaTeX text, 9/8/7 pt type, MATLAB blue for the
main series, orange for the comparison and dark grey for axes and text.
`export_pair.m` writes each PDF and 300-dpi PNG.

The table fragments are `tabular` environments. Typeset each one inside a standalone
page with `fontspec`, `booktabs`, `siunitx` and `xcolor` (XeLaTeX or Tectonic), then
rasterise at 300 dpi:

```latex
\documentclass[border=6pt]{standalone}
\usepackage{fontspec}\usepackage{booktabs}\usepackage{siunitx}\usepackage{xcolor}
\begin{document}\input{bounds_table.tex}\end{document}
```

```sh
pdftoppm -r 300 -png -singlefile bounds_table.pdf bounds_table
```

The words for each figure live in its `*.caption.md` file, written by the Python
script. Tests check the plot data, table fragments and captions against the records.
Pixels are not compared.
