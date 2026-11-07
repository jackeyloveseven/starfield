# -*- coding: utf-8 -*-
"""
Inject Void Extraction (Duckov/Tarkov in Space) and Orbital Slingshot (Angry Birds Space)
gameplay modes into starfield.html for the experimental branch.
"""

import sys

def get_expansion_script():
    return '''
<style id="sf-expansion-modes-css">
/* --- Mode Selector Bar --- */
#sf-mode-bar {
  position: fixed;
  top: calc(env(safe-area-inset-top, 0px) + 12px);
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  align-items: center;
  gap: 6px;
  background: rgba(8, 14, 24, 0.78);
  border: 1px solid rgba(255, 255, 255, 0.14);
  backdrop-filter: blur(14px);
  -webkit-backdrop-filter: blur(14px);
  border-radius: 20px;
  padding: 4px 6px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.6), 0 0 16px rgba(56, 189, 248, 0.15);
  z-index: 1000;
  transition: all 0.3s ease;
}
.sf-mode-btn {
  border: none;
  outline: none;
  background: transparent;
  color: #94a3b8;
  padding: 5px 12px;
  border-radius: 14px;
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 0.08em;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 5px;
  transition: all 0.25s cubic-bezier(0.2, 0.8, 0.2, 1);
  white-space: nowrap;
}
.sf-mode-btn:hover {
  color: #f1f5f9;
  background: rgba(255, 255, 255, 0.06);
}
.sf-mode-btn.active {
  background: linear-gradient(135deg, rgba(56, 189, 248, 0.25) 0%, rgba(14, 165, 233, 0.15) 100%);
  color: #38bdf8;
  border: 1px solid rgba(56, 189, 248, 0.4);
  box-shadow: 0 0 12px rgba(56, 189, 248, 0.3);
}

/* --- Fullscreen Game Overlay Overlays --- */
.sf-expansion-overlay {
  position: fixed;
  inset: 0;
  width: 100vw;
  height: 100vh;
  z-index: 900;
  display: none;
  background: #04070d;
  touch-action: none;
  user-select: none;
  overflow: hidden;
}
.sf-expansion-overlay.active {
  display: block;
}

/* --- Tactical HUD for Void Extraction (Duckov/Tarkov) --- */
#sf-ext-hud {
  position: absolute;
  inset: 0;
  pointer-events: none;
  z-index: 920;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  padding: calc(env(safe-area-inset-top, 0px) + 60px) 16px calc(env(safe-area-inset-bottom, 0px) + 16px) 16px;
  box-sizing: border-box;
}
.sf-ext-vitals {
  display: flex;
  flex-direction: column;
  gap: 6px;
  width: min(240px, 60vw);
}
.sf-ext-bar-wrap {
  display: flex;
  align-items: center;
  gap: 8px;
  background: rgba(15, 23, 42, 0.7);
  padding: 4px 8px;
  border-radius: 8px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(8px);
}
.sf-ext-bar-label {
  font-size: 9.5px;
  font-family: ui-monospace, monospace;
  font-weight: 700;
  letter-spacing: 0.1em;
  width: 48px;
}
.sf-ext-bar-track {
  flex: 1;
  height: 8px;
  background: rgba(0, 0, 0, 0.6);
  border-radius: 4px;
  overflow: hidden;
  position: relative;
}
.sf-ext-bar-fill {
  height: 100%;
  width: 100%;
  transition: width 0.15s ease;
}
.sf-ext-bar-fill.shield { background: linear-gradient(90deg, #38bdf8, #60a5fa); box-shadow: 0 0 8px #38bdf8; }
.sf-ext-bar-fill.hull { background: linear-gradient(90deg, #f43f5e, #fb7185); box-shadow: 0 0 8px #f43f5e; }

.sf-ext-top-center {
  position: absolute;
  top: calc(env(safe-area-inset-top, 0px) + 60px);
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  pointer-events: none;
}
.sf-ext-timer {
  font-size: 15px;
  font-family: ui-monospace, monospace;
  font-weight: 700;
  letter-spacing: 0.14em;
  color: #fbbf24;
  background: rgba(15, 23, 42, 0.8);
  border: 1px solid rgba(251, 191, 36, 0.4);
  padding: 4px 14px;
  border-radius: 12px;
  box-shadow: 0 0 16px rgba(251, 191, 36, 0.2);
}
.sf-ext-storm-note {
  font-size: 9px;
  color: #f87171;
  letter-spacing: 0.1em;
  text-shadow: 0 0 8px rgba(248, 113, 113, 0.5);
}

.sf-ext-cargo-grid {
  display: flex;
  gap: 6px;
  align-self: flex-start;
  margin-top: 10px;
}
.sf-ext-slot {
  width: 36px;
  height: 36px;
  background: rgba(15, 23, 42, 0.7);
  border: 1px solid rgba(255, 255, 255, 0.14);
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  box-shadow: inset 0 0 8px rgba(0, 0, 0, 0.6);
}

/* Mobile Touch Controls for Extraction */
.sf-ext-touch-layer {
  position: absolute;
  inset: 0;
  pointer-events: auto;
  z-index: 915;
}
.sf-ext-controls-bottom {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  width: 100%;
  pointer-events: none;
}
.sf-ext-btn-cluster {
  display: flex;
  gap: 12px;
  pointer-events: auto;
}
.sf-ext-act-btn {
  width: 58px;
  height: 58px;
  border-radius: 50%;
  border: 1.5px solid rgba(255, 255, 255, 0.25);
  background: rgba(15, 23, 42, 0.75);
  backdrop-filter: blur(10px);
  color: #f1f5f9;
  font-size: 12px;
  font-weight: 700;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.5);
  transition: all 0.15s ease;
  user-select: none;
  -webkit-user-select: none;
}
.sf-ext-act-btn:active {
  transform: scale(0.92);
  background: rgba(56, 189, 248, 0.3);
  border-color: #38bdf8;
}
.sf-ext-act-btn.fire {
  border-color: rgba(244, 63, 94, 0.6);
  color: #f43f5e;
  box-shadow: 0 0 16px rgba(244, 63, 94, 0.3);
}

/* Modals & Dialogs for Extraction Results */
.sf-ext-modal {
  position: absolute;
  inset: 0;
  background: rgba(4, 7, 13, 0.88);
  backdrop-filter: blur(12px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 950;
  pointer-events: auto;
}
.sf-ext-modal-box {
  width: min(360px, 88vw);
  background: linear-gradient(145deg, #10192a 0%, #080d16 100%);
  border: 1.5px solid rgba(56, 189, 248, 0.4);
  border-radius: 20px;
  padding: 24px 20px;
  box-shadow: 0 20px 50px rgba(0, 0, 0, 0.8), 0 0 30px rgba(56, 189, 248, 0.2);
  text-align: center;
  display: flex;
  flex-direction: column;
  gap: 14px;
}

/* --- HUD for Angry Birds Space (Orbital Slingshot) --- */
#sf-sling-hud {
  position: absolute;
  inset: 0;
  pointer-events: none;
  z-index: 920;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  padding: calc(env(safe-area-inset-top, 0px) + 60px) 16px calc(env(safe-area-inset-bottom, 0px) + 16px) 16px;
  box-sizing: border-box;
}
.sf-sling-top-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}
.sf-sling-score-box {
  background: rgba(15, 23, 42, 0.75);
  border: 1px solid rgba(255, 255, 255, 0.15);
  backdrop-filter: blur(10px);
  border-radius: 14px;
  padding: 6px 14px;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
}
.sf-sling-score-val {
  font-size: 20px;
  font-weight: 800;
  color: #ffd700;
  font-family: ui-monospace, monospace;
  text-shadow: 0 0 10px rgba(255, 215, 0, 0.5);
}
.sf-sling-roster {
  display: flex;
  gap: 8px;
  background: rgba(15, 23, 42, 0.75);
  border: 1px solid rgba(255, 255, 255, 0.15);
  backdrop-filter: blur(10px);
  border-radius: 14px;
  padding: 6px 12px;
}
.sf-sling-bird-token {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  box-shadow: 0 0 8px rgba(255, 255, 255, 0.2);
}
.sf-sling-bottom-hint {
  font-size: 11px;
  letter-spacing: 0.12em;
  color: rgba(255, 255, 255, 0.65);
  text-align: center;
  background: rgba(15, 23, 42, 0.6);
  padding: 6px 14px;
  border-radius: 12px;
  align-self: center;
}
</style>

<div id="sf-mode-bar">
  <button class="sf-mode-btn active" id="sf-btn-mode-cruise">
    <span>🌌</span> 自由漫游
  </button>
  <button class="sf-mode-btn" id="sf-btn-mode-extract">
    <span>🚀</span> 搜打撤 · 鸭科夫
  </button>
  <button class="sf-mode-btn" id="sf-btn-mode-slingshot">
    <span>🪐</span> 引力弹弓太空鸟
  </button>
</div>

<!-- ================= 模式一：深空搜打撤 (Escape from Duckov in Space) ================= -->
<div id="sf-extraction-overlay" class="sf-expansion-overlay">
  <canvas id="sf-extraction-canvas"></canvas>
  <div id="sf-ext-hud">
    <div style="display:flex; justify-content:space-between; align-items:flex-start; width:100%;">
      <div class="sf-ext-vitals">
        <div class="sf-ext-bar-wrap">
          <span class="sf-ext-bar-label" style="color:#38bdf8;">SHIELD</span>
          <div class="sf-ext-bar-track">
            <div class="sf-ext-bar-fill shield" id="sf-ext-shield-fill"></div>
          </div>
        </div>
        <div class="sf-ext-bar-wrap">
          <span class="sf-ext-bar-label" style="color:#f43f5e;">HULL</span>
          <div class="sf-ext-bar-track">
            <div class="sf-ext-bar-fill hull" id="sf-ext-hull-fill"></div>
          </div>
        </div>
        <div class="sf-ext-cargo-grid" id="sf-ext-cargo-grid">
          <!-- 6 Tactical Cargo Slots -->
        </div>
      </div>
      
      <div class="sf-ext-top-center">
        <div class="sf-ext-timer" id="sf-ext-timer-val">03:00</div>
        <div class="sf-ext-storm-note">⚠ 奇点辐射圈正在向中心收缩</div>
      </div>

      <div style="display:flex; flex-direction:column; align-items:flex-end; gap:6px;">
        <div class="sf-sling-score-box">
          <span style="font-size:9px; color:#94a3b8;">SECURED VALUE</span>
          <span class="sf-sling-score-val" id="sf-ext-loot-val" style="color:#38bdf8;">0 ST</span>
        </div>
        <button id="sf-ext-exit-btn" style="pointer-events:auto; padding:4px 10px; border-radius:8px; border:1px solid rgba(255,255,255,0.2); background:rgba(0,0,0,0.5); color:#94a3b8; font-size:10px; cursor:pointer;">退出战区 ✕</button>
      </div>
    </div>

    <div class="sf-ext-controls-bottom">
      <div id="sf-ext-joystick-zone" style="width:120px; height:120px; pointer-events:auto; border-radius:50%; border:1px dashed rgba(255,255,255,0.15); display:flex; align-items:center; justify-content:center; color:rgba(255,255,255,0.25); font-size:10px;">
        拖拽引航
      </div>
      <div class="sf-ext-btn-cluster">
        <button class="sf-ext-act-btn" id="sf-ext-btn-loot" title="靠近残骸搜索 [E]">
          <span>🔍</span>
          <span style="font-size:8px;">搜索</span>
        </button>
        <button class="sf-ext-act-btn" id="sf-ext-btn-boost" title="超载推进 [Shift]">
          <span>⚡</span>
          <span style="font-size:8px;">推进</span>
        </button>
        <button class="sf-ext-act-btn fire" id="sf-ext-btn-fire" title="等离子机炮 [Space]">
          <span>💥</span>
          <span style="font-size:8px;">开火</span>
        </button>
      </div>
    </div>
  </div>
</div>

<!-- ================= 模式二：愤怒的小鸟太空版 (Orbital Slingshot) ================= -->
<div id="sf-slingshot-overlay" class="sf-expansion-overlay">
  <canvas id="sf-slingshot-canvas"></canvas>
  <div id="sf-sling-hud">
    <div class="sf-sling-top-row">
      <div class="sf-sling-score-box">
        <span style="font-size:9px; color:#94a3b8;">ORBITAL SCORE</span>
        <span class="sf-sling-score-val" id="sf-sling-score-text">0</span>
      </div>
      
      <div style="display:flex; flex-direction:column; align-items:center; gap:2px;">
        <span style="font-size:13px; font-weight:700; color:#f1f5f9; letter-spacing:0.12em;" id="sf-sling-level-name">SECTOR 1 · 单星引力弹弓</span>
        <span style="font-size:9px; color:#38bdf8;">利用天体引力井弯曲弹道 击碎海盗核心</span>
      </div>

      <div style="display:flex; align-items:center; gap:8px;">
        <div class="sf-sling-roster" id="sf-sling-roster-box">
          <!-- Roster tokens -->
        </div>
        <button id="sf-sling-reset-btn" style="pointer-events:auto; padding:5px 10px; border-radius:10px; border:1px solid rgba(255,255,255,0.2); background:rgba(0,0,0,0.5); color:#ffd700; font-size:11px; cursor:pointer;">重置 ↺</button>
        <button id="sf-sling-exit-btn" style="pointer-events:auto; padding:5px 10px; border-radius:10px; border:1px solid rgba(255,255,255,0.2); background:rgba(0,0,0,0.5); color:#94a3b8; font-size:11px; cursor:pointer;">退出 ✕</button>
      </div>
    </div>

    <div class="sf-sling-bottom-hint">
      ✦ 按住弹弓向后拖拽并松手发射 · 点击屏幕触发弹头次级机动 ✦
    </div>
  </div>
</div>

<script id="sf-expansion-engine-js">
(function() {
  /* =========================================================================
   * 1. MODE MANAGER & AUDIO SYNTHESIZER
   * ========================================================================= */
  const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
  function playTone(freq, duration, type = 'sine', gainVal = 0.15) {
    if (!audioCtx) return;
    try {
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
    } catch(e) {}
  }

  function playExplosionSfx() {
    if (!audioCtx) return;
    try {
      if (audioCtx.state === 'suspended') audioCtx.resume();
      const bufSize = audioCtx.sampleRate * 0.4;
      const buffer = audioCtx.createBuffer(1, bufSize, audioCtx.sampleRate);
      const output = buffer.getChannelData(0);
      for (let i = 0; i < bufSize; i++) {
        output[i] = (Math.random() * 2 - 1) * Math.exp(-i / (bufSize * 0.3));
      }
      const whiteNoise = audioCtx.createBufferSource();
      whiteNoise.buffer = buffer;
      const filter = audioCtx.createBiquadFilter();
      filter.type = 'lowpass';
      filter.frequency.setValueAtTime(450, audioCtx.currentTime);
      filter.frequency.exponentialRampToValueAtTime(40, audioCtx.currentTime + 0.4);
      const gain = audioCtx.createGain();
      gain.gain.setValueAtTime(0.35, audioCtx.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.001, audioCtx.currentTime + 0.4);
      whiteNoise.connect(filter);
      filter.connect(gain);
      gain.connect(audioCtx.destination);
      whiteNoise.start();
    } catch(e) {}
  }

  let currentMode = 'cruise'; // 'cruise' | 'extract' | 'slingshot'

  const btnCruise = document.getElementById('sf-btn-mode-cruise');
  const btnExtract = document.getElementById('sf-btn-mode-extract');
  const btnSling = document.getElementById('sf-btn-mode-slingshot');
  const overlayExtract = document.getElementById('sf-extraction-overlay');
  const overlaySling = document.getElementById('sf-slingshot-overlay');

  function switchMode(newMode) {
    if (currentMode === newMode) return;
    currentMode = newMode;
    [btnCruise, btnExtract, btnSling].forEach(b => b && b.classList.remove('active'));
    overlayExtract.classList.remove('active');
    overlaySling.classList.remove('active');

    if (newMode === 'cruise') {
      btnCruise.classList.add('active');
      if (window.VoidExtraction) window.VoidExtraction.stop();
      if (window.OrbitalSlingshot) window.OrbitalSlingshot.stop();
      if (typeof showToast === 'function') showToast('已切回深空自由漫游心流 🌌', 2);
    } else if (newMode === 'extract') {
      btnExtract.classList.add('active');
      overlayExtract.classList.add('active');
      if (window.OrbitalSlingshot) window.OrbitalSlingshot.stop();
      if (window.VoidExtraction) window.VoidExtraction.start();
      if (typeof showToast === 'function') showToast('已部署至【搜打撤 · 鸭科夫战区】！搜索高维物资并成功撤离！', 3.5);
    } else if (newMode === 'slingshot') {
      btnSling.classList.add('active');
      overlaySling.classList.add('active');
      if (window.VoidExtraction) window.VoidExtraction.stop();
      if (window.OrbitalSlingshot) window.OrbitalSlingshot.start();
      if (typeof showToast === 'function') showToast('已进入【愤怒的小鸟太空版 · 轨道引力弹弓】！拉伸弹弓发射！', 3.5);
    }
  }

  btnCruise.addEventListener('click', () => switchMode('cruise'));
  btnExtract.addEventListener('click', () => switchMode('extract'));
  btnSling.addEventListener('click', () => switchMode('slingshot'));
  document.getElementById('sf-ext-exit-btn')?.addEventListener('click', () => switchMode('cruise'));
  document.getElementById('sf-sling-exit-btn')?.addEventListener('click', () => switchMode('cruise'));

  /* =========================================================================
   * 2. VOID EXTRACTION ENGINE (搜打撤 / Escape from Duckov in Space)
   * ========================================================================= */
  class VoidExtractionGame {
    constructor() {
      this.canvas = document.getElementById('sf-extraction-canvas');
      this.ctx = this.canvas.getContext('2d');
      this.active = false;
      this.animId = null;

      this.worldSize = 3200;
      this.player = {
        x: 1600, y: 1600,
        vx: 0, vy: 0,
        angle: 0,
        shield: 100, maxShield: 100,
        hull: 100, maxHull: 100,
        shieldRegenTimer: 0,
        cargo: [], maxCargo: 6
      };

      this.storm = {
        cx: 1600, cy: 1600,
        radius: 1750,
        shrinkRate: 4.8 // shrinks per second
      };

      this.timeRemainingSec = 180; // 3 minutes
      this.timerInterval = null;

      this.bullets = [];
      this.enemies = [];
      this.asteroids = [];
      this.derelicts = [];
      this.particles = [];
      this.evacZone = { x: 2600, y: 700, r: 160, progress: 0 };

      this.keys = { w: false, a: false, s: false, d: false, fire: false, boost: false, interact: false };
      this.mouse = { x: 0, y: 0, isDown: false };
      this.totalSecuredValue = 0;

      this.bindControls();
    }

    start() {
      this.resize();
      this.resetGame();
      this.active = true;
      this.lastTime = performance.now();
      this.animId = requestAnimationFrame((t) => this.loop(t));

      clearInterval(this.timerInterval);
      this.timerInterval = setInterval(() => {
        if (!this.active) return;
        this.timeRemainingSec--;
        const m = Math.floor(this.timeRemainingSec / 60);
        const s = this.timeRemainingSec % 60;
        const el = document.getElementById('sf-ext-timer-val');
        if (el) el.textContent = `${m < 10 ? '0' : ''}${m}:${s < 10 ? '0' : ''}${s}`;

        if (this.timeRemainingSec <= 0) {
          this.gameOver(false, '超时！奇点风暴吞噬了战区，星舰失联 (MIA)！');
        }
      }, 1000);
    }

    stop() {
      this.active = false;
      if (this.animId) cancelAnimationFrame(this.animId);
      clearInterval(this.timerInterval);
    }

    resize() {
      this.canvas.width = window.innerWidth;
      this.canvas.height = window.innerHeight;
    }

    resetGame() {
      this.player.x = 1600;
      this.player.y = 1600;
      this.player.vx = 0;
      this.player.vy = 0;
      this.player.angle = 0;
      this.player.shield = 100;
      this.player.hull = 100;
      this.player.cargo = [];
      this.timeRemainingSec = 180;
      this.storm.radius = 1750;
      this.evacZone.progress = 0;
      this.bullets = [];
      this.enemies = [];
      this.asteroids = [];
      this.derelicts = [];
      this.particles = [];

      // Spawn Asteroids
      for (let i = 0; i < 40; i++) {
        this.asteroids.push({
          x: Math.random() * (this.worldSize - 400) + 200,
          y: Math.random() * (this.worldSize - 400) + 200,
          r: 25 + Math.random() * 45,
          color: '#334155'
        });
      }

      // Spawn Derelicts / High-value Loot Crates (搜)
      const lootTypes = [
        { name: '量子核芯碎片', icon: '💎', value: 350, tier: 'rare' },
        { name: '氦-3 压缩气罐', icon: '🔋', value: 200, tier: 'common' },
        { name: '高维折纸图纸', icon: '📜', value: 650, tier: 'epic' },
        { name: '未孵化星核胚胎', icon: '🪐', value: 1200, tier: 'legend', isCore: true },
        { name: '超星系黑匣子', icon: '📦', value: 450, tier: 'rare' }
      ];

      for (let i = 0; i < 12; i++) {
        const item = lootTypes[Math.floor(Math.random() * lootTypes.length)];
        this.derelicts.push({
          x: Math.random() * (this.worldSize - 600) + 300,
          y: Math.random() * (this.worldSize - 600) + 300,
          r: 32,
          item: Object.assign({}, item),
          opened: false,
          progress: 0
        });
      }

      // Spawn Void Sentinels / Pirate Drones (打)
      for (let i = 0; i < 9; i++) {
        this.enemies.push({
          x: Math.random() * (this.worldSize - 600) + 300,
          y: Math.random() * (this.worldSize - 600) + 300,
          vx: 0, vy: 0,
          angle: Math.random() * Math.PI * 2,
          hp: 60, maxHp: 60,
          fireCooldown: 0
        });
      }

      // Pick random Evac Zone location (撤)
      const evacCorners = [
        { x: 2650, y: 650 },
        { x: 550, y: 2650 },
        { x: 2650, y: 2650 },
        { x: 650, y: 650 }
      ];
      const pick = evacCorners[Math.floor(Math.random() * evacCorners.length)];
      this.evacZone.x = pick.x;
      this.evacZone.y = pick.y;

      this.updateHUD();
    }

    bindControls() {
      window.addEventListener('resize', () => { if (this.active) this.resize(); });

      window.addEventListener('keydown', (e) => {
        if (!this.active) return;
        if (e.key === 'w' || e.key === 'W' || e.key === 'ArrowUp') this.keys.w = true;
        if (e.key === 'a' || e.key === 'A' || e.key === 'ArrowLeft') this.keys.a = true;
        if (e.key === 's' || e.key === 'S' || e.key === 'ArrowDown') this.keys.s = true;
        if (e.key === 'd' || e.key === 'D' || e.key === 'ArrowRight') this.keys.d = true;
        if (e.key === ' ') { this.keys.fire = true; e.preventDefault(); }
        if (e.key === 'Shift') this.keys.boost = true;
        if (e.key === 'e' || e.key === 'E') this.keys.interact = true;
      });

      window.addEventListener('keyup', (e) => {
        if (!this.active) return;
        if (e.key === 'w' || e.key === 'W' || e.key === 'ArrowUp') this.keys.w = false;
        if (e.key === 'a' || e.key === 'A' || e.key === 'ArrowLeft') this.keys.a = false;
        if (e.key === 's' || e.key === 'S' || e.key === 'ArrowDown') this.keys.s = false;
        if (e.key === 'd' || e.key === 'D' || e.key === 'ArrowRight') this.keys.d = false;
        if (e.key === ' ') this.keys.fire = false;
        if (e.key === 'Shift') this.keys.boost = false;
        if (e.key === 'e' || e.key === 'E') this.keys.interact = false;
      });

      this.canvas.addEventListener('pointerdown', (e) => {
        if (!this.active) return;
        this.mouse.isDown = true;
        this.mouse.x = e.clientX;
        this.mouse.y = e.clientY;
      });

      this.canvas.addEventListener('pointermove', (e) => {
        if (!this.active) return;
        this.mouse.x = e.clientX;
        this.mouse.y = e.clientY;
      });

      this.canvas.addEventListener('pointerup', () => { this.mouse.isDown = false; });

      // Mobile Touch Buttons
      const btnFire = document.getElementById('sf-ext-btn-fire');
      btnFire?.addEventListener('pointerdown', (e) => { e.preventDefault(); this.keys.fire = true; });
      btnFire?.addEventListener('pointerup', (e) => { e.preventDefault(); this.keys.fire = false; });

      const btnBoost = document.getElementById('sf-ext-btn-boost');
      btnBoost?.addEventListener('pointerdown', (e) => { e.preventDefault(); this.keys.boost = true; });
      btnBoost?.addEventListener('pointerup', (e) => { e.preventDefault(); this.keys.boost = false; });

      const btnLoot = document.getElementById('sf-ext-btn-loot');
      btnLoot?.addEventListener('pointerdown', (e) => { e.preventDefault(); this.keys.interact = true; });
      btnLoot?.addEventListener('pointerup', (e) => { e.preventDefault(); this.keys.interact = false; });

      // Virtual Joystick
      const joyZone = document.getElementById('sf-ext-joystick-zone');
      let joyActive = false, joyOrigin = { x: 0, y: 0 };
      joyZone?.addEventListener('pointerdown', (e) => {
        e.preventDefault();
        joyActive = true;
        const rect = joyZone.getBoundingClientRect();
        joyOrigin = { x: rect.left + rect.width / 2, y: rect.top + rect.height / 2 };
      });
      window.addEventListener('pointermove', (e) => {
        if (!joyActive) return;
        const dx = e.clientX - joyOrigin.x;
        const dy = e.clientY - joyOrigin.y;
        this.keys.w = dy < -15;
        this.keys.s = dy > 15;
        this.keys.a = dx < -15;
        this.keys.d = dx > 15;
      });
      window.addEventListener('pointerup', () => {
        if (joyActive) {
          joyActive = false;
          this.keys.w = this.keys.s = this.keys.a = this.keys.d = false;
        }
      });
    }

    loop(timestamp) {
      if (!this.active) return;
      const dt = Math.min(0.05, (timestamp - this.lastTime) / 1000);
      this.lastTime = timestamp;

      this.update(dt);
      this.render();

      this.animId = requestAnimationFrame((t) => this.loop(t));
    }

    update(dt) {
      const p = this.player;

      // Thrust & Acceleration
      let ax = 0, ay = 0;
      if (this.keys.w) ay -= 1;
      if (this.keys.s) ay += 1;
      if (this.keys.a) ax -= 1;
      if (this.keys.d) ax += 1;

      const thrustMag = this.keys.boost ? 950 : 540;
      const len = Math.hypot(ax, ay);
      if (len > 0) {
        p.vx += (ax / len) * thrustMag * dt;
        p.vy += (ay / len) * thrustMag * dt;

        // Thruster sparks
        if (Math.random() < 0.6) {
          this.particles.push({
            x: p.x - Math.cos(p.angle) * 16,
            y: p.y - Math.sin(p.angle) * 16,
            vx: -p.vx * 0.4 + (Math.random() - 0.5) * 50,
            vy: -p.vy * 0.4 + (Math.random() - 0.5) * 50,
            life: 0.25, maxLife: 0.25,
            color: this.keys.boost ? '#ffd700' : '#38bdf8',
            size: Math.random() * 4 + 2
          });
        }
      }

      // Inertia & Drag
      p.vx *= 0.94;
      p.vy *= 0.94;
      p.x += p.vx * dt;
      p.y += p.vy * dt;

      // Keep in world bounds
      p.x = Math.max(60, Math.min(this.worldSize - 60, p.x));
      p.y = Math.max(60, Math.min(this.worldSize - 60, p.y));

      // Aim Ship toward pointer/touch or velocity
      const screenMidX = this.canvas.width / 2;
      const screenMidY = this.canvas.height / 2;
      if (this.mouse.isDown || Math.hypot(this.mouse.x - screenMidX, this.mouse.y - screenMidY) > 50) {
        p.angle = Math.atan2(this.mouse.y - screenMidY, this.mouse.x - screenMidX);
      } else if (Math.hypot(p.vx, p.vy) > 10) {
        p.angle = Math.atan2(p.vy, p.vx);
      }

      // Fire Plasma Gun
      if ((this.keys.fire || this.mouse.isDown) && (this.fireCooldown || 0) <= 0) {
        this.fireCooldown = 0.18;
        const speed = 900;
        this.bullets.push({
          x: p.x + Math.cos(p.angle) * 20,
          y: p.y + Math.sin(p.angle) * 20,
          vx: p.vx * 0.3 + Math.cos(p.angle) * speed,
          vy: p.vy * 0.3 + Math.sin(p.angle) * speed,
          isEnemy: false,
          life: 1.2
        });
        playTone(650, 0.08, 'square', 0.12);
      }
      if (this.fireCooldown > 0) this.fireCooldown -= dt;

      // Radiation Storm Shrink
      this.storm.radius = Math.max(120, this.storm.radius - this.storm.shrinkRate * dt);
      const distFromStormCenter = Math.hypot(p.x - this.storm.cx, p.y - this.storm.cy);
      if (distFromStormCenter > this.storm.radius) {
        // Player outside safe zone: Radiation damage
        p.hull -= 16 * dt;
        if (Math.random() < 0.2) playTone(120, 0.15, 'sawtooth', 0.1);
        if (p.hull <= 0) {
          this.gameOver(false, '未能及时撤离，星舰损毁于超强黑洞潮汐辐射！');
          return;
        }
      }

      // Shield Passive Recharge
      if (p.shieldRegenTimer > 0) p.shieldRegenTimer -= dt;
      else if (p.shield < p.maxShield) {
        p.shield = Math.min(p.maxShield, p.shield + 20 * dt);
      }

      // Update Bullets
      for (let i = this.bullets.length - 1; i >= 0; i--) {
        const b = this.bullets[i];
        b.x += b.vx * dt;
        b.y += b.vy * dt;
        b.life -= dt;

        // Player hit by enemy bullet
        if (b.isEnemy && Math.hypot(b.x - p.x, b.y - p.y) < 22) {
          this.damagePlayer(15);
          this.bullets.splice(i, 1);
          continue;
        }

        // Enemy hit by player bullet
        if (!b.isEnemy) {
          for (let j = this.enemies.length - 1; j >= 0; j--) {
            const e = this.enemies[j];
            if (Math.hypot(b.x - e.x, b.y - e.y) < 26) {
              e.hp -= 28;
              this.bullets.splice(i, 1);
              playTone(280, 0.1, 'triangle', 0.2);

              if (e.hp <= 0) {
                // Kill Enemy
                this.enemies.splice(j, 1);
                playExplosionSfx();
                this.totalSecuredValue += 120;
                // Spawn scrap loot
                this.derelicts.push({
                  x: e.x, y: e.y, r: 24,
                  item: { name: '击毁残骸废料', icon: '🔩', value: 120, tier: 'common' },
                  opened: false, progress: 0
                });
                if (typeof showToast === 'function') showToast('击毁虚空游荡者哨戒机！+120 ST', 2);
              }
              break;
            }
          }
        }

        if (b.life <= 0) this.bullets.splice(i, 1);
      }

      // Update Enemies (AI)
      for (const e of this.enemies) {
        const dist = Math.hypot(p.x - e.x, p.y - e.y);
        if (dist < 420) {
          // Pursue player
          e.angle = Math.atan2(p.y - e.y, p.x - e.x);
          e.vx += Math.cos(e.angle) * 320 * dt;
          e.vy += Math.sin(e.angle) * 320 * dt;

          // Enemy fire
          e.fireCooldown = (e.fireCooldown || 0) - dt;
          if (e.fireCooldown <= 0 && dist < 340) {
            e.fireCooldown = 1.4;
            this.bullets.push({
              x: e.x + Math.cos(e.angle) * 18,
              y: e.y + Math.sin(e.angle) * 18,
              vx: Math.cos(e.angle) * 550,
              vy: Math.sin(e.angle) * 550,
              isEnemy: true,
              life: 1.5
            });
            playTone(420, 0.08, 'sawtooth', 0.1);
          }
        }
        e.vx *= 0.94;
        e.vy *= 0.94;
        e.x += e.vx * dt;
        e.y += e.vy * dt;
      }

      // Update Loot Interaction (搜)
      for (const d of this.derelicts) {
        if (d.opened) continue;
        const dist = Math.hypot(p.x - d.x, p.y - d.y);
        if (dist < 56 && this.keys.interact) {
          d.progress += dt / 1.2; // 1.2s to scavenge
          if (Math.random() < 0.3) playTone(700 + d.progress * 400, 0.05, 'sine', 0.08);

          if (d.progress >= 1.0) {
            d.opened = true;
            if (p.cargo.length < p.maxCargo) {
              p.cargo.push(d.item);
              this.totalSecuredValue += d.item.value;
              playTone(880, 0.25, 'triangle', 0.25);
              if (typeof showToast === 'function') {
                showToast(`[搜刮成功] 获得 ${d.item.icon} ${d.item.name} (+${d.item.value} ST)`, 2.5);
              }
            } else {
              if (typeof showToast === 'function') showToast('背包已满！无法收容更多战利品！', 2);
            }
          }
        } else {
          d.progress = Math.max(0, d.progress - dt * 1.5);
        }
      }

      // Update Extraction Zone (撤)
      const distEvac = Math.hypot(p.x - this.evacZone.x, p.y - this.evacZone.y);
      if (distEvac < this.evacZone.r) {
        this.evacZone.progress += dt / 5.0; // 5 seconds in zone
        playTone(500 + this.evacZone.progress * 600, 0.05, 'sine', 0.08);

        if (this.evacZone.progress >= 1.0) {
          this.gameOver(true, '安全撤离成功！全量搜刮物资已成功同步至深空基地！');
          return;
        }
      } else {
        this.evacZone.progress = Math.max(0, this.evacZone.progress - dt * 0.8);
      }

      // Update Particles
      for (let i = this.particles.length - 1; i >= 0; i--) {
        const pt = this.particles[i];
        pt.x += pt.vx * dt;
        pt.y += pt.vy * dt;
        pt.life -= dt;
        if (pt.life <= 0) this.particles.splice(i, 1);
      }

      this.updateHUD();
    }

    damagePlayer(amount) {
      const p = this.player;
      p.shieldRegenTimer = 4.0;
      if (p.shield > 0) {
        p.shield -= amount;
        if (p.shield < 0) {
          p.hull += p.shield;
          p.shield = 0;
        }
      } else {
        p.hull -= amount;
      }
      playTone(180, 0.15, 'sawtooth', 0.2);

      if (p.hull <= 0) {
        this.gameOver(false, '星舰核心过载引爆！搜刮战利品全部损毁遗失 (MIA)！');
      }
    }

    updateHUD() {
      const p = this.player;
      const shieldFill = document.getElementById('sf-ext-shield-fill');
      const hullFill = document.getElementById('sf-ext-hull-fill');
      const lootVal = document.getElementById('sf-ext-loot-val');
      const cargoGrid = document.getElementById('sf-ext-cargo-grid');

      if (shieldFill) shieldFill.style.width = `${Math.max(0, (p.shield / p.maxShield) * 100)}%`;
      if (hullFill) hullFill.style.width = `${Math.max(0, (p.hull / p.maxHull) * 100)}%`;
      if (lootVal) lootVal.textContent = `${this.totalSecuredValue} ST`;

      if (cargoGrid) {
        let slotsHtml = '';
        for (let i = 0; i < p.maxCargo; i++) {
          const it = p.cargo[i];
          if (it) {
            slotsHtml += `<div class="sf-ext-slot" title="${it.name} (${it.value} ST)">${it.icon}</div>`;
          } else {
            slotsHtml += `<div class="sf-ext-slot" style="opacity:0.3;">·</div>`;
          }
        }
        cargoGrid.innerHTML = slotsHtml;
      }
    }

    render() {
      const ctx = this.ctx;
      const w = this.canvas.width;
      const h = this.canvas.height;
      const p = this.player;

      ctx.clearRect(0, 0, w, h);

      // Camera Offset
      const camX = p.x - w / 2;
      const camY = p.y - h / 2;

      ctx.save();
      ctx.translate(-camX, -camY);

      // 1. World Grid & Space Dust
      ctx.strokeStyle = 'rgba(255, 255, 255, 0.04)';
      ctx.lineWidth = 1;
      const gridStep = 100;
      const startX = Math.floor(camX / gridStep) * gridStep;
      const startY = Math.floor(camY / gridStep) * gridStep;
      ctx.beginPath();
      for (let x = startX; x < startX + w + gridStep; x += gridStep) {
        ctx.moveTo(x, startY); ctx.lineTo(x, startY + h + gridStep);
      }
      for (let y = startY; y < startY + h + gridStep; y += gridStep) {
        ctx.moveTo(startX, y); ctx.lineTo(startX + w + gridStep, y);
      }
      ctx.stroke();

      // 2. Radiation Storm Ring
      ctx.save();
      ctx.strokeStyle = 'rgba(239, 68, 68, 0.65)';
      ctx.lineWidth = 6;
      ctx.setLineDash([16, 12]);
      ctx.beginPath();
      ctx.arc(this.storm.cx, this.storm.cy, this.storm.radius, 0, Math.PI * 2);
      ctx.stroke();
      ctx.restore();

      // 3. Evacuation Zone (撤)
      ctx.save();
      const evac = this.evacZone;
      const evacGlow = ctx.createRadialGradient(evac.x, evac.y, 20, evac.x, evac.y, evac.r);
      evacGlow.addColorStop(0, 'rgba(56, 189, 248, 0.35)');
      evacGlow.addColorStop(1, 'rgba(56, 189, 248, 0.02)');
      ctx.fillStyle = evacGlow;
      ctx.beginPath();
      ctx.arc(evac.x, evac.y, evac.r, 0, Math.PI * 2);
      ctx.fill();

      ctx.strokeStyle = '#38bdf8';
      ctx.lineWidth = 2.5;
      ctx.beginPath();
      ctx.arc(evac.x, evac.y, evac.r, 0, Math.PI * 2);
      ctx.stroke();

      // Evac Label & Progress Ring
      ctx.fillStyle = '#f1f5f9';
      ctx.font = '12px ui-monospace, monospace';
      ctx.textAlign = 'center';
      ctx.fillText('✦ 折跃跳跃撤离点 EVAC BEACON ✦', evac.x, evac.y - 12);
      if (evac.progress > 0) {
        ctx.strokeStyle = '#ffd700';
        ctx.lineWidth = 6;
        ctx.beginPath();
        ctx.arc(evac.x, evac.y, 35, -Math.PI / 2, -Math.PI / 2 + Math.PI * 2 * evac.progress);
        ctx.stroke();
        ctx.fillText(`跳跃引导中 ${Math.round(evac.progress * 100)}%`, evac.x, evac.y + 14);
      } else {
        ctx.fillStyle = 'rgba(255, 255, 255, 0.6)';
        ctx.fillText('停留 5 秒安全折跃', evac.x, evac.y + 14);
      }
      ctx.restore();

      // 4. Asteroids
      for (const ast of this.asteroids) {
        ctx.save();
        ctx.fillStyle = ast.color;
        ctx.beginPath();
        ctx.arc(ast.x, ast.y, ast.r, 0, Math.PI * 2);
        ctx.fill();
        ctx.strokeStyle = 'rgba(255, 255, 255, 0.12)';
        ctx.stroke();
        ctx.restore();
      }

      // 5. Derelicts & Loot Crates (搜)
      for (const d of this.derelicts) {
        ctx.save();
        ctx.translate(d.x, d.y);
        if (!d.opened) {
          ctx.strokeStyle = '#38bdf8';
          ctx.fillStyle = 'rgba(15, 23, 42, 0.85)';
          ctx.lineWidth = 1.5;
          ctx.beginPath();
          ctx.arc(0, 0, d.r, 0, Math.PI * 2);
          ctx.fill();
          ctx.stroke();

          ctx.font = '16px serif';
          ctx.textAlign = 'center';
          ctx.textBaseline = 'middle';
          ctx.fillText(d.item.icon, 0, -2);

          ctx.font = '9px monospace';
          ctx.fillStyle = '#94a3b8';
          ctx.fillText(d.item.name, 0, d.r + 12);

          if (d.progress > 0) {
            ctx.strokeStyle = '#ffd700';
            ctx.lineWidth = 3;
            ctx.beginPath();
            ctx.arc(0, 0, d.r + 4, -Math.PI / 2, -Math.PI / 2 + Math.PI * 2 * d.progress);
            ctx.stroke();
          }
        } else {
          ctx.strokeStyle = 'rgba(255, 255, 255, 0.15)';
          ctx.fillStyle = 'rgba(15, 23, 42, 0.3)';
          ctx.beginPath();
          ctx.arc(0, 0, d.r * 0.8, 0, Math.PI * 2);
          ctx.fill();
          ctx.stroke();
        }
        ctx.restore();
      }

      // 6. Enemies (打)
      for (const e of this.enemies) {
        ctx.save();
        ctx.translate(e.x, e.y);
        ctx.rotate(e.angle);

        // Enemy Drone Model
        ctx.fillStyle = '#e11d48';
        ctx.beginPath();
        ctx.moveTo(18, 0);
        ctx.lineTo(-12, -12);
        ctx.lineTo(-6, 0);
        ctx.lineTo(-12, 12);
        ctx.closePath();
        ctx.fill();

        ctx.strokeStyle = '#fda4af';
        ctx.lineWidth = 1.5;
        ctx.stroke();
        ctx.restore();

        // Enemy HP Bar
        ctx.fillStyle = 'rgba(0, 0, 0, 0.6)';
        ctx.fillRect(e.x - 16, e.y - 20, 32, 4);
        ctx.fillStyle = '#f43f5e';
        ctx.fillRect(e.x - 16, e.y - 20, (e.hp / e.maxHp) * 32, 4);
      }

      // 7. Bullets
      for (const b of this.bullets) {
        ctx.fillStyle = b.isEnemy ? '#f43f5e' : '#38bdf8';
        ctx.shadowColor = ctx.fillStyle;
        ctx.shadowBlur = 8;
        ctx.beginPath();
        ctx.arc(b.x, b.y, b.isEnemy ? 3.5 : 4, 0, Math.PI * 2);
        ctx.fill();
        ctx.shadowBlur = 0;
      }

      // 8. Player Ship
      ctx.save();
      ctx.translate(p.x, p.y);
      ctx.rotate(p.angle);

      // Ship Wings & Hull
      ctx.fillStyle = '#0284c7';
      ctx.beginPath();
      ctx.moveTo(22, 0);
      ctx.lineTo(-14, -14);
      ctx.lineTo(-8, 0);
      ctx.lineTo(-14, 14);
      ctx.closePath();
      ctx.fill();

      ctx.strokeStyle = '#38bdf8';
      ctx.lineWidth = 2;
      ctx.stroke();

      // Shield Bubble
      if (p.shield > 0) {
        ctx.strokeStyle = 'rgba(56, 189, 248, 0.45)';
        ctx.fillStyle = 'rgba(56, 189, 248, 0.08)';
        ctx.beginPath();
        ctx.arc(0, 0, 24, 0, Math.PI * 2);
        ctx.fill();
        ctx.stroke();
      }
      ctx.restore();

      // 9. Particles
      for (const pt of this.particles) {
        ctx.fillStyle = pt.color;
        ctx.beginPath();
        ctx.arc(pt.x, pt.y, pt.size * (pt.life / pt.maxLife), 0, Math.PI * 2);
        ctx.fill();
      }

      ctx.restore();
    }

    gameOver(success, reason) {
      this.stop();
      playExplosionSfx();

      const modal = document.createElement('div');
      modal.className = 'sf-ext-modal';

      let lootSummary = '';
      if (success) {
        if (this.player.cargo.length > 0) {
          lootSummary = `
            <div style="background:rgba(255,255,255,0.06); padding:10px; border-radius:12px; margin:8px 0; text-align:left;">
              <div style="font-size:11px; color:#38bdf8; font-weight:700; margin-bottom:6px;">SECURED LOOT // 撤离物资清单:</div>
              ${this.player.cargo.map(c => `
                <div style="display:flex; justify-content:space-between; font-size:11px; color:#e2e8f0; margin:3px 0;">
                  <span>${c.icon} ${c.name}</span>
                  <b style="color:#ffd700;">+${c.value} ST</b>
                </div>
              `).join('')}
            </div>
          `;
          // Award Cores if gathered
          const coresFound = this.player.cargo.filter(c => c.isCore).length;
          if (coresFound > 0 && window.StarfieldHatch && window.StarfieldHatch.addCores) {
            window.StarfieldHatch.addCores(coresFound);
          }
        }
      }

      modal.innerHTML = `
        <div class="sf-ext-modal-box">
          <div style="font-size:32px;">${success ? '🛸' : '💥'}</div>
          <h2 style="font-size:20px; color:${success ? '#38bdf8' : '#f43f5e'}; letter-spacing:0.12em; margin:0;">
            ${success ? 'EVACUATION SUCCESSFUL' : 'VESSEL DESTROYED · MIA'}
          </h2>
          <p style="font-size:12px; color:#94a3b8; line-height:1.5; margin:0;">
            ${reason}
          </p>
          ${lootSummary}
          <div style="display:flex; justify-content:space-between; padding:8px 12px; background:rgba(0,0,0,0.4); border-radius:10px; font-size:12px;">
            <span>战局收益:</span>
            <b style="color:#ffd700;">+${this.totalSecuredValue} ST</b>
          </div>
          <button id="sf-ext-modal-confirm-btn" style="padding:10px 0; border-radius:12px; border:none; background:linear-gradient(135deg, #38bdf8, #0284c7); color:#080e18; font-weight:700; cursor:pointer;">
            确认并返回基地 ↗
          </button>
        </div>
      `;

      document.body.appendChild(modal);
      document.getElementById('sf-ext-modal-confirm-btn').addEventListener('click', () => {
        modal.remove();
        switchMode('cruise');
      });
    }
  }

  window.VoidExtraction = new VoidExtractionGame();

  /* =========================================================================
   * 3. ORBITAL SLINGSHOT ENGINE (愤怒的小鸟太空版 / Gravitational Slingshot)
   * ========================================================================= */
  class OrbitalSlingshotGame {
    constructor() {
      this.canvas = document.getElementById('sf-slingshot-canvas');
      this.ctx = this.canvas.getContext('2d');
      this.active = false;
      this.animId = null;

      this.score = 0;
      this.levelIndex = 0;

      this.levels = [
        {
          name: 'SECTOR 1 · 单星引力弹弓',
          planets: [
            { x: 500, y: 380, r: 52, mass: 90000, atmoR: 120, atmoColor: 'rgba(56, 189, 248, 0.25)', coreColor: '#0284c7' }
          ],
          targets: [
            { x: 740, y: 360, r: 24, hp: 40, maxHp: 40, label: '海盗前哨' },
            { x: 780, y: 280, r: 20, hp: 30, maxHp: 30, label: '雷达天线' }
          ],
          obstacles: [
            { x: 670, y: 320, w: 16, h: 90, hp: 50 }
          ],
          slingshot: { x: 160, y: 380 }
        },
        {
          name: 'SECTOR 2 · 双星引力借力变轨',
          planets: [
            { x: 420, y: 260, r: 44, mass: 75000, atmoR: 100, atmoColor: 'rgba(168, 85, 247, 0.25)', coreColor: '#7e22ce' },
            { x: 580, y: 500, r: 50, mass: 85000, atmoR: 110, atmoColor: 'rgba(251, 191, 36, 0.25)', coreColor: '#d97706' }
          ],
          targets: [
            { x: 800, y: 440, r: 26, hp: 50, maxHp: 50, label: '主能量反应堆' },
            { x: 760, y: 200, r: 22, hp: 35, maxHp: 35, label: '无人机母巢' }
          ],
          obstacles: [
            { x: 720, y: 380, w: 20, h: 110, hp: 70 },
            { x: 700, y: 180, w: 18, h: 70, hp: 40 }
          ],
          slingshot: { x: 140, y: 380 }
        }
      ];

      this.birdsQueue = ['red', 'blue', 'bomb'];
      this.currentBird = null;
      this.flyingBirds = [];
      this.particles = [];

      this.dragState = {
        isDragging: false,
        dragX: 0, dragY: 0
      };

      this.bindEvents();
    }

    start() {
      this.resize();
      this.score = 0;
      this.loadLevel(this.levelIndex);
      this.active = true;
      this.lastTime = performance.now();
      this.animId = requestAnimationFrame((t) => this.loop(t));
    }

    stop() {
      this.active = false;
      if (this.animId) cancelAnimationFrame(this.animId);
    }

    resize() {
      this.canvas.width = window.innerWidth;
      this.canvas.height = window.innerHeight;
    }

    loadLevel(idx) {
      const lvl = this.levels[idx % this.levels.length];
      this.currentLevel = JSON.parse(JSON.stringify(lvl));
      this.birdsQueue = ['red', 'blue', 'bomb'];
      this.flyingBirds = [];
      this.particles = [];
      this.spawnNextBird();

      const nameEl = document.getElementById('sf-sling-level-name');
      if (nameEl) nameEl.textContent = lvl.name;
      this.updateRosterHUD();
    }

    spawnNextBird() {
      if (this.birdsQueue.length === 0) {
        // Check if targets remaining
        setTimeout(() => {
          if (this.currentLevel.targets.length > 0) {
            if (typeof showToast === 'function') showToast('探针鸟已耗尽！点击重置再次尝试！', 3);
          }
        }, 3000);
        return;
      }

      const type = this.birdsQueue.shift();
      const s = this.currentLevel.slingshot;
      this.currentBird = {
        type: type,
        x: s.x, y: s.y,
        vx: 0, vy: 0,
        r: 15,
        state: 'ready', // 'ready' | 'flying' | 'split'
        path: []
      };
      this.updateRosterHUD();
    }

    bindEvents() {
      window.addEventListener('resize', () => { if (this.active) this.resize(); });

      document.getElementById('sf-sling-reset-btn')?.addEventListener('click', () => {
        this.loadLevel(this.levelIndex);
      });

      const getPos = (e) => {
        const rect = this.canvas.getBoundingClientRect();
        return { x: e.clientX - rect.left, y: e.clientY - rect.top };
      };

      this.canvas.addEventListener('pointerdown', (e) => {
        if (!this.active) return;
        const pos = getPos(e);
        const s = this.currentLevel.slingshot;

        // Click on Ready Bird to Drag Slingshot
        if (this.currentBird && this.currentBird.state === 'ready') {
          if (Math.hypot(pos.x - s.x, pos.y - s.y) < 60) {
            this.dragState.isDragging = true;
            this.dragState.dragX = pos.x;
            this.dragState.dragY = pos.y;
            playTone(320, 0.1, 'sine', 0.1);
            return;
          }
        }

        // Click screen mid-flight to trigger probe secondary skill!
        for (const b of this.flyingBirds) {
          if (b.state === 'flying') {
            if (b.type === 'blue') {
              // Split into 3
              b.state = 'split';
              playTone(720, 0.15, 'square', 0.2);
              this.flyingBirds.push(
                { type: 'blue', x: b.x, y: b.y, vx: b.vx * 1.1 + b.vy * 0.2, vy: b.vy * 1.1 - b.vx * 0.2, r: 10, state: 'sub', path: [] },
                { type: 'blue', x: b.x, y: b.y, vx: b.vx * 1.1 - b.vy * 0.2, vy: b.vy * 1.1 + b.vx * 0.2, r: 10, state: 'sub', path: [] }
              );
              b.r = 10;
              if (typeof showToast === 'function') showToast('三联分形散射探针激活！', 1.5);
              break;
            } else if (b.type === 'bomb') {
              // Gravitational Implosion
              b.state = 'exploded';
              playExplosionSfx();
              this.triggerImplosion(b.x, b.y);
              break;
            }
          }
        }
      });

      this.canvas.addEventListener('pointermove', (e) => {
        if (!this.active || !this.dragState.isDragging) return;
        const pos = getPos(e);
        const s = this.currentLevel.slingshot;
        const dx = pos.x - s.x;
        const dy = pos.y - s.y;
        const dist = Math.hypot(dx, dy);
        const maxPull = 90;

        if (dist > maxPull) {
          this.dragState.dragX = s.x + (dx / dist) * maxPull;
          this.dragState.dragY = s.y + (dy / dist) * maxPull;
        } else {
          this.dragState.dragX = pos.x;
          this.dragState.dragY = pos.y;
        }
      });

      this.canvas.addEventListener('pointerup', () => {
        if (!this.active || !this.dragState.isDragging) return;
        this.dragState.isDragging = false;

        const s = this.currentLevel.slingshot;
        const dx = s.x - this.dragState.dragX;
        const dy = s.y - this.dragState.dragY;
        const impulse = 6.8;

        const b = this.currentBird;
        b.x = s.x;
        b.y = s.y;
        b.vx = dx * impulse;
        b.vy = dy * impulse;
        b.state = 'flying';

        this.flyingBirds.push(b);
        this.currentBird = null;
        playTone(580, 0.2, 'triangle', 0.25);

        // Spawn next bird after brief delay
        setTimeout(() => this.spawnNextBird(), 2200);
      });
    }

    triggerImplosion(x, y) {
      // Gravitational blast wave hits targets & obstacles
      for (let i = 0; i < 30; i++) {
        this.particles.push({
          x: x, y: y,
          vx: (Math.random() - 0.5) * 400,
          vy: (Math.random() - 0.5) * 400,
          color: '#fbbf24',
          life: 0.6, maxLife: 0.6,
          size: Math.random() * 6 + 2
        });
      }

      for (let i = this.currentLevel.targets.length - 1; i >= 0; i--) {
        const t = this.currentLevel.targets[i];
        if (Math.hypot(t.x - x, t.y - y) < 160) {
          t.hp -= 60;
          if (t.hp <= 0) {
            this.currentLevel.targets.splice(i, 1);
            this.addScore(5000);
          }
        }
      }
      this.checkLevelClear();
    }

    addScore(pts) {
      this.score += pts;
      const el = document.getElementById('sf-sling-score-text');
      if (el) el.textContent = this.score;
    }

    updateRosterHUD() {
      const box = document.getElementById('sf-sling-roster-box');
      if (!box) return;
      let html = '';
      const icons = { red: '🔴', blue: '🔵', bomb: '💣' };
      if (this.currentBird) {
        html += `<div class="sf-sling-bird-token" style="border:1.5px solid #ffd700;">${icons[this.currentBird.type]}</div>`;
      }
      for (const t of this.birdsQueue) {
        html += `<div class="sf-sling-bird-token" style="opacity:0.6;">${icons[t]}</div>`;
      }
      box.innerHTML = html;
    }

    loop(timestamp) {
      if (!this.active) return;
      const dt = Math.min(0.04, (timestamp - this.lastTime) / 1000);
      this.lastTime = timestamp;

      this.update(dt);
      this.render();

      this.animId = requestAnimationFrame((t) => this.loop(t));
    }

    update(dt) {
      const lvl = this.currentLevel;

      // Update Flying Probes
      for (let i = this.flyingBirds.length - 1; i >= 0; i--) {
        const b = this.flyingBirds[i];
        if (b.state === 'exploded') {
          this.flyingBirds.splice(i, 1);
          continue;
        }

        // Apply Newtonian Gravity from all Celestial Bodies
        for (const p of lvl.planets) {
          const dx = p.x - b.x;
          const dy = p.y - b.y;
          const distSq = dx * dx + dy * dy;
          const dist = Math.sqrt(distSq);

          if (dist < p.atmoR) {
            // Atmospheric drag
            b.vx *= 0.985;
            b.vy *= 0.985;
            // Gravity force F = G * M / r^2
            const force = (p.mass / Math.max(900, distSq)) * 14;
            b.vx += (dx / dist) * force * dt;
            b.vy += (dy / dist) * force * dt;
          }

          // Crash into Planet Surface
          if (dist < p.r + b.r) {
            playTone(180, 0.15, 'sawtooth', 0.2);
            b.state = 'exploded';
            this.flyingBirds.splice(i, 1);
            break;
          }
        }

        b.x += b.vx * dt;
        b.y += b.vy * dt;

        // Path trail
        if (Math.random() < 0.4) {
          b.path.push({ x: b.x, y: b.y });
          if (b.path.length > 30) b.path.shift();
        }

        // Check Target Collisions
        for (let j = lvl.targets.length - 1; j >= 0; j--) {
          const t = lvl.targets[j];
          if (Math.hypot(t.x - b.x, t.y - b.y) < t.r + b.r) {
            t.hp -= 35;
            playTone(480, 0.15, 'triangle', 0.25);
            b.vx *= -0.5;
            b.vy *= -0.5;

            if (t.hp <= 0) {
              lvl.targets.splice(j, 1);
              playExplosionSfx();
              this.addScore(3000);
              if (typeof showToast === 'function') showToast(`核心摧毁！+3000 PT 💥`, 2);
              this.checkLevelClear();
            }
            break;
          }
        }

        // Remove if off-screen
        if (b.x < -100 || b.x > this.canvas.width + 100 || b.y < -100 || b.y > this.canvas.height + 100) {
          this.flyingBirds.splice(i, 1);
        }
      }

      // Update Particles
      for (let i = this.particles.length - 1; i >= 0; i--) {
        const pt = this.particles[i];
        pt.x += pt.vx * dt;
        pt.y += pt.vy * dt;
        pt.life -= dt;
        if (pt.life <= 0) this.particles.splice(i, 1);
      }
    }

    checkLevelClear() {
      if (this.currentLevel.targets.length === 0) {
        playTone(880, 0.35, 'sine', 0.3);
        setTimeout(() => {
          if (typeof showToast === 'function') {
            showToast('🎉 SECTOR CLEARED! 恭喜达成三星引力弹弓！', 4);
          }
          this.levelIndex = (this.levelIndex + 1) % this.levels.length;
          this.loadLevel(this.levelIndex);
        }, 1200);
      }
    }

    render() {
      const ctx = this.ctx;
      const w = this.canvas.width;
      const h = this.canvas.height;
      const lvl = this.currentLevel;

      ctx.clearRect(0, 0, w, h);

      // 1. Starry Backdrop
      ctx.fillStyle = '#060a14';
      ctx.fillRect(0, 0, w, h);

      // 2. Planets & Gravity Well Atmospheres
      for (const p of lvl.planets) {
        ctx.save();
        // Atmospheric Gravity Rim
        const atmoGrad = ctx.createRadialGradient(p.x, p.y, p.r, p.x, p.y, p.atmoR);
        atmoGrad.addColorStop(0, p.atmoColor);
        atmoGrad.addColorStop(1, 'rgba(0, 0, 0, 0)');
        ctx.fillStyle = atmoGrad;
        ctx.beginPath();
        ctx.arc(p.x, p.y, p.atmoR, 0, Math.PI * 2);
        ctx.fill();

        ctx.strokeStyle = p.atmoColor;
        ctx.lineWidth = 1;
        ctx.setLineDash([4, 6]);
        ctx.beginPath();
        ctx.arc(p.x, p.y, p.atmoR, 0, Math.PI * 2);
        ctx.stroke();

        // Planet Body
        ctx.fillStyle = p.coreColor;
        ctx.beginPath();
        ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
        ctx.fill();
        ctx.strokeStyle = 'rgba(255, 255, 255, 0.4)';
        ctx.lineWidth = 2;
        ctx.stroke();
        ctx.restore();
      }

      // 3. Targets (Pirate Listening Posts)
      for (const t of lvl.targets) {
        ctx.save();
        ctx.fillStyle = '#10b981';
        ctx.beginPath();
        ctx.arc(t.x, t.y, t.r, 0, Math.PI * 2);
        ctx.fill();

        ctx.strokeStyle = '#34d399';
        ctx.lineWidth = 2;
        ctx.stroke();

        ctx.font = '16px serif';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText('🐷', t.x, t.y);

        // HP bar
        ctx.fillStyle = 'rgba(0, 0, 0, 0.6)';
        ctx.fillRect(t.x - 16, t.y - t.r - 8, 32, 4);
        ctx.fillStyle = '#10b981';
        ctx.fillRect(t.x - 16, t.y - t.r - 8, (t.hp / t.maxHp) * 32, 4);
        ctx.restore();
      }

      // 4. Slingshot Trajectory Projection (When Dragging)
      const s = lvl.slingshot;
      if (this.dragState.isDragging && this.currentBird) {
        ctx.save();
        const dx = s.x - this.dragState.dragX;
        const dy = s.y - this.dragState.dragY;
        const impulse = 6.8;

        let simX = s.x, simY = s.y;
        let simVx = dx * impulse, simVy = dy * impulse;
        const dt = 0.02;

        ctx.fillStyle = '#ffd700';
        for (let step = 0; step < 75; step++) {
          for (const p of lvl.planets) {
            const pdx = p.x - simX;
            const pdy = p.y - simY;
            const distSq = pdx * pdx + pdy * pdy;
            const dist = Math.sqrt(distSq);
            if (dist < p.atmoR) {
              simVx *= 0.985;
              simVy *= 0.985;
              const force = (p.mass / Math.max(900, distSq)) * 14;
              simVx += (pdx / dist) * force * dt;
              simVy += (pdy / dist) * force * dt;
            }
          }
          simX += simVx * dt;
          simY += simVy * dt;

          if (step % 3 === 0) {
            const alpha = 1.0 - (step / 75);
            ctx.fillStyle = `rgba(255, 215, 0, ${alpha * 0.8})`;
            ctx.beginPath();
            ctx.arc(simX, simY, 2.5, 0, Math.PI * 2);
            ctx.fill();
          }
        }

        // Draw Slingshot Bands
        ctx.strokeStyle = '#d97706';
        ctx.lineWidth = 3.5;
        ctx.beginPath();
        ctx.moveTo(s.x - 12, s.y - 12);
        ctx.lineTo(this.dragState.dragX, this.dragState.dragY);
        ctx.lineTo(s.x + 12, s.y - 12);
        ctx.stroke();
        ctx.restore();
      }

      // 5. Slingshot Anchor Stand
      ctx.fillStyle = '#64748b';
      ctx.fillRect(s.x - 4, s.y, 8, 48);
      ctx.strokeStyle = '#94a3b8';
      ctx.strokeRect(s.x - 4, s.y, 8, 48);

      // 6. Flying Probes & Trails
      for (const b of this.flyingBirds) {
        // Draw Trail
        ctx.strokeStyle = 'rgba(255, 215, 0, 0.4)';
        ctx.lineWidth = 1.5;
        ctx.beginPath();
        for (let i = 0; i < b.path.length; i++) {
          const pt = b.path[i];
          if (i === 0) ctx.moveTo(pt.x, pt.y);
          else ctx.lineTo(pt.x, pt.y);
        }
        ctx.stroke();

        // Draw Bird Probe
        ctx.save();
        ctx.translate(b.x, b.y);
        ctx.fillStyle = b.type === 'red' ? '#ef4444' : (b.type === 'blue' ? '#38bdf8' : '#1e1b4b');
        ctx.beginPath();
        ctx.arc(0, 0, b.r, 0, Math.PI * 2);
        ctx.fill();
        ctx.strokeStyle = '#f1f5f9';
        ctx.lineWidth = 1.5;
        ctx.stroke();
        ctx.restore();
      }

      // 7. Ready Bird in Slingshot
      if (this.currentBird && this.currentBird.state === 'ready') {
        const bx = this.dragState.isDragging ? this.dragState.dragX : s.x;
        const by = this.dragState.isDragging ? this.dragState.dragY : s.y;
        ctx.save();
        ctx.fillStyle = this.currentBird.type === 'red' ? '#ef4444' : (this.currentBird.type === 'blue' ? '#38bdf8' : '#1e1b4b');
        ctx.beginPath();
        ctx.arc(bx, by, this.currentBird.r, 0, Math.PI * 2);
        ctx.fill();
        ctx.strokeStyle = '#f1f5f9';
        ctx.lineWidth = 1.5;
        ctx.stroke();
        ctx.restore();
      }

      // 8. Particles
      for (const pt of this.particles) {
        ctx.fillStyle = pt.color;
        ctx.beginPath();
        ctx.arc(pt.x, pt.y, pt.size * (pt.life / pt.maxLife), 0, Math.PI * 2);
        ctx.fill();
      }
    }
  }

  window.OrbitalSlingshot = new OrbitalSlingshotGame();

})();
</script>
'''

if __name__ == '__main__':
    with open('starfield-pub/starfield.html', 'rb') as f:
        content = f.read()

    expansion = get_expansion_script().encode('utf-8')
    crlf_expansion = expansion.replace(b'\r\n', b'\n').replace(b'\n', b'\r\n')

    # Append before </body>
    target = b'</body>'
    if target not in content:
        print("Error: </body> not found")
        sys.exit(1)

    content = content.replace(target, crlf_expansion + b'\r\n</body>', 1)

    with open('starfield-pub/starfield.html', 'wb') as f:
        f.write(content)

    # Mirror to android assets
    with open('starfield-pub/android/app/src/main/assets/starfield.html', 'wb') as f:
        f.write(content)

    print("Injected Void Extraction and Orbital Slingshot engines successfully!")
