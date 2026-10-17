"""Synthetic method demonstration: disturbance scene -> extracted candidate corridors.

This validates the extraction tooling on data with KNOWN ground truth. It is not a
Mongolia result — real extraction stays gated on the Phase-1 negative-control test.
The canvas carries only the field and the paths; the words are written to
``method_demo_synthetic.caption.md`` beside the image.

    python analysis/demo_synthetic.py
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from catanroads.extract import candidate_coordinates_px, extract_candidates
from catanroads.synthetic import make_scene
from figstyle import WIDTH_IN, apply, letter, save
from plot_stress_cases import FIELD, PATH, KEYS, colorbar, field

OUT = Path(__file__).resolve().parents[1] / "results" / "method_demo_synthetic.png"


def scene():
    d, _truth = make_scene(size=256, seed=1)
    return d, extract_candidates(d)


def figure(d, cands):
    apply()
    fig, axes = plt.subplots(1, 2, figsize=(WIDTH_IN, 3.45))
    fig.subplots_adjust(left=.02, right=.93, top=.84, bottom=.03, wspace=.06)
    field(axes[0], d)
    im = field(axes[1], d)
    for k, c in enumerate(cands):
        axes[1].plot(*zip(*candidate_coordinates_px(c)), gid=f"path:{k}", **PATH)
    colorbar(fig, im, list(axes), [d])
    for ax, tag in zip(axes, "ab"):
        letter(ax, tag)
    fig.legend(handles=[KEYS["path"]], loc="upper center", bbox_to_anchor=(.5, .995),
               handlelength=2.6, handletextpad=.5, borderaxespad=0)
    return fig


def caption(cands):
    return (f"Synthetic method demo: {len(cands)} delivered paths trace the curved and braided corridors and "
            "part of the broken one; the round blob is rejected. Panel (a): the known-truth synthetic "
            "disturbance field from make_scene(size=256, seed=1). Panel (b): the same field with each "
            "candidate's delivered path_px as a white line with a black edge. Grey level is the disturbance "
            f"(colourbar), {FIELD['vmin']} to {FIELD['vmax']} z units; values beyond the scale are clipped. "
            "One interior-biased path per accepted component (CR-09); no branch or junction recovery. "
            "Not a real-imagery result. The path geometry is pinned in results/extractor_stress_cases.json "
            "(cases.demo_reference.exported_paths_px). Source: analysis/catanroads/synthetic.py and "
            "analysis/catanroads/extract.py.")


def main():
    d, cands = scene()
    fig = figure(d, cands)
    save(fig, OUT)
    OUT.with_suffix(".caption.md").write_text(caption(cands) + "\n")
    plt.close(fig)
    print(f"wrote {OUT}  ({len(cands)} candidates)")


if __name__ == "__main__":
    main()
