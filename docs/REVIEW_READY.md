# Review index

What to review, and where each piece of evidence lives. The plan is in the
[roadmap](../ROADMAP.md) and the history in the [progress log](SPRINT_PROGRESS.md).
The earlier, longer version of this index is kept at
[commit 033c951](https://github.com/500ft/informal-road-mapping/blob/033c9513db32b670cd56ae229f1afe4c390e0f9a/docs/REVIEW_READY.md).

Nothing here has had an independent review. No site is verified and the
Phase-1 gate has not run.

## Review now

1. **The first Earth Engine run**
   ([runtime record](../results/earth_engine_runtime_2026-09-29.json)). The
   grid probe's fixes, the measured 6.79 m pixel at 47.3°N, and the QA exports.
   Recheck the captured geometry offline with `python tools/check_grid_runtime.py`.
2. **The frozen gate** ([design](design.md#pre-registered-phase-1-gate-frozen-2026-08-23))
   against the grid-scale amendment. Worth checking: whether the 50-pixel
   component minimum, about 2,300 m² of ground rather than 5,000 m², still
   makes sense for corridor-scale roads.
3. **The missingness enumeration**
   ([record](../evidence/task-2026-09-25/missingness_sensitivity.json)).
   Dropping years that aren't missing at random can flip the gate either way.
   These are enumerated cases, not a probability model of cloud cover.

## Reproduce

Run the [README checks](../README.md#getting-started). None of them contacts
Earth Engine. Running Earth Engine itself needs the signed-in Code Editor and
the [Phase-1 runbook](PHASE1_RUNBOOK.md).

## Evidence records

| Folder | What it holds |
| --- | --- |
| [task-2026-09-25](../evidence/task-2026-09-25/README.md) | Closeout: missingness enumeration, compositor contract, grid probe and its expectations |
| [task-2026-09-19](../evidence/task-2026-09-19/README.md) | Week of 2026-09-19: intake, stack review and the first-site packet |
| [task-2026-09-14](../evidence/task-2026-09-14/README.md) | Path export built to the feasibility checkpoint |
| [task-2026-09-12](../evidence/task-2026-09-12/README.md) | Extractor stress test beyond the favourable demo |
| [correction-2026-09-11](../evidence/correction-2026-09-11/README.md) | Correction of what earlier work had and had not finished |
| [presentation-2026-09-10](../evidence/presentation-2026-09-10/README.md) | README presentation checks |
| [review-2026-09-09](../evidence/review-2026-09-09/README.md) | Review of the first two days' work |
| [task-2026-09-09](../evidence/task-2026-09-09/README.md) | Export-path rehearsal |
| [task-day3-2026-09-09](../evidence/task-day3-2026-09-09/README.md) | Site worksheet preparation |
| [task-2026-09-08](../evidence/task-2026-09-08/README.md) | Temporal evidence QA |
| [sprint-2026-09-05](../evidence/sprint-2026-09-05/) | First integrity sprint baseline |

Results live in [results/](../results/README.md): the stress-case records,
the gallery and the Earth Engine runtime record.
