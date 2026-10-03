"""Offline checks of clipping, historical snapshots and the captured packet."""
import csv
import io
import json
from pathlib import Path
import unittest
import tempfile
import osmium
import zipfile

from pyproj import Geod, Transformer
from shapely import from_wkt
from shapely.geometry import LineString, MultiLineString, box

from prepare_baselines import (ROOT, DEFAULT_SETTINGS, clip_rows, digest, footprint,
                               project, selected_sites, validate_osm, extract_osm)


class PreparationTests(unittest.TestCase):
    def setUp(self):
        self.settings = json.loads(DEFAULT_SETTINGS.read_text())

    def test_holdout_rejected_before_processing(self):
        manifest = json.loads((ROOT / "config/sites.geojson").read_text())
        self.settings["site_order"] = ["holdout-01"]
        with self.assertRaisesRegex(ValueError, "Holdout"):
            selected_sites(manifest, self.settings)

    def test_crossing_line_clipped_without_inside_endpoints(self):
        identity = Transformer.from_crs(4326, 4326, always_xy=True)
        line = LineString([(-2, 0), (2, 0)])
        rows = clip_rows("source", line, {}, box(-1, -1, 1, 1), identity, self.settings)
        self.assertEqual(len(rows), 1)
        clipped = from_wkt(rows[0]["geometry_wkt"])
        self.assertAlmostEqual(clipped.length, 2)
        self.assertEqual(clipped.bounds, (-1, 0, 1, 0))

    def test_multipart_kept_and_point_touch_discarded(self):
        identity = Transformer.from_crs(4326, 4326, always_xy=True)
        line = MultiLineString([[(-2, 0), (2, 0)], [(0, -2), (0, 2)], [(1, 1), (2, 2)]])
        rows = clip_rows("source", line, {}, box(-1, -1, 1, 1), identity, self.settings)
        self.assertAlmostEqual(sum(from_wkt(r["geometry_wkt"]).length for r in rows), 4)
        self.assertTrue(all(from_wkt(r["geometry_wkt"]).length > 0 for r in rows))

    def test_projection_axis_order_and_independent_geodesic_length(self):
        transformer = Transformer.from_crs(4326, self.settings["metric_crs"], always_xy=True)
        self.assertAlmostEqual(transformer.transform(103, 47)[0], 0, places=5)
        self.assertAlmostEqual(transformer.transform(103, 47)[1], 0, places=5)
        geod = Geod(ellps="WGS84")
        east = geod.fwd(103, 47, 90, 1000)[:2]
        line = project(LineString([(103, 47), east]), transformer, self.settings)
        self.assertLess(abs(line.length / 1000 - 1), self.settings["maximum_scale_error"])

    def test_osm_rejects_wrong_date_future_and_incomplete_geometry(self):
        good = {"as_of": self.settings["osm_as_of"], "elements": []}
        validate_osm(good, self.settings["osm_as_of"])
        for bad in [dict(good, as_of="2026-10-01T00:00:00Z"),
                    dict(good, elements=[{"timestamp": "2026-10-03T00:00:00Z"}]),
                    dict(good, elements=[{"timestamp": "2026-09-01T00:00:00Z",
                                         "nodes": [1, 2], "geometry": [[0, 0]]}])]:
            with self.assertRaises(ValueError):
                validate_osm(bad, self.settings["osm_as_of"])

    def test_pbf_selects_crossing_ways_without_inside_nodes(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "crossing.osm.pbf"
            header = osmium.io.Header()
            header.set("osmosis_replication_timestamp", self.settings["osm_as_of"])
            with osmium.SimpleWriter(str(path), header=header) as writer:
                writer.add_node(osmium.osm.mutable.Node(id=1, location=(-2, 0)))
                writer.add_node(osmium.osm.mutable.Node(id=2, location=(2, 0)))
                for identifier, tags in [(10, {"highway": "track"}),
                                         (11, {"highway": "pedestrian", "area": "yes"}),
                                         (12, {"waterway": "stream"})]:
                    writer.add_way(osmium.osm.mutable.Way(id=identifier, version=1,
                        timestamp="2026-09-01T00:00:00Z", nodes=[1, 2], tags=tags))
            replies, source = extract_osm(path, {"fixture": box(-1, -1, 1, 1)}, self.settings)
            self.assertEqual([way["id"] for way in replies["fixture"]["elements"]], [10])
            self.assertEqual(source["as_of"], self.settings["osm_as_of"])

    def test_reference_access_record_covers_only_selected_centers(self):
        record = json.loads((DEFAULT_SETTINGS.parent / "reference-access.json").read_text())
        self.assertEqual(set(record["sites"]), set(self.settings["site_order"]))
        self.assertEqual(record["status"], "ACCESS_CONFIRMED_AT_PROBED_CENTERS")
        for checks in record["sites"].values():
            self.assertEqual({c["period_probe"] for c in checks}, {"early", "recent"})
            for observation in checks:
                self.assertEqual(observation["status"], "DATED_METADATA_AND_TILE_REACHABLE")
                self.assertTrue(observation["acquisition_dates_utc"])
                self.assertTrue(all(d <= observation["release_date"] for d in observation["acquisition_dates_utc"]))
                self.assertFalse(observation["tile_delivery"]["retained_or_rendered"])

    def test_captured_packet_hashes_and_containment(self):
        folder = DEFAULT_SETTINGS.parent
        provenance = json.loads((folder / "provenance.json").read_text())
        self.assertEqual(provenance["source_manifest_sha256"], digest((ROOT / "config/sites.geojson").read_bytes()))
        self.assertEqual(provenance["settings_sha256"], digest(DEFAULT_SETTINGS.read_bytes()))
        self.assertEqual(provenance["preparation_script_sha256"], digest((ROOT / "tools/prepare_baselines.py").read_bytes()))
        for filename, expected in provenance["files"].items():
            self.assertEqual(digest((folder / filename).read_bytes()), expected)
        sites = selected_sites(json.loads((ROOT / "config/sites.geojson").read_text()), self.settings)
        transformer = Transformer.from_crs(4326, self.settings["metric_crs"], always_xy=True)
        with zipfile.ZipFile(folder / "candidates-unopened.zip") as archive:
            self.assertFalse(any("holdout" in name for name in archive.namelist()))
            inventory = json.loads(archive.read("inventory.json"))["sites"]
            self.assertEqual(set(inventory), set(self.settings["site_order"]))
            for site in sites:
                name = site["properties"]["id"]
                boundary = project(footprint(site, self.settings), transformer, self.settings)
                reply = json.loads(archive.read(f"{name}/osm-raw.json"))
                validate_osm(reply, self.settings["osm_as_of"])
                self.assertEqual(self.settings["osm_selection"], archive.read("osm-selection.txt").decode())
                for source in ("microsoft", "osm"):
                    rows = list(csv.DictReader(io.StringIO(archive.read(f"{name}/{source}.csv").decode())))
                    self.assertEqual(len(rows), inventory[name][source + "_clipped_parts"])
                    for row in rows:
                        line = from_wkt(row["geometry_wkt"])
                        self.assertEqual(line.geom_type, "LineString")
                        self.assertTrue(line.is_valid and line.length > 0)
                        self.assertTrue(boundary.buffer(1e-6).covers(line))


if __name__ == "__main__":
    unittest.main()
