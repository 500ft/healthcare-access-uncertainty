# Toy access bounds and source qualification

Generated from [result.json](../../evidence/access-stability-20261006/result.json) and
[qualification.json](../../evidence/access-stability-20261006/qualification.json).
These remain the authoritative sources; do not edit these derived tables.

## Deterministic toy bounds

Access threshold: 10 min, with equality counted as access.
Intervals are deterministic assumptions. Infinity denotes unreachable or unbounded
travel time, not missing data. Clinic is the fixed destination. Integers retain
the precision of the source. [Download bounds CSV](bounds.csv).

| Node | Original interval [min] | Original decision | Widened interval [min] | Widened decision |
| :--- | ---: | :--- | ---: | :--- |
| A | [5, 8] | Definite access | [3, 12] | Unresolved |
| B | [18, 25] | Definite exclusion | [8, 30] | Unresolved |
| C | [7, 11] | Unresolved | [4, 17] | Unresolved |
| D | [4, ∞] | Unresolved | [2, ∞] | Unresolved |
| E | [∞, ∞] | Definite exclusion | [∞, ∞] | Definite exclusion |
| Clinic | [0, 0] | Definite access | [0, 0] | Definite access |

## Development input qualification

Recorded baseline status: **blocked**.
These are recorded metadata findings, not new availability probes.
[Download qualification CSV](qualification.csv). Empty optional CSV fields mean
the source record does not supply that field; they do not mean zero.

| Input | Recorded source | Qualification finding |
| :--- | :--- | :--- |
| Road network | OpenStreetMap via osmextract / Geofabrik | upstream uses geofabrik_mozambique-latest.osm.pbf; no historical input bytes or checksum in pinned tree; data ODbL attribution must accompany any future extract |
| Facilities | OSM via ohsome | not incident-time observations; availability/service capability not established by map tags |
| Population | WorldPop | HEAD reachable; exact product redistribution license not qualified; payload not acquired |
| Boundary | geoBoundaries SSCGS via rgeoboundaries | version not pinned; exact input terms and bytes not qualified |
| Floods | UNOSAT plus ARC/WFP | UNOSAT HEAD reachable; WFP archive HEAD HTTP 403; exact input terms and bytes not qualified |

## Reserved WFP candidate

Metadata only. No reserved outcome rows or previews were opened.

| Item | Recorded finding |
| :--- | :--- |
| Eligibility | reserved candidate ineligible pending metadata |
| Vehicle scope | not established by catalog; generic schema speed fields do not establish observed speed or mode |
| Observation timing | catalog date and file update dates are not row observation times |
| Coverage | Only roads with access-constraint information; unreported roads remain unknown, never passable negatives. |
| Independence | Shared OSM geometry and same event as development. Partner reports may overlap development flood evidence; independence not established. |
| Outcome hash | not downloaded; provider hash fields are empty; originalHash is not a cryptographic content freeze |

The full source record retains the exclusion rules, licenses and source pins.
The [roadmap](../../ROADMAP.md) governs qualification before evaluation.
