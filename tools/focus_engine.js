/**
 * ============================================================================
 * STARFIELD FOCUS EXPEDITION ENGINE (深空专注番茄钟引擎)
 * ============================================================================
 * Gamified Deep Space Focus Pomodoro for Starfield.
 * 
 * Rules:
 * - Select 15min / 25min / 30min / 60min / Custom Deep Space Focus Voyage.
 * - Ship enters autonomous cruise with soothing classical music & cosmic vistas.
 * - Screen WakeLock keeps phone as an ambient deep space desk clock.
 * - Leaving the app (visibilitychange/blur) triggers a 10s emergency warp collapse.
 * - Abandoning the mission leads to fuel depletion crash / black hole swallow!
 * - Successfully completing the voyage unlocks exclusive origami hulls, trails & relics!
 * ============================================================================
 */

(function(global) {
  'use strict';

  const STORAGE_KEY = 'starfield_focus_v1';

  const FOCUS_PRESETS = [
    { id: 'trial', name: '深空试航', durationMinutes: 15, tag: '短时专注', desc: '15分钟高效短冲，适合晨间规划与阅读整理。' },
    { id: 'pomodoro', name: '经典番茄钟', durationMinutes: 25, tag: '标准冲刺', desc: '25分钟经典心流，让深空星光陪伴高度专注。' },
    { id: 'cruise', name: '深空巡航', durationMinutes: 30, tag: '深度自习', desc: '30分钟持续巡航，完成解锁【专注曜金·泰坦折纸舰】。' },
    { id: 'voyage', name: '跨星系远征', durationMinutes: 60, tag: '终极挑战', desc: '60分钟高难远征，完成解锁【黄金纪元光流】与先行者密文。' }
  ];

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
      this.currentPreset = FOCUS_PRESETS[2]; // Default 30min

      this.stats = this.loadStats();
      this.onTick = null;
      this.onStateChange = null;

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
          // User switched away / locked phone / left app
          this.triggerWarning();
        } else {
          // User returned
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

    // Start a Focus Mission
    startMission(durationMinutes = 30) {
      this.targetDurationSec = Math.max(60, durationMinutes * 60);
      this.elapsedSec = 0;
      this.state = 'RUNNING';
      this.startTravel = typeof travel !== 'undefined' ? travel : 0;

      // Ensure flight started & autonomous camera
      if (typeof window !== 'undefined' && window.Starfield) {
        if (!window.Starfield.getState().started && typeof window.Starfield.beginFlight === 'function') {
          window.Starfield.beginFlight();
        }
      }

      this.requestWakeLock();

      if (this.timerId) clearInterval(this.timerId);
      this.timerId = setInterval(() => this.tick(), 1000);

      if (typeof toast === 'function') {
        toast(`✦ 专注深空远征启航 · 目标 ${durationMinutes} 分钟 · 勿切后台 ✦`, 6);
      }

      this.notifyState();
    }

    tick() {
      if (this.state !== 'RUNNING') return;

      this.elapsedSec++;

      // Check for mission completion
      if (this.elapsedSec >= this.targetDurationSec) {
        this.completeMission();
        return;
      }

      this.notifyTick();
    }

    triggerWarning() {
      if (this.state !== 'RUNNING') return;
      this.state = 'WARNING';
      this.warningRemainingSec = 10;

      if (typeof toast === 'function') {
        toast('⚠️ 警告：检测到离开星舰！引力约束将在 10 秒后瓦解！请立即返回！', 5);
      }

      if (this.warningTimerId) clearInterval(this.warningTimerId);
      this.warningTimerId = setInterval(() => {
        this.warningRemainingSec--;
        if (this.warningRemainingSec <= 0) {
          clearInterval(this.warningTimerId);
          this.warningTimerId = null;
          this.failMission();
        } else {
          if (typeof toast === 'function') {
            toast(`⚠️ 偏离航道！剩余 ${this.warningRemainingSec} 秒坠毁！立即返回！`, 1.5);
          }
        }
        this.notifyTick();
      }, 1000);

      this.notifyState();
    }

    clearWarning() {
      if (this.state !== 'WARNING') return;
      if (this.warningTimerId) {
        clearInterval(this.warningTimerId);
        this.warningTimerId = null;
      }
      this.state = 'RUNNING';
      if (typeof toast === 'function') {
        toast('✦ 引力约束已恢复重稳 · 继续专注深空巡航 ✦', 4);
      }
      this.notifyState();
    }

    // Complete Mission
    completeMission() {
      if (this.timerId) { clearInterval(this.timerId); this.timerId = null; }
      this.state = 'SUCCESS';
      this.releaseWakeLock();

      const focusedMinutes = Math.round(this.targetDurationSec / 60);
      this.stats.totalFocusMinutes += focusedMinutes;
      this.stats.completedVoyages++;
      this.stats.currentStreak++;
      if (this.stats.currentStreak > this.stats.bestStreak) {
        this.stats.bestStreak = this.stats.currentStreak;
      }

      // Check Rewards Unlock
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

      // Trigger glorious celebration sequence in game
      if (typeof window !== 'undefined' && typeof window.triggerTesseract === 'function') {
        window.triggerTesseract();
      }
      if (typeof toast === 'function') {
        toast(`🏆 专注远征圆满达成！已累积专注 ${this.stats.totalFocusMinutes} 分钟！`, 8);
      }

      this.showSummaryModal(true, focusedMinutes, rewardsEarned);
      this.notifyState();
    }

    // Fail Mission (Crashed / Black Hole Swallowed)
    failMission() {
      if (this.timerId) { clearInterval(this.timerId); this.timerId = null; }
      if (this.warningTimerId) { clearInterval(this.warningTimerId); this.warningTimerId = null; }
      this.state = 'FAILED';
      this.releaseWakeLock();

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
      if (typeof WarpDrive !== 'undefined') {
        WarpDrive.shake = 6.0;
        WarpDrive.brakeKick = 200;
        WarpDrive.currentWarp = 0;
      }
      if (typeof capturePhase !== 'undefined') {
        capturePhase = 2; // Black hole event horizon plunge
      }

      if (typeof toast === 'function') {
        toast('💥 航行失败 · 离开星舰导致燃料耗尽，已被深空黑洞奇点吞噬！', 8);
      }

      this.showSummaryModal(false, elapsedMin, []);
      this.notifyState();
    }

    // Cancel Mission manually
    cancelMission() {
      if (this.state === 'RUNNING' || this.state === 'WARNING') {
        if (confirm('确认放弃当前深空远征？放弃将导致星舰失控并坠入黑洞！')) {
          this.failMission();
        }
      } else {
        this.state = 'IDLE';
        this.notifyState();
      }
    }

    notifyTick() {
      if (this.onTick) this.onTick(this.getRemainingSec(), this.elapsedSec, this.targetDurationSec);
    }

    notifyState() {
      if (this.onStateChange) this.onStateChange(this.state);
    }

    getRemainingSec() {
      return Math.max(0, this.targetDurationSec - this.elapsedSec);
    }

    formatTime(seconds) {
      const m = Math.floor(seconds / 60);
      const s = Math.floor(seconds % 60);
      return `${m < 10 ? '0' : ''}${m}:${s < 10 ? '0' : ''}${s}`;
    }

    // Summary Modal (Success / Failure Dialog)
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
            你保持专注不触碰手机，完成了 <strong>${minutes} 分钟</strong> 的全景深空漫游探索！
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
        setTimeout(() => modal.remove(), 300);
        this.state = 'IDLE';
        this.notifyState();
      });
    }
  }

  global.StarfieldFocusEngine = new StarfieldFocusEngine();
  global.FOCUS_PRESETS = FOCUS_PRESETS;

})(typeof window !== 'undefined' ? window : globalThis);
