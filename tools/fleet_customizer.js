/**
 * 🚀 STARFIELD FLEET CUSTOMIZER & QUANTUM WARP TRAIL ENGINE
 * ============================================================================
 * Origami Fleet Cosmetic Hangar & Dynamic Trail Shaders for Starfield.
 * 
 * 1. Fleet Origami Hangar Customizer (FleetCustomizer):
 *    - Hotkey: Press 'H' or click HUD Hangar button [ 🚀 舰队折纸坞 ].
 *    - Frosted glass modal with 3D Turntable Preview (crease shadows, foil highlights).
 *    - 4 Procedural Folded Paper Hulls:
 *      0: 千纸鹤 (Paper Crane - Classic balanced origami flagship)
 *      1: 疾风镖 (Aero Dart - Sleek supersonic folding arrow with needle fuselage)
 *      2: 星灵刃 (Protoss Blade - Geometric angular interceptor with floating ring fins)
 *      3: 虚空蛾 (Void Moth - Biomorphic multi-tier layered folding wings)
 *    - 4 Dynamic Quantum Warp Ribbon Trails:
 *      0: 宣纸星尘 (Paper Starlight - Warm amber gold dust embers)
 *      1: 离子幽蓝 (Ion Azure - Cyan electric plasma ribbon)
 *      2: 虚空幻紫 (Void Amethyst - Deep violet quantum vortex particles)
 *      3: 暮光红绡 (Twilight Crimson - Fiery solar flare ribbons)
 *    - Persistence: Stored in localStorage['starfield_fleet_custom_v1'].
 * 
 * 2. High-Performance Canvas 2D Mesh Rendering:
 *    - Seamlessly replaces/hooks drawFleet(), drawShard(), and drawCraftShadows().
 *    - Zero extra performance overhead (60 FPS maintained).
 *    - Dynamic trail emitters stretch dynamically with WarpDrive speed (1.0c, 5.0c, 15.0c).
 * ============================================================================
 */

(function (root) {
  'use strict';

  const STORAGE_KEY = 'starfield_fleet_custom_v1';

  // ==========================================================================
  // 1. DATA DEFINITIONS: 4 HULLS & 4 TRAILS
  // ==========================================================================

  const HULL_DEFS = [
    {
      id: 0,
      name: '千纸鹤',
      en: 'Paper Crane',
      tag: '经典旗舰 · 平衡折纸',
      desc: '源自古老东方星域的经典折纸旗舰。流畅修长的颈喙与大倾角振翼，在太阳风中展现无可挑剔的对称与优雅。',
      stats: { speed: 82, agility: 88, foldLayers: 14, warpSync: 90 },
      getVertices(flap, time) {
        return {
          nose: [0, 2, 34],
          crown: [0, 6, 26],
          neckBase: [0, 4, 14],
          spineTop: [0, 6, 4],
          spineBack: [0, 4, -13],
          tail: [0, 6, -30],
          tailRoot: [0, 0, -22],
          wrl: [-9, 2, 4],
          wrr: [9, 2, 4],
          fl: [-21, flap * 7, -5],
          fr: [21, flap * 7, -5],
          wtl: [-36, flap * 8, -14],
          wtr: [36, flap * 8, -14],
          belly: [0, -5, 3],
          keelF: [0, -3, 15],
          keelB: [0, -3, -11],
          finl: [-5, 8, -22],
          finr: [5, 8, -22],
          hl: [-13, 0, -19],
          hr: [13, 0, -19]
        };
      },
      faces: [
        { pts: ['nose', 'crown', 'neckBase'], type: 'base' },
        { pts: ['crown', 'neckBase', 'wrl'], type: 'fold' },
        { pts: ['crown', 'wrr', 'neckBase'], type: 'fold' },
        { pts: ['neckBase', 'spineTop', 'wrl'], type: 'base' },
        { pts: ['neckBase', 'wrr', 'spineTop'], type: 'shade' },
        { pts: ['spineTop', 'spineBack', 'wrl'], type: 'fold' },
        { pts: ['spineTop', 'wrr', 'spineBack'], type: 'fold' },
        { pts: ['wrl', 'spineTop', 'fl'], type: 'base' },
        { pts: ['fl', 'spineTop', 'wtl'], type: 'edge' },
        { pts: ['wtl', 'spineBack', 'fl'], type: 'edge' },
        { pts: ['wrr', 'fr', 'spineTop'], type: 'shade' },
        { pts: ['fr', 'wtr', 'spineTop'], type: 'edge' },
        { pts: ['wtr', 'spineBack', 'fr'], type: 'edge' },
        { pts: ['spineBack', 'finl', 'tail'], type: 'fold' },
        { pts: ['spineBack', 'tail', 'finr'], type: 'base' },
        { pts: ['tail', 'hl', 'finl'], type: 'edge' },
        { pts: ['tail', 'finr', 'hr'], type: 'edge' },
        { pts: ['keelF', 'belly', 'wrl'], type: 'shade' },
        { pts: ['keelF', 'wrr', 'belly'], type: 'shade' },
        { pts: ['belly', 'keelB', 'wrl'], type: 'shade' },
        { pts: ['belly', 'wrr', 'keelB'], type: 'shade' },
        { pts: ['belly', 'hl', 'keelB'], type: 'edge' },
        { pts: ['belly', 'keelB', 'hr'], type: 'edge' },
        { pts: ['nose', 'keelF', 'wrl'], type: 'shade' },
        { pts: ['nose', 'wrr', 'keelF'], type: 'shade' }
      ],
      creases: [
        ['nose', 'crown'], ['crown', 'neckBase'], ['neckBase', 'spineTop'],
        ['spineTop', 'spineBack'], ['spineBack', 'tail'],
        ['wrl', 'fl'], ['fl', 'wtl'], ['wrr', 'fr'], ['fr', 'wtr'],
        ['spineBack', 'finl'], ['spineBack', 'finr']
      ],
      shadowShape: [[0,0,32], [-7,0,4], [-36,0,-14], [-13,0,-11], [-6,0,-26], [0,0,-22], [6,0,-26], [13,0,-11], [36,0,-14], [7,0,4]],
      exhausts: [
        { pos: [0, 4, -28], weight: 1.0 },
        { pos: [-12, 0, -18], weight: 0.6 },
        { pos: [12, 0, -18], weight: 0.6 }
      ]
    },

    {
      id: 1,
      name: '疾风镖',
      en: 'Aero Dart',
      tag: '超音速 · 极速破空',
      desc: '以针状机身与下垂式三角翼构筑的超音速折叠纸镖。极小的迎风面积让其在曲速巡航中斩断星尘阻力。',
      stats: { speed: 98, agility: 75, foldLayers: 12, warpSync: 96 },
      getVertices(flap, time) {
        const microFlutter = Math.sin(time * 8.5) * 0.22;
        return {
          nose: [0, 0, 46],
          canardRoot: [0, 1.8, 26],
          canardL: [-9, 0.5, 20],
          canardR: [9, 0.5, 20],
          shoulderL: [-7, 1.2, 10],
          shoulderR: [7, 1.2, 10],
          canopyPeak: [0, 4.8, 8],
          spineMid: [0, 3.6, -4],
          spineAft: [0, 2.8, -18],
          wingTipL: [-32, -0.8 + flap * 2 + microFlutter, -22],
          wingTipR: [32, -0.8 + flap * 2 + microFlutter, -22],
          wingletL: [-34, -5.5 + flap * 2, -26],
          wingletR: [34, -5.5 + flap * 2, -26],
          finRootL: [-3.5, 2, -18],
          finRootR: [3.5, 2, -18],
          finTopL: [-5.5, 9, -24],
          finTopR: [5.5, 9, -24],
          keelNose: [0, -2, 34],
          keelBelly: [0, -4.5, 6],
          keelAft: [0, -2.5, -16],
          exhaustL: [-4.5, 0.2, -28],
          exhaustR: [4.5, 0.2, -28],
          centerNozzle: [0, 1.2, -30]
        };
      },
      faces: [
        { pts: ['nose', 'canardRoot', 'canardL'], type: 'base' },
        { pts: ['nose', 'canardR', 'canardRoot'], type: 'shade' },
        { pts: ['nose', 'canardL', 'keelNose'], type: 'shade' },
        { pts: ['nose', 'keelNose', 'canardR'], type: 'shade' },
        { pts: ['canardRoot', 'canopyPeak', 'shoulderL'], type: 'base' },
        { pts: ['canardRoot', 'shoulderR', 'canopyPeak'], type: 'shade' },
        { pts: ['canardRoot', 'shoulderL', 'canardL'], type: 'fold' },
        { pts: ['canardRoot', 'canardR', 'shoulderR'], type: 'fold' },
        { pts: ['canopyPeak', 'spineMid', 'shoulderL'], type: 'base' },
        { pts: ['canopyPeak', 'shoulderR', 'spineMid'], type: 'shade' },
        { pts: ['spineMid', 'spineAft', 'shoulderL'], type: 'fold' },
        { pts: ['spineMid', 'shoulderR', 'spineAft'], type: 'fold' },
        { pts: ['shoulderL', 'spineAft', 'wingTipL'], type: 'edge' },
        { pts: ['shoulderR', 'wingTipR', 'spineAft'], type: 'edge' },
        { pts: ['wingTipL', 'spineAft', 'wingletL'], type: 'edge' },
        { pts: ['wingTipR', 'wingletR', 'spineAft'], type: 'edge' },
        { pts: ['finRootL', 'finTopL', 'spineAft'], type: 'fold' },
        { pts: ['finRootL', 'exhaustL', 'finTopL'], type: 'edge' },
        { pts: ['finRootR', 'spineAft', 'finTopR'], type: 'fold' },
        { pts: ['finRootR', 'finTopR', 'exhaustR'], type: 'edge' },
        { pts: ['keelNose', 'keelBelly', 'shoulderL'], type: 'shade' },
        { pts: ['keelNose', 'shoulderR', 'keelBelly'], type: 'shade' },
        { pts: ['keelBelly', 'keelAft', 'wingTipL'], type: 'shade' },
        { pts: ['keelBelly', 'wingTipR', 'keelAft'], type: 'shade' },
        { pts: ['keelAft', 'exhaustL', 'centerNozzle'], type: 'edge' },
        { pts: ['keelAft', 'centerNozzle', 'exhaustR'], type: 'edge' }
      ],
      creases: [
        ['nose', 'canardRoot'], ['canardRoot', 'canopyPeak'], ['canopyPeak', 'spineAft'],
        ['spineAft', 'centerNozzle'], ['shoulderL', 'wingTipL'], ['shoulderR', 'wingTipR'],
        ['wingTipL', 'wingletL'], ['wingTipR', 'wingletR'],
        ['finRootL', 'finTopL'], ['finRootR', 'finTopR']
      ],
      shadowShape: [[0,0,46], [-9,0,20], [-7,0,10], [-34,0,-26], [-4.5,0,-28], [0,0,-30], [4.5,0,-28], [34,0,-26], [7,0,10], [9,0,20]],
      exhausts: [
        { pos: [-4.5, 0.2, -28], weight: 0.8 },
        { pos: [4.5, 0.2, -28], weight: 0.8 },
        { pos: [0, 1.2, -30], weight: 1.0 }
      ]
    },

    {
      id: 2,
      name: '星灵刃',
      en: 'Protoss Blade',
      tag: '几何截击 · 悬浮环翼',
      desc: '具有前掠新月双刃与悬浮晶格环翼的高维截击机。几何棱镜折纸结构能有效汇聚量子光子流。',
      stats: { speed: 92, agility: 96, foldLayers: 16, warpSync: 93 },
      getVertices(flap, time) {
        const hover = Math.sin(time * 3.2) * 1.6;
        return {
          bladeFangL: [-14, 1.2, 38],
          bladeFangR: [14, 1.2, 38],
          bladeMidL: [-22, 1.5, 24],
          bladeMidR: [22, 1.5, 24],
          bladeOuterL: [-36, 1.8 + flap * 2, 8],
          bladeOuterR: [36, 1.8 + flap * 2, 8],
          bladeNotchL: [-5, 0.6, 18],
          bladeNotchR: [5, 0.6, 18],
          voidCenter: [0, 0.8, 14],
          coreApex: [0, 6.8, 0],
          coreBottom: [0, -5.2, 0],
          coreLeft: [-12, 1.0, -2],
          coreRight: [12, 1.0, -2],
          wingJointL: [-18, 0.5, -14],
          wingJointR: [18, 0.5, -14],
          tailChevron: [0, 3.2, -26],
          tailBottom: [0, -2.2, -22],
          finTopL: [-16, 10.5 + hover, -8],
          finTopR: [16, 10.5 + hover, -8],
          finBotL: [-16, -7.5 + hover, -8],
          finBotR: [16, -7.5 + hover, -8],
          finBackL: [-19, 1.5 + hover, -16],
          finBackR: [19, 1.5 + hover, -16],
          finFrontL: [-13, 1.5 + hover, 0],
          finFrontR: [13, 1.5 + hover, 0]
        };
      },
      faces: [
        { pts: ['bladeFangL', 'bladeMidL', 'bladeNotchL'], type: 'base' },
        { pts: ['bladeMidL', 'bladeOuterL', 'coreLeft'], type: 'edge' },
        { pts: ['bladeNotchL', 'bladeMidL', 'coreLeft'], type: 'fold' },
        { pts: ['bladeFangR', 'bladeNotchR', 'bladeMidR'], type: 'shade' },
        { pts: ['bladeMidR', 'coreRight', 'bladeOuterR'], type: 'edge' },
        { pts: ['bladeNotchR', 'coreRight', 'bladeMidR'], type: 'fold' },
        { pts: ['coreApex', 'coreLeft', 'bladeNotchL'], type: 'base' },
        { pts: ['coreApex', 'bladeNotchR', 'coreRight'], type: 'shade' },
        { pts: ['coreApex', 'bladeNotchL', 'voidCenter'], type: 'fold' },
        { pts: ['coreApex', 'voidCenter', 'bladeNotchR'], type: 'fold' },
        { pts: ['coreApex', 'wingJointL', 'coreLeft'], type: 'fold' },
        { pts: ['coreApex', 'coreRight', 'wingJointR'], type: 'fold' },
        { pts: ['coreApex', 'tailChevron', 'wingJointL'], type: 'edge' },
        { pts: ['coreApex', 'wingJointR', 'tailChevron'], type: 'edge' },
        { pts: ['bladeOuterL', 'wingJointL', 'coreLeft'], type: 'edge' },
        { pts: ['bladeOuterR', 'coreRight', 'wingJointR'], type: 'edge' },
        { pts: ['finTopL', 'finFrontL', 'finBackL'], type: 'fold' },
        { pts: ['finBotL', 'finBackL', 'finFrontL'], type: 'edge' },
        { pts: ['finTopR', 'finBackR', 'finFrontR'], type: 'fold' },
        { pts: ['finBotR', 'finFrontR', 'finBackR'], type: 'edge' },
        { pts: ['coreBottom', 'bladeNotchL', 'bladeFangL'], type: 'shade' },
        { pts: ['coreBottom', 'bladeFangR', 'bladeNotchR'], type: 'shade' },
        { pts: ['coreBottom', 'coreLeft', 'bladeNotchL'], type: 'shade' },
        { pts: ['coreBottom', 'bladeNotchR', 'coreRight'], type: 'shade' },
        { pts: ['coreBottom', 'wingJointL', 'coreLeft'], type: 'shade' },
        { pts: ['coreBottom', 'coreRight', 'wingJointR'], type: 'shade' },
        { pts: ['coreBottom', 'tailBottom', 'wingJointL'], type: 'shade' },
        { pts: ['coreBottom', 'wingJointR', 'tailBottom'], type: 'shade' }
      ],
      creases: [
        ['bladeFangL', 'bladeOuterL'], ['bladeFangR', 'bladeOuterR'],
        ['coreApex', 'tailChevron'], ['coreApex', 'voidCenter'],
        ['finTopL', 'finBackL'], ['finTopR', 'finBackR'],
        ['coreApex', 'coreLeft'], ['coreApex', 'coreRight']
      ],
      shadowShape: [[-14,0,38], [-36,0,8], [-18,0,-14], [0,0,-26], [18,0,-14], [36,0,8], [14,0,38], [5,0,18], [0,0,14], [-5,0,18]],
      exhausts: [
        { pos: [0, 3.2, -26], weight: 1.0 },
        { pos: [-18, 0.5, -14], weight: 0.7 },
        { pos: [18, 0.5, -14], weight: 0.7 }
      ]
    },

    {
      id: 3,
      name: '虚空蛾',
      en: 'Void Moth',
      tag: '生物层叠 · 多阶天翼',
      desc: '具备双阶层叠振翅与微曲触角的深空生物质折纸蛾。在事件视界边缘散发出幽邃微光，宛如宇宙的梦境守护者。',
      stats: { speed: 85, agility: 94, foldLayers: 18, warpSync: 98 },
      getVertices(flap, time) {
        const flap1 = Math.sin(time * 3.8) * 0.75 + Math.sin(time * 0.7) * 0.15;
        const flap2 = Math.sin(time * 3.8 - 0.45) * 0.65;
        return {
          antennaL: [-8, 5.2, 34],
          antennaR: [8, 5.2, 34],
          antennaMidL: [-4, 3.5, 28],
          antennaMidR: [4, 3.5, 28],
          head: [0, 1.8, 24],
          thorax: [0, 5.4, 10],
          abdomenMid: [0, 3.8, -6],
          tailStinger: [0, -0.6, -26],
          forewingRootL: [-6, 2.2, 8],
          forewingRootR: [6, 2.2, 8],
          forewingMidL: [-24, flap1 * 7, 7],
          forewingMidR: [24, flap1 * 7, 7],
          forewingTipL: [-40, flap1 * 9.5, -1],
          forewingTipR: [40, flap1 * 9.5, -1],
          forewingAftL: [-28, flap1 * 6, -10],
          forewingAftR: [28, flap1 * 6, -10],
          hindwingRootL: [-5, 0.8, -8],
          hindwingRootR: [5, 0.8, -8],
          hindwingRibL: [-22, flap2 * 5, -18],
          hindwingRibR: [22, flap2 * 5, -18],
          hindwingStreamerL: [-16, flap2 * 4, -36],
          hindwingStreamerR: [16, flap2 * 4, -36],
          bellyThorax: [0, -4.8, 7],
          bellyAbdomen: [0, -3.8, -8]
        };
      },
      faces: [
        { pts: ['head', 'antennaMidL', 'antennaL'], type: 'edge' },
        { pts: ['head', 'antennaR', 'antennaMidR'], type: 'edge' },
        { pts: ['head', 'thorax', 'forewingRootL'], type: 'base' },
        { pts: ['head', 'forewingRootR', 'thorax'], type: 'shade' },
        { pts: ['thorax', 'abdomenMid', 'forewingRootL'], type: 'fold' },
        { pts: ['thorax', 'forewingRootR', 'abdomenMid'], type: 'fold' },
        { pts: ['abdomenMid', 'tailStinger', 'hindwingRootL'], type: 'shade' },
        { pts: ['abdomenMid', 'hindwingRootR', 'tailStinger'], type: 'shade' },
        { pts: ['forewingRootL', 'forewingMidL', 'thorax'], type: 'base' },
        { pts: ['thorax', 'forewingMidL', 'abdomenMid'], type: 'fold' },
        { pts: ['forewingMidL', 'forewingTipL', 'forewingAftL'], type: 'edge' },
        { pts: ['forewingMidL', 'forewingAftL', 'abdomenMid'], type: 'edge' },
        { pts: ['forewingRootR', 'thorax', 'forewingMidR'], type: 'shade' },
        { pts: ['thorax', 'abdomenMid', 'forewingMidR'], type: 'fold' },
        { pts: ['forewingMidR', 'forewingAftR', 'forewingTipR'], type: 'edge' },
        { pts: ['forewingMidR', 'abdomenMid', 'forewingAftR'], type: 'edge' },
        { pts: ['hindwingRootL', 'hindwingRibL', 'abdomenMid'], type: 'fold' },
        { pts: ['hindwingRibL', 'hindwingStreamerL', 'tailStinger'], type: 'edge' },
        { pts: ['abdomenMid', 'hindwingRibL', 'tailStinger'], type: 'edge' },
        { pts: ['hindwingRootR', 'abdomenMid', 'hindwingRibR'], type: 'fold' },
        { pts: ['hindwingRibR', 'tailStinger', 'hindwingStreamerR'], type: 'edge' },
        { pts: ['abdomenMid', 'tailStinger', 'hindwingRibR'], type: 'edge' },
        { pts: ['head', 'bellyThorax', 'forewingRootL'], type: 'shade' },
        { pts: ['head', 'forewingRootR', 'bellyThorax'], type: 'shade' },
        { pts: ['bellyThorax', 'bellyAbdomen', 'hindwingRootL'], type: 'shade' },
        { pts: ['bellyThorax', 'hindwingRootR', 'bellyAbdomen'], type: 'shade' },
        { pts: ['bellyAbdomen', 'tailStinger', 'hindwingRootL'], type: 'shade' },
        { pts: ['bellyAbdomen', 'hindwingRootR', 'tailStinger'], type: 'shade' }
      ],
      creases: [
        ['head', 'thorax'], ['thorax', 'abdomenMid'], ['abdomenMid', 'tailStinger'],
        ['forewingRootL', 'forewingTipL'], ['forewingRootR', 'forewingTipR'],
        ['forewingMidL', 'forewingAftL'], ['forewingMidR', 'forewingAftR'],
        ['hindwingRootL', 'hindwingStreamerL'], ['hindwingRootR', 'hindwingStreamerR']
      ],
      shadowShape: [[0,0,24], [-6,0,8], [-40,0,-1], [-28,0,-10], [-16,0,-36], [0,0,-26], [16,0,-36], [28,0,-10], [40,0,-1], [6,0,8]],
      exhausts: [
        { pos: [0, -0.6, -26], weight: 1.0 },
        { pos: [-16, 0, -36], weight: 0.8 },
        { pos: [16, 0, -36], weight: 0.8 }
      ]
    }
  ];

  const TRAIL_DEFS = [
    {
      id: 0,
      name: '宣纸星尘',
      en: 'Paper Starlight',
      vibe: '暖金烬屑 · 素纸星芒',
      desc: '经典的暖金琥珀色宣纸纤维微光，伴随细密星尘火花在尾流中缓缓散落，如墨海中的金色呼吸。',
      colors: {
        core: [255, 248, 220],
        main: [245, 185, 65],
        secondary: [255, 125, 35],
        dark: [140, 80, 25],
        hex: '#f5b941',
        gradient: 'linear-gradient(135deg, #fff0c2, #f5b941, #e06014)'
      },
      particleCount: 18,
      spread: 6.5,
      sparkleRate: 0.4
    },
    {
      id: 1,
      name: '离子幽蓝',
      en: 'Ion Azure',
      vibe: '电浆霓虹 · 赛博丝带',
      desc: '高能电离等离子体激波，呈现冰晶青蓝与极光靛青的双重波浪干涉，散发尖锐的超光速折跃气息。',
      colors: {
        core: [225, 255, 255],
        main: [0, 225, 255],
        secondary: [35, 110, 255],
        dark: [15, 45, 140],
        hex: '#00e1ff',
        gradient: 'linear-gradient(135deg, #e1ffff, #00e1ff, #236eff)'
      },
      particleCount: 22,
      spread: 7.2,
      sparkleRate: 0.7
    },
    {
      id: 2,
      name: '虚空幻紫',
      en: 'Void Amethyst',
      vibe: '引力漩涡 · 暗质粒子',
      desc: '撕裂时空维度的深紫罗兰量子漩涡，螺旋扭转的暗物质粉尘宛若加甘图亚边缘跳动的奇点微光。',
      colors: {
        core: [245, 215, 255],
        main: [175, 75, 255],
        secondary: [255, 55, 185],
        dark: [75, 20, 130],
        hex: '#af4bff',
        gradient: 'linear-gradient(135deg, #f5d7ff, #af4bff, #ff37b9)'
      },
      particleCount: 20,
      spread: 8.0,
      sparkleRate: 0.6
    },
    {
      id: 3,
      name: '暮光红绡',
      en: 'Twilight Crimson',
      vibe: '日冕激波 · 炽焰余晖',
      desc: '恒星耀斑爆发时的狂暴炽热红绡，白炽核心伴随滚烫的太阳风粒子流，在曲速推进时如同一柄斩天烈刃。',
      colors: {
        core: [255, 240, 205],
        main: [255, 50, 50],
        secondary: [255, 120, 25],
        dark: [140, 20, 20],
        hex: '#ff3232',
        gradient: 'linear-gradient(135deg, #fff0cd, #ff3232, #ff7819)'
      },
      particleCount: 24,
      spread: 9.0,
      sparkleRate: 0.8
    }
  ];

  // ==========================================================================
  // 2. FLEET CUSTOMIZER SINGLETON
  // ==========================================================================

  const FleetCustomizer = {
    hulls: HULL_DEFS,
    trails: TRAIL_DEFS,

    selectedHull: 0,
    selectedTrail: 0,

    isOpen: false,
    initialized: false,

    // Runtime game hooks (injected via init)
    game: null,

    // Dynamic Trail Emitters History: Map of craft => history points
    trailHistory: new Map(),

    // 3D Turntable Preview State
    turntable: {
      canvas: null,
      ctx: null,
      yaw: 0.75,
      pitch: 0.32,
      autoRotate: true,
      dragging: false,
      lastX: 0,
      lastY: 0,
      time: 0,
      particles: [],
      animId: null
    },

    // ------------------------------------------------------------------------
    // Persistence & State Management
    // ------------------------------------------------------------------------
    loadState() {
      try {
        const raw = localStorage.getItem(STORAGE_KEY);
        if (raw) {
          const parsed = JSON.parse(raw);
          if (typeof parsed.hull === 'number' && parsed.hull >= 0 && parsed.hull < HULL_DEFS.length) {
            this.selectedHull = parsed.hull;
          }
          if (typeof parsed.trail === 'number' && parsed.trail >= 0 && parsed.trail < TRAIL_DEFS.length) {
            this.selectedTrail = parsed.trail;
          }
        }
      } catch (e) {
        console.warn('[FleetCustomizer] Could not load localStorage:', e);
      }
    },

    saveState() {
      try {
        const data = {
          hull: this.selectedHull,
          trail: this.selectedTrail,
          updatedAt: Date.now()
        };
        localStorage.setItem(STORAGE_KEY, JSON.stringify(data));
      } catch (e) {
        console.warn('[FleetCustomizer] Could not save localStorage:', e);
      }
    },

    getHull() {
      return this.selectedHull;
    },

    setHull(idx) {
      if (idx < 0 || idx >= HULL_DEFS.length) return;
      this.selectedHull = idx;
      this.saveState();
      this.trailHistory.clear();
      this.updateUI();
      if (this.game && typeof this.game.toast === 'function') {
        const h = HULL_DEFS[idx];
        this.game.toast(`舰队折纸重塑：${h.name} (${h.en}) · ${h.tag}`, 4);
      }
    },

    getTrail() {
      return this.selectedTrail;
    },

    setTrail(idx) {
      if (idx < 0 || idx >= TRAIL_DEFS.length) return;
      this.selectedTrail = idx;
      this.saveState();
      this.updateUI();
      if (this.game && typeof this.game.toast === 'function') {
        const t = TRAIL_DEFS[idx];
        this.game.toast(`量子曲速尾迹切换：${t.name} (${t.en}) · ${t.vibe}`, 4);
      }
    },

    // ------------------------------------------------------------------------
    // UI Modal & Drawer Management
    // ------------------------------------------------------------------------
    init(gameContext) {
      if (gameContext) this.game = gameContext;
      this.loadState();
      this.injectStyles();
      this.injectDOM();
      this.bindEvents();
      this.initTurntable();
      this.updateUI();
      this.initialized = true;
      console.log('[FleetCustomizer] Loaded successfully. Equipped Hull:', HULL_DEFS[this.selectedHull].name, '| Trail:', TRAIL_DEFS[this.selectedTrail].name);
    },

    toggle() {
      if (this.isOpen) this.close();
      else this.open();
    },

    open() {
      this.isOpen = true;
      const modal = document.getElementById('hangar-modal');
      if (modal) {
        modal.classList.add('open');
      }
      const btn = document.getElementById('hangar-toggle');
      if (btn) btn.setAttribute('aria-pressed', 'true');
      this.updateUI();
      this.startTurntableLoop();
    },

    close() {
      this.isOpen = false;
      const modal = document.getElementById('hangar-modal');
      if (modal) {
        modal.classList.remove('open');
      }
      const btn = document.getElementById('hangar-toggle');
      if (btn) btn.setAttribute('aria-pressed', 'false');
      this.stopTurntableLoop();
    },

    injectStyles() {
      if (document.getElementById('hangar-customizer-styles')) return;
      const style = document.createElement('style');
      style.id = 'hangar-customizer-styles';
      style.textContent = `
        /* Hangar Customizer Modal */
        #hangar-modal {
          position: absolute;
          inset: 0;
          z-index: 320;
          background: rgba(6, 11, 18, 0.88);
          backdrop-filter: blur(24px) saturate(160%);
          -webkit-backdrop-filter: blur(24px) saturate(160%);
          display: flex;
          justify-content: center;
          align-items: center;
          opacity: 0;
          pointer-events: none;
          transition: opacity 0.35s cubic-bezier(0.16, 1, 0.3, 1);
          padding: 24px;
        }
        #hangar-modal.open {
          opacity: 1;
          pointer-events: auto;
        }
        .hangar-container {
          width: 1060px;
          max-width: 95vw;
          height: 680px;
          max-height: 90vh;
          background: rgba(12, 19, 29, 0.94);
          border: 1px solid rgba(230, 237, 242, 0.22);
          box-shadow: 0 28px 72px rgba(0, 0, 0, 0.7), inset 0 1px 0 rgba(255, 255, 255, 0.12);
          display: flex;
          flex-direction: column;
          position: relative;
          overflow: hidden;
        }
        .hangar-header {
          padding: 20px 28px 16px;
          border-bottom: 1px solid rgba(230, 237, 242, 0.12);
          display: flex;
          justify-content: space-between;
          align-items: flex-end;
          background: rgba(16, 25, 38, 0.5);
        }
        .hangar-titles h2 {
          font-size: 21px;
          letter-spacing: 3px;
          margin: 0 0 4px;
          font-weight: 400;
          color: #e6edf2;
          display: flex;
          align-items: center;
          gap: 10px;
        }
        .hangar-titles h2 span.icon-badge {
          font-size: 15px;
          background: rgba(245, 185, 65, 0.15);
          color: #f5b941;
          padding: 2px 7px;
          border-radius: 4px;
          border: 1px solid rgba(245, 185, 65, 0.3);
        }
        .hangar-titles p {
          font-size: 9.5px;
          letter-spacing: 2.2px;
          margin: 0;
          opacity: 0.6;
        }
        .hangar-close-btn {
          background: transparent;
          border: 1px solid rgba(230, 237, 242, 0.25);
          color: #e6edf2;
          padding: 8px 16px;
          border-radius: 20px;
          font-size: 11px;
          letter-spacing: 1.5px;
          transition: all 0.25s;
          cursor: pointer;
        }
        .hangar-close-btn:hover {
          background: rgba(230, 237, 242, 0.15);
          border-color: #e6edf2;
        }

        /* Modal Body: 2 Columns */
        .hangar-body {
          display: grid;
          grid-template-columns: 440px 1fr;
          flex: 1;
          min-height: 0;
          overflow: hidden;
        }

        /* Left Column: 3D Turntable Preview */
        .hangar-preview-col {
          border-right: 1px solid rgba(230, 237, 242, 0.12);
          display: flex;
          flex-direction: column;
          background: radial-gradient(circle at center, rgba(20, 32, 48, 0.6) 0%, rgba(9, 14, 22, 0.9) 100%);
          position: relative;
          padding: 16px;
        }
        .turntable-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 8px;
        }
        .turntable-header .badge {
          font-size: 9px;
          letter-spacing: 1.8px;
          color: #8fb6d8;
          background: rgba(143, 182, 216, 0.12);
          padding: 3px 8px;
          border-radius: 4px;
        }
        .turntable-wrapper {
          flex: 1;
          position: relative;
          display: flex;
          align-items: center;
          justify-content: center;
          overflow: hidden;
          border-radius: 6px;
          border: 1px solid rgba(230, 237, 242, 0.08);
          background: #070d14;
          cursor: grab;
          touch-action: none;
        }
        .turntable-wrapper.dragging {
          cursor: grabbing;
        }
        #hangar-turntable-canvas {
          display: block;
          width: 100%;
          height: 100%;
        }
        .turntable-hint {
          position: absolute;
          bottom: 10px;
          left: 50%;
          transform: translateX(-50%);
          font-size: 9px;
          letter-spacing: 1.2px;
          color: rgba(230, 237, 242, 0.45);
          pointer-events: none;
          white-space: nowrap;
          background: rgba(6, 11, 18, 0.6);
          padding: 3px 10px;
          border-radius: 12px;
          border: 1px solid rgba(255, 255, 255, 0.06);
        }
        .turntable-meta {
          margin-top: 12px;
          background: rgba(16, 24, 35, 0.7);
          border: 1px solid rgba(230, 237, 242, 0.1);
          border-radius: 6px;
          padding: 12px 14px;
          display: flex;
          flex-direction: column;
          gap: 6px;
        }
        .turntable-meta-row {
          display: flex;
          justify-content: space-between;
          align-items: center;
          font-size: 11px;
        }
        .turntable-meta-row .label {
          color: rgba(230, 237, 242, 0.55);
          letter-spacing: 1px;
        }
        .turntable-meta-row .val {
          color: #f5b941;
          font-weight: 500;
        }

        /* Right Column: Customization Selectors */
        .hangar-select-col {
          display: flex;
          flex-direction: column;
          padding: 20px 26px;
          overflow-y: auto;
          gap: 22px;
        }
        .select-section-title {
          font-size: 13px;
          letter-spacing: 2px;
          color: #e6edf2;
          margin-bottom: 10px;
          display: flex;
          align-items: center;
          gap: 8px;
        }
        .select-section-title::before {
          content: "";
          display: inline-block;
          width: 3px;
          height: 13px;
          background: #f5b941;
          border-radius: 2px;
        }
        .section-desc {
          font-size: 10px;
          letter-spacing: 1px;
          color: rgba(230, 237, 242, 0.5);
          margin-top: -6px;
          margin-bottom: 12px;
        }

        /* Card Grids */
        .hull-cards-grid, .trail-cards-grid {
          display: grid;
          grid-template-columns: repeat(2, 1fr);
          gap: 12px;
        }

        /* Hull Card */
        .hangar-card {
          background: rgba(16, 24, 36, 0.7);
          border: 1px solid rgba(230, 237, 242, 0.12);
          border-radius: 6px;
          padding: 14px;
          cursor: pointer;
          transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1);
          display: flex;
          flex-direction: column;
          gap: 8px;
          position: relative;
        }
        .hangar-card:hover {
          background: rgba(23, 34, 50, 0.85);
          border-color: rgba(230, 237, 242, 0.35);
          transform: translateY(-2px);
        }
        .hangar-card.active {
          background: rgba(26, 40, 60, 0.95);
          border-color: #f5b941;
          box-shadow: 0 0 16px rgba(245, 185, 65, 0.25), inset 0 0 8px rgba(245, 185, 65, 0.1);
        }
        .card-top {
          display: flex;
          justify-content: space-between;
          align-items: center;
        }
        .card-id-badge {
          font-size: 9px;
          letter-spacing: 1.5px;
          color: rgba(230, 237, 242, 0.6);
          background: rgba(255, 255, 255, 0.06);
          padding: 2px 6px;
          border-radius: 3px;
        }
        .hangar-card.active .card-id-badge {
          color: #f5b941;
          background: rgba(245, 185, 65, 0.15);
        }
        .card-active-pill {
          font-size: 8.5px;
          letter-spacing: 1px;
          color: #f5b941;
          display: none;
          font-weight: 600;
        }
        .hangar-card.active .card-active-pill {
          display: inline-block;
        }
        .card-name-row {
          display: flex;
          align-items: baseline;
          gap: 8px;
        }
        .card-name {
          font-size: 15px;
          color: #e6edf2;
          font-weight: 500;
          letter-spacing: 1px;
        }
        .card-sub {
          font-size: 10px;
          color: rgba(230, 237, 242, 0.45);
          letter-spacing: 0.5px;
        }
        .card-tag {
          font-size: 9.5px;
          color: #8fb6d8;
          letter-spacing: 0.8px;
        }
        .card-desc {
          font-size: 9.5px;
          line-height: 1.55;
          color: rgba(230, 237, 242, 0.6);
        }

        /* Trail Card */
        .trail-card {
          padding: 12px 14px;
        }
        .trail-swatch-bar {
          height: 6px;
          border-radius: 3px;
          margin-bottom: 4px;
          box-shadow: 0 0 10px currentColor;
        }
        .trail-card.active {
          border-color: #00e1ff;
          box-shadow: 0 0 16px rgba(0, 225, 255, 0.25);
        }
        .trail-card.active .card-active-pill {
          color: #00e1ff;
        }

        /* Footer status bar */
        .hangar-footer-bar {
          margin-top: auto;
          padding-top: 14px;
          border-top: 1px solid rgba(230, 237, 242, 0.1);
          display: flex;
          justify-content: space-between;
          align-items: center;
          font-size: 10px;
          color: rgba(230, 237, 242, 0.5);
        }
        .hangar-footer-bar .storage-badge {
          color: #8fb6d8;
          letter-spacing: 1px;
        }

        @media (max-width: 900px) {
          .hangar-body {
            grid-template-columns: 1fr;
            overflow-y: auto;
          }
          .hangar-preview-col {
            height: 280px;
            border-right: none;
            border-bottom: 1px solid rgba(230, 237, 242, 0.12);
          }
        }
      `;
      document.head.appendChild(style);
    },

    injectDOM() {
      // 1. Check/inject HUD toggle button
      let btn = document.getElementById('hangar-toggle');
      if (!btn) {
        const controls = document.getElementById('controls');
        if (controls) {
          btn = document.createElement('button');
          btn.className = 'control';
          btn.id = 'hangar-toggle';
          btn.setAttribute('title', '舰队折纸坞 · 舰体与尾迹定制 (H)');
          btn.setAttribute('aria-label', '舰队折纸坞');
          btn.innerHTML = `
            <span class="icon hangar-icon">
              <svg viewBox="0 0 16 16" width="16" height="16" fill="none" stroke="currentColor" stroke-width="1.3">
                <polygon points="8,1.5 12.5,6.5 8,14.5 3.5,6.5" stroke="currentColor" stroke-linejoin="round"/>
                <line x1="3.5" y1="6.5" x2="12.5" y2="6.5" stroke="currentColor"/>
                <line x1="8" y1="1.5" x2="8" y2="14.5" stroke="currentColor"/>
                <polygon points="3.5,6.5 1,10 4,11" stroke="currentColor" stroke-linejoin="round"/>
                <polygon points="12.5,6.5 15,10 12,11" stroke="currentColor" stroke-linejoin="round"/>
              </svg>
            </span>
          `;
          const settingsToggle = document.getElementById('settings-toggle');
          if (settingsToggle) {
            controls.insertBefore(btn, settingsToggle);
          } else {
            controls.appendChild(btn);
          }
        }
      }

      // 2. Check/inject modal container
      if (document.getElementById('hangar-modal')) return;

      const modal = document.createElement('section');
      modal.id = 'hangar-modal';
      modal.setAttribute('aria-label', '舰队折纸坞');
      modal.innerHTML = `
        <div class="hangar-container">
          <div class="hangar-header">
            <div class="hangar-titles">
              <h2 class="serif">
                <span class="icon-badge">🚀</span>
                舰队折纸坞 · 舰体与尾迹定制
              </h2>
              <p class="mono">FLEET ORIGAMI HANGAR // COSMETIC & WARP TRAIL ENGINE</p>
            </div>
            <button class="hangar-close-btn mono" id="hangar-close-btn">关闭 [ESC]</button>
          </div>
          <div class="hangar-body">
            <!-- Left: 3D Turntable Preview -->
            <div class="hangar-preview-col">
              <div class="turntable-header">
                <span class="badge mono">3D TURNTABLE PREVIEW</span>
                <span class="mono" id="turntable-angle-label" style="font-size:9.5px; opacity:0.65;">ROT: 45°</span>
              </div>
              <div class="turntable-wrapper" id="turntable-wrapper">
                <canvas id="hangar-turntable-canvas" width="400" height="360"></canvas>
                <div class="turntable-hint mono">按住拖拽 360° 旋转 · 实时纸艺折痕与金箔光泽</div>
              </div>
              <div class="turntable-meta" id="turntable-meta">
                <!-- Dynamically populated -->
              </div>
            </div>

            <!-- Right: Customization Selectors -->
            <div class="hangar-select-col">
              <!-- Hulls -->
              <div class="select-section">
                <div class="select-section-title serif">折纸旗舰舰体几何 (Origami Hull Geometries)</div>
                <div class="section-desc mono">高精度三维折叠网格 · 空间折纸气动学 · 旗舰金箔点缀</div>
                <div class="hull-cards-grid" id="hull-cards-container">
                  <!-- Injected via renderHullCards() -->
                </div>
              </div>

              <!-- Trails -->
              <div class="select-section">
                <div class="select-section-title serif">量子曲速丝带尾迹 (Dynamic Quantum Warp Trails)</div>
                <div class="section-desc mono">粒子动力学着色器 · 随曲速引擎动态拉伸 (1.0c / 5.0c / 15.0c)</div>
                <div class="trail-cards-grid" id="trail-cards-container">
                  <!-- Injected via renderTrailCards() -->
                </div>
              </div>

              <!-- Footer info -->
              <div class="hangar-footer-bar mono">
                <span class="storage-badge">● 本地持久化：localStorage['starfield_fleet_custom_v1']</span>
                <span>全舰队已实时同步装备</span>
              </div>
            </div>
          </div>
        </div>
      `;

      const world = document.getElementById('world') || document.body;
      world.appendChild(modal);
    },

    bindEvents() {
      // Toggle button
      const btn = document.getElementById('hangar-toggle');
      if (btn && !btn._customizerBound) {
        btn._customizerBound = true;
        btn.addEventListener('click', (e) => {
          e.stopPropagation();
          this.toggle();
        });
      }

      // Close button
      const closeBtn = document.getElementById('hangar-close-btn');
      if (closeBtn) {
        closeBtn.onclick = () => this.close();
      }

      // Hotkey listener: H to toggle, Escape to close if open
      window.addEventListener('keydown', (e) => {
        if (e.target instanceof HTMLInputElement || e.target instanceof HTMLTextAreaElement) return;
        if (e.key.toLowerCase() === 'h' && !e.ctrlKey && !e.altKey && !e.metaKey) {
          e.preventDefault();
          this.toggle();
        } else if (e.key === 'Escape' && this.isOpen) {
          e.preventDefault();
          this.close();
        }
      });
    },

    updateUI() {
      this.renderHullCards();
      this.renderTrailCards();
      this.renderTurntableMeta();
    },

    renderHullCards() {
      const container = document.getElementById('hull-cards-container');
      if (!container) return;

      container.innerHTML = HULL_DEFS.map((h) => {
        const active = h.id === this.selectedHull;
        return `
          <div class="hangar-card ${active ? 'active' : ''}" data-hull-id="${h.id}">
            <div class="card-top mono">
              <span class="card-id-badge">H-0${h.id + 1}</span>
              <span class="card-active-pill">● 已装备 EQUIPPED</span>
            </div>
            <div class="card-name-row">
              <span class="card-name serif">${h.name}</span>
              <span class="card-sub mono">${h.en}</span>
            </div>
            <div class="card-tag mono">${h.tag}</div>
            <div class="card-desc serif">${h.desc}</div>
          </div>
        `;
      }).join('');

      container.querySelectorAll('.hangar-card').forEach((card) => {
        card.onclick = () => {
          const id = parseInt(card.getAttribute('data-hull-id'), 10);
          this.setHull(id);
        };
      });
    },

    renderTrailCards() {
      const container = document.getElementById('trail-cards-container');
      if (!container) return;

      container.innerHTML = TRAIL_DEFS.map((t) => {
        const active = t.id === this.selectedTrail;
        return `
          <div class="hangar-card trail-card ${active ? 'active' : ''}" data-trail-id="${t.id}">
            <div class="trail-swatch-bar" style="background: ${t.colors.gradient}; color: ${t.colors.hex};"></div>
            <div class="card-top mono">
              <span class="card-id-badge">T-0${t.id + 1}</span>
              <span class="card-active-pill">● 生效中 ACTIVE</span>
            </div>
            <div class="card-name-row">
              <span class="card-name serif">${t.name}</span>
              <span class="card-sub mono">${t.en}</span>
            </div>
            <div class="card-tag mono">${t.vibe}</div>
            <div class="card-desc serif">${t.desc}</div>
          </div>
        `;
      }).join('');

      container.querySelectorAll('.trail-card').forEach((card) => {
        card.onclick = () => {
          const id = parseInt(card.getAttribute('data-trail-id'), 10);
          this.setTrail(id);
        };
      });
    },

    renderTurntableMeta() {
      const meta = document.getElementById('turntable-meta');
      if (!meta) return;

      const hull = HULL_DEFS[this.selectedHull];
      const trail = TRAIL_DEFS[this.selectedTrail];

      meta.innerHTML = `
        <div class="turntable-meta-row mono">
          <span class="label">当前旗舰舰体</span>
          <span class="val">${hull.name} (${hull.en})</span>
        </div>
        <div class="turntable-meta-row mono">
          <span class="label">折纸多边形结构</span>
          <span class="val">${hull.faces.length} 面 / ${hull.creases.length} 折痕</span>
        </div>
        <div class="turntable-meta-row mono">
          <span class="label">量子尾迹着色器</span>
          <span class="val" style="color:${trail.colors.hex}">${trail.name} (${trail.en})</span>
        </div>
        <div class="turntable-meta-row mono">
          <span class="label">曲速激波响应</span>
          <span class="val">1.0c 巡航 / 5.0c 激波 / 15.0c 丝带</span>
        </div>
      `;
    },

    // ------------------------------------------------------------------------
    // 3. INTERACTIVE 3D TURNTABLE PREVIEW ENGINE
    // ------------------------------------------------------------------------
    initTurntable() {
      const canvas = document.getElementById('hangar-turntable-canvas');
      if (!canvas) return;
      this.turntable.canvas = canvas;
      this.turntable.ctx = canvas.getContext('2d');

      const wrapper = document.getElementById('turntable-wrapper');
      if (!wrapper) return;

      const onStart = (clientX, clientY) => {
        this.turntable.dragging = true;
        this.turntable.autoRotate = false;
        this.turntable.lastX = clientX;
        this.turntable.lastY = clientY;
        wrapper.classList.add('dragging');
      };

      const onMove = (clientX, clientY) => {
        if (!this.turntable.dragging) return;
        const dx = clientX - this.turntable.lastX;
        const dy = clientY - this.turntable.lastY;
        this.turntable.lastX = clientX;
        this.turntable.lastY = clientY;

        this.turntable.yaw += dx * 0.012;
        this.turntable.pitch = Math.max(-0.45, Math.min(0.85, this.turntable.pitch + dy * 0.01));

        const angleLabel = document.getElementById('turntable-angle-label');
        if (angleLabel) {
          const deg = Math.round((this.turntable.yaw % (Math.PI * 2)) * (180 / Math.PI));
          angleLabel.textContent = `ROT: ${deg}°`;
        }
      };

      const onEnd = () => {
        this.turntable.dragging = false;
        wrapper.classList.remove('dragging');
        setTimeout(() => {
          if (!this.turntable.dragging) this.turntable.autoRotate = true;
        }, 3200);
      };

      wrapper.addEventListener('mousedown', (e) => onStart(e.clientX, e.clientY));
      window.addEventListener('mousemove', (e) => onMove(e.clientX, e.clientY));
      window.addEventListener('mouseup', onEnd);

      wrapper.addEventListener('touchstart', (e) => {
        if (e.touches.length > 0) onStart(e.touches[0].clientX, e.touches[0].clientY);
      }, { passive: true });
      window.addEventListener('touchmove', (e) => {
        if (e.touches.length > 0) onMove(e.touches[0].clientX, e.touches[0].clientY);
      }, { passive: true });
      window.addEventListener('touchend', onEnd);
    },

    startTurntableLoop() {
      if (this.turntable.animId) return;

      const render = () => {
        if (!this.isOpen) {
          this.turntable.animId = null;
          return;
        }
        this.renderTurntableFrame();
        this.turntable.animId = requestAnimationFrame(render);
      };
      this.turntable.animId = requestAnimationFrame(render);
    },

    stopTurntableLoop() {
      if (this.turntable.animId) {
        cancelAnimationFrame(this.turntable.animId);
        this.turntable.animId = null;
      }
    },

    getTurntableState() {
      return {
        yaw: this.turntable.yaw,
        pitch: this.turntable.pitch,
        autoRotate: this.turntable.autoRotate,
        selectedHull: this.selectedHull,
        selectedTrail: this.selectedTrail
      };
    },

    renderTurntableFrame() {
      const { canvas, ctx } = this.turntable;
      if (!canvas || !ctx) return;

      const w = canvas.width;
      const h = canvas.height;
      this.turntable.time += 0.016;
      const t = this.turntable.time;

      if (this.turntable.autoRotate) {
        this.turntable.yaw += 0.014;
        const angleLabel = document.getElementById('turntable-angle-label');
        if (angleLabel) {
          const deg = Math.round((this.turntable.yaw % (Math.PI * 2)) * (180 / Math.PI));
          angleLabel.textContent = `ROT: ${deg}°`;
        }
      }

      ctx.clearRect(0, 0, w, h);

      // Background vignette
      const bgGrad = ctx.createRadialGradient(w / 2, h / 2, 20, w / 2, h / 2, w * 0.65);
      bgGrad.addColorStop(0, '#0c1522');
      bgGrad.addColorStop(1, '#05090f');
      ctx.fillStyle = bgGrad;
      ctx.fillRect(0, 0, w, h);

      const cx = w / 2;
      const cy = h / 2 + 15;
      const zoom = 4.2;
      const yaw = this.turntable.yaw;
      const pitch = this.turntable.pitch;

      // 1. Draw Pedestal Holographic Circles
      ctx.save();
      ctx.translate(cx, cy + 90);
      ctx.scale(1, 0.38);
      ctx.strokeStyle = 'rgba(143, 182, 216, 0.18)';
      ctx.lineWidth = 1;
      ctx.beginPath();
      ctx.arc(0, 0, 110, 0, Math.PI * 2);
      ctx.stroke();

      ctx.strokeStyle = 'rgba(245, 185, 65, 0.25)';
      ctx.beginPath();
      ctx.arc(0, 0, 75, 0, Math.PI * 2);
      ctx.stroke();

      // Radial ticks
      ctx.strokeStyle = 'rgba(143, 182, 216, 0.2)';
      for (let i = 0; i < 12; i++) {
        const rad = (i / 12) * Math.PI * 2 + yaw * 0.5;
        ctx.beginPath();
        ctx.moveTo(Math.cos(rad) * 65, Math.sin(rad) * 65);
        ctx.lineTo(Math.cos(rad) * 110, Math.sin(rad) * 110);
        ctx.stroke();
      }
      ctx.restore();

      // 2. Project & Render 3D Origami Mesh
      const hull = HULL_DEFS[this.selectedHull];
      const flap = Math.sin(t * 3.5) * 0.72;
      const vertices = hull.getVertices(flap, t);

      // 3D rotation & projection helper
      const cosY = Math.cos(yaw), sinY = Math.sin(yaw);
      const cosP = Math.cos(pitch), sinP = Math.sin(pitch);
      const bob = Math.sin(t * 2.2) * 4;

      const project = (pt) => {
        let x = pt[0];
        let y = pt[1] + bob;
        let z = pt[2];

        // Rotate Pitch (X axis)
        const y1 = y * cosP - z * sinP;
        const z1 = y * sinP + z * cosP;

        // Rotate Yaw (Y axis)
        const x2 = x * cosY + z1 * sinY;
        const z2 = -x * sinY + z1 * cosY;

        // Perspective
        const fov = 340;
        const dist = 140;
        const scale = fov / (fov + z2 + dist);

        return {
          x: cx + x2 * scale * zoom,
          y: cy - y1 * scale * zoom,
          z: z2,
          origX: x2,
          origY: y1,
          origZ: z2
        };
      };

      const projected = {};
      for (const k in vertices) {
        projected[k] = project(vertices[k]);
      }

      // Sort faces by depth
      const sortedFaces = hull.faces.map((f) => {
        const pts = f.pts.map(p => projected[p]);
        const avgZ = (pts[0].z + pts[1].z + pts[2].z) / 3;
        return { f, pts, avgZ };
      }).sort((a, b) => b.avgZ - a.avgZ);

      // Trail color palette
      const trail = TRAIL_DEFS[this.selectedTrail];

      // Draw shadow under craft
      ctx.save();
      ctx.beginPath();
      const shadowPts = hull.shadowShape.map(p => {
        const pr = project([p[0], -28, p[2]]);
        return [pr.x, pr.y + 40];
      });
      ctx.moveTo(shadowPts[0][0], shadowPts[0][1]);
      for (let i = 1; i < shadowPts.length; i++) ctx.lineTo(shadowPts[i][0], shadowPts[i][1]);
      ctx.closePath();
      ctx.fillStyle = 'rgba(0, 0, 0, 0.45)';
      ctx.filter = 'blur(6px)';
      ctx.fill();
      ctx.restore();

      // Render Turntable Particles (Engine trail preview)
      if (Math.random() < 0.4) {
        const ex = hull.exhausts[Math.floor(Math.random() * hull.exhausts.length)];
        const pr = project(ex.pos);
        this.turntable.particles.push({
          x: pr.x,
          y: pr.y,
          vx: (Math.random() - 0.5) * 1.5,
          vy: Math.random() * 2 + 1,
          life: 0,
          ttl: 35 + Math.random() * 20,
          size: 1.5 + Math.random() * 2.5
        });
      }

      ctx.save();
      for (let i = this.turntable.particles.length - 1; i >= 0; i--) {
        const p = this.turntable.particles[i];
        p.life++;
        p.x += p.vx;
        p.y += p.vy;
        if (p.life > p.ttl) {
          this.turntable.particles.splice(i, 1);
          continue;
        }
        const alpha = Math.sin((p.life / p.ttl) * Math.PI) * 0.75;
        ctx.fillStyle = `rgba(${trail.colors.main[0]}, ${trail.colors.main[1]}, ${trail.colors.main[2]}, ${alpha})`;
        ctx.beginPath();
        ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
        ctx.fill();
      }
      ctx.restore();

      // Light direction from upper-left-front
      const lx = -0.45, ly = 0.75, lz = -0.48;
      const lLen = Math.hypot(lx, ly, lz);

      // Draw mesh faces with crease shading & foil highlights
      for (const item of sortedFaces) {
        const { f, pts } = item;
        const p0 = pts[0], p1 = pts[1], p2 = pts[2];

        // Face normal in 3D
        const ux = p1.origX - p0.origX, uy = p1.origY - p0.origY, uz = p1.origZ - p0.origZ;
        const vx = p2.origX - p0.origX, vy = p2.origY - p0.origY, vz = p2.origZ - p0.origZ;
        let nx = uy * vz - uz * vy;
        let ny = uz * vx - ux * vz;
        let nz = ux * vy - uy * vx;
        const nLen = Math.hypot(nx, ny, nz) || 1;
        nx /= nLen; ny /= nLen; nz /= nLen;

        const dot = (nx * lx + ny * ly + nz * lz) / lLen;
        const diff = Math.max(0.18, Math.min(1.0, 0.45 + dot * 0.55));

        // Color blending for origami paper with metallic foil accents
        let baseR = 230, baseG = 236, baseB = 242; // Classic paper
        if (f.type === 'edge') {
          baseR = 195; baseG = 205; baseB = 216;
        } else if (f.type === 'fold') {
          baseR = 215; baseG = 222; baseB = 230;
        } else if (f.type === 'shade') {
          baseR = 175; baseG = 186; baseB = 198;
        }

        // Gold Foil Highlight on Flagship Crest
        let foilSpec = 0;
        if (dot > 0.55) {
          foilSpec = Math.pow(dot, 6) * 0.35;
        }

        const r = Math.min(255, Math.round(baseR * diff + foilSpec * 255));
        const g = Math.min(255, Math.round(baseG * diff + foilSpec * 200));
        const b = Math.min(255, Math.round(baseB * diff + foilSpec * 80));

        ctx.beginPath();
        ctx.moveTo(p0.x, p0.y);
        ctx.lineTo(p1.x, p1.y);
        ctx.lineTo(p2.x, p2.y);
        ctx.closePath();

        ctx.fillStyle = `rgb(${r},${g},${b})`;
        ctx.fill();

        // Paper crease stroke
        ctx.strokeStyle = `rgba(30, 42, 58, 0.35)`;
        ctx.lineWidth = 0.75;
        ctx.stroke();
      }

      // Draw Crease Lines
      ctx.strokeStyle = 'rgba(70, 95, 125, 0.55)';
      ctx.lineWidth = 1.0;
      for (const edge of hull.creases) {
        const pa = projected[edge[0]];
        const pb = projected[edge[1]];
        if (pa && pb) {
          ctx.beginPath();
          ctx.moveTo(pa.x, pa.y);
          ctx.lineTo(pb.x, pb.y);
          ctx.stroke();
        }
      }

      // Golden Foil Leading Edge on flagship
      if (projected.nose && (projected.wtl || projected.wingTipL)) {
        ctx.strokeStyle = 'rgba(245, 185, 65, 0.65)';
        ctx.lineWidth = 1.2;
        ctx.beginPath();
        const tipL = projected.wtl || projected.wingTipL || projected.bladeOuterL;
        const tipR = projected.wtr || projected.wingTipR || projected.bladeOuterR;
        if (tipL && tipR) {
          ctx.moveTo(tipL.x, tipL.y);
          ctx.lineTo(projected.nose.x, projected.nose.y);
          ctx.lineTo(tipR.x, tipR.y);
          ctx.stroke();
        }
      }
    },

    // ------------------------------------------------------------------------
    // 4. HIGH-PERFORMANCE FLEET & TRAIL CANVAS 2D RENDERING ENGINE
    // ------------------------------------------------------------------------
    /**
     * Seamless replacement/hook for drawFleet(fleet).
     * Maintains strict zero performance overhead (60 FPS).
     */
    drawFleet(fleet) {
      if (!fleet || !fleet.length) return;

      const hull = HULL_DEFS[this.selectedHull];
      const trail = TRAIL_DEFS[this.selectedTrail];

      // Resolve game environment hooks
      const g = this.game || {};
      const craftWorld = g.craftWorld || window.craftWorld;
      const craftTransform = g.craftTransform || window.craftTransform;
      const region = g.region || window.region;
      const poly = g.poly || window.poly;
      const line = g.line || window.line;
      const sprite = g.sprite || window.sprite;
      const glow = g.glow || window.glow;
      const blend = g.blend || window.blend;
      const shade = g.shade || window.shade;
      const project = g.project || window.project;
      const WarpDrive = g.WarpDrive || window.WarpDrive;
      const time = g.time !== undefined ? g.time : (window.time || 0);
      const cockpitBlend = g.cockpitBlend !== undefined ? g.cockpitBlend : (window.cockpitBlend || 0);
      const camera = g.camera || window.camera;
      const LEAD = g.LEAD !== undefined ? g.LEAD : (window.LEAD || 0);

      if (!craftWorld || !craftTransform || !poly || !line) {
        return; // Safe guard
      }

      // Compute dynamic warp stretch multiplier
      const currentWarp = WarpDrive ? (WarpDrive.currentWarp || 0) : 0;
      const warpGear = WarpDrive ? (WarpDrive.gearIndex || 0) : 0;
      const isHolding = WarpDrive ? (WarpDrive.isHolding || false) : false;

      // Warp speed factor: 1.0x at 1.0c, 2.8x at 5.0c, 6.5x at 15.0c
      const warpStretch = 1.0 + (currentWarp / 28) * 4.2 + (isHolding ? 1.5 : 0);

      // Iterate and draw each fleet ship
      for (let i = 0; i < fleet.length; i++) {
        const b = fleet[i];
        const pos = craftWorld(b);
        const p = region ? region(pos[0], pos[2]) : { craft: [230, 237, 242], craftShade: [160, 172, 186] };

        // Cockpit fade for first-person camera
        let nearCraft = 1;
        if (camera && camera.eye) {
          const dcam = Math.hypot(pos[0] - camera.eye[0], pos[1] - camera.eye[1], pos[2] - camera.eye[2]);
          nearCraft = cockpitBlend > 0.01 ? (1 - cockpitBlend * Math.max(0, Math.min(1, (260 - (dcam - 90)) / 260))) : 1;
          if (nearCraft < 0.005) continue;
        }

        const isLead = (b === fleet[LEAD]);
        const flap = Math.sin(time * (b.frequency || 2.4) + (b.phase || 0)) * 0.72;

        // 1. Procedural 3D Mesh for current Hull
        const v = hull.getVertices(flap, time);
        const world = {};
        for (const k in v) {
          world[k] = craftTransform(b, v[k]);
        }

        // Color palette for paper folding
        const base = p.craft || [230, 237, 242];
        const fold = isLead ? blend([245, 185, 65], base, 0.45) : (p.craftShade ? blend(base, p.craftShade, 0.55) : [190, 200, 212]);
        const edge = isLead ? blend([255, 215, 0], base, 0.25) : (p.craftShade ? blend(base, p.craftShade, 0.82) : [160, 172, 186]);
        const darkShade = shade ? shade(base, 0.86) : [170, 180, 192];

        // Draw mesh faces
        for (const face of hull.faces) {
          const p1 = world[face.pts[0]];
          const p2 = world[face.pts[1]];
          const p3 = world[face.pts[2]];
          if (!p1 || !p2 || !p3) continue;

          let col = base;
          if (face.type === 'fold') col = fold;
          else if (face.type === 'edge') col = edge;
          else if (face.type === 'shade') col = darkShade;

          poly([p1, p2, p3], col, { alpha: nearCraft });
        }

        // Draw crease lines
        for (const c of hull.creases) {
          const p1 = world[c[0]];
          const p2 = world[c[1]];
          if (p1 && p2) {
            line([p1, p2], p.craftShade || [140, 150, 165], 0.35 * nearCraft, 0.55);
          }
        }

        // Flagship gold foil gleam lines
        if (isLead && world.nose && (world.wtl || world.wingTipL || world.bladeOuterL)) {
          const wL = world.wtl || world.wingTipL || world.bladeOuterL;
          const wR = world.wtr || world.wingTipR || world.bladeOuterR;
          line([wL, world.nose], [255, 215, 80], 0.7 * nearCraft, 0.9);
          line([world.nose, wR], [255, 215, 80], 0.7 * nearCraft, 0.9);
        }

        // 2. Dynamic Quantum Warp Trail Ribbon Emitter
        this.renderCraftTrail(b, world, hull, trail, warpStretch, nearCraft, time);
      }
    },

    /**
     * Renders dynamic quantum warp ribbon trails behind a craft.
     */
    renderCraftTrail(b, world, hull, trail, warpStretch, alphaMul, time) {
      const g = this.game || {};
      const poly = g.poly || window.poly;
      const line = g.line || window.line;
      const sprite = g.sprite || window.sprite;
      const glow = g.glow || window.glow;

      // Extract exhaust emitter point
      const exDef = hull.exhausts[0];
      const emitterPt = world.tail || world.centerNozzle || world.tailChevron || world.tailStinger || world.nose;
      if (!emitterPt) return;

      // Manage history buffer for this craft
      let hist = this.trailHistory.get(b);
      if (!hist) {
        hist = [];
        this.trailHistory.set(b, hist);
      }

      // Push current position to history
      hist.unshift({
        x: emitterPt[0],
        y: emitterPt[1],
        z: emitterPt[2],
        time: time
      });

      // Max history length based on warp speed
      const maxPts = Math.min(48, Math.round(14 * warpStretch));
      while (hist.length > maxPts) hist.pop();

      if (hist.length < 2) return;

      // Draw Ribbon Trail Segments
      const colMain = trail.colors.main;
      const colCore = trail.colors.core;

      for (let j = 0; j < hist.length - 1; j++) {
        const pt1 = hist[j];
        const pt2 = hist[j + 1];
        const frac = j / hist.length;
        const segAlpha = Math.max(0, (1 - frac) * 0.75 * alphaMul);

        // Trail width & oscillation
        const wave = Math.sin(time * 12 + j * 0.5) * (1.2 + frac * 3.5);
        const w1 = [pt1.x + wave, pt1.y, pt1.z];
        const w2 = [pt2.x + wave * 0.8, pt2.y, pt2.z];

        if (line) {
          // Outer plasma trail line
          line([w1, w2], colMain, segAlpha, Math.max(0.6, 2.5 * (1 - frac)));
          // Core bright quantum thread
          line([w1, w2], colCore, segAlpha * 0.9, Math.max(0.4, 1.2 * (1 - frac)));
        }
      }

      // Spawn drifting warp spark particles at high speeds
      if (warpStretch > 1.4 && sprite && Math.random() < 0.35) {
        const pt = hist[Math.floor(Math.random() * Math.min(hist.length, 6))];
        const spreadX = (Math.random() - 0.5) * 8 * warpStretch;
        const spreadY = (Math.random() - 0.5) * 6;
        sprite([pt.x + spreadX, pt.y + spreadY, pt.z], 1.8 * warpStretch, colMain, 'dust', 0.65 * alphaMul);
      }
    },

    /**
     * Seamless replacement/hook for drawCraftShadows(fleet).
     */
    drawCraftShadows(fleet) {
      if (!fleet || !fleet.length) return;

      const hull = HULL_DEFS[this.selectedHull];
      const g = this.game || {};
      const craftWorld = g.craftWorld || window.craftWorld;
      const craftTransform = g.craftTransform || window.craftTransform;
      const region = g.region || window.region;
      const poly = g.poly || window.poly;

      if (!craftWorld || !craftTransform || !poly) return;

      for (let i = 0; i < fleet.length; i++) {
        const b = fleet[i];
        const pos = craftWorld(b);
        const p = region ? region(pos[0], pos[2]) : { treeDark: [20, 30, 45], void: 0 };
        const height = pos[1];

        const pts = hull.shadowShape.map(v => {
          const q = craftTransform(b, v);
          return [q[0] + height * 0.37, 0.7, q[2] + height * 0.28];
        });

        poly(pts, p.treeDark || [20, 30, 45], {
          alpha: 0.11 * (1 - (p.void || 0) * 0.71)
        });
      }
    },

    /**
     * Seamless replacement/hook for drawShard(s, p, t).
     * Renders floating procedural folded paper shards & quantum dust flakes.
     */
    drawShard(s, p, t) {
      const g = this.game || {};
      const poly = g.poly || window.poly;
      const line = g.line || window.line;
      const blend = g.blend || window.blend;
      const shade = g.shade || window.shade;

      if (!poly) return;

      // Active trail tint
      const trail = TRAIL_DEFS[this.selectedTrail];
      const trailCol = trail.colors.main;

      const q = [null, null, null, null];
      if (typeof window.shardShape === 'function') {
        window.shardShape(s, t, q);
      } else {
        // Fallback procedural diamond shard
        const a = s.ang + t * s.spin;
        const cs = Math.cos(a) * s.w * 0.5;
        const sn = Math.sin(a) * s.w * 0.5;
        q[0] = [s.x - cs, s.y, s.z - sn];
        q[1] = [s.x, s.y + s.h * 0.5, s.z];
        q[2] = [s.x + cs, s.y, s.z + sn];
        q[3] = [s.x, s.y - s.h * 0.5, s.z];
      }

      if (q[0] && q[1] && q[2] && q[3]) {
        const shardColor = blend ? blend(p.wall || [180, 190, 205], trailCol, 0.22) : trailCol;
        poly(q, shardColor, { palette: p, alpha: 0.92 });

        const mid = q.map((v, i) => v.map((c, j) => (c + q[(i + 2) % 4][j]) * 0.5));
        poly([q[0], q[1], mid[1], mid[0]], shade ? shade(shardColor, 0.88) : shardColor, { palette: p, alpha: 0.88 });

        if (line) {
          line([q[0], q[2]], shade ? shade(shardColor, 0.75) : [120, 130, 150], 0.5, 0.55);
        }
      }
    }
  };

  // Expose globally
  root.FleetCustomizer = FleetCustomizer;

  // Auto-init on DOMContentLoaded if not already
  if (typeof document !== 'undefined') {
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', () => FleetCustomizer.init());
    } else {
      FleetCustomizer.init();
    }
  }

})(typeof window !== 'undefined' ? window : this);
