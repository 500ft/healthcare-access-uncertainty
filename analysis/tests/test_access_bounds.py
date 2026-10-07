"""Independent finite-world verification, including every directed 3-node graph."""
from itertools import permutations, product
from math import inf

import pytest

from catanroads.access_bounds import Edge, access_bounds, speed_to_minutes

# Absent, zero, exact, interval, optional, permanently closed. The interval
# includes an interior value so the oracle is not just the production endpoints.
STATES = (None, (0, 0, False), (1, 1, False), (0, 2, False),
          (1, 2, True), (inf, inf, False))
ARCS = tuple(permutations(range(3), 2))


def exhaustive_check():
    graphs = worlds = classifications = widenings = 0
    for choices in product(STATES, repeat=len(ARCS)):
        edges = [Edge(a, b, *state) for (a, b), state in zip(ARCS, choices)
                 if state is not None]
        domains = [((inf,) if s is None else
                    tuple(range(int(s[0]), int(s[1]) + 1)) + ((inf,) if s[2] else ()))
                   if s is None or s[0] != inf else (inf,) for s in choices]
        minimum = [[inf] * 3 for _ in range(3)]
        maximum = [[0] * 3 for _ in range(3)]
        for weights in product(*domains):
            # Independent simple-path enumeration. On three nodes, a shortest
            # nonnegative path is direct or visits the remaining node once.
            w = dict(zip(ARCS, weights))
            for a, b in ARCS:
                c = 3 - a - b
                distance = min(w[a, b], w[a, c] + w[c, b])
                minimum[a][b] = min(minimum[a][b], distance)
                maximum[a][b] = max(maximum[a][b], distance)
            worlds += 1
        widened = [Edge(e.start, e.end, 0, inf, True) for e in edges]
        for target in range(3):
            minimum[target][target] = maximum[target][target] = 0
            for threshold in (0, 1, 2, 4):
                result = access_bounds(3, edges, [target], threshold)
                wide = access_bounds(3, widened, [target], threshold)
                for source, ((lo, hi, label), (wl, wu, wc)) in enumerate(zip(result, wide)):
                    assert (lo, hi) == (minimum[source][target], maximum[source][target])
                    expected = ('definite_access' if maximum[source][target] <= threshold
                                else 'definite_exclusion' if minimum[source][target] > threshold
                                else 'unresolved')
                    assert label == expected
                    assert wl <= lo and wu >= hi
                    assert wc == 'unresolved' or wc == label
                    classifications += 1
                    widenings += 1
        graphs += 1
    return dict(graphs=graphs, worlds=worlds, classifications=classifications,
                widening_checks=widenings, failures=0)


def test_exhaustive_graphs():
    result = exhaustive_check()
    assert result['graphs'] == len(STATES) ** len(ARCS)


def test_multifacility_parallel_directed_and_speed():
    assert speed_to_minutes(10, 20, 60) == (10, 30)
    assert speed_to_minutes(0, 1, 2) == (0, 0)
    edges = [Edge(0, 1, 1, 2, True), Edge(0, 2, 3, 4), Edge(0, 2, 8, 9),
             Edge(2, 1, 0, 0), Edge(1, 1, 0, 0)]
    assert access_bounds(3, edges, [1, 2], 4) == [
        (1, 4, 'definite_access'), (0, 0, 'definite_access'), (0, 0, 'definite_access')]
    assert access_bounds(3, edges, [0], 4)[1:] == [(inf, inf, 'definite_exclusion')] * 2
    assert access_bounds(3, edges, [], 4) == [(inf, inf, 'definite_exclusion')] * 3
    assert access_bounds(3, edges, [1], 2)[0] == (1, 4, 'unresolved')
    for distance, slow, fast in product((0, 1, 7), (1, 2, 5), (5, 10)):
        low, high = speed_to_minutes(distance, slow, fast)
        assert low * fast / 60 == pytest.approx(distance)
        assert high * slow / 60 == pytest.approx(distance)


@pytest.mark.parametrize('args', [(1, 0, 1), (-1, 1, 2), (1, 3, 2),
                                  (inf, 1, 2), (1, 1, float('nan'))])
def test_invalid_speed(args):
    with pytest.raises(ValueError):
        speed_to_minutes(*args)


@pytest.mark.parametrize('edge', [Edge(0, 1, -1, 2), Edge(0, 1, 2, 1),
    Edge(0, 1, float('nan'), 2), Edge(0, 1, 0, float('nan')),
    Edge(0, 1, 0, 2, 1), Edge(0, 3, 0, 1), Edge(-1, 0, 0, 1)])
def test_invalid_edge(edge):
    with pytest.raises(ValueError):
        access_bounds(3, [edge], [2], 1)


@pytest.mark.parametrize('n,facilities,threshold', [(0, [], 1), (3, [3], 1),
    (3, [-1], 1), (3, [True], 1), (3, [1], -1), (3, [1], inf), (3, [1], float('nan'))])
def test_invalid_graph(n, facilities, threshold):
    with pytest.raises(ValueError):
        access_bounds(n, [], facilities, threshold)


def test_overflow_rejected():
    with pytest.raises(ValueError):
        speed_to_minutes(1e308, 1, 2)
    with pytest.raises(ValueError):
        access_bounds(3, [Edge(0, 1, 1e308, 1e308), Edge(1, 2, 1e308, 1e308)], [2], 1)
