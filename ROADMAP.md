# Roadmap

## Question and finish line

Which healthcare-access classifications remain stable under credible road-time,
closure and facility uncertainty, and which affordable observations resolve the
most consequential errors?

Finish with a reproduced development baseline, justified uncertainty bounds,
measurement policies compared at equal route-based acquisition cost, and a
separately registered evaluation against independent observations. Report both
unresolved decisions and observed errors. A negative comparison is a valid
result; missing observations cannot establish success or failure.

The owner adopted this dependency plan and cleanup for the existing software
project. The [decision record](docs/ACCESS_STABILITY.md#owner-decision) preserves
the scope of that adoption. [Current evidence](results/README.md) distinguishes
the executed toy result from the blocked real-area study.

## Dependencies and verified state

Qualified inputs and target → independent development replication → justified
bounds and stability → route-cost measurement selection → independent evaluation.

Evaluation metadata can be qualified alongside development, but reserved outcomes
stay closed until eligibility, models and the evaluation procedure are frozen.

- Done: interval bounds, optional closures, inverse speed conversion and nested
  widening verified on toy graphs by an independent exhaustive oracle.
- Done: development source and WFP catalog metadata inspected and hashed.
- Done: acquired and hashed the published population product and both
  development flood archives; matched an archived boundary candidate to its
  immutable archive object. The [input record](evidence/idai-development-inputs/README.md)
  separates qualified reuse from unresolved historical identity and flood terms.
- Done: inspected the paper supplements and source requests, confirmed actual
  flood sensor dates in the acquired archive, and corrected incomplete snapshot
  provenance. The [source review](evidence/idai-development-inputs/source-review.json)
  also records why the Robert candidate remains ineligible.
- Done: current Sofala topology fixture executed with synthetic intervals, closures,
  exhaustive small-subgraph checks, independent endpoint checks and measured
  scaling. The [compute record](evidence/sofala-scaling/README.md) also records
  actual isolated upstream schema and runtime failures. This owner-authorized
  software fixture does not replace the historical baseline or adopt a clinical
  target.
- Done: owner selected the published network-driving potential-access quantity
  at the paper's maximum driving horizon for first reproduction. The
  [decision record](docs/ACCESS_STABILITY.md#reproduction-target-adopted-by-the-owner)
  defines its scope and a precision-based comparison rule.
- Done: owner accepted a documented reconstruction of that quantity as the
  first fallback if original historical inputs cannot be recovered. Candidate
  substitutions still need identity, rights and sensitivity checks; see the
  [decision record](docs/ACCESS_STABILITY.md#reconstruction-fallback-adopted-by-the-owner).
- Done: sent the author and flood-custodian source and rights requests. The
  [decision record](docs/ACCESS_STABILITY.md#reproduction-target-adopted-by-the-owner)
  records the pending evidence.
- Done: checked the documented OSM history route and alternative public
  accessibility artifacts. The [source check](evidence/idai-development-inputs/reconstruction-qualification.json)
  records the failed tiny extraction and why the available distance and
  Google-derived time products do not qualify as this baseline or independent
  observations.
- Current, blocked: await responses to recover the historical road extract and
  final facility list, settle boundary and flood membership, confirm rights,
  and obtain reference output and routing settings to derive a numerical
  comparison tolerance. No Idai baseline has been reproduced.
- Future: real-area stability, policy comparison and independent evaluation.

## M1. Qualify and reproduce the development baseline

Prerequisites: immutable, legally usable development inputs and the original
routing configuration. The owner selected the paper's network-driving
potential-access quantity at its maximum driving horizon; see the
[decision record](docs/ACCESS_STABILITY.md#reproduction-target-adopted-by-the-owner).
Facility membership, input periods, direction and numerical comparison details
need original-source confirmation. This target measures modeled geographical
coverage, not actual service availability.

1. Pin road snapshot, facility list, population, boundary and impact inputs with
   source, rights, acquisition/snapshot timing and content hashes. Resolve the
   moving road extract and historical input discrepancies in the
   [acquired-input record](evidence/idai-development-inputs/README.md).
   The development flood download is recovered; its historical identity and
   rights qualification remain open.
2. Confirm the final mapped facility list, source snapshots, routing direction,
   raster denominator, boundary clipping and treatment of disconnected areas
   against the original calculation. Derive the reproduction tolerance from
   reference precision and checked numerical error before comparing results.
   Keep it separate from clinical acceptability.
3. Reproduce that baseline independently from its qualified inputs. Keep modeled
   flood closures distinct from observed passability. If upstream GPL code is
   incorporated into a distributed combined program, satisfy the applicable
   license obligations; a separate folder is insufficient.

Completion evidence: input hashes and permissions, a fully specified version of
the adopted estimand, runnable commands and a source-linked comparison within
the declared tolerance, or an explained discrepancy. Software tests alone do not complete this milestone.
Original road bytes remain unrecovered. A historical reconstruction is an
accepted conditional fallback and must be labeled separately from exact
replication. Its actual input substitutions still need qualification. Changes
to the published estimand require a new-study scope decision. The
[source request](evidence/idai-development-inputs/source-review.json#needed_source_request)
identifies missing author artifacts. Stop before replication or substitution
until source eligibility and remaining target details are settled.

## M2. Establish real-area decision stability

Prerequisites: M1 and at least two independently sourced, defensible bound
families. The existing toy intervals do not qualify either family.

1. Convert positive speed bounds into time bounds with the inverse endpoints.
   Represent possible closures explicitly; address common weather effects,
   correlated road conditions, missing links and facility availability.
2. Specify admissible joint scenarios and the assumptions connecting each bound
   source to the service and mode. Marginal coverage is not joint route coverage.
   The existing implementation assumes fixed available facilities; qualify any
   facility-scenario extension before using it for claims.
3. Compute definite access, definite exclusion and unresolved decisions, including
   disconnected cases. Verify nested widening cannot create a definite decision
   from an unresolved one on the same graph and facility set.
4. Produce a reproducible development figure and note linking classifications to
   source bounds, thresholds and assumptions. Label synthetic cases separately.

Completion evidence: qualified independent bound families, implementation checks
covering their joint assumptions, and real-area outputs with unresolved cases
and sensitivity to widening reported. No probabilistic guarantee is inferred
from the deterministic interval proof.

## M3. Compare measurement selection at route-based cost

Prerequisites: M2, an explicit observation model and a feasible acquisition-cost
model. A route incurs travel and observation costs, including shared travel,
return/access constraints and failed or inaccessible observations.

1. Freeze budgets and scoring before comparing decision-focused, random,
   near-threshold, road-class/length and feasible centrality policies. Use the
   same route-based budgets, starting conditions and feasible observation set.
   Include a greedy value-of-information verification rule (Li et al. 2026
   style); see [bibliography section 15](literature/bibliography.md#15-healthcare-access-under-road-closure-uncertainty-added-2026-10-09).
2. Specify how each observation updates bounds and how unresolved decisions,
   incorrect definite decisions and service consequences enter the comparison.
3. Run development comparisons. Synthetic hidden truth may test the procedure,
   but must be reported separately from errors measured against real observations.
   Report variation and sensitivity; neither a pilot target nor a problem count
   supplies a sample-size justification.

Completion evidence: reproducible policy outputs, actual route-cost accounting
and equal-budget comparisons with uncertainty and failure cases. If the more
complex policy does not improve on near-threshold or other simple policies,
simplify it and report the result rather than selecting favorable cases.

## M4. Evaluate independently, conditionally

Prerequisites: M3 and separately qualified observations with licensed immutable
bytes, observation timing, vehicle/service scope, coverage and traceable lineage.
WFP Idai is an ineligible reserved candidate until these requirements are met.
Shared event, OSM geometry and possible partner-report overlap with development
must be resolved. Unreported roads remain unknown, never passable negatives.

1. Freeze eligibility and exclusion rules from metadata, then arrange a custodian
   content-hash freeze before opening outcome rows. Register matching rules,
   models, bound widths, policies, budgets and metrics before exposure.
2. Evaluate the frozen procedure once. Report decision resolution and observed
   errors as bounds widen, accounting for dependence, incomplete reporting and
   uncertainty. Do not tune on reserved outcomes.
3. If independence cannot be established, request a decision on another source
   or event. A second region is a conditional extension requiring its own rights,
   qualification and registration, not an assumed ready dataset.

Completion evidence: frozen registration and hashes, independent observation
provenance, reproducible comparisons and an explicit account of exclusions and
limits. A write-up must separate executed findings from unresolved evidence.
Publication, external contact and field collection remain separate decisions.

## Owner inputs and retained safeguards

The next unblocking input is the original road extract or its exact historical
identity, the final facility export, boundary and flood member versions,
routing configuration and unrounded reference outputs. Custodians must confirm
the applicable dataset terms. Derive and freeze the numerical reproduction
tolerance from those sources before comparison; the target itself is selected.
Changing the study or its estimand, acquisition commitments and any physical
work require an explicit owner decision. No purchase, naming change or
publication is adopted.

The detector question is inactive and superseded; its scientific outcome remains
unresolved. The [history index](docs/history/README.md) identifies retained
reproduction code, frozen configuration and evidence. Candidate layers and old
holdouts remain closed. Cleanup supplies no labels or authority to resume that
study; resumption requires an explicit decision and the original blind safeguards.
