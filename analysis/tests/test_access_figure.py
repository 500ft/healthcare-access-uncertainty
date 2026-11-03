"""The bounds figure and tables are drawn by MATLAB from bounds.csv; their words live in the caption.

Pixels are not compared. The checks cover what MATLAB reads (the CSV export), the table fragments
it wrote against the record, the caption against its file and the docs, and the generated README.
"""
import csv
import json
import re
from pathlib import Path

import plot_access_bounds as plot

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / 'evidence/access-stability-20261006'
OUT = ROOT / 'results/access-stability'
REPORT = json.loads((SOURCE / 'result.json').read_text())
QUALIFICATION = json.loads((SOURCE / 'qualification.json').read_text())


def test_caption_matches_file_and_docs():
    text = plot.caption(REPORT)
    assert text == (OUT / 'bounds.caption.md').read_text().strip()
    assert '10-minute access threshold' in text and 'unresolved now also for A and B' in text
    squash = lambda s: ' '.join(s.split())
    for doc in ('README.md', 'results/README.md'):
        assert squash(text) in squash((ROOT / doc).read_text()), doc


def test_tables_preserve_record(tmp_path):
    plot.write_tables(REPORT, QUALIFICATION, tmp_path)
    with (tmp_path / 'bounds.csv').open() as stream:
        exported = list(csv.DictReader(stream))
    expected = [dict(scenario=s, node=r['node'], lower_min=str(r['lower']),
                     upper_min=str(r['upper']), threshold_min=str(REPORT['threshold']),
                     classification=r['classification'])
                for s, rows in REPORT['bounds'].items() for r in rows]
    assert exported == expected
    with (tmp_path / 'qualification.csv').open() as stream:
        exported = list(csv.DictReader(stream))
    for got, row in zip(exported, QUALIFICATION['development_baseline']['inputs'], strict=True):
        assert all(got[k] == str(v) for k, v in row.items())
    for name in ('bounds.csv', 'qualification.csv', 'README.md'):
        assert (tmp_path / name).read_bytes() == (OUT / name).read_bytes(), name


def test_typeset_bounds_table_holds_every_value():
    word = {'definite_access': 'definite access', 'definite_exclusion': 'definite exclusion',
            'unresolved': 'unresolved'}
    cell = lambda v: '{$\\infty$}' if v == 'infinity' else str(v)
    body = [line.strip() for line in (OUT / 'bounds_table.tex').read_text().splitlines()
            if re.match(r'^\S+ & ', line) and not line.startswith('Node &')]
    original, widened = REPORT['bounds']['original'], REPORT['bounds']['widened']
    assert len(body) == len(original)
    for line, a, b in zip(body, original, widened, strict=True):
        cells = [c.strip() for c in line.rstrip('\\').split(' & ')]
        assert cells[0] == a['node'] == b['node']
        assert cells[1:3] == [cell(a['lower']), cell(a['upper'])]
        assert cells[4:6] == [cell(b['lower']), cell(b['upper'])]
        assert word[a['classification']] in cells[3] and word[b['classification']] in cells[6]
    assert f"\\qty{{{REPORT['threshold']}}}{{\\minute}}" in (OUT / 'bounds_table.tex').read_text()


def test_typeset_qualification_table_holds_every_finding():
    tex = (OUT / 'qualification_table.tex').read_text().replace('\\_', '_')
    for row in QUALIFICATION['development_baseline']['inputs']:
        assert row['input'].capitalize() in tex and row['source'] in tex and row['qualification'] in tex


def test_rendered_outputs_are_committed():
    for stem in ('bounds', 'bounds_table', 'qualification_table'):
        for ext in ('.png', '.pdf'):
            assert (OUT / f'{stem}{ext}').stat().st_size > 5_000, stem + ext
