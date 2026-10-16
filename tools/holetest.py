"""Render the hole's GLSL sprite standalone, so its form can be judged without
the scene's bloom/post.  Extracts GLSL_HOLE from the artwork and drives it with
the same uniforms drawHole() sets.  Writes holetest.html next to itself and
screenshots it with headless Chrome.
"""
import re, os, subprocess, tempfile, sys

SRC = r"C:\Users\machine\Downloads\starfield.html"
CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
OUT = os.path.abspath("shots/hole-sprite-magenta.png")
HERE = os.path.dirname(os.path.abspath(__file__))

src = open(SRC, encoding="utf-8").read()
m = re.search(r"const GLSL_HOLE = `(.*?)`;", src, re.S)
if not m:
    sys.exit("GLSL_HOLE not found")
shader = m.group(1)
print("shader chars:", len(shader))

page = """<!doctype html><meta charset=utf-8>
<style>html,body{margin:0;background:#101426}canvas{display:block}</style>
<canvas id=c width=512 height=512></canvas>
<script>
const GLSL_HOLE = `""" + shader + """`;
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
gl.clearColor(1.0,0.0,1.0,1);gl.clear(gl.COLOR_BUFFER_BIT);
gl.drawArrays(gl.TRIANGLES,0,3);
if(!document.title)document.title='OK';
</script>"""
out_html = os.path.join(HERE, "holetest.html")
open(out_html, "w", encoding="utf-8", newline="").write(page)

base = [CHROME, "--headless=new", "--disable-gpu", "--no-sandbox", "--hide-scrollbars",
        "--no-first-run", "--window-size=512,512"]
with tempfile.TemporaryDirectory(prefix="ht-") as prof:
    r = subprocess.run(base + [f"--user-data-dir={prof}", f"--screenshot={OUT}",
                               "file:///" + out_html.replace("\\", "/")],
                       capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=120)
    d = subprocess.run(base + [f"--user-data-dir={prof}", "--dump-dom",
                               "file:///" + out_html.replace("\\", "/")],
                       capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=120)
mm = re.search(r"<title>(.*?)</title>", d.stdout or "", re.S)
print("title:", (mm.group(1)[:300] if mm else "NO TITLE"))
print("png:", OUT, os.path.getsize(OUT) if os.path.exists(OUT) else "MISSING")
