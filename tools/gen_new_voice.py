"""Render the handful of narrator lines the existing pack does not cover.

The key is read out of the original generator at runtime: it is never printed,
never written to another file, and this script never echoes the request body.
Output goes to mimo_new/, one mp3 per id.

  python -I gen_new_voice.py voice_new.json mimo_new
"""
import sys, os, re, json, time, base64, requests

scripts_path, out_dir = sys.argv[1], sys.argv[2]
os.makedirs(out_dir, exist_ok=True)

src = open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "generate_mimo_default.py"), encoding="utf-8").read()
m = re.search(r'API_KEY\s*=\s*"([^"]+)"', src)
if not m:
    sys.exit("no key found in the existing generator")
KEY = m.group(1)          # never printed
BASE_URL = "https://api.xiaomimimo.com/v1/chat/completions"
STYLE = ("语气生动自然，富有真人呼吸起伏与情绪，带有艾希游戏解说般的幽默、自嘲和吐槽感，"
         "口语化，不要死板念稿。")

items = json.load(open(scripts_path, encoding="utf-8"))
ok = fail = 0
for i, it in enumerate(items):
    sid, text = it["id"], it["text"]
    out = os.path.join(out_dir, sid + ".mp3")
    if os.path.exists(out) and os.path.getsize(out) > 5000:
        print(f"[{i+1}/{len(items)}] skip {sid}")
        ok += 1
        continue
    payload = {"model": "mimo-v2.5-tts",
               "messages": [{"role": "user", "content": STYLE},
                            {"role": "assistant", "content": text}],
               "audio": {"format": "mp3"}}
    done = False
    for attempt in range(3):
        try:
            r = requests.post(BASE_URL, headers={"Content-Type": "application/json",
                                                 "Authorization": f"Bearer {KEY}"},
                              json=payload, timeout=40)
            if r.status_code == 200:
                audio = base64.b64decode(r.json()["choices"][0]["message"]["audio"]["data"])
                open(out, "wb").write(audio)
                print(f"[{i+1}/{len(items)}] ok {sid} {len(audio)} bytes  ({text[:14]})")
                ok += 1
                done = True
                break
            print(f"[{i+1}/{len(items)}] retry {attempt+1} {sid} HTTP {r.status_code}")
            time.sleep(2)
        except Exception as e:
            print(f"[{i+1}/{len(items)}] retry {attempt+1} {sid} {type(e).__name__}")
            time.sleep(2)
    if not done:
        fail += 1
    time.sleep(0.4)
print(f"done {ok}/{len(items)}, failed {fail}")
