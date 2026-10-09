"""Render the committed toy result and qualification metadata without running a study.

Run: MPLBACKEND=Agg python analysis/plot_access_bounds.py
The original evidence and its hashed generator remain unchanged.
"""
import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'evidence/access-stability-20261006'
OUT = ROOT / 'results/access-stability'
STYLES = {
    'definite_access': ('#2980b9', 'o', '-', 'Definite access'),
    'definite_exclusion': ('#c0392b', 's', '--', 'Definite exclusion'),
    'unresolved': ('#7d3c98', 'D', '-.', 'Unresolved'),
}


def value(x):
    return '∞' if x == 'infinity' else str(x)


def interval(row):
    return f"[{value(row['lower'])}, {value(row['upper'])}]"


def make_figure(report):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.lines import Line2D
    from matplotlib.ticker import MultipleLocator

    with plt.rc_context({'font.family': 'DejaVu Sans', 'font.size': 11,
                         'axes.labelsize': 11, 'axes.titlesize': 13,
                         'svg.fonttype': 'none', 'svg.hashsalt': 'access-bounds'}):
        fig, axes = plt.subplots(1, 2, figsize=(10, 6.6), sharex=True, sharey=True)
        fig.subplots_adjust(left=.08, right=.98, bottom=.21, top=.77, wspace=.22)
        finite = [r[k] for rows in report['bounds'].values() for r in rows
                  for k in ('lower', 'upper') if r[k] != 'infinity']
        limit = max(*finite, report['threshold']) * 1.18
        for ax, (scenario, rows), letter in zip(axes, report['bounds'].items(), 'ab'):
            for i, row in enumerate(rows):
                lo, hi = row['lower'], row['upper']
                y = len(rows) - 1 - i
                color, marker, style, _ = STYLES[row['classification']]
                if lo == 'infinity':
                    ax.text(.5, y, 'No path · definite exclusion',
                            transform=ax.get_yaxis_transform(), ha='center',
                            va='center', color=color, fontsize=10)
                    continue
                end = limit * .96 if hi == 'infinity' else hi
                line, = ax.plot([lo, end], [y, y], color=color, ls=style, lw=2.2,
                                marker=marker, ms=5, markevery=[0] if hi == 'infinity' else None)
                line.set_gid(f'{scenario}:{row["node"]}')
                if hi == 'infinity':
                    ax.annotate('', xy=(end, y), xytext=(end - limit * .06, y),
                                arrowprops=dict(arrowstyle='->', lw=2.2, color=color))
                ax.annotate(interval(row), (lo, y), xytext=(0, 9),
                            textcoords='offset points', fontsize=10, color='#222222',
                            bbox=dict(facecolor='white', edgecolor='none', pad=1))
            ax.axvline(report['threshold'], color='#444444', ls=(0, (4, 4)), lw=1.1,
                       zorder=0)
            ax.text(report['threshold'], 1.015, f"τ = {report['threshold']} min",
                    transform=ax.get_xaxis_transform(), ha='center', fontsize=10)
            ax.set_title(f"({letter}) {scenario.capitalize()} intervals", loc='left', pad=28)
            ax.set_xlim(-limit * .035, limit)
            ax.set_ylim(-.5, len(rows) - .35)
            ax.set_yticks(range(len(rows)), [r['node'] for r in reversed(rows)])
            ax.tick_params(axis='y', labelleft=True, length=0, pad=8)
            ax.xaxis.set_major_locator(MultipleLocator(5))
            ax.set_xlabel('Shortest travel time to clinic [min]', labelpad=9)
            ax.grid(axis='y', color='#e8e8e8', linewidth=.6)
            ax.set_axisbelow(True)
            ax.spines[['top', 'right']].set_visible(False)
            ax.spines[['left', 'bottom']].set_color('#888888')
        handles = [Line2D([0], [0], color=c, marker=m, ls=s, lw=2.2, ms=5, label=label)
                   for c, m, s, label in STYLES.values()]
        fig.legend(handles=handles, loc='upper center', bbox_to_anchor=(.53, .90),
                   ncol=3, frameon=False, fontsize=10, handlelength=2.7)
        fig.suptitle('Access decisions under wider assumptions', x=.08, ha='left',
                     y=.985, fontsize=16, fontweight='bold')
        fig.text(.08, .922, 'TOY GRAPH  ·  Deterministic bounds, not confidence intervals',
                 fontsize=11, color='#444444')
        fig.text(.08, .09, f"Access includes equality at {report['threshold']} min. Arrows denote unbounded upper time.",
                 fontsize=10)
        fig.text(.08, .05, 'E has no path; Clinic is the fixed destination. No real-area validation.',
                 fontsize=10, color='#444444')
        fig.text(.08, .012, 'Source: evidence/access-stability-20261006/result.json',
                 fontsize=9, color='#555555')
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
            '| Node | Original [min] | Decision | Widened [min] | Decision |',
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
    fig.savefig(OUT / 'bounds.png', dpi=180, facecolor='white')
    with plt.rc_context({'svg.fonttype': 'none', 'svg.hashsalt': 'access-bounds'}):
        fig.savefig(OUT / 'bounds.svg', facecolor='white', metadata={'Date': None})
    # Matplotlib emits trailing spaces in SVG path attributes; retain newlines.
    svg = OUT / 'bounds.svg'
    svg.write_text('\n'.join(line.rstrip() for line in svg.read_text().splitlines()) + '\n')
    plt.close(fig)
    write_tables(report, qualification, OUT)
    files = [SOURCE / 'result.json', SOURCE / 'qualification.json', Path(__file__).resolve()]
    provenance = {'source_policy': 'Read existing records only; no model or evaluation run.',
                  'sha256': {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                             for p in files},
                  'reference': {'repository': '500ft/sensor-enclosure-thermal-design',
                                'commit': 'bad572fc0902437445a5446bb5bc43098cc6211f'},
                  'outputs': ['bounds.png', 'bounds.svg', 'bounds.csv', 'qualification.csv', 'README.md']}
    (OUT / 'provenance.json').write_text(json.dumps(provenance, indent=2) + '\n')


if __name__ == '__main__':
    main()
