# Data and figures

## Current figure

[Access bounds](../evidence/access-stability-20261006/bounds.png) plots the executed
[toy result](../evidence/access-stability-20261006/result.json). Both panels use the
fixed graph/facility specification in [demo.json](../evidence/access-stability-20261006/demo.json),
with original and nested wider intervals. Horizontal units are minutes. The
vertical dashed line is the demonstration threshold; labels state the decision
without relying on color. An arrow denotes an unbounded upper time; unreachable
means no possible path. Clinic is a fixed destination, not a settlement observation.

Run `MPLBACKEND=Agg PYTHONPATH=analysis python analysis/run_access_demo.py` from the
root after installing the README dependencies. The result records input and code
hashes. The intervals are fabricated test inputs; no observed access accuracy or
real geography is represented. The [method](ACCESS_STABILITY.md) defines the bounds.

## Retained historical figures

The detector's [figure manifest](figure-manifest.json),
[results narrative](history/detector-results.md) and
[historical overview](history/detector-overview.md) retain the generators,
limitations and provenance of its synthetic plots, placeholder NDVI rendering
and conceptual illustrations. Those figures are absent from the current narrative.
No Earth Engine or candidate imagery was rendered in this task.

The [history index](history/README.md) also retains the UCI parsing evidence and
blind baseline entry point. The [Idai qualification](../evidence/access-stability-20261006/qualification.json)
and [metadata snapshot](../evidence/access-stability-20261006/wfp-metadata.json)
contain no reserved outcome rows or map previews.
