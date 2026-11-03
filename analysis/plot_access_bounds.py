"""Write the caption, CSV tables, Markdown tables and provenance for the committed toy result.

Run: python analysis/plot_access_bounds.py
The MATLAB scripts in analysis/matlab draw bounds.png/pdf from bounds.csv and typeset the
bounds and qualification tables (see analysis/matlab/README.md). No study is run here.
The original evidence and its hashed generator remain unchanged.
"""
import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'evidence/access-stability-20261006'
OUT = ROOT / 'results/access-stability'
MATLAB = ROOT / 'analysis/matlab'
# Decision -> table label.
LABELS = {'definite_access': 'Definite access', 'definite_exclusion': 'Definite exclusion',
          'unresolved': 'Unresolved'}


def value(x):
    return '∞' if x == 'infinity' else str(x)


def interval(row):
    return f"[{value(row['lower'])}, {value(row['upper'])}]"


def _join(names):
    return ' and '.join(filter(None, [', '.join(names[:-1]), names[-1]]))


def _names(rows, label):
    """Nodes with a decision, excluding the destination itself ([0, 0])."""
    return [r['node'] for r in rows if r['classification'] == label and not r['lower'] == r['upper'] == 0]


def facts(report):
    """Validated statements shared by the figure and its caption."""
    original, widened = report['bounds']['original'], report['bounds']['widened']
    nodes = [r['node'] for r in original]
    assert nodes == [r['node'] for r in widened], nodes
    no_path = [r['node'] for r in original if r['lower'] == 'infinity']
    assert no_path == [r['node'] for r in widened if r['lower'] == 'infinity'], no_path
    assert all(r['classification'] == 'definite_exclusion' for r in original + widened if r['lower'] == 'infinity')
    unbounded = [r['node'] for r in original if r['lower'] != 'infinity' and r['upper'] == 'infinity']
    assert unbounded == [r['node'] for r in widened if r['lower'] != 'infinity' and r['upper'] == 'infinity'], unbounded
    changed = [a['node'] for a, b in zip(original, widened) if a['classification'] != b['classification']]
    assert all(b['classification'] == 'unresolved' for a, b in zip(original, widened)
               if a['classification'] != b['classification']), changed
    definite = [r['node'] for r in widened if r['classification'] != 'unresolved']
    assert no_path and unbounded and changed and definite
    return nodes, no_path, unbounded, changed, definite


def caption(report):
    thr = report['threshold']
    original = report['bounds']['original']
    nodes, no_path, unbounded, changed, definite = facts(report)
    return (
        'Deterministic shortest-time bounds on a toy graph, in minutes to the fixed destination '
        f'Clinic, for the {len(nodes)} nodes {_join(nodes)}. Panel (a): original assumptions. '
        'Panel (b): widened assumptions, same axes. Each horizontal line is one node\'s interval '
        'between its lower and upper travel time. Colour and fill give the decision, which is also '
        'written at the right of each row: a filled blue circle means definite access, a filled orange '
        'square means definite exclusion, and a hollow dark grey diamond means unresolved. The dotted '
        f'grey vertical line is the {thr}-minute access threshold; equality counts as access. No '
        f'finite upper time exists for {_join(unbounded)} in either panel; that line runs to the right '
        f'edge without an end marker. No path exists for {_join(no_path)} in either panel, so that row '
        'carries only the words no path; the decision is definite exclusion. '
        f"Original: access for {_join(_names(original, 'definite_access'))}, exclusion for "
        f"{_join(_names(original, 'definite_exclusion'))}, unresolved for "
        f"{_join(_names(original, 'unresolved'))}. Widened: unresolved now also for {_join(changed)}; "
        f'a definite decision remains only for {_join(definite)}. The bounds are deterministic '
        'assumptions, not confidence intervals; no geography or observed travel time is involved. '
        'Exact endpoints: README.md and bounds.csv beside this figure. '
        'Source: evidence/access-stability-20261006/result.json.'
    )


def write_tables(report, qualification, out):
    rows = [dict(scenario=scenario, node=r['node'], lower_min=r['lower'],
                 upper_min=r['upper'], threshold_min=report['threshold'],
                 classification=r['classification'])
            for scenario, items in report['bounds'].items() for r in items]
    inputs = qualification['development_baseline']['inputs']
    for name, data, fields in [
        ('bounds.csv', rows, list(rows[0])),
        ('qualification.csv', inputs, ['input', 'source', 'snapshot_in_script',
                                      'product_in_script', 'qualification']),
    ]:
        with (out / name).open('w', newline='') as stream:
            writer = csv.DictWriter(stream, fieldnames=fields, lineterminator='\n')
            writer.writeheader()
            writer.writerows(data)
    text = ['# Toy access bounds and source qualification', '',
            'Generated from [result.json](../../evidence/access-stability-20261006/result.json) and',
            '[qualification.json](../../evidence/access-stability-20261006/qualification.json).',
            'These remain the authoritative sources; do not edit these derived tables.', '',
            '## Deterministic toy bounds', '',
            f"Access threshold: {report['threshold']} min, with equality counted as access.",
            'Intervals are deterministic assumptions. Infinity denotes unreachable or unbounded',
            'travel time, not missing data. Clinic is the fixed destination. Integers retain',
            'the precision of the source. [Download bounds CSV](bounds.csv).', '',
            '![Bounds table: lower and upper travel time in minutes and the decision for each node, '
            'original and widened.](bounds_table.png)', '',
            '<details><summary>Table as text</summary>', '',
            '| Node | Original interval [min] | Original decision | Widened interval [min] | Widened decision |',
            '| :--- | ---: | :--- | ---: | :--- |']
    for a, b in zip(report['bounds']['original'], report['bounds']['widened']):
        assert a['node'] == b['node']
        text.append(f"| {a['node']} | {interval(a)} | {LABELS[a['classification']]} | "
                    f"{interval(b)} | {LABELS[b['classification']]} |")
    text += ['', '</details>', '', '## Development input qualification', '',
             f"Recorded baseline status: **{qualification['development_baseline']['status']}**.",
             'These are recorded metadata findings, not new availability probes.',
             '[Download qualification CSV](qualification.csv). Empty optional CSV fields mean',
             'the source record does not supply that field; they do not mean zero.', '',
             '![Qualification table: recorded source and qualification finding for each development '
             'input.](qualification_table.png)', '',
             '<details><summary>Table as text</summary>', '',
             '| Input | Recorded source | Qualification finding |',
             '| :--- | :--- | :--- |']
    for row in inputs:
        text.append(f"| {row['input'].capitalize()} | {row['source']} | {row['qualification']} |")
    text += ['', '</details>']
    reg = qualification['evaluation_registration']
    text += ['', '## Reserved WFP candidate', '',
             'Metadata only. No reserved outcome rows or previews were opened.', '',
             '| Item | Recorded finding |', '| :--- | :--- |']
    for title, key in [('Eligibility', 'status'), ('Vehicle scope', 'vehicle_class'),
                       ('Observation timing', 'observation_dates'), ('Coverage', 'coverage'),
                       ('Independence', 'lineage'), ('Outcome hash', 'outcome_hash_status')]:
        text.append(f"| {title} | {reg[key].replace('_', ' ') if key == 'status' else reg[key]} |")
    text += ['', 'The full source record retains the exclusion rules, licenses and source pins.',
             'The [roadmap](../../ROADMAP.md) governs qualification before evaluation.', '']
    (out / 'README.md').write_text('\n'.join(text))


def main():
    report = json.loads((SOURCE / 'result.json').read_text())
    qualification = json.loads((SOURCE / 'qualification.json').read_text())
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / 'bounds.caption.md').write_text(caption(report) + '\n')
    write_tables(report, qualification, OUT)
    files = [SOURCE / 'result.json', SOURCE / 'qualification.json', Path(__file__).resolve(),
             *(MATLAB / f for f in ('make_access_bounds.m', 'make_access_tables.m', 'fig_style.m',
                                    'export_pair.m'))]
    provenance = {'source_policy': 'Read existing records only; no model or evaluation run.',
                  'sha256': {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                             for p in files},
                  'reference': {'repository': '500ft/sensor-enclosure-thermal-design',
                                'commit': 'bad572fc0902437445a5446bb5bc43098cc6211f'},
                  'outputs': ['bounds.png', 'bounds.pdf', 'bounds.caption.md', 'bounds.csv',
                              'qualification.csv', 'bounds_table.tex', 'bounds_table.pdf',
                              'bounds_table.png', 'qualification_table.tex',
                              'qualification_table.pdf', 'qualification_table.png', 'README.md']}
    (OUT / 'provenance.json').write_text(json.dumps(provenance, indent=2) + '\n')


if __name__ == '__main__':
    main()
