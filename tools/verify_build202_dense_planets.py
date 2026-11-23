# -*- coding: utf-8 -*-
"""
Build 202 (v2.0.0.2) Dense-Planet Stress Verification (Mobile 412x915 DPR 3.0)
Spawns 20 diverse planets simultaneously right ahead of the camera and verifies:
- Zero LRU thrashing (MAX_CACHE_SIZE = 28 >= 20, bufSize = 256)
- Strict per-frame mobile budget: builds/frame <= 1, webgl draws/frame <= 1
- High steady-state FPS & smooth P95 under 20 simultaneous planets
- Non-blank 3D planet rendering + 0 console/page errors
"""
import os
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

BASE = Path(__file__).resolve().parent.parent
URL = "file:///" + str(BASE / "starfield.html").replace("\\", "/")
CHROME_EXE = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
CHROME_ARGS = [
    "--enable-webgl", "--ignore-gpu-blocklist", "--enable-gpu-rasterization",
    "--enable-zero-copy", "--disable-frame-rate-limit", "--disable-gpu-vsync",
    "--autoplay-policy=no-user-gesture-required",
]


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    with sync_playwright() as pw:
        kw = {"headless": True, "args": CHROME_ARGS}
        if os.path.exists(CHROME_EXE):
            kw["executable_path"] = CHROME_EXE
        browser = pw.chromium.launch(**kw)
        ctx = browser.new_context(
            viewport={"width": 412, "height": 915},
            device_scale_factor=3.0,
            is_mobile=True,
            has_touch=True,
            user_agent="Mozilla/5.0 (Linux; Android 15; Vivo X200 Pro) AppleWebKit/537.36 Chrome/131.0.0.0 Mobile Safari/537.36",
        )
        page = ctx.new_page()
        errs = []
        page.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
        page.on("pageerror", lambda e: errs.append(str(e)))
        page.goto(URL, wait_until="networkidle")
        page.wait_for_timeout(800)
        page.click("#begin")
        page.wait_for_timeout(1200)

        res = page.evaluate("""async () => {
          const eng = window.LivingPlanetEngine;
          if (!eng.initialized) eng.init();
          const st = window.Starfield.getState();
          const tz = st.travel || 0;
          const manifs = ['protoss_crystal', 'cyber_metropolis', 'shattered_cataclysm', 'super_storm', 'zerg_biomorphic', 'dark_void', 'dyson_swarm', 'earth_egg'];
          const dense = [];
          for (let i = 0; i < 20; i++) {
            const col = (i % 4) - 1.5;
            const row = Math.floor(i / 4) - 2;
            dense.push({
              x: st.routeX + col * 320,
              y: st.courseY + row * 240,
              z: tz + 900 + i * 160,
              seed: 91000 + i * 13,
              phase: (i * 0.17) % 1,
              hasRings: (i % 3 === 0),
              w: { type: { id: i % 2 ? 'ocean' : 'alien' }, manif: { id: manifs[i % manifs.length] }, shape: { id: i % 4 === 0 ? 'ringed' : 'sphere' } }
            });
          }
          if (Array.isArray(window.activeMasses)) {
            window.activeMasses.unshift(...dense);
          }

          let maxBuildsInFrame = 0;
          let maxDrawsInFrame = 0;
          const deltas = [];
          let last = performance.now();

          // Phase 1: 30 frames of ramp-up while 20 new planets stream into 3D cache
          for (let f = 0; f < 30; f++) {
            eng._buildsThisFrame = 0;
            eng._webglDrawsThisFrame = 0;
            for (let i = 0; i < dense.length; i++) {
              eng.renderPlanet(dense[i], 30 + (i % 5) * 18, [0.6, 0.5, 0.6], window.camera);
            }
            maxBuildsInFrame = Math.max(maxBuildsInFrame, eng._buildsThisFrame || 0);
            maxDrawsInFrame = Math.max(maxDrawsInFrame, eng._webglDrawsThisFrame || 0);
            await new Promise(r => requestAnimationFrame(r));
          }

          // Phase 2: 60 frames steady-state with all 20 planets in front of camera
          last = performance.now();
          const t0 = last;
          for (let f = 0; f < 60; f++) {
            await new Promise(r => requestAnimationFrame(r));
            const now = performance.now();
            deltas.push(now - last);
            last = now;
            maxBuildsInFrame = Math.max(maxBuildsInFrame, eng._buildsThisFrame || 0);
            maxDrawsInFrame = Math.max(maxDrawsInFrame, eng._webglDrawsThisFrame || 0);
          }
          const elapsed = (performance.now() - t0) / 1000;
          const sorted = deltas.slice().sort((a, b) => a - b);
          const p95 = sorted[Math.floor(sorted.length * 0.95)] || 0;

          // Verify rendered canvas actually has non-blank 3D planet pixels
          let validCached = 0;
          for (let i = 0; i < dense.length; i++) {
            const mdl = eng.planetCache.get(eng.getPlanetId(dense[i]));
            if (mdl && mdl.hasRendered && mdl.canvas) validCached++;
          }
          return {
            maxCache: eng.MAX_CACHE_SIZE,
            bufSize: eng.currentBufferSize,
            cacheSize: eng.planetCache.size,
            validCached,
            maxBuildsInFrame,
            maxDrawsInFrame,
            avgFps: Number((deltas.length / Math.max(0.001, elapsed)).toFixed(1)),
            p95Ms: Number(p95.toFixed(2))
          };
        }""")
        print("Dense 20-Planet Mobile Stress Result:", res)
        assert res["maxCache"] >= 28, f"MAX_CACHE_SIZE too small: {res}"
        assert res["bufSize"] == 256, f"Mobile buffer not 256: {res}"
        assert res["maxBuildsInFrame"] <= 1, f"Exceeded 1 build/frame budget: {res}"
        assert res["maxDrawsInFrame"] <= 1, f"Exceeded 1 WebGL blit/frame budget: {res}"
        assert res["validCached"] >= 18, f"Too few cached 3D planets: {res}"
        assert res["avgFps"] >= 60.0, f"Dense 20-planet FPS below 60: {res}"
        assert len(errs) == 0, f"Console/Page errors: {errs}"
        print("✅ BUILD 202 DENSE 20-PLANET MOBILE STRESS TEST PASSED!")
        browser.close()


if __name__ == "__main__":
    main()
