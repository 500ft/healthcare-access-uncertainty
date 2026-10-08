# Historical development inputs

The [manifest](manifest.json) pins acquired population and flood bytes and an
archived boundary candidate. The missing development flood download is recovered.
The population product has explicit reuse terms; exact historical roads and the
facility snapshot remain unresolved. M1 is incomplete.

## Qualification result

| Input | Acquired evidence | Remaining qualification |
| --- | --- | --- |
| Population | Original WorldPop raster, product DOI, catalog metadata and explicit CC BY license | No author-side hash is available; product and upstream filename agree. |
| Boundary | Archived SSCGS GeoJSON whose downloaded hash matches the Git LFS object at a fixed archive commit; ODbL terms | The study's unversioned boundary call does not establish which release it used. |
| Development WFP flood mask | Original ZIP, intact CRC and the expected TIFF; GET resolves the earlier HEAD access failure | Historical byte identity and exact catalog license version need confirmation. |
| Development UNOSAT flood mask | Original ZIP, intact CRC and member hashes | A populated water layer extends beyond the paper's stated dates. The upstream filename filter would include it. Historical membership and exact license version need confirmation. |
| Roads | Original source code and public archive index inspected | The moving extract has no historical hash or exact extraction day. No current or adjacent annual extract was substituted. |
| Facilities | Original paper and pinned request inspected | Their snapshot dates disagree. No date, service or replacement list was selected. |

All dates, identifiers, original response hashes, actual data hashes, inspected
header values, attribution and license URLs live in the manifest. Its selected
metadata fields are a projection of downloaded responses. Their response hashes
identify the original metadata bytes, separately from data hashes. A DOI or HDX
resource identifier does not guarantee that a downloadable file is immutable;
the fetch command rejects any change from the acquired content.

## Reproduce acquisition

Requires Python 3.11 or later with working HTTPS trust certificates. From the
repository root, choose an external directory:

```sh
python3 tools/fetch_idai_development.py --output /absolute/path/to/idai-development
python3 tools/fetch_idai_development.py --output /absolute/path/to/idai-development --check-only
python3 -m pytest analysis/tests/test_idai_fetch.py -q
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
those identities and the owner-defined estimand and tolerance. Reserved WFP
road-constraint outcomes and detector holdouts remain unopened. The acquired WFP
flood mask is the explicitly referenced development input.
