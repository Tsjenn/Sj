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
  var AC = null;
  function beep(f, dur, type, gain) {
    if (!AC) return;
    var o = AC.createOscillator(), g = AC.createGain(), t = AC.currentTime;
    o.type = type || "triangle"; o.frequency.value = f;
    g.gain.setValueAtTime(gain || 0.15, t);
    g.gain.exponentialRampToValueAtTime(0.001, t + dur);
    o.connect(g); g.connect(AC.destination); o.start(t); o.stop(t + dur + 0.02);
  }
  function thud() { beep(90, 0.12, "sine", 0.3); }
  function chime(combo) { beep(440 * Math.pow(2, Math.min(combo, 12) / 12), 0.22, "triangle", 0.2); }

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
  var baseW, stack, moving, debris, particles, floats;
  var score = 0, best = 0, combo = 0, state = "title";
  var t = 0, shake = 0, cam = 0, camTarget = 0, paused = false;

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
    debris = []; particles = []; floats = [];
    score = 0; combo = 0; cam = 0; camTarget = 0;
    reviveUsed = false;
    newMoving();
    setScore();
  }
  function newMoving() {
    var top = stack[stack.length - 1];
    moving = { w: top.w, n: stack.length % CRITTERS.length, phase: Math.random() * 6.28,
      speed: 1.4 + Math.min(score * 0.045, 1.6), drop: 0, dropping: false };
  }
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
    if (!AC) { try { AC = new (window.AudioContext || window.webkitAudioContext)(); } catch (e) {} }
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
    if (Math.abs(off) < 7) {                              // PERFECT
      combo++;
      w = Math.min(w + 4, baseW);                          // reward: regrow
      x = top.x;
      chime(combo);
      burst(x, rowY(stack.length) - cam, "#FFC46B", 18);
      floats.push({ x: W / 2, y: rowY(stack.length) - cam - 40, txt: "PERFECT!", a: 1 });
    } else {                                              // slice
      combo = 0;
      var sliceW = w - overlap;
      var sliceX = off > 0 ? x + overlap / 2 : x - overlap / 2;
      debris.push({ x: sliceX + (off > 0 ? sliceW / 2 : -sliceW / 2), y: rowY(stack.length) - cam,
        w: sliceW, n: moving.n, vy: -2, vr: (off > 0 ? 1 : -1) * 0.05, r: 0 });
      w = overlap;
      x = off > 0 ? x - sliceW / 2 : x + sliceW / 2;
      thud();
      shake = 7;
    }
    stack.push({ x: x, w: w, n: moving.n });
    score++;
    camTarget = Math.max(0, (stack.length - 4) * BLOCK_H);
    setScore();
    if (w < 26) { gameOver(); return; }
    newMoving();
  }

  function gameOver() {
    state = "over";
    overs++;
    thud(); shake = 12;
    if (score > best) { best = score; saveBest(); }
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
  function slab(x, y, w, n, withCritter) {
    var name = CRITTERS[n];
    cx.fillStyle = "rgba(20,16,24,0.25)";
    rr(x - w / 2 + 3, y + 4, w, BLOCK_H - 6, 10); cx.fill();
    cx.fillStyle = COLORS[name];
    rr(x - w / 2, y, w, BLOCK_H - 6, 10); cx.fill();
    cx.strokeStyle = "#30283040"; cx.lineWidth = 2;
    rr(x - w / 2, y, w, BLOCK_H - 6, 10); cx.stroke();
    cx.fillStyle = "rgba(255,255,255,0.28)";
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
  function sky() {
    var ph = (score % 40) / 40 * SKY.length;
    var i = Math.floor(ph) % SKY.length, j = (i + 1) % SKY.length, f = ph - Math.floor(ph);
    var g = cx.createLinearGradient(0, 0, 0, H);
    g.addColorStop(0, mix(SKY[i][0], SKY[j][0], f));
    g.addColorStop(1, mix(SKY[i][1], SKY[j][1], f));
    cx.fillStyle = g; cx.fillRect(0, 0, W, H);
    if (i >= 2) {                                        // stars at night
      cx.fillStyle = "rgba(255,244,228,0.7)";
      for (var s = 0; s < 24; s++) {
        var sx = (s * 727 % W), sy = (s * 331 % (H * 0.6));
        cx.fillRect(sx, sy, 2, 2);
      }
    }
  }
  function mix(a, b, f) {
    var pa = [parseInt(a.slice(1, 3), 16), parseInt(a.slice(3, 5), 16), parseInt(a.slice(5, 7), 16)];
    var pb = [parseInt(b.slice(1, 3), 16), parseInt(b.slice(3, 5), 16), parseInt(b.slice(5, 7), 16)];
    return "rgb(" + pa.map(function (v, i) { return Math.round(v + (pb[i] - v) * f); }).join(",") + ")";
  }

  function frame() {
    requestAnimationFrame(frame);
    if (paused) return;
    t += 1 / 60;
    cam += (camTarget - cam) * 0.12;
    if (shake > 0.3) shake *= 0.86; else shake = 0;

    cx.save();
    if (shake) cx.translate((Math.random() - 0.5) * shake, (Math.random() - 0.5) * shake);
    sky();

    for (var i = 0; i < stack.length; i++) {
      var b = stack[i];
      slab(b.x, rowY(i), b.w, b.n, i === stack.length - 1 && state !== "play" ? true : i === stack.length - 1);
    }
    if (state === "play" && moving) {
      var y;
      if (moving.dropping) {
        moving.drop += 16;
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
      cx.save(); cx.translate(d.x, d.y + cam - cam); cx.rotate(d.r);
      slab(0, 0, d.w, d.n, false);
      cx.restore();
      if (d.y > H + 80) debris.splice(i, 1);
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
      fl.y -= 1.2; fl.a -= 0.02;
      if (fl.a <= 0) { floats.splice(i, 1); continue; }
      cx.globalAlpha = fl.a; cx.fillStyle = "#FFF4E4";
      cx.font = "800 28px sans-serif"; cx.textAlign = "center";
      cx.fillText(fl.txt, fl.x, fl.y); cx.globalAlpha = 1;
    }
    cx.restore();
  }

  /* ---------------------------------------------------------------- input */
  function onTap(e) { e.preventDefault(); if (state !== "over") drop(); }
  cv.addEventListener("pointerdown", onTap);
  window.addEventListener("keydown", function (e) {
    if (e.code === "Space" || e.code === "Enter") { e.preventDefault(); if (state !== "over") drop(); }
  });
  document.getElementById("again").addEventListener("click", function () {
    document.getElementById("over").style.display = "none";
    state = "play"; reset();
    maybeInterstitial();
  });
  document.getElementById("revive").addEventListener("click", function () {
    var a = bridgeAds();
    if (a && rewardedAvailable() && !reviveUsed) { adGotReward = false; a.showRewarded(); }
  });
  document.getElementById("share").addEventListener("click", function () {
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
      paused: paused, reviveUsed: reviveUsed, overs: overs }; },
    drop: drop,
    topX: function () { return stack[stack.length - 1].x; },
    dropAt: function (x) {
      if (state === "title") { state = "play"; document.getElementById("hint").style.display = "none"; }
      if (state === "play" && moving && !moving.dropping) {
        moving.dropping = true; moving.fx = x; moving.drop = 999;
      }
    },
    reset: function () { document.getElementById("over").style.display = "none"; state = "play"; reset(); }
  };
})();
