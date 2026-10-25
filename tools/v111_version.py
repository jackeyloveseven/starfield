"""V111: version tag follows version.json (v1.1.8 / Build 110)."""
import sys
src_p, out_p = sys.argv[1], sys.argv[2]
src = open(src_p, encoding="utf-8").read()
old, new = 'v1.1.7 (Build 109)', 'v1.1.8 (Build 110)'
if src.count(old) != 1:
    sys.exit('count=%d (want 1)' % src.count(old))
open(out_p, "w", encoding="utf-8", newline="").write(src.replace(old, new, 1))
print('V111 written:', len(src), 'chars')
