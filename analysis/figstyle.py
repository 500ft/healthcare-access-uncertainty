"""Shared figure rules for the plotting scripts in this directory: a data-only canvas with the words in a caption.

Plots call ``apply()`` before drawing, ``save()`` to write every format and
``audit()`` to prove that nothing printed touches anything else. Only
presentation lives here; no plotted value is computed in this module.

- The canvas carries data, axes, tick labels, axis labels, panel letters and
  one framed legend. Titles, outcomes, scores and notes live in the
  ``<stem>.caption.md`` file written beside the image and in the docs under it.
- Condition (which decision, which geometry layer) is carried by marker shape
  and line style. State (definite or unresolved) is carried by marker fill.
  Colour is used only for a raster field, with a colourbar. Text is never
  coloured.
- Nothing printed may touch another printed thing or the data; ``audit``
  returns every pair that does, and ``save`` refuses a touching canvas.
- Type is Computer Modern (matplotlib's bundled ``cmr10``), the same family as
  the Latin Modern used by LaTeX-built figures.
"""
from pathlib import Path

import matplotlib as mpl
from matplotlib.text import Text
from matplotlib.transforms import Bbox

INK = 'black'
# Marker fill carries state: filled is definite, hollow is unresolved.
FILL = {True: INK, False: 'white'}
# Three type sizes by role: axis labels and legend, panel letters, tick labels.
LABEL_SIZE, LETTER_SIZE, TICK_SIZE = 9, 9, 7
WIDTH_IN = 7.2  # 183 mm, a double-column figure
DPI = 600


def apply():
    mpl.rcParams.update({
        'font.family': 'serif', 'font.serif': ['cmr10'], 'mathtext.fontset': 'cm',
        # cmr10 has no Unicode minus; mathtext tick labels carry a proper one.
        'axes.formatter.use_mathtext': True, 'axes.unicode_minus': False,
        'font.size': LABEL_SIZE, 'axes.labelsize': LABEL_SIZE, 'legend.fontsize': LABEL_SIZE,
        'xtick.labelsize': TICK_SIZE, 'ytick.labelsize': TICK_SIZE,
        'xtick.direction': 'out', 'ytick.direction': 'out',
        'axes.spines.top': False, 'axes.spines.right': False,
        'axes.linewidth': .8, 'axes.edgecolor': INK,
        'legend.frameon': True, 'legend.fancybox': False, 'legend.edgecolor': INK,
        'legend.framealpha': 1.0,
        'figure.facecolor': 'white', 'axes.facecolor': 'white',
        'savefig.dpi': DPI,
        # Editable SVG text and stable element ids, so reruns give the same bytes.
        'svg.fonttype': 'none', 'svg.hashsalt': 'healthcare-access-uncertainty',
    })


def letter(ax, tag):
    """Panel letter "(a)", top left and outside the axes."""
    ax.text(0, 1.04, f'({tag})', transform=ax.transAxes, ha='left', va='bottom', size=LETTER_SIZE)


def audit(fig):
    """Pairs of printed things whose boxes touch. Empty means the canvas is clean.

    Every drawn text (tick labels inside the view, axis labels, panel letters,
    legend entries) is checked against every other drawn text, against the
    lines drawn in each axes and against each legend frame. Data is not checked
    against data. Texts inside a legend are not checked against their own frame.
    """
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    legends = list(fig.legends) + [ax.get_legend() for ax in fig.axes if ax.get_legend()]
    owner = {id(child): legend for legend in legends for child in legend.findobj()}
    tick_labels, drawn = set(), []
    for ax in fig.axes:
        for axis in (ax.xaxis, ax.yaxis):
            low, high = sorted(axis.get_view_interval())
            slack = 1e-9 * (high - low)
            for tick in axis.get_major_ticks() + axis.get_minor_ticks():
                for label in (tick.label1, tick.label2):
                    tick_labels.add(id(label))
                    if label.get_visible() and label.get_text().strip() and low - slack <= tick.get_loc() <= high + slack:
                        drawn.append(label)
    drawn += [t for t in fig.findobj(Text)
              if id(t) not in tick_labels and t.get_visible() and t.get_text().strip()]
    texts = [(f'text {t.get_text()!r}', t.get_window_extent(renderer).padded(1), owner.get(id(t))) for t in drawn]
    # A clipped line is drawn only inside its axes, so only that part can touch anything.
    others = [(f"data in {ax.get_ylabel() or 'axes'}", box, None) for ax in fig.axes for line in ax.lines
              if (box := line.get_window_extent(renderer) if not line.get_clip_on()
                  else Bbox.intersection(line.get_window_extent(renderer), ax.bbox)) is not None]
    others += [('legend frame', legend.get_window_extent(renderer), legend) for legend in legends]
    hits = []
    for i, (name_a, box_a, legend_a) in enumerate(texts):
        for name_b, box_b, legend_b in texts[i + 1:] + others:
            if legend_a is not None and legend_a is legend_b:
                continue
            if box_a.overlaps(box_b):
                hits.append((name_a, name_b))
    return hits


def save(fig, png, svg=False):
    """Write the PNG at 600 dpi and, if asked, an SVG sibling without a date stamp.

    Refuses a canvas where printed items touch.
    """
    hits = audit(fig)
    if hits:
        raise ValueError(f'printed items touch: {hits}')
    png = Path(png)
    fig.savefig(png, dpi=DPI, metadata={'Software': None})
    if svg:
        out = png.with_suffix('.svg')
        fig.savefig(out, metadata={'Date': None})
        # Matplotlib emits trailing spaces in SVG path attributes; retain newlines.
        out.write_text('\n'.join(line.rstrip() for line in out.read_text().splitlines()) + '\n')
    return png
