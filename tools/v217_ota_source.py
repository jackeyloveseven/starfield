
# -*- coding: utf-8 -*-
"""v217 — 原生端 OTA 下载源改 GitHub Pages（raw 拉 34MB 实测 22.9s，Pages 2.4s）。"""
import json
import sys
from pathlib import Path

VER = Path(__file__).resolve().parent.parent / 'version.json'
meta = json.loads(VER.read_text(encoding='utf-8'))
old = meta.get('download_url', '')
new = 'https://jackeyloveseven.github.io/starfield/starfield.html'
assert old != new, 'already set'
meta['download_url'] = new
VER.write_text(json.dumps(meta, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
sys.stdout.reconfigure(encoding='utf-8')
print('download_url:')
print('  ' + old)
print('  -> ' + new)
