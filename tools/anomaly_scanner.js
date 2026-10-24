/**
 * ============================================================================
 * STARFIELD // DEEP SPACE ANOMALY SCANNING & RELIC DECIPHERING GAMEPLAY SYSTEM
 * File: tools/anomaly_scanner.js
 * 
 * Features:
 * 1. Deep-Space Long-Range Radar Ping (ScannerRadar):
 *    - Hotkey R or click '#radar-toggle' [ 📡 巡天雷达 ]
 *    - Concentric 3D holographic ripple pulses forward from flagship (spanning 15,000 units)
 *    - Sonar acoustic ping via Web Audio API (sine tone with pitch drop & stereo reverb)
 *    - Dynamic detection of derelicts, anomalies, and resource nodes with glowing papercraft HUD markers
 * 
 * 2. Interactive Origami Relic Deciphering Minigame (RelicTuner):
 *    - Proximity prompt when within 2,500 units of an anomaly or derelict: [ 按 E 或点击 调谐深空信号 ]
 *    - Minimalist papercraft waveform signal alignment puzzle with Carrier Wave (Target) & Receiver Wave (Adjustable)
 *    - Harmonic resonance locking (>95% alignment for 1.2 seconds)
 *    - Static noise resolving into celestial chime chord & Golden Discovery Toast
 *    - Classified deep-space lore entry unlocked into Celestial Codex (Codex.unlock / Codex.discover)
 * ============================================================================
 */

(function(window) {
  'use strict';

  // Prevent multiple initializations
  if (window.AnomalyScanner && window.AnomalyScanner.isInitialized && window.AnomalyScanner.isInitialized()) {
    return;
  }

  // ============================================================================
  // 1. CLASSIFIED DEEP-SPACE RELIC LORE DATABASE
  // ============================================================================
  const RELIC_ARCHIVE = [
    {
      id: 'relic_zero_fold',
      type: 'derelict',
      name: '先行者信标手札 · 零号折叠',
      en: 'First-Fold Beacon Relic #0',
      tag: '密文 / R1',
      desc: '“在光线无法逃逸的深渊边缘，我们曾折叠过第七个维度。所有旅者在星海留下的折痕，最终都会在奇点原点重聚。若你拾得此卷，请将引力帆调谐至 432 赫兹……”'
    },
    {
      id: 'relic_black_hole_echo',
      type: 'spatial_anomaly',
      name: '加甘图亚引力回声黑匣',
      en: 'Gargantua Gravitational Echo',
      tag: '密文 / R2',
      desc: '“测得吸积盘视界反向光子环中夹杂着规律的晶体脉冲。五维时间窗并非自然演化形成，而是超越纪元的折纸文明遗留在宇宙边缘的立构档案馆。”'
    },
    {
      id: 'relic_derelict_flagship',
      type: 'derelict',
      name: '破晓幽灵号巡航日志 · 终末航标',
      en: 'Ghost Flagship Final Log',
      tag: '密文 / R3',
      desc: '“全舰三联装折光偏折力场破损率 88%，已无法脱离当前引力阱。我们在核心舱铭刻了最后这串谐振密码，留给未来掠过此地的同道飞翔者——星空无涯，无需抵达。”'
    },
    {
      id: 'relic_quantum_monolith',
      type: 'spatial_anomaly',
      name: '黑色方尖碑谐振碑文 · 1:4:9 几何之谜',
      en: 'Monolith Harmonic Geometric Codex',
      tag: '密文 / R4',
      desc: '“1:4:9 的比例不是建筑，而是超空间天线。纯黑外壁在谐振锁定下变得晶莹剔透，内部是一整片凝固的光态超立方体，记载着贯穿 48 个星区的折跃航线。”'
    },
    {
      id: 'relic_void_fissure',
      type: 'spatial_anomaly',
      name: '莫比乌斯曲率拓扑刻印',
      en: 'Mobius Curvature Topological Engraving',
      tag: '密文 / R5',
      desc: '“空间曲率在此处发生了自旋反转。高维光子环以纸艺结的形式紧密编织在一起，证明了远古折叠者曾用微观奇点重写过当前星域的物理常数。”'
    },
    {
      id: 'relic_crystal_resonance',
      type: 'resource_node',
      name: '原生折光晶体簇共振图谱',
      en: 'Protoss Crystal Nexus Resonance Map',
      tag: '矿藏 / M1',
      desc: '“高纯度幽能晶体在真空中维持着稳定的八面体纸构形态。微量折射即可产生超距共鸣，是重塑舰载引力帆涂层的顶级稀有材料。”'
    }
  ];

  // ============================================================================
  // 2. WEB AUDIO ACOUSTIC & HARMONIC SOUND ENGINE
  // ============================================================================
  const ScannerAudio = {
    ac: null,
    masterGain: null,
    tuningHissGain: null,
    tuningHissNode: null,
    tuningDroneGain: null,
    tuningDroneOsc: null,
    isHissActive: false,

    init() {
      if (this.ac) {
        if (this.ac.state === 'suspended') this.ac.resume().catch(() => {});
        return;
      }
      try {
        const AC = window.AudioContext || window.webkitAudioContext;
        if (!AC) return;
        this.ac = new AC();
        this.masterGain = this.ac.createGain();
        this.masterGain.gain.value = 0.85;
        this.masterGain.connect(this.ac.destination);
      } catch (e) {
        console.warn('[ScannerAudio] AudioContext init deferred:', e);
      }
    },

    ensureContext() {
      if (!this.ac) this.init();
      if (this.ac && this.ac.state === 'suspended') {
        this.ac.resume().catch(() => {});
      }
      return this.ac;
    },

    // 1. Resonant Sonar Acoustic Ping (Sine with subtle pitch drop & stereo reverb)
    playSonarPing() {
      const ac = this.ensureContext();
      if (!ac) return;

      const now = ac.currentTime;

      // Master sonar gain
      const sonarGain = ac.createGain();
      sonarGain.gain.setValueAtTime(0.001, now);
      sonarGain.gain.linearRampToValueAtTime(0.48, now + 0.02);
      sonarGain.gain.exponentialRampToValueAtTime(0.0001, now + 2.4);

      // Stereo delay simulation (left 180ms, right 240ms)
      const splitter = ac.createChannelSplitter(2);
      const merger = ac.createChannelMerger(2);

      const delayL = ac.createDelay(1.0);
      delayL.delayTime.value = 0.18;
      const delayR = ac.createDelay(1.0);
      delayR.delayTime.value = 0.24;

      const feedbackL = ac.createGain();
      feedbackL.gain.value = 0.28;
      const feedbackR = ac.createGain();
      feedbackR.gain.value = 0.28;

      const filter = ac.createBiquadFilter();
      filter.type = 'lowpass';
      filter.frequency.value = 1400;

      // Connect delay feedback loop
      sonarGain.connect(filter);
      filter.connect(delayL);
      filter.connect(delayR);

      delayL.connect(feedbackL);
      feedbackL.connect(delayL);
      delayR.connect(feedbackR);
      feedbackR.connect(delayR);

      delayL.connect(merger, 0, 0);
      delayR.connect(merger, 0, 1);

      sonarGain.connect(this.masterGain);
      merger.connect(this.masterGain);

      // Main Sine Oscillator: 784 Hz (G5) dropping to 330 Hz (E4)
      const oscMain = ac.createOscillator();
      oscMain.type = 'sine';
      oscMain.frequency.setValueAtTime(784, now);
      oscMain.frequency.exponentialRampToValueAtTime(329.63, now + 1.8);
      oscMain.connect(sonarGain);
      oscMain.start(now);
      oscMain.stop(now + 2.5);

      // Sub-harmonic sine for deep cosmic body: 392 Hz dropping to 165 Hz
      const oscSub = ac.createOscillator();
      oscSub.type = 'sine';
      oscSub.frequency.setValueAtTime(392, now);
      oscSub.frequency.exponentialRampToValueAtTime(164.81, now + 1.8);
      const subGain = ac.createGain();
      subGain.gain.value = 0.25;
      oscSub.connect(subGain);
      subGain.connect(sonarGain);
      oscSub.start(now);
      oscSub.stop(now + 2.5);

      // Papercraft subtle initial air transient (20ms whisper)
      try {
        const buf = ac.createBuffer(1, Math.floor(ac.sampleRate * 0.03), ac.sampleRate);
        const data = buf.getChannelData(0);
        for (let i = 0; i < data.length; i++) data[i] = (Math.random() * 2 - 1) * 0.15;
        const noise = ac.createBufferSource();
        noise.buffer = buf;
        const nFilter = ac.createBiquadFilter();
        nFilter.type = 'highpass';
        nFilter.frequency.value = 2800;
        noise.connect(nFilter);
        nFilter.connect(sonarGain);
        noise.start(now);
      } catch (_) {}
    },

    // 2. High Sonar Detection Blip (when wavefront reaches target)
    playDetectionBlip(freq = 1046.5) {
      const ac = this.ensureContext();
      if (!ac) return;

      const now = ac.currentTime;
      const osc = ac.createOscillator();
      const gain = ac.createGain();
      osc.type = 'sine';
      osc.frequency.setValueAtTime(freq, now);
      osc.frequency.exponentialRampToValueAtTime(freq * 1.5, now + 0.14);

      gain.gain.setValueAtTime(0.001, now);
      gain.gain.linearRampToValueAtTime(0.22, now + 0.015);
      gain.gain.exponentialRampToValueAtTime(0.0001, now + 0.45);

      osc.connect(gain);
      gain.connect(this.masterGain);
      osc.start(now);
      osc.stop(now + 0.48);
    },

    // 3. Relic Tuner Static Hiss & Harmonic Resonance Drone
    startTuningAudio() {
      const ac = this.ensureContext();
      if (!ac || this.isHissActive) return;

      try {
        const now = ac.currentTime;
        // White noise buffer
        const bufSize = ac.sampleRate * 2;
        const noiseBuf = ac.createBuffer(1, bufSize, ac.sampleRate);
        const output = noiseBuf.getChannelData(0);
        for (let i = 0; i < bufSize; i++) {
          output[i] = Math.random() * 2 - 1;
        }

        this.tuningHissNode = ac.createBufferSource();
        this.tuningHissNode.buffer = noiseBuf;
        this.tuningHissNode.loop = true;

        this.tuningHissFilter = ac.createBiquadFilter();
        this.tuningHissFilter.type = 'bandpass';
        this.tuningHissFilter.frequency.value = 1800;
        this.tuningHissFilter.Q.value = 3.5;

        this.tuningHissGain = ac.createGain();
        this.tuningHissGain.gain.setValueAtTime(0.08, now);

        this.tuningHissNode.connect(this.tuningHissFilter);
        this.tuningHissFilter.connect(this.tuningHissGain);
        this.tuningHissGain.connect(this.masterGain);

        this.tuningHissNode.start(now);

        // Harmonic drone
        this.tuningDroneOsc = ac.createOscillator();
        this.tuningDroneOsc.type = 'triangle';
        this.tuningDroneOsc.frequency.setValueAtTime(260, now);

        this.tuningDroneGain = ac.createGain();
        this.tuningDroneGain.gain.setValueAtTime(0.001, now);

        this.tuningDroneOsc.connect(this.tuningDroneGain);
        this.tuningDroneGain.connect(this.masterGain);
        this.tuningDroneOsc.start(now);

        this.isHissActive = true;
      } catch (err) {
        console.warn('[ScannerAudio] startTuningAudio failed:', err);
      }
    },

    updateTuningAudio(freq, alignment) {
      if (!this.ac || !this.isHissActive) return;
      const now = this.ac.currentTime;
      const safeAlign = Math.max(0, Math.min(1, alignment));

      if (this.tuningHissFilter) {
        this.tuningHissFilter.frequency.setTargetAtTime(800 + freq * 400, now, 0.05);
      }
      if (this.tuningHissGain) {
        // Hiss attenuates as alignment approaches 100%
        const hissVol = Math.max(0.001, (1 - safeAlign) * 0.12);
        this.tuningHissGain.gain.setTargetAtTime(hissVol, now, 0.05);
      }
      if (this.tuningDroneOsc && this.tuningDroneGain) {
        // Drone pitch tracks frequency and rises in volume with alignment
        this.tuningDroneOsc.frequency.setTargetAtTime(140 + freq * 60, now, 0.05);
        const droneVol = safeAlign * 0.18;
        this.tuningDroneGain.gain.setTargetAtTime(droneVol, now, 0.05);
      }
    },

    stopTuningAudio() {
      if (!this.ac || !this.isHissActive) return;
      const now = this.ac.currentTime;
      try {
        if (this.tuningHissGain) {
          this.tuningHissGain.gain.linearRampToValueAtTime(0.0001, now + 0.1);
        }
        if (this.tuningDroneGain) {
          this.tuningDroneGain.gain.linearRampToValueAtTime(0.0001, now + 0.1);
        }
        setTimeout(() => {
          if (this.tuningHissNode) {
            try { this.tuningHissNode.stop(); } catch (_) {}
            this.tuningHissNode.disconnect();
          }
          if (this.tuningDroneOsc) {
            try { this.tuningDroneOsc.stop(); } catch (_) {}
            this.tuningDroneOsc.disconnect();
          }
          this.isHissActive = false;
        }, 120);
      } catch (_) {
        this.isHissActive = false;
      }
    },

    // 4. Celestial Chime Chord (Signal Lock Resolution)
    playCelestialChime() {
      const ac = this.ensureContext();
      if (!ac) return;

      const now = ac.currentTime;
      // Golden Pentatonic Celestial Chord: C5, E5, G5, C6, E6, G6
      const chord = [523.25, 659.25, 783.99, 1046.50, 1318.51, 1567.98];

      chord.forEach((freq, idx) => {
        const osc = ac.createOscillator();
        const gain = ac.createGain();

        osc.type = 'sine';
        // Micro-detune for lush celestial bell shimmer
        osc.frequency.setValueAtTime(freq + (idx % 2 === 0 ? 0.8 : -0.8), now);

        const startT = now + idx * 0.035;
        gain.gain.setValueAtTime(0.0001, startT);
        gain.gain.linearRampToValueAtTime(0.18 / Math.sqrt(idx + 1), startT + 0.02);
        gain.gain.exponentialRampToValueAtTime(0.0001, startT + 3.2);

        osc.connect(gain);
        gain.connect(this.masterGain);

        osc.start(startT);
        osc.stop(startT + 3.5);
      });
    }
  };

  // ============================================================================
  // 3. SCANNER RADAR ENGINE (3D Ripple Pulse & Dynamic Detection)
  // ============================================================================
  const ScannerRadar = {
    active: false,
    startTime: 0,
    duration: 3200,      // ms for wavefront to reach 15,000 units
    maxDistance: 15000,  // scanning range corridor in units
    waveDist: 0,
    cooldownUntil: 0,
    detectedTargets: new Map(), // key -> target metadata
    candidates: [],

    ping() {
      const now = performance.now();
      if (now < this.cooldownUntil) return;
      this.cooldownUntil = now + 900;

      this.active = true;
      this.startTime = now;
      this.waveDist = 0;

      // Play sonar acoustic ping
      ScannerAudio.playSonarPing();

      // Gather candidate targets along corridor
      this.gatherCandidates();

      // Golden HUD radar button ripple effect
      const radarBtn = document.getElementById('radar-toggle');
      if (radarBtn) {
        radarBtn.classList.add('pinging');
        setTimeout(() => radarBtn.classList.remove('pinging'), 1200);
      }
    },

    gatherCandidates() {
      this.candidates = [];
      const SF = window.Starfield;
      if (!SF) return;

      const travel = SF.getTravel ? SF.getTravel() : 0;
      const k0 = Math.floor(travel / 3200);

      // Scan chunks from k0 - 1 to k0 + 6 (spanning ~22,000 units forward)
      for (let k = k0 - 1; k <= k0 + 6; k++) {
        const c = SF.getChunk ? SF.getChunk(k) : null;
        if (!c) continue;

        // 1. Events in chunk
        if (c.events && Array.isArray(c.events)) {
          c.events.forEach((ev, evIdx) => {
            const key = `chunk_${k}_ev_${evIdx}_${ev.type}`;
            let name = '深空未知异常';
            let icon = '✦';
            let category = 'spatial_anomaly';

            if (ev.type === 'derelict') {
              name = '废弃信标浮标';
              icon = '⟐';
              category = 'derelict';
            } else if (ev.type === 'voyager_probe') {
              name = '旅行者深空探测器';
              icon = '⟐';
              category = 'derelict';
            } else if (ev.type === 'monolith_artifact') {
              name = '黑色方尖碑 1:4:9';
              icon = '◈';
              category = 'spatial_anomaly';
            } else if (ev.type === 'ghost_fleet') {
              name = '远古幽灵旗舰遗骸';
              icon = '⟐';
              category = 'derelict';
            } else if (ev.type === 'wormhole_sphere') {
              name = '莫比乌斯虫洞折射体';
              icon = '✦';
              category = 'spatial_anomaly';
            } else if (ev.type === 'dimension_foil') {
              name = '二向箔卷曲裂隙';
              icon = '✦';
              category = 'spatial_anomaly';
            } else if (ev.type === 'asteroid_field') {
              name = '高密小行星晶体群';
              icon = '◈';
              category = 'resource_node';
            }

            this.candidates.push({
              key,
              id: key,
              name,
              icon,
              category,
              x: ev.x,
              y: ev.y,
              z: ev.z,
              targetFreq: 2.2 + ((k * 37 + evIdx * 19) % 50) * 0.1,
              solved: this.detectedTargets.has(key) ? this.detectedTargets.get(key).solved : false,
              pinged: false
            });
          });
        }

        // 2. Procedural Hidden Relic Anchor (Ensures rich cosmic discoveries in every sector)
        const hasRelicType = (k % 2 === 0);
        if (hasRelicType) {
          const key = `relic_anchor_k${k}`;
          const pz = k * 3200 + 1600;
          const px = SF.corridorPoint ? SF.corridorPoint(pz)[0] + ((k % 3 === 0 ? 1 : -1) * 1450) : 1200;
          const py = SF.corridorPoint ? SF.corridorPoint(pz)[1] + 320 : 220;

          const archiveIndex = Math.abs(k) % RELIC_ARCHIVE.length;
          const lore = RELIC_ARCHIVE[archiveIndex];

          this.candidates.push({
            key,
            id: key,
            name: lore.name,
            icon: lore.type === 'derelict' ? '⟐' : '✦',
            category: lore.type,
            lore,
            x: px,
            y: py,
            z: pz,
            targetFreq: 2.5 + (archiveIndex * 0.95),
            solved: this.detectedTargets.has(key) ? this.detectedTargets.get(key).solved : false,
            pinged: false
          });
        }
      }
    },

    update(dt) {
      const SF = window.Starfield;
      if (!SF) return;

      const ship = SF.getFlagship ? SF.getFlagship() : [0, 196, SF.getTravel ? SF.getTravel() : 0];
      const now = performance.now();

      if (this.active) {
        const progress = (now - this.startTime) / this.duration;
        if (progress >= 1.0) {
          this.active = false;
          this.waveDist = this.maxDistance;
        } else {
          this.waveDist = progress * this.maxDistance;

          // Check candidate encounters reached by wavefront
          for (const cand of this.candidates) {
            const dist = Math.hypot(cand.x - ship[0], cand.y - ship[1], cand.z - ship[2]);
            if (dist <= this.waveDist && !cand.pinged) {
              cand.pinged = true;
              cand.revealedAt = now;
              this.detectedTargets.set(cand.key, cand);
              ScannerAudio.playDetectionBlip(cand.category === 'derelict' ? 987.77 : 1318.51);
            }
          }
        }
      }

      // Check proximity prompt for undeciphered targets within 2,500 units
      let nearestUndeciphered = null;
      let minPromptDist = 2500;

      for (const target of this.detectedTargets.values()) {
        const d = Math.hypot(target.x - ship[0], target.y - ship[1], target.z - ship[2]);
        target.currentDist = d;
        if (!target.solved && d <= minPromptDist) {
          minPromptDist = d;
          nearestUndeciphered = target;
        }
      }

      RelicTuner.updateProximityPrompt(nearestUndeciphered, minPromptDist);
    },

    // 3D Concentric Holographic Ripple Pulse Drawing
    draw3D(ctx, width, height, dpr) {
      const SF = window.Starfield;
      if (!SF) return;

      const cam = SF.getCamera ? SF.getCamera() : null;
      if (!cam) return;

      const project = SF.project || function(p) {
        const x = p[0] - cam.eye[0], y = p[1] - cam.eye[1], z = p[2] - cam.eye[2];
        const vx = x * cam.right[0] + y * cam.right[1] + z * cam.right[2];
        const vy = x * cam.up[0] + y * cam.up[1] + z * cam.up[2];
        const vz = x * cam.forward[0] + y * cam.forward[1] + z * cam.forward[2];
        if (vz < 18) return null;
        const k = cam.focal / vz;
        return [cam.cx + vx * k, cam.cy - vy * k, vz, k];
      };

      const ship = SF.getFlagship ? SF.getFlagship() : [0, 196, SF.getTravel ? SF.getTravel() : 0];
      const now = performance.now();

      // 1. Draw Active 3D Holographic Pulse Wavefronts
      if (this.active) {
        const ringOffsets = [0, 480, 960]; // 3 concentric ripple rings
        const progress = Math.min(1.0, (now - this.startTime) / this.duration);
        const baseAlpha = Math.max(0, (1 - progress) * (1 - progress * 0.4));

        ctx.save();
        ctx.lineCap = 'round';
        ctx.lineJoin = 'round';

        ringOffsets.forEach((offset, rIdx) => {
          const d = this.waveDist - offset;
          if (d <= 0 || d > this.maxDistance) return;

          const ringZ = ship[2] + d;
          const center = SF.corridorPoint ? SF.corridorPoint(ringZ) : [ship[0], ship[1], ringZ];

          // Compute forward tangent vector along flight corridor
          const ahead = SF.corridorPoint ? SF.corridorPoint(ringZ + 12) : [center[0], center[1], ringZ + 12];
          const behind = SF.corridorPoint ? SF.corridorPoint(ringZ - 12) : [center[0], center[1], ringZ - 12];
          let tx = ahead[0] - behind[0], ty = ahead[1] - behind[1], tz = ahead[2] - behind[2];
          const tLen = Math.hypot(tx, ty, tz) || 1;
          tx /= tLen; ty /= tLen; tz /= tLen;

          // Normal & Binormal for plane perpendicular to corridor
          let nx = -tz, ny = 0, nz = tx;
          const nLen = Math.hypot(nx, nz) || 1;
          nx /= nLen; nz /= nLen;
          const bx = ty * nz - tz * ny, by = tz * nx - tx * nz, bz = tx * ny - ty * nx;

          // Expanding radius: from 520 units at ship to 2,400 units at 15,000 units
          const radius = 520 + d * 0.125;
          const ringPoints = [];
          const stepCount = 36;

          for (let s = 0; s <= stepCount; s++) {
            const th = (s / stepCount) * Math.PI * 2;
            const cosT = Math.cos(th), sinT = Math.sin(th);
            const px = center[0] + (nx * cosT + bx * sinT) * radius;
            const py = center[1] + (ny * cosT + by * sinT) * radius;
            const pz = center[2] + (nz * cosT + bz * sinT) * radius;

            const sp = project([px, py, pz]);
            if (sp) ringPoints.push(sp);
          }

          if (ringPoints.length > 3) {
            const ringAlpha = baseAlpha * (1 - rIdx * 0.22);
            // Papercraft dashed holographic stroke
            ctx.setLineDash(rIdx === 0 ? [8, 4] : [4, 6]);
            ctx.lineWidth = rIdx === 0 ? 2.0 : 1.2;
            ctx.strokeStyle = `rgba(224, 192, 96, ${ringAlpha * 0.85})`;
            ctx.beginPath();
            ctx.moveTo(ringPoints[0][0], ringPoints[0][1]);
            for (let i = 1; i < ringPoints.length; i++) {
              ctx.lineTo(ringPoints[i][0], ringPoints[i][1]);
            }
            ctx.closePath();
            ctx.stroke();

            // Center range marker readout on primary wave
            if (rIdx === 0) {
              const cp = project(center);
              if (cp && cp[0] > 0 && cp[0] < width && cp[1] > 0 && cp[1] < height) {
                ctx.setLineDash([]);
                ctx.fillStyle = `rgba(242, 220, 135, ${ringAlpha * 0.9})`;
                ctx.font = '10px "SF Mono", Consolas, monospace';
                ctx.textAlign = 'center';
                ctx.fillText(`+${Math.round(d)} U`, cp[0], cp[1] - 8);

                // Crosshair tick marks
                ctx.strokeStyle = `rgba(242, 220, 135, ${ringAlpha * 0.6})`;
                ctx.beginPath();
                ctx.moveTo(cp[0] - 8, cp[1]); ctx.lineTo(cp[0] + 8, cp[1]);
                ctx.moveTo(cp[0], cp[1] - 8); ctx.lineTo(cp[0], cp[1] + 8);
                ctx.stroke();
              }
            }
          }
        });

        ctx.restore();
      }

      // 2. Draw Glowing Papercraft HUD Markers for Detected Targets
      ctx.save();
      for (const target of this.detectedTargets.values()) {
        const tp = project([target.x, target.y, target.z]);
        if (!tp) continue;

        const sx = tp[0], sy = tp[1];
        if (sx < -80 || sx > width + 80 || sy < -80 || sy > height + 80) continue;

        const dist = Math.round(target.currentDist || 0);
        const isSolved = !!target.solved;
        const isReady = !isSolved && dist <= 2500;

        // Papercraft Origami Diamond Bracket
        const boxSize = 14;
        const color = isSolved ? 'rgba(168, 230, 207, 0.85)' : isReady ? 'rgba(255, 215, 0, 0.95)' : 'rgba(224, 192, 96, 0.75)';

        ctx.strokeStyle = color;
        ctx.fillStyle = color;
        ctx.lineWidth = 1.3;
        ctx.setLineDash([]);

        // Diamond Bracket Corners
        ctx.beginPath();
        // Top Corner
        ctx.moveTo(sx - 5, sy - boxSize + 5); ctx.lineTo(sx, sy - boxSize); ctx.lineTo(sx + 5, sy - boxSize + 5);
        // Bottom Corner
        ctx.moveTo(sx - 5, sy + boxSize - 5); ctx.lineTo(sx, sy + boxSize); ctx.lineTo(sx + 5, sy + boxSize - 5);
        // Left Corner
        ctx.moveTo(sx - boxSize + 5, sy - 5); ctx.lineTo(sx - boxSize, sy); ctx.lineTo(sx - boxSize + 5, sy + 5);
        // Right Corner
        ctx.moveTo(sx + boxSize - 5, sy - 5); ctx.lineTo(sx + boxSize, sy); ctx.lineTo(sx + boxSize - 5, sy + 5);
        ctx.stroke();

        // Central Icon Symbol
        ctx.font = '12px "SF Mono", Consolas, sans-serif';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText(target.icon || '✦', sx, sy);

        // Holographic Labels & Distance Readouts
        ctx.font = '10px "SF Mono", Consolas, monospace';
        ctx.textAlign = 'left';
        ctx.textBaseline = 'bottom';
        const labelX = sx + boxSize + 8;
        const labelY = sy - 2;

        ctx.fillText(`${target.name}`, labelX, labelY);

        ctx.font = '9px "SF Mono", Consolas, monospace';
        ctx.fillStyle = isSolved ? 'rgba(168, 230, 207, 0.7)' : 'rgba(235, 240, 245, 0.7)';
        ctx.fillText(`DIST: ${dist} U  // ${isSolved ? '已破译 [SOLVED]' : isReady ? '可调谐 [按 E]' : '未破译'}`, labelX, labelY + 13);

        // Ground/corridor dotted drop-line
        ctx.setLineDash([2, 4]);
        ctx.strokeStyle = 'rgba(255, 255, 255, 0.15)';
        ctx.beginPath();
        ctx.moveTo(sx, sy + boxSize + 2);
        ctx.lineTo(sx, sy + boxSize + 18);
        ctx.stroke();
      }
      ctx.restore();
    }
  };

  // ============================================================================
  // 4. RELIC TUNER MINIGAME ENGINE (Origami Waveform Alignment Puzzle)
  // ============================================================================
  const RelicTuner = {
    isOpen: false,
    currentTarget: null,
    targetFreq: 3.40,
    playerFreq: 1.80,
    alignment: 0.0,
    lockHoldTime: 0.0,
    lockRequired: 1.2,    // 1.2 seconds of >95% resonance
    isLocked: false,
    animTime: 0,
    scopeCanvas: null,
    scopeCtx: null,

    init() {
      this.injectStyles();
      this.injectDOM();
      this.bindEvents();
    },

    injectStyles() {
      if (document.getElementById('anomaly-scanner-styles')) return;
      const style = document.createElement('style');
      style.id = 'anomaly-scanner-styles';
      style.textContent = `
        /* Radar Button in HUD */
        #radar-toggle.pinging {
          border-color: #f2dc87 !important;
          box-shadow: 0 0 16px rgba(242, 220, 135, 0.45);
          transform: scale(1.05);
        }
        #radar-toggle .radar-icon {
          color: #f2dc87;
        }

        /* 3D Scanner Overlay Canvas */
        #scanner-overlay-canvas {
          position: absolute;
          inset: 0;
          width: 100%;
          height: 100%;
          pointer-events: none;
          z-index: 5;
        }

        /* Proximity HUD Prompt */
        #relic-proximity-prompt {
          position: absolute;
          left: 50%;
          bottom: calc(var(--pad, 36px) + 64px);
          transform: translateX(-50%);
          display: none;
          align-items: center;
          gap: 12px;
          padding: 9px 20px;
          border: 1px solid rgba(242, 220, 135, 0.35);
          border-radius: 30px;
          background: rgba(17, 27, 39, 0.88);
          backdrop-filter: blur(14px);
          cursor: pointer;
          z-index: 9;
          transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1);
          box-shadow: 0 6px 24px rgba(0, 0, 0, 0.35), 0 0 14px rgba(242, 220, 135, 0.15);
          user-select: none;
        }
        #relic-proximity-prompt.visible {
          display: flex;
          animation: promptPulse 2.4s ease-in-out infinite;
        }
        #relic-proximity-prompt:hover {
          border-color: rgba(242, 220, 135, 0.85);
          background: rgba(26, 40, 58, 0.95);
          transform: translateX(-50%) translateY(-2px);
          box-shadow: 0 8px 28px rgba(0, 0, 0, 0.45), 0 0 20px rgba(242, 220, 135, 0.3);
        }
        @keyframes promptPulse {
          0%, 100% { border-color: rgba(242, 220, 135, 0.35); box-shadow: 0 0 10px rgba(242, 220, 135, 0.15); }
          50% { border-color: rgba(242, 220, 135, 0.75); box-shadow: 0 0 22px rgba(242, 220, 135, 0.35); }
        }
        .prompt-radar-icon {
          font-size: 16px;
          color: #f2dc87;
        }
        .prompt-content {
          display: flex;
          flex-direction: column;
          gap: 2px;
        }
        .prompt-headline {
          font-family: var(--serif, serif);
          font-size: 13px;
          letter-spacing: 0.08em;
          color: #f5f9fc;
        }
        .prompt-detail {
          font-family: var(--mono, monospace);
          font-size: 9px;
          color: rgba(212, 175, 55, 0.9);
          letter-spacing: 0.05em;
        }

        /* Relic Tuner Modal Window */
        #relic-tuner-modal {
          position: absolute;
          inset: 0;
          background: rgba(10, 16, 24, 0.72);
          backdrop-filter: blur(18px);
          display: none;
          align-items: center;
          justify-content: center;
          z-index: 100;
          opacity: 0;
          pointer-events: none;
          transition: opacity 0.3s ease;
        }
        #relic-tuner-modal.open {
          display: flex;
          opacity: 1;
          pointer-events: auto;
        }
        .relic-modal-frame {
          width: 680px;
          max-width: 92vw;
          border: 1px solid rgba(255, 255, 255, 0.14);
          border-radius: 12px;
          background: #111b27;
          box-shadow: 0 24px 64px rgba(0, 0, 0, 0.65), 0 0 32px rgba(212, 175, 55, 0.18);
          overflow: hidden;
          position: relative;
        }
        .relic-modal-header {
          display: flex;
          align-items: center;
          justify-content: space-between;
          padding: 18px 24px;
          border-bottom: 1px solid rgba(255, 255, 255, 0.08);
          background: rgba(255, 255, 255, 0.02);
        }
        .relic-tag-badge {
          display: inline-block;
          font-family: var(--mono, monospace);
          font-size: 9px;
          letter-spacing: 0.12em;
          color: #d4af37;
          border: 1px solid rgba(212, 175, 55, 0.35);
          padding: 2px 7px;
          border-radius: 3px;
          margin-bottom: 5px;
        }
        .relic-heading {
          font-family: var(--serif, serif);
          font-size: 19px;
          font-weight: 400;
          color: #f7f9fb;
          margin: 0;
          letter-spacing: 0.04em;
        }
        .relic-subheading {
          font-family: var(--mono, monospace);
          font-size: 10px;
          color: rgba(255, 255, 255, 0.45);
          margin-top: 3px;
        }
        .relic-close-btn {
          background: transparent;
          border: 1px solid rgba(255, 255, 255, 0.15);
          color: rgba(255, 255, 255, 0.65);
          border-radius: 4px;
          padding: 6px 14px;
          font-family: var(--mono, monospace);
          font-size: 11px;
          cursor: pointer;
          transition: all 0.2s ease;
        }
        .relic-close-btn:hover {
          color: #fff;
          border-color: rgba(255, 255, 255, 0.4);
          background: rgba(255, 255, 255, 0.05);
        }

        /* Oscilloscope Display */
        .relic-scope-wrapper {
          position: relative;
          background: #090e15;
          border-bottom: 1px solid rgba(255, 255, 255, 0.08);
          padding: 12px 18px;
        }
        #relic-waveform-canvas {
          display: block;
          width: 100%;
          height: 220px;
          border-radius: 6px;
          cursor: ew-resize;
        }
        .relic-scope-info {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-top: 10px;
          font-family: var(--mono, monospace);
          font-size: 10px;
          color: rgba(255, 255, 255, 0.6);
        }
        .scope-legend-group {
          display: flex;
          gap: 16px;
        }
        .legend-carrier {
          color: #d4af37;
        }
        .legend-receiver {
          color: #7ec8e3;
        }
        .scope-status-metric {
          font-weight: 600;
          color: #f7f9fb;
        }

        /* Tuning Controls */
        .relic-controls-box {
          padding: 20px 24px;
          background: rgba(255, 255, 255, 0.015);
        }
        .relic-slider-container {
          display: flex;
          align-items: center;
          gap: 14px;
        }
        .relic-freq-tag {
          font-family: var(--mono, monospace);
          font-size: 11px;
          color: rgba(255, 255, 255, 0.5);
          width: 55px;
        }
        .relic-freq-tag.right {
          text-align: right;
        }
        .paper-range-slider {
          flex: 1;
          -webkit-appearance: none;
          appearance: none;
          height: 6px;
          background: rgba(255, 255, 255, 0.12);
          border-radius: 3px;
          outline: none;
        }
        .paper-range-slider::-webkit-slider-thumb {
          -webkit-appearance: none;
          appearance: none;
          width: 18px;
          height: 18px;
          border-radius: 50%;
          background: #d4af37;
          border: 2px solid #fff;
          cursor: pointer;
          box-shadow: 0 0 10px rgba(212, 175, 55, 0.6);
          transition: transform 0.1s ease;
        }
        .paper-range-slider::-webkit-slider-thumb:hover {
          transform: scale(1.15);
        }
        .relic-tuner-guide {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-top: 12px;
          font-family: var(--mono, monospace);
          font-size: 10px;
          color: rgba(255, 255, 255, 0.45);
        }
        .relic-lock-bar {
          height: 3px;
          background: rgba(255, 255, 255, 0.08);
          border-radius: 2px;
          margin-top: 10px;
          overflow: hidden;
        }
        .relic-lock-bar-fill {
          height: 100%;
          width: 0%;
          background: linear-gradient(90deg, #7ec8e3, #d4af37);
          transition: width 0.08s linear;
        }

        /* Lock Victory Banner */
        .relic-victory-panel {
          padding: 24px;
          background: linear-gradient(180deg, rgba(212, 175, 55, 0.08) 0%, rgba(17, 27, 39, 0.95) 100%);
          border-top: 1px solid rgba(212, 175, 55, 0.35);
          display: none;
          animation: bannerFadeIn 0.4s ease forwards;
        }
        .relic-victory-panel.visible {
          display: block;
        }
        @keyframes bannerFadeIn {
          from { opacity: 0; transform: translateY(6px); }
          to { opacity: 1; transform: translateY(0); }
        }
        .victory-title {
          font-family: var(--serif, serif);
          font-size: 16px;
          color: #f2dc87;
          margin: 0 0 8px 0;
          letter-spacing: 0.06em;
        }
        .victory-lore-text {
          font-family: var(--serif, serif);
          font-size: 12px;
          line-height: 1.7;
          color: #d1dde8;
          margin: 0 0 16px 0;
          font-style: italic;
        }
        .victory-actions {
          display: flex;
          gap: 12px;
        }
        .victory-btn {
          font-family: var(--mono, monospace);
          font-size: 11px;
          padding: 7px 18px;
          border-radius: 4px;
          cursor: pointer;
          transition: all 0.2s ease;
        }
        .victory-btn.primary {
          background: #d4af37;
          color: #0b1118;
          border: 1px solid #d4af37;
          font-weight: 600;
        }
        .victory-btn.primary:hover {
          background: #f2dc87;
          box-shadow: 0 0 14px rgba(242, 220, 135, 0.45);
        }
        .victory-btn.secondary {
          background: transparent;
          color: rgba(255, 255, 255, 0.7);
          border: 1px solid rgba(255, 255, 255, 0.2);
        }
        .victory-btn.secondary:hover {
          color: #fff;
          border-color: rgba(255, 255, 255, 0.4);
        }

        /* Golden Toast Notification Overlay */
        #scanner-golden-toast {
          position: absolute;
          top: 14%;
          left: 50%;
          transform: translateX(-50%) translateY(-10px);
          padding: 12px 26px;
          border: 1px solid rgba(242, 220, 135, 0.6);
          border-radius: 28px;
          background: rgba(17, 27, 39, 0.94);
          backdrop-filter: blur(16px);
          box-shadow: 0 8px 32px rgba(0, 0, 0, 0.5), 0 0 24px rgba(242, 220, 135, 0.25);
          color: #f7f9fb;
          font-family: var(--serif, serif);
          font-size: 12px;
          letter-spacing: 0.06em;
          z-index: 999;
          opacity: 0;
          pointer-events: none;
          transition: all 0.45s cubic-bezier(0.16, 1, 0.3, 1);
          text-align: center;
        }
        #scanner-golden-toast.show {
          opacity: 1;
          transform: translateX(-50%) translateY(0);
        }
      `;
      document.head.appendChild(style);
    },

    injectDOM() {
      // 1. Scanner 3D Overlay Canvas
      let canvas = document.getElementById('scanner-overlay-canvas');
      if (!canvas) {
        canvas = document.createElement('canvas');
        canvas.id = 'scanner-overlay-canvas';
        const world = document.getElementById('world') || document.body;
        world.appendChild(canvas);
      }

      // 2. Proximity HUD Prompt
      let prompt = document.getElementById('relic-proximity-prompt');
      if (!prompt) {
        prompt = document.createElement('div');
        prompt.id = 'relic-proximity-prompt';
        prompt.innerHTML = `
          <div class="prompt-radar-icon">📡</div>
          <div class="prompt-content">
            <span class="prompt-headline">[ 按 E 或点击 调谐深空信号 ]</span>
            <span class="prompt-detail" id="prompt-target-detail">未知信标 // 距离: 1,840 U</span>
          </div>
        `;
        const world = document.getElementById('world') || document.body;
        world.appendChild(prompt);
      }

      // 3. Relic Tuner Modal
      let modal = document.getElementById('relic-tuner-modal');
      if (!modal) {
        modal = document.createElement('div');
        modal.id = 'relic-tuner-modal';
        modal.innerHTML = `
          <div class="relic-modal-frame">
            <div class="relic-modal-header">
              <div class="relic-header-titles">
                <span class="relic-tag-badge mono" id="tuner-category-tag">ORIGAMI RELIC // 信号破译</span>
                <h3 class="relic-heading serif" id="tuner-title-text">深空折纸信标破译仪</h3>
                <div class="relic-subheading mono" id="tuner-coord-text">TARGET: UNKNOWN // COORD: CHUNK-00</div>
              </div>
              <button class="relic-close-btn mono" id="tuner-close-button">关闭 [ESC]</button>
            </div>

            <div class="relic-scope-wrapper">
              <canvas id="relic-waveform-canvas" width="640" height="220"></canvas>
              <div class="relic-scope-info">
                <div class="scope-legend-group">
                  <span class="legend-carrier">── 载波信号 (Carrier Wave)</span>
                  <span class="legend-receiver">── 接收波形 (Receiver Wave)</span>
                </div>
                <div class="scope-status-metric mono" id="tuner-metric-text">谐振度: 0.0%</div>
              </div>
            </div>

            <div class="relic-controls-box" id="tuner-controls-box">
              <div class="relic-slider-container">
                <span class="relic-freq-tag mono">1.0 GHz</span>
                <input type="range" class="paper-range-slider" id="tuner-slider-input" min="1.0" max="8.0" step="0.01" value="1.8">
                <span class="relic-freq-tag right mono">8.0 GHz</span>
              </div>
              <div class="relic-tuner-guide">
                <span>滑动滑块 / 拖动画布 / 按 A-D 键匹配载波波形</span>
                <span id="tuner-lock-counter">锁定累积: 0.0s / 1.2s</span>
              </div>
              <div class="relic-lock-bar">
                <div class="relic-lock-bar-fill" id="tuner-lock-bar-fill"></div>
              </div>
            </div>

            <div class="relic-victory-panel" id="tuner-victory-panel">
              <h4 class="victory-title serif">✦ 谐振锁定 · 远古折纸密文破译完成 ✦</h4>
              <p class="victory-lore-text serif" id="tuner-lore-content">“在光线无法逃逸的深渊边缘，我们曾折叠过第七个维度……”</p>
              <div class="victory-actions">
                <button class="victory-btn primary mono" id="tuner-view-codex-btn">查阅星图手札 [Tab]</button>
                <button class="victory-btn secondary mono" id="tuner-continue-flight-btn">继续星海巡游</button>
              </div>
            </div>
          </div>
        `;
        document.body.appendChild(modal);
      }

      // 4. Golden Toast Element
      let goldenToast = document.getElementById('scanner-golden-toast');
      if (!goldenToast) {
        goldenToast = document.createElement('div');
        goldenToast.id = 'scanner-golden-toast';
        document.body.appendChild(goldenToast);
      }

      this.scopeCanvas = document.getElementById('relic-waveform-canvas');
      if (this.scopeCanvas) {
        this.scopeCtx = this.scopeCanvas.getContext('2d');
      }
    },

    bindEvents() {
      // 1. Radar button click
      const radarBtn = document.getElementById('radar-toggle');
      if (radarBtn) {
        radarBtn.addEventListener('click', () => ScannerRadar.ping());
      }

      // 2. Proximity Prompt click
      const prompt = document.getElementById('relic-proximity-prompt');
      if (prompt) {
        prompt.addEventListener('click', () => {
          if (this.currentTarget) this.open(this.currentTarget);
        });
      }

      // 3. Modal close button
      const closeBtn = document.getElementById('tuner-close-button');
      if (closeBtn) {
        closeBtn.addEventListener('click', () => this.close());
      }

      const contBtn = document.getElementById('tuner-continue-flight-btn');
      if (contBtn) {
        contBtn.addEventListener('click', () => this.close());
      }

      const codexBtn = document.getElementById('tuner-view-codex-btn');
      if (codexBtn) {
        codexBtn.addEventListener('click', () => {
          this.close();
          if (window.Codex && window.Codex.open) {
            window.Codex.open();
          } else if (window.Starfield && window.Starfield.toggleCodex) {
            window.Starfield.toggleCodex();
          }
        });
      }

      // 4. Frequency Slider
      const slider = document.getElementById('tuner-slider-input');
      if (slider) {
        slider.addEventListener('input', (e) => {
          this.setFrequency(parseFloat(e.target.value));
        });
      }

      // 5. Canvas Drag to Tune
      if (this.scopeCanvas) {
        let isDragging = false;
        let startX = 0;
        let startFreq = 0;

        const onDown = (clientX) => {
          if (this.isLocked) return;
          isDragging = true;
          startX = clientX;
          startFreq = this.playerFreq;
        };

        const onMove = (clientX) => {
          if (!isDragging || this.isLocked) return;
          const dx = clientX - startX;
          const newFreq = Math.max(1.0, Math.min(8.0, startFreq + dx * 0.015));
          this.setFrequency(newFreq);
          if (slider) slider.value = newFreq;
        };

        const onUp = () => { isDragging = false; };

        this.scopeCanvas.addEventListener('mousedown', (e) => onDown(e.clientX));
        window.addEventListener('mousemove', (e) => onMove(e.clientX));
        window.addEventListener('mouseup', onUp);

        this.scopeCanvas.addEventListener('touchstart', (e) => {
          if (e.touches.length > 0) onDown(e.touches[0].clientX);
        }, { passive: true });
        window.addEventListener('touchmove', (e) => {
          if (e.touches.length > 0) onMove(e.touches[0].clientX);
        }, { passive: true });
        window.addEventListener('touchend', onUp);
      }

      // 6. Global Keydown Handlers (R, E, A, D, Left, Right, Escape)
      window.addEventListener('keydown', (e) => {
        if (e.target instanceof HTMLInputElement || e.target instanceof HTMLTextAreaElement) return;

        // Hotkey R: Radar Ping
        if (e.code === 'KeyR' || e.key.toLowerCase() === 'r') {
          if (!this.isOpen) {
            e.preventDefault();
            ScannerRadar.ping();
          }
        }

        // Hotkey E: Open Relic Tuner when prompt visible
        if (e.code === 'KeyE' || e.key.toLowerCase() === 'e') {
          if (!this.isOpen && this.currentTarget) {
            e.preventDefault();
            this.open(this.currentTarget);
          }
        }

        // Tuner controls when modal is open
        if (this.isOpen && !this.isLocked) {
          if (e.code === 'KeyA' || e.key === 'ArrowLeft') {
            e.preventDefault();
            const nf = Math.max(1.0, this.playerFreq - 0.05);
            this.setFrequency(nf);
            if (slider) slider.value = nf;
          } else if (e.code === 'KeyD' || e.key === 'ArrowRight') {
            e.preventDefault();
            const nf = Math.min(8.0, this.playerFreq + 0.05);
            this.setFrequency(nf);
            if (slider) slider.value = nf;
          } else if (e.key === 'Escape') {
            e.preventDefault();
            this.close();
          }
        }
      });
    },

    updateProximityPrompt(nearestTarget, dist) {
      const prompt = document.getElementById('relic-proximity-prompt');
      if (!prompt) return;

      if (nearestTarget && !this.isOpen) {
        this.currentTarget = nearestTarget;
        prompt.classList.add('visible');
        const detailEl = document.getElementById('prompt-target-detail');
        if (detailEl) {
          detailEl.textContent = `${nearestTarget.name} // 距离: ${Math.round(dist)} U`;
        }
      } else {
        prompt.classList.remove('visible');
        if (!this.isOpen) this.currentTarget = null;
      }
    },

    open(target) {
      if (!target) return;
      this.isOpen = true;
      this.currentTarget = target;
      this.targetFreq = target.targetFreq || 3.42;
      // Start slightly detuned for engaging gameplay
      this.playerFreq = Math.max(1.0, Math.min(8.0, this.targetFreq + (Math.random() > 0.5 ? 1.5 : -1.5)));
      this.alignment = 0.0;
      this.lockHoldTime = 0.0;
      this.isLocked = false;

      // Update Header Text
      const titleEl = document.getElementById('tuner-title-text');
      if (titleEl) titleEl.textContent = `${target.name} · 信号调谐`;
      const tagEl = document.getElementById('tuner-category-tag');
      if (tagEl) tagEl.textContent = `TARGET [${target.id.toUpperCase()}] // FREQ: ${this.targetFreq.toFixed(2)} GHz`;
      const coordEl = document.getElementById('tuner-coord-text');
      if (coordEl) coordEl.textContent = `SPATIAL COORD: [${Math.round(target.x)}, ${Math.round(target.y)}, ${Math.round(target.z)}]`;

      const slider = document.getElementById('tuner-slider-input');
      if (slider) slider.value = this.playerFreq;

      const victoryPanel = document.getElementById('tuner-victory-panel');
      if (victoryPanel) victoryPanel.classList.remove('visible');
      const controlsBox = document.getElementById('tuner-controls-box');
      if (controlsBox) controlsBox.style.display = 'block';

      const modal = document.getElementById('relic-tuner-modal');
      if (modal) modal.classList.add('open');

      // Hide proximity prompt while modal is active
      const prompt = document.getElementById('relic-proximity-prompt');
      if (prompt) prompt.classList.remove('visible');

      // Start Web Audio Static Hiss & Resonance Tone
      ScannerAudio.startTuningAudio();
    },

    close() {
      this.isOpen = false;
      const modal = document.getElementById('relic-tuner-modal');
      if (modal) modal.classList.remove('open');
      ScannerAudio.stopTuningAudio();
    },

    setFrequency(freq) {
      this.playerFreq = Math.max(1.0, Math.min(8.0, freq));
    },

    // Programmatic auto-solve (useful for tests or assistive actions)
    solve() {
      if (!this.isOpen) {
        if (this.currentTarget) this.open(this.currentTarget);
        else if (ScannerRadar.candidates.length > 0) this.open(ScannerRadar.candidates[0]);
        else return;
      }
      this.playerFreq = this.targetFreq;
      this.alignment = 1.0;
      this.lockHoldTime = this.lockRequired;
      this.triggerSignalLock();
    },

    triggerSignalLock() {
      if (this.isLocked) return;
      this.isLocked = true;

      // 1. Audio: Static noise fades into clear celestial chime chord!
      ScannerAudio.stopTuningAudio();
      ScannerAudio.playCelestialChime();

      // 2. Mark target as deciphered
      if (this.currentTarget) {
        this.currentTarget.solved = true;
        ScannerRadar.detectedTargets.set(this.currentTarget.key, this.currentTarget);
      }

      // 3. Unlock classified lore into Codex
      let lore = this.currentTarget && this.currentTarget.lore;
      if (!lore) {
        lore = RELIC_ARCHIVE[Math.floor(Math.random() * RELIC_ARCHIVE.length)];
      }

      if (window.Codex && window.Codex.unlock) {
        window.Codex.unlock(lore.id, lore);
      } else if (window.Codex && window.Codex.discover) {
        window.Codex.discover(lore.id, lore.name);
      }

      // 4. Trigger Golden Discovery Toast
      this.showGoldenToast(`✦ 信号谐振锁定！已破译深空密文【${lore.name}】 · 已录入星图手札`);

      // 5. Update Victory Panel
      const victoryPanel = document.getElementById('tuner-victory-panel');
      const loreContent = document.getElementById('tuner-lore-content');
      if (loreContent) loreContent.textContent = lore.desc;
      if (victoryPanel) victoryPanel.classList.add('visible');

      const controlsBox = document.getElementById('tuner-controls-box');
      if (controlsBox) controlsBox.style.display = 'none';
    },

    showGoldenToast(text) {
      // Also invoke game's internal toast if present
      if (typeof window.toast === 'function') {
        window.toast(text);
      } else {
        const gameToast = document.getElementById('toast');
        if (gameToast) {
          gameToast.textContent = text;
          gameToast.style.opacity = '1';
          setTimeout(() => { gameToast.style.opacity = '0'; }, 4000);
        }
      }

      // Standalone Golden Shimmer Banner
      const gToast = document.getElementById('scanner-golden-toast');
      if (gToast) {
        gToast.textContent = text;
        gToast.classList.add('show');
        setTimeout(() => gToast.classList.remove('show'), 4200);
      }
    },

    update(dt) {
      if (!this.isOpen) return;
      this.animTime += dt;

      // Calculate harmonic resonance alignment
      const delta = Math.abs(this.playerFreq - this.targetFreq);
      // Resonance drops off as delta grows: tolerance curve
      const resonance = Math.max(0, 1 - Math.pow(delta / 0.42, 1.35));
      this.alignment = resonance;

      // Update Audio Filter & Volumes
      ScannerAudio.updateTuningAudio(this.playerFreq, this.alignment);

      // Check Harmonic Lock Requirement (>95% for 1.2s)
      if (!this.isLocked) {
        if (this.alignment >= 0.95) {
          this.lockHoldTime += dt;
          if (this.lockHoldTime >= this.lockRequired) {
            this.triggerSignalLock();
          }
        } else {
          this.lockHoldTime = Math.max(0, this.lockHoldTime - dt * 1.5);
        }
      }

      // Update UI Metrics
      const metricEl = document.getElementById('tuner-metric-text');
      if (metricEl) {
        const pct = (this.alignment * 100).toFixed(1);
        metricEl.textContent = this.isLocked
          ? '✦ 谐振锁定已达成 (100.0%)'
          : `谐振度: ${pct}% ${this.alignment >= 0.95 ? ' [锁定中...]' : ''}`;
        metricEl.style.color = this.isLocked ? '#f2dc87' : this.alignment >= 0.95 ? '#d4af37' : '#f7f9fb';
      }

      const counterEl = document.getElementById('tuner-lock-counter');
      if (counterEl) {
        counterEl.textContent = `锁定累积: ${this.lockHoldTime.toFixed(1)}s / ${this.lockRequired.toFixed(1)}s`;
      }

      const barFill = document.getElementById('tuner-lock-bar-fill');
      if (barFill) {
        const fillPct = Math.min(100, (this.lockHoldTime / this.lockRequired) * 100);
        barFill.style.width = `${fillPct}%`;
      }

      // Render Oscilloscope
      this.drawScope();
    },

    drawScope() {
      if (!this.scopeCtx || !this.scopeCanvas) return;
      const ctx = this.scopeCtx;
      const w = this.scopeCanvas.width;
      const h = this.scopeCanvas.height;
      const cy = h * 0.5;

      // Dark Paper Canvas Background
      ctx.fillStyle = '#080d14';
      ctx.fillRect(0, 0, w, h);

      // Oscilloscope Grid Lines (Papercraft ticks)
      ctx.strokeStyle = 'rgba(255, 255, 255, 0.05)';
      ctx.lineWidth = 1;
      ctx.beginPath();
      for (let x = 0; x <= w; x += 40) { ctx.moveTo(x, 0); ctx.lineTo(x, h); }
      for (let y = 0; y <= h; y += 30) { ctx.moveTo(0, y); ctx.lineTo(w, y); }
      ctx.stroke();

      // Center baseline
      ctx.strokeStyle = 'rgba(255, 255, 255, 0.12)';
      ctx.beginPath();
      ctx.moveTo(0, cy); ctx.lineTo(w, cy);
      ctx.stroke();

      const t = this.animTime;
      const amp = 46;

      // 1. Target Carrier Wave (Golden Harmonic Curve)
      ctx.save();
      ctx.strokeStyle = this.isLocked ? 'rgba(255, 240, 180, 0.95)' : '#d4af37';
      ctx.lineWidth = this.isLocked ? 3.0 : 2.0;
      ctx.shadowBlur = this.isLocked ? 14 : 6;
      ctx.shadowColor = '#d4af37';
      ctx.beginPath();

      for (let x = 0; x < w; x++) {
        const nx = (x / w) * 16;
        const y = cy + amp * Math.sin(nx * this.targetFreq + t * 2.2)
                     + (amp * 0.35) * Math.sin(nx * (this.targetFreq * 2.1) - t * 1.4);
        if (x === 0) ctx.moveTo(x, y); else ctx.lineTo(x, y);
      }
      ctx.stroke();
      ctx.restore();

      // 2. Player Receiver Wave (Adjustable Cyan Curve)
      if (!this.isLocked) {
        ctx.save();
        ctx.strokeStyle = '#7ec8e3';
        ctx.lineWidth = 1.8;
        ctx.shadowBlur = 6;
        ctx.shadowColor = '#7ec8e3';
        ctx.beginPath();

        for (let x = 0; x < w; x++) {
          const nx = (x / w) * 16;
          const y = cy + amp * Math.sin(nx * this.playerFreq + t * 2.2)
                       + (amp * 0.35) * Math.sin(nx * (this.playerFreq * 2.1) - t * 1.4);
          if (x === 0) ctx.moveTo(x, y); else ctx.lineTo(x, y);
        }
        ctx.stroke();
        ctx.restore();
      }

      // 3. Locked Harmonic Beam effect
      if (this.isLocked) {
        ctx.save();
        ctx.strokeStyle = 'rgba(255, 255, 255, 0.9)';
        ctx.lineWidth = 1.5;
        ctx.shadowBlur = 20;
        ctx.shadowColor = '#fff';
        ctx.beginPath();
        for (let x = 0; x < w; x++) {
          const nx = (x / w) * 16;
          const y = cy + (amp * 0.8) * Math.sin(nx * this.targetFreq + t * 2.2);
          if (x === 0) ctx.moveTo(x, y); else ctx.lineTo(x, y);
        }
        ctx.stroke();
        ctx.restore();
      }
    }
  };

  // ============================================================================
  // 5. MAIN SCANNER ENGINE FACADE & ANIMATION LOOP
  // ============================================================================
  let isInitialized = false;
  let lastFrameTime = performance.now();

  function onFrame(now) {
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
      const dpr = Math.min(window.devicePixelRatio || 1, 2);
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
  }

  const AnomalyScanner = {
    version: '1.0.0-origami-radar',

    isInitialized() {
      return isInitialized;
    },

    init() {
      if (isInitialized) return;
      isInitialized = true;

      ScannerAudio.init();
      RelicTuner.init();

      lastFrameTime = performance.now();
      requestAnimationFrame(onFrame);

      console.log('📡 [AnomalyScanner] Deep Space Radar & Relic Deciphering System initialized.');
    },

    ping() {
      ScannerAudio.init();
      ScannerRadar.ping();
    },

    openTuner(target) {
      if (target) {
        RelicTuner.open(target);
      } else if (ScannerRadar.candidates.length > 0) {
        RelicTuner.open(ScannerRadar.candidates[0]);
      } else {
        ScannerRadar.gatherCandidates();
        if (ScannerRadar.candidates.length > 0) {
          RelicTuner.open(ScannerRadar.candidates[0]);
        }
      }
    },

    closeTuner() {
      RelicTuner.close();
    },

    tune(freq) {
      RelicTuner.setFrequency(freq);
      const slider = document.getElementById('tuner-slider-input');
      if (slider) slider.value = freq;
    },

    solveTuner() {
      RelicTuner.solve();
    },

    unlockRelic(target) {
      let lore = (target && target.lore) || RELIC_ARCHIVE[0];
      if (window.Codex && window.Codex.unlock) {
        window.Codex.unlock(lore.id, lore);
      }
      RelicTuner.showGoldenToast(`✦ 已录入图鉴密文【${lore.name}】`);
    },

    getState() {
      return {
        radarActive: ScannerRadar.active,
        radarWaveDist: ScannerRadar.waveDist,
        detectedCount: ScannerRadar.detectedTargets.size,
        tunerOpen: RelicTuner.isOpen,
        tunerFrequency: RelicTuner.playerFreq,
        targetFrequency: RelicTuner.targetFreq,
        alignment: RelicTuner.alignment,
        lockHoldTime: RelicTuner.lockHoldTime,
        isLocked: RelicTuner.isLocked
      };
    },

    getTargets() {
      return Array.from(ScannerRadar.detectedTargets.values());
    },

    getCandidates() {
      return ScannerRadar.candidates;
    }
  };

  // Expose to window
  window.AnomalyScanner = AnomalyScanner;

  // Auto-initialize when ready
  if (document.readyState === 'complete' || document.readyState === 'interactive') {
    AnomalyScanner.init();
  } else {
    window.addEventListener('DOMContentLoaded', () => AnomalyScanner.init());
  }

})(typeof window !== 'undefined' ? window : this);
