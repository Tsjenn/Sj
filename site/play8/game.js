/* Critter Beat — tap the falling critters on the beat; your taps play
   the song. Wildhaven world. Self-contained: no external requests;
   ytgame SDK hooks optional with localStorage fallback. */
(function () {
  "use strict";

  var LANES = 4;
  var LCOL = ["#A2D286", "#84C0E4", "#F49E68", "#C0A0E8"];

  var cv = document.getElementById("c"), cx = cv.getContext("2d");
  var W = 0, H = 0, DPR = Math.min(window.devicePixelRatio || 1, 2), HITY = 0;
  function resize() {
    W = window.innerWidth; H = window.innerHeight;
    cv.width = W * DPR; cv.height = H * DPR;
    cx.setTransform(DPR, 0, 0, DPR, 0, 0);
    HITY = H * 0.8;
  }
  window.addEventListener("resize", resize);
  resize();
  function laneX(l) { return (l + 0.5) * (W / LANES); }
  function laneW() { return W / LANES; }

  /* ---------------------------------------------------- ytgame (optional) */
  var YT = typeof window.ytgame === "object" ? window.ytgame : null;
  function sdk(fn) { try { return fn && fn(); } catch (e) {} }

  /* --------------------------------------------------------------- audio */
  var AC = null, master = null, muted = false;
  try { muted = localStorage.getItem("critter-beat-muted") === "1"; } catch (e) {}
  function ensureAC() {
    if (!AC) {
      try {
        AC = new (window.AudioContext || window.webkitAudioContext)();
        master = AC.createGain();
        master.gain.value = muted ? 0 : 1;
        master.connect(AC.destination);
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
  function womp() { ensureAC(); tone(220, 0, 0.6, "sine", 0.24, 50); }
  function fanfare() {
    ensureAC(); if (!AC) return;
    [523.25, 659.25, 783.99, 1046.5].forEach(function (f, i) {
      tone(f, AC.currentTime + i * 0.09, 0.3, "triangle", 0.13);
    });
  }
  function click() { ensureAC(); tone(620, 0, 0.05, "square", 0.04); }

  /* the song: backing runs by itself, MELODY notes are the tiles you tap */
  var PROG = [[220, 261.63, 329.63], [174.61, 220, 261.63],
              [130.81, 164.81, 196], [196, 246.94, 293.66]];
  var BASS = [110, 87.31, 65.41, 98];
  var NOTES = [440, 523.25, 659.25, 783.99];         // one note per lane
  var MELO = [                                        // per-bar tap patterns (lane per 8th, -1 rest)
    [0, -1, 1, -1, 2, -1, 1, -1],
    [3, -1, 2, -1, -1, 1, -1, -1],
    [0, -1, 1, 2, -1, 3, -1, 2],
    [1, -1, 0, -1, 3, -1, -1, -1]
  ];
  var bpm = 96, songBeat = 0, nextNoteAt = 0, barIdx = 0, stepIdx = 0;
  function beatDur() { return 60 / bpm; }
  function playNote(lane) { tone(NOTES[lane], 0, 0.35, "triangle", 0.14); tone(NOTES[lane] * 2, 0, 0.2, "sine", 0.05); }
  function scheduleBacking() {
    // pads + bass keep time whether or not you hit the notes
    if (!AC || paused || state !== "play") return;
    while (nextNoteAt < AC.currentTime + 0.9) {
      var bar = Math.floor(songBeat / 8) % 4, st = songBeat % 8;
      if (st === 0) {
        PROG[bar].forEach(function (f) { tone(f, nextNoteAt, beatDur() * 8 * 0.48, "sine", 0.026); });
      }
      if (st % 2 === 0) tone(BASS[bar], nextNoteAt, beatDur() * 0.9, "sine", 0.09);
      // spawn the tap tile for this melody step, arriving TRAVEL sec later
      var lane = MELO[bar][st];
      if (lane >= 0) tiles.push({ lane: lane, at: nextNoteAt + TRAVEL, hit: false, missed: false });
      nextNoteAt += beatDur();
      songBeat++;
    }
  }
  document.getElementById("mute").textContent = muted ? "🔇" : "🔊";
  document.getElementById("mute").addEventListener("click", function () {
    muted = !muted;
    try { localStorage.setItem("critter-beat-muted", muted ? "1" : "0"); } catch (e) {}
    if (master) master.gain.value = muted ? 0 : 1;
    this.textContent = muted ? "🔇" : "🔊";
  });

  /* -------------------------------------------------------------- sprites */
  var IMGS = [], loaded = 0;
  for (var li = 0; li < LANES; li++) {
    (function (n) {
      var im = new Image();
      im.onload = function () { loaded++; };
      im.src = "img/lane" + n + ".png";
      IMGS[n] = im;
    })(li);
  }

  /* ---------------------------------------------------------------- state */
  var TRAVEL = 1.6;                                   // seconds from spawn to hit line
  var tiles, particles, floats;
  var score = 0, best = 0, combo = 0, hearts = 3, shield = 0, state = "title";
  var t = 0, paused = false, fever = false;

  try { best = +(localStorage.getItem("critter-beat-best") || 0); } catch (e) {}
  sdk(function () {
    if (YT && YT.game && YT.game.loadData) {
      YT.game.loadData().then(function (d) {
        try { var j = JSON.parse(d || "{}"); if (j.best > best) best = j.best; } catch (e) {}
      });
    }
  });
  function saveBest() {
    try { localStorage.setItem("critter-beat-best", "" + best); } catch (e) {}
    sdk(function () { YT && YT.game && YT.game.saveData && YT.game.saveData(JSON.stringify({ best: best })); });
  }
  function reset() {
    tiles = []; particles = []; floats = [];
    score = 0; combo = 0; hearts = 3; shield = 0; fever = false;
    bpm = 96; songBeat = 0;
    reviveUsed = false;
    if (AC) nextNoteAt = AC.currentTime + 0.6;
    setScore(); setHearts();
  }
  function setScore() {
    document.getElementById("score").textContent = score;
    var el = document.getElementById("combo");
    el.textContent = combo > 4 ? (fever ? "🔥 FEVER ×" : "COMBO ×") + combo : "";
    el.style.opacity = combo > 4 ? 1 : 0;
  }
  function setHearts() {
    var s = "";
    for (var i = 0; i < hearts; i++) s += "❤️";
    if (shield > 0) s += " 🛡" + shield;
    document.getElementById("hearts").textContent = s;
  }

  /* ------------------------------------------------------------ judgement */
  function tileY(tl) { return AC ? HITY - (tl.at - AC.currentTime) / TRAVEL * (HITY + 80) : -100; }
  function tap(lane) {
    if (state !== "play" || !AC) return;
    var bestTile = null, bestDt = 1e9;
    for (var i = 0; i < tiles.length; i++) {
      var tl = tiles[i];
      if (tl.lane !== lane || tl.hit || tl.missed) continue;
      var dt = Math.abs(tl.at - AC.currentTime);
      if (dt < bestDt) { bestDt = dt; bestTile = tl; }
    }
    // forgiving: generous windows, tapping an empty lane costs nothing
    if (!bestTile || bestDt > 0.24) return;
    bestTile.hit = true;
    playNote(lane);
    var pts, txt;
    if (bestDt < 0.1) { pts = 2; txt = "PERFECT!"; } else { pts = 1; txt = "GOOD"; }
    combo++;
    if (combo >= 20 && !fever) { fever = true; floats.push({ x: W / 2, y: H * 0.3, txt: "🔥 FEVER!", a: 1, s: 1.8 }); }
    if (fever) pts *= 2;
    score += pts;
    if (score % 40 === 0 && bpm < 140) bpm += 4;      // the song slowly heats up
    burst(laneX(lane), HITY, LCOL[lane], bestDt < 0.1 ? 16 : 8);
    floats.push({ x: laneX(lane), y: HITY - 46, txt: txt, a: 1, s: bestDt < 0.1 ? 1.5 : 1.1 });
    setScore();
  }
  function judgeMisses() {
    if (!AC) return;
    for (var i = tiles.length - 1; i >= 0; i--) {
      var tl = tiles[i];
      if (!tl.hit && !tl.missed && AC.currentTime - tl.at > 0.24) {
        tl.missed = true;
        combo = 0; fever = false;
        if (shield > 0) {
          shield--;
          floats.push({ x: laneX(tl.lane), y: HITY - 46, txt: "🛡", a: 1, s: 1.3 });
        } else {
          hearts--;
          floats.push({ x: laneX(tl.lane), y: HITY - 46, txt: "MISS", a: 1, s: 1.2 });
          tone(140, 0, 0.18, "sine", 0.12);
        }
        setScore(); setHearts();
        if (hearts <= 0) { gameOver(); return; }
      }
      if (AC.currentTime - tl.at > 1) tiles.splice(i, 1);
    }
  }

  function gameOver() {
    state = "over";
    overs++;
    womp();
    if (score > best && score > 0) {
      best = score; saveBest();
      fanfare();
      burst(W / 2, H * 0.4, "#FFC46B", 26);
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
    hearts = 3;
    for (var i = 0; i < tiles.length; i++) tiles[i].missed = true;  // clear the wave
    tiles = [];
    if (AC) nextNoteAt = AC.currentTime + 0.6;
    setHearts();
    document.getElementById("over").style.display = "none";
    state = "play";
  }
  function giftGrant() {
    shield = 3;
    giftCdUntil = Date.now() + 90000;
    floats.push({ x: W / 2, y: H * 0.35, txt: "🛡 SHIELD ×3!", a: 1, s: 1.6 });
    fanfare();
    setHearts();
  }
  function giftVisible() {
    return (state === "play" || state === "title") &&
      rewardedAvailable() && Date.now() > giftCdUntil;
  }
  function initAds() {
    var a = bridgeAds();
    if (!a || typeof a.on !== "function") return;
    a.on("rewarded_state_changed", function (s) {
      if (s === "opened") { paused = true; }
      if (s === "rewarded") { adGotReward = true; }
      if (s === "closed" || s === "failed") {
        paused = false;
        if (AC) nextNoteAt = Math.max(nextNoteAt, AC.currentTime + 0.5);
        if (adGotReward) {
          adGotReward = false;
          if (adPurpose === "gift") { giftGrant(); } else { revive(); }
        }
      }
    });
    a.on("interstitial_state_changed", function (s) {
      if (s === "opened") { paused = true; }
      if (s === "closed" || s === "failed") {
        paused = false;
        if (AC) nextNoteAt = Math.max(nextNoteAt, AC.currentTime + 0.5);
      }
    });
  }
  function maybeInterstitial() {
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
  // stage lighting cycles with the song; fever turns everything warm
  var PHASES = [
    { top: "#241F33", bot: "#3A2E4E", glow: "#8B7CF0" },
    { top: "#1E2440", bot: "#2E4356", glow: "#84C0E4" },
    { top: "#2C1F38", bot: "#4E2E42", glow: "#E0806A" },
    { top: "#1F2C33", bot: "#2E4E44", glow: "#A2D286" }
  ];
  function bg() {
    var ph = (score % 80) / 80 * PHASES.length;
    var i = Math.floor(ph) % PHASES.length, j = (i + 1) % PHASES.length, f = ph - Math.floor(ph);
    var top = mixh(PHASES[i].top, PHASES[j].top, f), bot = mixh(PHASES[i].bot, PHASES[j].bot, f);
    if (fever) { top = mixh(top.length > 7 ? "#3A2438" : top, "#5A2E33", 0.5); bot = mixh("#4E2E42", "#7A4633", 0.5); }
    var g = cx.createLinearGradient(0, 0, 0, H);
    g.addColorStop(0, top); g.addColorStop(1, bot);
    cx.fillStyle = g; cx.fillRect(0, 0, W, H);
    // pulsing stage glow on the beat
    if (AC && state === "play") {
      var beat = (AC.currentTime % beatDur()) / beatDur();
      var pulse = Math.max(0, 1 - beat * 3);
      var rg = cx.createRadialGradient(W / 2, HITY, 10, W / 2, HITY, W * 0.7);
      rg.addColorStop(0, "rgba(255,244,228," + (0.05 + pulse * 0.07) + ")");
      rg.addColorStop(1, "rgba(255,244,228,0)");
      cx.fillStyle = rg; cx.fillRect(0, 0, W, H);
    }
    // lanes
    for (var l = 0; l < LANES; l++) {
      cx.fillStyle = "rgba(255,255,255," + (l % 2 ? 0.03 : 0.055) + ")";
      cx.fillRect(l * laneW(), 0, laneW(), H);
      cx.fillStyle = LCOL[l];
      cx.globalAlpha = 0.5;
      cx.fillRect(l * laneW() + 6, HITY + 34, laneW() - 12, 5);
      cx.globalAlpha = 1;
    }
    // hit bar
    cx.fillStyle = "rgba(255,244,228,0.16)";
    cx.fillRect(0, HITY - 34, W, 68);
    cx.fillStyle = "rgba(255,244,228,0.6)";
    cx.fillRect(0, HITY - 2, W, 4);
    // twinkles
    for (var s2 = 0; s2 < 18; s2++) {
      cx.globalAlpha = 0.25 * (0.5 + 0.5 * Math.sin(t * 2 + s2 * 1.7));
      cx.fillStyle = "#FFF4E4";
      cx.fillRect((s2 * 727) % W, (s2 * 331) % (H * 0.5), 2, 2);
    }
    cx.globalAlpha = 1;
  }
  function drawTiles() {
    var d = Math.min(laneW() * 0.72, 96);
    for (var i = 0; i < tiles.length; i++) {
      var tl = tiles[i];
      if (tl.hit || tl.missed) continue;
      var y = tileY(tl);
      if (y < -d || y > H + d) continue;
      var x = laneX(tl.lane);
      var im = IMGS[tl.lane];
      var near = AC && Math.abs(tl.at - AC.currentTime) < 0.24;
      if (near) {
        cx.globalAlpha = 0.35;
        cx.fillStyle = LCOL[tl.lane];
        cx.beginPath(); cx.arc(x, y, d * 0.62, 0, 6.29); cx.fill();
        cx.globalAlpha = 1;
      }
      if (im && im.complete && im.naturalWidth) {
        cx.drawImage(im, x - d / 2, y - d / 2, d, d);
      }
    }
  }
  function drawTitle() {
    var size = Math.min(W * 0.14, 58);
    var by = H * 0.3 + Math.sin(t * 1.8) * 5;
    cx.textAlign = "center";
    cx.font = "900 " + size + "px -apple-system,'Segoe UI',Roboto,sans-serif";
    cx.fillStyle = "rgba(10,8,20,0.5)";
    cx.fillText("CRITTER", W / 2 + 3, by + 3);
    cx.fillText("BEAT", W / 2 + 3, by + size * 1.04 + 3);
    cx.fillStyle = "#FFF4E4";
    cx.fillText("CRITTER", W / 2, by);
    cx.fillStyle = "#FFC46B";
    cx.fillText("BEAT", W / 2, by + size * 1.04);
    cx.font = "700 " + Math.min(W * 0.042, 17) + "px sans-serif";
    cx.fillStyle = "rgba(255,244,228,0.85)";
    cx.fillText("your taps play the song", W / 2, by + size * 1.04 + 34);
    if (best > 0) cx.fillText("BEST  " + best, W / 2, by + size * 1.04 + 62);
    // bobbing lane critters
    var d = Math.min(laneW() * 0.6, 84);
    for (var l = 0; l < LANES; l++) {
      var im = IMGS[l];
      if (im && im.complete && im.naturalWidth) {
        cx.drawImage(im, laneX(l) - d / 2, H * 0.62 + Math.sin(t * 2 + l) * 8, d, d);
      }
    }
  }

  function frame() {
    requestAnimationFrame(frame);
    if (paused) return;
    t += 1 / 60;
    if (state === "play") { scheduleBacking(); judgeMisses(); }
    document.getElementById("gift").style.display = giftVisible() ? "block" : "none";

    bg();
    if (state === "play") drawTiles();
    var i;
    for (i = particles.length - 1; i >= 0; i--) {
      var p = particles[i];
      p.x += p.vx; p.y += p.vy; p.vy += 0.15; p.a -= 0.02;
      if (p.a <= 0) { particles.splice(i, 1); continue; }
      cx.globalAlpha = p.a; cx.fillStyle = p.col;
      cx.fillRect(p.x, p.y, 5, 5); cx.globalAlpha = 1;
    }
    for (i = floats.length - 1; i >= 0; i--) {
      var fl = floats[i];
      fl.y -= 1.2; fl.a -= 0.022;
      fl.s = fl.s ? fl.s + (1 - fl.s) * 0.15 : 1;
      if (fl.a <= 0) { floats.splice(i, 1); continue; }
      cx.globalAlpha = Math.min(1, fl.a);
      cx.font = "800 " + Math.round(24 * fl.s) + "px sans-serif"; cx.textAlign = "center";
      cx.strokeStyle = "rgba(10,8,20,0.5)"; cx.lineWidth = 4;
      cx.strokeText(fl.txt, fl.x, fl.y);
      cx.fillStyle = "#FFF4E4";
      cx.fillText(fl.txt, fl.x, fl.y);
      cx.globalAlpha = 1;
    }
    if (state === "title") drawTitle();
  }

  /* ---------------------------------------------------------------- input */
  function startPlay() {
    state = "play";
    document.getElementById("hint").style.display = "none";
    ensureAC();
    if (AC) nextNoteAt = AC.currentTime + 0.6;
    songBeat = 0;
  }
  cv.addEventListener("pointerdown", function (e) {
    e.preventDefault();
    ensureAC();
    if (state === "title") { startPlay(); return; }
    if (state !== "play") return;
    var x = (e.touches && e.touches[0]) ? e.touches[0].clientX : e.clientX;
    tap(Math.max(0, Math.min(LANES - 1, Math.floor(x / laneW()))));
  });
  window.addEventListener("keydown", function (e) {
    var keys = { KeyD: 0, KeyF: 1, KeyJ: 2, KeyK: 3, Digit1: 0, Digit2: 1, Digit3: 2, Digit4: 3 };
    if (e.code in keys) {
      e.preventDefault();
      ensureAC();
      if (state === "title") { startPlay(); }
      tap(keys[e.code]);
    }
    if ((e.code === "Space" || e.code === "Enter") && state === "title") {
      e.preventDefault(); ensureAC(); startPlay();
    }
  });
  document.getElementById("again").addEventListener("click", function () {
    click();
    document.getElementById("over").style.display = "none";
    state = "play"; reset();
    if (AC) nextNoteAt = AC.currentTime + 0.6;
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
    var txt = "🥁 Critter Beat — I kept the groove to " + score + "!\n" +
      "One thumb, no download → tsjenn.github.io/Sj/play8/";
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
    state: function () { return { state: state, score: score, best: best, combo: combo,
      hearts: hearts, shield: shield, tiles: tiles.length, bpm: bpm, fever: fever,
      loaded: loaded, paused: paused, reviveUsed: reviveUsed, overs: overs,
      giftReady: giftVisible() }; },
    start: startPlay,
    seedTile: function (lane, dt) { ensureAC(); if (AC) tiles.push({ lane: lane, at: AC.currentTime + dt, hit: false, missed: false }); },
    tap: tap,
    clearTiles: function () { tiles = []; },
    stopSong: function () { nextNoteAt = 1e12; },
    forceOver: gameOver,
    reset: function () { document.getElementById("over").style.display = "none"; state = "play"; reset(); }
  };
})();
