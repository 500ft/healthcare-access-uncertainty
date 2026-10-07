"""Run toy bounds, exhaustive oracle, and plot. Run from any working directory."""
import hashlib
import json
from math import isinf
from pathlib import Path
import platform
import runpy

from catanroads.access_bounds import Edge, access_bounds, speed_to_minutes

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'evidence/access-stability-20261006'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    config = json.loads((OUT / 'demo.json').read_text())
    results = {}
    for name, key in [('original', 'edges'), ('widened', 'widened_edges')]:
        bounds = access_bounds(len(config['nodes']), [Edge(**e) for e in config[key]],
                               config['facilities'], config['threshold'])
        results[name] = [dict(node=node, lower=('infinity' if isinf(lo) else lo),
                              upper=('infinity' if isinf(hi) else hi), classification=label)
                         for node, (lo, hi, label) in zip(config['nodes'], bounds)]
    oracle = runpy.run_path(str(ROOT / 'analysis/tests/test_access_bounds.py'))
    report = dict(evidence_type=config['evidence_type'], units=config['units'],
                  config='demo.json', threshold=config['threshold'],
                  bounds=results, exhaustive=oracle['exhaustive_check'](),
                  speed_example_minutes=speed_to_minutes(**config['speed_example']),
                  python=platform.python_version(),
                  sha256={str(p.relative_to(ROOT)): digest(p) for p in (
                      OUT / 'demo.json', Path(__file__),
                      ROOT / 'analysis/catanroads/access_bounds.py',
                      ROOT / 'analysis/tests/test_access_bounds.py')})
    # Serialize infinity explicitly: JSON Infinity is not portable JSON.
    (OUT / 'result.json').write_text(json.dumps(report, indent=2, allow_nan=False) + '\n')
    plot(report)
    print(json.dumps(report['exhaustive']))


def plot(report):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    colors = {'definite_access': '#16744a', 'definite_exclusion': '#9a3c23',
              'unresolved': '#6858a5'}
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.8), sharey=True)
    finite = [r['upper'] for rows in report['bounds'].values() for r in rows
              if r['upper'] != 'infinity']
    limit = max(finite) * 1.35
    for ax, (name, rows) in zip(axes, report['bounds'].items()):
        for i, row in enumerate(rows):
            lo, hi, label = row['lower'], row['upper'], row['classification']
            y = len(rows) - 1 - i
            text = label.replace('definite_', '').replace('_', ' ')
            if lo == 'infinity':
                ax.text(limit * .52, y, 'unreachable | ' + text, va='center', fontsize=10)
            else:
                end = limit * .85 if hi == 'infinity' else hi
                ax.plot([lo, end], [y, y], color=colors[label], lw=4, solid_capstyle='round')
                ax.plot(lo, y, '|', color=colors[label], ms=12)
                if hi == 'infinity':
                    ax.plot(end, y, '>', color=colors[label], ms=9)
                ax.text(lo, y + .22, f"[{lo}, {'∞' if hi == 'infinity' else hi}] | {text}",
                        fontsize=10)
        ax.axvline(report['threshold'], color='#555555', ls='--', lw=1)
        ax.set_title(name.capitalize() + ' intervals')
        ax.set_xlabel('Shortest travel time to fixed clinic (minutes)')
        ax.set_xlim(-1, limit)
        ax.set_ylim(-.6, len(rows) - .3)
        ax.set_yticks(range(len(rows)), [r['node'] for r in reversed(rows)])
        ax.grid(axis='x', alpha=.15)
        ax.spines[['top', 'right']].set_visible(False)
    fig.suptitle(f"Toy verification only • threshold {report['threshold']} minutes", fontsize=15)
    fig.text(.5, .015, 'D may have a closed edge; E has no path. Synthetic inputs: demo.json. No real geography.',
             ha='center', fontsize=10)
    fig.tight_layout(rect=(0, .045, 1, .95))
    fig.savefig(OUT / 'bounds.png', dpi=160)
    plt.close(fig)


if __name__ == '__main__':
    main()
