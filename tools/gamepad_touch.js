/**
 * ============================================================================
 * STARFIELD // HTML5 GAMEPAD & MOBILE TOUCH CONTROLS ENGINE
 * File: tools/gamepad_touch.js
 * 
 * Provides console-grade Gamepad (Xbox / PlayStation / Generic) support
 * and responsive Mobile/Tablet Virtual Touch Controls for Starfield.
 * 
 * Features:
 * - HTML5 Gamepad API polling loop with smooth stick interpolation & deadzone
 * - Dual-rumble haptic vibration feedback on slingshot surge, wormholes & black holes
 * - Dynamic floating virtual analog thumbstick with spring-damper return
 * - Bottom-right quick-touch action cluster (Boost, Cam, Codex, Photo, Settings, Warp)
 * - Two-finger pinch-to-zoom camera tracking
 * - Graceful fallback to DOM & KeyboardEvent dispatching
 * ============================================================================
 */

(function(window) {
  'use strict';

  // Prevent multiple initializations
  if (window.GamepadTouchControls && window.GamepadTouchControls.isInitialized()) {
    return;
  }

  // --- Constants & Config ---
  const DEADZONE_LEFT = 0.12;
  const DEADZONE_RIGHT = 0.12;
  const STICK_MAX_RADIUS = 54; // pixels for virtual joystick
  const CAMERA_YAW_SPEED = 1.6;
  const CAMERA_PITCH_SPEED = 1.2;

  // --- State Variables ---
  let isInitialized = false;
  let isTouchCapable = false;
  let touchHudVisible = false;
  let activeGamepadIndex = -1;
  let gamepadConnected = false;

  // Flight & Camera Steering State
  let steerX = 0.0;
  let steerY = 0.0;
  let targetSteerX = 0.0;
  let targetSteerY = 0.0;

  // Gamepad Previous Button States (for edge detection)
  let prevButtons = [];
  let prevAxes = [0, 0, 0, 0];

  // Game Vibration Tracking
  let prevSurge = false;
  let prevGateT = 0;
  let prevCapturePhase = 0;

  // Virtual Joystick DOM & Touch State
  let joyContainer = null;
  let joyBase = null;
  let joyKnob = null;
  let joyTouchId = null;
  let joyOrigin = { x: 0, y: 0 };
  let joyOffset = { x: 0, y: 0 };
  let joyActive = false;
  let joySpringAnimId = null;

  // Action Cluster DOM
  let actionCluster = null;
  let gamepadBadge = null;

  // Pinch-to-Zoom State
  let activeTouches = new Map();
  let initialPinchDist = 0;
  let lastPinchDist = 0;

  // Animation Loop
  let rafId = null;
  let lastFrameTime = performance.now();

  // --- Sound & Haptic Helpers ---
  function triggerHaptic(durationMs = 20) {
    try {
      if (typeof navigator !== 'undefined' && navigator.vibrate) {
        navigator.vibrate(durationMs);
      }
    } catch (_) {}
  }

  function playRumble(pad, { duration = 300, weakMagnitude = 0.6, strongMagnitude = 0.8, startDelay = 0 } = {}) {
    if (!pad) return;
    try {
      if (pad.vibrationActuator && typeof pad.vibrationActuator.playEffect === 'function') {
        pad.vibrationActuator.playEffect('dual-rumble', {
          startDelay,
          duration,
          weakMagnitude: Math.min(1, Math.max(0, weakMagnitude)),
          strongMagnitude: Math.min(1, Math.max(0, strongMagnitude))
        }).catch(() => {});
      } else if (pad.hapticActuators && pad.hapticActuators.length > 0) {
        pad.hapticActuators[0].pulse(strongMagnitude, duration).catch(() => {});
      }
    } catch (_) {}
  }

  // --- Game Dispatch Helper ---
  // Safely calls window.Starfield API or falls back to synthetic DOM / Keyboard events
  const Engine = {
    get sf() { return window.Starfield || null; },

    isFlightStarted() {
      if (this.sf && typeof this.sf.getState === 'function') {
        return !!this.sf.getState().started;
      }
      return document.getElementById('world')?.classList.contains('flying') || false;
    },

    beginFlight() {
      const beginBtn = document.getElementById('begin');
      if (beginBtn && beginBtn.offsetParent !== null) {
        beginBtn.click();
      }
    },

    applySteer(sx, sy) {
      if (this.sf && typeof this.sf.applySteer === 'function') {
        this.sf.applySteer(sx, sy);
      } else if (this.sf && typeof this.sf.feedWind === 'function') {
        const W = window.innerWidth, H = window.innerHeight;
        const tx = Math.max(0, Math.min(1, 0.42 + sx * 0.45));
        const ty = Math.max(0, Math.min(1, 0.50 + sy * 0.45));
        this.sf.feedWind({ x: tx * W, y: ty * H });
      } else {
        // PointerEvent Fallback
        const canvas = document.getElementById('landscape');
        if (canvas) {
          const clientX = (0.42 + sx * 0.45) * window.innerWidth;
          const clientY = (0.50 + sy * 0.45) * window.innerHeight;
          canvas.dispatchEvent(new PointerEvent('pointermove', {
            clientX, clientY, pointerType: 'mouse', bubbles: true
          }));
        }
      }
    },

    rotateCamera(dyaw, dpitch) {
      if (this.sf && typeof this.sf.rotateCamera === 'function') {
        this.sf.rotateCamera(dyaw, dpitch);
      } else {
        // Fallback: manually update camera or dispatch mouse drag
        const cam = this.sf && typeof this.sf.getCamera === 'function' ? this.sf.getCamera() : null;
        if (cam) {
          cam.yaw = (cam.yaw || 0) + dyaw;
          cam.pitch = Math.max(-0.16, Math.min(1.47, (cam.pitch || 0) + dpitch));
        }
      }
    },

    zoomCamera(factor) {
      if (this.sf && typeof this.sf.zoomCamera === 'function') {
        this.sf.zoomCamera(factor);
      } else {
        const canvas = document.getElementById('landscape');
        if (canvas) {
          const deltaY = (1 - factor) * 400;
          canvas.dispatchEvent(new WheelEvent('wheel', { deltaY, bubbles: true, cancelable: true }));
        }
      }
    },

    toggleCockpit() {
      if (this.sf && typeof this.sf.toggleCockpit === 'function') {
        this.sf.toggleCockpit();
      } else {
        window.dispatchEvent(new KeyboardEvent('keydown', { key: 'v', code: 'KeyV', bubbles: true }));
      }
    },

    toggleCamera() {
      if (this.sf && typeof this.sf.toggleCamera === 'function') {
        this.sf.toggleCamera();
      } else {
        const btn = document.getElementById('camera-toggle');
        if (btn) btn.click();
        else window.dispatchEvent(new KeyboardEvent('keydown', { key: 'c', code: 'KeyC', bubbles: true }));
      }
    },

    cycleFormation(dir = 1) {
      if (this.sf && typeof this.sf.cycleFormation === 'function') {
        this.sf.cycleFormation(dir);
      } else {
        const btn = document.getElementById('formation-toggle');
        if (btn) btn.click();
        else window.dispatchEvent(new KeyboardEvent('keydown', { key: 'f', code: 'KeyF', bubbles: true }));
      }
    },

    throttleUp() {
      if (this.sf && typeof this.sf.throttleUp === 'function') {
        this.sf.throttleUp();
      } else {
        const btn = document.getElementById('warp-toggle');
        if (btn) btn.click();
        else window.dispatchEvent(new KeyboardEvent('keydown', { key: 'g', code: 'KeyG', bubbles: true }));
      }
    },

    throttleDown() {
      if (this.sf && typeof this.sf.throttleDown === 'function') {
        this.sf.throttleDown();
      } else {
        // Fallback: cycle warp or brake
        window.dispatchEvent(new KeyboardEvent('keydown', { key: 'g', code: 'KeyG', bubbles: true }));
      }
    },

    slingshotBoost() {
      if (this.sf && typeof this.sf.slingshotBoost === 'function') {
        this.sf.slingshotBoost();
      } else {
        window.dispatchEvent(new KeyboardEvent('keydown', { key: 'Shift', code: 'ShiftLeft', bubbles: true }));
        setTimeout(() => {
          window.dispatchEvent(new KeyboardEvent('keyup', { key: 'Shift', code: 'ShiftLeft', bubbles: true }));
        }, 300);
      }
    },

    setWarpHold(hold) {
      if (this.sf && typeof this.sf.setWarpHold === 'function') {
        this.sf.setWarpHold(hold);
      } else {
        const type = hold ? 'keydown' : 'keyup';
        window.dispatchEvent(new KeyboardEvent(type, { key: 'Shift', code: 'ShiftLeft', bubbles: true }));
      }
    },

    closeModal() {
      if (this.sf && typeof this.sf.closeModal === 'function') {
        this.sf.closeModal();
      } else {
        window.dispatchEvent(new KeyboardEvent('keydown', { key: 'Escape', code: 'Escape', bubbles: true }));
      }
    },

    isModalOpen() {
      if (this.sf && typeof this.sf.isModalOpen === 'function') {
        return this.sf.isModalOpen();
      }
      return !!(
        document.querySelector('.photo-modal.open') ||
        document.getElementById('codex-modal')?.classList.contains('open') ||
        document.getElementById('settings-drawer')?.classList.contains('open')
      );
    },

    toggleCodex() {
      if (this.sf && typeof this.sf.toggleCodex === 'function') {
        this.sf.toggleCodex();
      } else {
        const btn = document.getElementById('codex-toggle');
        if (btn) btn.click();
        else window.dispatchEvent(new KeyboardEvent('keydown', { key: 'Tab', code: 'Tab', bubbles: true }));
      }
    },

    togglePhoto() {
      if (this.sf && typeof this.sf.togglePhoto === 'function') {
        this.sf.togglePhoto();
      } else {
        const btn = document.getElementById('photo-toggle');
        if (btn) btn.click();
        else window.dispatchEvent(new KeyboardEvent('keydown', { key: 'p', code: 'KeyP', bubbles: true }));
      }
    },

    toggleSettings() {
      if (this.sf && typeof this.sf.toggleSettings === 'function') {
        this.sf.toggleSettings();
      } else {
        const btn = document.getElementById('settings-toggle');
        if (btn) btn.click();
        else window.dispatchEvent(new KeyboardEvent('keydown', { key: 'Escape', code: 'Escape', bubbles: true }));
      }
    },

    isSlingshotSurge() {
      if (this.sf && typeof this.sf.isSlingshotSurge === 'function') {
        return this.sf.isSlingshotSurge();
      }
      return document.getElementById('slingshot-toast')?.classList.contains('show') || false;
    },

    getGateT() {
      if (this.sf && typeof this.sf.getGateT === 'function') {
        return this.sf.getGateT();
      }
      return 0;
    },

    getCapturePhase() {
      if (this.sf && typeof this.sf.getCapturePhase === 'function') {
        return this.sf.getCapturePhase();
      }
      return 0;
    }
  };

  // --- Inject CSS Stylesheet ---
  function injectStyles() {
    if (document.getElementById('starfield-gamepad-touch-styles')) return;

    const style = document.createElement('style');
    style.id = 'starfield-gamepad-touch-styles';
    style.textContent = `
      /* Touch Controls Overlay Layer */
      #starfield-touch-overlay {
        position: fixed;
        inset: 0;
        pointer-events: none;
        z-index: 120;
        user-select: none;
        -webkit-user-select: none;
        overflow: hidden;
      }

      /* Floating Virtual Joystick */
      .sf-touch-joy-zone {
        position: absolute;
        left: 0;
        bottom: 0;
        width: 45vw;
        height: 55vh;
        pointer-events: auto;
        touch-action: none;
      }

      .sf-touch-joy-base {
        position: absolute;
        width: 120px;
        height: 120px;
        border-radius: 50%;
        background: radial-gradient(circle, rgba(230, 237, 242, 0.05) 0%, rgba(11, 17, 24, 0.45) 80%);
        border: 1.5px solid rgba(230, 237, 242, 0.28);
        box-shadow: 0 4px 24px rgba(0, 0, 0, 0.3), inset 0 0 16px rgba(180, 215, 255, 0.08);
        backdrop-filter: blur(8px);
        -webkit-backdrop-filter: blur(8px);
        transform: translate(-50%, -50%);
        opacity: 0.35;
        transition: opacity 0.25s ease, border-color 0.25s ease;
        pointer-events: none;
        box-sizing: border-box;
      }

      .sf-touch-joy-base.active {
        opacity: 0.95;
        border-color: rgba(136, 192, 255, 0.7);
        box-shadow: 0 0 28px rgba(100, 180, 255, 0.35), inset 0 0 20px rgba(100, 180, 255, 0.15);
      }

      .sf-touch-joy-base:before {
        content: "";
        position: absolute;
        top: 50%;
        left: 50%;
        width: 6px;
        height: 6px;
        transform: translate(-50%, -50%);
        border-radius: 50%;
        background: rgba(230, 237, 242, 0.3);
      }

      .sf-touch-joy-knob {
        position: absolute;
        top: 50%;
        left: 50%;
        width: 52px;
        height: 52px;
        border-radius: 50%;
        background: radial-gradient(circle at 35% 35%, rgba(255, 255, 255, 0.9) 0%, rgba(180, 215, 255, 0.6) 60%, rgba(100, 160, 230, 0.4) 100%);
        border: 1.5px solid rgba(255, 255, 255, 0.85);
        box-shadow: 0 4px 14px rgba(0, 0, 0, 0.5), 0 0 16px rgba(136, 192, 255, 0.6);
        transform: translate(-50%, -50%);
        transition: transform 0.05s linear;
        pointer-events: none;
        box-sizing: border-box;
      }

      .sf-touch-joy-knob.spring-return {
        transition: transform 0.22s cubic-bezier(0.18, 0.89, 0.32, 1.28);
      }

      /* Virtual Action Button Cluster */
      .sf-touch-cluster {
        position: absolute;
        right: 20px;
        bottom: 24px;
        display: flex;
        flex-direction: column;
        align-items: flex-end;
        gap: 12px;
        pointer-events: auto;
        touch-action: none;
      }

      .sf-touch-btn-row {
        display: flex;
        align-items: center;
        gap: 10px;
      }

      .sf-touch-btn {
        width: 48px;
        height: 48px;
        border-radius: 50%;
        background: rgba(11, 17, 24, 0.65);
        border: 1px solid rgba(230, 237, 242, 0.3);
        color: #e6edf2;
        font-family: inherit;
        font-size: 16px;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.25);
        cursor: pointer;
        padding: 0;
        outline: none;
        transition: transform 0.12s ease, background 0.12s ease, border-color 0.12s ease;
        -webkit-tap-highlight-color: transparent;
      }

      .sf-touch-btn:active, .sf-touch-btn.active {
        transform: scale(0.92);
        background: rgba(100, 180, 255, 0.28);
        border-color: #88c0ff;
        box-shadow: 0 0 16px rgba(100, 180, 255, 0.5);
      }

      .sf-touch-btn span.label {
        font-size: 8px;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        opacity: 0.75;
        margin-top: 1px;
        font-family: "SFMono-Regular", Consolas, monospace;
      }

      /* Primary Slingshot Boost Button */
      .sf-touch-btn.boost {
        width: 62px;
        height: 62px;
        background: radial-gradient(circle, rgba(255, 215, 0, 0.2) 0%, rgba(11, 17, 24, 0.75) 100%);
        border: 1.5px solid rgba(255, 215, 0, 0.65);
        color: #fff3a8;
        box-shadow: 0 0 20px rgba(255, 215, 0, 0.35);
      }

      .sf-touch-btn.boost:active, .sf-touch-btn.boost.active {
        transform: scale(0.92);
        background: rgba(255, 215, 0, 0.4);
        box-shadow: 0 0 28px rgba(255, 215, 0, 0.7);
      }

      /* Gamepad HUD Status Badge */
      .sf-gamepad-badge {
        position: absolute;
        top: 24px;
        left: 50%;
        transform: translateX(-50%) translateY(-20px);
        padding: 6px 18px;
        border-radius: 20px;
        background: rgba(11, 17, 24, 0.75);
        border: 1px solid rgba(136, 192, 255, 0.45);
        color: #d6e8ff;
        font-family: "SFMono-Regular", Consolas, monospace;
        font-size: 11px;
        letter-spacing: 0.08em;
        backdrop-filter: blur(8px);
        -webkit-backdrop-filter: blur(8px);
        opacity: 0;
        pointer-events: none;
        transition: opacity 0.4s ease, transform 0.4s cubic-bezier(0.18, 0.89, 0.32, 1.28);
        z-index: 130;
        display: flex;
        align-items: center;
        gap: 8px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4);
      }

      .sf-gamepad-badge.show {
        opacity: 1;
        transform: translateX(-50%) translateY(0);
      }

      .sf-gamepad-badge .dot {
        width: 7px;
        height: 7px;
        border-radius: 50%;
        background: #00ff88;
        box-shadow: 0 0 8px #00ff88;
      }
    `;
    document.head.appendChild(style);
  }

  // --- Build Virtual Touch HUD ---
  function createTouchHUD() {
    if (document.getElementById('starfield-touch-overlay')) return;

    injectStyles();

    const overlay = document.createElement('div');
    overlay.id = 'starfield-touch-overlay';

    // 1. Virtual Joystick Zone
    joyContainer = document.createElement('div');
    joyContainer.className = 'sf-touch-joy-zone';

    joyBase = document.createElement('div');
    joyBase.className = 'sf-touch-joy-base';

    joyKnob = document.createElement('div');
    joyKnob.className = 'sf-touch-joy-knob';

    joyBase.appendChild(joyKnob);
    joyContainer.appendChild(joyBase);
    overlay.appendChild(joyContainer);

    // Initial default position for joystick base (resting position)
    const defaultX = Math.max(70, window.innerWidth * 0.14);
    const defaultY = window.innerHeight - 100;
    joyBase.style.left = defaultX + 'px';
    joyBase.style.top = defaultY + 'px';

    // 2. Quick Action Cluster
    actionCluster = document.createElement('div');
    actionCluster.className = 'sf-touch-cluster';

    // Row 1: Auxiliary Functions (Cam, Codex, Photo, Settings)
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
    overlay.appendChild(actionCluster);

    // 3. Gamepad Status Badge
    gamepadBadge = document.createElement('div');
    gamepadBadge.className = 'sf-gamepad-badge';
    gamepadBadge.innerHTML = `<i class="dot"></i><span id="sf-gp-name">GAMEPAD CONNECTED</span>`;
    overlay.appendChild(gamepadBadge);

    document.body.appendChild(overlay);

    // Bind Touch Events on Joystick
    setupJoystickEvents();

    // Bind Pinch-to-Zoom on Document/Canvas
    setupPinchZoomEvents();
  }

  function createTouchButton(icon, label, callback) {
    const btn = document.createElement('button');
    btn.className = 'sf-touch-btn';
    btn.innerHTML = `<span>${icon}</span><span class="label">${label}</span>`;
    btn.addEventListener('pointerdown', (e) => {
      e.preventDefault();
      btn.classList.add('active');
      triggerHaptic(15);
      callback();
    });
    btn.addEventListener('pointerup', () => btn.classList.remove('active'));
    btn.addEventListener('pointercancel', () => btn.classList.remove('active'));
    return btn;
  }

  // --- Virtual Joystick Touch Event Handlers ---
  function setupJoystickEvents() {
    if (!joyContainer) return;

    joyContainer.addEventListener('pointerdown', (e) => {
      e.preventDefault();
      if (joyActive) return;

      if (!Engine.isFlightStarted()) {
        Engine.beginFlight();
      }

      joyActive = true;
      joyTouchId = e.pointerId;
      joyContainer.setPointerCapture(e.pointerId);

      // Reposition base dynamically at touch start point
      joyOrigin.x = e.clientX;
      joyOrigin.y = e.clientY;
      joyBase.style.left = joyOrigin.x + 'px';
      joyBase.style.top = joyOrigin.y + 'px';
      joyBase.classList.add('active');
      joyKnob.classList.remove('spring-return');

      updateJoystick(e.clientX, e.clientY);
      triggerHaptic(10);
    });

    joyContainer.addEventListener('pointermove', (e) => {
      if (!joyActive || e.pointerId !== joyTouchId) return;
      e.preventDefault();
      updateJoystick(e.clientX, e.clientY);
    });

    const releaseJoystick = (e) => {
      if (!joyActive || (e && e.pointerId !== joyTouchId)) return;
      joyActive = false;
      joyTouchId = null;

      // Spring-damper return to center
      joyKnob.classList.add('spring-return');
      joyKnob.style.transform = 'translate(-50%, -50%)';
      joyBase.classList.remove('active');

      targetSteerX = 0;
      targetSteerY = 0;
    };

    joyContainer.addEventListener('pointerup', releaseJoystick);
    joyContainer.addEventListener('pointercancel', releaseJoystick);
    joyContainer.addEventListener('lostpointercapture', releaseJoystick);
  }

  function updateJoystick(clientX, clientY) {
    const dx = clientX - joyOrigin.x;
    const dy = clientY - joyOrigin.y;
    const dist = Math.hypot(dx, dy);

    let clampedDist = dist;
    let normX = 0;
    let normY = 0;

    if (dist > 0) {
      clampedDist = Math.min(dist, STICK_MAX_RADIUS);
      normX = (dx / dist) * (clampedDist / STICK_MAX_RADIUS);
      normY = (dy / dist) * (clampedDist / STICK_MAX_RADIUS);
    }

    const knobX = (dx / (dist || 1)) * clampedDist;
    const knobY = (dy / (dist || 1)) * clampedDist;

    joyKnob.style.transform = `translate(calc(-50% + ${knobX.toFixed(1)}px), calc(-50% + ${knobY.toFixed(1)}px))`;

    targetSteerX = normX;
    targetSteerY = normY;
  }

  // --- Two-Finger Pinch-to-Zoom Handler ---
  function setupPinchZoomEvents() {
    window.addEventListener('touchstart', (e) => {
      for (let i = 0; i < e.changedTouches.length; i++) {
        const t = e.changedTouches[i];
        activeTouches.set(t.identifier, { x: t.clientX, y: t.clientY });
      }

      if (activeTouches.size === 2) {
        const pts = Array.from(activeTouches.values());
        initialPinchDist = Math.hypot(pts[0].x - pts[1].x, pts[0].y - pts[1].y);
        lastPinchDist = initialPinchDist;
      }
    }, { passive: true });

    window.addEventListener('touchmove', (e) => {
      for (let i = 0; i < e.changedTouches.length; i++) {
        const t = e.changedTouches[i];
        if (activeTouches.has(t.identifier)) {
          activeTouches.set(t.identifier, { x: t.clientX, y: t.clientY });
        }
      }

      if (activeTouches.size >= 2) {
        const pts = Array.from(activeTouches.values());
        const curDist = Math.hypot(pts[0].x - pts[1].x, pts[0].y - pts[1].y);

        if (lastPinchDist > 0 && Math.abs(curDist - lastPinchDist) > 3) {
          const factor = curDist / lastPinchDist;
          Engine.zoomCamera(factor);
          lastPinchDist = curDist;
        }
      }
    }, { passive: true });

    const removeTouches = (e) => {
      for (let i = 0; i < e.changedTouches.length; i++) {
        activeTouches.delete(e.changedTouches[i].identifier);
      }
      if (activeTouches.size < 2) {
        initialPinchDist = 0;
        lastPinchDist = 0;
      }
    };

    window.addEventListener('touchend', removeTouches, { passive: true });
    window.addEventListener('touchcancel', removeTouches, { passive: true });
  }

  // --- Gamepad Connection Notification ---
  function showGamepadToast(name) {
    if (!gamepadBadge) return;
    const txt = document.getElementById('sf-gp-name');
    if (txt) txt.textContent = `🎮 ${name || 'GAMEPAD'} CONNECTED`;
    gamepadBadge.classList.add('show');
    setTimeout(() => {
      if (gamepadBadge) gamepadBadge.classList.remove('show');
    }, 3800);
  }

  // --- Gamepad Main Polling & Processing Loop ---
  function pollGamepad(now) {
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

    if (pad) {
      if (!gamepadConnected) {
        gamepadConnected = true;
        let padTitle = 'STANDARD CONTROLLER';
        if (pad.id.includes('045e') || pad.id.toLowerCase().includes('xbox')) padTitle = 'XBOX CONTROLLER';
        else if (pad.id.includes('054c') || pad.id.toLowerCase().includes('dualsense') || pad.id.toLowerCase().includes('wireless controller')) padTitle = 'PLAYSTATION CONTROLLER';
        showGamepadToast(padTitle);
        playRumble(pad, { duration: 180, weakMagnitude: 0.5, strongMagnitude: 0.5 });
      }

      // --- 1. Left Stick: Flight Steering ---
      let lx = pad.axes[0] || 0;
      let ly = pad.axes[1] || 0;
      const lmag = Math.hypot(lx, ly);

      if (lmag < DEADZONE_LEFT) {
        lx = 0;
        ly = 0;
      } else {
        const factor = (lmag - DEADZONE_LEFT) / (1 - DEADZONE_LEFT);
        lx = (lx / lmag) * factor;
        ly = (ly / lmag) * factor;
      }

      // If virtual touch joystick isn't overriding, use gamepad left stick
      if (!joyActive) {
        targetSteerX = lx;
        targetSteerY = ly;
      }

      // --- 2. Right Stick: Free Camera Rotation ---
      let rx = pad.axes[2] || 0;
      let ry = pad.axes[3] || 0;
      const rmag = Math.hypot(rx, ry);

      if (rmag > DEADZONE_RIGHT) {
        const factor = (rmag - DEADZONE_RIGHT) / (1 - DEADZONE_RIGHT);
        const dyaw = (rx / rmag) * factor * CAMERA_YAW_SPEED * dt;
        const dpitch = (ry / rmag) * factor * CAMERA_PITCH_SPEED * dt;
        Engine.rotateCamera(dyaw, dpitch);
      }

      // --- 3. Buttons & Triggers ---
      const buttons = pad.buttons || [];
      const isPressed = (idx) => buttons[idx] && (buttons[idx].pressed || buttons[idx].value > 0.5);
      const isJustPressed = (idx) => isPressed(idx) && !prevButtons[idx];

      // South Button A (buttons[0]): Slingshot Boost / Warp Burst
      if (isJustPressed(0)) {
        if (!Engine.isFlightStarted()) {
          Engine.beginFlight();
        } else {
          Engine.slingshotBoost();
          Engine.setWarpHold(true);
          playRumble(pad, { duration: 250, strongMagnitude: 0.85, weakMagnitude: 0.6 });
        }
      } else if (!isPressed(0) && prevButtons[0]) {
        Engine.setWarpHold(false);
      }

      // East Button B (buttons[1]): Close Modal / Back
      if (isJustPressed(1)) {
        Engine.closeModal();
      }

      // West Button X (buttons[2]): Toggle Deep Space Photo Mode ('P')
      if (isJustPressed(2)) {
        Engine.togglePhoto();
      }

      // North Button Y (buttons[3]): Toggle Codex ('Tab' / 'J')
      if (isJustPressed(3)) {
        Engine.toggleCodex();
      }

      // Triggers & Bumpers: Throttle Speed Up / Slow Down
      // LB (buttons[4]) or LT (buttons[6]): Slow Down
      if (isJustPressed(4) || isJustPressed(6)) {
        Engine.throttleDown();
        playRumble(pad, { duration: 120, weakMagnitude: 0.4, strongMagnitude: 0.2 });
      }

      // RB (buttons[5]) or RT (buttons[7]): Speed Up
      if (isJustPressed(5) || isJustPressed(7)) {
        Engine.throttleUp();
        playRumble(pad, { duration: 140, weakMagnitude: 0.5, strongMagnitude: 0.4 });
      }

      // Start / Menu Button (buttons[9]): System Settings ('ESC')
      if (isJustPressed(9)) {
        if (!Engine.isFlightStarted()) {
          Engine.beginFlight();
        } else {
          Engine.toggleSettings();
        }
      }

      // D-Pad Up (buttons[12]): Toggle Cockpit View ('V')
      if (isJustPressed(12)) {
        Engine.toggleCockpit();
        playRumble(pad, { duration: 80, weakMagnitude: 0.3, strongMagnitude: 0.2 });
      }

      // D-Pad Down (buttons[13]): Toggle Director Camera ('C')
      if (isJustPressed(13)) {
        Engine.toggleCamera();
        playRumble(pad, { duration: 80, weakMagnitude: 0.3, strongMagnitude: 0.2 });
      }

      // D-Pad Left (buttons[14]): Cycle Formations backward
      if (isJustPressed(14)) {
        Engine.cycleFormation(-1);
        playRumble(pad, { duration: 100, weakMagnitude: 0.3, strongMagnitude: 0.3 });
      }

      // D-Pad Right (buttons[15]): Cycle Formations forward
      if (isJustPressed(15)) {
        Engine.cycleFormation(1);
        playRumble(pad, { duration: 100, weakMagnitude: 0.3, strongMagnitude: 0.3 });
      }

      // --- 4. Haptic Vibration Event Triggers ---
      // Slingshot Surge Rumble
      const curSurge = Engine.isSlingshotSurge();
      if (curSurge && !prevSurge) {
        playRumble(pad, { duration: 650, strongMagnitude: 0.9, weakMagnitude: 0.95 });
      }
      prevSurge = curSurge;

      // Wormhole Passing Rumble
      const curGateT = Engine.getGateT();
      if (curGateT >= 3.0 && prevGateT < 3.0) {
        playRumble(pad, { duration: 850, strongMagnitude: 1.0, weakMagnitude: 0.75 });
      }
      prevGateT = curGateT;

      // Black Hole Event Horizon Skimming Rumble
      const curCapturePhase = Engine.getCapturePhase();
      if (curCapturePhase > 0 && prevCapturePhase === 0) {
        playRumble(pad, { duration: 700, strongMagnitude: 0.85, weakMagnitude: 0.45 });
      }
      prevCapturePhase = curCapturePhase;

      // Update button edge history
      prevButtons = buttons.map(b => b.pressed || b.value > 0.5);
    } else {
      if (gamepadConnected) {
        gamepadConnected = false;
        activeGamepadIndex = -1;
      }
    }

    // --- 5. Smooth Interpolation for Steering ---
    const smoothFactor = Math.min(1.0, dt * 8.5);
    steerX += (targetSteerX - steerX) * smoothFactor;
    steerY += (targetSteerY - steerY) * smoothFactor;

    if (Math.abs(steerX) > 0.001 || Math.abs(steerY) > 0.001 || joyActive) {
      Engine.applySteer(steerX, steerY);
    }

    // Continue frame loop
    rafId = requestAnimationFrame(pollGamepad);
  }

  // --- Gamepad Connection Events ---
  function setupGamepadEvents() {
    window.addEventListener('gamepadconnected', (e) => {
      const gp = e.gamepad || (navigator.getGamepads ? navigator.getGamepads()[0] : null);
      if (gp) {
        activeGamepadIndex = gp.index || 0;
        gamepadConnected = true;
        showGamepadToast(gp.id);
      }
    });

    window.addEventListener('gamepaddisconnected', (e) => {
      const gp = e.gamepad;
      if (!gp || activeGamepadIndex === gp.index) {
        activeGamepadIndex = -1;
        gamepadConnected = false;
        targetSteerX = 0;
        targetSteerY = 0;
      }
    });
  }

  // --- Auto Detection for Touch ---
  function detectTouch() {
    isTouchCapable = (
      ('ontouchstart' in window) ||
      (navigator.maxTouchPoints > 0) ||
      (window.matchMedia && window.matchMedia('(pointer: coarse)').matches)
    );

    if (isTouchCapable) {
      createTouchHUD();
      touchHudVisible = true;
    } else {
      // First touch listener: reveal HUD dynamically if user touches screen
      const onFirstTouch = () => {
        isTouchCapable = true;
        createTouchHUD();
        touchHudVisible = true;
        window.removeEventListener('touchstart', onFirstTouch);
      };
      window.addEventListener('touchstart', onFirstTouch, { passive: true, once: true });
    }
  }

  // --- Public Interface ---
  const GamepadTouchControls = {
    version: '1.0.0',

    init(options = {}) {
      if (isInitialized) return this;

      detectTouch();
      setupGamepadEvents();

      lastFrameTime = performance.now();
      rafId = requestAnimationFrame(pollGamepad);

      isInitialized = true;
      return this;
    },

    destroy() {
      if (rafId) {
        cancelAnimationFrame(rafId);
        rafId = null;
      }
      const overlay = document.getElementById('starfield-touch-overlay');
      if (overlay) overlay.remove();
      const style = document.getElementById('starfield-gamepad-touch-styles');
      if (style) style.remove();
      isInitialized = false;
    },

    isInitialized() {
      return isInitialized;
    },

    isTouchDevice() {
      return isTouchCapable;
    },

    isGamepadConnected() {
      return gamepadConnected;
    },

    getGamepadState() {
      return {
        connected: gamepadConnected,
        index: activeGamepadIndex,
        steerX,
        steerY
      };
    },

    getTouchState() {
      return {
        capable: isTouchCapable,
        hudVisible: touchHudVisible,
        joyActive,
        joyOffset: { ...joyOffset }
      };
    },

    simulateTouchSteer(sx, sy) {
      targetSteerX = Math.max(-1, Math.min(1, sx));
      targetSteerY = Math.max(-1, Math.min(1, sy));
      Engine.applySteer(targetSteerX, targetSteerY);
    },

    simulatePinchZoom(factor) {
      Engine.zoomCamera(factor);
    },

    playRumble(effectType = 'dual-rumble', params = {}) {
      const gamepads = (navigator.getGamepads ? navigator.getGamepads() : []) || [];
      const pad = gamepads[activeGamepadIndex] || gamepads[0];
      if (pad) {
        playRumble(pad, params);
      }
    },

    setTouchControlsVisible(visible) {
      const overlay = document.getElementById('starfield-touch-overlay');
      if (overlay) {
        overlay.style.display = visible ? '' : 'none';
        touchHudVisible = visible;
      }
    }
  };

  // Expose to window
  window.GamepadTouchControls = GamepadTouchControls;

  // Auto-initialize when ready
  if (document.readyState === 'complete' || document.readyState === 'interactive') {
    GamepadTouchControls.init();
  } else {
    window.addEventListener('DOMContentLoaded', () => GamepadTouchControls.init());
  }

})(typeof window !== 'undefined' ? window : this);
