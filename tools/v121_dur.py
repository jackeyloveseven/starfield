"""V121: the dolly's dur must be in the same unit as dt.

v119 made the transition advance by dt (seconds) but left dur in milliseconds,
so k advanced 1000x too slowly: a 2.2 s transition would have taken 36 minutes,
which on a phone reads as "tapping the chip does nothing". Found by printing
departK after one step: 0.1/2200 = 0.000045 instead of 0.045.

Run:  python -I v121_dur.py <in.html> <out.html>
"""
import sys
src_p, out_p = sys.argv[1], sys.argv[2]
src = open(src_p, encoding="utf-8").read()
old = "__depart={from:from,to:to,i:i,k:0,dur:Math.min(2200,700+Math.abs(to-from)/14)};"
new = "// seconds, because dt is seconds\n __depart={from:from,to:to,i:i,k:0,dur:Math.min(2.2,0.7+Math.abs(to-from)/14000)};"
if src.count(old) != 1:
    sys.exit('count=%d (want 1)' % src.count(old))
open(out_p, "w", encoding="utf-8", newline="").write(src.replace(old, new, 1))
print('V121 written:', len(src), 'chars')
