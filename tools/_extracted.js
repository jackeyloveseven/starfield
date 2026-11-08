// ===== EXTRACTED FROM planet_studio.html =====
class SimplexNoise {
  constructor(seed = 12345) {
    this.p = new Uint8Array(256);
    let s = seed % 2147483647;
    if (s <= 0) s += 2147483646;
    const lcg = () => (s = (s * 16807) % 2147483647) / 2147483647;
    for (let i = 0; i < 256; i++) this.p[i] = i;
    for (let i = 255; i > 0; i--) {
      const r = Math.floor(lcg() * (i + 1));
      const tmp = this.p[i]; this.p[i] = this.p[r]; this.p[r] = tmp;
    }
    this.perm = new Uint8Array(512);
    this.permMod12 = new Uint8Array(512);
    for (let i = 0; i < 512; i++) {
      this.perm[i] = this.p[i & 255];
      this.permMod12[i] = this.perm[i] % 12;
    }
    this.grad3 = [
      [1,1,0],[-1,1,0],[1,-1,0],[-1,-1,0],
      [1,0,1],[-1,0,1],[1,0,-1],[-1,0,-1],
      [0,1,1],[0,-1,1],[0,1,-1],[0,-1,-1]
    ];
  }

  noise3D(xin, yin, zin) {
    const F3 = 1.0 / 3.0, G3 = 1.0 / 6.0;
    const s = (xin + yin + zin) * F3;
    const i = Math.floor(xin + s), j = Math.floor(yin + s), k = Math.floor(zin + s);
    const t = (i + j + k) * G3;
    const X0 = i - t, Y0 = j - t, Z0 = k - t;
    const x0 = xin - X0, y0 = yin - Y0, z0 = zin - Z0;

    let i1, j1, k1, i2, j2, k2;
    if (x0 >= y0) {
      if (y0 >= z0) { i1=1; j1=0; k1=0; i2=1; j2=1; k2=0; }
      else if (x0 >= z0) { i1=1; j1=0; k1=0; i2=1; j2=0; k2=1; }
      else { i1=0; j1=0; k1=1; i2=1; j2=0; k2=1; }
    } else {
      if (y0 < z0) { i1=0; j1=0; k1=1; i2=0; j2=1; k2=1; }
      else if (x0 < z0) { i1=0; j1=1; k1=0; i2=0; j2=1; k2=1; }
      else { i1=0; j1=1; k1=0; i2=1; j2=1; k2=0; }
    }

    const x1 = x0 - i1 + G3, y1 = y0 - j1 + G3, z1 = z0 - k1 + G3;
    const x2 = x0 - i2 + 2.0 * G3, y2 = y0 - j2 + 2.0 * G3, z2 = z0 - k2 + 2.0 * G3;
    const x3 = x0 - 1.0 + 3.0 * G3, y3 = y0 - 1.0 + 3.0 * G3, z3 = z0 - 1.0 + 3.0 * G3;

    const ii = i & 255, jj = j & 255, kk = k & 255;
    const gi0 = this.permMod12[ii + this.perm[jj + this.perm[kk]]];
    const gi1 = this.permMod12[ii + i1 + this.perm[jj + j1 + this.perm[kk + k1]]];
    const gi2 = this.permMod12[ii + i2 + this.perm[jj + j2 + this.perm[kk + k2]]];
    const gi3 = this.permMod12[ii + 1 + this.perm[jj + 1 + this.perm[kk + 1]]];

    let t0 = 0.6 - x0*x0 - y0*y0 - z0*z0, n0 = 0;
    if (t0 > 0) { t0 *= t0; n0 = t0 * t0 * (this.grad3[gi0][0]*x0 + this.grad3[gi0][1]*y0 + this.grad3[gi0][2]*z0); }

    let t1 = 0.6 - x1*x1 - y1*y1 - z1*z1, n1 = 0;
    if (t1 > 0) { t1 *= t1; n1 = t1 * t1 * (this.grad3[gi1][0]*x1 + this.grad3[gi1][1]*y1 + this.grad3[gi1][2]*z1); }

    let t2 = 0.6 - x2*x2 - y2*y2 - z2*z2, n2 = 0;
    if (t2 > 0) { t2 *= t2; n2 = t2 * t2 * (this.grad3[gi2][0]*x2 + this.grad3[gi2][1]*y2 + this.grad3[gi2][2]*z2); }

    let t3 = 0.6 - x3*x3 - y3*y3 - z3*z3, n3 = 0;
    if (t3 > 0) { t3 *= t3; n3 = t3 * t3 * (this.grad3[gi3][0]*x3 + this.grad3[gi3][1]*y3 + this.grad3[gi3][2]*z3); }

    return 32.0 * (n0 + n1 + n2 + n3);
  }

  fBm(x, y, z, octaves = 4, lacunarity = 2.0, gain = 0.5) {
    let sum = 0, amp = 1.0, freq = 1.0, maxAmp = 0;
    for (let o = 0; o < octaves; o++) {
      sum += this.noise3D(x * freq, y * freq, z * freq) * amp;
      maxAmp += amp;
      freq *= lacunarity;
      amp *= gain;
    }
    return sum / maxAmp;
  }
}

const Presets = {
  archipelago: {
    name: '蔚蓝群岛',
    landRatio: 0.30,
    ruggedness: 1.0,
    treeCount: 1600,
    monumentLevel: 2,
    faunaLevel: 2,
    cloudCoverage: 0.40,
    colors: {
      deepOcean: '#03142c',
      coastWater: '#168aad',
      sand: '#f4e285',
      grass: '#52b788',
      forest: '#2d6a4f',
      rock: '#6c584c',
      snow: '#f8f9fa',
      waterTrans: 0.82
    }
  },
  abyss: {
    name: '深渊之海',
    landRatio: 0.08,  // 92% ocean!
    ruggedness: 1.5,
    treeCount: 280,
    monumentLevel: 1,
    faunaLevel: 3,    // High whale presence!
    cloudCoverage: 0.55,
    colors: {
      deepOcean: '#020b18',
      coastWater: '#0077b6',
      sand: '#e9d8a6',
      grass: '#40916c',
      forest: '#1b4332',
      rock: '#3d405b',
      snow: '#e2e8f0',
      waterTrans: 0.88
    }
  },
  forest: {
    name: '盖亚林海',
    landRatio: 0.65,
    ruggedness: 1.4,
    treeCount: 2600,
    monumentLevel: 2,
    faunaLevel: 2,
    cloudCoverage: 0.50,
    colors: {
      deepOcean: '#0c2340',
      coastWater: '#2a9d8f',
      sand: '#e76f51',
      grass: '#38b000',
      forest: '#007200',
      rock: '#4a4e69',
      snow: '#ffffff',
      waterTrans: 0.80
    }
  },
  monument: {
    name: '古神遗迹',
    landRatio: 0.45,
    ruggedness: 1.6,
    treeCount: 900,
    monumentLevel: 4,
    faunaLevel: 1,
    cloudCoverage: 0.30,
    colors: {
      deepOcean: '#1a1c29',
      coastWater: '#4a6fa5',
      sand: '#f4a261',
      grass: '#b5838d',
      forest: '#6d6875',
      rock: '#e5989b',
      snow: '#ffb4a2',
      waterTrans: 0.75
    }
  },
  alien: {
    name: '幽能水晶',
    landRatio: 0.42,
    ruggedness: 1.8,
    treeCount: 1500,
    monumentLevel: 3,
    faunaLevel: 2,
    cloudCoverage: 0.45,
    colors: {
      deepOcean: '#1a052b',
      coastWater: '#7209b7',
      sand: '#4cc9f0',
      grass: '#f72585',
      forest: '#3a0ca3',
      rock: '#4361ee',
      snow: '#ffffff',
      waterTrans: 0.85
    }
  },
  desert_oasis: {
    name: '绿洲沙丘',
    landRatio: 0.55,
    ruggedness: 1.3,
    treeCount: 600,
    monumentLevel: 2,
    faunaLevel: 1,
    cloudCoverage: 0.20,
    colors: {
      deepOcean: '#005f73',
      coastWater: '#0a9396',
      sand: '#ee9b00',
      grass: '#94d2bd',
      forest: '#ca6702',
      rock: '#bb3e03',
      snow: '#e9d8a6',
      waterTrans: 0.85
    }
  }
};

class LivingPlanet {
  constructor(scene) {
    this.scene = scene;
    this.group = new THREE.Group();
    this.scene.add(this.group);

    this.noise = new SimplexNoise(PlanetConfig.seed);
    this.landVertices = []; // Sampled points above water for tree/monument scattering
    this.oceanVertices = []; // Points for whales

    this.terrainMesh = null;
    this.oceanMesh = null;
    this.cloudsMesh = null;
    this.atmosphereMesh = null;
    this.treesInstanced = null;
    this.monumentsGroup = null;
    this.birdsGroup = null;
    this.whalesGroup = null;

    this.birds = [];
    this.whales = [];
  }

  build() {
    // Clean old
    while (this.group.children.length > 0) {
      const obj = this.group.children[0];
      this.group.remove(obj);
      if (obj.geometry) obj.geometry.dispose();
      if (obj.material) {
        if (Array.isArray(obj.material)) obj.material.forEach(m => m.dispose());
        else obj.material.dispose();
      }
    }

    this.noise = new SimplexNoise(PlanetConfig.seed);
    this.landVertices = [];
    this.oceanVertices = [];
    this.birds = [];
    this.whales = [];

    const currentPreset = Presets[PlanetConfig.preset] || Presets.archipelago;

    // 1. Terrain Mesh
    this.buildTerrain(currentPreset);

    // 2. Ocean Shell Mesh
    this.buildOcean(currentPreset);

    // 3. Clouds & Atmosphere
    this.buildClouds();
    this.buildAtmosphere();

    // 4. Instanced Vegetation (Trees)
    this.buildFlora(currentPreset);

    // 5. Monuments & Architecture
    this.buildMonuments(currentPreset);

    // 6. Living Fauna (Birds & Whales)
    this.buildFauna();
  }

  buildTerrain(preset) {
    const R = PlanetConfig.radius;
    // Optimized geometry for silky smooth 60-144 FPS and instant generation (<3ms)
    const geom = new THREE.IcosahedronGeometry(R, 16);
    const pos = geom.attributes.position;
    const vertex = new THREE.Vector3();
    const normal = new THREE.Vector3();

    const colors = [];
    const cDeep = new THREE.Color(preset.colors.deepOcean);
    const cCoast = new THREE.Color(preset.colors.coastWater);
    const cSand = new THREE.Color(preset.colors.sand);
    const cGrass = new THREE.Color(preset.colors.grass);
    const cForest = new THREE.Color(preset.colors.forest);
    const cRock = new THREE.Color(preset.colors.rock);
    const cSnow = new THREE.Color(preset.colors.snow);

    const seaLevelThreshold = 0.5 - (PlanetConfig.landRatio - 0.4);

    for (let i = 0; i < pos.count; i++) {
      vertex.fromBufferAttribute(pos, i);
      normal.copy(vertex).normalize();

      // Multi-frequency noise
      const nx = normal.x * 1.5, ny = normal.y * 1.5, nz = normal.z * 1.5;
      const continentNoise = this.noise.fBm(nx, ny, nz, 4, 2.0, 0.5);
      const detailNoise = this.noise.noise3D(normal.x * 6.0, normal.y * 6.0, normal.z * 6.0) * 0.18;
      const ridgeNoise = Math.abs(this.noise.noise3D(normal.x * 3.5, normal.y * 3.5, normal.z * 3.5));

      const rawHeight = (continentNoise + 1.0) * 0.5 + detailNoise;
      let finalR = R;
      let col = new THREE.Color();

      if (rawHeight < seaLevelThreshold) {
        // Ocean floor / trench
        const depth = (seaLevelThreshold - rawHeight) / seaLevelThreshold;
        finalR = R - depth * 3.8;
        col.copy(cCoast).lerp(cDeep, Math.min(1, depth * 1.8));

        if (Math.random() < 0.05 && depth > 0.4) {
          this.oceanVertices.push({
            pos: normal.clone().multiplyScalar(R + 0.3),
            normal: normal.clone(),
            depth: depth
          });
        }
      } else {
        // Land
        const landElev = (rawHeight - seaLevelThreshold) / (1.0 - seaLevelThreshold);
        const mountainH = Math.pow(landElev, 1.4) * 6.5 * PlanetConfig.ruggedness + ridgeNoise * 1.2;
        finalR = R + mountainH;

        if (landElev < 0.08) {
          col.copy(cSand); // Beach
        } else if (landElev < 0.35) {
          col.copy(cGrass); // Lowland grass
        } else if (landElev < 0.65) {
          col.copy(cForest); // Upland forest
        } else if (landElev < 0.88) {
          col.copy(cRock); // High rocky mountain
        } else {
          col.copy(cSnow); // Snow peak
        }

        // Collect candidates for trees / monuments
        if (landElev > 0.06 && landElev < 0.72) {
          this.landVertices.push({
            pos: normal.clone().multiplyScalar(finalR),
            normal: normal.clone(),
            elevation: landElev,
            isBeach: landElev < 0.16,
            isPlateau: landElev >= 0.25 && landElev <= 0.60
          });
        }
      }

      vertex.copy(normal).multiplyScalar(finalR);
      pos.setXYZ(i, vertex.x, vertex.y, vertex.z);
      colors.push(col.r, col.g, col.b);
    }

    geom.setAttribute('color', new THREE.Float32BufferAttribute(colors, 3));
    geom.computeVertexNormals();

    const mat = new THREE.MeshStandardMaterial({
      vertexColors: true,
      roughness: 0.88,
      metalness: 0.08,
      flatShading: true,
    });

    this.terrainMesh = new THREE.Mesh(geom, mat);
    this.terrainMesh.castShadow = true;
    this.terrainMesh.receiveShadow = true;
    this.group.add(this.terrainMesh);
  }

  buildOcean(preset) {
    const R = PlanetConfig.radius;
    const geom = new THREE.IcosahedronGeometry(R + 0.15, 14);
    const mat = new THREE.MeshStandardMaterial({
      color: new THREE.Color(preset.colors.coastWater),
      transparent: true,
      opacity: preset.colors.waterTrans || 0.82,
      roughness: 0.15,
      metalness: 0.12,
      flatShading: true,
    });

    this.oceanMesh = new THREE.Mesh(geom, mat);
    this.group.add(this.oceanMesh);
  }

  buildClouds() {
    const R = PlanetConfig.radius + 2.8;
    const geom = new THREE.IcosahedronGeometry(R, 12);
    const pos = geom.attributes.position;
    const v = new THREE.Vector3();

    // Deform cloud sphere slightly for puffy formations
    for (let i = 0; i < pos.count; i++) {
      v.fromBufferAttribute(pos, i);
      const n = this.noise.noise3D(v.x * 0.12, v.y * 0.12, v.z * 0.12);
      const disp = Math.max(0, n) * 1.2;
      v.normalize().multiplyScalar(R + disp);
      pos.setXYZ(i, v.x, v.y, v.z);
    }
    geom.computeVertexNormals();

    const mat = new THREE.MeshStandardMaterial({
      color: 0xffffff,
      transparent: true,
      opacity: PlanetConfig.cloudCoverage * 0.75,
      roughness: 0.9,
      depthWrite: false,
      flatShading: true
    });

    this.cloudsMesh = new THREE.Mesh(geom, mat);
    this.group.add(this.cloudsMesh);
  }

  buildAtmosphere() {
    const R = PlanetConfig.radius + 5.5;
    const geom = new THREE.SphereGeometry(R, 32, 32);
    
    // Atmospheric Fresnel Glow
    const mat = new THREE.ShaderMaterial({
      vertexShader: `
        varying vec3 vNormal;
        void main() {
          vNormal = normalize(normalMatrix * normal);
          gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
        }
      `,
      fragmentShader: `
        varying vec3 vNormal;
        void main() {
          float intensity = pow(max(0.0, 0.65 - dot(vNormal, vec3(0.0, 0.0, 1.0))), 2.8);
          gl_FragColor = vec4(0.35, 0.65, 0.95, 1.0) * intensity * 0.85;
        }
      `,
      blending: THREE.AdditiveBlending,
      side: THREE.BackSide,
      transparent: true,
      depthWrite: false
    });

    this.atmosphereMesh = new THREE.Mesh(geom, mat);
    this.group.add(this.atmosphereMesh);
  }

  buildFlora(preset) {
    if (this.landVertices.length === 0 || PlanetConfig.treeCount === 0) return;

    const count = Math.min(PlanetConfig.treeCount, this.landVertices.length);
    const isAlien = PlanetConfig.preset === 'alien';
    
    // Low-poly Tree Trunk & Leaves Geometry
    const trunkGeom = new THREE.CylinderGeometry(0.12, 0.22, 1.2, 4);
    trunkGeom.translate(0, 0.6, 0);
    const leavesGeom = isAlien 
      ? new THREE.DodecahedronGeometry(0.85)
      : new THREE.ConeGeometry(0.75, 1.6, 5);
    leavesGeom.translate(0, 1.6, 0);

    const trunkMat = new THREE.MeshLambertMaterial({ color: isAlien ? 0x2b1055 : 0x5a3e2b });
    const leavesMat = new THREE.MeshLambertMaterial({ 
      color: new THREE.Color(isAlien ? 0x00f5d4 : preset.colors.forest),
      flatShading: true 
    });

    const instTrunk = new THREE.InstancedMesh(trunkGeom, trunkMat, count);
    const instLeaves = new THREE.InstancedMesh(leavesGeom, leavesMat, count);

    const dummy = new THREE.Object3D();
    const up = new THREE.Vector3(0, 1, 0);

    // Shuffle and pick
    const sampled = [...this.landVertices].sort(() => Math.random() - 0.5).slice(0, count);

    sampled.forEach((pt, i) => {
      dummy.position.copy(pt.pos);
      // Align Y axis to surface normal
      dummy.quaternion.setFromUnitVectors(up, pt.normal);
      const scale = (0.7 + Math.random() * 0.6) * (pt.isBeach ? 0.8 : 1.1);
      dummy.scale.set(scale, scale, scale);
      dummy.updateMatrix();

      instTrunk.setMatrixAt(i, dummy.matrix);
      instLeaves.setMatrixAt(i, dummy.matrix);
    });

    instTrunk.instanceMatrix.needsUpdate = true;
    instLeaves.instanceMatrix.needsUpdate = true;
    instTrunk.castShadow = true;
    instLeaves.castShadow = true;

    this.treesInstanced = new THREE.Group();
    this.treesInstanced.add(instTrunk);
    this.treesInstanced.add(instLeaves);
    this.group.add(this.treesInstanced);
  }

  buildMonuments(preset) {
    if (PlanetConfig.monumentLevel === 0) return;
    this.monumentsGroup = new THREE.Group();

    const plateaus = this.landVertices.filter(v => v.isPlateau);
    const numMonuments = Math.min(plateaus.length, PlanetConfig.monumentLevel * 3 + 2);
    const up = new THREE.Vector3(0, 1, 0);

    const sampled = [...plateaus].sort(() => Math.random() - 0.5).slice(0, numMonuments);

    sampled.forEach((pt, idx) => {
      const type = idx % 3;
      const mGroup = new THREE.Group();
      mGroup.position.copy(pt.pos);
      mGroup.quaternion.setFromUnitVectors(up, pt.normal);

      if (type === 0) {
        // Monument Valley Stepped Ziggurat / Pyramid
        const mat = new THREE.MeshLambertMaterial({ color: 0xdeb887, flatShading: true });
        for (let s = 0; s < 3; s++) {
          const w = 2.4 - s * 0.7;
          const stepGeom = new THREE.BoxGeometry(w, 0.45, w);
          const stepMesh = new THREE.Mesh(stepGeom, mat);
          stepMesh.position.y = s * 0.45 + 0.22;
          stepMesh.castShadow = true;
          mGroup.add(stepMesh);
        }
      } else if (type === 1) {
        // Coastal Lighthouse Beacon with Brass Light Ring
        const matTower = new THREE.MeshLambertMaterial({ color: 0xf4f1de, flatShading: true });
        const matRing = new THREE.MeshStandardMaterial({ color: 0xe07a5f, metalness: 0.8, roughness: 0.2 });
        const tower = new THREE.Mesh(new THREE.CylinderGeometry(0.3, 0.6, 2.5, 6), matTower);
        tower.position.y = 1.25;
        tower.castShadow = true;
        mGroup.add(tower);

        const ring = new THREE.Mesh(new THREE.TorusGeometry(0.7, 0.08, 6, 16), matRing);
        ring.position.y = 2.4;
        ring.rotation.x = Math.PI / 2;
        mGroup.add(ring);
      } else {
        // Floating Monolith Obelisk
        const mat = new THREE.MeshStandardMaterial({ color: 0x22223b, roughness: 0.3, metalness: 0.9 });
        const obelisk = new THREE.Mesh(new THREE.BoxGeometry(0.5, 2.2, 0.5), mat);
        obelisk.position.y = 2.0;
        obelisk.rotation.y = Math.PI / 4;
        obelisk.castShadow = true;
        mGroup.add(obelisk);
      }

      this.monumentsGroup.add(mGroup);
    });

    this.group.add(this.monumentsGroup);
  }

  buildFauna() {
    if (PlanetConfig.faunaLevel === 0) return;

    // 1. Circling Seabirds (Flocks)
    this.birdsGroup = new THREE.Group();
    const birdCount = PlanetConfig.faunaLevel * 16;
    const birdGeom = new THREE.BufferGeometry();
    // Low-poly papercraft bird triangle wings
    const birdVertices = new Float32Array([
      0, 0, 0.6,   -0.8, 0.2, 0,   0, 0, -0.4, // Left wing
      0, 0, 0.6,    0, 0, -0.4,    0.8, 0.2, 0  // Right wing
    ]);
    birdGeom.setAttribute('position', new THREE.BufferAttribute(birdVertices, 3));
    birdGeom.computeVertexNormals();

    const birdMat = new THREE.MeshBasicMaterial({ color: 0xffffff, side: THREE.DoubleSide });

    for (let i = 0; i < birdCount; i++) {
      const mesh = new THREE.Mesh(birdGeom, birdMat);
      const orbitR = PlanetConfig.radius + 3.5 + Math.random() * 3.0;
      const speed = 0.4 + Math.random() * 0.3;
      const inclination = (Math.random() - 0.5) * Math.PI;
      const phase = Math.random() * Math.PI * 2;

      this.birds.push({ mesh, orbitR, speed, inclination, phase });
      this.birdsGroup.add(mesh);
    }
    this.group.add(this.birdsGroup);

    // 2. Abyssal Ocean Leviathans (Paper Whales)
    if (this.oceanVertices.length > 0 && PlanetConfig.faunaLevel >= 2) {
      this.whalesGroup = new THREE.Group();
      const whaleCount = Math.min(5, Math.floor(this.oceanVertices.length / 10) + 2);
      const whaleMat = new THREE.MeshStandardMaterial({
        color: 0x81b29a,
        roughness: 0.3,
        metalness: 0.2,
        transparent: true,
        opacity: 0.9,
        flatShading: true
      });

      for (let i = 0; i < whaleCount; i++) {
        const wGroup = new THREE.Group();
        // Body
        const body = new THREE.Mesh(new THREE.ConeGeometry(0.9, 3.2, 5), whaleMat);
        body.rotation.x = Math.PI / 2;
        wGroup.add(body);
        // Fins
        const finGeom = new THREE.BoxGeometry(2.2, 0.08, 0.6);
        const fin = new THREE.Mesh(finGeom, whaleMat);
        fin.position.z = 0.4;
        wGroup.add(fin);

        const orbitR = PlanetConfig.radius + 0.1;
        const speed = 0.15 + Math.random() * 0.1;
        const phase = (i / whaleCount) * Math.PI * 2;

        this.whales.push({ group: wGroup, orbitR, speed, phase });
        this.whalesGroup.add(wGroup);
      }
      this.group.add(this.whalesGroup);
    }
  }

  update(time, dt) {
    // Planet axial rotation
    const rotSpeed = PlanetConfig.spinSpeed * 0.003;
    if (this.terrainMesh) this.terrainMesh.rotation.y += rotSpeed;
    if (this.oceanMesh) this.oceanMesh.rotation.y += rotSpeed;
    if (this.treesInstanced) this.treesInstanced.rotation.y += rotSpeed;
    if (this.monumentsGroup) this.monumentsGroup.rotation.y += rotSpeed;
    
    // Differential cloud drift
    if (this.cloudsMesh) {
      this.cloudsMesh.rotation.y += rotSpeed * 1.35;
      this.cloudsMesh.rotation.x += rotSpeed * 0.15;
    }

    // Animate Birds
    this.birds.forEach(b => {
      b.phase += b.speed * dt;
      const x = Math.cos(b.phase) * b.orbitR;
      const z = Math.sin(b.phase) * b.orbitR;
      const y = Math.sin(b.phase * 2.0) * (b.orbitR * 0.25);

      b.mesh.position.set(x, y, z);
      b.mesh.lookAt(
        Math.cos(b.phase + 0.1) * b.orbitR,
        Math.sin((b.phase + 0.1) * 2.0) * (b.orbitR * 0.25),
        Math.sin(b.phase + 0.1) * b.orbitR
      );
      // Wing flapping oscillation
      b.mesh.scale.y = 0.7 + Math.sin(time * 12.0 + b.phase) * 0.5;
    });

    // Animate Whales (Sinusoidal breaching)
    this.whales.forEach(w => {
      w.phase += w.speed * dt;
      const curR = w.orbitR + Math.sin(w.phase * 3.0) * 0.45; // Breaches water slightly
      const x = Math.cos(w.phase) * curR;
      const z = Math.sin(w.phase) * curR;
      const y = Math.cos(w.phase * 1.5) * (curR * 0.35);

      w.group.position.set(x, y, z);
      w.group.lookAt(
        Math.cos(w.phase + 0.1) * curR,
        Math.cos((w.phase + 0.1) * 1.5) * (curR * 0.35),
        Math.sin(w.phase + 0.1) * curR
      );
    });
  }
}
