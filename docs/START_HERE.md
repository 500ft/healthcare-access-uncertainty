# Start here

The [README](../README.md) is the overview and the [roadmap](../ROADMAP.md) is
the plan. This guide is for reading the work quickly or rerunning it.

## Two-minute review

1. Read the [README](../README.md) and the [roadmap](../ROADMAP.md).
2. Look at the [stress-case results](../results/README.md) and the
   [Earth Engine runtime record](../results/earth_engine_runtime_2026-09-29.json).
3. Read the [frozen Phase-1 gate](design.md#pre-registered-phase-1-gate-frozen-2026-08-23)
   and the [review index](REVIEW_READY.md).

So far the project has tested screening and extraction code and a gate fixed in
advance. It has not produced a road map of any real site.

## Reproduce the local checks

Set up as in the [README](../README.md#getting-started). The Python import name
is still `catanroads`. The checks are the Python tests and the two Node scripts
in [CI](../.github/workflows/ci.yml); none of them contacts Earth Engine.

If pytest crashes while importing `readline` on your machine, this works around
it:

```sh
PYTHONPATH=analysis python -c 'import sys,types; sys.modules["readline"]=types.ModuleType("readline"); import pytest; raise SystemExit(pytest.main(["analysis/tests","-q"]))'
```

## Synthetic demonstration

After installing `analysis[dev]`:

```sh
python analysis/demo_synthetic.py
MPLBACKEND=Agg PYTHONPATH=analysis python analysis/plot_stress_cases.py
```

The first command overwrites `results/method_demo_synthetic.png`; the second
rewrites the five figures in `results/figures/`. Run them in a spare clone, or
check the diff afterwards. The [figure guide](data-and-figures.md) says where
each figure comes from.

The [method illustration](../assets/method.png) shows the full intended
pipeline. Its network-conditioning and confirmation stages are plans that have
not been built.

## Real imagery

Record what each site actually contains from dated imagery, using the
[site worksheet](SITE_VERIFICATION_WORKSHEET.md), before looking at any model
output. The worksheet leaves out the holdout site; don't open its imagery until
the candidate and the evaluation are frozen. A missing or unclear image leaves
the site unverified; it is not a negative.

Once sites are verified, run the [Phase-1 runbook](PHASE1_RUNBOOK.md) in the
signed-in Earth Engine Code Editor. The exported numbers decide the gate, not
the map colours. Run the primary configuration before any sensitivity study,
and don't swap sites after seeing a result.

The gate looks for new disturbance. It won't find a stable bare road or one
that is recovering, and it doesn't measure traffic.

## Where to make a change

| Change | Where |
| --- | --- |
| Study design and gate rules | [Design](design.md), [runbook](PHASE1_RUNBOOK.md) |
| Sites and the inspection form | [Site manifest](../config/sites.geojson), [worksheet](SITE_VERIFICATION_WORKSHEET.md) |
| Earth Engine screening | [gee/ndvi_change.js](../gee/ndvi_change.js) |
| Extraction and the gate code | [Python package](../analysis/catanroads/) |
| Tests | [analysis/tests](../analysis/tests/) |
| Figures | [Figure guide](data-and-figures.md), [results](../results/README.md) |

Read [CONTRIBUTING.md](../CONTRIBUTING.md) first. Never fill a site's
verification fields from assumptions. The [identity note](REPOSITORY_IDENTITY.md)
explains the rename, and the September 11
[completion correction](COMPLETION_RECONCILIATION.md) explains which early
deliverables were preparation rather than finished work.
