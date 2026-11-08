
# -*- coding: utf-8 -*-
"""v277 - 地表拖拽转向。"""
import sys
from pathlib import Path

HTML = Path(r'D:\items\code\projects\starfield\starfield-pub\starfield.html')
html = HTML.read_text(encoding='utf-8')
log = []

def rep(old, new, tag):
    global html
    assert html.count(old) == 1, tag + ' count=%d' % html.count(old)
    html = html.replace(old, new)
    log.append(tag)

rep("""titleEl = container.querySelector('#sf-surface-title');""",
    """titleEl = container.querySelector('#sf-surface-title');

    /* 拖拽转向：横向改经度、纵向改纬度。只监听地表 canvas。 */
    boundCv = container.querySelector('#sf-surface-canvas');
    handlers = {
      down: function (e) {
        dragging = true; dragMoved = false;
        dragX = e.clientX; dragY = e.clientY;
        if (boundCv.setPointerCapture) { try { boundCv.setPointerCapture(e.pointerId); } catch (err) {} }
      },
      move: function (e) {
        if (!dragging) return;
        var dx = e.clientX - dragX, dy = e.clientY - dragY;
        dragX = e.clientX; dragY = e.clientY;
        if (Math.abs(dx) + Math.abs(dy) > 2) dragMoved = true;
        userTh -= dx * 0.0045;
        userPhi -= dy * 0.0030;
        if (userPhi < 0.42) userPhi = 0.42;
        if (userPhi > 2.55) userPhi = 2.55;
      },
      up: function () { dragging = false; }
    };
    boundCv.addEventListener('pointerdown', handlers.down);
    boundCv.addEventListener('pointermove', handlers.move);
    boundCv.addEventListener('pointerup', handlers.up);
    boundCv.addEventListener('pointercancel', handlers.up);
    boundCv.style.touchAction = 'none';""",
    'bind')

rep("""    var t = (performance.now() - t0) / 1000;
    var R = planet.cfg.radius;
    var alt = 9.0;
    var th = t * 0.055, ph = 1.12;""",
    """    var t = (performance.now() - t0) / 1000;
    var dt = Math.min(0.05, Math.max(0.001, t - lastT));
    lastT = t;
    var R = planet.cfg.radius;
    var alt = 9.0;
    if (!dragging) autoTh += dt * 0.055;
    var th = autoTh + userTh, ph = userPhi;""",
    'frame')

rep("      active = true;\n      t0 = performance.now();",
    "      active = true;\n      autoTh = 0; userTh = 0; userPhi = 1.12; lastT = 0; dragging = false;\n      t0 = performance.now();",
    'init')

rep("      renderer = null; scene = null; camera = null; planet = null; cityGroup = null;",
    """      if (boundCv && handlers) {
        boundCv.removeEventListener('pointerdown', handlers.down);
        boundCv.removeEventListener('pointermove', handlers.move);
        boundCv.removeEventListener('pointerup', handlers.up);
        boundCv.removeEventListener('pointercancel', handlers.up);
      }
      boundCv = null; handlers = null;
      renderer = null; scene = null; camera = null; planet = null; cityGroup = null;""",
    'unbind')

rep("ESC / L 返回太空 · 拖动改变航向", "拖动转向 · ESC / L 返回太空", 'hint')

HTML.write_text(html, encoding='utf-8', newline='')
sys.stdout.reconfigure(encoding='utf-8')
print('done:', ', '.join(log))
