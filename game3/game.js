/* =====================================================================
   WILDHAVEN ARENA — battle & catch adventure with global Battle Codes
   Original game & creatures (Wildhaven universe). Three.js r128.
   ===================================================================== */
(function () {
  "use strict";

  var CFG = window.GAME_CONFIG || { mode: "full", buyLink: "" };
  var IS_DEMO = CFG.mode === "demo";
  var SAVE_KEY = "wildhaven-arena-" + CFG.mode + "-v1";

  // ------------------------------------------------------------- species
  var SPECIES = [
    { id: "flufftail",  name: "Flufftail",  type: "meadow", color: 0x7ec850, accent: 0xe8f5d0, size: 1.0,  atk: 4, zone: 0 },
    { id: "pebblit",    name: "Pebblit",    type: "meadow", color: 0x8d8d94, accent: 0xc9c9cf, size: 0.85, atk: 3, zone: 0 },
    { id: "aquaphin",   name: "Aquaphin",   type: "water",  color: 0x4aa8d8, accent: 0xbfe6f5, size: 1.0,  atk: 4, zone: 0 },
    { id: "bubbletide", name: "Bubbletide", type: "water",  color: 0x6fc4c9, accent: 0xffffff, size: 0.8,  atk: 5, zone: 1 },
    { id: "emberling",  name: "Emberling",  type: "ember",  color: 0xe07030, accent: 0xffc84a, size: 0.9,  atk: 5, zone: 1 },
    { id: "cinderpup",  name: "Cinderpup",  type: "ember",  color: 0xb84a3a, accent: 0xffa64a, size: 0.9,  atk: 6, zone: 1 },
    { id: "mossback",   name: "Mossback",   type: "meadow", color: 0x5d7a45, accent: 0x9fb56e, size: 1.3,  atk: 5, zone: 1 },
    { id: "zephyrix",   name: "Zephyrix",   type: "sky",    color: 0xe8c832, accent: 0xffffff, size: 0.85, atk: 6, zone: 2 },
    { id: "glimmerwing",name: "Glimmerwing",type: "sky",    color: 0x9a6ad8, accent: 0xe6d0ff, size: 0.9,  atk: 7, zone: 2 },
    { id: "nocturnix",  name: "Nocturnix",  type: "night",  color: 0x3a3f6b, accent: 0x8fd0ff, size: 1.1,  atk: 8, zone: 2 }
  ];
  if (IS_DEMO) SPECIES = SPECIES.filter(function (s) { return s.zone === 0; });
  var SP = {};
  SPECIES.forEach(function (s) { SP[s.id] = s; });

  var TYPE_ICON = { meadow: "🌿", water: "💧", ember: "🔥", sky: "🌪", night: "🌙" };
  function typeBonus(a, b) { // a attacking b
    if (a === "meadow" && b === "water") return 1.5;
    if (a === "water" && b === "ember") return 1.5;
    if (a === "ember" && b === "meadow") return 1.5;
    if (b === "meadow" && a === "water") return 0.7;
    if (b === "water" && a === "ember") return 0.7;
    if (b === "ember" && a === "meadow") return 0.7;
    return 1.0;
  }
  function maxHp(lvl) { return 20 + lvl * 6; }
  function xpNeed(lvl) { return 20 + lvl * 12; }

  var ZONES = [
    { name: "Sunmeadow", sub: "Wild critters · Lv 1–5", r: 95, lvl: [1, 5], grass: 0x79b34c, lawn: 0x8cc45e },
    { name: "Ember Ridge", sub: "Wild critters · Lv 6–12", r: 175, lvl: [6, 12], grass: 0xa88a4c, lawn: 0xb5975a },
    { name: "Starfall Hills", sub: "Wild critters · Lv 12–20", r: 9999, lvl: [12, 20], grass: 0x5c6a94, lawn: 0x6b7aa8 }
  ];
  var WORLD = IS_DEMO ? 130 : 250;
  if (IS_DEMO) { ZONES = [ZONES[0]]; ZONES[0].r = 9999; }

  function zoneAt(x, z) {
    var d = Math.sqrt(x * x + z * z);
    for (var i = 0; i < ZONES.length; i++) if (d < ZONES[i].r) return i;
    return ZONES.length - 1;
  }

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
  var WATER_Y = 0;

  function terrainHeight(x, z) {
    var n = 0, amp = 1, freq = 1 / 55, sum = 0;
    for (var o = 0; o < 4; o++) {
      n += noise(x * freq + 60, z * freq + 60) * amp;
      sum += amp; amp *= 0.5; freq *= 2;
    }
    n /= sum;
    var d = Math.sqrt(x * x + z * z) / (WORLD * 1.1);
    var island = 1 - Math.pow(Math.min(d, 1), 2.4);
    var ridge = zoneAt(x, z) >= 1 ? 3 : 0;
    return (n * 0.5 + 0.5) * (13 + ridge) * island - 2.0;
  }
  function isLand(x, z) { return terrainHeight(x, z) > WATER_Y + 0.4; }

  // ----------------------------------------------------------- three.js
  var scene = new THREE.Scene();
  scene.background = new THREE.Color(0x9fd8ef);
  scene.fog = new THREE.Fog(0x9fd8ef, WORLD * 0.5, WORLD * 1.6);
  var camera = new THREE.PerspectiveCamera(62, innerWidth / innerHeight, 0.1, 2000);
  var renderer = new THREE.WebGLRenderer({ antialias: true });
  renderer.setSize(innerWidth, innerHeight);
  renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
  renderer.shadowMap.enabled = true;
  renderer.shadowMap.type = THREE.PCFSoftShadowMap;
  document.getElementById("game").appendChild(renderer.domElement);

  scene.add(new THREE.HemisphereLight(0xeaf6ff, 0x8a9a6a, 0.95));
  var sun = new THREE.DirectionalLight(0xfff2d8, 0.9);
  sun.position.set(80, 120, 40);
  sun.castShadow = true;
  sun.shadow.mapSize.set(2048, 2048);
  sun.shadow.camera.left = -60; sun.shadow.camera.right = 60;
  sun.shadow.camera.top = 60; sun.shadow.camera.bottom = -60;
  sun.shadow.camera.far = 400;
  scene.add(sun); scene.add(sun.target);

  // terrain with zone-tinted colors
  var terrainMesh;
  (function () {
    var seg = IS_DEMO ? 120 : 180;
    var geo = new THREE.PlaneGeometry(WORLD * 2.6, WORLD * 2.6, seg, seg);
    geo.rotateX(-Math.PI / 2);
    var pos = geo.attributes.position;
    var colors = new Float32Array(pos.count * 3);
    var sand = new THREE.Color(0xe8d8a0), rock = new THREE.Color(0x9a938a), c = new THREE.Color();
    for (var i = 0; i < pos.count; i++) {
      var x = pos.getX(i), z = pos.getZ(i);
      var h = terrainHeight(x, z);
      pos.setY(i, h);
      var zn = ZONES[zoneAt(x, z)];
      if (h < WATER_Y + 0.7) c.copy(sand);
      else if (h < 7) c.setHex(zn.grass).lerp(new THREE.Color(zn.lawn), Math.min(1, h / 7));
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
  var water = new THREE.Mesh(new THREE.PlaneGeometry(WORLD * 6, WORLD * 6),
    new THREE.MeshLambertMaterial({ color: 0x3f8fbf, transparent: true, opacity: 0.72 }));
  water.rotation.x = -Math.PI / 2;
  water.position.y = WATER_Y;
  scene.add(water);

  // props: trees, rocks, grass tufts
  var trunkMat = new THREE.MeshLambertMaterial({ color: 0x8a6a4a });
  var rockMat = new THREE.MeshLambertMaterial({ color: 0x9a938a });
  function scatter(count, minH, maxH, build) {
    for (var i = 0; i < count; i++) {
      var x = (Math.random() * 2 - 1) * WORLD;
      var z = (Math.random() * 2 - 1) * WORLD;
      var h = terrainHeight(x, z);
      if (h < minH || h > maxH) continue;
      var obj = build(zoneAt(x, z));
      obj.position.set(x, h, z);
      obj.rotation.y = Math.random() * Math.PI * 2;
      obj.scale.setScalar(0.7 + Math.random() * 0.7);
      scene.add(obj);
    }
  }
  var LEAF = [0x4e8a3a, 0x8a6a2a, 0x4a5a8a];
  function makeTree(zi) {
    var g = new THREE.Group();
    var trunk = new THREE.Mesh(new THREE.CylinderGeometry(0.25, 0.35, 2.2, 6), trunkMat);
    trunk.position.y = 1.1; trunk.castShadow = true;
    var fol = new THREE.Mesh(new THREE.ConeGeometry(1.7, 3.4, 7),
      new THREE.MeshLambertMaterial({ color: LEAF[Math.min(zi, 2)] }));
    fol.position.y = 3.5; fol.castShadow = true;
    g.add(trunk, fol);
    return g;
  }
  function makeRock() {
    var g = new THREE.Group();
    var r = new THREE.Mesh(new THREE.IcosahedronGeometry(0.9, 0), rockMat);
    r.position.y = 0.3; r.castShadow = true;
    g.add(r); return g;
  }
  var TUFT = [0x9fd45e, 0xd4b45e, 0x8f9fd4];
  function makeTuft(zi) {
    var g = new THREE.Group();
    var m = new THREE.MeshLambertMaterial({ color: TUFT[Math.min(zi, 2)] });
    for (var i = 0; i < 5; i++) {
      var blade = new THREE.Mesh(new THREE.ConeGeometry(0.09, 0.8 + Math.random() * 0.5, 4), m);
      blade.position.set((Math.random() - 0.5) * 0.7, 0.4, (Math.random() - 0.5) * 0.7);
      blade.rotation.z = (Math.random() - 0.5) * 0.4;
      g.add(blade);
    }
    return g;
  }
  scatter(IS_DEMO ? 130 : 380, 1.2, 8, makeTree);
  scatter(IS_DEMO ? 40 : 120, 0.8, 12, makeRock);
  scatter(IS_DEMO ? 260 : 700, 0.8, 6, makeTuft);

  // ---------------------------------------------------------------- audio
  var AudioSys = (function () {
    var ctx = null, master, muted = false, started = false, nextBar = 0, barIdx = 0;
    var chordRoot = [0, 7, 5, 3];
    function ensure() {
      if (ctx) return true;
      var AC = window.AudioContext || window.webkitAudioContext;
      if (!AC) return false;
      ctx = new AC();
      master = ctx.createGain(); master.gain.value = 0.7; master.connect(ctx.destination);
      return true;
    }
    function freq(s) { return 261.63 * Math.pow(2, s / 12); }
    function tone(f0, f1, dur, type, vol, when) {
      if (!ctx || muted) return;
      var t = when || ctx.currentTime;
      var o = ctx.createOscillator(); o.type = type || "sine";
      o.frequency.setValueAtTime(f0, t);
      o.frequency.exponentialRampToValueAtTime(Math.max(f1, 1), t + dur);
      var g = ctx.createGain();
      g.gain.setValueAtTime(vol || 0.2, t);
      g.gain.exponentialRampToValueAtTime(0.001, t + dur);
      o.connect(g); g.connect(master);
      o.start(t); o.stop(t + dur + 0.05);
    }
    function music() {
      if (!ctx || muted) return;
      var now = ctx.currentTime;
      while (nextBar < now + 4) {
        var t = Math.max(nextBar, now + 0.05);
        var root = chordRoot[barIdx % 4];
        [root - 12, root - 5, root + 3].forEach(function (s) {
          tone(freq(s), freq(s), 3.6, "triangle", 0.05, t);
        });
        for (var i = 0; i < 4; i++) {
          if (Math.random() < 0.6) tone(freq(root + [0, 3, 7, 10][Math.floor(Math.random() * 4)]) * 2,
            freq(root) * 2, 0.5, "sine", 0.06, t + i * 0.9);
        }
        nextBar = t + 3.6; barIdx++;
      }
    }
    return {
      start: function () {
        if (started || !ensure()) return;
        started = true;
        if (ctx.state === "suspended") ctx.resume();
        nextBar = ctx.currentTime + 0.1;
        setInterval(music, 900);
      },
      hit: function () { tone(220, 90, 0.22, "sawtooth", 0.22); },
      special: function () { tone(600, 1400, 0.3, "square", 0.14); },
      catchOk: function () { [0, 4, 7, 12].forEach(function (s, i) { tone(freq(s + 12), freq(s + 12), 0.25, "triangle", 0.18, ctx ? ctx.currentTime + i * 0.09 : 0); }); },
      fail: function () { tone(300, 140, 0.35, "triangle", 0.16); },
      levelup: function () { [0, 7, 12, 19].forEach(function (s, i) { tone(freq(s + 12), freq(s + 12), 0.35, "triangle", 0.18, ctx ? ctx.currentTime + i * 0.11 : 0); }); },
      click: function () { tone(900, 700, 0.06, "square", 0.07); },
      toggleMute: function () { muted = !muted; if (master) master.gain.value = muted ? 0 : 0.7; return muted; }
    };
  })();

  // --------------------------------------------------------------- player
  var player = new THREE.Group();
  (function () {
    var mat = new THREE.MeshLambertMaterial({ color: 0x4a7ad8 });
    var skin = new THREE.MeshLambertMaterial({ color: 0xf5c9a0 });
    var body = new THREE.Mesh(new THREE.CylinderGeometry(0.4, 0.48, 1.0, 10), mat);
    body.position.y = 0.9; body.castShadow = true;
    var head = new THREE.Mesh(new THREE.SphereGeometry(0.36, 12, 10), skin);
    head.position.y = 1.72; head.castShadow = true;
    var cap = new THREE.Mesh(new THREE.SphereGeometry(0.38, 12, 8, 0, Math.PI * 2, 0, Math.PI / 2),
      new THREE.MeshLambertMaterial({ color: 0xd85a4a }));
    cap.position.y = 1.78;
    player.add(body, head, cap);
  })();
  player.position.set(4, terrainHeight(4, 4), 4);
  scene.add(player);

  // ------------------------------------------------------------ creatures
  function buildCreature(sp, scale) {
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
    var legs = [];
    for (var li = 0; li < 4; li++) {
      var leg = new THREE.Mesh(new THREE.CylinderGeometry(0.09, 0.11, 0.42, 6), mat);
      leg.position.set(li % 2 ? 0.28 : -0.28, 0.22, li < 2 ? 0.3 : -0.3);
      legs.push(leg); g.add(leg);
    }
    g.userData.legs = legs;
    if (sp.type === "meadow") {
      var ear1 = new THREE.Mesh(new THREE.ConeGeometry(0.1, 0.55, 6), mat);
      ear1.position.set(0.16, 1.56, 0.32);
      var ear2 = ear1.clone(); ear2.position.x = -0.16;
      g.add(ear1, ear2);
    }
    if (sp.type === "ember") {
      var flame = new THREE.Mesh(new THREE.ConeGeometry(0.18, 0.55, 7),
        new THREE.MeshLambertMaterial({ color: sp.accent, emissive: 0x552200 }));
      flame.position.set(0, 0.9, -0.66); flame.rotation.x = 0.7;
      g.add(flame);
    }
    if (sp.type === "water") {
      var fin = new THREE.Mesh(new THREE.ConeGeometry(0.22, 0.5, 4), acc);
      fin.position.set(0, 1.3, 0.02); fin.rotation.x = -0.4;
      g.add(fin);
    }
    if (sp.type === "sky" || sp.type === "night") {
      var wingGeo = new THREE.ConeGeometry(0.3, 0.8, 4);
      var w1 = new THREE.Mesh(wingGeo, acc);
      w1.position.set(0.6, 1.0, -0.05); w1.rotation.z = 1.2;
      var w2 = new THREE.Mesh(wingGeo, acc);
      w2.position.set(-0.6, 1.0, -0.05); w2.rotation.z = -1.2;
      g.add(w1, w2);
      g.userData.wings = [w1, w2];
    }
    g.scale.setScalar(sp.size * (scale || 1));
    return g;
  }
  function crown(mesh, sp) {
    var c = new THREE.Mesh(new THREE.ConeGeometry(0.35, 0.5, 5),
      new THREE.MeshLambertMaterial({ color: 0xffd870, emissive: 0x554400 }));
    c.position.y = 1.9 / sp.size;
    mesh.add(c);
  }

  function randPos(minR, maxR) {
    for (var t = 0; t < 200; t++) {
      var a = Math.random() * Math.PI * 2;
      var r = minR + Math.random() * (maxR - minR);
      var x = Math.cos(a) * r, z = Math.sin(a) * r;
      if (isLand(x, z)) return new THREE.Vector3(x, terrainHeight(x, z), z);
    }
    return new THREE.Vector3(6, terrainHeight(6, 6), 6);
  }

  var wild = [];
  function spawnWild(zoneIdx, guardian) {
    var pool = SPECIES.filter(function (s) { return s.zone <= zoneIdx; });
    var sp = pool[Math.floor(Math.random() * pool.length)];
    var zn = ZONES[zoneIdx];
    var lvl = guardian ? [8, 15, 22][zoneIdx] :
      zn.lvl[0] + Math.floor(Math.random() * (zn.lvl[1] - zn.lvl[0] + 1));
    if (guardian) sp = SPECIES.filter(function (s) { return s.zone === Math.min(zoneIdx, SPECIES[SPECIES.length - 1].zone); }).slice(-1)[0];
    var mesh = buildCreature(sp, guardian ? 2.2 : 1);
    var minR = zoneIdx === 0 ? 8 : ZONES[zoneIdx - 1].r;
    var maxR = Math.min(zn.r === 9999 ? WORLD * 0.9 : zn.r, WORLD * 0.9);
    var p = guardian ? randPos(maxR * 0.55, maxR * 0.8) : randPos(minR, maxR);
    mesh.position.copy(p);
    if (guardian) crown(mesh, sp);
    scene.add(mesh);
    wild.push({ sp: sp, lvl: lvl, hp: maxHp(lvl), mesh: mesh, guardian: !!guardian,
      state: "wander", target: p.clone(), idle: Math.random() * 3, bob: Math.random() * 10, moving: false, zone: zoneIdx });
  }
  ZONES.forEach(function (zn, zi) {
    var n = IS_DEMO ? 8 : 7;
    for (var i = 0; i < n; i++) spawnWild(zi, false);
    spawnWild(zi, true);   // one Guardian per zone
  });

  // pickups
  var pickups = [];
  var orbGeo = new THREE.SphereGeometry(0.35, 10, 8);
  var orbMat = new THREE.MeshLambertMaterial({ color: 0xffffff, emissive: 0x7A3FA0 });
  function spawnPickup() {
    var m = new THREE.Mesh(orbGeo, orbMat);
    m.position.copy(randPos(6, WORLD * 0.85)); m.position.y += 0.8;
    scene.add(m);
    pickups.push(m);
  }
  for (var pi0 = 0; pi0 < (IS_DEMO ? 12 : 24); pi0++) spawnPickup();

  // ---------------------------------------------------------------- save
  var save = { orbs: 5, team: [{ id: SPECIES[0].id, lvl: 3, xp: 0, hp: maxHp(3) }],
               badges: {}, pvpW: 0, pvpL: 0, muted: false, helpSeen: false };
  try {
    var raw = localStorage.getItem(SAVE_KEY);
    if (raw) { var l = JSON.parse(raw); for (var k in l) save[k] = l[k]; }
  } catch (e) {}
  function persist() { try { localStorage.setItem(SAVE_KEY, JSON.stringify(save)); } catch (e) {} }

  // ------------------------------------------------------------------ ui
  function $(id) { return document.getElementById(id); }
  var toastT = null;
  function toast(m) {
    $("toast").textContent = m;
    $("toast").classList.add("show");
    clearTimeout(toastT);
    toastT = setTimeout(function () { $("toast").classList.remove("show"); }, 2800);
  }
  function refreshHud() {
    $("orbs").textContent = save.orbs;
    $("badges").textContent = Object.keys(save.badges).length + " / " + ZONES.length;
    $("pvp").textContent = save.pvpW + "W · " + save.pvpL + "L";
    var tb = $("teambar");
    tb.innerHTML = "";
    for (var i = 0; i < 3; i++) {
      var d = document.createElement("div");
      if (save.team[i]) {
        var m = save.team[i], sp = SP[m.id];
        d.className = "slot" + (i === 0 ? " active" : "");
        d.innerHTML = '<div class="nm">' + TYPE_ICON[sp.type] + " " + sp.name +
          ' <span class="lv">Lv' + m.lvl + "</span></div>" +
          '<div class="hpbar"><div class="hpfill" style="width:' +
          Math.max(0, Math.round(m.hp / maxHp(m.lvl) * 100)) + '%"></div></div>';
      } else {
        d.className = "slot empty";
        d.textContent = "— empty —";
      }
      tb.appendChild(d);
    }
  }

  // floating creature cards
  var cards = [];
  for (var ci = 0; ci < 12; ci++) {
    var el = document.createElement("div");
    el.className = "ccard";
    el.innerHTML = '<span class="lv"></span><div class="nm"></div><div class="hpbar"><div class="hpfill"></div></div>';
    document.body.appendChild(el);
    cards.push(el);
  }
  var v3 = new THREE.Vector3();
  function updateCards() {
    var used = 0;
    var list = (battle && battle.wild && battle.wild.pvp && battle.wild.mesh)
      ? [battle.wild].concat(wild) : wild;
    for (var i = 0; i < list.length && used < cards.length; i++) {
      var cr = list[i];
      var d = cr.mesh.position.distanceTo(player.position);
      if (d > 26) continue;
      v3.copy(cr.mesh.position); v3.y += 2.1 * cr.sp.size * (cr.guardian ? 2.2 : 1);
      v3.project(camera);
      if (v3.z > 1) continue;
      var el2 = cards[used++];
      el2.style.display = "block";
      el2.style.left = ((v3.x * 0.5 + 0.5) * innerWidth) + "px";
      el2.style.top = ((-v3.y * 0.5 + 0.5) * innerHeight) + "px";
      el2.querySelector(".nm").textContent = (cr.guardian ? "👑 " : "") + cr.sp.name;
      el2.querySelector(".lv").textContent = "Lv" + cr.lvl;
      el2.querySelector(".hpfill").style.width = Math.round(cr.hp / maxHp(cr.lvl) * 100) + "%";
    }
    for (; used < cards.length; used++) cards[used].style.display = "none";
  }

  function dmgFloat(x, y, txt, color) {
    var el = document.createElement("div");
    el.className = "dmg";
    el.style.left = x + "px"; el.style.top = y + "px";
    if (color) el.style.color = color;
    el.textContent = txt;
    document.body.appendChild(el);
    requestAnimationFrame(function () {
      el.style.top = (y - 80) + "px"; el.style.opacity = "0";
    });
    setTimeout(function () { el.remove(); }, 950);
  }

  // zone banner
  var lastZone = -1;
  function checkZone() {
    var zi = zoneAt(player.position.x, player.position.z);
    if (zi !== lastZone) {
      lastZone = zi;
      $("zone-name").textContent = ZONES[zi].name;
      $("zone-sub").textContent = ZONES[zi].sub;
      $("zone-banner").classList.add("show");
      clearTimeout(checkZone._t);
      checkZone._t = setTimeout(function () { $("zone-banner").classList.remove("show"); }, 2600);
    }
  }

  // --------------------------------------------------------------- battle
  var battle = null;   // {wild, myIdx, over, pvp}
  function log(m) { $("b-log").textContent = m; }
  function myMon() { return save.team[battle.myIdx]; }

  function startBattle(cr) {
    battle = { wild: cr, myIdx: 0, over: false, busy: false };
    save.team.forEach(function (m) { if (m.hp <= 0) m.hp = 1; });
    $("battle").classList.add("open");
    $("b-catch").style.display = cr.pvp ? "none" : "";
    log("A wild " + (cr.guardian ? "GUARDIAN " : "") + cr.sp.name + " (Lv" + cr.lvl + ") challenges you!");
    refreshHud();
  }
  function endBattle(msg) {
    battle.over = true;
    if (battle.wild && battle.wild.pvp && battle.wild.mesh) scene.remove(battle.wild.mesh);
    $("battle").classList.remove("open");
    if (msg) toast(msg);
    battle = null;
    persist(); refreshHud();
  }
  function dmgRoll(atkSp, atkLvl, defSp) {
    var base = 4 + atkSp.atk * (1 + atkLvl * 0.12);
    return Math.max(1, Math.round(base * typeBonus(atkSp.type, defSp.type) * (0.85 + Math.random() * 0.3)));
  }
  function screenOf(mesh, up) {
    v3.copy(mesh.position); v3.y += up || 1.5;
    v3.project(camera);
    return [(v3.x * 0.5 + 0.5) * innerWidth, (-v3.y * 0.5 + 0.5) * innerHeight];
  }
  function lunge(mesh, toward) {
    var start = mesh.position.clone();
    var dir = toward.clone().sub(start).normalize().multiplyScalar(1.2);
    var t0 = performance.now();
    (function anim() {
      var t = (performance.now() - t0) / 260;
      if (t >= 1) { mesh.position.copy(start); return; }
      var k = Math.sin(t * Math.PI);
      mesh.position.copy(start).addScaledVector(dir, k);
      requestAnimationFrame(anim);
    })();
  }
  function giveXp(amount) {
    var m = myMon(), sp = SP[m.id];
    m.xp += amount;
    var leveled = false;
    while (m.xp >= xpNeed(m.lvl)) {
      m.xp -= xpNeed(m.lvl);
      m.lvl++;
      m.hp = maxHp(m.lvl);
      leveled = true;
    }
    if (leveled) { AudioSys.levelup(); toast("⬆️ " + sp.name + " grew to Lv" + m.lvl + "!"); }
  }
  function wildTurn() {
    if (!battle || battle.over) return;
    var cr = battle.wild, m = myMon(), sp = SP[m.id];
    var dmg = dmgRoll(cr.sp, cr.lvl, sp);
    m.hp -= dmg;
    AudioSys.hit();
    if (cr.mesh) lunge(cr.mesh, player.position);
    dmgFloat(innerWidth * 0.3, innerHeight * 0.6, "-" + dmg);
    refreshHud();
    if (m.hp <= 0) {
      m.hp = 0;
      var next = save.team.findIndex(function (t) { return t.hp > 0; });
      if (next === -1) {
        var wasPvp = !!battle.pvpQueue;
        if (wasPvp) save.pvpL++;
        save.team.forEach(function (t) { t.hp = Math.round(maxHp(t.lvl) / 2); });
        endBattle(wasPvp ? "💔 Duel lost! Train up and challenge them again."
                         : "Your team fainted! They limp home to recover…");
        if (!wasPvp) player.position.set(4, terrainHeight(4, 4), 4);
        return;
      }
      battle.myIdx = next;
      log(sp.name + " fainted! Go, " + SP[save.team[next].id].name + "!");
    } else {
      log(cr.sp.name + " hits " + sp.name + " for " + dmg + "!");
    }
    battle.busy = false;
  }
  function playerMove(special) {
    if (!battle || battle.busy || battle.over) return;
    battle.busy = true;
    var cr = battle.wild, m = myMon(), sp = SP[m.id];
    var dmg = dmgRoll(sp, m.lvl, cr.sp);
    if (special) { dmg = Math.round(dmg * 1.35); AudioSys.special(); }
    else AudioSys.hit();
    cr.hp -= dmg;
    if (cr.mesh) {
      lunge(player, cr.mesh.position);
      var s = screenOf(cr.mesh, 2);
      dmgFloat(s[0], s[1], "-" + dmg, special ? "#c58af0" : undefined);
    } else {
      dmgFloat(innerWidth * 0.7, innerHeight * 0.4, "-" + dmg, special ? "#c58af0" : undefined);
    }
    log(sp.name + " uses " + (special ? "Special" : "Attack") + "! " + dmg + " damage.");
    if (cr.hp <= 0) {
      if (cr.pvp) { pvpNext(); return; }
      var xp = 10 + cr.lvl * 4 + (cr.guardian ? 40 : 0);
      giveXp(xp);
      if (cr.guardian) {
        save.badges["z" + cr.zone] = true;
        toast("🏅 GUARDIAN of " + ZONES[cr.zone].name + " defeated!");
        if (Object.keys(save.badges).length >= ZONES.length) {
          setTimeout(function () { $("champion").classList.add("open"); }, 800);
        }
      }
      scene.remove(cr.mesh);
      wild.splice(wild.indexOf(cr), 1);
      setTimeout(function () { spawnWild(cr.zone, cr.guardian); }, cr.guardian ? 60000 : 12000);
      endBattle("Victory! +" + xp + " XP");
      return;
    }
    setTimeout(wildTurn, 700);
  }
  $("b-attack").addEventListener("click", function () { playerMove(false); });
  $("b-special").addEventListener("click", function () { playerMove(true); });
  $("b-run").addEventListener("click", function () {
    if (!battle || battle.busy) return;
    if (battle.pvpQueue) { save.pvpL++; endBattle("You forfeited the duel."); return; }
    endBattle("You got away safely!");
  });
  $("b-catch").addEventListener("click", function () {
    if (!battle || battle.busy || battle.over || battle.wild.pvp) return;
    if (save.orbs <= 0) { log("No orbs! Find glowing orbs in the wild."); return; }
    if (battle.wild.guardian) { log("Guardians cannot be caught — only defeated!"); return; }
    battle.busy = true;
    save.orbs--;
    var cr = battle.wild;
    var chance = (1 - cr.hp / maxHp(cr.lvl)) * 0.85 + 0.12;
    if (Math.random() < chance) {
      AudioSys.catchOk();
      if (save.team.length < 3) {
        save.team.push({ id: cr.sp.id, lvl: cr.lvl, xp: 0, hp: maxHp(cr.lvl) });
        toast("🎉 " + cr.sp.name + " joined your team!");
      } else {
        var weakest = save.team.reduce(function (a, b, i, arr) { return arr[a].lvl <= b.lvl ? a : arr.indexOf(b); }, 0);
        toast(cr.sp.name + " caught! (Team full — it swaps with your lowest-level teammate.)");
        save.team[weakest] = { id: cr.sp.id, lvl: cr.lvl, xp: 0, hp: maxHp(cr.lvl) };
      }
      scene.remove(cr.mesh);
      wild.splice(wild.indexOf(cr), 1);
      setTimeout(function () { spawnWild(cr.zone, false); }, 12000);
      endBattle(null);
    } else {
      AudioSys.fail();
      log(cr.sp.name + " broke free! (Weaken it first — low HP = easier catch.)");
      setTimeout(wildTurn, 700);
    }
    refreshHud();
  });

  // ---------------------------------------------------- global battle codes
  function myCode() {
    return "WA1." + btoa(JSON.stringify({ t: save.team.map(function (m) { return { id: m.id, lvl: m.lvl }; }) }));
  }
  function parseCode(s) {
    s = (s || "").trim();
    if (s.indexOf("WA1.") !== 0) return null;
    try {
      var d = JSON.parse(atob(s.slice(4)));
      if (!d.t || !d.t.length) return null;
      var team = d.t.slice(0, 3).filter(function (m) { return SP[m.id] && m.lvl >= 1 && m.lvl <= 40; });
      return team.length ? team : null;
    } catch (e) { return null; }
  }
  // rival creature stood in front of the player during a duel
  function spawnRival(id, lvl) {
    var sp = SP[id];
    var mesh = buildCreature(sp);
    var fx = player.position.x + Math.sin(yaw) * 6;
    var fz = player.position.z + Math.cos(yaw) * 6;
    var fy = terrainHeight(fx, fz);
    if (fy <= WATER_Y + 0.15) { fx = player.position.x; fz = player.position.z + 4; fy = terrainHeight(fx, fz); }
    mesh.position.set(fx, Math.max(fy, WATER_Y + 0.2), fz);
    mesh.lookAt(player.position.x, mesh.position.y, player.position.z);
    scene.add(mesh);
    return mesh;
  }
  function pvpNext() {
    var q = battle.pvpQueue;
    q.shift();
    if (battle.wild.mesh) scene.remove(battle.wild.mesh);
    if (!q.length) {
      save.pvpW++;
      giveXp(30);
      endBattle("🏆 DUEL WON! Their whole team is down. +30 XP");
      return;
    }
    var nxt = q[0];
    battle.wild = { sp: SP[nxt.id], lvl: nxt.lvl, hp: maxHp(nxt.lvl), pvp: true,
                    mesh: spawnRival(nxt.id, nxt.lvl) };
    log("They send out " + battle.wild.sp.name + " (Lv" + battle.wild.lvl + ")!");
    battle.busy = false;
  }
  $("duel-btn").addEventListener("click", function () {
    AudioSys.click();
    $("my-code").value = myCode();
    $("duel").classList.add("open");
  });
  $("duel-close").addEventListener("click", function () { $("duel").classList.remove("open"); });
  $("copy-code").addEventListener("click", function () {
    var ta = $("my-code");
    ta.select();
    try { document.execCommand("copy"); } catch (e) {}
    if (navigator.clipboard) navigator.clipboard.writeText(ta.value).catch(function () {});
    toast("Battle Code copied — send it to a rival anywhere on Earth!");
  });
  $("fight-btn").addEventListener("click", function () {
    var team = parseCode($("their-code").value);
    if (!team) { toast("That Battle Code doesn't look right."); return; }
    $("duel").classList.remove("open");
    var first = team[0];
    startBattle({ sp: SP[first.id], lvl: first.lvl, hp: maxHp(first.lvl), pvp: true,
                  mesh: spawnRival(first.id, first.lvl) });
    battle.pvpQueue = team.slice();
    log("DUEL! They send out " + SP[first.id].name + " (Lv" + first.lvl + ")!");
  });

  // ------------------------------------------------------------ misc UI
  $("help-btn").addEventListener("click", function () { $("help").classList.add("open"); });
  $("help-close").addEventListener("click", function () {
    $("help").classList.remove("open");
    save.helpSeen = true; persist();
  });
  $("champion-close").addEventListener("click", function () { $("champion").classList.remove("open"); });
  $("mute-btn").addEventListener("click", function () {
    var m = AudioSys.toggleMute();
    $("mute-btn").textContent = m ? "🔇" : "🔊";
  });
  var gameStarted = false;
  $("title-overlay").addEventListener("click", function () {
    this.style.display = "none";
    gameStarted = true;
    AudioSys.start();
    if (!save.helpSeen) $("help").classList.add("open");
  });
  if (IS_DEMO && CFG.buyLink) {
    $("demo-banner").style.display = "flex";
    $("buy-full").href = CFG.buyLink;
  }
  refreshHud();

  // --------------------------------------------------------------- input
  var keys = {};
  addEventListener("keydown", function (e) {
    keys[e.code] = true;
    if (e.code === "Space") { e.preventDefault(); tryEngage(); }
  });
  addEventListener("keyup", function (e) { keys[e.code] = false; });
  function bindHold(id, code) {
    var el = $(id);
    if (!el) return;
    var on = function (e) { e.preventDefault(); keys[code] = true; };
    var off = function (e) { e.preventDefault(); keys[code] = false; };
    el.addEventListener("touchstart", on); el.addEventListener("touchend", off);
    el.addEventListener("mousedown", on); el.addEventListener("mouseup", off);
    el.addEventListener("mouseleave", off);
  }
  bindHold("t-up", "KeyW"); bindHold("t-down", "KeyS");
  bindHold("t-left", "KeyA"); bindHold("t-right", "KeyD");
  $("t-act").addEventListener("touchstart", function (e) { e.preventDefault(); tryEngage(); });
  $("t-act").addEventListener("mousedown", function (e) { e.preventDefault(); tryEngage(); });
  if ("ontouchstart" in window) $("touch").style.display = "block";

  var nearCr = null;
  function tryEngage() {
    if (!gameStarted || battle) return;
    if (nearCr) startBattle(nearCr);
  }

  // ---------------------------------------------------------- game loop
  var yaw = 0, vel = new THREE.Vector3(), speedCur = 0;
  var clock = new THREE.Clock();
  var camPos = new THREE.Vector3();

  function animate() {
    requestAnimationFrame(animate);
    var dt = Math.min(clock.getDelta(), 0.05);
    var t = clock.elapsedTime;

    // ---- SMOOTH player movement: acceleration, sprint, eased camera
    if (gameStarted && !battle) {
      var turn = (keys.KeyA || keys.ArrowLeft ? 1 : 0) - (keys.KeyD || keys.ArrowRight ? 1 : 0);
      var move = (keys.KeyW || keys.ArrowUp ? 1 : 0) - (keys.KeyS || keys.ArrowDown ? 1 : 0);
      var sprint = keys.ShiftLeft || keys.ShiftRight;
      yaw += turn * dt * (2.2 + speedCur * 0.06);
      player.rotation.y = yaw;
      var target = move * (sprint ? 16 : 9);
      speedCur += (target - speedCur) * Math.min(1, dt * 6);   // eased accel/decel
      if (Math.abs(speedCur) > 0.05) {
        var nx = player.position.x + Math.sin(yaw) * speedCur * dt;
        var nz = player.position.z + Math.cos(yaw) * speedCur * dt;
        nx = Math.max(-WORLD, Math.min(WORLD, nx));
        nz = Math.max(-WORLD, Math.min(WORLD, nz));
        var nh = terrainHeight(nx, nz);
        if (nh > WATER_Y + 0.15) {
          player.position.x = nx; player.position.z = nz;
          player.position.y += (nh - player.position.y) * Math.min(1, dt * 12);
        } else speedCur = 0;
        player.position.y += Math.abs(Math.sin(t * (sprint ? 14 : 10))) * 0.05 * Math.min(1, Math.abs(speedCur) / 6);
        player.rotation.z = -turn * 0.06 * Math.min(1, Math.abs(speedCur) / 8); // lean
      } else player.rotation.z *= 0.9;
      camera.fov += ((sprint && move ? 68 : 62) - camera.fov) * Math.min(1, dt * 4);
      camera.updateProjectionMatrix();
      checkZone();
    }

    // camera: battle framing vs follow
    if (battle && battle.wild.mesh) {
      var wm = battle.wild.mesh.position;
      camPos.set(
        (player.position.x + wm.x) / 2 + Math.sin(yaw + 1.9) * 7,
        Math.max(player.position.y, wm.y) + 3.4,
        (player.position.z + wm.z) / 2 + Math.cos(yaw + 1.9) * 7);
      camera.position.lerp(camPos, 1 - Math.pow(0.001, dt));
      camera.lookAt((player.position.x + wm.x) / 2, wm.y + 1, (player.position.z + wm.z) / 2);
    } else {
      camPos.set(
        player.position.x - Math.sin(yaw) * 10.5,
        player.position.y + 6.2,
        player.position.z - Math.cos(yaw) * 10.5);
      camera.position.lerp(camPos, 1 - Math.pow(0.0005, dt));
      camera.lookAt(player.position.x, player.position.y + 2, player.position.z);
    }
    sun.position.set(player.position.x + 60, 120, player.position.z + 30);
    sun.target.position.copy(player.position);

    // ---- wild critters
    nearCr = null;
    wild.forEach(function (cr) {
      cr.moving = false;
      var m = cr.mesh;
      var d = m.position.distanceTo(player.position);
      if (d < 6.5 && (!nearCr || d < nearCr._d)) { cr._d = d; nearCr = cr; }
      if (battle && battle.wild === cr) {
        m.lookAt(player.position.x, m.position.y, player.position.z);
      } else {
        cr.idle -= dt;
        if (cr.idle <= 0) {
          var a = Math.random() * Math.PI * 2, r = 6 + Math.random() * 14;
          var tx = m.position.x + Math.cos(a) * r, tz = m.position.z + Math.sin(a) * r;
          if (isLand(tx, tz) && zoneAt(tx, tz) === cr.zone) cr.target.set(tx, 0, tz);
          cr.idle = 2 + Math.random() * 4;
        }
        var dir = cr.target.clone().sub(m.position).setY(0);
        if (dir.length() > 0.8) {
          dir.normalize();
          var sp2 = cr.guardian ? 0.7 : 2.0;
          var nx2 = m.position.x + dir.x * sp2 * dt, nz2 = m.position.z + dir.z * sp2 * dt;
          if (isLand(nx2, nz2)) {
            m.position.x = nx2; m.position.z = nz2;
            m.rotation.y = Math.atan2(dir.x, dir.z);
            cr.moving = true;
          }
        }
      }
      m.position.y = terrainHeight(m.position.x, m.position.z) + Math.abs(Math.sin(cr.bob)) * 0.1;
      cr.bob += dt * (cr.moving ? 9 : 4);
      if (m.userData.legs) {
        for (var i = 0; i < 4; i++) {
          m.userData.legs[i].rotation.x = cr.moving ?
            Math.sin(cr.bob + (i % 2 ? Math.PI : 0)) * 0.7 :
            m.userData.legs[i].rotation.x * 0.85;
        }
      }
      if (m.userData.wings) {
        m.userData.wings[0].rotation.z = 1.2 + Math.sin(t * 9) * 0.35;
        m.userData.wings[1].rotation.z = -1.2 - Math.sin(t * 9) * 0.35;
      }
    });
    $("prompt").style.display = nearCr && !battle && gameStarted ? "block" : "none";
    if (nearCr) $("prompt").textContent =
      (nearCr.guardian ? "👑 GUARDIAN " : "Wild ") + nearCr.sp.name +
      " Lv" + nearCr.lvl + " — SPACE / ⚔️ to battle!";

    // pickups
    for (var pi = pickups.length - 1; pi >= 0; pi--) {
      var pk = pickups[pi];
      pk.rotation.y += dt * 2;
      if (pk.position.distanceTo(player.position) < 2.2) {
        scene.remove(pk); pickups.splice(pi, 1);
        save.orbs += 2; persist(); refreshHud();
        toast("+2 orbs!");
        setTimeout(spawnPickup, 18000);
      }
    }

    updateCards();
    renderer.render(scene, camera);
  }

  addEventListener("resize", function () {
    camera.aspect = innerWidth / innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(innerWidth, innerHeight);
  });

  // dev hooks for testing
  window.DEV = {
    state: function () {
      return { team: save.team, orbs: save.orbs, badges: Object.keys(save.badges).length,
               wild: wild.length, zone: lastZone, pvp: [save.pvpW, save.pvpL] };
    },
    start: function () { $("title-overlay").click(); },
    lvl: function (n) { save.team.forEach(function (m) { m.lvl = n; m.hp = maxHp(n); }); refreshHud(); },
    orbs: function (n) { save.orbs += n; refreshHud(); },
    near: function () { return nearCr && { sp: nearCr.sp.id, lvl: nearCr.lvl }; },
    engage: tryEngage,
    code: myCode,
    wildAt: function (i) {
      var c = wild[i];
      return c && [c.mesh.position.x, c.mesh.position.z, c.sp.id, c.lvl, c.guardian];
    },
    teleport: function (x, z) { player.position.set(x, terrainHeight(x, z), z); }
  };

  animate();
})();
