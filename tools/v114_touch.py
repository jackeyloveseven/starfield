"""V114: fast-forward by pressing, and icons without furniture.

Two decisions from play-testing:

  * BOOST was a button for something a thumb already knows how to do. Press and
    hold anywhere that is not a control: after 320 ms the drive goes to 5x, after
    another 850 ms to 15x, and letting go returns to 1x. It reads like holding a
    video to scrub, which is the gesture people already have.
  * the labels were naming icons that already name themselves (an eye, a clock,
    three dots), and the frosted pill around each one was a second frame for no
    reason. Icon only, no background, no border; the tap target stays 44 px.

Run:  python -I v114_touch.py <in.html> <out.html>
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


# --- 1. icons without pills or labels -------------------------------------
rep("""      .sf-touch-btn:active, .sf-touch-btn.active {""",
    """      /* Icon only: the glyph is the label, and the pill was a second frame. */
      .sf-touch-btn {
        background: none !important;
        border: none !important;
        box-shadow: none !important;
        padding: 0 !important;
        width: 46px;
        height: 46px;
      }
      .sf-touch-btn span.label {
        display: none !important;
      }
      .sf-touch-btn .icon-wrap,
      .sf-touch-btn .icon-wrap svg {
        width: 21px !important;
        height: 21px !important;
      }
      /* BOOST is the long press now. */
      .sf-touch-btn.boost {
        display: none !important;
      }
      .sf-touch-btn:active, .sf-touch-btn.active {""")

rep("""      .sf-touch-btn:active, .sf-touch-btn.active {
        transform: scale(0.94);
        background: rgba(255, 255, 255, 0.18) !important;
        border-color: rgba(255, 255, 255, 0.65) !important;
        color: #ffffff;
      }""",
    """      .sf-touch-btn:active, .sf-touch-btn.active {
        transform: scale(0.9);
        background: none !important;
        color: #ffffff;
      }""")

# --- 2. press and hold to fast-forward -------------------------------------
rep("""  // --- Two-Finger Pinch-to-Zoom Handler ---""",
    """  // --- Press and hold to fast-forward ---------------------------------------
  // The same gesture as holding a video: 320 ms to 5x, another 850 ms to 15x,
  // release back to cruise. Anything that is already a control is excluded, so
  // the joystick and the icon row keep their own pointer handling.
  function setupLongPressSpeed() {
    let t1 = 0, t2 = 0, stage = 0;
    const gear = (i) => {
      if (WarpDrive.gearIndex === i) return;
      WarpDrive.gearIndex = i;
      WarpDrive.updateUI();
      toast(i === 0 ? '巡航 1×' : i === 1 ? '跃迁 5×' : '超曲 15×', 1.1);
    };
    const clear = () => { if (t1) clearTimeout(t1); if (t2) clearTimeout(t2); t1 = t2 = 0; };
    const down = (e) => {
      const t = e.target;
      if (t && t.closest && t.closest('button,.sf-touch-joy-zone,.sf-touch-more-tray,#settings-drawer,#codex-modal')) return;
      if (!Engine.isFlightStarted || !Engine.isFlightStarted()) return;
      stage = 0;
      t1 = setTimeout(() => {
        stage = 1; gear(1);
        t2 = setTimeout(() => { stage = 2; gear(2); }, 850);
      }, 320);
    };
    const up = () => { clear(); if (stage > 0) gear(0); stage = 0; };
    window.addEventListener('pointerdown', down, { passive: true });
    window.addEventListener('pointerup', up, { passive: true });
    window.addEventListener('pointercancel', up, { passive: true });
  }

  // --- Two-Finger Pinch-to-Zoom Handler ---""")

rep("""  function createTouchHUD() {
    if (document.getElementById('starfield-touch-overlay')) return;""",
    """  function createTouchHUD() {
    if (document.getElementById('starfield-touch-overlay')) return;
    setupLongPressSpeed();""")

open(out_p, "w", encoding="utf-8", newline="").write(src)
print("V114 written:", len(src), "chars")
