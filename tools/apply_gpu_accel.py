# -*- coding: utf-8 -*-
"""
tools/apply_gpu_accel.py
Applies GPU pipeline and WebGL cross-context bridging optimizations:
1. Promote #landscape to independent GPU composited layer with will-change: transform; transform: translateZ(0)
2. Main Canvas 2D context optimization: desynchronized: true, powerPreference: 'high-performance'
3. starfieldGL WebGL context optimization: desynchronized: true, powerPreference: 'high-performance'
4. SFPlanetGL canvas hardware acceleration: will-change: transform, transform: translateZ(0), disable MSAA on mobile
5. LivingPlanetEngine zero-copy WebGL pass-through on mobile: bypass intermediate 2D canvas copy
6. Ensure full-screen grain pattern is bypassed on mobile to save memory bus bandwidth
7. Sync changes to Android assets/starfield.html
"""
import os
import shutil

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HTML_FILE = os.path.join(ROOT, "starfield.html")
ANDROID_HTML = os.path.join(ROOT, "android", "app", "src", "main", "assets", "starfield.html")

def apply_gpu_accel():
    print("Reading starfield.html...")
    with open(HTML_FILE, "r", encoding="utf-8") as f:
        html = f.read()

    # 1. #landscape CSS will-change: transform
    t1 = "#landscape{position:absolute;width:100%;height:100%;inset:0;display:block;cursor:crosshair;touch-action:none;image-rendering:-webkit-optimize-contrast;-webkit-backface-visibility:hidden;backface-visibility:hidden;transform:translateZ(0)}"
    r1 = "#landscape{position:absolute;width:100%;height:100%;inset:0;display:block;cursor:crosshair;touch-action:none;image-rendering:-webkit-optimize-contrast;-webkit-backface-visibility:hidden;backface-visibility:hidden;transform:translateZ(0);will-change:transform}"
    assert t1 in html, "t1 not found"
    html = html.replace(t1, r1)
    print("1. Applied #landscape will-change: transform")

    # 2. Main canvas 2D desynchronized: true & powerPreference: 'high-performance'
    t2 = "const root = $('world'), canvas = $('landscape'), ctx = canvas.getContext('2d', {alpha:false, desynchronized:false});"
    r2 = "const root = $('world'), canvas = $('landscape'), ctx = canvas.getContext('2d', {alpha:false, desynchronized:true, powerPreference:'high-performance'});"
    assert t2 in html, "t2 not found"
    html = html.replace(t2, r2)
    print("2. Applied main canvas desynchronized: true & powerPreference")

    # 3. starfieldGL desynchronized: true & powerPreference
    t3 = """    cv = document.createElement('canvas');
    gl = cv.getContext('webgl2', {
      alpha: true,
      desynchronized: false,
      premultipliedAlpha: true,
      antialias: false,
      powerPreference: 'high-performance'
    }) || cv.getContext('webgl', {
      alpha: true,
      desynchronized: false,
      premultipliedAlpha: true,
      antialias: false
    });"""
    r3 = """    cv = document.createElement('canvas');
    gl = cv.getContext('webgl2', {
      alpha: true,
      desynchronized: true,
      premultipliedAlpha: true,
      antialias: false,
      powerPreference: 'high-performance'
    }) || cv.getContext('webgl', {
      alpha: true,
      desynchronized: true,
      premultipliedAlpha: true,
      antialias: false,
      powerPreference: 'high-performance'
    });"""
    assert t3 in html, "t3 not found"
    html = html.replace(t3, r3)
    print("3. Applied starfieldGL desynchronized: true")

    # 4. grainOn mobile guard
    t4 = " if(!coarse && (window.grainOn !== false)){"
    r4 = " if(!coarse && !_isMobileDevice && (window.grainOn !== false)){"
    assert t4 in html, "t4 not found"
    html = html.replace(t4, r4)
    print("4. Applied grainOn mobile guard")

    # 5. LivingPlanetEngine WebGLRenderer attributes & markers
    t5 = """      const isMob = (typeof window !== 'undefined' && window._isMobileDevice) || (typeof _isMobileDevice !== 'undefined' && _isMobileDevice);
      this.renderer = new THREE.WebGLRenderer({
        canvas: this.canvas,
        alpha: true,
        antialias: !isMob,
        preserveDrawingBuffer: false,
        powerPreference: 'high-performance'
      });"""
    r5 = """      const isMob = (typeof window !== 'undefined' && window._isMobileDevice) || (typeof _isMobileDevice !== 'undefined' && _isMobileDevice);
      this.canvas._isPlanetGLCanvas = true;
      this.canvas._isPlanetModelCanvas = true;
      this.renderer = new THREE.WebGLRenderer({
        canvas: this.canvas,
        alpha: true,
        antialias: !isMob,
        preserveDrawingBuffer: false,
        powerPreference: 'high-performance',
        premultipliedAlpha: true
      });"""
    assert t5 in html, "t5 not found"
    html = html.replace(t5, r5)
    print("5. Applied LivingPlanetEngine WebGLRenderer attributes & markers")

    # 6. LivingPlanetEngine model.canvas creation bypass on mobile
    t6 = """      const sz = 512;
      if (!model.canvas) {
        model.canvas = document.createElement('canvas');
        model.canvas.width = sz;
        model.canvas.height = sz;
        model.ctx = model.canvas.getContext('2d', { alpha: true });
      }"""
    r6 = """      const sz = 512;
      if (!isMob && !model.canvas) {
        model.canvas = document.createElement('canvas');
        model.canvas.width = sz;
        model.canvas.height = sz;
        model.ctx = model.canvas.getContext('2d', { alpha: true });
      }"""
    assert t6 in html, "t6 not found"
    html = html.replace(t6, r6)
    print("6. Applied LivingPlanetEngine model.canvas creation bypass on mobile")

    # 7. LivingPlanetEngine direct WebGL return on mobile (zero copy)
    t7 = """        if (model.canvas && model.ctx) {
          model.ctx.clearRect(0, 0, model.canvas.width, model.canvas.height);
          model.ctx.drawImage(this.canvas, 0, 0);
        }
        if (isMob) {
          return (model.canvas || this.canvas);
        }
      }
      return (model.canvas || this.canvas);"""
    r7 = """        if (isMob) {
          return this.canvas;
        }
        if (model.canvas && model.ctx) {
          model.ctx.clearRect(0, 0, model.canvas.width, model.canvas.height);
          model.ctx.drawImage(this.canvas, 0, 0);
        }
      }
      return isMob ? this.canvas : (model.canvas || this.canvas);"""
    assert t7 in html, "t7 not found"
    html = html.replace(t7, r7)
    print("7. Applied LivingPlanetEngine direct WebGL return on mobile")

    # 8. SFPlanetGL hardware acceleration & mobile MSAA disable
    t8 = """    var c = document.createElement('canvas');
    c.className = 'sf-planet-gl';
    c.style.cssText = 'position:absolute;inset:0;width:100%;height:100%;' +
      'border-radius:50%;pointer-events:none;z-index:2;';
    host.appendChild(c);

    renderer = new THREE.WebGLRenderer({
      canvas: c, antialias: true, alpha: true, powerPreference: 'high-performance'
    });"""
    r8 = """    var c = document.createElement('canvas');
    c.className = 'sf-planet-gl';
    c.style.cssText = 'position:absolute;inset:0;width:100%;height:100%;' +
      'border-radius:50%;pointer-events:none;z-index:2;transform:translateZ(0);will-change:transform;-webkit-backface-visibility:hidden;backface-visibility:hidden;';
    host.appendChild(c);

    var isMob = (typeof window !== 'undefined' && window._isMobileDevice) || (typeof _isMobileDevice !== 'undefined' && _isMobileDevice);
    renderer = new THREE.WebGLRenderer({
      canvas: c, antialias: !isMob, alpha: true, powerPreference: 'high-performance', premultipliedAlpha: true
    });"""
    assert t8 in html, "t8 not found"
    html = html.replace(t8, r8)
    print("8. Applied SFPlanetGL hardware acceleration & mobile MSAA disable")

    print("Writing modified starfield.html...")
    with open(HTML_FILE, "w", encoding="utf-8") as f:
        f.write(html)

    print("Syncing to Android asset starfield.html...")
    shutil.copy2(HTML_FILE, ANDROID_HTML)
    print("Done applying GPU acceleration optimizations!")

if __name__ == '__main__':
    apply_gpu_accel()
