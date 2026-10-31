# -*- coding: utf-8 -*-
"""
Inject Beta Channel (先锋实验室与实验性玩法自愿体验计划) into starfield.html
"""

with open('starfield-pub/starfield.html', 'rb') as f:
    content = f.read()

# 1. Add Beta Lab section into settings drawer before OTA UPDATE section
old_settings_ota = """  <div class="settings-section">
    <div class="settings-section-title mono">热更新与版本 // OTA UPDATE</div>""".encode('utf-8')

new_settings_ota = """  <div class="settings-section">
    <div class="settings-section-title mono">先锋实验室与实验性玩法 // BETA LAB</div>
    <div class="shortcut-list">
      <div class="shortcut-row">
        <span>当前体验通道</span>
        <span class="shortcut-key" id="sf-beta-channel-status" style="color:#38bdf8;">稳定正式版</span>
      </div>
      <div class="shortcut-row" style="align-items:flex-start;flex-direction:column;gap:6px;">
        <span style="font-size:11px;color:#94a3b8;line-height:1.4;">
          包含 4 大太空新玩法原型：搜打撤·鸭科夫、引力弹弓太空鸟、红警前哨战RTS、戴森球计划。玩家可自愿启用，随时退出。
        </span>
        <div style="display:flex;gap:8px;width:100%;margin-top:4px;">
          <button class="photo-btn active" id="btn-toggle-beta-channel" style="flex:1;padding:5px 10px;color:#ffd700;font-weight:700;">
            ✦ 自愿加入先锋测试 ↗
          </button>
        </div>
      </div>
    </div>
  </div>
  <div class="settings-section">
    <div class="settings-section-title mono">热更新与版本 // OTA UPDATE</div>""".encode('utf-8')

# 2. Add btn-toggle-beta-channel listener in drawer bindings
old_drawer_bindings = """    // OTA Update Button Binding
    const otaBtn = $('btn-check-ota');""".encode('utf-8')

new_drawer_bindings = """    // Beta Channel Toggle Binding
    const btnBetaToggle = $('btn-toggle-beta-channel');
    if (btnBetaToggle) {
      btnBetaToggle.addEventListener('click', () => {
        if (window.StarfieldBetaLab) {
          window.StarfieldBetaLab.toggle();
        }
      });
    }

    // OTA Update Button Binding
    const otaBtn = $('btn-check-ota');""".encode('utf-8')

# 3. Update showOtaNotification to support voluntary Beta participation
old_show_ota = """  function showOtaNotification(payload) {
    if (document.getElementById('sf-ota-banner')) return;
    const banner = document.createElement('div');
    banner.id = 'sf-ota-banner';
    banner.className = 'sf-ota-pill';
    // The native bridge used to send a bare string, the new one sends
    // {version, build, changelog}. Accept both.
    const info = (payload && typeof payload === 'object') ? payload : { version: payload };
    const rawVer = info.version ? String(info.version) : '1.1.0';
    const version = 'v' + rawVer.replace(/^v/i, '');
    const desc = info.changelog || '核心视觉与2K清晰度已优化，轻触立即热更新生效';

    banner.innerHTML = `
      <div class="sf-ota-sparkle">✦</div>
      <div class="sf-ota-content">
        <span class="sf-ota-title">发现热更新 ${version}</span>
        <span class="sf-ota-desc">${desc}</span>
      </div>
      <button class="sf-ota-apply" id="sf-ota-apply-btn">立即生效</button>
      <button class="sf-ota-close" id="sf-ota-close-btn" aria-label="关闭">✕</button>
    `;
    document.body.appendChild(banner);

    document.getElementById('sf-ota-apply-btn').addEventListener('click', () => {
      if (window.StarfieldNative && typeof window.StarfieldNative.reloadApp === 'function') {
        window.StarfieldNative.reloadApp();
      } else {
        location.reload();
      }
    });

    document.getElementById('sf-ota-close-btn').addEventListener('click', () => {
      banner.style.opacity = '0';
      banner.style.transform = 'translate(-50%, -20px)';
      setTimeout(() => banner.remove(), 400);
    });
  }""".encode('utf-8')

new_show_ota = """  function showOtaNotification(payload) {
    if (document.getElementById('sf-ota-banner')) return;
    const banner = document.createElement('div');
    banner.id = 'sf-ota-banner';
    banner.className = 'sf-ota-pill';
    // The native bridge used to send a bare string, the new one sends
    // {version, build, changelog}. Accept both.
    const info = (payload && typeof payload === 'object') ? payload : { version: payload };
    const rawVer = info.version ? String(info.version) : '1.18.0';
    const version = 'v' + rawVer.replace(/^v/i, '');
    const isBeta = info.is_beta || (rawVer.includes('beta') || (info.title && info.title.includes('先锋')));
    const title = isBeta ? `发现热更新 ${version} · 先锋实验版` : `发现热更新 ${version}`;
    const desc = info.changelog || (isBeta ? '全新上线先锋实验室，包含 4 大太空玩法！默认保持纯净漫游，您可自愿选择是否体验。' : '核心视觉与2K清晰度已优化，轻触立即热更新生效');

    banner.innerHTML = `
      <div class="sf-ota-sparkle">${isBeta ? '🚀' : '✦'}</div>
      <div class="sf-ota-content">
        <span class="sf-ota-title">${title}</span>
        <span class="sf-ota-desc">${desc}</span>
      </div>
      <div style="display:flex; gap:6px; align-items:center;">
        <button class="sf-ota-apply" id="sf-ota-apply-btn">${isBeta ? '立即体验 Beta' : '立即生效'}</button>
        ${isBeta ? '<button class="sf-ota-keep-stable" id="sf-ota-keep-btn" style="background:rgba(255,255,255,0.08);border:1px solid rgba(255,255,255,0.18);border-radius:12px;padding:4px 8px;color:#94a3b8;font-size:11px;cursor:pointer;">保持正式版</button>' : ''}
      </div>
      <button class="sf-ota-close" id="sf-ota-close-btn" aria-label="关闭">✕</button>
    `;
    document.body.appendChild(banner);

    document.getElementById('sf-ota-apply-btn').addEventListener('click', () => {
      if (isBeta && window.StarfieldBetaLab) {
        window.StarfieldBetaLab.setEnabled(true);
      }
      if (window.StarfieldNative && typeof window.StarfieldNative.reloadApp === 'function') {
        window.StarfieldNative.reloadApp();
      } else {
        location.reload();
      }
    });

    const keepBtn = document.getElementById('sf-ota-keep-btn');
    if (keepBtn) {
      keepBtn.addEventListener('click', () => {
        banner.style.opacity = '0';
        banner.style.transform = 'translate(-50%, -20px)';
        setTimeout(() => banner.remove(), 400);
        if (typeof showToast === 'function') showToast('已保持当前稳定版，随时可在设置菜单中开启先锋体验 ✦', 3);
      });
    }

    document.getElementById('sf-ota-close-btn').addEventListener('click', () => {
      banner.style.opacity = '0';
      banner.style.transform = 'translate(-50%, -20px)';
      setTimeout(() => banner.remove(), 400);
    });
  }""".encode('utf-8')

# 4. Insert StarfieldBetaLab controller before Master Mode Switcher
old_master_switcher = """  /* =========================================================================
   * 1. MASTER MODE SWITCHER
   * ========================================================================= */""".encode('utf-8')

new_master_switcher = """  /* =========================================================================
   * 0. BETA LAB & CHANNEL CONTROLLER (自愿加入先锋测试通道)
   * ========================================================================= */
  const BETA_KEY = 'sf_beta_channel_v1';
  function isBetaEnabled() {
    return localStorage.getItem(BETA_KEY) === 'true';
  }

  function setBetaEnabled(enabled) {
    try { localStorage.setItem(BETA_KEY, enabled ? 'true' : 'false'); } catch(e) {}
    updateBetaUI();
    if (!enabled && currentMode !== 'cruise') {
      switchMode('cruise');
    }
  }

  function updateBetaUI() {
    const enabled = isBetaEnabled();
    const modeBar = document.getElementById('sf-mode-bar');
    if (modeBar) {
      modeBar.style.display = enabled ? 'flex' : 'none';
    }
    const statusTag = document.getElementById('sf-beta-channel-status');
    const toggleBtn = document.getElementById('btn-toggle-beta-channel');
    if (statusTag) {
      statusTag.textContent = enabled ? '先锋测试版 (BETA)' : '稳定正式版';
      statusTag.style.color = enabled ? '#ffd700' : '#38bdf8';
    }
    if (toggleBtn) {
      toggleBtn.textContent = enabled ? '✕ 退出测试返回正式版' : '✦ 自愿加入先锋测试 ↗';
      toggleBtn.style.color = enabled ? '#94a3b8' : '#ffd700';
      toggleBtn.style.background = enabled ? 'rgba(255, 255, 255, 0.08)' : 'linear-gradient(135deg, rgba(251, 191, 36, 0.25) 0%, rgba(217, 119, 6, 0.15) 100%)';
    }
  }

  window.StarfieldBetaLab = {
    isEnabled: isBetaEnabled,
    setEnabled: setBetaEnabled,
    updateUI: updateBetaUI,
    toggle: function() {
      const next = !isBetaEnabled();
      setBetaEnabled(next);
      if (next) {
        if (typeof showToast === 'function') showToast('✦ 已加入先锋测试计划！顶部已解锁 4 大太空新玩法！', 3.5);
      } else {
        if (typeof showToast === 'function') showToast('已退出测试计划，恢复经典纯净漫游模式。', 2.5);
      }
      return next;
    }
  };

  // Initial update
  setTimeout(updateBetaUI, 100);

  /* =========================================================================
   * 1. MASTER MODE SWITCHER
   * ========================================================================= */""".encode('utf-8')

# 5. Default sf-mode-bar CSS to display: none;
old_mode_bar_css = """#sf-mode-bar {
  position: fixed;
  top: calc(env(safe-area-inset-top, 0px) + 10px);
  left: 50%;
  transform: translateX(-50%);
  display: flex;""".encode('utf-8')

new_mode_bar_css = """#sf-mode-bar {
  position: fixed;
  top: calc(env(safe-area-inset-top, 0px) + 10px);
  left: 50%;
  transform: translateX(-50%);
  display: none;""".encode('utf-8')

def apply_patch(data, old, new, name):
    old_crlf = old.replace(b'\r\n', b'\n').replace(b'\n', b'\r\n')
    new_crlf = new.replace(b'\r\n', b'\n').replace(b'\n', b'\r\n')
    if old_crlf not in data:
        raise ValueError(f"Failed to find match for: {name}")
    data = data.replace(old_crlf, new_crlf, 1)
    print(f"Successfully patched: {name}")
    return data

content = apply_patch(content, old_settings_ota, new_settings_ota, "1. Settings drawer Beta Lab section")
content = apply_patch(content, old_drawer_bindings, new_drawer_bindings, "2. Drawer bindings")
content = apply_patch(content, old_show_ota, new_show_ota, "3. showOtaNotification")
content = apply_patch(content, old_mode_bar_css, new_mode_bar_css, "4. mode_bar_css default hidden")
content = apply_patch(content, old_master_switcher, new_master_switcher, "5. StarfieldBetaLab controller")

with open('starfield-pub/starfield.html', 'wb') as f:
    f.write(content)

with open('starfield-pub/android/app/src/main/assets/starfield.html', 'wb') as f:
    f.write(content)

print("Beta Lab patches applied and mirrored to Android assets successfully!")
