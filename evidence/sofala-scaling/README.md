# Current Sofala software fixture

The [executed scaling record](scaling.json) passed exhaustive small-subgraph checks,
independent endpoint comparisons and nested widening on a current road-network
fixture. [The generated table](../../results/sofala-scaling.md) reports timing and
memory. This result does not complete historical M1 or qualify real travel bounds.

## Inputs and interpretation

[Source metadata](source.json) pins the dated Overpass query, retrieval time,
original response hash and compressed response hash. `sofala-osm.json.gz` restores
those exact response bytes offline. This modest fixture covers the declared
Beira-area bounding box within Sofala, not the whole province. No facility or
outcome records were requested. A timestamped query fixes the requested OSM state;
response service metadata can change on refetch, so use the retained bytes for
exact reproduction. The acquisition used one bounded request.

The [pre-execution protocol](protocol.json) is the source for selection, seed,
sizes, weights, threshold, oracle domain and stop rules. Every retained OSM node
is an origin. Fixed synthetic targets are chosen by OSM node ID and included in
all nested induced graphs. They are not verified healthcare facilities.

Ways become directed consecutive-node arcs, retaining parallel arcs and mapped
one-way direction. Both endpoints must be inside the box. Explicit private/no
access is excluded; unsupported or conditional one-way tags are excluded. No
largest-component filter or invented connector is used. Segment lengths use
WGS84 ellipsoidal geodesic meters. Synthetic positive times are independent of
length and are not road speeds. Turn restrictions and other conditional access
rules are unmodeled. Box clipping and OSM omissions can disconnect roads.

The uncertainty set is a Cartesian product of independent directed-arc intervals
and independent optional closures, with fixed available targets. Opposite arcs
can close independently. Always-closed arcs remain closed. Endpoint routing may
choose different paths at each extreme. Widening comparisons use the same graph
and targets; comparisons across graph sizes are scaling tests, not monotonicity
claims. The threshold is only a synthetic software parameter.

The small oracle enumerates every declared finite weight/closure world and all
simple paths in each retained sample, including its widened variant. It does not
enumerate the full road graph or every value in a continuous interval. Larger
checks use SciPy's directed shortest paths with explicit minimum aggregation of
parallel arcs. All nodes and both endpoints are compared, including infinity.
Finite-world counts and repeated timings are not independent empirical samples.

## Reproduce

Use the existing `analysis[dev,detector,baseline]` dependencies. From the repo root:

```sh
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
export VECLIB_MAXIMUM_THREADS=1 NUMEXPR_NUM_THREADS=1
PYTHONPATH=analysis python -m pytest analysis/tests/test_sofala_scaling.py -q
PYTHONPATH=analysis python analysis/run_sofala_scaling.py \
  evidence/sofala-scaling/sofala-osm.json.gz --output /tmp/sofala-scaling.json
python analysis/render_sofala_scaling.py
```

The runner performs the hand-computed check and small exhaustive oracle before
its smallest timing batch. It checkpoints after every size and stops expansion
on the registered resource checks. Peak RSS includes source parsing and earlier
sizes. Reproduction changes timings; graph and result hashes should match. The
renderer reads the committed record, leaving scientific outputs unchanged.
[Execution metadata](execution.json) records script hashes and resource use.

## Routing direction

The [direction record](direction.json) reruns the fixture's synthetic intervals
in both routing directions on the same graph, targets, seed and threshold. The
existing bounds measure time from each node to its nearest target along arc
direction. The variant applies the same intervals and closures to the reversed
arcs, which measures time from the nearest target outward, the direction the
pinned isochrone helper requests from facility coordinates. The record counts
the nodes whose decision class differs at the registered threshold, the same
count under the widened intervals, and the share of one-way arcs, at every
registered size. The to-target results reproduce the scaling record's result
hashes. Some decisions change, so routing direction stays an author input for
the comparison rule. The fixture cannot settle it nationally, and its synthetic
times carry no road meaning. Rerun with:

```sh
PYTHONPATH=analysis python analysis/run_sofala_direction.py \
  evidence/sofala-scaling/sofala-osm.json.gz --output /tmp/direction.json
```

## Actual upstream compatibility result

[The probe result](upstream.json) and [process log](upstream.log) record execution
of the pinned original Petricola helper and selected input-read expression in
an isolated R environment. The unmodified full driver stopped at its first
missing package. The standalone probe then reproduced these dependencies:

- The preparation script writes layer `health_facilities`; the vector driver
  reads layer `all`. A current-coordinate fixture using the preparation layer
  fails that unchanged input-read expression.
- The helper forwards projected coordinates without transforming them. The
  service boundary needs qualified longitude/latitude input.
- The helper hides the original missing-backend error and later reports that
  `raw_isochrones` does not exist. A deliberate backend-error adapter reproduces
  the same masking.
- A valid `sf` object with a `geom` column fails the helper's `geometry` selection.
  Empty source rows still trigger calls under the helper's loop. The permissive
  test adapter returns synthetic points for these calls, never real isochrones.

The service adapter records arguments and returns an explicitly synthetic point.
No ORS engine was running, and no population calculation, flood union, parallel
upstream driver or historical reproduction was executed. The test used actual
current OSM coordinates solely as synthetic computational targets. A successful
adapter call establishes only wrapper/schema behavior. No upstream fixes were
silently applied.

To repeat in a separate directory, use the
[pinned macOS ARM environment](upstream-environment-osx-arm64.txt), then:

```sh
git clone https://github.com/GIScience/healthcare-access-idai.git /tmp/petricola-source
git -C /tmp/petricola-source checkout --detach 69bbe253b4dcd926a630b557251b5f65688301d5
Rscript --vanilla tools/probe_petricola.R /tmp/petricola-source \
  evidence/sofala-scaling/synthetic-targets.csv /tmp/petricola-probe
```

Use a fresh output directory. Full execution remains dependent on the original
runtime, a qualified routing service and eligible inputs. Original historical
identity, flood rights/membership and owner estimand/tolerance remain unresolved.
Reserved WFP observations and detector holdouts remain closed.

## Rights

Contains © OpenStreetMap contributors data, available under
[ODbL 1.0](https://opendatacommons.org/licenses/odbl/1-0/) with
[OSM attribution](https://www.openstreetmap.org/copyright). The retained extract,
derived node table and any derived graph database remain under ODbL. The exact
source extract and transformation algorithm are provided here; retain these
notices and applicable share-alike terms when redistributing derivatives.

The external Petricola source is pinned and GPL-3.0; its data need separate
rights. The original compatibility harness is GPL-3.0-only, with the
[full license](../../tools/PETRICOLA_PROBE_LICENSE.md). The production interval
implementation remains independent MIT code. No upstream code is copied into
it. Program outputs require their own content-based license assessment and are
not assumed automatically GPL.
