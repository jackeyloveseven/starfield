"""Whole-frame before/after comparison. The acceptance test for the art-direction round.

The previous round was validated on 3x crops, and a fix that is visible at 3x is
invisible at 1x by construction. So this measures the WHOLE frame at 1x, and the
numbers it prints are the only acceptance criterion that counts.

  python -I framecompare.py <before.png> <after.png>

Reports, in the order that matters:
  mean |dL| over every pixel      - the "did the whole frame change" number
  fraction of pixels changed >30  - the "is it visible, not just measurable" number
  luminance percentiles p1/p50/p99 of each image
  fraction of pixels at literally 0 and literally 255
"""
import sys

import numpy as np
from PIL import Image

LUMA = np.array([0.2126, 0.7152, 0.0722])


def load(path):
    im = Image.open(path).convert('RGB')
    a = np.asarray(im, dtype=np.float32)
    return a, a @ LUMA


def pct(lum, q):
    return float(np.percentile(lum, q))


def main():
    a_path, b_path = sys.argv[1], sys.argv[2]
    a, la = load(a_path)
    b, lb = load(b_path)
    if la.shape != lb.shape:
        sys.exit('size mismatch: %s vs %s' % (la.shape, lb.shape))

    d = np.abs(la - lb)
    n = d.size
    changed = float((d > 30).sum()) / n * 100.0

    print('--- %s  vs  %s   (%dx%d) ---' % (a_path, b_path, la.shape[1], la.shape[0]))
    print('  mean |dL| whole frame : %6.2f      (target >= 8)   ' % d.mean())
    print('  pixels |dL|>30        : %6.2f %%    (target >= 50%%)' % changed)
    print()
    for tag, lum in (('before', la), ('after', lb)):
        print('  %-6s  p1 %5.1f   p50 %5.1f   p99 %5.1f   L=0 %5.2f%%   L=255 %5.2f%%'
              % (tag, pct(lum, 1), pct(lum, 50), pct(lum, 99),
                 float((lum < 0.5).sum()) / n * 100.0,
                 float((lum > 254.5).sum()) / n * 100.0))
    print()
    print('  targets: after.p1 <= 5, after.p99 >= 245, after L=0 >= 1.00%%, after L=255 >= 0.05%%')


main()
