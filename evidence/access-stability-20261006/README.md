# Access-stability execution and source qualification

[The executed result](result.json) verifies deterministic shortest-time bounds
and widening behavior on toy graphs. [demo.json](demo.json) supplies the graph,
fixed facility, minute threshold and inverse-speed example. These are constructed
software inputs, with no geographic coordinates or measured travel times.

## Reproduce

From the repository root, after installing `analysis[dev]`:

```sh
MPLBACKEND=Agg PYTHONPATH=analysis python analysis/run_access_demo.py
PYTHONPATH=analysis python -m pytest analysis/tests/test_access_bounds.py -q
(cd evidence/access-stability-20261006 && shasum -a 256 -c metadata-freeze.sha256)
```

The generator writes [result.json](result.json) and [bounds.png](bounds.png).
The result links hashes of its input, implementation, generator and independent
oracle. The oracle enumerates its finite directed graph state space, allowed
edge-time values and closures, then compares simple-path extrema with Dijkstra
and checks a nested widening. The [method note](../../docs/ACCESS_STABILITY.md)
contains the general monotonic argument and numerical limits.

The figure was visually inspected after generation. It labels toy evidence,
minutes, the threshold, closure and disconnection; no map is implied.

[checks.json](checks.json) records the local commands, environment and actual
check outcomes, including the initial interpreter failure.

## Development baseline qualification

The [qualification record](qualification.json) pins the inspected
[Idai source revision](https://github.com/GIScience/healthcare-access-idai/tree/69bbe253b4dcd926a630b557251b5f65688301d5),
source hashes, input lineage, header-only availability probes and unqualified
terms. The pinned scripts fetch a moving road extract and do not contain the
historical payloads or their checksums. The WFP development flood archive returned
an access error in the recorded header probe. A reachable header for other inputs
does not establish downloaded, licensed, reproducible bytes. No baseline was run.

The inspected Idai license is GPL. Only source qualification was performed; no
Idai code is incorporated or redistributed. The graph module is original code
implementing the documented mathematical argument with Python's standard library.
Any future combined derived work must meet the applicable GPL requirements;
a separate folder is not a waiver. Data permissions remain separate.

## Reserved WFP candidate

The exact [HDX catalog response](wfp-metadata.json) contains metadata and schema,
with no feature rows or map preview. It identifies the Logistics Cluster partner
reports, OSM geometry lineage, stated ODbL license and observational/anecdotal
method. The catalog's generic `isopen` flag is false despite its named license;
no payload license qualification is inferred from that flag. Links, dates and
missing provider content hashes remain visible in the snapshot.

[metadata-freeze.sha256](metadata-freeze.sha256) freezes both the catalog bytes
and this task's machine-readable eligibility decision in [qualification.json](qualification.json).
Eligibility is currently empty. Row observation times, vehicle scope, status
semantics and partner lineage need independent metadata before any outcome access.
The development source uses the same event and OSM geometry and WFP flood input;
no automatic independence is claimed for partner road reports. Roads with no
report are unknown. No constraint payload was downloaded, hashed, opened or used
for tuning, and the old detector holdout was not inspected.

A future outcome-byte freeze and row-level registration remain blocked. The
[roadmap](../../ROADMAP.md) states what must be supplied before proceeding.
