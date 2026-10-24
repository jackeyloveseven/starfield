/**
 * ============================================================================
 * STARFIELD: CONCERT GRAND & CHAMBER ORCHESTRA CLASSICAL MUSIC ENGINE
 * ============================================================================
 * High-fidelity, zero-dependency, procedural acoustic synthesis of timeless
 * classical masterworks for interstellar deep space voyages.
 *
 * Featured Masterpieces:
 * 1. 德彪西 ·《月光》(Claude Debussy - Clair de Lune)
 * 2. 萨蒂 ·《第一号裸体歌舞》(Erik Satie - Gymnopédie No. 1)
 * 3. 贝多芬 ·《月光奏鸣曲 第一乐章》(Ludwig van Beethoven - Moonlight Sonata)
 * 4. 巴赫 ·《G弦上的咏叹调》(J.S. Bach - Air on the G String - 旅行者金唱片)
 * 5. 肖邦 ·《降E大调夜曲》(Frédéric Chopin - Nocturne Op. 9 No. 2)
 * 6. 约翰·施特劳斯 ·《蓝色多瑙河》(Johann Strauss II - The Blue Danube - 2001太空漫游致敬)
 */

(function(global) {
  'use strict';

  // MIDI Note to Frequency (A4 = 440 Hz)
  const midiToFreq = m => 440 * Math.pow(2, (m - 69) / 12);

  // Generate Synthetic Cathedral / Concert Hall Stereo Reverb Impulse
  function createConcertHallReverb(ac, duration = 2.8, decay = 2.2) {
    const rate = ac.sampleRate;
    const length = Math.floor(rate * duration);
    const impulse = ac.createBuffer(2, length, rate);
    const left = impulse.getChannelData(0);
    const right = impulse.getChannelData(1);

    for (let i = 0; i < length; i++) {
      const t = i / length;
      const factor = Math.exp(-t * decay);
      // Diffused stereo white/pink noise envelope
      left[i] = (Math.random() * 2 - 1) * factor;
      right[i] = (Math.random() * 2 - 1) * factor;
      // Early reflection comb injection
      if (i > 1200 && i < 3500 && i % 420 === 0) {
        left[i] += 0.45 * factor;
        right[i] -= 0.45 * factor;
      }
    }
    const convolver = ac.createConvolver();
    convolver.buffer = impulse;
    return convolver;
  }

  // Classical Pieces Score Data: Exclusively Curated Saint-Saëns & Vivaldi Masterpieces
  // NoteEvent: [beatTime, midiNote, durationBeats, velocity]
  const CLASSICAL_PIECES = [
    {
      id: 'saint_saens_rondo',
      title: '圣-桑 ·《引子与回旋随想曲》',
      originalTitle: 'Camille Saint-Saëns - Introduction and Rondo Capriccioso, Op. 28',
      composer: 'Camille Saint-Saëns (1835–1921)',
      bpm: 72,
      inst: 'strings',
      notes: [
        // --- MOVEMENT 1: Andante malinconico (忧郁而崇高的引子) ---
        [0.0, 69, 1.5, 0.75], [1.5, 71, 0.5, 0.65], [2.0, 72, 2.0, 0.82], // A4, B4, C5
        [4.0, 71, 1.0, 0.70], [5.0, 69, 1.0, 0.65], [6.0, 68, 2.0, 0.85], // B4, A4, G#4
        [8.0, 69, 3.0, 0.90], [11.0, 72, 1.0, 0.70], [12.0, 76, 3.0, 0.92], // A4, C5, E5
        [15.0, 75, 1.0, 0.75], [16.0, 74, 2.0, 0.80], [18.0, 72, 1.0, 0.70], // D#5, D5, C5
        [19.0, 71, 2.5, 0.85], [21.5, 68, 0.5, 0.65], [22.0, 69, 3.0, 0.88], // B4, G#4, A4
        
        // Counterpoint cello / viola accompaniment (Andante)
        [0.0, 45, 4.0, 0.55], [4.0, 40, 4.0, 0.52], [8.0, 45, 4.0, 0.58],
        [12.0, 48, 4.0, 0.60], [16.0, 50, 4.0, 0.58], [20.0, 40, 4.0, 0.55],
        
        // Expressive violin cadence swell (华彩长音与装饰音)
        [24.0, 76, 2.0, 0.92], [26.0, 77, 1.0, 0.88], [27.0, 76, 1.0, 0.85],
        [28.0, 81, 3.0, 0.95], [31.0, 80, 1.0, 0.80], [32.0, 79, 2.0, 0.88],
        [34.0, 77, 2.0, 0.82], [36.0, 76, 4.0, 0.90],
        [24.0, 45, 6.0, 0.52], [30.0, 41, 6.0, 0.55], [36.0, 40, 6.0, 0.50],
        
        // --- MOVEMENT 2: Allegro ma non troppo (火热奔放的西班牙随想回旋) ---
        [42.0, 69, 0.5, 0.85], [42.5, 69, 0.5, 0.80], [43.0, 72, 0.5, 0.88], [43.5, 76, 1.0, 0.95],
        [44.5, 74, 0.5, 0.82], [45.0, 72, 0.5, 0.78], [45.5, 71, 1.0, 0.85],
        [46.5, 69, 0.5, 0.80], [47.0, 68, 0.5, 0.75], [47.5, 69, 1.5, 0.90],
        [49.0, 72, 0.5, 0.85], [49.5, 76, 0.5, 0.90], [50.0, 81, 2.0, 0.98],
        
        // Staccato rhythmic bass
        [42.0, 45, 1.0, 0.65], [43.0, 52, 1.0, 0.60], [44.0, 57, 1.0, 0.62],
        [45.0, 52, 1.0, 0.60], [46.0, 40, 1.0, 0.65], [47.0, 47, 1.0, 0.60],
        [48.0, 52, 1.0, 0.62], [49.0, 45, 1.0, 0.65], [50.0, 57, 2.0, 0.70],
        
        // --- MOVEMENT 3: Con morbidezza (柔美舒展的如歌副题) ---
        [53.0, 76, 1.5, 0.82], [54.5, 74, 0.5, 0.75], [55.0, 72, 1.5, 0.80],
        [56.5, 71, 0.5, 0.70], [57.0, 69, 2.0, 0.88], [59.0, 71, 1.0, 0.78],
        [60.0, 72, 1.5, 0.85], [61.5, 74, 0.5, 0.80], [62.0, 76, 3.0, 0.92],
        [53.0, 48, 4.0, 0.55], [57.0, 45, 4.0, 0.58], [61.0, 40, 4.0, 0.55],
        
        // --- MOVEMENT 4: Coda Brillante (辉煌壮丽的随想回旋高潮) ---
        [65.0, 81, 0.5, 0.95], [65.5, 83, 0.5, 0.92], [66.0, 84, 1.5, 0.98],
        [67.5, 83, 0.5, 0.90], [68.0, 81, 1.0, 0.88], [69.0, 79, 1.0, 0.85],
        [70.0, 77, 1.5, 0.90], [71.5, 76, 0.5, 0.85], [72.0, 74, 1.5, 0.88],
        [73.5, 72, 0.5, 0.82], [74.0, 71, 1.5, 0.85], [75.5, 68, 0.5, 0.80],
        [76.0, 69, 4.5, 0.95], [76.0, 81, 4.5, 0.98],
        [65.0, 45, 3.0, 0.72], [68.0, 41, 3.0, 0.70], [71.0, 43, 3.0, 0.72],
        [74.0, 40, 3.0, 0.75], [76.0, 45, 5.0, 0.82]
      ]
    },
    {
      id: 'vivaldi_spring',
      title: '维瓦尔第 ·《四季 · 春》',
      originalTitle: 'Antonio Vivaldi - The Four Seasons: Spring, RV 269',
      composer: 'Antonio Vivaldi (1678–1741)',
      bpm: 88,
      inst: 'strings',
      notes: [
        // --- MOVEMENT 1: Allegro (春临大地 · 经典赋格呈示部) ---
        [0.0, 64, 1.0, 0.85], [1.0, 68, 1.0, 0.88], [2.0, 71, 1.0, 0.92], // E4, G#4, B4
        [3.0, 71, 0.5, 0.82], [3.5, 71, 0.5, 0.80], [4.0, 71, 1.0, 0.90],
        [5.0, 73, 0.5, 0.85], [5.5, 71, 0.5, 0.80], [6.0, 69, 0.5, 0.78], [6.5, 68, 0.5, 0.75],
        [7.0, 69, 1.5, 0.88], [8.5, 68, 0.5, 0.78], [9.0, 66, 2.0, 0.85], // F#4
        [11.0, 64, 2.0, 0.90], // E4
        
        // Baroque basso continuo octave stepping
        [0.0, 40, 2.0, 0.65], [2.0, 47, 2.0, 0.60], [4.0, 40, 2.0, 0.65],
        [6.0, 45, 2.0, 0.62], [8.0, 42, 2.0, 0.60], [10.0, 40, 2.0, 0.68],
        
        // --- MOVEMENT 2: Canto degl'uccelli (雀跃欢鸣的林间百鸟) ---
        [13.0, 76, 0.5, 0.88], [13.5, 78, 0.5, 0.90], [14.0, 80, 1.0, 0.95], // E5, F#5, G#5
        [15.0, 80, 0.33, 0.85], [15.33, 80, 0.33, 0.82], [15.66, 80, 0.33, 0.85], // trills
        [16.0, 83, 1.0, 0.95], [17.0, 81, 0.5, 0.88], [17.5, 80, 0.5, 0.85],
        [18.0, 78, 1.5, 0.90], [19.5, 76, 0.5, 0.82], [20.0, 75, 2.0, 0.88],
        [13.0, 52, 4.0, 0.50], [17.0, 49, 4.0, 0.52],
        
        // --- MOVEMENT 3: Scorrono i fonti (微风吹拂 · 泉水淙淙) ---
        [22.0, 71, 1.0, 0.80], [23.0, 73, 1.0, 0.82], [24.0, 75, 1.5, 0.85],
        [25.5, 76, 0.5, 0.88], [26.0, 78, 1.5, 0.90], [27.5, 76, 0.5, 0.85],
        [28.0, 75, 1.0, 0.82], [29.0, 73, 1.0, 0.80], [30.0, 71, 2.5, 0.88],
        [22.0, 47, 4.0, 0.55], [26.0, 44, 4.0, 0.52], [30.0, 47, 3.0, 0.55],
        
        // --- MOVEMENT 4: Tuoni e lampi (春雷阵阵 · 电闪雷鸣骤雨) ---
        [33.0, 68, 0.33, 0.92], [33.33, 68, 0.33, 0.90], [33.66, 68, 0.33, 0.92],
        [34.0, 71, 0.33, 0.95], [34.33, 71, 0.33, 0.92], [34.66, 71, 0.33, 0.95],
        [35.0, 76, 1.5, 0.98], [36.5, 75, 0.5, 0.88], [37.0, 73, 1.0, 0.85],
        [38.0, 71, 1.5, 0.90], [39.5, 69, 0.5, 0.82], [40.0, 68, 2.0, 0.88],
        [33.0, 40, 1.0, 0.85], [34.0, 40, 1.0, 0.85], [35.0, 47, 2.0, 0.80],
        [37.0, 45, 2.0, 0.75], [39.0, 42, 2.0, 0.72],
        
        // --- MOVEMENT 5: Tutti Finale (凯旋再现与盛大春光) ---
        [42.0, 64, 1.0, 0.90], [43.0, 68, 1.0, 0.92], [44.0, 71, 1.0, 0.95],
        [45.0, 71, 0.5, 0.85], [45.5, 71, 0.5, 0.82], [46.0, 71, 1.0, 0.92],
        [47.0, 73, 0.5, 0.88], [47.5, 71, 0.5, 0.85], [48.0, 69, 0.5, 0.82], [48.5, 68, 0.5, 0.80],
        [49.0, 69, 1.5, 0.90], [50.5, 71, 0.5, 0.85], [51.0, 73, 1.0, 0.88],
        [52.0, 75, 1.0, 0.92], [53.0, 76, 3.5, 0.98], [53.0, 64, 3.5, 0.92],
        [42.0, 40, 2.0, 0.70], [44.0, 47, 2.0, 0.68], [46.0, 40, 2.0, 0.70],
        [48.0, 45, 2.0, 0.68], [50.0, 42, 2.0, 0.72], [52.0, 47, 1.5, 0.75], [53.5, 40, 3.5, 0.85]
      ]
    },
    {
      id: 'vivaldi_winter',
      title: '维瓦尔第 ·《四季 · 冬》',
      originalTitle: 'Antonio Vivaldi - The Four Seasons: Winter, RV 297',
      composer: 'Antonio Vivaldi (1678–1741)',
      bpm: 96,
      inst: 'strings',
      notes: [
        // --- MOVEMENT 1: Allegro non molto (冰封荒原 · 冷峻切分律动) ---
        [0.0, 65, 0.5, 0.70], [0.5, 65, 0.5, 0.75], [1.0, 65, 0.5, 0.78], [1.5, 65, 0.5, 0.80], // F4
        [2.0, 68, 0.5, 0.82], [2.5, 68, 0.5, 0.80], [3.0, 72, 0.5, 0.85], [3.5, 72, 0.5, 0.88], // Ab4, C5
        [4.0, 77, 1.0, 0.92], [5.0, 76, 0.5, 0.85], [5.5, 73, 0.5, 0.82], [6.0, 72, 1.5, 0.88], // F5, E5, Db5, C5
        [7.5, 70, 0.5, 0.80], [8.0, 68, 2.0, 0.85],
        [0.0, 41, 1.0, 0.65], [1.0, 41, 1.0, 0.68], [2.0, 41, 1.0, 0.70], [3.0, 41, 1.0, 0.72],
        [4.0, 48, 2.0, 0.65], [6.0, 46, 2.0, 0.62], [8.0, 44, 2.0, 0.65],
        
        // --- MOVEMENT 2: Orrida bufera (暴风雪呼啸 · 急速提琴旋风) ---
        [10.0, 77, 0.5, 0.90], [10.5, 75, 0.5, 0.85], [11.0, 73, 0.5, 0.88], [11.5, 72, 0.5, 0.85],
        [12.0, 70, 0.5, 0.88], [12.5, 68, 0.5, 0.82], [13.0, 67, 0.5, 0.85], [13.5, 65, 0.5, 0.80],
        [14.0, 64, 1.0, 0.92], [15.0, 65, 0.5, 0.85], [15.5, 67, 0.5, 0.88], [16.0, 68, 2.0, 0.95],
        [10.0, 41, 2.0, 0.75], [12.0, 43, 2.0, 0.72], [14.0, 40, 2.0, 0.78], [16.0, 41, 2.0, 0.80],
        
        // --- MOVEMENT 3: Largo (炉火旁的温馨深思 · 广板如歌) ---
        [18.5, 72, 2.0, 0.85], [20.5, 70, 1.0, 0.78], [21.5, 68, 1.5, 0.82],
        [23.0, 67, 1.0, 0.78], [24.0, 65, 2.5, 0.88], [26.5, 67, 0.5, 0.80],
        [27.0, 68, 2.0, 0.85], [29.0, 70, 1.0, 0.82], [30.0, 72, 3.0, 0.90],
        [18.5, 48, 4.0, 0.55], [22.5, 46, 4.0, 0.52], [26.5, 44, 4.0, 0.55],
        
        // --- MOVEMENT 4: Allegro finale (冰上滑行与傲雪凯旋) ---
        [33.5, 77, 0.5, 0.95], [34.0, 76, 0.5, 0.90], [34.5, 77, 1.0, 0.95],
        [35.5, 80, 1.0, 0.98], [36.5, 79, 0.5, 0.92], [37.0, 77, 0.5, 0.90],
        [37.5, 76, 1.5, 0.92], [39.0, 73, 1.0, 0.88], [40.0, 72, 2.0, 0.95],
        [42.0, 68, 1.0, 0.88], [43.0, 67, 1.0, 0.85], [44.0, 65, 4.0, 0.98],
        [33.5, 41, 3.0, 0.78], [36.5, 43, 3.0, 0.75], [39.5, 40, 3.0, 0.80], [42.5, 41, 5.5, 0.88]
      ]
    },
    {
      id: 'saint_saens_swan',
      title: '圣-桑 ·《动物狂欢节 · 天鹅》',
      originalTitle: 'Camille Saint-Saëns - The Carnival of the Animals: The Swan',
      composer: 'Camille Saint-Saëns (1835–1921)',
      bpm: 58,
      inst: 'strings',
      notes: [
        // --- MOVEMENT 1: Cantabile sereno (静谧星海 · 大提琴安详入场) ---
        [0.0, 67, 3.0, 0.85], [3.0, 69, 1.0, 0.78], [4.0, 71, 2.0, 0.88], // G4, A4, B4
        [6.0, 72, 1.0, 0.82], [7.0, 74, 3.0, 0.92], // C5, D5
        [10.0, 72, 1.5, 0.85], [11.5, 71, 0.5, 0.80], [12.0, 69, 2.0, 0.82], // C5, B4, A4
        [14.0, 67, 1.0, 0.78], [15.0, 66, 3.0, 0.88], // F#4
        
        // Piano gentle water ripple arpeggios
        [0.0, 43, 4.0, 0.52], [4.0, 47, 4.0, 0.50], [8.0, 50, 4.0, 0.55],
        [12.0, 45, 4.0, 0.52], [16.0, 42, 4.0, 0.50],
        
        // --- MOVEMENT 2: Espressivo ed appassionato (展翼翱翔 · 高八度如歌主旋律) ---
        [18.0, 74, 2.5, 0.90], [20.5, 76, 0.5, 0.85], [21.0, 78, 2.0, 0.95], // D5, E5, F#5
        [23.0, 79, 1.0, 0.90], [24.0, 81, 3.5, 0.98], // G5 (高潮翱翔顶峰)
        [27.5, 79, 1.0, 0.88], [28.5, 78, 1.0, 0.85], [29.5, 76, 2.0, 0.90], // G5, F#5, E5
        [31.5, 74, 1.0, 0.85], [32.5, 72, 3.0, 0.88], // D5, C5
        [18.0, 43, 4.0, 0.55], [22.0, 48, 4.0, 0.58], [26.0, 50, 4.0, 0.60], [30.0, 45, 4.0, 0.55],
        
        // --- MOVEMENT 3: Svanendo (余音回荡 · 悠远宁静尾声) ---
        [36.0, 71, 2.0, 0.85], [38.0, 69, 1.0, 0.80], [39.0, 67, 2.5, 0.88],
        [41.5, 66, 0.5, 0.78], [42.0, 67, 5.0, 0.95], [42.0, 55, 5.0, 0.85], // G4, G3
        [36.0, 47, 3.0, 0.52], [39.0, 43, 3.0, 0.55], [42.0, 43, 6.0, 0.65]
      ]
    }
  ];

  class ClassicalMusicEngine {
    constructor(ac, outputNode) {
      this.ac = ac;
      this.outputNode = outputNode;
      this.masterGain = ac.createGain();
      this.masterGain.gain.value = 0.85;

      // Reverb & Spatial Acoustics
      this.reverb = createConcertHallReverb(ac, 3.2, 2.4);
      this.dryGain = ac.createGain();
      this.wetGain = ac.createGain();
      this.dryGain.gain.value = 0.75;
      this.wetGain.gain.value = 0.48;

      this.masterGain.connect(this.dryGain);
      this.masterGain.connect(this.reverb);
      this.reverb.connect(this.wetGain);

      this.dryGain.connect(outputNode);
      this.wetGain.connect(outputNode);

      this.currentTrackIndex = 0;
      this.isPlaying = false;
      this.activeTimers = [];
      this.activeNodes = [];
      this.onTrackChange = null;
    }

    // Play a single Piano Note with Physical String Resonance & Hammer Strike
    playPianoNote(midiNote, durationSeconds, velocity = 0.7, startTime = 0) {
      const ac = this.ac;
      const t0 = startTime || ac.currentTime;
      const freq = midiToFreq(midiNote);

      // Stereo positioning based on keyboard pitch
      const panVal = Math.max(-0.4, Math.min(0.4, (midiNote - 60) / 40));
      const panner = ac.createStereoPanner ? ac.createStereoPanner() : null;
      if (panner) panner.pan.value = panVal;

      // Lowpass filter mimicking piano soundboard & hammer velocity response
      const filter = ac.createBiquadFilter();
      filter.type = 'lowpass';
      filter.frequency.setValueAtTime(600 + velocity * 4200, t0);
      filter.frequency.exponentialRampToValueAtTime(350 + velocity * 1200, t0 + Math.min(0.8, durationSeconds));

      const noteGain = ac.createGain();
      const peakGain = 0.16 * velocity;
      noteGain.gain.setValueAtTime(0.0001, t0);
      noteGain.gain.linearRampToValueAtTime(peakGain, t0 + 0.008); // 8ms hammer strike
      noteGain.gain.exponentialRampToValueAtTime(peakGain * 0.45, t0 + 0.15); // hammer release
      noteGain.gain.exponentialRampToValueAtTime(0.0001, t0 + Math.max(0.5, durationSeconds * 1.4)); // string decay

      // Multi-harmonic additive voice (Fundamental + Inharmonic overtone stretch)
      const osc1 = ac.createOscillator();
      osc1.type = 'sine';
      osc1.frequency.setValueAtTime(freq, t0);

      const osc2 = ac.createOscillator();
      osc2.type = 'triangle';
      osc2.frequency.setValueAtTime(freq * 2.001, t0); // 2nd harmonic
      const g2 = ac.createGain(); g2.gain.value = 0.42;
      osc2.connect(g2);

      const osc3 = ac.createOscillator();
      osc3.type = 'sine';
      osc3.frequency.setValueAtTime(freq * 3.003, t0); // 3rd harmonic
      const g3 = ac.createGain(); g3.gain.value = 0.22;
      osc3.connect(g3);

      osc1.connect(filter);
      g2.connect(filter);
      g3.connect(filter);

      filter.connect(noteGain);
      if (panner) {
        noteGain.connect(panner);
        panner.connect(this.masterGain);
      } else {
        noteGain.connect(this.masterGain);
      }

      const stopTime = t0 + Math.max(0.6, durationSeconds * 1.5);
      osc1.start(t0); osc1.stop(stopTime);
      osc2.start(t0); osc2.stop(stopTime);
      osc3.start(t0); osc3.stop(stopTime);

      this.activeNodes.push(osc1, osc2, osc3, noteGain);
    }

    // Play a Chamber String Note with Warm Expressive Vibrato & Slow Romantic Attack
    playStringNote(midiNote, durationSeconds, velocity = 0.7, startTime = 0) {
      const ac = this.ac;
      const t0 = startTime || ac.currentTime;
      const freq = midiToFreq(midiNote);

      const filter = ac.createBiquadFilter();
      filter.type = 'lowpass';
      filter.frequency.setValueAtTime(1400 + velocity * 2200, t0);
      filter.Q.value = 2.0;

      const noteGain = ac.createGain();
      const peakGain = 0.12 * velocity;
      noteGain.gain.setValueAtTime(0.0001, t0);
      noteGain.gain.linearRampToValueAtTime(peakGain, t0 + 0.18); // romantic 180ms swell
      noteGain.gain.setValueAtTime(peakGain * 0.90, t0 + durationSeconds * 0.8);
      noteGain.gain.exponentialRampToValueAtTime(0.0001, t0 + durationSeconds + 0.6); // smooth bow release

      // Dual detuned saw/triangle cluster for lush orchestral string section
      const osc1 = ac.createOscillator();
      osc1.type = 'sawtooth';
      osc1.frequency.setValueAtTime(freq, t0);

      const osc2 = ac.createOscillator();
      osc2.type = 'triangle';
      osc2.frequency.setValueAtTime(freq * 1.002, t0);

      // Natural violin/cello vibrato (5.4 Hz)
      const vibrato = ac.createOscillator();
      const vibGain = ac.createGain();
      vibrato.frequency.value = 5.4;
      vibGain.gain.value = freq * 0.008; // subtle vibrato depth
      vibrato.connect(osc1.frequency);
      vibrato.connect(osc2.frequency);
      vibrato.start(t0 + 0.2); // vibrato begins after bow onset

      osc1.connect(filter);
      osc2.connect(filter);
      filter.connect(noteGain);
      noteGain.connect(this.masterGain);

      const stopTime = t0 + durationSeconds + 0.7;
      osc1.start(t0); osc1.stop(stopTime);
      osc2.start(t0); osc2.stop(stopTime);
      vibrato.stop(stopTime);

      this.activeNodes.push(osc1, osc2, vibrato, noteGain);
    }

    // Play a Classical Masterpiece by Index
    playTrack(index, showToast = true) {
      this.stop();
      this.currentTrackIndex = (index + CLASSICAL_PIECES.length) % CLASSICAL_PIECES.length;
      const piece = CLASSICAL_PIECES[this.currentTrackIndex];
      const ac = this.ac;
      const now = ac.currentTime + 0.1;
      const secPerBeat = 60 / piece.bpm;

      let maxEndTime = 0;

      piece.notes.forEach(([beat, note, dur, vel]) => {
        const noteStart = now + beat * secPerBeat;
        const durSeconds = dur * secPerBeat;
        const noteEnd = noteStart + durSeconds;
        if (noteEnd > maxEndTime) maxEndTime = noteEnd;

        if (piece.inst === 'strings') {
          this.playStringNote(note, durSeconds, vel, noteStart);
        } else {
          this.playPianoNote(note, durSeconds, vel, noteStart);
        }
      });

      this.isPlaying = true;

      if (showToast && typeof toast === 'function') {
        toast(`✦ 正在演奏 [${this.currentTrackIndex + 1}/${CLASSICAL_PIECES.length}]：${piece.title} ✦`);
      }

      if (this.onTrackChange) {
        this.onTrackChange(piece, this.currentTrackIndex);
      }

      // Schedule next track with 3-second gentle cosmic pause
      const totalDurationMs = Math.max(15000, (maxEndTime - now + 4.0) * 1000);
      const timerId = setTimeout(() => {
        if (this.isPlaying) {
          this.nextTrack(true);
        }
      }, totalDurationMs);

      this.activeTimers.push(timerId);
    }

    nextTrack(showToast = true) {
      this.playTrack(this.currentTrackIndex + 1, showToast);
    }

    prevTrack(showToast = true) {
      this.playTrack(this.currentTrackIndex - 1, showToast);
    }

    stop() {
      this.isPlaying = false;
      this.activeTimers.forEach(id => clearTimeout(id));
      this.activeTimers = [];

      const now = this.ac.currentTime;
      this.activeNodes.forEach(node => {
        try {
          if (node.gain) {
            node.gain.cancelScheduledValues(now);
            node.gain.setValueAtTime(node.gain.value, now);
            node.gain.linearRampToValueAtTime(0.0001, now + 0.1);
          }
          if (node.stop) node.stop(now + 0.12);
        } catch (_) {}
      });
      this.activeNodes = [];
    }

    get currentTrack() {
      return CLASSICAL_PIECES[this.currentTrackIndex];
    }

    getCurrentPiece() {
      return CLASSICAL_PIECES[this.currentTrackIndex];
    }

    getAllPieces() {
      return CLASSICAL_PIECES;
    }
  }

  global.ClassicalMusicEngine = ClassicalMusicEngine;
  global.CLASSICAL_PIECES = CLASSICAL_PIECES;

})(typeof window !== 'undefined' ? window : globalThis);
