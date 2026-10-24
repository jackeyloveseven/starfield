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

  // Classical Pieces Score Data [BPM, Meter, InstrumentType, NoteEvents]
  // NoteEvent: [beatTime, midiNote, durationBeats, velocity]
  const CLASSICAL_PIECES = [
    {
      id: 'clair_de_lune',
      title: '德彪西 ·《月光》',
      originalTitle: 'Claude Debussy - Clair de Lune',
      composer: 'Claude Debussy (1862–1918)',
      bpm: 52,
      inst: 'piano',
      // Iconic impressionist opening in Db major
      notes: [
        // Measure 1 - 2
        [0.0, 77, 2.0, 0.65], [0.0, 73, 2.0, 0.55], // F5, Db5
        [2.0, 75, 1.5, 0.60], [2.0, 68, 1.5, 0.50], // Eb5, Ab4
        [3.5, 73, 2.5, 0.68], [3.5, 65, 2.5, 0.52], // Db5, F4
        [6.0, 72, 1.5, 0.55], [6.0, 63, 1.5, 0.48], // C5, Eb4
        [7.5, 70, 2.0, 0.60], [7.5, 61, 2.0, 0.50], // Bb4, Db4
        [9.5, 68, 3.0, 0.65], [9.5, 56, 3.0, 0.52], // Ab4, Ab3
        
        // Measure 3 - 4 (Arpeggiated starlight waves)
        [12.5, 65, 1.0, 0.55], [13.5, 68, 1.0, 0.58], [14.5, 73, 2.0, 0.68],
        [16.5, 72, 1.0, 0.60], [17.5, 70, 1.5, 0.62], [19.0, 68, 2.0, 0.65],
        [21.0, 65, 1.5, 0.58], [22.5, 61, 3.0, 0.60],
        
        // Left hand arpeggios
        [0.5, 49, 4.0, 0.45], [2.5, 56, 3.0, 0.42], [4.5, 61, 3.0, 0.45],
        [6.5, 48, 4.0, 0.42], [8.5, 56, 3.0, 0.40], [10.5, 60, 3.0, 0.42],
        [12.5, 46, 4.0, 0.45], [14.5, 53, 3.0, 0.42], [16.5, 58, 3.0, 0.44],
        [18.5, 44, 4.0, 0.45], [20.5, 51, 3.0, 0.42], [22.5, 56, 3.0, 0.45],
        
        // Measure 5 - 8 (Swell)
        [25.5, 73, 2.0, 0.72], [27.5, 75, 1.5, 0.75], [29.0, 77, 3.0, 0.82],
        [32.0, 75, 1.5, 0.70], [33.5, 73, 1.5, 0.68], [35.0, 70, 2.5, 0.65],
        [37.5, 68, 4.0, 0.60], [37.5, 49, 6.0, 0.55], [39.5, 56, 4.0, 0.50], [41.5, 61, 4.0, 0.52]
      ]
    },
    {
      id: 'gymnopedie_1',
      title: '萨蒂 ·《第一号裸体歌舞》',
      originalTitle: 'Erik Satie - Gymnopédie No. 1',
      composer: 'Erik Satie (1866–1925)',
      bpm: 64,
      inst: 'piano',
      // Iconic Gmaj7 / Dmaj7 alternating bass & tranquil soaring melody
      notes: [
        // Bar 1 (Gmaj7 bass + chord)
        [0.0, 43, 3.0, 0.52], // Bass G2
        [1.0, 59, 2.0, 0.45], [1.0, 62, 2.0, 0.45], [1.0, 66, 2.0, 0.48], // B3, D4, F#4
        
        // Bar 2 (Dmaj7 bass + chord)
        [3.0, 38, 3.0, 0.50], // Bass D2
        [4.0, 54, 2.0, 0.42], [4.0, 57, 2.0, 0.42], [4.0, 61, 2.0, 0.45], // F#3, A3, C#4
        
        // Bar 3
        [6.0, 43, 3.0, 0.52],
        [7.0, 59, 2.0, 0.45], [7.0, 62, 2.0, 0.45], [7.0, 66, 2.0, 0.48],
        
        // Bar 4
        [9.0, 38, 3.0, 0.50],
        [10.0, 54, 2.0, 0.42], [10.0, 57, 2.0, 0.42], [10.0, 61, 2.0, 0.45],
        
        // Bar 5 - Melody Enters! (F#4 -> A4)
        [12.0, 43, 3.0, 0.50],
        [13.0, 59, 2.0, 0.44], [13.0, 62, 2.0, 0.44], [13.0, 66, 2.0, 0.46],
        [12.0, 66, 2.0, 0.68], [14.0, 69, 1.0, 0.72], // F#4, A4
        
        // Bar 6 (G4 -> F#4)
        [15.0, 38, 3.0, 0.48],
        [16.0, 54, 2.0, 0.40], [16.0, 57, 2.0, 0.40], [16.0, 61, 2.0, 0.42],
        [15.0, 67, 2.0, 0.70], [17.0, 66, 1.0, 0.65], // G4, F#4
        
        // Bar 7 (C#4 -> B3)
        [18.0, 43, 3.0, 0.50],
        [19.0, 59, 2.0, 0.44], [19.0, 62, 2.0, 0.44],
        [18.0, 61, 2.0, 0.64], [20.0, 59, 1.0, 0.60], // C#4, B3
        
        // Bar 8 (C#4 -> D4)
        [21.0, 38, 3.0, 0.48],
        [22.0, 54, 2.0, 0.40], [22.0, 57, 2.0, 0.40], [22.0, 61, 2.0, 0.42],
        [21.0, 61, 1.5, 0.62], [22.5, 62, 1.5, 0.66], // C#4, D4
        
        // Bar 9 (B3 sustained)
        [24.0, 43, 3.0, 0.50],
        [25.0, 59, 2.0, 0.44], [25.0, 62, 2.0, 0.44], [25.0, 66, 2.0, 0.46],
        [24.0, 59, 3.0, 0.62],
        
        // Bar 10
        [27.0, 38, 3.0, 0.48],
        [28.0, 54, 2.0, 0.40], [28.0, 57, 2.0, 0.40], [28.0, 61, 2.0, 0.42],
        
        // Bar 11 - 14 (Second phrase)
        [30.0, 43, 3.0, 0.50],
        [31.0, 59, 2.0, 0.44], [31.0, 62, 2.0, 0.44], [31.0, 66, 2.0, 0.46],
        [30.0, 66, 2.0, 0.70], [32.0, 69, 1.0, 0.74],
        
        [33.0, 38, 3.0, 0.48],
        [34.0, 54, 2.0, 0.40], [34.0, 57, 2.0, 0.40], [34.0, 61, 2.0, 0.42],
        [33.0, 67, 2.0, 0.72], [35.0, 66, 1.0, 0.68],
        
        [36.0, 43, 3.0, 0.50],
        [37.0, 59, 2.0, 0.44], [37.0, 62, 2.0, 0.44],
        [36.0, 61, 2.0, 0.64], [38.0, 62, 1.0, 0.66],
        
        [39.0, 38, 3.0, 0.50],
        [40.0, 54, 2.0, 0.42], [40.0, 57, 2.0, 0.42], [40.0, 61, 2.0, 0.45],
        [39.0, 66, 3.0, 0.70]
      ]
    },
    {
      id: 'moonlight_sonata',
      title: '贝多芬 ·《月光奏鸣曲 第一乐章》',
      originalTitle: 'Ludwig van Beethoven - Moonlight Sonata',
      composer: 'Ludwig van Beethoven (1770–1827)',
      bpm: 50,
      inst: 'piano',
      // Continuous C# minor triplets + profound solemn bass + singing melody
      notes: [
        // Measure 1
        [0.0, 37, 4.0, 0.58], [0.0, 49, 4.0, 0.52], // Bass C#2, C#3
        [0.0, 56, 0.33, 0.40], [0.33, 61, 0.33, 0.42], [0.66, 64, 0.33, 0.44], // G#3, C#4, E4
        [1.0, 56, 0.33, 0.40], [1.33, 61, 0.33, 0.42], [1.66, 64, 0.33, 0.44],
        [2.0, 56, 0.33, 0.40], [2.33, 61, 0.33, 0.42], [2.66, 64, 0.33, 0.44],
        [3.0, 56, 0.33, 0.40], [3.33, 61, 0.33, 0.42], [3.66, 64, 0.33, 0.44],

        // Measure 2
        [4.0, 35, 4.0, 0.55], [4.0, 47, 4.0, 0.50], // Bass B1, B2
        [4.0, 56, 0.33, 0.40], [4.33, 61, 0.33, 0.42], [4.66, 64, 0.33, 0.44],
        [5.0, 56, 0.33, 0.40], [5.33, 61, 0.33, 0.42], [5.66, 64, 0.33, 0.44],
        [6.0, 56, 0.33, 0.40], [6.33, 61, 0.33, 0.42], [6.66, 64, 0.33, 0.44],
        [7.0, 56, 0.33, 0.40], [7.33, 61, 0.33, 0.42], [7.66, 64, 0.33, 0.44],

        // Measure 3
        [8.0, 33, 2.0, 0.55], [8.0, 45, 2.0, 0.50], // Bass A1, A2
        [8.0, 57, 0.33, 0.42], [8.33, 61, 0.33, 0.44], [8.66, 64, 0.33, 0.46], // A3, C#4, E4
        [9.0, 57, 0.33, 0.42], [9.33, 61, 0.33, 0.44], [9.66, 64, 0.33, 0.46],
        [10.0, 30, 2.0, 0.52], [10.0, 42, 2.0, 0.48], // Bass F#1, F#2
        [10.0, 57, 0.33, 0.42], [10.33, 62, 0.33, 0.44], [10.66, 66, 0.33, 0.46], // A3, D4, F#4
        [11.0, 57, 0.33, 0.42], [11.33, 62, 0.33, 0.44], [11.66, 66, 0.33, 0.46],

        // Measure 4
        [12.0, 32, 4.0, 0.56], [12.0, 44, 4.0, 0.50], // Bass G#1, G#2
        [12.0, 56, 0.33, 0.40], [12.33, 61, 0.33, 0.42], [12.66, 65, 0.33, 0.44],
        [13.0, 56, 0.33, 0.40], [13.33, 60, 0.33, 0.42], [13.66, 63, 0.33, 0.44],
        [14.0, 56, 0.33, 0.40], [14.33, 60, 0.33, 0.42], [14.66, 63, 0.33, 0.44],
        [15.0, 56, 0.33, 0.40], [15.33, 60, 0.33, 0.42], [15.66, 63, 0.33, 0.44],

        // Measure 5 - Dotted Melody Enters! (G#4 ... G#4 ... G#4 ... A4 ...)
        [16.0, 37, 4.0, 0.58], [16.0, 49, 4.0, 0.52],
        [16.0, 56, 0.33, 0.38], [16.33, 61, 0.33, 0.40], [16.66, 64, 0.33, 0.42],
        [17.0, 56, 0.33, 0.38], [17.33, 61, 0.33, 0.40], [17.66, 64, 0.33, 0.42],
        [18.0, 56, 0.33, 0.38], [18.33, 61, 0.33, 0.40], [18.66, 64, 0.33, 0.42],
        [19.0, 56, 0.33, 0.38], [19.33, 61, 0.33, 0.40], [19.66, 64, 0.33, 0.42],
        
        [18.0, 68, 1.5, 0.74], [19.5, 68, 0.5, 0.65], // G#4 dotted quarter + eighth
        
        // Measure 6
        [20.0, 37, 4.0, 0.58], [20.0, 49, 4.0, 0.52],
        [20.0, 56, 0.33, 0.38], [20.33, 61, 0.33, 0.40], [20.66, 64, 0.33, 0.42],
        [21.0, 56, 0.33, 0.38], [21.33, 61, 0.33, 0.40], [21.66, 64, 0.33, 0.42],
        [22.0, 56, 0.33, 0.38], [22.33, 61, 0.33, 0.40], [22.66, 64, 0.33, 0.42],
        [23.0, 56, 0.33, 0.38], [23.33, 61, 0.33, 0.40], [23.66, 64, 0.33, 0.42],
        
        [20.0, 68, 2.0, 0.72], [22.0, 69, 1.5, 0.78], [23.5, 68, 0.5, 0.68], // G#4 -> A4 -> G#4

        // Measure 7
        [24.0, 36, 4.0, 0.55], [24.0, 48, 4.0, 0.50],
        [24.0, 67, 2.0, 0.70], [26.0, 65, 1.5, 0.68], [27.5, 64, 0.5, 0.65]
      ]
    },
    {
      id: 'air_on_g_string',
      title: '巴赫 ·《G弦上的咏叹调》',
      originalTitle: 'J.S. Bach - Air on the G String',
      composer: 'Johann Sebastian Bach (1685–1750)',
      bpm: 46,
      inst: 'strings',
      // The historic track aboard Voyager Golden Record; stepping octave bass & soaring cantabile violin
      notes: [
        // Measure 1 (Walking bass D3 -> D2 -> C#3 -> C#2)
        [0.0, 50, 0.9, 0.65], [1.0, 38, 0.9, 0.60], [2.0, 49, 0.9, 0.65], [3.0, 37, 0.9, 0.60],
        // Violin 1 Long Sustained Breath (F#5)
        [0.0, 78, 3.8, 0.72],
        // Inner String Harmony
        [1.0, 66, 2.8, 0.48], [1.0, 62, 2.8, 0.45],

        // Measure 2 (Walking bass B2 -> B1 -> A2 -> A1)
        [4.0, 47, 0.9, 0.62], [5.0, 35, 0.9, 0.58], [6.0, 45, 0.9, 0.62], [7.0, 33, 0.9, 0.58],
        // Violin 1 Expressive Descent
        [4.0, 78, 1.5, 0.75], [5.5, 76, 0.5, 0.70], [6.0, 74, 1.0, 0.72], [7.0, 73, 1.0, 0.68],
        // Harmony
        [4.5, 59, 3.2, 0.46], [4.5, 62, 3.2, 0.44],

        // Measure 3 (Walking bass G2 -> G1 -> F#2 -> F#1)
        [8.0, 43, 0.9, 0.60], [9.0, 31, 0.9, 0.55], [10.0, 42, 0.9, 0.60], [11.0, 30, 0.9, 0.55],
        // Violin 1 Suspension & Resolution
        [8.0, 71, 1.5, 0.74], [9.5, 69, 0.5, 0.68], [10.0, 68, 1.0, 0.70], [11.0, 69, 1.0, 0.72],
        
        // Measure 4 (Cadence in A major)
        [12.0, 40, 1.8, 0.65], [14.0, 45, 2.0, 0.68],
        [12.0, 71, 1.0, 0.70], [13.0, 73, 1.0, 0.72], [14.0, 69, 2.0, 0.75]
      ]
    },
    {
      id: 'chopin_nocturne',
      title: '肖邦 ·《降E大调夜曲 Op. 9 No. 2》',
      originalTitle: 'Frédéric Chopin - Nocturne Op. 9 No. 2',
      composer: 'Frédéric Chopin (1810–1849)',
      bpm: 56,
      inst: 'piano',
      // Bel canto lyrical romance soaring over celestial oceans
      notes: [
        // Measure 1 - Accompaniment
        [0.0, 39, 3.0, 0.55], // Eb2 bass
        [1.0, 55, 1.0, 0.44], [1.0, 58, 1.0, 0.44], [1.0, 63, 1.0, 0.46], // G3, Bb3, Eb4
        [2.0, 55, 1.0, 0.44], [2.0, 58, 1.0, 0.44], [2.0, 63, 1.0, 0.46],
        [3.0, 44, 3.0, 0.52], // Ab2 bass
        [4.0, 56, 1.0, 0.42], [4.0, 60, 1.0, 0.42], [4.0, 63, 1.0, 0.45],
        [5.0, 56, 1.0, 0.42], [5.0, 60, 1.0, 0.42], [5.0, 63, 1.0, 0.45],

        // Measure 1 - Melody (Bb4 -> G5 -> F5 -> Eb5 -> Bb4)
        [0.0, 70, 0.75, 0.68], // Bb4
        [0.75, 79, 1.75, 0.78], // G5
        [2.5, 77, 0.5, 0.72], // F5
        [3.0, 75, 1.5, 0.74], // Eb5
        [4.5, 70, 1.5, 0.68], // Bb4

        // Measure 2 - Melody (C5 -> C6 -> Bb5 -> Ab5 ...)
        [6.0, 72, 0.75, 0.70],
        [6.75, 84, 1.75, 0.82],
        [8.5, 82, 0.5, 0.75],
        [9.0, 80, 1.5, 0.76],
        [10.5, 75, 1.5, 0.70],

        // Measure 2 - Accompaniment
        [6.0, 43, 3.0, 0.52],
        [7.0, 55, 1.0, 0.42], [7.0, 58, 1.0, 0.42], [7.0, 63, 1.0, 0.45],
        [8.0, 55, 1.0, 0.42], [8.0, 58, 1.0, 0.42], [8.0, 63, 1.0, 0.45],
        [9.0, 41, 3.0, 0.50],
        [10.0, 53, 1.0, 0.40], [10.0, 58, 1.0, 0.40], [10.0, 62, 1.0, 0.43],
        [11.0, 53, 1.0, 0.40], [11.0, 58, 1.0, 0.40], [11.0, 62, 1.0, 0.43]
      ]
    },
    {
      id: 'blue_danube',
      title: '施特劳斯 ·《蓝色多瑙河》',
      originalTitle: 'Johann Strauss II - The Blue Danube',
      composer: 'Johann Strauss II (1825–1899)',
      bpm: 96,
      inst: 'strings',
      // Iconic 2001: A Space Odyssey orbital spacecraft waltz
      notes: [
        // Bar 1 - 2 (Gentle introduction)
        [0.0, 38, 2.5, 0.55], // D2 bass
        [1.0, 62, 0.8, 0.45], [1.0, 66, 0.8, 0.48], // F#4, A4
        [2.0, 62, 0.8, 0.45], [2.0, 66, 0.8, 0.48],
        
        [0.0, 62, 1.0, 0.65], [1.0, 62, 1.0, 0.65], // D4, D4
        [2.0, 66, 1.0, 0.72], // F#4
        [3.0, 69, 1.0, 0.76], [4.0, 69, 1.0, 0.76], // A4, A4
        
        // Bar 3 - 4
        [3.0, 38, 2.5, 0.55],
        [4.0, 62, 0.8, 0.45], [4.0, 66, 0.8, 0.48],
        [5.0, 62, 0.8, 0.45], [5.0, 66, 0.8, 0.48],
        
        [5.0, 66, 1.0, 0.72], // F#4
        [6.0, 62, 2.0, 0.68], // D4
        
        // Bar 5 - 6 (Triad Waltz Swell)
        [6.0, 38, 2.5, 0.58],
        [7.0, 62, 0.8, 0.48], [7.0, 66, 0.8, 0.50],
        [8.0, 62, 0.8, 0.48], [8.0, 66, 0.8, 0.50],
        
        [8.0, 62, 1.0, 0.70], [9.0, 62, 1.0, 0.70],
        [10.0, 67, 1.0, 0.78], // G4
        [11.0, 71, 1.0, 0.82], [12.0, 71, 1.0, 0.82], // B4, B4
        [13.0, 67, 1.0, 0.75],
        [14.0, 62, 2.0, 0.70]
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
      const totalDurationMs = Math.max(10000, (maxEndTime - now + 3.0) * 1000);
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
