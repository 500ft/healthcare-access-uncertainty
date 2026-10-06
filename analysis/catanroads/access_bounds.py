"""Deterministic shortest-time bounds on a fixed directed graph; minutes throughout.

Original implementation of the interval argument in docs/ACCESS_STABILITY.md.
No upstream Idai code is incorporated. An optional edge may be absent; an
[inf, inf] edge is always closed. No probability coverage is asserted.
"""
from dataclasses import dataclass
from heapq import heappop, heappush
from math import inf, isfinite, isnan


@dataclass(frozen=True)
class Edge:
    start: int
    end: int
    lower: float
    upper: float
    optional: bool = False


def speed_to_minutes(distance_km, minimum_kph, maximum_kph):
    """Invert positive speed endpoints, returning (minimum, maximum) minutes."""
    if not all(isfinite(x) for x in (distance_km, minimum_kph, maximum_kph)):
        raise ValueError("distance and speeds must be finite")
    if distance_km < 0 or not 0 < minimum_kph <= maximum_kph:
        raise ValueError("require distance >= 0 and 0 < minimum speed <= maximum")
    times = (distance_km / maximum_kph * 60, distance_km / minimum_kph * 60)
    if not all(isfinite(x) for x in times):
        raise ValueError("travel time overflow")
    return times


def access_bounds(node_count, edges, facilities, threshold):
    """Return (L, U, class) at every node, allowing zero weights and parallel arcs.

    Facilities are fixed, available graph nodes. Access means time <= threshold.
    The interval box permits all endpoint/closure combinations jointly. For a
    correlated subset these bounds remain conservative, but can be loose.
    """
    if type(node_count) is not int or node_count < 1:
        raise ValueError("node_count must be a positive integer")
    if not isfinite(threshold) or threshold < 0:
        raise ValueError("threshold must be finite and nonnegative")
    edges, facilities = tuple(edges), set(facilities)
    valid_node = lambda x: type(x) is int and 0 <= x < node_count
    if not all(valid_node(x) for x in facilities):
        raise ValueError("facility node out of range")
    reverse = [[] for _ in range(node_count)]
    for e in edges:
        if not valid_node(e.start) or not valid_node(e.end):
            raise ValueError("edge node out of range")
        if isnan(e.lower) or isnan(e.upper) or not 0 <= e.lower <= e.upper:
            raise ValueError("require 0 <= lower <= upper, with no NaN")
        if type(e.optional) is not bool:
            raise ValueError("optional must be a boolean")
        reverse[e.end].append(e)

    def shortest(upper):
        distances = [inf] * node_count
        queue = []
        for node in facilities:
            distances[node] = 0
            heappush(queue, (0, node))
        while queue:
            time, node = heappop(queue)
            if time != distances[node]:
                continue
            for e in reverse[node]:
                weight = (inf if e.optional else e.upper) if upper else e.lower
                if weight == inf:
                    continue
                candidate = time + weight
                if not isfinite(candidate):
                    raise ValueError("path time overflow")
                if candidate < distances[e.start]:
                    distances[e.start] = candidate
                    heappush(queue, (candidate, e.start))
        return distances

    return [(lo, hi, "definite_access" if hi <= threshold else
             "definite_exclusion" if lo > threshold else "unresolved")
            for lo, hi in zip(shortest(False), shortest(True))]
