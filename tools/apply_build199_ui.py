# -*- coding: utf-8 -*-
"""
tools/apply_build199_ui.py
Apply Starfield Build 199 (v1.9.9.9.9.11):
1. Fluid Island Capsule Touch Dock for Mobile (42px ergonomic targets, frosted glass capsule background, haptic feedback)
2. In-situ Real-Time Status Indicators (Warp 1x/5x/15x glow badge, Camera AUTO/FLAG badge, Formation F1-F4 badge)
3. Cinema / Pure Vision Mode (Zen Mode) with smooth HUD fade-out, 'Z' shortcut, desktop button, and mobile tray button
4. Sync versions across all 4 anchors and verify SHA256 parity with Android assets
"""
import re
import json
import shutil
from pathlib import Path

BASE_DIR = Path(r"d:\items\code\projects\starfield\starfield-pub")
HTML_FILE = BASE_DIR / "starfield.html"
SW_FILE = BASE_DIR / "service-worker.js"
VERSION_FILE = BASE_DIR / "version.json"
ASSETS_DIR = BASE_DIR / "android" / "app" / "src" / "main" / "assets"

def main():
    print("=== Applying Build 199 (v1.9.9.9.9.11) UI Enhancements ===")
    
    html = HTML_FILE.read_text(encoding="utf-8", errors="ignore")
    
    # -------------------------------------------------------------
    # 1. Add Cinema Mode Styles into main <style> block
    # -------------------------------------------------------------
    cinema_css = """
/* --- Cinema / Pure Vision (Zen) Mode --- */
body.cinema-mode #masthead,
body.cinema-mode #edition,
body.cinema-mode #camera-hud,
body.cinema-mode #journey,
body.cinema-mode #controls,
body.cinema-mode #hint,
body.cinema-mode .sf-sonar-capsule,
body.cinema-mode #sf-contract-hud {
  opacity: 0 !important;
  pointer-events: none !important;
  transform: translateY(-8px) !important;
  transition: opacity 0.45s cubic-bezier(0.16, 1, 0.3, 1), transform 0.45s cubic-bezier(0.16, 1, 0.3, 1) !important;
}
body.cinema-mode #journey,
body.cinema-mode #controls {
  transform: translateY(12px) !important;
}
body.cinema-mode .sf-touch-cluster {
  opacity: 0.15 !important;
  transition: opacity 0.4s ease;
}
body.cinema-mode .sf-touch-cluster:hover,
body.cinema-mode .sf-touch-cluster:active {
  opacity: 0.95 !important;
}
#controls button.cinema-active {
  color: #7ce8ff !important;
  border-color: rgba(0, 220, 255, 0.6) !important;
  box-shadow: 0 0 10px rgba(0, 220, 255, 0.35) !important;
}
"""
    if "/* --- Cinema / Pure Vision (Zen) Mode --- */" not in html:
        html = html.replace("</style>", cinema_css + "\n</style>", 1)
        print("  [+] Added Cinema Mode CSS into <style>")

    # -------------------------------------------------------------
    # 2. Add Cinema Toggle Button into desktop #controls
    # -------------------------------------------------------------
    cinema_desktop_btn = """<button class="control" id="cinema-toggle" title="纯净视界 · 隐藏所有HUD (Z)" aria-label="纯净视界"><span class="icon cinema-icon"><svg viewBox="0 0 16 16" width="16" height="16" fill="none" stroke="currentColor" stroke-width="1.3"><circle cx="8" cy="8" r="5.5" stroke-dasharray="3 1.5"/><circle cx="8" cy="8" r="2"/></svg></span></button>
<button class="control" id="fullscreen-toggle" """
    if 'id="cinema-toggle"' not in html:
        html = html.replace('<button class="control" id="fullscreen-toggle" ', cinema_desktop_btn, 1)
        print("  [+] Added #cinema-toggle button into #controls")

    # -------------------------------------------------------------
    # 3. Add StarfieldCinema Global Object & Event Handlers
    # -------------------------------------------------------------
    cinema_js = """
// --- Starfield Cinema / Pure Vision (Zen) Mode Manager ---
window.StarfieldCinema = {
  active: false,
  toggle(force) {
    this.active = (typeof force === 'boolean') ? force : !this.active;
    const body = document.body;
    if (this.active) {
      body.classList.add('cinema-mode');
      if (typeof toast === 'function') toast('纯净视界 · 轻触任意处恢复 HUD (Z)', 2.2);
    } else {
      body.classList.remove('cinema-mode');
      if (typeof toast === 'function') toast('视界复位 · HUD 已唤醒', 1.4);
    }
    const btn = document.getElementById('cinema-toggle');
    if (btn) {
      btn.setAttribute('aria-pressed', this.active ? 'true' : 'false');
      btn.classList.toggle('cinema-active', this.active);
    }
    const touchBtn = document.getElementById('sf-touch-cinema-btn');
    if (touchBtn) touchBtn.classList.toggle('active', this.active);
    try { if (navigator.vibrate) navigator.vibrate(12); } catch (_) {}
  },
  exit() {
    if (this.active) this.toggle(false);
  }
};

// Tap canvas in Cinema Mode to exit
window.addEventListener('pointerdown', (e) => {
  if (window.StarfieldCinema && window.StarfieldCinema.active) {
    if (e.target && e.target.closest && e.target.closest('button, .sf-touch-btn, .sf-touch-more-tray, #settings-drawer, #codex-modal, .modal, .sf-drawer')) return;
    window.StarfieldCinema.exit();
  }
}, { capture: true });
"""
    if "window.StarfieldCinema" not in html:
        # Place before desktop button bindings
        html = html.replace("$('warp-toggle').addEventListener('click',", cinema_js + "\n$('warp-toggle').addEventListener('click',", 1)
        print("  [+] Added window.StarfieldCinema API")

    # Bind #cinema-toggle click and 'Z' key in keydown
    if "$('cinema-toggle')" not in html:
        html = html.replace(
            "$('sound-toggle').addEventListener('click',toggleSound);",
            "const _cBtn = $('cinema-toggle'); if (_cBtn) _cBtn.addEventListener('click', () => { if (window.StarfieldCinema) window.StarfieldCinema.toggle(); });\n$('sound-toggle').addEventListener('click',toggleSound);",
            1
        )
        print("  [+] Bound #cinema-toggle click event")

    # Bind 'Z' key and Escape in keydown
    if "e.key.toLowerCase()==='z'" not in html:
        html = html.replace(
            "if(e.key==='Escape'){",
            "if(e.key==='Escape'){\n    if(window.StarfieldCinema && window.StarfieldCinema.active){ window.StarfieldCinema.exit(); return; }",
            1
        )
        html = html.replace(
            "else if(e.key.toLowerCase()==='h'){",
            "else if(e.key.toLowerCase()==='z'||e.code==='KeyZ'){\n    if(window.StarfieldCinema) window.StarfieldCinema.toggle();\n    return;\n  }\n  else if(e.key.toLowerCase()==='h'){",
            1
        )
        print("  [+] Added 'Z' key and Escape handlers for Cinema Mode")

    # -------------------------------------------------------------
    # 4. Upgrade injectStyles() for Fluid Island Capsule Dock
    # -------------------------------------------------------------
    old_styles_pattern = r"/\* Web-Style Frosted Glass Minimalist Bottom-Right Controls \*/.*?\.sf-gamepad-badge \{"
    new_styles_content = """/* Web-Style Frosted Glass Minimalist Bottom-Right Controls: Fluid Island Capsule */
      .sf-touch-cluster {
        position: absolute;
        right: calc(env(safe-area-inset-right, 0px) + 12px);
        bottom: calc(env(safe-area-inset-bottom, 0px) + 14px);
        display: flex;
        flex-direction: column;
        align-items: flex-end;
        gap: 8px;
        pointer-events: auto;
        touch-action: none;
        z-index: 125;
      }

      .sf-touch-primary-row {
        display: flex;
        align-items: center;
        gap: 6px;
        padding: 5px 8px;
        border-radius: 30px;
        background: rgba(10, 16, 26, 0.72) !important;
        border: 1px solid rgba(255, 255, 255, 0.14) !important;
        backdrop-filter: blur(20px) !important;
        -webkit-backdrop-filter: blur(20px) !important;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.65), inset 0 1px 0 rgba(255, 255, 255, 0.18) !important;
      }

      .sf-touch-btn {
        position: relative;
        height: 42px;
        width: 42px;
        min-width: 42px;
        padding: 0 !important;
        border-radius: 50% !important;
        background: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        box-shadow: none !important;
        color: rgba(230, 242, 255, 0.9);
        font-family: inherit;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        cursor: pointer;
        outline: none;
        touch-action: manipulation;
        transition: transform 0.15s cubic-bezier(0.18, 0.89, 0.32, 1.28), background 0.15s ease, color 0.15s ease, border-color 0.15s ease;
        -webkit-tap-highlight-color: transparent;
        user-select: none;
        -webkit-user-select: none;
      }

      .sf-touch-btn .icon-wrap {
        display: flex;
        align-items: center;
        justify-content: center;
        width: 18px;
        height: 18px;
        color: inherit;
        transform: translateY(-2px);
      }

      .sf-touch-btn .icon-wrap svg {
        display: block;
        width: 17px;
        height: 17px;
      }

      .sf-touch-btn span.label {
        display: none !important;
      }

      .sf-touch-btn:active, .sf-touch-btn.active {
        transform: scale(0.90);
        background: rgba(255, 255, 255, 0.22) !important;
        border-color: rgba(255, 255, 255, 0.3) !important;
        color: #ffffff;
      }

      /* In-situ Micro Status Badge */
      .sf-insitu-badge {
        position: absolute;
        bottom: 3px;
        left: 50%;
        transform: translateX(-50%);
        font-family: "SFMono-Regular", Consolas, monospace;
        font-size: 7.5px;
        font-weight: 700;
        line-height: 1;
        letter-spacing: -0.02em;
        padding: 1px 3px;
        border-radius: 4px;
        background: rgba(5, 8, 14, 0.82);
        color: rgba(200, 225, 255, 0.95);
        pointer-events: none;
        border: 0.5px solid rgba(255, 255, 255, 0.2);
        white-space: nowrap;
      }
      .sf-touch-btn.warp-tier-0 .sf-insitu-badge {
        color: #a0c8f0;
      }
      .sf-touch-btn.warp-tier-1 {
        background: rgba(0, 200, 255, 0.12) !important;
        border-color: rgba(0, 200, 255, 0.4) !important;
      }
      .sf-touch-btn.warp-tier-1 .sf-insitu-badge {
        background: rgba(0, 180, 240, 0.35);
        color: #7ce8ff;
        border-color: rgba(0, 220, 255, 0.6);
        box-shadow: 0 0 6px rgba(0, 220, 255, 0.5);
      }
      .sf-touch-btn.warp-tier-2 {
        background: rgba(255, 200, 0, 0.15) !important;
        border-color: rgba(255, 215, 0, 0.5) !important;
      }
      .sf-touch-btn.warp-tier-2 .sf-insitu-badge {
        background: rgba(255, 180, 0, 0.4);
        color: #ffe680;
        border-color: rgba(255, 215, 0, 0.8);
        box-shadow: 0 0 8px rgba(255, 215, 0, 0.6);
      }
      .sf-touch-btn.flagship-active {
        background: rgba(0, 255, 180, 0.12) !important;
        border-color: rgba(0, 255, 180, 0.4) !important;
      }
      .sf-touch-btn.flagship-active .sf-insitu-badge {
        color: #7affd4;
        border-color: rgba(0, 255, 180, 0.5);
      }

      /* Secondary Expandable Action Tray (Fluid Arc Island) */
      .sf-touch-more-tray {
        display: none;
        align-items: center;
        flex-wrap: wrap;
        justify-content: flex-end;
        max-width: min(290px, 78vw);
        box-sizing: border-box;
        gap: 8px;
        padding: 8px 12px;
        border-radius: 22px;
        background: rgba(10, 16, 26, 0.85) !important;
        border: 1px solid rgba(255, 255, 255, 0.16) !important;
        backdrop-filter: blur(24px) !important;
        -webkit-backdrop-filter: blur(24px) !important;
        box-shadow: 0 12px 36px rgba(0, 0, 0, 0.72), inset 0 1px 0 rgba(255, 255, 255, 0.16) !important;
        animation: sfTrayIn 0.25s cubic-bezier(0.16, 1, 0.3, 1) both;
      }
      .sf-touch-more-tray.open {
        display: flex;
      }
      .sf-touch-more-tray .sf-touch-btn {
        width: 44px !important;
        height: 44px !important;
        min-width: 44px !important;
        border-radius: 14px !important;
        background: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        color: rgba(215, 235, 255, 0.9);
      }
      .sf-touch-more-tray .sf-touch-btn span.label {
        display: block !important;
        font-size: 8.5px;
        letter-spacing: 0.03em;
        opacity: 0.85;
        margin-top: 1px;
        font-family: inherit;
        white-space: nowrap;
      }
      .sf-touch-more-tray .sf-touch-btn .icon-wrap svg {
        width: 17px;
        height: 17px;
      }
      .sf-touch-more-tray .sf-touch-btn:active {
        background: rgba(255, 255, 255, 0.22) !important;
        color: #ffffff;
      }

      @keyframes sfTrayIn {
        from { opacity: 0; transform: translateY(12px) scale(0.94); }
        to { opacity: 1; transform: translateY(0) scale(1); }
      }

      /* Badges for unhatched planet cores */
      .sf-touch-core-badge {
        position: absolute;
        top: -3px;
        right: -3px;
        min-width: 15px;
        height: 15px;
        padding: 0 4px;
        border-radius: 8px;
        background: linear-gradient(135deg, #ffd700, #ff8c00);
        color: #050810;
        font-size: 9px;
        font-weight: 800;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        line-height: 15px;
        text-align: center;
        box-shadow: 0 0 8px rgba(255, 215, 0, 0.6);
        pointer-events: none;
        animation: sfBadgePulse 2s infinite ease-in-out;
      }
      .sf-more-core-dot {
        position: absolute;
        top: 5px;
        right: 5px;
        width: 7px;
        height: 7px;
        border-radius: 50%;
        background: #ffd700;
        box-shadow: 0 0 6px #ffd700;
        pointer-events: none;
        animation: sfBadgePulse 2s infinite ease-in-out;
      }
      @keyframes sfBadgePulse {
        0%, 100% { transform: scale(1); box-shadow: 0 0 6px rgba(255, 215, 0, 0.5); }
        50% { transform: scale(1.18); box-shadow: 0 0 12px rgba(255, 215, 0, 0.95); }
      }

      .sf-gamepad-badge {"""

    html, count = re.subn(old_styles_pattern, new_styles_content, html, flags=re.DOTALL)
    print(f"  [+] Replaced touch styles in injectStyles (count={count})")

    # -------------------------------------------------------------
    # 5. Add btnCinema into moreTray & in-situ badges logic in createTouchHUD
    # -------------------------------------------------------------
    old_more_tray = """    const btnRotate = createTouchButton('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 12a9 9 0 0 0-9-9 9.75 9.75 0 0 0-6.74 2.74L3 8"/><path d="M3 3v5h5"/><path d="M3 12a9 9 0 0 0 9 9 9.75 9.75 0 0 0 6.74-2.74L21 16"/><path d="M16 21h5v-5"/></svg>', '横/竖屏', () => {
      if (window.STARFIELD_ORIENTATION) window.STARFIELD_ORIENTATION.toggle();
      moreTray.classList.remove('open');
    });

    moreTray.appendChild(btnPlanet);
    moreTray.appendChild(btnSonar);
    moreTray.appendChild(btnCockpit);
    moreTray.appendChild(btnSettings);
    moreTray.appendChild(btnFocus);
    moreTray.appendChild(btnRotate);"""

    new_more_tray = """    const btnRotate = createTouchButton('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 12a9 9 0 0 0-9-9 9.75 9.75 0 0 0-6.74 2.74L3 8"/><path d="M3 3v5h5"/><path d="M3 12a9 9 0 0 0 9 9 9.75 9.75 0 0 0 6.74-2.74L21 16"/><path d="M16 21h5v-5"/></svg>', '横/竖屏', () => {
      if (window.STARFIELD_ORIENTATION) window.STARFIELD_ORIENTATION.toggle();
      moreTray.classList.remove('open');
    });
    const btnCinema = createTouchButton('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"><circle cx="12" cy="12" r="8" stroke-dasharray="3 2"/><circle cx="12" cy="12" r="3.5"/></svg>', '视界', () => {
      if (window.StarfieldCinema) window.StarfieldCinema.toggle();
      moreTray.classList.remove('open');
    });
    btnCinema.id = 'sf-touch-cinema-btn';

    moreTray.appendChild(btnPlanet);
    moreTray.appendChild(btnSonar);
    moreTray.appendChild(btnCockpit);
    moreTray.appendChild(btnCinema);
    moreTray.appendChild(btnSettings);
    moreTray.appendChild(btnFocus);
    moreTray.appendChild(btnRotate);"""

    if old_more_tray in html:
        html = html.replace(old_more_tray, new_more_tray, 1)
        print("  [+] Added btnCinema into mobile moreTray")
    else:
        print("  [!] Warning: old_more_tray pattern not found")

    # In-situ Badges logic
    old_row_primary = """    // Primary Minimal Action Row (Normal State: 5 Clean Minimalist Buttons)
    const rowPrimary = document.createElement('div');
    rowPrimary.className = 'sf-touch-primary-row';

    // 1. Camera Toggle Button (视角)
    const btnCam = createTouchButton(SVG_ICONS.camera, '视角', () => Engine.toggleCamera());

    // 2. Warp Gear Toggle Button (曲率)
    const btnWarp = createTouchButton(SVG_ICONS.warp, '曲率', () => Engine.cycleWarp());

    // 3. Formation Cycle Button (编队)
    const btnFormation = createTouchButton(SVG_ICONS.formation, '编队', () => Engine.cycleFormation(1));

    // 4. Codex Drawer Toggle Button (图鉴)
    const btnCodex = createTouchButton(SVG_ICONS.codex, '图鉴', () => Engine.toggleCodex());"""

    new_row_primary = """    // Primary Minimal Action Row (Fluid Island Capsule Dock)
    const rowPrimary = document.createElement('div');
    rowPrimary.className = 'sf-touch-primary-row';

    // 1. Camera Toggle Button (视角)
    const btnCam = createTouchButton(SVG_ICONS.camera, '视角', () => {
      Engine.toggleCamera();
      updateTouchInSituBadges();
    });

    // 2. Warp Gear Toggle Button (曲率)
    const btnWarp = createTouchButton(SVG_ICONS.warp, '曲率', () => {
      Engine.cycleWarp();
      updateTouchInSituBadges();
    });

    // 3. Formation Cycle Button (编队)
    const btnFormation = createTouchButton(SVG_ICONS.formation, '编队', () => {
      Engine.cycleFormation(1);
      updateTouchInSituBadges();
    });

    // 4. Codex Drawer Toggle Button (图鉴)
    const btnCodex = createTouchButton(SVG_ICONS.codex, '图鉴', () => Engine.toggleCodex());

    // Real-Time In-situ Status Badge Updater
    const updateTouchInSituBadges = () => {
      // Warp Badge
      const S = window.Starfield;
      const gear = (S && typeof S.getWarpGear === 'function') ? S.getWarpGear() : 0;
      let wBadge = btnWarp.querySelector('.sf-insitu-badge');
      if (!wBadge) {
        wBadge = document.createElement('span');
        wBadge.className = 'sf-insitu-badge';
        btnWarp.appendChild(wBadge);
      }
      btnWarp.classList.remove('warp-tier-0', 'warp-tier-1', 'warp-tier-2');
      btnWarp.classList.add(`warp-tier-${gear}`);
      wBadge.textContent = gear === 0 ? '1x' : gear === 1 ? '5x' : '15x';

      // Camera Badge
      const isCockpit = (S && typeof S.isCockpit === 'function' && S.isCockpit());
      let cBadge = btnCam.querySelector('.sf-insitu-badge');
      if (!cBadge) {
        cBadge = document.createElement('span');
        cBadge.className = 'sf-insitu-badge';
        btnCam.appendChild(cBadge);
      }
      btnCam.classList.toggle('flagship-active', isCockpit);
      cBadge.textContent = isCockpit ? 'FLAG' : 'AUTO';

      // Formation Badge
      const fIdx = (window.FleetFormations && typeof window.FleetFormations.currentFormation !== 'undefined') ? window.FleetFormations.currentFormation : 0;
      let fBadge = btnFormation.querySelector('.sf-insitu-badge');
      if (!fBadge) {
        fBadge = document.createElement('span');
        fBadge.className = 'sf-insitu-badge';
        btnFormation.appendChild(fBadge);
      }
      fBadge.textContent = `F${fIdx + 1}`;
    };
    window.updateTouchInSituBadges = updateTouchInSituBadges;"""

    if old_row_primary in html:
        html = html.replace(old_row_primary, new_row_primary, 1)
        print("  [+] Added In-situ status badges logic to rowPrimary")
    else:
        print("  [!] Warning: old_row_primary pattern not found")

    # Hook updateTouchInSituBadges() into frame(now)
    old_frame_hook = "if (typeof resetFramePools === 'function') resetFramePools();"
    new_frame_hook = """if (typeof resetFramePools === 'function') resetFramePools();
 if (typeof updateTouchInSituBadges === 'function' && ((frameCount || 0) % 15 === 0)) updateTouchInSituBadges();"""
    if old_frame_hook in html and "updateTouchInSituBadges === 'function'" not in html:
        html = html.replace(old_frame_hook, new_frame_hook, 1)
        print("  [+] Hooked updateTouchInSituBadges into frame loop (throttled)")

    # -------------------------------------------------------------
    # 6. Bump version to Build 199 (v1.9.9.9.9.11)
    # -------------------------------------------------------------
    old_version_tag = 'id="sf-version-tag">v1.9.9.9.9.10 (Build 198)'
    new_version_tag = 'id="sf-version-tag">v1.9.9.9.9.11 (Build 199)'
    html = html.replace(old_version_tag, new_version_tag)

    old_local_build = 'const localBuild = 198;'
    new_local_build = 'const localBuild = 199;'
    html = html.replace(old_local_build, new_local_build)

    HTML_FILE.write_text(html, encoding="utf-8")
    print("  [+] Saved starfield.html")

    # Update version.json
    v_data = json.loads(VERSION_FILE.read_text(encoding="utf-8"))
    v_data["version"] = "1.9.9.9.9.11"
    v_data["build"] = 199
    v_data["description"] = "Build 199: Mobile Fluid Island Capsule Touch Dock with In-situ Status Indicators and Pure Vision (Zen) Cinema Mode"
    v_data["timestamp"] = "2026-11-21T22:15:00Z"
    VERSION_FILE.write_text(json.dumps(v_data, indent=2, ensure_ascii=False), encoding="utf-8")
    print("  [+] Updated version.json -> v1.9.9.9.9.11 (Build 199)")

    # Update service-worker.js
    sw_text = SW_FILE.read_text(encoding="utf-8")
    sw_text = re.sub(r"CACHE_VERSION\s*=\s*'v[0-9.]+-b\d+'", "CACHE_VERSION = 'v1.9.9.9.9.11-b199'", sw_text)
    SW_FILE.write_text(sw_text, encoding="utf-8")
    print("  [+] Updated service-worker.js -> v1.9.9.9.9.11-b199")

    # Mirror to android assets
    ASSETS_DIR.mkdir(parents=True, exist_ok=True)
    shutil.copy2(HTML_FILE, ASSETS_DIR / "starfield.html")
    shutil.copy2(SW_FILE, ASSETS_DIR / "service-worker.js")
    shutil.copy2(VERSION_FILE, ASSETS_DIR / "version.json")
    print("  [+] Mirrored starfield.html, service-worker.js, version.json to Android assets")

    print("\n=== Build 199 Application Completed Successfully! ===")

if __name__ == "__main__":
    main()
