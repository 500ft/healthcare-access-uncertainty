# Timestamped trip feasibility probe

The [executed result](summary.json) contains usable/excluded counts for a small
development sample of UCI GPS Trajectories. Timestamped car/bus data can support a
parsing and travel-time prototype. This probe supplies no validated off-road
trips, no established Mongolian validation and no global journey-time model.
It makes no claim about suggested-route passability.

The analysis ran in an external local workspace. This directory preserves the
code, selection rules, source metadata and aggregate result. Raw data, exact
trip/device linkage, coordinates, endpoints and the owner exercise remain local.
No map or existing detector candidate layer was opened.

## Method and inventory

[protocol.json](protocol.json) fixes selection by declared mode and numeric trip
ID, timestamp ordering, gap treatment, provisional low-motion rules and the
constant-speed arithmetic exercise. Selection was fixed before point analysis.
Every selected trip is development. No final test set was allocated or scored.
The parser reports unknown mode codes separately and never assigns mode from
speed. A timestamped trip can pass structural parsing while still carrying a
gap or speed-consistency flag; only the continuous subset is eligible for the
worked timing example.

The [result](summary.json) records sampling intervals, stored coordinate and
timestamp precision, condition-code availability and a coarse geographic extent.
Decimal digits describe storage, not GPS accuracy. The coordinate datum is
undocumented, so distance uses a stated latitude/longitude assumption. The data
lack elevation, surface condition and vehicle configuration. Low-motion time is
an estimate; it cannot separate a traffic stop from other reasons for waiting.
Observed chords can miss turns or accumulate GPS jitter. Future validation must
use independent trips/corridors and account for repeated devices and seasons.

## Data rights and OSM assessment

Cruz, M., Macedo, H., Barreto, R., and Guimares, A. (2015),
[GPS Trajectories, UCI](https://doi.org/10.24432/C54S5Z), is licensed by its
[dataset page](https://archive.ics.uci.edu/dataset/354/gps%2Btrajectories) under
[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/legalcode.en).
The modifications here are selection and aggregate calculations. Source hashes,
download URL and retrieval dates are in [sources.json](sources.json). The MIT
licence for this repository's software does not replace the data licence.
CC BY does not grant privacy/personality rights; no identifiable trip example
is redistributed. The UCI website privacy policy concerns website use and does
not document consent for publishing a volunteer's home or destination.

The pinned [OSM visibility documentation](https://wiki.openstreetmap.org/w/index.php?title=Visibility_of_GPS_traces&oldid=3071050)
distinguishes identifiable and trackable traces, which expose timestamps through
the API, from legacy public/private settings without API timestamps. Visibility
alone does not establish vehicle mode or unrestricted reuse. Its details differ
from the older wording in the [OSMF privacy policy](https://osmfoundation.org/wiki/Privacy_Policy#GPS_Trace_Data),
so a future OSM sample must record the actual endpoint and fields received.
The [OSMF licensing minutes](https://osmfoundation.org/wiki/Licensing_Working_Group/Minutes/2024-10-07)
record historical GPX licensing ambiguity and date-dependent treatment. No OSM
traces were acquired in this probe. A direct archival fetch of the visibility
page returned HTTP 403; its pinned revision was read through the web tool.
Scheduled bus times were not used as observed trip times.

## Reproduce outside the repository

Needs Python and `bsdtar` with RAR reading support. Copy this directory into a
fresh external workspace, then run there:

```sh
python3 acquire.py
python3 parse_sample.py --output run-final
python3 check_sample.py
```

The downloader checks the data archive against the pinned hash. Documentation
captures can change; a new download receipt records their retrieved versions.
The parser refuses an existing output directory. Checks cover distance,
chronology, gaps, low-motion accounting, source/result hashes and public fields.
Compare the regenerated `run-final/summary.json` with this directory's captured
`summary.json`. Keep all `raw/`, `private-*` and per-trip run files outside git.
No detector test outputs or holdout imagery are needed.

The local `run-final/private-owner-exercise.json` identifies one continuous
example. Independently compute its adjacent-point distance, estimated low-motion
time, stop-adjusted elapsed time and residual against the protocol's illustrative
constant-speed baseline. This is an arithmetic exercise, not a validated model.

## Scope after the executed probe

The [owner decision](../../docs/ACCESS_STABILITY.md#owner-decision) supersedes the
separate route-planning proposal with healthcare-access software work in this
repository. No repository was created or renamed. This UCI sample is explicitly
non-Mongolian and provides no field validation.

This probe has no independent capture-reference comparison. Its worked timing
example reuses the source observations and cannot qualify their accuracy.
Likewise, two capture apps sharing a phone's GNSS or clock are not automatically
independent ground truth. Any successful qualification against a separate
reference would apply only to the tested setup.

The detector is inactive with its artifacts and blind labeling requirement
intact. No new drive, map matching, country-transfer test or route experiment
was performed during the software pivot.
