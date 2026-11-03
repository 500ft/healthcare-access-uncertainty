"""Synthetic method demonstration: disturbance scene -> extracted candidate corridors.

This validates the extraction tooling on data with KNOWN ground truth. It is not a
Mongolia result — real extraction stays gated on the Phase-1 negative-control test.
The scene is the stress case demo_reference, so analysis/matlab/make_stress_cases.m
draws ``method_demo_synthetic.png`` from results/figures/data/demo_reference.json.
This script checks that the scene and its paths match that file and writes the
words to ``method_demo_synthetic.caption.md`` beside the image.

    python analysis/demo_synthetic.py
"""
import json
from pathlib import Path

import numpy as np

from catanroads.extract import candidate_coordinates_px, extract_candidates
from catanroads.synthetic import make_scene
from plot_stress_cases import FIELD, FIGURES

OUT = Path(__file__).resolve().parents[1] / "results" / "method_demo_synthetic.png"
DATA = FIGURES / "data" / "demo_reference.json"


def scene():
    d, _truth = make_scene(size=256, seed=1)
    return d, extract_candidates(d)


def check(d, cands, data):
    """The plotted file must hold this scene and these paths."""
    # One rounding step of slack: platforms can differ in the last bit before rounding to 0.01.
    assert np.abs(d - np.array(data["field"])).max() <= 0.0051, "field differs from the plot data"
    drawn = [c["path_px"] for c in data["candidates"]]
    assert drawn == [[[float(x), float(y)] for x, y in candidate_coordinates_px(c)] for c in cands]


def caption(cands):
    return (f"Synthetic method demo: {len(cands)} delivered paths trace the curved and braided corridors and "
            "part of the broken one; the round blob is rejected. Panel (a): the known-truth synthetic "
            "disturbance field from make_scene(size=256, seed=1). Panel (b): the same field with each "
            "candidate's delivered path_px as a blue line. Grey level is the disturbance "
            f"(colour bar), {FIELD['vmin']} to {FIELD['vmax']} z units; values beyond the scale are clipped. "
            "One interior-biased path per accepted component (CR-09); no branch or junction recovery. "
            "Not a real-imagery result. The path geometry is pinned in results/extractor_stress_cases.json "
            "(cases.demo_reference.exported_paths_px). Source: analysis/catanroads/synthetic.py and "
            "analysis/catanroads/extract.py.")


def main():
    d, cands = scene()
    check(d, cands, json.loads(DATA.read_text()))
    OUT.with_suffix(".caption.md").write_text(caption(cands) + "\n")
    print(f"wrote {OUT.with_suffix('.caption.md')}  ({len(cands)} candidates)")


if __name__ == "__main__":
    main()
