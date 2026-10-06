# Roadmap

## Direction and current step

The owner adopted public-data-first route-planner feasibility as a separate
investigation. The [executed trip probe](evidence/route-feasibility-20261004/README.md)
records the sample, parsing result and data limitations. Acquisition and analysis
ran in an external local workspace. Detailed traces and source linkage remain
outside this repository; the committed record contains aggregate evidence and
the reproducible probe only.

The first evidence task is complete. Its source is UCI GPS Trajectories; the
[aggregate record](evidence/route-feasibility-20261004/summary.json) establishes
parsing feasibility only. No Mongolian or off-road validation was performed.
The detector remains paused and its artifacts are preserved.

The current step is the owner's direction decision. The documentation handoff
does not answer the outstanding choices: R1, whether to replace this repository's
finish line; R2, whether to close or keep the detector paused; R3, the commitment
and usable independent drive records; and R4, the relevant data terms. No such
approval is recorded here. The proposed replacement remains in the external
handoff until R1 is answered; this active roadmap has not adopted it.

The earlier `off-road-route-planning` proposal remains unapproved. No repository
creation or rename is authorized by this documentation task. The study described
below records that earlier proposal, rather than a new work authorization.

For that earlier proposed study, the finish line is candidate routes and travel-time
estimates compared with independent actual vehicle trips under known conditions,
with trips/corridors held out. Travel time on a driven route and passability of an
undriven suggested route are separate claims. Any next evidence task needs a new
authorization.

## Paused detector finish line

The next result is a baseline-coverage note comparing Microsoft RoadDetections,
OSM and their union against independently drawn, dated reference corridors.
Report per-site performance and the limits of the reference sample.

A temporal-change study is a later decision. It needs independently dated
absence before and presence after, plus a reason to add the detector beyond the
baselines. If those targets are absent, stop or obtain approval for a prospective
site redesign. Lack of eligible labels is inadequate evidence for that study,
not a measured resolution limit of Sentinel-2.

## Detector state

- The [baseline packet](baseline/20261003/README.md) contains clipped candidate
  layers, a dated OSM snapshot with an exact selection, input and output hashes,
  a common metric projection and prospective matching rules. The candidate
  archive remains unrendered.
- Dated reference metadata and tile delivery are reachable at the probed site
  centers. The [access record](baseline/20261003/reference-access.json) records
  acquisition dates separately from release dates. Whole-site suitability
  awaits owner inspection.
- No site has been verified and no baseline performance has been calculated.
  Owner labeling time remains an unapproved commitment.
- The existing extractor, tests and historical Earth Engine QA work are retained.
  The earlier gate is paused until the baseline decision; its configuration is
  unchanged. History is in [the progress log](docs/SPRINT_PROGRESS.md).

## Detector work remaining

| Step | Who | Done when |
|---|---|---|
| Baseline preparation | Agent | Prepared files and reproducible code are in the baseline packet; imagery access is recorded. Complete for the scoped preparation task. |
| Decide whether to spend time labeling | Owner | Explicit commitment or a decision to close. Required before resuming detector evaluation. |
| Draw references with candidate layers hidden | Owner | Dated centerlines, inspected extents, ambiguous regions and judgments are committed. Start with negative-01, then the development sites; inspect confound-01 separately if time permits. |
| Check baseline coverage | Agent | After labels are committed, reveal and compare Microsoft, OSM and their union under the packet's matching rules. Publish the baseline-coverage note. |
| Choose the endpoint | Owner | Close with the coverage note, or authorize a temporal-change study with eligible dated changes and unresolved baseline need. |
| If continuing, amend the detector study | Agent and owner | Projection and physical size thresholds change together; band-resolution handling and reference uncertainty are specified before evaluation. Tune on development sites, then run the untouched holdout once. The historical gate is not rerun before this decision. |

## Inspection rules

Use Google Earth historical imagery first, with Esri Wayback as fallback.
Only an owner judgment can verify a site. Unclear sites remain unverified.
A replacement needs an owner-identified problem and approval of an amendment
that keeps the old coordinates.

Keep baseline and detector overlays closed until the independent judgments are
committed. Prepare only the non-holdout sites; the holdout remains unopened.
The [packet](baseline/20261003/README.md) gives the blind entry point and links
to the existing worksheet.

## Scope

Preparation does not approve labeling time or reopen detector development.
Network conditioning, active-versus-abandoned classification and adaptive
site substitution after seeing results remain outside this task.
