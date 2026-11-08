# -*- coding: utf-8 -*-
"""v233 - version tag fallback"""
import sys
from pathlib import Path

HTML = Path(__file__).resolve().parent.parent / 'starfield.html'
src = HTML.read_text(encoding='utf-8', newline='')

old = (
    "        vTag.textContent = 'v' + window.StarfieldNative.getAppVersion() + build + ota;\r\n"
    "      } else {\r\n"
    "        vTag.textContent = 'v1.19.1 (Build 153)';\r\n"
    "      }"
)
new = (
    "        vTag.textContent = 'v' + window.StarfieldNative.getAppVersion() + build + ota;\r\n"
    "      }\r\n"
    "      // No native bridge (browser / PWA): leave the markup value alone.\r\n"
    "      // This branch used to assign a hard-coded 'v1.19.1 (Build 153)', which\r\n"
    "      // overwrote the correct version on every OTA release."
)
assert src.count(old) == 1, 'count=%d' % src.count(old)
src = src.replace(old, new)

HTML.write_text(src, encoding='utf-8', newline='')
sys.stdout.reconfigure(encoding='utf-8')
print('version tag fallback fixed')