"""V117: version tag follows version.json (v1.2.1 / Build 113)."""
import sys
src_p, out_p = sys.argv[1], sys.argv[2]
src = open(src_p, encoding="utf-8").read()
old, new = 'v1.2.0 (Build 112)', 'v1.2.1 (Build 113)'
if src.count(old) != 1:
    sys.exit('count=%d (want 1)' % src.count(old))
open(out_p, "w", encoding="utf-8", newline="").write(src.replace(old, new, 1))
print('V117 written:', len(src), 'chars')
