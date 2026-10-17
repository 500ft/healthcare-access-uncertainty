"""The bounds figure shows only the stored record, and its words live in the caption."""
import csv
import json
from pathlib import Path

import matplotlib.pyplot as plt
import pytest
from matplotlib.text import Text

import figstyle
import plot_access_bounds as plot

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / 'evidence/access-stability-20261006'
OUT = ROOT / 'results/access-stability'


@pytest.fixture(scope='module')
def built():
    report = json.loads((SOURCE / 'result.json').read_text())
    fig = plot.make_figure(report)
    yield report, fig
    plt.close(fig)


def test_marks_carry_stored_bounds_and_decisions(built):
    report, fig = built
    for ax, (scenario, rows) in zip(fig.axes, report['bounds'].items()):
        lines = {line.get_gid(): line for line in ax.lines if line.get_gid()}
        for row in rows:
            key = f'{scenario}:{row["node"]}'
            if row['lower'] == 'infinity':
                assert key not in lines  # No path is never drawn at a finite time.
                continue
            line = lines[key]
            marker, ls, definite, _ = plot.STYLES[row['classification']]
            assert line.get_marker() == marker
            assert line.get_markerfacecolor() == figstyle.FILL[definite]
            x = line.get_xdata()
            assert x[0] == row['lower']
            if row['upper'] == 'infinity':
                assert x[1] == ax.get_xlim()[1] and line.get_markevery() == [0]
            else:
                assert x[1] == row['upper']
        assert any(list(line.get_xdata()) == [report['threshold']] * 2
                   for line in ax.lines if line.get_gid() is None)


def test_canvas_holds_only_axes_text_panel_letters_and_legend(built):
    _, fig = built
    printed = {t.get_text() for t in fig.findobj(Text) if t.get_visible() and t.get_text().strip()}
    allowed = {'(a)', '(b)'} | {ax.get_xlabel() for ax in fig.axes}
    allowed |= {t.get_text() for legend in fig.legends for t in legend.get_texts()}
    allowed |= {t.get_text() for ax in fig.axes for t in ax.get_xticklabels() + ax.get_yticklabels()}
    assert printed <= allowed, printed - allowed


def test_nothing_printed_touches_anything(built):
    _, fig = built
    assert figstyle.audit(fig) == []


def test_caption_matches_file_and_docs(built):
    report, _ = built
    text = plot.caption(report)
    assert text == (OUT / 'bounds.caption.md').read_text().strip()
    assert '10-minute access threshold' in text and 'unresolved now also for A and B' in text
    squash = lambda s: ' '.join(s.split())
    for doc in ('README.md', 'results/README.md'):
        assert squash(text) in squash((ROOT / doc).read_text()), doc


def test_tables_preserve_record(tmp_path):
    report = json.loads((SOURCE / 'result.json').read_text())
    qualification = json.loads((SOURCE / 'qualification.json').read_text())
    plot.write_tables(report, qualification, tmp_path)
    with (tmp_path / 'bounds.csv').open() as stream:
        exported = list(csv.DictReader(stream))
    expected = [dict(scenario=s, node=r['node'], lower_min=str(r['lower']),
                     upper_min=str(r['upper']), threshold_min=str(report['threshold']),
                     classification=r['classification'])
                for s, rows in report['bounds'].items() for r in rows]
    assert exported == expected
    with (tmp_path / 'qualification.csv').open() as stream:
        exported = list(csv.DictReader(stream))
    for got, row in zip(exported, qualification['development_baseline']['inputs'], strict=True):
        assert all(got[k] == str(v) for k, v in row.items())
