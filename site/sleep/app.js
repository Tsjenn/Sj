/* ==========================================================================
   RESTED — sleep tracker & sleep sounds
   Everything runs on-device: microphone audio is analysed in real time and
   never stored or uploaded. Only the resulting activity envelope is kept.
   ========================================================================== */
(function () {
  "use strict";

  var CFG = window.APP_CONFIG || { mode: "full", buyLink: "" };
  var IS_FREE = CFG.mode === "demo";
  var FREE_HISTORY = 7;          // nights kept on the free tier

  var $ = function (id) { return document.getElementById(id); };
  var clamp = function (v, a, b) { return v < a ? a : v > b ? b : v; };
  var lerp = function (a, b, k) { return a + (b - a) * k; };

  var EPOCH_S = 30;              // one scored epoch = 30 seconds
  var STAGE = { AWAKE: 0, LIGHT: 1, DEEP: 2, REM: 3 };
  var STAGE_NAME = ["Awake", "Light", "Deep", "Dream"];
  var STAGE_COL = ["#EDF1FB", "#4FB6E0", "#3F5FD6", "#A874EE"];

  // ------------------------------------------------------------------ store
  var DEFAULTS = {
    nights: [], alarm: "07:00", smart: true, alarmOn: true, window: 30,
    sound: "none", volume: 60, fade: 30, seenIntro: false
  };
  var db;
  try { db = JSON.parse(localStorage.getItem("rested") || "null"); } catch (e) { db = null; }
  if (!db) db = JSON.parse(JSON.stringify(DEFAULTS));
  Object.keys(DEFAULTS).forEach(function (k) { if (!(k in db)) db[k] = DEFAULTS[k]; });
  function save() {
    try { localStorage.setItem("rested", JSON.stringify(db)); }
    catch (e) { toast("Storage full — export and clear old nights."); }
  }
  function nights() {
    var n = db.nights.slice().sort(function (a, b) { return b.start - a.start; });
    return IS_FREE ? n.slice(0, FREE_HISTORY) : n;
  }

  function toast(msg) {
    var el = $("toast");
    el.textContent = msg;
    el.classList.add("on");
    clearTimeout(toast._t);
    toast._t = setTimeout(function () { el.classList.remove("on"); }, 2600);
  }
  function fmtHM(min) {
    min = Math.max(0, Math.round(min));
    return Math.floor(min / 60) + "h " + String(min % 60).padStart(2, "0") + "m";
  }
  function fmtClock(ms) {
    var d = new Date(ms);
    return String(d.getHours()).padStart(2, "0") + ":" + String(d.getMinutes()).padStart(2, "0");
  }
  function dayKey(ms) {
    var d = new Date(ms);
    return d.getFullYear() + "-" + String(d.getMonth() + 1).padStart(2, "0") + "-" + String(d.getDate()).padStart(2, "0");
  }

  /* ======================================================================
     AUDIO — one context drives microphone analysis, soundscapes and alarm
     ====================================================================== */
  var Audio2 = (function () {
    var ctx = null, master = null, micStream = null, analyser = null, micData = null;
    var sceneNodes = [], sceneGain = null, sceneTimer = null, alarmNodes = [];

    function ensure() {
      if (!ctx) {
        ctx = new (window.AudioContext || window.webkitAudioContext)();
        master = ctx.createGain();
        master.gain.value = 1;
        master.connect(ctx.destination);
      }
      if (ctx.state === "suspended") ctx.resume();
      return ctx;
    }

    function noiseBuffer(seconds, brown) {
      var n = Math.floor(ctx.sampleRate * seconds);
      var b = ctx.createBuffer(1, n, ctx.sampleRate), d = b.getChannelData(0);
      var last = 0;
      for (var i = 0; i < n; i++) {
        var w = Math.random() * 2 - 1;
        if (brown) { last = (last + 0.02 * w) / 1.02; d[i] = last * 3.2; }
        else d[i] = w;
      }
      return b;
    }
    function noiseSource(brown) {
      var s = ctx.createBufferSource();
      s.buffer = noiseBuffer(4, brown);
      s.loop = true;
      return s;
    }

    // ---- microphone -----------------------------------------------------
    function startMic() {
      ensure();
      return navigator.mediaDevices.getUserMedia({
        audio: { echoCancellation: false, noiseSuppression: false, autoGainControl: false }
      }).then(function (stream) {
        micStream = stream;
        var src = ctx.createMediaStreamSource(stream);
        analyser = ctx.createAnalyser();
        analyser.fftSize = 2048;
        analyser.smoothingTimeConstant = 0.25;
        src.connect(analyser);
        micData = new Float32Array(analyser.fftSize);
        return true;
      });
    }
    function stopMic() {
      if (micStream) { micStream.getTracks().forEach(function (t) { t.stop(); }); micStream = null; }
      analyser = null;
    }
    /* Instantaneous loudness, 0..1, mapped from dBFS so a quiet bedroom sits
       near 0 and a cough or a roll-over spikes toward 1. */
    function level() {
      if (!analyser) return 0;
      analyser.getFloatTimeDomainData(micData);
      var sum = 0;
      for (var i = 0; i < micData.length; i++) sum += micData[i] * micData[i];
      var rms = Math.sqrt(sum / micData.length);
      var db = 20 * Math.log10(rms + 1e-9);        // about -90 (silent) .. 0 (loud)
      return clamp((db + 75) / 60, 0, 1);
    }

    // ---- soundscapes ----------------------------------------------------
    var SCENES = {
      rain:   { name: "Rain",         icon: "🌧️", pro: false },
      ocean:  { name: "Ocean waves",  icon: "🌊", pro: false },
      brown:  { name: "Brown noise",  icon: "🟤", pro: false },
      fan:    { name: "Fan",          icon: "🌀", pro: true },
      fire:   { name: "Campfire",     icon: "🔥", pro: true },
      forest: { name: "Night forest", icon: "🌲", pro: true },
      train:  { name: "Night train",  icon: "🚂", pro: true }
    };

    function stopScene() {
      if (sceneTimer) { clearInterval(sceneTimer); sceneTimer = null; }
      sceneNodes.forEach(function (n) { try { n.stop ? n.stop() : n.disconnect(); } catch (e) {} });
      sceneNodes = [];
      if (sceneGain) { try { sceneGain.disconnect(); } catch (e) {} sceneGain = null; }
    }

    function playScene(key, volume, fadeMinutes) {
      stopScene();
      if (!key || key === "none" || !SCENES[key]) return;
      ensure();
      sceneGain = ctx.createGain();
      sceneGain.gain.value = 0;
      sceneGain.connect(master);
      sceneGain.gain.linearRampToValueAtTime(volume, ctx.currentTime + 2.5);

      function add(n) { sceneNodes.push(n); return n; }

      if (key === "brown") {
        var s = add(noiseSource(true));
        var lp = ctx.createBiquadFilter(); lp.type = "lowpass"; lp.frequency.value = 900;
        s.connect(lp); lp.connect(sceneGain); s.start();

      } else if (key === "rain") {
        var s2 = add(noiseSource(false));
        var hp = ctx.createBiquadFilter(); hp.type = "highpass"; hp.frequency.value = 700;
        var lp2 = ctx.createBiquadFilter(); lp2.type = "lowpass"; lp2.frequency.value = 7000;
        s2.connect(hp); hp.connect(lp2); lp2.connect(sceneGain); s2.start();
        // heavier drops on top
        sceneTimer = setInterval(function () {
          if (!sceneGain) return;
          for (var i = 0; i < 3; i++) burst(1200 + Math.random() * 2600, 0.05, 0.28 * Math.random(), 0.4);
        }, 260);

      } else if (key === "ocean") {
        var s3 = add(noiseSource(true));
        var bp = ctx.createBiquadFilter(); bp.type = "lowpass"; bp.frequency.value = 600;
        var swell = ctx.createGain(); swell.gain.value = 0.35;
        s3.connect(bp); bp.connect(swell); swell.connect(sceneGain); s3.start();
        var lfo = add(ctx.createOscillator()); lfo.frequency.value = 0.085;   // ~12 s waves
        var lfoAmt = ctx.createGain(); lfoAmt.gain.value = 0.3;
        lfo.connect(lfoAmt); lfoAmt.connect(swell.gain); lfo.start();
        var lfo2 = add(ctx.createOscillator()); lfo2.frequency.value = 0.085;
        var lfoF = ctx.createGain(); lfoF.gain.value = 420;
        lfo2.connect(lfoF); lfoF.connect(bp.frequency); lfo2.start();

      } else if (key === "fan") {
        var s4 = add(noiseSource(true));
        var bp2 = ctx.createBiquadFilter(); bp2.type = "bandpass";
        bp2.frequency.value = 340; bp2.Q.value = 0.7;
        var am = ctx.createGain(); am.gain.value = 0.8;
        s4.connect(bp2); bp2.connect(am); am.connect(sceneGain); s4.start();
        var wob = add(ctx.createOscillator()); wob.frequency.value = 22;   // blade flutter
        var wobAmt = ctx.createGain(); wobAmt.gain.value = 0.07;
        wob.connect(wobAmt); wobAmt.connect(am.gain); wob.start();

      } else if (key === "fire") {
        var s5 = add(noiseSource(true));
        var lp3 = ctx.createBiquadFilter(); lp3.type = "lowpass"; lp3.frequency.value = 500;
        var g5 = ctx.createGain(); g5.gain.value = 0.5;
        s5.connect(lp3); lp3.connect(g5); g5.connect(sceneGain); s5.start();
        sceneTimer = setInterval(function () {
          if (!sceneGain) return;
          if (Math.random() < 0.7) burst(700 + Math.random() * 1800, 0.04, 0.5 * Math.random(), 1.4);
        }, 190);

      } else if (key === "forest") {
        var s6 = add(noiseSource(true));
        var lp4 = ctx.createBiquadFilter(); lp4.type = "lowpass"; lp4.frequency.value = 380;
        var g6 = ctx.createGain(); g6.gain.value = 0.35;
        s6.connect(lp4); lp4.connect(g6); g6.connect(sceneGain); s6.start();
        sceneTimer = setInterval(function () {
          if (!sceneGain) return;
          if (Math.random() < 0.55) chirp();
        }, 700);

      } else if (key === "train") {
        var s7 = add(noiseSource(true));
        var lp5 = ctx.createBiquadFilter(); lp5.type = "lowpass"; lp5.frequency.value = 260;
        var g7 = ctx.createGain(); g7.gain.value = 0.6;
        s7.connect(lp5); lp5.connect(g7); g7.connect(sceneGain); s7.start();
        var beat = 0;
        sceneTimer = setInterval(function () {
          if (!sceneGain) return;
          beat++;
          burst(90, 0.09, beat % 4 < 2 ? 0.34 : 0.24, 0.9);       // clickety-clack
        }, 340);
      }
    }

    function burst(freq, dur, vol, q) {
      if (!ctx || !sceneGain) return;
      var s = ctx.createBufferSource();
      s.buffer = noiseBuffer(0.25, false);
      var f = ctx.createBiquadFilter();
      f.type = "bandpass"; f.frequency.value = freq; f.Q.value = q || 1;
      var g = ctx.createGain();
      g.gain.setValueAtTime(vol, ctx.currentTime);
      g.gain.exponentialRampToValueAtTime(0.0001, ctx.currentTime + dur);
      s.connect(f); f.connect(g); g.connect(sceneGain);
      s.start(); s.stop(ctx.currentTime + dur + 0.05);
    }
    function chirp() {
      if (!ctx || !sceneGain) return;
      var base = 3200 + Math.random() * 1400;
      for (var i = 0; i < 3; i++) {
        var t = ctx.currentTime + i * 0.075;
        var o = ctx.createOscillator(), g = ctx.createGain();
        o.type = "triangle"; o.frequency.setValueAtTime(base, t);
        g.gain.setValueAtTime(0, t);
        g.gain.linearRampToValueAtTime(0.05, t + 0.012);
        g.gain.exponentialRampToValueAtTime(0.0001, t + 0.05);
        o.connect(g); g.connect(sceneGain);
        o.start(t); o.stop(t + 0.07);
      }
    }
    function fadeScene(seconds) {
      if (!sceneGain || !ctx) return;
      sceneGain.gain.cancelScheduledValues(ctx.currentTime);
      sceneGain.gain.setValueAtTime(sceneGain.gain.value, ctx.currentTime);
      sceneGain.gain.linearRampToValueAtTime(0.0001, ctx.currentTime + seconds);
      setTimeout(stopScene, seconds * 1000 + 400);
    }
    function scenePlaying() { return !!sceneGain; }

    // ---- alarm ----------------------------------------------------------
    function startAlarm() {
      ensure();
      stopAlarm();
      var g = ctx.createGain();
      g.gain.value = 0.0001;
      g.gain.exponentialRampToValueAtTime(0.55, ctx.currentTime + 28);  // gentle 28 s rise
      g.connect(master);
      alarmNodes.push(g);
      var step = 0;
      var notes = [523.25, 659.25, 783.99, 1046.5];
      var t = setInterval(function () {
        if (!ctx) return;
        var f = notes[step % notes.length];
        var o = ctx.createOscillator(), og = ctx.createGain();
        o.type = "sine"; o.frequency.value = f;
        og.gain.setValueAtTime(0, ctx.currentTime);
        og.gain.linearRampToValueAtTime(0.5, ctx.currentTime + 0.08);
        og.gain.exponentialRampToValueAtTime(0.0001, ctx.currentTime + 1.1);
        o.connect(og); og.connect(g);
        o.start(); o.stop(ctx.currentTime + 1.2);
        step++;
      }, 620);
      alarmNodes.push({ stop: function () { clearInterval(t); } });
    }
    function stopAlarm() {
      alarmNodes.forEach(function (n) { try { n.stop ? n.stop() : n.disconnect(); } catch (e) {} });
      alarmNodes = [];
    }

    return {
      ensure: ensure, startMic: startMic, stopMic: stopMic, level: level,
      playScene: playScene, stopScene: stopScene, fadeScene: fadeScene,
      scenePlaying: scenePlaying, SCENES: SCENES,
      startAlarm: startAlarm, stopAlarm: stopAlarm,
      hasMic: function () { return !!analyser; }
    };
  })();

  /* ======================================================================
     SLEEP ANALYSIS
     Actigraphy-style scoring: an activity envelope per 30-second epoch is
     turned into wake / light / deep / dream estimates. Thresholds are drawn
     from the night's own distribution so a noisy room and a silent one both
     work. Stage splits are estimates — see the note in the About card.
     ====================================================================== */
  function percentile(arr, p) {
    if (!arr.length) return 0;
    var s = arr.slice().sort(function (a, b) { return a - b; });
    var i = clamp(Math.floor(p * (s.length - 1)), 0, s.length - 1);
    return s[i];
  }
  function smooth(arr, win) {
    var out = new Array(arr.length);
    for (var i = 0; i < arr.length; i++) {
      var a = Math.max(0, i - win), b = Math.min(arr.length - 1, i + win), s = 0, n = 0;
      for (var j = a; j <= b; j++) { s += arr[j]; n++; }
      out[i] = s / n;
    }
    return out;
  }

  function classify(epochs) {
    var n = epochs.length;
    if (n < 4) return { stages: epochs.map(function () { return STAGE.AWAKE; }) };

    var act = epochs.map(function (e) { return e.a; });
    var quiet = epochs.filter(function (e) { return !e.s; }).map(function (e) { return e.a; });
    if (quiet.length < 10) quiet = act;

    var floor = percentile(quiet, 0.10);
    var norm = act.map(function (v) { return Math.max(0, v - floor); });
    var sm = smooth(norm, 2);

    var p50 = percentile(sm, 0.50), p85 = percentile(sm, 0.85), p20 = percentile(sm, 0.20);
    var awakeT = Math.max(p85 * 0.95, p50 * 2.6, 0.045);
    var deepT = Math.max(p20 * 1.25, 0.004);

    // find sleep onset: first run of 8 quiet epochs (4 minutes)
    var onset = -1, run = 0;
    for (var i = 0; i < n; i++) {
      if (sm[i] < awakeT) { run++; if (run >= 8) { onset = i - run + 1; break; } }
      else run = 0;
    }
    if (onset < 0) onset = n;

    // find final wake: last quiet epoch
    var finalWake = n;
    for (var w = n - 1; w >= onset; w--) { if (sm[w] < awakeT) { finalWake = w + 1; break; } }

    /* ---- wake vs sleep.
       Wake is decided on the *unsmoothed* envelope: smoothing smears one
       roll-over across several epochs, which inflates both the hypnogram and
       the "times woken" figure. A lone loud epoch is movement; two in a row
       is being awake. */
    var stages = new Array(n);
    var loud = new Array(n);
    for (var k = 0; k < n; k++) loud[k] = norm[k] >= awakeT;
    for (var k1 = 0; k1 < n; k1++) {
      var sustained = loud[k1] && ((k1 > 0 && loud[k1 - 1]) || (k1 < n - 1 && loud[k1 + 1]));
      stages[k1] = (k1 < onset || k1 >= finalWake || sustained) ? STAGE.AWAKE : STAGE.LIGHT;
    }
    /* Rolling over is not waking up. The activity envelope is smoothed, so a
       single movement smears across two or three epochs — without this the
       hypnogram is confetti and the "times woken" headline reads absurdly
       high. Anything under 90 seconds is treated as restless light sleep. */
    var zi = onset;
    while (zi < finalWake) {
      if (stages[zi] !== STAGE.AWAKE) { zi++; continue; }
      var zj = zi;
      while (zj < finalWake && stages[zj] === STAGE.AWAKE) zj++;
      if (zj - zi <= 2 && zi > onset && zj < finalWake) {
        for (var zk = zi; zk < zj; zk++) stages[zk] = STAGE.LIGHT;
      }
      zi = zj;
    }
    var sleepIdx = [];
    for (var k2 = 0; k2 < n; k2++) if (stages[k2] !== STAGE.AWAKE) sleepIdx.push(k2);

    /* ---- split sleep into light / deep / dream.
       Absolute thresholds give wildly unphysiological mixes (40% deep on a
       quiet night), so instead each sleep epoch gets a deep- and a dream-
       affinity from how still it is and where it sits in the ~90 minute
       cycle, then the quietest share of the night is allocated to each
       stage. Deep dominates the early cycles, dream the later ones — which
       is what actually happens — and the resulting mix always lands in a
       believable range. */
    if (sleepIdx.length > 20) {
      var sleepAct = sleepIdx.map(function (i) { return sm[i]; });
      var lo = percentile(sleepAct, 0.05), hi = percentile(sleepAct, 0.95);
      var span = Math.max(1e-6, hi - lo);
      var normOf = function (i) { return clamp((sm[i] - lo) / span, 0, 1); };

      var meanNorm = sleepIdx.reduce(function (s, i) { return s + normOf(i); }, 0) / sleepIdx.length;
      var quietness = clamp(1 - meanNorm, 0, 1);

      /* How broken up the night was drives the mix as much as how still it
         was: fragmented, inefficient sleep genuinely costs you deep sleep
         first and dream sleep second. Without this the stage split barely
         moves between a good night and a bad one. */
      var wakeRuns = 0, inRun = false;
      for (var f = onset; f < finalWake; f++) {
        if (stages[f] === STAGE.AWAKE) { if (!inRun) { wakeRuns++; inRun = true; } }
        else inRun = false;
      }
      var sleepHours = Math.max(0.5, sleepIdx.length * EPOCH_S / 3600);
      var fragPerHour = wakeRuns / sleepHours;
      var efficiency = sleepIdx.length / Math.max(1, finalWake - onset);
      var fragPenalty = clamp(1 - fragPerHour * 0.14, 0.45, 1);
      var effBonus = clamp((efficiency - 0.70) / 0.25, 0, 1);

      var targetDeep = clamp((0.07 + quietness * 0.13 + effBonus * 0.09) * fragPenalty, 0.05, 0.26);
      var targetRem = clamp((0.12 + quietness * 0.09 + effBonus * 0.08) * (0.6 + fragPenalty * 0.4), 0.09, 0.27);

      var scored = sleepIdx.map(function (i) {
        var na = normOf(i);
        var mins = (i - onset) * EPOCH_S / 60;
        var cyclePos = (mins % 90) / 90;
        var nightPos = clamp((i - onset) / Math.max(1, finalWake - onset), 0, 1);
        // deep: still, early in the night, early in each cycle
        var deepAff = (1 - na) * (1 - nightPos * 0.55) * clamp(1 - Math.abs(cyclePos - 0.32) * 1.6, 0.05, 1);
        // dream: fairly still but with micro-movement, late in the night and late in each cycle
        var remAff = (1 - na * 0.62) * (0.30 + nightPos * 0.95) *
                     clamp(Math.sin(clamp((cyclePos - 0.30) / 0.70, 0, 1) * Math.PI), 0.05, 1);
        return { i: i, deep: deepAff, rem: remAff };
      });

      var nDeep = Math.round(sleepIdx.length * targetDeep);
      var nRem = Math.round(sleepIdx.length * targetRem);

      scored.slice().sort(function (a, b) { return b.deep - a.deep; })
        .slice(0, nDeep).forEach(function (o) { stages[o.i] = STAGE.DEEP; });
      scored.filter(function (o) { return stages[o.i] !== STAGE.DEEP; })
        .sort(function (a, b) { return b.rem - a.rem; })
        .slice(0, nRem).forEach(function (o) { stages[o.i] = STAGE.REM; });
    }

    // a soundscape masks the room, so those epochs can only be scored as light
    for (var q2 = 0; q2 < n; q2++) {
      if (epochs[q2].s && stages[q2] !== STAGE.AWAKE) stages[q2] = STAGE.LIGHT;
    }

    // enforce a 3-epoch (90 s) minimum so the hypnogram is not confetti
    for (var pass = 0; pass < 2; pass++) {
      var i2 = 0;
      while (i2 < n) {
        var j = i2;
        while (j < n && stages[j] === stages[i2]) j++;
        if (j - i2 < 3 && i2 > 0 && j < n) {
          var fill = stages[i2 - 1];
          for (var m = i2; m < j; m++) stages[m] = fill;
        }
        i2 = j;
      }
    }
    return { stages: stages, onset: onset, finalWake: finalWake };
  }

  function summarise(night) {
    var st = night.stages, n = st.length;
    var mins = EPOCH_S / 60;
    var count = [0, 0, 0, 0];
    st.forEach(function (s) { count[s] += mins; });
    var inBed = n * mins;
    var asleep = count[1] + count[2] + count[3];

    // awakenings = sustained wake runs (>= 90 s) between falling asleep and getting up
    var wakes = 0, i = night.onset || 0, run = 0;
    var lastEp = (night.finalWake != null ? night.finalWake : n);
    for (; i < lastEp; i++) {
      if (st[i] === STAGE.AWAKE) run++;
      else { if (run >= 3) wakes++; run = 0; }
    }
    if (run >= 3) wakes++;

    var eff = inBed > 0 ? asleep / inBed : 0;
    var onsetMin = (night.onset || 0) * mins;
    var deepPct = asleep > 0 ? count[2] / asleep : 0;
    var remPct = asleep > 0 ? count[3] / asleep : 0;

    function band(v, lo, hi, soft) {
      if (v >= lo && v <= hi) return 1;
      var d = v < lo ? lo - v : v - hi;
      return clamp(1 - d / soft, 0, 1);
    }
    var durScore = band(asleep / 60, 7, 9, 1.6);
    var effScore = clamp((eff - 0.72) / 0.23, 0, 1);
    var deepScore = band(deepPct, 0.13, 0.25, 0.14);
    var remScore = band(remPct, 0.18, 0.28, 0.16);
    var fragScore = clamp(1 - wakes / 6, 0, 1);
    var onsetScore = band(onsetMin, 0, 20, 22);

    /* Duration, efficiency and fragmentation carry most of the weight: they
       are what the microphone can actually measure well, and what genuinely
       varies night to night. The stage percentages are estimates that move
       very little, so they only nudge the score. */
    var quality = Math.round(100 * (
      durScore * 0.38 + effScore * 0.24 + fragScore * 0.14 +
      onsetScore * 0.10 + deepScore * 0.08 + remScore * 0.06));

    night.inBed = inBed;
    night.asleep = asleep;
    night.awakeMin = count[0];
    night.lightMin = count[1];
    night.deepMin = count[2];
    night.remMin = count[3];
    night.awakenings = wakes;
    night.onsetMin = onsetMin;
    night.efficiency = eff;
    night.quality = clamp(quality, 1, 99);
    return night;
  }

  /* ======================================================================
     TRACKING SESSION
     ====================================================================== */
  var session = null, wakeLock = null, nightTimer = null, alarmFired = false;

  function requestWakeLock() {
    if (!("wakeLock" in navigator)) return;
    navigator.wakeLock.request("screen").then(function (l) {
      wakeLock = l;
      l.addEventListener("release", function () { wakeLock = null; });
    }).catch(function () {});
  }
  document.addEventListener("visibilitychange", function () {
    if (document.visibilityState === "visible" && session && !wakeLock) requestWakeLock();
  });

  function alarmTargetMs() {
    var parts = db.alarm.split(":");
    var d = new Date();
    d.setHours(+parts[0], +parts[1], 0, 0);
    if (d.getTime() <= Date.now()) d.setDate(d.getDate() + 1);
    return d.getTime();
  }

  function startSession() {
    Audio2.ensure();
    Audio2.startMic().then(function () {
      beginSession();
    }).catch(function (err) {
      // Tracking needs the microphone; without it we can still run as a
      // sound machine + alarm, so offer that rather than dead-ending.
      console.warn("mic denied", err);
      beginSession(true);
      toast("No microphone access — running as alarm + sounds only.");
    });
  }

  function beginSession(noMic) {
    session = {
      start: Date.now(), epochs: [], acc: [], noMic: !!noMic,
      alarmAt: db.alarmOn ? alarmTargetMs() : null,
      lastEpoch: Date.now()
    };
    alarmFired = false;
    if (db.sound !== "none") {
      Audio2.playScene(db.sound, db.volume / 100, db.fade);
      if (db.fade > 0) setTimeout(function () { Audio2.fadeScene(60); }, db.fade * 60000);
    }
    $("night").classList.add("on");
    $("nsub").textContent = session.alarmAt
      ? "Tracking · alarm " + db.alarm + (db.smart ? " (smart)" : "")
      : "Tracking · no alarm";
    requestWakeLock();
    tickNight();
    nightTimer = setInterval(tickNight, 1000);
    setTimeout(function () { $("night").classList.add("dim"); }, 12000);
  }

  var levelBuf = [], waveHist = new Array(120).fill(0);
  function tickNight() {
    if (!session) return;
    var now = Date.now();
    $("nclock").textContent = fmtClock(now);

    var lv = session.noMic ? 0 : Audio2.level();
    levelBuf.push(lv);
    waveHist.push(lv); waveHist.shift();
    drawWave();

    // close an epoch every EPOCH_S
    if (now - session.lastEpoch >= EPOCH_S * 1000) {
      session.lastEpoch = now;
      var peak = 0, sum = 0, events = 0;
      var floorGuess = percentile(levelBuf, 0.2);
      for (var i = 0; i < levelBuf.length; i++) {
        peak = Math.max(peak, levelBuf[i]);
        sum += levelBuf[i];
        if (levelBuf[i] > floorGuess + 0.06) events++;
      }
      var mean = levelBuf.length ? sum / levelBuf.length : 0;
      var activity = clamp((peak - floorGuess) * 0.75 + (events / Math.max(1, levelBuf.length)) * 0.5 + mean * 0.2, 0, 1);
      session.epochs.push({ a: +activity.toFixed(4), s: Audio2.scenePlaying() ? 1 : 0 });
      levelBuf = [];
      maybeSmartAlarm();
    }

    if (session.alarmAt && !alarmFired && now >= session.alarmAt) fireAlarm("Time to wake up");
  }

  /* Smart alarm: inside the window, wake on the first sign of light sleep or
     movement, so the alarm lands at a natural surfacing point. */
  function maybeSmartAlarm() {
    if (!session || !session.alarmAt || alarmFired || !db.smart || db.window <= 0) return;
    var now = Date.now();
    var winStart = session.alarmAt - db.window * 60000;
    if (now < winStart) return;
    var eps = session.epochs;
    if (eps.length < 12) return;
    var recent = eps.slice(-4).map(function (e) { return e.a; });
    var all = eps.map(function (e) { return e.a; });
    var floor = percentile(all, 0.10);
    var p60 = percentile(all, 0.60);
    var avgRecent = recent.reduce(function (a, b) { return a + b; }, 0) / recent.length;
    if (avgRecent - floor > Math.max((p60 - floor) * 1.15, 0.02)) {
      fireAlarm("Woke you in light sleep");
    }
  }

  function fireAlarm(why) {
    alarmFired = true;
    Audio2.stopScene();
    Audio2.startAlarm();
    $("al-time").textContent = fmtClock(Date.now());
    $("al-why").textContent = why;
    $("alarm-screen").classList.add("on");
    if (navigator.vibrate) navigator.vibrate([400, 200, 400, 200, 400]);
  }

  function endSession(skipReport) {
    if (!session) return;
    var s = session;
    session = null;
    clearInterval(nightTimer); nightTimer = null;
    Audio2.stopMic(); Audio2.stopScene(); Audio2.stopAlarm();
    if (wakeLock) { try { wakeLock.release(); } catch (e) {} wakeLock = null; }
    $("night").classList.remove("on", "dim");
    $("alarm-screen").classList.remove("on");

    if (s.epochs.length < 20) {          // under 10 minutes — not a night
      toast("Session too short to score (" + Math.round(s.epochs.length / 2) + " min).");
      render();
      return;
    }
    var res = classify(s.epochs);
    var night = summarise({
      id: s.start, start: s.start, end: Date.now(),
      epochs: s.epochs, stages: res.stages, onset: res.onset, finalWake: res.finalWake,
      tags: [], mood: 0, noMic: s.noMic
    });
    db.nights.push(night);
    if (db.nights.length > 400) db.nights = db.nights.slice(-400);
    save();
    render();
    if (!skipReport) {
      openReport(night);
      setTimeout(function () { openTags(night); }, 700);
    }
  }

  function drawWave() {
    var c = $("nwave"), x = c.getContext("2d");
    var W = c.width, H = c.height;
    x.clearRect(0, 0, W, H);
    x.strokeStyle = "#4A5573"; x.lineWidth = 2.5; x.lineJoin = "round";
    x.beginPath();
    for (var i = 0; i < waveHist.length; i++) {
      var px = i / (waveHist.length - 1) * W;
      var py = H - 6 - Math.pow(waveHist[i], 0.6) * (H - 14);
      if (i === 0) x.moveTo(px, py); else x.lineTo(px, py);
    }
    x.stroke();
  }

  /* ======================================================================
     CHARTS
     ====================================================================== */
  function fitCanvas(c, cssH) {
    var dpr = Math.min(devicePixelRatio || 1, 2);
    var w = c.clientWidth || c.parentNode.clientWidth || 320;
    c.width = w * dpr; c.height = cssH * dpr;
    c.style.height = cssH + "px";
    var x = c.getContext("2d");
    x.setTransform(dpr, 0, 0, dpr, 0, 0);
    return { x: x, w: w, h: cssH };
  }

  function drawHypnogram(canvas, night) {
    var f = fitCanvas(canvas, 150), x = f.x, W = f.w, H = f.h;
    var st = night.stages, n = st.length;
    if (!n) return;
    var padT = 8, padB = 26, plotH = H - padT - padB;
    // stage rows: awake top, then rem, light, deep
    var order = [STAGE.AWAKE, STAGE.REM, STAGE.LIGHT, STAGE.DEEP];
    var rowH = plotH / order.length;
    var yOf = function (s) { return padT + order.indexOf(s) * rowH + rowH / 2; };

    // subtle row guides
    x.strokeStyle = "rgba(255,255,255,.05)"; x.lineWidth = 1;
    order.forEach(function (s, i) {
      var y = padT + i * rowH + rowH / 2;
      x.beginPath(); x.moveTo(0, y); x.lineTo(W, y); x.stroke();
    });

    // filled blocks per run
    var i2 = 0;
    while (i2 < n) {
      var j = i2;
      while (j < n && st[j] === st[i2]) j++;
      var x0 = i2 / n * W, x1 = j / n * W;
      var y = yOf(st[i2]);
      x.fillStyle = STAGE_COL[st[i2]];
      x.globalAlpha = 0.22;
      x.fillRect(x0, y - rowH * 0.36, Math.max(1.5, x1 - x0), rowH * 0.72);
      x.globalAlpha = 1;
      x.fillRect(x0, y - 2, Math.max(1.5, x1 - x0), 4);
      i2 = j;
    }
    // connectors
    x.strokeStyle = "rgba(255,255,255,.22)"; x.lineWidth = 1.5;
    x.beginPath();
    var prev = null;
    i2 = 0;
    while (i2 < n) {
      var j2 = i2;
      while (j2 < n && st[j2] === st[i2]) j2++;
      var yy = yOf(st[i2]), xx = i2 / n * W;
      if (prev !== null) { x.moveTo(xx, prev); x.lineTo(xx, yy); }
      prev = yy;
      i2 = j2;
    }
    x.stroke();

    // time axis
    x.fillStyle = "#5A6580"; x.font = "11px -apple-system, system-ui, sans-serif";
    x.textAlign = "left"; x.fillText(fmtClock(night.start), 0, H - 8);
    x.textAlign = "right"; x.fillText(fmtClock(night.end), W, H - 8);
    x.textAlign = "center";
    var mid = night.start + (night.end - night.start) / 2;
    x.fillText(fmtClock(mid), W / 2, H - 8);
  }

  function drawTrend(canvas, points, opts) {
    opts = opts || {};
    var f = fitCanvas(canvas, opts.height || 130), x = f.x, W = f.w, H = f.h;
    if (points.length < 2) {
      x.fillStyle = "#5A6580"; x.font = "13px system-ui"; x.textAlign = "center";
      x.fillText("Track a few more nights to see a trend", W / 2, H / 2);
      return;
    }
    var vals = points.map(function (p) { return p.v; });
    var lo = opts.min != null ? opts.min : Math.min.apply(null, vals);
    var hi = opts.max != null ? opts.max : Math.max.apply(null, vals);
    if (hi - lo < 1e-6) { hi = lo + 1; }
    var pad = (hi - lo) * 0.18;
    lo -= pad; hi += pad;
    if (opts.clampMin != null) lo = Math.max(lo, opts.clampMin);
    if (opts.clampMax != null) hi = Math.min(hi, opts.clampMax);
    var padL = 34, padB = 20, padT = 8;
    var plotW = W - padL, plotH = H - padB - padT;
    var xOf = function (i) { return padL + i / (points.length - 1) * plotW; };
    var yOf = function (v) { return padT + (1 - (v - lo) / (hi - lo)) * plotH; };

    // grid + labels
    x.strokeStyle = "rgba(255,255,255,.06)"; x.fillStyle = "#5A6580";
    x.font = "10px system-ui"; x.textAlign = "right"; x.lineWidth = 1;
    for (var g = 0; g <= 2; g++) {
      var v = lo + (hi - lo) * (g / 2);
      var y = yOf(v);
      x.beginPath(); x.moveTo(padL, y); x.lineTo(W, y); x.stroke();
      x.fillText(opts.fmt ? opts.fmt(v) : Math.round(v), padL - 6, y + 3);
    }
    // average line
    var avg = vals.reduce(function (a, b) { return a + b; }, 0) / vals.length;
    x.strokeStyle = "rgba(255,255,255,.35)";
    x.setLineDash([4, 4]);
    x.beginPath(); x.moveTo(padL, yOf(avg)); x.lineTo(W, yOf(avg)); x.stroke();
    x.setLineDash([]);

    // area + line (smoothed)
    var col = opts.color || "#F2A65A";
    x.beginPath();
    points.forEach(function (p, i) {
      var px = xOf(i), py = yOf(p.v);
      if (i === 0) x.moveTo(px, py);
      else {
        var pxPrev = xOf(i - 1), pyPrev = yOf(points[i - 1].v);
        var cx = (pxPrev + px) / 2;
        x.bezierCurveTo(cx, pyPrev, cx, py, px, py);
      }
    });
    var stroke = new Path2D();
    x.strokeStyle = col; x.lineWidth = 2.4; x.lineJoin = "round"; x.stroke();
    x.lineTo(xOf(points.length - 1), padT + plotH);
    x.lineTo(padL, padT + plotH);
    x.closePath();
    var grad = x.createLinearGradient(0, padT, 0, padT + plotH);
    grad.addColorStop(0, col + "44");
    grad.addColorStop(1, col + "00");
    x.fillStyle = grad; x.fill();

    // end labels
    x.fillStyle = "#5A6580"; x.font = "10px system-ui";
    x.textAlign = "left"; x.fillText(points[0].l, padL, H - 5);
    x.textAlign = "right"; x.fillText(points[points.length - 1].l, W, H - 5);
  }

  /* ======================================================================
     RENDER
     ====================================================================== */
  function render() {
    renderTonight();
    renderStats();
    renderYou();
  }

  function renderTonight() {
    var all = nights();
    var last = all[0];
    var h = new Date().getHours();
    $("greet").textContent = h >= 19 || h < 4 ? "Tonight" : h < 12 ? "Good morning" : "Today";

    // week dots
    var wd = $("weekdots");
    wd.innerHTML = "";
    var names = ["S", "M", "T", "W", "T", "F", "S"];
    for (var i = 6; i >= 0; i--) {
      var d = new Date(); d.setDate(d.getDate() - i);
      var key = dayKey(d.getTime());
      var found = all.filter(function (n) { return dayKey(n.end || n.start) === key; })[0];
      var el = document.createElement("div");
      el.className = "wd";
      el.innerHTML = '<div class="d' + (found ? " has" : "") + (i === 0 ? " today" : "") + '">' +
        names[d.getDay()] + "</div>";
      if (found) {
        el.querySelector(".d").style.borderColor = "var(--accent)";
        el.title = found.quality + "%";
      }
      (function (f) {
        el.addEventListener("click", function () { if (f) openReport(f); });
      })(found);
      wd.appendChild(el);
    }

    if (last) {
      $("last-night").style.display = "";
      $("q-val").innerHTML = last.quality + "<span>%</span>";
      var dash = 352;
      $("qring").setAttribute("stroke-dashoffset", dash - dash * (last.quality / 100));
      $("s-inbed").innerHTML = fmtHM(last.inBed) + "<small>In bed</small>";
      $("s-asleep").innerHTML = fmtHM(last.asleep) + "<small>Asleep</small>";
    } else {
      $("last-night").style.display = "none";
    }

    $("alarm-time").value = db.alarm;
    $("win-range").value = db.window;
    $("win-lbl").textContent = db.window > 0 ? db.window + " minutes before" : "Off — ring exactly on time";
    $("smart-sw").classList.toggle("on", db.smart);
    $("alarm-sw").classList.toggle("on", db.alarmOn);
    var sc = Audio2.SCENES[db.sound];
    $("pick-sound").textContent = (sc ? sc.icon + " " + sc.name : "None") + " ›";
    $("sound-note").textContent = db.fade > 0 ? "Fades out after " + db.fade + " min" : "Plays all night";
    if (IS_FREE && CFG.buyLink) {
      $("premium-banner").style.display = "block";
      $("buy-btn").href = CFG.buyLink;
    }
  }

  function statPoints(days) {
    var all = nights().slice().sort(function (a, b) { return a.start - b.start; });
    if (days > 0) {
      var cut = Date.now() - days * 86400000;
      all = all.filter(function (n) { return n.start >= cut; });
    }
    return all;
  }

  function renderStats() {
    var body = $("stats-body");
    var days = +(document.querySelector("#range-seg button.on") || { dataset: { r: 7 } }).dataset.r;
    var list = statPoints(days);
    if (list.length < 1) {
      body.innerHTML = '<div class="card"><div class="empty">No nights yet.<br>Track one night and your trends start here.</div></div>';
      return;
    }
    var label = function (n) {
      var d = new Date(n.end || n.start);
      return (d.getMonth() + 1) + "/" + d.getDate();
    };
    body.innerHTML =
      '<div class="card"><div class="spread"><h3>Sleep quality</h3><div class="mono" style="color:var(--accent);font-weight:800" id="avg-q"></div></div>' +
        '<canvas class="chart" id="c-q"></canvas></div>' +
      '<div class="card"><div class="spread"><h3>Time asleep</h3><div class="mono" style="color:var(--lightx);font-weight:800" id="avg-a"></div></div>' +
        '<canvas class="chart" id="c-a"></canvas></div>' +
      '<div class="card"><div class="spread"><h3>Bedtime</h3><div class="mono" style="color:var(--rem);font-weight:800" id="avg-b"></div></div>' +
        '<canvas class="chart" id="c-b"></canvas>' +
        '<div class="note" style="margin-top:8px">Consistency matters more than any single night — a steady bedtime is the strongest lever most people have.</div></div>' +
      '<div class="card"><h3>Stage mix</h3><div id="mix"></div></div>';

    var avg = function (f) { return list.reduce(function (a, n) { return a + f(n); }, 0) / list.length; };
    $("avg-q").textContent = Math.round(avg(function (n) { return n.quality; })) + "% avg";
    $("avg-a").textContent = fmtHM(avg(function (n) { return n.asleep; })) + " avg";

    drawTrend($("c-q"), list.map(function (n) { return { v: n.quality, l: label(n) }; }),
      { color: "#F2A65A", clampMin: 0, clampMax: 100, fmt: function (v) { return Math.round(v) + "%"; } });
    drawTrend($("c-a"), list.map(function (n) { return { v: n.asleep / 60, l: label(n) }; }),
      { color: "#4FB6E0", fmt: function (v) { return v.toFixed(1) + "h"; } });

    // bedtime as hours since 18:00 so late nights read as "higher"
    var bed = list.map(function (n) {
      var d = new Date(n.start);
      var hrs = d.getHours() + d.getMinutes() / 60;
      if (hrs < 12) hrs += 24;
      return { v: hrs, l: label(n) };
    });
    var avgBed = bed.reduce(function (a, b) { return a + b.v; }, 0) / bed.length;
    var bh = Math.floor(avgBed) % 24, bm = Math.round((avgBed % 1) * 60);
    $("avg-b").textContent = String(bh).padStart(2, "0") + ":" + String(bm).padStart(2, "0") + " avg";
    drawTrend($("c-b"), bed, {
      color: "#A874EE",
      fmt: function (v) { return String(Math.floor(v) % 24).padStart(2, "0") + ":" + String(Math.round((v % 1) * 60)).padStart(2, "0"); }
    });

    var tot = avg(function (n) { return n.asleep; }) || 1;
    var mix = [
      ["Deep", avg(function (n) { return n.deepMin; }), STAGE_COL[2]],
      ["Dream", avg(function (n) { return n.remMin; }), STAGE_COL[3]],
      ["Light", avg(function (n) { return n.lightMin; }), STAGE_COL[1]],
      ["Awake", avg(function (n) { return n.awakeMin; }), STAGE_COL[0]]
    ];
    $("mix").innerHTML = '<div style="display:flex;height:12px;border-radius:99px;overflow:hidden;margin:12px 0">' +
      mix.map(function (m) {
        return '<div style="width:' + (m[1] / (tot + mix[3][1]) * 100) + '%;background:' + m[2] + '"></div>';
      }).join("") + "</div>" +
      '<div class="legend">' + mix.map(function (m) {
        return '<div><i style="background:' + m[2] + '"></i>' + m[0] + ' <b>' + fmtHM(m[1]) + "</b></div>";
      }).join("") + "</div>";
  }

  var TAGS = [
    { k: "caffeine", n: "☕ Caffeine" }, { k: "alcohol", n: "🍷 Alcohol" },
    { k: "latemeal", n: "🍔 Late meal" }, { k: "exercise", n: "🏃 Exercise" },
    { k: "stress", n: "😣 Stress" }, { k: "screens", n: "📱 Late screens" },
    { k: "nap", n: "😴 Napped" }, { k: "reading", n: "📖 Read in bed" },
    { k: "meditation", n: "🧘 Meditated" }, { k: "travel", n: "✈️ Travel" }
  ];

  function renderYou() {
    var all = nights();
    // streak
    var streak = 0;
    for (var i = 0; ; i++) {
      var d = new Date(); d.setDate(d.getDate() - i);
      var key = dayKey(d.getTime());
      var hit = all.some(function (n) { return dayKey(n.end || n.start) === key; });
      if (hit) streak++;
      else if (i > 0) break;
      else if (i === 0) continue;   // today may not be tracked yet
      if (i > 400) break;
    }
    $("streak-val").innerHTML = streak + "<small>nights tracked in a row</small>";
    $("streak-emoji").textContent = streak >= 30 ? "🏆" : streak >= 7 ? "🔥" : streak >= 3 ? "✨" : "🌙";

    // insights: compare quality on tagged vs untagged nights
    var box = $("insights");
    var tagged = all.filter(function (n) { return n.tags && n.tags.length; });
    var out = [];
    if (all.length < 3) {
      out.push(["🌱", "Track at least three nights and Rested will start finding patterns in your own data."]);
    } else {
      TAGS.forEach(function (t) {
        var withT = all.filter(function (n) { return (n.tags || []).indexOf(t.k) >= 0; });
        var without = all.filter(function (n) { return (n.tags || []).indexOf(t.k) < 0; });
        if (withT.length < 2 || without.length < 2) return;
        var a = withT.reduce(function (s, n) { return s + n.quality; }, 0) / withT.length;
        var b = without.reduce(function (s, n) { return s + n.quality; }, 0) / without.length;
        var diff = Math.round(a - b);
        if (Math.abs(diff) < 4) return;
        out.push([diff < 0 ? "⚠️" : "✅",
          "Your quality is <b>" + Math.abs(diff) + "% " + (diff < 0 ? "lower" : "higher") +
          "</b> on nights after " + t.n.replace(/^\S+\s/, "").toLowerCase() +
          " (" + withT.length + " night" + (withT.length > 1 ? "s" : "") + ")."]);
      });
      // bedtime consistency
      if (all.length >= 5) {
        var hrs = all.map(function (n) {
          var d = new Date(n.start), h = d.getHours() + d.getMinutes() / 60;
          return h < 12 ? h + 24 : h;
        });
        var m = hrs.reduce(function (a, b) { return a + b; }, 0) / hrs.length;
        var sd = Math.sqrt(hrs.reduce(function (a, b) { return a + (b - m) * (b - m); }, 0) / hrs.length);
        if (sd > 1.0) out.push(["🕰️", "Your bedtime swings by about <b>" + sd.toFixed(1) + " hours</b>. Narrowing that is usually the single biggest win."]);
        else out.push(["🕰️", "Your bedtime is steady to within <b>" + sd.toFixed(1) + " hours</b>. That consistency is doing a lot of work for you."]);
      }
      // duration
      var avgA = all.reduce(function (s, n) { return s + n.asleep; }, 0) / all.length / 60;
      if (avgA < 6.5) out.push(["⏳", "You average <b>" + avgA.toFixed(1) + "h</b> asleep. Most adults need 7–9."]);
      if (!tagged.length) out.push(["🏷️", "Tag a few mornings (coffee, alcohol, exercise…) and Rested can tell you what actually changes your sleep."]);
    }
    box.innerHTML = out.slice(0, 6).map(function (o) {
      return '<div class="insight"><div class="ic">' + o[0] + '</div><div class="tx">' + o[1] + "</div></div>";
    }).join("");
  }

  /* ======================================================================
     REPORT + JOURNAL
     ====================================================================== */
  function openReport(night) {
    var d = new Date(night.end || night.start);
    var days = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"];
    $("rep-title").textContent = days[d.getDay()];
    var b = $("rep-body");
    b.innerHTML =
      '<div class="spread" style="margin-bottom:16px">' +
        '<div><div class="lbl">Quality</div><div class="bigstat mono" style="color:var(--accent)">' + night.quality + '%</div></div>' +
        '<div><div class="lbl">In bed</div><div class="bigstat mono">' + fmtHM(night.inBed) + '</div></div>' +
        '<div><div class="lbl">Asleep</div><div class="bigstat mono">' + fmtHM(night.asleep) + '</div></div>' +
      '</div>' +
      '<div class="lbl" style="margin-bottom:6px">Estimated sleep stages</div>' +
      '<canvas class="chart" id="rep-hyp"></canvas>' +
      '<div class="legend" id="rep-leg"></div>' +
      '<div class="card" style="margin-top:16px;background:var(--card2)">' +
        '<div class="spread"><span class="note">Fell asleep in</span><b class="mono">' + Math.round(night.onsetMin) + ' min</b></div>' +
        '<div class="spread" style="margin-top:8px"><span class="note">Times woken</span><b class="mono">' + night.awakenings + '</b></div>' +
        '<div class="spread" style="margin-top:8px"><span class="note">Sleep efficiency</span><b class="mono">' + Math.round(night.efficiency * 100) + '%</b></div>' +
        '<div class="spread" style="margin-top:8px"><span class="note">Went to bed</span><b class="mono">' + fmtClock(night.start) + '</b></div>' +
        '<div class="spread" style="margin-top:8px"><span class="note">Got up</span><b class="mono">' + fmtClock(night.end) + '</b></div>' +
      '</div>' +
      (night.tags && night.tags.length
        ? '<div class="row wrap" style="margin-top:12px">' + night.tags.map(function (t) {
            var f = TAGS.filter(function (x) { return x.k === t; })[0];
            return '<span class="chip on">' + (f ? f.n : t) + "</span>";
          }).join("") + "</div>"
        : "") +
      '<button class="btn ghost" id="rep-tags" style="margin-top:14px">🏷️ Edit tags for this night</button>' +
      '<div class="disclaimer">Stage estimates come from movement and sound, not brain activity. ' +
      'Treat the shape of the night as a guide, not a measurement.</div>';

    $("report").classList.add("on");
    requestAnimationFrame(function () {
      drawHypnogram($("rep-hyp"), night);
      $("rep-leg").innerHTML = [
        ["Awake", night.awakeMin, STAGE_COL[0]], ["Light", night.lightMin, STAGE_COL[1]],
        ["Deep", night.deepMin, STAGE_COL[2]], ["Dream", night.remMin, STAGE_COL[3]]
      ].map(function (m) {
        return '<div><i style="background:' + m[2] + '"></i>' + m[0] + " <b>" + fmtHM(m[1]) + "</b></div>";
      }).join("");
    });
    $("rep-tags").addEventListener("click", function () { openTags(night); });
  }

  var tagTarget = null;
  function openTags(night) {
    tagTarget = night;
    var g = $("tag-grid");
    g.innerHTML = "";
    TAGS.forEach(function (t) {
      var b = document.createElement("button");
      b.className = "chip" + ((night.tags || []).indexOf(t.k) >= 0 ? " on" : "");
      b.textContent = t.n;
      b.addEventListener("click", function () {
        night.tags = night.tags || [];
        var i = night.tags.indexOf(t.k);
        if (i >= 0) night.tags.splice(i, 1); else night.tags.push(t.k);
        b.classList.toggle("on");
      });
      g.appendChild(b);
    });
    var m = $("mood-grid");
    m.innerHTML = "";
    ["😩", "😐", "🙂", "😃", "🤩"].forEach(function (e, i) {
      var b = document.createElement("button");
      b.className = "chip" + (night.mood === i + 1 ? " on" : "");
      b.style.fontSize = "20px";
      b.textContent = e;
      b.addEventListener("click", function () {
        night.mood = i + 1;
        Array.prototype.forEach.call(m.children, function (c) { c.classList.remove("on"); });
        b.classList.add("on");
      });
      m.appendChild(b);
    });
    $("tagsheet").classList.add("on");
  }

  /* ======================================================================
     UI WIRING
     ====================================================================== */
  Array.prototype.forEach.call(document.querySelectorAll("#tabs button"), function (b) {
    b.addEventListener("click", function () {
      Array.prototype.forEach.call(document.querySelectorAll("#tabs button"), function (x) { x.classList.remove("on"); });
      Array.prototype.forEach.call(document.querySelectorAll(".view"), function (x) { x.classList.remove("on"); });
      b.classList.add("on");
      $("v-" + b.dataset.v).classList.add("on");
      if (b.dataset.v === "stats") renderStats();
      if (b.dataset.v === "you") renderYou();
      if (b.dataset.v === "sounds") renderSounds();
    });
  });

  $("start-btn").addEventListener("click", startSession);
  $("stop-btn").addEventListener("click", function () { endSession(); });
  $("al-stop").addEventListener("click", function () { Audio2.stopAlarm(); endSession(); });
  $("al-snooze").addEventListener("click", function () {
    Audio2.stopAlarm();
    $("alarm-screen").classList.remove("on");
    alarmFired = false;
    if (session) session.alarmAt = Date.now() + 9 * 60000;
  });
  $("see-report").addEventListener("click", function () {
    var l = nights()[0]; if (l) openReport(l);
  });
  $("rep-close").addEventListener("click", function () { $("report").classList.remove("on"); });
  $("tag-save").addEventListener("click", function () {
    save(); $("tagsheet").classList.remove("on"); render();
    toast("Saved — insights update as you add more nights.");
  });

  $("alarm-time").addEventListener("change", function () { db.alarm = this.value; save(); renderTonight(); });
  $("win-range").addEventListener("input", function () {
    db.window = +this.value;
    $("win-lbl").textContent = db.window > 0 ? db.window + " minutes before" : "Off — ring exactly on time";
    save();
  });
  $("smart-sw").addEventListener("click", function () {
    db.smart = !db.smart; this.classList.toggle("on", db.smart); save();
    $("alarm-note").textContent = db.smart ? "Smart window: wakes you in light sleep" : "Rings exactly at the set time";
  });
  $("alarm-sw").addEventListener("click", function () {
    db.alarmOn = !db.alarmOn; this.classList.toggle("on", db.alarmOn); save();
  });

  // ---- sounds
  function sceneCard(key, sc, onPick, current) {
    var locked = IS_FREE && sc.pro;
    var b = document.createElement("button");
    b.className = "chip" + (current === key ? " on" : "");
    b.style.cssText = "display:flex;align-items:center;gap:10px;width:100%;text-align:left;margin-bottom:8px;padding:14px 16px;border-radius:16px;font-size:15px" +
      (locked ? ";opacity:.5" : "");
    b.innerHTML = '<span style="font-size:20px">' + sc.icon + "</span>" + sc.name +
      (locked ? '<span style="margin-left:auto;font-size:12px">🔒 Pro</span>' : "");
    b.addEventListener("click", function () {
      if (locked) { toast("Unlock Rested Pro for all soundscapes."); return; }
      onPick(key);
    });
    return b;
  }
  function renderSounds() {
    var g = $("sound-grid");
    g.innerHTML = "";
    g.appendChild(sceneCard("none", { name: "None", icon: "🔇", pro: false }, function () {
      db.sound = "none"; save(); Audio2.stopScene(); renderSounds(); renderTonight();
    }, db.sound));
    Object.keys(Audio2.SCENES).forEach(function (k) {
      g.appendChild(sceneCard(k, Audio2.SCENES[k], function (key) {
        db.sound = key; save();
        Audio2.playScene(key, db.volume / 100, db.fade);
        renderSounds(); renderTonight();
        toast("Playing " + Audio2.SCENES[key].name.toLowerCase() + " — tap Stop to end.");
      }, db.sound));
    });
    $("vol-range").value = db.volume;
    $("vol-val").textContent = db.volume + "%";
    $("fade-range").value = db.fade;
    $("fade-lbl").textContent = db.fade > 0 ? db.fade + " minutes" : "Never — play all night";
  }
  $("vol-range").addEventListener("input", function () {
    db.volume = +this.value; $("vol-val").textContent = db.volume + "%"; save();
    if (Audio2.scenePlaying()) Audio2.playScene(db.sound, db.volume / 100, db.fade);
  });
  $("fade-range").addEventListener("input", function () {
    db.fade = +this.value;
    $("fade-lbl").textContent = db.fade > 0 ? db.fade + " minutes" : "Never — play all night";
    save(); renderTonight();
  });
  $("stop-sound").addEventListener("click", function () { Audio2.stopScene(); toast("Sound stopped."); });

  $("pick-sound").addEventListener("click", function () {
    var g = $("sp-grid");
    g.innerHTML = "";
    g.appendChild(sceneCard("none", { name: "None", icon: "🔇", pro: false }, function () {
      db.sound = "none"; save(); Audio2.stopScene(); $("soundpick").classList.remove("on"); renderTonight();
    }, db.sound));
    Object.keys(Audio2.SCENES).forEach(function (k) {
      g.appendChild(sceneCard(k, Audio2.SCENES[k], function (key) {
        db.sound = key; save();
        Audio2.playScene(key, db.volume / 100, db.fade);
        setTimeout(function () { if (!session) Audio2.fadeScene(2); }, 6000);   // short preview
        $("soundpick").classList.remove("on"); renderTonight();
      }, db.sound));
    });
    $("soundpick").classList.add("on");
  });
  $("sp-close").addEventListener("click", function () {
    Audio2.stopScene(); $("soundpick").classList.remove("on");
  });

  // ---- range segments
  Array.prototype.forEach.call(document.querySelectorAll("#range-seg button"), function (b) {
    b.addEventListener("click", function () {
      Array.prototype.forEach.call(document.querySelectorAll("#range-seg button"), function (x) { x.classList.remove("on"); });
      b.classList.add("on");
      renderStats();
    });
  });

  // ---- breathing
  var brTimer = null;
  $("winddown-btn").addEventListener("click", function () { $("breathe").classList.add("on"); });
  $("br-close").addEventListener("click", function () {
    clearInterval(brTimer); $("breathe").classList.remove("on");
    $("br-circle").style.transform = "scale(1)";
  });
  $("br-start").addEventListener("click", function () {
    clearInterval(brTimer);
    var phases = [["Breathe in", 4, 1.42], ["Hold", 7, 1.42], ["Breathe out", 8, 0.72]];
    var pi = 0, left = phases[0][1], rounds = 0;
    function apply() {
      $("br-phase").textContent = phases[pi][0];
      $("br-count").textContent = left;
      $("br-circle").style.transitionDuration = phases[pi][1] + "s";
      $("br-circle").style.transform = "scale(" + phases[pi][2] + ")";
    }
    apply();
    brTimer = setInterval(function () {
      left--;
      if (left <= 0) {
        pi++;
        if (pi >= phases.length) {
          pi = 0; rounds++;
          if (rounds >= 4) {
            clearInterval(brTimer);
            $("br-phase").textContent = "Nicely done";
            $("br-count").textContent = "🌙";
            $("br-circle").style.transform = "scale(1)";
            return;
          }
        }
        left = phases[pi][1];
        apply();
      } else $("br-count").textContent = left;
    }, 1000);
  });

  // ---- data
  $("export-btn").addEventListener("click", function () {
    var blob = new Blob([JSON.stringify(db)], { type: "application/json" });
    var a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = "rested-backup-" + dayKey(Date.now()) + ".json";
    a.click();
    toast("Backup downloaded.");
  });
  $("import-btn").addEventListener("click", function () {
    var inp = document.createElement("input");
    inp.type = "file"; inp.accept = "application/json";
    inp.addEventListener("change", function () {
      var f = inp.files[0];
      if (!f) return;
      var r = new FileReader();
      r.onload = function () {
        try {
          var d = JSON.parse(r.result);
          if (!d.nights) throw new Error("bad");
          db = d; save(); render();
          toast("Imported " + d.nights.length + " nights.");
        } catch (e) { toast("That file doesn't look like a Rested backup."); }
      };
      r.readAsText(f);
    });
    inp.click();
  });
  $("wipe-btn").addEventListener("click", function () {
    if (!confirm("Delete all sleep data on this device? This cannot be undone.")) return;
    db = JSON.parse(JSON.stringify(DEFAULTS));
    save(); render();
    toast("All data cleared.");
  });

  Array.prototype.forEach.call(document.querySelectorAll(".modal"), function (m) {
    m.addEventListener("click", function (e) { if (e.target === m) m.classList.remove("on"); });
  });

  /* ======================================================================
     SYNTHETIC NIGHT — powers the sample data and the test suite
     ====================================================================== */
  function syntheticNight(daysAgo, opts) {
    opts = opts || {};
    var quality = opts.q != null ? opts.q : 0.55 + Math.random() * 0.4;
    var start = new Date();
    start.setDate(start.getDate() - daysAgo);
    start.setHours(22 + Math.floor(Math.random() * 2), Math.floor(Math.random() * 60), 0, 0);
    var hours = 6.2 + quality * 2.6;
    var nEp = Math.round(hours * 3600 / EPOCH_S);
    var eps = [];
    var onsetEp = Math.round((6 + (1 - quality) * 30) * 60 / EPOCH_S);
    var wakeLeft = 0;
    for (var i = 0; i < nEp; i++) {
      var a;
      if (i < onsetEp) a = 0.22 + Math.random() * 0.3;                    // settling
      else {
        var pos = (i - onsetEp) / (nEp - onsetEp);
        var cyc = ((i - onsetEp) * EPOCH_S / 60) % 90 / 90;
        var depth = Math.sin(cyc * Math.PI);                             // deep early in cycle
        var base = 0.045 + (1 - depth) * 0.05 + pos * 0.03;
        a = base + Math.random() * 0.035;
        // real awakenings last minutes, not seconds
        if (wakeLeft <= 0 && Math.random() < 0.004 * (1.3 - quality)) {
          wakeLeft = 3 + Math.floor(Math.random() * 8);
        }
        if (wakeLeft > 0) { a = 0.28 + Math.random() * 0.4; wakeLeft--; }
        else if (Math.random() < 0.02) a = 0.16 + Math.random() * 0.12;   // roll over
        if (pos > 0.985) a = 0.3 + Math.random() * 0.3;                   // morning stir
      }
      eps.push({ a: +clamp(a, 0, 1).toFixed(4), s: 0 });
    }
    var res = classify(eps);
    var night = summarise({
      id: start.getTime(), start: start.getTime(),
      end: start.getTime() + nEp * EPOCH_S * 1000,
      epochs: eps, stages: res.stages, onset: res.onset, finalWake: res.finalWake,
      tags: opts.tags || [], mood: opts.mood || 0, sample: true
    });
    return night;
  }

  function loadSample() {
    var tagPool = [["caffeine"], ["alcohol"], [], ["exercise"], ["stress", "screens"], [], ["exercise"], []];
    for (var d = 14; d >= 1; d--) {
      var t = tagPool[d % tagPool.length];
      var q = 0.5 + Math.random() * 0.42;
      if (t.indexOf("caffeine") >= 0 || t.indexOf("alcohol") >= 0) q -= 0.18;
      if (t.indexOf("exercise") >= 0) q += 0.10;
      db.nights.push(syntheticNight(d, { q: clamp(q, 0.25, 0.97), tags: t }));
    }
    save(); render();
    toast("Sample fortnight loaded — explore Stats and You.");
  }

  /* ======================================================================
     BOOT
     ====================================================================== */
  render();
  renderSounds();
  if (!db.nights.length) {
    var b = document.createElement("button");
    b.className = "btn ghost";
    b.id = "sample-btn";
    b.textContent = "👀 See a sample fortnight of data";
    b.addEventListener("click", function () { loadSample(); b.remove(); });
    $("v-sleep").insertBefore(b, $("winddown-btn").nextSibling);
  }
  addEventListener("resize", function () {
    if ($("v-stats").classList.contains("on")) renderStats();
  });

  window.DEV = {
    db: function () { return db; },
    state: function () {
      return {
        tracking: !!session, epochs: session ? session.epochs.length : 0,
        nights: db.nights.length, quality: db.nights.length ? nights()[0].quality : null,
        alarmFired: alarmFired, sound: db.sound, scene: Audio2.scenePlaying()
      };
    },
    sample: loadSample,
    synth: syntheticNight,
    addNight: function (daysAgo, opts) { db.nights.push(syntheticNight(daysAgo, opts)); save(); render(); },
    classify: classify,
    summarise: summarise,
    fireAlarm: fireAlarm,
    endSession: endSession,
    startSession: startSession,
    report: function () { var l = nights()[0]; if (l) openReport(l); return l; },
    wipe: function () { db = JSON.parse(JSON.stringify(DEFAULTS)); save(); render(); }
  };
})();
