"""Check the captured EE grid measurements against independent geometry.

Run: python tools/check_grid_runtime.py
This checks recorded observations, not a live Earth Engine execution.
"""
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
record = json.loads((ROOT / "results/earth_engine_runtime_2026-09-29.json").read_text())
rows = record["corrected_probe"]["observations"]
assert len(rows) == 8 and len({r["label"] for r in rows}) == 8
assert all(r["status"] == "OK" for r in rows)
values = {r["label"]: r["value"] for r in rows}
checks = {}


def close(name, observed, expected, tolerance):
    relative_error = abs(observed - expected) / abs(expected)
    checks[name] = {"expected": expected, "relative_error": relative_error,
                    "tolerance": tolerance, "passed": relative_error <= tolerance}


# WGS84 radii of curvature; independent of EE's projection/area operations.
a = 6378137.0
f = 1 / 298.257223563
e2 = f * (2 - f)
for label in ("dev-01-braided-lat", "equator-control"):
    v = values[label + ":geometry"]
    lon, lat = map(math.radians, v["center_lonlat"])
    den = 1 - e2 * math.sin(lat) ** 2
    n = a / math.sqrt(den)
    m = a * (1 - e2) / den ** 1.5
    east = n * math.cos(lat) * (math.radians(v["east_lonlat"][0]) - lon)
    north = m * (math.radians(v["north_lonlat"][1]) - lat)
    close(label + ":east", v["east_distance_m"], east, 0.001)
    close(label + ":north", v["north_distance_m"], north, 0.001)
    close(label + ":pixel_area", v["pixel_area_m2"], east * north, 0.001)
    x0, y0, x1, y1 = v["footprint_projected_bounds"]
    phi0 = math.atan(math.sinh(y0 / a))
    phi1 = math.atan(math.sinh(y1 / a))
    # Spherical expectation uses the Mercator radius, as in the prepared bounds.
    spherical_area = a * (x1 - x0) * (math.sin(phi1) - math.sin(phi0))
    close(label + ":geometry_area", v["footprint_area_m2"], spherical_area, 0.01)
    close(label + ":raster_area", v["raster_footprint"]["area"], spherical_area, 0.01)
    assert v["raster_footprint"]["cells"] == 50
    assert v["crs"] == "EPSG:3857" and v["nominal_scale_m"] == 10
    assert 'PARAMETER["elt_0_0", 10.0]' in v["transform"]
    assert 'PARAMETER["elt_1_1", -10.0]' in v["transform"]
    radii = [math.hypot(x, y) * 10 for x in range(-80, 81)
             for y in range(-80, 81) if 20 ** 2 < x * x + y * y <= 80 ** 2]
    ring = values[label + ":ring"]
    inner = sum(x * x + y * y <= 20 ** 2
                for x in range(-20, 21) for y in range(-20, 21))
    assert ring["counts"] == {"inner": inner, "outer": inner + len(radii), "ring": len(radii)}
    close(label + ":ring_min", ring["radial_extent"]["radius_projected_m_min"], min(radii), 1e-6)
    close(label + ":ring_max", ring["radial_extent"]["radius_projected_m_max"], max(radii), 1e-6)

print(json.dumps(checks, indent=2))
assert all(c["passed"] for c in checks.values()), "Captured measurements exceed prepared bounds"
