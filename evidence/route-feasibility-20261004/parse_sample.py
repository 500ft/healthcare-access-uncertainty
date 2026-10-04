"""Parse the local development sample. Public output contains aggregate evidence only."""
import argparse
from collections import Counter, defaultdict
import csv
from datetime import datetime, timedelta, timezone
from decimal import Decimal
import hashlib
import io
import json
import math
from pathlib import Path
import statistics
import subprocess
import zipfile

ROOT = Path(__file__).resolve().parent


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_table(rar, member):
    data = subprocess.run(['bsdtar', '-xOf', '-', member], input=rar,
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True).stdout
    return list(csv.DictReader(io.StringIO(data.decode('utf-8-sig'))))


def distance(a, b, radius):
    lat1, lon1, lat2, lon2 = map(math.radians, [a[0], a[1], b[0], b[1]])
    h = math.sin((lat2-lat1)/2)**2 + math.cos(lat1)*math.cos(lat2)*math.sin((lon2-lon1)/2)**2
    return 2 * radius * math.asin(math.sqrt(min(1, max(0, h))))


def summary(values):
    return {'minimum': min(values), 'median': statistics.median(values), 'maximum': max(values)} if values else None


def durations(intervals, settings):
    """Gaps break low-motion runs; never subtract unobserved time as a stop."""
    stopped = run = gaps = 0.0
    for dt, metres in intervals + [(math.inf, 0)]:
        if 0 < dt <= settings['maximum_observed_interval_s'] and metres/dt < settings['stop_speed_m_s']:
            run += dt
        else:
            if run >= settings['minimum_stop_run_s']:
                stopped += run
            run = 0.0
        if math.isfinite(dt) and dt > settings['maximum_observed_interval_s']:
            gaps += dt
    return stopped, gaps


def analyze(rows, settings):
    points = []
    try:
        for row in sorted(rows, key=lambda p: int(p['id'])):
            lat, lon = float(row['latitude']), float(row['longitude'])
            if not (math.isfinite(lat) and math.isfinite(lon) and -90 <= lat <= 90 and -180 <= lon <= 180):
                return {'usable': False, 'reason': 'invalid_coordinates'}
            time = datetime.fromisoformat(row['time']).replace(tzinfo=timezone(timedelta(hours=-3))).astimezone(timezone.utc)
            points.append((lat, lon, time))
    except (ValueError, KeyError):
        return {'usable': False, 'reason': 'unparseable_point'}
    if len(points) < 2:
        return {'usable': False, 'reason': 'fewer_than_two_points'}
    dt = [(b[2]-a[2]).total_seconds() for a, b in zip(points, points[1:])]
    if any(value <= 0 for value in dt):
        return {'usable': False, 'reason': 'nonincreasing_time',
                'zero_intervals': sum(value == 0 for value in dt),
                'negative_intervals': sum(value < 0 for value in dt)}
    metres = [distance(a, b, settings['earth_radius_m']) for a, b in zip(points, points[1:])]
    intervals = list(zip(dt, metres))
    stopped, gap_time = durations(intervals, settings)
    observed = [(t, d) for t, d in intervals if t <= settings['maximum_observed_interval_s']]
    flags = sum(d/t*3.6 > settings['speed_consistency_flag_km_h'] for t, d in observed)
    elapsed = (points[-1][2] - points[0][2]).total_seconds()
    return {'usable': True, 'points': len(points), 'elapsed_s': elapsed,
            'chord_distance_m': sum(metres), 'observed_chord_distance_m': sum(d for t, d in observed),
            'gap_chord_distance_m': sum(d for t, d in intervals if t > settings['maximum_observed_interval_s']),
            'gap_intervals': len(dt)-len(observed), 'gap_time_s': gap_time,
            'estimated_low_motion_s': stopped, 'stop_adjusted_elapsed_s': elapsed-stopped,
            'speed_consistency_flags': flags, 'continuous_example_eligible': gap_time == 0 and flags == 0,
            'interval_seconds': dt, 'interval_distance_m': metres,
            'years': sorted({p[2].year for p in points})}


def run(output):
    settings = json.loads((ROOT/'protocol.json').read_text())
    sources = json.loads((ROOT/'sources.json').read_text())
    archive = ROOT/'raw/uci-gps-trajectories.zip'
    if sha(archive) != sources['files'][archive.name]['sha256']:
        raise ValueError('Source hash mismatch')
    with zipfile.ZipFile(archive) as zipped:
        rar = zipped.read('GPS Trajectory.rar')
    metadata = read_table(rar, 'GPS Trajectory/go_track_tracks.csv')
    all_points = read_table(rar, 'GPS Trajectory/go_track_trackspoints.csv')
    by_id = {row['id']: row for row in metadata}
    if len(by_id) != len(metadata):
        raise ValueError('Duplicate trip metadata IDs')
    known = settings['mode_codes']
    selected = []
    for code in known:
        selected += sorted([row for row in metadata if row['car_or_bus'] == code], key=lambda row: int(row['id']))[:settings['trips_per_declared_mode']]
    selected_ids = {row['id'] for row in selected}
    groups = defaultdict(list)
    for row in all_points:
        if row['track_id'] in selected_ids:
            groups[row['track_id']].append(row)
    details = []
    for trip in selected:
        result = analyze(groups[trip['id']], settings)
        result.update({'source_trip_id': trip['id'], 'declared_mode': known[trip['car_or_bus']]})
        details.append(result)
    usable = [r for r in details if r['usable']]
    continuous = [r for r in usable if r['continuous_example_eligible']]
    rejected = [r for r in details if not r['usable']]
    intervals = [value for trip in usable for value in trip['interval_seconds']]
    selected_points = [row for key in selected_ids for row in groups[key]]
    digits = [max(0, -Decimal(row[field]).as_tuple().exponent) for row in selected_points for field in ('latitude', 'longitude')]
    fractional_time_digits = [len(row['time'].split('.')[-1]) if '.' in row['time'] else 0 for row in selected_points]
    counts = {'source_metadata_trips': len(metadata), 'source_point_rows': len(all_points),
              'source_declared_modes': dict(Counter(known.get(r['car_or_bus'], 'ambiguous') for r in metadata)),
              'ambiguous_mode_trips_quarantined': sum(r['car_or_bus'] not in known for r in metadata),
              'development_trips_selected': len(selected), 'unselected_known_mode_trips': sum(r['car_or_bus'] in known for r in metadata)-len(selected),
              'selected_point_rows': len(selected_points), 'timestamped_trips_usable': len(usable),
              'timestamped_trips_excluded': len(rejected), 'exclusion_reasons': dict(Counter(r['reason'] for r in rejected)),
              'usable_by_declared_mode': dict(Counter(r['declared_mode'] for r in usable)),
              'continuous_timing_examples_eligible': len(continuous), 'trips_with_gaps': sum(r['gap_intervals'] > 0 for r in usable),
              'trips_with_speed_consistency_flags': sum(r['speed_consistency_flags'] > 0 for r in usable),
              'offroad_condition_validated_trips': 0,
              'selected_distinct_devices': len({r['id_android'] for r in selected}),
              'orphan_point_rows': sum(r['track_id'] not in by_id for r in all_points)}
    coarse_extent = [math.floor(min(float(r['longitude']) for r in selected_points)),
                     math.floor(min(float(r['latitude']) for r in selected_points)),
                     math.ceil(max(float(r['longitude']) for r in selected_points)),
                     math.ceil(max(float(r['latitude']) for r in selected_points))]
    public = {'result': 'Timestamped vehicle sample parsed; off-road route evaluation remains unsupported.',
              'counts': counts, 'split': 'Development only; no test set or final evaluation.',
              'source_sha256': sha(archive), 'parser_sha256': sha(Path(__file__)), 'protocol_sha256': sha(ROOT/'protocol.json'),
              'data_license': sources['data_license'], 'source_doi': sources['doi'], 'attribution': sources['attribution'],
              'observations': {'time_interval_s_pooled_usable': summary(intervals),
                'timestamp_fractional_digits': summary(fractional_time_digits), 'coordinate_decimal_digits': summary(digits),
                'elapsed_s_pooled_usable': summary([r['elapsed_s'] for r in usable]),
                'chord_distance_m_pooled_usable': summary([r['chord_distance_m'] for r in usable]),
                'gap_intervals': sum(r['gap_intervals'] for r in usable), 'gap_time_s': sum(r['gap_time_s'] for r in usable),
                'estimated_low_motion_s': sum(r['estimated_low_motion_s'] for r in usable),
                'speed_consistency_flags': sum(r['speed_consistency_flags'] for r in usable),
                'collection_years': sorted({year for r in usable for year in r['years']}),
                'coarse_extent_lonlat_whole_degrees': coarse_extent,
                'condition_metadata_codes': {key: dict(Counter(row[key] for row in selected)) for key in ('rating','rating_bus','rating_weather')}},
              'inventory': {'vehicle_type': 'Declared car/bus only; no make, drivetrain, load or off-road configuration.',
                'mode_method': 'Use declared car_or_bus labels. Speed is a consistency flag only; ambiguous labels quarantined.',
                'coordinates': 'Latitude/longitude columns; datum, horizontal accuracy and sensor calibration undocumented. Spherical distances assume WGS84-like degrees.',
                'elevation': 'Not supplied; elevation resolution and slope unknown.',
                'geographic_coverage': 'Only pooled extent rounded outward to whole degrees is public. No Mongolia or off-road representativeness established.',
                'conditions': 'Traffic/weather/bus-rating code frequencies are inventoried. Zero is undocumented and cannot establish clear weather or an observed condition. No surface, ford, bridge or passability observations.',
                'stops': 'Low-motion estimates under protocol, not labeled physical stops.',
                'privacy': 'No individual trip IDs, device IDs, endpoints, dates or coordinates in public output.'},
              'limits': ['Observed chord distance and low-motion time are provisional estimates at the supplied sampling resolution.',
                'Declared modes do not independently validate the vehicle; the sample does not establish route quality or passability.',
                'Repeated trips/devices require grouped future splits; there is no independent test result here.']}
    local_inventory = {'source_trip_ids': sorted(selected_ids, key=int),
                       'extent_lonlat': [min(float(r['longitude']) for r in selected_points), min(float(r['latitude']) for r in selected_points),
                                         max(float(r['longitude']) for r in selected_points), max(float(r['latitude']) for r in selected_points)],
                       'metadata_value_counts': {key: dict(Counter(row[key] for row in selected)) for key in ('rating','rating_bus','rating_weather')},
                       'trips': details}
    exercise = None
    if continuous:
        trip = continuous[0]
        reference_seconds = trip['chord_distance_m'] / (settings['exercise_baseline_speed_km_h']/3.6)
        exercise = {'source_trip_id': trip['source_trip_id'], 'instruction': 'Independently recompute adjacent-point great-circle distance, low-motion runs, elapsed minus low-motion time, and residual against the protocol constant-speed example. Do not publish source linkage or endpoints.',
                    'expected_distance_m': trip['chord_distance_m'], 'expected_stop_adjusted_elapsed_s': trip['stop_adjusted_elapsed_s'],
                    'illustrative_baseline_s': reference_seconds, 'residual_s': trip['stop_adjusted_elapsed_s']-reference_seconds,
                    'qualification': 'Development arithmetic exercise; no prediction accuracy or passability claim.'}
    output.mkdir(parents=True, exist_ok=False)
    for name, value in [('summary.json', public), ('private-trip-inventory.json', local_inventory), ('private-owner-exercise.json', exercise)]:
        (output/name).write_text(json.dumps(value, indent=2, sort_keys=True, allow_nan=False)+'\n')
    print(json.dumps(counts, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    run(parser.parse_args().output)
