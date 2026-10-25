"""V110: three things that were still furniture on a phone.

1. The joystick ring drew at rest. "Zero occlusion" was in the comment but the
   base circle still appeared at its resting position. The ring is now never
   drawn: only a small soft knob follows the thumb, and it fades the moment the
   finger lifts.
2. The orientation toggle sat at the top right of the intro screen and read as a
   random floating pill (it was one). The 更多 tray already carries 横/竖屏, and
   rotating the device works anyway, so the intro button is gone on phones.
3. The codex-unlock toast fired on the title screen, before there is a ship.

Run:  python -I v110_ui2.py <in.html> <out.html>
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


# 1. the ring never shows; only the knob, and only while dragging
rep("""      .sf-touch-joy-base.active {
        opacity: 0.92;
        border-color: rgba(136, 192, 255, 0.75) !important;
      }""",
    """      /* The ring is furniture on an otherwise empty corner: it stays invisible
         even while dragging. The knob is the only feedback. */
      .sf-touch-joy-base.active {
        opacity: 0 !important;
      }
      .sf-touch-joy-knob {
        opacity: 0;
        transition: opacity 0.16s ease;
      }
      .sf-touch-joy-base.active .sf-touch-joy-knob {
        opacity: 0.5 !important;
      }""")

# 2. no floating pill over the title screen
rep("""  /* The toggle was inside #masthead, on top of the title (83x23 px of overlap).
     Fixed puts it under the seed line, clear of everything. */
  #orientation-toggle-btn {
    position: fixed !important;
    top: calc(env(safe-area-inset-top, 0px) + 30px) !important;
    right: 14px !important;
    left: auto !important;
  }
  /* .flying fades #masthead to 0 but leaves it clickable; an invisible button
     over the top-right of the scene would eat taps. */
  .flying #orientation-toggle-btn {
    pointer-events: none !important;
  }""",
    """  /* The 更多 tray carries 横/竖屏, and turning the phone works by itself: on a
     phone this button was only a floating pill over the title. */
  #orientation-toggle-btn {
    display: none !important;
  }""")

# 3. no unlock toast before the flight starts
rep("""body.modal-open #comms-hud {""",
    """body:not(.flying) #toast {
  opacity: 0 !important;
}

body.modal-open #comms-hud {""")

open(out_p, "w", encoding="utf-8", newline="").write(src)
print("V110 written:", len(src), "chars")
