# Frozen detector source

`gee/ndvi_change.js` is retained to reproduce the offline missingness analysis,
source checks and recorded Earth Engine work. It is inactive study source, not
an access-study configuration or a run request. Its bytes match the former
`gee/ndvi_change.js` at the
[pre-cleanup revision](https://github.com/500ft/informal-road-mapping/tree/f6d485d5434d7797d1b42855ea3f524e64eed37e).

The site manifest remains at [config/sites.geojson](../../config/sites.geojson).
The baseline packet pins the preparation script hash, and that unchanged script
resolves this original manifest path. Both are retained for reproduction.
Internal historical path comments in the frozen Earth Engine source remain
unchanged; local checks resolve its relocated path.

No site is verified by cleanup. Do not inspect holdout imagery or candidate
layers. See the [history index](../../docs/history/README.md).
