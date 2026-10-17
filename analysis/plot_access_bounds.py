"""Render the committed toy result and qualification metadata without running a study.

Run: MPLBACKEND=Agg python analysis/plot_access_bounds.py
The original evidence and its hashed generator remain unchanged.
"""
import csv
import hashlib
import json
from pathlib import Path

from figstyle import FILL, INK, WIDTH_IN, apply, letter, save

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'evidence/access-stability-20261006'
OUT = ROOT / 'results/access-stability'
# Decision -> marker shape, line style, definite (filled) or not (hollow), table label.
STYLES = {
    'definite_access': ('o', '-', True, 'Definite access'),
    'definite_exclusion': ('s', (0, (5, 2.5)), True, 'Definite exclusion'),
    'unresolved': ('D', (0, (4, 1.5, 1, 1.5)), False, 'Unresolved'),
}
LINE = {'color': INK, 'lw': 1.2, 'ms': 4.5, 'mew': .9}
THRESHOLD = {'color': INK, 'lw': .8, 'ls': (0, (1, 1.5))}


def value(x):
    return '∞' if x == 'infinity' else str(x)


def interval(row):
    return f"[{value(row['lower'])}, {value(row['upper'])}]"


def _join(names):
    return ' and '.join(filter(None, [', '.join(names[:-1]), names[-1]]))


def _names(rows, label):
    """Nodes with a decision, excluding the destination itself ([0, 0])."""
    return [r['node'] for r in rows if r['classification'] == label and not r['lower'] == r['upper'] == 0]


def axis_limit(report):
    finite = [r[k] for rows in report['bounds'].values() for r in rows
              for k in ('lower', 'upper') if r[k] != 'infinity']
    return max(*finite, report['threshold']) * 1.15


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
        'between its lower and upper travel time. A filled circle with a solid line means definite '
        'access, a filled square with a dashed line means definite exclusion, and a hollow diamond '
        f'with a dash-dot line means unresolved. The dotted vertical line is the {thr}-minute access '
        f'threshold; equality counts as access. No finite upper time exists for {_join(unbounded)} '
        'in either panel; that line runs to the right edge without an end marker. No path exists for '
        f'{_join(no_path)} in either panel, so nothing is drawn on that row; the decision is definite '
        f"exclusion. Original: access for {_join(_names(original, 'definite_access'))}, exclusion for "
        f"{_join(_names(original, 'definite_exclusion'))}, unresolved for "
        f"{_join(_names(original, 'unresolved'))}. Widened: unresolved now also for {_join(changed)}; "
        f'a definite decision remains only for {_join(definite)}. The bounds are deterministic '
        'assumptions, not confidence intervals; no geography or observed travel time is involved. '
        'Exact endpoints: README.md and bounds.csv beside this figure. '
        'Source: evidence/access-stability-20261006/result.json.'
    )


def make_figure(report):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.legend_handler import HandlerLine2D
    from matplotlib.lines import Line2D
    from matplotlib.ticker import MultipleLocator

    class LeftMarker(HandlerLine2D):
        """Legend entry with a marker at the left end only, as an unbounded interval is drawn."""
        def create_artists(self, *args, **kwargs):
            artists = super().create_artists(*args, **kwargs)
            artists[0].set_markevery([0])
            return artists

    facts(report)
    apply()
    # Legend handles show a marker at each end, as the intervals do.
    plt.rcParams['legend.numpoints'] = 2
    thr, limit = report['threshold'], axis_limit(report)
    fig, axes = plt.subplots(1, 2, figsize=(WIDTH_IN, 3.1), sharex=True, sharey=True)
    fig.subplots_adjust(left=.075, right=.985, bottom=.165, top=.79, wspace=.10)
    for ax, (scenario, rows), tag in zip(axes, report['bounds'].items(), 'ab'):
        for i, row in enumerate(rows):
            lo, hi = row['lower'], row['upper']
            if lo == 'infinity':
                continue  # No path: nothing is drawn; the caption says so.
            y = len(rows) - 1 - i
            marker, ls, definite, _ = STYLES[row['classification']]
            end = limit if hi == 'infinity' else hi
            line, = ax.plot([lo, end], [y, y], marker=marker, ls=ls, mfc=FILL[definite],
                            markevery=[0] if hi == 'infinity' else None, zorder=3, **LINE)
            line.set_gid(f'{scenario}:{row["node"]}')
        ax.axvline(thr, zorder=1, **THRESHOLD)
        letter(ax, tag)
        ax.set_xlim(-limit * .03, limit)
        ax.set_ylim(-.5, len(rows) - .5)
        ax.set_yticks(range(len(rows)), [r['node'] for r in reversed(rows)])
        ax.tick_params(axis='y', length=0, pad=4)
        ax.tick_params(axis='x', length=3)
        ax.xaxis.set_major_locator(MultipleLocator(5))
        ax.xaxis.set_minor_locator(MultipleLocator(1))
        ax.set_xlabel('Shortest travel time to clinic [min]')
    handles = [Line2D([], [], marker=m, ls=ls, mfc=FILL[d], label=label, **LINE)
               for m, ls, d, label in STYLES.values()]
    unbounded = Line2D([], [], marker='D', ls=STYLES['unresolved'][1], mfc=FILL[False],
                       markevery=[0], label='No finite upper time', **LINE)
    handles += [unbounded, Line2D([], [], label='Access threshold', **THRESHOLD)]
    fig.legend(handles=handles, loc='upper center', bbox_to_anchor=(.5, .995), ncol=3,
               handlelength=2.6, columnspacing=1.4, handletextpad=.5, borderaxespad=0,
               handler_map={unbounded: LeftMarker()})
    return fig


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
            '| Node | Original interval [min] | Original decision | Widened interval [min] | Widened decision |',
            '| :--- | ---: | :--- | ---: | :--- |']
    for a, b in zip(report['bounds']['original'], report['bounds']['widened']):
        assert a['node'] == b['node']
        text.append(f"| {a['node']} | {interval(a)} | {STYLES[a['classification']][3]} | "
                    f"{interval(b)} | {STYLES[b['classification']][3]} |")
    text += ['', '## Development input qualification', '',
             f"Recorded baseline status: **{qualification['development_baseline']['status']}**.",
             'These are recorded metadata findings, not new availability probes.',
             '[Download qualification CSV](qualification.csv). Empty optional CSV fields mean',
             'the source record does not supply that field; they do not mean zero.', '',
             '| Input | Recorded source | Qualification finding |',
             '| :--- | :--- | :--- |']
    for row in inputs:
        text.append(f"| {row['input'].capitalize()} | {row['source']} | {row['qualification']} |")
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
    import matplotlib.pyplot as plt
    report = json.loads((SOURCE / 'result.json').read_text())
    qualification = json.loads((SOURCE / 'qualification.json').read_text())
    OUT.mkdir(parents=True, exist_ok=True)
    fig = make_figure(report)
    save(fig, OUT / 'bounds.png', svg=True)
    plt.close(fig)
    (OUT / 'bounds.caption.md').write_text(caption(report) + '\n')
    write_tables(report, qualification, OUT)
    files = [SOURCE / 'result.json', SOURCE / 'qualification.json', Path(__file__).resolve(),
             Path(__file__).resolve().with_name('figstyle.py')]
    provenance = {'source_policy': 'Read existing records only; no model or evaluation run.',
                  'sha256': {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                             for p in files},
                  'reference': {'repository': '500ft/sensor-enclosure-thermal-design',
                                'commit': 'bad572fc0902437445a5446bb5bc43098cc6211f'},
                  'outputs': ['bounds.png', 'bounds.svg', 'bounds.caption.md', 'bounds.csv',
                              'qualification.csv', 'README.md']}
    (OUT / 'provenance.json').write_text(json.dumps(provenance, indent=2) + '\n')


if __name__ == '__main__':
    main()
