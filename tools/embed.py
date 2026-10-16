"""Swap 星空's embedded scores for the six space tracks, and keep the page's own
diagnostics truthful. Replaces the whole SCORES array, so it is re-runnable."""
import re, sys, base64, shutil, os, glob

SRC = sys.argv[1]
MP3 = sorted(glob.glob(sys.argv[2]))
TITLES = ["Paper / 素纸", "Ink Wash / 墨海", "Foil / 箔野",
          "Core / 星核", "Abyss / 深渊", "Drift / 深空漂移"]
assert len(MP3) == 6, MP3

s = open(SRC, encoding='utf-8').read()
shutil.copy2(SRC, SRC.replace('.html', '-prescores.html'))
m = re.search(r"const SCORES=\[.*?\];", s, re.S)
assert m, "SCORES not found"
items = ["'data:audio/mpeg;base64," + base64.b64encode(open(p, 'rb').read()).decode() + "'"
         for p in MP3]
s = s.replace(m.group(0), "const SCORES=[\n" + ",\n".join(items) + "];", 1)

t = re.search(r"scoreTitles:Object\.freeze\(\[.*?\]\)", s, re.S)
assert t, "scoreTitles not found"
s = s.replace(t.group(0),
              "scoreTitles:Object.freeze([" + ",".join(f"'{x}'" for x in TITLES) + "])", 1)

open(SRC, 'w', encoding='utf-8', newline='').write(s)
print(f"embedded {len(items)} scores -> {os.path.getsize(SRC)/1024/1024:.2f} MB")
