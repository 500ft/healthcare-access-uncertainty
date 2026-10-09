#!/usr/bin/env python3
"""Fetch only the acquired development assets; reject changed bytes, never extract."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import tempfile
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / 'evidence/idai-development-inputs/manifest.json'


def verify(path, asset):
    with path.open('rb') as stream:
        digest = hashlib.file_digest(stream, 'sha256').hexdigest()
    if path.stat().st_size != asset['bytes'] or digest != asset['sha256']:
        raise ValueError(f"Content mismatch: {asset['filename']}")


def acquire(asset, directory, check_only=False):
    target = directory / asset['filename']
    if target.exists() or check_only:
        verify(target, asset)
        return
    # Temporary file and hard link publish verified bytes without replacing a file.
    with tempfile.NamedTemporaryFile(dir=directory, prefix='.idai-') as stream:
        request = urllib.request.Request(asset['url'], headers={'User-Agent': '500ft-idai-inputs/1.0'})
        with urllib.request.urlopen(request, timeout=120) as response:
            shutil.copyfileobj(response, stream)
        stream.flush()
        verify(Path(stream.name), asset)
        os.link(stream.name, target)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, type=Path, help='Directory outside the checkout')
    parser.add_argument('--check-only', action='store_true', help='Verify local bytes without network access')
    args = parser.parse_args()
    directory = args.output.expanduser().resolve()
    if directory == ROOT or ROOT in directory.parents:
        parser.error('Keep original inputs outside the checkout')
    if not args.check_only:
        directory.mkdir(parents=True, exist_ok=True)
    manifest = json.loads(MANIFEST.read_text())
    for asset in manifest['assets']:
        acquire(asset, directory, args.check_only)
        print(f"Verified {asset['filename']}")


if __name__ == '__main__':
    main()
