"""Test a candidate fix for the hole sprite: rescale the shadow alpha mask and
the emission-radius mask out of the stale uScale=0.654 units into the current
uScale=27.5 units, then render the sprite over magenta (transparent shows
through) and over navy (to judge the form)."""
import re, os, subprocess, tempfile, sys

SRC = r"C:\Users\machine\Downloads\starfield.html"
CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
HERE = os.path.dirname(os.path.abspath(__file__))

src = open(SRC, encoding="utf-8").read()
shader = re.search(r"const GLSL_HOLE = `(.*?)`;", src, re.S).group(1)

FIXES = [
    # radius = length(p) (p is already the impact parameter in rs; the extra
    # 27.5 was from the reference's unscaled emission.frag p)
    (" float radius=length(p)*27.5;", " float radius=length(p);"),
    # shadow alpha mask, rescaled so its edge sits at CRIT=2.598 instead of 0.0949
    (" float shadow=1.0-smoothstep(0.093,0.102,length(p));",
     " float shadow=1.0-smoothstep(2.55,2.80,length(p));"),
]

def build(sh, clear, out, tag):
    page = """<!doctype html><meta charset=utf-8>
<style>html,body{margin:0;background:#101426}canvas{display:block}</style>
<canvas id=c width=512 height=512></canvas>
<script>
const GLSL_HOLE = `""" + sh + """`;
const cv=document.getElementById('c');
const gl=cv.getContext('webgl2',{alpha:true,antialias:false,depth:false,stencil:false,premultipliedAlpha:true});
const vs=gl.createShader(gl.VERTEX_SHADER);
gl.shaderSource(vs,'#version 300 es\\nvoid main(){vec2 p=vec2((gl_VertexID<<1)&2,gl_VertexID&2);gl_Position=vec4(p*2.0-1.0,0,1);}');
gl.compileShader(vs);
const fs=gl.createShader(gl.FRAGMENT_SHADER);
gl.shaderSource(fs,GLSL_HOLE);gl.compileShader(fs);
if(!gl.getShaderParameter(fs,gl.COMPILE_STATUS)){document.title='SHADER FAIL '+gl.getShaderInfoLog(fs);}
const pr=gl.createProgram();gl.attachShader(pr,vs);gl.attachShader(pr,fs);gl.linkProgram(pr);
gl.useProgram(pr);
const U=n=>gl.getUniformLocation(pr,n);
gl.uniform2f(U('uRes'),512,512);
gl.uniform1f(U('uTilt'),0.34);
gl.uniform1f(U('uIncl'),0.20);
gl.uniform1f(U('uScale'),27.5);
gl.uniform1f(U('uInner'),2.2);
gl.uniform1f(U('uTime'),60);
gl.uniform3f(U('uTint'),255/255,236/255,214/255);
gl.enable(gl.BLEND);gl.blendFunc(gl.ONE,gl.ONE_MINUS_SRC_ALPHA);
gl.viewport(0,0,512,512);
gl.clearColor(""" + clear + """,1);gl.clear(gl.COLOR_BUFFER_BIT);
gl.drawArrays(gl.TRIANGLES,0,3);
if(!document.title)document.title='OK';
</script>"""
    p = os.path.join(HERE, f"holetest_{tag}.html")
    open(p, "w", encoding="utf-8", newline="").write(page)
    base = [CHROME, "--headless=new", "--disable-gpu", "--no-sandbox", "--hide-scrollbars",
            "--no-first-run", "--window-size=512,512"]
    with tempfile.TemporaryDirectory(prefix="ht-") as prof:
        subprocess.run(base + [f"--user-data-dir={prof}", f"--screenshot={out}",
                     "file:///" + p.replace("\\", "/")],
                     capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=120)
        d = subprocess.run(base + [f"--user-data-dir={prof}", "--dump-dom",
                         "file:///" + p.replace("\\", "/")],
                         capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=120)
    mm = re.search(r"<title>(.*?)</title>", d.stdout or "", re.S)
    print(tag, "->", os.path.basename(out), "|", (mm.group(1)[:200] if mm else "NO TITLE"),
          "|", os.path.getsize(out) if os.path.exists(out) else "MISSING")

fixed = shader
for a, b in FIXES:
    assert fixed.count(a) == 1, (a, fixed.count(a))
    fixed = fixed.replace(a, b)
print("fixes applied:", len(FIXES))

# UNfixed, over navy - the current sprite as the scene sees it
build(shader, "0.06,0.08,0.15", os.path.abspath("shots/hole-before-navy.png"), "beforeNavy")
# FIXED, over navy
build(fixed, "0.06,0.08,0.15", os.path.abspath("shots/hole-after-navy.png"), "afterNavy")
# FIXED, over magenta - confirm the shadow is now opaque
build(fixed, "1.0,0.0,1.0", os.path.abspath("shots/hole-after-magenta.png"), "afterMagenta")
