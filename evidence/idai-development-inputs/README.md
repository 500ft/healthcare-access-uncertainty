# Historical development inputs

The [manifest](manifest.json) pins acquired population and flood bytes and an
archived boundary candidate. The missing development flood download is recovered.
The population product has explicit reuse terms; exact historical roads and the
facility snapshot remain unresolved. The [source review](source-review.json) corrects
the paper-period record and confirms flood dates from the acquired archive. M1
is incomplete.

The [reconstruction source check](reconstruction-qualification.json) verified
the available OSM history route and the downloaded Mao/Danso artifact hashes.
The paper used a later road extract for its retrospective event analysis and
notes the resulting time bias. The pinned author script downloads a moving PBF,
so neither that script nor an arbitrary event-time snapshot recovers its
original input. A tiny historical Overpass request first failed at both tested
endpoints; the rerun with an identifying User-Agent returned the requested 2021
state from both, so small-scale public attic access works. No road extract was
acquired. The full-history OSM route retains
raw nodes, ways and relations before clipping, but the author's timestamp,
extract rules and routing import remain unknown. Any newly built road input
would be a documented reconstruction.

The Mao/Danso code uses road distance in kilometers as model impedance and
snaps onto its largest strongly connected component. The Nigeria travel times
are Google-derived estimates checked against Google. Neither supplies
independent Idai driving-time observations. WFP road constraints and the
aerial survey were checked at catalog level only. Their outcome rows remain
reserved, and the WFP road catalog's terms do not settle the separate flood
archive grants.

## Qualification result

| Input | Acquired evidence | Remaining qualification |
| --- | --- | --- |
| Population | Original WorldPop raster, product DOI, catalog metadata and explicit CC BY license | No author-side hash is available; product and upstream filename agree. |
| Boundary | Archived SSCGS GeoJSON whose downloaded hash matches the Git LFS object at a fixed archive commit; ODbL terms | The study's unversioned boundary call does not establish which release it used. |
| Development WFP flood mask | Original ZIP, intact CRC and the expected TIFF; GET resolves the earlier HEAD access failure | Historical byte identity and exact catalog license version need confirmation. |
| Development UNOSAT flood mask | Original ZIP, intact CRC and member hashes | A populated water layer extends beyond the paper's stated dates. The upstream filename filter would include it. Historical membership and exact license version need confirmation. |
| Roads | Original source code and public archive index inspected | The moving extract has no historical hash or exact extraction day. No current or adjacent annual extract was substituted. |
| Facilities | Original paper and pinned request inspected | Paper, code and the performance supplement do not identify one final dated list. No replacement was selected. |

All dates, identifiers, original response hashes, actual data hashes, inspected
header values, attribution and license URLs live in the manifest. Its selected
metadata fields are a projection of downloaded responses. Their response hashes
identify the original metadata bytes, separately from data hashes. A DOI or HDX
resource identifier does not guarantee that a downloadable file is immutable;
the fetch command rejects any change from the acquired content.

## Reproduce acquisition

The [executed sensor-date inventory](flood-sensor-dates.json) reads the actual date
fields of the water layers selected by the upstream filename rule. It distinguishes
active and deleted records and leaves missing dates explicit. The alternative
March catalog links to the same cumulative ZIP. No historical subset was silently
chosen. The supplements also leave the boundary version unspecified.

Original road bytes were not recovered from the public tree, release listing or
extract index. Rebuilding a dated OSM state would be a reconstruction. Exact
replication requires the author's original bytes and processing identity. The
[source request](source-review.json#needed_source_request) identifies what is
missing. The author and WFP and UNOSAT custodians were contacted; responses
and rights confirmation are pending. The source-review field retains the
original draft status as historical evidence.

## Conditional reconstruction inputs

The owner accepts a documented reconstruction of the same published quantity
if the original historical inputs cannot be recovered. This table compares
available candidates with the original roles. The [manifest](manifest.json)
holds each acquired file's full SHA-256, source, snapshot and terms in one
place. The [current-network source](../sofala-scaling/source.json) separately
holds the exact hash and ODbL notice for the software fixture. No candidate is
selected for a baseline run here.

| Original role | Available candidate and source, hash, terms | Effect on comparison | Proposed sensitivity check |
| --- | --- | --- | --- |
| National road extract used by the routing engine | No suitable national replacement is acquired. The current Beira-area OSM fixture is pinned in the current-network source under ODbL and contains synthetic times. | Its limited area, later road state and assumed times change reachability and the driving model. | Once an eligible national historical reconstruction exists, compare road coverage, direction rules, connectivity and covered population against any recovered author extract or nearby qualified snapshots. |
| Final mapped healthcare facilities | No final export is acquired. The pinned ohsome query and ODbL terms are in the [source review](source-review.json); the code's active date conflicts with the paper's account. | Facility locations, eligibility and count alter every isochrone. | Compare facility IDs, tags and locations across the author export and any justified dated rebuild. Report coverage changes without tuning the chosen snapshot to the published total. |
| Population denominator and cell weights | The acquired original WorldPop product has a content hash, product identifier and CC BY 4.0 terms in the manifest. Author-side byte equality remains unconfirmed. | Different cells, nodata or totals change both numerator and denominator. | Check author bytes if supplied; otherwise report cell support, nodata and aggregate sensitivity for any eligible alternative product. |
| National clipping boundary | The archived SSCGS candidate has a content hash and ODbL terms in the manifest. Its match to the author's unpinned boundary call is unknown. | Clipping changes eligible facilities, road edges and population support. | Compare boundary geometry, included facilities and population support against a recovered author file or another qualified release. |
| Development WFP flood mask | The acquired ZIP is hash-pinned in the manifest. Historical byte identity and its resource-specific CC BY version remain open. | Normal-condition coverage is unaffected; a later flood-loss comparison could change. | After rights and membership are established, compare the impacted area and route closures under the original and eligible alternative mask. |
| Development UNOSAT flood members | The acquired ZIP is hash-pinned in the manifest. Its selected water layers include a later observation; historical membership and CC BY-SA version remain open. | The modeled impact union and later road removal could change. | Compare the author member list with each justified eligible member set before any flood-loss calculation. |

The [decision record](../../docs/ACCESS_STABILITY.md#reconstruction-fallback-adopted-by-the-owner)
retains the published estimand for reconstruction. A material change to its
population, facility eligibility, routing direction, mode or access statistic
needs a new-study decision. Source eligibility comes before any substitution
run. The isolated [upstream probe](../sofala-scaling/README.md#actual-upstream-compatibility-result)
already exposed layer, coordinate and backend dependencies; rerunning it cannot
recover historical inputs.

Requires Python 3.11 or later with working HTTPS trust certificates. From the
repository root, choose an external directory:

```sh
python3 tools/fetch_idai_development.py --output /absolute/path/to/idai-development
python3 tools/fetch_idai_development.py --output /absolute/path/to/idai-development --check-only
python3 tools/inspect_idai_flood_dates.py --input /absolute/path/to/idai-development
python3 -m pytest analysis/tests/test_idai_fetch.py analysis/tests/test_idai_flood_dates.py -q
```

Only the manifest's acquired development assets are fetched. Existing files are
verified and preserved. The command does not extract, clip, reproject, select
facilities, build a flood union or run accessibility analysis. Inputs remain
outside Git. The original ZIPs are unchanged; member hashes describe bytes read
inside them. Header inspection and archive CRC checks were performed during
qualification without rendering imagery or computing study results.

## Rights and limits

Retain the manifest with the downloaded data. WorldPop attribution and change
notices follow its dataset license; this does not grant rights to its separate
building-footprint inputs. The archived boundary carries OSM attribution and
ODbL obligations, including share-alike and access to alterations when publicly
using a derivative database. It is not qualified merely by the geoBoundaries
website's general license statement.

The flood catalogs point to license-family pages listing multiple versions.
Their current overview links alone cannot settle the historical grant. Keep
these archives local pending that resolution; no flood data or derivatives are
redistributed here. The upstream program's GPL license is separate from all
input licenses. This fetcher is original code and incorporates no upstream code.

The [paper](https://doi.org/10.1186/s12942-022-00315-2), pinned source and retrieved
archive disagree on parts of the historical input identity. No layer has been
silently excluded to resolve that disagreement. Baseline replication requires
those identities and the
[adopted reproduction target](../../docs/ACCESS_STABILITY.md#reproduction-target-adopted-by-the-owner)
with a source-derived numerical tolerance. Reserved WFP
road-constraint outcomes and detector holdouts remain unopened. The acquired WFP
flood mask is the explicitly referenced development input.

## Kenya source status

The exact Robert paper and supplement were read, and its linked source portals
were inspected for metadata and rights. The [candidate record](source-review.json#robert2026)
separates publication access from dataset permission. The roads portal requires
written consent and restricts transfer; the linked flood item has no license entry.
That input candidate remains unqualified. A separate
[owner-reported Macharia exchange](source-review.json#macharia_kenya_closure_route)
rules out its particular closure-report route for independent final evaluation.
The raw correspondence was not reviewed here. No Kenyan input layer or reserved
observation was acquired.
