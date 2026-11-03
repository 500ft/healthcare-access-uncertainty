"""The detector figures are drawn by MATLAB from plot data written here; their words live in caption files.

Pixels are not compared (font rasterisation differs between machines). The plot data are checked
against the committed files and the stress record, and the captions against their files and the
history page that shows the demo figure.
"""
import json
import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import demo_synthetic  # noqa: E402
import plot_stress_cases as gallery  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
RECORD = json.loads((ROOT / "results/extractor_stress_cases.json").read_text())


@pytest.fixture(scope="module")
def built():
    out, data = gallery.figures()
    d, cands = demo_synthetic.scene()
    return out + [("method_demo_synthetic", ["demo_reference"], demo_synthetic.caption(cands))], data


def _mismatches(fresh, committed):
    """Short list of differences between two case files.

    Values are compared, with one 0.01 rounding step of slack for the field and 0.001 px for
    geometry, so last-bit float differences between platforms pass. The list stays short so a
    failure never asks pytest to diff two large files.
    """
    out = []
    for key in sorted(fresh.keys() | committed.keys()):
        a, b = fresh.get(key), committed.get(key)
        if key in ("field", "field_min", "field_max"):
            a, b = np.array(a, float), np.array(b, float)
            if a.shape != b.shape or np.abs(a - b).max() > 0.0101:
                out.append(key)
        elif key == "candidates":
            if len(a) != len(b) or any(
                    np.shape(x[k]) != np.shape(y[k]) or not np.allclose(x[k], y[k], rtol=0, atol=1e-3)
                    for x, y in zip(a, b) for k in ("path_px", "endpoints_px")):
                out.append(key)
        elif a != b:
            out.append(key)
    return out


def test_export_matches_committed_files(tmp_path):
    written = gallery.export_all(tmp_path)
    assert len(written) == 12
    for path in written:
        committed = gallery.FIGURES / path.relative_to(tmp_path)
        if path.suffix == ".json":
            problems = _mismatches(json.loads(path.read_text()), json.loads(committed.read_text()))
            assert not problems, (path.name, problems)
        else:
            assert path.read_text() == committed.read_text(), path.name


def test_plot_data_hold_the_displayed_views(built):
    _, data = built
    for name, item in data.items():
        (c0, c1), (r0, r1) = gallery._span(name)
        assert item["origin_px"] == [c0, r0]
        assert len(item["field"]) == r1 - r0 + 1 and {len(r) for r in item["field"]} == {c1 - c0 + 1}
        assert item["display_range"] == [gallery.FIELD["vmin"], gallery.FIELD["vmax"]]
        assert len(item["candidates"]) == RECORD["cases"][name]["n_candidates"], name


def test_demo_paths_equal_committed_record(built):
    _, data = built
    expected = [c["path_px"] for c in RECORD["cases"]["demo_reference"]["exported_paths_px"]]
    assert [c["path_px"] for c in data["demo_reference"]["candidates"]] == expected
    demo_synthetic.check(*demo_synthetic.scene(), data["demo_reference"])


def test_captions_match_files_and_docs(built):
    out, _ = built
    squash = lambda s: " ".join(s.split())
    for stem, _, caption in out:
        folder = ROOT / "results" / ("" if stem == "method_demo_synthetic" else "figures")
        assert caption == (folder / f"{stem}.caption.md").read_text().strip(), stem
    demo = dict((stem, caption) for stem, _, caption in out)["01_demo_paths_vs_chords"]
    assert "delivered path 0.93 / 1.00, legacy chord 0.44 / 0.45" in demo
    assert squash(demo) in squash((ROOT / "docs/history/detector-overview.md").read_text())
