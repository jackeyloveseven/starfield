"""Original space scores for 星空 · STARFIELD.

Same toolchain shape as the 候鸟 scores (sustained swelling voices over a moving
bass line, convolution reverb, TPDF dither, lameenc MP3), but a different
measured target: longer tails, much wider stereo, a deeper sub, and a little
high shimmer. Voices swell rather than pluck - the 候鸟 notes record that a
plucked first attempt measured too dark and noisy and was scrapped.

  python -I synth.py out
"""
import sys, os
import numpy as np
import lameenc

SR = 22050


def m2f(m):
    return 440.0 * 2.0 ** ((m - 69) / 12.0)


def fade(x, n=64):
    if len(x) > 2 * n:
        x[:n] *= np.linspace(0, 1, n)
        x[-n:] *= np.linspace(1, 0, n)
    return x


def spectral(x, lo=None, hi=None, order=2):
    """Zero-phase magnitude shaping - no phase smear, so no pre-echo."""
    n = len(x)
    X = np.fft.rfft(x)
    f = np.fft.rfftfreq(n, 1.0 / SR)
    g = np.ones_like(f)
    if lo:
        g *= 1.0 / (1.0 + (lo / np.maximum(f, 1e-6)) ** (2 * order))
    if hi:
        g *= 1.0 / (1.0 + (np.maximum(f, 1e-6) / hi) ** (2 * order))
    return np.fft.irfft(X * g, n)


def voice(n, f, amp, attack, release, partials, detune, swell, swell_rate,
          phase, split=False):
    """One sustained tone. With split=False the two channels are identical (the
    dry image is mono and only panning differs); with split=True the partials
    start at different phases per channel, which is the one thing that puts a
    slow stereo beat in the dry signal. `wide` decides how many voices split."""
    t = np.arange(n) / SR
    env = np.minimum(1.0, t / max(attack, 1e-3)) * np.minimum(
        1.0, np.maximum(n / SR - t, 0) / max(release, 1e-3))
    env *= 1.0 - swell * 0.5 * (1.0 - np.cos(2 * np.pi * swell_rate * t))
    out = np.zeros((2, n))
    for mult, w in partials:
        if split:
            out[0] += w * np.sin(2 * np.pi * (f * mult + detune * mult) * t + phase * mult)
            out[1] += w * np.sin(2 * np.pi * (f * mult - detune * mult) * t + phase * mult * 1.7)
        else:
            osc = w * np.sin(2 * np.pi * f * mult * t + phase * mult)
            out[0] += osc
            out[1] += osc
    out[0] *= env
    out[1] *= env
    return out * amp


def bass(n, f, amp, attack, release, phase_l, phase_r):
    """A detuned pair an octave down: the pair beats slowly, and because the
    two channels start at different phases the beat is a stereo one."""
    t = np.arange(n) / SR
    env = np.minimum(1.0, t / max(attack, 1e-3)) * np.minimum(
        1.0, np.maximum(n / SR - t, 0) / max(release, 1e-3))
    out = np.zeros((2, n))
    for sign, ph in ((+1, phase_l), (-1, phase_r)):
        fv = f + sign * 0.35
        osc = (np.sin(2 * np.pi * fv * t + ph)
               + 0.55 * np.sin(2 * np.pi * fv * 2 * t + ph * 2)
               + 0.28 * np.sin(2 * np.pi * fv * 3 * t + ph * 3))
        out[0] += osc
        out[1] += osc
    return out * env * amp


def reverb(x, rt, cutoff, mix, seed, coh, predelay=0.0):
    """Convolution with a synthetic dark decaying IR. `coh` is how much of the
    tail the two channels share: 1 is a mono tail (correlated), 0 is two
    independent tails (over-decorrelated). It is the direct knob on L/R
    correlation and it is measurable."""
    n = x.shape[1]
    ln = int(rt * SR)
    rng = np.random.default_rng(seed)
    t = np.arange(ln) / SR
    decay = np.exp(-6.9078 * t / rt)
    n1 = rng.standard_normal(ln)
    n2 = rng.standard_normal(ln)
    ir = np.stack([n1, coh * n1 + (1.0 - coh) * n2]) * decay
    ir = np.stack([spectral(ir[0], hi=cutoff), spectral(ir[1], hi=cutoff)])
    ir /= np.max(np.abs(ir)) + 1e-9
    if predelay > 0:
        d = int(predelay * SR)
        ir = np.concatenate([np.zeros((2, d)), ir], axis=1)
    size = 1 << int(np.ceil(np.log2(n + ir.shape[1])))
    wet = np.stack([
        np.fft.irfft(np.fft.rfft(x[c], size) * np.fft.rfft(ir[c], size), size)[:n]
        for c in (0, 1)])
    return x * (1 - mix) + wet * mix * 2.2


def make_track(spec):
    mode = spec.get('mode', 'all')
    dur = spec['dur']
    n = int(dur * SR)
    out = np.zeros((2, n))
    vb = np.zeros((2, n))          # voice bus, high-passed so it stays out of lowmid
    sb = np.zeros((2, n))          # shimmer bus, added after the reverb
    bb = np.zeros((2, n))          # bass bus, keeps the sub
    chords = spec['chords']
    hold_lo, hold_hi = spec['hold']
    rng = np.random.default_rng(spec['seed'])
    # Chord schedule: each chord is held 4-8 s, so the harmonic rhythm is much
    # slower than the 候鸟 scores' 1-2 s.
    t0 = 0.0
    idx = 0
    while t0 < dur:
        hold = hold_lo + rng.random() * (hold_hi - hold_lo)
        bmidi, pool = chords[idx % len(chords)]
        idx += 1
        i0, i1 = int(t0 * SR), int(min(dur, t0 + hold + spec['tail']) * SR)
        if i1 - i0 < SR // 2:
            break
        seg = i1 - i0
        if mode in ('all', 'bass'):
         bb[:, i0:i1] += bass(seg, m2f(bmidi), spec['bass_amp'],
                             spec['attack'], spec['release'],
                             rng.random() * 6.283, rng.random() * 6.283)
        # A handful of sustained voices from the pool, panned wide.
        if mode in ('all', 'voices'):
         k = min(len(pool), spec['voices'])
         pick = rng.choice(len(pool), size=k, replace=False)
         for j in pick:
          midi = pool[j] - spec['pool_shift']
          pan = (j / max(1, len(pool) - 1)) * 2 - 1        # -1 .. 1
          amp = spec['voice_amp'] * (1.0 - 0.35 * abs(pan)) * (0.8 + rng.random() * 0.4)
          v = voice(seg, m2f(midi), amp, spec['attack'], spec['release'],
                        spec['partials'], spec['detune'], spec['swell'],
                        spec['swell_rate'], rng.random() * 6.283,
                        split=rng.random() < spec['wide'])
          gl = np.sqrt((1 - pan) / 2)
          gr = np.sqrt((1 + pan) / 2)
          vb[0, i0:i1] += v[0] * gl * 2 ** 0.5
          vb[1, i0:i1] += v[1] * gr * 2 ** 0.5
        # Shimmer: a very quiet high voice with a slow swell, never a pluck.
        if mode in ('all', 'shimmer'):
         for _sv in range(spec['shimmer_voices']):
          sm = spec['shimmer_midi'] + int(rng.random() * 4) * 3
          pan = rng.random() * 2 - 1
          v = voice(seg, m2f(sm), spec['shimmer_amp'], spec['attack'] * 2.4,
                        spec['release'] * 1.6, spec['shimmer_partials'], spec['detune'],
                        0.9, 0.021, rng.random() * 6.283, split=False)
          sb[0, i0:i1] += v[0] * np.sqrt((1 - pan) / 2) * 2 ** 0.5
          sb[1, i0:i1] += v[1] * np.sqrt((1 + pan) / 2) * 2 ** 0.5
        t0 += hold
    out = np.stack([fade(spectral(bb[c], lo=spec['low_cut']) +
                         spectral(vb[c], lo=spec['voice_hp']))
                    for c in (0, 1)])
    out = reverb(out, spec['rt'], spec['rev_cut'], spec['rev_mix'], spec['seed'] + 7,
                 spec['coh'], spec['predelay'])
    out = out + np.stack([fade(spectral(sb[c], lo=spec['voice_hp'])) for c in (0, 1)])
    out = np.stack([fade(spectral(out[c], lo=spec['low_cut'], hi=spec['bright_cut']))
                    for c in (0, 1)])
    if spec.get('raw'):
        return out
    peak = np.max(np.abs(out)) + 1e-9
    out *= spec['target_peak'] / peak
    return out


def encode(stereo, path):
    rng = np.random.default_rng(7)
    x = stereo.T
    # TPDF dither at 1 LSB
    x = x + (rng.random(x.shape) - rng.random(x.shape)) / 32768.0
    pcm = (np.clip(x, -1, 1) * 32767).astype('<i2').tobytes()
    enc = lameenc.Encoder()
    enc.set_bit_rate(56)
    enc.set_in_sample_rate(SR)
    enc.set_channels(2)
    enc.set_quality(2)
    data = enc.encode(pcm) + enc.flush()
    open(path, 'wb').write(data)
    return len(data)


# ---------------------------------------------------------------- the scores
# Voices sit at MIDI 67-88 (392-1319 Hz) and are high-passed, so they do not
# pile into low-mid; the sub is the bass line alone. The shimmer carries the
# 1.5-11 kHz the 候鸟 scores had none of.
PART = ((1, 1.0), (2, .16), (3, .05))
FULL = ((1, 1.0), (2, .18), (3, .06), (5, .022), (7, .012))
SHIM = ((1, 1.0), (2, .35), (3, .22), (4, .14), (6, .09), (8, .06))

COMMON = dict(target_peak=.27, low_cut=26, voice_hp=170, bright_cut=11000,
              wide=.05, attack=.8, release=3.0, detune=.30, swell=.5,
              swell_rate=.030, tail=10.0, rev_cut=5200, predelay=.012,
              shimmer_partials=SHIM, shimmer_midi=93, shimmer_voices=3,
              pool_shift=7)

def S(**kw):
    d = dict(COMMON); d.update(kw); return d

PAPER = S(name='paper', dur=82.0, seed=201,
          chords=[(33, [67, 71, 74, 76, 81, 84]), (31, [67, 69, 74, 78, 81, 85]),
                  (28, [67, 69, 72, 76, 81, 83]), (33, [67, 71, 74, 79, 84, 88]),
                  (35, [67, 71, 74, 76, 83, 86])],
          bass_amp=.060, voice_amp=.013, shimmer_amp=.034, voices=4, partials=FULL,
          hold=(5.0, 7.5), rt=5.8, rev_mix=.40, coh=.46, swell_rate=.035)

INKWASH = S(name='inkwash', dur=88.0, seed=211,
            chords=[(31, [67, 70, 74, 77, 79, 82, 86]), (29, [67, 69, 72, 77, 79, 83, 86]),
                    (26, [67, 70, 72, 75, 79, 82, 84]), (31, [67, 70, 74, 77, 82, 84, 88]),
                    (28, [68, 70, 75, 77, 82, 85, 87])],
            bass_amp=.062, voice_amp=.013, shimmer_amp=.040, voices=5, partials=FULL,
            hold=(6.0, 8.0), rt=7.4, rev_mix=.46, coh=.44, swell_rate=.028,
            predelay=.016, shimmer_midi=86)

FOIL = S(name='foil', dur=80.0, seed=221,
         chords=[(35, [71, 74, 78, 81, 83, 86, 88]), (33, [69, 74, 76, 81, 84, 86, 88]),
                 (30, [70, 74, 77, 79, 82, 86, 88]), (35, [71, 76, 78, 83, 86, 88, 90]),
                 (32, [69, 72, 77, 81, 84, 86, 89])],
         bass_amp=.054, voice_amp=.013, shimmer_amp=.048, voices=5, partials=FULL,
         hold=(4.0, 6.0), rt=5.6, rev_mix=.40, coh=.47, swell_rate=.042,
         shimmer_midi=89, rev_cut=6400, wide=.5)

CORE = S(name='core', dur=84.0, seed=231,
         chords=[(31, [67, 70, 74, 77, 79, 82, 86]), (33, [67, 71, 74, 76, 79, 83, 86]),
                 (29, [67, 69, 72, 76, 79, 84, 88]), (31, [67, 70, 75, 79, 82, 86, 88]),
                 (34, [69, 71, 74, 78, 81, 86, 88])],
         bass_amp=.066, voice_amp=.013, shimmer_amp=.040, voices=6, partials=FULL,
         hold=(5.5, 7.5), rt=6.6, rev_mix=.43, coh=.46, swell_rate=.032,
         shimmer_midi=87)

ABYSS = S(name='abyss', dur=92.0, seed=241,
          chords=[(24, [67, 70, 72, 75, 79, 82]), (26, [67, 70, 74, 77, 81, 84]),
                  (24, [67, 69, 72, 76, 79, 82]), (27, [67, 70, 75, 79, 82, 86]),
                  (25, [67, 70, 73, 77, 80, 84])],
          bass_amp=.074, voice_amp=.012, shimmer_amp=.026, voices=4, partials=PART,
          hold=(6.5, 8.0), rt=8.0, rev_mix=.48, coh=.42, swell_rate=.020,
          attack=1.4, release=4.0, predelay=.022, rev_cut=3800, bright_cut=9000,
          shimmer_midi=84, tail=13.0)

DRIFT = S(name='drift', dur=86.0, seed=251,
          chords=[(29, [67, 70, 73, 77, 81, 84, 88]), (31, [67, 71, 74, 79, 83, 86, 88]),
                  (27, [67, 70, 74, 77, 82, 84, 87]), (29, [67, 71, 76, 79, 83, 86, 88]),
                  (32, [68, 72, 75, 80, 84, 87, 89])],
          bass_amp=.060, voice_amp=.013, shimmer_amp=.040, voices=5, partials=FULL,
          hold=(5.0, 7.0), rt=6.8, rev_mix=.44, coh=.45, swell_rate=.030,
          shimmer_midi=88)

SPECS = [PAPER, INKWASH, FOIL, CORE, ABYSS, DRIFT]

if __name__ == '__main__':
    outdir = sys.argv[1] if len(sys.argv) > 1 else 'out'
    os.makedirs(outdir, exist_ok=True)
    for i, spec in enumerate(SPECS, 1):
        st = make_track(spec)
        path = os.path.join(outdir, f'{i}-{spec["name"]}.mp3')
        size = encode(st, path)
        print(f'{path}  {spec["dur"]:.0f}s  {size/1024:.0f} KB')
