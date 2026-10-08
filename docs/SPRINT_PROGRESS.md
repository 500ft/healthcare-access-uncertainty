> Retained detector evidence and contract history. [ROADMAP.md](../ROADMAP.md) is the only active plan; instructions below do not authorize resumption.

# Progress log

What changed and when, newest first, one line per change that matters. The
plan is in the [roadmap](../ROADMAP.md). The earlier, longer version of this
log is kept at
[commit 033c951](https://github.com/500ft/informal-road-mapping/blob/033c9513db32b670cd56ae229f1afe4c390e0f9a/docs/SPRINT_PROGRESS.md).

## Week of 2026-09-28

- **09-30** Site inspection decided: the owner inspects the four gate sites,
  negative-01 first, in Google Earth historical imagery (Esri Wayback as the
  fallback), in one two-hour sitting before any model output is opened.
  confound-01 waits; the holdout stays closed.
- **09-30** One roadmap: run the frozen Phase-1 gate on verified sites, then
  write up whichever way it goes. README rewritten
  ([#47](https://github.com/500ft/informal-road-mapping/pull/47)).
- **09-30** First real Earth Engine run. The grid probe failed on its first
  try (scaled projection units, a bad buffer call, a missing kernel method), was
  fixed and rerun. It confirmed that a nominal 10 m pixel is 6.79 m × 6.77 m on
  the ground at 47.3°N. The first Phase-1 exports were submitted on unverified
  sites as a QA run ([#46](https://github.com/500ft/informal-road-mapping/pull/46)).
- **09-29** Owner instruction recorded: run Earth Engine tests in the signed-in
  browser Code Editor ([#41](https://github.com/500ft/informal-road-mapping/pull/41)).

## Week of 2026-09-21

- **09-26** Missing years are not neutral. Across 176 enumerated cases,
  dropping only quiet years turned 18 fails into passes, and dropping only
  disturbed years turned 12 passes into fails. The compositor comparison was
  frozen and the grid probe prepared
  ([#38](https://github.com/500ft/informal-road-mapping/pull/38)).
- **09-26** Parameter provenance audit: most thresholds were fixed before any
  result existed, but few have a recorded reason for their value
  ([#39](https://github.com/500ft/informal-road-mapping/pull/39)). The link
  between two pixel-count limits in the Earth Engine script is now documented
  and guarded ([#40](https://github.com/500ft/informal-road-mapping/pull/40)).
- **09-24 to 09-26** Literature corrections: seven overstated claims fixed, and
  the grid-scale problem recorded as claim C19, then copied into the design and
  runbook ([#36](https://github.com/500ft/informal-road-mapping/pull/36),
  [#37](https://github.com/500ft/informal-road-mapping/pull/37)).
- **09-24** Phase-1 evaluation packet template and a design note for the later
  topology work ([#35](https://github.com/500ft/informal-road-mapping/pull/35)).
- **09-22** Literature review mapped to the project's own claims
  ([#29](https://github.com/500ft/informal-road-mapping/pull/29)). The site
  worksheet now asks for three confounds (drainage channels, fence lines,
  animal paths) and a named recovery variable
  ([#34](https://github.com/500ft/informal-road-mapping/pull/34)).
- **09-20 to 09-21** Week plan and site-check packet; the stress-case gallery,
  stranded on an old branch, recovered to main
  ([#25](https://github.com/500ft/informal-road-mapping/pull/25),
  [#26](https://github.com/500ft/informal-road-mapping/pull/26),
  [#27](https://github.com/500ft/informal-road-mapping/pull/27)).
- **09-21** Curved corridors delivered as paths: every curved case that failed
  as a straight chord (recall 0.11, 0.25, 0.44) now passes at 0.93 or better
  ([#22](https://github.com/500ft/informal-road-mapping/pull/22)), with a
  five-figure gallery ([#24](https://github.com/500ft/informal-road-mapping/pull/24)).

## Week of 2026-09-14

- **09-15 to 09-16** Path export planned, built early, reverted, and rebuilt
  under the reviewed plan to a feasibility checkpoint
  ([#17](https://github.com/500ft/informal-road-mapping/pull/17) to
  [#21](https://github.com/500ft/informal-road-mapping/pull/21)).
- **09-14** Code simplified in two passes, behaviour unchanged
  ([#15](https://github.com/500ft/informal-road-mapping/pull/15),
  [#16](https://github.com/500ft/informal-road-mapping/pull/16)).

## Week of 2026-09-07

- **09-13** Extractor stress-tested beyond its favourable demo: ten synthetic
  cases, scored first on the component, then on the exported line, then
  against a reference centreline
  ([#12](https://github.com/500ft/informal-road-mapping/pull/12),
  [#13](https://github.com/500ft/informal-road-mapping/pull/13),
  [#14](https://github.com/500ft/informal-road-mapping/pull/14)).
- **09-10 to 09-12** Site inspection worksheets generated with the holdout
  excluded; worksheet preparation kept separate from actual verification
  ([#8](https://github.com/500ft/informal-road-mapping/pull/8),
  [#11](https://github.com/500ft/informal-road-mapping/pull/11)).
- **09-11** README and presentation rewrite
  ([#9](https://github.com/500ft/informal-road-mapping/pull/9)).
- **09-09** Missing-year schemas preserved and temporal QA enforced
  ([#6](https://github.com/500ft/informal-road-mapping/pull/6)); export paths
  rehearsed ([#7](https://github.com/500ft/informal-road-mapping/pull/7)).
- **09-07** Phase-1 evidence intake: the gate refuses malformed or unverified
  exports ([#5](https://github.com/500ft/informal-road-mapping/pull/5)).

## Week of 2026-08-31

- **09-03** Figure manifest added and the synthetic demo gated on its numbers
  ([#1](https://github.com/500ft/informal-road-mapping/pull/1)); dependency
  ranges bounded ([#2](https://github.com/500ft/informal-road-mapping/pull/2)).

## Before September

Repository created 2026-08-10 with the Earth Engine screening script, the
Python extractor and a known-truth synthetic demonstration. The Phase-1 gate
was frozen on 2026-08-23.
