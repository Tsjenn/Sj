/* Critter Drop — drop-and-merge in the Wildhaven world.
   Two of a kind touch -> they merge into the next critter. Fill the
   jar past the line and it's over. Self-contained: no external
   requests; ytgame SDK hooks optional with localStorage fallback. */
(function () {
  "use strict";

  var TIERS = 10;
  var NAMES = ["pebblit", "flufftail", "bubbletide", "aquaphin", "cinderpup",
    "emberling", "mossback", "zephyrix", "glimmerwing", "nocturnix"];
  var TCOL = ["#B8B4C0", "#A2D286", "#A6DADA", "#84C0E4", "#E0806A",
    "#F49E68", "#9EB87A", "#F8DC7C", "#C0A0E8", "#7076AA"];

  var cv = document.getElementById("c"), cx = cv.getContext("2d");
  var W = 0, H = 0, DPR = Math.min(window.devicePixelRatio || 1, 2);
  var WALL = 6, FLOOR = 8, DANGER = 0;
  function resize() {
    W = window.innerWidth; H = window.innerHeight;
    cv.width = W * DPR; cv.height = H * DPR;
    cx.setTransform(DPR, 0, 0, DPR, 0, 0);
    DANGER = H * 0.17;
  }
  window.addEventListener("resize", resize);
  resize();
  function radius(t) { return Math.min(W, 480) * 0.0425 * Math.pow(1.185, t); }

  /* ---------------------------------------------------- ytgame (optional) */
  var YT = typeof window.ytgame === "object" ? window.ytgame : null;
  function sdk(fn) { try { return fn && fn(); } catch (e) {} }

  /* --------------------------------------------------------------- audio */
  var AC = null, master = null, noiseBuf = null, muted = false;
  try { muted = localStorage.getItem("critter-drop-muted") === "1"; } catch (e) {}
  function ensureAC() {
    if (!AC) {
      try {
        AC = new (window.AudioContext || window.webkitAudioContext)();
        master = AC.createGain();
        master.gain.value = muted ? 0 : 1;
        master.connect(AC.destination);
        var len = AC.sampleRate * 0.5;
        noiseBuf = AC.createBuffer(1, len, AC.sampleRate);
        var d = noiseBuf.getChannelData(0);
        for (var i = 0; i < len; i++) d[i] = Math.random() * 2 - 1;
        startMusic();
      } catch (e) {}
    }
    if (AC && AC.state === "suspended") { try { AC.resume(); } catch (e) {} }
  }
  function tone(f, when, dur, type, gain, glideTo) {
    if (!AC) return;
    var o = AC.createOscillator(), g = AC.createGain(), t0 = when || AC.currentTime;
    o.type = type || "triangle"; o.frequency.setValueAtTime(f, t0);
    if (glideTo) o.frequency.exponentialRampToValueAtTime(glideTo, t0 + dur);
    g.gain.setValueAtTime(0.0001, t0);
    g.gain.linearRampToValueAtTime(gain || 0.15, t0 + 0.012);
    g.gain.exponentialRampToValueAtTime(0.001, t0 + dur);
    o.connect(g); g.connect(master); o.start(t0); o.stop(t0 + dur + 0.05);
  }
  function noise(when, dur, freq, q, gain) {
    if (!AC || !noiseBuf) return;
    var s = AC.createBufferSource(), f = AC.createBiquadFilter(), g = AC.createGain();
    var t0 = when || AC.currentTime;
    s.buffer = noiseBuf; f.type = "bandpass"; f.frequency.value = freq; f.Q.value = q || 1;
    g.gain.setValueAtTime(gain || 0.2, t0);
    g.gain.exponentialRampToValueAtTime(0.001, t0 + dur);
    s.connect(f); f.connect(g); g.connect(master); s.start(t0); s.stop(t0 + dur + 0.05);
  }
  var PENTA = [523.25, 587.33, 659.25, 783.99, 880, 1046.5, 1174.7, 1318.5, 1568, 1760];
  function mergeChime(tier) {
    ensureAC(); if (!AC) return;
    var f = PENTA[Math.min(tier, PENTA.length - 1)];
    tone(f, 0, 0.3, "triangle", 0.16);
    tone(f * 1.5, AC.currentTime + 0.04, 0.22, "sine", 0.06);
    noise(0, 0.06, 2400, 0.8, 0.05);
  }
  function plop() { ensureAC(); if (AC) { tone(300, 0, 0.1, "sine", 0.12, 140); } }
  function womp() {
    ensureAC(); if (!AC) return;
    tone(220, 0, 0.6, "sine", 0.24, 50);
    noise(AC.currentTime + 0.05, 0.3, 260, 0.8, 0.1);
  }
  function fanfare() {
    ensureAC(); if (!AC) return;
    [523.25, 659.25, 783.99, 1046.5].forEach(function (f, i) {
      tone(f, AC.currentTime + i * 0.09, 0.3, "triangle", 0.13);
    });
  }
  function novaSfx() {
    ensureAC(); if (!AC) return;
    [392, 523.25, 659.25, 783.99, 1046.5, 1318.5].forEach(function (f, i) {
      tone(f, AC.currentTime + i * 0.05, 0.28, "triangle", 0.11);
    });
  }
  function click() { ensureAC(); tone(620, 0, 0.05, "square", 0.04); }

  /* music — brighter than the tower: C / G / Am / F, 92 BPM */
  var PROG = [[261.63, 329.63, 392], [196, 246.94, 293.66],
              [220, 261.63, 329.63], [174.61, 220, 261.63]];
  var POOL = [523.25, 587.33, 659.25, 783.99, 880, 1046.5];
  var MELO = [[0, -1, 1, -1, 2, -1, 3, -1], [4, -1, 3, -1, -1, 2, -1, -1],
              [2, -1, 3, -1, 4, -1, 5, -1], [3, -1, 2, -1, 0, -1, -1, -1]];
  var STEP = 60 / 92 / 2, musicAt = 0, musicStep = 0, musicTimer = null;
  function startMusic() {
    if (musicTimer || !AC) return;
    musicAt = AC.currentTime + 0.1;
    musicTimer = setInterval(function () {
      if (!AC || paused) return;
      while (musicAt < AC.currentTime + 0.9) {
        var bar = Math.floor(musicStep / 8) % 4, st = musicStep % 8;
        if (st === 0) {
          PROG[bar].forEach(function (f) {
            tone(f, musicAt, STEP * 8 * 0.95, "sine", 0.026);
          });
        }
        var m = MELO[bar][st];
        if (m >= 0) tone(POOL[m], musicAt, 0.4, "triangle", 0.045);
        musicAt += STEP; musicStep++;
      }
    }, 220);
  }
  document.getElementById("mute").textContent = muted ? "🔇" : "🔊";
  document.getElementById("mute").addEventListener("click", function () {
    muted = !muted;
    try { localStorage.setItem("critter-drop-muted", muted ? "1" : "0"); } catch (e) {}
    if (master) master.gain.value = muted ? 0 : 1;
    this.textContent = muted ? "🔇" : "🔊";
  });

  /* -------------------------------------------------------------- sprites */
  var IMGS = [], loaded = 0;
  for (var ti = 0; ti < TIERS; ti++) {
    (function (n) {
      var im = new Image();
      im.onload = function () { loaded++; };
      im.src = "img/b" + n + ".png";
      IMGS[n] = im;
    })(ti);
  }

  /* ---------------------------------------------------------------- state */
  var balls, particles, floats, rings;
  var score = 0, best = 0, state = "title", nextTier = 0, curTier = 0;
  var aimX = 0, aiming = false, dropCd = 0, dangerT = 0, idc = 0;
  var t = 0, paused = false, chainN = 0, chainT = 0;

  try { best = +(localStorage.getItem("critter-drop-best") || 0); } catch (e) {}
  sdk(function () {
    if (YT && YT.game && YT.game.loadData) {
      YT.game.loadData().then(function (d) {
        try { var j = JSON.parse(d || "{}"); if (j.best > best) best = j.best; } catch (e) {}
      });
    }
  });
  function saveBest() {
    try { localStorage.setItem("critter-drop-best", "" + best); } catch (e) {}
    sdk(function () { YT && YT.game && YT.game.saveData && YT.game.saveData(JSON.stringify({ best: best })); });
  }
  function pickTier() {
    var r = Math.random() * 100;
    return r < 30 ? 0 : r < 55 ? 1 : r < 75 ? 2 : r < 90 ? 3 : 4;
  }
  function reset() {
    balls = []; particles = []; floats = []; rings = [];
    score = 0; dangerT = 0; dropCd = 0; chainN = 0; chainT = 0;
    curTier = pickTier(); nextTier = pickTier();
    aimX = W / 2;
    reviveUsed = false;
    setScore();
  }
  function setScore() {
    document.getElementById("score").textContent = score;
    var el = document.getElementById("chain");
    el.textContent = chainN > 1 ? "CHAIN ×" + chainN : "";
    el.style.opacity = chainN > 1 ? 1 : 0;
  }

  /* -------------------------------------------------------------- physics */
  function spawn(tier, x, y, vy) {
    var r = radius(tier);
    x = Math.max(WALL + r, Math.min(W - WALL - r, x));
    balls.push({ id: ++idc, x: x, y: y, vx: 0, vy: vy || 0, r: r, tier: tier, cd: 5 });
  }
  function dropBall() {
    if (state !== "play" || dropCd > 0) return;
    plop();
    spawn(curTier, aimX, DANGER * 0.55, 2.5);
    curTier = nextTier; nextTier = pickTier();
    dropCd = 22;
  }
  function physics() {
    var steps = 2, g = 0.34, floorY = H - FLOOR;
    for (var s = 0; s < steps; s++) {
      var i, j, a, b;
      for (i = 0; i < balls.length; i++) {
        a = balls[i];
        a.vy += g; a.vx *= 0.999; a.vy *= 0.999;
        a.x += a.vx; a.y += a.vy;
        if (a.cd > 0) a.cd--;
        if (a.x < WALL + a.r) { a.x = WALL + a.r; a.vx *= -0.25; }
        if (a.x > W - WALL - a.r) { a.x = W - WALL - a.r; a.vx *= -0.25; }
        if (a.y > floorY - a.r) { a.y = floorY - a.r; a.vy *= -0.12; a.vx *= 0.95; }
      }
      for (i = 0; i < balls.length; i++) {
        a = balls[i]; if (!a) continue;
        for (j = i + 1; j < balls.length; j++) {
          b = balls[j]; if (!b) continue;
          var dx = b.x - a.x, dy = b.y - a.y;
          var rr = a.r + b.r, d2 = dx * dx + dy * dy;
          if (d2 === 0) continue;
          // merges fire on contact (small tolerance), not only on overlap —
          // two of a kind resting against each other must still combine
          if (a.tier === b.tier && a.cd <= 0 && b.cd <= 0 &&
              d2 < (rr + 2) * (rr + 2)) {
            if (a.tier < TIERS - 1) { merge(i, j); } else { nova(i, j); }
            j = balls.length; continue;
          }
          if (d2 >= rr * rr) continue;
          var d = Math.sqrt(d2), nx = dx / d, ny = dy / d, ov = rr - d;
          var ma = a.r * a.r, mb = b.r * b.r, tm = ma + mb;
          a.x -= nx * ov * (mb / tm); a.y -= ny * ov * (mb / tm);
          b.x += nx * ov * (ma / tm); b.y += ny * ov * (ma / tm);
          var rvx = b.vx - a.vx, rvy = b.vy - a.vy;
          var vn = rvx * nx + rvy * ny;
          if (vn < 0) {
            var imp = -(1 + 0.12) * vn / (1 / ma + 1 / mb);
            a.vx -= imp * nx / ma; a.vy -= imp * ny / ma;
            b.vx += imp * nx / mb; b.vy += imp * ny / mb;
          }
        }
      }
    }
  }
  function merge(i, j) {
    var a = balls[i], b = balls[j], nt = a.tier + 1;
    var mx = (a.x + b.x) / 2, my = (a.y + b.y) / 2;
    balls.splice(j, 1); balls.splice(i, 1);
    spawn(nt, mx, my, -1.2);
    score += (nt + 1) * (nt + 2) / 2;
    chainN = (chainT > 0) ? chainN + 1 : 1;
    chainT = 72;
    mergeChime(nt);
    burst(mx, my, TCOL[nt], 14 + nt * 3);
    rings.push({ x: mx, y: my, r: radius(nt) * 0.6, max: radius(nt) * 2.1, a: 0.8, col: TCOL[nt] });
    if (chainN > 1) floats.push({ x: mx, y: my - radius(nt), txt: "CHAIN ×" + chainN, a: 1, s: 1.4 });
    if (nt === TIERS - 1) floats.push({ x: W / 2, y: my - radius(nt) - 20, txt: "NOCTURNIX!", a: 1, s: 1.8 });
    setScore();
  }
  function nova(i, j) {
    // two nocturnix meet: moonburst — both vanish, big bonus
    var a = balls[i], b = balls[j];
    var mx = (a.x + b.x) / 2, my = (a.y + b.y) / 2;
    balls.splice(j, 1); balls.splice(i, 1);
    score += 200;
    novaSfx();
    for (var k = 0; k < 3; k++) burst(mx, my, ["#FFE9A8", "#C0A0E8", "#7076AA"][k], 26);
    rings.push({ x: mx, y: my, r: 30, max: Math.min(W, H) * 0.5, a: 0.9, col: "#FFE9A8" });
    floats.push({ x: W / 2, y: my - 40, txt: "MOONBURST! +200", a: 1, s: 1.8 });
    setScore();
  }
  function checkDanger() {
    var hot = false;
    for (var i = 0; i < balls.length; i++) {
      var a = balls[i];
      // "resting" = barely moved this frame (velocity jitters in a
      // pressured pile, displacement doesn't)
      if (a.cd <= 0 && a.y - a.r < DANGER &&
          Math.abs(a.y - (a.py === undefined ? a.y : a.py)) < 0.8) { hot = true; break; }
    }
    dangerT = hot ? dangerT + 1 / 60 : Math.max(0, dangerT - 2 / 60);
    if (dangerT > 1.6) gameOver();
  }

  function gameOver() {
    state = "over";
    overs++;
    womp();
    if (score > best && score > 0) {
      best = score; saveBest();
      fanfare();
      burst(W / 2, H * 0.4, "#F4A96A", 26);
      burst(W / 2, H * 0.4, "#A2D286", 26);
      floats.push({ x: W / 2, y: H * 0.3, txt: "NEW BEST!", a: 1, s: 1.8 });
    }
    document.getElementById("final").textContent = score;
    document.getElementById("best").textContent = "best " + best;
    document.getElementById("revive").style.display =
      (rewardedAvailable() && !reviveUsed) ? "block" : "none";
    document.getElementById("over").style.display = "flex";
    sdk(function () { YT && YT.engagement && YT.engagement.sendScore && YT.engagement.sendScore({ value: score }); });
  }

  /* ------------------------------------------------ ads (Playgama build) */
  // SDK ships only in the Playgama zip; inert everywhere else. Reward is
  // granted ONLY on the SDK's "rewarded" state.
  var reviveUsed = false, adGotReward = false, lastInterstitial = 0, overs = 0;
  var adPurpose = "revive", giftCdUntil = 0;
  function bridgeAds() {
    var b = window.bridge;
    return (b && b.advertisement) ? b.advertisement : null;
  }
  function rewardedAvailable() {
    try { var a = bridgeAds(); return !!(a && a.isRewardedSupported); } catch (e) { return false; }
  }
  function revive() {
    reviveUsed = true;
    for (var i = balls.length - 1; i >= 0; i--) {
      if (balls[i].tier <= 2) {
        burst(balls[i].x, balls[i].y, TCOL[balls[i].tier], 10);
        balls.splice(i, 1);
      }
    }
    dangerT = 0;
    document.getElementById("over").style.display = "none";
    state = "play";
  }
  function initAds() {
    var a = bridgeAds();
    if (!a || typeof a.on !== "function") return;
    a.on("rewarded_state_changed", function (s) {
      if (s === "opened") { paused = true; }
      if (s === "rewarded") { adGotReward = true; }
      if (s === "closed" || s === "failed") {
        paused = false;
        if (adGotReward) {
          adGotReward = false;
          if (adPurpose === "gift") { giftGrant(); } else { revive(); }
        }
      }
    });
    a.on("interstitial_state_changed", function (s) {
      if (s === "opened") { paused = true; }
      if (s === "closed" || s === "failed") { paused = false; }
    });
  }
  function maybeInterstitial() {
    // between runs only, never more than one a minute
    try {
      var a = bridgeAds();
      if (!a || !a.isInterstitialSupported) return;
      var now = Date.now();
      if (overs >= 1 && now - lastInterstitial > 60000) {
        lastInterstitial = now;
        a.showInterstitial();
      }
    } catch (e) {}
  }
  // mid-run rewarded gift: the NEXT critter becomes a big one.
  // Optional, 90s cooldown, granted only on a completed watch.
  function giftGrant() {
    nextTier = Math.max(nextTier, 6);
    giftCdUntil = Date.now() + 90000;
    floats.push({ x: W / 2, y: H * 0.35, txt: "BIG CRITTER INCOMING!", a: 1, s: 1.6 });
    fanfare();
  }
  function giftVisible() {
    // title too — certification testers sit on the title screen
    return (state === "play" || state === "title") &&
      rewardedAvailable() && Date.now() > giftCdUntil;
  }

  function burst(x, y, col, n) {
    for (var i = 0; i < n; i++) {
      var a = Math.random() * 6.28, s = 2 + Math.random() * 3.5;
      particles.push({ x: x, y: y, vx: Math.cos(a) * s, vy: Math.sin(a) * s - 2, a: 1, col: col });
    }
  }

  /* ----------------------------------------------------------------- draw */
  function hx(a) {
    return [parseInt(a.slice(1, 3), 16), parseInt(a.slice(3, 5), 16), parseInt(a.slice(5, 7), 16)];
  }
  function mixh(a, b, f) {
    var pa = hx(a), pb = hx(b);
    return "rgb(" + pa.map(function (v, i) { return Math.round(v + (pb[i] - v) * f); }).join(",") + ")";
  }
  // the meadow day cycle — advances with score, like a long afternoon
  var PHASES = [
    { top: "#BFE3F2", bot: "#FBEFD9", day: 1 },     // morning meadow
    { top: "#F7C989", bot: "#FBE3C4", day: 0.78 },  // golden hour
    { top: "#8E7FB8", bot: "#E5C3BE", day: 0.3 },   // dusk
    { top: "#565B8E", bot: "#33375C", day: 0.06 },  // moonlit night...
    { top: "#3E4370", bot: "#262A4A", day: 0.04 }   // ...held deep, then dawn
  ];
  var clouds = [], motes = [], flies = [];
  (function () {
    for (var i = 0; i < 4; i++) {
      clouds.push({ x: (i * 173 + 40) % 600, y: 0.05 + i * 0.045, s: 20 + (i % 3) * 9, v: 0.1 + i * 0.045 });
    }
    for (i = 0; i < 14; i++) {
      motes.push({ x: (i * 131 + 17) % 600, y: (i * 257 + 60) % 600, v: 0.14 + (i % 5) * 0.05, ph: i * 1.3 });
    }
    for (i = 0; i < 7; i++) {
      flies.push({ x: (i * 197 + 60) % 600, y: (i * 149 + 90) % 600, ph: i * 2.1 });
    }
  })();
  function phaseInfo() {
    var ph = (score % 60) / 60 * PHASES.length;
    var i = Math.floor(ph) % PHASES.length, j = (i + 1) % PHASES.length, f = ph - Math.floor(ph);
    return { top: mixh(PHASES[i].top, PHASES[j].top, f),
      bot: mixh(PHASES[i].bot, PHASES[j].bot, f),
      day: PHASES[i].day + (PHASES[j].day - PHASES[i].day) * f };
  }
  function bg() {
    var p = phaseInfo();
    var g = cx.createLinearGradient(0, 0, 0, H);
    g.addColorStop(0, p.top);
    g.addColorStop(1, p.bot);
    cx.fillStyle = g; cx.fillRect(0, 0, W, H);
    document.body.classList.toggle("night", p.day < 0.4);

    // sun / moon (upper-left, clear of the NEXT preview and gift button)
    var cxp = W * 0.16, cyp = H * 0.085;
    if (p.day > 0.3) {
      cx.globalAlpha = Math.min(1, (p.day - 0.3) / 0.4);
      var rg = cx.createRadialGradient(cxp, cyp, 6, cxp, cyp, 64);
      rg.addColorStop(0, "rgba(255,236,170,0.8)");
      rg.addColorStop(1, "rgba(255,236,170,0)");
      cx.fillStyle = rg; cx.fillRect(cxp - 64, cyp - 64, 128, 128);
      cx.fillStyle = "#FFE9A8";
      cx.beginPath(); cx.arc(cxp, cyp, 24, 0, 6.29); cx.fill();
    } else {
      cx.globalAlpha = Math.min(1, (0.3 - p.day) / 0.25);
      cx.fillStyle = "#EDEBE0";
      cx.beginPath(); cx.arc(cxp, cyp, 20, 0, 6.29); cx.fill();
      cx.fillStyle = "rgba(60,60,80,0.14)";
      cx.beginPath(); cx.arc(cxp - 6, cyp - 3, 5, 0, 6.29); cx.fill();
      cx.beginPath(); cx.arc(cxp + 5, cyp + 6, 3, 0, 6.29); cx.fill();
    }
    cx.globalAlpha = 1;

    var i2, c;
    if (p.day < 0.45) {                          // stars, twinkling
      for (i2 = 0; i2 < 22; i2++) {
        cx.globalAlpha = (0.45 - p.day) * 1.8 * (0.5 + 0.5 * Math.sin(t * 2 + i2 * 1.7));
        cx.fillStyle = "#FFF4E4";
        cx.fillRect((i2 * 727) % W, (i2 * 331) % (H * 0.4), 2, 2);
      }
      cx.globalAlpha = 1;
    }
    for (i2 = 0; i2 < clouds.length; i2++) {     // drifting clouds (day)
      c = clouds[i2];
      c.x += c.v;
      if (c.x > W + 90) c.x = -90;
      cx.globalAlpha = 0.1 + 0.45 * p.day;
      cx.fillStyle = "#FFFFFF";
      cx.beginPath();
      cx.arc(c.x, c.y * H, c.s, 0, 6.29);
      cx.arc(c.x + c.s * 0.9, c.y * H + 4, c.s * 0.7, 0, 6.29);
      cx.arc(c.x - c.s * 0.9, c.y * H + 5, c.s * 0.66, 0, 6.29);
      cx.fill();
    }
    cx.globalAlpha = 1;
    // rolling hills behind the pile
    cx.fillStyle = "rgba(60,50,70," + (0.10 + 0.06 * (1 - p.day)) + ")";
    cx.beginPath(); cx.ellipse(W * 0.2, H * 1.02, W * 0.55, H * 0.16, 0, 3.14, 6.29); cx.fill();
    cx.fillStyle = "rgba(60,50,70," + (0.16 + 0.08 * (1 - p.day)) + ")";
    cx.beginPath(); cx.ellipse(W * 0.85, H * 1.04, W * 0.6, H * 0.14, 0, 3.14, 6.29); cx.fill();
    // pollen motes by day, fireflies by night
    for (i2 = 0; i2 < motes.length; i2++) {
      c = motes[i2];
      c.y -= c.v; c.x += Math.sin(t * 0.7 + c.ph) * 0.3;
      if (c.y < -6) { c.y = H + 6; c.x = (c.x + 97) % W; }
      cx.globalAlpha = 0.16 * p.day;
      cx.fillStyle = "#FFF4D6";
      cx.beginPath(); cx.arc(c.x % W, c.y, 2.4, 0, 6.29); cx.fill();
    }
    if (p.day < 0.4) {
      for (i2 = 0; i2 < flies.length; i2++) {
        c = flies[i2];
        var fx2 = (c.x + Math.sin(t * 0.5 + c.ph) * 40) % W;
        var fy2 = (c.y + Math.cos(t * 0.35 + c.ph * 2) * 30) % (H * 0.8);
        cx.globalAlpha = (0.4 - p.day) * 2 * (0.35 + 0.65 * Math.abs(Math.sin(t * 1.6 + c.ph * 3)));
        cx.fillStyle = "#D8F0A0";
        cx.beginPath(); cx.arc(fx2, fy2, 2.6, 0, 6.29); cx.fill();
      }
    }
    cx.globalAlpha = 1;
    // the glass jar: translucent side walls with a gloss line
    var gw = Math.max(14, W * 0.035);
    var lg = cx.createLinearGradient(0, 0, gw, 0);
    lg.addColorStop(0, "rgba(255,255,255,0.20)");
    lg.addColorStop(1, "rgba(255,255,255,0)");
    cx.fillStyle = lg; cx.fillRect(0, DANGER, gw, H - DANGER);
    lg = cx.createLinearGradient(W, 0, W - gw, 0);
    lg.addColorStop(0, "rgba(255,255,255,0.20)");
    lg.addColorStop(1, "rgba(255,255,255,0)");
    cx.fillStyle = lg; cx.fillRect(W - gw, DANGER, gw, H - DANGER);
    cx.fillStyle = "rgba(255,255,255,0.35)";
    cx.fillRect(3, DANGER, 2, H - DANGER);
    cx.fillRect(W - 5, DANGER, 2, H - DANGER);
    cx.fillStyle = "rgba(90,76,92,0.12)";
    cx.fillRect(0, H - FLOOR, W, FLOOR);
    // danger line
    var hot = dangerT > 0.3;
    cx.strokeStyle = hot
      ? "rgba(224,90,80," + (0.5 + 0.4 * Math.sin(t * 12)) + ")"
      : (p.day < 0.4 ? "rgba(255,244,228,0.35)" : "rgba(90,76,92,0.25)");
    cx.lineWidth = hot ? 3 : 2;
    cx.setLineDash([10, 8]);
    cx.beginPath(); cx.moveTo(0, DANGER); cx.lineTo(W, DANGER); cx.stroke();
    cx.setLineDash([]);
    // evolution strip along the bottom
    var sw = Math.min(W / (TIERS + 2), 30), sx = (W - sw * TIERS) / 2;
    for (var i = 0; i < TIERS; i++) {
      var im = IMGS[i];
      if (im && im.complete && im.naturalWidth) {
        cx.globalAlpha = 0.55;
        cx.drawImage(im, sx + i * sw, H - FLOOR - sw - 4, sw - 3, sw - 3);
        cx.globalAlpha = 1;
      }
    }
  }
  function ballImg(b2) {
    var im = IMGS[b2.tier];
    if (im && im.complete && im.naturalWidth) {
      cx.drawImage(im, b2.x - b2.r, b2.y - b2.r, b2.r * 2, b2.r * 2);
    } else {
      cx.fillStyle = TCOL[b2.tier];
      cx.beginPath(); cx.arc(b2.x, b2.y, b2.r, 0, 6.29); cx.fill();
    }
  }
  function drawTitle() {
    var size = Math.min(W * 0.14, 58);
    var by = H * 0.32 + Math.sin(t * 1.8) * 5;
    cx.textAlign = "center";
    cx.font = "900 " + size + "px -apple-system,'Segoe UI',Roboto,sans-serif";
    cx.fillStyle = "rgba(58,44,52,0.25)";
    cx.fillText("CRITTER", W / 2 + 3, by + 3);
    cx.fillText("DROP", W / 2 + 3, by + size * 1.04 + 3);
    cx.fillStyle = "#5A4C5C";
    cx.fillText("CRITTER", W / 2, by);
    cx.fillStyle = "#E0806A";
    cx.fillText("DROP", W / 2, by + size * 1.04);
    cx.font = "700 " + Math.min(W * 0.042, 17) + "px sans-serif";
    cx.fillStyle = "rgba(90,76,92,0.8)";
    cx.fillText("match two of a kind — grow the biggest critter", W / 2, by + size * 1.04 + 34);
    if (best > 0) cx.fillText("BEST  " + best, W / 2, by + size * 1.04 + 62);
  }

  function frame() {
    requestAnimationFrame(frame);
    if (paused) return;
    t += 1 / 60;
    if (dropCd > 0) dropCd--;
    if (chainT > 0) { chainT--; if (chainT === 0) { chainN = 0; setScore(); } }

    if (state === "play") {
      for (var bi = 0; bi < balls.length; bi++) balls[bi].py = balls[bi].y;
      physics(); checkDanger();
    }
    document.getElementById("gift").style.display = giftVisible() ? "block" : "none";

    bg();
    var i;
    for (i = 0; i < balls.length; i++) ballImg(balls[i]);

    if (state === "play") {
      // aim preview: current ball at spawn height + guide line
      var r = radius(curTier);
      var ax = Math.max(WALL + r, Math.min(W - WALL - r, aimX));
      if (dropCd <= 0) {
        cx.globalAlpha = 0.9;
        var im = IMGS[curTier];
        if (im && im.complete && im.naturalWidth) {
          cx.drawImage(im, ax - r, DANGER * 0.55 - r, r * 2, r * 2);
        }
        cx.globalAlpha = 0.25;
        cx.strokeStyle = "#5A4C5C"; cx.lineWidth = 2; cx.setLineDash([4, 10]);
        cx.beginPath(); cx.moveTo(ax, DANGER * 0.55 + r); cx.lineTo(ax, H - FLOOR); cx.stroke();
        cx.setLineDash([]); cx.globalAlpha = 1;
      }
      // next preview
      var nr = 20;
      cx.font = "700 12px sans-serif"; cx.textAlign = "center";
      cx.fillStyle = "rgba(90,76,92,0.7)";
      cx.fillText("NEXT", W - 34, 78);
      var nim = IMGS[nextTier];
      if (nim && nim.complete && nim.naturalWidth) {
        cx.drawImage(nim, W - 34 - nr, 86, nr * 2, nr * 2);
      }
    }

    for (i = rings.length - 1; i >= 0; i--) {
      var rg = rings[i];
      rg.r += (rg.max - rg.r) * 0.18; rg.a -= 0.045;
      if (rg.a <= 0) { rings.splice(i, 1); continue; }
      cx.globalAlpha = rg.a; cx.strokeStyle = rg.col; cx.lineWidth = 3;
      cx.beginPath(); cx.arc(rg.x, rg.y, rg.r, 0, 6.29); cx.stroke();
      cx.globalAlpha = 1;
    }
    for (i = particles.length - 1; i >= 0; i--) {
      var p = particles[i];
      p.x += p.vx; p.y += p.vy; p.vy += 0.15; p.a -= 0.02;
      if (p.a <= 0) { particles.splice(i, 1); continue; }
      cx.globalAlpha = p.a; cx.fillStyle = p.col;
      cx.fillRect(p.x, p.y, 5, 5); cx.globalAlpha = 1;
    }
    for (i = floats.length - 1; i >= 0; i--) {
      var fl = floats[i];
      fl.y -= 1.2; fl.a -= 0.018;
      fl.s = fl.s ? fl.s + (1 - fl.s) * 0.15 : 1;
      if (fl.a <= 0) { floats.splice(i, 1); continue; }
      cx.globalAlpha = Math.min(1, fl.a);
      cx.font = "800 " + Math.round(26 * fl.s) + "px sans-serif"; cx.textAlign = "center";
      cx.strokeStyle = "rgba(58,44,52,0.5)"; cx.lineWidth = 4;
      cx.strokeText(fl.txt, fl.x, fl.y);
      cx.fillStyle = "#FFF7E8";
      cx.fillText(fl.txt, fl.x, fl.y);
      cx.globalAlpha = 1;
    }
    if (state === "title") drawTitle();

    var vg = cx.createRadialGradient(W / 2, H / 2, Math.min(W, H) * 0.45, W / 2, H / 2, Math.max(W, H) * 0.75);
    vg.addColorStop(0, "rgba(60,40,30,0)");
    vg.addColorStop(1, "rgba(60,40,30,0.12)");
    cx.fillStyle = vg; cx.fillRect(0, 0, W, H);
  }

  /* ---------------------------------------------------------------- input */
  function px(e) { return (e.touches && e.touches[0]) ? e.touches[0].clientX : e.clientX; }
  cv.addEventListener("pointerdown", function (e) {
    e.preventDefault();
    ensureAC();
    if (state === "title") { state = "play"; document.getElementById("hint").style.display = "none"; }
    if (state !== "play") return;
    aiming = true; aimX = px(e);
  });
  cv.addEventListener("pointermove", function (e) {
    if (aiming) aimX = px(e);
  });
  window.addEventListener("pointerup", function () {
    if (aiming && state === "play") dropBall();
    aiming = false;
  });
  window.addEventListener("keydown", function (e) {
    if (e.code === "ArrowLeft") { aimX -= 24; }
    if (e.code === "ArrowRight") { aimX += 24; }
    if (e.code === "Space" || e.code === "Enter") {
      e.preventDefault();
      if (state === "title") { state = "play"; document.getElementById("hint").style.display = "none"; return; }
      if (state === "play") dropBall();
    }
  });
  document.getElementById("again").addEventListener("click", function () {
    click();
    document.getElementById("over").style.display = "none";
    state = "play"; reset();
    maybeInterstitial();
  });
  document.getElementById("revive").addEventListener("click", function () {
    click();
    var a = bridgeAds();
    if (a && rewardedAvailable() && !reviveUsed) {
      adPurpose = "revive"; adGotReward = false; a.showRewarded();
    }
  });
  document.getElementById("gift").addEventListener("click", function () {
    click();
    var a = bridgeAds();
    if (a && giftVisible()) {
      adPurpose = "gift"; adGotReward = false; a.showRewarded();
    }
  });
  document.getElementById("share").addEventListener("click", function () {
    click();
    var txt = "🫙 Critter Drop — I merged my way to " + score + "!\n" +
      "One thumb, no download → tsjenn.github.io/Sj/play7/";
    if (navigator.clipboard) navigator.clipboard.writeText(txt).catch(function () {});
    this.textContent = "✓ Copied!";
    var b = this; setTimeout(function () { b.textContent = "📋 Share my score"; }, 1500);
  });

  sdk(function () {
    if (YT && YT.system) {
      YT.system.onPause && YT.system.onPause(function () { paused = true; });
      YT.system.onResume && YT.system.onResume(function () { paused = false; });
    }
  });

  reset();
  frame();
  sdk(function () { YT && YT.game && YT.game.gameReady && YT.game.gameReady(); });

  // Playgama Bridge (bundled only in the Playgama build; absent elsewhere).
  if (window.bridge && typeof window.bridge.initialize === "function") {
    window.bridge.initialize().then(function () {
      sdk(function () { window.bridge.platform.sendMessage("game_ready"); });
      sdk(initAds);
    }).catch(function () {});
  }

  window.DEV = {
    state: function () { return { state: state, score: score, best: best, balls: balls.length,
      tiers: balls.map(function (b2) { return b2.tier; }), loaded: loaded, paused: paused,
      reviveUsed: reviveUsed, overs: overs, dangerT: Math.round(dangerT * 100) / 100,
      nextTier: nextTier, giftReady: giftVisible() }; },
    dropAt: function (x, tier) {
      if (state === "title") { state = "play"; document.getElementById("hint").style.display = "none"; }
      if (tier !== undefined) curTier = tier;
      aimX = x; dropCd = 0; dropBall();
    },
    spawn: spawn,
    forceOver: gameOver,
    reset: function () { document.getElementById("over").style.display = "none"; state = "play"; reset(); }
  };
})();
