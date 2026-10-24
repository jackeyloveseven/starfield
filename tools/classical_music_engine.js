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
      bpm: 76,
      inst: 'strings',
      notes: [
        // --- MOVEMENT 1: Andante malinconico (忧郁而崇高的引子 · A小调 2/4拍) ---
        // 1. 乐队幽远的主和弦弱奏铺垫 (Andante malinconico)
        [0.0, 45, 1.8, 0.65], [0.0, 64, 0.8, 0.45], [0.0, 69, 0.8, 0.50], [0.0, 72, 0.8, 0.55],
        [1.0, 64, 0.8, 0.42], [1.0, 69, 0.8, 0.48], [1.0, 72, 0.8, 0.52],
        [2.0, 40, 1.8, 0.60], [2.0, 64, 0.8, 0.45], [2.0, 68, 0.8, 0.50], [2.0, 74, 0.8, 0.55],
        [3.0, 64, 0.8, 0.42], [3.0, 68, 0.8, 0.48], [3.0, 74, 0.8, 0.52],

        // 2. 独奏小提琴如歌切入 · 经典忧郁叹息主题 (第3小节起)
        [4.0, 76, 0.9, 0.88], // E5 孤傲叹息
        [4.0, 45, 2.0, 0.55], // 大提琴低音 A2
        [4.8, 64, 0.2, 0.65], [5.0, 68, 0.2, 0.70], [5.2, 71, 0.2, 0.75], [5.4, 74, 0.2, 0.80], [5.6, 72, 0.4, 0.85], // 竖琴般琶音 E4-G#4-B4-D5-C5
        [6.0, 76, 1.0, 0.92], [7.0, 74, 0.5, 0.78], [7.5, 72, 0.5, 0.75], // E5, D5, C5 连音叹息
        [6.0, 48, 2.0, 0.58], // 低音 C3
        
        // 3. 哀怨半音装饰与华丽上行
        [8.0, 71, 0.8, 0.80], [8.8, 69, 0.4, 0.72], [9.2, 71, 0.4, 0.75], [9.6, 72, 0.4, 0.80], [10.0, 74, 0.4, 0.82], [10.4, 76, 0.6, 0.88],
        [8.0, 40, 2.0, 0.52], [10.0, 45, 2.0, 0.55],
        
        // 4. 直冲云霄的高音 C6 抒情高潮与颤音舒展
        [11.0, 84, 1.5, 0.96], // 绝美高音 C6!
        [12.0, 41, 2.0, 0.60],
        [12.5, 83, 0.5, 0.85], [13.0, 81, 1.0, 0.90], [14.0, 80, 1.0, 0.88], // B5, A5, G#5
        [14.0, 40, 2.0, 0.62],
        [15.0, 81, 2.5, 0.95], [17.5, 80, 0.25, 0.75], [17.75, 81, 0.75, 0.80], // A5 悠长吟唱与柔美回音
        [16.0, 45, 2.5, 0.65],

        // 5. Animato 华彩飞瀑琶音 (向回旋曲热烈过渡)
        [19.0, 76, 0.5, 0.85], [19.5, 77, 0.5, 0.88], [20.0, 81, 0.5, 0.92], [20.5, 84, 0.5, 0.95],
        [19.0, 45, 2.0, 0.60],
        [21.0, 88, 1.2, 0.98], // 极高音 E6!
        [21.0, 40, 2.0, 0.62],
        [22.2, 86, 0.3, 0.85], [22.5, 84, 0.3, 0.82], [22.8, 83, 0.3, 0.80], [23.1, 81, 0.3, 0.82], [23.4, 80, 0.3, 0.80], [23.7, 81, 0.6, 0.85],
        [23.0, 41, 2.0, 0.60],
        [24.5, 76, 0.5, 0.80], [25.0, 72, 0.5, 0.78], [25.5, 69, 0.5, 0.75], [26.0, 64, 1.8, 0.85], // 属音驻留
        [25.0, 40, 2.8, 0.65],

        // --- MOVEMENT 2: Allegro ma non troppo (举世闻名的萨拉萨蒂西班牙回旋随想主题) ---
        // 1. 全乐队齐奏惊雷 (A小调柱状和弦 Tutti Strike)
        [28.0, 33, 1.0, 0.90], [28.0, 45, 1.0, 0.92], [28.0, 57, 1.0, 0.90], [28.0, 64, 1.0, 0.88], [28.0, 69, 1.0, 0.92], [28.0, 72, 1.0, 0.95],
        // 西班牙拨弦节奏律动 (6/8拍)
        [29.0, 45, 0.4, 0.55], [29.5, 52, 0.4, 0.50], [30.0, 45, 0.4, 0.55], [30.5, 52, 0.4, 0.50],

        // 2. 独奏小提琴 · 标志性西班牙随想回旋主部主题
        [30.7, 81, 0.15, 0.75], [30.85, 83, 0.15, 0.80], // 抢拍倚音 A5, B5
        [31.0, 88, 0.3, 0.98], [31.3, 87, 0.3, 0.95], [31.6, 88, 0.3, 0.98], // 核心动机: E6 - D#6 - E6 (十六分音符跳弓)
        [32.0, 84, 0.6, 0.92], // C6 重音
        [32.8, 83, 0.4, 0.85], [33.2, 81, 0.4, 0.88], [33.6, 80, 0.6, 0.92], // B5, A5, G#5 顿音
        [34.4, 81, 0.6, 0.92], // A5
        [35.0, 83, 0.15, 0.80], [35.15, 84, 0.35, 0.90], [35.5, 83, 0.35, 0.85], [35.85, 81, 0.35, 0.88], // B5 装饰音 -> C6 - B5 - A5
        [36.2, 77, 0.6, 0.90], // F5 巧妙降落
        [37.0, 74, 0.3, 0.82], [37.3, 76, 0.3, 0.85], [37.6, 77, 0.3, 0.88], [38.0, 79, 0.3, 0.90], [38.3, 81, 0.5, 0.95], // D5 - E5 - F5 - G5 - A5 奔腾上行
        [39.0, 84, 0.35, 0.92], [39.35, 83, 0.35, 0.88], [39.7, 81, 0.35, 0.85], [40.05, 80, 0.35, 0.88], [40.4, 81, 1.2, 0.95], // C6 - B5 - A5 - G#5 - A5

        // 回旋主题西班牙舞步低音伴奏
        [31.0, 45, 0.6, 0.68], [32.0, 52, 0.5, 0.60], [32.6, 57, 0.5, 0.62],
        [33.0, 40, 0.6, 0.65], [34.0, 47, 0.5, 0.58], [34.6, 52, 0.5, 0.60],
        [35.0, 41, 0.6, 0.68], [36.0, 48, 0.5, 0.60], [36.6, 53, 0.5, 0.62],
        [37.0, 43, 0.6, 0.65], [38.0, 50, 0.5, 0.60], [38.6, 55, 0.5, 0.62],
        [39.0, 40, 0.6, 0.70], [40.0, 47, 0.5, 0.65], [40.4, 45, 1.2, 0.75],

        // --- MOVEMENT 3: Con morbidezza (柔美舒展的如歌副题 · C大调) ---
        [42.0, 72, 1.2, 0.85], [43.2, 74, 0.4, 0.80], [43.6, 76, 1.2, 0.90], [44.8, 77, 0.4, 0.85], // C5, D5, E5, F5
        [45.2, 79, 1.6, 0.92], [46.8, 77, 0.4, 0.82], [47.2, 76, 0.8, 0.85], // G5, F5, E5
        [48.0, 74, 1.2, 0.88], [49.2, 76, 0.4, 0.82], [49.6, 77, 1.2, 0.88], [50.8, 79, 0.4, 0.85], // D5, E5, F5, G5
        [51.2, 81, 1.8, 0.95], [53.0, 79, 1.0, 0.88], // A5, G5

        // 副题如歌低音衬托
        [42.0, 48, 2.0, 0.55], [44.0, 52, 2.0, 0.52],
        [46.0, 48, 2.0, 0.58], [48.0, 43, 2.0, 0.55],
        [50.0, 41, 2.0, 0.58], [52.0, 45, 2.0, 0.62],

        // --- MOVEMENT 4: Coda Brillante (辉煌灿烂的终曲华彩与高潮) ---
        [55.0, 81, 0.25, 0.92], [55.25, 84, 0.25, 0.95], [55.5, 88, 0.5, 0.98], // A5 - C6 - E6
        [56.0, 87, 0.25, 0.92], [56.25, 88, 0.5, 0.98], [56.75, 89, 0.25, 0.95], // D#6 - E6 - F6
        [57.0, 88, 0.5, 0.98], [57.5, 86, 0.25, 0.90], [57.75, 84, 0.25, 0.92], [58.0, 83, 0.25, 0.90], [58.25, 81, 0.75, 0.95],
        [59.0, 80, 0.25, 0.88], [59.25, 81, 0.75, 0.95],
        [60.0, 83, 0.25, 0.90], [60.25, 84, 0.25, 0.92], [60.5, 86, 0.25, 0.95], [60.75, 88, 0.5, 0.98],
        [61.25, 93, 0.75, 1.0], // 冲顶巅峰超高音 A6!
        [62.0, 88, 0.4, 0.92], [62.4, 84, 0.4, 0.90], [62.8, 81, 0.4, 0.88], [63.2, 76, 0.8, 0.92], [64.0, 69, 1.2, 0.95],
        
        // 终曲全乐团终结大和弦
        [65.5, 33, 4.0, 0.90], [65.5, 45, 4.0, 0.92], [65.5, 57, 4.0, 0.95], [65.5, 64, 4.0, 0.90], [65.5, 69, 4.0, 0.95], [65.5, 81, 4.0, 0.98],

        // 终曲伴奏
        [55.0, 45, 1.0, 0.75], [56.0, 52, 1.0, 0.70],
        [57.0, 41, 1.0, 0.75], [58.0, 45, 1.0, 0.78],
        [59.0, 40, 1.0, 0.78], [60.0, 47, 1.0, 0.75],
        [61.0, 45, 1.0, 0.82], [62.0, 40, 1.0, 0.80],
        [63.0, 45, 2.0, 0.85]
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
    // Elevated Solo Violin Physical Acoustics: Bridge Hill Formant (~2850 Hz), Wood Cavity Resonance (~480 Hz)
    // Dynamic Spiccato vs Legato Bow Articulation & Soloist Concert Hall Staging
    playStringNote(midiNote, durationSeconds, velocity = 0.7, startTime = 0) {
      const ac = this.ac;
      const t0 = startTime || ac.currentTime;
      const freq = midiToFreq(midiNote);

      // 1. Acoustic Body Resonance & Formants:
      // Violin bridge hill formant (~2850 Hz) + Wood cavity resonance (~480 Hz)
      const bodyFilter = ac.createBiquadFilter();
      bodyFilter.type = 'peaking';
      bodyFilter.frequency.setValueAtTime(2850, t0);
      bodyFilter.Q.value = 3.0;
      bodyFilter.gain.setValueAtTime(6.0, t0); // +6dB bridge hill brilliance

      const warmFilter = ac.createBiquadFilter();
      warmFilter.type = 'peaking';
      warmFilter.frequency.setValueAtTime(480, t0);
      warmFilter.Q.value = 2.5;
      warmFilter.gain.setValueAtTime(3.5, t0); // +3.5dB warm wooden body resonance

      // Dynamic lowpass tracking string harmonic roll-off
      const lowpass = ac.createBiquadFilter();
      lowpass.type = 'lowpass';
      const cutoff = Math.min(12000, Math.max(2200, freq * 3.2 + velocity * 2200));
      lowpass.frequency.setValueAtTime(cutoff, t0);
      lowpass.Q.value = 1.8;

      // 2. Dynamic Bow Envelope (Articulated Spiccato vs Cantabile Legato)
      const isFast = durationSeconds < 0.35;
      const noteGain = ac.createGain();
      const peakGain = (isFast ? 0.15 : 0.12) * velocity;
      const attackTime = isFast ? 0.016 : Math.min(0.12, Math.max(0.04, durationSeconds * 0.22));

      noteGain.gain.setValueAtTime(0.0001, t0);
      noteGain.gain.linearRampToValueAtTime(peakGain, t0 + attackTime);
      if (isFast) {
        // Fast Spanish Rondo spiccato attack & snappy release
        noteGain.gain.exponentialRampToValueAtTime(peakGain * 0.3, t0 + durationSeconds * 0.75);
        noteGain.gain.exponentialRampToValueAtTime(0.0001, t0 + durationSeconds + 0.12);
      } else {
        // Expressive lyrical Andante cantabile bow swell & silky release
        noteGain.gain.linearRampToValueAtTime(peakGain * 0.95, t0 + durationSeconds * 0.6);
        noteGain.gain.exponentialRampToValueAtTime(0.0001, t0 + durationSeconds + 0.38);
      }

      // 3. Multi-timbral rich string oscillators
      const osc1 = ac.createOscillator();
      osc1.type = 'sawtooth';
      osc1.frequency.setValueAtTime(freq, t0);

      const osc2 = ac.createOscillator();
      osc2.type = 'sawtooth';
      osc2.frequency.setValueAtTime(freq * 1.0018, t0);
      const g2 = ac.createGain();
      g2.gain.value = 0.55;
      osc2.connect(g2);

      const osc3 = ac.createOscillator();
      osc3.type = 'triangle';
      osc3.frequency.setValueAtTime(freq, t0);
      const g3 = ac.createGain();
      g3.gain.value = 0.35;
      osc3.connect(g3);

      // 4. Natural 5.4 Hz Violin Vibrato with realistic onset delay (120ms)
      const vibrato = ac.createOscillator();
      const vibGain = ac.createGain();
      vibrato.frequency.value = 5.4;
      const targetDepth = freq * (isFast ? 0.004 : 0.009);
      vibGain.gain.setValueAtTime(0.00001, t0);
      vibGain.gain.setValueAtTime(0.00001, t0 + 0.12);
      vibGain.gain.linearRampToValueAtTime(targetDepth, t0 + 0.35);

      vibrato.connect(vibGain);
      vibGain.connect(osc1.frequency);
      vibGain.connect(osc2.frequency);
      vibGain.connect(osc3.frequency);
      vibrato.start(t0 + 0.1);

      // 5. Soloist Stereo Placement & Acoustic Concert Hall Staging
      const panner = ac.createStereoPanner ? ac.createStereoPanner() : null;
      if (panner) {
        // Soloist placed at left-of-center (-0.14), bass strings at right (+0.18)
        panner.pan.value = midiNote >= 65 ? -0.14 : 0.18;
      }

      // Chain audio graph: oscillators -> filters -> noteGain -> panner -> masterGain
      osc1.connect(lowpass);
      g2.connect(lowpass);
      g3.connect(lowpass);
      lowpass.connect(bodyFilter);
      bodyFilter.connect(warmFilter);
      warmFilter.connect(noteGain);

      if (panner) {
        noteGain.connect(panner);
        panner.connect(this.masterGain);
      } else {
        noteGain.connect(this.masterGain);
      }

      const stopTime = t0 + durationSeconds + (isFast ? 0.3 : 0.8);
      osc1.start(t0); osc1.stop(stopTime);
      osc2.start(t0); osc2.stop(stopTime);
      osc3.start(t0); osc3.stop(stopTime);
      vibrato.stop(stopTime);

      this.activeNodes.push(osc1, osc2, osc3, vibrato, noteGain);
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
      const nodesToDisconnect = this.activeNodes.slice();
      this.activeNodes = [];

      nodesToDisconnect.forEach(node => {
        try {
          if (node.gain) {
            node.gain.cancelScheduledValues(now);
            node.gain.setValueAtTime(node.gain.value, now);
            node.gain.linearRampToValueAtTime(0.0001, now + 0.1);
          }
          if (node.stop) node.stop(now + 0.12);
        } catch (_) {}
      });

      // Defensive memory cleanup: disconnect audio nodes from graph after ramp-down
      setTimeout(() => {
        nodesToDisconnect.forEach(node => {
          try { if (node.disconnect) node.disconnect(); } catch (_) {}
        });
      }, 180);
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
