import json

with open(r"d:\items\code\projects\starfield\starfield-pub\tools\artifacts\dimensity9400_profile_report.json", "r", encoding="utf-8") as f:
    data = json.load(f)

for cid, cfg in data.items():
    name = cfg["config"]["name"]
    cw = cfg["canvas"]["canvasW"]
    ch = cfg["canvas"]["canvasH"]
    mpx = cfg["canvas"]["pixels"] / 1e6
    dpr = cfg["canvas"]["dpr"]
    print("\n" + "="*70)
    print(f"CONFIG: {name}")
    print(f"Canvas: {cw}x{ch} ({mpx:.2f} Mpx), DPR: {dpr}")
    for sname, s in cfg["scenarios"].items():
        print(f"\n  --- Scenario: {sname} ---")
        print(f"    Avg Frame: {s['avgTotalMs']} ms | Calc FPS: {s['calculatedFps']} | p50: {s['p50Ms']} ms | p95: {s['p95Ms']} ms | Max: {s['maxFrameTimeMs']} ms")
        print(f"    Stages Breakdown:")
        print(f"      - SkyGrad Fill:       {s['avgSkyGradFillMs']} ms")
        print(f"      - StarGL Render:      {s['avgStarGLRenderMs']} ms")
        print(f"      - StarGL Blit (2D):   {s['avgStarGLDrawImageMs']} ms")
        print(f"      - Planet WebGL (LP):  {s['avgPlanetLPRenderMs']} ms")
        print(f"      - Planet Model Copy:  {s['avgPlanetModelCopyMs']} ms")
        print(f"      - Planet Composite:   {s['avgPlanetCompositeDrawMs']} ms")
        print(f"      - Vignette Fill:      {s['avgVignetteFillMs']} ms")
        print(f"      - Bloom Pass:         {s['avgBloomDrawMs']} ms")
        print(f"      - Sprites/Nebulae:    {s['avgNebulaSpritesDrawMs']} ms")
        print(f"      - Engine & Physics:   {s['avgEngineLogicMs']} ms")
        print(f"    Bandwidth:")
        print(f"      - Total Frame Bandwidth: {s['bwMBPerFrame']} MB/frame")
        print(f"      - Throughput @60Hz:      {s['bwGBPerSec60']} GB/s")
        print(f"      - Throughput @120Hz:     {s['bwGBPerSec120']} GB/s")
        print(f"      - Breakdown (MB):        {s['bwBreakdown']}")
        print(f"    Memory & GC:")
        print(f"      - Allocation Rate:       {s['heapAllocKBPerFrame']} KB/frame ({s['heapAllocMBPerSec60']} MB/s @60Hz)")
        print(f"      - Minor GC Count:        {s['minorGCCount']} events")
        print(f"      - GC Pauses Total:       {s['gcPausesTotalMs']} ms")
