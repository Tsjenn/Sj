/* =====================================================================
   CRITTER ISLES — a cozy 3D creature-catching adventure
   Original game & creatures. Built with Three.js (r128, vendored).

   Reads window.GAME_CONFIG:
     mode:      'demo' | 'full'
     buyLink:   URL shown in the demo's upgrade banner (demo only)
   ===================================================================== */
(function () {
  "use strict";

  var CFG = window.GAME_CONFIG || { mode: "full", buyLink: "" };
  var IS_DEMO = CFG.mode === "demo";

  // ------------------------------------------------------------- species
  // build: primitive shapes only — every creature is original art.
  var SPECIES = [
    { id: "flufftail",  name: "Flufftail",  color: 0x7ec850, accent: 0xe8f5d0, size: 1.0, speed: 2.2, catchRate: 0.75, hint: "Common in grassy meadows." },
    { id: "pebblit",    name: "Pebblit",    color: 0x8d8d94, accent: 0xc9c9cf, size: 0.8, speed: 1.2, catchRate: 0.75, hint: "Naps beside rocks." },
    { id: "aquaphin",   name: "Aquaphin",   color: 0x4aa8d8, accent: 0xbfe6f5, size: 1.0, speed: 2.6, catchRate: 0.6,  hint: "Splashes near the shoreline." },
    { id: "emberling",  name: "Emberling",  color: 0xe07030, accent: 0xffc84a, size: 0.9, speed: 2.8, catchRate: 0.55, hint: "A warm glow at the island's heart." },
    { id: "mossback",   name: "Mossback",   color: 0x5d7a45, accent: 0x9fb56e, size: 1.3, speed: 0.9, catchRate: 0.7,  hint: "Slow, sturdy, moss-covered." },
    { id: "zephyrix",   name: "Zephyrix",   color: 0xe8c832, accent: 0xffffff, size: 0.85, speed: 4.2, catchRate: 0.45, hint: "Fast as the wind on the hills." },
    { id: "glimmerwing",name: "Glimmerwing",color: 0x9a6ad8, accent: 0xe6d0ff, size: 0.9, speed: 3.2, catchRate: 0.4,  hint: "Sparkles at the forest edge." },
    { id: "nocturnix",  name: "Nocturnix",  color: 0x3a3f6b, accent: 0x8fd0ff, size: 1.1, speed: 3.6, catchRate: 0.3,  hint: "The rarest of all. Keep looking." }
  ];
  if (IS_DEMO) SPECIES = SPECIES.slice(0, 3);

  var WORLD = IS_DEMO ? 150 : 300;          // world half-size in units
  var PER_SPECIES = IS_DEMO ? 3 : 4;        // simultaneous wild critters each
  var SAVE_KEY = "critter-isles-" + CFG.mode + "-v1";

  // --------------------------------------------------------------- noise
  function makeNoise(seed) {
    var perm = [];
    var s = seed;
    for (var i = 0; i < 256; i++) perm[i] = i;
    for (i = 255; i > 0; i--) {
      s = (s * 16807) % 2147483647;
      var j = s % (i + 1);
      var t = perm[i]; perm[i] = perm[j]; perm[j] = t;
    }
    perm = perm.concat(perm);
    function fade(t) { return t * t * (3 - 2 * t); }
    function grad(h, x, y) {
      switch (h & 3) {
        case 0: return x + y;
        case 1: return -x + y;
        case 2: return x - y;
        default: return -x - y;
      }
    }
    return function (x, y) {
      var X = Math.floor(x) & 255, Y = Math.floor(y) & 255;
      x -= Math.floor(x); y -= Math.floor(y);
      var u = fade(x), v = fade(y);
      var a = perm[X] + Y, b = perm[X + 1] + Y;
      return (
        (1 - v) * ((1 - u) * grad(perm[a], x, y) + u * grad(perm[b], x - 1, y)) +
        v * ((1 - u) * grad(perm[a + 1], x, y - 1) + u * grad(perm[b + 1], x - 1, y - 1))
      );
    };
  }
  var noise = makeNoise(20260802);

  var WATER_Y = 0.0;
  function terrainHeight(x, z) {
    var n = 0, amp = 1, freq = 1 / 60, sum = 0;
    for (var o = 0; o < 4; o++) {
      n += noise(x * freq + 100, z * freq + 100) * amp;
      sum += amp; amp *= 0.5; freq *= 2;
    }
    n /= sum;
    // island falloff: high center, ocean at the edges
    var d = Math.sqrt(x * x + z * z) / WORLD;
    var island = 1 - Math.pow(Math.min(d, 1), 2.2);
    var h = (n * 0.5 + 0.5) * 14 * island - 2.5;
    return h;
  }
  function isLand(x, z) { return terrainHeight(x, z) > WATER_Y + 0.5; }

  // ---------------------------------------------------------------- scene
  var scene = new THREE.Scene();
  scene.background = new THREE.Color(0x9fd8ef);
  scene.fog = new THREE.Fog(0x9fd8ef, WORLD * 0.5, WORLD * 1.6);

  var camera = new THREE.PerspectiveCamera(60, innerWidth / innerHeight, 0.1, 2000);
  var renderer = new THREE.WebGLRenderer({ antialias: true });
  renderer.setSize(innerWidth, innerHeight);
  renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
  renderer.shadowMap.enabled = true;
  renderer.shadowMap.type = THREE.PCFSoftShadowMap;
  document.getElementById("game").appendChild(renderer.domElement);

  scene.add(new THREE.HemisphereLight(0xeaf6ff, 0x8a9a6a, 0.9));
  var sun = new THREE.DirectionalLight(0xfff2d8, 0.9);
  sun.position.set(80, 120, 40);
  sun.castShadow = true;
  sun.shadow.mapSize.set(2048, 2048);
  sun.shadow.camera.left = -60; sun.shadow.camera.right = 60;
  sun.shadow.camera.top = 60; sun.shadow.camera.bottom = -60;
  sun.shadow.camera.far = 400;
  scene.add(sun);
  scene.add(sun.target);

  // --------------------------------------------------------------- terrain
  (function buildTerrain() {
    var seg = IS_DEMO ? 120 : 200;
    var geo = new THREE.PlaneGeometry(WORLD * 2.4, WORLD * 2.4, seg, seg);
    geo.rotateX(-Math.PI / 2);
    var pos = geo.attributes.position;
    var colors = new Float32Array(pos.count * 3);
    var sand = new THREE.Color(0xe8d8a0), grass = new THREE.Color(0x79b34c),
        dark = new THREE.Color(0x527a35), rock = new THREE.Color(0x9a938a),
        c = new THREE.Color();
    for (var i = 0; i < pos.count; i++) {
      var x = pos.getX(i), z = pos.getZ(i);
      var h = terrainHeight(x, z);
      pos.setY(i, h);
      if (h < WATER_Y + 0.7) c.copy(sand);
      else if (h < 6) c.copy(grass).lerp(dark, h / 8);
      else c.copy(rock);
      // subtle variation
      var v = noise(x * 0.3, z * 0.3) * 0.06;
      c.offsetHSL(0, 0, v);
      colors[i * 3] = c.r; colors[i * 3 + 1] = c.g; colors[i * 3 + 2] = c.b;
    }
    geo.setAttribute("color", new THREE.BufferAttribute(colors, 3));
    geo.computeVertexNormals();
    var mesh = new THREE.Mesh(geo, new THREE.MeshLambertMaterial({ vertexColors: true }));
    mesh.receiveShadow = true;
    scene.add(mesh);

    var water = new THREE.Mesh(
      new THREE.PlaneGeometry(WORLD * 6, WORLD * 6),
      new THREE.MeshLambertMaterial({ color: 0x3f8fbf, transparent: true, opacity: 0.75 })
    );
    water.rotation.x = -Math.PI / 2;
    water.position.y = WATER_Y;
    scene.add(water);
  })();

  // ------------------------------------------------------ trees & rocks
  function scatter(count, minH, maxH, build) {
    for (var i = 0; i < count; i++) {
      var x = (Math.random() * 2 - 1) * WORLD;
      var z = (Math.random() * 2 - 1) * WORLD;
      var h = terrainHeight(x, z);
      if (h < minH || h > maxH) continue;
      var obj = build();
      obj.position.set(x, h, z);
      obj.rotation.y = Math.random() * Math.PI * 2;
      var s = 0.7 + Math.random() * 0.7;
      obj.scale.setScalar(s);
      scene.add(obj);
    }
  }
  var trunkMat = new THREE.MeshLambertMaterial({ color: 0x8a6a4a });
  var leafMat = new THREE.MeshLambertMaterial({ color: 0x4e8a3a });
  var leafMat2 = new THREE.MeshLambertMaterial({ color: 0x67a24a });
  var rockMat = new THREE.MeshLambertMaterial({ color: 0x9a938a });
  function makeTree() {
    var g = new THREE.Group();
    var trunk = new THREE.Mesh(new THREE.CylinderGeometry(0.25, 0.35, 2.2, 6), trunkMat);
    trunk.position.y = 1.1; trunk.castShadow = true;
    var fol = new THREE.Mesh(new THREE.ConeGeometry(1.6, 3.2, 7), Math.random() < 0.5 ? leafMat : leafMat2);
    fol.position.y = 3.4; fol.castShadow = true;
    g.add(trunk, fol);
    return g;
  }
  function makeRock() {
    var r = new THREE.Mesh(new THREE.IcosahedronGeometry(0.9, 0), rockMat);
    r.position.y = 0.3; r.castShadow = true;
    var g = new THREE.Group(); g.add(r); return g;
  }
  function makeFlower() {
    var g = new THREE.Group();
    var stem = new THREE.Mesh(new THREE.CylinderGeometry(0.03, 0.03, 0.5, 4),
      new THREE.MeshLambertMaterial({ color: 0x4e8a3a }));
    stem.position.y = 0.25;
    var head = new THREE.Mesh(new THREE.SphereGeometry(0.14, 6, 5),
      new THREE.MeshLambertMaterial({ color: [0xffffff, 0xffd0e0, 0xffe27a][Math.floor(Math.random() * 3)] }));
    head.position.y = 0.55;
    g.add(stem, head);
    return g;
  }
  scatter(IS_DEMO ? 160 : 550, 1.2, 7, makeTree);
  scatter(IS_DEMO ? 50 : 160, 0.8, 12, makeRock);
  scatter(IS_DEMO ? 80 : 260, 1.0, 5, makeFlower);

  // --------------------------------------------------------------- player
  var player = new THREE.Group();
  (function buildPlayer() {
    var mat = new THREE.MeshLambertMaterial({ color: 0xd85a4a });
    var skin = new THREE.MeshLambertMaterial({ color: 0xf5c9a0 });
    var body = new THREE.Mesh(new THREE.CylinderGeometry(0.42, 0.5, 1.0, 10), mat);
    body.position.y = 0.9; body.castShadow = true;
    var head = new THREE.Mesh(new THREE.SphereGeometry(0.38, 12, 10), skin);
    head.position.y = 1.75; head.castShadow = true;
    var hat = new THREE.Mesh(new THREE.ConeGeometry(0.42, 0.5, 10),
      new THREE.MeshLambertMaterial({ color: 0x3a6ea8 }));
    hat.position.y = 2.1; hat.castShadow = true;
    player.add(body, head, hat);
  })();
  player.position.set(0, terrainHeight(0, 0), 6);
  scene.add(player);

  // ------------------------------------------------------------ creatures
  function buildCreature(sp) {
    var g = new THREE.Group();
    var mat = new THREE.MeshLambertMaterial({ color: sp.color });
    var acc = new THREE.MeshLambertMaterial({ color: sp.accent });
    var body = new THREE.Mesh(new THREE.SphereGeometry(0.55, 12, 10), mat);
    body.position.y = 0.55; body.scale.set(1, 0.9, 1.15); body.castShadow = true;
    var head = new THREE.Mesh(new THREE.SphereGeometry(0.38, 12, 10), mat);
    head.position.set(0, 1.05, 0.35); head.castShadow = true;
    var eyeMat = new THREE.MeshBasicMaterial({ color: 0x222222 });
    var e1 = new THREE.Mesh(new THREE.SphereGeometry(0.06, 6, 5), eyeMat);
    var e2 = e1.clone();
    e1.position.set(0.15, 1.12, 0.66); e2.position.set(-0.15, 1.12, 0.66);
    g.add(body, head, e1, e2);
    // species flair
    if (sp.id === "flufftail" || sp.id === "zephyrix") {
      var ear1 = new THREE.Mesh(new THREE.ConeGeometry(0.1, 0.55, 6), mat);
      ear1.position.set(0.16, 1.5, 0.3);
      var ear2 = ear1.clone(); ear2.position.x = -0.16;
      var tail = new THREE.Mesh(new THREE.SphereGeometry(0.22, 8, 6), acc);
      tail.position.set(0, 0.6, -0.6);
      g.add(ear1, ear2, tail);
    }
    if (sp.id === "emberling") {
      var flame = new THREE.Mesh(new THREE.ConeGeometry(0.18, 0.55, 7), acc);
      flame.position.set(0, 0.85, -0.62); flame.rotation.x = 0.7;
      g.add(flame);
    }
    if (sp.id === "aquaphin") {
      var fin = new THREE.Mesh(new THREE.ConeGeometry(0.22, 0.5, 4), acc);
      fin.position.set(0, 1.25, 0); fin.rotation.z = Math.PI;
      fin.rotation.x = -0.4;
      g.add(fin);
    }
    if (sp.id === "mossback" || sp.id === "pebblit") {
      var shell = new THREE.Mesh(new THREE.SphereGeometry(0.5, 10, 8), acc);
      shell.position.set(0, 0.85, -0.15); shell.scale.set(1, 0.6, 1);
      g.add(shell);
    }
    if (sp.id === "glimmerwing" || sp.id === "nocturnix") {
      var wingGeo = new THREE.ConeGeometry(0.3, 0.8, 4);
      var w1 = new THREE.Mesh(wingGeo, acc);
      w1.position.set(0.6, 0.95, -0.1); w1.rotation.z = 1.2;
      var w2 = new THREE.Mesh(wingGeo, acc);
      w2.position.set(-0.6, 0.95, -0.1); w2.rotation.z = -1.2;
      g.add(w1, w2);
    }
    g.scale.setScalar(sp.size);
    return g;
  }

  function randomLandPos(minCenter) {
    for (var tries = 0; tries < 200; tries++) {
      var x = (Math.random() * 2 - 1) * WORLD * 0.9;
      var z = (Math.random() * 2 - 1) * WORLD * 0.9;
      if (!isLand(x, z)) continue;
      if (minCenter && Math.sqrt(x * x + z * z) < minCenter) continue;
      return new THREE.Vector3(x, terrainHeight(x, z), z);
    }
    return new THREE.Vector3(0, terrainHeight(0, 0), 0);
  }

  var critters = [];
  function spawnCritter(sp) {
    var mesh = buildCreature(sp);
    var p = randomLandPos(15);
    mesh.position.copy(p);
    scene.add(mesh);
    critters.push({
      sp: sp, mesh: mesh, state: "wander",
      target: p.clone(), idle: Math.random() * 3, fleeT: 0, bob: Math.random() * 10
    });
  }
  SPECIES.forEach(function (sp) {
    for (var i = 0; i < PER_SPECIES; i++) spawnCritter(sp);
  });

  // ------------------------------------------------------------- pickups
  var pickups = [];
  var orbGeo = new THREE.SphereGeometry(0.35, 10, 8);
  var orbMat = new THREE.MeshLambertMaterial({ color: 0xffffff, emissive: 0x5588ff });
  function spawnPickup() {
    var m = new THREE.Mesh(orbGeo, orbMat);
    var p = randomLandPos(8);
    m.position.copy(p).y += 0.8;
    scene.add(m);
    pickups.push(m);
  }
  for (var i = 0; i < (IS_DEMO ? 14 : 34); i++) spawnPickup();

  // ----------------------------------------------------------------- save
  var save = { caught: {}, orbs: 10 };
  try {
    var raw = localStorage.getItem(SAVE_KEY);
    if (raw) save = JSON.parse(raw);
  } catch (e) { /* private mode etc. — play without persistence */ }
  function persist() {
    try { localStorage.setItem(SAVE_KEY, JSON.stringify(save)); } catch (e) {}
  }

  // ------------------------------------------------------------------ ui
  var ui = {
    orbs: document.getElementById("orbs"),
    caught: document.getElementById("caught"),
    prompt: document.getElementById("prompt"),
    toast: document.getElementById("toast"),
    dex: document.getElementById("dex"),
    dexGrid: document.getElementById("dex-grid"),
    win: document.getElementById("win")
  };
  function caughtCount() {
    return SPECIES.filter(function (s) { return save.caught[s.id]; }).length;
  }
  function refreshHud() {
    ui.orbs.textContent = save.orbs;
    ui.caught.textContent = caughtCount() + " / " + SPECIES.length;
  }
  var toastT = null;
  function toast(msg) {
    ui.toast.textContent = msg;
    ui.toast.classList.add("show");
    clearTimeout(toastT);
    toastT = setTimeout(function () { ui.toast.classList.remove("show"); }, 2600);
  }
  function refreshDex() {
    ui.dexGrid.innerHTML = "";
    SPECIES.forEach(function (sp) {
      var d = document.createElement("div");
      d.className = "dex-card" + (save.caught[sp.id] ? " got" : "");
      var sw = document.createElement("div");
      sw.className = "swatch";
      sw.style.background = save.caught[sp.id]
        ? "#" + sp.color.toString(16).padStart(6, "0") : "#555";
      var nm = document.createElement("div");
      nm.className = "nm";
      nm.textContent = save.caught[sp.id] ? sp.name : "???";
      var ht = document.createElement("div");
      ht.className = "ht";
      ht.textContent = save.caught[sp.id] ? "Caught " + save.caught[sp.id] + "×" : sp.hint;
      d.appendChild(sw); d.appendChild(nm); d.appendChild(ht);
      ui.dexGrid.appendChild(d);
    });
  }
  document.getElementById("dex-btn").addEventListener("click", function () {
    refreshDex();
    ui.dex.classList.toggle("open");
  });
  document.getElementById("dex-close").addEventListener("click", function () {
    ui.dex.classList.remove("open");
  });
  document.getElementById("win-close").addEventListener("click", function () {
    ui.win.classList.remove("open");
  });
  refreshHud();

  // --------------------------------------------------------------- input
  var keys = {};
  addEventListener("keydown", function (e) {
    keys[e.code] = true;
    if (e.code === "Space") { e.preventDefault(); tryThrow(); }
    if (e.code === "KeyC") { refreshDex(); ui.dex.classList.toggle("open"); }
  });
  addEventListener("keyup", function (e) { keys[e.code] = false; });

  // touch controls
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
  if (tThrow) tThrow.addEventListener("touchstart", function (e) { e.preventDefault(); tryThrow(); });
  if (tThrow) tThrow.addEventListener("mousedown", function (e) { e.preventDefault(); tryThrow(); });
  if ("ontouchstart" in window) document.getElementById("touch").style.display = "block";

  // ------------------------------------------------------------ throwing
  var activeThrow = null;   // {mesh, from, to, t, critter}
  var nearCritter = null;

  function tryThrow() {
    if (activeThrow || !nearCritter) return;
    if (save.orbs <= 0) { toast("Out of orbs! Grab the glowing orbs around the island."); return; }
    save.orbs--; refreshHud(); persist();
    var orb = new THREE.Mesh(orbGeo, orbMat.clone());
    orb.scale.setScalar(0.7);
    var from = player.position.clone(); from.y += 1.6;
    scene.add(orb);
    activeThrow = { mesh: orb, from: from, to: nearCritter, t: 0 };
  }

  function resolveThrow(th) {
    var cr = th.critter || th.to;
    scene.remove(th.mesh);
    var success = Math.random() < cr.sp.catchRate;
    if (success) {
      save.caught[cr.sp.id] = (save.caught[cr.sp.id] || 0) + 1;
      persist(); refreshHud();
      toast("You caught " + cr.sp.name + "!");
      poof(cr.mesh.position, cr.sp.color);
      scene.remove(cr.mesh);
      var idx = critters.indexOf(cr);
      if (idx >= 0) critters.splice(idx, 1);
      setTimeout(function () { spawnCritter(cr.sp); }, 12000);
      if (caughtCount() === SPECIES.length) {
        setTimeout(function () { ui.win.classList.add("open"); }, 900);
      }
    } else {
      toast(cr.sp.name + " broke free and ran!");
      cr.state = "flee"; cr.fleeT = 3;
    }
  }

  // particle poof
  var poofs = [];
  function poof(pos, color) {
    var g = new THREE.Group();
    var m = new THREE.MeshBasicMaterial({ color: color });
    for (var i = 0; i < 10; i++) {
      var p = new THREE.Mesh(new THREE.SphereGeometry(0.09, 5, 4), m);
      p.position.copy(pos); p.position.y += 0.8;
      p.userData.v = new THREE.Vector3(
        (Math.random() - 0.5) * 4, Math.random() * 4 + 1, (Math.random() - 0.5) * 4);
      g.add(p);
    }
    scene.add(g);
    poofs.push({ g: g, t: 0 });
  }

  // ---------------------------------------------------------- game loop
  var yaw = 0;
  var clock = new THREE.Clock();
  var camPos = new THREE.Vector3();

  function animate() {
    requestAnimationFrame(animate);
    var dt = Math.min(clock.getDelta(), 0.05);
    var t = clock.elapsedTime;

    // --- player movement
    var turn = (keys.KeyA || keys.ArrowLeft ? 1 : 0) - (keys.KeyD || keys.ArrowRight ? 1 : 0);
    var move = (keys.KeyW || keys.ArrowUp ? 1 : 0) - (keys.KeyS || keys.ArrowDown ? 1 : 0);
    yaw += turn * dt * 2.4;
    player.rotation.y = yaw;
    if (move !== 0) {
      var speed = 9 * move;
      var nx = player.position.x + Math.sin(yaw) * speed * dt;
      var nz = player.position.z + Math.cos(yaw) * speed * dt;
      nx = Math.max(-WORLD, Math.min(WORLD, nx));
      nz = Math.max(-WORLD, Math.min(WORLD, nz));
      var nh = terrainHeight(nx, nz);
      if (nh > WATER_Y + 0.15) {          // can't swim
        player.position.x = nx; player.position.z = nz; player.position.y = nh;
      }
      player.position.y += Math.abs(Math.sin(t * 10)) * 0.06; // step bob
    }

    // --- camera follow
    camPos.set(
      player.position.x - Math.sin(yaw) * 10,
      player.position.y + 6.5,
      player.position.z - Math.cos(yaw) * 10
    );
    camera.position.lerp(camPos, 1 - Math.pow(0.001, dt));
    camera.lookAt(player.position.x, player.position.y + 2, player.position.z);
    sun.position.set(player.position.x + 60, 120, player.position.z + 30);
    sun.target.position.copy(player.position);

    // --- critters
    nearCritter = null;
    var nearDist = 7;
    critters.forEach(function (cr) {
      var m = cr.mesh;
      cr.bob += dt * 6;
      var d = m.position.distanceTo(player.position);
      if (d < nearDist && (!nearCritter || d < nearCritter._d)) {
        cr._d = d; nearCritter = cr;
      }
      if (cr.state === "flee") {
        cr.fleeT -= dt;
        var away = m.position.clone().sub(player.position).setY(0).normalize();
        moveCritter(cr, away, cr.sp.speed * 2.4, dt);
        if (cr.fleeT <= 0) cr.state = "wander";
      } else {
        if (d < 4.5) { cr.state = "flee"; cr.fleeT = 1.2; }
        cr.idle -= dt;
        if (cr.idle <= 0) {
          var a = Math.random() * Math.PI * 2, r = 8 + Math.random() * 16;
          var tx = m.position.x + Math.cos(a) * r, tz = m.position.z + Math.sin(a) * r;
          if (isLand(tx, tz)) cr.target.set(tx, 0, tz);
          cr.idle = 2 + Math.random() * 4;
        }
        var dir = cr.target.clone().sub(m.position).setY(0);
        if (dir.length() > 0.8) moveCritter(cr, dir.normalize(), cr.sp.speed, dt);
      }
      m.position.y = terrainHeight(m.position.x, m.position.z) + Math.abs(Math.sin(cr.bob)) * 0.12;
    });
    ui.prompt.style.display = nearCritter && !activeThrow ? "block" : "none";
    if (nearCritter) {
      ui.prompt.textContent = "Wild " + nearCritter.sp.name + "! SPACE / 🎯 to throw an orb";
    }

    // --- active throw
    if (activeThrow) {
      activeThrow.t += dt * 1.8;
      var th = activeThrow;
      var cr2 = th.to;
      if (th.t >= 1) {
        th.critter = cr2;
        activeThrow = null;
        resolveThrow(th);
      } else {
        var tp = cr2.mesh.position.clone(); tp.y += 0.8;
        th.mesh.position.lerpVectors(th.from, tp, th.t);
        th.mesh.position.y += Math.sin(th.t * Math.PI) * 3;
      }
    }

    // --- pickups
    for (var pi = pickups.length - 1; pi >= 0; pi--) {
      var pk = pickups[pi];
      pk.rotation.y += dt * 2;
      pk.position.y += Math.sin(t * 3 + pi) * 0.003;
      if (pk.position.distanceTo(player.position) < 2.2) {
        scene.remove(pk); pickups.splice(pi, 1);
        save.orbs += 3; refreshHud(); persist();
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

  function moveCritter(cr, dir, speed, dt) {
    var nx = cr.mesh.position.x + dir.x * speed * dt;
    var nz = cr.mesh.position.z + dir.z * speed * dt;
    if (isLand(nx, nz) && Math.abs(nx) < WORLD && Math.abs(nz) < WORLD) {
      cr.mesh.position.x = nx; cr.mesh.position.z = nz;
      cr.mesh.rotation.y = Math.atan2(dir.x, dir.z);
    }
  }

  addEventListener("resize", function () {
    camera.aspect = innerWidth / innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(innerWidth, innerHeight);
  });

  // demo banner
  if (IS_DEMO && CFG.buyLink) {
    var b = document.getElementById("demo-banner");
    if (b) {
      b.style.display = "flex";
      document.getElementById("buy-full").href = CFG.buyLink;
    }
  }

  animate();
})();
