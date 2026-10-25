"""V101: modals are modals, and the codex fits a phone.

Three things the phone screenshots showed:

1. #comms-hud has z-index 1000; the settings sheet has 400. Opening settings left
   the comms card floating over the audio mixer, cutting the section in half.
   Engine.isModalOpen() already knows about photo/codex/settings/focus, so a body
   class is toggled once per frame and the card stands down while any of them is
   open.
2. The codex close button was squeezed into a two-line column ("关" / "闭") because
   the header is flex and the title is long.
3. The four codex tabs and the three footer items wrapped into ragged columns at
   390 px wide.

Run:  python -I v101_modals.py <in.html> <out.html>
"""
import sys

src_p, out_p = sys.argv[1], sys.argv[2]
src = open(src_p, encoding="utf-8").read()


def rep(a, b):
    global src
    n = src.count(a)
    if n != 1:
        sys.exit("count=%d (want 1): %r" % (n, a[:120]))
    src = src.replace(a, b, 1)


# 1. one line in the frame loop, only when the state actually changes
rep(""" if(document.hidden)return;""",
    """ if(document.hidden)return;
 // Any sheet on top of the scene outranks the comms card (z 1000 > 400).
 // NB: the module object is window.Starfield; a bare `Engine` is out of scope
 // here and threw on every frame, which froze the scene.
 {const _S=window.Starfield;const _mo=!!(_S&&_S.isModalOpen&&_S.isModalOpen());
  if(_mo!==__modalOpen){__modalOpen=_mo;document.body.classList.toggle('modal-open',_mo);}}""")

rep("""let lastFillPx=0,fps=60,framesInWindow=0,measureStart=performance.now(),slowWindows=0;""",
    """let lastFillPx=0,fps=60,framesInWindow=0,measureStart=performance.now(),slowWindows=0;
let __modalOpen=false;""")

# 2 & 3. mobile codex layout
rep("""/* Floating Hot Update (OTA) Pill */""",
    """/* The comms card stands down while any sheet is open. */
body.modal-open #comms-hud {
  opacity: 0 !important;
  pointer-events: none !important;
}

/* Codex on a phone: the close button must not wrap, the tabs scroll instead of
   ragging into two lines, and the footer's three items stack. */
@media (max-width: 600px) {
  .codex-close {
    white-space: nowrap !important;
    flex: 0 0 auto !important;
  }
  .codex-tabs {
    flex-wrap: nowrap !important;
    overflow-x: auto !important;
    -webkit-overflow-scrolling: touch;
    gap: 8px !important;
    padding: 0 10px !important;
  }
  /* Measured: the four tabs are 64+64+108+78 = 314 px, so the strip needs
     ~350 px and the 92vw card only offers 331. A little more card, a little
     less type. */
  .codex-container {
    width: 96vw !important;
  }
  .codex-tab {
    white-space: nowrap !important;
    flex: 0 0 auto !important;
    font-size: 11.5px !important;
    padding: 0 1px !important;
  }
  .codex-footer {
    flex-wrap: wrap !important;
    gap: 6px 10px !important;
    padding: 10px 16px !important;
  }
  /* "按下 TAB 或 J 随时呼出" is advice a phone cannot follow. */
  .codex-footer > span:nth-child(2) {
    display: none !important;
  }
}

/* Floating Hot Update (OTA) Pill */""")

open(out_p, "w", encoding="utf-8", newline="").write(src)
print("V101 written:", len(src), "chars")
