"""Plot data and captions for the CR-09 stress-case gallery: what the extractor delivers (path_px)
against what it used to deliver (the endpoints_px chord), on synthetic constructions with known truth.

    PYTHONPATH=analysis python analysis/plot_stress_cases.py   # -> results/figures/data/*.json, *.caption.md

The MATLAB script analysis/matlab/make_stress_cases.m draws results/figures/*.png and *.pdf from
the JSON files written here. Each file holds one case: the displayed part of the disturbance field
(rounded to 0.01 z units), the reference centerline pixels and each candidate's path_px and
endpoints_px. Scores, case descriptions and outcomes go to ``<stem>.caption.md`` and are read from
results/extractor_stress_cases.json (schema v4), not typed. Synthetic only: nothing here is imagery
or a site result.
"""
import json
from pathlib import Path

import numpy as np

from catanroads.extract import candidate_coordinates_px, extract_candidates
from catanroads import stress_cases as SC

ROOT = Path(__file__).resolve().parents[1]
RECORD = ROOT / "results/extractor_stress_cases.json"
FIGURES = ROOT / "results/figures"
# Display range of the disturbance field, shared by every panel and quoted in the captions.
FIELD = {"vmin": -1, "vmax": 6}
FIELD_LABEL = "Synthetic disturbance (z units)"
FULL = ((0, 255), (0, 255))
# Case -> displayed views as ((first column, last column), (first row, last row)), 0-based pixels.
VIEWS = {"demo_reference": [FULL], "tight_curve": [((40, 216), (110, 170))],
         "wide_corridor": [((0, 47), (109, 147)), ((208, 255), (109, 147))], "low_snr": [FULL],
         "crossing": [FULL], "short_segments": [FULL], "linear_confound_riverbank": [FULL]}
SOURCE = "Source: results/extractor_stress_cases.json and analysis/catanroads/stress_cases.py."
SYNTHETIC = "Synthetic construction with known truth; not imagery and not a site result."


def _f(v):
    return "undefined" if v is None else f"{v:.2f}"


def scores(c):
    return (f"delivered path {_f(c['line_recall'])} / {_f(c['line_precision'])}, legacy chord "
            f"{_f(c['chord_line']['line_recall'])} / {_f(c['chord_line']['line_precision'])}")


def band(rec):
    return f"a {rec['tolerance']['tol_px']}-px band, measured as {rec['tolerance']['metric']}"


def styles(chords=True, ends=False):
    text = ("Geometry: the reference centerline is a thin dark grey line of pixels"
            + ("; the legacy straight chord between each candidate's endpoints_px is an orange dash-dot line"
               if chords else "")
            + "; the delivered path_px is a blue line"
            + ("; hollow blue circles mark the path endpoints" if ends else "") + ".")
    return text + (f" Grey level is the disturbance field (colour bar), {FIELD['vmin']} to {FIELD['vmax']} "
                   "z units; values beyond the scale are clipped.")


def checked(rec, name, cands):
    """The live extraction must match the committed record before it is drawn."""
    c = rec["cases"][name]
    assert len(cands) == c["n_candidates"], (name, len(cands), c["n_candidates"])
    return c


def _span(name):
    """Columns and rows covered by a case's views, so only the displayed field is stored."""
    views = VIEWS[name]
    return ((min(c[0] for c, _ in views), max(c[1] for c, _ in views)),
            (min(r[0] for _, r in views), max(r[1] for _, r in views)))


def _view(name, k=0):
    (c0, c1), (r0, r1) = VIEWS[name][k]
    return f"columns {c0} to {c1}", f"rows {r0} to {r1}"


def case_data(name, d, cl, cands):
    """Everything the MATLAB figure draws for one case."""
    (c0, c1), (r0, r1) = _span(name)
    rows, cols = np.nonzero(cl)
    return {"case": name, "generator": "analysis/plot_stress_cases.py",
            "source": "analysis/catanroads/stress_cases.py and analysis/catanroads/extract.py",
            "coordinates": "0-based pixel centres; x is the column, y is the row",
            "field_label": FIELD_LABEL, "display_range": [FIELD["vmin"], FIELD["vmax"]],
            "field_min": round(float(d[r0:r1 + 1, c0:c1 + 1].min()), 2),
            "field_max": round(float(d[r0:r1 + 1, c0:c1 + 1].max()), 2),
            "origin_px": [c0, r0],
            "views": [{"cols": list(c), "rows": list(r)} for c, r in VIEWS[name]],
            "reference_px": [[int(x), int(y)] for y, x in zip(rows, cols)],
            "candidates": [{"path_px": [[float(x), float(y)] for x, y in candidate_coordinates_px(c)],
                            # Rounded so last-digit float differences between platforms do not show.
                            "endpoints_px": [[round(float(x), 3), round(float(y), 3)] for x, y in c["endpoints_px"]]}
                           for c in cands],
            "field": (np.round(d[r0:r1 + 1, c0:c1 + 1], 2) + 0.0).tolist()}


def dumps(data):
    """JSON with one field row per line, so a change shows up as a readable diff."""
    head = {k: v for k, v in data.items() if k != "field"}
    rows = ",\n".join(json.dumps(row, separators=(",", ":")) for row in data["field"])
    return json.dumps(head, separators=(",", ":"))[:-1] + ',\n"field":[\n' + rows + "]}\n"


def figures():
    """(stem, case names, caption) for each gallery image in file order, and the data of every case."""
    rec = json.loads(RECORD.read_text())
    data, records = {}, {}
    for name in VIEWS:
        d, t, cl = SC.CASES[name](); cands = extract_candidates(d)
        records[name] = checked(rec, name, cands)
        data[name] = case_data(name, d, cl, cands)
    out = []

    # 1: the demo scene, chords against paths
    c = records["demo_reference"]
    out.append(("01_demo_paths_vs_chords", ["demo_reference"], " ".join([
        f"Demo scene: each accepted component is delivered as one path along its corridor. {SYNTHETIC}",
        "Panel (a): the known-truth synthetic disturbance field (case demo_reference).",
        f"Panel (b): the same field with the delivered geometry of the {c['n_candidates']} candidates.",
        styles(), f"Line recall / precision against the reference centerline within {band(rec)}:",
        f"{scores(c)}.", SOURCE])))

    # 2: hairpin
    c = records["tight_curve"]
    cols, rows = _view("tight_curve")
    out.append(("02_hairpin_chord_vs_path", ["tight_curve"], " ".join([
        f"Hairpin: the legacy chord cuts across the bend and the delivered path follows it. {SYNTHETIC}",
        f"Crop of case tight_curve, {cols} and {rows}. Case description: {c['doc']}",
        styles(ends=True), f"Line recall / precision against the reference centerline within {band(rec)}:",
        f"{scores(c)}.", SOURCE])))

    # 3: wide corridor
    c = records["wide_corridor"]
    # The chord lies exactly on the straight delivered path, so it is hidden; the caption says so.
    assert all(cand["endpoints_px"] == [cand["path_px"][0], cand["path_px"][-1]]
               and len({y for _, y in cand["path_px"]}) == 1 for cand in data["wide_corridor"]["candidates"])
    (left, rows), (right, _) = _view("wide_corridor", 0), _view("wide_corridor", 1)
    out.append(("03_wide_corridor_centred_endpoints", ["wide_corridor"], " ".join([
        f"Wide corridor: plan amendment A puts both path endpoints on the centre row. {SYNTHETIC}",
        f"Panel (a): left end, {left}. Panel (b): right end, {right}; {rows}",
        f"in both. Case description: {c['doc']}", styles(ends=True),
        "Here the legacy chord lies exactly on the straight delivered path and is hidden under it.",
        f"Line recall / precision against the reference centerline within {band(rec)}: {scores(c)}; both",
        "meet the frozen plan A3 target checked in analysis/tests/test_stress_cases.py.",
        f"Area coverage {_f(c['area_coverage'])}: a {rec['tolerance']['tol_px']}-px band on a wide road;",
        "it is a diagnostic, not a penalty.", SOURCE])))

    # 4: low SNR curve
    c = records["low_snr"]
    out.append(("04_low_snr_curve", ["low_snr"], " ".join([
        f"Low signal-to-noise curve: line recall rises from {_f(c['chord_line']['line_recall'])} (chord)",
        f"to {_f(c['line_recall'])} (path). {SYNTHETIC} Panel (a): the input field (case low_snr).",
        "Panel (b): the same field with the delivered geometry.", f"Case description: {c['doc']}",
        styles(), f"Line recall / precision against the reference centerline within {band(rec)}:",
        f"{scores(c)}. Component recall {_f(c['pixel_recall'])}.", SOURCE])))

    # 5: what stays missed or fabricated
    names = ["crossing", "short_segments", "linear_confound_riverbank"]
    outcome = {"crossing": "missed; the union fails min_elongation",
               "short_segments": "missed; each dash is shorter than min_length_px",
               "linear_confound_riverbank": "fabricated; delivered as the top candidate"}
    panels = []
    for name, tag in zip(names, "abc"):
        c = records[name]
        text = (f"Panel ({tag}), case {name}: {outcome[name]}. {c['doc']} {c['n_candidates']} candidate(s),"
                f" {c['n_false_candidates']} false; component recall {_f(c['pixel_recall'])}, line recall"
                f" {_f(c['line_recall'])}")
        panels.append(text + (f", line precision {_f(c['line_precision'])}." if c["line_precision"] is not None else "."))
    out.append(("05_misses_and_confound", names, " ".join([
        f"What stays missed or fabricated by construction, unchanged by CR-09. {SYNTHETIC}", *panels,
        "Undefined means the score has no denominator (no truth pixels or no candidate pixels).",
        styles(), f"Line scores use {band(rec)}.", SOURCE])))
    return out, data


def export_all(out_dir=FIGURES):
    """Write data/<case>.json and <stem>.caption.md; analysis/matlab/make_stress_cases.m draws the images."""
    out_dir = Path(out_dir); (out_dir / "data").mkdir(parents=True, exist_ok=True)
    out, data = figures()
    written = []
    for name, item in data.items():
        path = out_dir / "data" / f"{name}.json"
        path.write_text(dumps(item))
        written.append(path)
    for stem, _, caption in out:
        path = out_dir / f"{stem}.caption.md"
        path.write_text(caption + "\n")
        written.append(path)
    return written


if __name__ == "__main__":
    for p in export_all():
        print("wrote", p.relative_to(ROOT))
