"""Solve the three source levels against the band targets.

Rendering three sources at once and guessing is what produced two swings from
"all mid" to "all sub". Instead: render the bass, the voices and the shimmer
alone (the reverb is linear, so the band powers add), measure each one's
absolute band power, then search for the three scale factors that put the mix's
band shares on the targets.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))  # -I drops the script dir
import numpy as np
import synth as S

SR = S.SR
BANDS = [('sub', 30, 80), ('bass', 80, 200), ('lowmid', 200, 500),
         ('mid', 500, 1500), ('high', 1500, 4000), ('air', 4000, 11025)]
TARGET = np.array([.37, .18, .24, .24, .0425, .0175])


def bandpower(x):
    n = x.shape[1]
    mono = x.mean(axis=0) * np.hanning(n)
    P = np.abs(np.fft.rfft(mono)) ** 2
    f = np.fft.rfftfreq(n, 1.0 / SR)
    return np.array([P[(f >= lo) & (f < hi)].sum() for _, lo, hi in BANDS])


def render(spec, mode):
    return bandpower(S.make_track(dict(spec, mode=mode, raw=True)))


def shares(scales, cols):
    e = sum(s * c for s, c in zip(scales, cols))
    return e / e.sum()


def solve(cols):
    """shares() is scale-invariant, so pin the voice scale at 1 and search the
    two ratios. The overall level is set later by target_peak."""
    best, bestv = (1.0, 1.0), 1e9
    for lb in np.arange(-3.0, 3.01, .05):
        for ls in np.arange(-3.0, 3.01, .05):
            sc = [10 ** (2 * lb), 1.0, 10 ** (2 * ls)]
            err = ((shares(sc, cols) - TARGET) ** 2).sum()
            if err < bestv:
                bestv, best = err, (10 ** (2 * lb), 10 ** (2 * ls))
    b = np.array([best[0], 1.0, best[1]])
    for _ in range(200):
        improved = False
        for i in (0, 2):
            for m in (1.12, 1 / 1.12):
                t = b.copy(); t[i] *= m
                e = ((shares(t, cols) - TARGET) ** 2).sum()
                if e < bestv:
                    bestv, b, improved = e, t, True
        if not improved:
            break
    return b, bestv


if __name__ == '__main__':
    import os
    outdir = sys.argv[1] if len(sys.argv) > 1 else None
    for spec in S.SPECS:
        cols = [render(spec, m) for m in ('bass', 'voices', 'shimmer')]
        sc, err = solve(cols)
        got = shares(sc, cols)
        mb, mv, ms = np.sqrt(sc)
        spec['bass_amp'] *= mb
        spec['voice_amp'] *= mv
        spec['shimmer_amp'] *= ms
        print(f'{spec["name"]:<8} err {np.sqrt(err):.4f}  '
              f'got ' + ' '.join(f'{b}={v:.3f}' for (b, _, _), v in zip(BANDS, got)))
        if outdir:
            os.makedirs(outdir, exist_ok=True)
            st = S.make_track(spec)
            path = os.path.join(outdir, f'{S.SPECS.index(spec) + 1}-{spec["name"]}.mp3')
            print('   ->', path, f'{S.encode(st, path) / 1024:.0f} KB')
