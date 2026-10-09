"""Gallery of the CR-09 stress cases: what the extractor delivers (path_px) against what it used to
deliver (the endpoints_px chord), on synthetic constructions with known truth.

    MPLBACKEND=Agg PYTHONPATH=analysis python analysis/plot_stress_cases.py   # -> results/figures/*.png

Numbers in the titles are read from results/extractor_stress_cases.json (schema v4). Synthetic
only: nothing here is imagery or a site result.
"""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.patheffects as pe
import matplotlib.pyplot as plt
import numpy as np

from catanroads.extract import candidate_coordinates_px, extract_candidates
from catanroads import stress_cases as SC
from figstyle import COLORS, MUTED, SMALL, TICK, WIDTH_IN, apply, letter, save

ROOT = Path(__file__).resolve().parents[1]
FOOT = "Synthetic construction (analysis/catanroads/stress_cases.py); not imagery, not a site result."
EDGE = [pe.Stroke(linewidth=2.6, foreground="#1a1a1a"), pe.Normal()]  # keeps the path visible on any grey


def _f(v):
    return "—" if v is None else f"{v:.2f}"


def show_input(fig, ax, d, cmap="BrBG_r", vmin=-2, vmax=2):
    """The disturbance field itself, with its colour scale."""
    im = ax.imshow(d, cmap=cmap, vmin=vmin, vmax=vmax)
    ax.set_xticks([]); ax.set_yticks([])
    bar = fig.colorbar(im, ax=ax, fraction=.046, pad=.03)
    bar.set_label("Synthetic disturbance (z units)", fontsize=SMALL)
    bar.ax.tick_params(labelsize=TICK)


def draw(ax, d, cl, cands, title, vmin=-1, vmax=3, chords=True, ends=False, note=None):
    ax.imshow(d, cmap="Greys", vmin=vmin, vmax=vmax)
    h, w = d.shape
    ys, xs = np.nonzero(cl)
    ax.scatter(xs, ys, s=1, color=COLORS["reference"], zorder=2)
    ax.plot([], [], ".", color=COLORS["reference"], ms=6, label="Reference centerline")  # legend key only
    for k, c in enumerate(cands):
        if chords:
            (x0, y0), (x1, y1) = c["endpoints_px"]
            ax.plot([x0, x1], [y0, y1], "--", color=COLORS["chord"], lw=1.1,
                    label="Legacy chord (endpoints_px)" if k == 0 else None, zorder=3)
        px, py = zip(*candidate_coordinates_px(c))
        ax.plot(px, py, color=COLORS["path"], lw=1.4, path_effects=EDGE,
                label="Delivered path (path_px)" if k == 0 else None, zorder=4)
        if ends:
            ax.plot([px[0], px[-1]], [py[0], py[-1]], "o", color=COLORS["path"], mec="#1a1a1a",
                    mew=.8, ms=4.5, ls="none", label="Path endpoint" if k == 0 else None, zorder=5)
    ax.set_xlim(-0.5, w - 0.5); ax.set_ylim(h - 0.5, -0.5)
    ax.set_title(title, pad=4)
    if note:
        ax.set_xlabel(note, fontsize=SMALL, color=MUTED, labelpad=4)
    ax.set_xticks([]); ax.set_yticks([])
    ax.spines[:].set_visible(True); ax.spines[:].set_color("#808080")


def plot_all(out_dir):
    apply()
    out_dir = Path(out_dir); out_dir.mkdir(parents=True, exist_ok=True)
    rec = json.loads((ROOT / "results/extractor_stress_cases.json").read_text())["cases"]

    def scores(name):
        c = rec[name]
        return (f"Line recall / precision vs centerline (2-px band)\n"
                f"path {_f(c['line_recall'])} / {_f(c['line_precision'])}  ·  "
                f"legacy chord {_f(c['chord_line']['line_recall'])} / {_f(c['chord_line']['line_precision'])}")

    def finish(fig, name, title, legend_y):
        fig.text(.02, .975, title, fontsize=9, fontweight="bold", va="top")
        fig.text(.02, .012, FOOT, fontsize=TICK, color=MUTED)
        handles, labels = [], []
        for ax in fig.axes:
            for h, l in zip(*ax.get_legend_handles_labels()):
                if l not in labels:
                    handles.append(h); labels.append(l)
        if handles:
            fig.legend(handles, labels, loc="lower left", bbox_to_anchor=(.02, legend_y), ncol=4,
                       handlelength=2.4, columnspacing=1.2, borderaxespad=0)
        path = out_dir / f"{name}.png"; save(fig, path); plt.close(fig); return path

    written = []
    # 1: the demo scene, chords against paths
    d, t, cl = SC.case_demo_reference(); cands = extract_candidates(d)
    fig, axes = plt.subplots(1, 2, figsize=(WIDTH_IN, 4.3), gridspec_kw=dict(width_ratios=[1.09, 1]))
    fig.subplots_adjust(left=.03, right=.98, top=.83, bottom=.24, wspace=.12)
    show_input(fig, axes[0], d)
    axes[0].set_title("Input: known-truth synthetic scene", pad=4)
    draw(axes[1], d, cl, cands, f"Delivered geometry, {len(cands)} candidates", note=scores("demo_reference"))
    for ax, tag in zip(axes, "ab"):
        letter(ax, tag)
    written.append(finish(fig, "01_demo_paths_vs_chords",
                          "Demo scene: each accepted component is delivered as one path along its corridor", .065))
    # 2: hairpin
    d, t, cl = SC.case_tight_curve(); cands = extract_candidates(d)
    fig, ax = plt.subplots(figsize=(WIDTH_IN, 3.6))
    fig.subplots_adjust(left=.03, right=.97, top=.83, bottom=.27)
    draw(ax, d, cl, cands, "Half-ellipse corridor, 128 px wide and about 20 px tall",
         ends=True, note=scores("tight_curve"))
    ax.set_xlim(40, 216); ax.set_ylim(170, 110)
    written.append(finish(fig, "02_hairpin_chord_vs_path",
                          "Hairpin: the legacy chord cuts across the bend and the delivered path follows it", .075))
    # 3: wide corridor
    d, t, cl = SC.case_wide_corridor(); cands = extract_candidates(d)
    fig, axes = plt.subplots(1, 2, figsize=(WIDTH_IN, 3.6))
    fig.subplots_adjust(left=.03, right=.97, top=.83, bottom=.31, wspace=.06)
    for ax, (x0, x1), side, tag in zip(axes, ((-0.5, 47.5), (207.5, 255.5)), ("Left", "Right"), "ab"):
        draw(ax, d, cl, cands, f"{side} end of the 13-px corridor", ends=True)
        ax.set_xlim(x0, x1); ax.set_ylim(147.5, 108.5)
        letter(ax, tag)
    w = rec["wide_corridor"]
    fig.text(.03, .2, scores("wide_corridor").replace("\n", ": ")
             + f"\nArea coverage {_f(w['area_coverage'])}: a 2-px band on a 13-px road, a diagnostic and not a penalty",
             fontsize=SMALL, color=MUTED, linespacing=1.4)
    written.append(finish(fig, "03_wide_corridor_centred_endpoints",
                          "Wide corridor: amendment A puts both endpoints on the centre row (A3 target ≥ 0.98)", .075))
    # 4: low SNR curve
    d, t, cl = SC.case_low_snr(); cands = extract_candidates(d)
    fig, axes = plt.subplots(1, 2, figsize=(WIDTH_IN, 4.3), gridspec_kw=dict(width_ratios=[1.09, 1]))
    fig.subplots_adjust(left=.03, right=.98, top=.83, bottom=.24, wspace=.12)
    show_input(fig, axes[0], d, cmap="Greys", vmin=-2, vmax=4)
    axes[0].set_title("Input at 3× the demo noise (σ = 0.9)", pad=4)
    draw(axes[1], d, cl, cands, "Delivered geometry", vmin=-2, vmax=4,
         note=scores("low_snr") + f"\ncomponent recall {_f(rec['low_snr']['pixel_recall'])}")
    for ax, tag in zip(axes, "ab"):
        letter(ax, tag)
    c = rec["low_snr"]
    written.append(finish(fig, "04_low_snr_curve",
                          f"Low signal-to-noise curve: line recall rises from {_f(c['chord_line']['line_recall'])} "
                          f"(chord) to {_f(c['line_recall'])} (path)", .065))
    # 5: what stays missed or fabricated
    fig, axes = plt.subplots(1, 3, figsize=(WIDTH_IN, 3.7))
    fig.subplots_adjust(left=.03, right=.98, top=.76, bottom=.27, wspace=.1)
    for ax, name, label, tag in zip(axes, ("crossing", "short_segments", "linear_confound_riverbank"),
                                    ("Crossing: missed\nunion fails min_elongation",
                                     "Dashed track: missed\n9-px dashes < min_length_px",
                                     "River bank: fabricated\ndelivered as top candidate"), "abc"):
        d, t, cl = SC.CASES[name](); cands = extract_candidates(d); c = rec[name]
        note = (f"{c['n_candidates']} candidate(s), {c['n_false_candidates']} false\n"
                f"component recall {_f(c['pixel_recall'])} · line recall {_f(c['line_recall'])}")
        if c["line_precision"] is not None:
            note += f"\nline precision {_f(c['line_precision'])}"
        draw(ax, d, cl, cands, label, note=note)
        letter(ax, tag)
    written.append(finish(fig, "05_misses_and_confound",
                          "What stays missed or fabricated by construction, unchanged by CR-09", .065))
    return written


if __name__ == "__main__":
    for p in plot_all(ROOT / "results" / "figures"):
        print("wrote", p.relative_to(ROOT))
