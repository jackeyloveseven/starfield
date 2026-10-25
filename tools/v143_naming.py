"""V143: give every hatched planet one chance to be named.

The card already has a back face (.sf-hatch-back) and the collection lives in
localStorage['sf_collection_v1']. This patch adds, inside the back face, a
"命名" button that opens an inline input (prompt() is unavailable in some
WebViews). A successful rename writes name + named:true to the stored record,
so the card, the foil serial and the collection page all read the new name
after a reload. Each planet can be renamed once.

Replacements (each asserted to appear exactly once):
  1. cardcraft click handler: taps inside .sf-hb-name-ui must not flip the card.
  2. cardcraft fill(): refresh the naming row whenever the card is refilled.
  3. before </body>: naming CSS + standalone module.

Run:  python -I v143_naming.py <in.html> <out.html>
"""
import sys

if len(sys.argv) != 3:
    sys.exit("usage: python -I v143_naming.py <in.html> <out.html>")

src_p, out_p = sys.argv[1], sys.argv[2]
src = open(src_p, encoding="utf-8", newline="").read()

if "sf-naming-js" in src:
    sys.exit("v143 already present in input")

CLICK_OLD = """    var card=t.closest('.sf-hatch-card');
    if(!card)return;
    if(card.classList.contains('revealed'))card.classList.toggle('flipped');"""

CLICK_NEW = """    var card=t.closest('.sf-hatch-card');
    if(!card)return;
    // v143: the naming controls live on the back face; using them must not flip.
    if(t.closest('.sf-hb-name-ui'))return;
    if(card.classList.contains('revealed'))card.classList.toggle('flipped');"""

FILL_OLD = """    lastId=item.id;
  }"""

FILL_NEW = """    lastId=item.id;
    // v143: refresh the naming row for the card being shown.
    try { if(window.sfNamingSync) window.sfNamingSync(item, card); } catch (e) {}
  }"""

NAMING = r"""
<style id="sf-naming-css">
/* v143: one-shot naming row on the back face. */
.sf-hb-name-ui{margin-top:10px;padding-top:10px;border-top:1px solid rgba(255,255,255,.08);
 display:flex;flex-direction:column;gap:8px;position:relative;z-index:7}
.sf-hb-name-btn{align-self:flex-start;padding:6px 14px;border-radius:14px;cursor:pointer;
 border:1px solid rgba(217,192,138,.55);background:rgba(217,192,138,.10);color:#e8d9b0;
 font-size:10px;letter-spacing:.18em;font-family:inherit}
.sf-hb-name-btn:hover{background:rgba(217,192,138,.18)}
.sf-hb-name-btn:disabled{opacity:.5;cursor:default;background:rgba(255,255,255,.04);
 border-color:rgba(255,255,255,.16);color:#9fb0c2}
.sf-hb-name-form{display:none;flex-direction:column;gap:7px}
.sf-hb-name-form.on{display:flex}
.sf-hb-name-input{width:100%;box-sizing:border-box;padding:7px 9px;border-radius:9px;
 border:1px solid rgba(255,255,255,.18);background:rgba(0,0,0,.35);color:#eef4fa;
 font-size:12px;letter-spacing:.08em;font-family:inherit;outline:none}
.sf-hb-name-input:focus{border-color:rgba(217,192,138,.7)}
.sf-hb-name-acts{display:flex;gap:8px}
.sf-hb-name-acts button{flex:1;padding:6px 0;border-radius:9px;cursor:pointer;
 border:1px solid rgba(255,255,255,.16);background:rgba(255,255,255,.05);color:#dfe9f5;
 font-size:10px;letter-spacing:.14em;font-family:inherit}
.sf-hb-name-ok{border-color:rgba(217,192,138,.5);color:#f0e2bb;background:rgba(217,192,138,.12)}
.sf-hb-name-msg{min-height:12px;font-size:9px;line-height:1.4;letter-spacing:.08em;color:#ff9a8a}
</style>

<script id="sf-naming-js">
/* v143: one rename per planet, persisted in sf_collection_v1. */
(function () {
  var KEY = 'sf_collection_v1';
  var H = window.StarfieldHatch;
  if (!H) return;
  var target = null;               /* item passed to the exported openFor */

  function read() {
    try {
      var a = JSON.parse(localStorage.getItem(KEY) || '[]');
      return Array.isArray(a) ? a : [];
    } catch (e) { return []; }
  }
  function canonical(item) {
    var list = read();
    if (item && item.id) {
      for (var i = list.length - 1; i >= 0; i--) {
        if (list[i] && list[i].id === item.id) return list[i];
      }
    }
    return item || null;
  }
  function charCount(s) {
    return Array.from ? Array.from(s).length : s.length;
  }

  function commit(id, raw) {
    var name = String(raw == null ? '' : raw).trim();
    if (!name) return { ok: false, msg: '名字不能为空' };
    if (charCount(name) < 2) return { ok: false, msg: '至少 2 个字符' };
    if (charCount(name) > 12) return { ok: false, msg: '最多 12 个字符' };
    var list = read(), idx = -1;
    for (var i = list.length - 1; i >= 0; i--) {
      if (list[i] && list[i].id === id) { idx = i; break; }
    }
    if (idx < 0) return { ok: false, msg: '收藏里找不到这颗星球' };
    if (list[idx].named) return { ok: false, msg: '这颗已经命名过了' };
    list[idx].name = name;
    list[idx].named = true;
    try { localStorage.setItem(KEY, JSON.stringify(list)); }
    catch (e) { return { ok: false, msg: '保存失败' }; }
    return { ok: true, item: list[idx] };
  }

  function ensureUI(back) {
    var box = back.querySelector('.sf-hb-name-ui');
    if (box) return box;
    box = document.createElement('div');
    box.className = 'sf-hb-name-ui';
    box.innerHTML =
      '<button type="button" class="sf-hb-name-btn">命名</button>' +
      '<form class="sf-hb-name-form">' +
        '<input type="text" class="sf-hb-name-input" maxlength="12" ' +
          'placeholder="2–12 个字符" autocomplete="off" spellcheck="false">' +
        '<div class="sf-hb-name-acts">' +
          '<button type="submit" class="sf-hb-name-ok">确认</button>' +
          '<button type="button" class="sf-hb-name-cancel">取消</button>' +
        '</div>' +
      '</form>' +
      '<div class="sf-hb-name-msg" role="status"></div>';
    wire(box);
    back.appendChild(box);
    return box;
  }

  function wire(box) {
    var btn = box.querySelector('.sf-hb-name-btn');
    var form = box.querySelector('.sf-hb-name-form');
    var input = box.querySelector('.sf-hb-name-input');
    var msg = box.querySelector('.sf-hb-name-msg');

    btn.addEventListener('click', function (e) {
      e.stopPropagation();
      if (btn.disabled) return;
      form.classList.add('on');
      msg.textContent = '';
      input.value = '';
      try { input.focus(); } catch (err) {}
    });
    box.querySelector('.sf-hb-name-cancel').addEventListener('click', function (e) {
      e.stopPropagation();
      form.classList.remove('on');
      input.value = '';
      msg.textContent = '';
    });
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      e.stopPropagation();
      var res = commit(box.getAttribute('data-id'), input.value);
      if (!res.ok) { msg.textContent = res.msg; return; }
      form.classList.remove('on');
      input.value = '';
      msg.textContent = '';
      apply(box.closest('.sf-hatch-card'), res.item);
      if (window.toast) { try { toast('已命名 · ' + res.item.name, 2); } catch (err) {} }
    });
    /* Keep every tap on the naming row out of the card's flip/reveal handler. */
    box.addEventListener('click', function (e) { e.stopPropagation(); });
  }

  function apply(card, item) {
    if (!card) card = document.querySelector('#sf-hatch .sf-hatch-card');
    if (!card || !item) return;
    var canon = canonical(item) || item;

    var back = card.querySelector('.sf-hatch-back');
    if (back) {
      var box = ensureUI(back);
      box.setAttribute('data-id', canon.id || '');
      var btn = box.querySelector('.sf-hb-name-btn');
      var named = !!canon.named;
      btn.disabled = named;
      btn.textContent = named ? '已命名' : '命名';
      if (named) {
        var form = box.querySelector('.sf-hb-name-form');
        if (form) form.classList.remove('on');
        var msg = box.querySelector('.sf-hb-name-msg');
        if (msg) msg.textContent = '';
      }
    }

    var nameEl = card.querySelector('.sf-hatch-name');
    if (nameEl) nameEl.textContent = canon.name || '';

    var foil = card.querySelector('.sf-foil');
    if (foil) {
      /* cardcraft fills the serial from the list's last item. When an explicit
       * openFor targets an older planet, recompute the serial from that item so
       * the name and the foil never disagree. */
      var list = read(), serial = null;
      if (canon.id) {
        for (var i = list.length - 1; i >= 0; i--) {
          if (list[i] && list[i].id === canon.id) {
            serial = String(i + 1).padStart(3, '0');
            break;
          }
        }
      }
      var tier = (H.tiers && H.tiers[canon.tier]) || null;
      if (serial && tier) {
        foil.textContent = 'NO.' + serial + ' · ' + tier.cn + (canon.named ? ' · 自命名' : '');
      } else {
        var base = String(foil.textContent || '').replace(/\s*·\s*自命名\s*$/, '');
        foil.textContent = base + (canon.named ? ' · 自命名' : '');
      }
    }
  }

  window.sfNamingSync = function (item, card) {
    /* An explicit openFor wins over cardcraft's "last item" fill. */
    apply(card, target || item);
  };

  var openFor = H.openFor;
  if (typeof openFor === 'function') {
    H.openFor = function (item) {
      target = item || null;
      var out = openFor.apply(this, arguments);
      try { window.sfNamingSync(item); } catch (e) {}
      return out;
    };
  }
  var show = H.show;
  if (typeof show === 'function') {
    H.show = function () {
      target = null;
      return show.apply(this, arguments);
    };
  }
})();
</script>
"""


def replace_once(text, old, new, label):
    n = text.count(old)
    if n != 1:
        sys.exit(f"{label}: expected count 1, found {n}")
    return text.replace(old, new, 1)


src = replace_once(src, CLICK_OLD, CLICK_NEW, "cardcraft click guard")
src = replace_once(src, FILL_OLD, FILL_NEW, "cardcraft fill hook")
src = replace_once(src, "</body>", NAMING + "</body>", "naming block insert")

open(out_p, "w", encoding="utf-8", newline="").write(src)
print(f"wrote {out_p} ({len(src)} chars)")
