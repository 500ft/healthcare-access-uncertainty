# Retained history: inactive detector and trip feasibility

The [owner decision](../ACCESS_STABILITY.md#owner-decision) supersedes the detector
and former route-study work queues. Their scientific outcomes are not disproved
by that decision. [ROADMAP.md](../../ROADMAP.md) is the only active plan.

## Reproducible evidence retained

- [Synthetic extractor source and commands](../../analysis/README.md),
  [result narrative](detector-results.md), [figure provenance](../figure-manifest.json)
  and [scientific corrections](detector-limitations.md).
- [Frozen detector inputs](../../history/detector/README.md): Earth Engine
  source relocated byte-for-byte; the manifest stays at its pinned preparation path.
- [Baseline packet blind entry point](../../baseline/20261003/README.md).
  Candidate layers and holdouts remain closed; owner labeling is unapproved.
- [Design and frozen contract](../design.md), [runbook](../PHASE1_RUNBOOK.md),
  [worksheet](../SITE_VERIFICATION_WORKSHEET.md) and
  [completion correction](../COMPLETION_RECONCILIATION.md).
- [Executed records](../../evidence/), [historical results](../../results/),
  [progress log](../SPRINT_PROGRESS.md) and [ledger](../SPRINT_TASKS.csv).
- [Detector literature](../../literature/) and [retained contracts](../specs/README.md).
- [UCI trip probe](../../evidence/route-feasibility-20261004/README.md):
  non-Mongolian parsing evidence, with no field or off-road validation.

Numerical source, synthetic fixtures, checks and generators remain because they
reproduce retained results. The gate and worksheet modules remain for documented
synthetic rehearsals and packet consistency, not as a current execution queue.
The baseline preparation script and `config/sites.geojson` stay at their original
paths because the packet pins the script hash and it resolves that manifest path.
Changing either would break that provenance check; neither is active study config.
Local regression checks are still run in CI. No Earth Engine run is authorized.

## Removed obsolete surfaces

The unused export-figure compositor, placeholder NDVI image, conceptual detector
images, former roadmap, review queue, blank evaluation template and superseded
correction/topology proposals were removed. They have no current execution
consumer or measured result requiring them. The topology correction was retained
separately; the frozen compositor comparison and path-routing contract remain
because executed tests refer to them.

The detector is no longer imported through the package root. Historical callers
use explicit module imports and the optional `detector` dependencies. The unused
future `full` dependency bundle and retired CI branch trigger were removed.

The [pre-cleanup tree](https://github.com/500ft/informal-road-mapping/tree/f6d485d5434d7797d1b42855ea3f524e64eed37e)
retains original paths, exact historical commands, discarded proposals and the
original figure manifest. Old records that quote those paths describe that
revision. Current reproduction commands resolve the relocated inputs; original
source hashes and results have not been rewritten to conceal path changes.
