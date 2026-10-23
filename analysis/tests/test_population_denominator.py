"""Synthetic 4x4 raster checks nodata exclusion and the centre, full-cell, edge and fractional clips."""
import importlib.util
from pathlib import Path

import numpy as np
import pytest

rasterio = pytest.importorskip('rasterio')
pytest.importorskip('exactextract')
from rasterio.transform import from_origin
from shapely.geometry import box, mapping

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('denominator', ROOT / 'tools/check_population_denominator.py')
tool = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tool)


def test_rule_and_clips_on_synthetic_raster(tmp_path):
    data = np.arange(1, 17, dtype='float32').reshape(4, 4)
    data[0, 0] = data[1, 2] = -99999
    raster = tmp_path / 'pop.tif'
    with rasterio.open(raster, 'w', driver='GTiff', width=4, height=4, count=1, dtype='float32',
                       nodata=-99999, crs='EPSG:4326', transform=from_origin(0, 4, 1, 1)) as dst:
        dst.write(data, 1)
    geom = box(-0.5, -0.5, 2.25, 4.5)  # columns 0 and 1 wholly, one quarter of column 2
    features = [{'type': 'Feature', 'properties': {}, 'geometry': mapping(geom)}]
    with rasterio.open(raster) as src:
        s = tool.summarize(src, geom, rows=3)
    valid = data != -99999
    cols01, col2 = float(data[:, :2][valid[:, :2]].sum()), float(data[:, 2][valid[:, 2]].sum())
    assert s['all']['valid_cells'] == 14 and s['all']['population'] == float(data[valid].sum())
    assert s['all']['nodata_cells'] == 2 and s['all']['min_valid_value'] == 2
    assert s['center_inside'] == {'valid_cells': 7, 'population': cols01}
    assert s['fully_inside'] == {'valid_cells': 7, 'population': cols01}
    assert s['edge'] == {'valid_cells': 3, 'population': col2}
    assert s['center_outside']['valid_cells'] == 7
    frac = tool.fractional(raster, features)
    assert frac['sum'] == pytest.approx(cols01 + 0.25 * col2) and frac['count'] == pytest.approx(7.75)
    pair = tool.compare(31.25e6)[2]
    assert pair['computed_within_interval'] and abs(pair['computed_minus_implied']) < 1e4
