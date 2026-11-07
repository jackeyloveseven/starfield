
# -*- coding: utf-8 -*-
"""v151 — 收紧 sf-hatch-flat：停用粒子层、压缩版面、压暗扫描光带。"""
import sys
from pathlib import Path

HTML = Path(__file__).resolve().parent.parent / 'starfield.html'

with open(HTML, 'r', encoding='utf-8', newline='') as f:
    src = f.read()
nl = '\r\n' if '\r\n' in src[:6000] else '\n'
N = lambda s: s.replace('\r\n', '\n').replace('\n', nl)
log = []


def kill_fn(name, body):
    global src
    start = src.find('  CeremonyParticles.prototype.' + name + ' = function')
    assert start >= 0, name
    end = src.find('\n  };', start)
    assert end >= 0, name + ' end'
    end += len('\n  };')
    src = src[:start] + N(body) + src[end:]
    log.append('particles.' + name + ' disabled')


kill_fn('startSingularity', """  CeremonyParticles.prototype.startSingularity = function() {
    /* v151: 粒子层停用。极简版本只用发丝线与色块，不做散点。 */
    this.phase = 'IDLE';
    this.particles = [];
  };""")

kill_fn('explode', """  CeremonyParticles.prototype.explode = function() {
    this.phase = 'IDLE';
    this.particles = [];
  };""")


def rep(tag, old, new):
    global src
    o, n = N(old), N(new)
    c = src.count(o)
    assert c == 1, tag + ' count=' + str(c)
    src = src.replace(o, n)
    log.append(tag)


rep('orb-stage',
    """#sf-hatch .sf-card-orb-stage{
  flex:1 1 0;min-height:150px;max-height:230px;
  margin:0;padding:56px 0 0 0;
}""",
    """#sf-hatch .sf-card-orb-stage{
  flex:0 0 auto;height:258px;min-height:0;max-height:none;
  margin:0;padding:58px 0 0 0;
}""")

rep('info-pad',
    "#sf-hatch .sf-card-info{gap:6px;margin:0;padding:0 20px 74px 20px;z-index:6}",
    "#sf-hatch .sf-card-info{gap:6px;margin:0;padding:0 20px 66px 20px;z-index:6}")

rep('holo',
    """  background:linear-gradient(calc(var(--holo-angle,125deg)),
    transparent 42%,rgba(255,255,255,.09) 50%,transparent 58%);""",
    """  background:linear-gradient(calc(var(--holo-angle,125deg)),
    transparent 46.5%,rgba(255,255,255,.045) 50%,transparent 53.5%);""")

rep('prompt-font',
    """  font-family:"SFMono-Regular",Consolas,"Liberation Mono",monospace;
  color:rgba(255,255,255,.55);text-shadow:none;animation:none;opacity:1;""",
    """  font-family:"SFMono-Regular",Consolas,"Liberation Mono",monospace,"PingFang SC","Microsoft YaHei",sans-serif;
  color:rgba(255,255,255,.55);text-shadow:none;animation:none;opacity:1;""")

rep('grid-alpha',
    """    linear-gradient(rgba(255,255,255,.05) 1px,transparent 1px),
    linear-gradient(90deg,rgba(255,255,255,.05) 1px,transparent 1px);""",
    """    linear-gradient(rgba(255,255,255,.038) 1px,transparent 1px),
    linear-gradient(90deg,rgba(255,255,255,.038) 1px,transparent 1px);""")

with open(HTML, 'w', encoding='utf-8', newline='') as f:
    f.write(src)
sys.stdout.reconfigure(encoding='utf-8')
for l in log:
    print('  ' + l)
print('DONE')
