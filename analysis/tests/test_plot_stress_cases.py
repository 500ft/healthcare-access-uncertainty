"""The detector figures show only the field and geometry; their words live in caption files.

Pixels are not compared (font rasterisation differs between machines). The drawn demo paths are
checked against the committed record, the canvas text against the allowed set, and the captions
against their files and the history page that shows the demo figure.
"""
import json
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import pytest
from matplotlib.text import Text

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import demo_synthetic  # noqa: E402
import figstyle  # noqa: E402
import plot_stress_cases as gallery  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
RECORD = json.loads((ROOT / "results/extractor_stress_cases.json").read_text())


@pytest.fixture(scope="module")
def built():
    figures = gallery.figures()
    d, cands = demo_synthetic.scene()
    demo = ("method_demo_synthetic", demo_synthetic.figure(d, cands), demo_synthetic.caption(cands))
    yield figures + [demo]
    for _, fig, _ in figures + [demo]:
        plt.close(fig)


def test_gallery_writes_five_figures(tmp_path):
    written = gallery.plot_all(tmp_path)
    assert len(written) == 5 and all(p.exists() and p.stat().st_size > 10_000 for p in written)
    assert all(p.with_suffix(".caption.md").exists() for p in written)


def test_demo_paths_equal_committed_record(built):
    expected = [c["path_px"] for c in RECORD["cases"]["demo_reference"]["exported_paths_px"]]
    for stem, fig, _ in built:
        if stem not in ("01_demo_paths_vs_chords", "method_demo_synthetic"):
            continue
        paths = [line for line in fig.axes[1].lines if (line.get_gid() or "").startswith("path:")]
        drawn = [[[x, y] for x, y in zip(p.get_xdata(), p.get_ydata())] for p in paths]
        assert drawn == expected, stem


def test_canvas_holds_only_letters_colourbar_and_legend(built):
    for stem, fig, _ in built:
        printed = {t.get_text() for t in fig.findobj(Text) if t.get_visible() and t.get_text().strip()}
        allowed = {f"({c})" for c in "abc"} | {gallery.FIELD_LABEL}
        allowed |= {t.get_text() for legend in fig.legends for t in legend.get_texts()}
        allowed |= {t.get_text() for ax in fig.axes for t in ax.get_yticklabels()}
        assert printed <= allowed, (stem, printed - allowed)
        assert not any(ax.get_title() for ax in fig.axes), stem


def test_nothing_printed_touches_anything(built):
    for stem, fig, _ in built:
        assert figstyle.audit(fig) == [], stem


def test_captions_match_files_and_docs(built):
    squash = lambda s: " ".join(s.split())
    for stem, _, caption in built:
        folder = ROOT / "results" / ("" if stem == "method_demo_synthetic" else "figures")
        assert caption == (folder / f"{stem}.caption.md").read_text().strip(), stem
    demo = dict((stem, caption) for stem, _, caption in built)["01_demo_paths_vs_chords"]
    assert "delivered path 0.93 / 1.00, legacy chord 0.44 / 0.45" in demo
    assert squash(demo) in squash((ROOT / "docs/history/detector-overview.md").read_text())
