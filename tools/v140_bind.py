"""V140: bind the hatch to the world you actually met.

The hatch used to be pure luck: every roll invented a name and a hue. This
patch makes the encounter feed the hatch instead.

  * When an encounter planet reaches the fleet (the `notifiedSkim` block in
    the low-orbit director) its identity is written to
    localStorage['sf_pending_planet_v1'] as {kind, name, hue, at, travel}.
  * When a space event first enters view (the `ev.notified` block in
    SpaceEventEngine.drawEvent) the same record is written.
  * Only the most recent one is kept; the same kind+name is not rewritten.
  * StarfieldHatch.roll() uses a pending record as identity (name, hue, kind
    in the id), still draws the tier from the probability table, then clears
    the record. With no pending record it falls back to the old random path.

The returned item gains `bound` and `from: {kind, name}` so the card can say
"from the XX you met".

Run:  python -I v140_bind.py <in.html> <out.html>
"""
import sys

if len(sys.argv) != 3:
    sys.exit("usage: python -I v140_bind.py <in.html> <out.html>")

src_p, out_p = sys.argv[1], sys.argv[2]
src = open(src_p, encoding="utf-8", newline="").read()

if "sf-bind-v140" in src:
    sys.exit("v140 already present in input")

HELPER = r"""
<script id="sf-bind-v140">
/* v140: remember the world the player actually met. Additive: one storage
 * record, no rendering and no engine state. */
(function () {
  var KEY = 'sf_pending_planet_v1';
  var EVENT_NAMES = {
    voyager_probe: '旅行者号探测器',
    dimension_foil: '二向箔坍缩点',
    dyson_ring: '戴森环巨构',
    wormhole_sphere: '球形虫洞',
    pillars_of_creation: '创生之柱',
    monolith_artifact: '黑色方尖碑',
    ghost_fleet: '古战场幽灵旗舰',
    asteroid_field: '密集小行星带',
    pulsar: '星际脉冲星',
    comet: '掠日彗星',
    solar_flare: '日冕耀斑',
    derelict: '远古中继信标',
    spatial_anomaly: '时空微裂隙'
  };
  var EVENT_HUES = {
    voyager_probe: 210, dimension_foil: 52, dyson_ring: 45,
    wormhole_sphere: 285, pillars_of_creation: 320, monolith_artifact: 260,
    ghost_fleet: 170, asteroid_field: 35, pulsar: 190, comet: 200,
    solar_flare: 30, derelict: 160, spatial_anomaly: 275
  };

  function hueOfRgb(rgb) {
    var r = Number(rgb[0]) / 255, g = Number(rgb[1]) / 255, b = Number(rgb[2]) / 255;
    var mx = Math.max(r, g, b), mn = Math.min(r, g, b), d = mx - mn, h = 0;
    if (d) {
      if (mx === r) h = ((g - b) / d) % 6;
      else if (mx === g) h = (b - r) / d + 2;
      else h = (r - g) / d + 4;
      h *= 60;
      if (h < 0) h += 360;
    }
    return h;
  }

  function remember(rec) {
    try {
      var kind = String(rec.kind || 'unknown');
      var name = String(rec.name || '');
      if (!name) return null;
      var hue = Number(rec.hue);
      if (!isFinite(hue) && rec.rgb && rec.rgb.length === 3) hue = hueOfRgb(rec.rgb);
      if (!isFinite(hue)) hue = 0;
      hue = ((Math.round(hue) % 360) + 360) % 360;
      var prev = null;
      try { prev = JSON.parse(localStorage.getItem(KEY) || 'null'); } catch (e) {}
      /* Same world seen twice: keep the first sighting, do not rewrite it. */
      if (prev && prev.kind === kind && prev.name === name) return prev;
      var out = {
        kind: kind,
        name: name,
        hue: hue,
        at: String(rec.at || (new Date()).toISOString()),
        travel: (typeof rec.travel === 'number' && isFinite(rec.travel)) ? Math.round(rec.travel) : null
      };
      localStorage.setItem(KEY, JSON.stringify(out));
      return out;
    } catch (e) { return null; }
  }

  window.sfBindRemember = remember;

  window.sfBindPlanet = function (wD, travel) {
    try {
      if (!wD || !wD.type || !wD.type.id) return null;
      var earth = !!(wD.manif && wD.manif.id === 'earth_egg');
      return remember({
        kind: wD.type.id,
        name: earth ? '地球文明彩蛋' : wD.type.name,
        rgb: wD.type.c,
        at: (new Date()).toISOString(),
        travel: travel
      });
    } catch (e) { return null; }
  };

  window.sfBindEvent = function (type, travel) {
    try {
      if (!type) return null;
      var hue = EVENT_HUES[type];
      if (typeof hue !== 'number') {
        var h = 0, s = String(type);
        for (var i = 0; i < s.length; i++) h = (Math.imul(h, 31) + s.charCodeAt(i)) >>> 0;
        hue = h % 360;
      }
      return remember({
        kind: String(type),
        name: EVENT_NAMES[type] || String(type),
        hue: hue,
        at: (new Date()).toISOString(),
        travel: travel
      });
    } catch (e) { return null; }
  };
})();
</script>
"""

PLANET_OLD = """      if (!m.notifiedSkim && Math.abs(dz) < 900) {
        m.notifiedSkim = true;
        const wD = m.w;"""

PLANET_NEW = """      if (!m.notifiedSkim && Math.abs(dz) < 900) {
        m.notifiedSkim = true;
        const wD = m.w;
        // v140: this world is now the identity of the next hatch.
        try { if (window.sfBindPlanet) window.sfBindPlanet(wD, travel); } catch (e) {}"""

EVENT_OLD = """      ev.notified = true;
      if (ev.type === 'voyager_probe')"""

EVENT_NEW = """      ev.notified = true;
      // v140: an event actually seen can seed the next hatch.
      try { if (window.sfBindEvent) window.sfBindEvent(ev.type, travel); } catch (e) {}
      if (ev.type === 'voyager_probe')"""

ROLL_OLD = """    const name = PRE[(u(2) * PRE.length) | 0] + MID[(u(3) * MID.length) | 0] + SUF[(u(4) * SUF.length) | 0];
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
    return item;"""

ROLL_NEW = """    // v140: a pending encounter gives this roll its identity. The tier still
    // comes from the table; only name, hue, id provenance and the bound flag
    // change. With no pending record this is the original random path.
    let pending = null;
    try { pending = JSON.parse(localStorage.getItem('sf_pending_planet_v1') || 'null'); } catch (e) { pending = null; }
    if (!pending || typeof pending !== 'object' || !pending.name) pending = null;
    const bound = !!pending;
    const name = bound ? String(pending.name)
      : PRE[(u(2) * PRE.length) | 0] + MID[(u(3) * MID.length) | 0] + SUF[(u(4) * SUF.length) | 0];
    const kindTag = bound ? (String(pending.kind || 'unknown').replace(/[^a-z0-9]+/gi, '').slice(0, 16) || 'unknown') : '';
    const hue = (bound && isFinite(Number(pending.hue)))
      ? ((Math.round(Number(pending.hue)) % 360) + 360) % 360
      : Math.round(u(5) * 360);
    const item = {
      id: bound ? 'b' + kindTag + '-' + Date.now().toString(36) + idx
                : 'p' + Date.now().toString(36) + idx,
      tier: tier,
      name: name,
      minutes: minutes,
      hue: hue,
      at: new Date().toISOString().slice(0, 10),
      bound: bound,
      from: bound ? { kind: String(pending.kind || 'unknown'), name: String(pending.name) } : null
    };
    list.push(item);
    write(list);
    if (bound) { try { localStorage.removeItem('sf_pending_planet_v1'); } catch (e) {} }
    return item;"""

META = '<meta charset="utf-8">'


def replace_once(text, old, new, label):
    n = text.count(old)
    if n != 1:
        sys.exit(f"{label}: expected count 1, found {n}")
    return text.replace(old, new, 1)


src = replace_once(src, META, META + HELPER, "helper insert")
src = replace_once(src, PLANET_OLD, PLANET_NEW, "planet encounter hook")
src = replace_once(src, EVENT_OLD, EVENT_NEW, "event notified hook")
src = replace_once(src, ROLL_OLD, ROLL_NEW, "roll identity")

open(out_p, "w", encoding="utf-8", newline="").write(src)
print(f"wrote {out_p} ({len(src)} chars)")
