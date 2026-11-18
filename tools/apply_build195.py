# -*- coding: utf-8 -*-
"""
Build 195 (v1.9.9.9.9.7) Comprehensive Bug Fix & Optimization Script:
1. Fix 1 (P0): Secondary planet rendering - ensure LivingPlanetEngine copies to model.canvas before isMob return.
2. Fix 2 (P0): SFPlanetGL 60 FPS reconstruction storm - add buildupStage to key.
3. Fix 3 (P1): Voice volume slider - read this.volumeScale in Narrator._executeSpeak.
4. Fix 4 (P1): WebAudio context limit & SFX bus routing - ScannerAudio, CardCraft, RevealSfx, SFAmbience.
5. Fix 5 (P1): GLSL ES smoothstep violation - change smoothstep(0.5, 0.15, r) to (1.0 - smoothstep(0.15, 0.5, r)).
6. Fix 6 (P1): WarpDrive brakeKick camera jitter - kickZ before basis, remove post-basis subtraction.
7. Fix 7 (P1): Ghost gravitational lens leak - reset window.__sfBH to currentBH (null when no BH).
8. Fix 8 (P1): Android APK upgrade asset hijack - check bundled build >= currentBuild, clear old starfield_active.html.
9. Fix 9 (P2): Android assets parity - sync planet_studio.html and version.json, verify all mirrors.
10. Fix 10 (P2): Nebula cache true LRU - refresh Map insertion order on get().
11. Fix 11 (P2): Orbit mechanics speed scaling - account for effWarp during warp cruise.
12. Fix 12 (P2): Black hole escape fleet velocity spike - reset escort bird relative velocities exiting capture.
13. Fix 13 (P2): Touch gesture conflict - ignore non-primary pointerdown in setupLongPressSpeed.
14. Fix 14 (P3): Perf HUD DPR calculation - avoid multiplying dpr * scale.
15. Fix 15 (P3): Modal safe check - optional chaining for classList on codex-modal and settings-drawer.
16. Version bump to Build 195 (v1.9.9.9.9.7) across version.json, starfield.html, service-worker.js, and Android assets.
"""
import os
import sys
import json
import re
import shutil
import hashlib

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HTML_FILE = os.path.join(ROOT, "starfield.html")
ANDROID_HTML = os.path.join(ROOT, "android", "app", "src", "main", "assets", "starfield.html")
VERSION_FILE = os.path.join(ROOT, "version.json")
ANDROID_VERSION = os.path.join(ROOT, "android", "app", "src", "main", "assets", "version.json")
SW_FILE = os.path.join(ROOT, "service-worker.js")
ANDROID_SW = os.path.join(ROOT, "android", "app", "src", "main", "assets", "service-worker.js")
STUDIO_FILE = os.path.join(ROOT, "planet_studio.html")
ANDROID_STUDIO = os.path.join(ROOT, "android", "app", "src", "main", "assets", "planet_studio.html")
JAVA_FILE = os.path.join(ROOT, "android", "app", "src", "main", "java", "com", "starfield", "focus", "MainActivity.java")


def sha256_of_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def apply_step(content, target, repl, step_name):
    if repl in content:
        print(f"  [OK-ALREADY] {step_name}")
        return content
    elif target in content:
        print(f"  [APPLY] {step_name}")
        return content.replace(target, repl)
    else:
        raise AssertionError(f"Target not found for step: {step_name}")


def apply_build195():
    print("=================================================================")
    print(" APPLYING BUILD 195 (v1.9.9.9.9.7) COMPREHENSIVE BUG FIXES")
    print("=================================================================")

    # -----------------------------------------------------------------
    # A. Patch starfield.html
    # -----------------------------------------------------------------
    print("1. Reading starfield.html...")
    with open(HTML_FILE, "r", encoding="utf-8") as f:
        html = f.read()

    target_fix1 = """      if (shouldRenderWebGL) {
        model.renderAge = 0;
        model.hasRendered = true;
        this._lastRenderedId = pId;
        this.renderer.render(this.scene, this.camera);
        if (isMob) {
          return this.canvas;
        }
        if (model.canvas) {
          model.ctx.clearRect(0, 0, 512, 512);
          model.ctx.drawImage(this.canvas, 0, 0);
        }
      }"""
    repl_fix1 = """      if (shouldRenderWebGL) {
        model.renderAge = 0;
        model.hasRendered = true;
        this._lastRenderedId = pId;
        this.renderer.render(this.scene, this.camera);
        if (model.canvas && model.ctx) {
          model.ctx.clearRect(0, 0, model.canvas.width, model.canvas.height);
          model.ctx.drawImage(this.canvas, 0, 0);
        }
        if (isMob) {
          return this.canvas;
        }
      }"""
    html = apply_step(html, target_fix1, repl_fix1, "Fix 1: LivingPlanetEngine secondary planet copy")

    target_fix2 = """      sizeTo(p.canvas);

      var item = p.item || {};
      var key = (item.tier || 'common') + '|' + (item.hue || 200);
      if (key !== curKey) buildFor(item);"""
    repl_fix2 = """      sizeTo(p.canvas);

      var item = p.item || {};
      var buildupStage = window.SFBuildup ? window.SFBuildup.stage(item) : 0;
      var key = (item.tier || 'common') + '|' + (item.hue || 200) + '|' + buildupStage;
      if (key !== curKey) buildFor(item);"""
    html = apply_step(html, target_fix2, repl_fix2, "Fix 2: SFPlanetGL buildupStage key recreation storm")

    target_fix3 = """    this.currentAudio = snd;
    snd.volume = 0.95;
    let ended = false;"""
    repl_fix3 = """    this.currentAudio = snd;
    const vScale = (typeof this.volumeScale === 'number') ? this.volumeScale : 1.0;
    snd.volume = Math.max(0, Math.min(1, 0.95 * vScale));
    let ended = false;"""
    html = apply_step(html, target_fix3, repl_fix3, "Fix 3: Narrator._executeSpeak volumeScale setting slider")

    target_fix4a = """      try {
        const AC = window.AudioContext || window.webkitAudioContext;
        if (!AC) return;
        this.ac = new AC();
        this.masterGain = this.ac.createGain();
        this.masterGain.gain.value = 0.85;
        this.masterGain.connect(this.ac.destination);
      } catch (e) {
        console.warn('[ScannerAudio] AudioContext init deferred:', e);
      }"""
    repl_fix4a = """      try {
        const AC = window.AudioContext || window.webkitAudioContext;
        if (!AC && !(window.StarfieldAudio && window.StarfieldAudio.getContext)) return;
        this.ac = (window.StarfieldAudio && window.StarfieldAudio.getContext) ? window.StarfieldAudio.getContext() : new AC();
        if (this.ac) {
          const sfxDest = (window.StarfieldAudio && window.StarfieldAudio.sfxBus) ? window.StarfieldAudio.sfxBus : this.ac.destination;
          this.masterGain = this.ac.createGain();
          this.masterGain.gain.value = 0.85;
          this.masterGain.connect(sfxDest);
        }
      } catch (e) {
        console.warn('[ScannerAudio] AudioContext init deferred:', e);
      }"""
    html = apply_step(html, target_fix4a, repl_fix4a, "Fix 4A: ScannerAudio SFX bus routing")

    target_fix4b = """  // Web Audio procedural sound
  var audioCtx = null;
  function getAudio() {
    if (!audioCtx) {
      var AC = window.AudioContext || window.webkitAudioContext;
      if (AC) audioCtx = new AC();
    }
    if (audioCtx && audioCtx.state === 'suspended') audioCtx.resume();
    return audioCtx;
  }

  /* 正弦双音 + 低通上扫：玻璃感，不用锯齿（原方案太脏）。 */
  function playDrone() {
    var ctx = getAudio(); if (!ctx) return;
    try {
      var t0 = ctx.currentTime;
      var g = ctx.createGain();
      g.gain.setValueAtTime(0.0001, t0);
      g.gain.exponentialRampToValueAtTime(0.050, t0 + 0.55);
      g.gain.exponentialRampToValueAtTime(0.0001, t0 + 1.55);
      var lp = ctx.createBiquadFilter();
      lp.type = 'lowpass';
      lp.frequency.setValueAtTime(340, t0);
      lp.frequency.exponentialRampToValueAtTime(1500, t0 + 1.25);
      var tones = [220, 329.63];
      for (var i = 0; i < tones.length; i++) {
        var osc = ctx.createOscillator();
        osc.type = 'sine';
        osc.frequency.setValueAtTime(tones[i], t0);
        osc.detune.setValueAtTime(i ? 6 : -6, t0);
        osc.connect(lp);
        osc.start(t0);
        osc.stop(t0 + 1.6);
      }
      lp.connect(g);
      g.connect(ctx.destination);
    } catch (e) {}
  }

  function playSupernovaChime(tier) {
    var ctx = getAudio(); if (!ctx) return;
    try {
      var freqs = tier === 'myth' ? [523.25, 659.25, 783.99, 1046.50, 1318.51] :
                  tier === 'legend' ? [440, 554.37, 659.25, 880] :
                  tier === 'epic' ? [392, 493.88, 587.33, 783.99] :
                  [329.63, 392, 523.25];
      freqs.forEach(function(f, idx) {
        var osc = ctx.createOscillator(), gain = ctx.createGain();
        osc.type = 'sine';
        osc.frequency.setValueAtTime(f, ctx.currentTime + idx * 0.05);
        gain.gain.setValueAtTime(0.001, ctx.currentTime + idx * 0.05);
        gain.gain.linearRampToValueAtTime(0.14, ctx.currentTime + idx * 0.05 + 0.08);
        gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + idx * 0.05 + 1.8);
        osc.connect(gain); gain.connect(ctx.destination);
        osc.start(ctx.currentTime + idx * 0.05); osc.stop(ctx.currentTime + idx * 0.05 + 1.9);
      });
    } catch(e) {}
  }"""
    repl_fix4b = """  // Web Audio procedural sound
  var audioCtx = null;
  function getAudio() {
    if (!audioCtx) {
      if (window.StarfieldAudio && window.StarfieldAudio.getContext) {
        audioCtx = window.StarfieldAudio.getContext();
      } else {
        var AC = window.AudioContext || window.webkitAudioContext;
        if (AC) audioCtx = new AC();
      }
    }
    if (audioCtx && audioCtx.state === 'suspended') audioCtx.resume();
    return audioCtx;
  }

  /* 正弦双音 + 低通上扫：玻璃感，不用锯齿（原方案太脏）。 */
  function playDrone() {
    var ctx = getAudio(); if (!ctx) return;
    try {
      var t0 = ctx.currentTime;
      var g = ctx.createGain();
      g.gain.setValueAtTime(0.0001, t0);
      g.gain.exponentialRampToValueAtTime(0.050, t0 + 0.55);
      g.gain.exponentialRampToValueAtTime(0.0001, t0 + 1.55);
      var lp = ctx.createBiquadFilter();
      lp.type = 'lowpass';
      lp.frequency.setValueAtTime(340, t0);
      lp.frequency.exponentialRampToValueAtTime(1500, t0 + 1.25);
      var tones = [220, 329.63];
      for (var i = 0; i < tones.length; i++) {
        var osc = ctx.createOscillator();
        osc.type = 'sine';
        osc.frequency.setValueAtTime(tones[i], t0);
        osc.detune.setValueAtTime(i ? 6 : -6, t0);
        osc.connect(lp);
        osc.start(t0);
        osc.stop(t0 + 1.6);
      }
      var sfxDest = (window.StarfieldAudio && window.StarfieldAudio.sfxBus) ? window.StarfieldAudio.sfxBus : ctx.destination;
      lp.connect(g);
      g.connect(sfxDest);
    } catch (e) {}
  }

  function playSupernovaChime(tier) {
    var ctx = getAudio(); if (!ctx) return;
    try {
      var freqs = tier === 'myth' ? [523.25, 659.25, 783.99, 1046.50, 1318.51] :
                  tier === 'legend' ? [440, 554.37, 659.25, 880] :
                  tier === 'epic' ? [392, 493.88, 587.33, 783.99] :
                  [329.63, 392, 523.25];
      freqs.forEach(function(f, idx) {
        var osc = ctx.createOscillator(), gain = ctx.createGain();
        osc.type = 'sine';
        osc.frequency.setValueAtTime(f, ctx.currentTime + idx * 0.05);
        gain.gain.setValueAtTime(0.001, ctx.currentTime + idx * 0.05);
        gain.gain.linearRampToValueAtTime(0.14, ctx.currentTime + idx * 0.05 + 0.08);
        gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + idx * 0.05 + 1.8);
        var sfxDest = (window.StarfieldAudio && window.StarfieldAudio.sfxBus) ? window.StarfieldAudio.sfxBus : ctx.destination;
        osc.connect(gain); gain.connect(sfxDest);
        osc.start(ctx.currentTime + idx * 0.05); osc.stop(ctx.currentTime + idx * 0.05 + 1.9);
      });
    } catch(e) {}
  }"""
    html = apply_step(html, target_fix4b, repl_fix4b, "Fix 4B: CardCraft SFX bus routing")

    target_fix4c = """  /* All failures are swallowed: no output device, blocked autoplay or a
   * context that failed to start must leave the visual reveal untouched. */
  function playArpeggio(tier, rank) {
    window.__sfRevealSfxFired = true;
    window.__sfRevealSfxTier = tier;
    var notes = NOTES[tier] || NOTES.common;
    window.__sfRevealSfxNotes = notes.length;
    try {
      var AC = window.AudioContext || window.webkitAudioContext;
      if (!AC) { window.__sfRevealSfxState = 'unsupported'; return; }
      if (!actx || actx.state === 'closed') actx = new AC();
      if (actx.state === 'suspended' && typeof actx.resume === 'function') {
        try {
          var p = actx.resume();
          if (p && typeof p.then === 'function') {
            p.then(function () {
              window.__sfRevealSfxState = actx ? actx.state : 'gone';
            }, function () {
              window.__sfRevealSfxState = 'resume-blocked';
            });
          }
        } catch (e) { /* blocked: stay silent */ }
      }
      var t0 = actx.currentTime + 0.02;
      var master = actx.createGain();
      master.gain.setValueAtTime(0.14, t0);
      var lp = actx.createBiquadFilter();
      lp.type = 'lowpass';
      lp.frequency.setValueAtTime(5200, t0);
      master.connect(lp);
      lp.connect(actx.destination);"""
    repl_fix4c = """  /* All failures are swallowed: no output device, blocked autoplay or a
   * context that failed to start must leave the visual reveal untouched. */
  function playArpeggio(tier, rank) {
    window.__sfRevealSfxFired = true;
    window.__sfRevealSfxTier = tier;
    var notes = NOTES[tier] || NOTES.common;
    window.__sfRevealSfxNotes = notes.length;
    try {
      var AC = window.AudioContext || window.webkitAudioContext;
      if (!AC && !(window.StarfieldAudio && window.StarfieldAudio.getContext)) { window.__sfRevealSfxState = 'unsupported'; return; }
      if (!actx || actx.state === 'closed') {
        actx = (window.StarfieldAudio && window.StarfieldAudio.getContext) ? window.StarfieldAudio.getContext() : new AC();
      }
      if (actx && actx.state === 'suspended' && typeof actx.resume === 'function') {
        try {
          var p = actx.resume();
          if (p && typeof p.then === 'function') {
            p.then(function () {
              window.__sfRevealSfxState = actx ? actx.state : 'gone';
            }, function () {
              window.__sfRevealSfxState = 'resume-blocked';
            });
          }
        } catch (e) { /* blocked: stay silent */ }
      }
      var t0 = actx.currentTime + 0.02;
      var master = actx.createGain();
      master.gain.setValueAtTime(0.14, t0);
      var lp = actx.createBiquadFilter();
      lp.type = 'lowpass';
      lp.frequency.setValueAtTime(5200, t0);
      var sfxDest = (window.StarfieldAudio && window.StarfieldAudio.sfxBus) ? window.StarfieldAudio.sfxBus : actx.destination;
      master.connect(lp);
      lp.connect(sfxDest);"""
    html = apply_step(html, target_fix4c, repl_fix4c, "Fix 4C: RevealSfx SFX bus routing")

    target_fix4d_ac = """  function ac() {
    if (!ctx) {
      var AC = window.AudioContext || window.webkitAudioContext;
      if (!AC) return null;
      ctx = new AC();
    }
    if (ctx.state === 'suspended') { try { ctx.resume(); } catch (e) {} }
    return ctx;
  }"""
    repl_fix4d_ac = """  function ac() {
    if (!ctx) {
      if (window.StarfieldAudio && window.StarfieldAudio.getContext) {
        ctx = window.StarfieldAudio.getContext();
      } else {
        var AC = window.AudioContext || window.webkitAudioContext;
        if (!AC) return null;
        ctx = new AC();
      }
    }
    if (ctx && ctx.state === 'suspended') { try { ctx.resume(); } catch (e) {} }
    return ctx;
  }"""
    html = apply_step(html, target_fix4d_ac, repl_fix4d_ac, "Fix 4D-1: SFAmbience ac() routing")

    target_fix4d_dest = """    master = c.createGain();
    master.gain.setValueAtTime(0.0001, t);
    master.gain.exponentialRampToValueAtTime(v.gain, t + 2.2);  /* 淡入，别突兀 */
    master.connect(c.destination);"""
    repl_fix4d_dest = """    master = c.createGain();
    master.gain.setValueAtTime(0.0001, t);
    master.gain.exponentialRampToValueAtTime(v.gain, t + 2.2);  /* 淡入，别突兀 */
    var sfxDest = (window.StarfieldAudio && window.StarfieldAudio.sfxBus) ? window.StarfieldAudio.sfxBus : c.destination;
    master.connect(sfxDest);"""
    html = apply_step(html, target_fix4d_dest, repl_fix4d_dest, "Fix 4D-2: SFAmbience master bus routing")

    target_fix5_gl2 = """        vec2 p = gl_PointCoord - vec2(0.5);
        float r = length(p);
        float a = smoothstep(0.5, 0.15, r) * vAlpha;
        fragColor = vec4(uInk * a, a);"""
    repl_fix5_gl2 = """        vec2 p = gl_PointCoord - vec2(0.5);
        float r = length(p);
        float a = (1.0 - smoothstep(0.15, 0.5, r)) * vAlpha;
        fragColor = vec4(uInk * a, a);"""
    html = apply_step(html, target_fix5_gl2, repl_fix5_gl2, "Fix 5-1: GLSL ES smoothstep in WebGL2")

    target_fix5_gl1 = """        vec2 p = gl_PointCoord - vec2(0.5);
        float r = length(p);
        float a = smoothstep(0.5, 0.15, r) * vAlpha;
        gl_FragColor = vec4(uInk * a, a);"""
    repl_fix5_gl1 = """        vec2 p = gl_PointCoord - vec2(0.5);
        float r = length(p);
        float a = (1.0 - smoothstep(0.15, 0.5, r)) * vAlpha;
        gl_FragColor = vec4(uInk * a, a);"""
    html = apply_step(html, target_fix5_gl1, repl_fix5_gl1, "Fix 5-2: GLSL ES smoothstep in WebGL1")

    target_fix6_eye = """ const horizontal = Math.cos(camera.pitch) * camera.distance;
 const curSkimW = skimRes ? skimRes.sw : 0;
 let eye = [
  lookTarget[0] + Math.sin(camera.yaw) * horizontal,
  lookTarget[1] + Math.sin(camera.pitch) * camera.distance,
  lookTarget[2] - Math.cos(camera.yaw) * horizontal
 ];
 eye[0] = mix(eye[0], routeX(eye[2]), camera.lane * 0.90 * (1 - curSkimW));
 camera.eye = eye;"""
    repl_fix6_eye = """ const horizontal = Math.cos(camera.pitch) * camera.distance;
 const curSkimW = skimRes ? skimRes.sw : 0;
 const kickZ = (WarpDrive.shake > 0.05) ? WarpDrive.brakeKick : 0;
 let eye = [
  lookTarget[0] + Math.sin(camera.yaw) * horizontal,
  lookTarget[1] + Math.sin(camera.pitch) * camera.distance,
  lookTarget[2] - Math.cos(camera.yaw) * horizontal - kickZ
 ];
 eye[0] = mix(eye[0], routeX(eye[2]), camera.lane * 0.90 * (1 - curSkimW));
 camera.eye = eye;"""
    html = apply_step(html, target_fix6_eye, repl_fix6_eye, "Fix 6-1: Camera eye kickZ")

    target_fix6_post = """ if(WarpDrive.shake > 0.05){
  camera.cx += (Math.random() - 0.5) * WarpDrive.shake * 3.5;
  camera.cy += (Math.random() - 0.5) * WarpDrive.shake * 2.5;
  camera.eye[2] -= WarpDrive.brakeKick;
 }"""
    repl_fix6_post = """ if(WarpDrive.shake > 0.05){
  camera.cx += (Math.random() - 0.5) * WarpDrive.shake * 3.5;
  camera.cy += (Math.random() - 0.5) * WarpDrive.shake * 2.5;
 }"""
    html = apply_step(html, target_fix6_post, repl_fix6_post, "Fix 6-2: Remove post-basis eye[2] kick")

    target_fix7 = """function updateGravity(){
 activeMasses.length = 0;
 stepOrbits();
 const k0 = Math.floor(travel / CHUNK);
 const gBack = _isMobileDevice ? 18 : 36, gFwd = _isMobileDevice ? 32 : 52;
 for(let k = k0 - gBack; k <= k0 + gFwd; k++){
  const c = chunk(k);
  if(!c || !c.masses) continue;
  for(const m of c.masses){
   const dz = m.z - travel;
   if(m.kind === 4){
    if(dz >= -120000 && dz <= 168000){ activeMasses.push(m); window.__sfBH = m; }
   } else {
    if(dz >= -120000 && dz <= 140000) activeMasses.push(m);
   }
  }
 }
 window.activeMasses = activeMasses;"""
    repl_fix7 = """function updateGravity(){
 activeMasses.length = 0;
 stepOrbits();
 let currentBH = null;
 const k0 = Math.floor(travel / CHUNK);
 const gBack = _isMobileDevice ? 18 : 36, gFwd = _isMobileDevice ? 32 : 52;
 for(let k = k0 - gBack; k <= k0 + gFwd; k++){
  const c = chunk(k);
  if(!c || !c.masses) continue;
  for(const m of c.masses){
   const dz = m.z - travel;
   if(m.kind === 4){
    if(dz >= -120000 && dz <= 168000){ activeMasses.push(m); currentBH = m; }
   } else {
    if(dz >= -120000 && dz <= 140000) activeMasses.push(m);
   }
  }
 }
 window.__sfBH = currentBH;
 window.activeMasses = activeMasses;"""
    html = apply_step(html, target_fix7, repl_fix7, "Fix 7: Reset window.__sfBH to currentBH")

    target_fix10 = """function nebulaTex(seed,idx){
 const pal=NEB_PAL[idx % NEB_PAL.length] || NEB_PAL[0];
 const key=seed+'|'+idx;
 if(nebCache.has(key))return nebCache.get(key);"""
    repl_fix10 = """function nebulaTex(seed,idx){
 const pal=NEB_PAL[idx % NEB_PAL.length] || NEB_PAL[0];
 const key=seed+'|'+idx;
 if(nebCache.has(key)){
  const val = nebCache.get(key);
  nebCache.delete(key);
  nebCache.set(key, val);
  return val;
 }"""
    html = apply_step(html, target_fix10, repl_fix10, "Fix 10: Nebula cache true LRU")

    target_starfield_neb = "getNebPalettes:()=>NEB_PAL,nebulaTex:(s,i)=>nebulaTex(s,i),"
    repl_starfield_neb = "getNebPalettes:()=>NEB_PAL,nebulaTex:(s,i)=>nebulaTex(s,i),getNebCache:()=>nebCache,"
    html = apply_step(html, target_starfield_neb, repl_starfield_neb, "Fix 10b: Expose getNebCache on Starfield")

    target_fix11 = """      let simX = leadPos[0], simY = leadPos[1], simZ = leadPos[2];
      let simVx = (routeX(travel + 100) - routeX(travel)) * 12;
      let simVy = (courseY(travel + 100) - courseY(travel)) * 12;
      let simVz = SPEED * (1 + (warp || 0));"""
    repl_fix11 = """      let simX = leadPos[0], simY = leadPos[1], simZ = leadPos[2];
      let simVx = (routeX(travel + 100) - routeX(travel)) * 12;
      let simVy = (courseY(travel + 100) - courseY(travel)) * 12;
      const effWarp = Math.max(warp || 0, (typeof WarpDrive !== 'undefined' && WarpDrive.currentWarp) ? WarpDrive.currentWarp : 0);
      let simVz = SPEED * (1 + effWarp);"""
    html = apply_step(html, target_fix11, repl_fix11, "Fix 11: Orbit mechanics speed scaling effWarp")

    target_fix12_loop = """ for(const b of fleet){
  // Preserve delicate flapping flock formation
  const wx = routeX(travel) + b.bx + lateralOffset;
  const wy = courseY(travel) + b.by + vertOffset;
  const wz = travel + b.bz;
  b.x = wx - routeX(travel);
  b.y = wy - courseY(travel);
  b.z = wz - travel;
 }"""
    repl_fix12_loop = """ for(const b of fleet){
  // Preserve delicate flapping flock formation
  const wx = routeX(travel) + b.bx + lateralOffset;
  const wy = courseY(travel) + b.by + vertOffset;
  const wz = travel + b.bz;
  b.x = wx - routeX(travel);
  b.y = wy - courseY(travel);
  b.z = wz - travel;
  b.vx = 0; b.vy = 0; b.vz = 0;
 }"""
    html = apply_step(html, target_fix12_loop, repl_fix12_loop, "Fix 12-1: Reset fleet velocity during capture")

    target_fix12_exit = """ // End of 60-second flyby encounter
 if(captureT >= 60.0){
  if(m) m.passed = true;
  capturePhase = 0;
  captureMass = null;
  captureCamPose = null;
  warp = 0;
  sound.setTension(false);
  toast('重返浩瀚深空 · DEEP SPACE RESUMED', 5);"""
    repl_fix12_exit = """ // End of 60-second flyby encounter
 if(captureT >= 60.0){
  if(m) m.passed = true;
  capturePhase = 0;
  captureMass = null;
  captureCamPose = null;
  warp = 0;
  sound.setTension(false);
  for(const b of fleet){
   b.vx = 0; b.vy = 0; b.vz = 0;
   b.ax = 0; b.ay = 0; b.az = 0;
  }
  toast('重返浩瀚深空 · DEEP SPACE RESUMED', 5);"""
    html = apply_step(html, target_fix12_exit, repl_fix12_exit, "Fix 12-2: Reset fleet velocity exiting capture")

    target_fix13 = """    const down = (e) => {
      if ((typeof currentMode !== 'undefined' && currentMode !== 'cruise') || (window.currentMode && window.currentMode !== 'cruise')) return;
      const t = e.target;
      if (t && t.closest && t.closest('button, .sf-touch-cluster, .sf-touch-joy-zone, .sf-touch-more-tray, #settings-drawer, #codex-modal, #sf-contract-hud, #sf-descent-btn, #sf-sonar-capsule')) return;
      if (!Engine.isFlightStarted || !Engine.isFlightStarted()) return;
      startX = e.clientX;
      startY = e.clientY;
      stage = 0;
      t1 = setTimeout(() => {
        stage = 1; gear(1);
        t2 = setTimeout(() => { stage = 2; gear(2); }, 850);
      }, 320);
    };
    const move = (e) => {
      if (stage === 0 && (t1 || t2)) {
        if (Math.hypot(e.clientX - startX, e.clientY - startY) > 12) {
          clear();
        }
      }
    };
    const up = () => { clear(); if (stage > 0) gear(0); stage = 0; };"""
    repl_fix13 = """    const down = (e) => {
      if (!e.isPrimary) return;
      if ((typeof currentMode !== 'undefined' && currentMode !== 'cruise') || (window.currentMode && window.currentMode !== 'cruise')) return;
      const t = e.target;
      if (t && t.closest && t.closest('button, .sf-touch-cluster, .sf-touch-joy-zone, .sf-touch-more-tray, #settings-drawer, #codex-modal, #sf-contract-hud, #sf-descent-btn, #sf-sonar-capsule')) return;
      if (!Engine.isFlightStarted || !Engine.isFlightStarted()) return;
      startX = e.clientX;
      startY = e.clientY;
      stage = 0;
      t1 = setTimeout(() => {
        stage = 1; gear(1);
        t2 = setTimeout(() => { stage = 2; gear(2); }, 850);
      }, 320);
    };
    const move = (e) => {
      if (e && !e.isPrimary) return;
      if (stage === 0 && (t1 || t2)) {
        if (Math.hypot(e.clientX - startX, e.clientY - startY) > 12) {
          clear();
        }
      }
    };
    const up = (e) => {
      if (e && !e.isPrimary) return;
      clear(); if (stage > 0) gear(0); stage = 0;
    };"""
    html = apply_step(html, target_fix13, repl_fix13, "Fix 13: Touch gesture conflict primary check")

    target_fix14_toast = "window.toast(`渲染遥测: ${fps} FPS · 刷新率 ${hz}Hz · 视网膜 ${(dpr*scale).toFixed(2)}x (${modeName}) · 耗时 ${ms.toFixed(1)}ms`);"
    repl_fix14_toast = "window.toast(`渲染遥测: ${fps} FPS · 刷新率 ${hz}Hz · 视网膜 ${(dpr).toFixed(2)}x (${modeName}) · 耗时 ${ms.toFixed(1)}ms`);"
    html = apply_step(html, target_fix14_toast, repl_fix14_toast, "Fix 14-1: Perf HUD toast DPR")

    target_fix14_hud = """    if (dprEl) {
      dprEl.textContent = `${(dpr * scale).toFixed(2)}x`;
    }"""
    repl_fix14_hud = """    if (dprEl) {
      dprEl.textContent = `${(dpr).toFixed(2)}x`;
    }"""
    html = apply_step(html, target_fix14_hud, repl_fix14_hud, "Fix 14-2: Perf HUD badge DPR")

    target_fix15 = """ isModalOpen:()=>{
  const hangarOpen = (typeof FleetCustomizer !== 'undefined' && FleetCustomizer.isOpen) || ($('hangar-modal') && $('hangar-modal').classList.contains('open'));
  const hatchOpen = ($('sf-hatch') && $('sf-hatch').classList.contains('active')) || ($('sf-hatch-list') && $('sf-hatch-list').classList.contains('on'));
  const focusOpen = (window.StarfieldFocusEngine && window.StarfieldFocusEngine.isDashboardOpen);
  const upgradesOpen = !!(window.StarfieldShipUpgrades && window.StarfieldShipUpgrades.isOpen);
  return PhotoStudio.active||$('codex-modal').classList.contains('open')||$('settings-drawer').classList.contains('open')||focusOpen||upgradesOpen||hangarOpen||hatchOpen;
 },
 closeModal:()=>{
  if(window.StarfieldShipUpgrades && window.StarfieldShipUpgrades.isOpen)window.StarfieldShipUpgrades.closeModal();
  else if(PhotoStudio.active)PhotoStudio.close();
  else if(typeof FleetCustomizer !== 'undefined' && FleetCustomizer.isOpen)FleetCustomizer.close();
  else if($('hangar-modal') && $('hangar-modal').classList.contains('open'))$('hangar-modal').classList.remove('open');
  else if($('codex-modal').classList.contains('open'))Codex.close();
  else if($('sf-hatch-list') && $('sf-hatch-list').classList.contains('on'))$('sf-hatch-list').classList.remove('on');
  else if($('sf-hatch') && $('sf-hatch').classList.contains('active'))$('sf-hatch').classList.remove('active');
  else if($('settings-drawer').classList.contains('open'))GameSettings.close();
  else if(window.StarfieldFocusEngine && window.StarfieldFocusEngine.isDashboardOpen)window.StarfieldFocusEngine.closeDashboard();
 },"""
    repl_fix15 = """ isModalOpen:()=>{
  const hangarOpen = (typeof FleetCustomizer !== 'undefined' && FleetCustomizer.isOpen) || ($('hangar-modal')?.classList?.contains('open'));
  const hatchOpen = ($('sf-hatch')?.classList?.contains('active')) || ($('sf-hatch-list')?.classList?.contains('on'));
  const focusOpen = !!(window.StarfieldFocusEngine && window.StarfieldFocusEngine.isDashboardOpen);
  const upgradesOpen = !!(window.StarfieldShipUpgrades && window.StarfieldShipUpgrades.isOpen);
  return !!(PhotoStudio.active||$('codex-modal')?.classList?.contains('open')||$('settings-drawer')?.classList?.contains('open')||focusOpen||upgradesOpen||hangarOpen||hatchOpen);
 },
 closeModal:()=>{
  if(window.StarfieldShipUpgrades && window.StarfieldShipUpgrades.isOpen)window.StarfieldShipUpgrades.closeModal();
  else if(PhotoStudio.active)PhotoStudio.close();
  else if(typeof FleetCustomizer !== 'undefined' && FleetCustomizer.isOpen)FleetCustomizer.close();
  else if($('hangar-modal')?.classList?.contains('open'))$('hangar-modal').classList.remove('open');
  else if($('codex-modal')?.classList?.contains('open'))Codex.close();
  else if($('sf-hatch-list')?.classList?.contains('on'))$('sf-hatch-list').classList.remove('on');
  else if($('sf-hatch')?.classList?.contains('active'))$('sf-hatch').classList.remove('active');
  else if($('settings-drawer')?.classList?.contains('open'))GameSettings.close();
  else if(window.StarfieldFocusEngine && window.StarfieldFocusEngine.isDashboardOpen)window.StarfieldFocusEngine.closeDashboard();
 },"""
    html = apply_step(html, target_fix15, repl_fix15, "Fix 15: Modal safe check optional chaining")

    target_vtag = '<span class="shortcut-key" id="sf-version-tag">v1.9.9.9.9.6 (Build 194)</span>'
    repl_vtag = '<span class="shortcut-key" id="sf-version-tag">v1.9.9.9.9.7 (Build 195)</span>'
    html = apply_step(html, target_vtag, repl_vtag, "Version bump in UI tag")

    target_lbuild = 'const localBuild = 194;'
    repl_lbuild = 'const localBuild = 195;'
    html = apply_step(html, target_lbuild, repl_lbuild, "Version bump in localBuild")

    print("Writing updated starfield.html...")
    with open(HTML_FILE, "w", encoding="utf-8", newline="\n") as f:
        f.write(html)

    # -----------------------------------------------------------------
    # B. Patch MainActivity.java
    # -----------------------------------------------------------------
    print("Reading MainActivity.java...")
    with open(JAVA_FILE, "r", encoding="utf-8") as f:
        java = f.read()

    target_java_load = """        // 1. Initial Page Load (Cached active update file or bundled asset fallback)
        File activeHtml = new File(getFilesDir(), "starfield_active.html");
        if (activeHtml.exists() && activeHtml.length() > 500000) {
            webView.loadUrl("file://" + activeHtml.getAbsolutePath());
        } else {
            webView.loadUrl("file:///android_asset/starfield.html");
        }"""
    repl_java_load = """        // 1. Initial Page Load (Cached active update file or bundled asset fallback)
        SharedPreferences prefs = getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE);
        long currentBuild = prefs.getLong(KEY_BUILD, 0L);
        long bundledBuild = getBundledBuild();

        File activeHtml = new File(getFilesDir(), "starfield_active.html");
        if (bundledBuild >= currentBuild && activeHtml.exists()) {
            activeHtml.delete();
            prefs.edit().putLong(KEY_BUILD, bundledBuild).apply();
        }

        if (activeHtml.exists() && activeHtml.length() > 500000) {
            webView.loadUrl("file://" + activeHtml.getAbsolutePath());
        } else {
            webView.loadUrl("file:///android_asset/starfield.html");
        }"""
    java = apply_step(java, target_java_load, repl_java_load, "Fix 8-1: MainActivity asset hijack check")

    target_java_method = """    public void triggerOtaCheck(final boolean isManual) {"""
    repl_java_method = """    private long getBundledBuild() {
        try (InputStream is = getAssets().open("version.json")) {
            BufferedReader reader = new BufferedReader(new InputStreamReader(is, "UTF-8"));
            StringBuilder sb = new StringBuilder();
            String line;
            while ((line = reader.readLine()) != null) sb.append(line);
            JSONObject json = new JSONObject(sb.toString());
            return json.optLong("build", 0L);
        } catch (Exception e) {
            Log.w("StarfieldOTA", "Failed to read bundled version.json", e);
            return 0L;
        }
    }

    public void triggerOtaCheck(final boolean isManual) {"""
    if "private long getBundledBuild()" not in java:
        java = apply_step(java, target_java_method, repl_java_method, "Fix 8-2: getBundledBuild() helper")

    print("Writing updated MainActivity.java...")
    with open(JAVA_FILE, "w", encoding="utf-8", newline="\n") as f:
        f.write(java)

    # -----------------------------------------------------------------
    # C. Update service-worker.js
    # -----------------------------------------------------------------
    print("Updating service-worker.js...")
    with open(SW_FILE, "r", encoding="utf-8") as f:
        sw = f.read()
    sw = re.sub(
        r"const CACHE_VERSION = 'v[0-9.]+-b\d+';",
        r"const CACHE_VERSION = 'v1.9.9.9.9.7-b195';",
        sw
    )
    with open(SW_FILE, "w", encoding="utf-8", newline="\n") as f:
        f.write(sw)

    # -----------------------------------------------------------------
    # D. Update version.json
    # -----------------------------------------------------------------
    print("Updating version.json...")
    with open(VERSION_FILE, "r", encoding="utf-8") as f:
        ver_data = json.load(f)
    ver_data["version"] = "1.9.9.9.9.7"
    ver_data["build"] = 195
    ver_data["updated_at"] = "2026-11-18T21:30:00+08:00"
    ver_data["title"] = "深度全域优化与异常阻断：根治多机位渲染风暴与音频硬上限，满血跨端平稳运行 (Build 195)"
    ver_data["changelog"] = (
        "1. 根治移动端副星球与缓存星球白屏/黑屏：重构LivingPlanetEngine渲染管线，确保WebGL离屏光栅化结果每帧完整镜像至独立Canvas纹理；\n"
        "2. 阻断SFPlanetGL每帧Three.js网格重建风暴：补齐缓存键buildupStage阶段标识，消灭60 FPS无休止对象销毁与几何体垃圾回收卡顿；\n"
        "3. 修复Narrator语音音量滑块控制失效：在_executeSpeak正确挂载并计算volumeScale音量增益；\n"
        "4. 彻底收拢独立AudioContext与音频总线路由：收归ScannerAudio、CardCraft、RevealSfx及PlanetAmbientAudio至StarfieldAudio单例并汇入sfxBus，击碎移动端6-Context硬上限；\n"
        "5. 修正GLSL ES smoothstep参数顺序规范：将倒置范围重构为(1.0 - smoothstep)，消除特定移动端GPU着色器编译崩溃；\n"
        "6. 根治WarpDrive急刹时相机抖动与投影错位：在构建相机正交基前预先扣除brakeKick位移，确保视线与视锥体刚性一致；\n"
        "7. 消除黑洞引力透镜幽灵常驻泄漏：在updateGravity扫描范围外严谨复位__sfBH为null；\n"
        "8. 修复Android原生APK升级后旧版缓存覆盖新版资源：比对APK打包版本与本地OTA记录，高版本APK启动时自动清除陈旧HTML并直读打包资源；\n"
        "9. 补齐Android打包工程planet_studio.html与version.json双向镜像校验，确保100% SHA256哈希对齐；\n"
        "10. 星云贴图缓存升级为严格真LRU淘汰：访问缓存时刷新Map插入序，消除极速巡航时的FIFO缓存踩踏；\n"
        "11. 引力轨道推演力学全面适配超曲速巡航：轨迹预测模拟动态注入effWarp航速缩放；\n"
        "12. 消除黑洞掠过阶段结束时护航纸鹤相对速度尖峰爆发；\n"
        "13. 优化多指缩放触摸冲突：长按极速加速仅响应Primary主指针，消除双指缩放误触超光速飞窜；\n"
        "14. 纠正性能监视器HUD视网膜DPR倍率计算逻辑，杜绝二次折算畸变；\n"
        "15. 全面加固弹窗与抽屉classList安全链式调用，杜绝DOM节点缺失下的空指针异常。"
    )
    with open(VERSION_FILE, "w", encoding="utf-8", newline="\n") as f:
        json.dump(ver_data, f, ensure_ascii=False, indent=2)
        f.write("\n")

    # -----------------------------------------------------------------
    # E. Mirror assets to Android
    # -----------------------------------------------------------------
    print("Mirroring starfield.html to Android assets...")
    shutil.copyfile(HTML_FILE, ANDROID_HTML)

    print("Mirroring service-worker.js to Android assets...")
    shutil.copyfile(SW_FILE, ANDROID_SW)

    print("Mirroring version.json to Android assets...")
    shutil.copyfile(VERSION_FILE, ANDROID_VERSION)

    print("Copying planet_studio.html to Android assets...")
    shutil.copyfile(STUDIO_FILE, ANDROID_STUDIO)

    # -----------------------------------------------------------------
    # F. Assert SHA256 parity
    # -----------------------------------------------------------------
    print("Verifying SHA256 hash parity across root and Android assets...")
    pairs = [
        ("starfield.html", HTML_FILE, ANDROID_HTML),
        ("service-worker.js", SW_FILE, ANDROID_SW),
        ("version.json", VERSION_FILE, ANDROID_VERSION),
        ("planet_studio.html", STUDIO_FILE, ANDROID_STUDIO),
    ]
    for name, src, dst in pairs:
        h1 = sha256_of_file(src)
        h2 = sha256_of_file(dst)
        assert h1 == h2, f"SHA256 mismatch for {name}: {h1} vs {h2}"
        print(f"  [OK] {name}: {h1[:16]}... matched 100%")

    print("=================================================================")
    print(" >>> BUILD 195 APPLIED AND ALL ASSETS SYNCHRONIZED CLEANLY! <<<")
    print("=================================================================")


if __name__ == "__main__":
    apply_build195()
