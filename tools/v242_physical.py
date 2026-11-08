
# -*- coding: utf-8 -*-
"""v242 - MeshPhysicalMaterial + 环境贴图 + 卡通描边。"""
import sys
from pathlib import Path

HTML = Path(r'D:\items\code\projects\starfield\starfield-pub\starfield.html')
html = HTML.read_text(encoding='utf-8', errors='replace')
log = []

def rep(old, new, tag):
    global html
    assert html.count(old) == 1, tag + ' count=%d' % html.count(old)
    html = html.replace(old, new)
    log.append(tag)

# ---- 1. 地形材质：MeshPhysicalMaterial + clearcoat ----
rep("""    const mat = new THREE.MeshStandardMaterial({
      vertexColors: true,
      roughness: 0.88,
      metalness: 0.08,
      flatShading: true,
    });""",
    """    const mat = new THREE.MeshPhysicalMaterial({
      vertexColors: true,
      roughness: 0.86,
      metalness: 0.05,
      flatShading: true,
      clearcoat: this.cfg.clearcoat || 0,
      clearcoatRoughness: 0.42,
      envMapIntensity: this.cfg.envIntensity || 0.55
    });""",
    'terrainMat')

# ---- 2. 海洋材质：物理材质 + 高光 ----
rep("""    const mat = new THREE.MeshStandardMaterial({
      color: new THREE.Color(preset.colors.coastWater),
      transparent: true,
      opacity: preset.colors.waterTrans || 0.82,
      roughness: 0.15,
      metalness: 0.12,
      flatShading: true,
    });""",
    """    const mat = new THREE.MeshPhysicalMaterial({
      color: new THREE.Color(preset.colors.coastWater),
      transparent: true,
      opacity: preset.colors.waterTrans || 0.82,
      roughness: 0.10,
      metalness: 0.22,
      flatShading: true,
      clearcoat: 1.0,
      clearcoatRoughness: 0.06,
      envMapIntensity: (this.cfg.envIntensity || 0.55) * 2.0,
      iridescence: this.cfg.iridescence || 0,
      iridescenceIOR: 1.35
    });""",
    'oceanMat')

# ---- 3. 构造函数里接受 clearcoat / envIntensity / iridescence ----
rep("""  constructor(scene, cfg) {
    this.cfg = cfg || { radius: 36, seed: 1, preset: 'archipelago',
      landRatio: 0.38, ruggedness: 1.2, treeCount: 800, monumentLevel: 1,
      faunaLevel: 1, cloudCoverage: 0.4, spinSpeed: 1, colors: Presets.archipelago.colors };""",
    """  constructor(scene, cfg) {
    this.cfg = cfg || { radius: 36, seed: 1, preset: 'archipelago',
      landRatio: 0.38, ruggedness: 1.2, treeCount: 800, monumentLevel: 1,
      faunaLevel: 1, cloudCoverage: 0.4, spinSpeed: 1, colors: Presets.archipelago.colors };
    this.envMap = (cfg && cfg.envMap) || null;
    if (this.envMap) this.cfg.envMap = this.envMap;""",
    'ctorEnv')

# 地形/海洋应用 envMap
rep("      envMapIntensity: this.cfg.envIntensity || 0.55\n    });",
    "      envMapIntensity: this.cfg.envIntensity || 0.55,\n      envMap: this.cfg.envMap || null\n    });",
    'terrainEnv')
rep("      iridescenceIOR: 1.35\n    });",
    "      iridescenceIOR: 1.35,\n      envMap: this.cfg.envMap || null\n    });",
    'oceanEnv')

HTML.write_text(html, encoding='utf-8', newline='')
sys.stdout.reconfigure(encoding='utf-8')
print('done:', ', '.join(log))
