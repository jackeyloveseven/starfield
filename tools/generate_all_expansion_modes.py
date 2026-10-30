# -*- coding: utf-8 -*-
"""
Complete generator for Starfield Grand Expansion Modes.
Builds and injects:
1. Void Extraction (Escape from Duckov)
2. Orbital Slingshot (Angry Birds Space)
3. Red Alert RTS (Command & Conquer Base Building & War)
4. Dyson Sphere Program (Megastructure & Interstellar Logistics)
"""

import sys

def get_complete_expansion():
    # Read CSS and HTML from starfield.html
    with open('starfield-pub/starfield.html', 'r', encoding='utf-8') as f:
        html_content = f.read()

    css_start = html_content.find('<style id="sf-expansion-modes-css">')
    css_end = html_content.find('</style>', css_start) + len('</style>')
    css_block = html_content[css_start:css_end]

    html_start = html_content.find('<div id="sf-mode-bar">')
    html_end = html_content.find('<script id="sf-expansion-modes-js">', html_start)
    html_block = html_content[html_start:html_end].strip()

    # Read extracted Void Extraction & Orbital Slingshot engines
    with open('starfield-pub/tools/inject_expansion_modes.py', 'r', encoding='utf-8') as f:
        existing = f.read()

    # Extract Void Extraction code
    v_start = existing.find('class VoidExtractionGame')
    v_end = existing.find('window.VoidExtraction = new VoidExtractionGame();')

    s_start = existing.find('class OrbitalSlingshotGame')
    s_end = existing.find('window.OrbitalSlingshot = new OrbitalSlingshotGame();')

    void_engine = existing[v_start:v_end].strip()
    slingshot_engine = existing[s_start:s_end].strip()

    # Build the full JavaScript block
    js_block = f'''
<script id="sf-expansion-modes-js">
(function() {{
  "use strict";

  /* =========================================================================
   * 0. AUDIO SYNTHESIZER FOR EXPANSION MODES (Web Audio API)
   * ========================================================================= */
  const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
  function playTone(freq, duration, type = 'sine', gainVal = 0.15) {{
    if (!audioCtx) return;
    try {{
      if (audioCtx.state === 'suspended') audioCtx.resume();
      const osc = audioCtx.createOscillator();
      const gain = audioCtx.createGain();
      osc.type = type;
      osc.frequency.setValueAtTime(freq, audioCtx.currentTime);
      gain.gain.setValueAtTime(gainVal, audioCtx.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.0001, audioCtx.currentTime + duration);
      osc.connect(gain);
      gain.connect(audioCtx.destination);
      osc.start();
      osc.stop(audioCtx.currentTime + duration);
    }} catch(e) {{}}
  }}

  function playExplosionSfx() {{
    if (!audioCtx) return;
    try {{
      if (audioCtx.state === 'suspended') audioCtx.resume();
      const bufSize = audioCtx.sampleRate * 0.4;
      const buffer = audioCtx.createBuffer(1, bufSize, audioCtx.sampleRate);
      const output = buffer.getChannelData(0);
      for (let i = 0; i < bufSize; i++) {{
        output[i] = (Math.random() * 2 - 1) * Math.exp(-i / (bufSize * 0.3));
      }}
      const whiteNoise = audioCtx.createBufferSource();
      whiteNoise.buffer = buffer;
      const filter = audioCtx.createBiquadFilter();
      filter.type = 'lowpass';
      filter.frequency.setValueAtTime(400, audioCtx.currentTime);
      filter.frequency.exponentialRampToValueAtTime(50, audioCtx.currentTime + 0.4);
      const gain = audioCtx.createGain();
      gain.gain.setValueAtTime(0.3, audioCtx.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.001, audioCtx.currentTime + 0.4);
      whiteNoise.connect(filter);
      filter.connect(gain);
      gain.connect(audioCtx.destination);
      whiteNoise.start();
    }} catch(e) {{}}
  }}

  class SpaceAudioSynth {{
    constructor() {{
      this.ctx = null;
    }}
    init() {{
      if (!this.ctx) {{
        const AudioContext = window.AudioContext || window.webkitAudioContext;
        if (AudioContext) {{
          this.ctx = new AudioContext();
        }}
      }}
      if (this.ctx && this.ctx.state === 'suspended') {{
        this.ctx.resume().catch(() => {{}});
      }}
    }}
    playLaser() {{
      try {{
        this.init();
        if (!this.ctx) return;
        const now = this.ctx.currentTime;
        const osc = this.ctx.createOscillator();
        const gain = this.ctx.createGain();
        osc.type = 'sawtooth';
        osc.frequency.setValueAtTime(880, now);
        osc.frequency.exponentialRampToValueAtTime(110, now + 0.12);
        gain.gain.setValueAtTime(0.08, now);
        gain.gain.exponentialRampToValueAtTime(0.001, now + 0.12);
        osc.connect(gain);
        gain.connect(this.ctx.destination);
        osc.start(now);
        osc.stop(now + 0.12);
      }} catch(e) {{}}
    }}
    playTeslaZap() {{
      try {{
        this.init();
        if (!this.ctx) return;
        const now = this.ctx.currentTime;
        const osc = this.ctx.createOscillator();
        const gain = this.ctx.createGain();
        osc.type = 'triangle';
        osc.frequency.setValueAtTime(180, now);
        osc.frequency.linearRampToValueAtTime(1200, now + 0.04);
        osc.frequency.linearRampToValueAtTime(60, now + 0.16);
        gain.gain.setValueAtTime(0.12, now);
        gain.gain.exponentialRampToValueAtTime(0.001, now + 0.16);
        osc.connect(gain);
        gain.connect(this.ctx.destination);
        osc.start(now);
        osc.stop(now + 0.16);
      }} catch(e) {{}}
    }}
    playExplosion() {{
      try {{
        this.init();
        if (!this.ctx) return;
        const now = this.ctx.currentTime;
        const osc = this.ctx.createOscillator();
        const gain = this.ctx.createGain();
        osc.type = 'sawtooth';
        osc.frequency.setValueAtTime(150, now);
        osc.frequency.exponentialRampToValueAtTime(30, now + 0.35);
        gain.gain.setValueAtTime(0.15, now);
        gain.gain.exponentialRampToValueAtTime(0.001, now + 0.35);
        osc.connect(gain);
        gain.connect(this.ctx.destination);
        osc.start(now);
        osc.stop(now + 0.35);
      }} catch(e) {{}}
    }}
    playCredit() {{
      try {{
        this.init();
        if (!this.ctx) return;
        const now = this.ctx.currentTime;
        [523.25, 659.25, 783.99, 1046.50].forEach((freq, i) => {{
          const osc = this.ctx.createOscillator();
          const gain = this.ctx.createGain();
          osc.type = 'sine';
          osc.frequency.value = freq;
          gain.gain.setValueAtTime(0.05, now + i * 0.04);
          gain.gain.exponentialRampToValueAtTime(0.001, now + i * 0.04 + 0.15);
          osc.connect(gain);
          gain.connect(this.ctx.destination);
          osc.start(now + i * 0.04);
          osc.stop(now + i * 0.04 + 0.15);
        }});
      }} catch(e) {{}}
    }}
    playRocketLaunch() {{
      try {{
        this.init();
        if (!this.ctx) return;
        const now = this.ctx.currentTime;
        const osc = this.ctx.createOscillator();
        const gain = this.ctx.createGain();
        osc.type = 'sawtooth';
        osc.frequency.setValueAtTime(60, now);
        osc.frequency.exponentialRampToValueAtTime(340, now + 0.4);
        gain.gain.setValueAtTime(0.1, now);
        gain.gain.exponentialRampToValueAtTime(0.001, now + 0.45);
        osc.connect(gain);
        gain.connect(this.ctx.destination);
        osc.start(now);
        osc.stop(now + 0.45);
      }} catch(e) {{}}
    }}
    playSailLaunch() {{
      try {{
        this.init();
        if (!this.ctx) return;
        const now = this.ctx.currentTime;
        const osc = this.ctx.createOscillator();
        const gain = this.ctx.createGain();
        osc.type = 'sine';
        osc.frequency.setValueAtTime(440, now);
        osc.frequency.exponentialRampToValueAtTime(1760, now + 0.25);
        gain.gain.setValueAtTime(0.08, now);
        gain.gain.exponentialRampToValueAtTime(0.001, now + 0.25);
        osc.connect(gain);
        gain.connect(this.ctx.destination);
        osc.start(now);
        osc.stop(now + 0.25);
      }} catch(e) {{}}
    }}
    playIonCannon() {{
      try {{
        this.init();
        if (!this.ctx) return;
        const now = this.ctx.currentTime;
        const osc1 = this.ctx.createOscillator();
        const gain1 = this.ctx.createGain();
        osc1.type = 'sine';
        osc1.frequency.setValueAtTime(320, now);
        osc1.frequency.exponentialRampToValueAtTime(2600, now + 0.7);
        gain1.gain.setValueAtTime(0.15, now);
        gain1.gain.exponentialRampToValueAtTime(0.001, now + 0.75);
        osc1.connect(gain1);
        gain1.connect(this.ctx.destination);
        osc1.start(now);
        osc1.stop(now + 0.75);

        const osc2 = this.ctx.createOscillator();
        const gain2 = this.ctx.createGain();
        osc2.type = 'sawtooth';
        osc2.frequency.setValueAtTime(100, now + 0.7);
        osc2.frequency.exponentialRampToValueAtTime(25, now + 1.6);
        gain2.gain.setValueAtTime(0.28, now + 0.7);
        gain2.gain.exponentialRampToValueAtTime(0.001, now + 1.7);
        osc2.connect(gain2);
        gain2.connect(this.ctx.destination);
        osc2.start(now + 0.7);
        osc2.stop(now + 1.7);
      }} catch(e) {{}}
    }}
  }}
  const spaceAudio = new SpaceAudioSynth();

  /* =========================================================================
   * 1. MASTER MODE SWITCHER
   * ========================================================================= */
  const btnCruise = document.getElementById('sf-btn-mode-cruise');
  const btnExtract = document.getElementById('sf-btn-mode-extract');
  const btnSling = document.getElementById('sf-btn-mode-slingshot');
  const btnRedAlert = document.getElementById('sf-btn-mode-redalert');
  const btnDyson = document.getElementById('sf-btn-mode-dyson');

  const overlayExtract = document.getElementById('sf-extraction-overlay');
  const overlaySling = document.getElementById('sf-slingshot-overlay');
  const overlayRedAlert = document.getElementById('sf-redalert-overlay');
  const overlayDyson = document.getElementById('sf-dyson-overlay');

  let currentMode = 'cruise';

  function switchMode(newMode) {{
    if (currentMode === newMode) return;
    currentMode = newMode;
    [btnCruise, btnExtract, btnSling, btnRedAlert, btnDyson].forEach(b => b && b.classList.remove('active'));
    [overlayExtract, overlaySling, overlayRedAlert, overlayDyson].forEach(o => o && o.classList.remove('active'));

    // Stop all active engines
    if (window.VoidExtraction) window.VoidExtraction.stop();
    if (window.OrbitalSlingshot) window.OrbitalSlingshot.stop();
    if (window.RedAlertRTS) window.RedAlertRTS.stop();
    if (window.DysonSphereProgram) window.DysonSphereProgram.stop();

    if (newMode === 'cruise') {{
      btnCruise.classList.add('active');
      if (typeof showToast === 'function') showToast('已切回深空自由漫游心流 🌌', 2);
    }} else if (newMode === 'extract') {{
      btnExtract.classList.add('active');
      overlayExtract.classList.add('active');
      if (window.VoidExtraction) window.VoidExtraction.start();
      if (typeof showToast === 'function') showToast('已部署至【搜打撤 · 鸭科夫战区】！搜索高维物资并成功撤离！', 3.5);
    }} else if (newMode === 'slingshot') {{
      btnSling.classList.add('active');
      overlaySling.classList.add('active');
      if (window.OrbitalSlingshot) window.OrbitalSlingshot.start();
      if (typeof showToast === 'function') showToast('已进入【愤怒的小鸟太空版 · 轨道引力弹弓】！拉伸弹弓发射！', 3.5);
    }} else if (newMode === 'redalert') {{
      btnRedAlert.classList.add('active');
      overlayRedAlert.classList.add('active');
      if (window.RedAlertRTS) window.RedAlertRTS.start();
      if (typeof showToast === 'function') showToast('已启动【红色警戒 · 星际前哨RTS】！采矿精炼、建造磁暴与天启战舰！', 3.5);
    }} else if (newMode === 'dyson') {{
      btnDyson.classList.add('active');
      overlayDyson.classList.add('active');
      if (window.DysonSphereProgram) window.DysonSphereProgram.start();
      if (typeof showToast === 'function') showToast('已开启【戴森球计划 · 星系巨构】！电磁弹射太阳帆，运载火箭筑造戴森球！', 3.5);
    }}
  }}

  btnCruise?.addEventListener('click', () => switchMode('cruise'));
  btnExtract?.addEventListener('click', () => switchMode('extract'));
  btnSling?.addEventListener('click', () => switchMode('slingshot'));
  btnRedAlert?.addEventListener('click', () => switchMode('redalert'));
  btnDyson?.addEventListener('click', () => switchMode('dyson'));

  document.getElementById('sf-ext-exit-btn')?.addEventListener('click', () => switchMode('cruise'));
  document.getElementById('sf-sling-exit-btn')?.addEventListener('click', () => switchMode('cruise'));
  document.getElementById('sf-ra-exit-btn')?.addEventListener('click', () => switchMode('cruise'));
  document.getElementById('sf-dsp-exit-btn')?.addEventListener('click', () => switchMode('cruise'));

  window.switchStarfieldMode = switchMode;

  /* =========================================================================
   * 2. VOID EXTRACTION ENGINE (搜打撤 / Escape from Duckov in Space)
   * ========================================================================= */
  {void_engine}

  window.VoidExtraction = new VoidExtractionGame();

  /* =========================================================================
   * 3. ORBITAL SLINGSHOT ENGINE (引力弹弓太空鸟 / Angry Birds Space)
   * ========================================================================= */
  {slingshot_engine}

  window.OrbitalSlingshot = new OrbitalSlingshotGame();

  /* =========================================================================
   * 4. RED ALERT RTS ENGINE (红色警戒 · 星际基地争霸)
   * ========================================================================= */
  class RedAlertRTSGame {{
    constructor() {{
      this.canvas = document.getElementById('sf-redalert-canvas');
      this.ctx = this.canvas.getContext('2d');
      this.active = false;
      this.animId = null;

      this.worldWidth = 2400;
      this.worldHeight = 1600;
      this.camera = {{ x: 200, y: 400, zoom: 0.9 }};

      this.credits = 3000;
      this.powerGen = 160;
      this.powerReq = 30;
      this.isLowPower = false;

      this.ionCannon = {{
        unlocked: false,
        timer: 40,
        maxTimer: 40,
        ready: false,
        targeting: false
      }};

      this.wave = 1;
      this.waveTimer = 35;

      this.buildings = [];
      this.units = [];
      this.harvesters = [];
      this.enemies = [];
      this.oreFields = [];
      this.bullets = [];
      this.particles = [];
      this.orbitalStrikes = [];

      this.selectedUnits = [];
      this.dragSelect = {{ active: false, startX: 0, startY: 0, curX: 0, curY: 0 }};
      this.isPanning = false;
      this.panStart = {{ x: 0, y: 0, camX: 0, camY: 0 }};
      this.shake = 0;

      this.bindEvents();
    }}

    start() {{
      this.resize();
      this.resetGame();
      this.active = true;
      this.lastTime = performance.now();
      this.animId = requestAnimationFrame((t) => this.loop(t));
    }}

    stop() {{
      this.active = false;
      if (this.animId) cancelAnimationFrame(this.animId);
    }}

    resize() {{
      this.canvas.width = window.innerWidth;
      this.canvas.height = window.innerHeight;
    }}

    resetGame() {{
      this.credits = 3000;
      this.buildings = [
        {{ id: 1, type: 'hq', name: '基地指挥所', x: 450, y: 800, w: 90, h: 90, hp: 2500, maxHp: 2500, powerGen: 40, powerReq: 0, color: '#38bdf8' }},
        {{ id: 2, type: 'power', name: '聚变电厂', x: 340, y: 680, w: 70, h: 70, hp: 800, maxHp: 800, powerGen: 120, powerReq: 0, color: '#f59e0b' }},
        {{ id: 3, type: 'refinery', name: '矿石精炼厂', x: 580, y: 690, w: 85, h: 85, hp: 1000, maxHp: 1000, powerGen: 0, powerReq: 30, color: '#10b981' }}
      ];

      this.oreFields = [
        {{ x: 920, y: 480, radius: 110, ore: 6000, color: '#34d399' }},
        {{ x: 1050, y: 1100, radius: 130, ore: 8000, color: '#38bdf8' }},
        {{ x: 1450, y: 780, radius: 150, ore: 12000, color: '#a78bfa' }}
      ];

      this.harvesters = [
        {{
          id: 1, x: 580, y: 690, vx: 0, vy: 0, angle: 0,
          state: 'to_ore', cargo: 0, maxCargo: 1000,
          hp: 600, maxHp: 600, speed: 2.2, targetOre: this.oreFields[0]
        }}
      ];

      this.units = [
        {{ id: 101, type: 'fighter', x: 600, y: 860, vx: 0, vy: 0, angle: 0, hp: 140, maxHp: 140, speed: 3.5, range: 180, dmg: 14, reload: 0, maxReload: 0.35, selected: false }},
        {{ id: 102, type: 'fighter', x: 600, y: 920, vx: 0, vy: 0, angle: 0, hp: 140, maxHp: 140, speed: 3.5, range: 180, dmg: 14, reload: 0, maxReload: 0.35, selected: false }}
      ];

      this.enemies = [
        {{ id: 501, type: 'scout', x: 2100, y: 760, vx: 0, vy: 0, angle: Math.PI, hp: 120, maxHp: 120, speed: 2.8, range: 160, dmg: 10, reload: 0, maxReload: 0.4 }},
        {{ id: 502, type: 'scout', x: 2100, y: 840, vx: 0, vy: 0, angle: Math.PI, hp: 120, maxHp: 120, speed: 2.8, range: 160, dmg: 10, reload: 0, maxReload: 0.4 }}
      ];

      this.bullets = [];
      this.particles = [];
      this.orbitalStrikes = [];
      this.selectedUnits = [];
      this.wave = 1;
      this.waveTimer = 35;
      this.ionCannon.timer = 40;
      this.ionCannon.ready = false;
      this.ionCannon.targeting = false;

      this.updatePowerGrid();
      this.updateHUD();
    }}

    bindEvents() {{
      window.addEventListener('resize', () => {{ if (this.active) this.resize(); }});

      // Sidebar Building Buttons
      document.getElementById('sf-ra-btn-bld-power')?.addEventListener('click', () => this.buildBuilding('power', 300));
      document.getElementById('sf-ra-btn-bld-refinery')?.addEventListener('click', () => this.buildBuilding('refinery', 800));
      document.getElementById('sf-ra-btn-bld-shipyard')?.addEventListener('click', () => this.buildBuilding('shipyard', 1000));
      document.getElementById('sf-ra-btn-bld-tesla')?.addEventListener('click', () => this.buildBuilding('tesla', 600));
      document.getElementById('sf-ra-btn-bld-prism')?.addEventListener('click', () => this.buildBuilding('prism', 750));
      document.getElementById('sf-ra-btn-bld-ion')?.addEventListener('click', () => this.buildBuilding('ion', 1500));

      // Sidebar Unit Buttons
      document.getElementById('sf-ra-btn-unit-fighter')?.addEventListener('click', () => this.produceUnit('fighter', 200));
      document.getElementById('sf-ra-btn-unit-cruiser')?.addEventListener('click', () => this.produceUnit('cruiser', 550));
      document.getElementById('sf-ra-btn-unit-dreadnought')?.addEventListener('click', () => this.produceUnit('dreadnought', 1200));
      document.getElementById('sf-ra-btn-unit-harvester')?.addEventListener('click', () => this.produceUnit('harvester', 400));

      // Tactical Command Buttons
      document.getElementById('sf-ra-btn-select-all')?.addEventListener('click', () => this.selectAllCombatUnits());
      document.getElementById('sf-ra-btn-defend')?.addEventListener('click', () => this.commandDefendHQ());
      document.getElementById('sf-ra-btn-assault')?.addEventListener('click', () => this.commandAssaultRift());
      document.getElementById('sf-ra-btn-ion-strike')?.addEventListener('click', () => this.armIonCannon());
      document.getElementById('sf-ra-btn-spawn-wave')?.addEventListener('click', () => this.spawnWave());

      // Canvas Pointer Events
      const c = this.canvas;
      const getPos = (e) => {{
        const rect = c.getBoundingClientRect();
        return {{ x: e.clientX - rect.left, y: e.clientY - rect.top }};
      }};

      c.addEventListener('mousedown', (e) => {{
        if (!this.active) return;
        const p = getPos(e);

        if (this.ionCannon.targeting) {{
          // Fire Ion Cannon Strike
          const wx = (p.x / this.camera.zoom) + this.camera.x;
          const wy = (p.y / this.camera.zoom) + this.camera.y;
          this.executeIonCannonStrike(wx, wy);
          return;
        }}

        if (e.button === 0) {{
          // Left Click: Drag select or select
          this.dragSelect.active = true;
          this.dragSelect.startX = p.x;
          this.dragSelect.startY = p.y;
          this.dragSelect.curX = p.x;
          this.dragSelect.curY = p.y;
        }} else if (e.button === 2) {{
          // Right Click: Move or Attack Order
          const wx = (p.x / this.camera.zoom) + this.camera.x;
          const wy = (p.y / this.camera.zoom) + this.camera.y;
          this.issueOrder(wx, wy);
        }}
      }});

      window.addEventListener('mousemove', (e) => {{
        if (!this.active) return;
        const p = getPos(e);
        if (this.dragSelect.active) {{
          this.dragSelect.curX = p.x;
          this.dragSelect.curY = p.y;
        }}
        if (this.isPanning) {{
          const dx = (p.x - this.panStart.x) / this.camera.zoom;
          const dy = (p.y - this.panStart.y) / this.camera.zoom;
          this.camera.x = this.panStart.camX - dx;
          this.camera.y = this.panStart.camY - dy;
        }}
      }});

      window.addEventListener('mouseup', (e) => {{
        if (!this.active) return;
        if (e.button === 0 && this.dragSelect.active) {{
          this.dragSelect.active = false;
          this.applyBoxSelection();
        }}
        this.isPanning = false;
      }});

      c.addEventListener('contextmenu', (e) => e.preventDefault());

      // Touch Events for Mobile
      let touchStartDist = 0;
      c.addEventListener('touchstart', (e) => {{
        if (!this.active) return;
        if (e.touches.length === 1) {{
          const t = e.touches[0];
          const p = getPos(t);
          if (this.ionCannon.targeting) {{
            const wx = (p.x / this.camera.zoom) + this.camera.x;
            const wy = (p.y / this.camera.zoom) + this.camera.y;
            this.executeIonCannonStrike(wx, wy);
            return;
          }}
          if (this.selectedUnits.length > 0) {{
            // Touch order if units selected
            const wx = (p.x / this.camera.zoom) + this.camera.x;
            const wy = (p.y / this.camera.zoom) + this.camera.y;
            this.issueOrder(wx, wy);
          }} else {{
            // Drag select
            this.dragSelect.active = true;
            this.dragSelect.startX = p.x;
            this.dragSelect.startY = p.y;
            this.dragSelect.curX = p.x;
            this.dragSelect.curY = p.y;
          }}
        }} else if (e.touches.length === 2) {{
          // Two-finger pan & pinch
          this.dragSelect.active = false;
          const t1 = e.touches[0], t2 = e.touches[1];
          touchStartDist = Math.hypot(t2.clientX - t1.clientX, t2.clientY - t1.clientY);
          this.panStart.x = (t1.clientX + t2.clientX) / 2;
          this.panStart.y = (t1.clientY + t2.clientY) / 2;
          this.panStart.camX = this.camera.x;
          this.panStart.camY = this.camera.y;
        }}
      }}, {{ passive: false }});

      c.addEventListener('touchmove', (e) => {{
        if (!this.active) return;
        if (e.touches.length === 1 && this.dragSelect.active) {{
          const p = getPos(e.touches[0]);
          this.dragSelect.curX = p.x;
          this.dragSelect.curY = p.y;
        }} else if (e.touches.length === 2) {{
          const t1 = e.touches[0], t2 = e.touches[1];
          const midX = (t1.clientX + t2.clientX) / 2;
          const midY = (t1.clientY + t2.clientY) / 2;
          const dx = (midX - this.panStart.x) / this.camera.zoom;
          const dy = (midY - this.panStart.y) / this.camera.zoom;
          this.camera.x = this.panStart.camX - dx;
          this.camera.y = this.panStart.camY - dy;

          const dist = Math.hypot(t2.clientX - t1.clientX, t2.clientY - t1.clientY);
          if (touchStartDist > 0) {{
            this.camera.zoom = Math.max(0.5, Math.min(1.8, this.camera.zoom * (dist / touchStartDist)));
            touchStartDist = dist;
          }}
        }}
      }}, {{ passive: false }});

      c.addEventListener('touchend', (e) => {{
        if (!this.active) return;
        if (this.dragSelect.active) {{
          this.dragSelect.active = false;
          this.applyBoxSelection();
        }}
      }});

      // Mouse Wheel Zoom
      c.addEventListener('wheel', (e) => {{
        if (!this.active) return;
        e.preventDefault();
        const factor = e.deltaY < 0 ? 1.1 : 0.9;
        this.camera.zoom = Math.max(0.5, Math.min(1.8, this.camera.zoom * factor));
      }}, {{ passive: false }});
    }}

    buildBuilding(type, cost) {{
      if (this.credits < cost) {{
        if (typeof showToast === 'function') showToast('资金不足！需要 $' + cost, 2);
        return;
      }}
      this.credits -= cost;
      spaceAudio.playCredit();

      const baseHQ = this.buildings.find(b => b.type === 'hq') || {{ x: 450, y: 800 }};
      const angle = Math.random() * Math.PI * 2;
      const dist = 120 + Math.random() * 140;
      const bx = baseHQ.x + Math.cos(angle) * dist;
      const by = baseHQ.y + Math.sin(angle) * dist;

      const newB = {{
        id: Date.now() + Math.floor(Math.random() * 1000),
        type: type,
        name: type === 'power' ? '聚变电厂' : (type === 'refinery' ? '精炼厂' : (type === 'tesla' ? '磁暴线圈' : (type === 'prism' ? '光棱塔' : (type === 'shipyard' ? '船坞' : '轨道中继')))),
        x: bx, y: by,
        w: type === 'tesla' || type === 'prism' ? 60 : 75,
        h: type === 'tesla' || type === 'prism' ? 60 : 75,
        hp: type === 'tesla' || type === 'prism' ? 850 : 1000,
        maxHp: type === 'tesla' || type === 'prism' ? 850 : 1000,
        powerGen: type === 'power' ? 120 : 0,
        powerReq: type === 'power' ? 0 : (type === 'tesla' ? 50 : (type === 'prism' ? 40 : (type === 'shipyard' ? 40 : (type === 'refinery' ? 30 : 60)))),
        color: type === 'tesla' ? '#a855f7' : (type === 'prism' ? '#06b6d4' : (type === 'power' ? '#f59e0b' : '#38bdf8')),
        cooldown: 0
      }};

      this.buildings.push(newB);
      if (type === 'refinery') {{
        this.harvesters.push({{
          id: Date.now(), x: bx, y: by, vx: 0, vy: 0, angle: 0,
          state: 'to_ore', cargo: 0, maxCargo: 1000,
          hp: 600, maxHp: 600, speed: 2.2, targetOre: this.oreFields[0]
        }});
      }}
      if (type === 'ion') {{
        this.ionCannon.unlocked = true;
      }}

      this.updatePowerGrid();
      this.updateHUD();
      if (typeof showToast === 'function') showToast(`【${{newB.name}}】部署成功！`, 2);
    }}

    produceUnit(type, cost) {{
      const hasShipyard = this.buildings.some(b => b.type === 'shipyard' && b.hp > 0);
      if (type !== 'harvester' && !hasShipyard) {{
        if (typeof showToast === 'function') showToast('请先建造【战舰重工船坞】以制造主力战舰！', 2.5);
        return;
      }}
      if (this.credits < cost) {{
        if (typeof showToast === 'function') showToast('资金不足！需要 $' + cost, 2);
        return;
      }}
      this.credits -= cost;
      spaceAudio.playCredit();

      const spawnBase = this.buildings.find(b => b.type === 'shipyard') || this.buildings[0];
      const sx = spawnBase.x + 60;
      const sy = spawnBase.y + (Math.random() * 60 - 30);

      if (type === 'harvester') {{
        this.harvesters.push({{
          id: Date.now(), x: sx, y: sy, vx: 0, vy: 0, angle: 0,
          state: 'to_ore', cargo: 0, maxCargo: 1000,
          hp: 600, maxHp: 600, speed: 2.2, targetOre: this.oreFields[Math.floor(Math.random() * this.oreFields.length)]
        }});
      }} else {{
        const u = {{
          id: Date.now() + Math.floor(Math.random() * 1000),
          type: type,
          x: sx, y: sy, vx: 0, vy: 0, angle: 0,
          hp: type === 'dreadnought' ? 950 : (type === 'cruiser' ? 360 : 140),
          maxHp: type === 'dreadnought' ? 950 : (type === 'cruiser' ? 360 : 140),
          speed: type === 'dreadnought' ? 1.3 : (type === 'cruiser' ? 2.2 : 3.5),
          range: type === 'dreadnought' ? 240 : (type === 'cruiser' ? 300 : 180),
          dmg: type === 'dreadnought' ? 120 : (type === 'cruiser' ? 45 : 14),
          reload: 0,
          maxReload: type === 'dreadnought' ? 1.8 : (type === 'cruiser' ? 1.2 : 0.35),
          selected: false
        }};
        this.units.push(u);
      }}

      this.updateHUD();
    }}

    selectAllCombatUnits() {{
      this.selectedUnits = [...this.units];
      this.units.forEach(u => u.selected = true);
      if (typeof showToast === 'function') showToast(`已全选舰队 (${{this.units.length}} 艘战舰)`, 1.5);
    }}

    commandDefendHQ() {{
      const hq = this.buildings.find(b => b.type === 'hq') || {{ x: 450, y: 800 }};
      this.units.forEach((u, i) => {{
        const angle = (i / Math.max(1, this.units.length)) * Math.PI * 2;
        u.targetX = hq.x + Math.cos(angle) * 160;
        u.targetY = hq.y + Math.sin(angle) * 160;
        u.targetEnemy = null;
      }});
      if (typeof showToast === 'function') showToast('全军回防基地指挥所外围！', 2);
    }}

    commandAssaultRift() {{
      this.units.forEach(u => {{
        u.targetX = 2100;
        u.targetY = 800 + (Math.random() * 200 - 100);
        u.targetEnemy = this.enemies[0] || null;
      }});
      if (typeof showToast === 'function') showToast('全军突击敌军跃迁裂隙！', 2);
    }}

    armIonCannon() {{
      if (!this.ionCannon.ready) {{
        if (typeof showToast === 'function') showToast(`轨道离子炮正在充能 (${{Math.ceil(this.ionCannon.timer)}}s)...`, 2);
        return;
      }}
      this.ionCannon.targeting = true;
      if (typeof showToast === 'function') showToast('🛰️ 请轻触/点击战场指定轨道离子炮打击坐标！', 3);
    }}

    executeIonCannonStrike(wx, wy) {{
      this.ionCannon.targeting = false;
      this.ionCannon.ready = false;
      this.ionCannon.timer = this.ionCannon.maxTimer;
      document.getElementById('sf-ra-btn-ion-strike')?.classList.remove('ready');

      this.orbitalStrikes.push({{
        x: wx, y: wy,
        radius: 220,
        timer: 1.2,
        stage: 'locking'
      }});

      spaceAudio.playIonCannon();
      if (typeof showToast === 'function') showToast('⚠️ 轨道卫星锁定完成，离子光束已贯穿发射！', 3);
    }}

    applyBoxSelection() {{
      const x1 = Math.min(this.dragSelect.startX, this.dragSelect.curX);
      const y1 = Math.min(this.dragSelect.startY, this.dragSelect.curY);
      const x2 = Math.max(this.dragSelect.startX, this.dragSelect.curX);
      const y2 = Math.max(this.dragSelect.startY, this.dragSelect.curY);

      const isSingleClick = (x2 - x1 < 8 && y2 - y1 < 8);
      const wx1 = (x1 / this.camera.zoom) + this.camera.x;
      const wy1 = (y1 / this.camera.zoom) + this.camera.y;
      const wx2 = (x2 / this.camera.zoom) + this.camera.x;
      const wy2 = (y2 / this.camera.zoom) + this.camera.y;

      this.selectedUnits = [];
      this.units.forEach(u => {{
        if (isSingleClick) {{
          const d = Math.hypot(u.x - wx1, u.y - wy1);
          u.selected = (d < 30);
        }} else {{
          u.selected = (u.x >= wx1 && u.x <= wx2 && u.y >= wy1 && u.y <= wy2);
        }}
        if (u.selected) this.selectedUnits.push(u);
      }});
    }}

    issueOrder(wx, wy) {{
      if (this.selectedUnits.length === 0) return;
      // Check if target is an enemy
      const targetEnemy = this.enemies.find(e => Math.hypot(e.x - wx, e.y - wy) < 40);

      this.selectedUnits.forEach((u, idx) => {{
        if (targetEnemy) {{
          u.targetEnemy = targetEnemy;
          u.targetX = null;
        }} else {{
          u.targetEnemy = null;
          const offsetAngle = (idx / this.selectedUnits.length) * Math.PI * 2;
          const spread = Math.min(80, this.selectedUnits.length * 8);
          u.targetX = wx + Math.cos(offsetAngle) * spread;
          u.targetY = wy + Math.sin(offsetAngle) * spread;
        }}
      }});

      this.particles.push({{
        x: wx, y: wy,
        color: targetEnemy ? '#ef4444' : '#34d399',
        life: 0.4, maxLife: 0.4, radius: 24, type: 'marker'
      }});
    }}

    spawnWave() {{
      this.wave++;
      const count = 3 + this.wave * 2;
      for (let i = 0; i < count; i++) {{
        const isCruiser = (i === 0 && this.wave >= 2);
        const isDread = (i === 1 && this.wave >= 3);
        const ey = 800 + (Math.random() * 400 - 200);
        this.enemies.push({{
          id: Date.now() + i,
          type: isDread ? 'dreadnought' : (isCruiser ? 'cruiser' : 'scout'),
          x: 2150 + Math.random() * 80,
          y: ey,
          vx: 0, vy: 0, angle: Math.PI,
          hp: isDread ? 900 : (isCruiser ? 350 : 120),
          maxHp: isDread ? 900 : (isCruiser ? 350 : 120),
          speed: isDread ? 1.1 : (isCruiser ? 2.0 : 2.8),
          range: isDread ? 240 : (isCruiser ? 280 : 160),
          dmg: isDread ? 90 : (isCruiser ? 40 : 12),
          reload: 0, maxReload: isDread ? 1.8 : (isCruiser ? 1.2 : 0.4)
        }});
      }}
      this.waveTimer = 35;
      if (typeof showToast === 'function') showToast(`⚠️ 敌方舰队波次 Wave ${{this.wave}} 已跃迁入场！`, 3);
    }}

    updatePowerGrid() {{
      let gen = 0, req = 0;
      this.buildings.forEach(b => {{
        if (b.hp > 0) {{
          gen += b.powerGen;
          req += b.powerReq;
        }}
      }});
      this.powerGen = gen;
      this.powerReq = req;
      this.isLowPower = (this.powerGen < this.powerReq);
    }}

    updateHUD() {{
      const elCredits = document.getElementById('sf-ra-credits-val');
      if (elCredits) elCredits.textContent = '$' + Math.floor(this.credits).toLocaleString();

      const elPower = document.getElementById('sf-ra-power-val');
      const boxPower = document.getElementById('sf-ra-power-box');
      if (elPower) {{
        elPower.textContent = `${{this.powerGen}} / ${{this.powerReq}} MW${{this.isLowPower ? ' ⚠ LOW POWER' : ''}}`;
      }}
      if (boxPower) {{
        if (this.isLowPower) boxPower.classList.add('low');
        else boxPower.classList.remove('low');
      }}

      const elIon = document.getElementById('sf-ra-superweapon-timer');
      const btnIon = document.getElementById('sf-ra-btn-ion-strike');
      if (elIon) {{
        elIon.textContent = this.ionCannon.ready ? '已就绪 (READY)' : `充能中 ${{Math.ceil(this.ionCannon.timer)}}s`;
      }}
      if (btnIon) {{
        if (this.ionCannon.ready) btnIon.classList.add('ready');
        else btnIon.classList.remove('ready');
      }}

      const elWave = document.getElementById('sf-ra-wave-val');
      if (elWave) elWave.textContent = `Wave ${{this.wave}} (${{Math.ceil(this.waveTimer)}}s)`;
    }}

    loop(timestamp) {{
      if (!this.active) return;
      const dt = Math.min(0.1, (timestamp - (this.lastTime || timestamp)) / 1000);
      this.lastTime = timestamp;

      this.update(dt);
      this.render();

      this.animId = requestAnimationFrame((t) => this.loop(t));
    }}

    update(dt) {{
      // Wave Timer
      this.waveTimer -= dt;
      if (this.waveTimer <= 0) {{
        this.spawnWave();
      }}

      // Superweapon charge
      if (this.buildings.some(b => b.type === 'ion' && b.hp > 0)) {{
        if (!this.ionCannon.ready) {{
          this.ionCannon.timer -= dt;
          if (this.ionCannon.timer <= 0) {{
            this.ionCannon.ready = true;
            this.ionCannon.timer = 0;
          }}
        }}
      }}

      // Low Power penalty: reduce production and disable defense
      const prodSpeed = this.isLowPower ? 0.35 : 1.0;

      // 1. Harvester Loop
      for (const h of this.harvesters) {{
        if (h.hp <= 0) continue;
        if (h.state === 'to_ore') {{
          const target = h.targetOre || this.oreFields[0];
          const dx = target.x - h.x, dy = target.y - h.y;
          const dist = Math.hypot(dx, dy);
          h.angle = Math.atan2(dy, dx);
          if (dist > target.radius * 0.7) {{
            h.x += (dx / dist) * h.speed * 60 * dt;
            h.y += (dy / dist) * h.speed * 60 * dt;
          }} else {{
            h.state = 'mining';
            h.mineTimer = 0;
          }}
        }} else if (h.state === 'mining') {{
          h.cargo += 200 * dt;
          if (Math.random() < 0.3) {{
            this.particles.push({{
              x: h.x + Math.cos(h.angle) * 20,
              y: h.y + Math.sin(h.angle) * 20,
              vx: (Math.random() - 0.5) * 30,
              vy: (Math.random() - 0.5) * 30,
              color: '#34d399', life: 0.3, maxLife: 0.3, radius: 2
            }});
          }}
          if (h.cargo >= h.maxCargo) {{
            h.cargo = h.maxCargo;
            h.state = 'to_refinery';
          }}
        }} else if (h.state === 'to_refinery') {{
          const ref = this.buildings.find(b => b.type === 'refinery' && b.hp > 0) || this.buildings[0];
          const dx = ref.x - h.x, dy = ref.y - h.y;
          const dist = Math.hypot(dx, dy);
          h.angle = Math.atan2(dy, dx);
          if (dist > 30) {{
            h.x += (dx / dist) * h.speed * 60 * dt;
            h.y += (dy / dist) * h.speed * 60 * dt;
          }} else {{
            h.state = 'unloading';
            h.unloadTimer = 1.0;
          }}
        }} else if (h.state === 'unloading') {{
          h.unloadTimer -= dt;
          if (h.unloadTimer <= 0) {{
            this.credits += 500;
            spaceAudio.playCredit();
            this.particles.push({{
              x: h.x, y: h.y - 20,
              text: '+$500', color: '#34d399', life: 1.0, maxLife: 1.0, type: 'floatText'
            }});
            h.cargo = 0;
            h.state = 'to_ore';
          }}
        }}
      }}

      // 2. Defense Towers (Tesla & Prism)
      for (const b of this.buildings) {{
        if (b.hp <= 0) continue;
        if (b.type === 'tesla' && !this.isLowPower) {{
          b.cooldown = Math.max(0, (b.cooldown || 0) - dt);
          const range = (this.powerGen - this.powerReq > 50) ? 360 : 280;
          const target = this.enemies.find(e => Math.hypot(e.x - b.x, e.y - b.y) < range);
          if (target && b.cooldown <= 0) {{
            b.cooldown = (this.powerGen - this.powerReq > 50) ? 0.7 : 1.1;
            const dmg = (this.powerGen - this.powerReq > 50) ? 130 : 75;
            target.hp -= dmg;
            spaceAudio.playTeslaZap();
            this.particles.push({{
              type: 'lightning',
              x1: b.x, y1: b.y - 20,
              x2: target.x, y2: target.y,
              color: '#c084fc', life: 0.25, maxLife: 0.25
            }});
          }}
        }} else if (b.type === 'prism' && !this.isLowPower) {{
          b.cooldown = Math.max(0, (b.cooldown || 0) - dt);
          const range = 320;
          const target = this.enemies.find(e => Math.hypot(e.x - b.x, e.y - b.y) < range);
          if (target && b.cooldown <= 0) {{
            b.cooldown = 1.0;
            // Count neighboring prism towers to amplify beam!
            const prisms = this.buildings.filter(pb => pb.type === 'prism' && pb.hp > 0 && Math.hypot(pb.x - b.x, pb.y - b.y) < 260);
            const dmg = 60 + (prisms.length - 1) * 35;
            target.hp -= dmg;
            spaceAudio.playLaser();
            this.particles.push({{
              type: 'prismBeam',
              x1: b.x, y1: b.y - 24,
              x2: target.x, y2: target.y,
              color: '#38bdf8', life: 0.3, maxLife: 0.3, width: 3 + prisms.length * 1.5
            }});
          }}
        }}
      }}

      // 3. Player Units
      for (const u of this.units) {{
        if (u.hp <= 0) continue;
        u.reload = Math.max(0, u.reload - dt);

        if (u.targetEnemy && u.targetEnemy.hp > 0) {{
          const dx = u.targetEnemy.x - u.x, dy = u.targetEnemy.y - u.y;
          const dist = Math.hypot(dx, dy);
          u.angle = Math.atan2(dy, dx);
          if (dist > u.range * 0.8) {{
            u.x += (dx / dist) * u.speed * 60 * dt;
            u.y += (dy / dist) * u.speed * 60 * dt;
          }} else if (u.reload <= 0) {{
            u.reload = u.maxReload;
            u.targetEnemy.hp -= u.dmg;
            spaceAudio.playLaser();
            this.particles.push({{
              type: 'tracer',
              x1: u.x, y1: u.y,
              x2: u.targetEnemy.x, y2: u.targetEnemy.y,
              color: u.type === 'dreadnought' ? '#f59e0b' : '#38bdf8',
              life: 0.15, maxLife: 0.15
            }});
          }}
        }} else if (u.targetX !== null && u.targetY !== null) {{
          const dx = u.targetX - u.x, dy = u.targetY - u.y;
          const dist = Math.hypot(dx, dy);
          if (dist > 15) {{
            u.angle = Math.atan2(dy, dx);
            u.x += (dx / dist) * u.speed * 60 * dt;
            u.y += (dy / dist) * u.speed * 60 * dt;
          }} else {{
            u.targetX = null; u.targetY = null;
          }}
        }} else {{
          // Auto-acquire nearest enemy
          const enemy = this.enemies.find(e => Math.hypot(e.x - u.x, e.y - u.y) < u.range);
          if (enemy && u.reload <= 0) {{
            u.reload = u.maxReload;
            enemy.hp -= u.dmg;
            spaceAudio.playLaser();
            this.particles.push({{
              type: 'tracer',
              x1: u.x, y1: u.y,
              x2: enemy.x, y2: enemy.y,
              color: u.type === 'dreadnought' ? '#f59e0b' : '#38bdf8',
              life: 0.15, maxLife: 0.15
            }});
          }}
        }}
      }}

      // 4. Enemy Units
      for (const e of this.enemies) {{
        if (e.hp <= 0) continue;
        e.reload = Math.max(0, e.reload - dt);

        // Find closest target: harvester, defense tower, or unit
        let closestTarget = this.harvesters.find(h => h.hp > 0 && Math.hypot(h.x - e.x, h.y - e.y) < 350)
          || this.buildings.find(b => b.hp > 0 && Math.hypot(b.x - e.x, b.y - e.y) < 400)
          || this.units.find(u => u.hp > 0 && Math.hypot(u.x - e.x, u.y - e.y) < 350)
          || this.buildings[0];

        if (closestTarget) {{
          const dx = closestTarget.x - e.x, dy = closestTarget.y - e.y;
          const dist = Math.hypot(dx, dy);
          e.angle = Math.atan2(dy, dx);
          if (dist > e.range * 0.75) {{
            e.x += (dx / dist) * e.speed * 60 * dt;
            e.y += (dy / dist) * e.speed * 60 * dt;
          }} else if (e.reload <= 0) {{
            e.reload = e.maxReload;
            closestTarget.hp -= e.dmg;
            spaceAudio.playLaser();
            this.particles.push({{
              type: 'tracer',
              x1: e.x, y1: e.y,
              x2: closestTarget.x, y2: closestTarget.y,
              color: '#ef4444', life: 0.15, maxLife: 0.15
            }});
          }}
        }}
      }}

      // 5. Clean up dead entities & explosions
      for (let i = this.enemies.length - 1; i >= 0; i--) {{
        if (this.enemies[i].hp <= 0) {{
          spaceAudio.playExplosion();
          this.createExplosion(this.enemies[i].x, this.enemies[i].y, 30);
          this.credits += (this.enemies[i].type === 'dreadnought' ? 400 : 80);
          this.enemies.splice(i, 1);
        }}
      }}
      for (let i = this.units.length - 1; i >= 0; i--) {{
        if (this.units[i].hp <= 0) {{
          spaceAudio.playExplosion();
          this.createExplosion(this.units[i].x, this.units[i].y, 25);
          this.units.splice(i, 1);
        }}
      }}

      // 6. Orbital Strikes (Ion Cannon)
      for (let i = this.orbitalStrikes.length - 1; i >= 0; i--) {{
        const s = this.orbitalStrikes[i];
        s.timer -= dt;
        if (s.stage === 'locking' && s.timer <= 0) {{
          s.stage = 'blast';
          s.timer = 0.8;
          this.shake = 18;
          // Apply massive AOE damage
          this.enemies.forEach(e => {{
            if (Math.hypot(e.x - s.x, e.y - s.y) < s.radius) {{
              e.hp -= 850;
            }}
          }});
          this.createExplosion(s.x, s.y, 80);
        }} else if (s.stage === 'blast' && s.timer <= 0) {{
          this.orbitalStrikes.splice(i, 1);
        }}
      }}

      // 7. Update Particles
      for (let i = this.particles.length - 1; i >= 0; i--) {{
        const pt = this.particles[i];
        pt.life -= dt;
        if (pt.vx) pt.x += pt.vx * dt;
        if (pt.vy) pt.y += pt.vy * dt;
        if (pt.life <= 0) this.particles.splice(i, 1);
      }}

      this.shake = Math.max(0, this.shake - dt * 30);
      this.updatePowerGrid();
      this.updateHUD();
    }}

    createExplosion(x, y, radius) {{
      for (let i = 0; i < 18; i++) {{
        const a = Math.random() * Math.PI * 2;
        const sp = 40 + Math.random() * 100;
        this.particles.push({{
          x: x, y: y,
          vx: Math.cos(a) * sp,
          vy: Math.sin(a) * sp,
          color: Math.random() < 0.5 ? '#f59e0b' : '#ef4444',
          life: 0.4 + Math.random() * 0.3,
          maxLife: 0.7,
          radius: 3 + Math.random() * 4
        }});
      }}
    }}

    render() {{
      const ctx = this.ctx;
      const w = this.canvas.width;
      const h = this.canvas.height;
      ctx.clearRect(0, 0, w, h);

      ctx.save();
      if (this.shake > 0) {{
        ctx.translate((Math.random() - 0.5) * this.shake, (Math.random() - 0.5) * this.shake);
      }}
      ctx.scale(this.camera.zoom, this.camera.zoom);
      ctx.translate(-this.camera.x, -this.camera.y);

      // 1. Tactical Grid & Background Nebula
      ctx.strokeStyle = 'rgba(56, 189, 248, 0.05)';
      ctx.lineWidth = 1;
      const gridSize = 100;
      for (let x = 0; x <= this.worldWidth; x += gridSize) {{
        ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, this.worldHeight); ctx.stroke();
      }}
      for (let y = 0; y <= this.worldHeight; y += gridSize) {{
        ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(this.worldWidth, y); ctx.stroke();
      }}

      // 2. Ore Fields (Asteroid Crystals)
      for (const f of this.oreFields) {{
        ctx.save();
        ctx.fillStyle = 'rgba(15, 23, 42, 0.85)';
        ctx.strokeStyle = f.color;
        ctx.lineWidth = 1.5;
        ctx.beginPath();
        ctx.arc(f.x, f.y, f.radius, 0, Math.PI * 2);
        ctx.fill(); ctx.stroke();

        // Glowing crystals
        for (let i = 0; i < 8; i++) {{
          const a = (i / 8) * Math.PI * 2;
          const cx = f.x + Math.cos(a) * (f.radius * 0.55);
          const cy = f.y + Math.sin(a) * (f.radius * 0.55);
          ctx.fillStyle = f.color;
          ctx.beginPath();
          ctx.arc(cx, cy, 5, 0, Math.PI * 2);
          ctx.fill();
        }}
        ctx.fillStyle = '#94a3b8';
        ctx.font = '11px ui-monospace, monospace';
        ctx.textAlign = 'center';
        ctx.fillText(`矿石蕴藏量: ${{f.ore}}`, f.x, f.y + f.radius + 16);
        ctx.restore();
      }}

      // 3. Enemy Hyperspace Rift
      ctx.save();
      const riftPulse = Math.sin(performance.now() * 0.004) * 10;
      const riftGrad = ctx.createRadialGradient(2150, 800, 10, 2150, 800, 120 + riftPulse);
      riftGrad.addColorStop(0, '#ffffff');
      riftGrad.addColorStop(0.3, '#ec4899');
      riftGrad.addColorStop(0.7, '#7c3aed');
      riftGrad.addColorStop(1, 'transparent');
      ctx.fillStyle = riftGrad;
      ctx.beginPath();
      ctx.arc(2150, 800, 120 + riftPulse, 0, Math.PI * 2);
      ctx.fill();
      ctx.fillStyle = '#f87171';
      ctx.font = 'bold 12px ui-monospace, monospace';
      ctx.textAlign = 'center';
      ctx.fillText('⚡ 敌军超空间跳跃裂隙', 2150, 800 + 150);
      ctx.restore();

      // 4. Buildings
      for (const b of this.buildings) {{
        ctx.save();
        ctx.translate(b.x, b.y);

        // Building base
        ctx.fillStyle = '#0f172a';
        ctx.strokeStyle = b.color;
        ctx.lineWidth = 2;
        ctx.fillRect(-b.w / 2, -b.h / 2, b.w, b.h);
        ctx.strokeRect(-b.w / 2, -b.h / 2, b.w, b.h);

        // Building internals
        if (b.type === 'tesla') {{
          // Tesla Coil
          ctx.strokeStyle = '#c084fc';
          ctx.lineWidth = 2;
          ctx.beginPath();
          ctx.arc(0, 0, 14, 0, Math.PI * 2);
          ctx.arc(0, 0, 8, 0, Math.PI * 2);
          ctx.stroke();
          // Glowing top orb
          ctx.fillStyle = this.isLowPower ? '#64748b' : '#e9d5ff';
          ctx.beginPath(); ctx.arc(0, -18, 6, 0, Math.PI * 2); ctx.fill();
        }} else if (b.type === 'prism') {{
          // Prism Tower
          ctx.fillStyle = this.isLowPower ? '#64748b' : '#38bdf8';
          ctx.beginPath();
          ctx.moveTo(0, -22); ctx.lineTo(12, 12); ctx.lineTo(-12, 12);
          ctx.closePath();
          ctx.fill();
        }} else {{
          ctx.fillStyle = b.color;
          ctx.fillRect(-b.w * 0.3, -b.h * 0.3, b.w * 0.6, b.h * 0.6);
        }}

        // Health bar
        const hpRatio = Math.max(0, b.hp / b.maxHp);
        ctx.fillStyle = 'rgba(0,0,0,0.6)';
        ctx.fillRect(-25, -b.h / 2 - 12, 50, 5);
        ctx.fillStyle = hpRatio > 0.4 ? '#34d399' : '#f43f5e';
        ctx.fillRect(-25, -b.h / 2 - 12, 50 * hpRatio, 5);

        // Title
        ctx.fillStyle = '#f8fafc';
        ctx.font = '10px ui-monospace, monospace';
        ctx.textAlign = 'center';
        ctx.fillText(b.name, 0, b.h / 2 + 14);
        ctx.restore();
      }}

      // 5. Harvesters
      for (const h of this.harvesters) {{
        ctx.save();
        ctx.translate(h.x, h.y);
        ctx.rotate(h.angle);
        ctx.fillStyle = '#f59e0b';
        ctx.fillRect(-18, -12, 36, 24);
        ctx.strokeStyle = '#f8fafc';
        ctx.lineWidth = 1.5;
        ctx.strokeRect(-18, -12, 36, 24);

        // Mining beam when mining
        if (h.state === 'mining') {{
          ctx.strokeStyle = '#34d399';
          ctx.lineWidth = 3;
          ctx.beginPath();
          ctx.moveTo(18, 0); ctx.lineTo(45, 0);
          ctx.stroke();
        }}
        ctx.restore();
      }}

      // 6. Combat Ships (Units & Enemies)
      for (const u of this.units) {{
        ctx.save();
        ctx.translate(u.x, u.y);
        ctx.rotate(u.angle);

        // Selection ring
        if (u.selected) {{
          ctx.strokeStyle = '#38bdf8';
          ctx.lineWidth = 1.5;
          ctx.beginPath(); ctx.arc(0, 0, 22, 0, Math.PI * 2); ctx.stroke();
        }}

        // Hull shape
        ctx.fillStyle = u.type === 'dreadnought' ? '#1e293b' : '#0284c7';
        ctx.strokeStyle = '#38bdf8';
        ctx.lineWidth = 1.5;
        ctx.beginPath();
        if (u.type === 'dreadnought') {{
          ctx.moveTo(24, 0); ctx.lineTo(-18, 16); ctx.lineTo(-12, 0); ctx.lineTo(-18, -16);
        }} else {{
          ctx.moveTo(16, 0); ctx.lineTo(-12, 10); ctx.lineTo(-8, 0); ctx.lineTo(-12, -10);
        }}
        ctx.closePath();
        ctx.fill(); ctx.stroke();
        ctx.restore();
      }}

      for (const e of this.enemies) {{
        ctx.save();
        ctx.translate(e.x, e.y);
        ctx.rotate(e.angle);
        ctx.fillStyle = '#881337';
        ctx.strokeStyle = '#f43f5e';
        ctx.lineWidth = 1.5;
        ctx.beginPath();
        ctx.moveTo(18, 0); ctx.lineTo(-14, 12); ctx.lineTo(-8, 0); ctx.lineTo(-14, -12);
        ctx.closePath();
        ctx.fill(); ctx.stroke();
        ctx.restore();
      }}

      // 7. Beams & Projectiles & Strikes
      for (const pt of this.particles) {{
        if (pt.type === 'lightning') {{
          ctx.strokeStyle = pt.color;
          ctx.lineWidth = 2.5;
          ctx.beginPath();
          ctx.moveTo(pt.x1, pt.y1);
          const midX = (pt.x1 + pt.x2) / 2 + (Math.random() - 0.5) * 40;
          const midY = (pt.y1 + pt.y2) / 2 + (Math.random() - 0.5) * 40;
          ctx.lineTo(midX, midY);
          ctx.lineTo(pt.x2, pt.y2);
          ctx.stroke();
        }} else if (pt.type === 'prismBeam') {{
          ctx.strokeStyle = pt.color;
          ctx.lineWidth = pt.width;
          ctx.beginPath(); ctx.moveTo(pt.x1, pt.y1); ctx.lineTo(pt.x2, pt.y2); ctx.stroke();
        }} else if (pt.type === 'tracer') {{
          ctx.strokeStyle = pt.color;
          ctx.lineWidth = 2;
          ctx.beginPath(); ctx.moveTo(pt.x1, pt.y1); ctx.lineTo(pt.x2, pt.y2); ctx.stroke();
        }} else if (pt.type === 'floatText') {{
          ctx.fillStyle = pt.color;
          ctx.font = 'bold 13px ui-monospace, monospace';
          ctx.fillText(pt.text, pt.x, pt.y);
        }} else {{
          ctx.fillStyle = pt.color;
          ctx.beginPath(); ctx.arc(pt.x, pt.y, pt.radius || 2, 0, Math.PI * 2); ctx.fill();
        }}
      }}

      // 8. Orbital Strikes (Ion Cannon blast)
      for (const s of this.orbitalStrikes) {{
        if (s.stage === 'locking') {{
          ctx.strokeStyle = '#f43f5e';
          ctx.lineWidth = 2;
          ctx.beginPath(); ctx.arc(s.x, s.y, s.radius * (s.timer / 1.2), 0, Math.PI * 2); ctx.stroke();
          ctx.beginPath(); ctx.moveTo(s.x - 30, s.y); ctx.lineTo(s.x + 30, s.y); ctx.stroke();
          ctx.beginPath(); ctx.moveTo(s.x, s.y - 30); ctx.lineTo(s.x, s.y + 30); ctx.stroke();
        }} else if (s.stage === 'blast') {{
          // Massive Orbital Pillar of Light
          const grad = ctx.createLinearGradient(s.x - 40, s.y, s.x + 40, s.y);
          grad.addColorStop(0, 'rgba(56, 189, 248, 0)');
          grad.addColorStop(0.5, '#ffffff');
          grad.addColorStop(1, 'rgba(56, 189, 248, 0)');
          ctx.fillStyle = grad;
          ctx.fillRect(s.x - 50, -500, 100, s.y + 500);

          // Impact shockwave
          ctx.strokeStyle = '#38bdf8';
          ctx.lineWidth = 4;
          ctx.beginPath(); ctx.arc(s.x, s.y, s.radius, 0, Math.PI * 2); ctx.stroke();
        }}
      }}

      // 9. Box Selection Rectangle
      if (this.dragSelect.active) {{
        const wx1 = (this.dragSelect.startX / this.camera.zoom) + this.camera.x;
        const wy1 = (this.dragSelect.startY / this.camera.zoom) + this.camera.y;
        const wx2 = (this.dragSelect.curX / this.camera.zoom) + this.camera.x;
        const wy2 = (this.dragSelect.curY / this.camera.zoom) + this.camera.y;
        ctx.fillStyle = 'rgba(56, 189, 248, 0.15)';
        ctx.strokeStyle = '#38bdf8';
        ctx.lineWidth = 1;
        ctx.fillRect(wx1, wy1, wx2 - wx1, wy2 - wy1);
        ctx.strokeRect(wx1, wy1, wx2 - wx1, wy2 - wy1);
      }}

      ctx.restore();
    }}
  }}

  window.RedAlertRTS = new RedAlertRTSGame();

  /* =========================================================================
   * 5. DYSON SPHERE PROGRAM ENGINE (戴森球计划 · 星系工程)
   * ========================================================================= */
  class DysonSphereGame {{
    constructor() {{
      this.canvas = document.getElementById('sf-dyson-canvas');
      this.ctx = this.canvas.getContext('2d');
      this.active = false;
      this.animId = null;

      this.camera = {{
        pitch: 0.48,
        yaw: 0.65,
        zoom: 1.0,
        mode: 'system'
      }};

      this.star = {{
        radius: 65,
        luminosity: 2.14,
        pulsePhase: 0
      }};

      this.solarSails = [];
      this.nodes = [];
      this.struts = [];
      this.shells = [];
      this.rockets = [];
      this.conveyorItems = [];
      this.interstellarFreighters = [];

      this.universeMatrix = 150;
      this.totalPowerGW = 1.82;
      this.techLevels = {{ em: 0, sail: 0, rocket: 0, lens: 0, shell: 0 }};

      this.planets = [
        {{ name: 'Gaia Prime (母星)', radius: 32, dist: 310, angle: 0.5, speed: 0.003, color: '#38bdf8', isMother: true }},
        {{ name: 'Vulcan (钛矿星)', radius: 24, dist: 510, angle: 2.2, speed: 0.0018, color: '#f97316' }},
        {{ name: 'Zephyr (气态巨星)', radius: 48, dist: 740, angle: 4.0, speed: 0.0009, color: '#a855f7', hasRings: true }}
      ];

      this.dragState = {{ isDragging: false, lastX: 0, lastY: 0 }};

      this.initGeodesicSphere();
      this.initInitialSwarm();
      this.bindEvents();
    }}

    initGeodesicSphere() {{
      // 3D Geodesic Icosahedron Frame around Star
      const phi = (1 + Math.sqrt(5)) / 2;
      const baseVertices = [
        [-1,  phi, 0], [ 1,  phi, 0], [-1, -phi, 0], [ 1, -phi, 0],
        [ 0, -1,  phi], [ 0,  1,  phi], [ 0, -1, -phi], [ 0,  1, -phi],
        [ phi, 0, -1], [ phi, 0,  1], [-phi, 0, -1], [-phi, 0,  1]
      ];

      const R = 150;
      this.nodes = baseVertices.map((v, i) => {{
        const len = Math.hypot(v[0], v[1], v[2]);
        return {{
          id: i,
          x: (v[0] / len) * R,
          y: (v[1] / len) * R,
          z: (v[2] / len) * R,
          built: i < 8 // 8 built initially (25%)
        }};
      }});

      // Add subdivided midpoints to make 32 total nodes
      for (let i = 0; i < 20; i++) {{
        const a = this.nodes[i % 12];
        const b = this.nodes[(i + 1) % 12];
        const mx = (a.x + b.x) / 2;
        const my = (a.y + b.y) / 2;
        const mz = (a.z + b.z) / 2;
        const len = Math.hypot(mx, my, mz);
        this.nodes.push({{
          id: 12 + i,
          x: (mx / len) * R,
          y: (my / len) * R,
          z: (mz / len) * R,
          built: false
        }});
      }}
    }}

    initInitialSwarm() {{
      // Initial 120 solar sails orbiting in Keplerian rings
      for (let i = 0; i < 120; i++) {{
        this.solarSails.push({{
          ring: i % 3,
          angle: Math.random() * Math.PI * 2,
          speed: 0.008 + Math.random() * 0.006,
          radius: 200 + (i % 3) * 60,
          inclination: (i % 3 === 0 ? 0.25 : (i % 3 === 1 ? 0.65 : -0.45)),
          life: 90 + Math.random() * 30
        }});
      }}
    }}

    start() {{
      this.resize();
      this.active = true;
      this.lastTime = performance.now();
      this.animId = requestAnimationFrame((t) => this.loop(t));
      this.updateHUD();
    }}

    stop() {{
      this.active = false;
      if (this.animId) cancelAnimationFrame(this.animId);
    }}

    resize() {{
      this.canvas.width = window.innerWidth;
      this.canvas.height = window.innerHeight;
    }}

    bindEvents() {{
      window.addEventListener('resize', () => {{ if (this.active) this.resize(); }});

      document.getElementById('sf-dsp-btn-launch-sail')?.addEventListener('click', () => this.launchSolarSails());
      document.getElementById('sf-dsp-btn-launch-rocket')?.addEventListener('click', () => this.launchCarrierRocket());
      document.getElementById('sf-dsp-btn-tech-modal')?.addEventListener('click', () => this.toggleTechModal(true));
      document.getElementById('sf-dsp-close-tech-btn')?.addEventListener('click', () => this.toggleTechModal(false));
      document.getElementById('sf-dsp-btn-cam-view')?.addEventListener('click', () => this.cycleCameraView());

      // Tech upgrade buttons
      document.getElementById('sf-dsp-btn-upgrade-em')?.addEventListener('click', () => this.upgradeTech('em', 100));
      document.getElementById('sf-dsp-btn-upgrade-sail')?.addEventListener('click', () => this.upgradeTech('sail', 150));
      document.getElementById('sf-dsp-btn-upgrade-rocket')?.addEventListener('click', () => this.upgradeTech('rocket', 250));
      document.getElementById('sf-dsp-btn-upgrade-lens')?.addEventListener('click', () => this.upgradeTech('lens', 350));
      document.getElementById('sf-dsp-btn-upgrade-shell')?.addEventListener('click', () => this.upgradeTech('shell', 500));

      // 3D Canvas Touch & Drag
      const c = this.canvas;
      c.addEventListener('mousedown', (e) => {{
        this.dragState.isDragging = true;
        this.dragState.lastX = e.clientX;
        this.dragState.lastY = e.clientY;
      }});

      window.addEventListener('mousemove', (e) => {{
        if (!this.active || !this.dragState.isDragging) return;
        const dx = e.clientX - this.dragState.lastX;
        const dy = e.clientY - this.dragState.lastY;
        this.camera.yaw += dx * 0.005;
        this.camera.pitch = Math.max(-0.2, Math.min(1.4, this.camera.pitch + dy * 0.005));
        this.dragState.lastX = e.clientX;
        this.dragState.lastY = e.clientY;
      }});

      window.addEventListener('mouseup', () => {{ this.dragState.isDragging = false; }});

      c.addEventListener('wheel', (e) => {{
        if (!this.active) return;
        e.preventDefault();
        const factor = e.deltaY < 0 ? 1.08 : 0.92;
        this.camera.zoom = Math.max(0.45, Math.min(2.5, this.camera.zoom * factor));
      }}, {{ passive: false }});

      c.addEventListener('touchstart', (e) => {{
        if (e.touches.length === 1) {{
          this.dragState.isDragging = true;
          this.dragState.lastX = e.touches[0].clientX;
          this.dragState.lastY = e.touches[0].clientY;
        }}
      }}, {{ passive: false }});

      c.addEventListener('touchmove', (e) => {{
        if (!this.active || !this.dragState.isDragging || e.touches.length !== 1) return;
        const dx = e.touches[0].clientX - this.dragState.lastX;
        const dy = e.touches[0].clientY - this.dragState.lastY;
        this.camera.yaw += dx * 0.006;
        this.camera.pitch = Math.max(-0.2, Math.min(1.4, this.camera.pitch + dy * 0.006));
        this.dragState.lastX = e.touches[0].clientX;
        this.dragState.lastY = e.touches[0].clientY;
      }}, {{ passive: false }});

      c.addEventListener('touchend', () => {{ this.dragState.isDragging = false; }});
    }}

    launchSolarSails() {{
      const count = 3 + this.techLevels.em * 3;
      for (let i = 0; i < count; i++) {{
        this.solarSails.push({{
          ring: Math.floor(Math.random() * 3),
          angle: Math.random() * Math.PI * 2,
          speed: 0.008 + Math.random() * 0.006,
          radius: 200 + (Math.floor(Math.random() * 3)) * 60,
          inclination: Math.random() * 0.8 - 0.4,
          life: (90 + Math.random() * 30) * (1 + this.techLevels.sail * 0.5)
        }});
      }}
      spaceAudio.playSailLaunch();
      if (typeof showToast === 'function') showToast(`⚡ 电磁弹射齐射！${{count}} 枚太阳帆注入戴森云！`, 2);
    }}

    launchCarrierRocket() {{
      const targetNode = this.nodes.find(n => !n.built);
      if (!targetNode) {{
        if (typeof showToast === 'function') showToast('戴森球骨架已 100% 构筑完成！正在以全功率汲取恒星能量！', 2.5);
        return;
      }}

      this.rockets.push({{
        x: 310, y: 0, z: 0,
        progress: 0,
        targetNode: targetNode
      }});
      spaceAudio.playRocketLaunch();
      if (typeof showToast === 'function') showToast('🚀 垂直发射井点火！小型运载火箭正飞往戴森球骨架节点！', 2);
    }}

    cycleCameraView() {{
      if (this.camera.mode === 'system') {{
        this.camera.mode = 'planet';
        this.camera.zoom = 1.6;
        this.camera.pitch = 0.6;
        if (typeof showToast === 'function') showToast('视角：母星行星表面物流基建 🪐', 2);
      }} else if (this.camera.mode === 'planet') {{
        this.camera.mode = 'sphere';
        this.camera.zoom = 1.25;
        this.camera.pitch = 0.35;
        if (typeof showToast === 'function') showToast('视角：戴森球骨架透射总览 ☀️', 2);
      }} else {{
        this.camera.mode = 'system';
        this.camera.zoom = 0.85;
        this.camera.pitch = 0.52;
        if (typeof showToast === 'function') showToast('视角：恒星系全景 🌌', 2);
      }}
    }}

    toggleTechModal(open) {{
      const m = document.getElementById('sf-dsp-tech-modal');
      if (m) {{
        if (open) m.classList.add('active');
        else m.classList.remove('active');
      }}
    }}

    upgradeTech(key, cost) {{
      if (this.universeMatrix < cost) {{
        if (typeof showToast === 'function') showToast(`宇宙矩阵不足！需要 ${{cost}} 白糖`, 2);
        return;
      }}
      this.universeMatrix -= cost;
      this.techLevels[key] = (this.techLevels[key] || 0) + 1;
      spaceAudio.playCredit();

      const spanLvl = document.getElementById(`sf-dsp-tech-lvl-${{key}}`);
      if (spanLvl) spanLvl.textContent = `Lv.${{this.techLevels[key]}}`;

      this.updateHUD();
      if (typeof showToast === 'function') showToast('🎉 宇宙矩阵科技升级成功！', 2);
    }}

    updateHUD() {{
      const builtCount = this.nodes.filter(n => n.built).length;
      const pct = Math.round((builtCount / this.nodes.length) * 100);

      const elLum = document.getElementById('sf-dsp-val-lum');
      if (elLum) elLum.textContent = `${{this.star.luminosity}} L☉ (O型耀星)`;

      const elSails = document.getElementById('sf-dsp-val-sails');
      const swarmMW = Math.round(this.solarSails.length * 1.8 * this.star.luminosity);
      if (elSails) elSails.textContent = `${{this.solarSails.length}} 帆 (${{swarmMW}} MW)`;

      const elNodes = document.getElementById('sf-dsp-val-nodes');
      if (elNodes) elNodes.textContent = `${{builtCount}} / ${{this.nodes.length}} 节点 (${{pct}}%)`;

      const barFill = document.getElementById('sf-dsp-node-progress-fill');
      if (barFill) barFill.style.width = `${{pct}}%`;

      this.totalPowerGW = Number(((swarmMW / 1000) + (builtCount * 0.18 * this.star.luminosity)).toFixed(2));
      const elPower = document.getElementById('sf-dsp-val-total-gw');
      if (elPower) elPower.textContent = `${{this.totalPowerGW}} GW`;

      const elMatrix = document.getElementById('sf-dsp-val-matrix');
      if (elMatrix) elMatrix.textContent = `${{Math.floor(this.universeMatrix)}} 矩阵`;
    }}

    loop(timestamp) {{
      if (!this.active) return;
      const dt = Math.min(0.1, (timestamp - (this.lastTime || timestamp)) / 1000);
      this.lastTime = timestamp;

      this.update(dt);
      this.render();

      this.animId = requestAnimationFrame((t) => this.loop(t));
    }}

    update(dt) {{
      // Universe Matrix synthesis from Ray Receivers
      const lensMult = 1 + (this.techLevels.lens || 0) * 1.5;
      this.universeMatrix += (0.8 + this.totalPowerGW * 0.4) * lensMult * dt;

      // Update planets orbit
      for (const p of this.planets) {{
        p.angle += p.speed * 60 * dt;
      }}

      // Update solar sails in Dyson Swarm
      for (let i = this.solarSails.length - 1; i >= 0; i--) {{
        const s = this.solarSails[i];
        s.angle += s.speed * 60 * dt;
        s.life -= dt;
        if (s.life <= 0) {{
          this.solarSails.splice(i, 1);
        }}
      }}

      // Update Rockets in transit
      for (let i = this.rockets.length - 1; i >= 0; i--) {{
        const r = this.rockets[i];
        r.progress += 0.8 * dt;
        if (r.progress >= 1.0) {{
          r.targetNode.built = true;
          spaceAudio.playCredit();
          if (this.techLevels.rocket > 0) {{
            const nextNode = this.nodes.find(n => !n.built);
            if (nextNode) nextNode.built = true;
          }}
          this.rockets.splice(i, 1);
        }}
      }}

      // Auto-launch minor solar sails
      if (Math.random() < 0.05 + this.techLevels.em * 0.04) {{
        this.solarSails.push({{
          ring: Math.floor(Math.random() * 3),
          angle: 0,
          speed: 0.008 + Math.random() * 0.006,
          radius: 200 + (Math.floor(Math.random() * 3)) * 60,
          inclination: Math.random() * 0.8 - 0.4,
          life: 90 * (1 + this.techLevels.sail * 0.5)
        }});
      }}

      this.updateHUD();
    }}

    project3D(x, y, z, cx, cy) {{
      const cosY = Math.cos(this.camera.yaw);
      const sinY = Math.sin(this.camera.yaw);
      const x1 = x * cosY - z * sinY;
      const z1 = x * sinY + z * cosY;

      const cosP = Math.cos(this.camera.pitch);
      const sinP = Math.sin(this.camera.pitch);
      const y2 = y * cosP - z1 * sinP;
      const z2 = y * sinP + z1 * cosP;

      const dist = 1000;
      const scale = (dist / (dist + z2)) * this.camera.zoom;
      return {{
        x: cx + x1 * scale,
        y: cy + y2 * scale,
        scale: scale,
        z: z2
      }};
    }}

    render() {{
      const ctx = this.ctx;
      const w = this.canvas.width;
      const h = this.canvas.height;
      const cx = w / 2;
      const cy = h / 2;
      ctx.clearRect(0, 0, w, h);

      // 1. Central Star (Luminescent O-Type Sun)
      const starProj = this.project3D(0, 0, 0, cx, cy);
      const starR = this.star.radius * starProj.scale;

      const grad = ctx.createRadialGradient(starProj.x, starProj.y, starR * 0.2, starProj.x, starProj.y, starR * 2.2);
      grad.addColorStop(0, '#ffffff');
      grad.addColorStop(0.3, '#fef08a');
      grad.addColorStop(0.7, '#f59e0b');
      grad.addColorStop(1, 'transparent');

      ctx.fillStyle = grad;
      ctx.beginPath();
      ctx.arc(starProj.x, starProj.y, starR * 2.2, 0, Math.PI * 2);
      ctx.fill();

      // 2. Geodesic Dyson Sphere Frame Struts & Nodes
      for (const n of this.nodes) {{
        n.proj = this.project3D(n.x, n.y, n.z, cx, cy);
      }}

      // Draw Struts
      ctx.lineWidth = 1.2;
      for (let i = 0; i < this.nodes.length; i++) {{
        const n1 = this.nodes[i];
        for (let j = i + 1; j < this.nodes.length; j++) {{
          const n2 = this.nodes[j];
          const dist = Math.hypot(n1.x - n2.x, n1.y - n2.y, n1.z - n2.z);
          if (dist < 130) {{
            const bothBuilt = (n1.built && n2.built);
            ctx.strokeStyle = bothBuilt ? 'rgba(56, 189, 248, 0.65)' : 'rgba(255, 255, 255, 0.12)';
            ctx.beginPath();
            ctx.moveTo(n1.proj.x, n1.proj.y);
            ctx.lineTo(n2.proj.x, n2.proj.y);
            ctx.stroke();

            // Shell panel glow if built
            if (bothBuilt) {{
              ctx.fillStyle = 'rgba(56, 189, 248, 0.08)';
              ctx.beginPath();
              ctx.moveTo(starProj.x, starProj.y);
              ctx.lineTo(n1.proj.x, n1.proj.y);
              ctx.lineTo(n2.proj.x, n2.proj.y);
              ctx.fill();
            }}
          }}
        }}
      }}

      // Draw Nodes
      for (const n of this.nodes) {{
        ctx.fillStyle = n.built ? '#38bdf8' : 'rgba(255, 255, 255, 0.3)';
        ctx.beginPath();
        ctx.arc(n.proj.x, n.proj.y, (n.built ? 5 : 2.5) * n.proj.scale, 0, Math.PI * 2);
        ctx.fill();
      }}

      // 3. Dyson Swarm (Solar Sails Orbiting in 3D Keplerian Rings)
      for (const s of this.solarSails) {{
        const sx = Math.cos(s.angle) * s.radius;
        const sz = Math.sin(s.angle) * s.radius;
        const sy = Math.sin(s.angle) * s.radius * s.inclination;
        const sp = this.project3D(sx, sy, sz, cx, cy);

        ctx.fillStyle = '#fbbf24';
        ctx.beginPath();
        ctx.arc(sp.x, sp.y, 2 * sp.scale, 0, Math.PI * 2);
        ctx.fill();
      }}

      // 4. Planets & Conveyor Belt Logistics
      for (const p of this.planets) {{
        const px = Math.cos(p.angle) * p.dist;
        const pz = Math.sin(p.angle) * p.dist;
        const py = 0;
        const pp = this.project3D(px, py, pz, cx, cy);

        // Planet Body
        ctx.fillStyle = p.color;
        ctx.beginPath();
        ctx.arc(pp.x, pp.y, p.radius * pp.scale, 0, Math.PI * 2);
        ctx.fill();

        // Planet Label
        ctx.fillStyle = '#f8fafc';
        ctx.font = `${{Math.round(10 * pp.scale)}}px ui-monospace, monospace`;
        ctx.textAlign = 'center';
        ctx.fillText(p.name, pp.x, pp.y + p.radius * pp.scale + 12);

        // Mother Planet Conveyor Belts & Ray Receivers
        if (p.isMother) {{
          // Conveyor belt ring around planet
          ctx.strokeStyle = 'rgba(56, 189, 248, 0.4)';
          ctx.lineWidth = 1.5;
          ctx.beginPath();
          ctx.arc(pp.x, pp.y, (p.radius + 14) * pp.scale, 0, Math.PI * 2);
          ctx.stroke();

          // Flowing mineral cubes on conveyor
          const t = performance.now() * 0.003;
          for (let k = 0; k < 6; k++) {{
            const ca = t + (k / 6) * Math.PI * 2;
            const cxk = pp.x + Math.cos(ca) * (p.radius + 14) * pp.scale;
            const cyk = pp.y + Math.sin(ca) * (p.radius + 14) * pp.scale;
            ctx.fillStyle = (k % 2 === 0 ? '#38bdf8' : '#f59e0b');
            ctx.fillRect(cxk - 2, cyk - 2, 4, 4);
          }}

          // Ray Receiver absorption beam to star
          ctx.strokeStyle = 'rgba(56, 189, 248, 0.25)';
          ctx.lineWidth = 2;
          ctx.beginPath();
          ctx.moveTo(pp.x, pp.y);
          ctx.lineTo(starProj.x, starProj.y);
          ctx.stroke();
        }}
      }}

      // 5. Rockets In Flight
      for (const r of this.rockets) {{
        const mother = this.planets[0];
        const mx = Math.cos(mother.angle) * mother.dist;
        const mz = Math.sin(mother.angle) * mother.dist;
        const currX = mx + (r.targetNode.x - mx) * r.progress;
        const currY = (r.targetNode.y) * r.progress;
        const currZ = mz + (r.targetNode.z - mz) * r.progress;
        const rp = this.project3D(currX, currY, currZ, cx, cy);

        ctx.fillStyle = '#ef4444';
        ctx.beginPath();
        ctx.arc(rp.x, rp.y, 3 * rp.scale, 0, Math.PI * 2);
        ctx.fill();

        // Smoke / thrust trail
        ctx.strokeStyle = '#f59e0b';
        ctx.lineWidth = 1.5;
        ctx.beginPath();
        ctx.moveTo(rp.x, rp.y);
        ctx.lineTo(rp.x - 10, rp.y + 10);
        ctx.stroke();
      }}
    }}
  }}

  window.DysonSphereProgram = new DysonSphereGame();

}})();
</script>
'''

    full_expansion = f"{css_block}\n\n{html_block}\n\n{js_block}"
    return full_expansion

def apply_expansion():
    print("Building full grand expansion...")
    expansion_content = get_complete_expansion()

    # Read starfield-pub/starfield.html
    html_path = 'starfield-pub/starfield.html'
    mirror_path = 'starfield-pub/android/app/src/main/assets/starfield.html'

    with open(html_path, 'rb') as f:
        data = f.read()

    # Find expansion boundary
    tag_start = b'<style id="sf-expansion-modes-css">'
    tag_end = b'</body>'

    idx_start = data.find(tag_start)
    if idx_start == -1:
        # If not present, find </body>
        idx_start = data.find(tag_end)
        idx_end = idx_start
    else:
        idx_end = data.find(tag_end, idx_start)

    new_data = data[:idx_start] + expansion_content.encode('utf-8') + b'\r\n' + data[idx_end:]

    with open(html_path, 'wb') as f:
        f.write(new_data)
    print(f"Updated {html_path} ({len(new_data)} bytes)")

    with open(mirror_path, 'wb') as f:
        f.write(new_data)
    print(f"Mirrored to {mirror_path} ({len(new_data)} bytes)")

if __name__ == '__main__':
    apply_expansion()
