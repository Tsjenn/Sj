/* =====================================================================
   WILDHAVEN: CREATURE PARK — a cozy 3D catch-and-build tycoon
   Original game & creatures, same universe as Critter Isles.
   Built with Three.js (r128, vendored) + procedural WebAudio sound.
   ===================================================================== */
(function () {
  "use strict";

  var CFG = window.GAME_CONFIG || { mode: "full", buyLink: "" };
  var IS_DEMO = CFG.mode === "demo";
  if (IS_DEMO) document.body.classList.add("demo");
  var SAVE_KEY = "wildhaven-" + CFG.mode + "-v1";

  // ------------------------------------------------------------- species
  var SPECIES = [
    { id: "flufftail",  name: "Flufftail",  biome: "meadow", color: 0x7ec850, accent: 0xe8f5d0, size: 1.0,  speed: 2.2, catchRate: 0.75, income: 1, far: 0,   hint: "Meadow hopper. Loves flowers." },
    { id: "pebblit",    name: "Pebblit",    biome: "meadow", color: 0x8d8d94, accent: 0xc9c9cf, size: 0.8,  speed: 1.2, catchRate: 0.75, income: 1, far: 0,   hint: "Naps beside rocks." },
    { id: "aquaphin",   name: "Aquaphin",   biome: "water",  color: 0x4aa8d8, accent: 0xbfe6f5, size: 1.0,  speed: 2.6, catchRate: 0.6,  income: 2, far: 0,   hint: "Splashes near the shore." },
    { id: "emberling",  name: "Emberling",  biome: "ember",  color: 0xe07030, accent: 0xffc84a, size: 0.9,  speed: 2.8, catchRate: 0.55, income: 2, far: 60,  hint: "A warm glow inland." },
    { id: "mossback",   name: "Mossback",   biome: "meadow", color: 0x5d7a45, accent: 0x9fb56e, size: 1.3,  speed: 0.9, catchRate: 0.7,  income: 2, far: 40,  hint: "Slow, sturdy, moss-covered." },
    { id: "bubbletide", name: "Bubbletide", biome: "water",  color: 0x6fc4c9, accent: 0xffffff, size: 0.75, speed: 3.0, catchRate: 0.55, income: 3, far: 80,  hint: "Blows bubbles at dawn." },
    { id: "zephyrix",   name: "Zephyrix",   biome: "sky",    color: 0xe8c832, accent: 0xffffff, size: 0.85, speed: 4.2, catchRate: 0.45, income: 3, far: 100, hint: "Fast as the wind." },
    { id: "cinderpup",  name: "Cinderpup",  biome: "ember",  color: 0xb84a3a, accent: 0xffa64a, size: 0.9,  speed: 3.4, catchRate: 0.45, income: 4, far: 120, hint: "Sparks fly when it runs." },
    { id: "glimmerwing",name: "Glimmerwing",biome: "sky",    color: 0x9a6ad8, accent: 0xe6d0ff, size: 0.9,  speed: 3.2, catchRate: 0.4,  income: 4, far: 140, hint: "Sparkles at the forest edge." },
    { id: "nocturnix",  name: "Nocturnix",  biome: "night",  color: 0x3a3f6b, accent: 0x8fd0ff, size: 1.1,  speed: 3.6, catchRate: 0.3,  income: 6, far: 170, hint: "The rarest. Roams the far hills." }
  ];
  if (IS_DEMO) SPECIES = SPECIES.slice(0, 4);
  var SPECIES_BY_ID = {};
  SPECIES.forEach(function (s) { SPECIES_BY_ID[s.id] = s; });

  // ------------------------------------------------------------ buildings
  var BUILDINGS = [
    { id: "path",     name: "Path",           e: "🟫", cost: 5,   attract: 0.3 },
    { id: "flowers",  name: "Flower bed",     e: "🌸", cost: 15,  attract: 1 },
    { id: "lamp",     name: "Lamp",           e: "🏮", cost: 25,  attract: 1 },
    { id: "hab_meadow", name: "Meadow habitat", e: "🌿", cost: 60,  attract: 3, biome: "meadow" },
    { id: "hab_water",  name: "Water habitat",  e: "💧", cost: 80,  attract: 3, biome: "water" },
    { id: "fountain", name: "Fountain",       e: "⛲", cost: 70,  attract: 3 },
    { id: "stall",    name: "Snack stall",    e: "🍿", cost: 90,  attract: 2, stall: true },
    { id: "hab_ember",  name: "Ember habitat",  e: "🔥", cost: 100, attract: 3, biome: "ember", full: true },
    { id: "hab_sky",    name: "Sky habitat",    e: "☁️", cost: 120, attract: 3, biome: "sky",  full: true },
    { id: "shop",     name: "Gift shop",      e: "🎁", cost: 120, attract: 3, stall: true, full: true },
    { id: "hab_night",  name: "Night habitat",  e: "🌙", cost: 150, attract: 4, biome: "night", full: true },
    { id: "remove",   name: "Remove",         e: "🧹", cost: 0 }
  ];
  if (IS_DEMO) BUILDINGS = BUILDINGS.filter(function (b) { return !b.full; });
  var BUILDINGS_BY_ID = {};
  BUILDINGS.forEach(function (b) { BUILDINGS_BY_ID[b.id] = b; });

  // ----------------------------------------------------------------- rng
  function makeNoise(seed) {
    var perm = [], s = seed;
    for (var i = 0; i < 256; i++) perm[i] = i;
    for (i = 255; i > 0; i--) {
      s = (s * 16807) % 2147483647;
      var j = s % (i + 1), t = perm[i]; perm[i] = perm[j]; perm[j] = t;
    }
    perm = perm.concat(perm);
    function fade(t) { return t * t * (3 - 2 * t); }
    function grad(h, x, y) {
      switch (h & 3) {
        case 0: return x + y; case 1: return -x + y;
        case 2: return x - y; default: return -x - y;
      }
    }
    return function (x, y) {
      var X = Math.floor(x) & 255, Y = Math.floor(y) & 255;
      x -= Math.floor(x); y -= Math.floor(y);
      var u = fade(x), v = fade(y);
      var a = perm[X] + Y, b = perm[X + 1] + Y;
      return (1 - v) * ((1 - u) * grad(perm[a], x, y) + u * grad(perm[b], x - 1, y)) +
             v * ((1 - u) * grad(perm[a + 1], x, y - 1) + u * grad(perm[b + 1], x - 1, y - 1));
    };
  }
  var noise = makeNoise(20260803);

  // --------------------------------------------------------------- world
  var WORLD = IS_DEMO ? 160 : 240;         // half-size; park west, wilds east
  var WATER_Y = 0.0;
  var PARK = { x0: -78, x1: -18, z0: -30, z1: 30, y: 2.2, cell: 6 };
  var GATE = { x: PARK.x1, z: 0 };

  function smoothstep(a, b, x) {
    var t = Math.max(0, Math.min(1, (x - a) / (b - a)));
    return t * t * (3 - 2 * t);
  }
  function rawHeight(x, z) {
    var n = 0, amp = 1, freq = 1 / 60, sum = 0;
    for (var o = 0; o < 4; o++) {
      n += noise(x * freq + 100, z * freq + 100) * amp;
      sum += amp; amp *= 0.5; freq *= 2;
    }
    n /= sum;
    var d = Math.sqrt(x * x + z * z) / (WORLD * 1.08);
    var island = 1 - Math.pow(Math.min(d, 1), 2.3);
    return (n * 0.5 + 0.5) * 15 * island - 2.2;
  }
  function terrainHeight(x, z) {
    var h = rawHeight(x, z);
    // flatten the park plateau with a soft blend margin
    var m = 10;
    var inX = smoothstep(PARK.x0 - m, PARK.x0, x) * (1 - smoothstep(PARK.x1, PARK.x1 + m, x));
    var inZ = smoothstep(PARK.z0 - m, PARK.z0, z) * (1 - smoothstep(PARK.z1, PARK.z1 + m, z));
    var w = inX * inZ;
    return h * (1 - w) + PARK.y * w;
  }
  function isLand(x, z) { return terrainHeight(x, z) > WATER_Y + 0.5; }
  function inPark(x, z) {
    return x > PARK.x0 && x < PARK.x1 && z > PARK.z0 && z < PARK.z1;
  }

  // ----------------------------------------------------------- three.js
  var scene = new THREE.Scene();
  scene.background = new THREE.Color(0x9fd8ef);
  scene.fog = new THREE.Fog(0x9fd8ef, WORLD * 0.55, WORLD * 1.7);
  var camera = new THREE.PerspectiveCamera(60, innerWidth / innerHeight, 0.1, 2500);
  var renderer = new THREE.WebGLRenderer({ antialias: true });
  renderer.setSize(innerWidth, innerHeight);
  renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
  renderer.shadowMap.enabled = true;
  renderer.shadowMap.type = THREE.PCFSoftShadowMap;
  document.getElementById("game").appendChild(renderer.domElement);

  var hemi = new THREE.HemisphereLight(0xeaf6ff, 0x8a9a6a, 0.9);
  scene.add(hemi);
  var sun = new THREE.DirectionalLight(0xfff2d8, 0.95);
  sun.castShadow = true;
  sun.shadow.mapSize.set(2048, 2048);
  sun.shadow.camera.left = -70; sun.shadow.camera.right = 70;
  sun.shadow.camera.top = 70; sun.shadow.camera.bottom = -70;
  sun.shadow.camera.far = 500;
  scene.add(sun); scene.add(sun.target);

  // stars for night
  var starGeo = new THREE.BufferGeometry();
  var starPos = [];
  for (var si = 0; si < 300; si++) {
    var a = Math.random() * Math.PI * 2, r = 600 + Math.random() * 400;
    var y = 150 + Math.random() * 500;
    starPos.push(Math.cos(a) * r, y, Math.sin(a) * r);
  }
  starGeo.setAttribute("position", new THREE.Float32BufferAttribute(starPos, 3));
  var starMat = new THREE.PointsMaterial({ color: 0xffffff, size: 2.2, transparent: true, opacity: 0, sizeAttenuation: false });
  scene.add(new THREE.Points(starGeo, starMat));

  // ------------------------------------------------------------- terrain
  var terrainMesh;
  (function buildTerrain() {
    var seg = IS_DEMO ? 130 : 190;
    var geo = new THREE.PlaneGeometry(WORLD * 2.6, WORLD * 2.6, seg, seg);
    geo.rotateX(-Math.PI / 2);
    var pos = geo.attributes.position;
    var colors = new Float32Array(pos.count * 3);
    var sand = new THREE.Color(0xe8d8a0), grass = new THREE.Color(0x79b34c),
        dark = new THREE.Color(0x527a35), rock = new THREE.Color(0x9a938a),
        lawn = new THREE.Color(0x8cc45e), c = new THREE.Color();
    for (var i = 0; i < pos.count; i++) {
      var x = pos.getX(i), z = pos.getZ(i);
      var h = terrainHeight(x, z);
      pos.setY(i, h);
      if (inPark(x, z)) c.copy(lawn);
      else if (h < WATER_Y + 0.7) c.copy(sand);
      else if (h < 6.5) c.copy(grass).lerp(dark, h / 9);
      else c.copy(rock);
      c.offsetHSL(0, 0, noise(x * 0.3, z * 0.3) * 0.05);
      colors[i * 3] = c.r; colors[i * 3 + 1] = c.g; colors[i * 3 + 2] = c.b;
    }
    geo.setAttribute("color", new THREE.BufferAttribute(colors, 3));
    geo.computeVertexNormals();
    terrainMesh = new THREE.Mesh(geo, new THREE.MeshLambertMaterial({ vertexColors: true }));
    terrainMesh.receiveShadow = true;
    scene.add(terrainMesh);
  })();

  // animated water
  var waterMesh;
  (function () {
    var geo = new THREE.PlaneGeometry(WORLD * 6, WORLD * 6, 48, 48);
    geo.rotateX(-Math.PI / 2);
    waterMesh = new THREE.Mesh(geo, new THREE.MeshLambertMaterial({
      color: 0x3f8fbf, transparent: true, opacity: 0.72
    }));
    waterMesh.position.y = WATER_Y;
    scene.add(waterMesh);
  })();

  // ------------------------------------------------------- nature props
  var trunkMat = new THREE.MeshLambertMaterial({ color: 0x8a6a4a });
  var leafMats = [new THREE.MeshLambertMaterial({ color: 0x4e8a3a }),
                  new THREE.MeshLambertMaterial({ color: 0x67a24a })];
  var rockMat = new THREE.MeshLambertMaterial({ color: 0x9a938a });
  function scatter(count, minH, maxH, build) {
    for (var i = 0; i < count; i++) {
      var x = (Math.random() * 2 - 1) * WORLD;
      var z = (Math.random() * 2 - 1) * WORLD;
      if (inPark(x, z) || (x < PARK.x1 + 8 && x > PARK.x0 - 8 && z > PARK.z0 - 8 && z < PARK.z1 + 8)) continue;
      var h = terrainHeight(x, z);
      if (h < minH || h > maxH) continue;
      var obj = build();
      obj.position.set(x, h, z);
      obj.rotation.y = Math.random() * Math.PI * 2;
      obj.scale.setScalar(0.7 + Math.random() * 0.7);
      scene.add(obj);
    }
  }
  function makeTree() {
    var g = new THREE.Group();
    var trunk = new THREE.Mesh(new THREE.CylinderGeometry(0.25, 0.35, 2.2, 6), trunkMat);
    trunk.position.y = 1.1; trunk.castShadow = true;
    var fol = new THREE.Mesh(new THREE.ConeGeometry(1.6, 3.2, 7), leafMats[Math.random() < 0.5 ? 0 : 1]);
    fol.position.y = 3.4; fol.castShadow = true;
    g.add(trunk, fol);
    return g;
  }
  function makeRock() {
    var g = new THREE.Group();
    var r = new THREE.Mesh(new THREE.IcosahedronGeometry(0.9, 0), rockMat);
    r.position.y = 0.3; r.castShadow = true;
    g.add(r); return g;
  }
  scatter(IS_DEMO ? 150 : 420, 1.2, 8, makeTree);
  scatter(IS_DEMO ? 45 : 130, 0.8, 12, makeRock);

  // -------------------------------------------------------- park & fence
  (function buildFence() {
    var post = new THREE.BoxGeometry(0.3, 1.3, 0.3);
    var mat = new THREE.MeshLambertMaterial({ color: 0x9a6f45 });
    var g = new THREE.Group();
    function run(x0, z0, x1, z1) {
      var dx = x1 - x0, dz = z1 - z0;
      var len = Math.sqrt(dx * dx + dz * dz), n = Math.round(len / 3);
      for (var i = 0; i <= n; i++) {
        var x = x0 + dx * i / n, z = z0 + dz * i / n;
        if (Math.abs(x - GATE.x) < 0.5 && Math.abs(z - GATE.z) < 5) continue; // gate gap
        var p = new THREE.Mesh(post, mat);
        p.position.set(x, PARK.y + 0.65, z);
        p.castShadow = true;
        g.add(p);
        var rail = new THREE.Mesh(new THREE.BoxGeometry(dx ? len / n : 0.14, 0.14, dz ? len / n : 0.14), mat);
        rail.position.set(x - (dx ? dx / n / 2 : 0), PARK.y + 1.0, z - (dz ? dz / n / 2 : 0));
        if (i > 0 && !(Math.abs(x - GATE.x) < 0.6 && Math.abs(z - GATE.z) < 8)) g.add(rail);
      }
    }
    run(PARK.x0, PARK.z0, PARK.x1, PARK.z0);
    run(PARK.x0, PARK.z1, PARK.x1, PARK.z1);
    run(PARK.x0, PARK.z0, PARK.x0, PARK.z1);
    run(PARK.x1, PARK.z0, PARK.x1, PARK.z1);
    // gate arch
    var arch = new THREE.Mesh(new THREE.BoxGeometry(0.6, 0.6, 10.5),
      new THREE.MeshLambertMaterial({ color: 0xB4652F }));
    arch.position.set(GATE.x, PARK.y + 3.2, GATE.z);
    var p1 = new THREE.Mesh(new THREE.BoxGeometry(0.5, 3.2, 0.5), mat);
    p1.position.set(GATE.x, PARK.y + 1.6, GATE.z - 5);
    var p2 = p1.clone(); p2.position.z = GATE.z + 5;
    g.add(arch, p1, p2);
    scene.add(g);
  })();

  function cellKey(cx, cz) { return cx + "," + cz; }
  function cellCenter(cx, cz) {
    return {
      x: PARK.x0 + PARK.cell / 2 + cx * PARK.cell,
      z: PARK.z0 + PARK.cell / 2 + cz * PARK.cell
    };
  }
  var COLS = Math.floor((PARK.x1 - PARK.x0) / PARK.cell);
  var ROWS = Math.floor((PARK.z1 - PARK.z0) / PARK.cell);
  function worldToCell(x, z) {
    if (!inPark(x, z)) return null;
    var cx = Math.floor((x - PARK.x0) / PARK.cell);
    var cz = Math.floor((z - PARK.z0) / PARK.cell);
    if (cx < 0 || cz < 0 || cx >= COLS || cz >= ROWS) return null;
    return { cx: cx, cz: cz };
  }

  var BIOME_COLORS = { meadow: 0x6fae4e, water: 0x4aa8d8, ember: 0xc9744a, sky: 0xbcd6e8, night: 0x4a4f7a };
  var lampMats = [];   // emissive lamps to glow at night
  function buildBuildingMesh(type, cx, cz) {
    var b = BUILDINGS_BY_ID[type];
    var g = new THREE.Group();
    var c = cellCenter(cx, cz);
    var wood = new THREE.MeshLambertMaterial({ color: 0x9a6f45 });
    if (type === "path") {
      var tile = new THREE.Mesh(new THREE.BoxGeometry(PARK.cell - 0.4, 0.12, PARK.cell - 0.4),
        new THREE.MeshLambertMaterial({ color: 0xb59a6e }));
      tile.position.y = 0.06;
      g.add(tile);
    } else if (type === "flowers") {
      for (var i = 0; i < 7; i++) {
        var stem = new THREE.Mesh(new THREE.CylinderGeometry(0.03, 0.03, 0.5, 4),
          new THREE.MeshLambertMaterial({ color: 0x4e8a3a }));
        var fx = (Math.random() - 0.5) * 4, fz = (Math.random() - 0.5) * 4;
        stem.position.set(fx, 0.25, fz);
        var head = new THREE.Mesh(new THREE.SphereGeometry(0.16, 6, 5),
          new THREE.MeshLambertMaterial({ color: [0xffffff, 0xff9ec0, 0xffe27a, 0xc59af0][i % 4] }));
        head.position.set(fx, 0.55, fz);
        g.add(stem, head);
      }
    } else if (type === "lamp") {
      var goldL = save.unlocked && save.unlocked.gold;
      var pole = new THREE.Mesh(new THREE.CylinderGeometry(0.09, 0.12, 2.6, 6),
        new THREE.MeshLambertMaterial({ color: goldL ? 0xC9A34A : 0x3a3f45 }));
      pole.position.y = 1.3; pole.castShadow = true;
      var lm = new THREE.MeshLambertMaterial({ color: 0xfff2c0, emissive: 0x000000 });
      var bulb = new THREE.Mesh(new THREE.SphereGeometry(0.32, 8, 7), lm);
      bulb.position.y = 2.7;
      lampMats.push(lm);
      g.add(pole, bulb);
    } else if (type === "fountain") {
      var goldF = save.unlocked && save.unlocked.gold;
      var basin = new THREE.Mesh(new THREE.CylinderGeometry(2.1, 2.3, 0.6, 12),
        new THREE.MeshLambertMaterial({ color: goldF ? 0xC9A34A : 0xb9c0c9 }));
      basin.position.y = 0.3; basin.castShadow = true;
      var waterD = new THREE.Mesh(new THREE.CylinderGeometry(1.8, 1.8, 0.15, 12),
        new THREE.MeshLambertMaterial({ color: goldF ? 0xFFD870 : 0x5fb4de, emissive: goldF ? 0x443300 : 0x000000 }));
      waterD.position.y = 0.62;
      var jet = new THREE.Mesh(new THREE.ConeGeometry(0.35, 1.6, 8),
        new THREE.MeshLambertMaterial({ color: goldF ? 0xFFE9A8 : 0x9fd4ec, transparent: true, opacity: 0.8 }));
      jet.position.y = 1.5;
      g.add(basin, waterD, jet);
    } else if (type === "stall" || type === "shop") {
      var base = new THREE.Mesh(new THREE.BoxGeometry(3.4, 2.0, 2.6), wood);
      base.position.y = 1.0; base.castShadow = true;
      var roof = new THREE.Mesh(new THREE.BoxGeometry(4.0, 0.25, 3.2),
        new THREE.MeshLambertMaterial({ color: type === "stall" ? 0xd85a4a : 0x4a7ad8 }));
      roof.position.y = 2.3;
      var sign = new THREE.Mesh(new THREE.BoxGeometry(1.4, 0.7, 0.15),
        new THREE.MeshLambertMaterial({ color: 0xfff2c0 }));
      sign.position.set(0, 1.6, 1.4);
      g.add(base, roof, sign);
    } else if (b && b.biome) {
      // habitat: colored floor + low fence + biome prop
      var floor = new THREE.Mesh(new THREE.CylinderGeometry(2.6, 2.6, 0.14, 14),
        new THREE.MeshLambertMaterial({ color: BIOME_COLORS[b.biome] }));
      floor.position.y = 0.07;
      g.add(floor);
      for (var k = 0; k < 10; k++) {
        var ang = k / 10 * Math.PI * 2;
        var fp = new THREE.Mesh(new THREE.BoxGeometry(0.18, 0.7, 0.18), wood);
        fp.position.set(Math.cos(ang) * 2.7, 0.35, Math.sin(ang) * 2.7);
        g.add(fp);
      }
      var prop;
      if (b.biome === "water") {
        prop = new THREE.Mesh(new THREE.CylinderGeometry(1.0, 1.0, 0.1, 10),
          new THREE.MeshLambertMaterial({ color: 0x5fb4de }));
        prop.position.set(0.8, 0.16, 0.6);
      } else if (b.biome === "ember") {
        prop = new THREE.Mesh(new THREE.ConeGeometry(0.4, 0.9, 7),
          new THREE.MeshLambertMaterial({ color: 0xffa64a, emissive: 0x662200 }));
        prop.position.set(0.8, 0.55, 0.6);
      } else if (b.biome === "sky") {
        prop = new THREE.Mesh(new THREE.CylinderGeometry(0.12, 0.16, 2.4, 6), wood);
        prop.position.set(0.8, 1.2, 0.6);
        var perch = new THREE.Mesh(new THREE.BoxGeometry(1.4, 0.12, 0.24), wood);
        perch.position.set(0.8, 2.3, 0.6);
        g.add(perch);
      } else if (b.biome === "night") {
        prop = new THREE.Mesh(new THREE.IcosahedronGeometry(0.6, 0),
          new THREE.MeshLambertMaterial({ color: 0x5a5f8a, emissive: 0x11123a }));
        prop.position.set(0.8, 0.5, 0.6);
      } else {
        prop = new THREE.Mesh(new THREE.IcosahedronGeometry(0.5, 0), rockMat);
        prop.position.set(0.9, 0.35, 0.6);
      }
      g.add(prop);
    }
    g.position.set(c.x, PARK.y, c.z);
    return g;
  }

  // ---------------------------------------------------------------- audio
  var AudioSys = (function () {
    var ctx = null, master, musicG, sfxG, muted = false, started = false;
    var chordRoot = [0, 5, 7, 3];  // I IV V iii-ish, semitone offsets from C
    var barIdx = 0, nextBar = 0;
    function ensure() {
      if (ctx) return true;
      var AC = window.AudioContext || window.webkitAudioContext;
      if (!AC) return false;
      ctx = new AC();
      master = ctx.createGain(); master.gain.value = 0.8; master.connect(ctx.destination);
      musicG = ctx.createGain(); musicG.gain.value = 0.22; musicG.connect(master);
      sfxG = ctx.createGain(); sfxG.gain.value = 0.5; sfxG.connect(master);
      return true;
    }
    function freq(semi) { return 261.63 * Math.pow(2, semi / 12); }
    function padNote(semi, t, dur) {
      var o1 = ctx.createOscillator(), o2 = ctx.createOscillator();
      o1.type = "triangle"; o2.type = "sine";
      o1.frequency.value = freq(semi); o2.frequency.value = freq(semi) * 1.005;
      var g = ctx.createGain();
      g.gain.setValueAtTime(0, t);
      g.gain.linearRampToValueAtTime(0.08, t + dur * 0.3);
      g.gain.linearRampToValueAtTime(0, t + dur);
      var f = ctx.createBiquadFilter(); f.type = "lowpass"; f.frequency.value = 900;
      o1.connect(g); o2.connect(g); g.connect(f); f.connect(musicG);
      o1.start(t); o2.start(t); o1.stop(t + dur + 0.1); o2.stop(t + dur + 0.1);
    }
    function pluck(semi, t, vol) {
      var o = ctx.createOscillator(); o.type = "sine";
      o.frequency.value = freq(semi) * 2;
      var g = ctx.createGain();
      g.gain.setValueAtTime(vol, t);
      g.gain.exponentialRampToValueAtTime(0.001, t + 0.8);
      o.connect(g); g.connect(musicG);
      o.start(t); o.stop(t + 0.9);
    }
    var PENTA = [0, 2, 4, 7, 9, 12, 14];
    function scheduleMusic() {
      if (!ctx || muted) return;
      var now = ctx.currentTime;
      while (nextBar < now + 4.5) {
        var t = Math.max(nextBar, now + 0.05);
        var root = chordRoot[barIdx % chordRoot.length];
        padNote(root - 12, t, 4.2);
        padNote(root - 5, t, 4.2);
        padNote(root + (barIdx % 2 ? 4 : 7), t, 4.2);
        for (var i = 0; i < 4; i++) {
          if (Math.random() < 0.65) {
            pluck(root + PENTA[Math.floor(Math.random() * PENTA.length)], t + i + Math.random() * 0.4, 0.10);
          }
        }
        nextBar = t + 4;
        barIdx++;
      }
    }
    function tone(f0, f1, dur, type, vol) {
      if (!ctx || muted) return;
      var t = ctx.currentTime;
      var o = ctx.createOscillator(); o.type = type || "sine";
      o.frequency.setValueAtTime(f0, t);
      o.frequency.exponentialRampToValueAtTime(Math.max(f1, 1), t + dur);
      var g = ctx.createGain();
      g.gain.setValueAtTime(vol || 0.25, t);
      g.gain.exponentialRampToValueAtTime(0.001, t + dur);
      o.connect(g); g.connect(sfxG);
      o.start(t); o.stop(t + dur + 0.05);
    }
    function chirp() { tone(1800 + Math.random() * 800, 2600, 0.12, "sine", 0.05); }
    return {
      start: function () {
        if (started) return;
        if (!ensure()) return;
        started = true;
        if (ctx.state === "suspended") ctx.resume();
        nextBar = ctx.currentTime + 0.1;
        setInterval(scheduleMusic, 1000);
        setInterval(function () { if (!muted && Math.random() < 0.4) chirp(); }, 6000);
      },
      throwSfx: function () { tone(500, 120, 0.3, "sawtooth", 0.12); },
      catchSfx: function () {
        [0, 4, 7, 12].forEach(function (s, i) {
          setTimeout(function () { tone(freqOf(s), freqOf(s), 0.25, "triangle", 0.2); }, i * 90);
        });
        function freqOf(s) { return 523 * Math.pow(2, s / 12); }
      },
      failSfx: function () { tone(400, 180, 0.4, "triangle", 0.18); },
      coinSfx: function () { tone(1200, 1800, 0.12, "square", 0.06); },
      placeSfx: function () { tone(220, 140, 0.18, "square", 0.15); },
      clickSfx: function () { tone(900, 700, 0.06, "square", 0.08); },
      starSfx: function () {
        [0, 7, 12, 19].forEach(function (s, i) {
          setTimeout(function () { tone(659 * Math.pow(2, s / 12), 659 * Math.pow(2, s / 12), 0.4, "triangle", 0.2); }, i * 130);
        });
      },
      toggleMute: function () { muted = !muted; if (master) master.gain.value = muted ? 0 : 0.8; return muted; },
      setMuted: function (m) { muted = m; if (master) master.gain.value = muted ? 0 : 0.8; }
    };
  })();

  // --------------------------------------------------------------- player
  var player = new THREE.Group();
  (function () {
    var mat = new THREE.MeshLambertMaterial({ color: 0xd85a4a });
    var skin = new THREE.MeshLambertMaterial({ color: 0xf5c9a0 });
    var body = new THREE.Mesh(new THREE.CylinderGeometry(0.42, 0.5, 1.0, 10), mat);
    body.position.y = 0.9; body.castShadow = true;
    var head = new THREE.Mesh(new THREE.SphereGeometry(0.38, 12, 10), skin);
    head.position.y = 1.75; head.castShadow = true;
    var hat = new THREE.Mesh(new THREE.ConeGeometry(0.44, 0.55, 10),
      new THREE.MeshLambertMaterial({ color: 0xB4652F }));
    hat.position.y = 2.1; hat.castShadow = true;
    player.add(body, head, hat);
  })();
  player.position.set((PARK.x0 + PARK.x1) / 2, PARK.y, 0);
  scene.add(player);

  // ------------------------------------------------------------ creatures
  function buildCreature(sp) {
    var g = new THREE.Group();
    var mat = new THREE.MeshLambertMaterial({ color: sp.color });
    var acc = new THREE.MeshLambertMaterial({ color: sp.accent });
    var body = new THREE.Mesh(new THREE.SphereGeometry(0.55, 12, 10), mat);
    body.position.y = 0.62; body.scale.set(1, 0.9, 1.15); body.castShadow = true;
    var head = new THREE.Mesh(new THREE.SphereGeometry(0.38, 12, 10), mat);
    head.position.set(0, 1.1, 0.38); head.castShadow = true;
    var eyeMat = new THREE.MeshBasicMaterial({ color: 0x222222 });
    var e1 = new THREE.Mesh(new THREE.SphereGeometry(0.06, 6, 5), eyeMat);
    var e2 = e1.clone();
    e1.position.set(0.15, 1.17, 0.69); e2.position.set(-0.15, 1.17, 0.69);
    g.add(body, head, e1, e2);
    // little legs (animated)
    var legs = [];
    for (var li = 0; li < 4; li++) {
      var leg = new THREE.Mesh(new THREE.CylinderGeometry(0.09, 0.11, 0.42, 6), mat);
      leg.position.set(li % 2 ? 0.28 : -0.28, 0.22, li < 2 ? 0.3 : -0.3);
      legs.push(leg); g.add(leg);
    }
    g.userData.legs = legs;
    // tail
    var tail = new THREE.Mesh(new THREE.SphereGeometry(0.2, 8, 6), acc);
    tail.position.set(0, 0.66, -0.68);
    g.add(tail); g.userData.tail = tail;
    // flair
    if (sp.biome === "meadow") {
      var ear1 = new THREE.Mesh(new THREE.ConeGeometry(0.1, 0.55, 6), mat);
      ear1.position.set(0.16, 1.56, 0.32);
      var ear2 = ear1.clone(); ear2.position.x = -0.16;
      g.add(ear1, ear2);
    }
    if (sp.biome === "ember") {
      var flame = new THREE.Mesh(new THREE.ConeGeometry(0.18, 0.55, 7),
        new THREE.MeshLambertMaterial({ color: sp.accent, emissive: 0x552200 }));
      flame.position.set(0, 0.9, -0.66); flame.rotation.x = 0.7;
      g.add(flame);
    }
    if (sp.biome === "water") {
      var fin = new THREE.Mesh(new THREE.ConeGeometry(0.22, 0.5, 4), acc);
      fin.position.set(0, 1.3, 0.02); fin.rotation.x = -0.4;
      g.add(fin);
    }
    if (sp.biome === "sky" || sp.biome === "night") {
      var wingGeo = new THREE.ConeGeometry(0.3, 0.8, 4);
      var w1 = new THREE.Mesh(wingGeo, acc);
      w1.position.set(0.6, 1.0, -0.05); w1.rotation.z = 1.2;
      var w2 = new THREE.Mesh(wingGeo, acc);
      w2.position.set(-0.6, 1.0, -0.05); w2.rotation.z = -1.2;
      g.add(w1, w2);
      g.userData.wings = [w1, w2];
    }
    g.scale.setScalar(sp.size);
    return g;
  }

  function randomWildPos(minFar) {
    for (var tries = 0; tries < 200; tries++) {
      var x = 15 + Math.random() * (WORLD * 0.92 - 15);
      var z = (Math.random() * 2 - 1) * WORLD * 0.9;
      if (!isLand(x, z)) continue;
      var far = Math.sqrt(x * x + z * z);
      if (far < (minFar || 0)) continue;
      return new THREE.Vector3(x, terrainHeight(x, z), z);
    }
    return new THREE.Vector3(30, terrainHeight(30, 0), 0);
  }

  var wild = [];       // wandering wild creatures
  var residents = [];  // creatures living in habitats
  function spawnWild(sp) {
    var mesh = buildCreature(sp);
    var p = randomWildPos(sp.far);
    mesh.position.copy(p);
    scene.add(mesh);
    wild.push({ sp: sp, mesh: mesh, state: "wander", target: p.clone(), idle: Math.random() * 3, fleeT: 0, bob: Math.random() * 10, moving: false });
  }
  SPECIES.forEach(function (sp) {
    var n = IS_DEMO ? 2 : 3;
    for (var i = 0; i < n; i++) spawnWild(sp);
  });

  // ------------------------------------------------------------- pickups
  var pickups = [];
  var orbGeo = new THREE.SphereGeometry(0.35, 10, 8);
  var orbMat = new THREE.MeshLambertMaterial({ color: 0xffffff, emissive: 0x5588ff });
  function spawnPickup() {
    var m = new THREE.Mesh(orbGeo, orbMat);
    var p = randomWildPos(0);
    m.position.copy(p); m.position.y += 0.8;
    scene.add(m);
    pickups.push(m);
  }
  for (var pi0 = 0; pi0 < (IS_DEMO ? 12 : 26); pi0++) spawnPickup();

  // ------------------------------------------------------------- visitors
  var visitors = [];
  var shirtColors = [0xd85a4a, 0x4a7ad8, 0x58b368, 0xc59af0, 0xe8c832, 0x6fc4c9];
  function spawnVisitor() {
    var g = new THREE.Group();
    var body = new THREE.Mesh(new THREE.CylinderGeometry(0.3, 0.34, 0.9, 8),
      new THREE.MeshLambertMaterial({ color: shirtColors[Math.floor(Math.random() * shirtColors.length)] }));
    body.position.y = 0.75; body.castShadow = true;
    var head = new THREE.Mesh(new THREE.SphereGeometry(0.26, 10, 8),
      new THREE.MeshLambertMaterial({ color: 0xf5c9a0 }));
    head.position.y = 1.45;
    g.add(body, head);
    g.position.set(GATE.x + 2, PARK.y, GATE.z + (Math.random() - 0.5) * 4);
    scene.add(g);
    visitors.push({ mesh: g, target: null, idle: 0, life: 45 + Math.random() * 40 });
    addCoins(2);
    AudioSys.coinSfx();
  }
  function visitorTargetPos() {
    var cx = Math.floor(Math.random() * COLS), cz = Math.floor(Math.random() * ROWS);
    var c = cellCenter(cx, cz);
    return new THREE.Vector3(c.x + (Math.random() - 0.5) * 3, PARK.y, c.z + (Math.random() - 0.5) * 3);
  }

  // ---------------------------------------------------------------- save
  var save = { coins: 120, orbs: 10, caught: {}, grid: {}, muted: false, lastSeen: 0, won: false, helpSeen: false, unlocked: {} };
  try {
    var raw = localStorage.getItem(SAVE_KEY);
    if (raw) {
      var loaded = JSON.parse(raw);
      for (var k in loaded) save[k] = loaded[k];
    }
  } catch (e) {}
  save.unlocked = save.unlocked || {};
  var visiting = null;   // {c: caught, g: grid} of a friend's park while visiting
  function activeCaught() { return visiting ? visiting.c : save.caught; }
  function persist() {
    if (visiting) return;               // never save while touring a friend's park
    save.lastSeen = Date.now();
    try { localStorage.setItem(SAVE_KEY, JSON.stringify(save)); } catch (e) {}
  }
  AudioSys.setMuted(!!save.muted);

  // ------------------------------------------------------ premium packs
  // real-money DLC: buyers get an unlock code with purchase (sold on itch.io);
  // codes are verified by hash so they aren't readable in the source.
  function codeHash(s) {
    var h = 5381;
    for (var i = 0; i < s.length; i++) h = ((h * 33) + s.charCodeAt(i)) >>> 0;
    return h.toString(16);
  }
  var PACKS = [
    { id: "gold", e: "✨", name: "Golden Park Pack",
      desc: "Golden fountains, golden lamps, and a golden keeper's hat.",
      hash: "a1a5fd8c" },
    { id: "star", e: "🌠", name: "Starlight Keeper Pack",
      desc: "A starlight wizard hat and enchanted violet catch orbs.",
      hash: "e2b2c45" }
  ];
  function tryUnlock(code) {
    var h = codeHash(code.trim().toUpperCase());
    for (var i = 0; i < PACKS.length; i++) {
      if (PACKS[i].hash === h) {
        save.unlocked[PACKS[i].id] = true;
        persist();
        return PACKS[i];
      }
    }
    return null;
  }
  function applyKeeperCosmetics() {
    var hat = player.children[2];
    if (save.unlocked.gold) hat.material = new THREE.MeshLambertMaterial({ color: 0xE8C832, emissive: 0x332200 });
    if (save.unlocked.star) {
      hat.material = new THREE.MeshLambertMaterial({ color: 0x9a6ad8, emissive: 0x221133 });
      orbMat.emissive.setHex(0x8844cc);
    }
  }

  // grid state: key -> {type, mesh, habitatResidents:[]}
  var grid = {};
  function placeBuilding(cx, cz, type, silent) {
    var key = cellKey(cx, cz);
    if (grid[key]) return false;
    var mesh = buildBuildingMesh(type, cx, cz);
    scene.add(mesh);
    grid[key] = { type: type, mesh: mesh, cx: cx, cz: cz };
    if (!visiting) save.grid[key] = type;
    if (!silent) { AudioSys.placeSfx(); persist(); reassignResidents(); updateEconomy(); }
    return true;
  }
  function clearParkMeshes() {
    for (var key in grid) scene.remove(grid[key].mesh);
    grid = {};
  }
  function buildParkFrom(gridData) {
    for (var key in gridData) {
      if (!BUILDINGS_BY_ID[gridData[key]]) continue;
      var parts = key.split(",");
      var cx = parseInt(parts[0], 10), cz = parseInt(parts[1], 10);
      var mesh = buildBuildingMesh(gridData[key], cx, cz);
      scene.add(mesh);
      grid[key] = { type: gridData[key], mesh: mesh, cx: cx, cz: cz };
    }
  }
  function removeBuilding(cx, cz) {
    var key = cellKey(cx, cz);
    var g = grid[key];
    if (!g) return false;
    scene.remove(g.mesh);
    delete grid[key];
    delete save.grid[key];
    var b = BUILDINGS_BY_ID[g.type];
    addCoins(Math.floor((b ? b.cost : 0) / 2));
    persist(); reassignResidents(); updateEconomy();
    return true;
  }
  // restore saved park
  for (var gk in save.grid) {
    var parts = gk.split(",");
    placeBuilding(parseInt(parts[0], 10), parseInt(parts[1], 10), save.grid[gk], true);
  }

  // ------------------------------------------------- residents assignment
  function habitats() {
    var out = [];
    for (var key in grid) {
      var b = BUILDINGS_BY_ID[grid[key].type];
      if (b && b.biome) out.push(grid[key]);
    }
    return out;
  }
  function reassignResidents() {
    residents.forEach(function (r) { scene.remove(r.mesh); });
    residents = [];
    var habs = habitats();
    var capacity = {};
    habs.forEach(function (h) { capacity[cellKey(h.cx, h.cz)] = 2; });
    var caughtSrc = activeCaught();
    SPECIES.forEach(function (sp) {
      var count = Math.min(caughtSrc[sp.id] || 0, 4);
      for (var i = 0; i < count; i++) {
        var placed = false;
        for (var hi = 0; hi < habs.length && !placed; hi++) {
          var h = habs[hi];
          var b = BUILDINGS_BY_ID[h.type];
          var key = cellKey(h.cx, h.cz);
          if (b.biome === sp.biome && capacity[key] > 0) {
            capacity[key]--;
            var mesh = buildCreature(sp);
            mesh.scale.setScalar(sp.size * 0.8);
            var c = cellCenter(h.cx, h.cz);
            mesh.position.set(c.x + (Math.random() - 0.5) * 2, PARK.y, c.z + (Math.random() - 0.5) * 2);
            scene.add(mesh);
            residents.push({ sp: sp, mesh: mesh, home: c, target: null, idle: Math.random() * 2, bob: Math.random() * 10, moving: false });
            placed = true;
          }
        }
      }
    });
  }
  reassignResidents();

  // -------------------------------------------------------------- economy
  var attraction = 0, incomePerTick = 0, stallCount = 0, starCount = 0;
  function updateEconomy() {
    attraction = 0; incomePerTick = 0; stallCount = 0;
    for (var key in grid) {
      var b = BUILDINGS_BY_ID[grid[key].type];
      if (!b) continue;
      attraction += b.attract || 0;
      if (b.stall) stallCount++;
    }
    residents.forEach(function (r) {
      attraction += 4;
      incomePerTick += r.sp.income;
    });
    var thresholds = [0, 14, 32, 58, 92];
    var s = 1;
    for (var i = 1; i < thresholds.length; i++) if (attraction >= thresholds[i]) s = i + 1;
    if (s > starCount && starCount > 0) { AudioSys.starSfx(); toast("⭐ Your park reached " + s + " star" + (s > 1 ? "s" : "") + "!"); }
    starCount = s;
    refreshHud();
    checkWin();
  }
  function addCoins(n) { save.coins += n; refreshHud(); }
  function caughtSpecies() {
    return SPECIES.filter(function (s) { return save.caught[s.id]; }).length;
  }
  function checkWin() {
    if (save.won || visiting) return;
    if (starCount >= 5 && caughtSpecies() === SPECIES.length) {
      save.won = true; persist();
      document.getElementById("win").classList.add("open");
      AudioSys.starSfx();
    }
  }

  // offline earnings
  (function () {
    if (!save.lastSeen) return;
    var away = (Date.now() - save.lastSeen) / 1000;
    if (away < 90) return;
    away = Math.min(away, 8 * 3600);
    // recompute income from saved state (residents already assigned above)
    var inc = 0;
    residents.forEach(function (r) { inc += r.sp.income; });
    var earned = Math.floor(away / 5 * inc * 0.25);
    if (earned > 0) {
      save.coins += earned;
      setTimeout(function () {
        toast("💤 While you were away, your park earned " + earned + " coins!");
      }, 2500);
    }
  })();

  // ------------------------------------------------------------------ ui
  var ui = {
    coins: document.getElementById("coins"),
    orbs: document.getElementById("orbs"),
    visitors: document.getElementById("visitors"),
    stars: document.getElementById("stars"),
    prompt: document.getElementById("prompt"),
    toastEl: document.getElementById("toast"),
    buildPanel: document.getElementById("build-panel"),
    buildBtn: document.getElementById("build-btn")
  };
  function refreshHud() {
    ui.coins.textContent = save.coins;
    ui.orbs.textContent = save.orbs;
    ui.visitors.textContent = visitors.length;
    var s = "";
    for (var i = 1; i <= 5; i++) s += i <= starCount ? "★" : "☆";
    ui.stars.textContent = s;
  }
  var toastT = null;
  function toast(msg) {
    ui.toastEl.textContent = msg;
    ui.toastEl.classList.add("show");
    clearTimeout(toastT);
    toastT = setTimeout(function () { ui.toastEl.classList.remove("show"); }, 3000);
  }

  // build panel
  var buildMode = false, selectedTool = null;
  (function () {
    BUILDINGS.forEach(function (b) {
      var chip = document.createElement("div");
      chip.className = "chip";
      chip.id = "chip-" + b.id;
      chip.innerHTML = '<span class="e">' + b.e + '</span>' + b.name +
        (b.cost ? '<br><span class="c">🪙' + b.cost + "</span>" : "");
      chip.addEventListener("click", function () {
        selectedTool = b.id;
        AudioSys.clickSfx();
        document.querySelectorAll(".chip").forEach(function (c) { c.classList.remove("sel"); });
        chip.classList.add("sel");
        toast(b.id === "remove" ? "Tap a building to remove it (50% refund)" :
          "Tap a spot in your park to place: " + b.name);
      });
      ui.buildPanel.appendChild(chip);
    });
  })();
  ui.buildBtn.addEventListener("click", function () {
    buildMode = !buildMode;
    AudioSys.clickSfx();
    ui.buildPanel.classList.toggle("open", buildMode);
    ui.buildBtn.classList.toggle("active", buildMode);
    if (buildMode && !selectedTool) toast("Pick something to build, then tap inside your park!");
  });

  // collection
  function refreshDex() {
    var gridEl = document.getElementById("dex-grid");
    gridEl.innerHTML = "";
    var displayed = residents.length;
    document.getElementById("dex-summary").textContent =
      caughtSpecies() + " / " + SPECIES.length + " species caught · " + displayed +
      " on display earning 🪙" + incomePerTick + " every 5s. Creatures need a matching habitat to be displayed.";
    SPECIES.forEach(function (sp) {
      var d = document.createElement("div");
      d.className = "dex-card" + (save.caught[sp.id] ? " got" : "");
      var got = save.caught[sp.id] || 0;
      d.innerHTML = '<div class="swatch" style="background:' +
        (got ? "#" + sp.color.toString(16).padStart(6, "0") : "#555") + '"></div>' +
        '<div class="nm">' + (got ? sp.name : "???") + "</div>" +
        '<div class="ht">' + (got ? ("Caught " + got + "× · " + sp.biome + " · 🪙" + sp.income + "/5s") : sp.hint) + "</div>";
      gridEl.appendChild(d);
    });
  }
  document.getElementById("dex-btn").addEventListener("click", function () {
    AudioSys.clickSfx(); refreshDex();
    document.getElementById("dex").classList.add("open");
  });
  document.getElementById("dex-close").addEventListener("click", function () {
    document.getElementById("dex").classList.remove("open");
  });
  document.getElementById("help-btn").addEventListener("click", function () {
    AudioSys.clickSfx();
    document.getElementById("help").classList.add("open");
  });
  document.getElementById("help-close").addEventListener("click", function () {
    document.getElementById("help").classList.remove("open");
    save.helpSeen = true; persist();
  });
  document.getElementById("win-close").addEventListener("click", function () {
    document.getElementById("win").classList.remove("open");
  });
  var muteBtn = document.getElementById("mute-btn");
  muteBtn.textContent = save.muted ? "🔇" : "🔊";
  muteBtn.addEventListener("click", function () {
    save.muted = AudioSys.toggleMute();
    muteBtn.textContent = save.muted ? "🔇" : "🔊";
    persist();
  });

  // ------------------------------------------------ shop & friends UI
  function refreshShop() {
    var el = document.getElementById("shop-packs");
    el.innerHTML = "";
    PACKS.forEach(function (p) {
      var owned = !!save.unlocked[p.id];
      var div = document.createElement("div");
      div.className = "pack" + (owned ? " owned" : "");
      div.innerHTML = '<div class="pe">' + p.e + '</div>' +
        '<div><div class="pn">' + p.name + '</div><div class="pd">' + p.desc + "</div></div>" +
        (owned ? '<div class="owned-tag">✓ Owned</div>' :
          '<a class="buy-pack" target="_blank" rel="noopener" href="' +
          (CFG.buyLink || "https://tsjenn.itch.io/wildhaven") + '">Get code</a>');
      el.appendChild(div);
    });
  }
  document.getElementById("shop-btn").addEventListener("click", function () {
    AudioSys.clickSfx(); refreshShop();
    document.getElementById("shop").classList.add("open");
  });
  document.getElementById("shop-close").addEventListener("click", function () {
    document.getElementById("shop").classList.remove("open");
  });
  document.getElementById("code-btn").addEventListener("click", function () {
    var input = document.getElementById("code-input");
    var pack = tryUnlock(input.value || "");
    if (pack) {
      input.value = "";
      AudioSys.starSfx();
      toast("🎉 " + pack.name + " unlocked forever!");
      applyKeeperCosmetics();
      clearParkMeshes(); buildParkFrom(save.grid);   // re-skin placed buildings
      reassignResidents(); updateEconomy(); refreshShop();
    } else {
      AudioSys.failSfx();
      toast("That code doesn't look right — check for typos!");
    }
  });

  function myParkCode() {
    return "WH1." + btoa(unescape(encodeURIComponent(
      JSON.stringify({ g: save.grid, c: save.caught }))));
  }
  function parseParkCode(s) {
    s = (s || "").trim();
    if (s.indexOf("WH1.") !== 0) return null;
    try {
      var d = JSON.parse(decodeURIComponent(escape(atob(s.slice(4)))));
      if (!d || typeof d.g !== "object" || typeof d.c !== "object") return null;
      return d;
    } catch (e) { return null; }
  }
  function visitPark(data) {
    visiting = data;
    clearParkMeshes();
    buildParkFrom(data.g);
    reassignResidents(); updateEconomy();
    buildMode = false;
    ui.buildPanel.classList.remove("open");
    ui.buildBtn.classList.remove("active");
    player.position.set((PARK.x0 + PARK.x1) / 2, PARK.y, 0);
    document.getElementById("visit-banner").style.display = "block";
    document.getElementById("friends").classList.remove("open");
    toast("🌍 Welcome to your friend's park! Look around.");
  }
  document.getElementById("friends-btn").addEventListener("click", function () {
    AudioSys.clickSfx();
    document.getElementById("my-park-code").value = myParkCode();
    document.getElementById("friends").classList.add("open");
  });
  document.getElementById("friends-close").addEventListener("click", function () {
    document.getElementById("friends").classList.remove("open");
  });
  document.getElementById("copy-code-btn").addEventListener("click", function () {
    var ta = document.getElementById("my-park-code");
    ta.select();
    try { document.execCommand("copy"); } catch (e) {}
    if (navigator.clipboard) navigator.clipboard.writeText(ta.value).catch(function () {});
    toast("Park code copied — send it to a friend anywhere in the world!");
  });
  document.getElementById("visit-btn").addEventListener("click", function () {
    var data = parseParkCode(document.getElementById("friend-code-input").value);
    if (data) visitPark(data);
    else toast("That park code doesn't look right — ask your friend to copy it again.");
  });
  document.getElementById("visit-return").addEventListener("click", function (e) {
    e.preventDefault();
    location.reload();
  });

  // title overlay → start
  var titleEl = document.getElementById("title-overlay");
  var gameStarted = false;
  titleEl.addEventListener("click", function () {
    titleEl.style.display = "none";
    gameStarted = true;
    AudioSys.start();
    if (!save.helpSeen) document.getElementById("help").classList.add("open");
  });

  // demo banner
  if (IS_DEMO && CFG.buyLink) {
    var db = document.getElementById("demo-banner");
    db.style.display = "flex";
    document.getElementById("buy-full").href = CFG.buyLink;
  }

  applyKeeperCosmetics();
  refreshHud();
  updateEconomy();

  // --------------------------------------------------------------- input
  var keys = {};
  addEventListener("keydown", function (e) {
    keys[e.code] = true;
    if (e.code === "Space") { e.preventDefault(); tryThrow(); }
    if (e.code === "KeyB") ui.buildBtn.click();
    if (e.code === "KeyC") document.getElementById("dex-btn").click();
  });
  addEventListener("keyup", function (e) { keys[e.code] = false; });
  function bindHold(id, code) {
    var el = document.getElementById(id);
    if (!el) return;
    var on = function (e) { e.preventDefault(); keys[code] = true; };
    var off = function (e) { e.preventDefault(); keys[code] = false; };
    el.addEventListener("touchstart", on); el.addEventListener("touchend", off);
    el.addEventListener("mousedown", on); el.addEventListener("mouseup", off);
    el.addEventListener("mouseleave", off);
  }
  bindHold("t-up", "KeyW"); bindHold("t-down", "KeyS");
  bindHold("t-left", "KeyA"); bindHold("t-right", "KeyD");
  var tThrow = document.getElementById("t-throw");
  tThrow.addEventListener("touchstart", function (e) { e.preventDefault(); tryThrow(); });
  tThrow.addEventListener("mousedown", function (e) { e.preventDefault(); tryThrow(); });
  if ("ontouchstart" in window) document.getElementById("touch").style.display = "block";

  // build placement via tap/click on the ground
  var raycaster = new THREE.Raycaster();
  var pointer = new THREE.Vector2();
  renderer.domElement.addEventListener("pointerdown", function (e) {
    if (!buildMode || !selectedTool || !gameStarted || visiting) return;
    pointer.x = (e.clientX / innerWidth) * 2 - 1;
    pointer.y = -(e.clientY / innerHeight) * 2 + 1;
    raycaster.setFromCamera(pointer, camera);
    var hits = raycaster.intersectObject(terrainMesh);
    if (!hits.length) return;
    var p = hits[0].point;
    var cell = worldToCell(p.x, p.z);
    if (!cell) { toast("Build inside your park fence!"); return; }
    if (selectedTool === "remove") {
      if (removeBuilding(cell.cx, cell.cz)) toast("Removed (refunded half).");
      return;
    }
    var b = BUILDINGS_BY_ID[selectedTool];
    if (grid[cellKey(cell.cx, cell.cz)]) { toast("That spot is taken — pick an empty one."); return; }
    if (save.coins < b.cost) { toast("Not enough coins! Catch creatures & welcome visitors to earn more."); return; }
    save.coins -= b.cost;
    placeBuilding(cell.cx, cell.cz, selectedTool);
    refreshHud();
    if (b.biome) toast(b.name + " built! Matching creatures move in automatically.");
  });

  // ------------------------------------------------------------ throwing
  var activeThrow = null, nearCritter = null;
  function tryThrow() {
    if (visiting) { toast("You're visiting! Return home to catch creatures."); return; }
    if (!gameStarted || activeThrow || !nearCritter) return;
    if (save.orbs <= 0) { toast("Out of orbs! Grab the glowing orbs out in the wilds."); return; }
    save.orbs--; refreshHud(); persist();
    AudioSys.throwSfx();
    var orb = new THREE.Mesh(orbGeo, orbMat.clone());
    orb.scale.setScalar(0.7);
    var from = player.position.clone(); from.y += 1.6;
    scene.add(orb);
    activeThrow = { mesh: orb, from: from, to: nearCritter, t: 0 };
  }
  function resolveThrow(th) {
    var cr = th.to;
    scene.remove(th.mesh);
    if (Math.random() < cr.sp.catchRate) {
      save.caught[cr.sp.id] = (save.caught[cr.sp.id] || 0) + 1;
      persist();
      AudioSys.catchSfx();
      poof(cr.mesh.position, cr.sp.color);
      scene.remove(cr.mesh);
      var idx = wild.indexOf(cr);
      if (idx >= 0) wild.splice(idx, 1);
      setTimeout(function () { spawnWild(cr.sp); }, 15000);
      var hasHome = habitats().some(function (h) {
        return BUILDINGS_BY_ID[h.type].biome === cr.sp.biome;
      });
      toast("You caught " + cr.sp.name + "!" + (hasHome ? " It moved into your park." :
        " Build a " + cr.sp.biome + " habitat to display it."));
      reassignResidents(); updateEconomy();
    } else {
      AudioSys.failSfx();
      toast(cr.sp.name + " broke free and ran!");
      cr.state = "flee"; cr.fleeT = 3;
    }
  }

  var poofs = [];
  function poof(pos, color) {
    var g = new THREE.Group();
    var m = new THREE.MeshBasicMaterial({ color: color });
    for (var i = 0; i < 12; i++) {
      var p = new THREE.Mesh(new THREE.SphereGeometry(0.09, 5, 4), m);
      p.position.copy(pos); p.position.y += 0.8;
      p.userData.v = new THREE.Vector3((Math.random() - 0.5) * 4, Math.random() * 4 + 1, (Math.random() - 0.5) * 4);
      g.add(p);
    }
    scene.add(g);
    poofs.push({ g: g, t: 0 });
  }

  // ------------------------------------------------------- day/night sky
  var DAY_LEN = 210; // seconds per full cycle
  var skyDay = new THREE.Color(0x9fd8ef), skyDusk = new THREE.Color(0xe8a875),
      skyNight = new THREE.Color(0x152238), tmpC = new THREE.Color();
  function updateSky(t) {
    var phase = (t % DAY_LEN) / DAY_LEN;            // 0=dawn .. 0.5=dusk .. night
    var sunAng = phase * Math.PI * 2 - Math.PI / 2; // rises at phase 0
    var sunY = Math.sin(sunAng + Math.PI / 2);      // 1 at noon
    var day = Math.max(0, Math.min(1, (sunY + 0.15) * 2));
    var duskiness = Math.max(0, 1 - Math.abs(sunY) * 4);
    tmpC.copy(skyNight).lerp(skyDay, day).lerp(skyDusk, duskiness * 0.6);
    scene.background = tmpC;
    scene.fog.color.copy(tmpC);
    sun.intensity = 0.15 + day * 0.85;
    hemi.intensity = 0.35 + day * 0.6;
    starMat.opacity = Math.max(0, 1 - day * 2) * 0.9;
    var glow = day < 0.4 ? 1 : 0;
    for (var i = 0; i < lampMats.length; i++) {
      lampMats[i].emissive.setHex(glow ? 0xffdD70 : 0x000000);
    }
  }

  // ---------------------------------------------------------- game loop
  var yaw = 0;
  var clock = new THREE.Clock();
  var camPos = new THREE.Vector3();
  var incomeT = 0, visitorT = 0, saveT = 0;

  function moveActor(actor, dir, speed, dt, wildBounds) {
    var nx = actor.mesh.position.x + dir.x * speed * dt;
    var nz = actor.mesh.position.z + dir.z * speed * dt;
    if (wildBounds) {
      if (!isLand(nx, nz) || Math.abs(nx) > WORLD || Math.abs(nz) > WORLD || inPark(nx, nz)) return;
    }
    actor.mesh.position.x = nx; actor.mesh.position.z = nz;
    actor.mesh.rotation.y = Math.atan2(dir.x, dir.z);
    actor.moving = true;
  }

  function animateCreature(cr, dt, t) {
    var m = cr.mesh;
    cr.bob += dt * (cr.moving ? 10 : 4);
    if (m.userData.legs && cr.moving) {
      for (var i = 0; i < 4; i++) {
        m.userData.legs[i].rotation.x = Math.sin(cr.bob + (i % 2 ? Math.PI : 0)) * 0.7;
      }
    } else if (m.userData.legs) {
      for (var j = 0; j < 4; j++) m.userData.legs[j].rotation.x *= 0.85;
    }
    if (m.userData.tail) m.userData.tail.position.x = Math.sin(t * 6 + cr.bob) * 0.15;
    if (m.userData.wings) {
      m.userData.wings[0].rotation.z = 1.2 + Math.sin(t * 9) * 0.35;
      m.userData.wings[1].rotation.z = -1.2 - Math.sin(t * 9) * 0.35;
    }
  }

  function animate() {
    requestAnimationFrame(animate);
    var dt = Math.min(clock.getDelta(), 0.05);
    var t = clock.elapsedTime;
    updateSky(t);

    // water waves
    var wpos = waterMesh.geometry.attributes.position;
    for (var wi = 0; wi < wpos.count; wi += 3) {
      wpos.setY(wi, Math.sin(t * 1.2 + wi * 0.7) * 0.12);
    }
    wpos.needsUpdate = true;

    // --- player
    if (gameStarted) {
      var turn = (keys.KeyA || keys.ArrowLeft ? 1 : 0) - (keys.KeyD || keys.ArrowRight ? 1 : 0);
      var move = (keys.KeyW || keys.ArrowUp ? 1 : 0) - (keys.KeyS || keys.ArrowDown ? 1 : 0);
      yaw += turn * dt * 2.4;
      player.rotation.y = yaw;
      if (move !== 0) {
        var speed = 10 * move;
        var nx = player.position.x + Math.sin(yaw) * speed * dt;
        var nz = player.position.z + Math.cos(yaw) * speed * dt;
        nx = Math.max(-WORLD, Math.min(WORLD, nx));
        nz = Math.max(-WORLD, Math.min(WORLD, nz));
        var nh = terrainHeight(nx, nz);
        if (nh > WATER_Y + 0.15) {
          player.position.x = nx; player.position.z = nz; player.position.y = nh;
        }
        player.position.y += Math.abs(Math.sin(t * 10)) * 0.06;
      }
    }

    camPos.set(
      player.position.x - Math.sin(yaw) * 11,
      player.position.y + 7,
      player.position.z - Math.cos(yaw) * 11
    );
    camera.position.lerp(camPos, 1 - Math.pow(0.001, dt));
    camera.lookAt(player.position.x, player.position.y + 2, player.position.z);
    sun.position.set(player.position.x + 60, 120, player.position.z + 30);
    sun.target.position.copy(player.position);

    // --- wild creatures
    nearCritter = null;
    wild.forEach(function (cr) {
      cr.moving = false;
      var m = cr.mesh;
      var d = m.position.distanceTo(player.position);
      if (d < 7 && (!nearCritter || d < nearCritter._d)) { cr._d = d; nearCritter = cr; }
      if (cr.state === "flee") {
        cr.fleeT -= dt;
        var away = m.position.clone().sub(player.position).setY(0).normalize();
        moveActor(cr, away, cr.sp.speed * 2.4, dt, true);
        if (cr.fleeT <= 0) cr.state = "wander";
      } else {
        if (d < 4.5) { cr.state = "flee"; cr.fleeT = 1.2; }
        cr.idle -= dt;
        if (cr.idle <= 0) {
          var a = Math.random() * Math.PI * 2, r = 8 + Math.random() * 16;
          var tx = m.position.x + Math.cos(a) * r, tz = m.position.z + Math.sin(a) * r;
          if (isLand(tx, tz) && !inPark(tx, tz)) cr.target.set(tx, 0, tz);
          cr.idle = 2 + Math.random() * 4;
        }
        var dir = cr.target.clone().sub(m.position).setY(0);
        if (dir.length() > 0.8) moveActor(cr, dir.normalize(), cr.sp.speed, dt, true);
      }
      m.position.y = terrainHeight(m.position.x, m.position.z) + Math.abs(Math.sin(cr.bob)) * 0.1;
      animateCreature(cr, dt, t);
    });
    ui.prompt.style.display = nearCritter && !activeThrow && gameStarted ? "block" : "none";
    if (nearCritter) ui.prompt.textContent = "Wild " + nearCritter.sp.name + "! SPACE / 🎯 to throw an orb";

    // --- residents
    residents.forEach(function (r) {
      r.moving = false;
      r.idle -= dt;
      if (r.idle <= 0 || !r.target) {
        r.target = new THREE.Vector3(
          r.home.x + (Math.random() - 0.5) * 3.6, PARK.y,
          r.home.z + (Math.random() - 0.5) * 3.6);
        r.idle = 1.5 + Math.random() * 3;
      }
      var dir = r.target.clone().sub(r.mesh.position).setY(0);
      if (dir.length() > 0.4) moveActor(r, dir.normalize(), r.sp.speed * 0.5, dt, false);
      r.mesh.position.y = PARK.y + Math.abs(Math.sin(r.bob)) * 0.08;
      animateCreature(r, dt, t);
    });

    // --- visitors
    for (var vi = visitors.length - 1; vi >= 0; vi--) {
      var v = visitors[vi];
      v.life -= dt;
      if (v.life <= 0) {
        scene.remove(v.mesh); visitors.splice(vi, 1); refreshHud();
        continue;
      }
      v.idle -= dt;
      if (v.idle <= 0 || !v.target) {
        v.target = visitorTargetPos();
        v.idle = 4 + Math.random() * 6;
        if (stallCount > 0 && Math.random() < 0.3) { addCoins(1 + stallCount); AudioSys.coinSfx(); }
      }
      var vd = v.target.clone().sub(v.mesh.position).setY(0);
      if (vd.length() > 0.6) {
        vd.normalize();
        v.mesh.position.x += vd.x * 2.2 * dt;
        v.mesh.position.z += vd.z * 2.2 * dt;
        v.mesh.rotation.y = Math.atan2(vd.x, vd.z);
      }
      v.mesh.position.y = PARK.y + Math.abs(Math.sin(t * 8 + vi)) * 0.05;
    }

    // --- economy ticks
    if (gameStarted) {
      incomeT += dt;
      if (incomeT >= 5) {
        incomeT = 0;
        if (incomePerTick > 0) { addCoins(incomePerTick); }
      }
      visitorT += dt;
      var targetVisitors = Math.min(IS_DEMO ? 8 : 16, Math.floor(attraction / 6));
      if (visitorT >= 4) {
        visitorT = 0;
        if (visitors.length < targetVisitors) spawnVisitor();
        refreshHud();
      }
      saveT += dt;
      if (saveT > 12) { saveT = 0; persist(); }
    }

    // --- throw
    if (activeThrow) {
      activeThrow.t += dt * 1.8;
      var th = activeThrow;
      if (th.t >= 1) { activeThrow = null; resolveThrow(th); }
      else {
        var tp = th.to.mesh.position.clone(); tp.y += 0.8;
        th.mesh.position.lerpVectors(th.from, tp, th.t);
        th.mesh.position.y += Math.sin(th.t * Math.PI) * 3;
      }
    }

    // --- pickups
    for (var pi = pickups.length - 1; pi >= 0; pi--) {
      var pk = pickups[pi];
      pk.rotation.y += dt * 2;
      if (pk.position.distanceTo(player.position) < 2.2) {
        scene.remove(pk); pickups.splice(pi, 1);
        save.orbs += 3; refreshHud(); persist();
        AudioSys.coinSfx();
        toast("+3 orbs!");
        setTimeout(spawnPickup, 20000);
      }
    }

    // --- poofs
    for (var qi = poofs.length - 1; qi >= 0; qi--) {
      var pf = poofs[qi];
      pf.t += dt;
      pf.g.children.forEach(function (p) {
        p.position.addScaledVector(p.userData.v, dt);
        p.userData.v.y -= 9 * dt;
        p.scale.multiplyScalar(0.96);
      });
      if (pf.t > 1.2) { scene.remove(pf.g); poofs.splice(qi, 1); }
    }

    renderer.render(scene, camera);
  }

  addEventListener("resize", function () {
    camera.aspect = innerWidth / innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(innerWidth, innerHeight);
  });

  // dev hooks (used for testing & marketing screenshots)
  window.DEV = {
    coins: function (n) { addCoins(n); persist(); },
    catchAll: function () {
      SPECIES.forEach(function (s) { save.caught[s.id] = (save.caught[s.id] || 0) + 2; });
      persist(); reassignResidents(); updateEconomy();
    },
    place: function (cx, cz, type) { placeBuilding(cx, cz, type); },
    start: function () { titleEl.click(); },
    state: function () { return { coins: save.coins, attraction: attraction, stars: starCount, residents: residents.length, visitors: visitors.length }; }
  };

  animate();
})();
