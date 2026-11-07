
# -*- coding: utf-8 -*-
"""v174 — 压暗层顶部减弱，别把 masthead 也压了。"""
import sys
from pathlib import Path

HTML = Path(__file__).resolve().parent.parent / 'starfield.html'
with open(HTML, 'r', encoding='utf-8', newline='') as f:
    src = f.read()
nl = '\r\n' if '\r\n' in src[:6000] else '\n'
N = lambda s: s.replace('\r\n', '\n').replace('\n', nl)

old = N("""    linear-gradient(to bottom,
      rgba(5,9,14,.70) 0%, rgba(5,9,14,.10) 26%,
      rgba(5,9,14,.10) 66%, rgba(5,9,14,.82) 100%);
}""")
new = N("""    linear-gradient(to bottom,
      rgba(5,9,14,.34) 0%, rgba(5,9,14,.06) 22%,
      rgba(5,9,14,.06) 64%, rgba(5,9,14,.84) 100%);
}
#masthead{position:relative;z-index:6}""")
assert src.count(old) == 1
src = src.replace(old, new)

with open(HTML, 'w', encoding='utf-8', newline='') as f:
    f.write(src)
sys.stdout.reconfigure(encoding='utf-8')
print('scrim softened')
