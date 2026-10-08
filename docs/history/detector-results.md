# Retained detector results

The detector is inactive. The obsolete export/report workflow and placeholder
figure were removed; their original versions remain at the pre-cleanup revision
linked in the [history index](README.md). The following synthetic result
interpretation and numeric records are retained. Generators now use explicit
historical module imports.

## `extractor_stress_cases.json` — where the extractor detects, misses, fabricates, or misrepresents (CR-R03 → R03c → CR-09, 2026-09-16)

Ten fixed synthetic cases (`analysis/catanroads/stress_cases.py`), each with a road-area truth mask **and a 1-px reference centerline**, scored on two layers that must not be confused: the *component* layer (the extractor's internal mask vs the road-area truth, within 2 px) and the *delivered-line* layer (the geometry the extractor exports — since CR-09 the `path_px` polyline — **vs the reference centerline**, within 2 px, two 4-neighbour dilations). `chord_line` re-scores the legacy straight `endpoints_px` chord through the same scorer, so the pre-CR-09 line layer stays visible; `area_coverage` (how much of the road-area mask the delivered band covers) is a separate diagnostic and never enters `line_ok`. Regenerate with `PYTHONPATH=analysis python -m catanroads.stress_cases --out results/extractor_stress_cases.json` (schema v4 with provenance metadata), which stages a temporary file beside the destination, validates it by parsing it back, and only then replaces the record; a plain shell redirect truncates the committed record if the run fails mid-way, so `--out` is the documented path; `tests/test_stress_cases.py` pins the observed behaviour and the frozen CR-09 acceptance targets. `extractor_stress_cases_baseline_2026-09-12.json` (v1) and `extractor_stress_cases_baseline_v3_2026-09-14.json` (v3) are kept byte-unchanged and hash-tested. **Synthetic constructions only — nothing here is imagery or a site result.**

| case | cands | false | component recall | delivered path recall / precision | legacy chord recall / precision | area coverage |
|---|---:|---:|---:|---:|---:|---:|
| demo_reference | 6 | 0 | 0.92 | 0.93 / 1.00 | 0.44 / 0.45 | 0.89 |
| faint_corridor | 7 | 0 | 0.93 | 0.93 / 1.00 | 0.94 / 1.00 | 0.91 |
| wide_corridor | 1 | 0 | 1.00 | 1.00 / 1.00 | 1.00 / 1.00 | 0.38 |
| crossing | 0 | 0 | 0.00 | 0.00 / — | 0.00 / — | 0.00 |
| short_segments | 0 | 0 | 0.00 | 0.00 / — | 0.00 / — | 0.00 |
| linear_confound_riverbank | 1 | 1 | — | — / 0.00 | — / 0.00 | — |
| speckle_only | 0 | 0 | — | — / — | — / — | — |
| low_snr | 1 | 0 | 1.00 | 0.99 / 1.00 | 0.11 / 0.11 | 0.99 |
| gradient_background | 3 | 2 | 1.00 | 1.00 / 0.90 | 1.00 / 0.90 | 1.00 |
| tight_curve | 1 | 0 | 1.00 | 1.00 / 1.00 | 0.25 / 0.26 | 1.00 |

**Four records.** (v1) component layer only. (v2) the component score is blind to the exported geometry, so a line layer was added; `width_px` is the component's minor-axis *extent*, 54.7 px for the curved corridor at zero noise. (v3) the line layer is scored against the reference centerline, not the road-area mask, so a perfect centerline scores 1.0 regardless of road width. (v4, CR-09) the delivered geometry is `path_px`, one interior-biased route per accepted component (padded-crop distance transform, symmetric `1/edt` edge cost, single-source Dijkstra, every vertex kept; endpoints per plan amendment A), and the chord result is retained as `chord_line`. Every curved corridor that failed the chord (0.11 / 0.25 / 0.44) now passes at ≥ 0.93 recall with ≥ 0.99 precision; straight cases are within their frozen allowances; component-layer numbers are identical across all four records. Three declared sensitivity seeds are recorded under `sensitivity_seeds`, unturned.

What still fails, by construction: crossings and dashes are missed (elongation and minimum-length filters); the river-bank confound is fabricated; the faint corridor is still delivered as seven pieces; one route per component cannot represent junctions, loops or braids. Recorded in [the CR-09 evidence](../../evidence/task-2026-09-14/README.md).
