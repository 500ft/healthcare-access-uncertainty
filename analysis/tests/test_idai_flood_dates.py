"""Check date inspection before using it on the acquired development archive."""
import importlib.util
from pathlib import Path
import struct

import pytest

spec = importlib.util.spec_from_file_location(
    'flood_dates', Path(__file__).resolve().parents[2] / 'tools/inspect_idai_flood_dates.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def test_dates_exclude_deleted_records_and_keep_missing_explicit():
    header = bytearray(65)
    struct.pack_into('<IHH', header, 4, 3, 65, 9)
    header[32:43] = b'Sensor_Dat\0'
    header[43] = ord('D')
    header[48] = 8
    header[64] = 13
    data = bytes(header) + b' 20190407' + b'*20190326' + b'         '
    assert module.sensor_dates(data) == ({'20190407': 1, 'missing': 1}, 1)
    with pytest.raises(ValueError, match='malformed'):
        module.sensor_dates(data[:-1])
