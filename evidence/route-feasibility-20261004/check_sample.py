"""Small offline checks of the actual parser and its development result."""
import json
import math
from pathlib import Path
from parse_sample import analyze, distance, durations, sha

ROOT = Path(__file__).resolve().parent
s = json.loads((ROOT/'protocol.json').read_text())
assert distance((0, 0), (0, 0), s['earth_radius_m']) == 0
assert math.isclose(distance((0, 0), (0, 90), s['earth_radius_m']), math.pi*s['earth_radius_m']/2)
assert durations([(10, 0)]*3, s) == (30, 0)
assert durations([(10, 0)]*2+[(61, 0)]+[(10, 0)]*2, s) == (0, 61)
rows = [{'id': '1', 'latitude': '0', 'longitude': '0', 'time': '2014-01-01 00:00:00'},
        {'id': '2', 'latitude': '0', 'longitude': '0.001', 'time': '2014-01-01 00:00:10'}]
assert analyze(rows, s)['elapsed_s'] == 10
assert analyze(rows[:1], s)['reason'] == 'fewer_than_two_points'
bad = [dict(rows[0]), dict(rows[1], time='2013-12-31 23:59:59')]
assert analyze(bad, s)['reason'] == 'nonincreasing_time'
bad = [dict(rows[0]), dict(rows[1], latitude='nan')]
assert analyze(bad, s)['reason'] == 'invalid_coordinates'
result = json.loads((ROOT/'run-final/summary.json').read_text())
counts = result['counts']
assert counts['development_trips_selected'] == counts['timestamped_trips_usable'] + counts['timestamped_trips_excluded']
assert result['parser_sha256'] == sha(ROOT/'parse_sample.py')
assert result['protocol_sha256'] == sha(ROOT/'protocol.json')
private = json.loads((ROOT/'run-final/private-trip-inventory.json').read_text())
for trip in private['trips']:
    if trip['usable']:
        assert math.isclose(sum(trip['interval_seconds']), trip['elapsed_s'])
        assert math.isclose(trip['chord_distance_m'], trip['observed_chord_distance_m'] + trip['gap_chord_distance_m'])
        assert 0 <= trip['estimated_low_motion_s'] <= trip['elapsed_s']-trip['gap_time_s']
        assert math.isclose(trip['stop_adjusted_elapsed_s'], trip['elapsed_s']-trip['estimated_low_motion_s'])
        assert trip['continuous_example_eligible'] == (trip['gap_intervals'] == 0 and trip['speed_consistency_flags'] == 0)
text = json.dumps(result)
for forbidden in ['source_trip_id', 'id_android', 'latitude', 'longitude', 'start_time', 'end_time']:
    # Explanatory prose may name coordinates; keys must never expose individual linkage.
    assert f'"{forbidden}":' not in text
assert result['source_sha256'] == sha(ROOT/'raw/uci-gps-trajectories.zip')
print('PASS: geometry, time ordering, gaps, low-motion accounting, actual source/result hashes and public field checks.')
