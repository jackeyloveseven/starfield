"""V142: two rare sky events - a gamma-ray burst and an occultation.

Both are observation-only: zero input, no change to the simulation state, and
no new full-screen canvas. They ride the existing depth queue and the existing
post pass.

  * Gamma-ray burst: about one per 200 chunks (hash(chunk, 7001) < 1/200).
    A 0.25-0.4 s full-screen flash, then a very faint afterglow ring that
    fades over 20 s. Duration is hash(SEED, chunk, 7002); no Math.random.
  * Occultation: armed in a chunk that owns a world (about 55% of encounter
    chunks). The pair is taken from the EXISTING world positions and the
    EXISTING bright-star table; the star's brightness dips and recovers over
    4-8 s (hash(chunk, 7102)).

Global kill switch: window.SF_SKY_EVENTS = false. When false no event is
triggered and no pixel is touched, so a frame is identical to the pre-patch
build.

Debug surface for the headless verifier:
  window.sfTriggerGRB([age])   force a burst, returns the flash intensity
  window.sfSkyEventFreeze(age) hold the burst at a given age for a screenshot
  window.sfSkyEventRelease()
  window.__grb                  current flash intensity (0..1)
  window.__grbDuration         duration of the last burst (seconds)
  window.__occ                  current occultation dip (0..1)

Run:  python -I v142_skyevent.py <in.html> <out.html>
"""
import sys

if len(sys.argv) != 3:
    sys.exit("usage: python -I v142_skyevent.py <in.html> <out.html>")

src_p, out_p = sys.argv[1], sys.argv[2]
src = open(src_p, encoding="utf-8", newline="").read()

if "v142-sky-events" in src:
    sys.exit("v142 already present in input")

BLOCK = r"""
/* v142-sky-events ---------------------------------------------------------
 * Two rare, observation-only sky events.
 *
 * Determinism: every choice comes from hash(SEED-derived, chunk, salt), which
 * already mixes SEED in `hash`. No Math.random, no wall-clock. The world and
 * star positions are the ones the page already has (activeMasses / brightStars).
 *
 * Rendering: the afterglow ring is a normal depth-queue item (type 4, far
 * depth) so worlds and stars occlude it; the flash is one additive fillRect on
 * the existing canvas, exactly like gateFlash, and it goes through postPass.
 * No extra canvas, no new layer.
 * ---------------------------------------------------------------------- */
if (typeof window.SF_SKY_EVENTS === 'undefined') window.SF_SKY_EVENTS = true;

let _skyEventsChunk = null, _skyFreeze = false;
let _skyGrbT = -1, _skyGrbDur = 0, _skyGrbDir = null, _skyGrbChunk = 0;
let _skyOccArmed = false, _skyOccChunk = -1, _skyOccStar = null;
let _skyOccT = -1, _skyOccDur = 0, _skyOccDepth = 0;
window.__grb = 0; window.__occ = 0; window.__grbDuration = 0;

function skyEventsOn() { return window.SF_SKY_EVENTS !== false; }

/* Flash: instantaneous rise, decay to zero at the end of the burst. The
 * exponent keeps > 0.5 through the first third of the window. */
function grbFlashAt(t) {
 if (t < 0 || _skyGrbDur <= 0 || t > _skyGrbDur) return 0;
 return Math.pow(1 - t / _skyGrbDur, .5);
}
function grbAfterglowAt() {
 if (_skyGrbT < 0) return 0;
 const a = _skyGrbT - _skyGrbDur;
 if (a < 0 || a > 20) return 0;
 return .16 * Math.pow(1 - a / 20, 1.7);
}
function skyTriggerGRB(age) {
 if (!skyEventsOn()) return 0;
 const k = Math.floor(travel / CHUNK);
 _skyGrbChunk = k;
 const d = .25 + .15 * hash(k, 7002);
 _skyGrbDur = d; window.__grbDuration = Math.round(d * 1e4) / 1e4;
 _skyGrbT = (typeof age === 'number' && isFinite(age)) ? Math.max(0, age) : 0;
 /* Put the ring near where the camera is looking at trigger time, so it is
  * on screen; it is a fixed world direction afterwards. */
 const f = camera.forward, r = camera.right, u = camera.up;
 const ax = (hash(k, 7003) - .5) * 1.1, ay = (hash(k, 7004) - .5) * .7;
 let vx = f[0] + r[0] * ax + u[0] * ay;
 let vy = f[1] + r[1] * ax + u[1] * ay;
 let vz = f[2] + r[2] * ax + u[2] * ay;
 const vl = Math.hypot(vx, vy, vz) || 1;
 _skyGrbDir = [vx / vl, vy / vl, vz / vl];
 window.__grb = grbFlashAt(_skyGrbT);
 return window.__grb;
}
window.sfTriggerGRB = skyTriggerGRB;
window.sfSkyEventFreeze = function (age) {
 if (!skyEventsOn()) return 0;
 if (_skyGrbT < 0) skyTriggerGRB(age);
 else _skyGrbT = Math.max(0, Number(age) || 0);
 _skyFreeze = true;
 window.__grb = grbFlashAt(_skyGrbT);
 window.__occ = _skyOccT >= 0 ? skyOccDip(_skyOccT) : 0;
 return window.__grb;
};
window.sfSkyEventRelease = function () { _skyFreeze = false; };

/* Occultation envelope: 18% ingress, flat, 22% egress. */
function skyOccDip(t) {
 if (_skyOccDur <= 0) return 0;
 const x = clamp(t / _skyOccDur, 0, 1);
 const n = smooth(clamp(x / .18, 0, 1)) * (1 - smooth(clamp((x - .78) / .22, 0, 1)));
 return _skyOccDepth * n;
}
function skyEventStarDim(st) {
 if (!skyEventsOn() || _skyOccT < 0 || st !== _skyOccStar) return 1;
 return 1 - skyOccDip(_skyOccT);
}

/* Pick a bright star that is ALREADY behind a world disk on screen. Both
 * sides come from existing tables/positions; nothing is invented and nothing
 * is moved. lensWarp matches the transform drawSky applies to the star. */
function skyFindOccultation() {
 let best = null, bestScore = 1e9;
 for (const m of activeMasses) {
  if (!m.w || m.kind === 4 || m.isBlackHole) continue;
  const q = project([m.x, m.y, m.z]);
  if (!q) continue;
  const rad = m.r * q[3];
  if (rad < 14) continue;
  if (q[0] < -rad || q[0] > W + rad || q[1] < -rad || q[1] > H + rad) continue;
  for (let i = 0; i < brightStars.length; i++) {
   const st = brightStars[i];
   const s = skyPoint([st.x, st.y, st.z]);
   if (!s) continue;
   const w = lensWarp(s[0], s[1]);
   if (w[0] < -40 || w[0] > W + 40 || w[1] < -40 || w[1] > H + 40) continue;
   const d = Math.hypot(w[0] - q[0], w[1] - q[1]);
   if (d > rad * 1.05) continue;
   const score = d / (rad + 1) / (.6 + st.size * .18);
   if (score < bestScore) { bestScore = score; best = { m, star: st }; }
  }
 }
 return best;
}

function updateSkyEvents(dt) {
 if (!skyEventsOn()) { window.__grb = 0; window.__occ = 0; return; }
 if (_skyFreeze) {
  window.__grb = grbFlashAt(_skyGrbT);
  window.__occ = _skyOccT >= 0 ? skyOccDip(_skyOccT) : 0;
  return;
 }
 if (_skyGrbT >= 0) {
  _skyGrbT += dt;
  window.__grb = grbFlashAt(_skyGrbT);
  if (_skyGrbT > _skyGrbDur + 20.4) { _skyGrbT = -1; window.__grb = 0; }
 }
 const k = Math.floor(travel / CHUNK);
 if (k !== _skyEventsChunk) {
  _skyEventsChunk = k;
  /* One roll per chunk: ~1 burst per 200 chunks. */
  if (started && _skyGrbT < 0 && hash(k, 7001) < .005) skyTriggerGRB(0);
  /* Occultations only where the page already placed a world. */
  let hasWorld = false;
  if (started) {
   const c = chunk(k);
   for (const m of c.masses) if (m.w && m.kind !== 4) { hasWorld = true; break; }
  }
  _skyOccArmed = hasWorld && hash(k, 7101) < .55 && _skyOccT < 0;
  _skyOccChunk = k;
 }
 if (_skyOccArmed) {
  if (k !== _skyOccChunk || !started) _skyOccArmed = false;
  else {
   const pair = skyFindOccultation();
   if (pair) {
    _skyOccStar = pair.star;
    _skyOccDur = 4 + 4 * hash(k, 7102);
    _skyOccDepth = .72 + .22 * hash(k, 7103);
    _skyOccT = 0; _skyOccArmed = false; window.__occ = 0;
   }
  }
 }
 if (_skyOccT >= 0) {
  _skyOccT += dt;
  if (_skyOccT > _skyOccDur) { _skyOccT = -1; window.__occ = 0; }
  else window.__occ = skyOccDip(_skyOccT);
 }
}

/* Depth-queue item: a thin, very faint ring at far depth, so a world in front
 * of it still hides it. Called from drawSky before the sky's own flush. */
function skyEventQueueRing() {
 if (!skyEventsOn()) return;
 const a = grbAfterglowAt();
 if (a <= .0005 || !_skyGrbDir) return;
 const q = skyPoint(_skyGrbDir);
 if (!q) return;
 const x = q[0], y = q[1];
 const R = (camera.focal || 900) * (.085 + .05 * hash(_skyGrbChunk, 7005));
 const grow = 1 + (1 - a / .16) * .14, r = R * grow;
 const w = Math.max(2, r * .075), outer = r + w;
 if (outer < 3) return;
 if (x + outer < -40 || x - outer > W + 40 || y + outer < -40 || y - outer > H + 40) return;
 const aa = a.toFixed(3);
 queue.push({ type: 4, d: 1e6, alpha: 1, fn: () => {
  const g = ctx.createRadialGradient(x, y, 0, x, y, outer);
  g.addColorStop(Math.max(0, (r - w) / outer), 'rgba(140,205,255,0)');
  g.addColorStop(Math.max(0, r / outer), 'rgba(214,240,255,' + aa + ')');
  g.addColorStop(1, 'rgba(140,205,255,0)');
  ctx.save(); ctx.globalCompositeOperation = 'lighter'; ctx.fillStyle = g;
  ctx.beginPath(); ctx.arc(x, y, outer, 0, TAU); ctx.fill(); ctx.restore();
 }});
}

/* The burst itself: one additive full-screen fill on the existing canvas,
 * after the depth queue has been flushed, before the existing post pass. */
function drawSkyEvents() {
 if (!skyEventsOn()) return;
 const I = grbFlashAt(_skyGrbT);
 if (I <= .002) return;
 ctx.save(); ctx.globalCompositeOperation = 'lighter';
 ctx.fillStyle = css([238, 246, 255], .96 * I);
 ctx.fillRect(0, 0, W, H);
 ctx.restore();
 fillPx += W * H;
}
window.__skyEventState = () => ({
 grbT: _skyGrbT, grbDur: _skyGrbDur, flash: window.__grb,
 afterglow: grbAfterglowAt(), occT: _skyOccT, occDur: _skyOccDur, occ: window.__occ,
 chunk: _skyEventsChunk
});
"""

BRIGHT_OLD = """  const tw=.42+.58*Math.sin(time*.5+st.phase)**2,r=st.size*(1+.35*tw);
  const tint=st.warm?[255,236,206]:[226,240,255],gr=ctx.createRadialGradient(x,y,0,x,y,r*11);
  gr.addColorStop(0,css(tint,.95*clamp(dense,0,1.3)));gr.addColorStop(.16,css(tint,.30*dense));gr.addColorStop(1,css(tint,0));"""

BRIGHT_NEW = """  const tw=.42+.58*Math.sin(time*.5+st.phase)**2,r=st.size*(1+.35*tw);
  const _skye=skyEventStarDim(st);
  const tint=st.warm?[255,236,206]:[226,240,255],gr=ctx.createRadialGradient(x,y,0,x,y,r*11);
  gr.addColorStop(0,css(tint,.95*clamp(dense,0,1.3)*_skye));gr.addColorStop(.16,css(tint,.30*dense*_skye));gr.addColorStop(1,css(tint,0));"""

CORE_OLD = "  ctx.fillStyle='rgba(255,255,255,.92)';ctx.beginPath();ctx.arc(x,y,r,0,TAU);ctx.fill();"
CORE_NEW = "  ctx.fillStyle=_skye<.999?css([255,255,255],.92*_skye):'rgba(255,255,255,.92)';ctx.beginPath();ctx.arc(x,y,r,0,TAU);ctx.fill();"

STROKE_OLD = "  ctx.strokeStyle=css(tint,.55);ctx.lineWidth=.7;ctx.beginPath();"
STROKE_NEW = "  ctx.strokeStyle=css(tint,.55*_skye);ctx.lineWidth=.7;ctx.beginPath();"

RING_OLD = " // The faint field, batched: a handful of fills (or strokes) instead of"
RING_NEW = """ skyEventQueueRing();
 // The faint field, batched: a handful of fills (or strokes) instead of"""

FRAME_OLD = " drawSky();deepfield();drawCraftShadows();bodies();drawFleet();drawParticles();flush();"
FRAME_NEW = """ updateSkyEvents(realDt);
 drawSky();deepfield();drawCraftShadows();bodies();drawFleet();drawParticles();flush();drawSkyEvents();"""

SEEK_OLD = """   stepDeparture(step);
   currentPalette=region(routeX(travel),travel);"""
SEEK_NEW = """   stepDeparture(step);
   currentPalette=region(routeX(travel),travel);
   updateSkyEvents(step);"""

ANCHOR_OLD = "window.Starfield=Object.freeze({"
ANCHOR_NEW = BLOCK + "\nwindow.Starfield=Object.freeze({"


def replace_once(text, old, new, label):
    n = text.count(old)
    if n != 1:
        sys.exit(f"{label}: expected count 1, found {n}")
    return text.replace(old, new, 1)


src = replace_once(src, ANCHOR_OLD, ANCHOR_NEW, "event block insert")
src = replace_once(src, BRIGHT_OLD, BRIGHT_NEW, "bright star tint")
src = replace_once(src, CORE_OLD, CORE_NEW, "bright star core")
src = replace_once(src, STROKE_OLD, STROKE_NEW, "bright star cross")
src = replace_once(src, RING_OLD, RING_NEW, "afterglow ring enqueue")
src = replace_once(src, FRAME_OLD, FRAME_NEW, "frame hook")
src = replace_once(src, SEEK_OLD, SEEK_NEW, "seek hook")

open(out_p, "w", encoding="utf-8", newline="").write(src)
print(f"wrote {out_p} ({len(src)} chars)")
