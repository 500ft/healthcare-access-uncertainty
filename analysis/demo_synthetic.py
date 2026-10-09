"""Synthetic method demonstration: disturbance scene -> extracted candidate corridors.

This validates the extraction tooling on data with KNOWN ground truth. It is not a
Mongolia result — real extraction stays gated on the Phase-1 negative-control test.

    python analysis/demo_synthetic.py
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from catanroads.extract import candidate_coordinates_px, extract_candidates
from catanroads.synthetic import make_scene
from figstyle import COLORS, MUTED, TICK, WIDTH_IN, apply, letter, save
from plot_stress_cases import EDGE, show_input

d, truth = make_scene(size=256, seed=1)
cands = extract_candidates(d)

apply()
fig, axes = plt.subplots(1, 2, figsize=(WIDTH_IN, 4.1), gridspec_kw=dict(width_ratios=[1.09, 1]))
fig.subplots_adjust(left=.03, right=.98, top=.83, bottom=.17, wspace=.12)

show_input(fig, axes[0], d)
axes[0].set_title("Input: synthetic surface disturbance", pad=4)

axes[1].imshow(d, cmap="Greys", vmin=-1, vmax=3)
for k, c in enumerate(cands):
    axes[1].plot(*zip(*candidate_coordinates_px(c)), color=COLORS["path"], lw=1.4, path_effects=EDGE,
                 label="Delivered path (path_px)" if k == 0 else None)
axes[1].set_title(f"Extracted candidate corridors (n = {len(cands)})", pad=4)
axes[1].set_xticks([]); axes[1].set_yticks([])
axes[1].spines[:].set_visible(True); axes[1].spines[:].set_color("#808080")
for ax, tag in zip(axes, "ab"):
    letter(ax, tag)

fig.text(.02, .975, f"Synthetic method demo: {len(cands)} delivered paths trace the curved and braided corridors "
         "and part of\nthe broken one; the round blob is rejected", fontsize=9, fontweight="bold", va="top",
         linespacing=1.3)
fig.legend(loc="lower left", bbox_to_anchor=(.02, .085), borderaxespad=0, handlelength=2.4)
fig.text(.02, .015,
         "Known-truth scene make_scene(size=256, seed=1). One interior-biased path per accepted component (CR-09); "
         "no branch or\njunction recovery. Not a real-imagery result.",
         fontsize=TICK, color=MUTED, linespacing=1.4)

out = Path(__file__).resolve().parents[1] / "results" / "method_demo_synthetic.png"
save(fig, out)
print(f"wrote {out}  ({len(cands)} candidates)")
