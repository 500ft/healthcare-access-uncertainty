"""Acquire the tiny licensed source and documentation, without printing trace data."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parent
SOURCES = {
    'uci-gps-trajectories.zip': 'https://archive.ics.uci.edu/static/public/354/gps+trajectories.zip',
    'uci-dataset.html': 'https://archive.ics.uci.edu/dataset/354/gps+trajectories',
    'cc-by-4.0.html': 'https://creativecommons.org/licenses/by/4.0/legalcode.en',
    'uci-privacy.html': 'https://archive.ics.uci.edu/privacy',
    'osm-visibility.html': 'https://wiki.openstreetmap.org/w/index.php?title=Visibility_of_GPS_traces&oldid=3071050',
    'osm-privacy.html': 'https://osmfoundation.org/wiki/Privacy_Policy',
    'osm-gpx-license-minutes.html': 'https://osmfoundation.org/wiki/Licensing_Working_Group/Minutes/2024-10-07',
}

if __name__ == '__main__':
    raw = ROOT / 'raw'
    raw.mkdir(exist_ok=True)
    expected_path = ROOT / 'sources.json'
    expected = json.loads(expected_path.read_text()) if expected_path.exists() else None
    records = {}
    for name, url in SOURCES.items():
        path = raw / name
        if not path.exists():
            try:
                subprocess.run(['curl', '-L', '--fail', '--max-time', '60', '-sS', url, '-o', str(path)], check=True)
            except subprocess.CalledProcessError as error:
                if name in ('uci-gps-trajectories.zip', 'uci-dataset.html', 'cc-by-4.0.html'):
                    raise
                records[name] = {'url': url, 'curl_exit_status': error.returncode,
                                 'capture_status': 'Direct capture failed; consult the original pinned documentation record'}
                continue
        records[name] = {'url': url, 'retrieved_utc': datetime.fromtimestamp(path.stat().st_mtime, timezone.utc).isoformat(),
                         'sha256': hashlib.sha256(path.read_bytes()).hexdigest(), 'bytes': path.stat().st_size}
    if expected and records['uci-gps-trajectories.zip']['sha256'] != expected['files']['uci-gps-trajectories.zip']['sha256']:
        raise ValueError('Downloaded data differ from the pinned sample')
    record = {'dataset': 'GPS Trajectories, UCI dataset 354', 'doi': '10.24432/C54S5Z',
              'attribution': 'Cruz, M., Macedo, H., Barreto, R., & Guimares, A. (2015). GPS Trajectories. UCI Machine Learning Repository.',
              'data_license': 'CC-BY-4.0', 'data_license_url': SOURCES['cc-by-4.0.html'],
              'license_evidence': 'uci-dataset.html explicitly licenses this dataset, independently of parser software.',
              'software_license': 'MIT for the new local scripts; data retain CC BY 4.0.',
              'modifications': 'Deterministic development subset, timing and distance summaries; no raw trace redistribution.',
              'files': records}
    destination = ROOT / ('download-receipt.json' if expected else 'sources.json')
    with destination.open('x') as handle:
        json.dump(record, handle, indent=2); handle.write('\n')
    print('Source data and licence evidence pinned locally; no trace values displayed.')
