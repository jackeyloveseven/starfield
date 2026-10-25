"""V133: replace the classical "violin" voice with a warm chamber string ensemble.

Diagnosis of the old playStringNote (not an EQ problem, so the whole voice is replaced):
  * two sawtooths + a triangle, barely damped, fed through two FIXED peaking filters:
      bodyFilter 2600 Hz, Q=1.1, -3 dB
      warmFilter  480 Hz, Q=2.5, +3.5 dB
    A frequency-locked formant on a harmonically dense saw is the exact cue the
    listener reads as a reed horn ("suona"), no matter how the gain is tuned.
  * the sustain is flat (linear ramp to 0.95*peak over 60% of the note) -> organ,
    not a bowed string that keeps breathing.
  * a perfect-sine 5.4 Hz vibrato applied to all three oscillators.
  * saw pair detuned by 0.18% (~3.1 cents) plus triangle 0.55, so the fixed
    formant is excited by a strong, static harmonic stack.

Replacement: three saws with a wider ensemble spread (-5.5 / +4.5 / +11 cents),
a sine core for a solid fundamental, two cascaded 12 dB/oct lowpasses with no
peaking at all, a 70 Hz rumble cut, a short filtered bow-noise transient, a slow
bow-pressure swell inside the envelope, and a delayed 8-cent vibrato plus a
0.19 Hz drift.

Usage: python -I v133_music.py <in.html> <out.html>
"""
import sys

src_p, out_p = sys.argv[1], sys.argv[2]
src = open(src_p, encoding="utf-8").read()

START = "    // Play a Chamber String Note with Warm Expressive Vibrato & Slow Romantic Attack"
END = "    // Play a Classical Masterpiece by Index"

for anchor in (START, END):
    n = src.count(anchor)
    if n != 1:
        sys.exit("anchor count=%d: %r" % (n, anchor))

i = src.index(START)
j = src.index(END, i)
if j <= i:
    sys.exit("bad slice: %d..%d" % (i, j))

NEW = r'''    // Play a Warm Chamber String Ensemble Note (v133)
    // No peaking filters and no fixed formant: the "suona" cue came from a
    // frequency-locked resonance on a static saw stack. This voice is three
    // detuned saws + a sine core through two gentle 12 dB/oct lowpasses, with
    // a bow-noise transient and a slow pressure swell.
    playStringNote(midiNote, durationSeconds, velocity = 0.7, startTime = 0) {
      const ac = this.ac;
      const t0 = startTime || ac.currentTime;
      const freq = midiToFreq(midiNote);
      const isSolo = midiNote >= 60;
      const isFast = durationSeconds < 0.35;
      const velScale = isSolo ? 1.0 : 0.62;

      // 1. Bow-noise buffer, baked once and shared by every note.
      if (!this._bowBuffer) {
        const len = Math.floor(ac.sampleRate * 0.14);
        const buf = ac.createBuffer(1, len, ac.sampleRate);
        const ch = buf.getChannelData(0);
        let last = 0;
        for (let i = 0; i < len; i++) {
          const white = Math.random() * 2 - 1;
          last = last * 0.55 + white * 0.45;
          ch[i] = (white - last) * (1 - i / len);
        }
        this._bowBuffer = buf;
      }

      // 2. Wooden body as a gentle roll-off, never a formant: no peaking filters.
      const lowpass = ac.createBiquadFilter();
      lowpass.type = 'lowpass';
      const maxCut = isSolo ? 2200 : 1600;
      const cutoff = Math.min(maxCut, Math.max(isSolo ? 1400 : 1000, freq * 2.0 + velocity * 700));
      lowpass.frequency.setValueAtTime(cutoff, t0);
      lowpass.Q.value = 0.55;

      const lowpass2 = ac.createBiquadFilter();
      lowpass2.type = 'lowpass';
      lowpass2.frequency.setValueAtTime(Math.min(cutoff * 1.65, 3200), t0);
      lowpass2.Q.value = 0.45;

      const rumbleCut = ac.createBiquadFilter();
      rumbleCut.type = 'highpass';
      rumbleCut.frequency.setValueAtTime(70, t0);
      rumbleCut.Q.value = 0.5;

      // 3. Bowed envelope: slow contact, soft sustain breathing, silky release.
      const noteGain = ac.createGain();
      const peakGain = (isFast ? 0.125 : 0.105) * velocity * velScale;
      const attackTime = isFast ? 0.035 : Math.min(0.16, Math.max(0.09, durationSeconds * 0.18));
      const sustainLevel = peakGain * (isFast ? 0.55 : 0.74);
      const holdEnd = t0 + attackTime + 0.22;
      const releaseStart = t0 + Math.max(attackTime + 0.24, durationSeconds);

      noteGain.gain.setValueAtTime(0.0001, t0);
      noteGain.gain.linearRampToValueAtTime(peakGain, t0 + attackTime);
      noteGain.gain.linearRampToValueAtTime(sustainLevel, holdEnd);

      // Slow bow-pressure swell, only when the note is long enough to breathe.
      if (!isFast) {
        const swellBack = t0 + Math.max(attackTime + 0.5, durationSeconds * 0.75);
        if (swellBack < releaseStart - 0.05) {
          noteGain.gain.linearRampToValueAtTime(sustainLevel * 1.05, (holdEnd + swellBack) * 0.5);
          noteGain.gain.linearRampToValueAtTime(sustainLevel * 0.98, swellBack);
        }
      }
      noteGain.gain.linearRampToValueAtTime(sustainLevel, releaseStart);
      noteGain.gain.exponentialRampToValueAtTime(0.0001, releaseStart + (isFast ? 0.12 : 0.55));

      // 4. Ensemble spread: three saws at -5.5 / +4.5 / +11 cents + a sine core.
      const osc1 = ac.createOscillator();
      osc1.type = 'sawtooth';
      osc1.frequency.setValueAtTime(freq, t0);
      osc1.detune.setValueAtTime(-5.5, t0);

      const osc2 = ac.createOscillator();
      osc2.type = 'sawtooth';
      osc2.frequency.setValueAtTime(freq, t0);
      osc2.detune.setValueAtTime(4.5, t0);
      const g2 = ac.createGain(); g2.gain.value = 0.52;
      osc2.connect(g2);

      const osc3 = ac.createOscillator();
      osc3.type = 'sawtooth';
      osc3.frequency.setValueAtTime(freq, t0);
      osc3.detune.setValueAtTime(11.0, t0);
      const g3 = ac.createGain(); g3.gain.value = 0.34;
      osc3.connect(g3);

      const core = ac.createOscillator();
      core.type = 'sine';
      core.frequency.setValueAtTime(freq, t0);
      const gCore = ac.createGain(); gCore.gain.value = 0.34;
      core.connect(gCore);

      // 5. Human vibrato: delayed onset, 8 cents, plus a slow 2.5-cent drift.
      const vibrato = ac.createOscillator();
      const vibGain = ac.createGain();
      vibrato.frequency.value = 5.2;
      vibGain.gain.setValueAtTime(0.0001, t0);
      vibGain.gain.setValueAtTime(0.0001, t0 + 0.18);
      vibGain.gain.linearRampToValueAtTime(8.0, t0 + 0.55);
      vibrato.connect(vibGain);

      const drift = ac.createOscillator();
      const driftGain = ac.createGain();
      drift.frequency.value = 0.19;
      driftGain.gain.setValueAtTime(0.0001, t0);
      driftGain.gain.linearRampToValueAtTime(2.5, t0 + 0.8);
      drift.connect(driftGain);

      [osc1, osc2, osc3, core].forEach(o => { vibGain.connect(o.detune); driftGain.connect(o.detune); });

      // 6. Bow-hair transient: a whisper of filtered noise at the attack only.
      const bow = ac.createBufferSource();
      bow.buffer = this._bowBuffer;
      const bowHP = ac.createBiquadFilter();
      bowHP.type = 'highpass';
      bowHP.frequency.setValueAtTime(2200, t0);
      bowHP.Q.value = 0.7;
      const bowGain = ac.createGain();
      bowGain.gain.setValueAtTime(0.0001, t0);
      bowGain.gain.linearRampToValueAtTime(0.016 * velocity, t0 + (isFast ? 0.01 : 0.025));
      bowGain.gain.exponentialRampToValueAtTime(0.0001, t0 + 0.11);
      bow.connect(bowHP);
      bowHP.connect(bowGain);

      // 7. Graph: saws + core -> lowpass -> lowpass2 -> rumble cut -> envelope.
      osc1.connect(lowpass);
      g2.connect(lowpass);
      g3.connect(lowpass);
      gCore.connect(lowpass);
      lowpass.connect(lowpass2);
      lowpass2.connect(rumbleCut);
      rumbleCut.connect(noteGain);

      const panner = ac.createStereoPanner ? ac.createStereoPanner() : null;
      if (panner) {
        panner.pan.value = midiNote >= 65 ? -0.12 : 0.16;
        noteGain.connect(panner);
        bowGain.connect(panner);
        panner.connect(this.masterGain);
      } else {
        noteGain.connect(this.masterGain);
        bowGain.connect(this.masterGain);
      }

      const stopTime = releaseStart + (isFast ? 0.18 : 0.6);
      osc1.start(t0); osc1.stop(stopTime);
      osc2.start(t0); osc2.stop(stopTime);
      osc3.start(t0); osc3.stop(stopTime);
      core.start(t0); core.stop(stopTime);
      vibrato.start(t0); vibrato.stop(stopTime);
      drift.start(t0); drift.stop(stopTime);
      bow.start(t0); bow.stop(stopTime);

      this.activeNodes.push(osc1, osc2, osc3, core, vibrato, drift, bow, noteGain, bowGain);
    }

'''

if "type = 'peaking'" in NEW or "bodyFilter" in NEW or "warmFilter" in NEW:
    sys.exit("new voice still contains a formant filter")

src = src[:i] + NEW + src[j:]

if src.count("Warm Chamber String Ensemble Note") != 1:
    sys.exit("replacement marker not unique")

open(out_p, "w", encoding="utf-8", newline="").write(src)
print("V133 written:", len(src), "chars")
