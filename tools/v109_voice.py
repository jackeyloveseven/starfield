"""V109: the voice gaps.

Three moments had no narration at all:

  * the five-dimensional room (added after the pack was rendered) - silent
  * the reconnect line, which had text but no clip, so it fell through to
    speechSynthesis and, on Android WebView, to nothing
  * the idle pool: 20 lines is a repeat every quarter of an hour

Twelve clips are rendered from voice_new.json and merged into NarratorClips;
the room now speaks on entry and on the way back, and five idle lines join the
pool. Clips are embedded as base64 exactly like the rest of the pack.

  python -I v109_voice.py <in.html> <out.html> <clip-dir>
"""
import sys, os, json, base64

src_p, out_p, clip_dir = sys.argv[1], sys.argv[2], sys.argv[3]
src = open(src_p, encoding="utf-8").read()

NEW = ["voice_reconnected", "tesseract_in", "tesseract_in_alt1", "tesseract_in_alt2",
       "tesseract_in_alt3", "tesseract_out", "tesseract_out_alt1",
       "idle_alt20", "idle_alt21", "idle_alt22", "idle_alt23", "idle_alt24"]
TEXTS = {x["id"]: x["text"] for x in json.load(open("voice_new.json", encoding="utf-8"))}

# ---------------------------------------------------------------- 1. clips
lines = src.split("\n")
idx = next(i for i, l in enumerate(lines) if l.startswith("const NarratorClips"))
line = lines[idx]
clips = json.loads(line[line.find("{"):line.rstrip().rstrip(";").rfind("}") + 1])
before = len(clips)
for nid in NEW:
    path = os.path.join(clip_dir, nid + ".mp3")
    if not os.path.exists(path):
        sys.exit("missing clip: " + path)
    b64 = base64.b64encode(open(path, "rb").read()).decode("ascii")
    clips[nid] = "data:audio/mp3;base64," + b64
lines[idx] = "const NarratorClips = " + json.dumps(clips, ensure_ascii=False, separators=(",", ":")) + ";"
src = "\n".join(lines)
print("clips: %d -> %d" % (before, len(clips)))

# ---------------------------------------------------------------- 2. idle pool
entries = "".join(
    json.dumps({"id": i, "text": TEXTS[i]}, ensure_ascii=False) + ", " for i in
    ("idle_alt20", "idle_alt21", "idle_alt22", "idle_alt23", "idle_alt24"))
old = "idleTalks: ["
if src.count(old) != 1:
    sys.exit("idleTalks anchor count=%d" % src.count(old))
src = src.replace(old, old + entries, 1)

# ---------------------------------------------------------------- 3. the room
old = "let tessT=0;"
new = """let tessT=0;
// What the room says on the way in and on the way out. The clips and these
// strings are the same twelve entries in voice_new.json, so they cannot drift.
const TESS_IN=[['tesseract_in','%s'],['tesseract_in_alt1','%s'],['tesseract_in_alt2','%s'],['tesseract_in_alt3','%s']];
const TESS_OUT=[['tesseract_out','%s'],['tesseract_out_alt1','%s']];""" % (
    TEXTS["tesseract_in"], TEXTS["tesseract_in_alt1"],
    TEXTS["tesseract_in_alt2"], TEXTS["tesseract_in_alt3"],
    TEXTS["tesseract_out"], TEXTS["tesseract_out_alt1"])
if src.count(old) != 1:
    sys.exit("tessT anchor count=%d" % src.count(old))
src = src.replace(old, new, 1)

old = """if(hash(cycle,707)<.45){tessT=1e-4;toast('五维空间 · TESSERACT',9);}"""
new = """if(hash(cycle,707)<.45){tessT=1e-4;toast('五维空间 · TESSERACT',9);
   const L=TESS_IN[hash(cycle,707)%TESS_IN.length];Narrator.speak(L[1],{id:L[0],priority:2});}"""
if src.count(old) != 1:
    sys.exit("trigger anchor count=%d" % src.count(old))
src = src.replace(old, new, 1)

old = "if(tessT>0){tessT+=dt;drawTesseract();if(tessT>TESS_DUR)tessT=0;}"
new = """if(tessT>0){tessT+=dt;drawTesseract();if(tessT>TESS_DUR){tessT=0;
   const L=TESS_OUT[hash(cycle,911)%TESS_OUT.length];Narrator.speak(L[1],{id:L[0],priority:1});}}"""
if src.count(old) != 1:
    sys.exit("exit anchor count=%d" % src.count(old))
src = src.replace(old, new, 1)

# ---------------------------------------------------------------- 4. reconnected
# The line already carries id 'voice_reconnected'; the clip now exists.
open(out_p, "w", encoding="utf-8", newline="").write(src)
print("V109 written:", len(src), "chars")
