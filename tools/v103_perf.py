"""V103: let the GPU do its job, and trade resolution instead of frames.

Three separate things were capping performance:

1. `getContext('2d', {alpha:false})` without `desynchronized` — the canvas goes
   through an extra composition step every frame. `desynchronized:true` lets the
   compositor take the buffer directly.
2. There was no way back down from a full-resolution canvas. DPR was fixed at
   boot, so a phone that could not fill 1.75x dropped *frames* forever. The
   adaptive block now scales resolution between 1.0x and the profile cap in
   0.15 steps: a slightly soft frame reads far better than a stuttering one.
3. `lowQuality` latched to true after three slow windows and never cleared, so a
   single bad minute permanently thinned the stars. It is now recomputed each
   window (still forced on for coarse pointers, which is deliberate).

The Android side drops `setLayerType(LAYER_TYPE_HARDWARE)`: forcing a hardware
layer on a WebView routes every canvas update through a full-layer re-upload,
which is slower than the default path on most devices.

Run:  python -I v103_perf.py <in.html> <out.html>
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


# 1. direct-to-compositor canvas
rep("ctx = canvas.getContext('2d', {alpha:false});",
    "ctx = canvas.getContext('2d', {alpha:false, desynchronized:true});")

# 2. the scale factor resize() must respect
rep("let toastUntil=0,uiAccumulator=0,wakeLock=null,lowQuality=coarse;",
    "let toastUntil=0,uiAccumulator=0,wakeLock=null,lowQuality=coarse,qualityScale=1;")

rep("""DPR=(window.STARFIELD_QUALITY ? window.STARFIELD_QUALITY.getMaxDPR() : Math.min(devicePixelRatio||1,2)); window.DPR = DPR;""",
    """DPR=Math.max(1,(window.STARFIELD_QUALITY ? window.STARFIELD_QUALITY.getMaxDPR() : Math.min(devicePixelRatio||1,2))*qualityScale); window.DPR = DPR;""")

# 3. adaptive: resolution is the knob, not frames
rep("""if(now-measureStart>3000){fps=framesInWindow*1000/(now-measureStart);framesInWindow=0;measureStart=now;if(fps<25)slowWindows++;else slowWindows=Math.max(0,slowWindows-1);if(slowWindows>2)lowQuality=true;}""",
    """if(now-measureStart>3000){fps=framesInWindow*1000/(now-measureStart);framesInWindow=0;measureStart=now;
  if(fps<30)slowWindows++;else slowWindows=Math.max(0,slowWindows-1);
  // coarse pointers keep the thin detail path; everything else may recover it
  lowQuality=coarse||slowWindows>2;
  // Below 45 fps, buy frames with resolution - the compositor's upscale is much
  // less visible than a stutter. Go back up only after a long clean stretch.
  const cap=window.STARFIELD_QUALITY?window.STARFIELD_QUALITY.getMaxDPR():Math.min(devicePixelRatio||1,2);
  if(fps<45&&qualityScale>.55){qualityScale=Math.max(.55,qualityScale-.15);resize();}
  else if(fps>57&&qualityScale<1&&++fastWindows>4){qualityScale=Math.min(1,qualityScale+.15);fastWindows=0;resize();}
  if(fps<=57)fastWindows=0;
}""")

rep("let lastFillPx=0,fps=60,framesInWindow=0,measureStart=performance.now(),slowWindows=0;",
    "let lastFillPx=0,fps=60,framesInWindow=0,measureStart=performance.now(),slowWindows=0,fastWindows=0;")

open(out_p, "w", encoding="utf-8", newline="").write(src)
print("V103 written:", len(src), "chars")
