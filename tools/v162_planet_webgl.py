
# -*- coding: utf-8 -*-
"""v162 — 开卡星球改 WebGL 实时渲染（噪声大陆 + 硬分色光照 + 大气菲涅尔），
   卡片退成薄层。WebGL 不可用时自动回退 Canvas2D。"""
import sys
from pathlib import Path

HTML = Path(__file__).resolve().parent.parent / 'starfield.html'
with open(HTML, 'r', encoding='utf-8', newline='') as f:
    src = f.read()
nl = '\r\n' if '\r\n' in src[:6000] else '\n'
N = lambda s: s.replace('\r\n', '\n').replace('\n', nl)


# ---- 1. render() 优先交给 GL ----
old_render = N("""    var ctx = this.ctx, w = this.canvas.width, h = this.canvas.height;
    var cx = w * 0.5, cy = h * 0.5, r = w * 0.33;""")
new_render = N("""    if (window.SFPlanetGL && window.SFPlanetGL.frame(this)) return;

    var ctx = this.ctx, w = this.canvas.width, h = this.canvas.height;
    var cx = w * 0.5, cy = h * 0.5, r = w * 0.33;""")
assert src.count(old_render) == 1, 'render anchor'
src = src.replace(old_render, new_render)


GL_JS = N(r"""<script id="sf-planet-gl">
/* v162 · 开卡星球：WebGL 实时渲染。
 * 球面法线 + 三维 fBm 生成大陆，光照做硬分色（不是平滑渐变），
 * 大气用菲涅尔描边。旋转由原有 ProceduralPlanet 的拖拽惯性驱动。
 * WebGL 不可用时 frame() 返回 false，调用方继续走 Canvas2D。 */
(function () {
  if (window.SFPlanetGL) return;

  var VS = [
    'attribute vec2 aPos;',
    'varying vec2 vUv;',
    'void main(){ vUv = aPos * 0.5 + 0.5; gl_Position = vec4(aPos, 0.0, 1.0); }'
  ].join('\n');

  var FS = [
    'precision highp float;',
    'varying vec2 vUv;',
    'uniform vec2  uRes;',
    'uniform float uTime;',
    'uniform vec3  uTint;',
    'uniform vec3  uBase;',
    'uniform vec3  uLand;',
    'uniform float uRotX;',
    'uniform float uRotY;',
    'uniform float uSeed;',
    'uniform float uRing;',
    'uniform float uMoon;',
    '',
    'float hash(vec3 p){',
    '  p = fract(p * 0.3183099 + vec3(0.1, 0.2, 0.3));',
    '  p *= 17.0;',
    '  return fract(p.x * p.y * p.z * (p.x + p.y + p.z));',
    '}',
    'float vnoise(vec3 x){',
    '  vec3 i = floor(x);',
    '  vec3 f = fract(x);',
    '  f = f * f * (3.0 - 2.0 * f);',
    '  float n000 = hash(i);',
    '  float n100 = hash(i + vec3(1.0, 0.0, 0.0));',
    '  float n010 = hash(i + vec3(0.0, 1.0, 0.0));',
    '  float n110 = hash(i + vec3(1.0, 1.0, 0.0));',
    '  float n001 = hash(i + vec3(0.0, 0.0, 1.0));',
    '  float n101 = hash(i + vec3(1.0, 0.0, 1.0));',
    '  float n011 = hash(i + vec3(0.0, 1.0, 1.0));',
    '  float n111 = hash(i + vec3(1.0, 1.0, 1.0));',
    '  return mix(mix(mix(n000, n100, f.x), mix(n010, n110, f.x), f.y),',
    '             mix(mix(n001, n101, f.x), mix(n011, n111, f.x), f.y), f.z);',
    '}',
    'float fbm(vec3 p){',
    '  float a = 0.5, s = 0.0;',
    '  for (int i = 0; i < 5; i++) {',
    '    s += a * vnoise(p);',
    '    p *= 2.03;',
    '    a *= 0.5;',
    '  }',
    '  return s;',
    '}',
    'mat3 rotY(float a){',
    '  float c = cos(a), s = sin(a);',
    '  return mat3(c, 0.0, -s, 0.0, 1.0, 0.0, s, 0.0, c);',
    '}',
    'mat3 rotX(float a){',
    '  float c = cos(a), s = sin(a);',
    '  return mat3(1.0, 0.0, 0.0, 0.0, c, s, 0.0, -s, c);',
    '}',
    '',
    'void main(){',
    '  vec2 p = vUv * 2.0 - 1.0;',
    '  p.x *= uRes.x / uRes.y;',
    '  float R = 0.82;',
    '  float r2 = dot(p, p);',
    '  float R2 = R * R;',
    '',
    '  vec3 col = vec3(0.0);',
    '  float alpha = 0.0;',
    '',
    '  /* ---- ring line, axis-aligned ellipse in screen space ---- */',
    '  float A = 0.384;',
    '  float ca = cos(A), sa = sin(A);',
    '  vec2 q = vec2(p.x * ca + p.y * sa, -p.x * sa + p.y * ca);',
    '  float ringFront = 0.0;',
    '  float ringBack = 0.0;',
    '  if (uRing > 0.5) {',
    '    float e1 = length(vec2(q.x / (R * 1.46), q.y / (R * 0.30))) - 1.0;',
    '    float d1 = abs(e1) * (R * 0.30);',
    '    ringFront += 1.0 - smoothstep(0.0, 0.006, d1);',
    '    if (uRing > 1.5) {',
    '      float e2 = length(vec2(q.x / (R * 1.66), q.y / (R * 0.38))) - 1.0;',
    '      float d2 = abs(e2) * (R * 0.38);',
    '      ringFront += (1.0 - smoothstep(0.0, 0.005, d2)) * 0.55;',
    '    }',
    '  }',
    '  bool front = q.y > 0.0;',
    '  if (!front) ringBack = ringFront; else ringFront = ringFront;',
    '',
    '  /* ---- back half of ring (behind the sphere) ---- */',
    '  if (!front && ringBack > 0.0 && r2 > R2) {',
    '    col = uTint * ringBack * 0.30;',
    '    alpha = max(alpha, ringBack * 0.30);',
    '  }',
    '',
    '  /* ---- sphere ---- */',
    '  if (r2 < R2) {',
    '    vec3 n = vec3(p.x, p.y, sqrt(R2 - r2)) / R;',
    '    vec3 nw = rotX(uRotX) * rotY(uRotY) * n;',
    '',
    '    float f = fbm(nw * 2.35 + uSeed);',
    '    float land = smoothstep(0.495, 0.515, f);',
    '    vec3 albedo = mix(uBase, uLand, land);',
    '',
    '    /* 极冠 */',
    '    float pole = smoothstep(0.86, 0.94, abs(nw.y));',
    '    albedo = mix(albedo, vec3(0.80, 0.85, 0.92), pole * 0.55);',
    '',
    '    vec3 L = normalize(vec3(-0.46, 0.52, 0.72));',
    '    float l = dot(n, L);',
    '    /* 硬分色：三层，不做平滑渐变 */',
    '    float band = l < 0.02 ? 0.16 : (l < 0.42 ? 0.52 : 1.0);',
    '    col = albedo * band;',
    '',
    '    /* 昼面边缘一点点提亮 */',
    '    float edgeLift = smoothstep(0.30, 0.75, l) * 0.10;',
    '    col += uTint * edgeLift;',
    '',
    '    /* 大气菲涅尔 */',
    '    float rim = pow(1.0 - n.z, 3.2);',
    '    col += uTint * rim * 0.55;',
    '',
    '    alpha = 1.0;',
    '  }',
    '',
    '  /* ---- front half of ring ---- */',
    '  if (front && ringFront > 0.0) {',
    '    vec3 rc = uTint * ringFront * 0.85;',
    '    col = mix(col, rc, ringFront * 0.9);',
    '    alpha = max(alpha, ringFront * 0.9);',
    '  }',
    '',
    '  /* ---- moons ---- */',
    '  for (int m = 0; m < 3; m++) {',
    '    if (float(m) >= uMoon) break;',
    '    float ang = uTime * 0.55 + float(m) * 2.1;',
    '    vec2 e = vec2(cos(ang) * R * 1.46, sin(ang) * R * 0.30);',
    '    vec2 mp = vec2(e.x * ca - e.y * sa, e.x * sa + e.y * ca);',
    '    float behind = sin(ang) < 0.0;',
    '    float rad = behind ? 0.022 : 0.036;',
    '    float d = length(p - mp);',
    '    float mAlpha = 1.0 - smoothstep(rad - 0.004, rad, d);',
    '    if (behind > 0.5 && r2 < R2) mAlpha = 0.0;',
    '    if (mAlpha > 0.0) {',
    '      vec3 mc = behind ? uTint * 0.28 : uTint * 1.15;',
    '      col = mix(col, mc, mAlpha);',
    '      alpha = max(alpha, mAlpha);',
    '    }',
    '  }',
    '',
    '  gl_FragColor = vec4(col, alpha);',
    '}'
  ].join('\n');

  var glCanvas = null, gl = null, prog = null, uni = {}, buf = null, ok = false, failed = false;
  var host = null, pp = null;

  function compile(type, srcText) {
    var sh = gl.createShader(type);
    gl.shaderSource(sh, srcText);
    gl.compileShader(sh);
    if (!gl.getShaderParameter(sh, gl.COMPILE_STATUS)) {
      if (window.console) console.warn('[SFPlanetGL] shader', gl.getShaderInfoLog(sh));
      return null;
    }
    return sh;
  }

  function boot(canvas2d) {
    host = canvas2d.parentNode;
    if (!host) return false;
    glCanvas = document.createElement('canvas');
    glCanvas.className = 'sf-planet-gl';
    glCanvas.style.cssText = 'position:absolute;inset:0;width:100%;height:100%;' +
      'border-radius:50%;pointer-events:none;z-index:2;';
    host.appendChild(glCanvas);

    gl = glCanvas.getContext('webgl', {
      alpha: true, premultipliedAlpha: false, antialias: true, depth: false
    }) || glCanvas.getContext('experimental-webgl');
    if (!gl) return false;

    var vs = compile(gl.VERTEX_SHADER, VS);
    var fs = compile(gl.FRAGMENT_SHADER, FS);
    if (!vs || !fs) return false;

    prog = gl.createProgram();
    gl.attachShader(prog, vs);
    gl.attachShader(prog, fs);
    gl.linkProgram(prog);
    if (!gl.getProgramParameter(prog, gl.LINK_STATUS)) return false;
    gl.useProgram(prog);

    buf = gl.createBuffer();
    gl.bindBuffer(gl.ARRAY_BUFFER, buf);
    gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([
      -1, -1, 3, -1, -1, 3
    ]), gl.STATIC_DRAW);
    var loc = gl.getAttribLocation(prog, 'aPos');
    gl.enableVertexAttribArray(loc);
    gl.vertexAttribPointer(loc, 2, gl.FLOAT, false, 0, 0);

    ['uRes', 'uTime', 'uTint', 'uBase', 'uLand', 'uRotX', 'uRotY', 'uSeed', 'uRing', 'uMoon']
      .forEach(function (k) { uni[k] = gl.getUniformLocation(prog, k); });

    gl.enable(gl.BLEND);
    gl.blendFunc(gl.SRC_ALPHA, gl.ONE_MINUS_SRC_ALPHA);
    gl.clearColor(0, 0, 0, 0);
    ok = true;
    return true;
  }

  function hsl(h, s, l) {
    h = ((h % 360) + 360) % 360 / 360;
    var a = s * Math.min(l, 1 - l);
    function f(n) {
      var k = (n + h * 12) % 12;
      return l - a * Math.max(-1, Math.min(Math.min(k - 3, 9 - k), 1));
    }
    return [f(0), f(8), f(4)];
  }

  function sizeOf(canvas2d) {
    var dpr = Math.min(window.devicePixelRatio || 1, 2);
    var box = canvas2d.getBoundingClientRect();
    var w = Math.max(64, Math.round((box.width || 222) * dpr));
    var h = w;
    if (glCanvas.width !== w || glCanvas.height !== h) {
      glCanvas.width = w;
      glCanvas.height = h;
    }
  }

  window.SFPlanetGL = {
    frame: function (planet) {
      if (failed) return false;
      if (!ok) {
        if (!boot(planet.canvas)) { failed = true; return false; }
        pp = planet;
      }
      if (!gl) return false;
      if (gl.isContextLost && gl.isContextLost()) { failed = true; return false; }

      sizeOf(planet.canvas);
      var item = planet.item || {};
      var hue = item.hue || 200;
      var tier = item.tier || 'common';
      var rank = 0;
      var T = (window.StarfieldHatch && window.StarfieldHatch.tiers) || {};
      if (T[tier] && typeof T[tier].rank === 'number') rank = T[tier].rank;

      var base = hsl(hue, 0.30, 0.13);
      var land = hsl(hue, 0.42, 0.27);
      var tint = hsl(hue, 0.62, 0.66);

      gl.viewport(0, 0, glCanvas.width, glCanvas.height);
      gl.clear(gl.COLOR_BUFFER_BIT);
      gl.useProgram(prog);

      gl.uniform2f(uni.uRes, glCanvas.width, glCanvas.height);
      gl.uniform1f(uni.uTime, planet.cloudRot * 12.0);
      gl.uniform3f(uni.uTint, tint[0], tint[1], tint[2]);
      gl.uniform3f(uni.uBase, base[0], base[1], base[2]);
      gl.uniform3f(uni.uLand, land[0], land[1], land[2]);
      gl.uniform1f(uni.uRotX, planet.rotX || 0);
      gl.uniform1f(uni.uRotY, planet.rotY || 0);
      gl.uniform1f(uni.uSeed, (hue % 97) * 0.137);
      gl.uniform1f(uni.uRing, rank >= 1 ? (rank >= 4 ? 2 : 1) : 0);
      gl.uniform1f(uni.uMoon, rank >= 2 ? Math.min(3, rank - 1) : 0);

      gl.drawArrays(gl.TRIANGLES, 0, 3);
      return true;
    },
    isOn: function () { return ok; }
  };
})();
</script>

""")

body = src.rfind('</body>')
assert body > 0
src = src[:body] + GL_JS + src[body:]

with open(HTML, 'w', encoding='utf-8', newline='') as f:
    f.write(src)
sys.stdout.reconfigure(encoding='utf-8')
print('planet GL injected, script chars =', len(GL_JS))
