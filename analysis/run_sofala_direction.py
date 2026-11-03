"""Routing-direction sensitivity on the Sofala fixture: bounds to the targets versus from them."""
import argparse
from collections import Counter
from dataclasses import replace
import gzip
import json
import math
from pathlib import Path
import platform
import sys
import time

from catanroads.access_bounds import Edge, access_bounds
from run_sofala_scaling import RECORD, bfs_order, digest, graph_from_osm, synthetic_edges, widen, write_json

CLASSES = ('definite_access', 'definite_exclusion', 'unresolved')


def reverse_arcs(edges):
    """Same intervals and closures on the opposite arcs: times from the targets outward."""
    return [replace(e, start=e.end, end=e.start) for e in edges]


def compare(n, edges, targets, threshold):
    to_target = access_bounds(n, edges, targets, threshold)
    from_target = access_bounds(n, reverse_arcs(edges), targets, threshold)
    matrix = Counter((a[2], b[2]) for a, b in zip(to_target, from_target))
    summary = {
        'decision_changes': sum(v for (a, b), v in matrix.items() if a != b),
        'changes_to_target->from_target': {f'{a}->{b}': matrix[a, b] for a in CLASSES for b in CLASSES
                                           if a != b and matrix[a, b]},
        'decisions_to_target': {c: sum(r[2] == c for r in to_target) for c in CLASSES},
        'decisions_from_target': {c: sum(r[2] == c for r in from_target) for c in CLASSES},
        'nodes_with_any_endpoint_difference': sum(a[:2] != b[:2] for a, b in zip(to_target, from_target)),
        'to_target_unreachable_lower_upper': [sum(math.isinf(r[i]) for r in to_target) for i in (0, 1)],
        'from_target_unreachable_lower_upper': [sum(math.isinf(r[i]) for r in from_target) for i in (0, 1)],
    }
    return summary, to_target


def one_way(arcs):
    """Arcs without the opposite arc of the same way segment; two-way ways contribute both."""
    keys = {(a, b, way, seg) for a, b, _, way, seg in arcs}
    single = [(a, b, way, seg) for a, b, _, way, seg in arcs if (b, a, way, seg) not in keys]
    return {'one_way_arcs': len(single), 'one_way_arc_share': len(single) / len(arcs),
            'ways_with_one_way_arcs': len({w for _, _, w, _ in single}), 'ways': len({a[3] for a in arcs})}


def self_check():
    # Hand case: one-way arc 0->1 reaches target 1 but target 1 cannot reach 0; 2 is two-way.
    edges = [Edge(0, 1, 2, 3), Edge(2, 1, 1, 2), Edge(1, 2, 1, 2)]
    summary, to_target = compare(3, edges, [1], 4)
    assert [r[2] for r in to_target] == ['definite_access', 'definite_access', 'definite_access']
    assert summary['decision_changes'] == 1
    assert summary['changes_to_target->from_target'] == {'definite_access->definite_exclusion': 1}
    assert summary['decisions_from_target'] == {'definite_access': 2, 'definite_exclusion': 1, 'unresolved': 0}
    assert summary['nodes_with_any_endpoint_difference'] == 1
    assert summary['from_target_unreachable_lower_upper'] == [1, 1]
    share = one_way([(0, 1, 1.0, 7, 0), (2, 1, 1.0, 8, 0), (1, 2, 1.0, 8, 0)])
    assert share == {'one_way_arcs': 1, 'one_way_arc_share': 1 / 3, 'ways_with_one_way_arcs': 1, 'ways': 2}
    return summary


def run(raw, output):
    started = time.perf_counter()
    protocol = json.loads((RECORD / 'protocol.json').read_text())
    source = json.loads((RECORD / 'source.json').read_text())
    scaling = json.loads((RECORD / 'scaling.json').read_text())
    assert digest(raw) == source['response_sha256'], 'OSM source hash mismatch'
    check = self_check()
    ids, arcs, _, _ = graph_from_osm(json.loads(raw), protocol)
    graph_sha256 = digest(json.dumps(arcs, separators=(',', ':')).encode())
    assert graph_sha256 == scaling['graph_sha256'], 'graph differs from the scaling record'
    targets = [ids[len(ids) * q // 4] for q in (1, 2, 3)]
    assert targets == scaling['fixed_synthetic_target_osm_ids']
    order, _ = bfs_order(ids, arcs, targets[0])
    order = targets + [v for v in order if v not in targets]
    base = synthetic_edges(arcs, protocol['seed'])
    expanded = widen(base)
    recorded = {s['nodes']: s['result_sha256'] for s in scaling['sizes']}
    rows = []
    for requested in protocol['sizes_nodes']:
        n = len(ids) if requested == 'all' else min(requested, len(ids))
        if rows and n == rows[-1]['nodes']:
            continue
        index = {v: i for i, v in enumerate(order[:n])}
        keep = [i for i, e in enumerate(base) if e.start in index and e.end in index]
        remap = lambda pool: [replace(pool[i], start=index[pool[i].start], end=index[pool[i].end]) for i in keep]
        target_indices = [index[t] for t in targets]
        registered, to_target = compare(n, remap(base), target_indices, protocol['threshold_minutes'])
        widened, _ = compare(n, remap(expanded), target_indices, protocol['threshold_minutes'])
        encoded = json.dumps([[None if math.isinf(v) else v for v in r[:2]] + [r[2]] for r in to_target],
                             separators=(',', ':')).encode()
        rows.append({'nodes': n, 'arcs': len(keep), **one_way([arcs[i] for i in keep]),
                     'to_target_result_sha256': digest(encoded),
                     'matches_scaling_record': recorded.get(n) == digest(encoded),
                     'registered_intervals': registered, 'widened_intervals': widened})
    result = {
        'status': 'executed',
        'purpose': 'Direction sensitivity of synthetic interval decisions on the current Beira-area fixture. Synthetic times and targets only; no historical replication, no national road input, no clinical threshold.',
        'direction': {
            'to_target': 'Existing access_bounds: reverse multi-source Dijkstra, shortest time from each node to its nearest target along arc direction (resident travels to the facility).',
            'from_target': 'Same intervals and closures on the reversed arcs: shortest time from the nearest target to each node (outward isochrone, as the pinned isochrone helper requests from facility coordinates).',
            'comparison': 'Decision classes at the registered threshold are compared node by node on the same graph, targets, seed and interval set.',
        },
        'protocol_sha256': digest((RECORD / 'protocol.json').read_bytes()),
        'source_sha256': digest(raw), 'graph_sha256': graph_sha256, 'seed': protocol['seed'],
        'threshold_minutes': protocol['threshold_minutes'],
        'fixed_synthetic_target_osm_ids': targets,
        'self_check': check, 'sizes': rows,
        'command': 'PYTHONPATH=analysis python analysis/run_sofala_direction.py evidence/sofala-scaling/sofala-osm.json.gz --output evidence/sofala-scaling/direction.json',
        'environment': {'python': sys.version, 'platform': platform.platform()},
        'elapsed_seconds': time.perf_counter() - started,
    }
    write_json(output, result)
    for row in rows:
        print(json.dumps({k: row[k] for k in ('nodes', 'arcs', 'one_way_arc_share', 'matches_scaling_record')}
                         | {'registered_changes': row['registered_intervals']['decision_changes'],
                            'widened_changes': row['widened_intervals']['decision_changes']}))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input', type=Path)
    parser.add_argument('--output', type=Path, default=RECORD / 'direction.json')
    args = parser.parse_args()
    raw = gzip.decompress(args.input.read_bytes()) if args.input.suffix == '.gz' else args.input.read_bytes()
    run(raw, args.output)
