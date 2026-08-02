/* ==========================================================================
   NEON DRIFT RACERS
   A neon-city arcade racer: drift-charge boosting, a driver you build whose
   face reacts to the race, AI rivals, and asynchronous worldwide competition
   through shareable Race Codes.
   ========================================================================== */
(function () {
  "use strict";

  var CFG = window.GAME_CONFIG || { mode: "full", buyLink: "" };
  var IS_DEMO = CFG.mode === "demo";
  var $ = function (id) { return document.getElementById(id); };
  var clamp = function (v, a, b) { return v < a ? a : v > b ? b : v; };
  var lerp = function (a, b, k) { return a + (b - a) * k; };
  var TAU = Math.PI * 2;

  function fmtTime(s) {
    if (s == null || !isFinite(s)) return "—";
    var m = Math.floor(s / 60);
    var r = s - m * 60;
    return m + ":" + (r < 10 ? "0" : "") + r.toFixed(3);
  }
  function fmtDelta(d) { return (d >= 0 ? "+" : "−") + Math.abs(d).toFixed(3); }

  // ------------------------------------------------------------------ save
  var DEFAULT_SAVE = {
    name: "RACER",
    ch: { face: 0, skin: 2, hair: 1, haircol: 0, gear: 1, suit: 0, trim: 1 },
    car: 0, paint: 0, track: 0,
    best: {}, lb: [], medals: {}, helpSeen: false, muted: false
  };
  var save;
  try {
    save = JSON.parse(localStorage.getItem("neondrift") || "null") || null;
  } catch (e) { save = null; }
  if (!save) save = JSON.parse(JSON.stringify(DEFAULT_SAVE));
  for (var k in DEFAULT_SAVE) if (!(k in save)) save[k] = DEFAULT_SAVE[k];
  for (var k2 in DEFAULT_SAVE.ch) if (!(k2 in save.ch)) save.ch[k2] = DEFAULT_SAVE.ch[k2];
  function persist() {
    try { localStorage.setItem("neondrift", JSON.stringify(save)); } catch (e) {}
  }

  // ----------------------------------------------------------------- audio
  var AudioSys = (function () {
    var ctx = null, master = null, engineOsc = null, engineOsc2 = null, engineGain = null,
        engineFilter = null, driftGain = null, driftSrc = null, muted = save.muted, musicTimer = null;
    function noiseBuffer() {
      var n = ctx.sampleRate * 2, b = ctx.createBuffer(1, n, ctx.sampleRate), d = b.getChannelData(0);
      for (var i = 0; i < n; i++) d[i] = Math.random() * 2 - 1;
      return b;
    }
    function start() {
      if (ctx) { if (ctx.state === "suspended") ctx.resume(); return; }
      try { ctx = new (window.AudioContext || window.webkitAudioContext)(); } catch (e) { return; }
      master = ctx.createGain();
      master.gain.value = muted ? 0 : 0.5;
      master.connect(ctx.destination);

      engineFilter = ctx.createBiquadFilter();
      engineFilter.type = "lowpass"; engineFilter.frequency.value = 900;
      engineGain = ctx.createGain(); engineGain.gain.value = 0;
      engineFilter.connect(engineGain); engineGain.connect(master);
      engineOsc = ctx.createOscillator(); engineOsc.type = "sawtooth"; engineOsc.frequency.value = 60;
      engineOsc2 = ctx.createOscillator(); engineOsc2.type = "square"; engineOsc2.frequency.value = 30;
      engineOsc.connect(engineFilter); engineOsc2.connect(engineFilter);
      engineOsc.start(); engineOsc2.start();

      driftSrc = ctx.createBufferSource();
      driftSrc.buffer = noiseBuffer(); driftSrc.loop = true;
      var bp = ctx.createBiquadFilter(); bp.type = "bandpass"; bp.frequency.value = 2600; bp.Q.value = 2.2;
      driftGain = ctx.createGain(); driftGain.gain.value = 0;
      driftSrc.connect(bp); bp.connect(driftGain); driftGain.connect(master);
      driftSrc.start();
      music();
    }
    function blip(freq, dur, type, vol, slideTo) {
      if (!ctx || muted) return;
      var o = ctx.createOscillator(), g = ctx.createGain();
      o.type = type || "square"; o.frequency.setValueAtTime(freq, ctx.currentTime);
      if (slideTo) o.frequency.exponentialRampToValueAtTime(slideTo, ctx.currentTime + dur);
      g.gain.setValueAtTime(vol || 0.18, ctx.currentTime);
      g.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + dur);
      o.connect(g); g.connect(master); o.start(); o.stop(ctx.currentTime + dur + 0.02);
    }
    function noiseHit(dur, freq, vol) {
      if (!ctx || muted) return;
      var s = ctx.createBufferSource(); s.buffer = noiseBuffer();
      var f = ctx.createBiquadFilter(); f.type = "lowpass"; f.frequency.value = freq || 1200;
      var g = ctx.createGain(); g.gain.setValueAtTime(vol || 0.3, ctx.currentTime);
      g.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + dur);
      s.connect(f); f.connect(g); g.connect(master); s.start(); s.stop(ctx.currentTime + dur);
    }
    var SCALE = [0, 3, 5, 7, 10, 12, 10, 7];
    function music() {
      if (musicTimer) clearInterval(musicTimer);
      var step = 0;
      musicTimer = setInterval(function () {
        if (!ctx || muted) return;
        var root = 55 * Math.pow(2, (step % 32 < 16 ? 0 : 3) / 12);
        var n = SCALE[step % SCALE.length];
        blip(root * Math.pow(2, n / 12) * 2, 0.16, "sawtooth", 0.045);
        if (step % 4 === 0) blip(root, 0.22, "triangle", 0.09);
        if (step % 2 === 1) noiseHit(0.05, 5000, 0.035);
        step++;
      }, 155);
    }
    return {
      start: start,
      engine: function (speedRatio, boosting) {
        if (!ctx || !engineGain) return;
        var f = 52 + speedRatio * 240 + (boosting ? 60 : 0);
        engineOsc.frequency.setTargetAtTime(f, ctx.currentTime, 0.05);
        engineOsc2.frequency.setTargetAtTime(f * 0.5, ctx.currentTime, 0.05);
        engineFilter.frequency.setTargetAtTime(500 + speedRatio * 2600, ctx.currentTime, 0.08);
        engineGain.gain.setTargetAtTime(muted ? 0 : 0.05 + speedRatio * 0.1, ctx.currentTime, 0.1);
      },
      drift: function (amount) {
        if (!ctx || !driftGain) return;
        driftGain.gain.setTargetAtTime(muted ? 0 : amount * 0.14, ctx.currentTime, 0.05);
      },
      boost: function () { blip(180, 0.5, "sawtooth", 0.24, 1400); noiseHit(0.4, 3000, 0.2); },
      crash: function () { noiseHit(0.3, 700, 0.4); blip(90, 0.2, "square", 0.16, 50); },
      beep: function (hi) { blip(hi ? 880 : 440, hi ? 0.35 : 0.16, "square", 0.22); },
      pass: function () { blip(660, 0.12, "triangle", 0.14, 990); },
      win: function () { [523, 659, 784, 1047].forEach(function (f, i) { setTimeout(function () { blip(f, 0.3, "triangle", 0.2); }, i * 110); }); },
      lap: function () { blip(784, 0.14, "triangle", 0.18); setTimeout(function () { blip(1047, 0.2, "triangle", 0.18); }, 120); },
      toggleMute: function () {
        muted = !muted; save.muted = muted; persist();
        if (master) master.gain.value = muted ? 0 : 0.5;
        return muted;
      }
    };
  })();

  // ------------------------------------------------------------- character
  var SKINS = ["#F7D9BE", "#EBC08F", "#D69A66", "#A9663B", "#6E4326", "#F2C9C9"];
  var HAIRCOLS = ["#1B1B22", "#5B3A22", "#C9973F", "#E8E6E3", "#FF2FA8", "#12F2E4", "#8B5CF6"];
  var SUITS = ["#12F2E4", "#FF2FA8", "#8B5CF6", "#FFB020", "#39D353", "#F04438", "#EDEDF2", "#1E2A5A"];
  var HAIRS = ["Buzz", "Swept", "Bun", "Curls", "Long", "Mohawk"];
  var GEARS = ["None", "Helmet", "Visor", "Cap", "Goggles"];
  var FACES = ["Round", "Sharp", "Soft", "Bold"];

  /* Draws the driver's face onto a canvas. Expression is re-rendered live
     during the race, so the driver visibly reacts to what you're doing. */
  function drawFace(ctx, ch, expr, W, H) {
    var skin = SKINS[ch.skin % SKINS.length];
    var hairCol = HAIRCOLS[ch.haircol % HAIRCOLS.length];
    var face = ch.face % FACES.length;
    ctx.clearRect(0, 0, W, H);
    ctx.fillStyle = skin;
    ctx.fillRect(0, 0, W, H);

    var cx = W * 0.5, cy = H * 0.53, u = W / 512;

    // jaw shading gives each face shape a distinct silhouette
    ctx.fillStyle = "rgba(0,0,0,.06)";
    if (face === 1) { ctx.beginPath(); ctx.moveTo(cx - 120 * u, cy + 60 * u); ctx.lineTo(cx + 120 * u, cy + 60 * u); ctx.lineTo(cx, cy + 150 * u); ctx.fill(); }
    if (face === 2) { ctx.beginPath(); ctx.ellipse(cx, cy + 78 * u, 118 * u, 62 * u, 0, 0, TAU); ctx.fill(); }
    if (face === 3) { ctx.fillRect(cx - 128 * u, cy + 66 * u, 256 * u, 60 * u); }

    // hair
    ctx.fillStyle = hairCol;
    var hs = ch.hair % HAIRS.length;
    if (hs === 0) { ctx.fillRect(0, 0, W, H * 0.27); }
    else if (hs === 1) {
      ctx.fillRect(0, 0, W, H * 0.29);
      ctx.beginPath(); ctx.moveTo(cx - 150 * u, H * 0.29); ctx.quadraticCurveTo(cx + 40 * u, H * 0.20, cx + 160 * u, H * 0.36); ctx.lineTo(cx + 160 * u, H * 0.29); ctx.fill();
    } else if (hs === 2) {
      ctx.fillRect(0, 0, W, H * 0.26);
      ctx.beginPath(); ctx.ellipse(cx, H * 0.10, 66 * u, 52 * u, 0, 0, TAU); ctx.fill();
    } else if (hs === 3) {
      ctx.fillRect(0, 0, W, H * 0.24);
      for (var i = 0; i < 9; i++) {
        ctx.beginPath();
        ctx.ellipse(W * (0.06 + i * 0.11), H * (0.25 + (i % 2) * 0.035), 40 * u, 32 * u, 0, 0, TAU); ctx.fill();
      }
    } else if (hs === 4) {
      ctx.fillRect(0, 0, W, H * 0.31);
      ctx.fillRect(0, 0, W * 0.14, H * 0.72); ctx.fillRect(W * 0.86, 0, W * 0.14, H * 0.72);
    } else {
      ctx.fillRect(0, 0, W, H * 0.20);
      ctx.fillRect(cx - 42 * u, 0, 84 * u, H * 0.33);
    }
    // hair sheen
    ctx.fillStyle = "rgba(255,255,255,.16)";
    ctx.fillRect(0, H * 0.045, W, H * 0.022);

    // ---- expression tables
    var browY = cy - 62 * u, eyeY = cy - 8 * u, eyeDX = 74 * u;
    var browTilt = 0, eyeMode = "open", mouthMode = "flat";
    if (expr === "focus") { browTilt = -0.16; eyeMode = "open"; mouthMode = "flat"; }
    else if (expr === "determined") { browTilt = -0.42; eyeMode = "narrow"; mouthMode = "grit"; }
    else if (expr === "grin") { browTilt = 0.12; eyeMode = "happy"; mouthMode = "grin"; }
    else if (expr === "wince") { browTilt = 0.55; eyeMode = "shut"; mouthMode = "ohno"; }
    else if (expr === "shock") { browTilt = 0.4; eyeMode = "wide"; mouthMode = "o"; }
    else if (expr === "cheer") { browTilt = 0.2; eyeMode = "happy"; mouthMode = "cheer"; }
    else if (expr === "sad") { browTilt = 0.5; eyeMode = "open"; mouthMode = "frown"; }

    // brows
    ctx.strokeStyle = hairCol; ctx.lineWidth = 11 * u; ctx.lineCap = "round";
    [-1, 1].forEach(function (s) {
      ctx.save(); ctx.translate(cx + s * eyeDX, browY); ctx.rotate(s * browTilt);
      ctx.beginPath(); ctx.moveTo(-30 * u, 0); ctx.lineTo(30 * u, -6 * u); ctx.stroke(); ctx.restore();
    });

    // eyes
    ctx.fillStyle = "#15151F";
    [-1, 1].forEach(function (s) {
      var ex = cx + s * eyeDX;
      if (eyeMode === "shut") {
        ctx.strokeStyle = "#15151F"; ctx.lineWidth = 9 * u;
        ctx.beginPath(); ctx.moveTo(ex - 26 * u, eyeY); ctx.quadraticCurveTo(ex, eyeY + 16 * u, ex + 26 * u, eyeY); ctx.stroke();
      } else if (eyeMode === "happy") {
        ctx.strokeStyle = "#15151F"; ctx.lineWidth = 10 * u;
        ctx.beginPath(); ctx.moveTo(ex - 26 * u, eyeY + 8 * u); ctx.quadraticCurveTo(ex, eyeY - 20 * u, ex + 26 * u, eyeY + 8 * u); ctx.stroke();
      } else {
        var rw = eyeMode === "wide" ? 30 : eyeMode === "narrow" ? 26 : 27;
        var rh = eyeMode === "wide" ? 32 : eyeMode === "narrow" ? 13 : 25;
        ctx.fillStyle = "#FFFFFF";
        ctx.beginPath(); ctx.ellipse(ex, eyeY, rw * u, rh * u, 0, 0, TAU); ctx.fill();
        ctx.fillStyle = "#15151F";
        ctx.beginPath(); ctx.ellipse(ex + s * 3 * u, eyeY + 2 * u, 13 * u, Math.min(rh, 15) * u, 0, 0, TAU); ctx.fill();
        ctx.fillStyle = "rgba(255,255,255,.9)";
        ctx.beginPath(); ctx.ellipse(ex + s * 7 * u, eyeY - 6 * u, 5 * u, 5 * u, 0, 0, TAU); ctx.fill();
      }
    });

    // mouth
    var my = cy + 72 * u;
    ctx.strokeStyle = "#7A3B3B"; ctx.lineWidth = 10 * u; ctx.lineCap = "round";
    ctx.fillStyle = "#7A3B3B";
    if (mouthMode === "flat") { ctx.beginPath(); ctx.moveTo(cx - 30 * u, my); ctx.lineTo(cx + 30 * u, my); ctx.stroke(); }
    else if (mouthMode === "grit") {
      ctx.fillStyle = "#5C2B2B";
      ctx.beginPath(); ctx.roundRect ? ctx.roundRect(cx - 40 * u, my - 12 * u, 80 * u, 26 * u, 8 * u) : ctx.rect(cx - 40 * u, my - 12 * u, 80 * u, 26 * u);
      ctx.fill();
      ctx.strokeStyle = "#FFFFFF"; ctx.lineWidth = 5 * u;
      ctx.beginPath(); ctx.moveTo(cx - 40 * u, my); ctx.lineTo(cx + 40 * u, my); ctx.stroke();
    } else if (mouthMode === "grin" || mouthMode === "cheer") {
      var w = mouthMode === "cheer" ? 62 : 50, h = mouthMode === "cheer" ? 58 : 40;
      ctx.fillStyle = "#5C2B2B";
      ctx.beginPath(); ctx.moveTo(cx - w * u, my - 10 * u);
      ctx.quadraticCurveTo(cx, my + h * u, cx + w * u, my - 10 * u); ctx.closePath(); ctx.fill();
      // teeth only along the top lip, so the open mouth still reads as a smile
      ctx.fillStyle = "#FFFFFF";
      ctx.beginPath(); ctx.moveTo(cx - w * u * 0.88, my - 9 * u);
      ctx.lineTo(cx + w * u * 0.88, my - 9 * u); ctx.lineTo(cx + w * u * 0.74, my - 1 * u);
      ctx.lineTo(cx - w * u * 0.74, my - 1 * u); ctx.closePath(); ctx.fill();
    } else if (mouthMode === "ohno") {
      ctx.fillStyle = "#5C2B2B";
      ctx.beginPath(); ctx.ellipse(cx, my + 4 * u, 30 * u, 22 * u, 0, 0, TAU); ctx.fill();
    } else if (mouthMode === "o") {
      ctx.fillStyle = "#5C2B2B";
      ctx.beginPath(); ctx.ellipse(cx, my + 6 * u, 24 * u, 30 * u, 0, 0, TAU); ctx.fill();
    } else {
      ctx.beginPath(); ctx.moveTo(cx - 32 * u, my + 12 * u);
      ctx.quadraticCurveTo(cx, my - 14 * u, cx + 32 * u, my + 12 * u); ctx.stroke();
    }

    // effort blush when pushing hard
    if (expr === "determined" || expr === "wince" || expr === "cheer") {
      ctx.fillStyle = "rgba(255,90,120,.28)";
      [-1, 1].forEach(function (s) {
        ctx.beginPath(); ctx.ellipse(cx + s * 108 * u, cy + 34 * u, 34 * u, 20 * u, 0, 0, TAU); ctx.fill();
      });
    }
    // headgear drawn into the texture (visor band / cap brim shadow)
    var g = ch.gear % GEARS.length;
    if (g === 2) {
      ctx.fillStyle = "rgba(18,242,228,.55)";
      ctx.fillRect(0, cy - 52 * u, W, 62 * u);
      ctx.fillStyle = "rgba(255,255,255,.22)";
      ctx.fillRect(0, cy - 52 * u, W, 12 * u);
    }
  }

  function makeFaceTexture(ch, expr) {
    var c = document.createElement("canvas");
    c.width = 512; c.height = 512;
    drawFace(c.getContext("2d"), ch, expr, 512, 512);
    var t = new THREE.CanvasTexture(c);
    t.needsUpdate = true;
    return { tex: t, canvas: c };
  }

  // ------------------------------------------------------------------ cars
  var CARS = [
    { name: "Voltra",  w: 1.9, l: 4.3, h: 0.52, wing: 0.55, top: 82,  acc: 34, grip: 0.82, demo: true },
    { name: "Kitsune", w: 1.8, l: 4.0, h: 0.48, wing: 0.30, top: 78,  acc: 38, grip: 0.86, demo: true },
    { name: "Onyx GT", w: 2.0, l: 4.6, h: 0.50, wing: 0.75, top: 88,  acc: 31, grip: 0.79 },
    { name: "Mirai-X", w: 1.85, l: 4.2, h: 0.44, wing: 0.62, top: 85, acc: 36, grip: 0.84 },
    { name: "Havoc",   w: 2.1, l: 4.5, h: 0.58, wing: 0.85, top: 90,  acc: 33, grip: 0.76 },
    { name: "Lumen",   w: 1.75, l: 4.1, h: 0.46, wing: 0.40, top: 86, acc: 39, grip: 0.88 }
  ];
  var PAINTS = ["#12F2E4", "#FF2FA8", "#8B5CF6", "#FFB020", "#39D353", "#F04438", "#FFFFFF", "#101733"];

  // ---------------------------------------------------------------- tracks
  /* Circuit shapes are generated as smooth closed loops and checked for
     minimum corner radius, so no corner is tighter than the cars can
     actually carry speed through. */
  var TRACKS = [
    {
      name: "NEON MILE", sub: "Downtown · 3 laps · flowing",
      accent: 0x12F2E4, accent2: 0xFF2FA8, sky: [0x1A1040, 0x05060F], fog: 0x0A0A1E,
      width: 15, gold: 36, silver: 40, bronze: 46,
      pts: [[507,13,0],[456,25,331],[152,21,467],[-120,5,370],[-323,1,235],
            [-507,13,0],[-456,25,-331],[-152,21,-467],[120,5,-370],[323,1,-235]]
    },
    {
      name: "SKYLINE LOOP", sub: "Elevated · 3 laps · fast & hilly",
      accent: 0xFFB020, accent2: 0x8B5CF6, sky: [0x40184A, 0x0B0713], fog: 0x140B1E,
      width: 14, gold: 40, silver: 45, bronze: 51,
      pts: [[617,37,0],[502,74,290],[231,37,401],[0,0,501],[-309,37,534],
            [-502,74,290],[-463,37,0],[-434,0,-250],[-309,37,-534],[0,74,-579],
            [231,37,-401],[434,0,-250]]
    },
    {
      name: "HARBOR LIGHTS", sub: "Waterfront · 3 laps · technical",
      accent: 0x39D353, accent2: 0x12F2E4, sky: [0x06283A, 0x03080F], fog: 0x04141F,
      width: 13, gold: 36, silver: 40, bronze: 46,
      pts: [[443,10,0],[440,20,212],[244,6,306],[86,2,379],[-108,18,475],
            [-278,14,349],[-329,0,159],[-443,10,0],[-440,20,-212],[-244,6,-306],
            [-86,2,-379],[108,18,-475],[278,14,-349],[329,0,-159]]
    }
  ];

  // -------------------------------------------------------- renderer/scene
  var renderer = new THREE.WebGLRenderer({ antialias: true, powerPreference: "high-performance" });
  renderer.setPixelRatio(Math.min(devicePixelRatio || 1, 2));
  renderer.setSize(innerWidth, innerHeight);
  renderer.domElement.style.cssText = "position:fixed;inset:0;z-index:1";
  document.body.appendChild(renderer.domElement);

  var scene = new THREE.Scene();
  var camera = new THREE.PerspectiveCamera(72, innerWidth / innerHeight, 0.5, 6000);
  var ambient = new THREE.AmbientLight(0x6070A0, 1.15);
  scene.add(ambient);
  var keyLight = new THREE.DirectionalLight(0xBFA8FF, 0.75);
  keyLight.position.set(0.4, 1, 0.35);
  scene.add(keyLight);
  var rimLight = new THREE.DirectionalLight(0x12F2E4, 0.5);
  rimLight.position.set(-0.6, 0.3, -0.8);
  scene.add(rimLight);

  // gradient sky dome
  var skyGeo = new THREE.SphereGeometry(3000, 24, 16);
  var skyMat = new THREE.MeshBasicMaterial({ side: THREE.BackSide, vertexColors: true, fog: false });
  var skyMesh = new THREE.Mesh(skyGeo, skyMat);
  scene.add(skyMesh);
  function paintSky(topHex, botHex) {
    var pos = skyGeo.attributes.position, n = pos.count;
    var colors = new Float32Array(n * 3);
    var top = new THREE.Color(topHex), bot = new THREE.Color(botHex), c = new THREE.Color();
    for (var i = 0; i < n; i++) {
      var y = pos.getY(i) / 3000;
      c.copy(bot).lerp(top, clamp(y * 0.8 + 0.35, 0, 1));
      colors[i * 3] = c.r; colors[i * 3 + 1] = c.g; colors[i * 3 + 2] = c.b;
    }
    skyGeo.setAttribute("color", new THREE.BufferAttribute(colors, 3));
  }

  // stars
  (function () {
    var g = new THREE.BufferGeometry(), n = 900, p = new Float32Array(n * 3);
    for (var i = 0; i < n; i++) {
      var a = Math.random() * TAU, e = Math.random() * 0.6 + 0.08, r = 2400;
      p[i * 3] = Math.cos(a) * Math.cos(e) * r;
      p[i * 3 + 1] = Math.sin(e) * r;
      p[i * 3 + 2] = Math.sin(a) * Math.cos(e) * r;
    }
    g.setAttribute("position", new THREE.BufferAttribute(p, 3));
    scene.add(new THREE.Points(g, new THREE.PointsMaterial({ color: 0xBFD8FF, size: 6, sizeAttenuation: false, fog: false })));
  })();

  // window texture shared by every building
  function windowTexture(tint) {
    var c = document.createElement("canvas"); c.width = 64; c.height = 128;
    var x = c.getContext("2d");
    x.fillStyle = "#080A18"; x.fillRect(0, 0, 64, 128);
    for (var yy = 4; yy < 124; yy += 8) {
      for (var xx = 4; xx < 60; xx += 8) {
        if (Math.random() < 0.42) {
          x.fillStyle = Math.random() < 0.25 ? tint : "rgba(200,220,255," + (0.25 + Math.random() * 0.6) + ")";
          x.fillRect(xx, yy, 5, 5);
        }
      }
    }
    var t = new THREE.CanvasTexture(c);
    t.wrapS = t.wrapT = THREE.RepeatWrapping;
    return t;
  }

  // --------------------------------------------------------- track builder
  var trackGroup = new THREE.Group();
  scene.add(trackGroup);
  var SAMPLES = 900;
  var TP = [], TT = [], TR = [], trackLen = 0, halfW = 7.5, curTrack = null;

  function disposeGroup(g) {
    for (var i = g.children.length - 1; i >= 0; i--) {
      var c = g.children[i];
      if (c.geometry) c.geometry.dispose();
      if (c.material) { if (c.material.map) c.material.map.dispose(); c.material.dispose(); }
      g.remove(c);
    }
  }

  function ribbon(inner, outer, color, yOff, opacity, additive) {
    var pos = [], col = [], idx = [];
    var c = new THREE.Color(color);
    for (var i = 0; i <= SAMPLES; i++) {
      var p = TP[i], r = TR[i];
      pos.push(p.x + r.x * inner, p.y + yOff, p.z + r.z * inner);
      pos.push(p.x + r.x * outer, p.y + yOff, p.z + r.z * outer);
      col.push(c.r, c.g, c.b, c.r * 0.55, c.g * 0.55, c.b * 0.55);
      if (i < SAMPLES) {
        var a = i * 2;
        idx.push(a, a + 1, a + 2, a + 1, a + 3, a + 2);
      }
    }
    var g = new THREE.BufferGeometry();
    g.setAttribute("position", new THREE.Float32BufferAttribute(pos, 3));
    g.setAttribute("color", new THREE.Float32BufferAttribute(col, 3));
    g.setIndex(idx);
    g.computeVertexNormals();
    var m = new THREE.MeshBasicMaterial({
      vertexColors: true, side: THREE.DoubleSide,
      transparent: opacity < 1, opacity: opacity,
      blending: additive ? THREE.AdditiveBlending : THREE.NormalBlending,
      depthWrite: opacity >= 1
    });
    return new THREE.Mesh(g, m);
  }

  function buildTrack(def) {
    disposeGroup(trackGroup);
    curTrack = def;
    halfW = def.width;
    paintSky(def.sky[0], def.sky[1]);
    scene.fog = new THREE.FogExp2(def.fog, 0.00085);

    var pts = def.pts.map(function (p) { return new THREE.Vector3(p[0], p[1], p[2]); });
    var curve = new THREE.CatmullRomCurve3(pts, true, "catmullrom", 0.5);
    trackLen = curve.getLength();
    TP = []; TT = []; TR = [];
    var up = new THREE.Vector3(0, 1, 0);
    for (var i = 0; i <= SAMPLES; i++) {
      var t = i / SAMPLES;
      var p = curve.getPointAt(t % 1);
      var tan = curve.getTangentAt(t % 1).normalize();
      var right = new THREE.Vector3().crossVectors(tan, up).normalize();
      TP.push(p); TT.push(tan); TR.push(right);
    }

    // road surface
    var pos = [], col = [], idx = [];
    var base = new THREE.Color(0x14161F), edge = new THREE.Color(0x1D2130);
    for (var j = 0; j <= SAMPLES; j++) {
      var pp = TP[j], rr = TR[j];
      pos.push(pp.x - rr.x * halfW, pp.y + 0.02, pp.z - rr.z * halfW);
      pos.push(pp.x + rr.x * halfW, pp.y + 0.02, pp.z + rr.z * halfW);
      col.push(edge.r, edge.g, edge.b, base.r, base.g, base.b);
      if (j < SAMPLES) { var a = j * 2; idx.push(a, a + 1, a + 2, a + 1, a + 3, a + 2); }
    }
    var rg = new THREE.BufferGeometry();
    rg.setAttribute("position", new THREE.Float32BufferAttribute(pos, 3));
    rg.setAttribute("color", new THREE.Float32BufferAttribute(col, 3));
    rg.setIndex(idx); rg.computeVertexNormals();
    trackGroup.add(new THREE.Mesh(rg, new THREE.MeshLambertMaterial({ vertexColors: true, side: THREE.DoubleSide })));

    // wet-neon sheen on the tarmac
    trackGroup.add(ribbon(-halfW * 0.92, halfW * 0.92, def.accent, 0.05, 0.10, true));
    // glowing kerbs
    trackGroup.add(ribbon(-halfW - 0.9, -halfW + 0.2, def.accent, 0.10, 1, false));
    trackGroup.add(ribbon(halfW - 0.2, halfW + 0.9, def.accent2, 0.10, 1, false));
    // centre dashes
    (function () {
      var p2 = [], i2 = [], v = 0;
      for (var s = 0; s < SAMPLES; s += 8) {
        var A = TP[s], B = TP[Math.min(s + 4, SAMPLES)], ra = TR[s], rb = TR[Math.min(s + 4, SAMPLES)];
        p2.push(A.x - ra.x * 0.18, A.y + 0.07, A.z - ra.z * 0.18);
        p2.push(A.x + ra.x * 0.18, A.y + 0.07, A.z + ra.z * 0.18);
        p2.push(B.x - rb.x * 0.18, B.y + 0.07, B.z - rb.z * 0.18);
        p2.push(B.x + rb.x * 0.18, B.y + 0.07, B.z + rb.z * 0.18);
        i2.push(v, v + 1, v + 2, v + 1, v + 3, v + 2); v += 4;
      }
      var dg = new THREE.BufferGeometry();
      dg.setAttribute("position", new THREE.Float32BufferAttribute(p2, 3));
      dg.setIndex(i2);
      trackGroup.add(new THREE.Mesh(dg, new THREE.MeshBasicMaterial({ color: 0x5A6480, side: THREE.DoubleSide })));
    })();

    // barrier walls
    (function () {
      [-1, 1].forEach(function (side) {
        var p3 = [], c3 = [], i3 = [], v = 0;
        var lo = new THREE.Color(0x0B0D18);
        var hi = new THREE.Color(side < 0 ? def.accent : def.accent2);
        for (var s = 0; s <= SAMPLES; s++) {
          var P = TP[s], R = TR[s], o = (halfW + 1.0) * side;
          p3.push(P.x + R.x * o, P.y, P.z + R.z * o);
          p3.push(P.x + R.x * o, P.y + 1.7, P.z + R.z * o);
          c3.push(lo.r, lo.g, lo.b, hi.r, hi.g, hi.b);
          if (s < SAMPLES) { i3.push(v, v + 1, v + 2, v + 1, v + 3, v + 2); v += 2; }
        }
        var bg = new THREE.BufferGeometry();
        bg.setAttribute("position", new THREE.Float32BufferAttribute(p3, 3));
        bg.setAttribute("color", new THREE.Float32BufferAttribute(c3, 3));
        bg.setIndex(i3);
        trackGroup.add(new THREE.Mesh(bg, new THREE.MeshBasicMaterial({ vertexColors: true, side: THREE.DoubleSide })));
      });
    })();

    // start/finish gantry + line
    (function () {
      var P = TP[0], R = TR[0], T = TT[0];
      var lineGeo = new THREE.PlaneGeometry(halfW * 2, 3);
      var lc = document.createElement("canvas"); lc.width = 64; lc.height = 8;
      var lx = lc.getContext("2d");
      for (var i = 0; i < 8; i++) for (var j = 0; j < 64; j++) {
        lx.fillStyle = ((i + j) % 2) ? "#FFFFFF" : "#101018"; lx.fillRect(j, i, 1, 1);
      }
      var lt = new THREE.CanvasTexture(lc);
      lt.wrapS = lt.wrapT = THREE.RepeatWrapping; lt.repeat.set(8, 1);
      var line = new THREE.Mesh(lineGeo, new THREE.MeshBasicMaterial({ map: lt }));
      line.rotation.x = -Math.PI / 2;
      line.rotation.z = Math.atan2(R.x, R.z);
      line.position.set(P.x, P.y + 0.09, P.z);
      trackGroup.add(line);

      var pillarGeo = new THREE.BoxGeometry(1.1, 9, 1.1);
      var pm = new THREE.MeshLambertMaterial({ color: 0x1B2038, emissive: def.accent, emissiveIntensity: 0.25 });
      [-1, 1].forEach(function (s) {
        var pil = new THREE.Mesh(pillarGeo, pm);
        pil.position.set(P.x + R.x * (halfW + 1.6) * s, P.y + 4.5, P.z + R.z * (halfW + 1.6) * s);
        trackGroup.add(pil);
      });
      var beam = new THREE.Mesh(new THREE.BoxGeometry(halfW * 2 + 4, 1.5, 1.1),
        new THREE.MeshBasicMaterial({ color: def.accent }));
      beam.position.set(P.x, P.y + 9, P.z);
      beam.rotation.y = Math.atan2(T.x, T.z);
      trackGroup.add(beam);
    })();

    // light arches over the road
    (function () {
      var am = new THREE.MeshBasicMaterial({ color: def.accent2 });
      var am2 = new THREE.MeshBasicMaterial({ color: def.accent });
      for (var s = 60; s < SAMPLES; s += 95) {
        var P = TP[s], R = TR[s], T = TT[s];
        var yaw = Math.atan2(T.x, T.z);
        var top = new THREE.Mesh(new THREE.BoxGeometry(halfW * 2 + 3, 0.55, 0.55), s % 190 === 60 ? am : am2);
        top.position.set(P.x, P.y + 7, P.z); top.rotation.y = yaw;
        trackGroup.add(top);
        [-1, 1].forEach(function (side) {
          var leg = new THREE.Mesh(new THREE.BoxGeometry(0.55, 7, 0.55),
            new THREE.MeshLambertMaterial({ color: 0x151A2C }));
          leg.position.set(P.x + R.x * (halfW + 1.4) * side, P.y + 3.5, P.z + R.z * (halfW + 1.4) * side);
          trackGroup.add(leg);
        });
      }
    })();

    // skyline
    (function () {
      var tex = windowTexture(def.accent === 0x12F2E4 ? "#12F2E4" : "#FF2FA8");
      var mat = new THREE.MeshLambertMaterial({ map: tex, color: 0x8892B0 });
      var geo = new THREE.BoxGeometry(1, 1, 1);
      for (var s = 0; s < SAMPLES; s += 11) {
        [-1, 1].forEach(function (side) {
          if (Math.random() < 0.42) return;
          var P = TP[s], R = TR[s];
          var dist = halfW + 16 + Math.random() * 90;
          var w = 12 + Math.random() * 26, h = 30 + Math.random() * 190, d = 12 + Math.random() * 26;
          var b = new THREE.Mesh(geo, mat);
          b.scale.set(w, h, d);
          b.position.set(P.x + R.x * dist * side, P.y + h / 2 - 3, P.z + R.z * dist * side);
          b.rotation.y = Math.random() * TAU;
          trackGroup.add(b);
          if (Math.random() < 0.3) {
            var cap = new THREE.Mesh(geo, new THREE.MeshBasicMaterial({ color: Math.random() < 0.5 ? def.accent : def.accent2 }));
            cap.scale.set(w * 0.55, 1.2, d * 0.55);
            cap.position.set(b.position.x, P.y + h - 2, b.position.z);
            trackGroup.add(cap);
          }
        });
      }
    })();

    // dark ground
    (function () {
      var g = new THREE.PlaneGeometry(7000, 7000);
      var m = new THREE.MeshLambertMaterial({ color: 0x07080F });
      var mesh = new THREE.Mesh(g, m);
      mesh.rotation.x = -Math.PI / 2;
      mesh.position.y = -6;
      trackGroup.add(mesh);
    })();

    buildMinimapPath();
  }

  // road lookup helpers -----------------------------------------------------
  function nearestIndex(x, z, hint) {
    var best = hint || 0, bd = Infinity;
    var from = (hint == null) ? 0 : hint - 45, to = (hint == null) ? SAMPLES : hint + 45;
    for (var i = from; i <= to; i++) {
      var j = ((i % SAMPLES) + SAMPLES) % SAMPLES;
      var p = TP[j], dx = p.x - x, dz = p.z - z;
      var d = dx * dx + dz * dz;
      if (d < bd) { bd = d; best = j; }
    }
    return best;
  }
  function lateralOffset(x, z, i) {
    var p = TP[i], r = TR[i];
    return (x - p.x) * r.x + (z - p.z) * r.z;
  }
  function roadY(i) { return TP[i].y; }

  // ------------------------------------------------------------- car build
  function buildCar(carDef, paintHex, opts) {
    opts = opts || {};
    var g = new THREE.Group();
    var paint = new THREE.Color(paintHex);
    var bodyMat = opts.ghost
      ? new THREE.MeshLambertMaterial({ color: paint, emissive: paint, emissiveIntensity: 0.55,
          transparent: true, opacity: 0.42 })
      : new THREE.MeshPhongMaterial({ color: paint, specular: 0xAAB4CC, shininess: 70,
          emissive: paint, emissiveIntensity: 0.10 });
    var darkMat = new THREE.MeshLambertMaterial({
      color: 0x121624, transparent: !!opts.ghost, opacity: opts.ghost ? 0.35 : 1
    });
    var glassMat = new THREE.MeshLambertMaterial({
      color: 0x0A1826, emissive: 0x1B3A55, transparent: true, opacity: opts.ghost ? 0.3 : 0.75
    });

    var W = carDef.w, L = carDef.l, H = carDef.h;
    var body = new THREE.Mesh(new THREE.BoxGeometry(W, H, L), bodyMat);
    body.position.y = 0.52; g.add(body);

    var nose = new THREE.Mesh(new THREE.BoxGeometry(W * 0.82, H * 0.7, L * 0.3), bodyMat);
    nose.position.set(0, 0.44, L * 0.5); g.add(nose);

    var cabin = new THREE.Mesh(new THREE.BoxGeometry(W * 0.72, 0.42, L * 0.38), glassMat);
    cabin.position.set(0, 0.86, -L * 0.05); g.add(cabin);

    var skirtL = new THREE.Mesh(new THREE.BoxGeometry(0.16, 0.22, L * 0.7), darkMat);
    skirtL.position.set(-W / 2, 0.3, 0); g.add(skirtL);
    var skirtR = skirtL.clone(); skirtR.position.x = W / 2; g.add(skirtR);

    if (carDef.wing > 0.35) {
      var wing = new THREE.Mesh(new THREE.BoxGeometry(W * 1.02, 0.1, 0.55), bodyMat);
      wing.position.set(0, 0.95 + carDef.wing * 0.25, -L * 0.5);
      g.add(wing);
      [-1, 1].forEach(function (s) {
        var stay = new THREE.Mesh(new THREE.BoxGeometry(0.1, carDef.wing * 0.5, 0.3), darkMat);
        stay.position.set(s * W * 0.36, 0.78 + carDef.wing * 0.12, -L * 0.5);
        g.add(stay);
      });
    }

    // wheels
    var wheelGeo = new THREE.CylinderGeometry(0.42, 0.42, 0.32, 14);
    var tyreMat = new THREE.MeshLambertMaterial({ color: 0x0C0D14 });
    var rimMat = new THREE.MeshBasicMaterial({ color: paint });
    var wheels = [];
    [[-1, 1], [1, 1], [-1, -1], [1, -1]].forEach(function (o) {
      var wg = new THREE.Group();
      var w = new THREE.Mesh(wheelGeo, tyreMat);
      w.rotation.z = Math.PI / 2; wg.add(w);
      var rim = new THREE.Mesh(new THREE.CylinderGeometry(0.2, 0.2, 0.34, 10), rimMat);
      rim.rotation.z = Math.PI / 2; wg.add(rim);
      wg.position.set(o[0] * (W / 2 + 0.02), 0.42, o[1] * L * 0.33);
      g.add(wg); wheels.push(wg);
    });
    g.userData.wheels = wheels;
    g.userData.frontWheels = [wheels[0], wheels[1]];

    // lights
    var head = new THREE.Mesh(new THREE.BoxGeometry(W * 0.68, 0.11, 0.1),
      new THREE.MeshBasicMaterial({ color: 0xEAF6FF }));
    head.position.set(0, 0.5, L * 0.64); g.add(head);
    var tail = new THREE.Mesh(new THREE.BoxGeometry(W * 0.8, 0.12, 0.1),
      new THREE.MeshBasicMaterial({ color: 0xFF2F4A }));
    tail.position.set(0, 0.6, -L * 0.5); g.add(tail);
    g.userData.tail = tail;

    // underglow
    var glow = new THREE.Mesh(new THREE.PlaneGeometry(W * 1.45, L * 1.08),
      new THREE.MeshBasicMaterial({ color: paint, transparent: true, opacity: 0.16, blending: THREE.AdditiveBlending, depthWrite: false }));
    glow.rotation.x = -Math.PI / 2; glow.position.y = 0.035;
    g.add(glow);
    g.userData.glow = glow;

    // boost flames
    var flames = [];
    [-1, 1].forEach(function (s) {
      var f = new THREE.Mesh(new THREE.ConeGeometry(0.22, 1.5, 8),
        new THREE.MeshBasicMaterial({ color: 0x9BE8FF, transparent: true, opacity: 0.9, blending: THREE.AdditiveBlending, depthWrite: false }));
      f.rotation.x = Math.PI / 2;
      f.position.set(s * W * 0.28, 0.5, -L * 0.58);
      f.visible = false;
      g.add(f); flames.push(f);
    });
    g.userData.flames = flames;

    // shadow blob
    var sh = new THREE.Mesh(new THREE.PlaneGeometry(W * 1.12, L * 0.94),
      new THREE.MeshBasicMaterial({ color: 0x000000, transparent: true, opacity: 0.45, depthWrite: false }));
    sh.rotation.x = -Math.PI / 2; sh.position.y = 0.018;
    g.add(sh);

    return g;
  }

  // driver that sits in the cockpit; face texture is swapped live
  function buildDriver(ch, carDef, ghost) {
    var g = new THREE.Group();
    var suit = new THREE.Color(SUITS[ch.suit % SUITS.length]);
    var trim = new THREE.Color(SUITS[ch.trim % SUITS.length]);
    var opts = { transparent: !!ghost, opacity: ghost ? 0.4 : 1 };

    var torso = new THREE.Mesh(new THREE.CylinderGeometry(0.3, 0.36, 0.62, 12),
      new THREE.MeshLambertMaterial(Object.assign({ color: suit, emissive: suit, emissiveIntensity: 0.16 }, opts)));
    torso.position.y = 0.32; g.add(torso);

    var collar = new THREE.Mesh(new THREE.CylinderGeometry(0.31, 0.31, 0.09, 12),
      new THREE.MeshBasicMaterial(Object.assign({ color: trim }, opts)));
    collar.position.y = 0.63; g.add(collar);

    [-1, 1].forEach(function (s) {
      var sh = new THREE.Mesh(new THREE.SphereGeometry(0.16, 10, 8),
        new THREE.MeshLambertMaterial(Object.assign({ color: trim }, opts)));
      sh.position.set(s * 0.3, 0.5, 0); g.add(sh);
      var arm = new THREE.Mesh(new THREE.CylinderGeometry(0.1, 0.1, 0.5, 8),
        new THREE.MeshLambertMaterial(Object.assign({ color: suit }, opts)));
      arm.position.set(s * 0.29, 0.38, 0.18); arm.rotation.x = -0.85; g.add(arm);
    });

    var faceTex = makeFaceTexture(ch, "focus");
    var headMat = new THREE.MeshLambertMaterial(Object.assign({ map: faceTex.tex }, opts));
    var head = new THREE.Mesh(new THREE.SphereGeometry(0.34, 24, 18), headMat);
    head.position.y = 0.96;
    head.rotation.y = Math.PI;          // face the front of the car
    g.add(head);
    g.userData.faceTex = faceTex;
    g.userData.ch = ch;
    g.userData.expr = "focus";
    g.userData.head = head;

    // headgear geometry
    var gear = ch.gear % GEARS.length;
    var hairCol = new THREE.Color(HAIRCOLS[ch.haircol % HAIRCOLS.length]);
    if (gear === 1) {
      var helm = new THREE.Mesh(new THREE.SphereGeometry(0.372, 20, 14, 0, TAU, 0, Math.PI * 0.58),
        new THREE.MeshLambertMaterial(Object.assign({ color: suit, emissive: suit, emissiveIntensity: 0.2 }, opts)));
      helm.position.y = 0.96; g.add(helm);
      var stripe = new THREE.Mesh(new THREE.BoxGeometry(0.09, 0.38, 0.56),
        new THREE.MeshBasicMaterial(Object.assign({ color: trim }, opts)));
      stripe.position.set(0, 1.09, 0); g.add(stripe);
    } else if (gear === 3) {
      var capTop = new THREE.Mesh(new THREE.SphereGeometry(0.35, 16, 10, 0, TAU, 0, Math.PI * 0.5),
        new THREE.MeshLambertMaterial(Object.assign({ color: trim }, opts)));
      capTop.position.y = 1.0; g.add(capTop);
      var brim = new THREE.Mesh(new THREE.BoxGeometry(0.48, 0.05, 0.3),
        new THREE.MeshLambertMaterial(Object.assign({ color: trim }, opts)));
      brim.position.set(0, 1.0, 0.33); g.add(brim);
    } else if (gear === 4) {
      [-1, 1].forEach(function (s) {
        var lens = new THREE.Mesh(new THREE.CylinderGeometry(0.1, 0.1, 0.06, 10),
          new THREE.MeshBasicMaterial(Object.assign({ color: 0x12F2E4 }, opts)));
        lens.rotation.x = Math.PI / 2;
        lens.position.set(s * 0.13, 1.03, 0.31); g.add(lens);
      });
      var band = new THREE.Mesh(new THREE.TorusGeometry(0.34, 0.04, 6, 18),
        new THREE.MeshBasicMaterial(Object.assign({ color: 0x1B2038 }, opts)));
      band.position.y = 1.03; band.rotation.y = Math.PI / 2; g.add(band);
    }
    // hair volume for the styles that need it
    var hs = ch.hair % HAIRS.length;
    if (gear !== 1 && (hs === 2 || hs === 5)) {
      var bun = new THREE.Mesh(new THREE.SphereGeometry(hs === 2 ? 0.17 : 0.11, 10, 8),
        new THREE.MeshLambertMaterial(Object.assign({ color: hairCol }, opts)));
      bun.position.set(0, hs === 2 ? 1.2 : 1.26, hs === 2 ? -0.19 : 0); g.add(bun);
    }

    g.position.set(0, 0.60, -carDef.l * 0.04);
    g.scale.setScalar(1.06);
    return g;
  }

  function setExpression(driver, expr) {
    if (!driver || driver.userData.expr === expr) return;
    driver.userData.expr = expr;
    var ft = driver.userData.faceTex;
    drawFace(ft.canvas.getContext("2d"), driver.userData.ch, expr, 512, 512);
    ft.tex.needsUpdate = true;
    // mirror the player's face into the HUD portrait so the reaction is visible
    if (driver.userData.isPlayer) {
      var hf = $("hudface");
      if (hf) drawFace(hf.getContext("2d"), driver.userData.ch, expr, 128, 128);
    }
  }

  // --------------------------------------------------------------- racers
  var racers = [];      // {kind:'player'|'ai'|'ghost', mesh, ...}
  var player = null;
  var racerGroup = new THREE.Group();
  scene.add(racerGroup);

  var AI_NAMES = ["VYPER", "RONIN", "AZUL", "HEX", "NOVA", "KAZE", "GLITCH", "ONYX"];

  function makeRacerVisual(carIdx, paintIdx, ch, ghost, isPlayer) {
    var carDef = CARS[carIdx % CARS.length];
    var mesh = buildCar(carDef, PAINTS[paintIdx % PAINTS.length], { ghost: ghost });
    var driver = buildDriver(ch, carDef, ghost);
    driver.userData.isPlayer = !!isPlayer;
    mesh.add(driver);
    mesh.userData.driver = driver;
    mesh.userData.carDef = carDef;
    racerGroup.add(mesh);
    return mesh;
  }

  function randomCh(seed) {
    function r(n) { seed = (seed * 9301 + 49297) % 233280; return Math.floor(seed / 233280 * n); }
    return { face: r(FACES.length), skin: r(SKINS.length), hair: r(HAIRS.length),
             haircol: r(HAIRCOLS.length), gear: 1 + r(GEARS.length - 1),
             suit: r(SUITS.length), trim: r(SUITS.length) };
  }

  function clearRacers() {
    for (var i = racerGroup.children.length - 1; i >= 0; i--) racerGroup.remove(racerGroup.children[i]);
    racers = []; player = null;
  }

  // ------------------------------------------------------------- particles
  var Particles = (function () {
    var MAX = 220, pool = [], mat = new THREE.SpriteMaterial({
      color: 0xffffff, transparent: true, opacity: 0.7, blending: THREE.AdditiveBlending, depthWrite: false
    });
    var group = new THREE.Group();
    scene.add(group);
    for (var i = 0; i < MAX; i++) {
      var s = new THREE.Sprite(mat.clone());
      s.visible = false; s.userData.life = 0;
      group.add(s); pool.push(s);
    }
    var next = 0;
    function spawn(x, y, z, color, size, life, vx, vy, vz) {
      var s = pool[next]; next = (next + 1) % MAX;
      s.visible = true;
      s.position.set(x, y, z);
      s.material.color.setHex(color);
      s.material.opacity = 0.8;
      s.scale.setScalar(size);
      s.userData.life = life; s.userData.max = life;
      s.userData.v = [vx || 0, vy || 0, vz || 0];
      s.userData.size = size;
    }
    function update(dt) {
      for (var i = 0; i < MAX; i++) {
        var s = pool[i];
        if (!s.visible) continue;
        s.userData.life -= dt;
        if (s.userData.life <= 0) { s.visible = false; continue; }
        var v = s.userData.v;
        s.position.x += v[0] * dt; s.position.y += v[1] * dt; s.position.z += v[2] * dt;
        v[1] -= 2 * dt;
        var k = s.userData.life / s.userData.max;
        s.material.opacity = 0.8 * k;
        s.scale.setScalar(s.userData.size * (1 + (1 - k) * 1.6));
      }
    }
    return { spawn: spawn, update: update };
  })();

  // ------------------------------------------------------- screen-space FX
  var fx = $("fx"), fxc = fx.getContext("2d");
  var streaks = [];
  for (var si = 0; si < 90; si++) {
    streaks.push({ a: Math.random() * TAU, r: 0.18 + Math.random() * 0.9, len: 0.05 + Math.random() * 0.16 });
  }
  function sizeFx() {
    fx.width = innerWidth; fx.height = innerHeight;
  }
  sizeFx();
  var flashAmount = 0;
  function drawFx(speedRatio, boosting, drifting) {
    var W = fx.width, H = fx.height;
    fxc.clearRect(0, 0, W, H);
    var cx = W / 2, cy = H / 2, R = Math.sqrt(W * W + H * H) / 2;

    // speed streaks
    var intensity = clamp((speedRatio - 0.34) / 0.66, 0, 1) * (boosting ? 1.5 : 1);
    if (intensity > 0.01) {
      fxc.save();
      fxc.strokeStyle = boosting ? "rgba(180,240,255,0.75)" : "rgba(190,210,255,0.5)";
      fxc.lineWidth = 2;
      for (var i = 0; i < streaks.length; i++) {
        var s = streaks[i];
        var r0 = R * s.r, r1 = R * (s.r + s.len * intensity * 2.1);
        fxc.globalAlpha = intensity * 0.55 * (0.4 + s.r * 0.6);
        fxc.beginPath();
        fxc.moveTo(cx + Math.cos(s.a) * r0, cy + Math.sin(s.a) * r0);
        fxc.lineTo(cx + Math.cos(s.a) * r1, cy + Math.sin(s.a) * r1);
        fxc.stroke();
        s.a += 0.0009 * (i % 3 - 1);
      }
      fxc.restore();
    }

    // vignette that tightens with speed
    var vg = fxc.createRadialGradient(cx, cy, R * (0.42 - speedRatio * 0.16), cx, cy, R);
    vg.addColorStop(0, "rgba(0,0,0,0)");
    vg.addColorStop(1, "rgba(0,0,0," + (0.45 + speedRatio * 0.22) + ")");
    fxc.fillStyle = vg; fxc.fillRect(0, 0, W, H);

    // colour bleed at the edges — cyan on boost, magenta on drift
    if (boosting || drifting) {
      var g2 = fxc.createRadialGradient(cx, cy, R * 0.5, cx, cy, R);
      g2.addColorStop(0, "rgba(0,0,0,0)");
      g2.addColorStop(1, boosting ? "rgba(18,242,228,0.24)" : "rgba(255,47,168,0.2)");
      fxc.fillStyle = g2; fxc.fillRect(0, 0, W, H);
    }

    if (flashAmount > 0.01) {
      fxc.fillStyle = "rgba(255,255,255," + flashAmount * 0.5 + ")";
      fxc.fillRect(0, 0, W, H);
      flashAmount *= 0.86;
    }
  }

  // -------------------------------------------------------------- minimap
  var mm = $("minimap"), mmc = mm.getContext("2d"), mmPath = null;
  function buildMinimapPath() {
    var minX = Infinity, maxX = -Infinity, minZ = Infinity, maxZ = -Infinity;
    for (var i = 0; i < SAMPLES; i += 4) {
      var p = TP[i];
      if (p.x < minX) minX = p.x; if (p.x > maxX) maxX = p.x;
      if (p.z < minZ) minZ = p.z; if (p.z > maxZ) maxZ = p.z;
    }
    var w = maxX - minX, h = maxZ - minZ, s = 216 / Math.max(w, h);
    mmPath = { minX: minX, minZ: minZ, s: s, ox: (256 - w * s) / 2, oy: (256 - h * s) / 2 };
  }
  function mmXY(x, z) {
    return [mmPath.ox + (x - mmPath.minX) * mmPath.s, mmPath.oy + (z - mmPath.minZ) * mmPath.s];
  }
  function drawMinimap() {
    if (!mmPath) return;
    mmc.clearRect(0, 0, 256, 256);
    mmc.strokeStyle = "rgba(255,255,255,.28)";
    mmc.lineWidth = 9; mmc.lineJoin = "round";
    mmc.beginPath();
    for (var i = 0; i <= SAMPLES; i += 6) {
      var p = TP[i % SAMPLES], xy = mmXY(p.x, p.z);
      if (i === 0) mmc.moveTo(xy[0], xy[1]); else mmc.lineTo(xy[0], xy[1]);
    }
    mmc.closePath(); mmc.stroke();
    mmc.strokeStyle = "rgba(18,242,228,.55)"; mmc.lineWidth = 3; mmc.stroke();

    racers.forEach(function (r) {
      var xy = mmXY(r.mesh.position.x, r.mesh.position.z);
      mmc.fillStyle = r.kind === "player" ? "#FFFFFF" : r.kind === "ghost" ? "rgba(139,92,246,.9)" : "#FF2FA8";
      mmc.beginPath();
      mmc.arc(xy[0], xy[1], r.kind === "player" ? 9 : 6, 0, TAU);
      mmc.fill();
    });
  }

  // ---------------------------------------------------------- race codes
  function myCode(trackIdx, best, splits) {
    var payload = {
      n: (save.name || "RACER").slice(0, 12), c: save.car, p: save.paint,
      t: trackIdx, b: Math.round(best * 1000), s: splits.map(function (s) { return Math.round(s * 1000); }),
      h: [save.ch.face, save.ch.skin, save.ch.hair, save.ch.haircol, save.ch.gear, save.ch.suit, save.ch.trim]
    };
    return "RC1." + btoa(JSON.stringify(payload));
  }
  function parseCode(str) {
    str = (str || "").trim();
    if (str.indexOf("RC1.") !== 0) return null;
    try {
      var d = JSON.parse(atob(str.slice(4)));
      if (typeof d.b !== "number" || !d.s || !d.s.length) return null;
      if (typeof d.t !== "number" || d.t < 0 || d.t >= TRACKS.length) return null;
      var h = d.h || [0, 2, 1, 0, 1, 0, 1];
      return {
        n: String(d.n || "RIVAL").slice(0, 12),
        car: clamp(d.c | 0, 0, CARS.length - 1),
        paint: clamp(d.p | 0, 0, PAINTS.length - 1),
        track: d.t | 0,
        best: d.b / 1000,
        splits: d.s.map(function (v) { return v / 1000; }),
        ch: { face: h[0] | 0, skin: h[1] | 0, hair: h[2] | 0, haircol: h[3] | 0,
              gear: h[4] | 0, suit: h[5] | 0, trim: h[6] | 0 }
      };
    } catch (e) { return null; }
  }

  var SECTORS = 8;

  // ------------------------------------------------------------ race state
  var STATE = "title";     // title | garage | countdown | racing | finished
  var raceLaps = 3;
  var raceTime = 0, countdown = 0, lapStart = 0, sessionBest = null, lastSplits = [];
  var raceStarted = false;   // true once the player has crossed the start line
  var shake = 0, camShakeV = new THREE.Vector3();

  function spawnAt(t, laneOff, mesh) {
    var i = Math.floor(t * SAMPLES) % SAMPLES;
    var p = TP[i], r = TR[i], tan = TT[i];
    mesh.position.set(p.x + r.x * laneOff, p.y + 0.02, p.z + r.z * laneOff);
    mesh.rotation.y = Math.atan2(tan.x, tan.z);
    return i;
  }

  function startRace(mode) {
    var tIdx = save.track;
    if (IS_DEMO) tIdx = 0;
    if (curTrack !== TRACKS[tIdx]) buildTrack(TRACKS[tIdx]);
    clearRacers();

    // --- player
    var pmesh = makeRacerVisual(save.car, save.paint, save.ch, false, true);
    var startI = spawnAt(0.997, -3, pmesh);
    player = {
      kind: "player", name: save.name || "YOU", mesh: pmesh,
      carDef: CARS[save.car % CARS.length],
      vel: new THREE.Vector3(), yaw: pmesh.rotation.y, idx: startI,
      lap: -1, prevT: startI / SAMPLES, progress: -0.003, speed: 0,
      drift: false, driftCharge: 0, boost: 0, nitro: 0,
      sector: 0, splits: [], lapTime: 0, best: null, crashT: 0, exprT: 0, steer: 0
    };
    racers.push(player);

    // --- AI rivals (skipped in time attack)
    if (mode !== "ta") {
      var aiCount = IS_DEMO ? 3 : 3;
      for (var a = 0; a < aiCount; a++) {
        var ch = randomCh(1000 + a * 77);
        var carI = (save.car + a + 1) % (IS_DEMO ? 2 : CARS.length);
        var paintI = (save.paint + a + 2) % PAINTS.length;
        var m = makeRacerVisual(carI, paintI, ch, false);
        var lane = [-3, 3, -6.5, 6.5][a % 4];
        spawnAt(0.997 - (a + 1) * 0.004, lane, m);
        racers.push({
          kind: "ai", name: AI_NAMES[a % AI_NAMES.length], mesh: m,
          t: 0.997 - (a + 1) * 0.004, lane: lane, laneT: Math.random() * 10,
          skill: 0.93 + a * 0.022, speed: 0, lap: -1, prevT: 0.997, progress: -0.003, sector: 0
        });
      }
    }

    // --- ghosts from the leaderboard for this circuit
    var ghosts = save.lb.filter(function (e) { return e.track === tIdx; })
      .sort(function (x, y) { return x.best - y.best; }).slice(0, 4);
    ghosts.forEach(function (e, gi) {
      var m = makeRacerVisual(e.car, e.paint, e.ch, true);
      spawnAt(0.997, [6.5, -6.5, 9, -9][gi % 4], m);
      racers.push({
        kind: "ghost", name: e.n, mesh: m, data: e, lane: [6.5, -6.5, 9, -9][gi % 4],
        t: 0, lap: -1, prevT: 0, progress: -1, elapsed: 0, sector: 0
      });
    });

    raceStarted = false;
    raceTime = 0; countdown = 3.999; lapStart = 0; lastSplits = [];
    sessionBest = (save.best[tIdx] && save.best[tIdx].time) || null;
    STATE = "countdown";
    $("hud").classList.add("on");
    $("garage").classList.remove("on");
    $("results").classList.remove("open");
    $("besttime").textContent = "BEST " + (sessionBest ? fmtTime(sessionBest) : "—");
    setExpression(player.mesh.userData.driver, "focus");
    AudioSys.start();
    bigText("", 0);
  }

  function bigText(txt, ms, color) {
    var el = $("bigtext");
    if (!txt) { el.classList.remove("show"); return; }
    el.textContent = txt;
    el.style.color = color || "#fff";
    el.classList.add("show");
    clearTimeout(bigText._t);
    if (ms) bigText._t = setTimeout(function () { el.classList.remove("show"); }, ms);
  }
  function toast(msg) {
    var el = $("toast");
    el.textContent = msg; el.classList.add("show");
    clearTimeout(toast._t);
    toast._t = setTimeout(function () { el.classList.remove("show"); }, 2200);
  }

  // ------------------------------------------------------------- physics
  var keys = {};
  function inputSteer() {
    return (keys.KeyA || keys.ArrowLeft ? 1 : 0) - (keys.KeyD || keys.ArrowRight ? 1 : 0);
  }
  function inputThrottle() {
    if (keys.KeyW || keys.ArrowUp) return 1;
    if (keys.KeyS || keys.ArrowDown) return -1;
    return 0;
  }
  function driftHeld() { return !!(keys.ShiftLeft || keys.ShiftRight || keys.Space); }

  function wrapAngle(a) {
    while (a > Math.PI) a -= TAU;
    while (a < -Math.PI) a += TAU;
    return a;
  }
  var AUTOPILOT = false;   // dev/attract-mode driver

  function updatePlayer(dt) {
    var p = player, car = p.carDef;
    var steer = inputSteer(), thr = inputThrottle(), wantDrift = driftHeld();

    var fwdVec = new THREE.Vector3(Math.sin(p.yaw), 0, Math.cos(p.yaw));
    var rightVec = new THREE.Vector3(Math.cos(p.yaw), 0, -Math.sin(p.yaw));
    var fwd = p.vel.dot(fwdVec), lat = p.vel.dot(rightVec);

    if (AUTOPILOT) {
      var look = 16 + Math.round(fwd * 0.55);
      var aim = TP[(p.idx + look) % SAMPLES];
      var err = wrapAngle(Math.atan2(aim.x - p.mesh.position.x, aim.z - p.mesh.position.z) - p.yaw);
      steer = clamp(err * 2.6, -1, 1);
      // ease off before the tight stuff, and drift the big corners
      var far = TP[(p.idx + look + 30) % SAMPLES];
      var errFar = Math.abs(wrapAngle(Math.atan2(far.x - p.mesh.position.x, far.z - p.mesh.position.z) - p.yaw));
      thr = errFar > 0.55 && fwd > car.top * 0.72 ? 0 : 1;
      wantDrift = Math.abs(err) > 0.30 && fwd > 30;
    }

    p.steer = lerp(p.steer, steer, clamp(dt * 12, 0, 1));

    var topSpeed = car.top * (p.boost > 0 ? 1.28 : 1);
    var accel = car.acc * (p.boost > 0 ? 2.0 : 1);

    if (thr > 0) fwd += accel * dt;
    else if (thr < 0) fwd -= (fwd > 0 ? 70 : 26) * dt;
    fwd = clamp(fwd, -22, topSpeed);

    // drift: hold the button through a corner to break traction
    var canDrift = wantDrift && Math.abs(p.steer) > 0.25 && fwd > 16;
    if (canDrift && !p.drift) { p.drift = true; p.driftCharge = 0; }
    if (!wantDrift || fwd < 10) {
      if (p.drift) releaseDrift();
    }
    if (p.drift) {
      p.driftCharge += dt * (0.6 + Math.abs(lat) * 0.055);
      lat += -p.steer * 34 * dt;
      p.nitro = clamp(p.nitro + dt * 0.20, 0, 1);
    }

    var gripFactor = p.drift ? 0.965 : car.grip + 0.13;
    lat *= Math.pow(clamp(gripFactor, 0, 0.999), dt * 60);
    fwd *= Math.pow(0.9965, dt * 60);

    var steerRate = (2.05 - (fwd / car.top) * 0.85) * (p.drift ? 1.5 : 1);
    p.yaw += p.steer * steerRate * dt * (fwd > 1.5 ? 1 : Math.max(0, fwd / 1.5));

    p.vel.copy(fwdVec).multiplyScalar(fwd).addScaledVector(rightVec, lat);
    p.mesh.position.addScaledVector(p.vel, dt);
    p.speed = fwd;

    if (p.boost > 0) p.boost = Math.max(0, p.boost - dt);

    // ---- road containment
    p.idx = nearestIndex(p.mesh.position.x, p.mesh.position.z, p.idx);
    var off = lateralOffset(p.mesh.position.x, p.mesh.position.z, p.idx);
    var limit = halfW + 0.35;
    if (Math.abs(off) > limit) {
      var over = Math.abs(off) - limit;
      var sgn = off > 0 ? 1 : -1;
      var cp = TP[p.idx], rv = TR[p.idx];
      p.mesh.position.x = cp.x + rv.x * limit * sgn;
      p.mesh.position.z = cp.z + rv.z * limit * sgn;

      // slide along the barrier instead of dead-stopping against it: kill the
      // velocity going into the wall, keep (most of) the speed running along it
      var normal = new THREE.Vector3(rv.x * sgn, 0, rv.z * sgn);
      var into = p.vel.dot(normal);
      var hit = clamp(Math.max(0, into) * 0.045 + over * 0.25, 0, 1);
      if (into > 0) p.vel.addScaledVector(normal, -into * 1.15);
      p.vel.multiplyScalar(1 - 0.22 * hit);
      p.speed = p.vel.dot(fwdVec);
      if (hit > 0.25 && p.crashT <= 0) {
        AudioSys.crash();
        shake = Math.min(1.1, 0.35 + hit);
        p.crashT = 0.85;
        for (var s = 0; s < 9; s++) {
          Particles.spawn(p.mesh.position.x, p.mesh.position.y + 0.6, p.mesh.position.z,
            0xFFC24A, 0.5, 0.5, (Math.random() - 0.5) * 12, Math.random() * 7, (Math.random() - 0.5) * 12);
        }
      }
    }

    // follow the road surface
    var targetY = roadY(p.idx);
    p.mesh.position.y = lerp(p.mesh.position.y, targetY, clamp(dt * 8, 0, 1));

    // ---- lap + sector timing
    var tNow = p.idx / SAMPLES;
    if (p.prevT > 0.85 && tNow < 0.15) {
      // crossed the line
      completeLap();
    }
    var sec = Math.floor(tNow * SECTORS);
    if (sec !== p.sector && ((sec === p.sector + 1) || (p.sector === SECTORS - 1 && sec === 0))) {
      p.splits.push(p.lapTime);
      p.sector = sec;
    }
    p.prevT = tNow;
    p.progress = p.lap + tNow;

    // ---- visuals
    var mesh = p.mesh;
    var slip = Math.atan2(lat, Math.max(6, Math.abs(fwd)));
    mesh.rotation.y = p.yaw + slip * 0.75;          // visible counter-steer
    mesh.rotation.z = lerp(mesh.rotation.z, -p.steer * 0.055 - slip * 0.09, clamp(dt * 8, 0, 1));

    var wheels = mesh.userData.wheels;
    if (wheels) {
      var spin = fwd * dt * 2.4;
      wheels.forEach(function (w) { w.children[0].rotation.x += spin; w.children[1].rotation.x += spin; });
      mesh.userData.frontWheels.forEach(function (w) { w.rotation.y = p.steer * 0.42; });
    }
    var flames = mesh.userData.flames;
    if (flames) {
      var on = p.boost > 0;
      flames.forEach(function (f) {
        f.visible = on;
        if (on) f.scale.set(1, 0.7 + Math.random() * 0.8, 1);
      });
    }
    mesh.userData.glow.material.opacity = 0.2 + (p.drift ? 0.3 : 0) + (p.boost > 0 ? 0.35 : 0);

    // drift smoke + sparks
    if (p.drift && Math.abs(lat) > 4) {
      var tier = driftTier(p.driftCharge);
      var col = [0xBFD8FF, 0x7FF6EE, 0xC58AF0, 0xFF86C8][tier];
      for (var w2 = -1; w2 <= 1; w2 += 2) {
        Particles.spawn(
          mesh.position.x - Math.sin(p.yaw) * 1.4 + Math.cos(p.yaw) * w2 * 0.9,
          mesh.position.y + 0.15,
          mesh.position.z - Math.cos(p.yaw) * 1.4 - Math.sin(p.yaw) * w2 * 0.9,
          col, 0.75, 0.55, (Math.random() - 0.5) * 3, 1.2 + Math.random(), (Math.random() - 0.5) * 3);
      }
    }
    if (p.boost > 0 && Math.random() < 0.6) {
      Particles.spawn(mesh.position.x - Math.sin(p.yaw) * 2.4, mesh.position.y + 0.5,
        mesh.position.z - Math.cos(p.yaw) * 2.4, 0x9BE8FF, 0.9, 0.35,
        -Math.sin(p.yaw) * 8, Math.random() * 2, -Math.cos(p.yaw) * 8);
    }

    // ---- driver expression reacts to the driving
    if (p.crashT > 0) { p.crashT -= dt; setExpression(mesh.userData.driver, "wince"); }
    else if (p.boost > 0) setExpression(mesh.userData.driver, "grin");
    else if (p.drift) setExpression(mesh.userData.driver, "determined");
    else if (p.speed > car.top * 0.86) setExpression(mesh.userData.driver, "shock");
    else setExpression(mesh.userData.driver, "focus");

    AudioSys.engine(clamp(Math.abs(fwd) / car.top, 0, 1.2), p.boost > 0);
    AudioSys.drift(p.drift ? clamp(Math.abs(lat) / 24, 0, 1) : 0);

    p.lapTime += dt;
  }

  function driftTier(charge) {
    if (charge > 2.6) return 3;
    if (charge > 1.6) return 2;
    if (charge > 0.85) return 1;
    return 0;
  }
  function releaseDrift() {
    var p = player, tier = driftTier(p.driftCharge);
    p.drift = false;
    if (tier > 0) {
      p.boost = [0, 0.75, 1.25, 1.9][tier];
      AudioSys.boost();
      flashAmount = 0.35 + tier * 0.12;
      shake = Math.max(shake, 0.22 + tier * 0.1);
      bigText(["", "BOOST!", "SUPER BOOST!", "ULTRA BOOST!"][tier], 900,
              ["#fff", "#7ff6ee", "#c58af0", "#ff86c8"][tier]);
    }
    p.driftCharge = 0;
  }
  function fireNitro() {
    var p = player;
    if (p.nitro < 0.999 || p.boost > 0) return;
    p.nitro = 0; p.boost = 1.7;
    AudioSys.boost(); flashAmount = 0.5; shake = 0.4;
    bigText("NITRO!", 800, "#FFB020");
  }

  function completeLap() {
    var p = player;
    var lapT = p.lapTime;
    p.lap++;
    lastSplits = p.splits.slice(0, SECTORS);
    p.splits = [];
    p.sector = 0;
    p.lapTime = 0;

    // the first crossing only starts the clock — the grid sits behind the line
    if (p.lap <= 0) {
      raceStarted = true;
      bigText("LAP 1", 900, "#fff");
      return;
    }

    if (p.best == null || lapT < p.best) p.best = lapT;
    var tIdx = IS_DEMO ? 0 : save.track;
    var prevBest = save.best[tIdx] && save.best[tIdx].time;
    if (lapT > 4 && (prevBest == null || lapT < prevBest)) {
      save.best[tIdx] = { time: lapT, splits: lastSplits.slice() };
      sessionBest = lapT;
      persist();
      upsertLeaderboard(save.name || "YOU", tIdx, lapT, lastSplits, save.ch, save.car, save.paint, true);
      bigText("NEW RECORD!", 1600, "#12F2E4");
    } else {
      bigText("LAP " + p.lap, 1000, "#fff");
    }
    AudioSys.lap();
    $("besttime").textContent = "BEST " + (sessionBest ? fmtTime(sessionBest) : "—");

    if (p.lap >= raceLaps) finishRace();
  }

  function upsertLeaderboard(name, track, best, splits, ch, car, paint, isMe) {
    var existing = null;
    for (var i = 0; i < save.lb.length; i++) {
      if (save.lb[i].n === name && save.lb[i].track === track) { existing = save.lb[i]; break; }
    }
    if (existing) {
      if (best < existing.best) { existing.best = best; existing.splits = splits; }
      existing.me = !!isMe;
    } else {
      save.lb.push({ n: name, track: track, best: best, splits: splits, ch: ch, car: car, paint: paint, me: !!isMe });
    }
    save.lb.sort(function (a, b) { return a.best - b.best; });
    if (save.lb.length > 40) save.lb.length = 40;
    persist();
  }

  function finishRace() {
    STATE = "finished";
    var p = player;
    var place = 1;
    racers.forEach(function (r) { if (r !== p && r.progress > p.progress) place++; });
    var tIdx = IS_DEMO ? 0 : save.track;
    var def = TRACKS[tIdx];
    var best = p.best || Infinity;

    var medal = "🏁", label = "Finished";
    if (best <= def.gold) { medal = "🥇"; label = "GOLD — you are elite"; save.medals[tIdx] = "gold"; }
    else if (best <= def.silver) { medal = "🥈"; label = "SILVER — so close"; if (save.medals[tIdx] !== "gold") save.medals[tIdx] = "silver"; }
    else if (best <= def.bronze) { medal = "🥉"; label = "BRONZE — keep pushing"; if (!save.medals[tIdx]) save.medals[tIdx] = "bronze"; }
    persist();

    setExpression(p.mesh.userData.driver, place === 1 ? "cheer" : place <= 2 ? "grin" : "sad");
    AudioSys.win();
    bigText("FINISH", 1400, "#12F2E4");

    // portrait of the driver reacting to the result
    var pc = $("portrait").getContext("2d");
    drawFace(pc, save.ch, place === 1 ? "cheer" : place <= 2 ? "grin" : "sad", 216, 216);

    $("medal").textContent = medal;
    $("rtime").textContent = isFinite(best) ? fmtTime(best) : "—";
    $("rsub").textContent = "P" + place + " · best lap · " + label;
    var sp = $("rsplits");
    sp.innerHTML = "";
    lastSplits.forEach(function (s, i) {
      var el = document.createElement("span");
      el.textContent = "S" + (i + 1) + " " + s.toFixed(2);
      sp.appendChild(el);
    });

    var tb = $("rlb").querySelector("tbody");
    tb.innerHTML = "";
    var rows = racers.map(function (r) {
      var lap = r === p ? best : (r.kind === "ghost" ? r.data.best : estimateAiLap(r));
      return { n: r === p ? (save.name || "YOU") : r.name, best: isFinite(lap) ? lap : 1e9, me: r === p };
    }).sort(function (a, b) { return a.best - b.best; });
    rows.forEach(function (row, i) {
      var tr = document.createElement("tr");
      if (row.me) tr.className = "me";
      tr.innerHTML = "<td>" + (i + 1) + "</td><td>" + escapeHtml(row.n) + "</td><td class='t'>" + fmtTime(row.best) + "</td>";
      tb.appendChild(tr);
    });

    setTimeout(function () { $("results").classList.add("open"); }, 1200);
  }
  function estimateAiLap(r) { return TRACKS[IS_DEMO ? 0 : save.track].silver * (2 - r.skill); }
  function escapeHtml(s) {
    return String(s).replace(/[&<>"']/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
    });
  }

  // ---------------------------------------------------------------- AI/ghost
  function updateAI(r, dt) {
    var def = TRACKS[IS_DEMO ? 0 : save.track];
    var pace = trackLen / (def.silver * (2 - r.skill));   // units per second
    // rubber band so the pack stays exciting without feeling cheap
    if (player) {
      var gap = player.progress - r.progress;
      pace *= clamp(1 + gap * 0.12, 0.86, 1.16);
    }
    r.laneT += dt * 0.5;
    var lane = r.lane * (0.7 + Math.sin(r.laneT) * 0.3);
    r.t = (r.t + (pace * dt) / trackLen) % 1;
    if (r.prevT > 0.85 && r.t < 0.15) r.lap++;
    r.prevT = r.t;
    r.progress = r.lap + r.t;

    var i = Math.floor(r.t * SAMPLES) % SAMPLES;
    var p = TP[i], rv = TR[i], tan = TT[i];
    r.mesh.position.set(p.x + rv.x * lane, p.y + 0.02, p.z + rv.z * lane);
    r.mesh.rotation.y = Math.atan2(tan.x, tan.z);
    var w = r.mesh.userData.wheels;
    if (w) w.forEach(function (ww) { ww.children[0].rotation.x += dt * 20; });
  }

  function updateGhost(r, dt) {
    // a ghost's recorded lap begins at the line, so hold them until we cross it
    if (raceStarted) r.elapsed += dt;
    var splits = r.data.splits && r.data.splits.length ? r.data.splits : null;
    var lapTime = r.data.best;
    var e = r.elapsed % lapTime;
    var frac;
    if (splits && splits.length >= 2) {
      // interpolate along the sector splits so their pace is genuinely theirs
      var s = 0;
      while (s < splits.length && splits[s] < e) s++;
      var prevT = s === 0 ? 0 : splits[s - 1];
      var nextT = s < splits.length ? splits[s] : lapTime;
      var segFrac = nextT > prevT ? (e - prevT) / (nextT - prevT) : 0;
      frac = (s + segFrac) / (splits.length + 1);
    } else {
      frac = e / lapTime;
    }
    r.lap = Math.floor(r.elapsed / lapTime);
    r.t = clamp(frac, 0, 0.9999);
    r.progress = raceStarted ? r.lap + r.t : -1;

    var i = Math.floor(r.t * SAMPLES) % SAMPLES;
    var p = TP[i], rv = TR[i], tan = TT[i];
    r.mesh.position.set(p.x + rv.x * r.lane, p.y + 0.02, p.z + rv.z * r.lane);
    r.mesh.rotation.y = Math.atan2(tan.x, tan.z);
    var op = 0.30 + Math.sin(r.elapsed * 3) * 0.05;
    r.mesh.traverse(function (o) {
      if (o.material && o.material.transparent && o.userData.baseOp !== false) o.material.opacity = op + 0.12;
    });
  }

  // ------------------------------------------------------------------- HUD
  var hudAcc = 0;
  function updateHud(dt) {
    var p = player;
    if (!p) return;
    var def = TRACKS[IS_DEMO ? 0 : save.track];
    var t = p.idx / SAMPLES;

    $("lapfill").style.width = (t * 100).toFixed(1) + "%";
    $("lapdot").style.left = (t * 100).toFixed(1) + "%";
    $("lappct").textContent = Math.round(t * 100) + "%";
    $("lapnum").textContent = "LAP " + clamp(p.lap + 1, 1, raceLaps) + "/" + raceLaps;

    var kmh = Math.max(0, Math.round(p.speed * 3.9));
    $("spdnum").textContent = kmh;
    var ratio = clamp(p.speed / p.carDef.top, 0, 1);
    $("gaugefill").setAttribute("stroke-dashoffset", (286 - 286 * ratio).toFixed(1));
    $("gear").textContent = Math.min(6, 1 + Math.floor(ratio * 6));

    $("curtime").textContent = fmtTime(p.lapTime);
    $("nitrofill").style.width = (p.nitro * 100).toFixed(0) + "%";
    $("nitro").classList.toggle("ready", p.nitro >= 0.999);

    // live delta against the personal best, sector by sector
    var d = $("delta");
    var bestSplits = (save.best[IS_DEMO ? 0 : save.track] || {}).splits;
    if (bestSplits && bestSplits.length && p.splits.length) {
      var i = p.splits.length - 1;
      if (bestSplits[i] != null) {
        var diff = p.splits[i] - bestSplits[i];
        d.textContent = fmtDelta(diff);
        d.className = "mono show " + (diff > 0 ? "up" : "dn");
      }
    } else if (!p.splits.length) {
      d.className = "mono";
    }

    // drift charge readout
    var dl = $("driftlbl");
    if (p.drift) {
      var tier = driftTier(p.driftCharge);
      dl.textContent = ["DRIFT", "BLUE", "VIOLET", "PINK"][tier];
      dl.style.color = ["#BFD8FF", "#7ff6ee", "#c58af0", "#ff86c8"][tier];
      dl.classList.add("show");
    } else dl.classList.remove("show");

    // position
    var place = 1;
    racers.forEach(function (r) { if (r !== p && r.progress > p.progress) place++; });
    if (place !== updateHud._place) {
      if (updateHud._place && place < updateHud._place) AudioSys.pass();
      updateHud._place = place;
    }
    $("posnum").textContent = place;
    $("posof").textContent = "OF " + racers.length;

    hudAcc += dt;
    if (hudAcc > 0.05) { drawMinimap(); hudAcc = 0; }
  }

  // ---------------------------------------------------------------- camera
  var camTarget = new THREE.Vector3(), camLook = new THREE.Vector3();
  function updateCamera(dt) {
    var p = player;
    if (!p) return;
    var back = 6.9, up = 2.55;
    var ratio = clamp(p.speed / p.carDef.top, 0, 1);
    back += ratio * 1.4;

    var yaw = p.yaw;
    camTarget.set(
      p.mesh.position.x - Math.sin(yaw) * back,
      p.mesh.position.y + up,
      p.mesh.position.z - Math.cos(yaw) * back
    );
    var k = 1 - Math.pow(0.0022, dt);
    camera.position.lerp(camTarget, k);

    camLook.set(
      p.mesh.position.x + Math.sin(yaw) * 11,
      p.mesh.position.y + 1.25,
      p.mesh.position.z + Math.cos(yaw) * 11
    );
    camera.lookAt(camLook);

    if (shake > 0.002) {
      camShakeV.set((Math.random() - 0.5) * shake, (Math.random() - 0.5) * shake, (Math.random() - 0.5) * shake);
      camera.position.add(camShakeV);
      shake *= Math.pow(0.02, dt);
    }
    var targetFov = 62 + ratio * 16 + (p.boost > 0 ? 9 : 0);
    camera.fov = lerp(camera.fov, targetFov, clamp(dt * 4, 0, 1));
    camera.updateProjectionMatrix();
  }

  // garage turntable camera
  var garageAngle = 0;
  function updateGarageCamera(dt) {
    garageAngle += dt * 0.30;
    var r = 11.5;
    var focus = player ? player.mesh.position : new THREE.Vector3();
    // frame the car left of centre so it isn't hidden behind the options panel
    camera.position.set(focus.x + Math.sin(garageAngle) * r, focus.y + 3.5, focus.z + Math.cos(garageAngle) * r);
    camera.lookAt(focus.x + 3.2, focus.y + 0.75, focus.z);
    camera.fov = lerp(camera.fov, 40, clamp(dt * 4, 0, 1));
    camera.updateProjectionMatrix();
  }

  // --------------------------------------------------------------- garage
  function showGarage() {
    STATE = "garage";
    $("garage").classList.add("on");
    $("hud").classList.remove("on");
    $("results").classList.remove("open");
    var tIdx = IS_DEMO ? 0 : save.track;
    if (curTrack !== TRACKS[tIdx]) buildTrack(TRACKS[tIdx]);
    clearRacers();
    var mesh = makeRacerVisual(save.car, save.paint, save.ch, false, true);
    spawnAt(0.5, 0, mesh);
    player = { kind: "player", mesh: mesh, carDef: CARS[save.car % CARS.length], progress: 0, speed: 0 };
    racers.push(player);
    setExpression(mesh.userData.driver, "grin");
    renderGarageUI();
  }

  function chip(label, sel, locked, onClick, styleColor) {
    var b = document.createElement("button");
    b.className = "chip" + (sel ? " sel" : "") + (locked ? " lock" : "");
    if (styleColor) {
      b.className = "sw" + (sel ? " sel" : "") + (locked ? " lock" : "");
      b.style.background = styleColor;
      b.title = label;
    } else b.textContent = label;
    if (!locked) b.addEventListener("click", onClick);
    else b.addEventListener("click", function () { toast("🔒 Unlock in the full game"); });
    return b;
  }
  function rebuildPlayerPreview() {
    clearRacers();
    var mesh = makeRacerVisual(save.car, save.paint, save.ch, false, true);
    spawnAt(0.5, 0, mesh);
    player = { kind: "player", mesh: mesh, carDef: CARS[save.car % CARS.length], progress: 0, speed: 0 };
    racers.push(player);
    setExpression(mesh.userData.driver, "grin");
    persist();
  }
  // garage portrait cycles through the in-race expressions so you can see
  // exactly how your driver will react before you ever turn a wheel
  var GARAGE_EXPRS = ["focus", "determined", "grin", "shock", "wince", "cheer"];
  var garageExprI = 0;
  function drawGarageFace() {
    var c = $("gface");
    if (c) drawFace(c.getContext("2d"), save.ch, GARAGE_EXPRS[garageExprI % GARAGE_EXPRS.length], 256, 256);
  }
  setInterval(function () {
    if (STATE !== "garage") return;
    garageExprI++;
    drawGarageFace();
  }, 1400);

  function renderGarageUI() {
    $("pname").value = save.name;
    drawGarageFace();
    function fill(id, arr, key, colors) {
      var el = $(id); el.innerHTML = "";
      arr.forEach(function (label, i) {
        var locked = IS_DEMO && i >= 2;
        el.appendChild(chip(label, save.ch[key] === i, locked, function () {
          save.ch[key] = i; rebuildPlayerPreview(); renderGarageUI();
        }, colors ? colors[i] : null));
      });
    }
    fill("c-face", FACES, "face");
    fill("c-skin", SKINS.map(function (s, i) { return "Skin " + (i + 1); }), "skin", SKINS);
    fill("c-hair", HAIRS, "hair");
    fill("c-haircol", HAIRCOLS.map(function (s, i) { return "Hair " + (i + 1); }), "haircol", HAIRCOLS);
    fill("c-gear", GEARS, "gear");
    fill("c-suit", SUITS.map(function (s, i) { return "Suit " + (i + 1); }), "suit", SUITS);
    fill("c-trim", SUITS.map(function (s, i) { return "Trim " + (i + 1); }), "trim", SUITS);

    var cc = $("c-car"); cc.innerHTML = "";
    CARS.forEach(function (c, i) {
      var locked = IS_DEMO && !c.demo;
      cc.appendChild(chip(c.name, save.car === i, locked, function () {
        save.car = i; rebuildPlayerPreview(); renderGarageUI();
      }));
    });
    var cp = $("c-paint"); cp.innerHTML = "";
    PAINTS.forEach(function (p, i) {
      var locked = IS_DEMO && i >= 3;
      cp.appendChild(chip("Paint " + (i + 1), save.paint === i, locked, function () {
        save.paint = i; rebuildPlayerPreview(); renderGarageUI();
      }, p));
    });

    var ct = $("c-track"); ct.innerHTML = "";
    TRACKS.forEach(function (t, i) {
      var locked = IS_DEMO && i > 0;
      var d = document.createElement("div");
      d.className = "tcard" + (save.track === i ? " sel" : "") + (locked ? " lock" : "");
      var medal = save.medals[i] === "gold" ? "🥇" : save.medals[i] === "silver" ? "🥈" : save.medals[i] === "bronze" ? "🥉" : "";
      var bestT = save.best[i] && save.best[i].time;
      d.innerHTML = '<div class="dot" style="background:linear-gradient(135deg,#' +
        t.accent.toString(16).padStart(6, "0") + ',#' + t.accent2.toString(16).padStart(6, "0") + ')"></div>' +
        '<div><div class="nm">' + t.name + (locked ? " 🔒" : "") + '</div><div class="mt">' + t.sub +
        (bestT ? " · PB " + fmtTime(bestT) : "") + '</div></div><div class="md">' + medal + '</div>';
      d.addEventListener("click", function () {
        if (locked) { toast("🔒 Unlock all 3 circuits in the full game"); return; }
        save.track = i; persist();
        buildTrack(TRACKS[i]);
        rebuildPlayerPreview();
        renderGarageUI();
      });
      ct.appendChild(d);
    });
  }

  // ---------------------------------------------------------- online panel
  function renderLeaderboard(tableId, filterTrack) {
    var tb = $(tableId).querySelector("tbody");
    tb.innerHTML = "";
    var rows = save.lb.filter(function (e) { return filterTrack == null || e.track === filterTrack; });
    if (!rows.length) {
      tb.innerHTML = '<tr><td colspan="4" style="color:#7f93bd">No times yet — finish a lap to set one.</td></tr>';
      return;
    }
    rows.slice(0, 15).forEach(function (e, i) {
      var tr = document.createElement("tr");
      if (e.me) tr.className = "me";
      tr.innerHTML = "<td>" + (i + 1) + "</td><td>" + escapeHtml(e.n) + "</td><td>" +
        TRACKS[e.track].name + "</td><td class='t'>" + fmtTime(e.best) + "</td>";
      tb.appendChild(tr);
    });
  }
  function openOnline() {
    var tIdx = IS_DEMO ? 0 : save.track;
    var b = save.best[tIdx];
    $("my-code").value = b ? myCode(tIdx, b.time, b.splits || []) :
      "Set a lap time first — then your Race Code appears here.";
    renderLeaderboard("lb", null);
    $("online").classList.add("open");
  }

  // ----------------------------------------------------------------- input
  addEventListener("keydown", function (e) {
    keys[e.code] = true;
    if (["Space", "ArrowUp", "ArrowDown", "ArrowLeft", "ArrowRight"].indexOf(e.code) >= 0) e.preventDefault();
    if (e.code === "Space" && player && STATE === "racing" && player.nitro >= 0.999 && !player.drift) fireNitro();
    if (e.code === "KeyR" && STATE === "racing") respawn();
  });
  addEventListener("keyup", function (e) { keys[e.code] = false; });

  function respawn() {
    var p = player;
    var i = p.idx;
    var tan = TT[i], pp = TP[i];
    p.mesh.position.set(pp.x, pp.y + 0.05, pp.z);
    p.yaw = Math.atan2(tan.x, tan.z);
    p.vel.set(0, 0, 0); p.speed = 0; p.drift = false; p.driftCharge = 0;
    toast("Respawned");
  }

  function bindHold(id, code) {
    var el = $(id);
    if (!el) return;
    var on = function (e) { e.preventDefault(); keys[code] = true; };
    var off = function (e) { e.preventDefault(); keys[code] = false; };
    el.addEventListener("touchstart", on, { passive: false });
    el.addEventListener("touchend", off);
    el.addEventListener("touchcancel", off);
    el.addEventListener("mousedown", on);
    el.addEventListener("mouseup", off);
    el.addEventListener("mouseleave", off);
  }
  bindHold("t-left", "KeyA"); bindHold("t-right", "KeyD");
  bindHold("t-gas", "KeyW"); bindHold("t-drift", "ShiftLeft");
  if ("ontouchstart" in window) $("touch").style.display = "block";

  // buttons
  $("title-go").addEventListener("click", function (e) {
    e.stopPropagation();
    $("title").classList.remove("on");
    AudioSys.start();
    if (!save.helpSeen) { $("help").classList.add("open"); }
    showGarage();
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
  $("garage-btn").addEventListener("click", function () { showGarage(); });
  $("online-btn").addEventListener("click", openOnline);
  $("online-close").addEventListener("click", function () { $("online").classList.remove("open"); });
  $("copy-code").addEventListener("click", function () {
    var ta = $("my-code");
    ta.select();
    try { document.execCommand("copy"); } catch (e) {}
    if (navigator.clipboard) navigator.clipboard.writeText(ta.value).catch(function () {});
    toast("Race Code copied — send it to a rival!");
  });
  $("add-code").addEventListener("click", function () {
    var d = parseCode($("their-code").value);
    if (!d) { toast("That Race Code doesn't look right."); return; }
    upsertLeaderboard(d.n, d.track, d.best, d.splits, d.ch, d.car, d.paint, false);
    renderLeaderboard("lb", null);
    $("their-code").value = "";
    toast("👻 " + d.n + " added — their ghost races you on " + TRACKS[d.track].name);
  });
  $("pname").addEventListener("input", function () {
    save.name = this.value.toUpperCase().slice(0, 12) || "RACER"; persist();
  });
  $("race-btn").addEventListener("click", function () { startRace("race"); });
  $("ta-btn").addEventListener("click", function () { startRace("ta"); });
  $("again-btn").addEventListener("click", function () {
    $("results").classList.remove("open"); startRace("race");
  });
  $("togarage-btn").addEventListener("click", function () {
    $("results").classList.remove("open"); showGarage();
  });
  $("share-btn").addEventListener("click", function () {
    var tIdx = IS_DEMO ? 0 : save.track;
    var b = save.best[tIdx];
    if (!b) { toast("Finish a clean lap first."); return; }
    var code = myCode(tIdx, b.time, b.splits || []);
    if (navigator.clipboard) navigator.clipboard.writeText(code).catch(function () {});
    $("results").classList.remove("open");
    openOnline();
    toast("Race Code ready — send it to the world!");
  });

  if (IS_DEMO && CFG.buyLink) {
    $("demo-banner").style.display = "flex";
    $("buy-full").href = CFG.buyLink;
  }

  addEventListener("resize", function () {
    camera.aspect = innerWidth / innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(innerWidth, innerHeight);
    sizeFx();
  });

  // ------------------------------------------------------------- main loop
  buildTrack(TRACKS[0]);
  camera.position.set(0, 12, 26);
  camera.lookAt(0, 0, 0);

  var clock = new THREE.Clock();
  function animate() {
    requestAnimationFrame(animate);
    var dt = Math.min(clock.getDelta(), 0.05);

    if (STATE === "countdown") {
      var prev = Math.ceil(countdown);
      countdown -= dt;
      var now = Math.ceil(countdown);
      if (now !== prev) {
        if (now > 0) { bigText(String(now), 900, "#fff"); AudioSys.beep(false); }
        else { bigText("GO!", 900, "#12F2E4"); AudioSys.beep(true); STATE = "racing"; flashAmount = 0.4; }
      }
      updateCamera(dt);
    } else if (STATE === "racing") {
      raceTime += dt;
      updatePlayer(dt);
      racers.forEach(function (r) {
        if (r.kind === "ai") updateAI(r, dt);
        else if (r.kind === "ghost") updateGhost(r, dt);
      });
      updateCamera(dt);
      updateHud(dt);
    } else if (STATE === "garage") {
      updateGarageCamera(dt);
    } else if (STATE === "finished") {
      racers.forEach(function (r) {
        if (r.kind === "ai") updateAI(r, dt);
        else if (r.kind === "ghost") updateGhost(r, dt);
      });
      if (player) {
        player.vel.multiplyScalar(Math.pow(0.2, dt));
        player.mesh.position.addScaledVector(player.vel, dt);
        player.speed *= Math.pow(0.2, dt);
      }
      updateCamera(dt);
    } else {
      // title: slow flyover of the circuit
      garageAngle += dt * 0.06;
      var i = Math.floor((garageAngle * 0.05 % 1) * SAMPLES) % SAMPLES;
      var p = TP[i], tan = TT[i];
      camera.position.set(p.x - Math.sin(Math.atan2(tan.x, tan.z)) * 16, p.y + 7, p.z - Math.cos(Math.atan2(tan.x, tan.z)) * 16);
      camera.lookAt(p.x, p.y + 1.5, p.z);
      camera.fov = 62; camera.updateProjectionMatrix();
    }

    Particles.update(dt);
    var ratio = player && player.speed ? clamp(player.speed / player.carDef.top, 0, 1) : 0;
    drawFx(STATE === "racing" ? ratio : 0, !!(player && player.boost > 0), !!(player && player.drift));

    skyMesh.position.copy(camera.position);
    renderer.render(scene, camera);
  }
  animate();

  // --------------------------------------------------------------- DEV API
  window.DEV = {
    state: function () {
      return {
        st: STATE, lap: player && player.lap, speed: player && Math.round(player.speed),
        racers: racers.length, track: (IS_DEMO ? 0 : save.track), best: save.best,
        nitro: player && player.nitro, drift: player && player.drift, boost: player && player.boost,
        expr: player && player.mesh.userData.driver && player.mesh.userData.driver.userData.expr
      };
    },
    go: function () { $("title-go").click(); },
    autopilot: function (on) { AUTOPILOT = on !== false; },
    setTrack: function (i) { save.track = i; persist(); },
    lapOf: function () { return player && player.best; },
    race: function (mode) { startRace(mode || "race"); },
    key: function (code, down) { keys[code] = !!down; },
    warp: function (t) {
      // jump the player along the circuit — used to test laps quickly
      var i = Math.floor(t * SAMPLES) % SAMPLES;
      player.mesh.position.set(TP[i].x, TP[i].y + 0.05, TP[i].z);
      player.idx = i; player.prevT = t;
      player.yaw = Math.atan2(TT[i].x, TT[i].z);
    },
    finish: function () { player.lap = raceLaps - 1; player.lapTime = 30; completeLap(); },
    code: function () {
      var t = IS_DEMO ? 0 : save.track;
      return save.best[t] ? myCode(t, save.best[t].time, save.best[t].splits || []) : null;
    },
    addCode: function (c) { $("their-code").value = c; $("add-code").click(); },
    setBest: function (time) {
      var t = IS_DEMO ? 0 : save.track;
      var sp = []; for (var i = 1; i <= SECTORS; i++) sp.push(time * i / (SECTORS + 1));
      save.best[t] = { time: time, splits: sp };
      upsertLeaderboard(save.name, t, time, sp, save.ch, save.car, save.paint, true);
      persist();
    },
    reset: function () { localStorage.removeItem("neondrift"); location.reload(); }
  };
})();
