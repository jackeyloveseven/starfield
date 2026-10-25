import os
import sys

def apply_flat_mobile_ui():
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
    # 1. Update Focus HUD & Modal CSS (Flat Sci-Fi Aesthetic)
    # -------------------------------------------------------------
    old_focus_css = """.sf-focus-ticker {
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
}"""

    new_focus_css = """.sf-focus-ticker {
  position: fixed;
  top: 16px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 150;
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 16px;
  border-radius: 20px;
  background: rgba(11, 17, 24, 0.88);
  border: 1px solid rgba(255, 215, 0, 0.4);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.5), 0 0 16px rgba(255, 215, 0, 0.15);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  cursor: pointer;
  color: #fff3a8;
  font-family: "SFMono-Regular", Consolas, monospace;
  font-size: 11px;
  letter-spacing: 0.08em;
  user-select: none;
  -webkit-user-select: none;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}
.sf-focus-ticker:active {
  transform: translateX(-50%) scale(0.96);
}
.sf-focus-ticker-tag {
  font-size: 9px;
  padding: 2px 6px;
  border-radius: 4px;
  background: rgba(255, 215, 0, 0.15);
  color: #ffd700;
  font-weight: 600;
  letter-spacing: 0.1em;
}
.sf-focus-ticker-time {
  font-size: 13px;
  font-weight: 600;
  color: #ffffff;
  font-family: "SFMono-Regular", Consolas, monospace;
}
.sf-focus-ticker-sub {
  font-size: 9px;
  opacity: 0.65;
  letter-spacing: 0.06em;
}
.sf-focus-pulse-dot {
  width: 7px;
  height: 7px;
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
  border-radius: 16px;
  background: rgba(14, 22, 32, 0.96);
  border: 1px solid rgba(230, 237, 242, 0.18);
  box-shadow: 0 16px 48px rgba(0, 0, 0, 0.65), inset 0 0 24px rgba(255, 215, 0, 0.03);
  padding: 28px 24px;
  color: #e6edf2;
  font-family: inherit;
  display: flex;
  flex-direction: column;
  gap: 16px;
  box-sizing: border-box;
}
.sf-focus-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  align-self: flex-start;
  padding: 3px 10px;
  border-radius: 6px;
  background: rgba(255, 215, 0, 0.1);
  border: 1px solid rgba(255, 215, 0, 0.35);
  color: #ffd700;
  font-size: 10px;
  font-family: "SFMono-Regular", Consolas, monospace;
  letter-spacing: 0.12em;
  text-transform: uppercase;
}
.sf-focus-badge.fail {
  background: rgba(244, 63, 94, 0.1);
  border-color: rgba(244, 63, 94, 0.45);
  color: #fb7185;
}
.sf-focus-alert-text {
  display: block;
  margin-top: 8px;
  padding: 8px 12px;
  border-radius: 8px;
  background: rgba(245, 158, 11, 0.1);
  border-left: 3px solid #f59e0b;
  color: #fbbf24;
  font-size: 12px;
  line-height: 1.6;
}
.sf-reward-dot {
  display: inline-block;
  width: 5px;
  height: 5px;
  border-radius: 50%;
  background: #ffd700;
  margin-right: 8px;
  vertical-align: middle;
}"""
    rep(old_focus_css, new_focus_css, "Flat Sci-Fi Focus HUD & Modal CSS")

    # -------------------------------------------------------------
    # 2. Update Touch Controls CSS (Flat Squircle & Vector Icons)
    # -------------------------------------------------------------
    old_touch_css = """      .sf-touch-btn {
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
      }"""

    new_touch_css = """      .sf-touch-btn {
        width: 46px;
        height: 46px;
        border-radius: 12px;
        background: rgba(14, 22, 32, 0.72);
        border: 1px solid rgba(230, 237, 242, 0.16);
        color: #e6edf2;
        font-family: inherit;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        gap: 2px;
        backdrop-filter: blur(14px);
        -webkit-backdrop-filter: blur(14px);
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.4);
        cursor: pointer;
        padding: 0;
        outline: none;
        transition: transform 0.12s ease, background 0.12s ease, border-color 0.12s ease, color 0.12s ease;
        -webkit-tap-highlight-color: transparent;
      }

      .sf-touch-btn .icon-wrap {
        display: flex;
        align-items: center;
        justify-content: center;
        width: 20px;
        height: 20px;
        color: inherit;
      }

      .sf-touch-btn .icon-wrap svg {
        display: block;
        width: 18px;
        height: 18px;
      }

      .sf-touch-btn:active, .sf-touch-btn.active {
        transform: scale(0.92);
        background: rgba(56, 189, 248, 0.18);
        border-color: rgba(56, 189, 248, 0.65);
        color: #38bdf8;
        box-shadow: 0 0 16px rgba(56, 189, 248, 0.35);
      }

      .sf-touch-btn span.label {
        font-size: 8px;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        opacity: 0.75;
        font-family: "SFMono-Regular", Consolas, monospace;
      }

      /* Primary Slingshot Boost Button (Flat Gold Accent) */
      .sf-touch-btn.boost {
        width: 58px;
        height: 58px;
        border-radius: 16px;
        background: rgba(255, 215, 0, 0.08);
        border: 1.5px solid rgba(255, 215, 0, 0.55);
        color: #ffd700;
        box-shadow: 0 0 20px rgba(255, 215, 0, 0.2);
      }

      .sf-touch-btn.boost .icon-wrap svg {
        width: 22px;
        height: 22px;
      }

      .sf-touch-btn.boost:active, .sf-touch-btn.boost.active {
        transform: scale(0.92);
        background: rgba(255, 215, 0, 0.25);
        border-color: #ffd700;
        box-shadow: 0 0 28px rgba(255, 215, 0, 0.5);
      }"""
    rep(old_touch_css, new_touch_css, "Flat Touch Button CSS")

    # -------------------------------------------------------------
    # 3. Replace Touch HUD Buttons with SVG Vector Icons
    # -------------------------------------------------------------
    old_hud_cluster = """    // Row 1: Auxiliary Functions (Focus, Cam, Cockpit, Formation)
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

    new_hud_cluster = """    // Vector SVG Icons for Flat Minimalist Mobile Touch UI
    const SVG_ICONS = {
      focus: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"><circle cx="12" cy="13" r="8"/><path d="M12 9v4l2.5 2.5M12 5V2M10 2h4"/></svg>',
      camera: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"><path d="M2 12s3.6-7 10-7 10 7 10 7-3.6 7-10 7-10-7-10-7Z"/><circle cx="12" cy="12" r="3"/></svg>',
      cockpit: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"><path d="M4 19V9l8-5 8 5v10M2 19h20M9 19v-4h6v4"/></svg>',
      formation: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3l4 7h-8zM6 14l3 6h-6zM18 14l3 6h-6z"/></svg>',
      codex: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"><path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20M4 19.5A2.5 2.5 0 0 0 6.5 22H20V2H6.5A2.5 2.5 0 0 0 4 4.5v15zM8 7h8M8 11h5"/></svg>',
      settings: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 1 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 1 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 1 1-2.83-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 1 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 1 1 2.83-2.83l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 1 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 1 1 2.83 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 1 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z"/></svg>',
      warp: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M13 2L3 14h9l-1 8 10-12h-9l1-8z"/></svg>',
      boost: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2l7 10h-5v10h-4V12H5l7-10z"/></svg>'
    };

    // Row 1: Auxiliary Functions (Focus, Cam, Cockpit, Formation)
    const rowAux = document.createElement('div');
    rowAux.className = 'sf-touch-btn-row';

    const btnFocus = createTouchButton(SVG_ICONS.focus, '专注', () => {
      if (window.StarfieldFocusEngine) window.StarfieldFocusEngine.toggleDashboard();
    });
    const btnCam = createTouchButton(SVG_ICONS.camera, '镜头', () => Engine.toggleCamera());
    const btnCockpit = createTouchButton(SVG_ICONS.cockpit, '舱内', () => Engine.toggleCockpit());
    const btnFormation = createTouchButton(SVG_ICONS.formation, '编队', () => Engine.cycleFormation());

    rowAux.appendChild(btnFocus);
    rowAux.appendChild(btnCam);
    rowAux.appendChild(btnCockpit);
    rowAux.appendChild(btnFormation);

    // Row 2: Flight Primary Actions (Codex, Settings, Warp Gear, Slingshot Boost)
    const rowFlight = document.createElement('div');
    rowFlight.className = 'sf-touch-btn-row';

    const btnCodex = createTouchButton(SVG_ICONS.codex, '图鉴', () => Engine.toggleCodex());
    const btnSettings = createTouchButton(SVG_ICONS.settings, '设置', () => Engine.toggleSettings());
    const btnWarp = createTouchButton(SVG_ICONS.warp, '曲速', () => Engine.throttleUp());
    
    // Slingshot Boost primary button (Flat High-Energy Surge)
    const btnBoost = document.createElement('button');
    btnBoost.className = 'sf-touch-btn boost';
    btnBoost.innerHTML = `<span class="icon-wrap">${SVG_ICONS.boost}</span><span class="label">BOOST</span>`;
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
    rep(old_hud_cluster, new_hud_cluster, "GamepadTouchControls SVG Vector Icons & Action Cluster")

    old_create_touch_btn = """  function createTouchButton(icon, label, callback) {
    const btn = document.createElement('button');
    btn.className = 'sf-touch-btn';
    btn.innerHTML = `<span>${icon}</span><span class="label">${label}</span>`;
    btn.addEventListener('pointerdown', (e) => {"""

    new_create_touch_btn = """  function createTouchButton(iconSvg, label, callback) {
    const btn = document.createElement('button');
    btn.className = 'sf-touch-btn';
    btn.innerHTML = `<span class="icon-wrap">${iconSvg}</span><span class="label">${label}</span>`;
    btn.addEventListener('pointerdown', (e) => {"""
    rep(old_create_touch_btn, new_create_touch_btn, "createTouchButton with SVG icon-wrap")

    # -------------------------------------------------------------
    # 4. Remove Emoji from Gamepad status text
    # -------------------------------------------------------------
    old_gp_txt = """    if (txt) txt.textContent = `🎮 ${name || 'GAMEPAD'} CONNECTED`;"""
    new_gp_txt = """    if (txt) txt.textContent = `[CONTROLLER] ${name || 'GAMEPAD'} CONNECTED`;"""
    rep(old_gp_txt, new_gp_txt, "Gamepad badge clean text (remove emoji)")

    # -------------------------------------------------------------
    # 5. Flat Design Updates in StarfieldFocusEngine
    # -------------------------------------------------------------
    old_focus_open = """        <div class="sf-focus-badge">⏱️ STARFIELD FOCUS EXPEDITION</div>
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
        <button class="sf-focus-btn cancel" id="sf-focus-cancel-btn">返回漫游</button>"""

    new_focus_open = """        <div class="sf-focus-badge">FOCUS EXPEDITION // CHRONO FLOW</div>
        <h2>深空专注远征 · 番茄钟心流</h2>
        <div class="sf-focus-summary">
          把手机作为深空挂机摆件。星舰在浩瀚宇宙中默默前行，伴你进入深度心流。
          <div class="sf-focus-alert-text">
            <strong>航道约束准则</strong>：严禁中途切换应用或离开星舰；脱离引力场将导致动力枯竭坠入黑洞奇点。
          </div>
        </div>

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
          <div class="sf-focus-rewards-title">EXPEDITION REWARDS // 专属探索勋礼</div>
          <div class="sf-reward-item"><span class="sf-reward-dot"></span><b>30 MIN</b> 达成解锁【专属曜金 · 泰坦折纸旗舰】</div>
          <div class="sf-reward-item"><span class="sf-reward-dot"></span><b>60 MIN</b> 达成解锁【黄金纪元引力波流光】与先行者密文</div>
        </div>

        <button class="sf-focus-btn primary" id="sf-focus-start-btn">启动深空专注探索</button>
        <button class="sf-focus-btn cancel" id="sf-focus-cancel-btn">返回漫游</button>"""
    rep(old_focus_open, new_focus_open, "Focus Dashboard Flat Content (no emoji)")

    # -------------------------------------------------------------
    # 6. Flat Ticker HUD and Toasts
    # -------------------------------------------------------------
    old_ticker_hud = """      ticker.innerHTML = `
        <div class="sf-focus-pulse-dot"></div>
        <span>✦ 专注探索中 · 剩余 ${timeStr} · 勿切后台 ✦</span>
      `;"""

    new_ticker_hud = """      ticker.innerHTML = `
        <div class="sf-focus-pulse-dot"></div>
        <span class="sf-focus-ticker-tag">FOCUS</span>
        <span class="sf-focus-ticker-time">${timeStr}</span>
        <span class="sf-focus-ticker-sub">AUTONOMOUS CRUISE</span>
      `;"""
    rep(old_ticker_hud, new_ticker_hud, "Flat Ticker HUD layout")

    # Toasts in startMission, triggerWarning, completeMission, failMission
    old_toasts_block = """      showToast(`✦ 专注深空远征启航 · 目标 ${durationMinutes} 分钟 · 勿切后台 ✦`, 6);
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
    }"""

    new_toasts_block = """      showToast(`[FOCUS CRUISE] 专注深空远征启航 · 目标 ${durationMinutes} 分钟 · 勿切后台`, 6);
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

      showToast('[GRAVITY ALERT] 检测到离开星舰！引力约束将在 10 秒后瓦解！请立即返回！', 5);

      if (this.warningTimerId) clearInterval(this.warningTimerId);
      this.warningTimerId = setInterval(() => {
        this.warningRemainingSec--;
        if (this.warningRemainingSec <= 0) {
          clearInterval(this.warningTimerId);
          this.warningTimerId = null;
          this.failMission();
        } else {
          showToast(`[GRAVITY ALERT] 偏离航道！剩余 ${this.warningRemainingSec} 秒坠毁！立即返回！`, 1.5);
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
      showToast('[GRAVITY STABILIZED] 引力约束已恢复重稳 · 继续专注深空巡航', 4);
    }"""
    rep(old_toasts_block, new_toasts_block, "Flat Warning & Status Toasts")

    # Complete & Fail toasts & modals
    old_complete_fail = """      // Trigger 5D Tesseract celebration
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
    }"""

    new_complete_fail = """      // Trigger 5D Tesseract celebration
      if (typeof window.triggerTesseract === 'function') {
        window.triggerTesseract();
      }
      showToast(`[VOYAGE COMPLETE] 专注远征圆满达成 · 累积专注 ${this.stats.totalFocusMinutes} 分钟`, 8);

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

      showToast('[SINGULARITY PLUNGE] 离开星舰导致燃料耗尽 · 星舰已坠入黑洞奇点', 8);

      this.showSummaryModal(false, elapsedMin, []);
    }"""
    rep(old_complete_fail, new_complete_fail, "Flat Completion & Failure Toasts")

    old_summary_modal = """      if (success) {
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
      }"""

    new_summary_modal = """      if (success) {
        content.innerHTML = `
          <div class="sf-focus-badge">MISSION ACCOMPLISHED // EXPEDITION COMPLETE</div>
          <h2>深空远征 · 圆满抵达</h2>
          <p class="sf-focus-summary">
            保持专注未触碰手机，成功完成了 <strong>${minutes} 分钟</strong> 全景深空自主漫游探索！
          </p>
          <div class="sf-focus-stats-row">
            <div><span>累积专注</span><b>${this.stats.totalFocusMinutes} 分钟</b></div>
            <div><span>远征航次</span><b>${this.stats.completedVoyages} 次</b></div>
            <div><span>当前连胜</span><b>${this.stats.currentStreak} 次</b></div>
          </div>
          ${rewards.length > 0 ? `
            <div class="sf-focus-rewards">
              <div class="sf-focus-rewards-title">UNLOCKED REWARDS // 专属探索勋礼</div>
              ${rewards.map(r => `<div class="sf-reward-item"><span class="sf-reward-dot"></span>${r}</div>`).join('')}
            </div>
          ` : ''}
          <div class="sf-focus-quote">“把方向交给星光，把时间留给当下。”</div>
          <button class="sf-focus-btn primary" id="sf-focus-confirm-btn">继续深空漫游</button>
        `;
      } else {
        content.innerHTML = `
          <div class="sf-focus-badge fail">CRITICAL FAILURE // SINGULARITY PLUNGE</div>
          <h2>引力坍缩 · 坠毁于视界</h2>
          <p class="sf-focus-summary">
            在专注进行至 <strong>${minutes} 分钟</strong> 时脱离星舰，折叠力场失谐，星舰动力核心熄火坠入黑洞奇点。
          </p>
          <div class="sf-focus-stats-row">
            <div><span>累积专注</span><b>${this.stats.totalFocusMinutes} 分钟</b></div>
            <div><span>失败航次</span><b>${this.stats.failedVoyages} 次</b></div>
            <div><span>连胜纪录</span><b>${this.stats.bestStreak} 次</b></div>
          </div>
          <div class="sf-focus-quote">“浩瀚星海从不苛责跌落者。重整引力帆，下一次我们将飞得更远。”</div>
          <button class="sf-focus-btn restart" id="sf-focus-confirm-btn">重整星舰 · 再次起航</button>
        `;
      }"""
    rep(old_summary_modal, new_summary_modal, "Summary Modal Flat Aesthetic")

    old_active_modal = """        <div class="sf-focus-badge">✦ VOYAGE IN PROGRESS</div>
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
        <button class="sf-focus-btn restart" id="sf-focus-abort-btn" style="border-color:#ff6666;color:#ff8888;">放弃本次远征 (将坠毁)</button>"""

    new_active_modal = """        <div class="sf-focus-badge">VOYAGE IN PROGRESS // CRUISE ACTIVE</div>
        <h2>深空专注探索状态</h2>
        <div class="sf-focus-stats-row">
          <div><span>剩余时间</span><b style="font-size:20px;color:#fff3a8;">${timeStr}</b></div>
          <div><span>当前里程</span><b>${distance} KLY</b></div>
          <div><span>目标时长</span><b>${Math.round(this.targetDurationSec / 60)} 分钟</b></div>
        </div>
        <p class="sf-focus-summary" style="text-align:center;">
          星舰正在深空自主巡航，请将手机放置在桌面享受星光与古典乐心流。<br>
          <span style="opacity:0.6;font-size:12px;">（屏幕常亮保护已开启 · 切出应用或离开界面将导致坠机）</span>
        </p>
        <button class="sf-focus-btn primary" id="sf-focus-resume-btn">继续专注心流</button>
        <button class="sf-focus-btn restart" id="sf-focus-abort-btn" style="border-color:#f43f5e;color:#fb7185;">放弃本次远征 (将坠毁)</button>"""
    rep(old_active_modal, new_active_modal, "Active Dialog Flat Aesthetic")

    with open(target_path, "w", encoding="utf-8") as f:
        f.write(content)

    print("FLAT DESIGN SYSTEM SUCCESSFULLY APPLIED TO starfield.html!")

if __name__ == "__main__":
    apply_flat_mobile_ui()
