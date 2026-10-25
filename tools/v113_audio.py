"""V113: stop the strings sounding like a suona, and let 更多 wrap.

The classical jukebox is synthesised live, and its "violin" was dual detuned
sawtooths with a +6 dB peaking filter at 2850 Hz (Q 3). That band is exactly the
suona's nasal formant: a buzzy source plus a narrow boost two octaves above the
fundamental is the definition of a Chinese double-reed, not a bowed string.

The fix is subtractive, not a new instrument:

  * the 2850 Hz peak becomes a 3 dB dip - the honk is removed rather than retuned;
  * the lowpass ceiling drops from 4.2 kHz to 2.6 kHz, which takes the sawtooth's
    upper buzz with it;
  * the second saw is quieter and the triangle louder, so the fundamental
    dominates the waveform instead of the edge;
  * the attack lengthens, which is what makes a bow sound bowed.

Second fix: the 更多 tray is five buttons in a row anchored to the right, so on a
narrow screen its leftmost item (图鉴) fell outside the screen and could not be
reached. It now wraps and, under 420 px, drops the labels.

Run:  python -I v113_audio.py <in.html> <out.html>
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


# --- the voice -------------------------------------------------------------
rep("bodyFilter.frequency.setValueAtTime(2850, t0);",
    "bodyFilter.frequency.setValueAtTime(2600, t0);")
rep("bodyFilter.Q.value = 3.0;", "bodyFilter.Q.value = 1.1;")
rep("bodyFilter.gain.setValueAtTime(6.0, t0);",
    "bodyFilter.gain.setValueAtTime(-3.0, t0);")
rep("const maxCut = isSolo ? 4200 : 2200;", "const maxCut = isSolo ? 2600 : 1900;")
rep("g2.gain.value = 0.55;", "g2.gain.value = 0.38;")
rep("g3.gain.value = 0.35;", "g3.gain.value = 0.55;")
rep("const attackTime = isFast ? 0.022 :", "const attackTime = isFast ? 0.045 :")

# --- the tray --------------------------------------------------------------
rep("""      .sf-touch-more-tray {
        display: none;
        align-items: center;
        gap: 6px;""",
    """      .sf-touch-more-tray {
        display: none;
        align-items: center;
        /* Five buttons in one right-anchored row pushed 图鉴 off the left edge
           on a narrow screen, where nothing could reach it. */
        flex-wrap: wrap;
        justify-content: flex-end;
        max-width: calc(100vw - 28px);
        box-sizing: border-box;
        gap: 6px;""")

rep("""      .sf-touch-more-tray.open {
        display: flex;
      }""",
    """      .sf-touch-more-tray.open {
        display: flex;
      }
      @media (max-width: 420px) {
        .sf-touch-more-tray .sf-touch-btn span.label {
          display: none;
        }
      }""")

open(out_p, "w", encoding="utf-8", newline="").write(src)
print("V113 written:", len(src), "chars")
