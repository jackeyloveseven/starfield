import os
import sys

def apply_focus_and_mobile_patch():
    target_path = os.path.abspath(r"d:\items\code\starfield-pub\starfield.html")
    with open(target_path, "r", encoding="utf-8") as f:
        content = f.read()

    crlf = "\r\n" in content
    nl = "\r\n" if crlf else "\n"

    def rep(old_block, new_block, name=""):
        nonlocal content
        old_normalized = old_block.replace("\r\n", "\n").replace("\n", nl)
        new_normalized = new_block.replace("\r\n", "\n").replace("\n", nl)
        cnt = content.count(old_normalized)
        if cnt != 1:
            raise ValueError(f"Failed replacement for [{name}]: found {cnt} occurrences (expected 1)")
        content = content.replace(old_normalized, new_normalized, 1)
        print(f"Applied: [{name}]")

    # -------------------------------------------------------------
    # 1. PWA Manifest & Meta Tags in <head>
    # -------------------------------------------------------------
    old_head = """<meta name="description" content="星空 · STARFIELD — 一场没有尽头的航行。零依赖 Canvas 程序化交互作品。">
<title>星空 · STARFIELD</title>"""

    new_head = """<meta name="description" content="星空 · STARFIELD — 一场没有尽头的航行。挂机深空探索与专注番茄钟。">
<link rel="manifest" href="manifest.json">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<meta name="apple-mobile-web-app-title" content="星空专注">
<title>星空 · STARFIELD // 深空专注探索</title>"""
    rep(old_head, new_head, "PWA Manifest & Mobile Web App Meta Tags")

    # -------------------------------------------------------------
    # 2. Responsive Portrait & Mobile Touch CSS (Remove #world.rotated)
    # -------------------------------------------------------------
    old_world_css = """#world{color:var(--ink);position:absolute;inset:0;overflow:hidden;touch-action:none;background:var(--paper);isolation:isolate}#world.rotated{inset:auto;left:50%;top:50%;transform:translate(-50%,-50%) rotate(90deg);transform-origin:center}#landscape{position:absolute;width:100%;height:100%;inset:0;display:block;cursor:crosshair;touch-action:none}"""
    new_world_css = """#world{color:var(--ink);position:absolute;inset:0;overflow:hidden;touch-action:none;background:var(--paper);isolation:isolate}#landscape{position:absolute;width:100%;height:100%;inset:0;display:block;cursor:crosshair;touch-action:none}"""
    rep(old_world_css, new_world_css, "Clean #world CSS (remove #world.rotated)")

    # -------------------------------------------------------------
    # 3. Add Mobile Responsive Styles & Focus Mode CSS
    # -------------------------------------------------------------
    old_media = """@media(prefers-reduced-motion:reduce){.poem-line span{animation-duration:.2s;transform:none!important;filter:none!important}.sound-on .sound-icon i{animation:none}}"""
    new_media = """@media(prefers-reduced-motion:reduce){.poem-line span{animation-duration:.2s;transform:none!important;filter:none!important}.sound-on .sound-icon i{animation:none}}

/* --- Responsive Native Mobile Portrait & Tablet Layout --- */
@media (max-aspect-ratio: 1/1) {
  .intro-inner {
    left: 8% !important;
    right: 8% !important;
    top: 50% !important;
    transform: translateY(-50%) !important;
    display: flex;
    flex-direction: column;
    align-items: center;
    text-align: center;
  }
  .intro-kicker { justify-content: center; }
  .destinations { justify-content: center; gap: 6px; }
  h1 { font-size: clamp(40px, 11vw, 68px) !important; margin: 10px 0 2px !important; }
  .english-title { font-size: 11px !important; margin: 6px 0 14px !important; }
  .intro-poem { font-size: 13px !important; margin-bottom: 20px !important; line-height: 1.8; }
  #begin { margin: 0 auto; min-width: 200px; }
  #journey { width: 190px; }
  #camera-hud { top: calc(var(--pad) + 8px); left: var(--pad); }
}

@media (max-width: 900px) and (pointer: coarse) {
  #controls {
    display: none !important; /* Hide desktop toolbar on touch screens to eliminate collision */
  }
}

/* --- Focus Expedition Ambient HUD & Modals --- */
.sf-focus-ticker {
  position: fixed;
  top: 16px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 150;
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 20px;
  border-radius: 30px;
  background: rgba(11, 17, 24, 0.88);
  border: 1px solid rgba(255, 215, 0, 0.5);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.5), 0 0 16px rgba(255, 215, 0, 0.2);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  cursor: pointer;
  color: #fff3a8;
  font-family: "SFMono-Regular", Consolas, monospace;
  font-size: 12px;
  letter-spacing: 0.08em;
  user-select: none;
  -webkit-user-select: none;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}
.sf-focus-ticker:active {
  transform: translateX(-50%) scale(0.96);
}
.sf-focus-pulse-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #ffd700;
  box-shadow: 0 0 10px #ffd700;
  animation: focusPulse 1.8s infinite ease-in-out;
}
@keyframes focusPulse {
  0%, 100% { transform: scale(0.85); opacity: 0.6; }
  50% { transform: scale(1.25); opacity: 1.0; }
}

/* Focus Modal Overlay & Cards */
.sf-focus-modal-overlay {
  position: fixed;
  inset: 0;
  z-index: 400;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(4, 8, 14, 0.82);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  opacity: 1;
  transition: opacity 0.3s ease;
}
.sf-focus-modal-overlay.closing {
  opacity: 0;
}
.sf-focus-modal-box {
  width: min(540px, 92vw);
  max-height: 90vh;
  overflow-y: auto;
  border-radius: 20px;
  background: rgba(14, 22, 32, 0.95);
  border: 1px solid rgba(230, 237, 242, 0.22);
  box-shadow: 0 12px 48px rgba(0, 0, 0, 0.6), inset 0 0 24px rgba(255, 215, 0, 0.05);
  padding: 30px 26px;
  color: #e6edf2;
  font-family: inherit;
  display: flex;
  flex-direction: column;
  gap: 18px;
  box-sizing: border-box;
}
.sf-focus-badge {
  display: inline-flex;
  align-self: flex-start;
  padding: 4px 12px;
  border-radius: 12px;
  background: rgba(255, 215, 0, 0.15);
  border: 1px solid rgba(255, 215, 0, 0.5);
  color: #fff3a8;
  font-size: 11px;
  font-family: "SFMono-Regular", Consolas, monospace;
  letter-spacing: 0.1em;
}
.sf-focus-badge.fail {
  background: rgba(255, 68, 68, 0.15);
  border-color: rgba(255, 68, 68, 0.5);
  color: #ff8888;
}
.sf-focus-modal-box h2 {
  margin: 0;
  font-size: 22px;
  font-weight: 400;
  letter-spacing: 0.08em;
}
.sf-focus-summary {
  font-size: 14px;
  line-height: 1.7;
  opacity: 0.85;
  margin: 0;
}
.sf-focus-presets {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(110px, 1fr));
  gap: 10px;
  margin: 6px 0;
}
.sf-focus-preset-card {
  padding: 12px 8px;
  border-radius: 12px;
  background: rgba(230, 237, 242, 0.04);
  border: 1px solid rgba(230, 237, 242, 0.14);
  text-align: center;
  cursor: pointer;
  transition: all 0.2s ease;
  user-select: none;
}
.sf-focus-preset-card:hover, .sf-focus-preset-card.active {
  background: rgba(255, 215, 0, 0.12);
  border-color: rgba(255, 215, 0, 0.65);
  transform: translateY(-2px);
  box-shadow: 0 4px 14px rgba(255, 215, 0, 0.2);
}
.sf-focus-preset-card b {
  display: block;
  font-size: 18px;
  font-family: "SFMono-Regular", Consolas, monospace;
  color: #fff3a8;
}
.sf-focus-preset-card span {
  font-size: 11px;
  opacity: 0.72;
}
.sf-focus-stats-row {
  display: flex;
  justify-content: space-around;
  padding: 12px 8px;
  border-radius: 12px;
  background: rgba(0, 0, 0, 0.3);
  border: 1px solid rgba(230, 237, 242, 0.08);
  font-family: "SFMono-Regular", Consolas, monospace;
  font-size: 11px;
  text-align: center;
}
.sf-focus-stats-row div span { display: block; opacity: 0.55; font-size: 10px; margin-bottom: 2px; }
.sf-focus-stats-row div b { font-size: 14px; color: #aed4ff; }
.sf-focus-rewards {
  padding: 12px 14px;
  border-radius: 12px;
  background: rgba(255, 215, 0, 0.08);
  border: 1px solid rgba(255, 215, 0, 0.35);
  font-size: 12px;
}
.sf-focus-rewards-title {
  font-weight: 500;
  color: #fff3a8;
  margin-bottom: 6px;
  font-family: "SFMono-Regular", Consolas, monospace;
}
.sf-reward-item {
  color: #e6edf2;
  margin: 3px 0;
}
.sf-focus-quote {
  font-size: 12px;
  font-style: italic;
  opacity: 0.6;
  text-align: center;
  margin-top: 4px;
}
.sf-focus-btn {
  padding: 13px 20px;
  border-radius: 30px;
  border: 0;
  font-size: 14px;
  letter-spacing: 0.08em;
  cursor: pointer;
  transition: transform 0.2s ease, opacity 0.2s ease;
  font-weight: 500;
}
.sf-focus-btn:hover { transform: scale(1.02); }
.sf-focus-btn:active { transform: scale(0.97); }
.sf-focus-btn.primary {
  background: linear-gradient(135deg, #ffd700 0%, #ffae00 100%);
  color: #0b1118;
  box-shadow: 0 4px 18px rgba(255, 215, 0, 0.35);
}
.sf-focus-btn.restart {
  background: rgba(230, 237, 242, 0.12);
  border: 1px solid rgba(230, 237, 242, 0.3);
  color: #e6edf2;
}
.sf-focus-btn.cancel {
  background: transparent;
  color: #a0aec0;
}"""
    rep(old_media, new_media, "Mobile Responsive & Focus Mode CSS")

    # -------------------------------------------------------------
    # 4. Expose window.toast
    # -------------------------------------------------------------
    old_toast = """function toast(text,duration=4){$('toast').textContent=text;toastUntil=time+duration;$('toast').style.opacity=1;}"""
    new_toast = """function toast(text,duration=4){$('toast').textContent=text;toastUntil=time+duration;$('toast').style.opacity=1;}
window.toast = toast;"""
    rep(old_toast, new_toast, "Expose window.toast")

    # -------------------------------------------------------------
    # 5. Update Camera Centering for Native Portrait
    # -------------------------------------------------------------
    old_cam = """ // 9. Cinematic IMAX Centering: smoothly shifts from cruise offset (0.385, 0.465) to majestic center (0.485, 0.495)
 const centerWeight = Math.max(captureCamPose ? captureCamPose.blend : 0, curSkimW, hm ? horizonW : 0);
 camera.cx = W * mix(0.385, 0.485, centerWeight);
 camera.cy = H * mix(0.465, 0.495, centerWeight);

 const effWarpF = Math.max(warp, WarpDrive.currentWarp);
 const warpFactor = clamp(effWarpF / 28, 0, 1.2);
 const fovWarp = 1 / (1 + warpFactor * 0.35 - WarpDrive.reverseR * 0.22);
 camera.focal = H * 1.12 * fovWarp * (captureCamPose ? mix(1, captureCamPose.focal, captureCamPose.blend) : 1);"""

    new_cam = """ // 9. Cinematic IMAX Centering: smoothly shifts from cruise offset (0.385, 0.465) to majestic center (0.485, 0.495)
 const centerWeight = Math.max(captureCamPose ? captureCamPose.blend : 0, curSkimW, hm ? horizonW : 0);
 const isPortrait = H > W;
 camera.cx = W * (isPortrait ? 0.50 : mix(0.385, 0.485, centerWeight));
 camera.cy = H * (isPortrait ? 0.48 : mix(0.465, 0.495, centerWeight));

 const effWarpF = Math.max(warp, WarpDrive.currentWarp);
 const warpFactor = clamp(effWarpF / 28, 0, 1.2);
 const fovWarp = 1 / (1 + warpFactor * 0.35 - WarpDrive.reverseR * 0.22);
 camera.focal = (isPortrait ? Math.min(W, H) * 1.25 : H * 1.12) * fovWarp * (captureCamPose ? mix(1, captureCamPose.focal, captureCamPose.blend) : 1);"""
    rep(old_cam, new_cam, "Camera Centering for Native Portrait")

    # -------------------------------------------------------------
    # 6. Fix logicalPoint() and resize()
    # -------------------------------------------------------------
    old_logical = """function logicalPoint(e){return rotated?{x:e.clientY,y:innerWidth-e.clientX}:{x:e.clientX,y:e.clientY};}"""
    new_logical = """function logicalPoint(e){return {x:e.clientX,y:e.clientY};}"""
    rep(old_logical, new_logical, "logicalPoint direct screen coordinates")

    old_resize = """function resize(){
 rotated=matchMedia('(pointer:coarse)').matches&&innerHeight>innerWidth;W=rotated?innerHeight:innerWidth;H=rotated?innerWidth:innerHeight;DPR=Math.min(devicePixelRatio||1,2);
 root.classList.toggle('rotated',rotated);root.classList.toggle('compact',H<580);root.style.width=W+'px';root.style.height=H+'px';root.style.setProperty('--unit',W>=3200?'2':W>=2200?'1.5':'1');"""

    new_resize = """function resize(){
 rotated=false;W=innerWidth;H=innerHeight;DPR=Math.min(devicePixelRatio||1,2);
 root.classList.remove('rotated');root.classList.toggle('compact',H<580);root.style.width=W+'px';root.style.height=H+'px';root.style.setProperty('--unit',W>=3200?'2':W>=2200?'1.5':'1');"""
    rep(old_resize, new_resize, "resize() native viewport without rotation hack")

    # -------------------------------------------------------------
    # 7. Add 'O' key for Focus Mode in keydown
    # -------------------------------------------------------------
    old_key = """ else if(e.key.toLowerCase()==='p')PhotoStudio.toggle();"""
    new_key = """ else if(e.key.toLowerCase()==='o'){if(window.StarfieldFocusEngine)window.StarfieldFocusEngine.toggleDashboard();}
 else if(e.key.toLowerCase()==='p')PhotoStudio.toggle();"""
    rep(old_key, new_key, "Key 'o' for Focus Engine toggle")

    # -------------------------------------------------------------
    # 8. Update isModalOpen() and window.Starfield additions
    # -------------------------------------------------------------
    old_modal = """ isModalOpen:()=>{
  return PhotoStudio.active||$('codex-modal').classList.contains('open')||$('settings-drawer').classList.contains('open');
 },"""

    new_modal = """ isModalOpen:()=>{
  const focusOpen = (window.StarfieldFocusEngine && window.StarfieldFocusEngine.isDashboardOpen);
  return PhotoStudio.active||$('codex-modal').classList.contains('open')||$('settings-drawer').classList.contains('open')||focusOpen;
 },"""
    rep(old_modal, new_modal, "isModalOpen() with Focus Dashboard")

    old_sf_methods = """ getGateT:()=>gateT,
 getCapturePhase:()=>capturePhase,"""
    new_sf_methods = """ getGateT:()=>gateT,
 getCapturePhase:()=>capturePhase,
 setCapturePhase:(p)=>{capturePhase=p;},
 triggerCrash:()=>{if(typeof WarpDrive!=='undefined'){WarpDrive.shake=6;WarpDrive.brakeKick=200;WarpDrive.currentWarp=0;}capturePhase=2;},"""
    rep(old_sf_methods, new_sf_methods, "Expose triggerCrash and setCapturePhase on window.Starfield")

    # -------------------------------------------------------------
    # 9. Refactor GamepadTouchControls (Clean UI, Focus Button & Lifecycle)
    # -------------------------------------------------------------
    old_touch_create = """    // Row 1: Auxiliary Functions (Cam, Codex, Photo, Settings)
    const rowAux = document.createElement('div');
    rowAux.className = 'sf-touch-btn-row';

    // Cam
    const btnCam = createTouchButton('👁️', '镜头', () => Engine.toggleCamera());
    // Codex
    const btnCodex = createTouchButton('📖', '图鉴', () => Engine.toggleCodex());
    // Photo
    const btnPhoto = createTouchButton('🌌', '摄影', () => Engine.togglePhoto());
    // Settings
    const btnSettings = createTouchButton('⚙️', '设置', () => Engine.toggleSettings());

    rowAux.appendChild(btnCam);
    rowAux.appendChild(btnCodex);
    rowAux.appendChild(btnPhoto);
    rowAux.appendChild(btnSettings);

    // Row 2: Flight Primary Actions (Warp Gear, Slingshot Boost)
    const rowFlight = document.createElement('div');
    rowFlight.className = 'sf-touch-btn-row';

    const btnCockpit = createTouchButton('🪟', '舱内', () => Engine.toggleCockpit());
    const btnFormation = createTouchButton('📐', '编队', () => Engine.cycleFormation());
    const btnWarp = createTouchButton('⚡', '曲速', () => Engine.throttleUp());
    
    // Slingshot Boost primary button
    const btnBoost = document.createElement('button');
    btnBoost.className = 'sf-touch-btn boost';
    btnBoost.innerHTML = `<span style="font-size:22px;line-height:1;">🚀</span><span class="label">BOOST</span>`;
    btnBoost.title = '脉冲加速 / 弹射爆冲';

    const onBoostPress = (e) => {
      e.preventDefault();
      btnBoost.classList.add('active');
      triggerHaptic(30);
      Engine.slingshotBoost();
      Engine.setWarpHold(true);
    };
    const onBoostRelease = (e) => {
      e.preventDefault();
      btnBoost.classList.remove('active');
      Engine.setWarpHold(false);
    };
    btnBoost.addEventListener('pointerdown', onBoostPress);
    btnBoost.addEventListener('pointerup', onBoostRelease);
    btnBoost.addEventListener('pointercancel', onBoostRelease);

    rowFlight.appendChild(btnCockpit);
    rowFlight.appendChild(btnFormation);
    rowFlight.appendChild(btnWarp);
    rowFlight.appendChild(btnBoost);

    actionCluster.appendChild(rowAux);
    actionCluster.appendChild(rowFlight);
    overlay.appendChild(actionCluster);"""

    new_touch_create = """    // Row 1: Auxiliary Functions (Focus, Cam, Cockpit, Formation)
    const rowAux = document.createElement('div');
    rowAux.className = 'sf-touch-btn-row';

    const btnFocus = createTouchButton('⏱️', '专注', () => {
      if (window.StarfieldFocusEngine) window.StarfieldFocusEngine.toggleDashboard();
    });
    const btnCam = createTouchButton('👁️', '镜头', () => Engine.toggleCamera());
    const btnCockpit = createTouchButton('🪟', '舱内', () => Engine.toggleCockpit());
    const btnFormation = createTouchButton('📐', '编队', () => Engine.cycleFormation());

    rowAux.appendChild(btnFocus);
    rowAux.appendChild(btnCam);
    rowAux.appendChild(btnCockpit);
    rowAux.appendChild(btnFormation);

    // Row 2: Flight Primary Actions (Codex, Settings, Warp Gear, Slingshot Boost)
    const rowFlight = document.createElement('div');
    rowFlight.className = 'sf-touch-btn-row';

    const btnCodex = createTouchButton('📖', '图鉴', () => Engine.toggleCodex());
    const btnSettings = createTouchButton('⚙️', '设置', () => Engine.toggleSettings());
    const btnWarp = createTouchButton('⚡', '曲速', () => Engine.throttleUp());
    
    // Slingshot Boost primary button
    const btnBoost = document.createElement('button');
    btnBoost.className = 'sf-touch-btn boost';
    btnBoost.innerHTML = `<span style="font-size:22px;line-height:1;">🚀</span><span class="label">BOOST</span>`;
    btnBoost.title = '脉冲加速 / 弹射爆冲';

    const onBoostPress = (e) => {
      e.preventDefault();
      btnBoost.classList.add('active');
      triggerHaptic(30);
      Engine.slingshotBoost();
      Engine.setWarpHold(true);
    };
    const onBoostRelease = (e) => {
      e.preventDefault();
      btnBoost.classList.remove('active');
      Engine.setWarpHold(false);
    };
    btnBoost.addEventListener('pointerdown', onBoostPress);
    btnBoost.addEventListener('pointerup', onBoostRelease);
    btnBoost.addEventListener('pointercancel', onBoostRelease);

    rowFlight.appendChild(btnCodex);
    rowFlight.appendChild(btnSettings);
    rowFlight.appendChild(btnWarp);
    rowFlight.appendChild(btnBoost);

    actionCluster.appendChild(rowAux);
    actionCluster.appendChild(rowFlight);
    overlay.appendChild(actionCluster);"""
    rep(old_touch_create, new_touch_create, "GamepadTouchControls ergonomic action cluster with Focus button")

    # In createTouchHUD, set overlay initially hidden:
    old_init_hud = """    const overlay = document.createElement('div');
    overlay.id = 'starfield-touch-overlay';"""

    new_init_hud = """    const overlay = document.createElement('div');
    overlay.id = 'starfield-touch-overlay';
    overlay.style.display = 'none'; // Initially hidden before flight begins"""
    rep(old_init_hud, new_init_hud, "createTouchHUD initially hidden")

    # In pollGamepad, manage touch HUD visibility lifecycle:
    old_poll_loop = """    // Pick first connected gamepad
    for (let i = 0; i < gamepads.length; i++) {
      if (gamepads[i] && gamepads[i].connected) {
        pad = gamepads[i];
        activeGamepadIndex = i;
        break;
      }
    }

    if (pad) {"""

    new_poll_loop = """    // Pick first connected gamepad
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
    }

    if (pad) {"""
    rep(old_poll_loop, new_poll_loop, "pollGamepad touch HUD lifecycle management")

    # -------------------------------------------------------------
    # 10. Inline StarfieldFocusEngine Module at end of scripts
    # -------------------------------------------------------------
    focus_engine_code = """
<!-- STARFIELD FOCUS EXPEDITION MODULE INLINED -->
<script>
(function(global) {
  'use strict';

  const STORAGE_KEY = 'starfield_focus_v1';

  const FOCUS_PRESETS = [
    { id: 'trial', name: '深空试航', durationMinutes: 15, tag: '短时专注', desc: '15分钟高效短冲，适合晨间规划与阅读整理。' },
    { id: 'pomodoro', name: '经典番茄钟', durationMinutes: 25, tag: '标准冲刺', desc: '25分钟经典心流，让深空星光陪伴高度专注。' },
    { id: 'cruise', name: '深空巡航', durationMinutes: 30, tag: '深度自习', desc: '30分钟持续巡航，完成解锁【专注曜金·泰坦折纸舰】。' },
    { id: 'voyage', name: '跨星系远征', durationMinutes: 60, tag: '终极挑战', desc: '60分钟高难远征，完成解锁【黄金纪元光流】与先行者密文。' }
  ];

  function showToast(text, duration = 4) {
    if (typeof window.toast === 'function') {
      window.toast(text, duration);
    } else {
      const el = document.getElementById('toast');
      if (el) {
        el.textContent = text;
        el.style.opacity = '1';
        setTimeout(() => { if (el) el.style.opacity = '0'; }, duration * 1000);
      }
    }
  }

  class StarfieldFocusEngine {
    constructor() {
      this.state = 'IDLE'; // 'IDLE', 'RUNNING', 'WARNING', 'SUCCESS', 'FAILED'
      this.targetDurationSec = 30 * 60;
      this.elapsedSec = 0;
      this.startTravel = 0;
      this.timerId = null;
      this.warningTimerId = null;
      this.warningRemainingSec = 10;
      this.wakeLock = null;
      this.selectedPresetIndex = 2; // Default 30min
      this.isDashboardOpen = false;

      this.stats = this.loadStats();
      this.setupVisibilityListeners();
    }

    loadStats() {
      try {
        const raw = localStorage.getItem(STORAGE_KEY);
        if (raw) return JSON.parse(raw);
      } catch (_) {}
      return {
        totalFocusMinutes: 0,
        completedVoyages: 0,
        failedVoyages: 0,
        currentStreak: 0,
        bestStreak: 0,
        unlockedRewards: {
          hull_titan: false,
          trail_golden: false,
          relic_focus: false
        },
        history: []
      };
    }

    saveStats() {
      try {
        localStorage.setItem(STORAGE_KEY, JSON.stringify(this.stats));
      } catch (_) {}
    }

    setupVisibilityListeners() {
      if (typeof document === 'undefined') return;

      document.addEventListener('visibilitychange', () => {
        if (this.state !== 'RUNNING' && this.state !== 'WARNING') return;

        if (document.hidden) {
          this.triggerWarning();
        } else {
          this.clearWarning();
        }
      });

      window.addEventListener('blur', () => {
        if (this.state === 'RUNNING') {
          this.triggerWarning();
        }
      });

      window.addEventListener('focus', () => {
        if (this.state === 'WARNING') {
          this.clearWarning();
        }
      });
    }

    async requestWakeLock() {
      try {
        if ('wakeLock' in navigator && !this.wakeLock) {
          this.wakeLock = await navigator.wakeLock.request('screen');
        }
      } catch (_) {}
    }

    releaseWakeLock() {
      if (this.wakeLock) {
        try { this.wakeLock.release(); } catch (_) {}
        this.wakeLock = null;
      }
    }

    toggleDashboard() {
      if (this.state === 'RUNNING') {
        this.showActiveStatusDialog();
      } else {
        if (this.isDashboardOpen) this.closeDashboard();
        else this.openDashboard();
      }
    }

    openDashboard() {
      this.isDashboardOpen = true;
      const existing = document.getElementById('sf-focus-dashboard-modal');
      if (existing) existing.remove();

      const modal = document.createElement('div');
      modal.id = 'sf-focus-dashboard-modal';
      modal.className = 'sf-focus-modal-overlay';

      const content = document.createElement('div');
      content.className = 'sf-focus-modal-box';

      content.innerHTML = `
        <div class="sf-focus-badge">⏱️ STARFIELD FOCUS EXPEDITION</div>
        <h2>深空专注远征 · 番茄钟心流</h2>
        <p class="sf-focus-summary">
          把手机作为深空挂机摆件。星舰在浩瀚宇宙中默默前行，伴你进入深度心流。<br>
          <strong style="color:#ffae00;">⚠️ 严禁中途切换应用或离开星舰</strong>，否则燃料耗尽星舰将坠毁或被黑洞视界吞噬！
        </p>

        <div class="sf-focus-presets">
          ${FOCUS_PRESETS.map((p, idx) => `
            <div class="sf-focus-preset-card ${idx === this.selectedPresetIndex ? 'active' : ''}" data-idx="${idx}">
              <b>${p.durationMinutes}m</b>
              <span>${p.name}</span>
            </div>
          `).join('')}
        </div>

        <div class="sf-focus-stats-row">
          <div><span>累积专注</span><b>${this.stats.totalFocusMinutes} 分钟</b></div>
          <div><span>成功远征</span><b>${this.stats.completedVoyages} 次</b></div>
          <div><span>连续远征</span><b>${this.stats.currentStreak} 次</b></div>
        </div>

        <div class="sf-focus-rewards">
          <div class="sf-focus-rewards-title">✦ 远征达成解锁专属探索勋礼 ✦</div>
          <div class="sf-reward-item">🚀 30分钟达成：解锁【专属曜金·泰坦折纸旗舰】</div>
          <div class="sf-reward-item">✨ 60分钟达成：解锁【黄金纪元引力波流光】与先行者密文</div>
        </div>

        <button class="sf-focus-btn primary" id="sf-focus-start-btn">✦ 启动深空专注探索 ✦</button>
        <button class="sf-focus-btn cancel" id="sf-focus-cancel-btn">返回漫游</button>
      `;

      modal.appendChild(content);
      document.body.appendChild(modal);

      content.querySelectorAll('.sf-focus-preset-card').forEach(card => {
        card.addEventListener('click', () => {
          content.querySelectorAll('.sf-focus-preset-card').forEach(c => c.classList.remove('active'));
          card.classList.add('active');
          this.selectedPresetIndex = parseInt(card.getAttribute('data-idx'), 10);
        });
      });

      document.getElementById('sf-focus-start-btn').addEventListener('click', () => {
        const preset = FOCUS_PRESETS[this.selectedPresetIndex] || FOCUS_PRESETS[2];
        this.closeDashboard();
        this.startMission(preset.durationMinutes);
      });

      document.getElementById('sf-focus-cancel-btn').addEventListener('click', () => {
        this.closeDashboard();
      });
    }

    closeDashboard() {
      this.isDashboardOpen = false;
      const modal = document.getElementById('sf-focus-dashboard-modal');
      if (modal) {
        modal.classList.add('closing');
        setTimeout(() => modal.remove(), 250);
      }
    }

    startMission(durationMinutes = 30) {
      this.targetDurationSec = Math.max(60, durationMinutes * 60);
      this.elapsedSec = 0;
      this.state = 'RUNNING';

      const SF = window.Starfield;
      this.startTravel = (SF && SF.getTravel) ? SF.getTravel() : 0;

      // Start flight if not yet started
      const isStarted = SF && SF.getState ? SF.getState().started : (document.getElementById('world')?.classList.contains('flying') || false);
      if (!isStarted) {
        const btn = document.getElementById('begin');
        if (btn) btn.click();
      }

      // Enter autonomous camera & enable classical soundtrack
      const isAuto = SF && SF.isAutoCamera ? SF.isAutoCamera() : true;
      if (!isAuto && SF && SF.toggleCamera) {
        SF.toggleCamera();
      }
      const sound = window.sound || (SF && SF.getSoundscape ? SF.getSoundscape() : null);
      if (sound && !sound.ready) {
        const soundBtn = document.getElementById('sound-toggle');
        if (soundBtn) soundBtn.click();
      }

      this.requestWakeLock();
      this.updateTickerHUD(true);

      if (this.timerId) clearInterval(this.timerId);
      this.timerId = setInterval(() => this.tick(), 1000);

      showToast(`✦ 专注深空远征启航 · 目标 ${durationMinutes} 分钟 · 勿切后台 ✦`, 6);
    }

    tick() {
      if (this.state !== 'RUNNING') return;

      this.elapsedSec++;
      this.updateTickerHUD(true);

      // Check for mission completion
      if (this.elapsedSec >= this.targetDurationSec) {
        this.completeMission();
      }
    }

    triggerWarning() {
      if (this.state !== 'RUNNING') return;
      this.state = 'WARNING';
      this.warningRemainingSec = 10;

      showToast('⚠️ 警告：检测到离开星舰！引力约束将在 10 秒后瓦解！请立即返回！', 5);

      if (this.warningTimerId) clearInterval(this.warningTimerId);
      this.warningTimerId = setInterval(() => {
        this.warningRemainingSec--;
        if (this.warningRemainingSec <= 0) {
          clearInterval(this.warningTimerId);
          this.warningTimerId = null;
          this.failMission();
        } else {
          showToast(`⚠️ 偏离航道！剩余 ${this.warningRemainingSec} 秒坠毁！立即返回！`, 1.5);
        }
      }, 1000);
    }

    clearWarning() {
      if (this.state !== 'WARNING') return;
      if (this.warningTimerId) {
        clearInterval(this.warningTimerId);
        this.warningTimerId = null;
      }
      this.state = 'RUNNING';
      showToast('✦ 引力约束已恢复重稳 · 继续专注深空巡航 ✦', 4);
    }

    completeMission() {
      if (this.timerId) { clearInterval(this.timerId); this.timerId = null; }
      this.state = 'SUCCESS';
      this.releaseWakeLock();
      this.updateTickerHUD(false);

      const focusedMinutes = Math.round(this.targetDurationSec / 60);
      this.stats.totalFocusMinutes += focusedMinutes;
      this.stats.completedVoyages++;
      this.stats.currentStreak++;
      if (this.stats.currentStreak > this.stats.bestStreak) {
        this.stats.bestStreak = this.stats.currentStreak;
      }

      const rewardsEarned = [];
      if (focusedMinutes >= 30 && !this.stats.unlockedRewards.hull_titan) {
        this.stats.unlockedRewards.hull_titan = true;
        rewardsEarned.push('专属旗舰：专注曜金·泰坦折纸舰');
      }
      if (focusedMinutes >= 60 && !this.stats.unlockedRewards.trail_golden) {
        this.stats.unlockedRewards.trail_golden = true;
        rewardsEarned.push('专属尾迹：黄金纪元引力波流光');
      }
      if (!this.stats.unlockedRewards.relic_focus) {
        this.stats.unlockedRewards.relic_focus = true;
        rewardsEarned.push('星图图鉴密文：先行者心流手札');
      }

      this.stats.history.unshift({
        date: new Date().toISOString(),
        minutes: focusedMinutes,
        status: 'SUCCESS'
      });
      if (this.stats.history.length > 50) this.stats.history.pop();
      this.saveStats();

      // Trigger 5D Tesseract celebration
      if (typeof window.triggerTesseract === 'function') {
        window.triggerTesseract();
      }
      showToast(`🏆 专注远征圆满达成！已累积专注 ${this.stats.totalFocusMinutes} 分钟！`, 8);

      this.showSummaryModal(true, focusedMinutes, rewardsEarned);
    }

    failMission() {
      if (this.timerId) { clearInterval(this.timerId); this.timerId = null; }
      if (this.warningTimerId) { clearInterval(this.warningTimerId); this.warningTimerId = null; }
      this.state = 'FAILED';
      this.releaseWakeLock();
      this.updateTickerHUD(false);

      const elapsedMin = Math.floor(this.elapsedSec / 60);
      this.stats.failedVoyages++;
      this.stats.currentStreak = 0;
      this.stats.history.unshift({
        date: new Date().toISOString(),
        minutes: elapsedMin,
        status: 'FAILED'
      });
      if (this.stats.history.length > 50) this.stats.history.pop();
      this.saveStats();

      // Trigger black hole / emergency crash sequence in engine
      const SF = window.Starfield;
      if (SF && SF.triggerCrash) {
        SF.triggerCrash();
      } else {
        if (typeof WarpDrive !== 'undefined') {
          WarpDrive.shake = 6.0;
          WarpDrive.brakeKick = 200;
          WarpDrive.currentWarp = 0;
        }
      }

      showToast('💥 航行失败 · 离开星舰导致燃料耗尽，已被深空黑洞奇点吞噬！', 8);

      this.showSummaryModal(false, elapsedMin, []);
    }

    updateTickerHUD(show = (this.state === 'RUNNING')) {
      let ticker = document.getElementById('sf-focus-ticker');
      if (!ticker) {
        ticker = document.createElement('div');
        ticker.id = 'sf-focus-ticker';
        ticker.className = 'sf-focus-ticker';
        ticker.addEventListener('click', () => this.showActiveStatusDialog());
        document.body.appendChild(ticker);
      }

      if (!show) {
        ticker.style.display = 'none';
        return;
      }

      ticker.style.display = 'flex';
      const rem = Math.max(0, this.targetDurationSec - this.elapsedSec);
      const m = Math.floor(rem / 60);
      const s = Math.floor(rem % 60);
      const timeStr = `${m < 10 ? '0' : ''}${m}:${s < 10 ? '0' : ''}${s}`;
      ticker.innerHTML = `
        <div class="sf-focus-pulse-dot"></div>
        <span>✦ 专注探索中 · 剩余 ${timeStr} · 勿切后台 ✦</span>
      `;
    }

    showActiveStatusDialog() {
      const rem = Math.max(0, this.targetDurationSec - this.elapsedSec);
      const m = Math.floor(rem / 60);
      const s = Math.floor(rem % 60);
      const timeStr = `${m < 10 ? '0' : ''}${m}:${s < 10 ? '0' : ''}${s}`;
      const SF = window.Starfield;
      const travelVal = SF && SF.getTravel ? SF.getTravel() : 0;
      const distance = (travelVal * 0.001).toFixed(1);

      const existing = document.getElementById('sf-focus-active-modal');
      if (existing) existing.remove();

      const modal = document.createElement('div');
      modal.id = 'sf-focus-active-modal';
      modal.className = 'sf-focus-modal-overlay';

      const content = document.createElement('div');
      content.className = 'sf-focus-modal-box';

      content.innerHTML = `
        <div class="sf-focus-badge">✦ VOYAGE IN PROGRESS</div>
        <h2>深空专注探索状态</h2>
        <div class="sf-focus-stats-row">
          <div><span>剩余时间</span><b style="font-size:20px;color:#fff3a8;">${timeStr}</b></div>
          <div><span>当前里程</span><b>${distance} KLY</b></div>
          <div><span>目标时长</span><b>${Math.round(this.targetDurationSec / 60)} 分钟</b></div>
        </div>
        <p class="sf-focus-summary" style="text-align:center;">
          正在自主巡航中，请将手机放置在桌面上享受星光与古典乐心流。<br>
          <span style="opacity:0.6;font-size:12px;">（屏幕常亮保护已开启，切后台或退出将导致坠机）</span>
        </p>
        <button class="sf-focus-btn primary" id="sf-focus-resume-btn">继续专注心流</button>
        <button class="sf-focus-btn restart" id="sf-focus-abort-btn" style="border-color:#ff6666;color:#ff8888;">放弃本次远征 (将坠毁)</button>
      `;

      modal.appendChild(content);
      document.body.appendChild(modal);

      document.getElementById('sf-focus-resume-btn').addEventListener('click', () => {
        modal.classList.add('closing');
        setTimeout(() => modal.remove(), 250);
      });

      document.getElementById('sf-focus-abort-btn').addEventListener('click', () => {
        modal.remove();
        this.failMission();
      });
    }

    showSummaryModal(success, minutes, rewards) {
      const existing = document.getElementById('starfield-focus-modal');
      if (existing) existing.remove();

      const modal = document.createElement('div');
      modal.id = 'starfield-focus-modal';
      modal.className = 'sf-focus-modal-overlay';

      const content = document.createElement('div');
      content.className = `sf-focus-modal-box ${success ? 'success' : 'failed'}`;

      if (success) {
        content.innerHTML = `
          <div class="sf-focus-badge">🏆 MISSION ACCOMPLISHED</div>
          <h2>深空远征 · 圆满抵达</h2>
          <p class="sf-focus-summary">
            你保持专注不触碰手机，成功完成了 <strong>${minutes} 分钟</strong> 的全景深空漫游探索！
          </p>
          <div class="sf-focus-stats-row">
            <div><span>累积专注</span><b>${this.stats.totalFocusMinutes} 分钟</b></div>
            <div><span>远征航次</span><b>${this.stats.completedVoyages} 次</b></div>
            <div><span>当前连胜</span><b>${this.stats.currentStreak} 次</b></div>
          </div>
          ${rewards.length > 0 ? `
            <div class="sf-focus-rewards">
              <div class="sf-focus-rewards-title">✦ 解锁专属专注探索勋礼 ✦</div>
              ${rewards.map(r => `<div class="sf-reward-item">✨ ${r}</div>`).join('')}
            </div>
          ` : ''}
          <div class="sf-focus-quote">“把方向交给星光，把时间留给当下。”</div>
          <button class="sf-focus-btn primary" id="sf-focus-confirm-btn">继续深空漫游</button>
        `;
      } else {
        content.innerHTML = `
          <div class="sf-focus-badge fail">💥 MISSION FAILED</div>
          <h2>引力坍缩 · 坠毁于视界</h2>
          <p class="sf-focus-summary">
            在专注进行至 <strong>${minutes} 分钟</strong> 时脱离星舰，折叠力场失谐，星舰燃料耗尽坠入黑洞奇点。
          </p>
          <div class="sf-focus-stats-row">
            <div><span>累积专注</span><b>${this.stats.totalFocusMinutes} 分钟</b></div>
            <div><span>失败航次</span><b>${this.stats.failedVoyages} 次</b></div>
            <div><span>连胜纪录</span><b>${this.stats.bestStreak} 次</b></div>
          </div>
          <div class="sf-focus-quote">“浩瀚星海从不苛责跌落者。重整引力帆，下一次我们将飞得更远。”</div>
          <button class="sf-focus-btn restart" id="sf-focus-confirm-btn">重整星舰 · 再次起航</button>
        `;
      }

      modal.appendChild(content);
      document.body.appendChild(modal);

      document.getElementById('sf-focus-confirm-btn').addEventListener('click', () => {
        modal.classList.add('closing');
        setTimeout(() => modal.remove(), 250);
        this.state = 'IDLE';
      });
    }
  }

  global.StarfieldFocusEngine = new StarfieldFocusEngine();

  // Register PWA ServiceWorker
  if ('serviceWorker' in navigator && (location.protocol === 'https:' || location.hostname === 'localhost' || location.hostname === '127.0.0.1')) {
    window.addEventListener('load', () => {
      navigator.serviceWorker.register('./service-worker.js').catch(() => {});
    });
  }

})(typeof window !== 'undefined' ? window : globalThis);
</script>
"""

    old_end_script = "</body>"
    new_end_script = focus_engine_code + ("\n</body>" if not crlf else "\r\n</body>")
    rep(old_end_script, new_end_script, "Inline StarfieldFocusEngine and ServiceWorker registration")

    with open(target_path, "w", encoding="utf-8") as f:
        f.write(content)

    print("ALL FOCUS & MOBILE UI FIXES SUCCESSFULLY APPLIED TO starfield.html!")

if __name__ == "__main__":
    apply_focus_and_mobile_patch()
