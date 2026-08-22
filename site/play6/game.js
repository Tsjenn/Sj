/* Critter Tower — one-thumb stacker in the Wildhaven world.
   Self-contained: no external requests; ytgame SDK hooks are optional
   (Playables-ready) with localStorage fallback. */
(function () {
  "use strict";

  var CRITTERS = ["flufftail", "pebblit", "aquaphin", "emberling", "mossback",
    "bubbletide", "zephyrix", "cinderpup", "glimmerwing", "nocturnix"];
  var COLORS = { flufftail: "#A2D286", pebblit: "#B8B4C0", aquaphin: "#84C0E4",
    emberling: "#F49E68", mossback: "#9EB87A", bubbletide: "#A6DADA",
    zephyrix: "#F8DC7C", cinderpup: "#E0806A", glimmerwing: "#C0A0E8",
    nocturnix: "#7076AA" };

  var cv = document.getElementById("c"), cx = cv.getContext("2d");
  var W = 0, H = 0, DPR = Math.min(window.devicePixelRatio || 1, 2);
  function resize() {
    W = window.innerWidth; H = window.innerHeight;
    cv.width = W * DPR; cv.height = H * DPR;
    cx.setTransform(DPR, 0, 0, DPR, 0, 0);
  }
  window.addEventListener("resize", resize);
  resize();

  /* ---------------------------------------------------- ytgame (optional) */
  var YT = typeof window.ytgame === "object" ? window.ytgame : null;
  function sdk(fn) { try { return fn && fn(); } catch (e) {} }

  /* --------------------------------------------------------------- audio */
  var AC = null, master = null, noiseBuf = null, muted = false;
  try { muted = localStorage.getItem("critter-tower-muted") === "1"; } catch (e) {}
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
  /* sfx — layered, musical (A-minor pentatonic ladder for combos) */
  var PENTA = [220, 261.63, 293.66, 329.63, 392, 440, 523.25, 587.33, 659.25, 783.99, 880, 1046.5];
  function chime(combo) {
    ensureAC(); if (!AC) return;
    var f = PENTA[Math.min(combo + 3, PENTA.length - 1)];
    tone(f, 0, 0.28, "triangle", 0.16);
    tone(f * 2, 0, 0.2, "sine", 0.07);
    tone(f * 3, AC.currentTime + 0.05, 0.14, "sine", 0.03);
  }
  function crunch() {
    ensureAC(); if (!AC) return;
    noise(0, 0.09, 900, 1.4, 0.22);
    tone(80, 0, 0.14, "sine", 0.26);
  }
  function womp() {
    ensureAC(); if (!AC) return;
    tone(240, 0, 0.55, "sine", 0.24, 55);
    noise(AC.currentTime + 0.04, 0.3, 300, 0.8, 0.1);
  }
  function whoosh() {
    ensureAC(); if (!AC) return;
    noise(0, 0.14, 1800, 0.6, 0.05);
  }
  function fanfare() {
    ensureAC(); if (!AC) return;
    [523.25, 659.25, 783.99, 1046.5].forEach(function (f, i) {
      tone(f, AC.currentTime + i * 0.09, 0.3, "triangle", 0.13);
    });
  }
  function milestoneSfx() {
    ensureAC(); if (!AC) return;
    [392, 493.88, 587.33, 783.99].forEach(function (f, i) {
      tone(f, AC.currentTime + i * 0.06, 0.22, "triangle", 0.12);
      tone(f * 2, AC.currentTime + i * 0.06, 0.16, "sine", 0.045);
    });
  }
  function click() { ensureAC(); tone(620, 0, 0.05, "square", 0.04); }

  /* music — calm generative loop, Am / F / C / G with pentatonic plucks */
  var PROG = [[220, 261.63, 329.63], [174.61, 220, 261.63],
              [130.81, 164.81, 196], [196, 246.94, 293.66]];
  var POOL = [440, 523.25, 587.33, 659.25, 783.99, 880];
  var MELO = [[0, -1, 2, -1, 3, -1, 2, -1], [1, -1, 0, -1, -1, 2, -1, -1],
              [3, -1, 4, -1, 3, -1, 2, -1], [1, -1, 2, -1, 0, -1, -1, -1]];
  var STEP = 60 / 84 / 2, musicAt = 0, musicStep = 0, musicTimer = null;
  function startMusic() {
    if (musicTimer || !AC) return;
    musicAt = AC.currentTime + 0.1;
    musicTimer = setInterval(function () {
      if (!AC || paused) return;
      while (musicAt < AC.currentTime + 0.9) {
        var bar = Math.floor(musicStep / 8) % 4, st = musicStep % 8;
        if (st === 0) {
          PROG[bar].forEach(function (f) {
            tone(f, musicAt, STEP * 8 * 0.95, "sine", 0.028);
          });
        }
        var m = MELO[bar][st];
        if (m >= 0) tone(POOL[m], musicAt, 0.42, "triangle", 0.05);
        musicAt += STEP; musicStep++;
      }
    }, 220);
  }
  document.getElementById("mute").textContent = muted ? "🔇" : "🔊";
  document.getElementById("mute").addEventListener("click", function () {
    muted = !muted;
    try { localStorage.setItem("critter-tower-muted", muted ? "1" : "0"); } catch (e) {}
    if (master) master.gain.value = muted ? 0 : 1;
    this.textContent = muted ? "🔇" : "🔊";
  });

  /* -------------------------------------------------------------- sprites */
  var IMGS = {}, loaded = 0;
  CRITTERS.forEach(function (n) {
    var im = new Image();
    im.onload = function () { loaded++; };
    im.src = "img/" + n + ".png";
    IMGS[n] = im;
  });

  /* ---------------------------------------------------------------- state */
  var BLOCK_H = 46;
  var baseW, stack, moving, debris, particles, floats, rings, clouds;
  var score = 0, best = 0, combo = 0, state = "title";
  var t = 0, shake = 0, cam = 0, camTarget = 0, paused = false, landT = 0;

  try { best = +(localStorage.getItem("critter-tower-best") || 0); } catch (e) {}
  sdk(function () {
    if (YT && YT.game && YT.game.loadData) {
      YT.game.loadData().then(function (d) {
        try { var j = JSON.parse(d || "{}"); if (j.best > best) best = j.best; } catch (e) {}
      });
    }
  });
  function saveBest() {
    try { localStorage.setItem("critter-tower-best", "" + best); } catch (e) {}
    sdk(function () { YT && YT.game && YT.game.saveData && YT.game.saveData(JSON.stringify({ best: best })); });
  }

  function reset() {
    baseW = Math.min(W * 0.62, 300);
    stack = [{ x: W / 2, w: baseW, n: 0 }];
    debris = []; particles = []; floats = []; rings = [];
    score = 0; combo = 0; cam = 0; camTarget = 0; landT = 0;
    reviveUsed = false;
    newMoving();
    setScore();
  }
  function newMoving() {
    var top = stack[stack.length - 1];
    // gentle start, slow ramp — long runs are the fun, not instant panic
    var sp = score < 3 ? 0.9 + score * 0.06 : 1.08 + Math.min(score * 0.03, 1.2);
    moving = { w: top.w, n: stack.length % CRITTERS.length, phase: Math.random() * 6.28,
      speed: sp, drop: 0, vy: 6, dropping: false };
  }
  // forgiving early, honest later: the perfect window tightens as you climb
  function perfectWin() { return score < 8 ? 15 : score < 20 ? 11 : score < 35 ? 9 : 7; }
  function rowY(i) { return H * 0.78 - i * BLOCK_H + cam; }

  function setScore() {
    document.getElementById("score").textContent = score;
    var cEl = document.getElementById("combo");
    cEl.textContent = combo > 1 ? "PERFECT ×" + combo : "";
    cEl.style.opacity = combo > 1 ? 1 : 0;
  }

  /* ----------------------------------------------------------------- drop */
  function movingX() {
    var amp = (W - moving.w) / 2 - 8;
    return W / 2 + Math.sin(t * moving.speed + moving.phase) * Math.max(amp, 30);
  }
  function drop() {
    if (state === "title") { state = "play"; document.getElementById("hint").style.display = "none"; }
    if (state !== "play" || moving.dropping) return;
    ensureAC();
    whoosh();
    moving.dropping = true;
    moving.fx = movingX();
  }
  function land() {
    var top = stack[stack.length - 1];
    var x = moving.fx, w = moving.w;
    var overlap = Math.min(x + w / 2, top.x + top.w / 2) - Math.max(x - w / 2, top.x - top.w / 2);
    if (overlap <= 4) {                                   // clean miss — topple
      debris.push({ x: x, y: rowY(stack.length) - cam, w: w, n: moving.n, vy: 0, vr: (x > top.x ? 1 : -1) * 0.06, r: 0 });
      gameOver();
      return;
    }
    var off = x - top.x;
    if (Math.abs(off) < perfectWin()) {                   // PERFECT
      combo++;
      x = top.x;
      var y0 = rowY(stack.length) - cam;
      if (combo > 0 && combo % 5 === 0) {                 // every 5th: full regrow
        w = baseW;
        milestoneSfx();
        rings.push({ x: x, y: y0, r: 12, max: 150, a: 0.9, col: "#FFE9A8" });
        burst(x, y0, "#FFE9A8", 30);
        floats.push({ x: W / 2, y: y0 - 44, txt: "TOWER POWER!", a: 1, s: 1.7 });
      } else {
        w = Math.min(w + 6, baseW);                       // reward: regrow
        chime(combo);
        rings.push({ x: x, y: y0, r: 10, max: 70, a: 0.8, col: "#FFC46B" });
        burst(x, y0, "#FFC46B", 18);
        floats.push({ x: W / 2, y: y0 - 40, txt: "PERFECT!", a: 1, s: 1.4 });
      }
    } else {                                              // slice
      combo = 0;
      var sliceW = w - overlap;
      var sliceX = off > 0 ? x + overlap / 2 : x - overlap / 2;
      debris.push({ x: sliceX + (off > 0 ? sliceW / 2 : -sliceW / 2), y: rowY(stack.length) - cam,
        w: sliceW, n: moving.n, vy: -2, vr: (off > 0 ? 1 : -1) * 0.05, r: 0 });
      w = overlap;
      x = off > 0 ? x - sliceW / 2 : x + sliceW / 2;
      crunch();
      shake = 7;
    }
    stack.push({ x: x, w: w, n: moving.n });
    landT = 1;
    score++;
    camTarget = Math.max(0, (stack.length - 4) * BLOCK_H);
    setScore();
    if (w < 26) { gameOver(); return; }
    newMoving();
  }

  function gameOver() {
    state = "over";
    overs++;
    womp(); shake = 12;
    if (score > best && score > 0) {
      best = score; saveBest();
      fanfare();
      burst(W / 2, H * 0.4, "#FFC46B", 26);
      burst(W / 2, H * 0.4, "#A2D286", 26);
      burst(W / 2, H * 0.4, "#84C0E4", 26);
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
  // The Bridge SDK ships only in the Playgama zip; everywhere else these
  // are inert: no button, no ad calls. Reward is granted ONLY on the
  // SDK's "rewarded" state — an early-closed ad revives nothing.
  var reviveUsed = false, adGotReward = false, lastInterstitial = 0, overs = 0;
  function bridgeAds() {
    var b = window.bridge;
    return (b && b.advertisement) ? b.advertisement : null;
  }
  function rewardedAvailable() {
    try { var a = bridgeAds(); return !!(a && a.isRewardedSupported); } catch (e) { return false; }
  }
  function revive() {
    reviveUsed = true;
    var top = stack[stack.length - 1];
    top.w = Math.max(top.w, baseW * 0.55);       // enough width to keep playing
    document.getElementById("over").style.display = "none";
    state = "play";
    newMoving();
  }
  function initAds() {
    var a = bridgeAds();
    if (!a || typeof a.on !== "function") return;
    a.on("rewarded_state_changed", function (s) {
      if (s === "opened") { paused = true; }
      if (s === "rewarded") { adGotReward = true; }
      if (s === "closed" || s === "failed") {
        paused = false;
        if (adGotReward) { adGotReward = false; revive(); }
      }
    });
    a.on("interstitial_state_changed", function (s) {
      if (s === "opened") { paused = true; }
      if (s === "closed" || s === "failed") { paused = false; }
    });
  }
  function maybeInterstitial() {
    // natural pause: between runs, from the 2nd topple on, >=60s apart
    try {
      var a = bridgeAds();
      if (!a || !a.isInterstitialSupported) return;
      var now = Date.now();
      if (overs >= 2 && now - lastInterstitial > 60000) {
        lastInterstitial = now;
        a.showInterstitial();
      }
    } catch (e) {}
  }

  function burst(x, y, col, n) {
    for (var i = 0; i < n; i++) {
      var a = Math.random() * 6.28, s = 2 + Math.random() * 3.5;
      particles.push({ x: x, y: y, vx: Math.cos(a) * s, vy: Math.sin(a) * s - 2, a: 1, col: col });
    }
  }

  /* ----------------------------------------------------------------- draw */
  function shade(hex, f) { return mix(hex, f > 0 ? "#FFFFFF" : "#000000", Math.abs(f)); }
  function slab(x, y, w, n, withCritter) {
    var name = CRITTERS[n], col = COLORS[name];
    cx.fillStyle = "rgba(20,16,24,0.12)";
    rr(x - w / 2 + 5, y + 7, w, BLOCK_H - 6, 10); cx.fill();
    cx.fillStyle = "rgba(20,16,24,0.16)";
    rr(x - w / 2 + 3, y + 4, w, BLOCK_H - 6, 10); cx.fill();
    var g = cx.createLinearGradient(0, y, 0, y + BLOCK_H - 6);
    g.addColorStop(0, shade(col, 0.22));
    g.addColorStop(0.45, col);
    g.addColorStop(1, shade(col, -0.14));
    cx.fillStyle = g;
    rr(x - w / 2, y, w, BLOCK_H - 6, 10); cx.fill();
    cx.strokeStyle = "rgba(48,40,48,0.3)"; cx.lineWidth = 2;
    rr(x - w / 2, y, w, BLOCK_H - 6, 10); cx.stroke();
    cx.fillStyle = "rgba(255,255,255,0.3)";
    rr(x - w / 2 + 4, y + 3, w - 8, 9, 5); cx.fill();
    if (withCritter) {
      var im = IMGS[name], s = Math.min(w * 0.75, 84);
      if (im.complete && im.naturalWidth) cx.drawImage(im, x - s / 2, y - s + 8, s, s);
    }
  }
  function rr(x, y, w, h, r) {
    cx.beginPath();
    cx.moveTo(x + r, y);
    cx.arcTo(x + w, y, x + w, y + h, r); cx.arcTo(x + w, y + h, x, y + h, r);
    cx.arcTo(x, y + h, x, y, r); cx.arcTo(x, y, x + w, y, r);
    cx.closePath();
  }

  var SKY = [["#8ED0F0", "#FDF3E0"], ["#F7B267", "#FBE8D0"], ["#5A5E9E", "#2B3054"],
             ["#20243A", "#0E1020"]];
  var DAYNESS = [1, 0.75, 0.2, 0.02];
  function skyPhase() {
    var ph = (score % 40) / 40 * SKY.length;
    var i = Math.floor(ph) % SKY.length, j = (i + 1) % SKY.length, f = ph - Math.floor(ph);
    return { i: i, j: j, f: f, day: DAYNESS[i] + (DAYNESS[j] - DAYNESS[i]) * f,
      bottom: mix(SKY[i][1], SKY[j][1], f) };
  }
  function sky(p) {
    var g = cx.createLinearGradient(0, 0, 0, H);
    g.addColorStop(0, mix(SKY[p.i][0], SKY[p.j][0], p.f));
    g.addColorStop(1, p.bottom);
    cx.fillStyle = g; cx.fillRect(0, 0, W, H);

    if (p.day < 0.45) {                                   // stars, twinkling
      for (var s = 0; s < 26; s++) {
        var sx = (s * 727 % W), sy = (s * 331 % (H * 0.55));
        cx.globalAlpha = (0.45 - p.day) * 2 * (0.55 + 0.45 * Math.sin(t * 2 + s * 1.7));
        cx.fillStyle = "#FFF4E4";
        cx.fillRect(sx, sy, 2, 2);
      }
      cx.globalAlpha = 1;
    }
    // sun / moon crossfade with the day cycle
    var cxp = W * 0.8, cyp = H * 0.14;
    if (p.day > 0.3) {
      cx.globalAlpha = Math.min(1, (p.day - 0.3) / 0.4);
      var rg = cx.createRadialGradient(cxp, cyp, 8, cxp, cyp, 80);
      rg.addColorStop(0, "rgba(255,236,170,0.85)");
      rg.addColorStop(1, "rgba(255,236,170,0)");
      cx.fillStyle = rg; cx.fillRect(cxp - 80, cyp - 80, 160, 160);
      cx.fillStyle = "#FFE9A8";
      cx.beginPath(); cx.arc(cxp, cyp, 30, 0, 6.29); cx.fill();
      cx.globalAlpha = 1;
    } else {
      cx.globalAlpha = Math.min(1, (0.3 - p.day) / 0.25);
      cx.fillStyle = "#EDEBE0";
      cx.beginPath(); cx.arc(cxp, cyp, 24, 0, 6.29); cx.fill();
      cx.fillStyle = "rgba(60,60,80,0.14)";
      cx.beginPath(); cx.arc(cxp - 8, cyp - 4, 6, 0, 6.29); cx.fill();
      cx.beginPath(); cx.arc(cxp + 6, cyp + 8, 4, 0, 6.29); cx.fill();
      cx.globalAlpha = 1;
    }
    // drifting clouds (fade out at night)
    var ca = 0.14 + 0.5 * p.day;
    for (var c = 0; c < clouds.length; c++) {
      var cl = clouds[c];
      cl.x += cl.v;
      if (cl.x > W + 90) cl.x = -90;
      cx.globalAlpha = ca;
      cx.fillStyle = "#FFFFFF";
      cx.beginPath();
      cx.arc(cl.x, cl.y, cl.s, 0, 6.29);
      cx.arc(cl.x + cl.s * 0.9, cl.y + 4, cl.s * 0.75, 0, 6.29);
      cx.arc(cl.x - cl.s * 0.9, cl.y + 5, cl.s * 0.7, 0, 6.29);
      cx.fill();
      cx.globalAlpha = 1;
    }
    // parallax hills at the horizon
    var camf = cam * 0.06;
    cx.fillStyle = mix(p.bottom, "#000000", 0.1);
    cx.beginPath();
    cx.ellipse(W * 0.22, H * 0.97 + camf, W * 0.5, H * 0.15, 0, 3.14, 6.29);
    cx.fill();
    cx.fillStyle = mix(p.bottom, "#000000", 0.18);
    cx.beginPath();
    cx.ellipse(W * 0.85, H * 1.0 + camf * 1.4, W * 0.55, H * 0.13, 0, 3.14, 6.29);
    cx.fill();
  }
  function mix(a, b, f) {
    var pa = [parseInt(a.slice(1, 3), 16), parseInt(a.slice(3, 5), 16), parseInt(a.slice(5, 7), 16)];
    var pb = [parseInt(b.slice(1, 3), 16), parseInt(b.slice(3, 5), 16), parseInt(b.slice(5, 7), 16)];
    return "rgb(" + pa.map(function (v, i) { return Math.round(v + (pb[i] - v) * f); }).join(",") + ")";
  }
  function initClouds() {
    clouds = [];
    for (var i = 0; i < 4; i++) {
      clouds.push({ x: (i * 173 + 60) % Math.max(W, 320), y: H * 0.08 + i * 44,
        s: 20 + (i % 3) * 9, v: 0.12 + i * 0.05 });
    }
  }

  function drawTitle() {
    var size = Math.min(W * 0.14, 58);
    var by = H * 0.3 + Math.sin(t * 1.8) * 5;
    cx.textAlign = "center";
    cx.font = "900 " + size + "px -apple-system,'Segoe UI',Roboto,sans-serif";
    cx.fillStyle = "rgba(32,26,40,0.3)";
    cx.fillText("CRITTER", W / 2 + 3, by + 3);
    cx.fillText("TOWER", W / 2 + 3, by + size * 1.04 + 3);
    cx.fillStyle = "#FFF4E4";
    cx.fillText("CRITTER", W / 2, by);
    cx.fillStyle = "#FFC46B";
    cx.fillText("TOWER", W / 2, by + size * 1.04);
    if (best > 0) {
      cx.font = "700 " + Math.min(W * 0.045, 18) + "px sans-serif";
      cx.fillStyle = "rgba(255,244,228,0.85)";
      cx.fillText("BEST  " + best, W / 2, by + size * 1.04 + 34);
    }
  }

  function frame() {
    requestAnimationFrame(frame);
    if (paused) return;
    t += 1 / 60;
    cam += (camTarget - cam) * 0.12;
    if (shake > 0.3) shake *= 0.86; else shake = 0;
    if (landT > 0.01) landT *= 0.82; else landT = 0;

    cx.save();
    if (shake) cx.translate((Math.random() - 0.5) * shake, (Math.random() - 0.5) * shake);
    var ph = skyPhase();
    sky(ph);

    for (var i = 0; i < stack.length; i++) {
      var b = stack[i];
      var squash = (i === stack.length - 1 && landT > 0) ? landT : 0;
      if (squash) {
        var cyc = rowY(i) + (BLOCK_H - 6);
        cx.save();
        cx.translate(b.x, cyc);
        cx.scale(1 + 0.2 * squash, 1 - 0.26 * squash);
        cx.translate(-b.x, -cyc);
      }
      slab(b.x, rowY(i), b.w, b.n, i === stack.length - 1);
      if (squash) cx.restore();
    }
    if (state === "play" && moving) {
      var y;
      if (moving.dropping) {
        moving.vy += 2.4;
        moving.drop += moving.vy;
        y = H * 0.2 + moving.drop;
        var targetY = rowY(stack.length);
        if (y >= targetY) { land(); }
        else slab(moving.fx, y, moving.w, moving.n, true);
      } else {
        slab(movingX(), H * 0.2, moving.w, moving.n, true);
      }
    }
    for (i = debris.length - 1; i >= 0; i--) {
      var d = debris[i];
      d.vy += 0.5; d.y += d.vy; d.r += d.vr;
      cx.save(); cx.translate(d.x, d.y); cx.rotate(d.r);
      slab(0, 0, d.w, d.n, false);
      cx.restore();
      if (d.y > H + 80) debris.splice(i, 1);
    }
    for (i = rings.length - 1; i >= 0; i--) {
      var rg2 = rings[i];
      rg2.r += (rg2.max - rg2.r) * 0.18; rg2.a -= 0.045;
      if (rg2.a <= 0) { rings.splice(i, 1); continue; }
      cx.globalAlpha = rg2.a; cx.strokeStyle = rg2.col; cx.lineWidth = 3;
      cx.beginPath(); cx.arc(rg2.x, rg2.y + BLOCK_H / 2, rg2.r, 0, 6.29); cx.stroke();
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
      cx.font = "800 " + Math.round(28 * fl.s) + "px sans-serif"; cx.textAlign = "center";
      cx.strokeStyle = "rgba(32,26,40,0.5)"; cx.lineWidth = 4;
      cx.strokeText(fl.txt, fl.x, fl.y);
      cx.fillStyle = "#FFF4E4";
      cx.fillText(fl.txt, fl.x, fl.y);
      cx.globalAlpha = 1;
    }
    if (state === "title") drawTitle();

    // soft vignette
    var vg = cx.createRadialGradient(W / 2, H / 2, Math.min(W, H) * 0.45, W / 2, H / 2, Math.max(W, H) * 0.75);
    vg.addColorStop(0, "rgba(10,8,16,0)");
    vg.addColorStop(1, "rgba(10,8,16,0.16)");
    cx.fillStyle = vg; cx.fillRect(0, 0, W, H);
    cx.restore();
  }

  /* ---------------------------------------------------------------- input */
  function onTap(e) { e.preventDefault(); if (state !== "over") drop(); }
  cv.addEventListener("pointerdown", onTap);
  window.addEventListener("keydown", function (e) {
    if (e.code === "Space" || e.code === "Enter") { e.preventDefault(); if (state !== "over") drop(); }
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
    if (a && rewardedAvailable() && !reviveUsed) { adGotReward = false; a.showRewarded(); }
  });
  document.getElementById("share").addEventListener("click", function () {
    click();
    var txt = "🏗️ Critter Tower — I stacked " + score + " critters high!\n" +
      "One thumb, no download → tsjenn.github.io/Sj/play6/";
    if (navigator.clipboard) navigator.clipboard.writeText(txt).catch(function () {});
    this.textContent = "✓ Copied!";
    var b = this; setTimeout(function () { b.textContent = "📋 Share my tower"; }, 1500);
  });

  sdk(function () {
    if (YT && YT.system) {
      YT.system.onPause && YT.system.onPause(function () { paused = true; });
      YT.system.onResume && YT.system.onResume(function () { paused = false; });
    }
  });

  initClouds();
  reset();
  frame();
  sdk(function () { YT && YT.game && YT.game.gameReady && YT.game.gameReady(); });

  // Playgama Bridge (bundled only in the Playgama build; absent elsewhere).
  // Their platform requires game_ready within 30s of load.
  if (window.bridge && typeof window.bridge.initialize === "function") {
    window.bridge.initialize().then(function () {
      sdk(function () { window.bridge.platform.sendMessage("game_ready"); });
      sdk(initAds);
    }).catch(function () {});
  }

  window.DEV = {
    state: function () { return { state: state, score: score, best: best, combo: combo,
      stack: stack.length, topW: Math.round(stack[stack.length - 1].w), loaded: loaded,
      paused: paused, reviveUsed: reviveUsed, overs: overs, win: perfectWin() }; },
    drop: drop,
    topX: function () { return stack[stack.length - 1].x; },
    dropAt: function (x) {
      if (state === "title") { state = "play"; document.getElementById("hint").style.display = "none"; }
      if (state === "play" && moving && !moving.dropping) {
        moving.dropping = true; moving.fx = x; moving.drop = 9999;
      }
    },
    reset: function () { document.getElementById("over").style.display = "none"; state = "play"; reset(); }
  };
})();
