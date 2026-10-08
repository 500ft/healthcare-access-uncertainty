# Healthcare-access decision stability

## Owner decision

On 2026-10-06 the owner authorized Codex implementation of the reviewed v2
software pivot in this repository. ROAD-1 adopts the question in the
[README](../README.md); ROAD-2 makes the detector inactive with evidence retained.
ROAD-3 is satisfied for this implementation by original graph code with no
incorporated Idai source. No physical readiness, spending, fieldwork or new
repository decision is inferred. The [roadmap](../ROADMAP.md) holds the remaining
work.

PR [#52](https://github.com/500ft/informal-road-mapping/pull/52) was reviewed at
`14f3e8d37f399fec08868ea1ce331fe52de84f95`. Its scope corrections are retained.
The initial implementation incorporated those scope corrections in
[#53](https://github.com/500ft/informal-road-mapping/pull/53). Both PRs are merged;
the cleanup starts from that merged state.

| Previous active question | Disposition |
| --- | --- |
| R1 replacement finish line | Adopted for this software question only. |
| R2 detector disposition | Inactive and superseded; no scientific disproof. |
| R3 independent off-road drives and owner commitment | Superseded as an active task by healthcare access. No drive records or commitment supplied. |
| R4 former route-study data terms | Superseded as an active question; unresolved historical terms remain in the UCI record. Each new access input still requires qualification. |
| Separate route-planning repository/name | Superseded within this task; none created or renamed. |
| Temporal detector gate and baseline labeling | Inactive. Evidence and blind restrictions remain in the [history index](history/README.md). |

## Dependency plan and cleanup adoption

The owner authorized the dependency-based [roadmap](../ROADMAP.md) and removal
of obsolete detector execution and reporting surfaces. This does not qualify
real data or authorize research runs. The [history index](history/README.md)
records removals and necessary retained reproduction dependencies. Reserved
outcomes and detector holdouts remain closed. Physical work, funding, naming
and publication decisions remain unprovided.

## Model and argument

Use a fixed directed graph with nonnegative edge-time intervals in minutes and
fixed available facility nodes. Bidirectional roads need both arcs. An optional
edge can close; it is present at its lower time in the optimistic graph and
absent in the pessimistic graph. A permanently closed edge has infinite time
at both endpoints, or is omitted. No reachable facility gives infinite distance.

Compute shortest times L using all lower endpoints and U using all upper
endpoints. For any admissible configuration, every path gets no shorter than
its optimistic length, and the pessimistic shortest path bounds the actual
shortest path above. Thus L <= actual shortest time <= U. For the independent
interval box these endpoints are attainable. With correlated restrictions they
can be conservative. This is a deterministic argument, not probabilistic coverage.

For finite nonnegative threshold tau, U <= tau means definite access; L > tau
means definite exclusion; all other cases remain unresolved. Equality at tau
counts as access. Widening intervals or allowing additional closures cannot
increase L or decrease U, so it cannot turn an unresolved decision into a definite
one. This requires nested sets on the same graph and facility set. Adding a
facility or previously omitted connection changes the model.

For distance d in km and positive speeds v_min <= v_max in km/h, the minute
interval is [60d/v_max, 60d/v_min]. Zero minimum speed must be modeled as closure
or unbounded time, rather than silently divided by zero. The current module
rejects invalid speeds, negative/NaN times, invalid nodes and numerical overflow.

The [implementation](../analysis/catanroads/access_bounds.py) uses reverse
multi-source Dijkstra. The [independent oracle](../analysis/tests/test_access_bounds.py)
enumerates all directed graphs in its declared finite state space and all allowed
integer edge values and closures, then enumerates simple paths. Its graph size,
state definitions and thresholds are executable test inputs; counts and outcomes
live in the [result](../evidence/access-stability-20261006/result.json).
Continuous nonnegative intervals are covered by the monotonic argument above,
not exhaustive sampling of real numbers. Multi-facility, parallel-arc, direction,
zero-time, invalid-input and speed inversion cases have separate checks.
The executed integer-time example is exactly representable. Arbitrary floating
inputs use ordinary machine arithmetic; decisions within rounding error of the
threshold require numerical error bounds before use as real-arithmetic certificates.

## Limits and open evidence questions

These toy bounds do not qualify a real-area uncertainty family. Real healthcare
access also depends on graph completeness, transport mode, correlated conditions
and whether a facility actually provides the required service. Marginal interval
coverage cannot establish joint route or population coverage.

The [source qualification](../evidence/access-stability-20261006/qualification.json)
records the development reproduction blockers and WFP candidate ineligibility.
No outcome rows were fetched or inspected, no observation policy was evaluated,
and no synthetic agreement is reported as observed accuracy. Metadata hashes
freeze this qualification decision; they do not freeze unavailable outcome bytes.

There is no manuscript in the tracked repository. The current README and this
method note state the supported claims; prior detector claims and figures are
retained under the labeled [history area](history/README.md).
