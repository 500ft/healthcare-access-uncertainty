"""Shared figure settings for the plotting scripts in this directory.

Three font sizes by role, outward ticks, frameless legends, one colour per
entity in every figure, 300-dpi PNG and SVG output without a date stamp.
"""
from pathlib import Path

import matplotlib as mpl

BASE, SMALL, TICK = 9, 8, 7  # titles and axis labels; legend and notes; ticks and footers
WIDTH_IN = 7.2  # 183 mm, a double-column figure
INK, MUTED = '#1a1a1a', '#595959'
# Okabe-Ito hues. Each entity keeps its colour in every figure.
COLORS = {
    'definite_access': '#0072B2',
    'definite_exclusion': '#D55E00',
    'unresolved': '#CC79A7',
    'path': '#E69F00',       # delivered path (path_px)
    'chord': '#4D4D4D',      # legacy chord (endpoints_px)
    'reference': '#56B4E9',  # reference centerline
}


def apply():
    mpl.rcParams.update({
        'font.family': 'DejaVu Sans', 'font.size': BASE, 'text.color': INK,
        'axes.titlesize': BASE, 'axes.labelsize': BASE, 'axes.titlelocation': 'left',
        'axes.labelcolor': INK, 'axes.edgecolor': '#808080', 'axes.linewidth': .8,
        'axes.spines.top': False, 'axes.spines.right': False,
        'figure.titlesize': BASE, 'legend.fontsize': SMALL, 'legend.frameon': False,
        'xtick.labelsize': TICK, 'ytick.labelsize': TICK,
        'xtick.direction': 'out', 'ytick.direction': 'out',
        'xtick.color': '#808080', 'ytick.color': '#808080',
        'xtick.labelcolor': INK, 'ytick.labelcolor': INK,
        'savefig.dpi': 300, 'savefig.facecolor': 'white',
        'svg.fonttype': 'none', 'svg.hashsalt': 'healthcare-access-uncertainty',
    })


def letter(ax, text):
    """Bold panel letter, top left and outside the axes."""
    ax.text(-0.02, 1.02, text, transform=ax.transAxes, ha='right', va='bottom',
            fontsize=BASE + 1, fontweight='bold')


def save(fig, png, svg=False):
    """Write the PNG at 300 dpi and, if asked, an SVG sibling without a date stamp."""
    png = Path(png)
    fig.savefig(png, metadata={'Software': None})
    if svg:
        out = png.with_suffix('.svg')
        fig.savefig(out, metadata={'Date': None})
        # Matplotlib emits trailing spaces in SVG path attributes; retain newlines.
        out.write_text('\n'.join(line.rstrip() for line in out.read_text().splitlines()) + '\n')
    return png
