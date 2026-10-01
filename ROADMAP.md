# Roadmap

This is the plan for finishing the project. The method and its frozen rules
are in [docs/design.md](docs/design.md); task status is in
[docs/SPRINT_TASKS.csv](docs/SPRINT_TASKS.csv); work history is in
[docs/SPRINT_PROGRESS.md](docs/SPRINT_PROGRESS.md) and
[docs/REVIEW_READY.md](docs/REVIEW_READY.md).

## Finish line

The project is finished when the pre-registered Phase-1 gate
([design.md](docs/design.md#pre-registered-phase-1-gate-frozen-2026-08-23)) has
run on verified sites and one of its two endings is written up:

- **Gate passes.** Extract candidate lines on the development sites and the
  untouched holdout, and report precision and recall against dated reference
  imagery (Phase 4 in the design, without network conditioning).
- **Gate fails.** Write up where 10 m Sentinel-2 data stops resolving these
  corridors. The design lists this as a legitimate outcome, not a failure of
  the project.

The design capped Phase 0 and 1 at one weekend. They have taken seven weeks,
mostly because step 1 below has not happened.

## Where it stands (2026-09-30)

- Earth Engine screening code, the Phase-1 admission gate and the Python line
  extractor exist and are tested.
- The extractor passes 10 synthetic stress cases for curved corridors (≥ 0.93
  recall, ≥ 0.99 precision against the reference centreline). It still misses
  crossings and dashed tracks, splits one faint corridor into seven pieces, and
  invents a road along a riverbank ([stress results](results/README.md)).
- The first real Earth Engine run happened on 2026-09-29. The grid probe
  failed, was fixed and rerun, and confirmed that a nominal 10 m pixel in the
  Web Mercator grid is 6.79 m × 6.77 m on the ground at 47.3°N
  ([runtime record](results/earth_engine_runtime_2026-09-29.json)).
- First Phase-1 exports were submitted on unverified sites as a QA run. They
  are not a gate result.
- None of the six registered sites is verified.

## What's left

| # | Step | Who | Done when |
|---|---|---|---|
| 1 | Inspect the four gate sites (negative-01 first, then dev-01, dev-02, dev-03) in dated imagery using the [worksheet](docs/SITE_VERIFICATION_WORKSHEET.md): scene dates, provider, what is visible, and the three confounds (drainage channels, fence lines, animal paths). One sitting of about two hours, before looking at any model output. See [inspection decisions](#site-inspection-decisions-2026-09-30) | Owner | `verified`, `ref_imagery_date` and `provenance` filled in `config/sites.geojson` for the four sites, or a site recorded as rejected or uncertain. **Current step.** |
| 2 | Confirm the QA exports finished and match the runbook's expected files. Record task states and file names only; don't open the values until step 1 is committed | Agent | Export states recorded |
| 3 | Run the frozen Phase-1 configuration on the verified sites and apply the gate | Agent, in the Earth Engine Code Editor | Gate verdict committed with its exports |
| 4a | If it passes: extract lines on the development sites, then the holdout, and score them against the reference imagery | Agent, owner judges the holdout imagery | Precision and recall reported per site |
| 4b | If it fails: write the "where Sentinel-2 fails" report from the gate run and the sensitivity grid | Agent | Report merged |
| 5 | Update the README and portfolio with the outcome | Agent | Merged |

## Site inspection decisions (2026-09-30)

Made under the owner's delegation, before any site judgment or model output
has been looked at.

- **Inspector: the owner.** The gate needs a dated judgment by an actual
  person ([first-site packet](evidence/task-2026-09-19/cr08-first-site-packet.md)).
  An agent's read of the imagery is labelled AI-assisted and can't set
  `verified`.
- **Imagery: Google Earth historical imagery first.** If a site has no usable
  dated scene there, use Esri World Imagery Wayback and record the scene's
  acquisition date from its imagery metadata, not the Wayback release date.
- **Scope: the four sites the gate reads.** The gate code requires
  negative-01 and all three development sites verified. confound-01 isn't
  part of the gate and is inspected later. The holdout stays closed.
- **Order: negative-01 first.** If the road-free control turns out to have
  tracks, it needs a replacement, and that's cleanest to choose before any
  positive site has been judged.
- **Time limit: one sitting of about two hours.** Anything not clearly
  visible is recorded as uncertain and stays unverified. If a site is
  rejected or uncertain, the agent drafts a replacement-site amendment (old
  coordinates kept, chosen from imagery only) for the owner to approve before
  any gate output is opened.

## Not in this version

- OpenStreetMap network conditioning and seeded tracing (design Phase 3).
- Active versus abandoned classification.
- Any site substitution after seeing results. A relocated site is a design
  amendment that keeps the old coordinates.
