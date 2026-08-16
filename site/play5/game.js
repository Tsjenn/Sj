/* ==========================================================================
   SKYLINE — a momentum swinging game.
   A lantern-spirit courier swings on ropes of light through a dusk city
   floating above the fog. Pendulum physics, flow chaining, timed deliveries,
   and asynchronous worldwide ghost racing through Flight Codes.
   ========================================================================== */
(function () {
  "use strict";

  var CFG = window.GAME_CONFIG || { mode: "full", buyLink: "" };
  var IS_DEMO = CFG.mode === "demo";
  var $ = function (id) { return document.getElementById(id); };
  var clamp = function (v, a, b) { return v < a ? a : v > b ? b : v; };
  var lerp = function (a, b, k) { return a + (b - a) * k; };
  var TAU = Math.PI * 2;

  function fmtT(s) {
    if (s == null || !isFinite(s)) return "—";
    var m = Math.floor(s / 60), r = s - m * 60;
    return m + ":" + (r < 10 ? "0" : "") + r.toFixed(1);
  }

  // ------------------------------------------------------------------ save
  var save;
  try { save = JSON.parse(localStorage.getItem("skyline") || "null"); } catch (e) { save = null; }
  if (!save) save = { best: {}, medals: {}, ghosts: [], helpSeen: false, muted: false, name: "COURIER" };
  function persist() { try { localStorage.setItem("skyline", JSON.stringify(save)); } catch (e) {} }

  // ----------------------------------------------------------------- audio
  var AudioSys = (function () {
    var ctx = null, master = null, wind = null, windGain = null, muted = save.muted, musicTimer = null;
    function ensure() {
      if (!ctx) {
        ctx = new (window.AudioContext || window.webkitAudioContext)();
        master = ctx.createGain(); master.gain.value = muted ? 0 : 0.5;
        master.connect(ctx.destination);
        var n = ctx.sampleRate * 2, buf = ctx.createBuffer(1, n, ctx.sampleRate), d = buf.getChannelData(0);
        var last = 0;
        for (var i = 0; i < n; i++) { var w = Math.random() * 2 - 1; last = (last + 0.03 * w) / 1.03; d[i] = last * 3; }
        wind = ctx.createBufferSource(); wind.buffer = buf; wind.loop = true;
        var lp = ctx.createBiquadFilter(); lp.type = "lowpass"; lp.frequency.value = 500;
        windGain = ctx.createGain(); windGain.gain.value = 0;
        wind.connect(lp); lp.connect(windGain); windGain.connect(master);
        wind.start();
        music();
      }
      if (ctx.state === "suspended") ctx.resume();
    }
    function tone(f, dur, type, vol, slide) {
      if (!ctx || muted) return;
      var o = ctx.createOscillator(), g = ctx.createGain();
      o.type = type || "sine"; o.frequency.setValueAtTime(f, ctx.currentTime);
      if (slide) o.frequency.exponentialRampToValueAtTime(slide, ctx.currentTime + dur);
      g.gain.setValueAtTime(vol || 0.15, ctx.currentTime);
      g.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + dur);
      o.connect(g); g.connect(master); o.start(); o.stop(ctx.currentTime + dur + 0.02);
    }
    var PENTA = [0, 3, 5, 7, 10];
    function music() {
      if (musicTimer) clearInterval(musicTimer);
      var step = 0;
      musicTimer = setInterval(function () {
        if (!ctx || muted) return;
        var root = 110 * Math.pow(2, (step % 64 < 32 ? 0 : -2) / 12);
        if (step % 2 === 0) tone(root * Math.pow(2, PENTA[(step / 2) % 5] / 12) * 2, 0.9, "sine", 0.035);
        if (step % 8 === 0) tone(root, 1.6, "triangle", 0.05);
        step++;
      }, 640);
    }
    return {
      ensure: ensure,
      wind: function (speedRatio) {
        if (windGain && ctx) windGain.gain.setTargetAtTime(muted ? 0 : speedRatio * 0.22, ctx.currentTime, 0.15);
      },
      attach: function () { tone(660, 0.1, "sine", 0.14, 990); },
      release: function () { tone(440, 0.16, "sine", 0.1, 330); },
      ring: function (i) { tone(523 * Math.pow(2, (i % 5) / 12), 0.3, "triangle", 0.2); },
      goal: function () { [523, 659, 784, 1047].forEach(function (f, i) { setTimeout(function () { tone(f, 0.4, "triangle", 0.18); }, i * 110); }); },
      fall: function () { tone(220, 0.5, "sawtooth", 0.12, 60); },
      flow: function () { tone(880, 0.25, "sine", 0.12, 1320); },
      toggleMute: function () { muted = !muted; save.muted = muted; persist(); if (master) master.gain.value = muted ? 0 : 0.5; return muted; }
    };
  })();

  // -------------------------------------------------------- renderer/scene
  var renderer = new THREE.WebGLRenderer({ antialias: true, powerPreference: "high-performance" });
  renderer.setPixelRatio(Math.min(devicePixelRatio || 1, 2));
  renderer.setSize(innerWidth, innerHeight);
  renderer.domElement.className = "gl";
  renderer.domElement.style.cssText = "position:fixed;inset:0;z-index:1";
  document.body.appendChild(renderer.domElement);

  var scene = new THREE.Scene();
  scene.fog = new THREE.FogExp2(0x3A2450, 0.0042);
  var camera = new THREE.PerspectiveCamera(70, innerWidth / innerHeight, 0.5, 3000);

  scene.add(new THREE.AmbientLight(0x8A6BAF, 1.0));
  var sun = new THREE.DirectionalLight(0xFFB37A, 1.25);
  sun.position.set(-0.7, 0.5, -0.4);
  scene.add(sun);
  var fill = new THREE.DirectionalLight(0x5A7ACF, 0.5);
  fill.position.set(0.6, 0.3, 0.7);
  scene.add(fill);

  // gradient dusk sky
  var skyGeo = new THREE.SphereGeometry(2400, 24, 16);
  (function () {
    var pos = skyGeo.attributes.position, n = pos.count;
    var colors = new Float32Array(n * 3);
    var top = new THREE.Color(0x241A48), mid = new THREE.Color(0x7A3B5E), low = new THREE.Color(0xE08A5A);
    for (var i = 0; i < n; i++) {
      var y = pos.getY(i) / 2400, c = new THREE.Color();
      if (y > 0.15) c.copy(mid).lerp(top, clamp((y - 0.15) / 0.7, 0, 1));
      else c.copy(low).lerp(mid, clamp((y + 0.25) / 0.4, 0, 1));
      colors[i * 3] = c.r; colors[i * 3 + 1] = c.g; colors[i * 3 + 2] = c.b;
    }
    skyGeo.setAttribute("color", new THREE.BufferAttribute(colors, 3));
  })();
  var skyMesh = new THREE.Mesh(skyGeo, new THREE.MeshBasicMaterial({ side: THREE.BackSide, vertexColors: true, fog: false }));
  scene.add(skyMesh);

  // low sun disc + glow sprite
  (function () {
    var glowC = document.createElement("canvas"); glowC.width = glowC.height = 128;
    var g = glowC.getContext("2d");
    var grd = g.createRadialGradient(64, 64, 4, 64, 64, 64);
    grd.addColorStop(0, "rgba(255,214,150,1)"); grd.addColorStop(0.3, "rgba(255,160,100,.55)");
    grd.addColorStop(1, "rgba(255,140,90,0)");
    g.fillStyle = grd; g.fillRect(0, 0, 128, 128);
    var spr = new THREE.Sprite(new THREE.SpriteMaterial({
      map: new THREE.CanvasTexture(glowC), transparent: true, fog: false,
      blending: THREE.AdditiveBlending, depthWrite: false }));
    spr.scale.setScalar(900);
    spr.position.set(-1400, 160, -800);
    scene.add(spr);
  })();

  // fog sea below
  (function () {
    var m = new THREE.Mesh(new THREE.PlaneGeometry(6000, 6000),
      new THREE.MeshBasicMaterial({ color: 0x4A2E5E, transparent: true, opacity: 0.96 }));
    m.rotation.x = -Math.PI / 2; m.position.y = -6;
    scene.add(m);
    var m2 = new THREE.Mesh(new THREE.PlaneGeometry(6000, 6000),
      new THREE.MeshBasicMaterial({ color: 0x5E3A6E, transparent: true, opacity: 0.55 }));
    m2.rotation.x = -Math.PI / 2; m2.position.y = 6;
    scene.add(m2);
  })();

  // window texture
  function windowTexture(warmth) {
    var c = document.createElement("canvas"); c.width = 64; c.height = 128;
    var x = c.getContext("2d");
    x.fillStyle = "#191428"; x.fillRect(0, 0, 64, 128);
    for (var yy = 3; yy < 125; yy += 7) {
      for (var xx = 3; xx < 61; xx += 7) {
        if (Math.random() < 0.5) {
          var warm = Math.random() < warmth;
          x.fillStyle = warm ? "rgba(255,196,120," + (0.5 + Math.random() * 0.5) + ")"
                             : "rgba(150,190,255," + (0.25 + Math.random() * 0.4) + ")";
          x.fillRect(xx, yy, 4, 4);
        }
      }
    }
    var t = new THREE.CanvasTexture(c);
    t.wrapS = t.wrapT = THREE.RepeatWrapping;
    return t;
  }

  /* ================================================================ CITY */
  var WORLD = 600;
  var towers = [];          // {x,z,hw,hd,top} axis-aligned boxes for collision
  var anchors = [];         // Vector3 anchor points (tower tops + sky hooks)
  var cityGroup = new THREE.Group();
  scene.add(cityGroup);

  function seededRand(seed) {
    var s = seed;
    return function () { s = (s * 1103515245 + 12345) % 2147483648; return s / 2147483648; };
  }

  function buildCity() {
    var rnd = seededRand(77);
    var rnd2 = seededRand(913);  // decoration-only stream — keeps the main
                                 // sequence (tower layout, medal-time world) intact
    var texA = windowTexture(0.7), texB = windowTexture(0.35);
    var geo = new THREE.BoxGeometry(1, 1, 1);
    var bodyCols = [0x9A8AB8, 0x7A6E9E, 0xB89A96];
    var capMat = new THREE.MeshBasicMaterial({ color: 0xFFC46B });
    var capMat2 = new THREE.MeshBasicMaterial({ color: 0x59E0C8 });
    var neonMats = [0xFF5FA2, 0x59E0C8, 0xFFC46B].map(function (c) {
      return new THREE.MeshBasicMaterial({ color: c });
    });

    for (var gx = -6; gx <= 6; gx++) {
      for (var gz = -6; gz <= 6; gz++) {
        if (rnd() < 0.28) continue;                          // plazas / gaps
        var x = gx * 46 + (rnd() - 0.5) * 22;
        var z = gz * 46 + (rnd() - 0.5) * 22;
        var d2 = x * x + z * z;
        if (d2 > WORLD * WORLD) continue;
        var h = 34 + rnd() * 96 * (1 - Math.sqrt(d2) / (WORLD * 1.4));
        var w = 14 + rnd() * 16, dep = 14 + rnd() * 16;
        // window texture tiled to the tower's real proportions, so lit
        // windows stay window-sized on every building instead of
        // stretching into blurry blocks on tall towers
        var tex = (rnd2() < 0.6 ? texA : texB).clone();
        tex.repeat.set(Math.max(1, Math.round(w / 9)), Math.max(1, Math.round(h / 13)));
        tex.needsUpdate = true;
        var b = new THREE.Mesh(geo, new THREE.MeshLambertMaterial({
          map: tex, color: bodyCols[Math.floor(rnd() * bodyCols.length)] }));
        b.scale.set(w, h, dep);
        b.position.set(x, h / 2, z);
        cityGroup.add(b);
        towers.push({ x: x, z: z, hw: w / 2, hd: dep / 2, top: h });
        // neon edge strip on some towers — the dusk-city signage glow
        // (rnd2 only: must not disturb the layout-defining sequence)
        if (rnd2() < 0.4) {
          var strip = new THREE.Mesh(geo, neonMats[Math.floor(rnd2() * neonMats.length)]);
          var sx = rnd2() < 0.5 ? -1 : 1, sz = rnd2() < 0.5 ? -1 : 1;
          strip.scale.set(0.55, h * (0.55 + rnd2() * 0.35), 0.55);
          strip.position.set(x + sx * (w / 2 + 0.1), h * 0.48, z + sz * (dep / 2 + 0.1));
          cityGroup.add(strip);
        }
        // rooftop cap light + anchor
        if (rnd() < 0.75) {
          var cap = new THREE.Mesh(geo, rnd() < 0.5 ? capMat : capMat2);
          cap.scale.set(w * 0.45, 1.2, dep * 0.45);
          cap.position.set(x, h + 0.7, z);
          cityGroup.add(cap);
        }
        anchors.push(new THREE.Vector3(x, h + 2, z));
      }
    }
  }

  // glowing sky-hooks along likely flight paths
  var hookGroup = new THREE.Group();
  scene.add(hookGroup);
  function addSkyHook(x, y, z) {
    var m = new THREE.Mesh(new THREE.SphereGeometry(1.1, 10, 8),
      new THREE.MeshBasicMaterial({ color: 0xFFD9A0 }));
    m.position.set(x, y, z);
    hookGroup.add(m);
    var halo = new THREE.Sprite(haloMat);
    halo.scale.setScalar(9);
    halo.position.copy(m.position);
    hookGroup.add(halo);
    anchors.push(m.position.clone());
  }
  var haloC = document.createElement("canvas"); haloC.width = haloC.height = 64;
  (function () {
    var g = haloC.getContext("2d");
    var grd = g.createRadialGradient(32, 32, 2, 32, 32, 32);
    grd.addColorStop(0, "rgba(255,220,160,.9)"); grd.addColorStop(1, "rgba(255,196,107,0)");
    g.fillStyle = grd; g.fillRect(0, 0, 64, 64);
  })();
  var haloMat = new THREE.SpriteMaterial({ map: new THREE.CanvasTexture(haloC), transparent: true,
    blending: THREE.AdditiveBlending, depthWrite: false });

  /* ============================================================== COURSES */
  var COURSES = [
    { id: "lantern-run", district: "Lantern District", name: "First Delivery", icon: "🏮",
      demo: true, gold: 38, silver: 46, bronze: 60,
      pts: [[-180, 55, -60], [-120, 62, 10], [-40, 58, 60], [40, 66, 80], [120, 60, 30], [180, 70, -40]] },
    { id: "market-sweep", district: "Lantern District", name: "Market Sweep", icon: "🎐",
      demo: true, gold: 52, silver: 63, bronze: 82,
      pts: [[170, 52, 120], [80, 60, 160], [-20, 55, 120], [-110, 64, 150], [-190, 58, 60],
            [-150, 68, -40], [-60, 60, -90]] },
    { id: "high-wire", district: "Aurora Heights", name: "High Wire", icon: "🌌",
      gold: 46, silver: 56, bronze: 74,
      pts: [[-60, 88, -180], [20, 96, -120], [110, 92, -150], [170, 100, -70], [120, 108, 20], [30, 98, 60]] },
    { id: "thin-air", district: "Aurora Heights", name: "Thin Air", icon: "🪁",
      gold: 58, silver: 70, bronze: 92,
      pts: [[200, 90, -160], [140, 104, -60], [190, 96, 60], [110, 112, 140], [0, 100, 170],
            [-100, 110, 120], [-170, 96, 40]] },
    { id: "fog-line", district: "The Deep Fog", name: "The Fog Line", icon: "🌫️",
      gold: 50, silver: 62, bronze: 82,
      pts: [[-200, 34, 100], [-130, 28, 40], [-60, 32, -20], [20, 26, -70], [110, 32, -110], [190, 38, -60]] },
    { id: "last-light", district: "The Deep Fog", name: "The Last Light", icon: "🕯️",
      gold: 70, silver: 85, bronze: 110,
      pts: [[-190, 30, -140], [-90, 44, -170], [10, 30, -140], [90, 52, -80], [160, 34, 10],
            [90, 60, 100], [-20, 40, 150], [-130, 56, 110]] }
  ];

  var ringGroup = new THREE.Group();
  scene.add(ringGroup);
  var course = null, ringIdx = 0, ringMeshes = [];

  function loadCourse(c) {
    course = c;
    ringIdx = 0;
    while (ringMeshes.length) { ringGroup.remove(ringMeshes.pop()); }
    c.pts.forEach(function (p, i) {
      var last = i === c.pts.length - 1;
      var geo = last ? new THREE.SphereGeometry(3.4, 14, 12) : new THREE.TorusGeometry(6, 0.55, 10, 28);
      var mat = new THREE.MeshBasicMaterial({ color: last ? 0xFFC46B : 0x59E0C8, transparent: true, opacity: 0.9 });
      var m = new THREE.Mesh(geo, mat);
      m.position.set(p[0], p[1], p[2]);
      var halo = new THREE.Sprite(haloMat);
      halo.scale.setScalar(last ? 26 : 18);
      m.add(halo);
      ringGroup.add(m);
      ringMeshes.push(m);
    });
    updateRingStates();
  }
  function updateRingStates() {
    ringMeshes.forEach(function (m, i) {
      var active = i === ringIdx, passed = i < ringIdx;
      m.visible = !passed;
      m.material.opacity = active ? 0.95 : 0.3;
      m.scale.setScalar(active ? 1 : 0.75);
    });
  }

  /* ============================================================== PLAYER */
  var player = new THREE.Group();
  (function () {
    // lantern spirit: glowing core, hooded body, ribbon tail
    var core = new THREE.Mesh(new THREE.SphereGeometry(0.55, 14, 12),
      new THREE.MeshBasicMaterial({ color: 0xFFE2AE }));
    core.position.y = 0.7;
    player.add(core);
    var hood = new THREE.Mesh(new THREE.ConeGeometry(0.75, 1.7, 10),
      new THREE.MeshLambertMaterial({ color: 0x3A2E5E, emissive: 0x1A1230 }));
    hood.position.y = 0.4;
    player.add(hood);
    var glow = new THREE.Sprite(haloMat);
    glow.scale.setScalar(7);
    glow.position.y = 0.7;
    player.add(glow);
    player.userData.core = core;
  })();
  scene.add(player);

  var pos = new THREE.Vector3(-180, 80, -60);
  var vel = new THREE.Vector3();
  var roped = false, anchor = new THREE.Vector3(), ropeLen = 0;
  var flow = 0, flowFull = false, airTime = 0;
  var GRAV = -32, MAXV = 62;

  // rope visual
  var ropeGeo = new THREE.BufferGeometry();
  ropeGeo.setAttribute("position", new THREE.BufferAttribute(new Float32Array(6), 3));
  var ropeLine = new THREE.Line(ropeGeo, new THREE.LineBasicMaterial({ color: 0xFFD9A0, transparent: true, opacity: 0.95 }));
  ropeLine.visible = false;
  scene.add(ropeLine);

  // ribbon trail
  var TRAIL_N = 40, trailPts = [];
  var trailGeo = new THREE.BufferGeometry();
  trailGeo.setAttribute("position", new THREE.BufferAttribute(new Float32Array(TRAIL_N * 3), 3));
  var trail = new THREE.Line(trailGeo, new THREE.LineBasicMaterial({ color: 0xFFC46B, transparent: true, opacity: 0.55 }));
  scene.add(trail);

  /* ------------------------------------------------------- anchor picking */
  var camFwd = new THREE.Vector3(0, 0, -1);
  var aimDir = new THREE.Vector3();
  function currentAim() {
    /* A courier aims at the objective: during a run the rope reaches toward
       the next ring, so holding SPACE always swings you along the course.
       In free flight (or past the last ring) it follows the camera. */
    if (mode === "run" && course && course.pts[ringIdx]) {
      var p = course.pts[ringIdx];
      aimDir.set(p[0] - pos.x, p[1] + 10 - pos.y, p[2] - pos.z).normalize();
    } else {
      camera.getWorldDirection(camFwd);
      aimDir.copy(camFwd);
    }
    return aimDir;
  }
  function pickAnchor() {
    var aim = currentAim();
    var best = null, bestScore = -1;
    for (var pass = 0; pass < 2 && !best; pass++) {
      var minAlign = pass === 0 ? 0.2 : -0.3;            // strict, then lenient
      for (var i = 0; i < anchors.length; i++) {
        var a = anchors[i];
        var dx = a.x - pos.x, dy = a.y - pos.y, dz = a.z - pos.z;
        var d2 = dx * dx + dy * dy + dz * dz;
        if (d2 < 64 || d2 > 6400) continue;              // 8..80 range
        if (dy < 2) continue;                             // must be above us
        var d = Math.sqrt(d2);
        var align = (dx * aim.x + dy * aim.y + dz * aim.z) / d;
        if (align < minAlign) continue;
        var score = align * 2 + dy / d + (1 - d / 80) * 0.5;
        if (score > bestScore) { bestScore = score; best = a; }
      }
    }
    return best;
  }

  function tryAttach() {
    if (roped || !running()) return;
    var a = pickAnchor();
    if (!a) { hint("No anchor in reach — aim at a rooftop or a golden hook"); return; }
    roped = true;
    anchor.copy(a);
    ropeLen = Math.max(9, pos.distanceTo(a) * 0.92);
    // throw yourself into the swing: an impulse along the aim direction turns
    // "dangling" into "swinging" even from a standstill
    var aim = currentAim();
    var boost = clamp(26 - vel.length() * 0.4, 6, 26);
    vel.addScaledVector(aim, boost);
    ropeLine.visible = true;
    AudioSys.attach();
  }
  function release() {
    if (!roped) return;
    roped = false;
    ropeLine.visible = false;
    AudioSys.release();
  }

  /* ------------------------------------------------------------- physics */
  function stepPhysics(dt, steer, reel) {
    vel.y += GRAV * dt;

    // steering: gentle lateral force relative to your motion, stronger while
    // roped (pumping the swing)
    if (steer !== 0) {
      var fwd = (vel.x * vel.x + vel.z * vel.z > 9)
        ? new THREE.Vector3(vel.x, 0, vel.z).normalize()
        : new THREE.Vector3(camFwd.x, 0, camFwd.z).normalize();
      var right = new THREE.Vector3(fwd.z, 0, -fwd.x);
      vel.addScaledVector(right, -steer * (roped ? 26 : 15) * dt);
    }

    if (roped) {
      // the rope reels itself gently (arcade swing) — W reels hard for speed
      ropeLen = Math.max(8, ropeLen - (reel ? 16 : 4.5) * dt);
      // predict, then project onto rope sphere
      var next = pos.clone().addScaledVector(vel, dt);
      var toA = next.clone().sub(anchor);
      var d = toA.length();
      if (d > ropeLen) {
        toA.multiplyScalar(ropeLen / d);
        next.copy(anchor).add(toA);
        // remove outward radial velocity -> tangential swing
        var n = toA.normalize();
        var vr = vel.dot(n);
        if (vr > 0) vel.addScaledVector(n, -vr);
        // energy pump on the downswing keeps arcs lively
        if (vel.y < 0) vel.multiplyScalar(1 + 0.55 * dt);
      }
      pos.copy(next);
    } else {
      vel.multiplyScalar(Math.pow(0.995, dt * 60));      // light air drag
      pos.addScaledVector(vel, dt);
    }

    var sp = vel.length();
    if (sp > MAXV * (flowFull ? 1.15 : 1)) vel.multiplyScalar(MAXV * (flowFull ? 1.15 : 1) / sp);

    // tower collision: push out of the box, kill normal velocity
    for (var i = 0; i < towers.length; i++) {
      var t = towers[i];
      if (pos.y > t.top + 1.4) continue;
      var lx = pos.x - t.x, lz = pos.z - t.z;
      if (Math.abs(lx) < t.hw + 1 && Math.abs(lz) < t.hd + 1) {
        if (pos.y > t.top - 2.5) {                        // landed on roof
          pos.y = t.top + 1.4;
          if (vel.y < 0) vel.y = 0;
          vel.x *= 0.86; vel.z *= 0.86;
          if (airTime > 0.4) { flow = 0; setFlow(); }
          airTime = 0;
          continue;
        }
        var px = (t.hw + 1) - Math.abs(lx), pz = (t.hd + 1) - Math.abs(lz);
        if (px < pz) { pos.x = t.x + (lx > 0 ? 1 : -1) * (t.hw + 1); vel.x *= -0.25; }
        else { pos.z = t.z + (lz > 0 ? 1 : -1) * (t.hd + 1); vel.z *= -0.25; }
      }
    }

    // fog sea = respawn
    if (pos.y < 4) fellInFog();
  }

  function fellInFog() {
    AudioSys.fall();
    release();
    flow = 0; setFlow();
    if (mode === "run" && course) {
      runTime += 3;
      toast("🌫️ The fog took you — +3s");
      var p = course.pts[Math.max(0, ringIdx - 1)];
      pos.set(p[0], p[1] + 6, p[2]);
    } else {
      var a = anchors[Math.floor(Math.random() * anchors.length)] || new THREE.Vector3(0, 80, 0);
      pos.set(a.x, a.y + 10, a.z);
    }
    vel.set(0, 0, 0);
  }

  /* ------------------------------------------------------------- ghosts */
  // A ghost replays checkpoint splits along the course, easing between rings.
  var ghostMeshes = [];
  function spawnGhosts() {
    ghostMeshes.forEach(function (g) { scene.remove(g.mesh); });
    ghostMeshes = [];
    if (!course) return;
    var list = save.ghosts.filter(function (g) { return g.c === course.id; }).slice(0, 3);
    list.forEach(function (g) {
      var m = new THREE.Group();
      var core = new THREE.Mesh(new THREE.SphereGeometry(0.55, 10, 8),
        new THREE.MeshBasicMaterial({ color: 0xFFE9C4, transparent: true, opacity: 0.5 }));
      var glow = new THREE.Sprite(haloMat); glow.scale.setScalar(6);
      m.add(core); m.add(glow);
      scene.add(m);
      ghostMeshes.push({ mesh: m, data: g });
    });
  }
  function updateGhosts(t) {
    ghostMeshes.forEach(function (g) {
      var splits = g.data.s, pts = course.pts;
      var seg = 0;
      while (seg < splits.length - 1 && splits[seg + 1] / 1000 < t) seg++;
      var t0 = seg === 0 ? 0 : splits[seg] / 1000;
      var t1 = splits[Math.min(seg + 1, splits.length - 1)] / 1000;
      var frac = t1 > t0 ? clamp((t - t0) / (t1 - t0), 0, 1) : 1;
      // ease and add a swing-like dip between rings
      var e = frac * frac * (3 - 2 * frac);
      var i0 = Math.min(seg, pts.length - 1), i1 = Math.min(seg + 1, pts.length - 1);
      var x = lerp(pts[i0][0], pts[i1][0], e);
      var y = lerp(pts[i0][1], pts[i1][1], e) - Math.sin(frac * Math.PI) * 14;
      var z = lerp(pts[i0][2], pts[i1][2], e);
      g.mesh.position.set(x, y, z);
      g.mesh.visible = t < splits[splits.length - 1] / 1000 + 1;
    });
  }

  function myCode() {
    if (!course) return null;
    var b = save.best[course.id];
    if (!b) return null;
    return "FC1." + btoa(JSON.stringify({ n: save.name, c: course.id, t: b.ms, s: b.splits }));
  }
  function parseCode(str) {
    str = (str || "").trim();
    if (str.indexOf("FC1.") !== 0) return null;
    try {
      var d = JSON.parse(atob(str.slice(4)));
      if (!d.c || !d.s || !d.s.length || typeof d.t !== "number") return null;
      if (!COURSES.some(function (c) { return c.id === d.c; })) return null;
      return { n: String(d.n || "RIVAL").slice(0, 12), c: d.c, t: d.t, s: d.s.map(Number) };
    } catch (e) { return null; }
  }

  /* ------------------------------------------------------------ run state */
  var mode = "idle";     // idle | run | free
  var runTime = 0, splits = [], started = false;
  function running() { return mode === "run" || mode === "free"; }

  function startRun(c) {
    loadCourse(c);
    mode = "run";
    runTime = 0; splits = []; started = true;
    flow = 0; setFlow();
    var p = c.pts[0];
    pos.set(p[0], p[1] + 6, p[2]);
    vel.set(0, 0, 0);
    release();
    ringIdx = 1;                    // ring 0 is the start point itself
    updateRingStates();
    spawnGhosts();
    // face the course: snap the camera behind the player, looking at ring 1
    var r1 = c.pts[1];
    camFwd.set(r1[0] - pos.x, 0, r1[2] - pos.z).normalize();
    camera.position.set(pos.x - camFwd.x * 14, pos.y + 6, pos.z - camFwd.z * 14);
    camera.lookAt(r1[0], r1[1], r1[2]);
    $("hud").classList.add("on");
    $("menu").classList.remove("on");
    $("results").classList.remove("open");
    $("course-name").textContent = c.icon + " " + c.name;
    $("best").textContent = "BEST " + (save.best[c.id] ? fmtT(save.best[c.id].ms / 1000) : "—");
    big(c.name, 1100, "#FFC46B");
    hint("Hold SPACE to throw a rope · release on the upswing");
    AudioSys.ensure();
  }

  function startFree() {
    mode = "free";
    course = null;
    while (ringMeshes.length) { ringGroup.remove(ringMeshes.pop()); }
    ghostMeshes.forEach(function (g) { scene.remove(g.mesh); });
    ghostMeshes = [];
    pos.set(0, 100, 0); vel.set(0, 0, 0);
    $("hud").classList.add("on");
    $("menu").classList.remove("on");
    $("course-name").textContent = "🕊️ Free flight";
    $("course-prog").textContent = "no timer";
    $("timer").textContent = "—";
    big("FREE FLIGHT", 1000, "#59E0C8");
    AudioSys.ensure();
  }

  function checkRings(dt) {
    if (mode !== "run" || !course) return;
    runTime += dt;
    var p = course.pts[ringIdx];
    if (!p) return;
    var dx = pos.x - p[0], dy = pos.y - p[1], dz = pos.z - p[2];
    var r = ringIdx === course.pts.length - 1 ? 8 : 9.5;
    if (dx * dx + dy * dy + dz * dz < r * r) {
      splits.push(Math.round(runTime * 1000));
      if (ringIdx === course.pts.length - 1) { finishRun(); return; }
      AudioSys.ring(ringIdx);
      big(ringIdx + " / " + (course.pts.length - 1), 500, "#59E0C8");
      ringIdx++;
      updateRingStates();
    }
  }

  function finishRun() {
    AudioSys.goal();
    mode = "idle";
    var ms = Math.round(runTime * 1000);
    var c = course;
    var prev = save.best[c.id];
    var isPB = !prev || ms < prev.ms;
    if (isPB) { save.best[c.id] = { ms: ms, splits: splits.slice() }; }
    var t = ms / 1000;
    var medal = t <= c.gold ? "🥇" : t <= c.silver ? "🥈" : t <= c.bronze ? "🥉" : "🏮";
    var mKey = { "🥇": 3, "🥈": 2, "🥉": 1, "🏮": 0 }[medal];
    if (mKey > (save.medals[c.id] || 0)) save.medals[c.id] = mKey;
    persist();

    // did we beat any ghosts?
    var beaten = save.ghosts.filter(function (g) { return g.c === c.id && ms < g.t; }).length;

    $("r-medal").textContent = medal;
    $("r-time").textContent = fmtT(t);
    $("r-sub").textContent =
      (isPB ? "NEW BEST · " : "") +
      (medal === "🥇" ? "Gold — a perfect line" : medal === "🥈" ? "Silver — nearly flawless"
        : medal === "🥉" ? "Bronze — keep chaining" : "Delivered") +
      (beaten ? " · beat " + beaten + " rival ghost" + (beaten > 1 ? "s" : "") : "");
    var sp = $("r-splits");
    sp.innerHTML = "";
    splits.forEach(function (s, i) {
      var el = document.createElement("span");
      el.textContent = "R" + (i + 1) + " " + (s / 1000).toFixed(1);
      sp.appendChild(el);
    });
    big("DELIVERED", 1300, "#FFC46B");
    setTimeout(function () { $("results").classList.add("open"); }, 1000);
  }

  /* ----------------------------------------------------------------- UI */
  function big(txt, ms, color) {
    var el = $("bigtext");
    el.textContent = txt;
    el.style.color = color || "#fff";
    el.classList.add("show");
    clearTimeout(big._t);
    big._t = setTimeout(function () { el.classList.remove("show"); }, ms || 900);
  }
  function toast(msg) {
    var el = $("toast");
    el.textContent = msg; el.classList.add("show");
    clearTimeout(toast._t);
    toast._t = setTimeout(function () { el.classList.remove("show"); }, 2200);
  }
  function hint(msg) {
    var el = $("hint");
    el.textContent = msg; el.classList.add("show");
    clearTimeout(hint._t);
    hint._t = setTimeout(function () { el.classList.remove("show"); }, 3600);
  }
  function setFlow() {
    flowFull = flow >= 1;
    $("flow-fill").style.width = Math.round(clamp(flow, 0, 1) * 100) + "%";
    player.userData.core.material.color.setHex(flowFull ? 0xFFF6DC : 0xFFE2AE);
  }

  function renderMenu() {
    var list = $("course-list");
    list.innerHTML = "";
    var lastDistrict = "";
    COURSES.forEach(function (c) {
      var locked = IS_DEMO && !c.demo;
      if (c.district !== lastDistrict) {
        lastDistrict = c.district;
        var h = document.createElement("div");
        h.className = "district";
        h.textContent = c.district + (IS_DEMO && !c.demo ? " 🔒" : "");
        list.appendChild(h);
      }
      var d = document.createElement("div");
      d.className = "ccard" + (locked ? " lock" : "");
      var b = save.best[c.id];
      var medal = ["", "🥉", "🥈", "🥇"][save.medals[c.id] || 0] || "";
      d.innerHTML = '<div class="dot">' + c.icon + '</div><div><div class="nm">' + c.name +
        '</div><div class="mt mono">' + (b ? "PB " + fmtT(b.ms / 1000) : "not yet flown") +
        " · gold " + fmtT(c.gold) + '</div></div><div class="medal">' + medal + "</div>";
      d.addEventListener("click", function () {
        if (locked) { toast("🔒 Unlock all districts in the full game"); return; }
        startRun(c);
      });
      list.appendChild(d);
    });
  }

  /* --------------------------------------------------------------- input */
  var keys = {}, steerIn = 0;
  addEventListener("keydown", function (e) {
    if (["Space", "ArrowLeft", "ArrowRight", "ArrowUp", "ArrowDown"].indexOf(e.code) >= 0) e.preventDefault();
    if (e.code === "Space" && !keys.Space) tryAttach();
    keys[e.code] = true;
  });
  addEventListener("keyup", function (e) {
    if (e.code === "Space") release();
    keys[e.code] = false;
  });
  addEventListener("mousedown", function (e) {
    if (e.target.closest && (e.target.closest(".panel") || e.target.closest("#mpanel") ||
        e.target.closest("button") || e.target.closest("a"))) return;
    if (running()) tryAttach();
  });
  addEventListener("mouseup", function () { release(); });

  function bindHold(id, on, off) {
    var el = $(id);
    el.addEventListener("touchstart", function (e) { e.preventDefault(); on(); }, { passive: false });
    el.addEventListener("touchend", function (e) { e.preventDefault(); off(); });
  }
  bindHold("t-swing", tryAttach, release);
  bindHold("t-left", function () { keys.KeyA = true; }, function () { keys.KeyA = false; });
  bindHold("t-right", function () { keys.KeyD = true; }, function () { keys.KeyD = false; });
  if ("ontouchstart" in window) $("touch").style.display = "block";

  // buttons
  $("title-go").addEventListener("click", function (e) {
    e.stopPropagation();
    $("title").classList.remove("on");
    AudioSys.ensure();
    if (!save.helpSeen) $("help").classList.add("open");
    $("menu").classList.add("on");
    renderMenu();
  });
  $("title").addEventListener("click", function () { $("title-go").click(); });
  $("help-btn").addEventListener("click", function () { $("help").classList.add("open"); });
  $("help-close").addEventListener("click", function () {
    $("help").classList.remove("open"); save.helpSeen = true; persist();
  });
  $("mute-btn").addEventListener("click", function () {
    $("mute-btn").textContent = AudioSys.toggleMute() ? "🔇" : "🔊";
  });
  $("mute-btn").textContent = save.muted ? "🔇" : "🔊";
  $("menu-btn").addEventListener("click", function () {
    mode = "idle";
    $("hud").classList.remove("on");
    $("results").classList.remove("open");
    $("menu").classList.add("on");
    renderMenu();
  });
  $("free-btn").addEventListener("click", startFree);
  $("r-again").addEventListener("click", function () { $("results").classList.remove("open"); startRun(course); });
  $("r-menu").addEventListener("click", function () { $("menu-btn").click(); });
  $("r-code").addEventListener("click", function () {
    var code = myCode();
    if (code && navigator.clipboard) navigator.clipboard.writeText(code).catch(function () {});
    $("results").classList.remove("open");
    openCodes();
  });
  $("code-btn").addEventListener("click", openCodes);
  function openCodes() {
    $("my-code").value = myCode() || "Fly a course first — your best run becomes your code.";
    $("codes").classList.add("open");
  }
  $("codes-close").addEventListener("click", function () { $("codes").classList.remove("open"); });
  $("copy-code").addEventListener("click", function () {
    var ta = $("my-code");
    ta.select();
    try { document.execCommand("copy"); } catch (e) {}
    if (navigator.clipboard) navigator.clipboard.writeText(ta.value).catch(function () {});
    toast("Flight Code copied — send it to a rival!");
  });
  $("add-code").addEventListener("click", function () {
    var d = parseCode($("their-code").value);
    if (!d) { toast("That Flight Code doesn't look right."); return; }
    save.ghosts = save.ghosts.filter(function (g) { return !(g.c === d.c && g.n === d.n); });
    save.ghosts.push(d);
    if (save.ghosts.length > 12) save.ghosts.shift();
    persist();
    $("their-code").value = "";
    var cname = COURSES.filter(function (c) { return c.id === d.c; })[0].name;
    toast("👻 " + d.n + "'s ghost added on " + cname);
    if (course && course.id === d.c && mode === "run") spawnGhosts();
    $("codes").classList.remove("open");
  });

  if (IS_DEMO && CFG.buyLink) {
    $("demo-banner").style.display = "flex";
    $("buy-full").href = CFG.buyLink;
  }

  addEventListener("resize", function () {
    camera.aspect = innerWidth / innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(innerWidth, innerHeight);
  });

  /* ---------------------------------------------------------------- loop */
  buildCity();
  // sky hooks between course rings so every leg is swingable
  COURSES.forEach(function (c) {
    for (var i = 0; i < c.pts.length - 1; i++) {
      var a = c.pts[i], b = c.pts[i + 1];
      addSkyHook((a[0] + b[0]) / 2 + 6, Math.max(a[1], b[1]) + 26, (a[2] + b[2]) / 2 + 6);
    }
  });

  var camPos = new THREE.Vector3(0, 140, 260), camLook = new THREE.Vector3();
  camera.position.copy(camPos);
  var clock = new THREE.Clock();
  var hudAcc = 0;

  function animate() {
    requestAnimationFrame(animate);
    var dt = Math.min(clock.getDelta(), 0.04);
    var t = clock.elapsedTime;

    if (running()) {
      steerIn = (keys.KeyA || keys.ArrowLeft ? 1 : 0) - (keys.KeyD || keys.ArrowRight ? 1 : 0);
      stepPhysics(dt, steerIn, keys.KeyW || keys.ArrowUp);
      checkRings(dt);

      // flow: build while airborne & fast, decay on rooftops
      airTime += dt;
      var sp = vel.length();
      if (sp > 22 && airTime > 0.3) {
        var was = flowFull;
        flow = clamp(flow + dt * 0.14, 0, 1);
        if (!was && flow >= 1) { AudioSys.flow(); big("FLOW", 700, "#FFF6DC"); }
      }
      setFlow();

      if (mode === "run") updateGhosts(runTime);
    }

    // player visuals: face velocity, tilt into swing
    player.position.copy(pos);
    var sp2 = vel.length();
    if (sp2 > 2) {
      var yaw = Math.atan2(vel.x, vel.z);
      player.rotation.y = yaw;
      player.rotation.x = clamp(-vel.y / 60, -0.8, 0.8);
    }

    // rope line
    if (roped) {
      var rp = ropeGeo.attributes.position.array;
      rp[0] = pos.x; rp[1] = pos.y + 0.7; rp[2] = pos.z;
      rp[3] = anchor.x; rp[4] = anchor.y; rp[5] = anchor.z;
      ropeGeo.attributes.position.needsUpdate = true;
    }

    // trail
    trailPts.push(pos.clone());
    if (trailPts.length > TRAIL_N) trailPts.shift();
    var tp = trailGeo.attributes.position.array;
    for (var i = 0; i < TRAIL_N; i++) {
      var p = trailPts[Math.min(i, trailPts.length - 1)] || pos;
      tp[i * 3] = p.x; tp[i * 3 + 1] = p.y; tp[i * 3 + 2] = p.z;
    }
    trailGeo.attributes.position.needsUpdate = true;
    trail.material.opacity = clamp(sp2 / MAXV, 0, 1) * 0.6;

    // camera: chase velocity direction
    var ratio = clamp(sp2 / MAXV, 0, 1);
    if (running()) {
      var dir = sp2 > 4 ? vel.clone().normalize() : camFwd.clone();
      camPos.set(pos.x - dir.x * (11 + ratio * 5), pos.y + 4.5 - dir.y * 5, pos.z - dir.z * (11 + ratio * 5));
      camera.position.lerp(camPos, 1 - Math.pow(0.004, dt));
      camLook.set(pos.x + dir.x * 10, pos.y + dir.y * 6, pos.z + dir.z * 10);
      camera.lookAt(camLook);
      camera.fov = lerp(camera.fov, 66 + ratio * 16 + (flowFull ? 5 : 0), clamp(dt * 4, 0, 1));
      camera.updateProjectionMatrix();
    } else {
      // idle: slow drift over the city
      var a = t * 0.05;
      camera.position.set(Math.cos(a) * 280, 150 + Math.sin(t * 0.3) * 8, Math.sin(a) * 280);
      camera.lookAt(0, 60, 0);
      camera.fov = lerp(camera.fov, 62, clamp(dt * 2, 0, 1));
      camera.updateProjectionMatrix();
    }

    // ring pulse
    ringMeshes.forEach(function (m, i) {
      if (i === ringIdx) m.rotation.y += dt * 1.4;
      m.rotation.x = Math.sin(t * 1.2 + i) * 0.15;
    });

    AudioSys.wind(ratio);
    skyMesh.position.copy(camera.position);

    // HUD
    hudAcc += dt;
    if (hudAcc > 0.08 && running()) {
      hudAcc = 0;
      if (mode === "run") {
        $("timer").textContent = fmtT(runTime);
        $("course-prog").textContent = Math.max(0, ringIdx - 1) + " / " + (course.pts.length - 1) + " rings";
        var b = save.best[course.id];
        var d = $("delta");
        if (b && splits.length && b.splits[splits.length - 1] != null) {
          var diff = (splits[splits.length - 1] - b.splits[splits.length - 1]) / 1000;
          d.textContent = (diff >= 0 ? "+" : "−") + Math.abs(diff).toFixed(1);
          d.className = "mono show " + (diff > 0 ? "up" : "dn");
        } else d.className = "mono";
      }
      $("speed").innerHTML = Math.round(sp2 * 3.6) + " <small>KM/H</small>";
    }

    renderer.render(scene, camera);
  }
  animate();

  /* ------------------------------------------------------------- DEV API */
  window.DEV = {
    state: function () {
      return { mode: mode, pos: [Math.round(pos.x), Math.round(pos.y), Math.round(pos.z)],
        speed: Math.round(vel.length()), roped: roped, ring: ringIdx,
        time: +runTime.toFixed(1), flow: +flow.toFixed(2),
        anchors: anchors.length, ghosts: ghostMeshes.length, best: save.best };
    },
    go: function () { $("title-go").click(); },
    run: function (i) { startRun(COURSES[i || 0]); },
    free: startFree,
    key: function (code, down) {
      if (code === "Space") { if (down) tryAttach(); else release(); }
      keys[code] = !!down;
    },
    warp: function (x, y, z) { pos.set(x, y, z); vel.set(0, 0, 0); },
    push: function (x, y, z) { vel.set(x, y, z); },
    ringPos: function () { return course && course.pts[ringIdx]; },
    finish: function () {
      if (!course) return;
      // legitimate-looking completion for pipeline tests
      splits = course.pts.slice(1).map(function (_, i) { return (i + 1) * 7000; });
      runTime = splits[splits.length - 1] / 1000;
      finishRun();
    },
    code: myCode,
    addCode: function (c) { $("their-code").value = c; $("add-code").click(); },
    courses: function () { return COURSES.map(function (c) { return c.id; }); },
    reset: function () { localStorage.removeItem("skyline"); location.reload(); }
  };
})();
