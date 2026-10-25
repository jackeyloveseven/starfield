"""V102: version tag follows version.json (v1.1.4 / Build 106).

Run:  python -I v102_version.py <in.html> <out.html>
"""
import sys
src_p, out_p = sys.argv[1], sys.argv[2]
src = open(src_p, encoding="utf-8").read()
old, new = 'v1.1.3 (Build 105)', 'v1.1.4 (Build 106)'
if src.count(old) != 1:
    sys.exit('count=%d (want 1)' % src.count(old))
open(out_p, "w", encoding="utf-8", newline="").write(src.replace(old, new, 1))
print('V102 written:', len(src), 'chars')
