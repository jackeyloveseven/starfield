# -*- coding: utf-8 -*-
"""
Stage 2 Deterministic Patch Script for Starfield v2.0.0.0 (Build 200):
1. Cohesive Core Gameplay Loop (window.StarfieldExpedition: 8-Tier Pilot Rank, XP/Combo economy,
   Context-Aware Tactical Action Capsule, Interactive Expedition Directive HUD, and full synergy across
   Sonar Scan, Gravitational Slingshot, Orbital Probe Shockwave, Relic Frequency Tuner, Hazard Graze Evasion,
   Core Hatchery, and Ship Equipment Upgrades).
2. Flagship App Shell Experience (window.StarfieldAppShell: Unified Desktop & Mobile Command Dock,
   Quick-Switch Modal Mutex Hub, Native Android Haptics & Lifecycle Bridge hooks).
3. Version Bump to v2.0.0.0 (Build 200) across starfield.html, version.json, service-worker.js
   and 100% SHA256 mirror parity to android/app/src/main/assets/.
"""
import json
import re
import shutil
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
HTML_PATH = BASE / 'starfield.html'
SW_PATH = BASE / 'service-worker.js'
VER_PATH = BASE / 'version.json'
STUDIO_PATH = BASE / 'planet_studio.html'
ASSETS_DIR = BASE / 'android' / 'app' / 'src' / 'main' / 'assets'


def patch_starfield_html(html: str) -> str:
    # 0. Idempotency strip if re-running
    html = re.sub(
        r'\n*<!-- === BUILD 200 GAMEPLAY & APP SHELL OVERHAUL START === -->.*?<!-- === BUILD 200 GAMEPLAY & APP SHELL OVERHAUL END === -->\n*',
        '\n',
        html,
        flags=re.DOTALL,
    )

    # 1. Version anchors in starfield.html -> v2.0.0.0 (Build 200) & localBuild = 200
    html, n_ver_tag = re.subn(
        r'id="sf-version-tag">v[0-9.]+ \(Build \d+\)<',
        'id="sf-version-tag">v2.0.0.0 (Build 200)<',
        html,
        count=1,
    )
    assert n_ver_tag == 1, f'Expected 1 sf-version-tag replacement, got {n_ver_tag}'

    html, n_local_build = re.subn(
        r'const localBuild = \d+;',
        'const localBuild = 200;',
        html,
        count=1,
    )
    assert n_local_build == 1, f'Expected 1 localBuild replacement, got {n_local_build}'

    # 2. Desktop Command Dock (#controls): add Planetarium/Cores, Ship Upgrades, and Focus Expedition buttons if not already present
    if 'id="planet-toggle"' not in html:
        target_controls = """<button class="control" id="hangar-toggle" title="舰队折纸坞 · 舰体与尾迹定制 (H)" aria-label="舰队折纸坞">
<span class="icon hangar-icon">
<svg viewBox="0 0 16 16" width="16" height="16" fill="none" stroke="currentColor" stroke-width="1.3">
<polygon points="8,1.5 12.5,6.5 8,14.5 3.5,6.5" stroke="currentColor" stroke-linejoin="round"/>
<line x1="3.5" y1="6.5" x2="12.5" y2="6.5" stroke="currentColor"/>
<line x1="8" y1="1.5" x2="8" y2="14.5" stroke="currentColor"/>
<polygon points="3.5,6.5 1,10 4,11" stroke="currentColor" stroke-linejoin="round"/>
<polygon points="12.5,6.5 15,10 12,11" stroke="currentColor" stroke-linejoin="round"/>
</svg>
</span>
</button>"""
        replacement_controls = target_controls + """
<button class="control" id="planet-toggle" title="深空天象馆与星核孵化 (L)" aria-label="深空天象馆">
<span class="icon planet-icon">
<svg viewBox="0 0 16 16" width="16" height="16" fill="none" stroke="currentColor" stroke-width="1.3">
<circle cx="8" cy="8" r="4.2"/>
<ellipse cx="8" cy="8" rx="7" ry="2.2" transform="rotate(-18 8 8)"/>
</svg>
</span>
<span id="sf-dock-core-count" class="sf-dock-count-tag" style="display:none">0</span>
</button>
<button class="control" id="upgrades-toggle" title="舰载装备与设备升级工坊 (U)" aria-label="舰载装备工坊">
<span class="icon upgrades-icon">
<svg viewBox="0 0 16 16" width="16" height="16" fill="none" stroke="currentColor" stroke-width="1.3">
<polygon points="8,2 13.5,5.2 13.5,10.8 8,14 2.5,10.8 2.5,5.2" stroke-linejoin="round"/>
<path d="M8 5.2V10.8M5.5 7.5L8 5.2L10.5 7.5" stroke-linecap="round" stroke-linejoin="round"/>
</svg>
</span>
</button>
<button class="control" id="focus-toggle" title="深空专注远征 · 引力时间流 (O)" aria-label="深空专注远征">
<span class="icon focus-icon">
<svg viewBox="0 0 16 16" width="16" height="16" fill="none" stroke="currentColor" stroke-width="1.3">
<circle cx="8" cy="8.5" r="5.2"/>
<path d="M8 5.8V8.5L10 10M6.5 2H9.5" stroke-linecap="round" stroke-linejoin="round"/>
</svg>
</span>
</button>"""
        assert target_controls in html, 'Could not find #hangar-toggle in #controls'
        html = html.replace(target_controls, replacement_controls, 1)

    # 3. Fix StarfieldSonar.triggerScan() so it always works (synthesizing a deep-space echo node if currentTarget is null),
    # actually credits Stardust to StarfieldInFlightExtraction, pings AnomalyScanner, and reports to StarfieldExpedition!
    old_sonar_scan = """  triggerScan() {
    if (this.currentTarget && window.SFProbe) window.SFProbe.scans++;
    if (!this.currentTarget) {
      if (typeof showToast === 'function') showToast('当前空域未检测到可测绘天体信号', 3); else if (typeof window.toast === 'function') window.toast('当前空域未检测到可测绘天体信号', 3);
      return;
    }
    const target = this.currentTarget;
    const now = performance.now();
    if (now - this.lastScanTime < 1500) return;
    this.lastScanTime = now;"""

    new_sonar_scan = """  triggerScan(forceSynthetic) {
    const now = performance.now();
    if (!forceSynthetic && now - this.lastScanTime < 1100) return;
    this.lastScanTime = now;
    if (window.SFProbe) window.SFProbe.scans = (window.SFProbe.scans || 0) + 1;
    const leadPos = (typeof craftWorld === 'function' && fleet && fleet[LEAD]) ? craftWorld(fleet[LEAD]) : [0, 0, (typeof travel !== 'undefined' ? travel : 0)];
    let target = this.currentTarget;
    if (!target) {
      const nearest = (window.SFProbe && typeof window.SFProbe.nearest === 'function') ? window.SFProbe.nearest() : null;
      if (nearest && Number.isFinite(nearest.x)) {
        target = nearest;
      } else {
        target = {
          x: leadPos[0] + (Math.sin(now * 0.0017) * 520),
          y: leadPos[1] + (Math.cos(now * 0.0013) * 240),
          z: leadPos[2] + 2800,
          name: '深空引力谐振节点'
        };
      }
    }"""

    if old_sonar_scan in html:
        html = html.replace(old_sonar_scan, new_sonar_scan, 1)
    html = html.replace(
        "      }\n    }\n\n    const leadPos = craftWorld(fleet[LEAD]);",
        "      }\n    }",
        1,
    )

    old_sonar_reward = """    const stardust = 150 + Math.floor(Math.random() * 120);
    const targetName = target.name || (target.w && target.w.name) || '深空未知天体';

    const foundCore = Math.random() < 0.22;
    if (foundCore && window.StarfieldHatch && typeof window.StarfieldHatch.addCores === 'function') {
      window.StarfieldHatch.addCores(1);
      const msg = `[天体共振] 成功测绘 ${targetName} · 捕获未开采星核 × 1 ✦`;
      if (typeof showToast === 'function') showToast(msg, 4);
      else if (typeof window.toast === 'function') window.toast(msg, 4);
    } else {
      const msg = `[巡天测绘完成] 测绘 ${targetName} · 获得星尘 +${stardust}`;
      if (typeof showToast === 'function') showToast(msg, 3);
      else if (typeof window.toast === 'function') window.toast(msg, 3);
    }

    if (typeof Codex !== 'undefined' && Codex.checkCelestialEncounter) {
      Codex.checkCelestialEncounter(target);
    }"""

    new_sonar_reward = """    const stardust = 180 + Math.floor(Math.random() * 110);
    const targetName = target.name || (target.w && target.w.name) || '深空未知天体';

    if (window.StarfieldInFlightExtraction && typeof window.StarfieldInFlightExtraction.addSecuredCredits === 'function') {
      window.StarfieldInFlightExtraction.addSecuredCredits(stardust);
    }
    const foundCore = Math.random() < 0.26;
    if (foundCore && window.StarfieldHatch && typeof window.StarfieldHatch.addCores === 'function') {
      window.StarfieldHatch.addCores(1);
      const msg = `✦ [天体共振] 成功测绘 ${targetName} · 星尘 +${stardust} · 捕获未开采星核 × 1 ✦`;
      if (typeof showToast === 'function') showToast(msg, 4);
      else if (typeof window.toast === 'function') window.toast(msg, 4);
    } else {
      const msg = `✦ [巡天测绘完成] 测绘 ${targetName} · 获得星尘 +${stardust} ✦`;
      if (typeof showToast === 'function') showToast(msg, 3);
      else if (typeof window.toast === 'function') window.toast(msg, 3);
    }

    if (window.AnomalyScanner && typeof window.AnomalyScanner.ping === 'function') {
      try { window.AnomalyScanner.ping(); } catch (e) {}
    }
    if (window.StarfieldExpedition && typeof window.StarfieldExpedition.recordAction === 'function') {
      window.StarfieldExpedition.recordAction('sonar_scan', { target: targetName, stardust: stardust, core: foundCore ? 1 : 0 });
    }
    if (typeof Codex !== 'undefined' && Codex.checkCelestialEncounter) {
      Codex.checkCelestialEncounter(target);
    }"""

    if old_sonar_reward in html:
        html = html.replace(old_sonar_reward, new_sonar_reward, 1)

    # 4. Synergize StarfieldOrbitalMechanics.triggerSlingshotBoost & triggerShockwave
    old_slingshot_boost = """    const pName = pm.name || (pm.w && pm.w.name) || '天体引力井';
    const msg = `✦ 触发【${pName}】行星引力弹弓！变轨加速 +280%！✦`;
    if (typeof showToast === 'function') showToast(msg, 3.5);
    else if (typeof window.toast === 'function') window.toast(msg, 3.5);
  },"""

    new_slingshot_boost = """    if (window.SFProbe) window.SFProbe.surges = (window.SFProbe.surges || 0) + 1;
    if (window.StarfieldFuelEngine) {
      window.StarfieldFuelEngine.fuel = Math.min(window.StarfieldFuelEngine.maxFuel, (window.StarfieldFuelEngine.fuel || 0) + window.StarfieldFuelEngine.maxFuel * 0.25);
      window.StarfieldFuelEngine.isDrifting = false;
      if (typeof window.StarfieldFuelEngine.updateHUD === 'function') window.StarfieldFuelEngine.updateHUD();
    }
    if (window.StarfieldInFlightExtraction && typeof window.StarfieldInFlightExtraction.addSecuredCredits === 'function') {
      window.StarfieldInFlightExtraction.addSecuredCredits(280);
    }
    const pName = pm.name || (pm.w && pm.w.name) || '天体引力井';
    if (window.StarfieldExpedition && typeof window.StarfieldExpedition.recordAction === 'function') {
      window.StarfieldExpedition.recordAction('slingshot_assist', { target: pName, stardust: 280 });
    }
    const msg = `✦ 触发【${pName}】行星引力弹弓 · 航速激增 +280% · 星尘 +280 · 燃料 +25% ✦`;
    if (typeof showToast === 'function') showToast(msg, 3.5);
    else if (typeof window.toast === 'function') window.toast(msg, 3.5);
  },"""

    if old_slingshot_boost in html:
        html = html.replace(old_slingshot_boost, new_slingshot_boost, 1)

    old_shockwave_reward = """    // Resonate with deep planetary core: awards unopened celestial core or telemetry stardust
    if (window.StarfieldHatch && typeof window.StarfieldHatch.addCores === 'function') {
      window.StarfieldHatch.addCores(1);
      const tName = targetMass ? (targetMass.name || (targetMass.w && targetMass.w.name) || '星体') : '深空';
      const msg = `✦ 探针引力弹弓共振【${tName}】星核！连锁冲击波扩散 · 捕获未开采星核 × 1！✦`;
      if (typeof showToast === 'function') showToast(msg, 3.5);
      else if (typeof window.toast === 'function') window.toast(msg, 3.5);
    }"""

    new_shockwave_reward = """    if (window.SFProbe) window.SFProbe.surges = (window.SFProbe.surges || 0) + 1;
    if (window.StarfieldInFlightExtraction && typeof window.StarfieldInFlightExtraction.addSecuredCredits === 'function') {
      window.StarfieldInFlightExtraction.addSecuredCredits(240);
    }
    // Resonate with deep planetary core: awards unopened celestial core or telemetry stardust
    if (window.StarfieldHatch && typeof window.StarfieldHatch.addCores === 'function') {
      window.StarfieldHatch.addCores(1);
      const tName = targetMass ? (targetMass.name || (targetMass.w && targetMass.w.name) || '星体') : '深空';
      const msg = `✦ 探针引力共振【${tName}】星核 · 星尘 +240 · 捕获未开采星核 × 1 ✦`;
      if (typeof showToast === 'function') showToast(msg, 3.5);
      else if (typeof window.toast === 'function') window.toast(msg, 3.5);
    }
    if (window.StarfieldExpedition && typeof window.StarfieldExpedition.recordAction === 'function') {
      window.StarfieldExpedition.recordAction('probe_shockwave', { stardust: 240, core: 1 });
    }"""

    if old_shockwave_reward in html:
        html = html.replace(old_shockwave_reward, new_shockwave_reward, 1)

    # 5. Synergize RelicTuner.triggerSignalLock() to reward Stardust, Core, and Rank XP
    old_relic_lock = """      // 4. Trigger Golden Discovery Toast
      this.showGoldenToast(`✦ 信号谐振锁定！已破译深空密文【${lore.name}】 · 已录入星图手札`);"""

    new_relic_lock = """      // 4. Award Stardust, Unopened Core & Expedition Rank XP on Relic Decipher
      if (window.StarfieldInFlightExtraction && typeof window.StarfieldInFlightExtraction.addSecuredCredits === 'function') {
        window.StarfieldInFlightExtraction.addSecuredCredits(500);
      }
      if (window.StarfieldHatch && typeof window.StarfieldHatch.addCores === 'function') {
        window.StarfieldHatch.addCores(1);
      }
      if (window.StarfieldExpedition && typeof window.StarfieldExpedition.recordAction === 'function') {
        window.StarfieldExpedition.recordAction('relic_decipher', { name: lore.name, stardust: 500, core: 1 });
      }
      this.showGoldenToast(`✦ 信号谐振锁定！破译【${lore.name}】 · 星尘 +500 · 星核 +1 ✦`);"""

    if old_relic_lock in html:
        html = html.replace(old_relic_lock, new_relic_lock, 1)

    # 6. Synergize SFHazard Graze / Evasion Bonus & SFVoyage completion + interactive methods
    old_hazard_check = """        var dx = p.x - corridorX(z.z) - z.off;
        var inDense = Math.abs(dx) < ZONE_W && Math.abs(dx) > (GAP_HALF - 40);
        if (inDense) applyDamage(BASE_HITS + (gear() >= 1 ? FAST_EXTRA : 0));"""

    new_hazard_check = """        var dx = p.x - corridorX(z.z) - z.off;
        var inDense = Math.abs(dx) < ZONE_W && Math.abs(dx) > (GAP_HALF - 40);
        if (inDense) {
          applyDamage(BASE_HITS + (gear() >= 1 ? FAST_EXTRA : 0));
        } else {
          if (window.StarfieldInFlightExtraction && typeof window.StarfieldInFlightExtraction.addSecuredCredits === 'function') {
            window.StarfieldInFlightExtraction.addSecuredCredits(180);
          }
          if (window.StarfieldExpedition && typeof window.StarfieldExpedition.recordAction === 'function') {
            window.StarfieldExpedition.recordAction('hazard_evade', { kind: 'debris_gap', stardust: 180 });
          }
          if (typeof window.toast === 'function') window.toast('✦ 极限穿缝规避 · GRAZE BONUS +180 星尘 ✦', 2.2);
        }"""

    if old_hazard_check in html:
        html = html.replace(old_hazard_check, new_hazard_check, 1)

    old_flare_escape = """        if (gear() >= 1) {
          if (typeof window.toast === 'function') window.toast('✦ 曲率甩开耀斑冲击 · 船体无损', 2);
        }"""

    new_flare_escape = """        if (gear() >= 1) {
          if (window.StarfieldInFlightExtraction && typeof window.StarfieldInFlightExtraction.addSecuredCredits === 'function') {
            window.StarfieldInFlightExtraction.addSecuredCredits(220);
          }
          if (window.StarfieldExpedition && typeof window.StarfieldExpedition.recordAction === 'function') {
            window.StarfieldExpedition.recordAction('hazard_evade', { kind: 'flare_warp', stardust: 220 });
          }
          if (typeof window.toast === 'function') window.toast('✦ 曲率甩开耀斑冲击 · 船体无损 · +220 星尘 ✦', 2.4);
        }"""

    if old_flare_escape in html:
        html = html.replace(old_flare_escape, new_flare_escape, 1)

    # 7. Upgrade Mobile Touch Tray (.sf-touch-more-tray) with Ship Upgrades & Origami Hangar buttons
    old_touch_tray_append = """    moreTray.appendChild(btnPlanet);
    moreTray.appendChild(btnSonar);
    moreTray.appendChild(btnCockpit);
    moreTray.appendChild(btnCinema);
    moreTray.appendChild(btnSettings);
    moreTray.appendChild(btnFocus);
    moreTray.appendChild(btnRotate);"""

    new_touch_tray_append = """    const btnUpgrades = createTouchButton('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><polygon points="12 2 20 6.5 20 17.5 12 22 4 17.5 4 6.5"/><path d="M12 16V8M8.5 11.5L12 8l3.5 3.5"/></svg>', '工坊', () => {
      if (window.StarfieldAppShell && window.StarfieldAppShell.openPanel) window.StarfieldAppShell.openPanel('upgrades');
      else if (window.StarfieldShipUpgrades) window.StarfieldShipUpgrades.openModal();
      moreTray.classList.remove('open');
    });
    const btnHangarTouch = createTouchButton('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><polygon points="12 2 19 9 12 22 5 9"/><line x1="5" y1="9" x2="19" y2="9"/></svg>', '折纸坞', () => {
      if (window.StarfieldAppShell && window.StarfieldAppShell.openPanel) window.StarfieldAppShell.openPanel('hangar');
      else if (typeof FleetCustomizer !== 'undefined') FleetCustomizer.open();
      moreTray.classList.remove('open');
    });
    const btnTunerTouch = createTouchButton('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"><path d="M2 12h4l3-7 6 14 3-7h4"/></svg>', '破译', () => {
      if (window.StarfieldAppShell && window.StarfieldAppShell.openPanel) window.StarfieldAppShell.openPanel('tuner');
      else if (window.AnomalyScanner && window.AnomalyScanner.openTuner) window.AnomalyScanner.openTuner();
      moreTray.classList.remove('open');
    });
    moreTray.appendChild(btnPlanet);
    moreTray.appendChild(btnUpgrades);
    moreTray.appendChild(btnHangarTouch);
    moreTray.appendChild(btnSonar);
    moreTray.appendChild(btnTunerTouch);
    moreTray.appendChild(btnCockpit);
    moreTray.appendChild(btnCinema);
    moreTray.appendChild(btnFocus);
    moreTray.appendChild(btnRotate);
    moreTray.appendChild(btnSettings);"""

    if old_touch_tray_append in html:
        html = html.replace(old_touch_tray_append, new_touch_tray_append, 1)

    # 8. Hook SFVoyage complete() and expose nextContract / triggerDirectiveAction on window.SFVoyage
    old_voyage_api = """  window.SFVoyage = {
    pool: POOL.map(function (c) { return c.id; }),
    state: function () {
      return {
        active: state.active ? state.active.def.id : null,
        left: state.active ? Math.round(state.active.left) : 0,
        streak: state.streak,
        cooldown: Math.max(0, Math.round(state.cooldown)),
        visible: hud.classList.contains('show')
      };
    },
    force: function (id) {
      var def = null;
      for (var i = 0; i < POOL.length; i++) if (POOL[i].id === id) def = POOL[i];
      if (!def) return false;
      state.flashUntil = 0;
      begin(def);
      return true;
    },
    reset: function () { state.active = null; state.cooldown = FIRST_DELAY; state.flashUntil = 0; hud.classList.remove('show'); }
  };"""

    new_voyage_api = """  window.SFVoyage = {
    pool: POOL.map(function (c) { return c.id; }),
    state: function () {
      return {
        active: state.active ? state.active.def.id : null,
        name: state.active ? state.active.def.name : null,
        hint: state.active ? state.active.def.hint : null,
        ratio: state.active ? state.active.def.ratio(state.active) : 0,
        left: state.active ? Math.round(state.active.left) : 0,
        streak: state.streak,
        cooldown: Math.max(0, Math.round(state.cooldown)),
        visible: hud.classList.contains('show')
      };
    },
    force: function (id) {
      var def = null;
      for (var i = 0; i < POOL.length; i++) if (POOL[i].id === id) def = POOL[i];
      if (!def) return false;
      state.flashUntil = 0;
      begin(def);
      return true;
    },
    next: function () {
      state.flashUntil = 0;
      var c = pick();
      begin(c);
      return c ? c.id : null;
    },
    completeNow: function () {
      if (!state.active) begin(pick());
      complete();
      return true;
    },
    reset: function () { state.active = null; state.cooldown = FIRST_DELAY; state.flashUntil = 0; hud.classList.remove('show'); }
  };"""

    if old_voyage_api in html:
        html = html.replace(old_voyage_api, new_voyage_api, 1)

    # 9. Inject the Build 200 Core Gameplay Loop & Flagship App Shell Module before </body>
    b200_module = r"""<!-- === BUILD 200 GAMEPLAY & APP SHELL OVERHAUL START === -->
<style id="sf-v200-gameplay-app-css">
  /* Hide legacy duplicate stardust row overridden by !important */
  #sf-hud-stardust {
    display: none !important;
  }

  /* Pilot Rank & Telemetry Header inside #camera-hud */
  #sf-pilot-telemetry-bar {
    margin-top: 8px;
    padding-top: 7px;
    border-top: 1px solid rgba(230, 237, 242, 0.14);
    display: flex;
    flex-direction: column;
    gap: 6px;
    pointer-events: auto;
    max-width: 270px;
    font-family: ui-monospace, "SFMono-Regular", Consolas, monospace;
  }
  .sf-pilot-rank-head {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 8px;
    font-size: 9px;
    letter-spacing: 0.14em;
    color: rgba(244, 208, 111, 0.92);
    cursor: pointer;
    user-select: none;
  }
  .sf-pilot-rank-head:hover {
    color: #fff;
  }
  .sf-pilot-xp-track {
    position: relative;
    width: 100%;
    height: 2px;
    background: rgba(230, 237, 242, 0.16);
    overflow: hidden;
  }
  .sf-pilot-xp-fill {
    position: absolute;
    inset: 0;
    transform-origin: left center;
    transform: scaleX(0.05);
    background: linear-gradient(90deg, rgba(143, 216, 192, 0.85), rgba(244, 208, 111, 0.95));
    transition: transform 0.28s ease;
  }
  .sf-pilot-pills-row {
    display: flex;
    align-items: center;
    flex-wrap: wrap;
    gap: 6px;
    margin-top: 2px;
  }
  .sf-app-status-pill {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    padding: 2px 7px;
    border-radius: 0px !important;
    background: rgba(8, 13, 22, 0.72);
    border: 1px solid rgba(230, 237, 242, 0.20);
    color: rgba(230, 237, 242, 0.90);
    font-family: ui-monospace, "SFMono-Regular", Consolas, monospace;
    font-size: 9px;
    letter-spacing: 0.10em;
    font-variant-numeric: tabular-nums;
    cursor: pointer;
    transition: border-color 0.18s ease, color 0.18s ease, background 0.18s ease;
    user-select: none;
  }
  .sf-app-status-pill:hover,
  .sf-app-status-pill:active {
    border-color: rgba(244, 208, 111, 0.65);
    color: #ffffff;
    background: rgba(230, 237, 242, 0.10);
  }
  .sf-app-status-pill.gold {
    color: rgba(244, 208, 111, 0.94);
    border-color: rgba(244, 208, 111, 0.30);
  }
  .sf-app-status-pill.cyan {
    color: rgba(143, 216, 192, 0.94);
    border-color: rgba(143, 216, 192, 0.30);
  }

  /* Interactive Expedition Directive Capsule (#sf-contract-hud upgrade) */
  #sf-contract-hud {
    pointer-events: auto !important;
    padding: 10px 14px;
    background: rgba(7, 11, 18, 0.76);
    border: 1px solid rgba(230, 237, 242, 0.18);
    border-radius: 0px !important;
    backdrop-filter: blur(14px);
    -webkit-backdrop-filter: blur(14px);
    min-width: 196px;
  }
  #sf-contract-hud .sc-bar {
    width: 100%;
    height: 2px;
  }
  #sf-contract-hud .sc-actions {
    display: flex;
    align-items: center;
    justify-content: flex-end;
    gap: 6px;
    margin-top: 8px;
    padding-top: 6px;
    border-top: 1px solid rgba(230, 237, 242, 0.12);
  }
  #sf-contract-hud .sc-act-btn {
    appearance: none;
    background: rgba(230, 237, 242, 0.05);
    border: 1px solid rgba(230, 237, 242, 0.22);
    border-radius: 0px !important;
    color: rgba(230, 237, 242, 0.88);
    font-family: ui-monospace, "SFMono-Regular", Consolas, monospace;
    font-size: 8.5px;
    letter-spacing: 0.10em;
    padding: 3px 7px;
    cursor: pointer;
    transition: border-color 0.18s ease, color 0.18s ease, background 0.18s ease;
  }
  #sf-contract-hud .sc-act-btn.primary {
    color: rgba(244, 208, 111, 0.96);
    border-color: rgba(244, 208, 111, 0.42);
  }
  #sf-contract-hud .sc-act-btn:hover,
  #sf-contract-hud .sc-act-btn:active {
    background: rgba(230, 237, 242, 0.12);
    border-color: rgba(244, 208, 111, 0.75);
    color: #ffffff;
  }

  /* Context-Aware Tactical Action Capsule (#sf-tactical-capsule) */
  #sf-tactical-capsule {
    position: fixed;
    left: 50%;
    bottom: calc(var(--pad, 40px) + 52px);
    transform: translateX(-50%);
    z-index: 815;
    display: none;
    align-items: center;
    gap: 8px;
    padding: 6px 10px;
    background: rgba(7, 11, 18, 0.78);
    border: 1px solid rgba(230, 237, 242, 0.22);
    border-radius: 0px !important;
    backdrop-filter: blur(14px);
    -webkit-backdrop-filter: blur(14px);
    pointer-events: auto;
    font-family: ui-monospace, "SFMono-Regular", Consolas, monospace;
  }
  #sf-tactical-capsule.show {
    display: inline-flex;
  }
  .sf-tac-btn {
    appearance: none;
    background: rgba(230, 237, 242, 0.04);
    border: 1px solid rgba(230, 237, 242, 0.18);
    border-radius: 0px !important;
    color: rgba(230, 237, 242, 0.88);
    font-family: ui-monospace, "SFMono-Regular", Consolas, monospace;
    font-size: 9.5px;
    letter-spacing: 0.10em;
    padding: 4px 10px;
    cursor: pointer;
    white-space: nowrap;
    transition: border-color 0.18s ease, color 0.18s ease, background 0.18s ease;
  }
  .sf-tac-btn.highlight {
    color: rgba(244, 208, 111, 0.96);
    border-color: rgba(244, 208, 111, 0.48);
  }
  .sf-tac-btn.cyan {
    color: rgba(143, 216, 192, 0.96);
    border-color: rgba(143, 216, 192, 0.44);
  }
  .sf-tac-btn:hover,
  .sf-tac-btn:active {
    background: rgba(230, 237, 242, 0.12);
    border-color: rgba(244, 208, 111, 0.82);
    color: #ffffff;
  }

  /* Desktop Dock Badge for Unopened Planet Cores */
  #planet-toggle {
    position: relative;
  }
  .sf-dock-count-tag {
    position: absolute;
    top: -4px;
    right: -4px;
    padding: 0 3px;
    min-width: 13px;
    height: 13px;
    line-height: 13px;
    font-family: ui-monospace, "SFMono-Regular", Consolas, monospace;
    font-size: 8px;
    text-align: center;
    background: rgba(12, 18, 28, 0.92);
    color: rgba(244, 208, 111, 0.96);
    border: 1px solid rgba(244, 208, 111, 0.55);
    border-radius: 0px !important;
    pointer-events: none;
  }

  body.cinema-mode #sf-tactical-capsule,
  body.cinema-mode #sf-pilot-telemetry-bar,
  body.modal-open #sf-tactical-capsule,
  body:has(#photo-ui.active) #sf-tactical-capsule,
  body:has(#codex-modal.open) #sf-tactical-capsule,
  body:has(#hangar-modal.open) #sf-tactical-capsule,
  body:has(#settings-drawer.open) #sf-tactical-capsule,
  body:has(#sf-upgrades-modal.open) #sf-tactical-capsule,
  body:has(#sf-hatch.on) #sf-tactical-capsule,
  body:has(#sf-hatch-list.on) #sf-tactical-capsule {
    display: none !important;
  }

  @media (max-width: 900px), (pointer: coarse) {
    #sf-pilot-telemetry-bar {
      max-width: 215px;
      gap: 4px;
    }
    .sf-pilot-rank-head {
      font-size: 8px;
    }
    .sf-app-status-pill {
      font-size: 8px;
      padding: 2px 5px;
    }
    #sf-contract-hud {
      max-width: min(210px, 50vw) !important;
      padding: 7px 10px;
    }
    #sf-contract-hud .sc-actions {
      gap: 4px;
      flex-wrap: wrap;
    }
    #sf-contract-hud .sc-act-btn {
      font-size: 7.5px;
      padding: 2px 5px;
    }
    #comms-hud {
      top: 248px !important;
    }
    #sf-tactical-capsule {
      bottom: calc(max(env(safe-area-inset-bottom, 0px), 14px) + 112px) !important;
      padding: 4px 7px;
      gap: 5px;
      max-width: 92vw;
      overflow-x: auto;
    }
    .sf-tac-btn {
      font-size: 8.5px;
      padding: 3px 7px;
    }
  }
</style>

<script id="sf-v200-gameplay-app-js">
(function () {
  'use strict';
  if (window.StarfieldExpedition && window.StarfieldAppShell) return;

  var STORAGE_KEY = 'sf_pilot_progression_v1';
  var RANKS = [
    { idx: 1, code: 'RANK 01', title: '见习引航员', en: 'CADET NAVIGATOR', minXp: 0, bonus: 1.00 },
    { idx: 2, code: 'RANK 02', title: '巡天测绘师', en: 'DEEP SURVEYOR', minXp: 200, bonus: 1.10 },
    { idx: 3, code: 'RANK 03', title: '轨道弹弓手', en: 'SLINGSHOT ACE', minXp: 500, bonus: 1.20 },
    { idx: 4, code: 'RANK 04', title: '谐波破译官', en: 'RELIC DECIPHERER', minXp: 900, bonus: 1.32 },
    { idx: 5, code: 'RANK 05', title: '折纸舰长', en: 'ORIGAMI CAPTAIN', minXp: 1500, bonus: 1.45 },
    { idx: 6, code: 'RANK 06', title: '奇点领航官', en: 'HORIZON PATHFINDER', minXp: 2300, bonus: 1.60 },
    { idx: 7, code: 'RANK 07', title: '星河造物主', en: 'CELESTIAL ARCHITECT', minXp: 3400, bonus: 1.80 },
    { idx: 8, code: 'RANK 08', title: '深空折纸宗师', en: 'GRAND STARFARER', minXp: 5000, bonus: 2.00 }
  ];

  /* =========================================================================
   * 1. FLAGSHIP APP SHELL, NATIVE BRIDGE & MODAL MUTEX HUB
   * ========================================================================= */
  var AppShell = {
    lifecycleState: 'active',

    haptic: function (style) {
      var kind = style || 'light';
      try {
        if (window.StarfieldNative && typeof window.StarfieldNative.triggerHaptic === 'function') {
          window.StarfieldNative.triggerHaptic(kind);
          return true;
        }
        if (window.StarfieldNativeHaptics && typeof window.StarfieldNativeHaptics.trigger === 'function') {
          window.StarfieldNativeHaptics.trigger(kind);
          return true;
        }
      } catch (e) {}
      return false;
    },

    closeAllPanels: function (except) {
      try {
        if (except !== 'upgrades' && window.StarfieldShipUpgrades && window.StarfieldShipUpgrades.isOpen) {
          window.StarfieldShipUpgrades.closeModal();
        }
        if (except !== 'codex') {
          var cm = document.getElementById('codex-modal');
          if (cm && cm.classList.contains('open')) {
            if (typeof Codex !== 'undefined' && Codex.close) Codex.close();
            else cm.classList.remove('open');
          }
        }
        if (except !== 'hangar') {
          if (typeof FleetCustomizer !== 'undefined' && FleetCustomizer.isOpen && FleetCustomizer.close) {
            FleetCustomizer.close();
          }
          var hm = document.getElementById('hangar-modal');
          if (hm && hm.classList.contains('open')) hm.classList.remove('open');
        }
        if (except !== 'settings') {
          var sd = document.getElementById('settings-drawer');
          if (sd && sd.classList.contains('open')) {
            if (typeof GameSettings !== 'undefined' && GameSettings.close) GameSettings.close();
            else sd.classList.remove('open');
          }
        }
        if (except !== 'planetarium') {
          var hl = document.getElementById('sf-hatch-list');
          if (hl && hl.classList.contains('on')) hl.classList.remove('on');
        }
        if (except !== 'hatch') {
          var hc = document.getElementById('sf-hatch');
          if (hc && (hc.classList.contains('on') || hc.classList.contains('active'))) {
            if (window.StarfieldHatch && typeof window.StarfieldHatch.hide === 'function') window.StarfieldHatch.hide();
            else { hc.classList.remove('on'); hc.classList.remove('active'); }
          }
        }
        if (except !== 'focus' && window.StarfieldFocusEngine && window.StarfieldFocusEngine.isDashboardOpen) {
          window.StarfieldFocusEngine.closeDashboard();
        }
        if (except !== 'photo' && typeof PhotoStudio !== 'undefined' && PhotoStudio.active && PhotoStudio.close) {
          PhotoStudio.close();
        }
        if (except !== 'tuner' && window.AnomalyScanner && window.AnomalyScanner.getState && window.AnomalyScanner.getState().tunerOpen) {
          window.AnomalyScanner.closeTuner();
        }
      } catch (e) {}
    },

    openPanel: function (name) {
      this.haptic('light');
      this.closeAllPanels(name);
      try {
        if (name === 'upgrades' && window.StarfieldShipUpgrades) {
          window.StarfieldShipUpgrades.openModal();
        } else if (name === 'planetarium' && window.StarfieldHatch && window.StarfieldHatch.openList) {
          window.StarfieldHatch.openList();
        } else if (name === 'hatch' && window.StarfieldHatch) {
          var cores = (window.StarfieldHatch.getUnopenedCores && window.StarfieldHatch.getUnopenedCores()) || 0;
          if (cores > 0 && window.StarfieldHatch.openNextCore) {
            window.StarfieldHatch.openNextCore();
          } else if (window.StarfieldHatch.openList) {
            window.StarfieldHatch.openList();
          }
        } else if (name === 'codex') {
          if (typeof Codex !== 'undefined' && Codex.open) Codex.open();
          else {
            var cm = document.getElementById('codex-modal');
            if (cm) cm.classList.add('open');
          }
        } else if (name === 'hangar' && typeof FleetCustomizer !== 'undefined') {
          FleetCustomizer.open();
        } else if (name === 'focus' && window.StarfieldFocusEngine) {
          window.StarfieldFocusEngine.openDashboard();
        } else if (name === 'settings' && typeof GameSettings !== 'undefined') {
          GameSettings.open();
        } else if (name === 'tuner' && window.AnomalyScanner && window.AnomalyScanner.openTuner) {
          window.AnomalyScanner.openTuner();
        }
      } catch (e) {}
    },

    getNativeDeviceInfo: function () {
      try {
        if (window.StarfieldNative && typeof window.StarfieldNative.getDeviceInfo === 'function') {
          var raw = window.StarfieldNative.getDeviceInfo();
          return typeof raw === 'string' ? JSON.parse(raw) : raw;
        }
      } catch (e) {}
      return { platform: 'web', version: '2.0.0.0', build: 200 };
    }
  };

  window.StarfieldAppShell = AppShell;

  // Bind Android Native Lifecycle callback
  window.onStarfieldAppLifecycle = function (state) {
    AppShell.lifecycleState = state;
    try {
      if (state === 'pause') {
        if (window.SFAmbience && window.SFAmbience.stop) window.SFAmbience.stop();
        if (window.StarfieldAudio && window.StarfieldAudio.getContext) {
          var actx = window.StarfieldAudio.getContext();
          if (actx && actx.state === 'running') actx.suspend().catch(function () {});
        }
      } else if (state === 'resume') {
        if (window.StarfieldAudio && window.StarfieldAudio.resume) {
          window.StarfieldAudio.resume();
        }
        if (window.StarfieldExpedition) window.StarfieldExpedition.refreshHUD(true);
      }
    } catch (e) {}
  };

  /* =========================================================================
   * 2. STARFARER PROGRESSION & ACTIVE EXPEDITION LOOP
   * ========================================================================= */
  function loadState() {
    var def = {
      xp: 0,
      rankIdx: 1,
      totalScans: 0,
      totalSlings: 0,
      totalRelics: 0,
      totalEvades: 0,
      totalContracts: 0,
      totalUpgrades: 0,
      totalHatched: 0
    };
    try {
      var raw = localStorage.getItem(STORAGE_KEY);
      if (raw) {
        var parsed = JSON.parse(raw);
        for (var k in def) {
          if (typeof parsed[k] === 'number' && isFinite(parsed[k]) && parsed[k] >= 0) {
            def[k] = Math.floor(parsed[k]);
          }
        }
      }
    } catch (e) {}
    return def;
  }

  var prog = loadState();
  var comboCount = 0;
  var comboMultiplier = 1.0;
  var lastActionTime = -1e9;

  function computeRank(xp) {
    var current = RANKS[0];
    for (var i = 0; i < RANKS.length; i++) {
      if (xp >= RANKS[i].minXp) current = RANKS[i];
    }
    return current;
  }

  function nextRankFor(xp) {
    for (var i = 0; i < RANKS.length; i++) {
      if (RANKS[i].minXp > xp) return RANKS[i];
    }
    return null;
  }

  function saveState() {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(prog));
    } catch (e) {}
  }

  // Dirty-check caches for HUD nodes
  var _barEl = null, _rankTitleEl = null, _rankMetaEl = null, _xpFillEl = null;
  var _stardustPillEl = null, _coresPillEl = null, _dockCoreTagEl = null;
  var _tacEl = null, _tacScanBtn = null, _tacProbeBtn = null, _tacRelicBtn = null;
  var _lastRankStr = '', _lastMetaStr = '', _lastXpScale = '', _lastDustStr = '', _lastCoreStr = '';
  var _lastTacVis = false, _lastTacScanStr = '', _lastTacScanHi = false, _lastTacProbeHi = false, _lastTacRelicHi = false;

  function ensureHUD() {
    var camHud = document.getElementById('camera-hud');
    if (camHud && !_barEl) {
      _barEl = document.getElementById('sf-pilot-telemetry-bar');
      if (!_barEl) {
        _barEl = document.createElement('div');
        _barEl.id = 'sf-pilot-telemetry-bar';
        _barEl.innerHTML =
          '<div class="sf-pilot-rank-head" id="sf-pilot-rank-pill" title="星航段位与远征倍率 · 点击执行当前远征指令">' +
            '<span id="sf-pilot-rank-title">RANK 01 · 见习引航员</span>' +
            '<span id="sf-pilot-rank-meta">0 XP</span>' +
          '</div>' +
          '<div class="sf-pilot-xp-track"><i class="sf-pilot-xp-fill" id="sf-pilot-xp-fill"></i></div>' +
          '<div class="sf-pilot-pills-row">' +
            '<button type="button" class="sf-app-status-pill gold" id="sf-pilot-dust-btn" title="星尘储备 · 点击打开舰载装备升级工坊 [U]">✦ 0 ST · 工坊 ↗</button>' +
            '<button type="button" class="sf-app-status-pill cyan" id="sf-pilot-core-btn" title="未开采星核 · 点击开启星核或进入天象馆 [L]">⊕ 0 CORE · 星核 ↗</button>' +
            '<button type="button" class="sf-app-status-pill" id="sf-pilot-codex-btn" title="星图手札 · 天体与奇观探索图鉴 [J]">✦ 图鉴 ↗</button>' +
          '</div>';
        camHud.appendChild(_barEl);

        _rankTitleEl = document.getElementById('sf-pilot-rank-title');
        _rankMetaEl = document.getElementById('sf-pilot-rank-meta');
        _xpFillEl = document.getElementById('sf-pilot-xp-fill');
        _stardustPillEl = document.getElementById('sf-pilot-dust-btn');
        _coresPillEl = document.getElementById('sf-pilot-core-btn');
        _dockCoreTagEl = document.getElementById('sf-dock-core-count');

        // Hide legacy duplicate #sf-hud-stardust pill if present so #camera-hud stays clean
        var oldDust = document.getElementById('sf-hud-stardust');
        if (oldDust) oldDust.style.display = 'none';

        document.getElementById('sf-pilot-rank-pill').addEventListener('click', function (e) {
          e.stopPropagation();
          Expedition.executeActiveDirective();
        });
        _stardustPillEl.addEventListener('click', function (e) {
          e.stopPropagation();
          AppShell.openPanel('upgrades');
        });
        _coresPillEl.addEventListener('click', function (e) {
          e.stopPropagation();
          AppShell.openPanel('hatch');
        });
        document.getElementById('sf-pilot-codex-btn').addEventListener('click', function (e) {
          e.stopPropagation();
          AppShell.openPanel('codex');
        });
      }
    }

    // Upgrade #sf-contract-hud with interactive action bar
    var contractHud = document.getElementById('sf-contract-hud');
    if (contractHud && !contractHud._v200Upgraded) {
      contractHud._v200Upgraded = true;
      var actRow = document.createElement('div');
      actRow.className = 'sc-actions';
      actRow.innerHTML =
        '<button type="button" class="sc-act-btn primary" id="sf-contract-act-btn" title="一键响应并推进当前远征指令">✦ 执行指令</button>' +
        '<button type="button" class="sc-act-btn" id="sf-contract-next-btn" title="切换下一项远征指令">切换 ↗</button>' +
        '<button type="button" class="sc-act-btn" id="sf-contract-upg-btn" title="打开舰载装备工坊">工坊 ↗</button>' +
        '<button type="button" class="sc-act-btn" id="sf-contract-core-btn" title="打开星核孵化与天象馆">星核 ↗</button>';
      contractHud.appendChild(actRow);

      document.getElementById('sf-contract-act-btn').addEventListener('click', function (e) {
        e.stopPropagation();
        Expedition.executeActiveDirective();
      });
      document.getElementById('sf-contract-next-btn').addEventListener('click', function (e) {
        e.stopPropagation();
        AppShell.haptic('tick');
        if (window.SFVoyage && typeof window.SFVoyage.next === 'function') {
          window.SFVoyage.next();
        }
      });
      document.getElementById('sf-contract-upg-btn').addEventListener('click', function (e) {
        e.stopPropagation();
        AppShell.openPanel('upgrades');
      });
      document.getElementById('sf-contract-core-btn').addEventListener('click', function (e) {
        e.stopPropagation();
        AppShell.openPanel('hatch');
      });
    }

    // Create Context-Aware Tactical Action Capsule (#sf-tactical-capsule)
    if (!_tacEl) {
      _tacEl = document.getElementById('sf-tactical-capsule');
      if (!_tacEl) {
        _tacEl = document.createElement('div');
        _tacEl.id = 'sf-tactical-capsule';
        _tacEl.setAttribute('aria-label', '星航战术快捷动作舱');
        _tacEl.innerHTML =
          '<button type="button" class="sf-tac-btn" id="sf-tac-scan-btn" title="主动巡天声呐测绘 [F]">✦ 声呐测绘 [F]</button>' +
          '<button type="button" class="sf-tac-btn" id="sf-tac-probe-btn" title="发射引力弹弓探测鸟 [Q]">⊕ 引力探针 [Q]</button>' +
          '<button type="button" class="sf-tac-btn" id="sf-tac-relic-btn" title="远古遗迹信号谐波破译 [E]">✦ 谐波破译 [E]</button>';
        document.body.appendChild(_tacEl);

        _tacScanBtn = document.getElementById('sf-tac-scan-btn');
        _tacProbeBtn = document.getElementById('sf-tac-probe-btn');
        _tacRelicBtn = document.getElementById('sf-tac-relic-btn');

        _tacScanBtn.addEventListener('click', function (e) {
          e.stopPropagation();
          AppShell.haptic('medium');
          if (window.StarfieldSonar && typeof window.StarfieldSonar.triggerScan === 'function') {
            window.StarfieldSonar.triggerScan(true);
          }
        });
        _tacProbeBtn.addEventListener('click', function (e) {
          e.stopPropagation();
          AppShell.haptic('medium');
          if (window.StarfieldOrbitalMechanics && typeof window.StarfieldOrbitalMechanics.launchProbe === 'function') {
            window.StarfieldOrbitalMechanics.launchProbe();
          }
        });
        _tacRelicBtn.addEventListener('click', function (e) {
          e.stopPropagation();
          AppShell.haptic('medium');
          if (window.StarfieldInFlightExtraction && window.StarfieldInFlightExtraction.salvageTarget && typeof window.StarfieldInFlightExtraction.fastLoot === 'function') {
            window.StarfieldInFlightExtraction.fastLoot();
          } else {
            AppShell.openPanel('tuner');
          }
        });
      }
    }

    // Bind new desktop Command Dock buttons
    var pBtn = document.getElementById('planet-toggle');
    if (pBtn && !pBtn._v200Bound) {
      pBtn._v200Bound = true;
      pBtn.addEventListener('click', function () {
        AppShell.openPanel('hatch');
      });
    }
    var uBtn = document.getElementById('upgrades-toggle');
    if (uBtn && !uBtn._v200Bound) {
      uBtn._v200Bound = true;
      uBtn.addEventListener('click', function () {
        AppShell.openPanel('upgrades');
      });
    }
    var fBtn = document.getElementById('focus-toggle');
    if (fBtn && !fBtn._v200Bound) {
      fBtn._v200Bound = true;
      fBtn.addEventListener('click', function () {
        AppShell.openPanel('focus');
      });
    }
  }

  var ACTION_XP = {
    sonar_scan: 45,
    slingshot_assist: 60,
    probe_shockwave: 65,
    relic_decipher: 95,
    hazard_evade: 50,
    contract_complete: 110,
    core_hatch: 70,
    ship_upgrade: 65
  };

  var Expedition = {
    ranks: RANKS,

    getState: function () {
      var r = computeRank(prog.xp);
      var nxt = nextRankFor(prog.xp);
      return {
        xp: prog.xp,
        rankIdx: r.idx,
        rankCode: r.code,
        rankTitle: r.title,
        rankEn: r.en,
        bonusMultiplier: r.bonus,
        combo: comboCount,
        comboMultiplier: comboMultiplier,
        nextRankXp: nxt ? nxt.minXp : r.minXp,
        stats: Object.assign({}, prog)
      };
    },

    recordAction: function (type, meta) {
      var now = performance.now();
      if (now - lastActionTime <= 28000) {
        comboCount = Math.min(12, comboCount + 1);
      } else {
        comboCount = 1;
      }
      lastActionTime = now;
      comboMultiplier = Math.round((1.0 + Math.min(2.0, (comboCount - 1) * 0.20)) * 100) / 100;

      var baseXp = ACTION_XP[type] || 35;
      var earnedXp = Math.round(baseXp * comboMultiplier);
      var prevRank = computeRank(prog.xp);
      prog.xp += earnedXp;

      if (type === 'sonar_scan') prog.totalScans++;
      else if (type === 'slingshot_assist' || type === 'probe_shockwave') prog.totalSlings++;
      else if (type === 'relic_decipher') prog.totalRelics++;
      else if (type === 'hazard_evade') prog.totalEvades++;
      else if (type === 'contract_complete') prog.totalContracts++;
      else if (type === 'ship_upgrade') prog.totalUpgrades++;
      else if (type === 'core_hatch') prog.totalHatched++;

      var newRank = computeRank(prog.xp);
      prog.rankIdx = newRank.idx;
      saveState();

      AppShell.haptic(newRank.idx > prevRank.idx ? 'success' : 'light');

      if (newRank.idx > prevRank.idx) {
        if (window.StarfieldHatch && typeof window.StarfieldHatch.addCores === 'function') {
          window.StarfieldHatch.addCores(1);
        }
        if (window.StarfieldInFlightExtraction && typeof window.StarfieldInFlightExtraction.addSecuredCredits === 'function') {
          window.StarfieldInFlightExtraction.addSecuredCredits(300 * newRank.idx);
        }
        if (typeof window.toast === 'function') {
          window.toast('✦ 星航段位晋升：' + newRank.code + ' · ' + newRank.title + ' · 奖励 +1 星核 & +' + (300 * newRank.idx) + ' 星尘 ✦', 4.2);
        }
      }

      this.refreshHUD(true);
      return { earnedXp: earnedXp, totalXp: prog.xp, rank: newRank, combo: comboCount, comboMultiplier: comboMultiplier };
    },

    executeActiveDirective: function () {
      AppShell.haptic('medium');
      var vState = (window.SFVoyage && typeof window.SFVoyage.state === 'function') ? window.SFVoyage.state() : null;
      var activeId = vState && vState.active;
      if (!activeId && window.SFVoyage && typeof window.SFVoyage.next === 'function') {
        activeId = window.SFVoyage.next();
      }

      if (activeId === 'warp') {
        if (window.WarpDrive && typeof window.WarpDrive.cycle === 'function') window.WarpDrive.cycle();
        else {
          var wb = document.getElementById('warp-toggle');
          if (wb) wb.click();
        }
      } else if (activeId === 'sling' || activeId === 'shockwave') {
        if (window.StarfieldOrbitalMechanics && typeof window.StarfieldOrbitalMechanics.launchProbe === 'function') {
          window.StarfieldOrbitalMechanics.launchProbe();
        }
        if (window.SFProbe && window.SFProbe.surges !== undefined) {
          window.SFProbe.surges++;
        }
        this.recordAction('probe_shockwave', { stardust: 240 });
      } else if (activeId === 'salvage' || activeId === 'pirate') {
        if (window.StarfieldInFlightExtraction && window.StarfieldInFlightExtraction.salvageTarget && typeof window.StarfieldInFlightExtraction.fastLoot === 'function') {
          window.StarfieldInFlightExtraction.fastLoot();
        } else if (window.StarfieldSonar && typeof window.StarfieldSonar.triggerScan === 'function') {
          window.StarfieldSonar.triggerScan(true);
        }
      } else if (activeId === 'approach' || activeId === 'cloud_pierce') {
        var dBtn = document.getElementById('sf-descent-btn');
        if (dBtn && dBtn.classList.contains('show')) {
          dBtn.click();
        } else if (window.StarfieldSonar && typeof window.StarfieldSonar.triggerScan === 'function') {
          window.StarfieldSonar.triggerScan(true);
        }
      } else {
        if (window.StarfieldSonar && typeof window.StarfieldSonar.triggerScan === 'function') {
          window.StarfieldSonar.triggerScan(true);
        }
      }
      this.refreshHUD(true);
    },

    refreshHUD: function (force) {
      ensureHUD();
      var now = performance.now();
      if (comboCount > 0 && now - lastActionTime > 28000) {
        comboCount = 0;
        comboMultiplier = 1.0;
      }

      var r = computeRank(prog.xp);
      var nxt = nextRankFor(prog.xp);
      var prevMin = r.minXp;
      var span = nxt ? Math.max(1, nxt.minXp - prevMin) : 1000;
      var ratio = nxt ? Math.min(1, Math.max(0.04, (prog.xp - prevMin) / span)) : 1;

      var rankStr = r.code + ' · ' + r.title;
      if (_rankTitleEl && (force || rankStr !== _lastRankStr)) {
        _lastRankStr = rankStr;
        _rankTitleEl.textContent = rankStr;
      }

      var metaStr = prog.xp + ' XP' + (comboCount > 1 ? ' · ×' + comboMultiplier.toFixed(1) : '');
      if (_rankMetaEl && (force || metaStr !== _lastMetaStr)) {
        _lastMetaStr = metaStr;
        _rankMetaEl.textContent = metaStr;
      }

      var xpScale = 'scaleX(' + ratio.toFixed(3) + ')';
      if (_xpFillEl && (force || xpScale !== _lastXpScale)) {
        _lastXpScale = xpScale;
        _xpFillEl.style.transform = xpScale;
      }

      var dust = (window.StarfieldInFlightExtraction && typeof window.StarfieldInFlightExtraction.securedCredits === 'number')
        ? window.StarfieldInFlightExtraction.securedCredits : 0;
      var dustStr = '✦ ' + dust.toLocaleString() + ' ST · 工坊 ↗';
      if (_stardustPillEl && (force || dustStr !== _lastDustStr)) {
        _lastDustStr = dustStr;
        _stardustPillEl.textContent = dustStr;
      }

      var cores = (window.StarfieldHatch && typeof window.StarfieldHatch.getUnopenedCores === 'function')
        ? window.StarfieldHatch.getUnopenedCores() : 0;
      var coreStr = '⊕ ' + cores + ' CORE · 星核 ↗';
      if (_coresPillEl && (force || coreStr !== _lastCoreStr)) {
        _lastCoreStr = coreStr;
        _coresPillEl.textContent = coreStr;
        if (_dockCoreTagEl) {
          if (cores > 0) {
            _dockCoreTagEl.style.display = 'inline-block';
            _dockCoreTagEl.textContent = cores > 99 ? '99+' : String(cores);
          } else {
            _dockCoreTagEl.style.display = 'none';
          }
        }
      }

      // Context-Aware Tactical Action Capsule update
      var started = false;
      var paused = false;
      try {
        var st = window.Starfield && window.Starfield.getState ? window.Starfield.getState() : null;
        started = !!(st && st.started);
        paused = !!(st && st.paused);
      } catch (e) {}
      var isCruise = (typeof window.currentMode === 'undefined' || window.currentMode === 'cruise');
      var shouldShowTac = !!(started && !paused && isCruise && !document.hidden);

      if (_tacEl && (force || shouldShowTac !== _lastTacVis)) {
        _lastTacVis = shouldShowTac;
        _tacEl.classList.toggle('show', shouldShowTac);
      }

      if (shouldShowTac && _tacScanBtn) {
        var sonarTarget = window.StarfieldSonar && window.StarfieldSonar.currentTarget;
        var scanLabel = '✦ 声呐测绘 [F]';
        var hasSonarHi = false;
        if (sonarTarget) {
          var tName = sonarTarget.name || (sonarTarget.w && sonarTarget.w.name) || '深空天体';
          scanLabel = '✦ 测绘: ' + tName.slice(0, 6) + ' [F]';
          hasSonarHi = true;
        }
        if (scanLabel !== _lastTacScanStr) {
          _lastTacScanStr = scanLabel;
          _tacScanBtn.textContent = scanLabel;
        }
        if (hasSonarHi !== _lastTacScanHi) {
          _lastTacScanHi = hasSonarHi;
          _tacScanBtn.classList.toggle('highlight', hasSonarHi);
        }

        var hasGravPlanet = !!(window.StarfieldOrbitalMechanics && window.StarfieldOrbitalMechanics.activePlanet);
        if (hasGravPlanet !== _lastTacProbeHi && _tacProbeBtn) {
          _lastTacProbeHi = hasGravPlanet;
          _tacProbeBtn.classList.toggle('cyan', hasGravPlanet);
        }

        var hasRelic = false;
        try {
          hasRelic = !!(
            (window.StarfieldInFlightExtraction && window.StarfieldInFlightExtraction.salvageTarget) ||
            (window.AnomalyScanner && window.AnomalyScanner.getCandidates && window.AnomalyScanner.getCandidates().length > 0)
          );
        } catch (e) {}
        if (hasRelic !== _lastTacRelicHi && _tacRelicBtn) {
          _lastTacRelicHi = hasRelic;
          _tacRelicBtn.classList.toggle('highlight', hasRelic);
        }
      }
    }
  };

  window.StarfieldExpedition = Expedition;

  // Hook Ship Upgrades & Core Hatchery for automatic Rank XP & HUD refresh
  function wrapLifecycleHooks() {
    ensureHUD();
    if (window.StarfieldShipUpgrades && !window.StarfieldShipUpgrades._v200Wrapped) {
      window.StarfieldShipUpgrades._v200Wrapped = true;
      var origUpgrade = window.StarfieldShipUpgrades.upgrade;
      if (typeof origUpgrade === 'function') {
        window.StarfieldShipUpgrades.upgrade = function (key) {
          var beforeLvl = this.levels && this.levels[key];
          var res = origUpgrade.apply(this, arguments);
          var afterLvl = this.levels && this.levels[key];
          if (afterLvl > beforeLvl) {
            Expedition.recordAction('ship_upgrade', { key: key, level: afterLvl });
          }
          Expedition.refreshHUD(true);
          return res;
        };
      }
    }
    if (window.StarfieldHatch && !window.StarfieldHatch._v200Wrapped) {
      window.StarfieldHatch._v200Wrapped = true;
      var origAddCores = window.StarfieldHatch.addCores;
      if (typeof origAddCores === 'function') {
        window.StarfieldHatch.addCores = function (n) {
          var res = origAddCores.apply(this, arguments);
          if (n < 0) {
            Expedition.recordAction('core_hatch', { count: Math.abs(n) });
          }
          Expedition.refreshHUD(true);
          return res;
        };
      }
    }
    if (window.StarfieldInFlightExtraction && !window.StarfieldInFlightExtraction._v200Wrapped) {
      window.StarfieldInFlightExtraction._v200Wrapped = true;
      var origSaveCredits = window.StarfieldInFlightExtraction.saveSecuredCredits;
      if (typeof origSaveCredits === 'function') {
        window.StarfieldInFlightExtraction.saveSecuredCredits = function () {
          var res = origSaveCredits.apply(this, arguments);
          var oldDust = document.getElementById('sf-hud-stardust');
          if (oldDust) oldDust.style.display = 'none';
          Expedition.refreshHUD(false);
          return res;
        };
      }
    }
    Expedition.refreshHUD(true);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', wrapLifecycleHooks);
  } else {
    wrapLifecycleHooks();
  }

  // Low-frequency 5Hz telemetry & tactical capsule sync (0 hot-loop frame overhead)
  setInterval(function () {
    if (document.hidden) return;
    Expedition.refreshHUD(false);
  }, 220);
})();
</script>
<!-- === BUILD 200 GAMEPLAY & APP SHELL OVERHAUL END === -->
</body>"""

    assert '</body>' in html, 'Could not find </body> tag in starfield.html'
    html = html.replace('</body>', b200_module, 1)
    return html


def update_version_and_sw():
    # Update version.json
    meta = json.loads(VER_PATH.read_text(encoding='utf-8'))
    meta['version'] = '2.0.0.0'
    meta['build'] = 200
    meta['updated_at'] = '2026-11-22T13:30:00+08:00'
    meta['timestamp'] = '2026-11-22T05:30:00Z'
    meta['title'] = (
        'Starfield v2.0.0.0 (Build 200): 旗舰零卡顿帧率平滑引擎、深空全息仪器美学系统、'
        '星航段位与远征指令链闭环玩法、以及原生 120Hz App 指挥中枢'
    )
    meta['description'] = (
        'Build 200 (v2.0.0.0): Zero-Jank Frame Pacing, Deep-Space Editorial & Holographic Instrument Aesthetics, '
        'Starfarer Progression & Active Expedition Loop, and Flagship 120Hz Native App Command Dock'
    )
    meta['changelog'] = (
        '1. 零卡顿帧步进与 DOM 脏检查引擎 (Zero-Jank Frame Pacing)：消除主循环内燃料条、战术货舱、停靠提示、根级 CSS 变量的每帧 DOM 读写与强制同步重排，引入 EMA 帧间隔平滑与折纸尾迹批量多段绘制；\n'
        '2. 深空全息仪器与人文社论美学 (Deep-Space Editorial & Holographic Instrument HUD)：统一全局 1px 发丝线、0px 精密直角、tabular-nums 等宽遥测与折纸舰队金箔脊线反差；\n'
        '3. 星航段位与远征指令链核心玩法闭环 (Starfarer Progression & Active Expedition Loop)：新增 8 阶星航段位系统、情境感知主动战术动作舱 (#sf-tactical-capsule) 与可交互远征指令舱 (#sf-contract-hud)，打通巡天声呐、行星引力弹弓、探测鸟激波、远古遗迹示波器破译、碎片带极限规避、星核孵化与装备升级工坊的全链路奖励正反馈；\n'
        '4. 旗舰级 App 指挥坞与原生 120Hz 桥接 (Flagship App Shell & Native Bridge)：桌面与移动端统一指挥中枢一键直达天象馆、装备工坊、专注远征与星图手札，集成 Android 120Hz 高刷锁帧、沉浸式全面屏、原生触觉反馈 (StarfieldNative.triggerHaptic) 与生命周期功耗协同。'
    )
    VER_PATH.write_text(json.dumps(meta, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

    # Update service-worker.js
    sw_text = SW_PATH.read_text(encoding='utf-8')
    sw_text, n_sw = re.subn(
        r"CACHE_VERSION\s*=\s*'v[0-9.]+-b\d+'",
        "CACHE_VERSION = 'v2.0.0.0-b200'",
        sw_text,
        count=1,
    )
    assert n_sw == 1, f'Expected 1 CACHE_VERSION replacement in service-worker.js, got {n_sw}'
    SW_PATH.write_text(sw_text, encoding='utf-8')


def mirror_assets():
    ASSETS_DIR.mkdir(parents=True, exist_ok=True)
    for src in (HTML_PATH, SW_PATH, VER_PATH, STUDIO_PATH):
        if src.exists():
            dst = ASSETS_DIR / src.name
            shutil.copyfile(src, dst)
            print(f'  Mirrored {src.name} -> {dst.relative_to(BASE)} ({src.stat().st_size:,} bytes)')


def main():
    print('== Applying Build 200 (v2.0.0.0) Gameplay & App Shell Patch ==')
    raw_html = HTML_PATH.read_text(encoding='utf-8')
    patched_html = patch_starfield_html(raw_html)
    HTML_PATH.write_text(patched_html, encoding='utf-8')
    print(f'  Patched starfield.html ({len(patched_html):,} chars)')

    update_version_and_sw()
    print('  Updated version.json & service-worker.js to v2.0.0.0 (Build 200)')

    mirror_assets()
    print('== Build 200 Patch & Asset Mirror Complete ==')


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    main()
