"""One offline check of immutable acquisition against actual manifest structure."""
import hashlib
import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('fetch_idai', ROOT / 'tools/fetch_idai_development.py')
fetch = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fetch)


def test_acquisition_rejects_changed_bytes_and_preserves_existing_files(tmp_path):
    # file: transport exercises the same streaming and verification path offline.
    source = tmp_path / 'source'
    source.write_bytes(b'original source bytes')
    output = tmp_path / 'output'
    output.mkdir()
    asset = dict(filename='input', url=source.as_uri(), bytes=source.stat().st_size,
                 sha256=hashlib.sha256(source.read_bytes()).hexdigest())
    fetch.acquire(asset, output)
    fetch.acquire(asset, output, check_only=True)
    source.write_bytes(b'changed upstream bytes')
    fetch.acquire(asset, output)  # existing verified bytes are reused
    assert (output / 'input').read_bytes() == b'original source bytes'
    (output / 'input').write_bytes(b'existing unrelated bytes')
    with pytest.raises(ValueError, match='Content mismatch'):
        fetch.acquire(asset, output)
    assert (output / 'input').read_bytes() == b'existing unrelated bytes'
    with pytest.raises(ValueError, match='Content mismatch'):
        fetch.acquire(dict(asset, filename='new-input'), output)
    assert not (output / 'new-input').exists()
    assert not list(output.glob('.idai-*'))
    manifest = json.loads(fetch.MANIFEST.read_text())
    for item in manifest['assets']:
        assert Path(item['filename']).name == item['filename']
        assert item['url'].startswith('https://')
        assert len(item['sha256']) == 64 and item['bytes'] > 0
