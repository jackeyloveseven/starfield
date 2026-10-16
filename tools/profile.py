"""Measure decoded MP3s against the 星空 target profile.

Measure the decoded MP3, never the pre-encode PCM: MP3 at 56 kbps can move the
peak by 1-3 dB and it is the encoder's band allocation that decides whether the
shimmer survives.

  python -I profile.py out/*.mp3
"""
import sys, os, subprocess, glob
import numpy as np
import imageio_ffmpeg

FF = imageio_ffmpeg.get_ffmpeg_exe()
SR = 22050

BANDS = [('sub', 30, 80), ('bass', 80, 200), ('lowmid', 200, 500),
         ('mid', 500, 1500), ('high', 1500, 4000), ('air', 4000, 11025)]
TARGETS = {'sub': (.34, .40), 'bass': (.16, .20), 'lowmid': (.22, .26),
           'mid': (.22, .26), 'high': (.030, .055), 'air': (.010, .025),
           'centroid': (420, 560), 'rolloff85': (900, 1400),
           'corr': (.42, .62), 'dbfs': (-26.5, -24.5)}


def decode(path):
    r = subprocess.run([FF, '-v', 'error', '-i', path, '-f', 'f32le',
                        '-acodec', 'pcm_f32le', '-ac', '2', '-ar', str(SR), '-'],
                       capture_output=True)
    a = np.frombuffer(r.stdout, dtype='<f4')
    return a.reshape(-1, 2).T.astype(np.float64)


def measure(x):
    n = x.shape[1]
    win = np.hanning(n)
    mono = x.mean(axis=0) * win
    X = np.abs(np.fft.rfft(mono))
    f = np.fft.rfftfreq(n, 1.0 / SR)
    power = X ** 2
    total = power.sum() + 1e-30
    out = {}
    for name, lo, hi in BANDS:
        out[name] = power[(f >= lo) & (f < hi)].sum() / total
    out['centroid'] = (f * power).sum() / total
    cum = np.cumsum(power) / total
    out['rolloff85'] = f[np.searchsorted(cum, .85)]
    a, b = x[0] - x[0].mean(), x[1] - x[1].mean()
    out['corr'] = float((a * b).sum() / (np.sqrt((a * a).sum() * (b * b).sum()) + 1e-30))
    # RMS, to stay in the same units as the measured 候鸟 profile
    out['dbfs'] = 20 * np.log10(np.sqrt((x ** 2).mean()) + 1e-12)
    return out


def check(m):
    bad = []
    for k, (lo, hi) in TARGETS.items():
        v = m[k]
        if not (lo <= v <= hi):
            bad.append(f'{k}={v:.4g} (want {lo}-{hi})')
    return bad


if __name__ == '__main__':
    paths = []
    for a in sys.argv[1:]:
        paths.extend(sorted(glob.glob(a)))
    if not paths:
        sys.exit('no input files')
    print(f'{"file":<22}{"sub":>6}{"bass":>6}{"lmid":>6}{"mid":>6}{"high":>7}{"air":>7}'
          f'{"cent":>7}{"roll":>7}{"corr":>7}{"dBFS":>8}')
    fails = 0
    for p in paths:
        m = measure(decode(p))
        print(f'{os.path.basename(p):<22}{m["sub"]:>6.3f}{m["bass"]:>6.3f}'
              f'{m["lowmid"]:>6.3f}{m["mid"]:>6.3f}{m["high"]:>7.4f}{m["air"]:>7.4f}'
              f'{m["centroid"]:>7.0f}{m["rolloff85"]:>7.0f}{m["corr"]:>7.2f}'
              f'{m["dbfs"]:>8.2f}')
        bad = check(m)
        if bad:
            fails += 1
            print('   OFF: ' + '; '.join(bad))
    print(f'\ntargets: ' + '  '.join(f'{k} {v[0]}-{v[1]}' for k, v in TARGETS.items()))
    print(f'{len(paths) - fails}/{len(paths)} tracks in range')
