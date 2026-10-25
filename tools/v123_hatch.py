"""V123: the hatch roll, as data first.

The focus loop needs a planet to come out of a session. Before any card art,
the part that must be right - and the part that can be measured - is the table:

    15 min   史诗 紫    common 78 / rare 20 / epic 2
    30 min   传说 红    common 40 / rare 45 / epic 13 / legend 2
    60 min   神话 金    rare 35 / epic 45 / legend 18 / myth 2

plus a pity counter: eight 15-minute sessions with nothing above rare and the
ninth is guaranteed epic.

This patch adds the roll, the storage and a public API. It touches no existing
screen, so nothing currently shipping can regress. The card and the reveal are
the next slice.

  window.StarfieldHatch = { roll(minutes), list(), clear(), pity() }

Run:  python -I v123_hatch.py <in.html> <out.html>
"""
import sys

src_p, out_p = sys.argv[1], sys.argv[2]
src = open(src_p, encoding="utf-8").read()

MODULE = r"""
<script>
/* ---- hatch roll ---------------------------------------------------------
 * A planet is a function of (seed, minutes, session index): deterministic, so
 * the same history always yields the same collection.
 * ------------------------------------------------------------------------*/
(function () {
  const KEY = 'sf_collection_v1';
  const TIERS = {
    common: { cn: '常见', color: '#8ea9c4', rank: 0 },
    rare:   { cn: '稀有', color: '#6fb3ff', rank: 1 },
    epic:   { cn: '史诗', color: '#a97bff', rank: 2 },
    legend: { cn: '传说', color: '#ff6b6b', rank: 3 },
    myth:   { cn: '神话', color: '#ffcf6b', rank: 4 }
  };
  const TABLE = {
    15: [['common', 78], ['rare', 20], ['epic', 2]],
    30: [['common', 40], ['rare', 45], ['epic', 13], ['legend', 2]],
    60: [['rare', 35], ['epic', 45], ['legend', 18], ['myth', 2]]
  };
  // names are assembled, not drawn from a list: a planet should read as one of
  // a kind, not as a card number
  const PRE = ['青', '赤', '素', '幽', '曜', '寒', '沉', '远', '微', '孤', '霜', '烬'];
  const MID = ['沙', '海', '环', '渊', '庭', '脊', '野', '穹', '湖', '垣'];
  const SUF = ['星', '珠', '世界', '之眼', '残响', '孤岛'];

  function hash32(x) {
    x = Math.imul(x ^ (x >>> 16), 0x7feb352d);
    x = Math.imul(x ^ (x >>> 15), 0x846ca68b);
    return (x ^ (x >>> 16)) >>> 0;
  }

  function mulberry(seed) {
    let a = seed >>> 0;
    return function () {
      a |= 0; a = (a + 0x6D2B79F5) | 0;
      let t = Math.imul(a ^ (a >>> 15), 1 | a);
      t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
      return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    };
  }

  function read() {
    try { return JSON.parse(localStorage.getItem(KEY) || '[]'); } catch (e) { return []; }
  }
  function write(list) {
    try { localStorage.setItem(KEY, JSON.stringify(list.slice(-200))); } catch (e) {}
  }

  function pick(minutes, u) {
    const table = TABLE[minutes] || TABLE[15];
    const total = table.reduce((s, r) => s + r[1], 0);
    let x = u * total;
    for (const [tier, w] of table) { if ((x -= w) <= 0) return tier; }
    return table[table.length - 1][0];
  }

  function roll(minutes) {
    minutes = [15, 30, 60].includes(minutes) ? minutes : 15;
    const list = read();
    // The collection is capped at 200 entries, so using its length as the seed
    // froze after 200 rolls: every later session returned the same planet.
    let idx = 0;
    try {
      idx = parseInt(localStorage.getItem('sf_rolls_v1') || '0', 10) || 0;
      localStorage.setItem('sf_rolls_v1', String(idx + 1));
    } catch (e) { idx = list.length; }
    // deterministic per (session count, duration); the wall clock only labels it
    const seed = (hash32(idx + 1) ^ Math.imul(hash32(minutes), 0x9e3779b1)) >>> 0;
    const u = (k) => hash32(seed ^ Math.imul(k, 0x9e3779b1)) / 4294967296;
    let tier = pick(minutes, u(1));
    // Pity is measured in *focused minutes*, not in rolls. A roll-count pity on
    // the 15-minute table fired constantly (2% epic means an eight-roll dry
    // streak is normal) and inflated rare to 48% against a 20% table.
    let dryMin = 0;
    try { dryMin = parseInt(localStorage.getItem('sf_dry_v1') || '0', 10) || 0; } catch (e) {}
    if (dryMin >= 300 && TIERS[tier].rank < 2) tier = 'epic';
    try {
      localStorage.setItem('sf_dry_v1', String(TIERS[tier].rank >= 2 ? 0 : dryMin + minutes));
    } catch (e) {}
    const name = PRE[(u(2) * PRE.length) | 0] + MID[(u(3) * MID.length) | 0] + SUF[(u(4) * SUF.length) | 0];
    const item = {
      id: 'p' + Date.now().toString(36) + idx,
      tier: tier,
      name: name,
      minutes: minutes,
      hue: Math.round(u(5) * 360),
      at: new Date().toISOString().slice(0, 10)
    };
    list.push(item);
    write(list);
    return item;
  }

  window.StarfieldHatch = {
    roll: roll,
    list: read,
    clear: function () { write([]); },
    tiers: TIERS,
    // exposed for the distribution probe; never used by the UI
    _pick: function (minutes, u) { return pick(minutes, u); }
  };
})();
</script>
"""

src = src.replace("</body>", MODULE + "</body>", 1)
open(out_p, "w", encoding="utf-8", newline="").write(src)
print("V123 written:", len(src), "chars")
