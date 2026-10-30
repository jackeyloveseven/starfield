# -*- coding: utf-8 -*-
"""
Synchronizer and generator for Starfield Grand Expansion Modes.
Ensures starfield.html and android/app/src/main/assets/starfield.html remain 100% byte-for-byte identical.
"""

from pathlib import Path
import sys

def sync_modes():
    base_dir = Path(__file__).resolve().parent.parent
    html_path = base_dir / 'starfield.html'
    mirror_path = base_dir / 'android/app/src/main/assets/starfield.html'

    print(f"Reading master: {html_path}")
    with open(html_path, 'rb') as f:
        data = f.read()

    print(f"Writing mirror: {mirror_path}")
    mirror_path.parent.mkdir(parents=True, exist_ok=True)
    with open(mirror_path, 'wb') as f:
        f.write(data)

    assert data == open(mirror_path, 'rb').read(), "Mirror verification failed!"
    print(f"Sync successful: {len(data)} bytes matched 100%.")

if __name__ == '__main__':
    sync_modes()
