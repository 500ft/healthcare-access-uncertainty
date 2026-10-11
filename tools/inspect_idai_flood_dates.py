#!/usr/bin/env python3
"""Inspect sensor dates in the already acquired DEVELOPMENT UNOSAT archive."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import struct
import zipfile

ROOT = Path(__file__).resolve().parents[1]


def sensor_dates(data):
    count, header, width = struct.unpack_from('<IHH', data, 4)
    offset = 1  # deletion flag starts every dBASE record
    date_column = None
    for start in range(32, header - 1, 32):
        field = data[start:start + 32]
        name = field[:11].split(b'\0')[0].decode('ascii')
        if name == 'Sensor_Dat':
            if field[11:12] != b'D' or field[16] != 8:
                raise ValueError('Unexpected sensor date field')
            date_column = slice(offset, offset + 8)
        offset += field[16]
    if date_column is None or offset != width or len(data) < header + count * width:
        raise ValueError('Missing date field or malformed dBASE layout')
    dates = Counter()
    deleted = 0
    for start in range(header, header + count * width, width):
        row = data[start:start + width]
        if row[:1] == b'*':
            deleted += 1
        elif row[:1] == b' ':
            dates[row[date_column].decode('ascii').strip() or 'missing'] += 1
        else:
            raise ValueError('Unexpected deletion flag')
    return dict(sorted(dates.items())), deleted


def inspect(directory):
    manifest = json.loads((ROOT / 'evidence/idai-development-inputs/manifest.json').read_text())
    asset = next(a for a in manifest['assets'] if a['role'] == 'unosat_development_flood')
    archive = directory / asset['filename']
    with archive.open('rb') as stream:
        if hashlib.file_digest(stream, 'sha256').hexdigest() != asset['sha256']:
            raise ValueError('Archive differs from acquired source')
    result = {'source_asset': 'manifest.json#/assets/3',
              'selection': 'Upstream Water.+.shp$ filename rule; inspection only, no union or exclusion',
              'layers': []}
    with zipfile.ZipFile(archive) as z:
        for name in sorted(z.namelist()):
            if not re.search(r'Water.+.shp$', name):
                continue
            dbf = str(Path(name).with_suffix('.dbf'))
            dates, deleted = sensor_dates(z.read(dbf))
            result['layers'].append({'dbf_member': dbf, 'sensor_dates_yyyymmdd': dates,
                                     'deleted_records': deleted})
    return result


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--input', required=True, type=Path, help='Existing external development-input directory')
    args = p.parse_args()
    print(json.dumps(inspect(args.input), indent=2))
