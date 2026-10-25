"""V100: the version tag the web build shows.

In the APK the bridge overwrites it; on the website nothing did, so the settings
sheet still claimed v1.1.0 (Build 102). Bumped to match version.json.

Run:  python -I v100_version.py <in.html> <out.html>
"""
import sys

src_p, out_p = sys.argv[1], sys.argv[2]
src = open(src_p, encoding="utf-8").read()
old, new = 'v1.1.0 (Build 102)', 'v1.1.3 (Build 105)'
if src.count(old) != 1:
    sys.exit('count=%d (want 1)' % src.count(old))
open(out_p, "w", encoding="utf-8", newline="").write(src.replace(old, new, 1))
print('V100 written:', len(src), 'chars')
