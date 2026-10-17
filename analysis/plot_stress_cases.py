"""Gallery of the CR-09 stress cases: what the extractor delivers (path_px) against what it used to
deliver (the endpoints_px chord), on synthetic constructions with known truth.

    MPLBACKEND=Agg PYTHONPATH=analysis python analysis/plot_stress_cases.py   # -> results/figures/*.png

The canvas carries only the field, the geometry, panel letters, a colourbar and one legend. Scores,
case descriptions and outcomes are written by the caption builders to ``<stem>.caption.md`` and are
read from results/extractor_stress_cases.json (schema v4), not typed. Synthetic only: nothing here
is imagery or a site result.
"""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.patheffects as pe
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import ListedColormap
from matplotlib.lines import Line2D

from catanroads.extract import candidate_coordinates_px, extract_candidates
from catanroads import stress_cases as SC
from figstyle import INK, WIDTH_IN, apply, letter, save

ROOT = Path(__file__).resolve().parents[1]
RECORD = ROOT / "results/extractor_stress_cases.json"
# One grey scale for every panel, light enough that black geometry stays visible on a corridor.
FIELD = {"cmap": "Greys", "vmin": -1, "vmax": 6}
FIELD_LABEL = "Synthetic disturbance [z units]"
# Geometry is told apart by line style: the delivered path is a white line with a black edge,
# the legacy chord is dash-dot, the reference centerline is a thin solid line of pixels.
PATH = {"color": "white", "lw": 1.3, "path_effects": [pe.Stroke(linewidth=2.7, foreground=INK), pe.Normal()]}
CHORD = {"color": INK, "lw": 1.0, "ls": (0, (5, 1.5, 1, 1.5))}
REFERENCE = {"color": INK, "lw": .8}
ENDPOINT = {"marker": "o", "ls": "none", "mfc": "white", "mec": INK, "mew": .9, "ms": 4.5}
KEYS = {"reference": Line2D([], [], label="Reference centerline", **REFERENCE),
        "chord": Line2D([], [], label="Legacy chord", **CHORD),
        "path": Line2D([], [], label="Delivered path", **PATH),
        "end": Line2D([], [], label="Path endpoint", **ENDPOINT)}
SOURCE = "Source: results/extractor_stress_cases.json and analysis/catanroads/stress_cases.py."
SYNTHETIC = "Synthetic construction with known truth; not imagery and not a site result."


def _f(v):
    return "undefined" if v is None else f"{v:.2f}"


def field(ax, d):
    """The disturbance field in the shared grey scale; no ticks, since pixels carry no unit here."""
    im = ax.imshow(d, **FIELD)
    ax.set_xticks([]); ax.set_yticks([])
    ax.spines[:].set_visible(True)
    return im


def colorbar(fig, im, axes, fields):
    clipped = (min(d.min() for d in fields) < FIELD["vmin"], max(d.max() for d in fields) > FIELD["vmax"])
    extend = {(False, False): "neither", (True, False): "min", (False, True): "max", (True, True): "both"}[clipped]
    bar = fig.colorbar(im, ax=axes, fraction=.046, pad=.03, extend=extend)
    bar.set_label(FIELD_LABEL)
    bar.ax.tick_params(length=3)
    return bar


def draw(ax, d, cl, cands, chords=True, ends=False):
    im = field(ax, d)
    h, w = d.shape
    ax.imshow(np.ma.masked_where(~cl, cl), cmap=ListedColormap([INK]), interpolation="nearest", zorder=2)
    for k, c in enumerate(cands):
        if chords:
            (x0, y0), (x1, y1) = c["endpoints_px"]
            ax.plot([x0, x1], [y0, y1], zorder=3, gid=f"chord:{k}", **CHORD)
        px, py = zip(*candidate_coordinates_px(c))
        ax.plot(px, py, zorder=4, gid=f"path:{k}", **PATH)
        if ends:
            ax.plot([px[0], px[-1]], [py[0], py[-1]], zorder=5, **ENDPOINT)
    ax.set_xlim(-0.5, w - 0.5); ax.set_ylim(h - 0.5, -0.5)
    return im


def legend(fig, keys, y=.995):
    handles = [KEYS[k] for k in keys]
    fig.legend(handles=handles, loc="upper center", bbox_to_anchor=(.5, y), ncol=len(handles),
               handlelength=2.6, columnspacing=1.4, handletextpad=.5, borderaxespad=0)


def scores(c):
    return (f"delivered path {_f(c['line_recall'])} / {_f(c['line_precision'])}, legacy chord "
            f"{_f(c['chord_line']['line_recall'])} / {_f(c['chord_line']['line_precision'])}")


def band(rec):
    return f"a {rec['tolerance']['tol_px']}-px band, measured as {rec['tolerance']['metric']}"


def styles(chords=True, ends=False):
    text = ("Geometry: the reference centerline is a thin solid black line of pixels"
            + ("; the legacy straight chord between each candidate's endpoints_px is dash-dot" if chords else "")
            + "; the delivered path_px is a white line with a black edge"
            + ("; hollow circles mark the path endpoints" if ends else "") + ".")
    return text + (f" Grey level is the disturbance field (colourbar), {FIELD['vmin']} to {FIELD['vmax']} "
                   "z units; values beyond the scale are clipped.")


def checked(rec, name, cands):
    """The live extraction must match the committed record before it is drawn."""
    c = rec["cases"][name]
    assert len(cands) == c["n_candidates"], (name, len(cands), c["n_candidates"])
    return c


def figures():
    """(stem, figure, caption) for each gallery image, in file order."""
    apply()
    rec = json.loads(RECORD.read_text())
    out = []

    # 1: the demo scene, chords against paths
    d, t, cl = SC.case_demo_reference(); cands = extract_candidates(d)
    c = checked(rec, "demo_reference", cands)
    fig, axes = plt.subplots(1, 2, figsize=(WIDTH_IN, 3.45))
    fig.subplots_adjust(left=.02, right=.93, top=.80, bottom=.03, wspace=.06)
    field(axes[0], d)
    im = draw(axes[1], d, cl, cands)
    colorbar(fig, im, list(axes), [d])
    for ax, tag in zip(axes, "ab"):
        letter(ax, tag)
    legend(fig, ("reference", "chord", "path"))
    out.append(("01_demo_paths_vs_chords", fig, " ".join([
        f"Demo scene: each accepted component is delivered as one path along its corridor. {SYNTHETIC}",
        "Panel (a): the known-truth synthetic disturbance field (case demo_reference).",
        f"Panel (b): the same field with the delivered geometry of the {c['n_candidates']} candidates.",
        styles(), f"Line recall / precision against the reference centerline within {band(rec)}:",
        f"{scores(c)}.", SOURCE])))

    # 2: hairpin
    d, t, cl = SC.case_tight_curve(); cands = extract_candidates(d)
    c = checked(rec, "tight_curve", cands)
    fig, ax = plt.subplots(figsize=(WIDTH_IN, 2.85))
    fig.subplots_adjust(left=.02, right=.95, top=.86, bottom=.03)
    im = draw(ax, d, cl, cands, ends=True)
    ax.set_xlim(40, 216); ax.set_ylim(170, 110)
    colorbar(fig, im, ax, [d[110:171, 40:217]])
    legend(fig, ("reference", "chord", "path", "end"))
    out.append(("02_hairpin_chord_vs_path", fig, " ".join([
        f"Hairpin: the legacy chord cuts across the bend and the delivered path follows it. {SYNTHETIC}",
        f"Crop of case tight_curve, columns 40 to 216 and rows 110 to 170. Case description: {c['doc']}",
        styles(ends=True), f"Line recall / precision against the reference centerline within {band(rec)}:",
        f"{scores(c)}.", SOURCE])))

    # 3: wide corridor
    d, t, cl = SC.case_wide_corridor(); cands = extract_candidates(d)
    c = checked(rec, "wide_corridor", cands)
    # The chord lies exactly on the straight delivered path, so it is hidden; the caption says so.
    assert all(cand["endpoints_px"] == [cand["path_px"][0], cand["path_px"][-1]]
               and len({y for _, y in cand["path_px"]}) == 1 for cand in cands)
    fig, axes = plt.subplots(1, 2, figsize=(WIDTH_IN, 2.55))
    fig.subplots_adjust(left=.02, right=.93, top=.80, bottom=.04, wspace=.06)
    crops = ((-0.5, 47.5), (207.5, 255.5))
    for ax, (x0, x1), tag in zip(axes, crops, "ab"):
        im = draw(ax, d, cl, cands, ends=True)
        ax.set_xlim(x0, x1); ax.set_ylim(147.5, 108.5)
        letter(ax, tag)
    colorbar(fig, im, list(axes), [d[109:148, :48], d[109:148, 208:]])
    legend(fig, ("reference", "chord", "path", "end"))
    out.append(("03_wide_corridor_centred_endpoints", fig, " ".join([
        f"Wide corridor: plan amendment A puts both path endpoints on the centre row. {SYNTHETIC}",
        "Panel (a): left end, columns 0 to 47. Panel (b): right end, columns 208 to 255; rows 109 to 147",
        f"in both. Case description: {c['doc']}", styles(ends=True),
        "Here the legacy chord lies exactly on the straight delivered path and is hidden under it.",
        f"Line recall / precision against the reference centerline within {band(rec)}: {scores(c)}; both",
        "meet the frozen plan A3 target checked in analysis/tests/test_stress_cases.py.",
        f"Area coverage {_f(c['area_coverage'])}: a {rec['tolerance']['tol_px']}-px band on a wide road;",
        "it is a diagnostic, not a penalty.", SOURCE])))

    # 4: low SNR curve
    d, t, cl = SC.case_low_snr(); cands = extract_candidates(d)
    c = checked(rec, "low_snr", cands)
    fig, axes = plt.subplots(1, 2, figsize=(WIDTH_IN, 3.45))
    fig.subplots_adjust(left=.02, right=.93, top=.80, bottom=.03, wspace=.06)
    field(axes[0], d)
    im = draw(axes[1], d, cl, cands)
    colorbar(fig, im, list(axes), [d])
    for ax, tag in zip(axes, "ab"):
        letter(ax, tag)
    legend(fig, ("reference", "chord", "path"))
    out.append(("04_low_snr_curve", fig, " ".join([
        f"Low signal-to-noise curve: line recall rises from {_f(c['chord_line']['line_recall'])} (chord)",
        f"to {_f(c['line_recall'])} (path). {SYNTHETIC} Panel (a): the input field (case low_snr).",
        "Panel (b): the same field with the delivered geometry.", f"Case description: {c['doc']}",
        styles(), f"Line recall / precision against the reference centerline within {band(rec)}:",
        f"{scores(c)}. Component recall {_f(c['pixel_recall'])}.", SOURCE])))

    # 5: what stays missed or fabricated
    names = ("crossing", "short_segments", "linear_confound_riverbank")
    outcome = {"crossing": "missed; the union fails min_elongation",
               "short_segments": "missed; each dash is shorter than min_length_px",
               "linear_confound_riverbank": "fabricated; delivered as the top candidate"}
    fig, axes = plt.subplots(1, 3, figsize=(WIDTH_IN, 2.75))
    fig.subplots_adjust(left=.02, right=.92, top=.80, bottom=.03, wspace=.06)
    fields, panels = [], []
    for ax, name, tag in zip(axes, names, "abc"):
        d, t, cl = SC.CASES[name](); cands = extract_candidates(d); c = checked(rec, name, cands)
        im = draw(ax, d, cl, cands)
        letter(ax, tag)
        fields.append(d)
        text = (f"Panel ({tag}), case {name}: {outcome[name]}. {c['doc']} {c['n_candidates']} candidate(s),"
                f" {c['n_false_candidates']} false; component recall {_f(c['pixel_recall'])}, line recall"
                f" {_f(c['line_recall'])}")
        panels.append(text + (f", line precision {_f(c['line_precision'])}." if c["line_precision"] is not None else "."))
    colorbar(fig, im, list(axes), fields)
    legend(fig, ("reference", "chord", "path"))
    out.append(("05_misses_and_confound", fig, " ".join([
        f"What stays missed or fabricated by construction, unchanged by CR-09. {SYNTHETIC}", *panels,
        "Undefined means the score has no denominator (no truth pixels or no candidate pixels).",
        styles(), f"Line scores use {band(rec)}.", SOURCE])))
    return out


def plot_all(out_dir):
    out_dir = Path(out_dir); out_dir.mkdir(parents=True, exist_ok=True)
    written = []
    for stem, fig, caption in figures():
        path = save(fig, out_dir / f"{stem}.png")
        path.with_suffix(".caption.md").write_text(caption + "\n")
        plt.close(fig)
        written.append(path)
    return written


if __name__ == "__main__":
    for p in plot_all(ROOT / "results" / "figures"):
        print("wrote", p.relative_to(ROOT))
