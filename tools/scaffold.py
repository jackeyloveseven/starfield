"""P0 scaffold: migration.html -> starfield.html

migration.html stays the untouched base. Every phase builds on starfield.html.
This script refuses to overwrite an existing starfield.html unless --force,
so it cannot silently wipe later phases.
"""
import sys, os, shutil

SRC = r"C:\Users\machine\Downloads\migration.html"
DST = r"C:\Users\machine\Downloads\starfield.html"
FORCE = '--force' in sys.argv

if os.path.exists(DST) and not FORCE:
    sys.exit(f"{DST} already exists; pass --force to regenerate from scratch")

s = open(SRC, encoding='utf-8').read()
n = len(s)

REPS = [
    # ---- head -------------------------------------------------------------
    ('<meta name="theme-color" content="#f6f2e9">',
     '<meta name="theme-color" content="#0b1118">'),
    ('content="候鸟 · MIGRATION — 一场没有终点的飞行。零依赖 Canvas 程序化交互作品。"',
     'content="星空 · STARFIELD — 一场没有尽头的航行。零依赖 Canvas 程序化交互作品。"'),
    ('<title>候鸟 · MIGRATION</title>', '<title>星空 · STARFIELD</title>'),

    # ---- dark paper defaults (the JS palette takes over at runtime) --------
    (':root{color-scheme:light;--paper:#f6f2e9;--ink:#3a362c;--line:rgba(58,54,44,.22);--soft:rgba(246,242,233,.64);--unit:1;--pad:40px}',
     ':root{color-scheme:dark;--paper:#0b1118;--ink:#e6edf2;--line:rgba(230,237,242,.22);--soft:rgba(11,17,24,.66);--unit:1;--pad:40px}'),
    ('::selection{background:#bc8d6466}', '::selection{background:#8fb6d855}'),

    # ---- body copy --------------------------------------------------------
    ('<main id="world" aria-label="候鸟，一场由风引航的无限飞行">',
     '<main id="world" aria-label="星空，一场由引力引航的无限航行">'),
    ('aria-label="程序化大地、河流、城镇与纸鸟；移动鼠标或触摸屏幕来引导风向"',
     'aria-label="程序化星海、星云、陨石与纸鹤；移动鼠标或触摸屏幕来引导航向"'),
    ('<div class="small-title">一场没有终点的飞行<span>AN ENDLESS FLIGHT</span></div>',
     '<div class="small-title">一场没有尽头的航行<span>AN ENDLESS VOYAGE</span></div>'),
    ('>MIGRATION &nbsp; / &nbsp; <span id="edition-seed">',
     '>STARFIELD &nbsp; / &nbsp; <span id="edition-seed">'),
    ('<section id="intro" aria-label="选择迁徙的起点">',
     '<section id="intro" aria-label="选择起航的星域">'),
    ('<div class="intro-kicker eyebrow mono">A GENERATIVE JOURNEY</div>',
     '<div class="intro-kicker eyebrow mono">A GENERATIVE VOYAGE</div>'),
    ('<h1 class="serif">候鸟</h1><div class="english-title">MIGRATION</div>',
     '<h1 class="serif">星空</h1><div class="english-title">STARFIELD</div>'),
    ('<p class="intro-poem serif">把方向交给风。<br>把远方，交给时间。</p>',
     '<p class="intro-poem serif">把方向交给星光。<br>把远方，交给引力。</p>'),
    ('<div class="departure-label">选择一处起点 &nbsp; / &nbsp; DEPARTURE</div>',
     '<div class="departure-label">选择一处起航点 &nbsp; / &nbsp; DEPARTURE</div>'),
    ('<div class="destinations" role="radiogroup" aria-label="起飞地点">',
     '<div class="destinations" role="radiogroup" aria-label="起航星域">'),
    ('<button class="destination" role="radio" aria-checked="true" data-climate="0" style="--dot:#b29b65">暖纸</button>\n'
     '<button class="destination" role="radio" aria-checked="false" data-climate="2" style="--dot:#c68f8e">暮粉</button>\n'
     '<button class="destination" role="radio" aria-checked="false" data-climate="4" style="--dot:#6b7892">夜航</button>\n'
     '<button class="destination" role="radio" aria-checked="false" data-climate="1" style="--dot:#a3b7b4">雾境</button>\n'
     '<button class="destination" role="radio" aria-checked="false" data-climate="3" style="--dot:#becbd0">雪境</button>',
     '<button class="destination" role="radio" aria-checked="true" data-climate="0" style="--dot:#e8d9a8">近星海</button>\n'
     '<button class="destination" role="radio" aria-checked="false" data-climate="1" style="--dot:#c98fb0">星云带</button>\n'
     '<button class="destination" role="radio" aria-checked="false" data-climate="2" style="--dot:#b9b2a4">陨石带</button>\n'
     '<button class="destination" role="radio" aria-checked="false" data-climate="3" style="--dot:#f2ead6">星系核</button>\n'
     '<button class="destination" role="radio" aria-checked="false" data-climate="4" style="--dot:#6f8ba8">事件视界</button>'),
    ('<button id="begin">开始迁徙 <b aria-hidden="true">→</b></button>',
     '<button id="begin">起航 <b aria-hidden="true">→</b></button>'),
    ('<div class="intro-note">移动光标，让风带路。<br>建议开启声音 · 无终点，无需抵达</div>',
     '<div class="intro-note">移动光标，让星光带路。<br>建议开启声音 · 无终点，无需抵达</div>'),
    ('<section id="poem" aria-label="旅途诗句">', '<section id="poem" aria-label="航行手记">'),
    ('<section id="journey" class="hud" aria-label="旅程状态">',
     '<section id="journey" class="hud" aria-label="航行状态">'),
    ('<div id="climate-name">01 &nbsp; 暖纸 / WARM</div>',
     '<div id="climate-name">01 &nbsp; 近星海 / NEAR STARS</div>'),
    ('<div id="climate-caption">大地是一封尚未寄出的信</div>',
     '<div id="climate-caption">星光是还没读完的信</div>'),
    ('<nav id="controls" class="hud" aria-label="迁徙控制">',
     '<nav id="controls" class="hud" aria-label="航行控制">'),
    ('title="诗句开关（P）" aria-label="诗句开关"', 'title="手记开关（P）" aria-label="手记开关"'),
    ('<div id="hint">移动光标引风 &nbsp; · &nbsp; 滚轮轻探远方 &nbsp; · &nbsp; C 自主运镜</div>',
     '<div id="hint">移动光标引航 &nbsp; · &nbsp; 滚轮轻探远方 &nbsp; · &nbsp; C 自主运镜</div>'),
    ('<div id="pause-label" class="serif">风在等你</div>',
     '<div id="pause-label" class="serif">星光在等你</div>'),

    # ---- header comment ---------------------------------------------------
    (' * 候鸟 · MIGRATION\n'
     ' * A self-contained, software-projected Canvas 2D world. No WebGL, libraries,\n'
     ' * network requests, external fonts, recordings, or pre-rendered landscapes.\n'
     ' * Geometry is coordinate-seeded; climate belongs to geography, not a timer.\n'
     ' * The five climates, thirteen poems and six scores intentionally recur. The\n'
     ' * terrain and camera variations are generated afresh instead of film loops.',
     ' * 星空 · STARFIELD\n'
     ' * A self-contained, software-projected Canvas 2D world. No WebGL, libraries,\n'
     ' * network requests, external fonts, recordings, or pre-rendered landscapes.\n'
     ' * Geometry is coordinate-seeded; the region belongs to geography, not a timer.\n'
     ' * The five regions, thirteen field notes and six scores intentionally recur.\n'
     ' * Star fields and camera variations are generated afresh instead of film loops.\n'
     ' *\n'
     ' * Sister piece to 候鸟 · MIGRATION: the same paper world, the light inverted.\n'
     ' * Real migratory birds navigate by the stars; here that sense is the subject.'),

    # ---- ?seed= override: makes a run reproducible (and shareable) ---------
    ('const hexSeed = new Uint32Array(1);\n'
     'try { crypto.getRandomValues(hexSeed); } catch (_) { hexSeed[0]=Date.now()>>>0; }\n'
     'const SEED=hexSeed[0];',
     'const hexSeed = new Uint32Array(1);\n'
     'try { crypto.getRandomValues(hexSeed); } catch (_) { hexSeed[0]=Date.now()>>>0; }\n'
     '// ?seed=HEX or ?seed=DECIMAL reproduces an exact sky; omit for a new one.\n'
     'const seedParam=new URLSearchParams(location.search).get(\'seed\');\n'
     'const seedParsed=seedParam==null?NaN:(parseInt(seedParam,16)>>>0)||(parseInt(seedParam,10)>>>0);\n'
     'const SEED=Number.isNaN(seedParsed)?hexSeed[0]:seedParsed;'),

    # ---- remaining 风/迁徙 wording in JS toasts ---------------------------
    ("toast('移动光标引风 · C 镜头 · M 声音 · P 诗句 · 空格暂停 · F 全屏',6)",
     "toast('移动光标引航 · C 镜头 · M 声音 · P 手记 · 空格暂停 · F 全屏',6)"),
    ("toast(autoCamera?'镜头交还旅程，移动光标引风':'拖拽调整方向 · 滚轮或双指捏合缩放');",
     "toast(autoCamera?'镜头交还航行，移动光标引航':'拖拽调整方向 · 滚轮或双指捏合缩放');"),
    ("$('hint').textContent='触摸引风 · 切换自主镜头后，可拖拽与双指缩放';",
     "$('hint').textContent='触摸引航 · 切换自主镜头后，可拖拽与双指缩放';"),

    # ---- cap the backing store: fill-rate is the binding constraint --------
    ('DPR=devicePixelRatio||1;', 'DPR=Math.min(devicePixelRatio||1,2);'),

    # ---- diagnostic surface ----------------------------------------------
    ('window.Migration=Object.freeze({', 'window.Starfield=Object.freeze({'),

    # ---- deterministic seeking, so a screenshot is reproducible -----------
    # Mirrors the frame loop's update section without drawing. Lets a harness
    # jump to t=300 s instead of waiting for it.
    (' scoreTitles:Object.freeze([',
     ' seek:(seconds)=>{\n'
     '  const step=1/60,n=Math.max(0,Math.round(seconds/step));\n'
     '  for(let i=0;i<n;i++){\n'
     '   time+=step;if(started){travel+=SPEED*step;flightTime+=step;}else{previewTime+=step;travel+=SPEED*.15*step;}\n'
     '   updateDirector(step);updateWind(step);updateBirds(step);updateParticles(step);updatePoem(step);\n'
     '   currentPalette=climate(routeX(travel),travel);\n'
     '  }\n'
     '  return {travel,time};\n'
     ' },\n'
     ' scoreTitles:Object.freeze(['),
]

for old, new in REPS:
    if s.count(old) != 1:
        sys.exit(f"expected exactly 1 occurrence, found {s.count(old)}:\n{old[:120]}")
    s = s.replace(old, new, 1)

open(DST, 'w', encoding='utf-8', newline='').write(s)
print(f"wrote {DST}\n  {n/1024/1024:.2f} MB -> {len(s)/1024/1024:.2f} MB, "
      f"{len(REPS)} replacements")
