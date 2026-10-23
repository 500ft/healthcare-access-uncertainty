#!/usr/bin/env python3
"""Valid-cell support and totals of the pinned WorldPop raster under the pinned author rule.

The pinned helper (src/2_healthcare_access/vector_analysis/1.4_population_estimates.R
at 69bbe253b4dcd926a630b557251b5f65688301d5) sets the denominator with
``cellStats(population, 'sum')``: every valid cell of the national raster, no
boundary clip. Isochrone numerators use ``exact_extract(..., 'sum')``: cell value
times the covered fraction. This tool reports the denominator under that rule and
the boundary-clipped totals as a sensitivity. It needs rasterio and exactextract.
"""
import argparse
import datetime
import hashlib
import json
import math
from pathlib import Path
import platform
import sys
import time

import numpy as np
import rasterio
from rasterio.features import geometry_mask, rasterize
from rasterio.windows import Window
from shapely.geometry import shape
from exactextract import exact_extract

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / 'evidence/idai-development-inputs/manifest.json'
RULE = {
    'source': 'https://raw.githubusercontent.com/GIScience/healthcare-access-idai/69bbe253b4dcd926a630b557251b5f65688301d5/src/2_healthcare_access/vector_analysis/1.4_population_estimates.R',
    'sha256': '25721923e81323382a2378306023e7c2dddca7717a96d22be13e400c42f3c720',
    'denominator': "total_pop <- cellStats(population, 'sum'): sum of every non-NA raster cell; the boundary is not applied",
    'numerator': "exact_extract(population, differenced_isochrones$geom[i], 'sum'): cell value times covered fraction per isochrone polygon",
}
# Printed in the paper's Results (PMC9559768); no explicit national total is printed.
PRINTED = [
    {'quantity': 'beyond 6 h walking, raster-based', 'million': 3.01, 'percent': 9.61},
    {'quantity': 'beyond 6 h walking, network-based', 'million': 14.76, 'percent': 47.23},
    {'quantity': 'beyond 1 h driving, raster-based', 'million': 4.52, 'percent': 14.46},
    {'quantity': 'beyond 1 h driving, network-based', 'million': 14.15, 'percent': 45.29},
]


def sha256(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def summarize(src, geom, rows=512):
    """Valid-cell counts and sums: whole raster, centre inside, fully inside, edge, centre outside."""
    nodata = src.nodata
    inside = geometry_mask([geom], out_shape=src.shape, transform=src.transform, invert=True)
    edge = rasterize([(geom.boundary, 1)], out_shape=src.shape, transform=src.transform,
                     all_touched=True, dtype='uint8').astype(bool)
    keys = ('all', 'center_inside', 'fully_inside', 'edge', 'center_outside')
    counts, sums = dict.fromkeys(keys, 0), {k: [] for k in keys}
    extra = dict(nodata_cells=0, nan_cells=0, negative_valid_cells=0, zero_valid_cells=0)
    low, high, running = math.inf, -math.inf, 0.0
    for row in range(0, src.height, rows):
        h = min(rows, src.height - row)
        data = src.read(1, window=Window(0, row, src.width, h)).astype(np.float64)
        valid = (data != nodata) & np.isfinite(data)
        extra['nodata_cells'] += int((data == nodata).sum())
        extra['nan_cells'] += int(np.isnan(data).sum())
        extra['negative_valid_cells'] += int((valid & (data < 0)).sum())
        extra['zero_valid_cells'] += int((valid & (data == 0)).sum())
        if valid.any():
            low, high = min(low, float(data[valid].min())), max(high, float(data[valid].max()))
        inner, rim = inside[row:row + h], edge[row:row + h]
        selections = {'all': valid, 'center_inside': valid & inner, 'fully_inside': valid & inner & ~rim,
                      'edge': valid & rim, 'center_outside': valid & ~inner}
        for key, sel in selections.items():
            counts[key] += int(sel.sum())
            sums[key].append(float(data[sel].sum()))
        running += float(data[valid].sum())
    result = {k: {'valid_cells': counts[k], 'population': math.fsum(sums[k])} for k in keys}
    result['all'].update(extra, min_valid_value=low, max_valid_value=high, float64_running_sum=running)
    return result


def fractional(raster_path, features):
    """exactextract sum and coverage-weighted count, the same library the pinned R helper calls."""
    result = exact_extract(str(raster_path), list(features), ['sum', 'count'])
    assert len(result) == 1
    return {k: float(v) for k, v in result[0]['properties'].items()}


def compare(total, clipped=None):
    """Consistency of the computed denominators with each printed count/percent pair."""
    rows = []
    for item in PRINTED:
        count, pct = item['million'] * 1e6, item['percent']
        implied = count / (pct / 100)
        # Round-half-to-nearest at the printed decimals gives these intervals.
        interval = [(count - 5e3) / ((pct + 5e-3) / 100), (count + 5e3) / ((pct - 5e-3) / 100)]
        row = {**item, 'implied_country_population': implied,
               'implied_interval_at_printed_precision': interval,
               'computed_minus_implied': total - implied,
               'computed_within_interval': interval[0] <= total <= interval[1]}
        if clipped is not None:
            row['exactextract_clip_within_interval'] = interval[0] <= clipped <= interval[1]
        rows.append(row)
    return rows


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', required=True, type=Path, help='Directory holding the fetched assets')
    parser.add_argument('--output', type=Path, default=MANIFEST.with_name('population-denominator.json'))
    args = parser.parse_args()
    started = time.perf_counter()
    assets = {a['role']: a for a in json.loads(MANIFEST.read_text())['assets']}
    paths, inputs = {}, {}
    for role in ('population', 'boundary_candidate'):
        path = args.input.expanduser().resolve() / assets[role]['filename']
        digest = sha256(path)
        if digest != assets[role]['sha256'] or path.stat().st_size != assets[role]['bytes']:
            raise SystemExit(f'Content mismatch: {path.name} {digest}')
        paths[role] = path
        inputs[role] = {'filename': path.name, 'bytes': path.stat().st_size, 'sha256': digest,
                        'matches_manifest': True}
    features = json.loads(paths['boundary_candidate'].read_text())['features']
    assert len(features) == 1
    geom = shape(features[0]['geometry'])
    with rasterio.open(paths['population']) as src:
        raster = {'crs': src.crs.to_string(), 'width': src.width, 'height': src.height,
                  'cells': src.width * src.height, 'dtype': src.dtypes[0], 'nodata': src.nodata,
                  'pixel_size_deg': list(src.res), 'bounds': list(src.bounds),
                  'block_shape': list(src.block_shapes[0]), 'area_or_point': src.tags().get('AREA_OR_POINT')}
        summary = summarize(src, geom)
    boundary = {'geometry_type': geom.geom_type, 'parts': len(getattr(geom, 'geoms', [geom])),
                'bounds': list(geom.bounds), 'valid': bool(geom.is_valid),
                'extends_beyond_raster': [geom.bounds[0] < raster['bounds'][0], geom.bounds[1] < raster['bounds'][1],
                                          geom.bounds[2] > raster['bounds'][2], geom.bounds[3] > raster['bounds'][3]]}
    frac = fractional(paths['population'], features)
    total = summary['all']['population']
    bracket = [summary['fully_inside']['population'],
               summary['fully_inside']['population'] + summary['edge']['population']]
    result = {
        'status': 'executed',
        'scope': 'Population support and denominator check on hash-pinned DEVELOPMENT inputs. No isochrone, facility, road or flood input was used; no baseline was reproduced.',
        'executed_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'commands': [
            'python3 tools/fetch_idai_development.py --output <external-dir>',
            'python3 tools/fetch_idai_development.py --output <external-dir> --check-only',
            'python3 tools/check_population_denominator.py --input <external-dir> --output evidence/idai-development-inputs/population-denominator.json',
        ],
        'inputs': inputs,
        'pinned_rule': RULE,
        'rule_applied': 'Denominator: every raster cell not equal to nodata and finite, summed with math.fsum over float64 strip sums. Clip variants: cell centre inside the boundary (rasterio geometry_mask), cells fully inside (centre inside and not touched by the boundary line), edge cells (touched by the boundary line, all_touched), and exactextract coverage-fraction sum.',
        'raster': raster,
        'boundary': boundary,
        'cells': summary,
        'denominator_cellstats_rule': total,
        'float64_running_sum_minus_fsum': summary['all']['float64_running_sum'] - total,
        'boundary_clip': {
            'exactextract': frac,
            'fractional_bracket_full_cells_to_edge_cells': bracket,
            'exactextract_within_bracket': bracket[0] <= frac['sum'] <= bracket[1],
            'center_inside_minus_exactextract': summary['center_inside']['population'] - frac['sum'],
            'cellstats_minus_exactextract': total - frac['sum'],
            'cellstats_minus_center_inside': total - summary['center_inside']['population'],
        },
        'printed_totals': {
            'explicit_national_total_in_paper_or_supplements': None,
            'note': 'The paper prints population counts with a percentage of the country population; the supplements print no population total. The implied denominators below are consistency checks only. No input version is selected by agreement with any printed value.',
            'pairs': compare(total, frac['sum']),
        },
        'environment': {'python': sys.version, 'platform': platform.platform(), 'numpy': np.__version__,
                        'rasterio': rasterio.__version__, 'gdal': rasterio.__gdal_version__,
                        'exactextract': __import__('exactextract').__version__},
        'elapsed_seconds': time.perf_counter() - started,
    }
    args.output.write_text(json.dumps(result, indent=2, allow_nan=False) + '\n')
    print(json.dumps({'denominator_cellstats_rule': total, 'valid_cells': summary['all']['valid_cells'],
                      'exactextract_sum': frac['sum'], 'elapsed_seconds': result['elapsed_seconds']}))


if __name__ == '__main__':
    main()
