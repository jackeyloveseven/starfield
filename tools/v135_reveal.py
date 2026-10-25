"""V135: give the hatch reveal a pulse.

The card already changes from silhouette to planet on click. This patch adds
emotion around that one frame, additively:

  * the card lifts and flashes once (120-200ms, scaled by tier rank)
  * legend / myth get one 600ms expanding halo ring
  * a 3-5 note Web Audio arpeggio is synthesised live (no base64, no assets)
    and the context is created/resumed inside the click handler itself
  * prefers-reduced-motion: reduce collapses everything to a 200ms fade

It touches no existing markup or logic: a scoped <style> and a capture-phase
click listener are appended before </body>.

Run:  python -I v135_reveal.py <in.html> <out.html>
"""
import sys

if len(sys.argv) != 3:
    sys.exit("usage: python -I v135_reveal.py <in.html> <out.html>")

src_p, out_p = sys.argv[1], sys.argv[2]
src = open(src_p, encoding="utf-8").read()

if "sf-reveal-css" in src:
    sys.exit("v135 already present in input")

CSS = r"""
<style id="sf-reveal-css">
/* v135: reveal pulse. Scoped to the hatch overlay, appended after its CSS. */
@keyframes sf-reveal-lift {
  0%   { transform: translateY(0) scale(1); filter: brightness(1); }
  42%  { transform: translateY(calc(-1 * var(--sf-lift, 4px))) scale(1.015);
         filter: brightness(var(--sf-flash, 1.5)); }
  100% { transform: translateY(0) scale(1); filter: brightness(1); }
}
@keyframes sf-reveal-fade {
  from { opacity: .55; }
  to   { opacity: 1; }
}
@keyframes sf-halo-ring {
  0%   { opacity: .95; transform: translate(-50%, -50%) scale(.55); }
  65%  { opacity: .45; transform: translate(-50%, -50%) scale(1.55); }
  100% { opacity: 0;   transform: translate(-50%, -50%) scale(2.2); }
}
.sf-hatch-card.revealed {
  animation: sf-reveal-lift var(--sf-flash-dur, 160ms)
             cubic-bezier(.22, 1, .36, 1) both;
}
/* The halo lives on the overlay, not the card: the card clips its children. */
#sf-hatch::after {
  content: ""; position: absolute; left: 50%; top: 50%;
  width: min(300px, 74vw); height: min(300px, 74vw);
  border-radius: 50%; border: 2px solid var(--sf-halo-color, #fff);
  box-shadow: 0 0 26px var(--sf-halo-color, #fff),
              inset 0 0 26px var(--sf-halo-color, #fff);
  transform: translate(-50%, -50%) scale(.55);
  opacity: 0; display: none; pointer-events: none; z-index: -1;
}
#sf-hatch.sf-halo::after {
  display: block;
  animation: sf-halo-ring 600ms cubic-bezier(.16, .84, .44, 1) both;
}
@media (prefers-reduced-motion: reduce) {
  .sf-hatch-card.revealed {
    animation: sf-reveal-fade .2s ease-out both !important;
  }
  .sf-hatch-card.revealed .sf-hatch-orb { transition-duration: .2s !important; }
  .sf-hatch-card.revealed .sf-hatch-name,
  .sf-hatch-card.revealed .sf-hatch-meta {
    transition-duration: .2s !important; transition-delay: 0s !important;
  }
  #sf-hatch.sf-halo::after { display: none !important; animation: none !important; }
}
</style>
"""

JS = r"""
<script id="sf-reveal-js">
/* v135: reveal pulse + live arpeggio. Additive; never touches the card's own
 * reveal logic. The click listener is capture-phase so the audio context is
 * created/resumed synchronously inside the same user gesture, before the
 * existing bubble listener paints the reveal. */
(function () {
  if (window.__sfRevealV135) return;
  window.__sfRevealV135 = true;
  window.__sfRevealSfxFired = false;
  window.__sfRevealSfxState = 'pending';

  var ORDER = ['common', 'rare', 'epic', 'legend', 'myth'];
  /* rank -> flash strength / duration / lift */
  var CFG = [
    { dur: 120, flash: 1.28, lift: 3 },
    { dur: 140, flash: 1.46, lift: 4 },
    { dur: 160, flash: 1.66, lift: 5 },
    { dur: 180, flash: 1.92, lift: 7 },
    { dur: 200, flash: 2.20, lift: 8 }
  ];
  /* 3 / 3 / 4 / 5 / 5 notes, ascending with the tier. */
  var NOTES = {
    common: [523.25, 659.25, 783.99],
    rare:   [587.33, 739.99, 880.00],
    epic:   [523.25, 659.25, 783.99, 1046.50],
    legend: [659.25, 830.61, 987.77, 1318.51, 1661.22],
    myth:   [783.99, 987.77, 1174.66, 1567.98, 1975.53]
  };

  var actx = null;

  function tiers() {
    return (window.StarfieldHatch && window.StarfieldHatch.tiers) || {};
  }

  function tierOf(card) {
    var T = tiers();
    var color = String(card.style.getPropertyValue('--tier') || '')
      .trim().toLowerCase();
    var found = null, k;
    for (k in T) {
      if (T[k] && String(T[k].color || '').toLowerCase() === color) found = k;
    }
    if (found) return found;
    var meta = card.querySelector('.sf-hatch-meta');
    var txt = meta ? String(meta.textContent || '') : '';
    for (k in T) {
      if (!found && T[k] && T[k].cn && txt.indexOf(T[k].cn) >= 0) found = k;
    }
    return found || 'common';
  }

  function rankOf(tier) {
    var T = tiers();
    var r = T[tier] && typeof T[tier].rank === 'number'
      ? T[tier].rank : ORDER.indexOf(tier);
    return Math.max(0, Math.min(4, r | 0));
  }

  /* All failures are swallowed: no output device, blocked autoplay or a
   * context that failed to start must leave the visual reveal untouched. */
  function playArpeggio(tier, rank) {
    window.__sfRevealSfxFired = true;
    window.__sfRevealSfxTier = tier;
    var notes = NOTES[tier] || NOTES.common;
    window.__sfRevealSfxNotes = notes.length;
    try {
      var AC = window.AudioContext || window.webkitAudioContext;
      if (!AC) { window.__sfRevealSfxState = 'unsupported'; return; }
      if (!actx || actx.state === 'closed') actx = new AC();
      if (actx.state === 'suspended' && typeof actx.resume === 'function') {
        try {
          var p = actx.resume();
          if (p && typeof p.then === 'function') {
            p.then(function () {
              window.__sfRevealSfxState = actx ? actx.state : 'gone';
            }, function () {
              window.__sfRevealSfxState = 'resume-blocked';
            });
          }
        } catch (e) { /* blocked: stay silent */ }
      }
      var t0 = actx.currentTime + 0.02;
      var master = actx.createGain();
      master.gain.setValueAtTime(0.14, t0);
      var lp = actx.createBiquadFilter();
      lp.type = 'lowpass';
      lp.frequency.setValueAtTime(5200, t0);
      master.connect(lp);
      lp.connect(actx.destination);

      var step = 0.06;
      var dur = rank >= 3 ? 0.42 : 0.30;
      var type = rank >= 2 ? 'triangle' : 'sine';
      for (var i = 0; i < notes.length; i++) {
        var at = t0 + i * step;
        var osc = actx.createOscillator();
        var g = actx.createGain();
        osc.type = type;
        osc.frequency.setValueAtTime(notes[i], at);
        if (rank >= 3) osc.detune.setValueAtTime(i % 2 ? 5 : -5, at);
        g.gain.setValueAtTime(0.0001, at);
        g.gain.exponentialRampToValueAtTime(0.16, at + 0.012);
        g.gain.exponentialRampToValueAtTime(0.0001, at + dur);
        osc.connect(g);
        g.connect(master);
        osc.start(at);
        osc.stop(at + dur + 0.03);
      }
      window.__sfRevealSfxState = actx.state;
    } catch (e) {
      window.__sfRevealSfxState = 'error';
      window.__sfRevealSfxError = String((e && e.message) || e);
    }
  }

  function onClick(e) {
    var t = e.target;
    var card = t && t.closest ? t.closest('.sf-hatch-card') : null;
    if (!card) return;
    /* Bubble listener has already run on a second click: never double-fire. */
    if (card.classList.contains('revealed')) return;

    var tier = tierOf(card);
    var rank = rankOf(tier);
    var cfg = CFG[rank] || CFG[0];
    card.style.setProperty('--sf-flash-dur', cfg.dur + 'ms');
    card.style.setProperty('--sf-flash', String(cfg.flash));
    card.style.setProperty('--sf-lift', cfg.lift + 'px');

    var root = document.getElementById('sf-hatch');
    if (root) {
      if (rank >= 3) {
        var T = tiers();
        root.style.setProperty('--sf-halo-color',
          (T[tier] && T[tier].color) || '#ffffff');
        root.classList.remove('sf-halo');
        void root.offsetWidth;            /* restart the pseudo animation */
        root.classList.add('sf-halo');
        window.setTimeout(function () {
          if (root.classList.contains('sf-halo')) root.classList.remove('sf-halo');
        }, 720);
      } else {
        root.classList.remove('sf-halo');
      }
    }
    playArpeggio(tier, rank);
  }

  document.addEventListener('click', onClick, true);
})();
</script>
"""

if "</body>" not in src:
    sys.exit("no </body> in input")
out = src.replace("</body>", CSS + JS + "</body>", 1)
open(out_p, "w", encoding="utf-8", newline="").write(out)
print("V135 written:", out_p, len(out), "chars (delta", len(out) - len(src), ")")
