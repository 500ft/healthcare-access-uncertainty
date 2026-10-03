"""Prepare unrendered road baselines. See baseline/20261003/README.md.

No detector, scoring, imagery interpretation or site verification is performed.
"""
import argparse
import base64
import csv
from datetime import datetime, timezone
import hashlib
import io
from importlib.metadata import version
import json
from pathlib import Path
import ssl
import urllib.request
import zipfile

import certifi
import osmium
import pyproj
from pyproj import CRS, Geod, Proj, Transformer
import shapely
from shapely.geometry import LineString, box, mapping, shape
from shapely.ops import transform

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SETTINGS = ROOT / "baseline/20261003/settings.json"


def digest(data):
    return hashlib.sha256(data).hexdigest()


def encoded(value):
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode()


def get(url, data=None, method=None):
    request = urllib.request.Request(url, data=data, method=method, headers={
        "User-Agent": "500ft-road-baseline-preparation/1.0",
        "Content-Type": "application/x-www-form-urlencoded"})
    with urllib.request.urlopen(request, timeout=180,
            context=ssl.create_default_context(cafile=certifi.where())) as response:
        return response.read(), dict(response.headers)


def selected_sites(manifest, settings):
    sites = {f["properties"]["id"]: f for f in manifest["features"]}
    selected = [sites[name] for name in settings["site_order"]]
    if len(set(settings["site_order"])) != len(selected):
        raise ValueError("Duplicate site")
    if any(f["properties"]["stratum"] == "holdout" for f in selected):
        raise ValueError("Holdout access is forbidden")
    return selected


def footprint(site, settings):
    lon, lat = site["geometry"]["coordinates"]
    radius = site["properties"]["half_km"] * 1000
    geod = Geod(ellps="WGS84")
    step = settings["circle_azimuth_step_deg"]
    points = [geod.fwd(lon, lat, i * step, radius)[:2]
              for i in range(round(360 / step))]
    xs, ys = zip(*points)
    return box(min(xs), min(ys), max(xs), max(ys))


def project(geometry, transformer, settings):
    # Densify before projection so long source segments and bbox edges remain curved.
    return transform(transformer.transform,
                     geometry.segmentize(settings["geographic_edge_step_deg"]))


def line_parts(geometry):
    if geometry.is_empty:
        return []
    if geometry.geom_type == "LineString":
        return [geometry] if geometry.length > 0 else []
    if hasattr(geometry, "geoms"):
        return [part for g in geometry.geoms for part in line_parts(g)]
    return []


def clip_rows(identifier, geometry, properties, projected_aoi, transformer, settings):
    clipped = project(geometry, transformer, settings).intersection(projected_aoi)
    return [{"source_id": identifier, "part": i, "geometry_wkt": g.wkt,
             "properties": json.dumps(properties, sort_keys=True)}
            for i, g in enumerate(line_parts(clipped))]


def csv_bytes(rows):
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream,
        fieldnames=["source_id", "part", "geometry_wkt", "properties"])
    writer.writeheader()
    writer.writerows(rows)
    return stream.getvalue().encode()


def validate_osm(reply, as_of):
    if reply["as_of"] != as_of:
        raise ValueError("Snapshot timestamp does not match settings")
    for way in reply["elements"]:
        if not way.get("timestamp") or way["timestamp"] > as_of:
            raise ValueError("Missing timestamp or way dated after snapshot")
        if len(way["geometry"]) != len(way["nodes"]) or len(way["nodes"]) < 2:
            raise ValueError("Incomplete way geometry")


def extract_osm(pbf, areas, settings):
    """Stream the country once; copy only ways intersecting the selected sites."""
    with osmium.io.Reader(str(pbf)) as reader:
        header = reader.header()
        timestamp = header.get("osmosis_replication_timestamp")
        if timestamp != settings["osm_as_of"]:
            raise ValueError("PBF header timestamp does not match settings")
        source = {"as_of": timestamp, "generator": header.get("generator"),
                  "replication_sequence": header.get("osmosis_replication_sequence_number")}
    replies = {name: {"as_of": timestamp, "elements": []} for name in areas}

    class Roads(osmium.SimpleHandler):
        def way(self, way):
            tags = dict(way.tags)
            if "highway" not in tags or tags.get("area") == "yes":
                return
            if len(way.nodes) < 2 or any(not n.location.valid() for n in way.nodes):
                raise ValueError("Snapshot contains a highway with missing geometry")
            coordinates = [(n.lon, n.lat) for n in way.nodes]
            geometry = LineString(coordinates)
            for name, area in areas.items():
                if geometry.intersects(area):
                    replies[name]["elements"].append({"id": way.id, "version": way.version,
                        "timestamp": way.timestamp.isoformat().replace("+00:00", "Z"),
                        "nodes": [n.ref for n in way.nodes], "geometry": coordinates, "tags": tags})

    Roads().apply_file(str(pbf), locations=True)
    for reply in replies.values():
        validate_osm(reply, timestamp)
    return replies, source


def write_zip(path, contents):
    # Stable metadata permits byte-identical offline rebuilds.
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for name, data in sorted(contents.items()):
            info = zipfile.ZipInfo(name, date_time=(2026, 10, 3, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            archive.writestr(info, data)


def prepare(archive_path, output, settings_path=DEFAULT_SETTINGS, replay=None, osm_pbf=None):
    settings = json.loads(settings_path.read_text())
    manifest_path = ROOT / "config/sites.geojson"
    sites = selected_sites(json.loads(manifest_path.read_text()), settings)
    output.mkdir(parents=True, exist_ok=True)
    if (output / "candidates-unopened.zip").exists():
        raise FileExistsError("Use a new output directory; captured packets are not overwritten")
    crs = CRS.from_user_input(settings["metric_crs"])
    transformer = Transformer.from_crs("EPSG:4326", crs, always_xy=True)
    proj = Proj(crs)
    areas = {f["properties"]["id"]: footprint(f, settings) for f in sites}
    projected = {k: project(g, transformer, settings) for k, g in areas.items()}
    # Numerical checks of the chosen projection, without inspecting baseline geometry.
    factors = []
    for area in areas.values():
        w, s, e, n = area.bounds
        for i in range(5):
            for j in range(5):
                f = proj.get_factors(w + (e-w)*i/4, s + (n-s)*j/4)
                factors.extend([f.meridional_scale, f.parallel_scale])
    error = max(abs(k-1) for k in factors)
    if error > settings["maximum_scale_error"]:
        raise ValueError("Projection exceeds prospective scale-error bound")
    content = {"metric-crs.wkt": crs.to_wkt().encode(),
               "ATTRIBUTION.md": (DEFAULT_SETTINGS.parent / "ATTRIBUTION.md").read_bytes()}
    inventory = {}
    ms_rows = {key: [] for key in areas}
    # Stream the owner-supplied archive in place; do not extract a whole region.
    with zipfile.ZipFile(archive_path) as archive:
        with archive.open(settings["microsoft_archive_member"]) as source:
            for line_number, line in enumerate(source, 1):
                country, feature_text = line.decode().split("\t", 1)
                if country != "MNG":
                    continue
                feature = json.loads(feature_text)
                geom = shape(feature["geometry"])
                if geom.geom_type not in ("LineString", "MultiLineString"):
                    raise ValueError("Microsoft source contains a non-line feature")
                for name, area in areas.items():
                    if geom.intersects(area):
                        ms_rows[name].extend(clip_rows(f"Eastern_Asia.tsv:{line_number}",
                            geom, feature["properties"], projected[name], transformer, settings))
    cached = zipfile.ZipFile(replay) if replay else None
    try:
        archive_bytes = archive_path.read_bytes()
        if cached:
            source_head = json.loads(cached.read("microsoft-source.json"))
        else:
            _, headers = get(settings["microsoft_catalog_archive_url"], method="HEAD")
            source_head = {"url": settings["microsoft_catalog_archive_url"],
                "retrieved_utc": datetime.now(timezone.utc).isoformat(),
                "headers": {k.lower(): v for k, v in headers.items()}}
        published_md5 = source_head["headers"].get("content-md5")
        if not published_md5 or base64.b64encode(hashlib.md5(archive_bytes).digest()).decode() != published_md5:
            raise ValueError("Local Microsoft archive does not match the published Content-MD5")
        content["microsoft-source.json"] = encoded(source_head)
        if cached:
            osm_source = json.loads(cached.read("osm-source.json"))
            if cached.read("osm-selection.txt").decode() != settings["osm_selection"]:
                raise ValueError("Replay selection differs from settings")
        else:
            if osm_pbf is None:
                raise ValueError("Supply --osm-pbf or --replay")
            checksum, _ = get(settings["osm_checksum_url"])
            pbf_bytes = osm_pbf.read_bytes()
            if hashlib.md5(pbf_bytes).hexdigest() != checksum.decode().split()[0]:
                raise ValueError("OSM snapshot does not match published MD5")
            replies, osm_source = extract_osm(osm_pbf, areas, settings)
            osm_source.update({"url": settings["osm_snapshot_url"],
                "checksum_url": settings["osm_checksum_url"], "published_md5": checksum.decode().strip(),
                "sha256": digest(pbf_bytes), "bytes": len(pbf_bytes),
                "retrieved_utc": datetime.now(timezone.utc).isoformat(),
                "extraction": "pyosmium full-way geometry; no node-in-bbox restriction",
                "source_privacy": "Geofabrik public extracts omit contributor usernames, user IDs and changeset IDs."})
        content["osm-source.json"] = encoded(osm_source)
        content["osm-selection.txt"] = settings["osm_selection"].encode()
        for site in sites:
            name = site["properties"]["id"]
            raw_path = f"{name}/osm-raw.json"
            raw = cached.read(raw_path) if cached else encoded(replies[name])
            reply = json.loads(raw)
            validate_osm(reply, settings["osm_as_of"])
            content[raw_path] = raw
            rows = []
            for way in reply["elements"]:
                if len(way["geometry"]) >= 2:
                    geom = LineString(way["geometry"])
                    rows.extend(clip_rows(f"way/{way['id']}@{way['version']}", geom,
                        {"tags": way.get("tags", {}), "timestamp": way["timestamp"]},
                        projected[name], transformer, settings))
            content[f"{name}/microsoft.csv"] = csv_bytes(ms_rows[name])
            content[f"{name}/osm.csv"] = csv_bytes(rows)
            inventory[name] = {"microsoft_clipped_parts": len(ms_rows[name]),
                               "osm_clipped_parts": len(rows)}
    finally:
        if cached:
            cached.close()
    content["inventory.json"] = encoded({"counts_are_baseline_inventory_only": True,
                                          "sites": inventory})
    write_zip(output / "candidates-unopened.zip", content)
    locations = {"type": "FeatureCollection", "features": []}
    for site in sites:
        name = site["properties"]["id"]
        locations["features"].append({"type": "Feature", "geometry": mapping(areas[name]),
            "properties": {"site_id": name, "center_lonlat": site["geometry"]["coordinates"],
                           "purpose": "Reference labeling boundary; no candidate overlay"}})
    (output / "locations.json").write_bytes(encoded(locations))
    provenance = {"status": "BASELINES_PREPARED_UNRENDERED", "source_manifest_sha256": digest(manifest_path.read_bytes()),
        "settings_sha256": digest(settings_path.read_bytes()),
        "preparation_script_sha256": digest(Path(__file__).read_bytes()),
        "microsoft": {"input_filename": archive_path.name,
            "sha256": digest(archive_bytes), "member": settings["microsoft_archive_member"],
            "catalog_archive_url": settings["microsoft_catalog_archive_url"],
            "published_content_md5_match": True,
            "source_http_metadata": "microsoft-source.json inside candidates-unopened.zip",
            "catalog": settings["microsoft_catalog"], "license": settings["license"]},
        "osm": {"as_of": settings["osm_as_of"], "snapshot_url": settings["osm_snapshot_url"],
            "source_sha256": osm_source["sha256"], "published_md5_match": True,
            "source_metadata_and_selection": "osm-source.json and osm-selection.txt inside candidates-unopened.zip",
            "raw_subsets": "Per-site osm-raw.json inside candidates-unopened.zip", "license": settings["license"]},
        "projection": {"definition": settings["metric_crs"], "sampled_max_scale_error": error,
            "check": "Regular grid over each baseline footprint; meridional and parallel scale factors"},
        "versions": {"osmium": version("osmium"), "shapely": shapely.__version__, "pyproj": pyproj.__version__, "PROJ": pyproj.proj_version_str},
        "files": {p.name: digest(p.read_bytes()) for p in
                  [output / "candidates-unopened.zip", output / "locations.json"]}}
    (output / "provenance.json").write_bytes(encoded(provenance))
    print("Baseline packet prepared. Candidate layers remain unrendered; no scores computed.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--replay", type=Path, help="Reuse captured OSM subsets without network access")
    source.add_argument("--osm-pbf", type=Path, help="Dated Geofabrik snapshot specified in settings")
    args = parser.parse_args()
    prepare(args.archive, args.output, replay=args.replay, osm_pbf=args.osm_pbf)
