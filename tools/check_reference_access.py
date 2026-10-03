"""Capture dated Wayback metadata and check tile delivery, without rendering imagery."""
import argparse
from datetime import datetime, timezone
import json
import math
from pathlib import Path
import re
import urllib.parse

from prepare_baselines import DEFAULT_SETTINGS, ROOT, digest, encoded, get, selected_sites


def release_date(item):
    return re.search(r"\d{4}-\d{2}-\d{2}", item["itemTitle"])[0]


def check(output):
    settings = json.loads(DEFAULT_SETTINGS.read_text())
    sites = selected_sites(json.loads((ROOT / "config/sites.geojson").read_text()), settings)
    raw, _ = get(settings["wayback_catalog_url"])
    catalog = json.loads(raw)
    available = [(key, item) for key, item in catalog.items()
                 if release_date(item) <= settings["osm_as_of"][:10]]
    recent = max(available, key=lambda pair: release_date(pair[1]))
    early = max((pair for pair in available
                 if release_date(pair[1]) <= settings["early_wayback_release_on_or_before"]),
                key=lambda pair: release_date(pair[1]))
    record = {"checked_utc": datetime.now(timezone.utc).isoformat(),
        "route": "Esri World Imagery Wayback public metadata and tile endpoints",
        "catalog_url": settings["wayback_catalog_url"], "catalog_sha256": digest(raw),
        "scope": "Site-center access probes only. Whole-footprint coverage, image clarity, legal permission for label redistribution, and temporal eligibility require owner review. No AI labels or verification.",
        "date_rule": "SRC_DATE/SRC_DATE2 describe acquisition; the Wayback item title describes archive publication. Do not substitute release dates for acquisition dates.",
        "sites": {}}
    for site in sites:
        name = site["properties"]["id"]
        lon, lat = site["geometry"]["coordinates"]
        checks = []
        for period, (release, item) in [("early", early), ("recent", recent)]:
            query = {"f": "json", "geometry": f"{lon},{lat}",
                "geometryType": "esriGeometryPoint", "inSR": "4326",
                "spatialRel": "esriSpatialRelIntersects", "outFields": "*", "returnGeometry": "false"}
            url = (item["metadataLayerUrl"] + f'/{settings["reference_metadata_layer"]}/query?'
                   + urllib.parse.urlencode(query))
            observation = {"period_probe": period, "release_date": release_date(item),
                "wayback_item": item, "query_url": url,
                "viewer_url": f"https://livingatlas.arcgis.com/wayback/#active={release}&mapCenter={lon}%2C{lat}%2C{settings['reference_zoom']}"}
            try:
                body, _ = get(url)
                reply = json.loads(body)
                observation["metadata_response"] = reply
                if reply.get("error") or reply.get("exceededTransferLimit"):
                    raise ValueError("Metadata query failed or was truncated")
                attrs = [f["attributes"] for f in reply.get("features", [])]
                dated = [a for a in attrs if a.get("SRC_DATE2") and a.get("SRC_DATE")]
                if not dated:
                    raise ValueError("No acquisition-dated metadata at the site center")
                observation["acquisition_dates_utc"] = sorted({
                    datetime.fromtimestamp(a["SRC_DATE2"] / 1000, timezone.utc).date().isoformat()
                    for a in dated})
                z = settings["reference_zoom"]
                col = math.floor((lon + 180) / 360 * 2**z)
                row = math.floor((1 - math.asinh(math.tan(math.radians(lat))) / math.pi) / 2 * 2**z)
                tile_url = item["itemURL"].format(level=z, row=row, col=col)
                tile, headers = get(tile_url)
                if not (tile.startswith(b"\xff\xd8\xff") or tile.startswith(b"\x89PNG\r\n\x1a\n")):
                    raise ValueError("Tile endpoint did not return JPEG/PNG bytes")
                observation["tile_delivery"] = {"url": tile_url, "sha256": digest(tile),
                    "content_type": next((v for k, v in headers.items() if k.lower() == "content-type"), None),
                    "bytes": len(tile), "retained_or_rendered": False}
                observation["status"] = "DATED_METADATA_AND_TILE_REACHABLE"
            except Exception as exc:
                observation["status"] = "INCOMPLETE"
                observation["blocker"] = f"{type(exc).__name__}: {exc}"
            checks.append(observation)
        record["sites"][name] = checks
    record["status"] = ("ACCESS_CONFIRMED_AT_PROBED_CENTERS"
        if all(c["status"] == "DATED_METADATA_AND_TILE_REACHABLE"
               for checks in record["sites"].values() for c in checks) else "PARTIAL_ACCESS")
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("xb") as handle:
        handle.write(encoded(record))
    print(record["status"] + "; imagery was not rendered and no sites were judged.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    check(parser.parse_args().output)
