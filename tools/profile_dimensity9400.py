# tools/profile_dimensity9400.py
import os
import sys
import time
import json
import statistics
from playwright.sync_api import sync_playwright

if sys.stdout.encoding.lower() != 'utf-8':
    try: sys.stdout.reconfigure(encoding='utf-8')
    except Exception: pass

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
HTML_FILE = os.path.join(BASE_DIR, 'starfield.html')
ARTIFACT_DIR = os.path.join(BASE_DIR, 'tools', 'artifacts')
os.makedirs(ARTIFACT_DIR, exist_ok=True)
CHROME_PATH = r'C:\Program Files\Google\Chrome\Application\chrome.exe'

print("======================================================================")
print(" DIMENSITY 9400+ (天玑 9400+) FLAGSHIP MOBILE PROFILING SUITE")
print(" Hardware Target: 2800x1260 120Hz LTPO OLED, DPR 3.0, Immortalis-G925")
print("======================================================================")

INIT_INSTRUMENTATION = '''
window.__profiler = {
    active: false,
    currentScenario: 'idle',
    metrics: {},
    frameHistory: [],
    scenarioResults: {}
};

function resetMetrics() {
    return {
        frameCount: 0,
        totalFrameMs: 0,
        frameTimes: [],
        
        // Stage Timings (ms)
        skyGradFillMs: 0,
        starGLRenderMs: 0,
        starGLDrawImageMs: 0,
        starCPUMs: 0,
        milkyWayStrokesMs: 0,
        planetLPRenderMs: 0,
        planetModelCopyMs: 0,
        planetCompositeDrawMs: 0,
        grainPatternFillMs: 0,
        vignetteFillMs: 0,
        bloomDrawMs: 0,
        nebulaAndSpritesDrawMs: 0,
        fleetAndShadowsMs: 0,
        otherStrokesMs: 0,
        otherDrawImageMs: 0,
        otherFillRectMs: 0,
        
        // Operation Counts & Pixels
        starGLDrawCalls: 0,
        planetDrawCalls: 0,
        grainFillCalls: 0,
        vignetteFillCalls: 0,
        bloomDrawCalls: 0,
        otherDrawCalls: 0,
        
        // Memory & GC
        heapBeforeFirst: 0,
        heapAfterLast: 0,
        heapAllocTotalBytes: 0,
        minorGCCount: 0,
        gcSpikeFrames: 0,
        gcPausesTotalMs: 0,
        maxFrameTimeMs: 0
    };
}
window.resetMetrics = resetMetrics;

window.__profiler.metrics = resetMetrics();

// 1. Hook Canvas2D DrawImage
const origDrawImage = CanvasRenderingContext2D.prototype.drawImage;
CanvasRenderingContext2D.prototype.drawImage = function(img, ...args) {
    if (!window.__profiler.active) return origDrawImage.apply(this, [img, ...args]);
    
    const t0 = performance.now();
    const res = origDrawImage.apply(this, [img, ...args]);
    const dt = performance.now() - t0;
    const m = window.__profiler.metrics;
    
    if (window._sfStarGL && img === window._sfStarGL.cv) {
        m.starGLDrawImageMs += dt;
        m.starGLDrawCalls++;
    } else if (img && img._isPlanetModelCanvas) {
        m.planetCompositeDrawMs += dt;
        m.planetDrawCalls++;
    } else if (img && img._isPlanetGLCanvas) {
        m.planetModelCopyMs += dt;
    } else if (img && (img._isBloomCanvas || img.id === 'landscape' || (window.canvas && img === window.canvas))) {
        m.bloomDrawMs += dt;
        m.bloomDrawCalls++;
    } else {
        m.nebulaAndSpritesDrawMs += dt;
        m.otherDrawCalls++;
    }
    return res;
};

// 2. Hook Canvas2D FillRect
const origFillRect = CanvasRenderingContext2D.prototype.fillRect;
CanvasRenderingContext2D.prototype.fillRect = function(x, y, w, h) {
    if (!window.__profiler.active) return origFillRect.apply(this, [x, y, w, h]);
    
    const t0 = performance.now();
    const res = origFillRect.apply(this, [x, y, w, h]);
    const dt = performance.now() - t0;
    const m = window.__profiler.metrics;
    
    if (this.fillStyle === window._sfSkyGrad) {
        m.skyGradFillMs += dt;
    } else if (this.fillStyle === window._sfCachedVigGrad) {
        m.vignetteFillMs += dt;
        m.vignetteFillCalls++;
    } else if (this.fillStyle instanceof CanvasPattern || (typeof grainPattern !== 'undefined' && this.fillStyle === grainPattern)) {
        m.grainPatternFillMs += dt;
        m.grainFillCalls++;
    } else {
        m.otherFillRectMs += dt;
    }
    return res;
};

// 3. Hook Canvas2D Stroke
const origStroke = CanvasRenderingContext2D.prototype.stroke;
CanvasRenderingContext2D.prototype.stroke = function() {
    if (!window.__profiler.active) return origStroke.apply(this, arguments);
    
    const t0 = performance.now();
    const res = origStroke.apply(this, arguments);
    const dt = performance.now() - t0;
    const m = window.__profiler.metrics;
    
    if (window._isDrawingMilkyWay) {
        m.milkyWayStrokesMs += dt;
    } else {
        m.otherStrokesMs += dt;
    }
    return res;
};

// 4. Hook Non-Recursive RequestAnimationFrame
const origRAF = window.requestAnimationFrame;
let mainFrameWrapper = null;

window.requestAnimationFrame = function(callback) {
    if (!mainFrameWrapper) {
        mainFrameWrapper = function(now) {
            const p = window.__profiler;
            if (!p.active) {
                callback(now);
                return;
            }
            
            const memBefore = (performance.memory) ? performance.memory.usedJSHeapSize : 0;
            const t0 = performance.now();
            
            callback(now);
            
            const frameDur = performance.now() - t0;
            const memAfter = (performance.memory) ? performance.memory.usedJSHeapSize : 0;
            
            const m = p.metrics;
            m.frameCount++;
            m.totalFrameMs += frameDur;
            m.frameTimes.push(frameDur);
            if (frameDur > m.maxFrameTimeMs) m.maxFrameTimeMs = frameDur;
            
            const memDelta = memAfter - memBefore;
            if (memDelta > 0) {
                m.heapAllocTotalBytes += memDelta;
            } else if (memDelta < -100000) {
                // GC occurred during this frame
                m.minorGCCount++;
                m.gcPausesTotalMs += frameDur;
                if (frameDur > 16.6) m.gcSpikeFrames++;
            }
        };
        return origRAF.call(window, mainFrameWrapper);
    }
    return origRAF.call(window, mainFrameWrapper);
};
'''

POST_INIT_HOOKS = '''
(() => {
    // 1. Hook StarfieldGL Render
    if (window._sfStarGL) {
        const origRender = window._sfStarGL.render;
        window._sfStarGL.render = function() {
            if (!window.__profiler.active) return origRender.apply(this, arguments);
            const t0 = performance.now();
            const res = origRender.apply(this, arguments);
            const dt = performance.now() - t0;
            window.__profiler.metrics.starGLRenderMs += dt;
            return res;
        };
    }
    
    // 2. Hook LivingPlanetEngine Render & Tag Canvas
    if (window.LivingPlanetEngine) {
        const origRenderPlanet = window.LivingPlanetEngine.renderPlanet;
        window.LivingPlanetEngine.renderPlanet = function(m, rad, lightDir, cam) {
            if (!window.__profiler.active) return origRenderPlanet.apply(this, arguments);
            const t0 = performance.now();
            const res = origRenderPlanet.apply(this, arguments);
            const dt = performance.now() - t0;
            window.__profiler.metrics.planetLPRenderMs += dt;
            if (res) {
                res._isPlanetModelCanvas = true;
            }
            if (this.canvas) {
                this.canvas._isPlanetGLCanvas = true;
            }
            return res;
        };
    }
    
    // 3. Mark Bloom Canvas
    if (typeof bloom !== 'undefined') {
        bloom._isBloomCanvas = true;
    }
    
    // Control API
    window.startProfiling = function(scenarioName) {
        window.__profiler.currentScenario = scenarioName;
        window.__profiler.metrics = window.resetMetrics();
        if (performance.memory) {
            window.__profiler.metrics.heapBeforeFirst = performance.memory.usedJSHeapSize;
        }
        window.__profiler.active = true;
    };
    
    window.stopProfiling = function() {
        window.__profiler.active = false;
        if (performance.memory) {
            window.__profiler.metrics.heapAfterLast = performance.memory.usedJSHeapSize;
        }
        const m = window.__profiler.metrics;
        const name = window.__profiler.currentScenario;
        window.__profiler.scenarioResults[name] = Object.assign({}, m);
        return m;
    };
})();
'''

def run_profiling():
    file_url = 'file:///' + HTML_FILE.replace('\\', '/')
    results = {}
    
    with sync_playwright() as p:
        browser = p.chromium.launch(
            channel='chrome',
            headless=True,
            args=[
                '--enable-webgl',
                '--no-sandbox',
                '--js-flags=--expose-gc',
                '--enable-precise-memory-info',
                '--disable-gpu-throttling'
            ]
        )
        
        # Test Profiles Matrix
        configs = [
            {
                'id': 'mobile_balanced',
                'name': '天玑 9400+ 极速高刷模式 (Mobile Balanced)',
                'profile': 'balanced',
                'forceDPR': None,
                'viewport': {'width': 412, 'height': 915},
                'is_portrait': True
            },
            {
                'id': 'mobile_2k',
                'name': '天玑 9400+ 2K 极清模式 (Mobile 2K Retina)',
                'profile': '2k',
                'forceDPR': None,
                'viewport': {'width': 412, 'height': 915},
                'is_portrait': True
            },
            {
                'id': 'mobile_native_3k_portrait',
                'name': '天玑 9400+ 原生满血竖屏 (Physical 1236x2745, DPR 3.0)',
                'profile': '2k',
                'forceDPR': 3.0,
                'viewport': {'width': 412, 'height': 915},
                'is_portrait': True
            },
            {
                'id': 'mobile_native_3k_landscape',
                'name': '天玑 9400+ 原生满血横屏手游 (Physical 2745x1236, DPR 3.0)',
                'profile': '2k',
                'forceDPR': 3.0,
                'viewport': {'width': 915, 'height': 412},
                'is_portrait': False
            }
        ]
        
        for cfg in configs:
            print(f"\n==================================================================")
            print(f" TESTING CONFIG: {cfg['name']}")
            print(f" Viewport: {cfg['viewport']['width']}x{cfg['viewport']['height']} (DPR: {cfg['forceDPR'] or 'Auto'})")
            print(f"==================================================================")
            
            context = browser.new_context(
                viewport=cfg['viewport'],
                device_scale_factor=3.0,
                is_mobile=True,
                has_touch=True,
                user_agent="Mozilla/5.0 (Linux; Android 15; vivo X200 Pro Build/AP2A.240905.003) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.6723.107 Mobile Safari/537.36"
            )
            page = context.new_page()
            page.add_init_script(INIT_INSTRUMENTATION)
            page.goto(file_url)
            page.wait_for_timeout(1000)
            page.click('#begin')
            page.wait_for_timeout(1000)
            
            # Post init hooks
            page.evaluate(POST_INIT_HOOKS)
            
            # Apply quality & DPR
            page.evaluate(f'''() => {{
                window.STARFIELD_QUALITY.setProfile('{cfg["profile"]}');
                if ({str(cfg["forceDPR"] is not None).lower()}) {{
                    window.STARFIELD_QUALITY.getMaxDPR = () => {cfg["forceDPR"]};
                }}
                window.dispatchEvent(new Event('resize'));
            }}''')
            page.wait_for_timeout(500)
            
            canvas_info = page.evaluate('''() => {
                const cv = document.getElementById('landscape');
                return {
                    dpr: window.DPR,
                    w: window.W,
                    h: window.H,
                    canvasW: cv.width,
                    canvasH: cv.height,
                    pixels: cv.width * cv.height
                };
            }''')
            print(f" Active Resolution: Canvas {canvas_info['canvasW']}x{canvas_info['canvasH']} ({canvas_info['pixels']/1e6:.2f} Mpx), DPR: {canvas_info['dpr']}")
            
            cfg_results = {'config': cfg, 'canvas': canvas_info, 'scenarios': {}}
            
            # -------------------------------------------------------------
            # Scenario 1: Deep Space Normal Cruise
            # -------------------------------------------------------------
            print("\n  [Scenario 1/3] Deep Space Cruise (120 frames)...")
            page.evaluate("() => window.gc && window.gc()")
            page.evaluate("() => window.startProfiling('cruise')")
            page.wait_for_timeout(2200) # collect ~120-130 frames
            m1 = page.evaluate("() => window.stopProfiling()")
            cfg_results['scenarios']['cruise'] = analyze_metrics(m1, canvas_info['pixels'])
            print(f"    Avg Frame: {cfg_results['scenarios']['cruise']['avgTotalMs']:.2f} ms ({cfg_results['scenarios']['cruise']['calculatedFps']:.1f} FPS) | Heap Alloc: {cfg_results['scenarios']['cruise']['heapAllocKBPerFrame']:.1f} KB/f")
            
            # -------------------------------------------------------------
            # Scenario 2: Planet Close Encounter (LivingPlanet 3D Engine)
            # -------------------------------------------------------------
            print("\n  [Scenario 2/3] Living Planet Close Encounter (120 frames)...")
            page.evaluate("() => { window.Starfield.seekEncounter(0); }")
            page.wait_for_timeout(600)
            page.evaluate("() => window.gc && window.gc()")
            page.evaluate("() => window.startProfiling('planet_encounter')")
            page.wait_for_timeout(2200)
            m2 = page.evaluate("() => window.stopProfiling()")
            cfg_results['scenarios']['planet_encounter'] = analyze_metrics(m2, canvas_info['pixels'])
            print(f"    Avg Frame: {cfg_results['scenarios']['planet_encounter']['avgTotalMs']:.2f} ms ({cfg_results['scenarios']['planet_encounter']['calculatedFps']:.1f} FPS) | Planet Render: {cfg_results['scenarios']['planet_encounter']['avgPlanetLPRenderMs']:.2f} ms | Model Copy: {cfg_results['scenarios']['planet_encounter']['avgPlanetModelCopyMs']:.2f} ms")
            
            # -------------------------------------------------------------
            # Scenario 3: High-Warp Pulse & Star Trails
            # -------------------------------------------------------------
            print("\n  [Scenario 3/3] Warp Pulse & Relativistic Star Trails (120 frames)...")
            page.evaluate("() => { window.Starfield.slingshotBoost(); window.Starfield.setWarpGear(2); window.Starfield.setWarpHold(true); }")
            page.wait_for_timeout(300)
            page.evaluate("() => window.gc && window.gc()")
            page.evaluate("() => window.startProfiling('warp_boost')")
            page.wait_for_timeout(2200)
            m3 = page.evaluate("() => window.stopProfiling()")
            cfg_results['scenarios']['warp_boost'] = analyze_metrics(m3, canvas_info['pixels'])
            print(f"    Avg Frame: {cfg_results['scenarios']['warp_boost']['avgTotalMs']:.2f} ms ({cfg_results['scenarios']['warp_boost']['calculatedFps']:.1f} FPS) | StarGL: {cfg_results['scenarios']['warp_boost']['avgStarGLRenderMs']:.2f} ms")
            
            results[cfg['id']] = cfg_results
            context.close()
            
        browser.close()
        
    # Save full JSON report
    report_file = os.path.join(ARTIFACT_DIR, 'dimensity9400_profile_report.json')
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"\n==================================================================")
    print(f" Profiling completed. Full JSON saved to: {report_file}")
    print(f"==================================================================")
    return results

def analyze_metrics(m, screen_pixels):
    n = max(1, m['frameCount'])
    times = m['frameTimes'] or [16.6]
    times_sorted = sorted(times)
    
    p50 = statistics.median(times)
    p95 = times_sorted[int(len(times_sorted) * 0.95)] if len(times_sorted) >= 20 else max(times)
    p99 = times_sorted[int(len(times_sorted) * 0.99)] if len(times_sorted) >= 100 else max(times)
    
    avgTotal = m['totalFrameMs'] / n
    fps = 1000.0 / avgTotal if avgTotal > 0 else 60.0
    
    # Per-stage averages
    avgSkyGrad = m['skyGradFillMs'] / n
    avgStarGLRender = m['starGLRenderMs'] / n
    avgStarGLDrawImage = m['starGLDrawImageMs'] / n
    avgPlanetLPRender = m['planetLPRenderMs'] / n
    avgPlanetModelCopy = m['planetModelCopyMs'] / n
    avgPlanetCompositeDraw = m['planetCompositeDrawMs'] / n
    avgGrainPattern = m['grainPatternFillMs'] / n
    avgVignette = m['vignetteFillMs'] / n
    avgBloom = m['bloomDrawMs'] / n
    avgNebulaSprites = m['nebulaAndSpritesDrawMs'] / n
    avgMilkyWay = m['milkyWayStrokesMs'] / n
    avgOtherStrokes = m['otherStrokesMs'] / n
    avgOtherFill = m['otherFillRectMs'] / n
    
    # Calculate remainder (director, physics, boids, matrix projection overhead)
    measuredStages = (avgSkyGrad + avgStarGLRender + avgStarGLDrawImage + avgPlanetLPRender +
                      avgPlanetModelCopy + avgPlanetCompositeDraw + avgGrainPattern +
                      avgVignette + avgBloom + avgNebulaSprites + avgMilkyWay + avgOtherStrokes + avgOtherFill)
    avgEngineLogic = max(0, avgTotal - measuredStages)
    
    # Theoretical GPU Bandwidth Estimation per frame (Bytes):
    # 1 screen pass RGBA8 = screen_pixels * 4 bytes
    bytesPerScreenPass = screen_pixels * 4
    
    # 1. Sky Gradient: 1 write = 1 pass
    bwSky = bytesPerScreenPass
    # 2. StarfieldGL drawImage: 1 read (WebGL) + 1 write (Canvas2D) = 2 passes
    bwStarGL = bytesPerScreenPass * 2 if m['starGLDrawCalls'] > 0 else 0
    # 3. Grain Pattern fillRect: 1 read (pattern) + 1 read (dest) + 1 write (dest blend) = 2.5 passes
    bwGrain = bytesPerScreenPass * 2.5 if m['grainFillCalls'] > 0 else 0
    # 4. Vignette multiply fillRect: 1 read (gradient) + 1 read (dest) + 1 write (dest) = 2 passes
    bwVignette = bytesPerScreenPass * 2 if m['vignetteFillCalls'] > 0 else 0
    # 5. Bloom: downscale (1/16) + upscale = ~0.35 passes
    bwBloom = bytesPerScreenPass * 0.35 if m['bloomDrawCalls'] > 0 else 0
    # 6. Planet: Three.js 512x512 render (1MB) + model.canvas copy (2MB) + composite to main (~0.2-1.0MB) = ~4.0 MB
    bwPlanet = (512 * 512 * 4 * 3) if m['planetDrawCalls'] > 0 else 0
    
    totalBwPerFrame = bwSky + bwStarGL + bwGrain + bwVignette + bwBloom + bwPlanet
    bwMBPerFrame = totalBwPerFrame / (1024 * 1024)
    bwGBPerSec60 = (totalBwPerFrame * 60) / (1024 * 1024 * 1024)
    bwGBPerSec120 = (totalBwPerFrame * 120) / (1024 * 1024 * 1024)
    
    heapAllocKBPerFrame = (m['heapAllocTotalBytes'] / n) / 1024.0
    heapAllocMBPerSec60 = (heapAllocKBPerFrame * 60) / 1024.0
    
    return {
        'frameCount': n,
        'avgTotalMs': round(avgTotal, 3),
        'calculatedFps': round(fps, 1),
        'p50Ms': round(p50, 3),
        'p95Ms': round(p95, 3),
        'p99Ms': round(p99, 3),
        'maxFrameTimeMs': round(m['maxFrameTimeMs'], 3),
        
        # Stage Timings
        'avgSkyGradFillMs': round(avgSkyGrad, 3),
        'avgStarGLRenderMs': round(avgStarGLRender, 3),
        'avgStarGLDrawImageMs': round(avgStarGLDrawImage, 3),
        'avgPlanetLPRenderMs': round(avgPlanetLPRender, 3),
        'avgPlanetModelCopyMs': round(avgPlanetModelCopy, 3),
        'avgPlanetCompositeDrawMs': round(avgPlanetCompositeDraw, 3),
        'avgGrainPatternFillMs': round(avgGrainPattern, 3),
        'avgVignetteFillMs': round(avgVignette, 3),
        'avgBloomDrawMs': round(avgBloom, 3),
        'avgNebulaSpritesDrawMs': round(avgNebulaSprites, 3),
        'avgMilkyWayStrokesMs': round(avgMilkyWay, 3),
        'avgEngineLogicMs': round(avgEngineLogic, 3),
        
        # Bandwidth Estimates
        'bwMBPerFrame': round(bwMBPerFrame, 2),
        'bwGBPerSec60': round(bwGBPerSec60, 2),
        'bwGBPerSec120': round(bwGBPerSec120, 2),
        'bwBreakdown': {
            'skyGradMB': round(bwSky / (1024*1024), 2),
            'starGLBlitMB': round(bwStarGL / (1024*1024), 2),
            'grainPatternMB': round(bwGrain / (1024*1024), 2),
            'vignetteMB': round(bwVignette / (1024*1024), 2),
            'bloomPassMB': round(bwBloom / (1024*1024), 2),
            'planetRenderMB': round(bwPlanet / (1024*1024), 2)
        },
        
        # Memory & GC
        'heapAllocKBPerFrame': round(heapAllocKBPerFrame, 2),
        'heapAllocMBPerSec60': round(heapAllocMBPerSec60, 2),
        'minorGCCount': m['minorGCCount'],
        'gcSpikeFrames': m['gcSpikeFrames'],
        'gcPausesTotalMs': round(m['gcPausesTotalMs'], 2)
    }

if __name__ == '__main__':
    run_profiling()
