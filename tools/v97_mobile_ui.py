"""V97: the four phone-layout collisions, each measured before it was touched.

uiprobe.py (rects + overlap detection) and mshot.py (true 390x844 pixels) found:

1. #comms-hud is 92vw wide, centred at top --pad+8 = 34px, so it lands directly
   on top of #camera-hud (lens name + flight stats), which occupies y 10..104 at
   x 14..172. The lens name was completely hidden while a comms line played.
2. #poem is max-width 36% with .poem-line{white-space:nowrap}; at 390 px wide the
   block is 140 px and the lines ran 160 px past the right edge (one line ended at
   x = 547).
3. The touch action row (BOOST / 视角 / 专注 / 更多) is anchored bottom-right but
   is ~320 px wide on a 390 px screen; it covers the KM / time row of #journey.
4. #orientation-toggle-btn lives inside #masthead and sat on the title in portrait
   (83 x 23 px of overlap).
5. .destinations is a centred flex item, so its width was max-content and it never
   wrapped: the last chip (事件视界) was clipped by the right edge.

Run:  python -I v97_mobile_ui.py <in.html> <out.html>
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


# ---------------------------------------------------------------- 1 & 3: comms
rep("""  #comms-hud {
    width: 92vw !important;
    left: 50% !important;
    transform: translateX(-50%) !important;""",
    """  #comms-hud {
    width: 92vw !important;
    left: 50% !important;
    /* Below the lens name, not on it: #camera-hud owns y 10..104 and a centred
       92vw card covers all of it on a phone. */
    top: calc(env(safe-area-inset-top, 0px) + 106px) !important;
    transform: translateX(-50%) !important;""")

# ------------------------------------------------- 2, 3, 4, 5: portrait block
rep("""  #camera-hud {
    top: calc(env(safe-area-inset-top, 0px) + 10px) !important;
    left: 14px !important;
  }
}
""",
    """  #camera-hud {
    top: calc(env(safe-area-inset-top, 0px) + 10px) !important;
    left: 14px !important;
  }

  /* A centred flex item in a column becomes max-content wide, so the row never
     wrapped and the last destination sat outside the screen. */
  .destinations {
    width: 100% !important;
    max-width: 100% !important;
  }

  /* The toggle was inside #masthead, on top of the title (83x23 px of overlap).
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
  }

  /* .poem-line is nowrap: at 36% of 390 px the lines ran off the right edge. */
  #poem {
    right: 6% !important;
    max-width: 66vw !important;
  }
  .poem-line {
    white-space: normal !important;
    font-size: 15px !important;
    line-height: 1.85 !important;
  }

  /* The touch action row is ~320 px wide and owns the bottom-right corner. */
  #journey {
    bottom: calc(env(safe-area-inset-bottom, 0px) + 58px) !important;
  }
}
""")

open(out_p, "w", encoding="utf-8", newline="").write(src)
print("V97 written:", len(src), "chars")
