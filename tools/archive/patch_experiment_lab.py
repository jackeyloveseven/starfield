# -*- coding: utf-8 -*-
"""
实验舱改造（信息架构修复）
=============================================================================
问题：beta 通道把「自由漫游」也是一个 tab 的常驻顶栏钉在每一屏的最上方，
把原作品降级成「两个外部玩法原型」的兄弟，而且标题页/开局页也压着它。

本补丁：
1. 拆除 #sf-mode-bar（常驻顶栏）与 .sf-mode-btn；
2. 新增 #sf-lab-modal「实验舱」——原型玩法的唯一入口，位于 设置(ESC) → 实验舱；
3. 退出原型：右上角 ✕ / ESC（ESC 原本被主键位表吞掉，是死路）；
4. 修正设置抽屉里「4 大玩法」的过期文案与「解锁 4 大玩法」的 toast。
"""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent
MASTER = ROOT / 'starfield.html'
MIRROR = ROOT / 'android/app/src/main/assets/starfield.html'


def crlf(s: str) -> str:
    return s.replace('\r\n', '\n').replace('\n', '\r\n')


def replace_span(text, start, end, new, label, include_end=False):
    i = text.find(start)
    if i < 0:
        sys.exit(f'[FAIL] {label}: start anchor missing -> {start[:60]!r}')
    j = text.find(end, i)
    if j < 0:
        sys.exit(f'[FAIL] {label}: end anchor missing -> {end[:60]!r}')
    if include_end:
        j += len(end)
    print(f'  [ok] {label}: {j - i} bytes -> {len(new)} bytes')
    return text[:i] + new + text[j:]


def replace_once(text, old, new, label):
    n = text.count(old)
    if n != 1:
        sys.exit(f'[FAIL] {label}: expected 1 occurrence, found {n}')
    print(f'  [ok] {label}')
    return text.replace(old, new, 1)


LAB_CSS = crlf('''/* --- Experiment Lab: 原型玩法的唯一入口（不再常驻顶栏） --- */
#sf-lab-modal {
  position: fixed;
  inset: 0;
  z-index: 1300;
  display: none;
  align-items: center;
  justify-content: center;
  padding: 16px;
  background: rgba(4, 7, 13, 0.72);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
}
#sf-lab-modal.open { display: flex; }
.sf-lab-box {
  width: min(440px, 92vw);
  max-height: 86vh;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 9px;
  padding: 20px;
  border: 1px solid rgba(255, 255, 255, 0.14);
  border-radius: 18px;
  background: linear-gradient(160deg, rgba(12, 19, 30, 0.98) 0%, rgba(8, 12, 20, 0.99) 100%);
  box-shadow: 0 24px 64px rgba(0, 0, 0, 0.72);
}
.sf-lab-head { display: flex; align-items: center; justify-content: space-between; }
.sf-lab-kicker { font-size: 10px; letter-spacing: 0.18em; color: #7dd3fc; }
.sf-lab-close {
  border: none;
  background: transparent;
  color: #94a3b8;
  font-size: 13px;
  line-height: 1;
  padding: 5px 7px;
  border-radius: 8px;
  cursor: pointer;
}
.sf-lab-close:hover { color: #f1f5f9; background: rgba(255, 255, 255, 0.08); }
.sf-lab-note {
  margin: 0 0 3px;
  font-size: 11px;
  line-height: 1.65;
  color: #94a3b8;
}
.sf-lab-item {
  display: flex;
  align-items: center;
  gap: 12px;
  width: 100%;
  padding: 11px 13px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 14px;
  background: rgba(255, 255, 255, 0.03);
  color: #e6edf2;
  font: inherit;
  text-align: left;
  cursor: pointer;
  transition: border-color 0.2s ease, background 0.2s ease;
}
.sf-lab-item:hover { border-color: rgba(125, 211, 252, 0.45); background: rgba(125, 211, 252, 0.07); }
.sf-lab-item.is-current {
  border-color: rgba(244, 208, 111, 0.45);
  background: rgba(244, 208, 111, 0.06);
  cursor: default;
}
.sf-lab-glyph { width: 22px; font-size: 17px; text-align: center; }
.sf-lab-text { display: flex; flex-direction: column; gap: 3px; flex: 1; min-width: 0; }
.sf-lab-name { font-size: 13px; font-weight: 600; letter-spacing: 0.02em; }
.sf-lab-desc { font-size: 10.5px; line-height: 1.45; color: #94a3b8; }
.sf-lab-tag { flex-shrink: 0; font-size: 9.5px; letter-spacing: 0.1em; color: #7dd3fc; }
.sf-lab-item.is-current .sf-lab-tag { color: #f4d06f; }
.sf-lab-foot { margin-top: 2px; text-align: center; font-size: 9px; letter-spacing: 0.12em; color: rgba(148, 163, 184, 0.7); }

''')


LAB_HTML = crlf('''<!-- 实验舱：原型玩法的唯一入口。主航线不需要也不应该和原型并排成 tab。 -->
<div id="sf-lab-modal" role="dialog" aria-modal="true" aria-labelledby="sf-lab-title" aria-hidden="true">
  <div class="sf-lab-box">
    <div class="sf-lab-head">
      <span class="sf-lab-kicker mono" id="sf-lab-title">EXPERIMENT LAB // 实验舱</span>
      <button class="sf-lab-close" id="sf-lab-close-btn" aria-label="关闭实验舱">✕</button>
    </div>
    <p class="sf-lab-note">主航线只有一条。下面两个是独立原型，各有自己的画布与玩法；退出即回到星空，不记录专注，也不改动主航线。</p>
    <button class="sf-lab-item is-current" id="sf-lab-item-cruise" aria-current="true">
      <span class="sf-lab-glyph" aria-hidden="true">🌌</span>
      <span class="sf-lab-text">
        <span class="sf-lab-name">主航线 · 深空漫游</span>
        <span class="sf-lab-desc">星空本体：折纸舰队、引力走廊、黑洞与专注计时</span>
      </span>
      <span class="sf-lab-tag mono">当前</span>
    </button>
    <button class="sf-lab-item" id="sf-lab-item-redalert" aria-current="false">
      <span class="sf-lab-glyph" aria-hidden="true">⚡</span>
      <span class="sf-lab-text">
        <span class="sf-lab-name">红色警戒 · 前哨 RTS</span>
        <span class="sf-lab-desc">采矿 / 建造 / 波次防御的即时战略原型</span>
      </span>
      <span class="sf-lab-tag mono">进入 ↗</span>
    </button>
    <button class="sf-lab-item" id="sf-lab-item-dyson" aria-current="false">
      <span class="sf-lab-glyph" aria-hidden="true">☀️</span>
      <span class="sf-lab-text">
        <span class="sf-lab-name">戴森球 · 星系工程</span>
        <span class="sf-lab-desc">太阳帆、运载火箭与巨构骨架的工程原型</span>
      </span>
      <span class="sf-lab-tag mono">进入 ↗</span>
    </button>
    <div class="sf-lab-foot mono">原型玩法不写入专注记录 · ESC 退出</div>
  </div>
</div>

''')


LAB_JS = crlf('''  const labModal = document.getElementById('sf-lab-modal');
  const labItems = {
    cruise: document.getElementById('sf-lab-item-cruise'),
    redalert: document.getElementById('sf-lab-item-redalert'),
    dyson: document.getElementById('sf-lab-item-dyson')
  };

  const overlayRedAlert = document.getElementById('sf-redalert-overlay');
  const overlayDyson = document.getElementById('sf-dyson-overlay');

  let currentMode = 'cruise';
  window.currentMode = 'cruise';

  function updateLabState() {
    Object.keys(labItems).forEach(k => {
      const el = labItems[k];
      if (!el) return;
      const isCurrent = (k === currentMode);
      el.classList.toggle('is-current', isCurrent);
      el.setAttribute('aria-current', isCurrent ? 'true' : 'false');
      const tag = el.querySelector('.sf-lab-tag');
      if (tag) tag.textContent = isCurrent ? '当前' : '进入 ↗';
    });
  }

  function openLab() {
    if (!labModal) return;
    if (typeof GameSettings !== 'undefined' && GameSettings.close) GameSettings.close();
    updateLabState();
    labModal.classList.add('open');
    labModal.setAttribute('aria-hidden', 'false');
  }

  function closeLab() {
    if (!labModal) return;
    if (!labModal.classList.contains('open')) return;
    labModal.classList.remove('open');
    labModal.setAttribute('aria-hidden', 'true');
  }

  window.openStarfieldLab = openLab;
  window.closeStarfieldLab = closeLab;

  function switchMode(newMode) {
    if (currentMode === newMode) { closeLab(); return; }
    currentMode = newMode;
    window.currentMode = newMode;
    [overlayRedAlert, overlayDyson].forEach(o => o && o.classList.remove('active'));

    // Stop all active expansion engines
    if (window.RedAlertRTS) window.RedAlertRTS.stop();
    if (window.DysonSphereProgram) window.DysonSphereProgram.stop();
    document.getElementById('sf-dsp-tech-modal')?.classList.remove('active');
    const touchOverlay = document.getElementById('starfield-touch-overlay');
    if (touchOverlay && newMode !== 'cruise') touchOverlay.style.display = 'none';

    if (newMode === 'cruise') {
      if (typeof showToast === 'function') showToast('已回到主航线 · 深空漫游 🌌', 2);
    } else if (newMode === 'redalert') {
      overlayRedAlert && overlayRedAlert.classList.add('active');
      if (window.RedAlertRTS) window.RedAlertRTS.start();
      if (typeof showToast === 'function') showToast('实验舱 · 红色警戒前哨 RTS（ESC 退出）', 3);
    } else if (newMode === 'dyson') {
      overlayDyson && overlayDyson.classList.add('active');
      if (window.DysonSphereProgram) window.DysonSphereProgram.start();
      if (typeof showToast === 'function') showToast('实验舱 · 戴森球星系工程（ESC 退出）', 3);
    }
    updateLabState();
    closeLab();
  }

  // 原型玩法里主键位表会整体 return，ESC 因此没有出口 —— 这里补一条独占的退出键。
  window.addEventListener('keydown', (e) => {
    if (e.key !== 'Escape') return;
    if (currentMode !== 'cruise') {
      e.preventDefault();
      e.stopPropagation();
      switchMode('cruise');
      return;
    }
    if (labModal && labModal.classList.contains('open')) {
      e.preventDefault();
      e.stopPropagation();
      closeLab();
    }
  }, true);

  labItems.cruise?.addEventListener('click', () => switchMode('cruise'));
  labItems.redalert?.addEventListener('click', () => switchMode('redalert'));
  labItems.dyson?.addEventListener('click', () => switchMode('dyson'));
  document.getElementById('sf-lab-close-btn')?.addEventListener('click', closeLab);
  labModal?.addEventListener('click', (e) => { if (e.target === labModal) closeLab(); });

  document.getElementById('sf-ra-exit-btn')?.addEventListener('click', () => switchMode('cruise'));
  document.getElementById('sf-dsp-exit-btn')?.addEventListener('click', () => switchMode('cruise'));

  window.switchStarfieldMode = switchMode;
''')


def main():
    text = MASTER.read_text(encoding='utf-8', newline='')
    before_len = len(text)
    print('patching', MASTER)

    # 1. CSS: 顶栏样式 -> 实验舱样式
    text = replace_span(
        text,
        crlf('#sf-mode-bar {\n  position: fixed;'),
        crlf('/* --- Fullscreen Game Overlay Overlays --- */'),
        LAB_CSS,
        'CSS: mode bar -> lab modal',
    )

    # 2. HTML: 顶栏 DOM -> 实验舱 DOM
    text = replace_span(
        text,
        crlf('<div id="sf-mode-bar">'),
        crlf('<!-- 2D minigame overlays removed'),
        LAB_HTML,
        'HTML: mode bar -> lab modal',
    )

    # 3. JS: 主模式切换器 -> 实验舱 + switchMode
    text = replace_span(
        text,
        crlf("  const btnCruise = document.getElementById('sf-btn-mode-cruise');"),
        crlf('  window.switchStarfieldMode = switchMode;'),
        LAB_JS,
        'JS: master mode switcher -> lab',
        include_end=True,
    )

    # 4. updateBetaUI: 不再控制顶栏显隐，改为控制「打开实验舱」按钮
    text = replace_once(
        text,
        crlf("""    const modeBar = document.getElementById('sf-mode-bar');
    if (modeBar) {
      modeBar.style.display = enabled ? 'flex' : 'none';
    }
"""),
        crlf("""    const openLabBtn = document.getElementById('btn-open-lab');
    if (openLabBtn) {
      openLabBtn.style.display = enabled ? 'block' : 'none';
    }
    if (!enabled) closeLab();
"""),
        'JS: updateBetaUI mode bar -> lab button',
    )

    # 5. setBetaEnabled: 退出测试时收起实验舱
    text = replace_once(
        text,
        crlf("""    updateBetaUI();
    if (!enabled && currentMode !== 'cruise') {
      switchMode('cruise');
    }"""),
        crlf("""    updateBetaUI();
    if (!enabled) {
      closeLab();
      if (currentMode !== 'cruise') switchMode('cruise');
    }"""),
        'JS: setBetaEnabled closes lab',
    )

    # 6. 加入/退出文案：不再宣称「解锁 4 大玩法」
    text = replace_once(
        text,
        crlf("""        if (typeof showToast === 'function') showToast('✦ 已加入先锋测试计划！顶部已解锁 4 大太空新玩法！', 3.5);
      } else {
        if (typeof showToast === 'function') showToast('已退出测试计划，恢复经典纯净漫游模式。', 2.5);"""),
        crlf("""        if (typeof showToast === 'function') showToast('✦ 已加入先锋测试。实验舱入口在设置(ESC)里，随时进出原型玩法。', 3.5);
        if (typeof openLab === 'function') openLab();
      } else {
        if (typeof showToast === 'function') showToast('已退出先锋测试，回到纯净主航线。', 2.5);"""),
        'JS: beta toggle toast copy',
    )

    # 7. 抽屉：章节标题 + 过期文案 + 新增「打开实验舱」
    text = replace_once(
        text,
        crlf("""    <div class="settings-section-title mono">先锋实验室与实验性玩法 // BETA LAB</div>"""),
        crlf("""    <div class="settings-section-title mono">实验舱与原型玩法 // EXPERIMENT LAB</div>"""),
        'HTML: drawer section title',
    )
    text = replace_once(
        text,
        crlf("""          包含 4 大太空新玩法原型：搜打撤·鸭科夫、引力弹弓太空鸟、红警前哨战RTS、戴森球计划。玩家可自愿启用，随时退出。"""),
        crlf("""          <strong style="color:#e2e8f0;font-weight:600;">主航线永远只有一条。</strong>实验舱里另放着两个独立原型（前哨 RTS / 星系巨构）；进去是另一块画布，退出即回到星空，不写入专注记录。<br>（搜打撤与引力弹弓已并入主航线的飞行系统，不再是独立模式。）"""),
        'HTML: drawer stale copy',
    )
    text = replace_once(
        text,
        crlf("""        <div style="display:flex;gap:8px;width:100%;margin-top:4px;">
          <button class="photo-btn active" id="btn-toggle-beta-channel" style="flex:1;padding:5px 10px;color:#ffd700;font-weight:700;">
            ✦ 自愿加入先锋测试 ↗
          </button>
        </div>"""),
        crlf("""        <div style="display:flex;gap:8px;width:100%;margin-top:4px;">
          <button class="photo-btn active" id="btn-open-lab" style="flex:1;padding:5px 10px;color:#7dd3fc;font-weight:700;display:none;">
            ✦ 打开实验舱
          </button>
          <button class="photo-btn active" id="btn-toggle-beta-channel" style="flex:1;padding:5px 10px;color:#ffd700;font-weight:700;">
            ✦ 自愿加入先锋测试 ↗
          </button>
        </div>"""),
        'HTML: drawer open-lab button',
    )

    # 8. 抽屉里绑定「打开实验舱」
    text = replace_once(
        text,
        crlf("""    // Beta Channel Toggle Binding
    const btnBetaToggle = $('btn-toggle-beta-channel');"""),
        crlf("""    // Experiment Lab Entry (prototype modes live behind this hatch only)
    const btnOpenLab = $('btn-open-lab');
    if (btnOpenLab) {
      btnOpenLab.addEventListener('click', () => {
        if (window.StarfieldBetaLab) window.StarfieldBetaLab.setEnabled(true);
        if (window.openStarfieldLab) window.openStarfieldLab();
      });
    }

    // Beta Channel Toggle Binding
    const btnBetaToggle = $('btn-toggle-beta-channel');"""),
        'JS: drawer open-lab binding',
    )

    leftovers = ['sf-mode-bar', 'sf-mode-btn', 'sf-btn-mode-']
    for token in leftovers:
        n = text.count(token)
        if n:
            sys.exit(f'[FAIL] stale token still present: {token} x{n}')

    MASTER.write_text(text, encoding='utf-8', newline='')
    MIRROR.write_text(text, encoding='utf-8', newline='')
    print(f'written: {MASTER} ({before_len} -> {len(text)} bytes)')
    print(f'mirrored: {MIRROR}')


if __name__ == '__main__':
    main()
