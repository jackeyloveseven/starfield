"""V139: the touch HUD lays itself out again when the phone is turned.

The joystick base was placed once, when createTouchHUD() ran:

    const defaultX = Math.max(70, window.innerWidth * 0.14);
    const defaultY = window.innerHeight - 100;

`resize()` re-tailed the canvas, the DPR and --pad, but nothing recomputed
those two numbers, so after portrait -> landscape -> portrait the HUD still
carried the viewport it was created in. The base also lived inside
`.sf-touch-joy-zone` (45vw x 55vh, bottom-left), while both the default value
and the pointerdown handler use viewport coordinates (clientX / clientY);
that added the zone's 45%-of-height offset, so the resting base sat at
y = 1073 in a 844-tall portrait screen and at y = 869 in a 390-tall landscape
one, and the knob rendered ~360 px below the finger.

There is a second, louder stale value. resize() pins the stage to the last
measured viewport in pixels:

    root.style.width = W + 'px';
    root.style.height = H + 'px';

On a phone (Chrome mobile / WebView), a stage wider than the screen widens the
layout viewport itself. Rotating 844x390 back to portrait leaves #world at
844 px for the first layout pass, so the browser makes the layout viewport
844x1827 and zooms out to 0.462 - the whole UI shrinks into the left half of
the screen. resize() then reads that expanded innerWidth/innerHeight and pins
#world to 844x1827, so the broken size is now self-sustaining. Reproduced in
mobile emulation on every landscape -> portrait turn; a fresh portrait load is
fine. #world is position:absolute; inset:0, so 100% tracks the viewport and
can never define it.

This patch:

  1. moves the base out of the touch-catch zone and onto the overlay
     (fixed, inset: 0) so left/top really are viewport coordinates;
  2. puts every viewport-derived quantity in layoutTouch(), called at
     creation, on resize, and on orientationchange (with a delayed second
     pass, because Android fires resize before innerWidth flips);
  3. stops resize() from pinning #world to a stale pixel size, so the
     layout viewport cannot be dragged back to the previous orientation;
  4. leaves the joystick gesture, the action cluster and every other HUD
     element alone - they are CSS-driven and already reflow.

  python -I v139_rotate.py <in.html> <out.html>
"""
import sys

if len(sys.argv) != 3:
    sys.exit("usage: python -I v139_rotate.py <in.html> <out.html>")

src_p, out_p = sys.argv[1], sys.argv[2]
b = open(src_p, "rb").read()


def sub(old, new, tag):
    n = b.count(old)
    if n != 1:
        sys.exit("%s: count=%d (want 1)" % (tag, n))
    return b.replace(old, new, 1)


# 1. The base belongs to the viewport, not to the 45vw x 55vh touch zone.
#    Its position now comes from layoutTouch() instead of a one-shot pair of
#    consts captured at creation time.
b = sub(
    b"""    joyBase.appendChild(joyKnob);
    joyContainer.appendChild(joyBase);
    overlay.appendChild(joyContainer);

    // Initial default position for joystick base (resting position)
    const defaultX = Math.max(70, window.innerWidth * 0.14);
    const defaultY = window.innerHeight - 100;
    joyBase.style.left = defaultX + 'px';
    joyBase.style.top = defaultY + 'px';
""",
    b"""    joyBase.appendChild(joyKnob);
    // v139: the base is drawn in viewport coordinates - pointerdown copies
    // clientX/clientY straight into left/top. Nested in the 45vw x 55vh touch
    // zone it inherited that zone's offset (45% of the screen height), which
    // put the resting base below the screen and the knob far below the finger.
    // The zone still catches the gesture; only the artwork moves out.
    overlay.appendChild(joyContainer);
    overlay.appendChild(joyBase);

    layoutTouch();
""",
    "#1 base out of the zone",
)

# 2. One function owns every viewport-derived number in the touch layer, and
#    it is re-run whenever the viewport changes.
b = sub(
    b"""  // --- Build Virtual Touch HUD ---
  function createTouchHUD() {
""",
    b"""  // --- Viewport-dependent touch geometry --------------------------------
  // Anything measured from innerWidth/innerHeight lives here, never in a
  // creation-time const: the phone can be turned while the HUD is mounted.
  function layoutTouch() {
    if (!joyBase || joyActive) return;   // a live drag keeps its own origin
    joyBase.style.left = Math.max(70, window.innerWidth * 0.14) + 'px';
    joyBase.style.top = (window.innerHeight - 100) + 'px';
  }
  window.addEventListener('resize', layoutTouch);
  // Android fires resize before innerWidth has flipped; the delayed pass is
  // the one that lands in the new orientation.
  window.addEventListener('orientationchange', () => {
    layoutTouch();
    setTimeout(layoutTouch, 160);
  });

  // --- Build Virtual Touch HUD ---
  function createTouchHUD() {
""",
    "#2 layoutTouch",
)

# 3. The stage must not define the layout viewport. A px size captured in the
#    old orientation is what turned the phone's layout viewport into 844x1827
#    when it came back to portrait. #world is absolute; inset:0 already.
b = sub(
    b"root.style.width=W+'px';root.style.height=H+'px';",
    b"root.style.width='100%';root.style.height='100%';",
    "#3 world size follows the viewport",
)

open(out_p, "wb").write(b)
print("wrote %s (%d bytes)" % (out_p, len(b)))
