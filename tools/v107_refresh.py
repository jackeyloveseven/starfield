"""V107: the frame ceiling is the panel, not the page.

There is no 60 fps cap in this code: `frame()` is driven by requestAnimationFrame,
which the browser locks to the display's refresh rate. On a 60 Hz panel that is
60; on a 120 Hz phone or a 144/240 Hz monitor it is 120/144/240 - provided a
frame fits in 8.3 / 6.9 / 4.2 ms.

What was wrong is that the adaptive scaler assumed 60. It bought resolution back
whenever the frame rate passed 57, so on a 120 Hz panel a 70 fps result looked
"fine" and the piece never tried for the panel's actual rate. Now the refresh
rate is measured once from the first ~90 frames and the scaler targets it:

    target = clamp(measuredHz * 0.92, 60, 240)

Also reported as `hz` in getState, so it can be verified per device.

Run:  python -I v107_refresh.py <in.html> <out.html>
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


# 1. measure the panel once
rep("let lastFillPx=0,fps=60,framesInWindow=0,measureStart=performance.now(),slowWindows=0,fastWindows=0;",
    """let lastFillPx=0,fps=60,framesInWindow=0,measureStart=performance.now(),slowWindows=0,fastWindows=0;
// The display's refresh, measured from the first clean frames. rAF cannot run
// faster than the panel, so this is the real ceiling - not 60.
let refreshHz=60,hzSamples=[],hzDone=false;""")

rep(""" frameCount++;framesInWindow++;lastFillPx=fillPx;fillPx=0;""",
    """ frameCount++;framesInWindow++;lastFillPx=fillPx;fillPx=0;
 if(!hzDone&&realDt>0.001){
  hzSamples.push(realDt);
  if(hzSamples.length>=90){
   const a=hzSamples.slice(10).sort((x,y)=>x-y),med=a[a.length>>1]||1/60;
   refreshHz=Math.max(60,Math.min(240,Math.round(1/med)));
   hzDone=true;hzSamples=null;
  }
 }""")

# 2. the scaler targets the panel
rep("""  const cap=window.STARFIELD_QUALITY?window.STARFIELD_QUALITY.getMaxDPR():Math.min(devicePixelRatio||1,2);
  if(fps<45&&qualityScale>.55){qualityScale=Math.max(.55,qualityScale-.15);resize();}
  else if(fps>57&&qualityScale<1&&++fastWindows>4){qualityScale=Math.min(1,qualityScale+.15);fastWindows=0;resize();}
  if(fps<=57)fastWindows=0;""",
    """  const cap=window.STARFIELD_QUALITY?window.STARFIELD_QUALITY.getMaxDPR():Math.min(devicePixelRatio||1,2);
  const target=Math.min(240,Math.max(60,refreshHz*0.92));
  if(fps<target*0.75&&qualityScale>.55){qualityScale=Math.max(.55,qualityScale-.15);resize();}
  else if(fps>target*0.95&&qualityScale<1&&++fastWindows>4){qualityScale=Math.min(1,qualityScale+.15);fastWindows=0;resize();}
  if(fps<=target*0.95)fastWindows=0;""")

# 3. expose it
rep("gpu:_GPU.tier,gpuName:String(_GPU.name).slice(0,48),",
    "gpu:_GPU.tier,gpuName:String(_GPU.name).slice(0,48),hz:refreshHz,")

open(out_p, "w", encoding="utf-8", newline="").write(src)
print("V107 written:", len(src), "chars")
