"""V106: version tag follows version.json (v1.1.6 / Build 108).

Run:  python -I v106_version.py <in.html> <out.html>
"""
import sys
src_p, out_p = sys.argv[1], sys.argv[2]
src = open(src_p, encoding="utf-8").read()
old, new = 'v1.1.5 (Build 107)', 'v1.1.6 (Build 108)'
if src.count(old) != 1:
    sys.exit('count=%d (want 1)' % src.count(old))
open(out_p, "w", encoding="utf-8", newline="").write(src.replace(old, new, 1))
print('V106 written:', len(src), 'chars')
