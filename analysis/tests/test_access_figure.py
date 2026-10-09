"""Check the rendered marks and downloadable tables against the existing record."""
import csv
import json
from pathlib import Path

import matplotlib.pyplot as plt

from plot_access_bounds import make_figure, write_tables

SOURCE = Path(__file__).resolve().parents[2] / 'evidence/access-stability-20261006'


def test_marks_and_tables_preserve_record(tmp_path):
    report = json.loads((SOURCE / 'result.json').read_text())
    qualification = json.loads((SOURCE / 'qualification.json').read_text())
    fig = make_figure(report)
    try:
        for ax, (scenario, rows) in zip(fig.axes, report['bounds'].items()):
            lines = {line.get_gid(): line for line in ax.lines if line.get_gid()}
            for row in rows:
                key = f'{scenario}:{row["node"]}'
                if row['lower'] == 'infinity':
                    assert key not in lines  # Disconnected is never plotted at a finite time.
                    assert any('No path' in t.get_text() for t in ax.texts)
                else:
                    x = lines[key].get_xdata()
                    assert x[0] == row['lower']
                    if row['upper'] != 'infinity':
                        assert x[1] == row['upper']
                    else:
                        assert any(t.arrow_patch is not None for t in ax.texts
                                   if hasattr(t, 'arrow_patch'))
            assert any(list(line.get_xdata()) == [report['threshold']] * 2
                       for line in ax.lines if line.get_gid() is None)
        write_tables(report, qualification, tmp_path)
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
    finally:
        plt.close(fig)
