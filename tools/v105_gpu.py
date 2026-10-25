"""V105: one page, four GPUs, four fill-rate budgets.

The same build runs on a Dimensity 9400+ (Mali-G925), on an Intel iGPU driving a
4K panel, on a discrete card, and in software. What differs is not the code path
but how many pixels per frame are sane, so the GPU is detected once and only the
DPR ceiling moves:

    Mali / Adreno / PowerVR / Apple   1.75   (a phone's panel is 3x, not 6x)
    Intel / Iris / Radeon Graphics     1.6   (an iGPU at 4K is fill-rate bound)
    GeForce / Radeon RX / Arc          2.0
    SwiftShader / llvmpipe             1.0

Detection is a hint, so `?gpu=mobile|igpu|dgpu|cpu` overrides it for testing.

The black-hole shader also now asks for `powerPreference:'high-performance'`: on
a hybrid laptop a context created without it may be placed on the integrated
GPU, which is the opposite of what a 5070 Ti is for.

Run:  python -I v105_gpu.py <in.html> <out.html>
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


DETECT = """// --- GPU tier ---------------------------------------------------------------
// Read the renderer string once, at boot, and keep it: the only decision it
// feeds is the DPR ceiling, and a WebGL context just for the string is cheap
// once it is released again.
function _detectGpu(){
 let name='unknown',tier='balanced';
 try{
  const cv=document.createElement('canvas');
  const gl=cv.getContext('webgl2',{powerPreference:'high-performance'})||cv.getContext('webgl');
  if(gl){
   const ext=gl.getExtension('WEBGL_debug_renderer_info');
   if(ext)name=String(gl.getParameter(ext.UNMASKED_RENDERER_WEBGL)||'');
   const lc=gl.getExtension('WEBGL_lose_context');
   if(lc)lc.loseContext();
  }
 }catch(e){}
 const s=name.toLowerCase();
 if(/swiftshader|llvmpipe|software|basic render/.test(s))tier='cpu';
 else if(/mali|adreno|powervr|immortalis|apple gpu/.test(s))tier='mobile';
 else if(/intel|iris|uhd graphics|radeon\\(tm\\) graphics|vega \\d+ graphics/.test(s))tier='igpu';
 else if(/nvidia|geforce|rtx|radeon rx|arc a\\d/.test(s))tier='dgpu';
 // ?gpu= lets a tier be checked without owning the hardware
 const q=/[?&]gpu=(\\w+)/.exec(location.search);
 if(q&&['cpu','mobile','igpu','dgpu','balanced'].includes(q[1]))tier=q[1];
 return {tier:tier,name:name};
}
const _GPU=_detectGpu();
window.STARFIELD_QUALITY = {"""

rep("window.STARFIELD_QUALITY = {", DETECT)

rep("""  getMaxDPR() {
    const raw = window.devicePixelRatio || 1.0;
    if (this.profile === '2k') return Math.min(raw, 3.0);
    if (this.profile === 'balanced') return _isMobileDevice ? Math.min(raw, 1.75) : Math.min(raw, 2.0);
    return Math.min(raw, 1.25);
  },""",
    """  // Fill-rate ceilings by GPU class. A phone panel is 3x, but drawing 6 MP per
  // frame on a Mali is how a 60 fps piece becomes a 30 fps one.
  tierCap: { cpu: 1.0, mobile: 1.75, igpu: 1.6, dgpu: 2.0, balanced: 2.0 },
  getMaxDPR() {
    const raw = window.devicePixelRatio || 1.0;
    const cap = this.tierCap[_GPU.tier] || 2.0;
    if (this.profile === '2k') return Math.min(raw, Math.min(3.0, cap + 0.5));
    if (this.profile === 'balanced') return Math.min(raw, cap);
    return Math.min(raw, 1.25);
  },""")

rep("gl=cv.getContext('webgl2',{alpha:true,antialias:false,premultipliedAlpha:true});",
    "gl=cv.getContext('webgl2',{alpha:true,antialias:false,premultipliedAlpha:true,powerPreference:'high-performance'});")

rep("postMs:+(postMs).toFixed(2),postOn,holeGL:!!holeGL,",
    "postMs:+(postMs).toFixed(2),postOn,holeGL:!!holeGL,gpu:_GPU.tier,gpuName:String(_GPU.name).slice(0,48),dprCap:(window.STARFIELD_QUALITY?STARFIELD_QUALITY.tierCap[_GPU.tier]:null),")

open(out_p, "w", encoding="utf-8", newline="").write(src)
print("V105 written:", len(src), "chars")
