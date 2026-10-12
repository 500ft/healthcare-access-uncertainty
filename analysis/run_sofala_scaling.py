"""Current OSM topology with synthetic weights. No historical/clinical inference."""
import argparse
from collections import Counter, deque
from dataclasses import replace
import gzip
import hashlib
from itertools import product
import json
import math
from pathlib import Path
import platform
import random
import resource
import statistics
import sys
import time

import numpy as np
from pyproj import Geod
import scipy
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import connected_components, dijkstra

from catanroads.access_bounds import Edge, access_bounds

ROOT = Path(__file__).resolve().parents[1]
RECORD = ROOT / 'evidence/sofala-scaling'


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2, allow_nan=False) + '\n')


def graph_from_osm(data, protocol):
    south, west, north, east = protocol['bbox_south_west_north_east']
    nodes = {e['id']: (e['lon'], e['lat']) for e in data['elements']
             if e['type'] == 'node' and south <= e['lat'] <= north
             and west <= e['lon'] <= east}
    geod = Geod(ellps='WGS84')
    arcs, skipped = [], Counter()
    for way in sorted((e for e in data['elements'] if e['type'] == 'way'), key=lambda e: e['id']):
        tags = way.get('tags', {})
        if tags.get('highway') not in protocol['highways']:
            skipped['highway'] += 1
            continue
        if any(tags.get(k) in ('no', 'private') for k in ('access', 'motor_vehicle')):
            skipped['access'] += 1
            continue
        one = tags.get('oneway', '').lower()
        if 'oneway:conditional' in tags or one not in ('', 'yes', '1', 'true', '-1', 'no', '0', 'false'):
            skipped['unsupported_oneway'] += 1
            continue
        forward = one in ('yes', '1', 'true') or (not one and (
            tags.get('highway') == 'motorway' or tags.get('junction') == 'roundabout'))
        for segment, (a, b) in enumerate(zip(way['nodes'], way['nodes'][1:])):
            if a not in nodes or b not in nodes:
                skipped['bbox_segments'] += 1
                continue
            if a == b:
                skipped['self_segments'] += 1
                continue
            length = geod.inv(*nodes[a], *nodes[b])[2]
            assert math.isfinite(length) and length >= 0
            directions = [(b, a)] if one == '-1' else ([(a, b)] if forward else [(a, b), (b, a)])
            for start, end in directions:
                arcs.append((start, end, length, way['id'], segment))
    ids = sorted({v for a in arcs for v in a[:2]})
    return ids, arcs, nodes, dict(skipped)


def synthetic_edges(arcs, seed):
    rng = random.Random(seed)
    edges = []
    for i, (a, b, *_) in enumerate(arcs):
        lo = rng.randint(1, 9)
        hi = lo + rng.randint(1, 9)
        edges.append(Edge(a, b, math.inf if i % 101 == 0 else lo,
                          math.inf if i % 101 == 0 else hi, i % 17 == 0))
    return edges


def widen(edges):
    return [replace(e, lower=e.lower / 2, upper=e.upper * 2,
                    optional=e.optional or i % 13 == 0)
            if math.isfinite(e.lower) else e for i, e in enumerate(edges)]


def sparse_endpoints(n, edges, targets, upper):
    # Explicit minimum, since sparse duplicate entries would otherwise be summed.
    weights = {}
    for e in edges:
        w = (math.inf if e.optional else e.upper) if upper else e.lower
        if math.isfinite(w):
            pair = (e.end, e.start)
            weights[pair] = min(weights.get(pair, math.inf), w)
    for t in targets:
        weights[n, t] = 0.0
    rows, cols = zip(*weights)
    graph = csr_matrix((list(weights.values()), (rows, cols)), shape=(n+1, n+1))
    return dijkstra(graph, directed=True, indices=n)[:n]


def simple_paths(n, edges, weights, targets):
    adjacent = [[] for _ in range(n)]
    for e, w in zip(edges, weights):
        if math.isfinite(w):
            adjacent[e.start].append((e.end, w))
    def visit(node, seen):
        if node in targets:
            return 0.0
        return min((w + visit(end, seen | {end}) for end, w in adjacent[node]
                    if end not in seen), default=math.inf)
    return [visit(node, {node}) for node in range(n)]


def exhaustive(n, edges, targets, threshold):
    domains = [(math.inf,) if not math.isfinite(e.lower) else
               (e.lower, (e.lower+e.upper)/2, e.upper) + ((math.inf,) if e.optional else ())
               for e in edges]
    count = math.prod(map(len, domains))
    assert count <= 4096
    low, high = [math.inf]*n, [0.0]*n
    for weights in product(*domains):
        distances = simple_paths(n, edges, weights, targets)
        low = list(map(min, low, distances))
        high = list(map(max, high, distances))
    result = access_bounds(n, edges, targets, threshold)
    for a, b in zip(result, zip(low, high)):
        assert a[:2] == b, (a, b)
    return count


def self_check():
    # Independent hand-calculated direction, closure, unreachable, parallel case.
    edges = [Edge(0, 1, 1, 2, True), Edge(0, 2, 3, 4), Edge(2, 1, 2, 3),
             Edge(0, 2, 7, 9)]
    expected = [(1, 7, 'unresolved'), (0, 0, 'definite_access'),
                (2, 3, 'definite_access'), (math.inf, math.inf, 'definite_exclusion')]
    assert access_bounds(4, edges, [1], 4) == expected
    assert access_bounds(4, edges, [0], 4)[1][0] == math.inf
    for upper in (False, True):
        assert list(sparse_endpoints(4, edges, [1], upper)) == [r[int(upper)] for r in expected]
    return exhaustive(4, edges, [1], 4)


def bfs_order(ids, arcs, first):
    adjacent = {v: set() for v in ids}
    for a, b, *_ in arcs:
        adjacent[a].add(b)
        adjacent[b].add(a)
    seen, order = set(), []
    for root in [first] + ids:
        if root in seen:
            continue
        queue = deque([root]); seen.add(root)
        while queue:
            node = queue.popleft(); order.append(node)
            for neighbor in sorted(adjacent[node] - seen):
                seen.add(neighbor); queue.append(neighbor)
    return order, adjacent


def run(raw, output):
    started = time.perf_counter()
    protocol = json.loads((RECORD/'protocol.json').read_text())
    source = json.loads((RECORD/'source.json').read_text())
    assert digest(raw) == source['response_sha256'], 'OSM source hash mismatch'
    self_worlds = self_check()
    ids, arcs, positions, skipped = graph_from_osm(json.loads(raw), protocol)
    assert len(ids) >= 128
    targets = [ids[len(ids)*q//4] for q in (1, 2, 3)]
    order, adjacent = bfs_order(ids, arcs, targets[0])
    order = targets + [v for v in order if v not in targets]
    base = synthetic_edges(arcs, protocol['seed'])
    expanded = widen(base)
    result = {'status':'running', 'purpose':protocol['purpose'], 'protocol_sha256':digest((RECORD/'protocol.json').read_bytes()),
              'source_sha256':digest(raw), 'seed':protocol['seed'],
              'environment':{'python':sys.version, 'scipy':scipy.__version__, 'numpy':np.__version__, 'platform':platform.platform()},
              'fixed_synthetic_target_osm_ids':targets, 'skipped':skipped,
              'self_check_worlds':self_worlds, 'small_oracle':[], 'sizes':[],
              'rss_scope':'Process high-water RSS including imports, full source/graph, oracle and preceding sizes; macOS bytes converted to MiB.',
              'length_m':{'min':min(a[2] for a in arcs),'max':max(a[2] for a in arcs)},
              'graph_sha256':digest(json.dumps(arcs,separators=(',',':')).encode())}
    rng = random.Random(protocol['seed'])
    for start in rng.sample(ids, 8):
        sample, queue = [start], deque([start])
        while queue and len(sample) < 4:
            for v in sorted(adjacent[queue.popleft()]):
                if v not in sample and len(sample) < 4:
                    sample.append(v); queue.append(v)
        index = {v:i for i,v in enumerate(sample)}
        subset = [e for e in base if e.start in index and e.end in index][:6]
        subset = [replace(e,start=index[e.start],end=index[e.end]) for e in subset]
        try:
            worlds = exhaustive(len(sample), subset, [len(sample)-1], protocol['threshold_minutes'])
            wide_worlds = exhaustive(len(sample), widen(subset), [len(sample)-1], protocol['threshold_minutes'])
        except AssertionError:
            write_json(output.with_suffix('.failure.json'), {'nodes':sample,'edges':[str(e) for e in subset]})
            raise
        result['small_oracle'].append({'osm_nodes':sample,'arcs':len(subset),'worlds':worlds,'widened_worlds':wide_worlds,'failures':0})
    write_json(output,result)
    for requested in protocol['sizes_nodes']:
        n = len(ids) if requested == 'all' else min(requested,len(ids))
        if result['sizes'] and n == result['sizes'][-1]['nodes']:
            continue
        index = {v:i for i,v in enumerate(order[:n])}
        keep = [i for i,e in enumerate(base) if e.start in index and e.end in index]
        edges = [replace(base[i],start=index[base[i].start],end=index[base[i].end]) for i in keep]
        wider = [replace(expanded[i],start=index[expanded[i].start],end=index[expanded[i].end]) for i in keep]
        target_indices = [index[t] for t in targets]
        timings = []
        for _ in range(protocol['repetitions']):
            tick = time.perf_counter()
            narrow = access_bounds(n,edges,target_indices,protocol['threshold_minutes'])
            wide = access_bounds(n,wider,target_indices,protocol['threshold_minutes'])
            timings.append(time.perf_counter()-tick)
        errors=[]
        for candidate, table in ((edges,narrow),(wider,wide)):
            for upper in (False, True):
                reference=sparse_endpoints(n,candidate,target_indices,upper)
                actual=np.array([row[int(upper)] for row in table])
                assert np.array_equal(np.isinf(reference),np.isinf(actual))
                finite=np.isfinite(reference)
                np.testing.assert_allclose(actual[finite],reference[finite],rtol=1e-12,atol=1e-10)
                errors.append(float(np.max(np.abs(actual[finite]-reference[finite]),initial=0)))
        for old,new in zip(narrow,wide):
            assert new[0] <= old[0] and new[1] >= old[1]
            assert new[2] == 'unresolved' or new[2] == old[2]
        graph=csr_matrix(([1]*len(edges),([e.start for e in edges],[e.end for e in edges])),shape=(n,n))
        rss=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/(1024**2 if sys.platform=='darwin' else 1024)
        encoded=json.dumps([[None if math.isinf(v) else v for v in row[:2]]+[row[2]] for row in narrow],separators=(',',':')).encode()
        row={'nodes':n,'arcs':len(edges),'weak_components':int(connected_components(graph,directed=True,connection='weak',return_labels=False)),
             'strong_components':int(connected_components(graph,directed=True,connection='strong',return_labels=False)),
             'lower_unreachable':sum(math.isinf(r[0]) for r in narrow),'upper_unreachable':sum(math.isinf(r[1]) for r in narrow),
             'narrow_and_wide_seconds':timings,'median_seconds':statistics.median(timings),'min_seconds':min(timings),'max_seconds':max(timings),
             'peak_process_rss_mib':rss,'endpoint_max_abs_error_minutes':max(errors),'widening_failures':0,'endpoint_values_checked':4*n,
             'result_sha256':digest(encoded)}
        result['sizes'].append(row); result['elapsed_seconds']=time.perf_counter()-started
        write_json(output,result); print(json.dumps(row),flush=True)
        if rss>1536 or result['elapsed_seconds']>14400 or (requested==128 and statistics.median(timings)*len(ids)/128*30>14400):
            result['status']='resource_stop';write_json(output,result);return
    result['status']='executed';result['elapsed_seconds']=time.perf_counter()-started
    write_json(output,result)
    # Only actual OSM coordinates of the fixed synthetic targets, not facilities.
    (output.parent/'synthetic-targets.csv').write_text('osm_id,longitude_deg,latitude_deg\n'+''.join(f'{t},{positions[t][0]},{positions[t][1]}\n' for t in targets))


if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input',type=Path)
    parser.add_argument('--output',type=Path,default=RECORD/'scaling.json')
    args=parser.parse_args()
    raw=gzip.decompress(args.input.read_bytes()) if args.input.suffix=='.gz' else args.input.read_bytes()
    run(raw,args.output)
