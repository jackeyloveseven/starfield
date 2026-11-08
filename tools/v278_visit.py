
# -*- coding: utf-8 -*-
"""v278 - 卡面加「前往此星」按钮：从收藏直接进入该星地表。"""
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

# 1) 加按钮
rep("""<button class="sf-card-act-btn" id="sf-btn-flip">天文档案</button>""",
    """<button class="sf-card-act-btn" id="sf-btn-flip">天文档案</button>
          <button class="sf-card-act-btn" id="sf-btn-visit">前往此星</button>""",
    'btn')

# 2) 绑定：关闭卡面后进入地表
rep("    escortBtn = card.querySelector('#sf-btn-escort');",
    """    escortBtn = card.querySelector('#sf-btn-escort');

    var visitBtn = card.querySelector('#sf-btn-visit');
    if (visitBtn) {
      visitBtn.addEventListener('click', function (e) {
        e.stopPropagation();
        if (!window.SFSurface || !cur) return;
        var manifId = cur.manif;
        if (!manifId && typeof sfManifFor === 'function') {
          try { manifId = sfManifFor(cur).id; } catch (err) { manifId = null; }
        }
        var opts = { manif: manifId || 'earth_egg', hue: cur.hue || 200, name: cur.name || '未命名星体' };
        hide();
        window.SFSurface.enter(opts);
      });
    }""",
    'bind')

# 3) 引导文案不再是「三个按钮」
rep("\\u4e0b\\u65b9\\u4e09\\u4e2a\\u6309\\u94ae\\u76f4\\u63a5\\u64cd\\u4f5c",
    "\\u4e0b\\u65b9\\u6309\\u94ae\\u76f4\\u63a5\\u64cd\\u4f5c",
    'guide')

HTML.write_text(html, encoding='utf-8', newline='')
sys.stdout.reconfigure(encoding='utf-8')
print('done:', ', '.join(log))
