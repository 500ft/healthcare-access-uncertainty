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
- Current, blocked: recover the historical road extract, resolve the facility
  snapshot and flood membership, confirm the boundary version and flood license
  versions, and define the estimand. No Idai baseline has been reproduced.
- Future: real-area stability, policy comparison and independent evaluation.

## M1. Qualify and reproduce the development baseline

Prerequisites: access to immutable, legally usable development inputs and a
specific healthcare service, transport mode, study period and access threshold.
The target must distinguish network travel time from actual service availability.
No choice is inferred from an example in the external proposal.

1. Pin road snapshot, facility list, population, boundary and impact inputs with
   source, rights, acquisition/snapshot timing and content hashes. Resolve the
   moving road extract and historical input discrepancies in the
   [acquired-input record](evidence/idai-development-inputs/README.md).
   The development flood download is recovered; its historical identity and
   rights qualification remain open.
2. State the target population, origin units, facility eligibility, departure
   conditions and treatment of missing connections and disconnected origins.
   Identify which published Idai quantity is being reproduced and predeclare
   its tolerance and denominator before comparing results.
3. Reproduce that baseline independently from its qualified inputs. Keep modeled
   flood closures distinct from observed passability. If upstream GPL code is
   incorporated into a distributed combined program, satisfy the applicable
   license obligations; a separate folder is insufficient.

Completion evidence: input hashes and permissions, a precise estimand, runnable
commands and a source-linked comparison within the declared tolerance, or an
explained discrepancy. Software tests alone do not complete this milestone.
If exact historical inputs cannot be qualified, stop replication and request a
scope decision before substituting a new development study.

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
   style), added 2026-10-09 from the literature review under owner instruction;
   see [bibliography section 15](literature/bibliography.md#15-healthcare-access-under-road-closure-uncertainty-added-2026-10-09).
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
identity, resolution of the facility snapshot and flood membership discrepancies,
and confirmation of boundary version and flood license terms. The owner must
also specify the target and comparison tolerance before replication.
Substitution of the study, acquisition commitments and any physical work require
an explicit owner decision. No purchase, naming change or publication is adopted.

The detector question is inactive and superseded; its scientific outcome remains
unresolved. The [history index](docs/history/README.md) identifies retained
reproduction code, frozen configuration and evidence. Candidate layers and old
holdouts remain closed. Cleanup supplies no labels or authority to resume that
study; resumption requires an explicit decision and the original blind safeguards.
