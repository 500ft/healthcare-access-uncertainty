# Start here

Read the [current question and result](../README.md),
[method and adoption decision](ACCESS_STABILITY.md), then the
[roadmap](../ROADMAP.md). The [qualification record](../evidence/access-stability-20261006/qualification.json)
is the source for real-data blockers and the reserved candidate's eligibility.

## Reproduce the software result

Install the existing dependencies as described in the
[README](../README.md#getting-started), then run from the repository root:

```sh
MPLBACKEND=Agg PYTHONPATH=analysis python analysis/run_access_demo.py
PYTHONPATH=analysis python -m pytest analysis/tests/test_access_bounds.py -q
(cd evidence/access-stability-20261006 && shasum -a 256 -c metadata-freeze.sha256)
python tools/check_presentation.py . "Healthcare Access Uncertainty" healthcare-access-uncertainty
python tools/test_presentation.py
```

The generator runs the toy example and exhaustive finite-world oracle. It writes
[result.json](../evidence/access-stability-20261006/result.json) and the
[figure](../evidence/access-stability-20261006/bounds.png).

## Retained checks and history

The [history index](history/README.md) labels the inactive detector work. Its
software regression checks remain useful:

```sh
python -m pip install -e "analysis[dev,baseline,detector]"
PYTHONPATH=analysis python -m pytest analysis/tests -q
node tools/validate_phase1.mjs
node tools/test_temporal_qa.mjs
python tools/test_prepare_baselines.py
PYTHONPATH=analysis python -m catanroads.site_worksheet --check
```

These are local software/static checks. They do not establish Earth Engine
runtime behavior or authorize opening detector candidate layers and holdouts.
The new WFP candidate's outcome rows also remain reserved.
