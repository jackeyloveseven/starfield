
# -*- coding: utf-8 -*-
"""v263 - 装饰物被地形起伏埋住：抬高到地形之上；水晶放大；菌毯改紫。"""
import sys
from pathlib import Path

HTML = Path(r'D:\items\code\projects\starfield\starfield-pub\starfield.html')
html = HTML.read_text(encoding='utf-8')
log = []

def rep(old, new, tag):
    global html
    assert html.count(old) == 1, tag + ' count=%d' % html.count(old)
    html = html.replace(old, new)
    log.append(tag)

# --- 都市：霓虹网格与城市光点抬到地形之上 ---
rep("var rr2 = Math.cos(phi) * (R + 0.5), yy = Math.sin(phi) * (R + 0.5);",
    "var rr2 = Math.cos(phi) * (R + 7.0), yy = Math.sin(phi) * (R + 7.0);", 'neonLat')
rep("""        pts3.push(new THREE.Vector3(
          Math.sin(p3) * Math.cos(la) * (R + 0.5),
          Math.cos(p3) * (R + 0.5),
          Math.sin(p3) * Math.sin(la) * (R + 0.5)));""",
    """        pts3.push(new THREE.Vector3(
          Math.sin(p3) * Math.cos(la) * (R + 7.0),
          Math.cos(p3) * (R + 7.0),
          Math.sin(p3) * Math.sin(la) * (R + 7.0)));""",
    'neonLon')
rep("""      cp.push(Math.sin(cv) * Math.cos(cu) * (R + 0.7),
              Math.cos(cv) * (R + 0.7),
              Math.sin(cv) * Math.sin(cu) * (R + 0.7));""",
    """      cp.push(Math.sin(cv) * Math.cos(cu) * (R + 7.2),
              Math.cos(cv) * (R + 7.2),
              Math.sin(cv) * Math.sin(cu) * (R + 7.2));""",
    'cityPts')

# --- 水晶：更大更高，真正的"参天晶体簇" ---
rep("      var h = 5 + rng() * 7;", "      var h = 9 + rng() * 12;", 'crystalH')
rep("      m.position.copy(n).multiplyScalar(R + h * 0.35);",
    "      m.position.copy(n).multiplyScalar(R + 5.5 + h * 0.42);", 'crystalPos')
rep("      m.scale.set(1.5 + rng(), h, 1.5 + rng());",
    "      m.scale.set(2.4 + rng() * 1.4, h, 2.4 + rng() * 1.4);", 'crystalScale')
rep("      tops.push(n.clone().multiplyScalar(R + h));",
    "      tops.push(n.clone().multiplyScalar(R + 5.5 + h));", 'crystalTop')

# --- 菌毯：囊肿抬高、加深为紫红，且预设改 abyss 让底色偏冷紫 ---
rep("      cm2.position.copy(zn).multiplyScalar(R + cr * 0.18);",
    "      cm2.position.copy(zn).multiplyScalar(R + 6.0 + cr * 0.18);", 'cystPos')
rep("      color: col(H(310), 0.72, 0.42),", "      color: col(H(315), 0.80, 0.30),", 'cystCol')
rep("      emissive: col(H(325), 0.8, 0.14),", "      emissive: col(H(330), 0.85, 0.10),", 'cystEm')
rep("        var p0 = zn.clone().multiplyScalar(R + 0.4);",
    "        var p0 = zn.clone().multiplyScalar(R + 6.2);", 'veinA')
rep("        var p1 = p0.clone().add(tangent.multiplyScalar(3 + rng() * 4)).normalize().multiplyScalar(R + 0.4);",
    "        var p1 = p0.clone().add(tangent.multiplyScalar(3 + rng() * 4)).normalize().multiplyScalar(R + 6.2);",
    'veinB')
rep("  { id: 'zerg_biomorphic',    cn: '生化菌毯星',   preset: 'forest' },",
    "  { id: 'zerg_biomorphic',    cn: '生化菌毯星',   preset: 'abyss' },", 'zergPreset')

# --- 撕裂：电弧抬到地形之上 ---
rep("          Math.sin(v0) * Math.cos(aa) * R * jitter,\n          Math.cos(v0) * R * jitter,\n          Math.sin(v0) * Math.sin(aa) * R * jitter));",
    "          Math.sin(v0) * Math.cos(aa) * (R + 6.5) * jitter,\n          Math.cos(v0) * (R + 6.5) * jitter,\n          Math.sin(v0) * Math.sin(aa) * (R + 6.5) * jitter));",
    'arcPos')

HTML.write_text(html, encoding='utf-8', newline='')
sys.stdout.reconfigure(encoding='utf-8')
print('done:', ', '.join(log))
