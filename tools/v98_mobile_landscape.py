"""V98: the comms card in landscape.

V97 pushed #comms-hud below #camera-hud on every narrow layout, which fixed the
overlap but left a 92vw x 130px card on a 390px-tall screen: a third of the
height, for one line of narration. Landscape keeps it at the same top edge but
gives it a short page's typography.

It has to sit after the (max-width:900px) block: both rules are !important with
the same specificity, so source order decides.

Run:  python -I v98_mobile_landscape.py <in.html> <out.html>
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


rep("""/* Floating Hot Update (OTA) Pill */""",
    """/* A short screen: the comms card is one line of speech, not a panel. */
@media (max-width: 900px) and (max-height: 580px) {
  #comms-hud {
    width: min(560px, 66vw) !important;
    padding: 8px 14px 9px 14px !important;
  }
  #comms-hud .comms-header {
    margin-bottom: 4px !important;
    font-size: 9.5px !important;
  }
  #comms-hud .comms-body {
    font-size: 12.5px !important;
    line-height: 1.45 !important;
  }
}

/* Floating Hot Update (OTA) Pill */""")

open(out_p, "w", encoding="utf-8", newline="").write(src)
print("V98 written:", len(src), "chars")
