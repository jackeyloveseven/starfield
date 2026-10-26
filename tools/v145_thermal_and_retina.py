import sys
import os

def apply_patch():
    file_path = os.path.abspath(r"d:\items\code\starfield-pub\starfield.html")
    with open(file_path, "r", encoding="utf-8", newline="") as f:
        src = f.read()

    def rep(old, new, desc=""):
        nonlocal src
        count = src.count(old)
        if count != 1:
            raise ValueError(f"Patch failed for '{desc}': found {count} occurrences (expected 1)")
        src = src.replace(old, new, 1)
        print(f"Applied: {desc}")

    # 1. Meta Viewport & Canvas CSS
    rep(
        '<meta name="viewport" content="width=device-width,initial-scale=1,maximum-scale=1,viewport-fit=cover">',
        '<meta name="viewport" content="width=device-width,initial-scale=1,maximum-scale=1,user-scalable=no,viewport-fit=cover">',
        "Viewport user-scalable=no"
    )

    rep(
        '#world{color:var(--ink);position:absolute;inset:0;overflow:hidden;touch-action:none;background:var(--paper);isolation:isolate}#landscape{position:absolute;width:100%;height:100%;inset:0;display:block;cursor:crosshair;touch-action:none}#landscape.manual{cursor:grab}#landscape.dragging{cursor:grabbing}',
        '#world{color:var(--ink);position:absolute;inset:0;overflow:hidden;touch-action:none;background:var(--paper);isolation:isolate}#landscape{position:absolute;width:100%;height:100%;inset:0;display:block;cursor:crosshair;touch-action:none;image-rendering:-webkit-optimize-contrast;-webkit-backface-visibility:hidden;backface-visibility:hidden;transform:translateZ(0)}#landscape.manual{cursor:grab}#landscape.dragging{cursor:grabbing}',
        "Canvas contrast & GPU layer CSS"
    )

    # 2. Black Hole Shader mobile step tuning
    old_boot = """    const fs=gl.createShader(gl.FRAGMENT_SHADER);
    gl.shaderSource(fs,GLSL_HOLE);
    gl.compileShader(fs);"""

    new_boot = """    const fs=gl.createShader(gl.FRAGMENT_SHADER);
    let tunedFS = GLSL_HOLE;
    if (_isMobileDevice) {
      tunedFS = tunedFS.replace(
        'for (int i = 0; i < 540; i++)',
        'for (int i = 0; i < 180; i++)'
      ).replace(
        'float dt = clamp(r < 6.5 ? (r - 0.96) * 0.020 : r * 0.048, 0.005, 2.5);',
        'float dt = clamp(r < 6.5 ? (r - 0.96) * 0.032 : r * 0.060, 0.008, 2.5);'
      );
    }
    gl.shaderSource(fs,tunedFS);
    gl.compileShader(fs);"""
    rep(old_boot, new_boot, "Mobile Black Hole 180-step GLSL_HOLE tuning")

    # 3. Dynamic SPRITE_CAP in drawHole
    old_cap = """  const sc = Math.min(1, SPRITE_CAP / Math.max(pw0, ph0));"""
    new_cap = """  const spriteCap = (window.STARFIELD_QUALITY && window.STARFIELD_QUALITY.getHoleSpriteCap) ? window.STARFIELD_QUALITY.getHoleSpriteCap() : (_isMobileDevice ? 512 : 1280);
  const sc = Math.min(1, spriteCap / Math.max(pw0, ph0));"""
    rep(old_cap, new_cap, "Dynamic Black Hole SpriteCap (512 on mobile)")

    # 4. STARFIELD_QUALITY DPR and mobile targetFPS
    old_quality = """window.STARFIELD_QUALITY = {
  profile: _isMobileDevice ? 'balanced' : '2k', // Mobile defaults to balanced for silky 60fps; Desktop defaults to 2K
  // Fill-rate ceilings by GPU class. A phone panel is 3x, but drawing 6 MP per
  // frame on a Mali is how a 60 fps piece becomes a 30 fps one.
  tierCap: { cpu: 1.0, mobile: 1.75, igpu: 1.6, dgpu: 2.0, balanced: 2.0 },
  getMaxDPR() {
    const raw = window.devicePixelRatio || 1.0;
    const cap = this.tierCap[_GPU.tier] || 2.0;
    if (this.profile === '2k') return Math.min(raw, Math.min(3.0, cap + 0.5));
    if (this.profile === 'balanced') return Math.min(raw, cap);
    return Math.min(raw, 1.25);
  },
  setProfile(p) {
    if (!['2k', 'balanced', 'powersave'].includes(p)) return;
    this.profile = p;
    try { localStorage.setItem('sf_quality_profile', p); } catch(e) {}
    this.updateUI();
    if (typeof resize === 'function') resize();
    if (window.toast) {
      const labels = { '2k': '2K 极清模式 (Retina Ultra)', 'balanced': '均衡高刷模式 (Smooth 60fps)', 'powersave': '能效省电模式 (Battery Saver)' };
      window.toast(`画质已切换: ${labels[p] || p}`);
    }
  },"""

    new_quality = """window.STARFIELD_QUALITY = {
  profile: _isMobileDevice ? 'balanced' : '2k', // Mobile defaults to balanced for silky 60fps; Desktop defaults to 2K
  tierCap: { cpu: 1.0, mobile: 2.0, igpu: 1.8, dgpu: 2.5, balanced: 2.0 },
  getTargetFps() {
    if (this.profile === 'powersave') return 45;
    if (this.profile === 'balanced' || _isMobileDevice) return 60;
    return 0; // 0 = native display refresh rate (Desktop 2K mode)
  },
  getHoleSpriteCap() {
    if (this.profile === 'powersave') return 384;
    if (_isMobileDevice || this.profile === 'balanced') return 512;
    return 1280;
  },
  getMaxDPR() {
    const raw = window.devicePixelRatio || 1.0;
    const cap = this.tierCap[_GPU.tier] || 2.0;
    if (this.profile === '2k') {
      const limit = _isMobileDevice ? 2.75 : 3.0;
      return Math.min(raw, Math.max(cap, limit));
    }
    if (this.profile === 'balanced') return Math.min(raw, cap);
    return Math.min(raw, 1.25);
  },
  setProfile(p) {
    if (!['2k', 'balanced', 'powersave'].includes(p)) return;
    this.profile = p;
    qualityScale = 1.0; // Reset scaler on profile switch
    fastWindows = 0;
    try { localStorage.setItem('sf_quality_profile', p); } catch(e) {}
    this.updateUI();
    if (typeof resize === 'function') resize();
    if (window.toast) {
      const labels = { '2k': '2K 极清视网膜 (Retina Ultra)', 'balanced': '均衡高清模式 (Smooth 60fps)', 'powersave': '能效省电模式 (Battery Saver)' };
      window.toast(`画质已切换: ${labels[p] || p}`);
    }
  },"""
    rep(old_quality, new_quality, "STARFIELD_QUALITY DPR tiers, 60fps target & 512 spriteCap")

    # 5. frame(now) throttle and adaptive scaler thresholds
    old_frame = """let lastFillPx=0,fps=60,framesInWindow=0,measureStart=performance.now(),slowWindows=0,fastWindows=0;
// The display's refresh, measured from the first clean frames. rAF cannot run
// faster than the panel, so this is the real ceiling - not 60.
let refreshHz=60,hzSamples=[],hzDone=false;
let __modalOpen=false;
function frame(now){
 requestAnimationFrame(frame);const realDt=Math.min(.05,Math.max(.001,(now-last)/1000));last=now;
 if(document.hidden)return;"""

    new_frame = """let lastFillPx=0,fps=60,framesInWindow=0,measureStart=performance.now(),slowWindows=0,fastWindows=0;
// The display's refresh, measured from the first clean frames. rAF cannot run
// faster than the panel, so this is the real ceiling - not 60.
let refreshHz=60,hzSamples=[],hzDone=false;
let __modalOpen=false;
let lastRenderTime=0;
function frame(now){
 requestAnimationFrame(frame);
 if(document.hidden)return;
 const targetFps = (window.STARFIELD_QUALITY && window.STARFIELD_QUALITY.getTargetFps) ? window.STARFIELD_QUALITY.getTargetFps() : 0;
 if (targetFps > 0) {
  const frameInterval = 1000 / targetFps;
  const elapsed = now - lastRenderTime;
  if (elapsed < frameInterval - 1.5) {
   return;
  }
  lastRenderTime = now - (elapsed % frameInterval);
 } else {
  lastRenderTime = now;
 }
 const realDt=Math.min(.05,Math.max(.001,(now-last)/1000));last=now;"""
    rep(old_frame, new_frame, "frame(now) mobile 60fps steady throttle")

    old_scaler = """  const cap=window.STARFIELD_QUALITY?window.STARFIELD_QUALITY.getMaxDPR():Math.min(devicePixelRatio||1,2);
  const target=Math.min(240,Math.max(60,refreshHz*0.92));
  if(fps<target*0.6&&qualityScale>.8){qualityScale=Math.max(.8,qualityScale-.1);resize();}
  else if(fps>target*0.95&&qualityScale<1&&++fastWindows>4){qualityScale=Math.min(1,qualityScale+.15);fastWindows=0;resize();}
  if(fps<=target*0.95)fastWindows=0;"""

    new_scaler = """  const cap=window.STARFIELD_QUALITY?window.STARFIELD_QUALITY.getMaxDPR():Math.min(devicePixelRatio||1,2);
  const is2k = (window.STARFIELD_QUALITY && window.STARFIELD_QUALITY.profile === '2k');
  const downFloor = is2k ? 32 : Math.min(42, Math.max(30, refreshHz * 0.5));
  const recCeil = is2k ? 45 : Math.min(54, refreshHz * 0.88);
  if(fps<downFloor&&qualityScale>.8){qualityScale=Math.max(.8,qualityScale-.1);resize();}
  else if(fps>recCeil&&qualityScale<1&&++fastWindows>2){qualityScale=Math.min(1,qualityScale+.1);fastWindows=0;resize();}
  if(fps<=recCeil)fastWindows=0;"""
    rep(old_scaler, new_scaler, "Adaptive downscaling threshold decoupled from 120Hz")

    # 6. AnomalyScanner onFrame & pollGamepad battery savers
    old_scan = """  function onFrame(now) {
    const dt = Math.min(0.1, Math.max(0.001, (now - lastFrameTime) / 1000));
    lastFrameTime = now;

    // Update Radar & Proximity
    ScannerRadar.update(dt);

    // Update Tuner
    RelicTuner.update(dt);

    // Draw 3D Overlay Canvas
    const canvas = document.getElementById('scanner-overlay-canvas');
    if (canvas) {
      const w = window.innerWidth, h = window.innerHeight;
      const dpr = (window.STARFIELD_QUALITY ? window.STARFIELD_QUALITY.getMaxDPR() : Math.min(window.devicePixelRatio || 1, 2.0));
      if (canvas.width !== Math.round(w * dpr) || canvas.height !== Math.round(h * dpr)) {
        canvas.width = Math.round(w * dpr);
        canvas.height = Math.round(h * dpr);
      }
      const ctx = canvas.getContext('2d');
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      ctx.clearRect(0, 0, w, h);

      // Render 3D Radar Wave & HUD Markers
      ScannerRadar.draw3D(ctx, w, h, dpr);
    }

    requestAnimationFrame(onFrame);
  }"""

    new_scan = """  function onFrame(now) {
    if (document.hidden) {
      requestAnimationFrame(onFrame);
      return;
    }
    const dt = Math.min(0.1, Math.max(0.001, (now - lastFrameTime) / 1000));
    lastFrameTime = now;

    // Update Radar & Proximity
    ScannerRadar.update(dt);

    // Update Tuner
    RelicTuner.update(dt);

    // Draw 3D Overlay Canvas only when radar is active or targets exist
    const hasActiveRadar = ScannerRadar.active || (ScannerRadar.detectedTargets && ScannerRadar.detectedTargets.size > 0);
    const canvas = document.getElementById('scanner-overlay-canvas');
    if (canvas && hasActiveRadar) {
      const w = window.innerWidth, h = window.innerHeight;
      const dpr = (window.STARFIELD_QUALITY ? window.STARFIELD_QUALITY.getMaxDPR() : Math.min(window.devicePixelRatio || 1, 1.5));
      if (canvas.width !== Math.round(w * dpr) || canvas.height !== Math.round(h * dpr)) {
        canvas.width = Math.round(w * dpr);
        canvas.height = Math.round(h * dpr);
      }
      const ctx = canvas.getContext('2d');
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      ctx.clearRect(0, 0, w, h);
      ScannerRadar.draw3D(ctx, w, h, dpr);
    } else if (canvas && !hasActiveRadar && canvas.width > 0) {
      const ctx = canvas.getContext('2d');
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      canvas.width = 0; canvas.height = 0;
    }

    requestAnimationFrame(onFrame);
  }"""
    rep(old_scan, new_scan, "AnomalyScanner idle clearRect saver")

    old_gp = """  function pollGamepad(now) {
    const dt = Math.min(0.05, Math.max(0.001, (now - lastFrameTime) / 1000));
    lastFrameTime = now;"""
    new_gp = """  function pollGamepad(now) {
    if (document.hidden) {
      rafId = requestAnimationFrame(pollGamepad);
      return;
    }
    const dt = Math.min(0.05, Math.max(0.001, (now - lastFrameTime) / 1000));
    lastFrameTime = now;"""
    rep(old_gp, new_gp, "pollGamepad document.hidden pause")

    with open(file_path, "w", encoding="utf-8", newline="") as f:
        f.write(src)
    print("SUCCESS: starfield.html patched with thermal and retina optimizations!")

if __name__ == "__main__":
    apply_patch()
