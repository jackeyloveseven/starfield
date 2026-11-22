#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Stage 1 Patch Script: Build 200 (v2.0.0.0) Zero-Jank Frame Pacing & Flagship Aesthetics Overhaul
Author: perf-polish
Applies deterministic performance (DOM dirty-checking, EMA realDt smoothing, zero shadowBlur/RadialGradient hot-loop overhead)
and unified Deep-Space Editorial & Holographic Instrument aesthetics to starfield.html.
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HTML_PATH = os.path.join(ROOT, "starfield.html")


def replace_exact(content: str, target: str, replacement: str, label: str) -> str:
    if target not in content:
        if replacement in content:
            print(f"[SKIP] {label} already applied.")
            return content
        raise RuntimeError(f"[FAIL] Target not found for: {label}")
    count = content.count(target)
    if count != 1:
        print(f"[WARN] {label} matched {count} times; replacing first occurrence.")
    print(f"[OK] Applied: {label}")
    return content.replace(target, replacement, 1)


def main():
    with open(HTML_PATH, "r", encoding="utf-8") as f:
        html = f.read()

    orig_len = len(html)

    # -------------------------------------------------------------------------
    # 1. Origami Flagship & Fleet Lighting Contrast + Continuous Ribbon Trails
    # -------------------------------------------------------------------------
    html = replace_exact(
        html,
        """          // Directional starlight & normal dot product
          const lx = 0.35, ly = 0.82, lz = -0.45;
          const dot = nx * lx + ny * ly + nz * lz;
          const diffuse = Math.max(0.42, Math.min(1.18, dot * 0.38 + 0.72));
          const translucency = Math.max(0, Math.min(0.38, -dot * 0.32 + 0.14)) * (isLead ? 1.15 : 0.75);

          let finalCol = shade ? shade(col, diffuse) : col;
          if (translucency > 0.02) {
            finalCol = blend(finalCol, [255, 238, 204], translucency);
          }

          poly([p1, p2, p3], finalCol, { alpha: nearCraft });
        }

        // Draw crease lines
        for (const c of hull.creases) {
          const p1 = world[c[0]];
          const p2 = world[c[1]];
          if (p1 && p2) {
            line([p1, p2], p.craftShade || [140, 150, 165], 0.35 * nearCraft, 0.55);
          }
        }

        // Flagship gold foil gleam lines
        if (isLead && world.nose && (world.wtl || world.wingTipL || world.bladeOuterL)) {
          const wL = world.wtl || world.wingTipL || world.bladeOuterL;
          const wR = world.wtr || world.wingTipR || world.bladeOuterR;
          line([wL, world.nose], [255, 215, 80], 0.7 * nearCraft, 0.9);
          line([world.nose, wR], [255, 215, 80], 0.7 * nearCraft, 0.9);
        }""",
        """          // Directional starlight & normal dot product (Enhanced chiaroscuro facet contrast)
          const lx = 0.34, ly = 0.84, lz = -0.42;
          const dot = nx * lx + ny * ly + nz * lz;
          const diffuse = Math.max(0.36, Math.min(1.24, dot * 0.46 + 0.70));
          const translucency = Math.max(0, Math.min(0.42, -dot * 0.35 + 0.15)) * (isLead ? 1.25 : 0.78);

          let finalCol = shade ? shade(col, diffuse) : col;
          if (translucency > 0.02) {
            finalCol = blend(finalCol, isLead ? [255, 242, 214] : [236, 242, 250], translucency);
          }

          poly([p1, p2, p3], finalCol, { alpha: nearCraft });
        }

        // Draw crease lines with crisp architectural definition
        for (const c of hull.creases) {
          const p1 = world[c[0]];
          const p2 = world[c[1]];
          if (p1 && p2) {
            line([p1, p2], isLead ? [244, 208, 111] : (p.craftShade || [155, 168, 184]), (isLead ? 0.48 : 0.38) * nearCraft, isLead ? 0.72 : 0.58);
          }
        }

        // Flagship gold foil gleam lines
        if (isLead && world.nose && (world.wtl || world.wingTipL || world.bladeOuterL)) {
          const wL = world.wtl || world.wingTipL || world.bladeOuterL;
          const wR = world.wtr || world.wingTipR || world.bladeOuterR;
          line([wL, world.nose], [255, 224, 130], 0.84 * nearCraft, 1.05);
          line([world.nose, wR], [255, 224, 130], 0.84 * nearCraft, 1.05);
        }""",
        "Origami flagship & fleet chiaroscuro facet lighting contrast"
    )

    html = replace_exact(
        html,
        """      // Manage history Ring Buffer for this craft (Zero GC churn)
      const MAX_TRAIL_PTS = 64;
      let ring = this.trailHistory.get(b);
      if (!ring || !ring.slots) {
        ring = {
          slots: new Array(MAX_TRAIL_PTS),
          head: 0,
          count: 0
        };
        for (let s = 0; s < MAX_TRAIL_PTS; s++) {
          ring.slots[s] = { x: 0, y: 0, z: 0, time: 0 };
        }
        this.trailHistory.set(b, ring);
      }

      const maxPts = Math.min(MAX_TRAIL_PTS, Math.round(14 * warpStretch));
      const curSlot = ring.slots[ring.head];
      curSlot.x = emitterPt[0];
      curSlot.y = emitterPt[1];
      curSlot.z = emitterPt[2];
      curSlot.time = time;
      ring.head = (ring.head + 1) % MAX_TRAIL_PTS;
      ring.count = Math.min(maxPts, ring.count + 1);

      if (ring.count < 2) return;

      // Draw Ribbon Trail Segments
      const colMain = trail.colors.main;
      const colCore = trail.colors.core;

      for (let j = 0; j < ring.count - 1; j++) {
        const idx1 = (ring.head - 1 - j + MAX_TRAIL_PTS) % MAX_TRAIL_PTS;
        const idx2 = (ring.head - 2 - j + MAX_TRAIL_PTS) % MAX_TRAIL_PTS;
        const pt1 = ring.slots[idx1];
        const pt2 = ring.slots[idx2];
        const frac = j / ring.count;
        const segAlpha = Math.max(0, (1 - frac) * 0.75 * alphaMul);

        // Trail width & oscillation
        const wave = Math.sin(time * 12 + j * 0.5) * (1.2 + frac * 3.5);
        const w1 = [pt1.x + wave, pt1.y, pt1.z];
        const w2 = [pt2.x + wave * 0.8, pt2.y, pt2.z];

        if (line) {
          // Outer plasma trail line
          line([w1, w2], colMain, segAlpha, Math.max(0.6, 2.5 * (1 - frac)));
          // Core bright quantum thread
          line([w1, w2], colCore, segAlpha * 0.9, Math.max(0.4, 1.2 * (1 - frac)));
        }
      }""",
        """      // Manage history Ring Buffer for this craft (Zero GC churn & batched polyline ribbons)
      const MAX_TRAIL_PTS = 24;
      let ring = this.trailHistory.get(b);
      if (!ring || !ring.slots || ring.slots.length !== MAX_TRAIL_PTS) {
        ring = {
          slots: new Array(MAX_TRAIL_PTS),
          ptsBuf: new Array(MAX_TRAIL_PTS),
          head: 0,
          count: 0
        };
        for (let s = 0; s < MAX_TRAIL_PTS; s++) {
          ring.slots[s] = { x: 0, y: 0, z: 0, time: 0 };
          ring.ptsBuf[s] = [0, 0, 0];
        }
        this.trailHistory.set(b, ring);
      }

      const maxPts = Math.min(MAX_TRAIL_PTS, Math.max(6, Math.round(10 * Math.min(2.4, warpStretch))));
      const curSlot = ring.slots[ring.head];
      curSlot.x = emitterPt[0];
      curSlot.y = emitterPt[1];
      curSlot.z = emitterPt[2];
      curSlot.time = time;
      ring.head = (ring.head + 1) % MAX_TRAIL_PTS;
      ring.count = Math.min(maxPts, ring.count + 1);

      if (ring.count < 2 || !line) return;

      const colMain = trail.colors.main;
      const colCore = trail.colors.core;
      const nPts = ring.count;
      const chain = [];
      for (let j = 0; j < nPts; j++) {
        const idx = (ring.head - 1 - j + MAX_TRAIL_PTS) % MAX_TRAIL_PTS;
        const pt = ring.slots[idx];
        const frac = j / nPts;
        const wave = Math.sin(time * 10.5 + j * 0.45) * (0.9 + frac * 2.6);
        const bp = ring.ptsBuf[j];
        bp[0] = pt.x + wave;
        bp[1] = pt.y;
        bp[2] = pt.z;
        chain.push(bp);
      }

      // Draw continuous tapered 3-stage calligraphic ribbon instead of 120 disjoint segment calls
      const mid1 = Math.max(2, Math.floor(nPts * 0.38));
      const mid2 = Math.max(mid1 + 1, Math.floor(nPts * 0.72));
      line(chain.slice(0, mid1 + 1), colMain, 0.72 * alphaMul, 2.25);
      line(chain.slice(0, mid1 + 1), colCore, 0.86 * alphaMul, 1.10);
      if (nPts > mid1 + 1) {
        line(chain.slice(mid1, Math.min(nPts, mid2 + 1)), colMain, 0.44 * alphaMul, 1.45);
        line(chain.slice(mid1, Math.min(nPts, mid2 + 1)), colCore, 0.52 * alphaMul, 0.75);
      }
      if (nPts > mid2 + 1) {
        line(chain.slice(mid2), colMain, 0.20 * alphaMul, 0.85);
      }""",
        "Batched continuous calligraphic engine ribbon trails in renderCraftTrail"
    )

    # -------------------------------------------------------------------------
    # 2. cockpitPose(dt) & Frame-Rate-Independent Exponential Damping
    # -------------------------------------------------------------------------
    html = replace_exact(
        html,
        """function updateDirector(dt){
 if(cockpitMode && cockpitBlend >= 0.999){cockpitPose();captureCamPose=null;return;}""",
        """function updateDirector(dt){
 if(cockpitMode && cockpitBlend >= 0.999){cockpitPose(dt);captureCamPose=null;return;}""",
        "Pass dt into cockpitPose(dt) in updateDirector"
    )

    html = replace_exact(
        html,
        """ // 7. Smooth Target Settling
 if(!lookInit){lookSmooth[0]=lookTarget[0];lookSmooth[1]=lookTarget[1];lookSmooth[2]=lookTarget[2];lookInit=true;}
 else{
  const kk = Math.min(1, dt * 2.8);
  for(let i=0;i<3;i++){lookSmooth[i] += (lookTarget[i] - lookSmooth[i]) * kk; lookTarget[i] = lookSmooth[i];}
 }""",
        """ // 7. Smooth Target Settling (Frame-rate-independent exponential decay)
 if(!lookInit){lookSmooth[0]=lookTarget[0];lookSmooth[1]=lookTarget[1];lookSmooth[2]=lookTarget[2];lookInit=true;}
 else{
  const kk = 1 - Math.exp(-dt * 3.0);
  for(let i=0;i<3;i++){lookSmooth[i] += (lookTarget[i] - lookSmooth[i]) * kk; lookTarget[i] = lookSmooth[i];}
 }""",
        "Exponential decay in lookSmooth target settling"
    )

    html = replace_exact(
        html,
        """ if(!chaseSmoothEye){
  chaseSmoothEye = [...targetEye];
  chaseSmoothLook = [...targetLook];
 } else {
  const kEye = Math.min(1, dt * 5.5);
  const kLook = Math.min(1, dt * 4.8);
  chaseSmoothEye[0] += (targetEye[0] - chaseSmoothEye[0]) * kEye;
  chaseSmoothEye[1] += (targetEye[1] - chaseSmoothEye[1]) * kEye;
  chaseSmoothEye[2] += (targetEye[2] - chaseSmoothEye[2]) * Math.min(1, dt * 7.5);
  chaseSmoothLook[0] += (targetLook[0] - chaseSmoothLook[0]) * kLook;
  chaseSmoothLook[1] += (targetLook[1] - chaseSmoothLook[1]) * kLook;
  chaseSmoothLook[2] += (targetLook[2] - chaseSmoothLook[2]) * Math.min(1, dt * 7.0);
 }""",
        """ if(!chaseSmoothEye){
  chaseSmoothEye = [...targetEye];
  chaseSmoothLook = [...targetLook];
 } else {
  const kEye = 1 - Math.exp(-dt * 6.2);
  const kEyeZ = 1 - Math.exp(-dt * 8.8);
  const kLook = 1 - Math.exp(-dt * 5.4);
  const kLookZ = 1 - Math.exp(-dt * 8.2);
  chaseSmoothEye[0] += (targetEye[0] - chaseSmoothEye[0]) * kEye;
  chaseSmoothEye[1] += (targetEye[1] - chaseSmoothEye[1]) * kEye;
  chaseSmoothEye[2] += (targetEye[2] - chaseSmoothEye[2]) * kEyeZ;
  chaseSmoothLook[0] += (targetLook[0] - chaseSmoothLook[0]) * kLook;
  chaseSmoothLook[1] += (targetLook[1] - chaseSmoothLook[1]) * kLook;
  chaseSmoothLook[2] += (targetLook[2] - chaseSmoothLook[2]) * kLookZ;
 }""",
        "Exponential damping in getChasePose(dt)"
    )

    html = replace_exact(
        html,
        """function cockpitPose(){
 const cp = getChasePose(0.016);
 camera.eye = [...cp.eye]; camera.forward = [...cp.forward]; camera.right = [...cp.right]; camera.up = [...cp.up];
 camera.roll = cp.roll; camera.focal = cp.focal; camera.cx = cp.cx; camera.cy = cp.cy;
}""",
        """function cockpitPose(dt = 0.016){
 const cp = getChasePose(dt);
 camera.eye[0] = cp.eye[0]; camera.eye[1] = cp.eye[1]; camera.eye[2] = cp.eye[2];
 camera.forward[0] = cp.forward[0]; camera.forward[1] = cp.forward[1]; camera.forward[2] = cp.forward[2];
 camera.right[0] = cp.right[0]; camera.right[1] = cp.right[1]; camera.right[2] = cp.right[2];
 camera.up[0] = cp.up[0]; camera.up[1] = cp.up[1]; camera.up[2] = cp.up[2];
 camera.roll = cp.roll; camera.focal = cp.focal; camera.cx = cp.cx; camera.cy = cp.cy;
}""",
        "Pass real dt into cockpitPose(dt) and avoid per-frame spread allocations"
    )

    # -------------------------------------------------------------------------
    # 3. Eliminate Per-Particle RadialGradient in flush() & Cache Particle Palette
    # -------------------------------------------------------------------------
    html = replace_exact(
        html,
        """   else if(o.kind==='firefly'){const g=ctx.createRadialGradient(x,y,0,x,y,s*4);g.addColorStop(0,o.c);g.addColorStop(.23,css([218,232,153],.3));g.addColorStop(1,'rgba(218,232,153,0)');ctx.fillStyle=g;ctx.beginPath();ctx.arc(x,y,s*4,0,TAU);ctx.fill();}""",
        """   else if(o.kind==='firefly'){const spr=typeof getStarBloomSprite==='function'?getStarBloomSprite(true):null;if(spr){const r4=s*4;ctx.drawImage(spr,x-r4,y-r4,r4*2,r4*2);}else{ctx.beginPath();ctx.arc(x,y,s*1.6,0,TAU);ctx.fill();}}""",
        "Replace per-particle createRadialGradient in flush() with pre-baked bloom sprite"
    )

    html = replace_exact(
        html,
        """function updateParticles(dt){
 for(const p of particles){
  p.life+=dt;
  if(p.life>p.ttl||Math.abs(p.z-travel)>5700||(!p.isCosmic&&p.y<2))resetParticle(p);
  const pal=region(p.x,p.z);
  p.x+=(p.drift+wind.x*29+Math.sin(time*.4+p.phase)*5)*dt;
  p.z+=Math.cos(p.phase)*7*dt;
  if(!p.isCosmic)p.y-=(3+pal.wash*15+pal.shimmer*9-pal.void*1.5)*dt;
  else p.y+=Math.sin(time*.5+p.phase)*4*dt;
 }
}
function drawParticles(){
 for(const p of particles){
  const pal=region(p.x,p.z),alpha=smooth(p.life/3)*smooth((p.ttl-p.life)/5);""",
        """function updateParticles(dt){
 for(const p of particles){
  p.life+=dt;
  if(p.life>p.ttl||Math.abs(p.z-travel)>5700||(!p.isCosmic&&p.y<2))resetParticle(p);
  const pal=p.pal=region(p.x,p.z);
  p.x+=(p.drift+wind.x*29+Math.sin(time*.4+p.phase)*5)*dt;
  p.z+=Math.cos(p.phase)*7*dt;
  if(!p.isCosmic)p.y-=(3+pal.wash*15+pal.shimmer*9-pal.void*1.5)*dt;
  else p.y+=Math.sin(time*.5+p.phase)*4*dt;
 }
}
function drawParticles(){
 for(const p of particles){
  const pal=p.pal||region(p.x,p.z),alpha=smooth(p.life/3)*smooth((p.ttl-p.life)/5);""",
        "Cache particle region palette between updateParticles and drawParticles"
    )

    # -------------------------------------------------------------------------
    # 4. LivingPlanetEngine Mobile Multi-Planet Guard & Adaptive LOD Threshold
    # -------------------------------------------------------------------------
    html = replace_exact(
        html,
        """      const minLivingRad = 7.5;
      if (typeof LivingPlanetEngine !== 'undefined' && LivingPlanetEngine.enabled && rad >= minLivingRad && typeof THREE !== 'undefined') {""",
        """      const minLivingRad = (_isMobileDevice ? 13.5 : 9.0) * (1 + Math.min(1.4, Math.max(warp, WarpDrive.currentWarp) * 0.06));
      if (typeof LivingPlanetEngine !== 'undefined' && LivingPlanetEngine.enabled && rad >= minLivingRad && typeof THREE !== 'undefined') {""",
        "Adaptive minLivingRad threshold during high-speed warp and mobile distant views"
    )

    html = replace_exact(
        html,
        """      // On mobile devices, prioritize active planet and reuse cached buffer for secondary celestial bodies
      const isMob = (typeof window !== 'undefined' && window._isMobileDevice) || (typeof _isMobileDevice !== 'undefined' && _isMobileDevice);
      if (isMob && this._mobileRenderedThisFrame && this._lastRenderedId !== this.getPlanetId(m)) {
        const mCached = this.planetCache.get(this.getPlanetId(m));
        if (mCached && mCached.canvas && mCached.hasRendered) return mCached.canvas;
      }
      if (isMob) this._mobileRenderedThisFrame = true;""",
        """      // On mobile devices, prioritize primary planet and let secondary distant bodies use the 2D procedural sphere fallback
      const isMob = (typeof window !== 'undefined' && window._isMobileDevice) || (typeof _isMobileDevice !== 'undefined' && _isMobileDevice);
      if (isMob && this._mobileRenderedThisFrame && this._lastRenderedId !== this.getPlanetId(m)) {
        return null;
      }
      if (isMob) this._mobileRenderedThisFrame = true;""",
        "Prevent multi-planet shared WebGL buffer thrashing on mobile"
    )

    html = replace_exact(
        html,
        """      const refreshInterval = isMob ? 1 : (rad < 35 ? 3 : (rad < 70 ? 2 : 1));
      const shouldRenderWebGL = !model.hasRendered || (model.renderAge >= refreshInterval);""",
        """      const refreshInterval = (rad < 35 ? 3 : (rad < 70 ? 2 : 1));
      const shouldRenderWebGL = !model.hasRendered || (isMob && this._lastRenderedId !== pId) || (model.renderAge >= refreshInterval);""",
        "Enable sub-frame LOD throttling for distant planets on both mobile and desktop"
    )

    # -------------------------------------------------------------------------
    # 5. StarfieldSonar: Remove per-frame DOM queries, emoji & shadowBlur
    # -------------------------------------------------------------------------
    html = replace_exact(
        html,
        """    this.currentTarget = candidate;
    const oldBtn = document.getElementById('sf-sonar-lock-btn');
    if (oldBtn) oldBtn.remove();
    this.updateSituationCapsule(candidate);""",
        """    this.currentTarget = candidate;
    if (!this._cleanedLegacyDom) {
      this._cleanedLegacyDom = true;
      const oldBtn = document.getElementById('sf-sonar-lock-btn');
      if (oldBtn) oldBtn.remove();
      const capsule = document.getElementById('sf-sonar-capsule');
      if (capsule) capsule.remove();
    }""",
        "Eliminate per-frame getElementById calls in StarfieldSonar.update"
    )

    html = replace_exact(
        html,
        """      const msg = `[天体共振] 成功测绘 ${targetName} · 捕获未开采星核 × 1! 🌌`;""",
        """      const msg = `[天体共振] 成功测绘 ${targetName} · 捕获未开采星核 × 1 ✦`;""",
        "Replace colored emoji in StarfieldSonar toast"
    )

    html = replace_exact(
        html,
        """      const screenR = clamp((350 / q[2]) * ring.r * 0.08, 12, 280);
      c.beginPath();
      c.arc(q[0], q[1], screenR, 0, TAU);
      c.strokeStyle = `rgba(56, 189, 248, ${(ring.life * 0.7).toFixed(2)})`;
      c.lineWidth = 2.5;
      c.shadowColor = '#38bdf8';
      c.shadowBlur = 15;
      c.stroke();""",
        """      const screenR = clamp((350 / q[2]) * ring.r * 0.08, 12, 280);
      const aCore = (ring.life * 0.72).toFixed(2);
      const aHalo = (ring.life * 0.22).toFixed(2);
      c.beginPath();
      c.arc(q[0], q[1], screenR, 0, TAU);
      c.strokeStyle = `rgba(143, 216, 192, ${aHalo})`;
      c.lineWidth = 6.0;
      c.stroke();
      c.strokeStyle = `rgba(230, 237, 242, ${aCore})`;
      c.lineWidth = 1.6;
      c.stroke();""",
        "Replace shadowBlur in StarfieldSonar.draw with double-stroke holographic ring"
    )

    # -------------------------------------------------------------------------
    # 6. StarfieldInFlightExtraction: Eliminate Per-Frame innerHTML Thrash & shadowBlur
    # -------------------------------------------------------------------------
    html = replace_exact(
        html,
        """  createHUD() {
    if (typeof document === 'undefined') return;
    if (!document.getElementById('sf-inflight-extract-hud')) {
      const hud = document.createElement('div');
      hud.id = 'sf-inflight-extract-hud';
      hud.style.cssText = `
        position: fixed;
        top: calc(max(env(safe-area-inset-top, 0px), 16px) + 78px);
        right: 18px;
        z-index: 105;
        background: transparent;
        border: none;
        border-radius: 12px;
        padding: 6px 10px;
        color: #e0f2fe;
        box-shadow: none;
        backdrop-filter: none;
        -webkit-backdrop-filter: none;
        font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
        font-size: 10.5px;
        text-shadow: 0 2px 10px rgba(0,0,0,0.9);
        pointer-events: auto;
        display: none;
        transition: opacity 0.25s ease, transform 0.25s ease;
      `;
      hud.innerHTML = `
        <div style="display:flex; justify-content:space-between; align-items:center; gap:12px; margin-bottom:6px; border-bottom:1px solid rgba(56,189,248,0.2); padding-bottom:4px;">
          <span style="font-weight:700; color:#38bdf8; letter-spacing:0.05em; display:flex; align-items:center; gap:5px;">
            <span style="width:6px; height:6px; border-radius:50%; background:#38bdf8; box-shadow:0 0 6px #38bdf8;"></span>
            战术货舱
          </span>
          <span id="sf-inflight-cargo-count" style="color:#94a3b8; font-size:10px;">0 / 6</span>
        </div>
        <div id="sf-inflight-cargo-grid" style="display:grid; grid-template-columns:repeat(6, 26px); gap:5px; margin-bottom:6px;">
        </div>
        <div style="display:flex; justify-content:space-between; align-items:center; font-size:10px; color:#cbd5e1;">
          <span id="sf-inflight-gate-status" style="color:#fbbf24;">✦ 正在搜寻折跃门...</span>
          <span id="sf-inflight-loot-val" style="color:#38bdf8; font-weight:700;">0 ST</span>
        </div>
      `;
      document.body.appendChild(hud);
      this.hudElement = hud;
    }

    // No blocking bottom button created; automatic gravitational tractor beam & [E] hotkey
    const existingLootBtn = document.getElementById('sf-inflight-loot-btn');
    if (existingLootBtn) existingLootBtn.remove();
    this.lootBtnElement = null;
  },""",
        """  createHUD() {
    if (typeof document === 'undefined') return;
    let hud = document.getElementById('sf-inflight-extract-hud');
    if (!hud) {
      hud = document.createElement('div');
      hud.id = 'sf-inflight-extract-hud';
      hud.style.cssText = `
        position: fixed;
        top: calc(max(env(safe-area-inset-top, 0px), 16px) + 84px);
        right: calc(env(safe-area-inset-right, 0px) + 22px);
        z-index: 105;
        background: rgba(6, 9, 14, 0.72);
        border-top: 1px solid rgba(230, 237, 242, 0.22);
        border-bottom: 1px solid rgba(230, 237, 242, 0.10);
        border-radius: 0;
        padding: 7px 10px;
        color: rgba(230, 237, 242, 0.88);
        font-family: var(--ui-mono, ui-monospace, SFMono-Regular, Menlo, monospace);
        font-size: 9px;
        letter-spacing: 0.16em;
        font-variant-numeric: tabular-nums;
        text-shadow: 0 1px 10px rgba(0,0,0,0.92);
        pointer-events: auto;
        display: none;
      `;
      hud.innerHTML = `
        <div style="display:flex; justify-content:space-between; align-items:center; gap:12px; margin-bottom:6px; border-bottom:1px solid rgba(230,237,242,0.12); padding-bottom:4px;">
          <span style="font-weight:500; color:rgba(230,237,242,0.72); letter-spacing:0.22em;">CARGO BAY // 战术货舱</span>
          <span id="sf-inflight-cargo-count" style="color:rgba(230,237,242,0.52); font-size:8.5px;">0 / 6</span>
        </div>
        <div id="sf-inflight-cargo-grid" style="display:grid; grid-template-columns:repeat(6, 24px); gap:4px; margin-bottom:6px;">
        </div>
        <div style="display:flex; justify-content:space-between; align-items:center; font-size:8.5px; color:rgba(230,237,242,0.62);">
          <span id="sf-inflight-gate-status" style="color:rgba(244,208,111,0.82);">✦ 正在搜寻折跃门...</span>
          <span id="sf-inflight-loot-val" style="color:rgba(230,237,242,0.88); font-weight:500;">0 ST</span>
        </div>
      `;
      document.body.appendChild(hud);
    }
    this.hudElement = hud;
    this._cCountEl = document.getElementById('sf-inflight-cargo-count');
    this._gridEl = document.getElementById('sf-inflight-cargo-grid');
    this._valEl = document.getElementById('sf-inflight-loot-val');
    this._gateEl = document.getElementById('sf-inflight-gate-status');

    const existingLootBtn = document.getElementById('sf-inflight-loot-btn');
    if (existingLootBtn) existingLootBtn.remove();
    this.lootBtnElement = null;
  },""",
        "Editorial instrument styling and cached DOM references in StarfieldInFlightExtraction.createHUD"
    )

    html = replace_exact(
        html,
        """      const lootTable = [
        { name: '高维先驱遗物', icon: '🔮', value: 950, tier: 'legendary' },
        { name: '反物质湮灭核心', icon: '⚛️', value: 880, tier: 'legendary' },
        { name: '暗物质折跃燃料', icon: '🌌', value: 620, tier: 'epic' },
        { name: '先驱聚能晶核', icon: '💎', value: 560, tier: 'epic' },
        { name: '量子跃迁线圈', icon: '🌀', value: 420, tier: 'rare' },
        { name: '高维星图磁盘', icon: '💾', value: 360, tier: 'rare' },
        { name: '精炼复合装甲板', icon: '🛡️', value: 240, tier: 'uncommon' },
        { name: '离子推进废料', icon: '🔋', value: 160, tier: 'common' }
      ];""",
        """      const lootTable = [
        { name: '高维先驱遗物', icon: '✦', value: 950, tier: 'legendary' },
        { name: '反物质湮灭核心', icon: '⊕', value: 880, tier: 'legendary' },
        { name: '暗物质折跃燃料', icon: '♃', value: 620, tier: 'epic' },
        { name: '先驱聚能晶核', icon: '♄', value: 560, tier: 'epic' },
        { name: '量子跃迁线圈', icon: '♂', value: 420, tier: 'rare' },
        { name: '高维星图磁盘', icon: '♀', value: 360, tier: 'rare' },
        { name: '精炼复合装甲板', icon: '☿', value: 240, tier: 'uncommon' },
        { name: '离子推进废料', icon: '•', value: 160, tier: 'common' }
      ];""",
        "Replace colored loot emojis with astronomical geometric glyphs"
    )

    html = replace_exact(
        html,
        """  updateHUD(leadPos) {
    const hud = this.hudElement || document.getElementById('sf-inflight-extract-hud');
    const lootBtn = this.lootBtnElement || document.getElementById('sf-inflight-loot-btn');
    if (!hud) return;

    const isNonCruise = ((typeof currentMode !== 'undefined' && currentMode !== 'cruise') || (typeof window !== 'undefined' && window.currentMode && window.currentMode !== 'cruise'));
    if (isNonCruise) {
      hud.style.display = 'none';
      return;
    }

    const hasCargo = this.cargo.length > 0;
    const nearTarget = !!this.salvageTarget;
    const isExtractMode = (typeof currentMode !== 'undefined' && currentMode === 'extract');

    if (hasCargo || nearTarget || isExtractMode) {
      hud.style.display = 'block';
      const cCount = document.getElementById('sf-inflight-cargo-count');
      if (cCount) cCount.textContent = `${this.cargo.length} / ${this.maxCargo}`;

      const grid = document.getElementById('sf-inflight-cargo-grid');
      if (grid) {
        let slotsHtml = '';
        for (let i = 0; i < this.maxCargo; i++) {
          const item = this.cargo[i];
          if (item) {
            const borderColor = item.tier === 'legendary' ? '#fbbf24' : (item.tier === 'epic' ? '#c084fc' : (item.tier === 'rare' ? '#38bdf8' : '#94a3b8'));
            slotsHtml += `<div style="width:26px; height:26px; border-radius:6px; border:1px solid ${borderColor}; background:rgba(15,23,42,0.8); display:flex; align-items:center; justify-content:center; font-size:13px;" title="${item.name} (+${item.value} ST)">${item.icon}</div>`;
          } else {
            slotsHtml += `<div style="width:26px; height:26px; border-radius:6px; border:1px dashed rgba(148,163,184,0.3); background:rgba(15,23,42,0.4);"></div>`;
          }
        }
        grid.innerHTML = slotsHtml;
      }

      let totalVal = 0;
      for (const c of this.cargo) totalVal += c.value;
      const valEl = document.getElementById('sf-inflight-loot-val');
      if (valEl) valEl.textContent = `+${totalVal} ST`;

      const gateStatus = document.getElementById('sf-inflight-gate-status');
      if (gateStatus) {
        if (this.evacGate && !this.evacGate.evacuated) {
          const gDist = Math.round(Math.hypot(this.evacGate.x - leadPos[0], this.evacGate.y - leadPos[1], this.evacGate.z - leadPos[2]));
          if (this.evacGate.progress > 0) {
            gateStatus.innerHTML = `<span style="color:#4ade80;">✦ 折跃撤离中 ${Math.round(this.evacGate.progress * 100)}%</span>`;
          } else {
            gateStatus.innerHTML = `<span style="color:#fbbf24;">✦ 撤离门: ${gDist}m</span>`;
          }
        } else {
          gateStatus.textContent = '✦ 搜寻撤离门中...';
        }
      }
    } else {
      hud.style.display = 'none';
    }

    // Clean unobstructed HUD: No bottom button
    if (lootBtn) lootBtn.remove();
    this.lootBtnElement = null;
  },""",
        """  updateHUD(leadPos) {
    const hud = this.hudElement || (this.hudElement = document.getElementById('sf-inflight-extract-hud'));
    if (!hud) return;

    const isNonCruise = ((typeof currentMode !== 'undefined' && currentMode !== 'cruise') || (typeof window !== 'undefined' && window.currentMode && window.currentMode !== 'cruise'));
    const hasCargo = this.cargo.length > 0;
    const nearTarget = !!this.salvageTarget;
    const isExtractMode = (typeof currentMode !== 'undefined' && currentMode === 'extract');
    const shouldShow = !isNonCruise && (hasCargo || nearTarget || isExtractMode);

    if (!shouldShow) {
      if (this._lastHudVis !== false) {
        this._lastHudVis = false;
        hud.style.display = 'none';
      }
      return;
    }

    if (this._lastHudVis !== true) {
      this._lastHudVis = true;
      hud.style.display = 'block';
    }

    // Dirty-checked cargo slot update (ONLY rebuilds innerHTML when cargo items change)
    let cargoKey = `${this.cargo.length}:`;
    for (let i = 0; i < this.cargo.length; i++) cargoKey += this.cargo[i].name + '|';
    if (this._lastCargoKey !== cargoKey) {
      this._lastCargoKey = cargoKey;
      const cCount = this._cCountEl || (this._cCountEl = document.getElementById('sf-inflight-cargo-count'));
      if (cCount) cCount.textContent = `${this.cargo.length} / ${this.maxCargo}`;

      const grid = this._gridEl || (this._gridEl = document.getElementById('sf-inflight-cargo-grid'));
      if (grid) {
        let slotsHtml = '';
        for (let i = 0; i < this.maxCargo; i++) {
          const item = this.cargo[i];
          if (item) {
            const borderColor = item.tier === 'legendary' ? 'rgba(244,208,111,0.72)' : (item.tier === 'epic' ? 'rgba(200,180,245,0.65)' : (item.tier === 'rare' ? 'rgba(143,216,192,0.65)' : 'rgba(230,237,242,0.35)'));
            slotsHtml += `<div style="width:24px; height:24px; border-radius:0; border:1px solid ${borderColor}; background:rgba(230,237,242,0.04); display:flex; align-items:center; justify-content:center; font-size:11px; color:rgba(230,237,242,0.9);" title="${item.name} (+${item.value} ST)">${item.icon}</div>`;
          } else {
            slotsHtml += `<div style="width:24px; height:24px; border-radius:0; border:1px solid rgba(230,237,242,0.12); background:rgba(230,237,242,0.015);"></div>`;
          }
        }
        grid.innerHTML = slotsHtml;
      }

      let totalVal = 0;
      for (const c of this.cargo) totalVal += c.value;
      const valEl = this._valEl || (this._valEl = document.getElementById('sf-inflight-loot-val'));
      if (valEl) valEl.textContent = `+${totalVal} ST`;
    }

    const gateStatus = this._gateEl || (this._gateEl = document.getElementById('sf-inflight-gate-status'));
    if (gateStatus) {
      let nextText = '✦ 搜寻撤离门中...';
      let nextColor = 'rgba(230,237,242,0.52)';
      if (this.evacGate && !this.evacGate.evacuated) {
        if (this.evacGate.progress > 0) {
          nextText = `✦ 折跃撤离中 ${Math.round(this.evacGate.progress * 100)}%`;
          nextColor = 'rgba(143,216,192,0.92)';
        } else {
          const gDistQ = Math.round(Math.hypot(this.evacGate.x - leadPos[0], this.evacGate.y - leadPos[1], this.evacGate.z - leadPos[2]) / 20) * 20;
          nextText = `✦ 撤离门: ${gDistQ}m`;
          nextColor = 'rgba(244,208,111,0.85)';
        }
      }
      if (this._lastGateText !== nextText) {
        this._lastGateText = nextText;
        gateStatus.textContent = nextText;
      }
      if (this._lastGateColor !== nextColor) {
        this._lastGateColor = nextColor;
        gateStatus.style.color = nextColor;
      }
    }
  },""",
        "Eliminate per-frame innerHTML & DOM layout thrashing in StarfieldInFlightExtraction.updateHUD"
    )

    # Remove shadowBlur in StarfieldInFlightExtraction render methods
    html = replace_exact(
        html,
        """      c.strokeStyle = 'rgba(56, 189, 248, 0.88)';
      c.lineWidth = 2.4;
      c.setLineDash([8, 4]);
      c.shadowColor = '#38bdf8';
      c.shadowBlur = 14;
      c.stroke();""",
        """      c.strokeStyle = 'rgba(143, 216, 192, 0.82)';
      c.lineWidth = 1.8;
      c.setLineDash([8, 4]);
      c.stroke();""",
        "Remove shadowBlur in tractor beam stroke"
    )

    html = replace_exact(
        html,
        """    c.fillStyle = '#f43f5e';
    c.shadowColor = '#f43f5e';
    c.shadowBlur = 10;
    c.fill();
    c.shadowBlur = 0;""",
        """    c.fillStyle = '#f43f5e';
    c.fill();""",
        "Remove shadowBlur in renderPirate"
    )

    html = replace_exact(
        html,
        """    c.strokeStyle = l.color;
    c.globalAlpha = alpha;
    c.lineWidth = 2.4;
    c.shadowColor = l.color;
    c.shadowBlur = 12;
    c.stroke();""",
        """    c.strokeStyle = l.color;
    c.globalAlpha = alpha * 0.35;
    c.lineWidth = 5.0;
    c.stroke();
    c.globalAlpha = alpha;
    c.lineWidth = 2.0;
    c.stroke();""",
        "Replace shadowBlur in renderLaser with double-stroke"
    )

    html = replace_exact(
        html,
        """    c.fillStyle = `rgba(251, 146, 60, ${(alpha * 0.5).toFixed(2)})`;
    c.shadowColor = '#fb923c';
    c.shadowBlur = 16;
    c.fill();""",
        """    c.fillStyle = `rgba(251, 146, 60, ${(alpha * 0.45).toFixed(2)})`;
    c.fill();""",
        "Remove shadowBlur in renderBurst"
    )

    html = replace_exact(
        html,
        """    c.strokeStyle = 'rgba(251, 191, 36, 0.88)';
    c.lineWidth = 2.8;
    c.shadowColor = '#fbbf24';
    c.shadowBlur = 20;
    c.stroke();

    c.beginPath();
    c.arc(0, 0, gR * 0.62, 0, TAU);
    c.strokeStyle = 'rgba(168, 85, 247, 0.82)';
    c.lineWidth = 2.2;
    c.shadowColor = '#a855f7';
    c.shadowBlur = 16;
    c.stroke();
    c.shadowBlur = 0;""",
        """    c.strokeStyle = 'rgba(244, 208, 111, 0.24)';
    c.lineWidth = 6.5;
    c.stroke();
    c.strokeStyle = 'rgba(244, 208, 111, 0.86)';
    c.lineWidth = 2.0;
    c.stroke();

    c.beginPath();
    c.arc(0, 0, gR * 0.62, 0, TAU);
    c.strokeStyle = 'rgba(180, 160, 235, 0.76)';
    c.lineWidth = 1.6;
    c.stroke();""",
        "Replace shadowBlur in renderEvacGate with double-stroke"
    )

    html = replace_exact(
        html,
        """      c.strokeStyle = `rgba(56, 189, 248, ${(this.fleetShieldFlare * (0.8 + shieldLvl * 0.04)).toFixed(2)})`;
      c.lineWidth = 2.5 + shieldLvl * 0.7;
      c.shadowColor = '#38bdf8';
      c.shadowBlur = 14 + shieldLvl * 3.5;
      c.stroke();""",
        """      c.strokeStyle = `rgba(143, 216, 192, ${(this.fleetShieldFlare * 0.25).toFixed(2)})`;
      c.lineWidth = 6.0 + shieldLvl;
      c.stroke();
      c.strokeStyle = `rgba(230, 237, 242, ${(this.fleetShieldFlare * 0.82).toFixed(2)})`;
      c.lineWidth = 1.8 + shieldLvl * 0.4;
      c.stroke();""",
        "Replace shadowBlur in fleetShieldFlare with double-stroke"
    )

    # -------------------------------------------------------------------------
    # 7. StarfieldFuelEngine.updateHUD: Dirty-Check Cache & Editorial Styling
    # -------------------------------------------------------------------------
    html = replace_exact(
        html,
        """  updateHUD() {
    let hud = document.getElementById('sf-fuel-hud');
    if (!hud && typeof document !== 'undefined') {
      hud = document.createElement('div');
      hud.id = 'sf-fuel-hud';
      hud.className = 'sf-fuel-gauge';
      hud.title = '反物质燃料储备 · 点击打开装备升级';
      hud.innerHTML = '<span style="font-size:11px; color:#38bdf8;">✦</span><div class="sf-fuel-bar"><div id="sf-hud-fuel-fill" class="sf-fuel-fill"></div></div><span id="sf-hud-fuel-text" class="sf-fuel-label">燃料 100%</span>';
      hud.addEventListener('click', () => {
        if (window.StarfieldShipUpgrades) window.StarfieldShipUpgrades.toggleModal();
      });
      const anchor = document.getElementById('camera-hud') || document.body;
      anchor.appendChild(hud);
    }

    const el = document.getElementById('sf-hud-fuel-fill');
    const txt = document.getElementById('sf-hud-fuel-text');
    const pct = Math.round((this.fuel / Math.max(1, this.maxFuel)) * 100);
    if (el) {
      el.style.width = `${pct}%`;
      if (this.isDrifting) {
        el.style.background = 'linear-gradient(90deg, #f59e0b, #fbbf24)';
      } else if (pct < 25) {
        el.style.background = 'linear-gradient(90deg, #ef4444, #f87171)';
      } else {
        el.style.background = 'linear-gradient(90deg, #06b6d4, #38bdf8)';
      }
    }
    if (txt) {
      txt.textContent = this.isDrifting ? `微速漂流 ${pct}%` : `燃料 ${pct}%`;
    }
  }""",
        """  updateHUD() {
    const pct = Math.round((this.fuel / Math.max(1, this.maxFuel)) * 100);
    if (this._hudEl && this._lastPct === pct && this._lastDrift === this.isDrifting) return;
    this._lastPct = pct;
    this._lastDrift = this.isDrifting;

    let hud = this._hudEl || document.getElementById('sf-fuel-hud');
    if (!hud && typeof document !== 'undefined') {
      hud = document.createElement('div');
      hud.id = 'sf-fuel-hud';
      hud.className = 'sf-fuel-gauge';
      hud.title = '反物质燃料储备 · 点击打开装备升级';
      hud.innerHTML = '<span class="sf-fuel-k">FUEL</span><div class="sf-fuel-bar"><div id="sf-hud-fuel-fill" class="sf-fuel-fill"></div></div><span id="sf-hud-fuel-text" class="sf-fuel-label">100%</span>';
      hud.addEventListener('click', () => {
        if (window.StarfieldShipUpgrades) window.StarfieldShipUpgrades.toggleModal();
      });
      const anchor = document.getElementById('camera-hud') || document.body;
      anchor.appendChild(hud);
      this._hudEl = hud;
      this._fillEl = document.getElementById('sf-hud-fuel-fill');
      this._txtEl = document.getElementById('sf-hud-fuel-text');
    }

    const el = this._fillEl || (this._fillEl = document.getElementById('sf-hud-fuel-fill'));
    const txt = this._txtEl || (this._txtEl = document.getElementById('sf-hud-fuel-text'));
    if (el) {
      el.style.width = `${pct}%`;
      if (this.isDrifting || pct < 25) {
        el.style.background = 'rgba(244, 208, 111, 0.85)';
      } else {
        el.style.background = 'rgba(230, 237, 242, 0.72)';
      }
    }
    if (txt) {
      txt.textContent = this.isDrifting ? `DRIFT ${pct}%` : `${pct}%`;
    }
  }""",
        "Add dirty-checking cache & monochrome editorial styling to StarfieldFuelEngine.updateHUD"
    )

    # -------------------------------------------------------------------------
    # 8. StarfieldOrbitalMechanics: Cache Descent Button & Remove shadowBlur
    # -------------------------------------------------------------------------
    html = replace_exact(
        html,
        """    // Unobstructed HUD: ensure no bottom probe button exists
    const pBtn = document.getElementById('sf-inflight-probe-btn');
    if (pBtn) pBtn.remove();
    this.updateDescentCorridor(dt);
  },

  updateDescentCorridor(dt) {
    if ((typeof currentMode !== 'undefined' && currentMode !== 'cruise') || (window.currentMode && window.currentMode !== 'cruise')) {
      const btn = document.getElementById('sf-descent-btn');
      if (btn) btn.classList.remove('show');
      return;
    }
    const ap = this.activePlanet || (window.SFProbe && window.SFProbe.nearest && window.SFProbe.nearest());
    const dist = ap ? (ap.dist !== undefined ? ap.dist : (ap.d !== undefined ? ap.d : 99999)) : 99999;
    let btn = document.getElementById('sf-descent-btn');
    if (!btn && typeof document !== 'undefined') {
      btn = document.createElement('button');
      btn.id = 'sf-descent-btn';
      btn.className = 'sf-descent-corridor-btn';
      btn.innerHTML = '✦ 降轨穿云 · DESCENT ✦';
      btn.setAttribute('aria-label', '进入近地走廊');
      document.body.appendChild(btn);
      btn.addEventListener('click', (e) => {
        e.stopPropagation();
        this.triggerDescentTransition(ap);
      });
      btn.addEventListener('pointerdown', (e) => e.stopPropagation());
    }
    const flightActive = (typeof started !== 'undefined' && started) || (window.Starfield && window.Starfield.getState && window.Starfield.getState().started);
    if (btn) {
      if (dist < 4500 && flightActive && window.SFSurface && !window.SFSurface.isActive()) {
        btn.classList.add('show');
      } else {
        btn.classList.remove('show');
      }
    }
  },""",
        """    if (!this._cleanedProbeBtn) {
      this._cleanedProbeBtn = true;
      const pBtn = document.getElementById('sf-inflight-probe-btn');
      if (pBtn) pBtn.remove();
    }
    this.updateDescentCorridor(dt);
  },

  updateDescentCorridor(dt) {
    const isNonCruise = (typeof currentMode !== 'undefined' && currentMode !== 'cruise') || (window.currentMode && window.currentMode !== 'cruise');
    if (isNonCruise) {
      if (this._lastDescentShow) {
        this._lastDescentShow = false;
        const btn = this._descentBtn || document.getElementById('sf-descent-btn');
        if (btn) btn.classList.remove('show');
      }
      return;
    }
    const ap = this.activePlanet || (window.SFProbe && window.SFProbe.nearest && window.SFProbe.nearest());
    this._currentDescentPlanet = ap;
    const dist = ap ? (ap.dist !== undefined ? ap.dist : (ap.d !== undefined ? ap.d : 99999)) : 99999;
    const flightActive = (typeof started !== 'undefined' && started) || (window.Starfield && window.Starfield.getState && window.Starfield.getState().started);
    const shouldShow = !!(dist < 4500 && flightActive && window.SFSurface && !window.SFSurface.isActive());

    if (shouldShow && !this._descentBtn && typeof document !== 'undefined') {
      let btn = document.getElementById('sf-descent-btn');
      if (!btn) {
        btn = document.createElement('button');
        btn.id = 'sf-descent-btn';
        btn.className = 'sf-descent-corridor-btn';
        btn.innerHTML = '✦ 降轨穿云 · DESCENT ↗';
        btn.setAttribute('aria-label', '进入近地走廊');
        document.body.appendChild(btn);
        btn.addEventListener('click', (e) => {
          e.stopPropagation();
          this.triggerDescentTransition(this._currentDescentPlanet);
        });
        btn.addEventListener('pointerdown', (e) => e.stopPropagation());
      }
      this._descentBtn = btn;
    }

    if (this._lastDescentShow !== shouldShow) {
      this._lastDescentShow = shouldShow;
      const btn = this._descentBtn || (this._descentBtn = document.getElementById('sf-descent-btn'));
      if (btn) btn.classList.toggle('show', shouldShow);
    }
  },""",
        "Cache _descentBtn and _lastDescentShow in updateDescentCorridor"
    )

    html = replace_exact(
        html,
        """      c.strokeStyle = 'rgba(120, 200, 245, 0.34)';
      c.lineWidth = 1.1;
      c.setLineDash([5, 7]);
      c.lineDashOffset = -(performance.now() * 0.02) % 12;
      c.shadowColor = 'rgba(56, 189, 248, 0.35)';
      c.shadowBlur = 5;
      c.stroke();""",
        """      c.strokeStyle = 'rgba(230, 237, 242, 0.36)';
      c.lineWidth = 1.1;
      c.setLineDash([5, 7]);
      c.lineDashOffset = -(performance.now() * 0.02) % 12;
      c.stroke();""",
        "Remove shadowBlur in slingshot trajectory arc"
    )

    html = replace_exact(
        html,
        """        c.beginPath();
        c.arc(lq[0], lq[1] - 4, 36, Math.PI * 0.8, Math.PI * 2.2);
        c.strokeStyle = pColor;
        c.lineWidth = 3.5;
        c.shadowColor = pColor;
        c.shadowBlur = 18;
        c.stroke();""",
        """        c.beginPath();
        c.arc(lq[0], lq[1] - 4, 36, Math.PI * 0.8, Math.PI * 2.2);
        c.strokeStyle = pColor;
        c.lineWidth = 2.4;
        c.stroke();""",
        "Remove shadowBlur in atmospheric entry plasma bow arc"
    )

    html = replace_exact(
        html,
        """        c.strokeStyle = 'rgba(244, 63, 94, 0.88)';
        c.lineWidth = 2.5;
        c.shadowColor = '#f43f5e';
        c.shadowBlur = 12;
        c.stroke();
        c.restore();
      }

      const headQ = project([pr.x, pr.y, pr.z]);
      if (headQ && headQ[2] > 0) {
        c.save();
        c.translate(headQ[0], headQ[1]);
        c.rotate(pr.spin || 0);

        // Stylized Orbital Bird Probe Satellite
        c.beginPath();
        c.arc(0, 0, 5, 0, TAU);
        c.fillStyle = '#ffedd5';
        c.shadowColor = '#fb923c';
        c.shadowBlur = 12;
        c.fill();""",
        """        c.strokeStyle = 'rgba(244, 208, 111, 0.78)';
        c.lineWidth = 1.8;
        c.stroke();
        c.restore();
      }

      const headQ = project([pr.x, pr.y, pr.z]);
      if (headQ && headQ[2] > 0) {
        c.save();
        c.translate(headQ[0], headQ[1]);
        c.rotate(pr.spin || 0);

        // Stylized Orbital Bird Probe Satellite
        c.beginPath();
        c.arc(0, 0, 5, 0, TAU);
        c.fillStyle = '#ffedd5';
        c.fill();""",
        "Remove shadowBlur in orbital probe trail and head"
    )

    html = replace_exact(
        html,
        """            ctx.beginPath();
            ctx.arc(q[0], q[1], sR, 0, TAU);
            ctx.strokeStyle = `rgba(168, 85, 247, ${alpha.toFixed(2)})`;
            ctx.lineWidth = 3.0;
            ctx.shadowColor = '#c084fc';
            ctx.shadowBlur = 16;
            ctx.stroke();""",
        """            ctx.beginPath();
            ctx.arc(q[0], q[1], sR, 0, TAU);
            ctx.strokeStyle = `rgba(230, 237, 242, ${(alpha * 0.25).toFixed(2)})`;
            ctx.lineWidth = 6.5;
            ctx.stroke();
            ctx.strokeStyle = `rgba(244, 208, 111, ${alpha.toFixed(2)})`;
            ctx.lineWidth = 2.0;
            ctx.stroke();""",
        "Replace shadowBlur in gravitational shockwave queue3D with double-stroke"
    )

    # -------------------------------------------------------------------------
    # 9. updatePoem, drawRoute & updateUI: Eliminate Forced Synchronous Layout
    # -------------------------------------------------------------------------
    html = replace_exact(
        html,
        """function updatePoem(dt){
 if(!started||paused)return;
 if(poemIndex===-1){if(flightTime>4)showPoem();return;}
 poemAge+=dt;if(poemAge>poemDuration+2)showPoem();
 poemOpacity=smooth(poemAge/2.2)*smooth((poemDuration-poemAge)/2.5);
 $('poem').style.opacity=poemsEnabled?poemOpacity:0;
}
function toast(text,duration=4){$('toast').textContent=text;toastUntil=time+duration;$('toast').style.opacity=1;}
window.toast = toast;
const routeCtx=$('route').getContext('2d');
function drawRoute(){
 const el=$('route'),w=el.clientWidth,h=el.clientHeight;
 if(el.width!==Math.round(w*DPR)||el.height!==Math.round(h*DPR)){el.width=Math.round(w*DPR);el.height=Math.round(h*DPR);}
 routeCtx.setTransform(DPR,0,0,DPR,0,0);routeCtx.clearRect(0,0,w,h);
 const y=x=>h*.56+Math.sin(x/w*4.7+travel*.00023)*h*.13;
 routeCtx.strokeStyle=css(currentPalette.ink,.22);routeCtx.lineWidth=.7;routeCtx.beginPath();for(let x=0;x<=w;x+=2){if(x===0)routeCtx.moveTo(x,y(x));else routeCtx.lineTo(x,y(x));}routeCtx.stroke();
 for(let i=0;i<5;i++){const x=(i+.5)/5*w;routeCtx.fillStyle=css(currentPalette.ink,i===currentPalette.index?.55:.16);routeCtx.beginPath();routeCtx.arc(x,y(x),i===currentPalette.index?2.5:1.6,0,TAU);routeCtx.fill();}
 const x=mod(travel,SEGMENT*5)/(SEGMENT*5)*w;routeCtx.strokeStyle=css(currentPalette.ink,.55);routeCtx.beginPath();routeCtx.arc(x,y(x),5,0,TAU);routeCtx.stroke();
}
function updateUI(){
 const p=currentPalette,style=rawStyles[p.index],list=plans.get(cycle),lens=list[shot],progress=shotTime/lens.duration;
 root.style.setProperty('--ink',css(p.ink));root.style.setProperty('--paper',css(p.paper));root.style.setProperty('--line',css(p.ink,.20));root.style.setProperty('--soft',css(p.paper,.70));
 $('camera-name').textContent=cockpitMode?'星海引航':autoCamera?lens.name:'随风而观';$('camera-mode-label').textContent=cockpitMode?'FLAGSHIP CHASE':autoCamera?(progress>.44?'AUTO · IN TRANSIT':'AUTO FLIGHT'):'FREE FLIGHT';$('variation').textContent=`VAR ${String(cycle+1).padStart(2,'0')}`;
 $('camera-progress').firstElementChild.style.transform=`scaleX(${progress})`;
 const effW = Math.max(warp, WarpDrive.currentWarp);
   const spdReadout = effW > 1 ? `  /  WARP ${(1 + effW/2).toFixed(1)}c` : '';
   $('flight-stats').textContent=`${(travel/1000).toFixed(1)} KLY${spdReadout}  /  ${FLEET_COUNT} CRAFT`;
 $('region-name').textContent=`${String(p.index+1).padStart(2,'0')}  ${style.name} / ${style.en}`;
 $('region-caption').textContent=style.caption;
 $('distance').textContent=`${((travel-departure)/1000).toFixed(1).padStart(5,'0')} KM`;
 const seconds=Math.floor(flightTime);$('flight-time').textContent=`${String(Math.floor(seconds/60)).padStart(2,'0')}:${String(seconds%60).padStart(2,'0')}`;
 if(time>toastUntil)$('toast').style.opacity=0;
 $('hint').style.opacity=started&&flightTime<6&&!paused?.42:0;
 drawRoute();sound.update();
}""",
        """let _lastPoemOp = -1;
function updatePoem(dt){
 if(!started||paused)return;
 if(poemIndex===-1){if(flightTime>4)showPoem();return;}
 poemAge+=dt;if(poemAge>poemDuration+2)showPoem();
 poemOpacity=smooth(poemAge/2.2)*smooth((poemDuration-poemAge)/2.5);
 const nextOp=poemsEnabled?Math.round(poemOpacity*250)/250:0;
 if(nextOp!==_lastPoemOp){_lastPoemOp=nextOp;$('poem').style.opacity=nextOp;}
}
let _lastToastOp = 0;
function toast(text,duration=4){$('toast').textContent=text;toastUntil=time+duration;_lastToastOp=1;$('toast').style.opacity=1;}
window.toast = toast;
const routeCtx=$('route').getContext('2d');
let _routeW=0,_routeH=0,_routeResizeDirty=true;
function drawRoute(){
 const el=$('route');
 if(_routeResizeDirty||!_routeW||!_routeH){
  _routeW=el.clientWidth||180;_routeH=el.clientHeight||28;_routeResizeDirty=false;
 }
 const w=_routeW,h=_routeH;
 if(el.width!==Math.round(w*DPR)||el.height!==Math.round(h*DPR)){el.width=Math.round(w*DPR);el.height=Math.round(h*DPR);}
 routeCtx.setTransform(DPR,0,0,DPR,0,0);routeCtx.clearRect(0,0,w,h);
 const y=x=>h*.56+Math.sin(x/w*4.7+travel*.00023)*h*.13;
 routeCtx.strokeStyle=css(currentPalette.ink,.22);routeCtx.lineWidth=.7;routeCtx.beginPath();for(let x=0;x<=w;x+=2){if(x===0)routeCtx.moveTo(x,y(x));else routeCtx.lineTo(x,y(x));}routeCtx.stroke();
 for(let i=0;i<5;i++){const x=(i+.5)/5*w;routeCtx.fillStyle=css(currentPalette.ink,i===currentPalette.index?.55:.16);routeCtx.beginPath();routeCtx.arc(x,y(x),i===currentPalette.index?2.5:1.6,0,TAU);routeCtx.fill();}
 const x=mod(travel,SEGMENT*5)/(SEGMENT*5)*w;routeCtx.strokeStyle=css(currentPalette.ink,.55);routeCtx.beginPath();routeCtx.arc(x,y(x),5,0,TAU);routeCtx.stroke();
}
const _uiCache={};
function _setTxt(id,val){if(_uiCache[id]!==val){_uiCache[id]=val;const el=$(id);if(el)el.textContent=val;}}
function _setRootProp(k,val){if(_uiCache[k]!==val){_uiCache[k]=val;root.style.setProperty(k,val);}}
function updateUI(){
 // Draw route BEFORE any DOM mutations so reading clientWidth never triggers Forced Synchronous Layout
 drawRoute();
 const p=currentPalette,style=rawStyles[p.index],list=plans.get(cycle),lens=list[shot],progress=shotTime/lens.duration;
 _setRootProp('--ink',css(p.ink));_setRootProp('--paper',css(p.paper));_setRootProp('--line',css(p.ink,.20));_setRootProp('--soft',css(p.paper,.70));
 _setTxt('camera-name',cockpitMode?'星海引航':autoCamera?lens.name:'随风而观');
 _setTxt('camera-mode-label',cockpitMode?'FLAGSHIP CHASE':autoCamera?(progress>.44?'AUTO · IN TRANSIT':'AUTO FLIGHT'):'FREE FLIGHT');
 _setTxt('variation',`VAR ${String(cycle+1).padStart(2,'0')}`);
 const progQ=`scaleX(${progress.toFixed(3)})`;
 if(_uiCache._camProg!==progQ){_uiCache._camProg=progQ;$('camera-progress').firstElementChild.style.transform=progQ;}
 const effW = Math.max(warp, WarpDrive.currentWarp);
 const spdReadout = effW > 1 ? `  /  WARP ${(1 + effW/2).toFixed(1)}c` : '';
 _setTxt('flight-stats',`${(travel/1000).toFixed(1)} KLY${spdReadout}  /  ${FLEET_COUNT} CRAFT`);
 _setTxt('region-name',`${String(p.index+1).padStart(2,'0')}  ${style.name} / ${style.en}`);
 _setTxt('region-caption',style.caption);
 _setTxt('distance',`${((travel-departure)/1000).toFixed(1).padStart(5,'0')} KM`);
 const seconds=Math.floor(flightTime);
 _setTxt('flight-time',`${String(Math.floor(seconds/60)).padStart(2,'0')}:${String(seconds%60).padStart(2,'0')}`);
 if(time>toastUntil&&_lastToastOp!==0){_lastToastOp=0;$('toast').style.opacity=0;}
 const hintOp=started&&flightTime<6&&!paused?.42:0;
 if(_uiCache._hintOp!==hintOp){_uiCache._hintOp=hintOp;$('hint').style.opacity=hintOp;}
 sound.update();
}""",
        "Dirty-check updatePoem, drawRoute, and updateUI to eliminate Forced Synchronous Layout"
    )

    # Mark _routeResizeDirty = true in resize()
    html = replace_exact(
        html,
        """ updateDirector(.016);drawRoute();
}""",
        """ _routeResizeDirty=true;updateDirector(.016);drawRoute();
}""",
        "Invalidate cached route dimensions on window resize"
    )

    # -------------------------------------------------------------------------
    # 10. frame(now): EMA realDt Smoothing, Modal Cache, & Docking Prompt Cache
    # -------------------------------------------------------------------------
    html = replace_exact(
        html,
        """ const realDt=Math.min(.05,Math.max(.001,(now-last)/1000));last=now;
 stepDeparture(realDt);
 // Any sheet on top of the scene outranks the comms card (z 1000 > 400).
 // NB: the module object is window.Starfield; a bare `Engine` is out of scope
 // here and threw on every frame, which froze the scene.
 {const _S=window.Starfield;const _mo=!!(_S&&_S.isModalOpen&&_S.isModalOpen());
  if(_mo!==__modalOpen){__modalOpen=_mo;document.body.classList.toggle('modal-open',_mo);}}""",
        """ const rawDt=Math.min(.05,Math.max(.001,(now-last)/1000));last=now;
 window._smoothDt=(window._smoothDt===undefined||rawDt>0.042)?rawDt:(window._smoothDt*0.80+rawDt*0.20);
 const realDt=window._smoothDt;
 stepDeparture(realDt);
 // Any sheet on top of the scene outranks the comms card (z 1000 > 400).
 {const _S=window.Starfield;const _mo=!!(_S&&_S.isModalOpen&&_S.isModalOpen());
  window._frameModalOpen=_mo;
  if(_mo!==__modalOpen){__modalOpen=_mo;document.body.classList.toggle('modal-open',_mo);}}""",
        "EMA frame delta realDt smoothing & per-frame modal state cache in frame(now)"
    )

    html = replace_exact(
        html,
        """      const dockPrompt = document.getElementById('sf-docking-prompt');
      if (dockPrompt) {
        if (nearStation && nearDist < 2000 && !nearStation.docked) {
          dockPrompt.style.display = 'flex';
          window._activeDockStation = nearStation;
        } else {
          dockPrompt.style.display = 'none';
          window._activeDockStation = null;
        }
      }""",
        """      const showDock = !!(nearStation && nearDist < 2000 && !nearStation.docked);
      window._activeDockStation = showDock ? nearStation : null;
      if (window._lastDockPromptShow !== showDock) {
        const dockPrompt = window._dockPromptEl || (window._dockPromptEl = document.getElementById('sf-docking-prompt'));
        if (dockPrompt) {
          window._lastDockPromptShow = showDock;
          dockPrompt.style.display = showDock ? 'flex' : 'none';
        }
      }""",
        "Dirty-check #sf-docking-prompt display in frame(now)"
    )

    # -------------------------------------------------------------------------
    # 11. pollGamepad(now) & updateTouchInSituBadges Dirty Checking
    # -------------------------------------------------------------------------
    html = replace_exact(
        html,
        """    // Real-Time In-situ Status Badge Updater
    const updateTouchInSituBadges = () => {
      // Warp Badge
      const S = window.Starfield;
      const gear = (S && typeof S.getWarpGear === 'function') ? S.getWarpGear() : 0;
      let wBadge = btnWarp.querySelector('.sf-insitu-badge');
      if (!wBadge) {
        wBadge = document.createElement('span');
        wBadge.className = 'sf-insitu-badge';
        btnWarp.appendChild(wBadge);
      }
      btnWarp.classList.remove('warp-tier-0', 'warp-tier-1', 'warp-tier-2');
      btnWarp.classList.add(`warp-tier-${gear}`);
      wBadge.textContent = gear === 0 ? '1x' : gear === 1 ? '5x' : '15x';

      // Camera Badge
      const isCockpit = (S && typeof S.isCockpit === 'function' && S.isCockpit());
      let cBadge = btnCam.querySelector('.sf-insitu-badge');
      if (!cBadge) {
        cBadge = document.createElement('span');
        cBadge.className = 'sf-insitu-badge';
        btnCam.appendChild(cBadge);
      }
      btnCam.classList.toggle('flagship-active', isCockpit);
      cBadge.textContent = isCockpit ? 'FLAG' : 'AUTO';

      // Formation Badge
      const fIdx = (window.FleetFormations && typeof window.FleetFormations.currentFormation !== 'undefined') ? window.FleetFormations.currentFormation : 0;
      let fBadge = btnFormation.querySelector('.sf-insitu-badge');
      if (!fBadge) {
        fBadge = document.createElement('span');
        fBadge.className = 'sf-insitu-badge';
        btnFormation.appendChild(fBadge);
      }
      fBadge.textContent = `F${fIdx + 1}`;
    };""",
        """    // Real-Time In-situ Status Badge Updater (Dirty-checked)
    let _wBadgeEl = null, _cBadgeEl = null, _fBadgeEl = null;
    let _lastGear = -1, _lastCockpit = null, _lastFormIdx = -1;
    const updateTouchInSituBadges = () => {
      const S = window.Starfield;
      const gear = (S && typeof S.getWarpGear === 'function') ? S.getWarpGear() : 0;
      if (gear !== _lastGear) {
        _lastGear = gear;
        if (!_wBadgeEl) {
          _wBadgeEl = btnWarp.querySelector('.sf-insitu-badge') || document.createElement('span');
          _wBadgeEl.className = 'sf-insitu-badge';
          if (!_wBadgeEl.parentNode) btnWarp.appendChild(_wBadgeEl);
        }
        btnWarp.classList.remove('warp-tier-0', 'warp-tier-1', 'warp-tier-2');
        btnWarp.classList.add(`warp-tier-${gear}`);
        _wBadgeEl.textContent = gear === 0 ? '1x' : gear === 1 ? '5x' : '15x';
      }

      const isCockpit = !!(S && typeof S.isCockpit === 'function' && S.isCockpit());
      if (isCockpit !== _lastCockpit) {
        _lastCockpit = isCockpit;
        if (!_cBadgeEl) {
          _cBadgeEl = btnCam.querySelector('.sf-insitu-badge') || document.createElement('span');
          _cBadgeEl.className = 'sf-insitu-badge';
          if (!_cBadgeEl.parentNode) btnCam.appendChild(_cBadgeEl);
        }
        btnCam.classList.toggle('flagship-active', isCockpit);
        _cBadgeEl.textContent = isCockpit ? 'FLAG' : 'AUTO';
      }

      const fIdx = (window.FleetFormations && typeof window.FleetFormations.currentFormation !== 'undefined') ? window.FleetFormations.currentFormation : 0;
      if (fIdx !== _lastFormIdx) {
        _lastFormIdx = fIdx;
        if (!_fBadgeEl) {
          _fBadgeEl = btnFormation.querySelector('.sf-insitu-badge') || document.createElement('span');
          _fBadgeEl.className = 'sf-insitu-badge';
          if (!_fBadgeEl.parentNode) btnFormation.appendChild(_fBadgeEl);
        }
        _fBadgeEl.textContent = `F${fIdx + 1}`;
      }
    };""",
        "Dirty-check updateTouchInSituBadges"
    )

    html = replace_exact(
        html,
        """  // --- Gamepad Main Polling & Processing Loop (Zero idle spin when disconnected) ---
  function pollGamepad(now) {
    if (document.hidden) return;
    if ((typeof currentMode !== 'undefined' && currentMode !== 'cruise') || (window.currentMode && window.currentMode !== 'cruise')) {
      const touchOverlay = document.getElementById('starfield-touch-overlay');
      if (touchOverlay) touchOverlay.style.display = 'none';
      return;
    }
    const dt = Math.min(0.05, Math.max(0.001, (now - lastFrameTime) / 1000));
    lastFrameTime = now;

    const gamepads = (navigator.getGamepads ? navigator.getGamepads() : []) || [];
    let pad = null;

    // Pick first connected gamepad
    for (let i = 0; i < gamepads.length; i++) {
      if (gamepads[i] && gamepads[i].connected) {
        pad = gamepads[i];
        activeGamepadIndex = i;
        break;
      }
    }

    // Manage Touch HUD visibility lifecycle (only show during active flight with no modal open)
    const touchOverlay = document.getElementById('starfield-touch-overlay');
    if (touchOverlay) {
      const flightActive = Engine.isFlightStarted();
      const modalOpen = Engine.isModalOpen();
      const focusRunning = (window.StarfieldFocusEngine && window.StarfieldFocusEngine.state === 'RUNNING');
      const shouldShow = isTouchCapable && flightActive && !modalOpen && !focusRunning;
      touchOverlay.style.display = shouldShow ? 'block' : 'none';
    }""",
        """  // --- Gamepad Main Polling & Processing Loop (Zero idle spin when disconnected) ---
  let _cachedTouchOverlay = null, _lastTouchOverlayShow = null, _gpPollTick = 0;
  function pollGamepad(now) {
    if (document.hidden) return;
    const touchOverlay = _cachedTouchOverlay || (_cachedTouchOverlay = document.getElementById('starfield-touch-overlay'));
    if ((typeof currentMode !== 'undefined' && currentMode !== 'cruise') || (window.currentMode && window.currentMode !== 'cruise')) {
      if (touchOverlay && _lastTouchOverlayShow !== false) {
        _lastTouchOverlayShow = false;
        touchOverlay.style.display = 'none';
      }
      return;
    }
    const dt = Math.min(0.05, Math.max(0.001, (now - lastFrameTime) / 1000));
    lastFrameTime = now;

    // Manage Touch HUD visibility lifecycle (dirty-checked; reuses per-frame modal state)
    if (touchOverlay) {
      const flightActive = Engine.isFlightStarted();
      const modalOpen = (window._frameModalOpen !== undefined) ? window._frameModalOpen : Engine.isModalOpen();
      const focusRunning = !!(window.StarfieldFocusEngine && window.StarfieldFocusEngine.state === 'RUNNING');
      const shouldShow = !!(isTouchCapable && flightActive && !modalOpen && !focusRunning);
      if (_lastTouchOverlayShow !== shouldShow) {
        _lastTouchOverlayShow = shouldShow;
        touchOverlay.style.display = shouldShow ? 'block' : 'none';
      }
    }

    // Only call navigator.getGamepads() every frame when connected, or once every 60 frames to probe
    _gpPollTick = (_gpPollTick + 1) % 60;
    if (!gamepadConnected && _gpPollTick !== 0) return;

    const gamepads = (navigator.getGamepads ? navigator.getGamepads() : []) || [];
    let pad = null;

    for (let i = 0; i < gamepads.length; i++) {
      if (gamepads[i] && gamepads[i].connected) {
        pad = gamepads[i];
        activeGamepadIndex = i;
        break;
      }
    }""",
        "Dirty-check touchOverlay.style.display and throttle disconnected gamepad polling"
    )

    # -------------------------------------------------------------------------
    # 12. AnomalyScanner & RelicTuner: Prune Passed Targets & Stop Per-Frame DOM Query
    # -------------------------------------------------------------------------
    html = replace_exact(
        html,
        """      for (const target of this.detectedTargets.values()) {
        const d = Math.hypot(target.x - ship[0], target.y - ship[1], target.z - ship[2]);
        target.currentDist = d;
        if (!target.solved && d <= minPromptDist) {
          minPromptDist = d;
          nearestUndeciphered = target;
        }
      }""",
        """      for (const [tKey, target] of this.detectedTargets.entries()) {
        if (target.z < ship[2] - 2500) {
          this.detectedTargets.delete(tKey);
          continue;
        }
        const d = Math.hypot(target.x - ship[0], target.y - ship[1], target.z - ship[2]);
        if (d > 26000) {
          this.detectedTargets.delete(tKey);
          continue;
        }
        target.currentDist = d;
        if (!target.solved && d <= minPromptDist) {
          minPromptDist = d;
          nearestUndeciphered = target;
        }
      }""",
        "Prune passed targets from ScannerRadar.detectedTargets so #scanner-overlay-canvas sleeps when idle"
    )

    html = replace_exact(
        html,
        """      const prompt = document.getElementById('relic-proximity-prompt');
      if (prompt) prompt.remove();
    },""",
        """      if (!this._cleanedRelicPrompt) {
        this._cleanedRelicPrompt = true;
        const prompt = document.getElementById('relic-proximity-prompt');
        if (prompt) prompt.remove();
      }
    },""",
        "Eliminate per-frame getElementById('relic-proximity-prompt') in RelicTuner"
    )

    # -------------------------------------------------------------------------
    # 13. SFHazard & SFPlanetGL: Dirty-Check DOM & Layout-Invariant WebGL Sizing
    # -------------------------------------------------------------------------
    html = replace_exact(
        html,
        """  function draw(ctx) {
    var live = running();
    hullEl.style.display = live ? '' : 'none';
    note.style.display = live ? '' : 'none';
    if (!live) return;""",
        """  function draw(ctx) {
    var live = running();
    if (st.lastLive !== live) {
      st.lastLive = live;
      hullEl.style.display = live ? '' : 'none';
      note.style.display = live ? '' : 'none';
    }
    if (!live) return;""",
        "Dirty-check hullEl and note display in SFHazard.draw"
    )

    html = replace_exact(
        html,
        """    hullFill.style.transform = 'scaleX(' + (st.hull / 100).toFixed(3) + ')';
    hullVal.textContent = String(Math.round(st.hull));
    var repairing = (now - st.lastHit > REPAIR_DELAY) && st.hull < 100;
    hullEl.classList.toggle('warn', st.hull < 40);
    hullEl.classList.toggle('repair', repairing && st.hull >= 40);
    hullKey.textContent = st.tidal > 0 ? 'TIDAL SHEAR'
      : (st.hull < 25 ? 'POWER LOSS' : (repairing ? 'REPAIRING' : 'INTEGRITY'));""",
        """    var hullScale = 'scaleX(' + (st.hull / 100).toFixed(3) + ')';
    if (st.lastHullScale !== hullScale) { st.lastHullScale = hullScale; hullFill.style.transform = hullScale; }
    var hullInt = String(Math.round(st.hull));
    if (st.lastHullInt !== hullInt) { st.lastHullInt = hullInt; hullVal.textContent = hullInt; }
    var repairing = (now - st.lastHit > REPAIR_DELAY) && st.hull < 100;
    var isWarn = st.hull < 40, isRep = repairing && st.hull >= 40;
    if (st.lastWarn !== isWarn) { st.lastWarn = isWarn; hullEl.classList.toggle('warn', isWarn); }
    if (st.lastRep !== isRep) { st.lastRep = isRep; hullEl.classList.toggle('repair', isRep); }
    var nextKey = st.tidal > 0 ? 'TIDAL SHEAR'
      : (st.hull < 25 ? 'POWER LOSS' : (repairing ? 'REPAIRING' : 'INTEGRITY'));
    if (st.lastKey !== nextKey) { st.lastKey = nextKey; hullKey.textContent = nextKey; }""",
        "Dirty-check SFHazard.drawHud hull telemetry writes"
    )

    html = replace_exact(
        html,
        """  function sizeTo(canvas2d) {
    var dpr = Math.min(window.devicePixelRatio || 1, 2);
    var box = canvas2d.getBoundingClientRect();
    var w = Math.max(64, Math.round((box.width || 222) * dpr));
    var h = w;
    if (renderer.domElement.width !== w || renderer.domElement.height !== h) {
      renderer.setSize(w, h, false);
      camera.aspect = 1;
      camera.updateProjectionMatrix();
    }
  }""",
        """  function sizeTo(canvas2d) {
    var dpr = Math.min(window.devicePixelRatio || 1, 2);
    var cssW = canvas2d.clientWidth || canvas2d.offsetWidth || 222;
    var w = Math.max(64, Math.round(cssW * dpr));
    var h = w;
    if (renderer.domElement.width !== w || renderer.domElement.height !== h) {
      renderer.setSize(w, h, false);
      camera.aspect = 1;
      camera.updateProjectionMatrix();
    }
  }""",
        "Use layout-invariant clientWidth in SFPlanetGL.sizeTo to prevent 3D-tilt framebuffer thrashing"
    )

    # -------------------------------------------------------------------------
    # 14. Residual Emoji Cleanup & Inline Settings Jukebox Harmonization
    # -------------------------------------------------------------------------
    html = replace_exact(
        html,
        """<span id="radar-button-name">📡 巡天雷达</span>""",
        """<span id="radar-button-name">✦ 巡天雷达</span>""",
        "Remove 📡 emoji from #radar-button-name"
    )

    html = replace_exact(
        html,
        """<span class="icon-badge">🚀</span>""",
        """<span class="icon-badge">✦</span>""",
        "Remove 🚀 emoji from hangar header"
    )

    html = replace_exact(
        html,
        """toast('📷 深空摄影模式：拖拽调整构图 · 滚轮缩放 · 导出高清壁纸');""",
        """toast('✦ 深空摄影模式：拖拽调整构图 · 滚轮缩放 · 导出高清壁纸');""",
        "Remove 📷 emoji from photo studio toast"
    )

    html = replace_exact(
        html,
        """      if (ev.type === 'asteroid_field') toast('☄ 密集小行星带 · ASTEROID BELT HAZARD', 4);
      else if (ev.type === 'pulsar') toast('✦ 星际脉冲星 · PULSAR BEACON', 4);
      else if (ev.type === 'comet') toast('☄ 掠日彗星 · COSMIC COMET DETECTED', 4);
      else if (ev.type === 'solar_flare') toast('☀ 日冕耀斑 · CORONAL MASS EJECTION', 4);
      else if (ev.type === 'derelict') toast('📡 远古中继信标 · ANCIENT RELAY BEACON', 4);
      else if (ev.type === 'spatial_anomaly') toast('◎ 时空微裂隙透镜异常 · GRAVITATIONAL ANOMALY', 4);
      // 10 Epic Easter Egg Toasts
      else if (ev.type === 'gundam_relic') toast('🤖 折翼高达遗迹残骸 · RX-78 WHITE DEVIL RELIC', 6);
      else if (ev.type === 'eva_longinus') toast('🩸 朗基努斯之枪 · SPEAR OF LONGINUS & A.T. FIELD', 6);
      else if (ev.type === 'ultraman_m78') toast('✨ M78星云 · 光之巨人十字斯派修姆粒子流', 6);
      else if (ev.type === 'dyson_ring') toast('✨ 戴森环巨构 · DYSON RING MEGASTRUCTURE', 5);
      else if (ev.type === 'wormhole_sphere') toast('🌀 球形虫洞 · INTERSTELLAR WORMHOLE SPHERE', 5);
      else if (ev.type === 'voyager_probe') toast('📡 旅行者号探测器 · VOYAGER INTERSTELLAR PROBE', 5);
      else if (ev.type === 'dimension_foil') toast('📜 二向箔坍缩点 · DUAL-VECTOR FOIL COLLAPSE', 5);
      else if (ev.type === 'pillars_of_creation') toast('🌌 创生之柱 · PILLARS OF CREATION', 5);
      else if (ev.type === 'monolith_artifact') toast('⬛ 黑色方尖碑 · 1:4:9 ALIEN MONOLITH', 5);
      else if (ev.type === 'ghost_fleet') toast('⚔️ 古战场幽灵旗舰 · DREADNOUGHT GHOST FLEET', 5);""",
        """      if (ev.type === 'asteroid_field') toast('✦ 密集小行星带 · ASTEROID BELT HAZARD', 4);
      else if (ev.type === 'pulsar') toast('✦ 星际脉冲星 · PULSAR BEACON', 4);
      else if (ev.type === 'comet') toast('✦ 掠日彗星 · COSMIC COMET DETECTED', 4);
      else if (ev.type === 'solar_flare') toast('✦ 日冕耀斑 · CORONAL MASS EJECTION', 4);
      else if (ev.type === 'derelict') toast('✦ 远古中继信标 · ANCIENT RELAY BEACON', 4);
      else if (ev.type === 'spatial_anomaly') toast('⊕ 时空微裂隙透镜异常 · GRAVITATIONAL ANOMALY', 4);
      // 10 Epic Easter Egg Toasts
      else if (ev.type === 'gundam_relic') toast('✦ 折翼高达遗迹残骸 · RX-78 WHITE DEVIL RELIC', 6);
      else if (ev.type === 'eva_longinus') toast('✦ 朗基努斯之枪 · SPEAR OF LONGINUS & A.T. FIELD', 6);
      else if (ev.type === 'ultraman_m78') toast('✦ M78星云 · 光之巨人十字斯派修姆粒子流', 6);
      else if (ev.type === 'dyson_ring') toast('✦ 戴森环巨构 · DYSON RING MEGASTRUCTURE', 5);
      else if (ev.type === 'wormhole_sphere') toast('⊕ 球形虫洞 · INTERSTELLAR WORMHOLE SPHERE', 5);
      else if (ev.type === 'voyager_probe') toast('✦ 旅行者号探测器 · VOYAGER INTERSTELLAR PROBE', 5);
      else if (ev.type === 'dimension_foil') toast('✦ 二向箔坍缩点 · DUAL-VECTOR FOIL COLLAPSE', 5);
      else if (ev.type === 'pillars_of_creation') toast('✦ 创生之柱 · PILLARS OF CREATION', 5);
      else if (ev.type === 'monolith_artifact') toast('✦ 黑色方尖碑 · 1:4:9 ALIEN MONOLITH', 5);
      else if (ev.type === 'ghost_fleet') toast('✦ 古战场幽灵旗舰 · DREADNOUGHT GHOST FLEET', 5);""",
        "Replace colored emojis in cosmic event toasts with geometric symbols"
    )

    html = replace_exact(
        html,
        """   toast('🔇 领航员旁白解说已静音', 3);
  } else {
   toast('🎙️ 领航员旁白解说已启用', 3);""",
        """   toast('✦ 领航员旁白解说已静音', 3);
  } else {
   toast('✦ 领航员旁白解说已启用', 3);""",
        "Replace colored emojis in narrator mute/unmute toasts"
    )

    html = replace_exact(
        html,
        """    if (trk && typeof toast === 'function') toast('🎼 配乐切换 · ' + trk.title);
  }
 }
 else if(e.key.toLowerCase()==='b'||e.key==='['){
  if(typeof sound!=='undefined'&&(sound.prevTrack||(sound.classical&&sound.classical.prevTrack))){
    if(!soundEnabled && typeof toggleSound==='function') toggleSound();
    if(sound.prevTrack) sound.prevTrack();
    else if(sound.classical&&sound.classical.prevTrack) sound.classical.prevTrack();
    const trk = sound.originalTracks && sound.originalTracks[sound.index];
    if (trk && typeof toast === 'function') toast('🎼 配乐切换 · ' + trk.title);""",
        """    if (trk && typeof toast === 'function') toast('✦ 配乐切换 · ' + trk.title);
  }
 }
 else if(e.key.toLowerCase()==='b'||e.key==='['){
  if(typeof sound!=='undefined'&&(sound.prevTrack||(sound.classical&&sound.classical.prevTrack))){
    if(!soundEnabled && typeof toggleSound==='function') toggleSound();
    if(sound.prevTrack) sound.prevTrack();
    else if(sound.classical&&sound.classical.prevTrack) sound.classical.prevTrack();
    const trk = sound.originalTracks && sound.originalTracks[sound.index];
    if (trk && typeof toast === 'function') toast('✦ 配乐切换 · ' + trk.title);""",
        "Replace 🎼 emoji in track switch toasts"
    )

    html = replace_exact(
        html,
        """        <span class="fps-icon">⚡</span>""",
        """        <span class="fps-icon">✦</span>""",
        "Replace ⚡ emoji in #sf-perf-hud"
    )

    html = replace_exact(
        html,
        """      btn.innerHTML = `🔄 切换${isPortrait ? '横屏' : '竖屏'}`;""",
        """      btn.innerHTML = `✦ 切换${isPortrait ? '横屏' : '竖屏'}`;""",
        "Replace 🔄 emoji in orientation toggle button"
    )

    html = replace_exact(
        html,
        """  toast('⚡ 超曲速脉冲爆冲 // WARP BURST ENGAGED');""",
        """  toast('✦ 超曲速脉冲爆冲 // WARP BURST ENGAGED');""",
        "Replace ⚡ emoji in slingshotBoost toast"
    )

    html = replace_exact(
        html,
        """          toast(LivingPlanetEngine.enabled ? '已开启 3D 活体生态星球引擎 🌍' : '已切换回经典宣纸行星 ');""",
        """          toast(LivingPlanetEngine.enabled ? '✦ 已开启 3D 活体生态星球引擎' : '✦ 已切换回经典宣纸行星');""",
        "Replace 🌍 emoji in LivingPlanetEngine toggle toast"
    )

    html = replace_exact(
        html,
        """      rewardsEarned.push(`✨ 捕获未开采深空星核 × ${earnedCores}`);
      rewardsEarned.push(`🌌 凝聚深空星尘 +${focusedMinutes * 120}`);""",
        """      rewardsEarned.push(`✦ 捕获未开采深空星核 × ${earnedCores}`);
      rewardsEarned.push(`✦ 凝聚深空星尘 +${focusedMinutes * 120}`);""",
        "Replace ✨/🌌 emojis in FocusEngine reward list"
    )

    html = replace_exact(
        html,
        """      const ecoTag = isEco ? `<span class="sf-focus-ticker-eco">❄ 控温巡航 45FPS</span>` : '';""",
        """      const ecoTag = isEco ? `<span class="sf-focus-ticker-eco">✦ 控温巡航 45FPS</span>` : '';""",
        "Replace ❄ emoji in FocusEngine eco tag"
    )

    html = replace_exact(
        html,
        """      const msg = `[护航入列] ${item.name} 已编入随行护航轨道 ✨`;""",
        """      const msg = `[护航入列] ${item.name} 已编入随行护航轨道 ✦`;""",
        "Replace ✨ emoji in escort toast"
    )

    html = replace_exact(
        html,
        """    <!-- ORIGINAL MUSIC JUKEBOX -->
    <div class="classical-jukebox" style="background: rgba(255,255,255,0.04); border: 1px solid rgba(244,208,111,0.25); border-radius: 8px; padding: 10px 12px; margin-top: 10px;">
      <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom: 6px;">
        <span style="font-size:10px; letter-spacing:0.12em; color:#f4d06f; font-weight:600;">候鸟星海 · 8首典藏配乐</span>
        <div style="display:flex; gap:6px;">
          <button id="btn-prev-track" class="photo-btn" style="padding:2px 8px; font-size:11px;" title="上一首">◀</button>
          <button id="btn-next-track" class="photo-btn" style="padding:2px 8px; font-size:11px;" title="下一首">▶</button>
        </div>
      </div>
      <div id="classical-track-title" style="font-size:12px; font-weight:500; color:#e6edf2; line-height:1.4;">1. 原野 · 晨曦微光 (D 大调 / A 混合利底亚)</div>
      <div id="classical-track-composer" style="font-size:10px; opacity:0.6; margin-top:2px;">和纸原野 · 66s 沉浸原曲</div>
      <div style="display:grid; grid-template-columns: 1fr 1fr; gap:6px; margin-top:8px;">
        <button class="photo-btn track-select-btn active" data-track="0" style="padding:5px 8px; font-size:11px; text-align:left; overflow:hidden; text-overflow:ellipsis; white-space:nowrap;">1. 原野 · 晨曦</button>
        <button class="photo-btn track-select-btn" data-track="1" style="padding:5px 8px; font-size:11px; text-align:left; overflow:hidden; text-overflow:ellipsis; white-space:nowrap;">2. 月图 · 水墨</button>
        <button class="photo-btn track-select-btn" data-track="2" style="padding:5px 8px; font-size:11px; text-align:left; overflow:hidden; text-overflow:ellipsis; white-space:nowrap;">3. 暖纸 · 金箔</button>
        <button class="photo-btn track-select-btn" data-track="3" style="padding:5px 8px; font-size:11px; text-align:left; overflow:hidden; text-overflow:ellipsis; white-space:nowrap;">4. 暮粉 · 核心</button>
        <button class="photo-btn track-select-btn" data-track="4" style="padding:5px 8px; font-size:11px; text-align:left; overflow:hidden; text-overflow:ellipsis; white-space:nowrap;">5. 夜航 · 深渊</button>
        <button class="photo-btn track-select-btn" data-track="5" style="padding:5px 8px; font-size:11px; text-align:left; overflow:hidden; text-overflow:ellipsis; white-space:nowrap;">6. 雪境 · 低语</button>
        <button class="photo-btn track-select-btn" data-track="6" style="grid-column: span 1; padding:5px 8px; font-size:11px; text-align:left; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; border-color: rgba(244,208,111,0.5); color: #ffd700; background: rgba(244,208,111,0.08);">7. 律政狂想 · Better Call Saul TV Theme (15s)</button>
        <button class="photo-btn track-select-btn" data-track="7" style="grid-column: span 2; padding:5px 8px; font-size:11px; text-align:left; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; border-color: rgba(255,105,180,0.6); color: #ff9ecf; background: rgba(255,105,180,0.12); font-weight:600;">8. 四月是你的谎言 · 圣-桑：引子与回旋随想曲 Op.28 完整版 (9:15)</button>
      </div>
    </div>""",
        """    <!-- ORIGINAL MUSIC JUKEBOX -->
    <div class="classical-jukebox" style="background: rgba(230,237,242,0.02); border: 1px solid rgba(230,237,242,0.14); border-radius: 0; padding: 10px 12px; margin-top: 10px;">
      <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom: 6px;">
        <span style="font-size:10px; letter-spacing:0.16em; color:rgba(230,237,242,0.78); font-weight:500;">候鸟星海 · 8首典藏配乐</span>
        <div style="display:flex; gap:6px;">
          <button id="btn-prev-track" class="photo-btn" style="padding:2px 8px; font-size:11px;" title="上一首">◀</button>
          <button id="btn-next-track" class="photo-btn" style="padding:2px 8px; font-size:11px;" title="下一首">▶</button>
        </div>
      </div>
      <div id="classical-track-title" style="font-size:12px; font-weight:500; color:#e6edf2; line-height:1.4;">1. 原野 · 晨曦微光 (D 大调 / A 混合利底亚)</div>
      <div id="classical-track-composer" style="font-size:10px; opacity:0.6; margin-top:2px;">和纸原野 · 66s 沉浸原曲</div>
      <div style="display:grid; grid-template-columns: 1fr 1fr; gap:6px; margin-top:8px;">
        <button class="photo-btn track-select-btn active" data-track="0" style="padding:5px 8px; font-size:11px; text-align:left; overflow:hidden; text-overflow:ellipsis; white-space:nowrap;">1. 原野 · 晨曦</button>
        <button class="photo-btn track-select-btn" data-track="1" style="padding:5px 8px; font-size:11px; text-align:left; overflow:hidden; text-overflow:ellipsis; white-space:nowrap;">2. 月图 · 水墨</button>
        <button class="photo-btn track-select-btn" data-track="2" style="padding:5px 8px; font-size:11px; text-align:left; overflow:hidden; text-overflow:ellipsis; white-space:nowrap;">3. 暖纸 · 金箔</button>
        <button class="photo-btn track-select-btn" data-track="3" style="padding:5px 8px; font-size:11px; text-align:left; overflow:hidden; text-overflow:ellipsis; white-space:nowrap;">4. 暮粉 · 核心</button>
        <button class="photo-btn track-select-btn" data-track="4" style="padding:5px 8px; font-size:11px; text-align:left; overflow:hidden; text-overflow:ellipsis; white-space:nowrap;">5. 夜航 · 深渊</button>
        <button class="photo-btn track-select-btn" data-track="5" style="padding:5px 8px; font-size:11px; text-align:left; overflow:hidden; text-overflow:ellipsis; white-space:nowrap;">6. 雪境 · 低语</button>
        <button class="photo-btn track-select-btn" data-track="6" style="grid-column: span 1; padding:5px 8px; font-size:11px; text-align:left; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; border-color: rgba(230,237,242,0.24); color: rgba(230,237,242,0.88); background: rgba(230,237,242,0.03);">7. 律政狂想 · Better Call Saul TV Theme (15s)</button>
        <button class="photo-btn track-select-btn" data-track="7" style="grid-column: span 2; padding:5px 8px; font-size:11px; text-align:left; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; border-color: rgba(230,237,242,0.24); color: rgba(230,237,242,0.88); background: rgba(230,237,242,0.03);">8. 四月是你的谎言 · 圣-桑：引子与回旋随想曲 Op.28 完整版 (9:15)</button>
      </div>
    </div>""",
        "Harmonize inline jukebox styles in #settings-drawer"
    )

    # -------------------------------------------------------------------------
    # 15. Unified Holographic Editorial HUD CSS Injection (#sf-ui-v200-aesthetics)
    # -------------------------------------------------------------------------
    v200_css = """</style>
<style id="sf-ui-v200-aesthetics">
/* ============================================================================
 * BUILD 200: DEEP SPACE EDITORIAL & HOLOGRAPHIC INSTRUMENT DESIGN SYSTEM
 * Harmonizes all HUD telemetry rows, floating prompts, modals & mobile dock
 * into 1px hairline precision architecture (0 >=9px radius, 0 neon saturation)
 * ============================================================================ */
:root {
  --sf-surface-deep: rgba(6, 9, 14, 0.90);
  --sf-surface-glass: rgba(10, 15, 24, 0.74);
  --ui-line: rgba(230, 237, 242, 0.22);
  --ui-line-soft: rgba(230, 237, 242, 0.10);
  --ui-ink: rgba(230, 237, 242, 0.94);
  --ui-dim: rgba(230, 237, 242, 0.48);
}

/* 1. Top-Left Instrument Telemetry Cluster (#camera-hud, #sf-hull, #sf-fuel-hud, #sf-hud-stardust) */
#camera-hud {
  font-variant-numeric: tabular-nums;
}
.sf-stardust-pill {
  display: flex !important;
  align-items: center !important;
  gap: 8px !important;
  margin-top: 6px !important;
  padding: 2px 0 !important;
  background: none !important;
  border: 0 !important;
  border-radius: 0 !important;
  box-shadow: none !important;
  font-family: var(--ui-mono, ui-monospace, monospace) !important;
  font-size: 8.5px !important;
  letter-spacing: 0.22em !important;
  font-variant-numeric: tabular-nums !important;
  color: rgba(230, 237, 242, 0.72) !important;
  text-shadow: 0 1px 10px rgba(0, 0, 0, 0.92) !important;
  pointer-events: auto !important;
  transition: color 0.25s ease !important;
}
.sf-stardust-pill:hover {
  color: rgba(244, 208, 111, 0.95) !important;
}
.sf-fuel-gauge {
  display: flex !important;
  align-items: center !important;
  gap: 8px !important;
  margin-top: 5px !important;
  padding: 2px 0 !important;
  background: none !important;
  border: 0 !important;
  border-radius: 0 !important;
  box-shadow: none !important;
  backdrop-filter: none !important;
  -webkit-backdrop-filter: none !important;
  font-family: var(--ui-mono, ui-monospace, monospace) !important;
  font-size: 8.5px !important;
  letter-spacing: 0.20em !important;
  font-variant-numeric: tabular-nums !important;
  color: rgba(230, 237, 242, 0.62) !important;
}
.sf-fuel-gauge:hover {
  border-color: transparent !important;
  box-shadow: none !important;
  color: rgba(230, 237, 242, 0.92) !important;
}
.sf-fuel-k {
  font-size: 8px !important;
  letter-spacing: 0.22em !important;
  color: rgba(230, 237, 242, 0.42) !important;
}
.sf-fuel-bar {
  width: 64px !important;
  height: 1px !important;
  background: rgba(230, 237, 242, 0.16) !important;
  border-radius: 0 !important;
}
.sf-fuel-fill {
  height: 1px !important;
  background: rgba(230, 237, 242, 0.72) !important;
  background-image: none !important;
  border-radius: 0 !important;
}
.sf-fuel-label {
  font-size: 8.5px !important;
  letter-spacing: 0.16em !important;
  color: rgba(230, 237, 242, 0.72) !important;
}

/* 2. Floating Tactical Prompts (.sf-descent-corridor-btn, .sf-docking-banner) */
.sf-descent-corridor-btn {
  border-radius: 0 !important;
  background: rgba(6, 9, 14, 0.86) !important;
  border: 0 !important;
  border-top: 1px solid rgba(244, 208, 111, 0.55) !important;
  border-bottom: 1px solid rgba(230, 237, 242, 0.16) !important;
  color: rgba(230, 237, 242, 0.92) !important;
  font-family: var(--ui-mono, ui-monospace, monospace) !important;
  font-size: 9.5px !important;
  letter-spacing: 0.24em !important;
  padding: 9px 18px !important;
  box-shadow: 0 12px 32px rgba(0, 0, 0, 0.72) !important;
  text-shadow: none !important;
}
.sf-descent-corridor-btn:hover {
  background: rgba(230, 237, 242, 0.08) !important;
  border-top-color: rgba(244, 208, 111, 0.90) !important;
}
.sf-docking-banner {
  border-radius: 0 !important;
  background: rgba(6, 9, 14, 0.90) !important;
  border: 0 !important;
  border-top: 1px solid rgba(230, 237, 242, 0.28) !important;
  border-bottom: 1px solid rgba(230, 237, 242, 0.12) !important;
  box-shadow: 0 14px 40px rgba(0, 0, 0, 0.75) !important;
  color: rgba(230, 237, 242, 0.92) !important;
  font-family: var(--ui-mono, ui-monospace, monospace) !important;
  font-size: 10px !important;
  letter-spacing: 0.18em !important;
  animation: none !important;
}
.sf-dock-action-btn {
  background: rgba(230, 237, 242, 0.06) !important;
  background-image: none !important;
  border: 1px solid rgba(230, 237, 242, 0.28) !important;
  border-radius: 0 !important;
  color: rgba(230, 237, 242, 0.94) !important;
  font-family: var(--ui-mono, ui-monospace, monospace) !important;
  font-size: 9.5px !important;
  font-weight: 500 !important;
  letter-spacing: 0.20em !important;
  padding: 5px 12px !important;
  box-shadow: none !important;
}
.sf-dock-action-btn:hover {
  background: rgba(230, 237, 242, 0.12) !important;
  border-color: rgba(230, 237, 242, 0.55) !important;
  transform: none !important;
}

/* 3. Ship Equipment Upgrades Modal & Relic Frequency Tuner Modal */
.sf-upgrades-panel,
.relic-modal-frame {
  background: #06090e !important;
  border: 1px solid rgba(230, 237, 242, 0.16) !important;
  border-radius: 0 !important;
  box-shadow: 0 24px 64px rgba(0, 0, 0, 0.85) !important;
  color: rgba(230, 237, 242, 0.92) !important;
}
.sf-upgrades-title {
  font-family: var(--ui-serif, "Noto Serif SC", serif) !important;
  font-weight: 400 !important;
  letter-spacing: 0.14em !important;
  color: rgba(230, 237, 242, 0.94) !important;
}
.sf-upgrades-credits,
.relic-tag-badge {
  background: rgba(230, 237, 242, 0.03) !important;
  border: 1px solid rgba(230, 237, 242, 0.20) !important;
  border-radius: 0 !important;
  color: rgba(244, 208, 111, 0.88) !important;
  font-family: var(--ui-mono, ui-monospace, monospace) !important;
  letter-spacing: 0.16em !important;
}
.sf-upgrade-card {
  background: rgba(230, 237, 242, 0.02) !important;
  border: 1px solid rgba(230, 237, 242, 0.10) !important;
  border-radius: 0 !important;
}
.sf-upgrade-card:hover {
  background: rgba(230, 237, 242, 0.04) !important;
  border-color: rgba(230, 237, 242, 0.26) !important;
}
.sf-upgrade-lvl {
  background: rgba(230, 237, 242, 0.04) !important;
  border: 1px solid rgba(230, 237, 242, 0.16) !important;
  border-radius: 0 !important;
  color: rgba(230, 237, 242, 0.78) !important;
}
.sf-upgrade-stat-row {
  background: rgba(230, 237, 242, 0.02) !important;
  border-radius: 0 !important;
  color: rgba(230, 237, 242, 0.68) !important;
}
.sf-upgrade-btn,
.relic-close-btn,
.victory-btn {
  background: rgba(230, 237, 242, 0.05) !important;
  background-image: none !important;
  border: 1px solid rgba(230, 237, 242, 0.22) !important;
  border-radius: 0 !important;
  color: rgba(230, 237, 242, 0.92) !important;
  font-family: var(--ui-mono, ui-monospace, monospace) !important;
  font-weight: 400 !important;
  letter-spacing: 0.16em !important;
  box-shadow: none !important;
}
.sf-upgrade-btn:hover:not(:disabled),
.relic-close-btn:hover,
.victory-btn:hover {
  background: rgba(230, 237, 242, 0.11) !important;
  border-color: rgba(230, 237, 242, 0.48) !important;
  transform: none !important;
}
.sf-upgrade-btn.maxed {
  background: rgba(230, 237, 242, 0.02) !important;
  border-color: rgba(244, 208, 111, 0.35) !important;
  color: rgba(244, 208, 111, 0.85) !important;
}
#scanner-golden-toast {
  border-radius: 0 !important;
  background: rgba(6, 9, 14, 0.90) !important;
  border: 0 !important;
  border-top: 1px solid rgba(244, 208, 111, 0.45) !important;
  border-bottom: 1px solid rgba(230, 237, 242, 0.14) !important;
}

/* 4. Mobile & Touch Precision Architectural Command Dock (.sf-touch-cluster) */
.sf-touch-primary-row,
.sf-touch-more-tray {
  border-radius: 0 !important;
  background: rgba(6, 9, 14, 0.84) !important;
  border: 1px solid rgba(230, 237, 242, 0.16) !important;
  box-shadow: 0 12px 36px rgba(0, 0, 0, 0.72) !important;
}
.sf-touch-btn,
.sf-touch-more-tray .sf-touch-btn {
  border-radius: 0 !important;
  background: rgba(230, 237, 242, 0.03) !important;
  border: 1px solid rgba(230, 237, 242, 0.10) !important;
  color: rgba(230, 237, 242, 0.86) !important;
}
.sf-touch-btn.warp-tier-1,
.sf-touch-btn.warp-tier-2,
.sf-touch-btn.flagship-active {
  background: rgba(230, 237, 242, 0.08) !important;
  border-color: rgba(230, 237, 242, 0.32) !important;
}
.sf-insitu-badge,
.sf-touch-btn.warp-tier-1 .sf-insitu-badge,
.sf-touch-btn.warp-tier-2 .sf-insitu-badge,
.sf-touch-btn.flagship-active .sf-insitu-badge {
  border-radius: 0 !important;
  background: rgba(6, 9, 14, 0.92) !important;
  border: 1px solid rgba(230, 237, 242, 0.22) !important;
  color: rgba(230, 237, 242, 0.88) !important;
  box-shadow: none !important;
}
.sf-touch-core-badge {
  border-radius: 0 !important;
  background: rgba(6, 9, 14, 0.92) !important;
  background-image: none !important;
  border: 1px solid rgba(244, 208, 111, 0.65) !important;
  color: rgba(244, 208, 111, 0.95) !important;
  box-shadow: none !important;
}
.sf-gamepad-badge {
  border-radius: 0 !important;
  background: rgba(6, 9, 14, 0.90) !important;
  border: 1px solid rgba(230, 237, 242, 0.20) !important;
}
</style>"""

    html = replace_exact(
        html,
        """#sf-hatch .sf-card-evolution::before{
  content:"";
  display:inline-block;
  width:4px;height:4px;border-radius:50%;
  background:rgba(200,214,228,.5);
  margin-right:7px;
  vertical-align:middle;
}
</style>""",
        """#sf-hatch .sf-card-evolution::before{
  content:"";
  display:inline-block;
  width:4px;height:4px;border-radius:50%;
  background:rgba(200,214,228,.5);
  margin-right:7px;
  vertical-align:middle;
}
""" + v200_css,
        "Inject #sf-ui-v200-aesthetics stylesheet"
    )

    with open(HTML_PATH, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"\n[SUCCESS] Stage 1 patch applied cleanly to {HTML_PATH} ({orig_len} -> {len(html)} bytes).")


if __name__ == "__main__":
    main()
