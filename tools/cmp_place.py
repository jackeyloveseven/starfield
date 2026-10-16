"""TEMP: print the before/after placement comparison from two measure_place runs."""
import re, sys

def parse(p):
    t = open(p, encoding='utf-8', errors='replace').read()
    d = {}
    def g(pat, cast=float, key=None, flags=0):
        m = re.search(pat, t, flags)
        return cast(m.group(1)) if m else None
    d['projPerFrame'] = g(r'projected bodies=(\d+) avg/frame=([\d.]+)', str)  # placeholder
    m = re.search(r'projected bodies=\d+ avg/frame=([\d.]+)', t); d['perFrame'] = float(m.group(1))
    m = re.search(r'on-screen bodies=(\d+) \(([\d.]+)%', t); d['onScreen'] = int(m.group(1)); d['onPct'] = float(m.group(2))
    m = re.search(r'frames with ZERO on-screen bodies: \d+ \(([\d.]+)%', t); d['zero'] = float(m.group(1))
    m = re.search(r'frames with ZERO on-screen world >=30px: \d+ \(([\d.]+)%', t); d['zeroBig'] = float(m.group(1))
    m = re.search(r'within outer 25% band of an edge: \d+ \(([\d.]+)%', t); d['nearEdge'] = float(m.group(1))
    m = re.search(r'disc clipped by frame edge\s+: \d+ \(([\d.]+)%', t); d['clipped'] = float(m.group(1))
    m = re.search(r'frames with >=1 overlapping pair: \d+ \(([\d.]+)%', t); d['overlap'] = float(m.group(1))
    m = re.search(r'avg off lattice=(\d+)\s+system=(\d+)', t); d['offL'] = int(m.group(1)); d['offS'] = int(m.group(2))
    m = re.search(r'>3000u: \d+ \(([\d.]+)%', t); d['bigOff'] = float(m.group(1))
    m = re.search(r'y range lattice=(-?\d+)\.\.(-?\d+)\s+system=(-?\d+)\.\.(-?\d+)', t)
    d['yL'] = (int(m.group(1)), int(m.group(2))); d['yS'] = (int(m.group(3)), int(m.group(4)))
    sec = t.split('--- z-gap to previous body')[1]
    m = re.search(r'\n\s*0-400\s+(\d+)\s+([\d.]+)%', sec); d['zg0'] = float(m.group(2))
    m = re.search(r'6000-6400\+\s+(\d+)\s+([\d.]+)%', sec); d['zgBig'] = float(m.group(2))
    m = re.search(r'of those, ZERO bodies on screen : \d+ \(([\d.]+)%', t); d['zeroFwd'] = float(m.group(1))
    # y/H bins
    sec = t.split('y/H (n=')[1].split('within outer')[0]
    bins = [float(v) for v in re.findall(r'([\d.]+)%', sec)]
    d['top20'] = bins[0] + bins[1]
    d['bot30'] = bins[7] + bins[8] + bins[9]
    # x/W bins
    sec = t.split('x/W (n=')[1].split('y/H (n=')[0]
    xb = [float(v) for v in re.findall(r'([\d.]+)%', sec)]
    d['midX'] = xb[3] + xb[4] + xb[5]
    # system radius <40px
    sec = t.split('--- on-screen radius px')[1].split('--- bodies on screen per frame')[0]
    sec = sec.split('SYSTEM ')[1]
    d['sysSmall'] = float(re.search(r'0-40\s+\d+\s+([\d.]+)%', sec).group(1))
    sec = t.split('--- on-screen count split')[1]
    sec = sec.split('CHUNKS  (n=')[1].split('frames showing')[0]
    cb = [float(v) for v in re.findall(r'([\d.]+)%', sec)]
    d['chunk01'] = cb[0] + cb[1]
    return d

a = parse(sys.argv[1]); b = parse(sys.argv[2])
rows = [
    ('projected bodies / frame', 'perFrame', '{:.2f}'),
    ('on-screen bodies / frame', None, ''),
    ('on-screen % of projected', 'onPct', '{:.1f}%'),
    ('frames with ZERO bodies on screen', 'zero', '{:.1f}%'),
    ('frames with ZERO world >=30px', 'zeroBig', '{:.1f}%'),
    ('frames showing 0 or 1 chunk', 'chunk01', '{:.1f}%'),
    ('facing forward, ZERO bodies', 'zeroFwd', '{:.1f}%'),
    ('bodies in outer 25% band', 'nearEdge', '{:.1f}%'),
    ('bodies clipped by frame edge', 'clipped', '{:.1f}%'),
    ('bodies in top 20% of frame (y/H)', 'top20', '{:.1f}%'),
    ('bodies in bottom 30% of frame (y/H)', 'bot30', '{:.1f}%'),
    ('bodies in middle x/W 0.3-0.6', 'midX', '{:.1f}%'),
    ('z-gap < 400u', 'zg0', '{:.1f}%'),
    ('z-gap > 6000u', 'zgBig', '{:.1f}%'),
    ('avg |x-laneX| lattice', 'offL', '{}'),
    ('avg |x-laneX| system', 'offS', '{}'),
    ('bodies with |x-laneX| > 3000', 'bigOff', '{:.1f}%'),
    ('system on-screen radius < 40px', 'sysSmall', '{:.1f}%'),
    ('frames with an overlapping pair', 'overlap', '{:.1f}%'),
]
print(f'{"metric":<38}{"before":>10}{"after":>10}')
for name, k, f in rows:
    if k is None:
        print(f'{name:<38}{a["onScreen"]/3000:>10.2f}{b["onScreen"]/3000:>10.2f}')
        continue
    print(f'{name:<38}{f.format(a[k]):>10}{f.format(b[k]):>10}')
print(f'{"world y range lattice":<38}{str(a["yL"]):>10}{str(b["yL"]):>10}')
print(f'{"world y range system":<38}{str(a["yS"]):>10}{str(b["yS"]):>10}')
