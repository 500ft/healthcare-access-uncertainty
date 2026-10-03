# Baseline packet

This packet contains clipped Microsoft RoadDetections and a historical OSM
snapshot for the non-holdout sites. Candidate layers remain unrendered in
`candidates-unopened.zip`. No baseline performance has been calculated.

## Owner entry point

Open only this page, [locations.json](locations.json), the
[reference-access record](reference-access.json), and the existing
[site worksheet](../../docs/SITE_VERIFICATION_WORKSHEET.md) before committing
your judgments. The location file contains boundaries and centers only. Its `.json` extension
avoids GitHub map previews that could expose OSM roads underneath the boundary.
Use its coordinates in the imagery viewer with map overlays off.
Do not open the candidate archive, existing detector outputs or holdout imagery.
The archive is packaged to avoid automatic map previews; it is not encrypted.

Labeling time has not been approved. If you choose to proceed, begin with the
road-free control, then the development sites in [settings.json](settings.json)
order. Inspect the confound site separately if time permits. Google Earth
historical imagery is the first viewing option; the access record supplies
Esri Wayback fallback links for each center. Keep road labels and other map
overlays off.

Draw reference corridor centerlines across the areas you actually inspect,
including corridors absent from existing maps. Record the inspected extent and
ambiguous or obscured polygons, rather than treating unseen areas as road-free.
For each judgment retain the provider, acquisition date, source link and
positional uncertainty. Record drainage channels, fence lines and animal paths
as possible confounds. An AI reading cannot verify a site. Unclear sites stay
unverified; replacements require an owner judgment and approval of an amendment
that retains the old coordinates.

A new-corridor label needs independently dated absence before and presence after,
compatible with the detector's periods. Archive publication dates cannot supply
either observation. Commit the references and judgments before revealing
Microsoft, OSM or detector geometry. Retain provider terms when making labels;
this packet does not grant rights to redistribute imagery or traced data.

## Prepared data and prospective rules

[provenance.json](provenance.json) records the input hash, published checksum
check, snapshot date, projection check and output hashes. The candidate archive
contains the exact OSM selection, snapshot metadata and raw selected ways, source IDs,
clipped line WKT in metres, source properties and an internal inventory. Inventory
counts describe extracted data only and stay out of the blind owner packet.

[settings.json](settings.json) is the source for the common metric CRS,
footprints, OSM selection and matching tolerances. The common Lambert conformal
conic covers the study region with checked scale distortion. Baseline footprint
bounds come from the registered centers and sizes. They do not change the
historical Earth Engine grid or gate.

Matching uses buffered centerline length, after clipping prediction and reference
to the same owner-inspected area and excluding ambiguous regions. Rules for
partial matches, branches, duplicates, empty denominators and the baseline union
are fixed in settings before any comparison. The primary radius is a prospective
engineering choice; assess reference uncertainty before revealing candidates and
record any required amendment. Future comparison must report Microsoft, OSM and
their union separately, including unmasked detection and additional coverage.

## Access and limits

The reference-access record confirms dated metadata and successful image-tile
delivery at the probed centers. The images were neither retained nor rendered.
Whole-site clarity, spatial coverage and eligibility of before/after dates still
need owner inspection. Acquisition fields and archive release dates are kept
separate, following [Esri's description](https://www.esri.com/arcgis-blog/products/arcgis-living-atlas/mapping/use-world-imagery-wayback).

Microsoft's per-feature acquisition dates are unavailable in this archive,
as its [data-vintage statement](https://github.com/microsoft/RoadDetections#data-vintage)
explains. The OSM snapshot dates the database state, not road construction.
The [Geofabrik country snapshot](https://download.geofabrik.de/asia/mongolia.html)
is streamed with complete way geometry, including crossings with no node inside
the footprint. Its public extract omits contributor identity fields. Selection
retains all highway values, including proposed and construction ways, for later
interpretation against dated references.
Neither baseline omissions nor their union establish ground truth. Neighboring
segments are not independent samples. Geometry overlap cannot establish network
connectivity or corridor identity.

Data extracts carry [ODbL attribution and derivative terms](ATTRIBUTION.md).

## Reproduce preparation

Use a fresh output directory. The supplied Microsoft ZIP remains input only.

```sh
python -m pip install -e 'analysis[dev,baseline]'
python tools/prepare_baselines.py \
  --archive /path/to/microsoft-eastern-asia.zip \
  --replay baseline/20261003/candidates-unopened.zip \
  --output /tmp/road-baseline-replay
python tools/test_prepare_baselines.py
```

Replay rebuilds the packet from the exact captured OSM subsets without network
requests or rendering. To prepare from the original sources, download the dated
PBF at `osm_snapshot_url` in settings, then replace `--replay` with
`--osm-pbf /path/to/mongolia-260930.osm.pbf`. The tool checks the published MD5
and the PBF header timestamp before extracting; retrieval metadata will change.
The initial Overpass requests failed with rate limiting and a timeout, so this
packet uses the dated country download instead. The preparation tool does not
print candidate counts. WKT coordinates use the archive's `metric-crs.wkt`.
To repeat the public imagery-access check without viewing images:

```sh
python tools/check_reference_access.py --output /tmp/road-reference-access.json
```

That command reads public metadata and checks tile bytes at the non-holdout
centers. It refuses to overwrite an existing record. No runtime approval or
permission change is required by these public endpoints.
