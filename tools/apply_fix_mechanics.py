# -*- coding: utf-8 -*-
import os
import sys

new_code = '''const StarfieldSonar = {
  currentTarget: null,
  activeSonarRings: [],
  lastScanTime: -9999,
  btnElement: null,
  audioCtx: null,

  init() {
    if (this._inited) return;
    this._inited = true;
    window.addEventListener('keydown', (e) => {
      if ((typeof currentMode !== 'undefined' && currentMode !== 'cruise') || (typeof window !== 'undefined' && window.currentMode && window.currentMode !== 'cruise')) return;
      if ((e.key.toLowerCase() === 'f' || e.code === 'KeyF') && !e.repeat) {
        this.triggerScan();
      }
    });
  },

  update(dt) {
    if (!this._inited) this.init();
    if (!fleet || !fleet[LEAD]) return;
    const leadPos = craftWorld(fleet[LEAD]);

    let candidate = null;
    let minCandidateDist = 1e9;

    const massesPool = (typeof window !== 'undefined' && Array.isArray(window.activeMasses) && window.activeMasses.length > 0) ? window.activeMasses : (typeof activeMasses !== 'undefined' && Array.isArray(activeMasses) ? activeMasses : []);
    for (let i = 0; i < massesPool.length; i++) {
      const m = massesPool[i];
      if (!m || (!m.w && m.kind !== 1 && m.kind !== 8 && m.kind !== 6 && m.kind !== 4)) continue;
      if (!Number.isFinite(m.x) || !Number.isFinite(m.y) || !Number.isFinite(m.z)) continue;
      const dx = m.x - leadPos[0], dy = m.y - leadPos[1], dz = m.z - leadPos[2];
      const dist = Math.hypot(dx, dy, dz);
      if (dist > 800 && dist < 32000 && dist < minCandidateDist) {
        minCandidateDist = dist;
        candidate = m;
      }
    }

    this.currentTarget = candidate;
    // Completely remove bottom-center HUD button to keep screen pure & unobstructed
    const oldBtn = document.getElementById('sf-sonar-lock-btn');
    if (oldBtn) oldBtn.remove();

    for (let i = this.activeSonarRings.length - 1; i >= 0; i--) {
      const ring = this.activeSonarRings[i];
      ring.r += dt * 4800;
      ring.life -= dt * 0.9;
      if (ring.life <= 0 || ring.r > ring.maxR * 1.2) {
        this.activeSonarRings.splice(i, 1);
      }
    }
  },

  updateHUDButton(target) {
    // Non-obstructive: No bottom button created. Press [F] or tap celestial body to scan.
    const btn = document.getElementById('sf-sonar-lock-btn');
    if (btn) btn.remove();
  },

  triggerScan() {
    if (!this.currentTarget) {
      if (typeof showToast === 'function') showToast('当前空域未检测到可测绘天体信号', 3); else if (typeof window.toast === 'function') window.toast('当前空域未检测到可测绘天体信号', 3);
      return;
    }
    const target = this.currentTarget;
    const now = performance.now();
    if (now - this.lastScanTime < 1500) return;
    this.lastScanTime = now;

    const leadPos = craftWorld(fleet[LEAD]);
    const dx = target.x - leadPos[0], dy = target.y - leadPos[1], dz = target.z - leadPos[2];
    const dist = Math.hypot(dx, dy, dz) || 1000;

    this.activeSonarRings.push({
      start: [...leadPos],
      target: [target.x, target.y, target.z],
      r: 10,
      maxR: dist,
      life: 1.2
    });

    try {
      const AudioCtx = window.AudioContext || window.webkitAudioContext;
      if (AudioCtx) {
        if (!this.audioCtx || this.audioCtx.state === 'closed') {
          this.audioCtx = new AudioCtx();
        } else if (this.audioCtx.state === 'suspended') {
          this.audioCtx.resume();
        }
        const ctx = this.audioCtx;
        const osc = ctx.createOscillator();
        const gain = ctx.createGain();
        osc.type = 'sine';
        osc.frequency.setValueAtTime(880, ctx.currentTime);
        osc.frequency.exponentialRampToValueAtTime(1760, ctx.currentTime + 0.35);
        gain.gain.setValueAtTime(0.18, ctx.currentTime);
        gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.9);
        osc.connect(gain);
        gain.connect(ctx.destination);
        osc.onended = () => {
          try { osc.disconnect(); gain.disconnect(); } catch(e) {}
        };
        osc.start();
        osc.stop(ctx.currentTime + 0.9);
      }
    } catch(e) {}

    const stardust = 150 + Math.floor(Math.random() * 120);
    const targetName = target.name || (target.w && target.w.name) || '深空未知天体';

    const foundCore = Math.random() < 0.22;
    if (foundCore && window.StarfieldHatch && typeof window.StarfieldHatch.addCores === 'function') {
      window.StarfieldHatch.addCores(1);
      const msg = `[天体共振] 成功测绘 ${targetName} · 捕获未开采星核 × 1! 🌌`;
      if (typeof showToast === 'function') showToast(msg, 4);
      else if (typeof window.toast === 'function') window.toast(msg, 4);
    } else {
      const msg = `[巡天测绘完成] 测绘 ${targetName} · 获得星尘 +${stardust}`;
      if (typeof showToast === 'function') showToast(msg, 3);
      else if (typeof window.toast === 'function') window.toast(msg, 3);
    }

    if (typeof Codex !== 'undefined' && Codex.checkCelestialEncounter) {
      Codex.checkCelestialEncounter(target);
    }
  },

  draw(c) {
    if (!this.activeSonarRings.length) return;
    c.save();
    for (let i = 0; i < this.activeSonarRings.length; i++) {
      const ring = this.activeSonarRings[i];
      const prog = clamp(ring.r / Math.max(ring.maxR, 1), 0, 1);
      const currPos = [
        ring.start[0] + (ring.target[0] - ring.start[0]) * prog,
        ring.start[1] + (ring.target[1] - ring.start[1]) * prog,
        ring.start[2] + (ring.target[2] - ring.start[2]) * prog
      ];
      const q = project(currPos);
      if (!q || q[2] <= 0) continue;
      const screenR = clamp((350 / q[2]) * ring.r * 0.08, 12, 280);
      c.beginPath();
      c.arc(q[0], q[1], screenR, 0, TAU);
      c.strokeStyle = `rgba(56, 189, 248, ${(ring.life * 0.7).toFixed(2)})`;
      c.lineWidth = 2.5;
      c.shadowColor = '#38bdf8';
      c.shadowBlur = 15;
      c.stroke();
    }
    c.restore();
  }
};
window.StarfieldSonar = StarfieldSonar;

/* ============================================================================
 * 3D IN-FLIGHT VOID EXTRACTION (深空搜打撤 · 空间域沉浸融入)
 * ============================================================================ */
const StarfieldInFlightExtraction = {
  derelicts: [],
  pirates: [],
  lasers: [],
  bursts: [],
  sparks: [],
  evacGate: null,
  cargo: [],
  maxCargo: 6,
  securedCredits: 0,
  salvageTarget: null,
  salvageProgress: 0,
  lastSpawnTravel: 0,
  lastAmbushTime: 0,
  hudElement: null,
  lootBtnElement: null,
  audioCtx: null,
  tractorPulse: 0,
  fleetShieldFlare: 0,
  escortLaserTimer: 0,

  init() {
    if (this._inited) return;
    this._inited = true;
    window.addEventListener('keydown', (e) => {
      if (e.target && (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA' || e.target.isContentEditable)) return;
      if ((typeof currentMode !== 'undefined' && currentMode !== 'cruise') || (typeof window !== 'undefined' && window.currentMode && window.currentMode !== 'cruise')) return;
      if ((e.key.toLowerCase() === 'e' || e.code === 'KeyE') && !e.repeat) {
        if (this.salvageTarget) this.fastLoot();
      }
    });
    this.createHUD();
  },

  playChirp(type) {
    try {
      const AudioCtx = window.AudioContext || window.webkitAudioContext;
      if (!AudioCtx) return;
      if (!this.audioCtx) this.audioCtx = new AudioCtx();
      if (this.audioCtx.state === 'suspended') {
        this.audioCtx.resume().catch(() => {});
      }
      const ctx = this.audioCtx;
      const osc = ctx.createOscillator();
      const gain = ctx.createGain();
      if (type === 'tractor') {
        osc.type = 'sine';
        osc.frequency.setValueAtTime(520, ctx.currentTime);
        osc.frequency.exponentialRampToValueAtTime(880, ctx.currentTime + 0.16);
        gain.gain.setValueAtTime(0.06, ctx.currentTime);
        gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.16);
      } else if (type === 'loot') {
        osc.type = 'triangle';
        osc.frequency.setValueAtTime(587.33, ctx.currentTime);
        osc.frequency.exponentialRampToValueAtTime(1174.66, ctx.currentTime + 0.32);
        gain.gain.setValueAtTime(0.12, ctx.currentTime);
        gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.32);
      } else if (type === 'evac') {
        osc.type = 'sine';
        osc.frequency.setValueAtTime(261.63, ctx.currentTime);
        osc.frequency.linearRampToValueAtTime(523.25, ctx.currentTime + 0.22);
        osc.frequency.linearRampToValueAtTime(1046.5, ctx.currentTime + 0.55);
        gain.gain.setValueAtTime(0.14, ctx.currentTime);
        gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.55);
      } else if (type === 'laser') {
        osc.type = 'sawtooth';
        osc.frequency.setValueAtTime(980, ctx.currentTime);
        osc.frequency.exponentialRampToValueAtTime(220, ctx.currentTime + 0.12);
        gain.gain.setValueAtTime(0.05, ctx.currentTime);
        gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.12);
      }
      osc.connect(gain);
      gain.connect(ctx.destination);
      osc.onended = () => {
        try { osc.disconnect(); gain.disconnect(); } catch(e) {}
      };
      osc.start();
      osc.stop(ctx.currentTime + (type === 'evac' ? 0.55 : 0.32));
    } catch(e) {}
  },

  createHUD() {
    if (typeof document === 'undefined') return;
    if (!document.getElementById('sf-inflight-extract-hud')) {
      const hud = document.createElement('div');
      hud.id = 'sf-inflight-extract-hud';
      hud.style.cssText = `
        position: fixed;
        top: calc(max(env(safe-area-inset-top, 0px), 16px) + 78px);
        right: 18px;
        z-index: 105;
        background: linear-gradient(135deg, rgba(15, 23, 42, 0.88) 0%, rgba(8, 14, 26, 0.96) 100%);
        border: 1px solid rgba(56, 189, 248, 0.45);
        border-radius: 12px;
        padding: 8px 12px;
        color: #e0f2fe;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.55), 0 0 16px rgba(56, 189, 248, 0.22);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
        font-size: 10.5px;
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
  },

  update(dt) {
    if (!this._inited) this.init();
    if (typeof window !== 'undefined' && typeof window.travel === 'number' && Math.abs(window.travel - travel) > 500) {
      travel = window.travel;
    }
    if (typeof window !== 'undefined') window.travel = travel;

    if (!fleet || !fleet[LEAD]) return;
    const leadPos = craftWorld(fleet[LEAD]);
    const leadTravel = travel;

    if (this.fleetShieldFlare > 0) this.fleetShieldFlare = Math.max(0, this.fleetShieldFlare - dt * 2.5);

    // Procedurally spawn space encounters along flight path every ~8,000 units
    if (this.lastSpawnTravel === 0 || leadTravel - this.lastSpawnTravel > 8000 || this.derelicts.length === 0) {
      this.lastSpawnTravel = (leadTravel || 1);
      const spawnZ = (leadTravel || 0) + 3600 + Math.random() * 4200;
      const rx = routeX(spawnZ) + (Math.random() - 0.5) * 2800;
      const ry = courseY(spawnZ) + (Math.random() - 0.5) * 1400;

      const types = ['wreck', 'debris', 'outpost', 'distress'];
      const chosenType = types[Math.floor(Math.random() * types.length)];
      let typeName = '';
      if (chosenType === 'wreck') {
        typeName = Math.random() < 0.5 ? '远古科考驱逐舰残骸' : '深空武装巡洋舰废墟';
      } else if (chosenType === 'debris') {
        typeName = Math.random() < 0.5 ? '第Ⅶ星区星际战损残骸区' : '碎裂钛金甲板残骸带';
      } else if (chosenType === 'outpost') {
        typeName = Math.random() < 0.5 ? '先驱者废弃深空中继站' : '先驱者废弃观测哨所';
      } else {
        typeName = Math.random() < 0.5 ? '遇难逃生舱 SOS 应急道标' : '未知深空求救应答器';
      }
      
      const lootTable = [
        { name: '高维先驱遗物', icon: '🔮', value: 950, tier: 'legendary' },
        { name: '反物质湮灭核心', icon: '⚛️', value: 880, tier: 'legendary' },
        { name: '暗物质折跃燃料', icon: '🌌', value: 620, tier: 'epic' },
        { name: '先驱聚能晶核', icon: '💎', value: 560, tier: 'epic' },
        { name: '量子跃迁线圈', icon: '🌀', value: 420, tier: 'rare' },
        { name: '高维星图磁盘', icon: '💾', value: 360, tier: 'rare' },
        { name: '精炼复合装甲板', icon: '🛡️', value: 240, tier: 'uncommon' },
        { name: '离子推进废料', icon: '🔋', value: 160, tier: 'common' }
      ];
      const lootItem = lootTable[Math.floor(Math.random() * lootTable.length)];
      
      this.derelicts.push({
        id: 'derelict_' + Math.floor(spawnZ),
        type: chosenType,
        name: typeName,
        x: rx, y: ry, z: spawnZ,
        item: lootItem,
        salvaged: false,
        salvageProgress: 0,
        roll: Math.random() * Math.PI * 2,
        pitch: Math.random() * Math.PI * 2,
        spinSpeed: (Math.random() - 0.5) * 0.8,
        len: 140 + Math.random() * 80
      });

      // Singularity evacuation gate portal placed ahead
      if (!this.evacGate || this.evacGate.evacuated || this.evacGate.z < leadTravel - 10000) {
        this.evacGate = {
          x: routeX(spawnZ + 8500),
          y: courseY(spawnZ + 8500),
          z: spawnZ + 8500,
          radius: 1200,
          progress: 0,
          evacuated: false,
          imploding: 0
        };
      }
    }

    // Step ruin rotations
    for (const d of this.derelicts) {
      if (d.spinSpeed) d.roll = (d.roll || 0) + d.spinSpeed * dt;
    }

    // Cull old derelicts
    for (let i = this.derelicts.length - 1; i >= 0; i--) {
      if (this.derelicts[i].z < leadTravel - 12000) {
        this.derelicts.splice(i, 1);
      }
    }

    // Check closest derelict for salvage
    let nearest = null;
    let minDist = 1e9;
    for (const d of this.derelicts) {
      if (d.salvaged) continue;
      const dist = Math.hypot(d.x - leadPos[0], d.y - leadPos[1], d.z - leadPos[2]);
      if (dist < 4600 && dist < minDist) {
        minDist = dist;
        nearest = d;
      }
    }

    this.salvageTarget = (minDist < 2600) ? nearest : null;

    if (this.salvageTarget) {
      this.salvageProgress = Math.min(1.0, this.salvageProgress + dt * 0.48);
      this.tractorPulse = (this.tractorPulse + dt * 5.0) % 1.0;
      if (this.salvageProgress >= 1.0) {
        this.fastLoot();
      }
    } else {
      this.salvageProgress = 0;
    }

    // Check Singularity Extraction Gate
    if (this.evacGate) {
      if (this.evacGate.imploding > 0) {
        this.evacGate.imploding -= dt * 1.5;
        if (this.evacGate.imploding <= 0) {
          this.evacGate = null;
        }
      } else if (!this.evacGate.evacuated) {
        const gDist = Math.hypot(this.evacGate.x - leadPos[0], this.evacGate.y - leadPos[1], this.evacGate.z - leadPos[2]);
        if (gDist < 2400) {
          this.evacGate.progress = Math.min(1.0, this.evacGate.progress + dt * 0.65);
          if (this.evacGate.progress >= 1.0) {
            this.triggerEvacuation();
          }
        } else {
          this.evacGate.progress = Math.max(0, this.evacGate.progress - dt * 0.2);
        }
      }
    }

    // Hostile pirate patrols & dogfight simulation
    const nowSec = performance.now() * 0.001;
    if (this.salvageTarget && nowSec - this.lastAmbushTime > 32 && Math.random() < 0.02) {
      this.lastAmbushTime = nowSec;
      this.spawnPiratePatrol(leadPos, 2);
    }

    this.escortLaserTimer = Math.max(0, this.escortLaserTimer - dt);

    for (let i = this.pirates.length - 1; i >= 0; i--) {
      const p = this.pirates[i];
      p.life -= dt;
      p.fireCd = (p.fireCd || 0) - dt;
      
      // Orbiting attack vector around lead ship
      p.phase = (p.phase || 0) + dt * 1.5;
      p.x += Math.sin(p.phase) * 75 * dt;
      p.y += Math.cos(p.phase * 0.8) * 45 * dt;
      const desiredZ = leadPos[2] + 1600 + Math.sin(p.phase) * 600;
      p.z += (desiredZ - p.z) * 1.2 * dt;

      // Pirate fires crimson laser pulse at fleet
      if (p.fireCd <= 0) {
        p.fireCd = 1.3 + Math.random() * 0.7;
        this.fleetShieldFlare = 1.0;
        this.playChirp('laser');
        this.lasers.push({
          x0: p.x, y0: p.y, z0: p.z,
          x1: leadPos[0] + (Math.random() - 0.5) * 80,
          y1: leadPos[1] + (Math.random() - 0.5) * 40,
          z1: leadPos[2],
          color: '#f43f5e',
          life: 0.28,
          maxLife: 0.28
        });
      }

      // Escorts retaliate against pirate
      if (this.escortLaserTimer <= 0 && fleet.length > 1) {
        this.escortLaserTimer = 0.6;
        const escortCraft = fleet[1 + (i % (fleet.length - 1))];
        if (escortCraft) {
          const ep = craftWorld(escortCraft);
          p.hp = (p.hp || 3) - 1;
          this.lasers.push({
            x0: ep[0], y0: ep[1], z0: ep[2],
            x1: p.x, y1: p.y, z1: p.z,
            color: '#38bdf8',
            life: 0.28,
            maxLife: 0.28
          });
        }
      }

      if (p.life <= 0 || (p.hp !== undefined && p.hp <= 0)) {
        // Destroyed: spawn explosion burst and spark debris
        this.bursts.push({
          x: p.x, y: p.y, z: p.z,
          size: 55,
          life: 0.45,
          maxLife: 0.45
        });
        for (let s = 0; s < 14; s++) {
          this.sparks.push({
            x: p.x, y: p.y, z: p.z,
            vx: (Math.random() - 0.5) * 360,
            vy: (Math.random() - 0.5) * 360,
            vz: (Math.random() - 0.5) * 360,
            life: 1.2
          });
        }
        this.pirates.splice(i, 1);
      }
    }

    // Step combat lasers
    for (let l = this.lasers.length - 1; l >= 0; l--) {
      this.lasers[l].life -= dt;
      if (this.lasers[l].life <= 0) this.lasers.splice(l, 1);
    }

    // Step explosion bursts
    for (let b = this.bursts.length - 1; b >= 0; b--) {
      this.bursts[b].life -= dt;
      if (this.bursts[b].life <= 0) this.bursts.splice(b, 1);
    }

    // Step spark particles
    for (let i = this.sparks.length - 1; i >= 0; i--) {
      const sp = this.sparks[i];
      sp.life -= dt;
      sp.x += sp.vx * dt;
      sp.y += sp.vy * dt;
      sp.z += sp.vz * dt;
      if (sp.life <= 0) this.sparks.splice(i, 1);
    }

    this.updateHUD(leadPos);
  },

  updateHUD(leadPos) {
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
  },

  fastLoot() {
    if (!this.salvageTarget || this.salvageTarget.salvaged) return;
    const d = this.salvageTarget;
    d.salvaged = true;
    this.salvageProgress = 0;
    this.salvageTarget = null;

    if (this.cargo.length < this.maxCargo) {
      this.cargo.push(d.item);
    }
    const val = d.item.value;
    this.playChirp('loot');
    if (typeof navigator !== 'undefined' && (navigator.userActivation ? navigator.userActivation.hasBeenActive : true) && navigator.vibrate) {
      try { navigator.vibrate([40, 30, 60]); } catch(e) {}
    }

    const msg = `[战利品搜寻] 成功回收【${d.item.name}】(+${val} ST)！当前货舱 ${this.cargo.length}/${this.maxCargo}`;
    if (typeof showToast === 'function') showToast(msg, 3.5);
    else if (typeof window.toast === 'function') window.toast(msg, 3.5);

    // High-value loot attracts hostile pirate interceptor ambush
    if (d.item.tier === 'legendary' || d.item.tier === 'epic' || Math.random() < 0.4) {
      if (fleet && fleet[LEAD]) {
        const leadPos = craftWorld(fleet[LEAD]);
        this.spawnPiratePatrol(leadPos, 2);
        if (typeof gateFlash !== 'undefined') gateFlash = Math.max(gateFlash || 0, 0.4);
      }
    }
  },

  spawnPiratePatrol(leadPos, count = 1) {
    for (let k = 0; k < count; k++) {
      this.pirates.push({
        x: leadPos[0] + (Math.random() - 0.5) * 1600,
        y: leadPos[1] + (Math.random() - 0.5) * 900,
        z: leadPos[2] + 2400 + k * 400,
        hp: 3,
        life: 12.0,
        fireCd: 0.5 + k * 0.4,
        phase: Math.random() * Math.PI * 2
      });
    }
    const msg = count > 1 ? '⚠ 紧急截击: 侦测到虚空海盗突袭机群折跃包围！护航机组展开拦截！' : '⚠ 警告: 侦测到虚空海盗拦截巡逻舰！护航编队已就位！';
    if (typeof showToast === 'function') showToast(msg, 3.5);
    else if (typeof window.toast === 'function') window.toast(msg, 3.5);
  },

  triggerEvacuation() {
    if (!this.evacGate || this.evacGate.evacuated) return;
    this.evacGate.evacuated = true;
    this.evacGate.imploding = 1.0;

    let totalLoot = 0;
    for (const c of this.cargo) totalLoot += c.value;
    const count = this.cargo.length;
    this.cargo.length = 0;

    this.playChirp('evac');
    warp = Math.max(warp || 0, 3.2);
    if (typeof slingshotSurgeActive !== 'undefined') {
      slingshotSurgeActive = true;
      slingshotSurgeTimer = 4.5;
    }

    // Warp escape leaves pursuing pirates behind
    this.pirates.length = 0;

    if (count > 0) {
      const bonus = 600;
      const grandTotal = totalLoot + bonus;
      this.securedCredits += grandTotal;

      let coresGained = 0;
      if (window.StarfieldHatch && typeof window.StarfieldHatch.addCores === 'function') {
        coresGained = Math.max(1, Math.floor(grandTotal / 450));
        window.StarfieldHatch.addCores(coresGained);
      }

      const coreMsg = coresGained > 0 ? ` · 转化未开采星核 × ${coresGained}` : '';
      const msg = `✦ 成功穿透奇点折跃门！安全撤离 ${count} 件物资，星尘 +${grandTotal} ST${coreMsg}！✦`;
      if (typeof showToast === 'function') showToast(msg, 4.5);
      else if (typeof window.toast === 'function') window.toast(msg, 4.5);
    } else {
      const msg = `✦ 成功穿透奇点折跃门！跃迁航道畅通，完成战术折跃冲刺！✦`;
      if (typeof showToast === 'function') showToast(msg, 3.5);
      else if (typeof window.toast === 'function') window.toast(msg, 3.5);
    }
  },

  draw(c) {
    if (!fleet || !fleet[LEAD]) return;
    const leadPos = craftWorld(fleet[LEAD]);
    const leadQ = project(leadPos);

    // 1. Draw 3D Derelict & Ruins with Distinctive Geometry & Tractor Beam
    for (const d of this.derelicts) {
      if (d.salvaged) continue;
      const q = project([d.x, d.y, d.z]);
      if (!q || q[2] <= 0 || q[2] > 45000) continue;

      const sz = Math.max(16, Math.min(105, (400 / q[2]) * 65));
      c.save();
      c.translate(q[0], q[1]);
      c.rotate(d.roll || 0);

      if (d.type === 'debris') {
        // Battle Debris: multi-fragment scattered scrap metal & armor chunks
        c.fillStyle = '#334155';
        c.strokeStyle = '#94a3b8';
        c.lineWidth = 1.2;
        // Scrap plate A
        c.beginPath();
        c.moveTo(-sz * 0.8, -sz * 0.4);
        c.lineTo(-sz * 0.2, -sz * 0.7);
        c.lineTo(sz * 0.1, -sz * 0.3);
        c.lineTo(-sz * 0.5, -sz * 0.1);
        c.closePath();
        c.fill(); c.stroke();
        // Scrap plate B
        c.beginPath();
        c.moveTo(sz * 0.2, sz * 0.1);
        c.lineTo(sz * 0.8, sz * 0.3);
        c.lineTo(sz * 0.6, sz * 0.7);
        c.lineTo(sz * 0.0, sz * 0.5);
        c.closePath();
        c.fill(); c.stroke();
        // Twisting girder
        c.strokeStyle = '#fbbf24';
        c.lineWidth = 1.5;
        c.beginPath();
        c.moveTo(-sz * 0.3, sz * 0.2);
        c.lineTo(sz * 0.4, -sz * 0.2);
        c.stroke();
      } else if (d.type === 'outpost') {
        // Forerunner Outpost: Glowing geometric crystalline core with rotating pylons
        const pRot = performance.now() * 0.001;
        c.rotate(pRot * 0.5);
        // Outer hexagonal ring
        c.strokeStyle = '#38bdf8';
        c.lineWidth = 1.8;
        c.beginPath();
        for (let a = 0; a < 6; a++) {
          const ang = a * (Math.PI / 3);
          const px = Math.cos(ang) * sz * 0.75;
          const py = Math.sin(ang) * sz * 0.75;
          if (a === 0) c.moveTo(px, py); else c.lineTo(px, py);
        }
        c.closePath();
        c.stroke();
        // Crystalline Core
        c.fillStyle = '#a855f7';
        c.shadowColor = '#c084fc';
        c.shadowBlur = 14;
        c.beginPath();
        c.arc(0, 0, sz * 0.28, 0, TAU);
        c.fill();
        c.shadowBlur = 0;
      } else if (d.type === 'distress') {
        // Distress Beacon Capsule
        c.fillStyle = '#ef4444';
        c.strokeStyle = '#fca5a5';
        c.lineWidth = 1.4;
        c.beginPath();
        c.arc(0, 0, sz * 0.32, 0, TAU);
        c.fill(); c.stroke();
        // Concentric SOS radar pulses expanding into space
        const pulse = (performance.now() * 0.002) % 1.0;
        c.strokeStyle = `rgba(239, 68, 68, ${(1 - pulse).toFixed(2)})`;
        c.lineWidth = 2.0;
        c.beginPath();
        c.arc(0, 0, sz * (0.4 + pulse * 1.2), 0, TAU);
        c.stroke();
      } else {
        // Starship Wreckage: Fragmented hull geometry
        c.fillStyle = '#1e293b';
        c.strokeStyle = '#64748b';
        c.lineWidth = 1.4;
        c.beginPath();
        c.moveTo(-sz * 0.9, -sz * 0.25);
        c.lineTo(sz * 0.5, -sz * 0.45);
        c.lineTo(sz * 0.85, 0);
        c.lineTo(sz * 0.35, sz * 0.4);
        c.lineTo(-sz * 0.8, sz * 0.3);
        c.closePath();
        c.fill(); c.stroke();

        // Armor hazard plating
        c.fillStyle = '#fbbf24';
        c.beginPath();
        c.moveTo(-sz * 0.3, -sz * 0.3);
        c.lineTo(-sz * 0.1, -sz * 0.33);
        c.lineTo(-sz * 0.25, -sz * 0.1);
        c.closePath();
        c.fill();

        // Fractured solar wing
        c.fillStyle = '#1e3a8a';
        c.strokeStyle = '#38bdf8';
        c.lineWidth = 1.0;
        c.beginPath();
        c.rect(-sz * 0.7, -sz * 0.75, sz * 0.55, sz * 0.28);
        c.fill(); c.stroke();

        // Pulsing reactor core
        const pulse = 0.85 + Math.sin(performance.now() * 0.006) * 0.25;
        c.beginPath();
        c.arc(0, 0, sz * 0.22 * pulse, 0, TAU);
        c.fillStyle = '#38bdf8';
        c.shadowColor = '#38bdf8';
        c.shadowBlur = 14;
        c.fill();
        c.shadowBlur = 0;
      }
      c.restore();

      // Tactical Wireframe Bracket & Telemetry HUD
      c.save();
      c.translate(q[0], q[1]);
      c.strokeStyle = 'rgba(56, 189, 248, 0.75)';
      c.lineWidth = 1.5;
      const bSz = sz * 0.95;
      c.beginPath();
      c.moveTo(-bSz, -bSz + 6); c.lineTo(-bSz, -bSz); c.lineTo(-bSz + 6, -bSz);
      c.moveTo(bSz - 6, -bSz); c.lineTo(bSz, -bSz); c.lineTo(bSz, -bSz + 6);
      c.moveTo(-bSz, bSz - 6); c.lineTo(-bSz, bSz); c.lineTo(-bSz + 6, bSz);
      c.moveTo(bSz - 6, bSz); c.lineTo(bSz, bSz); c.lineTo(bSz, -bSz + 6);
      c.stroke();

      c.font = '10px ui-monospace, sans-serif';
      c.fillStyle = '#38bdf8';
      c.textAlign = 'center';
      const distM = Math.round(q[2]);
      const typeTag = d.type === 'debris' ? '[战损残骸]' : (d.type === 'outpost' ? '[先驱哨所]' : (d.type === 'distress' ? '[求救信号]' : '[空间沉船]'));
      c.fillText(`${typeTag} ${d.name} · ${distM}m`, 0, -bSz - 8);
      c.restore();

      // 3D Automated Tractor Beam & Recovery Progress Bar
      if (this.salvageTarget === d) {
        c.save();
        const originQ = leadQ || [camera.cx || ((typeof W !== 'undefined' ? W : 400) * 0.5), (typeof H !== 'undefined' ? H : 600) * 0.92];
        // Dual braided luminous tractor beam
        const tOffset = Math.sin(performance.now() * 0.01) * 6;
        c.beginPath();
        c.moveTo(originQ[0], originQ[1]);
        c.quadraticCurveTo((originQ[0] + q[0]) * 0.5 + tOffset, (originQ[1] + q[1]) * 0.5 - tOffset, q[0], q[1]);
        c.strokeStyle = 'rgba(56, 189, 248, 0.88)';
        c.lineWidth = 2.4;
        c.setLineDash([8, 4]);
        c.shadowColor = '#38bdf8';
        c.shadowBlur = 14;
        c.stroke();

        c.beginPath();
        c.moveTo(originQ[0], originQ[1]);
        c.quadraticCurveTo((originQ[0] + q[0]) * 0.5 - tOffset, (originQ[1] + q[1]) * 0.5 + tOffset, q[0], q[1]);
        c.strokeStyle = 'rgba(251, 191, 36, 0.75)';
        c.lineWidth = 1.4;
        c.stroke();
        c.restore();

        // 3D Progress Bar
        c.save();
        c.translate(q[0], q[1] + bSz + 14);
        c.fillStyle = 'rgba(15, 23, 42, 0.85)';
        c.fillRect(-50, 0, 100, 6);
        c.fillStyle = '#38bdf8';
        c.fillRect(-50, 0, 100 * this.salvageProgress, 6);
        c.strokeStyle = 'rgba(56, 189, 248, 0.6)';
        c.strokeRect(-50, 0, 100, 6);
        c.font = '9.5px ui-monospace, sans-serif';
        c.fillStyle = '#e0f2fe';
        c.textAlign = 'center';
        c.fillText(`牵引回收中 ${Math.round(this.salvageProgress * 100)}% [E]`, 0, 16);
        c.restore();
      }
    }

    // 2. Draw Hostile Pirate Interceptors & Tactical Dogfight Fire
    for (const p of this.pirates) {
      const pq = project([p.x, p.y, p.z]);
      if (!pq || pq[2] <= 0 || pq[2] > 42000) continue;

      const psz = Math.max(14, Math.min(90, (400 / pq[2]) * 55));
      c.save();
      c.translate(pq[0], pq[1]);

      // Tactical Red Diamond Bracket
      c.strokeStyle = 'rgba(244, 63, 94, 0.88)';
      c.lineWidth = 1.6;
      c.beginPath();
      c.moveTo(0, -psz * 0.95);
      c.lineTo(psz * 0.95, 0);
      c.lineTo(0, psz * 0.95);
      c.lineTo(-psz * 0.95, 0);
      c.closePath();
      c.stroke();

      // Pirate Raider Fighter Silhouette
      c.fillStyle = '#0f172a';
      c.strokeStyle = '#f43f5e';
      c.lineWidth = 1.5;
      c.beginPath();
      c.moveTo(0, -psz * 0.65);
      c.lineTo(psz * 0.55, psz * 0.45);
      c.lineTo(0, psz * 0.2);
      c.lineTo(-psz * 0.55, psz * 0.45);
      c.closePath();
      c.fill(); c.stroke();

      // Twin red glowing engine thrusters
      c.beginPath();
      c.arc(-psz * 0.22, psz * 0.45, 3.5, 0, TAU);
      c.arc(psz * 0.22, psz * 0.45, 3.5, 0, TAU);
      c.fillStyle = '#f43f5e';
      c.shadowColor = '#f43f5e';
      c.shadowBlur = 10;
      c.fill();
      c.shadowBlur = 0;

      c.font = '10px ui-monospace, sans-serif';
      c.fillStyle = '#f87171';
      c.textAlign = 'center';
      c.fillText(`⚠ 虚空拦截机 · ${Math.round(pq[2])}m`, 0, -psz * 0.95 - 6);
      c.restore();
    }

    // 3. Draw Active 3D Combat Lasers
    for (const l of this.lasers) {
      const A = project([l.x0, l.y0, l.z0]);
      const B = project([l.x1, l.y1, l.z1]);
      if (!A || !B || A[2] <= 0 || B[2] <= 0) continue;
      const alpha = Math.max(0, l.life / (l.maxLife || 0.28));
      c.save();
      c.beginPath();
      c.moveTo(A[0], A[1]);
      c.lineTo(B[0], B[1]);
      c.strokeStyle = l.color;
      c.globalAlpha = alpha;
      c.lineWidth = 2.4;
      c.shadowColor = l.color;
      c.shadowBlur = 12;
      c.stroke();

      c.beginPath();
      c.moveTo(A[0], A[1]);
      c.lineTo(B[0], B[1]);
      c.strokeStyle = '#ffffff';
      c.globalAlpha = alpha * 0.9;
      c.lineWidth = 1.0;
      c.stroke();
      c.restore();
    }

    // 4. Draw Active 3D Explosion Bursts
    for (const b of this.bursts) {
      const q = project([b.x, b.y, b.z]);
      if (!q || q[2] <= 0) continue;
      const prog = 1 - (b.life / (b.maxLife || 0.45));
      const r = (b.size * (0.3 + prog * 1.2)) * q[3];
      const alpha = Math.max(0, (1 - prog) * 0.85);
      c.save();
      c.beginPath();
      c.arc(q[0], q[1], r, 0, TAU);
      c.strokeStyle = `rgba(251, 146, 60, ${alpha.toFixed(2)})`;
      c.lineWidth = 2.5;
      c.shadowColor = '#fb923c';
      c.shadowBlur = 14;
      c.stroke();
      c.restore();
    }

    // Flagship Shield Flare Deflection Ripple
    if (this.fleetShieldFlare > 0 && leadQ) {
      c.save();
      c.beginPath();
      c.arc(leadQ[0], leadQ[1], 48 + (1 - this.fleetShieldFlare) * 16, 0, TAU);
      c.strokeStyle = `rgba(56, 189, 248, ${(this.fleetShieldFlare * 0.8).toFixed(2)})`;
      c.lineWidth = 3.0;
      c.shadowColor = '#38bdf8';
      c.shadowBlur = 16;
      c.stroke();
      c.restore();
    }

    // Spark Particles from destroyed craft
    for (const sp of this.sparks) {
      const sq = project([sp.x, sp.y, sp.z]);
      if (sq && sq[2] > 0) {
        c.fillStyle = '#fbbf24';
        c.fillRect(sq[0], sq[1], 2, 2);
      }
    }

    // 5. Draw Singularity Extraction Gate in 3D
    if (this.evacGate) {
      const g = this.evacGate;
      const q = project([g.x, g.y, g.z]);
      if (q && q[2] > 0 && q[2] < 55000) {
        let gR = Math.max(18, Math.min(200, (400 / q[2]) * 85));
        if (g.imploding > 0) {
          gR *= Math.max(0.05, g.imploding);
        }
        c.save();
        c.translate(q[0], q[1]);

        // Swirling golden accretion corona
        const rotTime = performance.now() * 0.0015;
        c.rotate(rotTime);
        c.beginPath();
        c.arc(0, 0, gR, 0, TAU);
        c.strokeStyle = 'rgba(251, 191, 36, 0.88)';
        c.lineWidth = 2.8;
        c.shadowColor = '#fbbf24';
        c.shadowBlur = 20;
        c.stroke();

        // Inner cosmic violet singularity disk
        c.beginPath();
        c.arc(0, 0, gR * 0.62, 0, TAU);
        c.strokeStyle = 'rgba(168, 85, 247, 0.82)';
        c.lineWidth = 2.2;
        c.shadowColor = '#a855f7';
        c.shadowBlur = 16;
        c.stroke();
        c.shadowBlur = 0;

        c.rotate(-rotTime);
        c.font = '11px ui-monospace, sans-serif';
        c.fillStyle = '#ffd700';
        c.textAlign = 'center';
        c.fillText('✦ 奇点折跃撤离门 ✦', 0, -gR - 10);
        c.restore();
      }
    }
  }
};
window.StarfieldInFlightExtraction = StarfieldInFlightExtraction;

/* ============================================================================
 * 3D PLANETARY GRAVITATIONAL SLINGSHOT & PROBE SYSTEM (天体引力弹弓与轨道探针)
 * ============================================================================ */
const StarfieldOrbitalMechanics = {
  activePlanet: null,
  slingshotArc: [],
  slingshotPeriapsisIdx: 0,
  probes: [],
  shockwaves: [],
  periapsisDist: 0,
  lastMinDist: 0,
  boostReady: false,
  slingshotCooldown: 0,
  slingshotGlowTimer: 0,
  hudElement: null,
  probeBtnElement: null,
  audioCtx: null,

  init() {
    if (this._inited) return;
    this._inited = true;
    window.addEventListener('keydown', (e) => {
      if (e.target && (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA' || e.target.isContentEditable)) return;
      if ((typeof currentMode !== 'undefined' && currentMode !== 'cruise') || (typeof window !== 'undefined' && window.currentMode && window.currentMode !== 'cruise')) return;
      if ((e.key.toLowerCase() === 'p' || e.code === 'KeyP') && !e.repeat) {
        this.launchProbe();
      }
    });

    // Touch gesture: Double-tap on canvas in flight launches telemetry probe
    let lastTapTime = 0;
    window.addEventListener('touchend', (e) => {
      if ((typeof currentMode !== 'undefined' && currentMode !== 'cruise') || (typeof window !== 'undefined' && window.currentMode && window.currentMode !== 'cruise')) return;
      const now = performance.now();
      if (now - lastTapTime < 320) {
        this.launchProbe();
        lastTapTime = 0;
      } else {
        lastTapTime = now;
      }
    }, { passive: true });

    this.createHUD();
  },

  playGravSound(type) {
    try {
      const AudioCtx = window.AudioContext || window.webkitAudioContext;
      if (!AudioCtx) return;
      if (!this.audioCtx) this.audioCtx = new AudioCtx();
      if (this.audioCtx.state === 'suspended') {
        this.audioCtx.resume().catch(() => {});
      }
      const ctx = this.audioCtx;
      const osc = ctx.createOscillator();
      const gain = ctx.createGain();
      if (type === 'slingshot') {
        osc.type = 'sawtooth';
        osc.frequency.setValueAtTime(140, ctx.currentTime);
        osc.frequency.exponentialRampToValueAtTime(540, ctx.currentTime + 0.7);
        gain.gain.setValueAtTime(0.09, ctx.currentTime);
        gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.7);
      } else if (type === 'shockwave') {
        osc.type = 'sine';
        osc.frequency.setValueAtTime(320, ctx.currentTime);
        osc.frequency.exponentialRampToValueAtTime(75, ctx.currentTime + 0.6);
        gain.gain.setValueAtTime(0.12, ctx.currentTime);
        gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.6);
      }
      osc.connect(gain);
      gain.connect(ctx.destination);
      osc.onended = () => {
        try { osc.disconnect(); gain.disconnect(); } catch(e) {}
      };
      osc.start();
      osc.stop(ctx.currentTime + 0.7);
    } catch(e) {}
  },

  createHUD() {
    if (typeof document === 'undefined') return;
    // Pure, clean HUD: probe launched via [P] hotkey or double-tap gesture; no bottom buttons
    const existingProbeBtn = document.getElementById('sf-inflight-probe-btn');
    if (existingProbeBtn) existingProbeBtn.remove();
    this.probeBtnElement = null;
  },

  update(dt) {
    if (!this._inited) this.init();
    if (typeof window !== 'undefined' && typeof window.travel === 'number' && Math.abs(window.travel - travel) > 500) {
      travel = window.travel;
    }
    if (typeof window !== 'undefined') window.travel = travel;

    if (!fleet || !fleet[LEAD]) return;
    const leadPos = craftWorld(fleet[LEAD]);

    if (this.slingshotCooldown > 0) this.slingshotCooldown -= dt;
    if (this.slingshotGlowTimer > 0) this.slingshotGlowTimer -= dt;

    let nearestMass = null;
    let minDist = 1e9;

    const massesPool = (typeof window !== 'undefined' && Array.isArray(window.activeMasses) && window.activeMasses.length > 0) ? window.activeMasses : (typeof activeMasses !== 'undefined' && Array.isArray(activeMasses) ? activeMasses : []);
    for (let i = 0; i < massesPool.length; i++) {
      const m = massesPool[i];
      if (!m || (!m.w && m.kind !== 1 && m.kind !== 8 && m.kind !== 6 && m.kind !== 4)) continue;
      if (!Number.isFinite(m.x) || !Number.isFinite(m.y) || !Number.isFinite(m.z)) continue;
      const dx = m.x - leadPos[0], dy = m.y - leadPos[1], dz = m.z - leadPos[2];
      const dist = Math.hypot(dx, dy, dz);
      const massR = m.r || m.rad || 240;
      const influenceR = Math.max(4800, massR * 14);
      if (dist < influenceR && dist < minDist) {
        minDist = dist;
        nearestMass = m;
      }
    }

    if (this.activePlanet !== nearestMass) {
      this._lastActivePlanet = this.activePlanet;
      this.lastMinDist = minDist;
    }
    this.activePlanet = nearestMass;
    this.periapsisDist = minDist;

    this.slingshotArc.length = 0;
    this.slingshotPeriapsisIdx = 0;

    if (this.activePlanet) {
      const pm = this.activePlanet;
      const pRad = pm.r || pm.rad || 240;
      let simX = leadPos[0], simY = leadPos[1], simZ = leadPos[2];
      let simVx = (routeX(travel + 100) - routeX(travel)) * 12;
      let simVy = (courseY(travel + 100) - courseY(travel)) * 12;
      let simVz = SPEED * (1 + (warp || 0));

      const steps = 36;
      const targetZDist = Math.max(1200, pm.z - simZ);
      const totalSimTime = (targetZDist / Math.max(30, simVz)) * 1.5;
      const simDt = Math.max(0.08, Math.min(1.2, totalSimTime / steps));
      const massG = (pm.mass || (pRad * pRad * 320));

      let minArcDist = 1e9;
      let closestIdx = 0;

      for (let s = 0; s < steps; s++) {
        const pdx = pm.x - simX, pdy = pm.y - simY, pdz = pm.z - simZ;
        const pDistSq = pdx * pdx + pdy * pdy + pdz * pdz + 10000;
        const pDist = Math.sqrt(pDistSq);
        const force = massG / pDistSq;

        simVx += (pdx / pDist) * force * simDt;
        simVy += (pdy / pDist) * force * simDt;
        simVz += (pdz / pDist) * force * simDt;

        simX += simVx * simDt;
        simY += simVy * simDt;
        simZ += simVz * simDt;

        this.slingshotArc.push([simX, simY, simZ]);
        if (pDist < minArcDist) {
          minArcDist = pDist;
          closestIdx = s;
        }
      }
      this.slingshotPeriapsisIdx = closestIdx;

      // Gravitational Well Force: Celestial gravity gently influences flight trajectory
      if (minDist < pRad * 8.0) {
        const pdx = pm.x - leadPos[0], pdy = pm.y - leadPos[1];
        const pDist = Math.hypot(pdx, pdy) || 1;
        if (fleet[LEAD]) {
          const pull = Math.min(60, (pRad * 40) / Math.max(pRad * 0.5, pDist));
          fleet[LEAD].vx += (pdx / pDist) * pull * dt;
          fleet[LEAD].vy += (pdy / pDist) * (pull * 0.5) * dt;
        }
      }

      const sweetSpot = pRad * 4.5;
      const isPassingPeriapsis = (minDist < sweetSpot && ((this.lastMinDist && minDist > this.lastMinDist) || minDist < pRad * 2.2));
      if (isPassingPeriapsis && this.slingshotCooldown <= 0) {
        this.slingshotCooldown = 12.0;
        this.triggerSlingshotBoost(pm);
      }
      this.lastMinDist = minDist;
    }

    // Step active orbital probes
    for (let i = this.probes.length - 1; i >= 0; i--) {
      const pr = this.probes[i];
      pr.life -= dt;
      pr.spin = (pr.spin || 0) + dt * 8.0;

      // If probe has no target, dynamically scan for upcoming celestial body ahead
      if (!pr.targetMass) {
        for (const m of massesPool) {
          if (!m || !Number.isFinite(m.x) || !Number.isFinite(m.y) || !Number.isFinite(m.z)) continue;
          const dz = m.z - pr.z;
          if (dz > 0 && dz < 18000 && Math.hypot(m.x - pr.x, m.y - pr.y) < (m.r || m.rad || 240) * 8) {
            pr.targetMass = m;
            break;
          }
        }
      }

      if (pr.targetMass && Number.isFinite(pr.targetMass.x) && Number.isFinite(pr.targetMass.y) && Number.isFinite(pr.targetMass.z)) {
        const pdx = pr.targetMass.x - pr.x;
        const pdy = pr.targetMass.y - pr.y;
        const pdz = pr.targetMass.z - pr.z;
        const pDistSq = pdx * pdx + pdy * pdy + pdz * pdz + 4000;
        const pDist = Math.sqrt(pDistSq);
        const f = 2.4e8 / pDistSq;

        pr.vx += (pdx / pDist) * f * dt;
        pr.vy += (pdy / pDist) * f * dt;
        pr.vz += (pdz / pDist) * f * dt;

        // Periapsis proximity triggers chain gravitational shockwave
        const rad = pr.targetMass.r || pr.targetMass.rad || 240;
        if (pDist < rad * 1.8 && !pr.hasTriggeredShock) {
          pr.hasTriggeredShock = true;
          this.triggerShockwave(pr.x, pr.y, pr.z, pr.targetMass);
        }
      }
      pr.x += pr.vx * dt;
      pr.y += pr.vy * dt;
      pr.z += pr.vz * dt;

      pr.trail.push([pr.x, pr.y, pr.z]);
      if (pr.trail.length > 28) pr.trail.shift();

      if (pr.life <= 0) {
        if (!pr.hasTriggeredShock) {
          pr.hasTriggeredShock = true;
          this.triggerShockwave(pr.x, pr.y, pr.z, pr.targetMass || null);
        }
        this.probes.splice(i, 1);
      }
    }

    // Step expanding gravitational shockwaves
    for (let i = this.shockwaves.length - 1; i >= 0; i--) {
      const sw = this.shockwaves[i];
      sw.life -= dt;
      sw.radius += dt * 3800;

      // Deflect space particles
      if (typeof particles !== 'undefined' && Array.isArray(particles)) {
        for (const p of particles) {
          const dx = p.x - sw.x, dy = p.y - sw.y, dz = p.z - sw.z;
          const d = Math.hypot(dx, dy, dz);
          if (Math.abs(d - sw.radius) < 400) {
            p.drift += (dx / (d || 1)) * 3.5;
          }
        }
      }

      if (sw.life <= 0) this.shockwaves.splice(i, 1);
    }

    // Unobstructed HUD: ensure no bottom probe button exists
    const pBtn = document.getElementById('sf-inflight-probe-btn');
    if (pBtn) pBtn.remove();
  },

  triggerSlingshotBoost(pm) {
    warp = Math.min(3.8, (warp || 0) + 2.0);
    this.slingshotGlowTimer = 4.0;
    if (typeof slingshotSurgeActive !== 'undefined') {
      slingshotSurgeActive = true;
      slingshotSurgeTimer = 4.5;
    }
    const toastEl = document.getElementById('slingshot-toast');
    if (toastEl) toastEl.classList.add('show');

    this.playGravSound('slingshot');
    if (typeof navigator !== 'undefined' && (navigator.userActivation ? navigator.userActivation.hasBeenActive : true) && navigator.vibrate) {
      try { navigator.vibrate([60, 40, 100]); } catch(e) {}
    }

    const pName = pm.name || (pm.w && pm.w.name) || '天体引力井';
    const msg = `✦ 触发【${pName}】行星引力弹弓！变轨加速 +280%！✦`;
    if (typeof showToast === 'function') showToast(msg, 3.5);
    else if (typeof window.toast === 'function') window.toast(msg, 3.5);
  },

  triggerShockwave(x, y, z, targetMass) {
    this.shockwaves.push({
      x, y, z,
      radius: 60,
      maxRadius: 2800,
      life: 1.8,
      maxLife: 1.8
    });
    this.playGravSound('shockwave');
    if (typeof navigator !== 'undefined' && (navigator.userActivation ? navigator.userActivation.hasBeenActive : true) && navigator.vibrate) {
      try { navigator.vibrate([80, 50, 140]); } catch(e) {}
    }

    // Resonate with deep planetary core: awards unopened celestial core or telemetry stardust
    if (window.StarfieldHatch && typeof window.StarfieldHatch.addCores === 'function') {
      window.StarfieldHatch.addCores(1);
      const tName = targetMass ? (targetMass.name || (targetMass.w && targetMass.w.name) || '星体') : '深空';
      const msg = `✦ 探针引力弹弓共振【${tName}】星核！连锁冲击波扩散 · 捕获未开采星核 × 1！✦`;
      if (typeof showToast === 'function') showToast(msg, 3.5);
      else if (typeof window.toast === 'function') window.toast(msg, 3.5);
    }
  },

  launchProbe() {
    if (!fleet || !fleet[LEAD]) return;
    const leadPos = craftWorld(fleet[LEAD]);
    const target = (this.activePlanet && (this.activePlanet.z >= leadPos[2] - 400)) ? this.activePlanet : null;
    this.probes.push({
      x: leadPos[0],
      y: leadPos[1],
      z: leadPos[2],
      vx: (routeX(travel + 100) - routeX(travel)) * 20 + (Math.random() - 0.5) * 400,
      vy: (courseY(travel + 100) - courseY(travel)) * 20 + 200,
      vz: (SPEED * (1 + (warp || 0))) + 1800,
      targetMass: target,
      life: 6.0,
      spin: 0,
      hasTriggeredShock: false,
      trail: []
    });
    const msg = '✦ 成功发射引力弹弓探测鸟！探测星体引力弯曲弹道 [P / 双击屏幕] ✦';
    if (typeof showToast === 'function') showToast(msg, 2.5);
    else if (typeof window.toast === 'function') window.toast(msg, 2.5);
  },

  draw(c) {
    // 1. Draw High-Precision Dynamic Orbital Trajectory Arc
    if (this.slingshotArc.length > 2 && this.activePlanet) {
      c.save();
      c.beginPath();
      let first = true;
      for (let i = 0; i < this.slingshotArc.length; i++) {
        const pt = this.slingshotArc[i];
        const q = project(pt);
        if (!q || q[2] <= 0) continue;
        if (first) { c.moveTo(q[0], q[1]); first = false; }
        else { c.lineTo(q[0], q[1]); }
      }
      c.strokeStyle = 'rgba(56, 189, 248, 0.72)';
      c.lineWidth = 2.2;
      c.setLineDash([7, 4]);
      c.lineDashOffset = -(performance.now() * 0.02) % 11;
      c.shadowColor = '#38bdf8';
      c.shadowBlur = 12;
      c.stroke();
      c.restore();

      // Periapsis Sweet-Spot Marker
      const midIdx = Math.max(0, Math.min(this.slingshotArc.length - 1, this.slingshotPeriapsisIdx || Math.floor(this.slingshotArc.length * 0.45)));
      const midQ = project(this.slingshotArc[midIdx]);
      if (midQ && midQ[2] > 0) {
        c.save();
        c.translate(midQ[0], midQ[1]);
        // Tangent trajectory marker diamond
        c.strokeStyle = '#ffd700';
        c.lineWidth = 1.6;
        c.beginPath();
        c.moveTo(0, -6); c.lineTo(6, 0); c.lineTo(0, 6); c.lineTo(-6, 0);
        c.closePath();
        c.stroke();

        c.font = '10px ui-monospace, sans-serif';
        c.fillStyle = '#ffd700';
        c.textAlign = 'center';
        c.fillText('✦ 引力借力点 · 弹弓加速 +280% ✦', 0, -12);
        c.restore();
      }
    }

    // 2. Relativistic Space-Stretching Stream Glow FX (空间拉伸流光特效)
    if (this.slingshotGlowTimer > 0) {
      const alpha = Math.min(1.0, this.slingshotGlowTimer * 0.8);
      c.save();
      c.strokeStyle = `rgba(56, 189, 248, ${(alpha * 0.55).toFixed(2)})`;
      c.lineWidth = 1.6;
      const cx = (typeof W !== 'undefined' ? W : 400) * 0.5;
      const cy = (typeof H !== 'undefined' ? H : 600) * 0.5;
      const numLines = 18;
      for (let k = 0; k < numLines; k++) {
        const ang = (k / numLines) * TAU + (performance.now() * 0.001);
        const r1 = 80 + Math.sin(ang * 4) * 30;
        const r2 = 360 + Math.cos(ang * 3) * 60;
        c.beginPath();
        c.moveTo(cx + Math.cos(ang) * r1, cy + Math.sin(ang) * r1);
        c.lineTo(cx + Math.cos(ang) * r2, cy + Math.sin(ang) * r2);
        c.stroke();
      }
      c.restore();
    }

    // Atmospheric Entry Plasma Compression Glow during Low-Orbit Skims
    const activeRad = this.activePlanet ? (this.activePlanet.r || this.activePlanet.rad || 300) : 300;
    if (this.activePlanet && this.periapsisDist < activeRad * 2.2) {
      c.save();
      const pColor = this.activePlanet.w && this.activePlanet.w.type && this.activePlanet.w.type.id === 'forest' ? 'rgba(52, 211, 153, 0.45)' :
                     this.activePlanet.w && this.activePlanet.w.type && this.activePlanet.w.type.id === 'ocean' ? 'rgba(56, 189, 248, 0.55)' :
                     'rgba(251, 146, 60, 0.45)';
      const leadPt = craftWorld(fleet[LEAD]);
      const lq = project(leadPt);
      if (lq && lq[2] > 0) {
        c.beginPath();
        c.arc(lq[0], lq[1] - 4, 36, Math.PI * 0.8, Math.PI * 2.2);
        c.strokeStyle = pColor;
        c.lineWidth = 3.5;
        c.shadowColor = pColor;
        c.shadowBlur = 18;
        c.stroke();
      }
      c.restore();
    }

    // 3. Render Stylized Space Bird Gravity Probes & Ribbon Particle Trails
    for (const pr of this.probes) {
      if (pr.trail.length > 1) {
        c.save();
        c.beginPath();
        let f = true;
        for (let j = 0; j < pr.trail.length; j++) {
          const q = project(pr.trail[j]);
          if (!q || q[2] <= 0) continue;
          if (f) { c.moveTo(q[0], q[1]); f = false; }
          else { c.lineTo(q[0], q[1]); }
        }
        c.strokeStyle = 'rgba(244, 63, 94, 0.88)';
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
        c.fill();

        // Twin deployable solar panels
        c.fillStyle = '#38bdf8';
        c.fillRect(-9, -1.5, 4, 3);
        c.fillRect(5, -1.5, 4, 3);

        // Pulsing telemetry broadcast wave
        c.beginPath();
        c.arc(0, 0, 9 + Math.sin(performance.now() * 0.01) * 3, 0, TAU);
        c.strokeStyle = 'rgba(251, 146, 60, 0.55)';
        c.lineWidth = 1.0;
        c.stroke();
        c.restore();
      }
    }

    // 4. Render 3D Expanding Gravitational Shockwaves (连锁引力冲击波)
    for (const sw of this.shockwaves) {
      const q = project([sw.x, sw.y, sw.z]);
      if (q && q[2] > 0) {
        const prog = 1 - (sw.life / (sw.maxLife || 1.8));
        const sR = Math.max(12, Math.min(320, (400 / q[2]) * sw.radius * 0.08));
        const alpha = Math.max(0, (1 - prog) * 0.85);

        c.save();
        c.beginPath();
        c.arc(q[0], q[1], sR, 0, TAU);
        c.strokeStyle = `rgba(168, 85, 247, ${alpha.toFixed(2)})`;
        c.lineWidth = 3.0;
        c.shadowColor = '#c084fc';
        c.shadowBlur = 16;
        c.stroke();

        // Inner harmonic resonance ripple
        c.beginPath();
        c.arc(q[0], q[1], sR * 0.65, 0, TAU);
        c.strokeStyle = `rgba(56, 189, 248, ${(alpha * 0.7).toFixed(2)})`;
        c.lineWidth = 1.8;
        c.stroke();
        c.restore();
      }
    }
  }
};
window.StarfieldOrbitalMechanics = StarfieldOrbitalMechanics;
'''

def patch_file(filepath):
    print("Patching:", filepath)
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    start_marker = "const StarfieldSonar = {"
    end_marker = "const particles=[],MAX_PARTICLES=coarse?168:240;"
    
    p1 = content.find(start_marker)
    p2 = content.find(end_marker)
    
    assert p1 != -1, f"Could not find start marker in {filepath}"
    assert p2 != -1, f"Could not find end marker in {filepath}"
    
    patched = content[:p1] + new_code + "\n\n" + content[p2:]
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(patched)
    print("Done patching:", filepath, "Size:", len(patched))

def main():
    root_path = os.path.abspath('starfield.html')
    android_path = os.path.abspath('android/app/src/main/assets/starfield.html')
    
    patch_file(root_path)
    patch_file(android_path)
    
    with open(root_path, 'rb') as f1, open(android_path, 'rb') as f2:
        b1 = f1.read()
        b2 = f2.read()
        assert b1 == b2, f"Byte mismatch! Root: {len(b1)} bytes, Android: {len(b2)} bytes"
        print(f"100% BYTE-FOR-BYTE PARITY VERIFIED: {len(b1)} bytes")

if __name__ == '__main__':
    main()
