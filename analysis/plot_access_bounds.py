"""Render the committed toy result and qualification metadata without running a study.

Run: MPLBACKEND=Agg python analysis/plot_access_bounds.py
The original evidence and its hashed generator remain unchanged.
"""
import csv
import hashlib
import json
from pathlib import Path

from figstyle import BASE, COLORS, MUTED, SMALL, TICK, WIDTH_IN, apply, letter, save

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'evidence/access-stability-20261006'
OUT = ROOT / 'results/access-stability'
STYLES = {
    'definite_access': (COLORS['definite_access'], 'o', '-', 'Definite access'),
    'definite_exclusion': (COLORS['definite_exclusion'], 's', '--', 'Definite exclusion'),
    'unresolved': (COLORS['unresolved'], 'D', '-.', 'Unresolved'),
}


def value(x):
    return '∞' if x == 'infinity' else str(x)


def interval(row):
    return f"[{value(row['lower'])}, {value(row['upper'])}]"


def _names(rows, label):
    return ' and '.join(r['node'] for r in rows if r['classification'] == label
                        and not r['lower'] == r['upper'] == 0)


def make_figure(report):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.lines import Line2D
    from matplotlib.ticker import MultipleLocator

    apply()
    thr = report['threshold']
    original, widened = report['bounds']['original'], report['bounds']['widened']
    # Titles are built from the record so they stay true for every row.
    definite = [r['node'] for r in widened if r['classification'] != 'unresolved']
    changed = [a['node'] for a, b in zip(original, widened)
               if a['classification'] != b['classification']]
    titles = {'original': f"Original: {_names(original, 'definite_access')} has access; "
                          f"{_names(original, 'definite_exclusion')} are excluded",
              'widened': f"Widened: {' and '.join(changed)} become unresolved"}
    fig, axes = plt.subplots(1, 2, figsize=(WIDTH_IN, 4.3), sharex=True, sharey=True)
    fig.subplots_adjust(left=.075, right=.985, bottom=.19, top=.72, wspace=.08)
    finite = [r[k] for rows in report['bounds'].values() for r in rows
              for k in ('lower', 'upper') if r[k] != 'infinity']
    limit = max(*finite, thr) * 1.15
    for ax, (scenario, rows), tag in zip(axes, report['bounds'].items(), 'ab'):
        for i, row in enumerate(rows):
            lo, hi = row['lower'], row['upper']
            y = len(rows) - 1 - i
            color, marker, style, _ = STYLES[row['classification']]
            if lo == 'infinity':
                ax.text(thr + 1, y, 'No path (definite exclusion)', ha='left', va='center',
                        color=color, fontsize=SMALL)
                continue
            end = limit * .97 if hi == 'infinity' else hi
            line, = ax.plot([lo, end], [y, y], color=color, ls=style, lw=1.8, marker=marker,
                            ms=4.5, markevery=[0] if hi == 'infinity' else None, zorder=3)
            line.set_gid(f'{scenario}:{row["node"]}')
            if hi == 'infinity':
                ax.annotate('', xy=(end, y), xytext=(end - limit * .05, y), zorder=3,
                            arrowprops=dict(arrowstyle='->', lw=1.8, color=color))
        ax.axvline(thr, color='#4D4D4D', ls=(0, (3, 3)), lw=.9, zorder=1)
        if tag == 'a':
            ax.text(thr, len(rows) - .45, f' {thr}-min threshold', ha='left', va='bottom',
                    fontsize=SMALL, color='#4D4D4D')
        ax.set_title(titles[scenario], pad=6)
        letter(ax, tag)
        ax.set_xlim(-limit * .03, limit)
        ax.set_ylim(-.5, len(rows) - .1)
        ax.set_yticks(range(len(rows)), [r['node'] for r in reversed(rows)])
        ax.tick_params(axis='y', length=0, pad=4, labelsize=BASE)
        ax.xaxis.set_major_locator(MultipleLocator(5))
        ax.xaxis.set_minor_locator(MultipleLocator(1))
        ax.grid(axis='y', color='#ebebeb', linewidth=.6)
        ax.set_axisbelow(True)
        ax.spines['left'].set_visible(False)
    fig.supxlabel('Shortest travel time to clinic [min]', y=.085, fontsize=BASE)
    handles = [Line2D([0], [0], color=c, marker=m, ls=s, lw=1.8, ms=4.5, label=label)
               for c, m, s, label in STYLES.values()]
    handles.append(Line2D([0], [0], color='#4D4D4D', marker='>', ls='-', lw=1.2, ms=4.5,
                          markevery=[1], label='No finite upper time'))
    fig.legend(handles=handles, loc='upper left', bbox_to_anchor=(.065, .865), ncol=4,
               handlelength=2.6, columnspacing=1.4, borderaxespad=0)
    definite_text = ' and '.join(definite)
    fig.text(.075, .965, f'Widening the toy assumptions leaves only {definite_text} with a definite decision',
             fontsize=BASE, fontweight='bold', va='top')
    fig.text(.075, .915, 'TOY GRAPH  ·  Deterministic bounds, not confidence intervals',
             fontsize=SMALL, color=MUTED, va='top')
    fig.text(.075, .02, f"n = {len(original)} nodes per panel on one graph; Clinic is the fixed destination. "
             f"Equality at {thr} min counts as access.\nSource: evidence/access-stability-20261006/result.json. "
             "Exact endpoints are in results/access-stability/README.md.",
             fontsize=TICK, color=MUTED, linespacing=1.4)
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
    write_tables(report, qualification, OUT)
    files = [SOURCE / 'result.json', SOURCE / 'qualification.json', Path(__file__).resolve(),
             Path(__file__).resolve().with_name('figstyle.py')]
    provenance = {'source_policy': 'Read existing records only; no model or evaluation run.',
                  'sha256': {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                             for p in files},
                  'reference': {'repository': '500ft/sensor-enclosure-thermal-design',
                                'commit': 'bad572fc0902437445a5446bb5bc43098cc6211f'},
                  'outputs': ['bounds.png', 'bounds.svg', 'bounds.csv', 'qualification.csv', 'README.md']}
    (OUT / 'provenance.json').write_text(json.dumps(provenance, indent=2) + '\n')


if __name__ == '__main__':
    main()
