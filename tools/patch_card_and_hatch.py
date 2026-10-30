# -*- coding: utf-8 -*-
"""
Patch starfield.html to address:
1. Card bottom typography occluding action buttons (both front & back)
2. Refined exquisite color palettes & styling across all tiers
3. Disallow incubation when planets/cores are depleted (0 count)
"""

with open('starfield-pub/starfield.html', 'rb') as f:
    content = f.read()

# 1. Update btnHatchCore click handler in drawer
old_hatch_btn = """    const btnHatchCore = $('btn-hatch-core');
    if (btnHatchCore) {
      btnHatchCore.addEventListener('click', () => {
        if (window.StarfieldHatch && window.StarfieldHatch.openNextCore) {
          window.StarfieldHatch.openNextCore();
        }
      });
    }""".encode('utf-8')

new_hatch_btn = """    const btnHatchCore = $('btn-hatch-core');
    if (btnHatchCore) {
      btnHatchCore.addEventListener('click', () => {
        if (window.StarfieldHatch && window.StarfieldHatch.getUnopenedCores) {
          const c = window.StarfieldHatch.getUnopenedCores();
          if (c <= 0) {
            const msg = '✦ 暂无待孵化星核 · 前往专注远征即可凝聚新星核';
            if (typeof showToast === 'function') showToast(msg, 3);
            else if (typeof window.toast === 'function') window.toast(msg, 3);
            return;
          }
        }
        if (window.StarfieldHatch && window.StarfieldHatch.openNextCore) {
          window.StarfieldHatch.openNextCore();
        }
      });
    }""".encode('utf-8')

# 2. Update TIERS definition with exquisite palettes
old_tiers = """  const TIERS = {
    common: { cn: '常见', color: '#8ea9c4', rank: 0 },
    rare:   { cn: '稀有', color: '#6fb3ff', rank: 1 },
    epic:   { cn: '史诗', color: '#a97bff', rank: 2 },
    legend: { cn: '传说', color: '#ff6b6b', rank: 3 },
    myth:   { cn: '神话', color: '#ffcf6b', rank: 4 }
  };""".encode('utf-8')

new_tiers = """  const TIERS = {
    common: {
      cn: '常见',
      title: '钛银深青 · 漫游星界',
      color: '#7dd3fc',
      border: 'rgba(125, 211, 252, 0.45)',
      glow: 'rgba(56, 189, 248, 0.28)',
      accent: '#38bdf8',
      badgeBg: 'rgba(56, 189, 248, 0.12)',
      grad: 'linear-gradient(150deg, rgba(15, 23, 42, 0.98) 0%, rgba(12, 74, 110, 0.85) 60%, rgba(7, 12, 20, 0.98) 100%)',
      rank: 0
    },
    rare: {
      cn: '稀有',
      title: '极光碧玉 · 深空灵光',
      color: '#34d399',
      border: 'rgba(52, 211, 153, 0.52)',
      glow: 'rgba(16, 185, 129, 0.32)',
      accent: '#10b981',
      badgeBg: 'rgba(16, 185, 129, 0.14)',
      grad: 'linear-gradient(150deg, rgba(6, 38, 31, 0.98) 0%, rgba(4, 120, 87, 0.85) 60%, rgba(5, 20, 16, 0.98) 100%)',
      rank: 1
    },
    epic: {
      cn: '史诗',
      title: '星云紫晶 · 虚空奇观',
      color: '#c084fc',
      border: 'rgba(192, 132, 252, 0.58)',
      glow: 'rgba(168, 85, 247, 0.38)',
      accent: '#a855f7',
      badgeBg: 'rgba(168, 85, 247, 0.16)',
      grad: 'linear-gradient(150deg, rgba(30, 17, 58, 0.98) 0%, rgba(88, 28, 135, 0.85) 60%, rgba(11, 7, 24, 0.98) 100%)',
      rank: 2
    },
    legend: {
      cn: '传说',
      title: '曜金日曜 · 恒星加冕',
      color: '#fbbf24',
      border: 'rgba(251, 191, 36, 0.68)',
      glow: 'rgba(245, 158, 11, 0.42)',
      accent: '#f59e0b',
      badgeBg: 'rgba(245, 158, 11, 0.18)',
      grad: 'linear-gradient(150deg, rgba(38, 25, 4, 0.98) 0%, rgba(120, 53, 15, 0.88) 60%, rgba(18, 10, 3, 0.98) 100%)',
      rank: 3
    },
    myth: {
      cn: '神话',
      title: '奇点幻彩 · 高维神话',
      color: '#f472b6',
      border: 'rgba(244, 114, 182, 0.72)',
      glow: 'rgba(236, 72, 153, 0.48)',
      accent: '#e879f9',
      badgeBg: 'rgba(244, 114, 182, 0.20)',
      grad: 'linear-gradient(150deg, rgba(37, 9, 30, 0.98) 0%, rgba(74, 4, 78, 0.88) 40%, rgba(23, 37, 84, 0.92) 100%)',
      rank: 4
    }
  };""".encode('utf-8')

# 3. Update openNextCore to forbid hatch when cores <= 0
old_open_next = """  function openNextCore() {
    const cores = getUnopenedCores();
    if (cores <= 0) {
      if (typeof showToast === 'function') showToast('暂无待孵化星核，已为你补充 3 颗测试星核！', 3); else if (typeof window.toast === 'function') window.toast('暂无待孵化星核，已为你补充 3 颗测试星核！', 3);
      addCores(3);
    }
    const left = getUnopenedCores();
    setUnopenedCores(left - 1);
    const item = roll(30);
    if (window.StarfieldHatch && typeof window.StarfieldHatch.openFor === 'function') {
      window.StarfieldHatch.openFor(item, true);
    }
    return item;
  }""".encode('utf-8')

new_open_next = """  function openNextCore() {
    const cores = getUnopenedCores();
    if (cores <= 0) {
      const msg = '✦ 暂无待孵化星核 · 前往专注远征即可凝聚新星核';
      if (typeof showToast === 'function') showToast(msg, 3);
      else if (typeof window.toast === 'function') window.toast(msg, 3);
      return null;
    }
    setUnopenedCores(cores - 1);
    const item = roll(30);
    if (window.StarfieldHatch && typeof window.StarfieldHatch.openFor === 'function') {
      window.StarfieldHatch.openFor(item, true);
    }
    return item;
  }""".encode('utf-8')

# 4. Update card CSS to give spacious bottom reserve and avoid overlap
old_card_css = """.sf-hatch-card {
  position: relative;
  width: min(340px, 86vw);
  aspect-ratio: 9 / 15.2;
  border-radius: 24px;
  background: linear-gradient(150deg, rgba(20, 29, 46, 0.96) 0%, rgba(7, 12, 20, 0.98) 100%);
  border: 1.5px solid rgba(212, 175, 55, 0.4);
  box-shadow: 0 24px 60px rgba(0, 0, 0, 0.8), inset 0 1px 0 rgba(255, 255, 255, 0.15), 0 0 28px rgba(212, 175, 55, 0.15);
  display: flex;
  flex-direction: column;
  padding: 16px 14px;
  box-sizing: border-box;
  cursor: pointer;
  overflow: hidden;
  perspective: 1200px;
  transform-style: preserve-3d;
  transition: transform 0.6s cubic-bezier(0.2, 0.8, 0.2, 1), box-shadow 0.4s ease;
  z-index: 20;
}""".encode('utf-8')

new_card_css = """.sf-hatch-card {
  position: relative;
  width: min(340px, 88vw);
  aspect-ratio: 9 / 15.6;
  border-radius: 24px;
  background: var(--tier-grad, linear-gradient(150deg, rgba(20, 29, 46, 0.96) 0%, rgba(7, 12, 20, 0.98) 100%));
  border: 1.5px solid var(--tier-border, rgba(212, 175, 55, 0.45));
  box-shadow: 0 24px 60px rgba(0, 0, 0, 0.85), inset 0 1px 0 rgba(255, 255, 255, 0.18), 0 0 32px var(--tier-glow, rgba(212, 175, 55, 0.2));
  display: flex;
  flex-direction: column;
  padding: 14px 14px 64px 14px;
  box-sizing: border-box;
  cursor: pointer;
  overflow: hidden;
  perspective: 1200px;
  transform-style: preserve-3d;
  transition: transform 0.6s cubic-bezier(0.2, 0.8, 0.2, 1), box-shadow 0.4s ease, border-color 0.4s ease;
  z-index: 20;
}""".encode('utf-8')

# 5. Update orb stage, card info and actions in CSS
old_card_body_css = """.sf-card-orb-stage {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  z-index: 6;
  margin: 4px 0;
}
.sf-hatch-orb {
  position: relative;
  width: min(175px, 50vw);
  aspect-ratio: 1;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 0 32px var(--tier, rgba(255, 215, 0, 0.3)), inset 0 0 20px rgba(0, 0, 0, 0.8);
  cursor: grab;
}
.sf-hatch-orb:active { cursor: grabbing; }
.sf-hatch-orb::before {
  content: "";
  position: absolute;
  inset: -6px;
  border-radius: 50%;
  border: 1.5px solid rgba(212, 175, 55, 0.4);
  box-shadow: 0 0 16px rgba(212, 175, 55, 0.2);
  pointer-events: none;
}
.sf-hatch-orb::after {
  content: "";
  position: absolute;
  inset: -12px;
  border-radius: 50%;
  border: 1px dashed rgba(255, 255, 255, 0.15);
  pointer-events: none;
  animation: spinClockwise 45s infinite linear;
}
canvas.sf-planet-canvas {
  width: 100%;
  height: 100%;
  border-radius: 50%;
  display: block;
  filter: drop-shadow(0 4px 18px rgba(0, 0, 0, 0.6));
}

.sf-card-info {
  position: relative;
  z-index: 6;
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  gap: 4px;
}
.sf-hatch-name {
  font-size: 21px;
  font-weight: 700;
  letter-spacing: 0.16em;
  color: #f8fafc;
  line-height: 1.25;
  text-shadow: 0 2px 10px rgba(0, 0, 0, 0.8), 0 0 16px var(--tier, rgba(255, 215, 0, 0.4));
  transition: opacity 0.5s ease;
}
.sf-hatch-meta {
  font-size: 11px;
  letter-spacing: 0.14em;
  color: var(--tier, #ffd700);
  font-weight: 500;
  transition: opacity 0.5s ease;
}
.sf-card-specs {
  font-size: 9px;
  letter-spacing: 0.1em;
  color: #94a3b8;
  font-family: ui-monospace, monospace;
  margin-top: 2px;
}
.sf-hatch-hint {
  font-size: 9px;
  letter-spacing: 0.2em;
  color: rgba(255, 255, 255, 0.4);
  margin-top: 4px;
}
.sf-hatch-card.revealed .sf-hatch-hint { display: none; }

.sf-card-actions {
  position: absolute;
  bottom: 14px;
  left: 14px;
  right: 14px;
  z-index: 25;
  display: flex;
  gap: 8px;
  box-sizing: border-box;
}
.sf-card-act-btn {
  flex: 1;
  padding: 8px 0;
  border-radius: 14px;
  font-size: 10.5px;
  letter-spacing: 0.08em;
  font-weight: 600;
  cursor: pointer;
  border: 1px solid rgba(255, 255, 255, 0.16);
  background: rgba(255, 255, 255, 0.06);
  color: #f1f5f9;
  transition: all 0.2s ease;
}
.sf-card-act-btn:hover { background: rgba(255, 255, 255, 0.15); }
.sf-card-act-btn.primary {
  border-color: rgba(212, 175, 55, 0.4);
  background: linear-gradient(135deg, rgba(212, 175, 55, 0.25) 0%, rgba(212, 175, 55, 0.08) 100%);
  color: #ffd700;
}""".encode('utf-8')

new_card_body_css = """.sf-card-orb-stage {
  flex: 1 1 0;
  min-height: 110px;
  max-height: 190px;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  z-index: 6;
  margin: 2px 0;
}
.sf-hatch-orb {
  position: relative;
  width: min(150px, 44vw);
  aspect-ratio: 1;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 0 32px var(--tier-glow, rgba(255, 215, 0, 0.3)), inset 0 0 20px rgba(0, 0, 0, 0.8);
  cursor: grab;
}
.sf-hatch-orb:active { cursor: grabbing; }
.sf-hatch-orb::before {
  content: "";
  position: absolute;
  inset: -6px;
  border-radius: 50%;
  border: 1.5px solid var(--tier-border, rgba(212, 175, 55, 0.4));
  box-shadow: 0 0 16px var(--tier-glow, rgba(212, 175, 55, 0.2));
  pointer-events: none;
}
.sf-hatch-orb::after {
  content: "";
  position: absolute;
  inset: -12px;
  border-radius: 50%;
  border: 1px dashed rgba(255, 255, 255, 0.18);
  pointer-events: none;
  animation: spinClockwise 45s infinite linear;
}
canvas.sf-planet-canvas {
  width: 100%;
  height: 100%;
  border-radius: 50%;
  display: block;
  filter: drop-shadow(0 4px 18px rgba(0, 0, 0, 0.6));
}

.sf-card-info {
  position: relative;
  z-index: 6;
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  gap: 2px;
  margin-bottom: 2px;
}
.sf-hatch-name {
  font-size: 18.5px;
  font-weight: 700;
  letter-spacing: 0.16em;
  color: #f8fafc;
  line-height: 1.2;
  text-shadow: 0 2px 10px rgba(0, 0, 0, 0.85), 0 0 16px var(--tier-glow, rgba(255, 215, 0, 0.4));
  transition: opacity 0.5s ease;
}
.sf-hatch-meta {
  font-size: 10px;
  letter-spacing: 0.12em;
  color: var(--tier, #ffd700);
  font-weight: 600;
  transition: opacity 0.5s ease;
}
.sf-card-specs {
  font-size: 8.5px;
  letter-spacing: 0.08em;
  color: #cbd5e1;
  font-family: ui-monospace, SFMono-Regular, monospace;
  margin-top: 1px;
  opacity: 0.9;
}
.sf-hatch-hint {
  font-size: 8.5px;
  letter-spacing: 0.16em;
  color: rgba(255, 255, 255, 0.45);
  margin-top: 2px;
}
.sf-hatch-card.revealed .sf-hatch-hint { display: none; }

.sf-card-actions {
  position: absolute;
  bottom: 12px;
  left: 12px;
  right: 12px;
  height: 36px;
  z-index: 30;
  display: flex;
  gap: 6px;
  box-sizing: border-box;
}
.sf-card-act-btn {
  flex: 1;
  padding: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 12px;
  font-size: 10px;
  letter-spacing: 0.06em;
  font-weight: 600;
  cursor: pointer;
  border: 1px solid rgba(255, 255, 255, 0.16);
  background: rgba(15, 23, 42, 0.75);
  backdrop-filter: blur(8px);
  color: #f1f5f9;
  transition: all 0.2s ease;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.35);
}
.sf-card-act-btn:hover { background: rgba(255, 255, 255, 0.15); }
.sf-card-act-btn.primary {
  border-color: var(--tier-border, rgba(212, 175, 55, 0.5));
  background: linear-gradient(135deg, rgba(212, 175, 55, 0.3) 0%, rgba(15, 23, 42, 0.8) 100%);
  color: var(--tier, #ffd700);
}
.sf-card-act-btn:disabled {
  opacity: 0.45;
  cursor: not-allowed;
  filter: grayscale(0.6);
}""".encode('utf-8')

# 6. Update openFor to set all CSS custom properties and handle nextBtn disable state
old_open_for = """    nameEl.textContent = item.name;
    metaEl.textContent = t.cn + ' · ' + (item.minutes || 15) + ' 分钟 · ' + (item.at || '');
    tierBadgeEl.textContent = t.cn + ' · ' + (item.tier ? item.tier.toUpperCase() : 'CELESTIAL');
    tierBadgeEl.style.borderColor = t.color;
    tierBadgeEl.style.color = t.color;

    var list = (window.StarfieldHatch.list) ? window.StarfieldHatch.list() : [];
    var serial = String(list.length || 1).padStart(3, '0');
    serialEl.textContent = 'NO. ' + serial + ' · CELESTIAL';

    planetRenderer.setItem(item);
    updateEscortBtn(window.StarfieldHatch.isEscorted(item.id));

    var nextBtn = card.querySelector('#sf-btn-next-core');
    if (nextBtn) {
      var coresLeft = window.StarfieldHatch.getUnopenedCores();
      nextBtn.textContent = coresLeft > 0 ? `✦ 开启下一颗 (${coresLeft})` : '✦ 暂无更多星核';
    }""".encode('utf-8')

new_open_for = """    card.style.setProperty('--tier-glow', t.glow || 'rgba(212, 175, 55, 0.3)');
    card.style.setProperty('--tier-border', t.border || 'rgba(212, 175, 55, 0.45)');
    card.style.setProperty('--tier-accent', t.accent || t.color);
    card.style.setProperty('--tier-grad', t.grad || 'linear-gradient(150deg, rgba(20, 29, 46, 0.96) 0%, rgba(7, 12, 20, 0.98) 100%)');

    nameEl.textContent = item.name;
    metaEl.textContent = t.cn + ' · ' + (item.minutes || 15) + ' 分钟 · ' + (item.at || '');
    tierBadgeEl.textContent = t.cn + ' · ' + (item.tier ? item.tier.toUpperCase() : 'CELESTIAL');
    tierBadgeEl.style.borderColor = t.border || t.color;
    tierBadgeEl.style.color = t.color;
    tierBadgeEl.style.background = t.badgeBg || 'rgba(255, 255, 255, 0.06)';

    var list = (window.StarfieldHatch.list) ? window.StarfieldHatch.list() : [];
    var serial = String(list.length || 1).padStart(3, '0');
    serialEl.textContent = 'NO. ' + serial + ' · CELESTIAL';

    planetRenderer.setItem(item);
    updateEscortBtn(window.StarfieldHatch.isEscorted(item.id));

    var nextBtn = card.querySelector('#sf-btn-next-core');
    if (nextBtn) {
      var coresLeft = window.StarfieldHatch.getUnopenedCores();
      if (coresLeft > 0) {
        nextBtn.textContent = `✦ 开启下一颗 (${coresLeft})`;
        nextBtn.disabled = false;
        nextBtn.style.opacity = '1';
        nextBtn.style.cursor = 'pointer';
      } else {
        nextBtn.textContent = '✦ 星核已用尽 (0)';
        nextBtn.disabled = true;
        nextBtn.style.opacity = '0.45';
        nextBtn.style.cursor = 'not-allowed';
      }
    }""".encode('utf-8')

# 7. Update back face CSS to be scrollable and reserve bottom clearance
old_back_css = """.sf-hatch-back{position:absolute;inset:0;z-index:15;border-radius:24px;padding:20px 18px 70px 18px;box-sizing:border-box;
 display:flex;flex-direction:column;justify-content:space-between;text-align:left;
 background:radial-gradient(circle at 50% 25%, #162236 0%, #070c14 100%);
 border: 1.5px solid var(--tier, rgba(212, 175, 55, 0.45));
 box-shadow: inset 0 0 40px rgba(0, 0, 0, 0.85), 0 0 30px rgba(0, 0, 0, 0.6);
 opacity:0;transform:rotateY(90deg);transform-origin:50% 50%;pointer-events:none;
 transition:transform .45s cubic-bezier(.2, .8, .2, 1), opacity .35s ease}
.sf-hatch-card.flipped .sf-hatch-back{opacity:1;transform:rotateY(0deg);pointer-events:auto}
.sf-hb-top-seal{display:flex;flex-direction:column;align-items:center;text-align:center;gap:3px;padding-bottom:10px;border-bottom:1px solid rgba(255,255,255,.08)}
.sf-hb-astrolabe-icon{font-size:11px;letter-spacing:.28em;color:var(--tier,#d4af37);opacity:.9;text-shadow:0 0 10px var(--tier,rgba(212,175,55,.5))}
.sf-hb-card-title{font-size:9.5px;font-weight:700;letter-spacing:.18em;color:#f1f5f9;font-family:ui-monospace,monospace}
.sf-hb-card-sub{font-size:8.5px;letter-spacing:.14em;color:#94a3b8;font-family:ui-monospace,monospace}
.sf-hb-telemetry-grid{display:flex;flex-direction:column;gap:6px;margin:6px 0}
.sf-hb-row{display:flex;justify-content:space-between;align-items:center;padding:5px 8px;border-radius:8px;background:rgba(255,255,255,.03);border:1px solid rgba(255,255,255,.05);font-size:10px;letter-spacing:.08em;opacity:.9;line-height:1.4}
.sf-hb-row span{color:#94a3b8;font-weight:400}
.sf-hb-row b{font-weight:500;color:#e2e8f0;text-align:right;font-family:ui-monospace,monospace}
.sf-hb-quote-box{padding:6px 8px;border-radius:8px;background:rgba(212,175,55,.05);border-left:2.5px solid var(--tier,#d4af37)}
.sf-hb-line{font-size:9.5px;line-height:1.5;letter-spacing:.06em;color:rgba(255,255,255,.75)}
.sf-hb-flip-hint{font-size:8.5px;letter-spacing:.14em;text-align:center;color:rgba(255,255,255,.4);margin-top:2px}""".encode('utf-8')

new_back_css = """.sf-hatch-back{position:absolute;inset:0;z-index:15;border-radius:24px;padding:16px 14px 60px 14px;box-sizing:border-box;
 display:flex;flex-direction:column;text-align:left;overflow-y:auto;scrollbar-width:none;
 background:var(--tier-grad, radial-gradient(circle at 50% 25%, #162236 0%, #070c14 100%));
 border: 1.5px solid var(--tier-border, rgba(212, 175, 55, 0.45));
 box-shadow: inset 0 0 40px rgba(0, 0, 0, 0.85), 0 0 30px rgba(0, 0, 0, 0.6);
 opacity:0;transform:rotateY(90deg);transform-origin:50% 50%;pointer-events:none;
 transition:transform .45s cubic-bezier(.2, .8, .2, 1), opacity .35s ease}
.sf-hatch-back::-webkit-scrollbar{display:none}
.sf-hatch-card.flipped .sf-hatch-back{opacity:1;transform:rotateY(0deg);pointer-events:auto}
.sf-hb-top-seal{display:flex;flex-direction:column;align-items:center;text-align:center;gap:2px;padding-bottom:8px;border-bottom:1px solid rgba(255,255,255,.08)}
.sf-hb-astrolabe-icon{font-size:10px;letter-spacing:.26em;color:var(--tier-accent, #d4af37);opacity:.9;text-shadow:0 0 10px var(--tier-glow, rgba(212,175,55,.5))}
.sf-hb-card-title{font-size:9px;font-weight:700;letter-spacing:.16em;color:#f1f5f9;font-family:ui-monospace,monospace}
.sf-hb-card-sub{font-size:8px;letter-spacing:.12em;color:#94a3b8;font-family:ui-monospace,monospace}
.sf-hb-telemetry-grid{display:flex;flex-direction:column;gap:4px;margin:6px 0}
.sf-hb-row{display:flex;justify-content:space-between;align-items:center;padding:4px 8px;border-radius:8px;background:rgba(255,255,255,.03);border:1px solid rgba(255,255,255,.05);font-size:9.5px;letter-spacing:.06em;opacity:.9;line-height:1.35}
.sf-hb-row span{color:#94a3b8;font-weight:400}
.sf-hb-row b{font-weight:500;color:#e2e8f0;text-align:right;font-family:ui-monospace,monospace}
.sf-hb-quote-box{padding:5px 8px;border-radius:8px;background:rgba(255,255,255,.03);border-left:2.5px solid var(--tier-accent, #d4af37);margin:3px 0}
.sf-hb-line{font-size:9px;line-height:1.45;letter-spacing:.05em;color:rgba(255,255,255,.75)}
.sf-hb-flip-hint{font-size:8px;letter-spacing:.12em;text-align:center;color:rgba(255,255,255,.4);margin-top:4px}""".encode('utf-8')

# 8. Update emptyBtn in planetarium list
old_empty_btn = """      var emptyBox = document.createElement('div');
      emptyBox.className = 'sf-hl-empty sf-hl-empty-box';
      emptyBox.innerHTML = `
        <div class="sf-hl-empty-icon">🪐</div>
        <div class="sf-hl-empty-title">星图尚待点亮</div>
        <div class="sf-hl-empty-sub">已为你备妥 3 颗赠送星核，立即孵化你的第一颗深空世界！</div>
        <button class="sf-hl-btn-open pulse" id="sf-hl-empty-open-btn">✦ 开启第 1 颗星球</button>
      `;
      var emptyBtn = emptyBox.querySelector('#sf-hl-empty-open-btn');
      if (emptyBtn) {
        emptyBtn.addEventListener('click', function() {
          if (H && H.openNextCore) {
            root.classList.remove('on');
            H.openNextCore();
          }
        });
      }""".encode('utf-8')

new_empty_btn = """      var emptyBox = document.createElement('div');
      emptyBox.className = 'sf-hl-empty sf-hl-empty-box';
      var curCores = (H && H.getUnopenedCores) ? H.getUnopenedCores() : 0;
      emptyBox.innerHTML = `
        <div class="sf-hl-empty-icon">🪐</div>
        <div class="sf-hl-empty-title">星图尚待点亮</div>
        <div class="sf-hl-empty-sub">${curCores > 0 ? `已为你备妥 ${curCores} 颗赠送星核，立即孵化你的第一颗深空世界！` : '暂无待孵化星核，开启专注远征即可凝聚第一颗深空世界！'}</div>
        <button class="sf-hl-btn-open pulse" id="sf-hl-empty-open-btn">${curCores > 0 ? `✦ 开启第 1 颗星球 (${curCores})` : '✦ 开启专注远征以凝聚星核 ↗'}</button>
      `;
      var emptyBtn = emptyBox.querySelector('#sf-hl-empty-open-btn');
      if (emptyBtn) {
        emptyBtn.addEventListener('click', function() {
          root.classList.remove('on');
          if (curCores > 0) {
            if (H && H.openNextCore) H.openNextCore();
          } else {
            if (window.StarfieldFocus && window.StarfieldFocus.openDashboard) {
              window.StarfieldFocus.openDashboard();
            }
          }
        });
      }""".encode('utf-8')

def apply_patch(data, old, new, name):
    old_crlf = old.replace(b'\r\n', b'\n').replace(b'\n', b'\r\n')
    new_crlf = new.replace(b'\r\n', b'\n').replace(b'\n', b'\r\n')
    if old_crlf not in data:
        raise ValueError(f"Failed to find match for: {name}")
    data = data.replace(old_crlf, new_crlf, 1)
    print(f"Successfully patched: {name}")
    return data

content = apply_patch(content, old_hatch_btn, new_hatch_btn, "1. btnHatchCore")
content = apply_patch(content, old_tiers, new_tiers, "2. TIERS")
content = apply_patch(content, old_open_next, new_open_next, "3. openNextCore")
content = apply_patch(content, old_card_css, new_card_css, "4. card_css")
content = apply_patch(content, old_card_body_css, new_card_body_css, "5. card_body_css")
content = apply_patch(content, old_open_for, new_open_for, "6. openFor")
content = apply_patch(content, old_back_css, new_back_css, "7. back_css")
content = apply_patch(content, old_empty_btn, new_empty_btn, "8. empty_btn")

with open('starfield-pub/starfield.html', 'wb') as f:
    f.write(content)

print("All patches applied to starfield.html successfully!")
