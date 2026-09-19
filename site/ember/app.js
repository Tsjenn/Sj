/* Ember — a focus timer with a dragon. Everything stays on this device. */
(function () {
  "use strict";
  var KEY = "ember.v1";
  var CFG = (window.STORE && window.STORE.products && window.STORE.products.ember) || {};
  var BUY = (CFG.link && CFG.link !== "SET-ME") ? CFG.link : "";
  // Unlock keys are checked by SHA-256 against this list; the codes themselves are never in source.
  var KEY_HASHES = ["3f1c9e6b1d4e6d2e7c0a6a2c0d8b7f0b2a1c9e8d7f6a5b4c3d2e1f0a9b8c7d6e"];
  var STAGES = [
    { name: "egg", min: 0 }, { name: "hatchling", min: 60 }, { name: "drake", min: 300 },
    { name: "wyrm", min: 900 }, { name: "elder", min: 2400 }
  ];
  var COLOURS = [
    { id: "ember", body: "#C4552E", belly: "#F2B77E", eye: "#FFE7B0", free: true },
    { id: "moss", body: "#4F8A5B", belly: "#CFE3B3", eye: "#F7F3C9", free: true },
    { id: "slate", body: "#5D6B8A", belly: "#C9D2E6", eye: "#FFF3D6", free: true },
    { id: "rose", body: "#B2477A", belly: "#F4C4DA", eye: "#FFF0F6", free: false },
    { id: "gold", body: "#C79A2E", belly: "#F9E7A9", eye: "#FFFFFF", free: false },
    { id: "night", body: "#2E2447", belly: "#8F7BC2", eye: "#E8DDFF", free: false }
  ];
  var GRACE_MS = 10000;

  function blank() { return { name: "", colour: "ember", quest: 50, sound: 1, keyOk: false, sessions: [], questDays: {} }; }
  function load() { try { var s = JSON.parse(localStorage.getItem(KEY) || "null"); if (!s) return blank(); var b = blank(); for (var k in b) if (s[k] === undefined) s[k] = b[k]; return s; } catch (e) { return blank(); } }
  function save() { try { localStorage.setItem(KEY, JSON.stringify(S)); } catch (e) {} }
  var S = load();
  var $ = function (id) { return document.getElementById(id); };
  var pad = function (n) { return (n < 10 ? "0" : "") + n; };
  function ymd(d) { return d.getFullYear() + "-" + pad(d.getMonth() + 1) + "-" + pad(d.getDate()); }
  function today() { return ymd(new Date()); }
  var toastT; function toast(m) { var t = $("toast"); t.textContent = m; t.classList.add("on"); clearTimeout(toastT); toastT = setTimeout(function () { t.classList.remove("on"); }, 2200); }

  /* ---------- stats ---------- */
  function keptMinutes(day) { return S.sessions.filter(function (s) { return s.kept && (!day || s.date === day); }).reduce(function (a, s) { return a + s.min; }, 0); }
  function stageFor(min) { var st = STAGES[0]; STAGES.forEach(function (x) { if (min >= x.min) st = x; }); return st; }
  function stageIndex(min) { return STAGES.indexOf(stageFor(min)); }
  function streak() {
    var n = 0, d = new Date();
    if (!S.questDays[ymd(d)]) d.setDate(d.getDate() - 1); // today not done yet doesn't break the streak
    while (S.questDays[ymd(d)]) { n++; d.setDate(d.getDate() - 1); }
    return n;
  }

  /* ---------- dragon (canvas) ---------- */
  var cv = $("dragon"), cx = cv.getContext("2d"), t0 = performance.now(), mood = "idle", moodUntil = 0, embers = [];
  function colour() { return COLOURS.find(function (c) { return c.id === S.colour; }) || COLOURS[0]; }
  function drawDragon(now) {
    var W = cv.width, H = cv.height, time = (now - t0) / 1000, stage = stageIndex(keptMinutes());
    var c = colour(); cx.clearRect(0, 0, W, H);
    // ground glow
    var g = cx.createRadialGradient(W / 2, H * 0.82, 10, W / 2, H * 0.82, W * 0.5);
    g.addColorStop(0, "rgba(255,122,61," + (mood === "lit" ? 0.35 : 0.14) + ")"); g.addColorStop(1, "rgba(255,122,61,0)");
    cx.fillStyle = g; cx.fillRect(0, 0, W, H);
    // embers
    if (mood === "lit" && Math.random() < 0.35) embers.push({ x: W / 2 + (Math.random() - .5) * 220, y: H * 0.8, v: 40 + Math.random() * 60, s: 2 + Math.random() * 4, a: 1, dx: (Math.random() - .5) * 20 });
    embers = embers.filter(function (e) { return e.a > 0; });
    embers.forEach(function (e) { e.y -= e.v / 60; e.x += e.dx / 60; e.a -= 0.008; cx.globalAlpha = Math.max(0, e.a); cx.fillStyle = "#FFC27A"; cx.beginPath(); cx.arc(e.x, e.y, e.s, 0, 7); cx.fill(); });
    cx.globalAlpha = 1;
    var breathe = 1 + Math.sin(time * 1.6) * (mood === "lit" ? 0.03 : 0.018);
    var base = [0.28, 0.42, 0.55, 0.68, 0.8][stage], scale = base * breathe;
    cx.save(); cx.translate(W / 2, H * 0.78); cx.scale(scale, scale);
    if (stage === 0) { // egg
      cx.fillStyle = c.belly; cx.beginPath(); cx.ellipse(0, -160, 150, 200, 0, 0, 7); cx.fill();
      cx.fillStyle = c.body; cx.globalAlpha = .55;
      for (var i = 0; i < 7; i++) { cx.beginPath(); cx.ellipse(-90 + (i % 4) * 60, -260 + Math.floor(i / 4) * 110 + (i % 2) * 40, 22, 30, 0.4, 0, 7); cx.fill(); }
      cx.globalAlpha = 1;
      if (mood === "lit") { cx.strokeStyle = "#FFC27A"; cx.lineWidth = 6; cx.beginPath(); cx.moveTo(-20, -240); cx.lineTo(10, -190); cx.lineTo(-15, -150); cx.stroke(); }
      cx.restore(); return;
    }
    var wob = Math.sin(time * 2.2) * 6;
    // tail
    cx.strokeStyle = c.body; cx.lineWidth = 46; cx.lineCap = "round"; cx.beginPath(); cx.moveTo(-120, -60); cx.quadraticCurveTo(-320, -40 + wob, -360, -200 + wob * 2); cx.stroke();
    cx.fillStyle = c.body; cx.beginPath(); cx.moveTo(-372, -230 + wob * 2); cx.lineTo(-330, -190 + wob * 2); cx.lineTo(-395, -175 + wob * 2); cx.closePath(); cx.fill();
    // wings from drake up
    if (stage >= 2) {
      var flap = Math.sin(time * (mood === "lit" ? 4 : 1.4)) * 30;
      cx.fillStyle = c.body; cx.globalAlpha = .9;
      [[-1, 1]].forEach(function () {
        cx.beginPath(); cx.moveTo(-40, -220); cx.quadraticCurveTo(-260, -420 + flap, -330, -300 + flap); cx.quadraticCurveTo(-240, -300 + flap * .5, -180, -230); cx.closePath(); cx.fill();
        cx.beginPath(); cx.moveTo(40, -220); cx.quadraticCurveTo(220, -420 + flap, 300, -320 + flap); cx.quadraticCurveTo(200, -300 + flap * .5, 150, -230); cx.closePath(); cx.fill();
      });
      cx.globalAlpha = 1;
    }
    // body
    cx.fillStyle = c.body; cx.beginPath(); cx.ellipse(0, -150, 190, 150, 0, 0, 7); cx.fill();
    cx.fillStyle = c.belly; cx.beginPath(); cx.ellipse(10, -120, 120, 100, 0, 0, 7); cx.fill();
    // legs
    cx.fillStyle = c.body; [[-110, 0], [90, 0]].forEach(function (p) { cx.beginPath(); cx.ellipse(p[0], -20, 60, 40, 0, 0, 7); cx.fill(); });
    // neck + head
    var nod = mood === "fed" ? Math.sin(time * 8) * 10 : 0;
    cx.beginPath(); cx.ellipse(150, -250 + nod, 70, 90, -0.4, 0, 7); cx.fill();
    cx.beginPath(); cx.ellipse(215, -330 + nod, 95, 78, 0.1, 0, 7); cx.fill();
    cx.fillStyle = c.belly; cx.beginPath(); cx.ellipse(275, -300 + nod, 55, 32, 0.15, 0, 7); cx.fill(); // snout
    // horns from wyrm up
    if (stage >= 3) { cx.fillStyle = c.belly; cx.beginPath(); cx.moveTo(190, -395 + nod); cx.lineTo(160, -470 + nod); cx.lineTo(215, -405 + nod); cx.fill(); cx.beginPath(); cx.moveTo(240, -400 + nod); cx.lineTo(250, -480 + nod); cx.lineTo(268, -395 + nod); cx.fill(); }
    // crown for elder
    if (stage >= 4) { cx.fillStyle = "#FFC27A"; for (var k = 0; k < 3; k++) { cx.beginPath(); cx.arc(180 + k * 35, -395 + nod, 9, 0, 7); cx.fill(); } }
    // eye (blink)
    var blink = (Math.sin(time * 0.9) > 0.985) ? 0.15 : 1;
    cx.fillStyle = c.eye; cx.beginPath(); cx.ellipse(235, -345 + nod, 18, 22 * blink, 0, 0, 7); cx.fill();
    cx.fillStyle = "#1B1220"; cx.beginPath(); cx.ellipse(239, -343 + nod, 8, 11 * blink, 0, 0, 7); cx.fill();
    // breath while lit
    if (mood === "lit") { cx.fillStyle = "rgba(255,194,122,.85)"; var f = 0.8 + Math.sin(time * 9) * 0.2; cx.beginPath(); cx.ellipse(345, -300 + nod, 28 * f, 14 * f, 0, 0, 7); cx.fill(); }
    cx.restore();
  }
  function loop(now) { drawDragon(now); if (mood === "fed" && now > moodUntil) mood = timer ? "lit" : "idle"; requestAnimationFrame(loop); }
  requestAnimationFrame(loop);

  /* ---------- timer ---------- */
  var minutes = 25, timer = null, endAt = 0, hiddenAt = 0, wandered = false;
  function fmt(ms) { var s = Math.max(0, Math.ceil(ms / 1000)); return pad(Math.floor(s / 60)) + ":" + pad(s % 60); }
  function renderClock() {
    if (!timer) { $("clock").textContent = pad(minutes) + ":00"; $("ring").style.width = "0%"; return; }
    var left = endAt - Date.now(); $("clock").textContent = fmt(left);
    $("ring").style.width = (100 * (1 - left / (minutes * 60000))) + "%";
    if (left <= 0) finish(true);
  }
  function start() {
    if (timer) return;
    endAt = Date.now() + minutes * 60000; wandered = false; mood = "lit";
    timer = setInterval(renderClock, 250); renderClock();
    $("start").hidden = true; $("giveup").hidden = false; $("status").textContent = "The ember is lit. Stay here.";
    document.querySelectorAll("#lens .chip").forEach(function (c) { c.disabled = true; });
    try { if (navigator.wakeLock) navigator.wakeLock.request("screen").then(function (l) { wake = l; }).catch(function () {}); } catch (e) {}
  }
  var wake = null;
  function finish(kept) {
    clearInterval(timer); timer = null; if (wake) { try { wake.release(); } catch (e) {} wake = null; }
    var sess = { date: today(), min: minutes, kept: !!kept, at: Date.now() };
    S.sessions.push(sess); if (S.sessions.length > 2000) S.sessions = S.sessions.slice(-2000);
    var before = stageIndex(keptMinutes() - (kept ? minutes : 0));
    if (kept) {
      var t = keptMinutes(today()); if (t >= S.quest) S.questDays[today()] = true;
      mood = "fed"; moodUntil = performance.now() + 4000; chime();
      var after = stageIndex(keptMinutes());
      $("doneH").textContent = after > before ? "It grew." : "Fed.";
      $("doneP").textContent = (after > before ? (S.name || "Your dragon") + " is now a " + STAGES[after].name + ". " : "") + minutes + " minutes kept. " + (S.questDays[today()] ? "Today's quest is done." : (S.quest - t) + " minutes left on today's quest.");
    } else {
      mood = "idle";
      $("doneH").textContent = "The ember faded."; $("doneP").textContent = "Nothing fed the dragon this time. Light it again when you are ready to stay.";
    }
    save(); $("done").classList.add("on");
    $("start").hidden = false; $("giveup").hidden = true; $("status").textContent = "Choose a length and light the ember.";
    document.querySelectorAll("#lens .chip").forEach(function (c) { c.disabled = false; });
    renderClock(); renderAll();
  }
  $("doneOk").addEventListener("click", function () { $("done").classList.remove("on"); });
  $("start").addEventListener("click", start);
  $("giveup").addEventListener("click", function () { if (timer && confirm("Give up this session? The ember fades and the dragon goes unfed.")) finish(false); });
  document.querySelectorAll("#lens .chip").forEach(function (c) { c.addEventListener("click", function () { if (timer) return; minutes = +c.dataset.m; document.querySelectorAll("#lens .chip").forEach(function (x) { x.classList.toggle("on", x === c); }); renderClock(); }); });
  document.addEventListener("visibilitychange", function () {
    if (!timer) return;
    if (document.hidden) { hiddenAt = Date.now(); }
    else if (hiddenAt && Date.now() - hiddenAt > GRACE_MS) { hiddenAt = 0; finish(false); }
    else hiddenAt = 0;
  });
  // if the page was hidden past the grace and the timer would have ended meanwhile, judge on return
  setInterval(function () { if (timer && document.hidden && hiddenAt && Date.now() - hiddenAt > GRACE_MS) { wandered = true; } }, 1000);
  document.addEventListener("visibilitychange", function () { if (!document.hidden && wandered && timer) { wandered = false; finish(false); } });

  function chime() {
    if (!S.sound) return;
    try { var A = new (window.AudioContext || window.webkitAudioContext)(); var t = A.currentTime;
      [523.25, 659.25, 783.99].forEach(function (f, i) { var o = A.createOscillator(), g = A.createGain(); o.type = "sine"; o.frequency.value = f; g.gain.setValueAtTime(0, t + i * .18); g.gain.linearRampToValueAtTime(.18, t + i * .18 + .03); g.gain.exponentialRampToValueAtTime(.001, t + i * .18 + 1.1); o.connect(g); g.connect(A.destination); o.start(t + i * .18); o.stop(t + i * .18 + 1.2); });
    } catch (e) {}
  }

  /* ---------- views ---------- */
  var view = "focus";
  function show(v) { view = v; document.querySelectorAll(".view").forEach(function (el) { el.classList.toggle("on", el.id === "v-" + v); }); document.querySelectorAll(".tabs button").forEach(function (b) { b.classList.toggle("on", b.dataset.view === v); }); window.scrollTo(0, 0); renderAll(); }
  document.querySelectorAll(".tabs button").forEach(function (b) { b.addEventListener("click", function () { show(b.dataset.view); }); });

  function renderAll() {
    var all = keptMinutes(), td = keptMinutes(today()), st = stageFor(all);
    $("dName").textContent = S.name || "Unnamed"; $("dStage").textContent = st.name;
    $("streak").innerHTML = "streak <b>" + streak() + "</b> · today <b>" + td + "</b> min";
    $("questText").textContent = td >= S.quest ? "Done — " + td + " of " + S.quest + " minutes" : td + " of " + S.quest + " minutes kept";
    $("questBar").style.width = Math.min(100, 100 * td / S.quest) + "%";
    // hoard
    var kept = S.sessions.filter(function (s) { return s.kept; }).length, faded = S.sessions.length - kept;
    $("hAll").textContent = all >= 120 ? (all / 60).toFixed(1) + " h" : all + " min"; $("hToday").textContent = td + " min";
    $("hKept").textContent = kept + " / " + faded; $("hStreak").textContent = streak();
    var byDay = {}; S.sessions.forEach(function (s) { if (s.kept) byDay[s.date] = (byDay[s.date] || 0) + s.min; });
    var best = Object.keys(byDay).sort(function (a, b) { return byDay[b] - byDay[a]; })[0];
    $("hBest").textContent = best ? byDay[best] + " min · " + best : "—";
    var html = "", d = new Date(), max = 1; var days = [];
    for (var i = 6; i >= 0; i--) { var dd = new Date(d.getFullYear(), d.getMonth(), d.getDate() - i); var k = ymd(dd); days.push([k, byDay[k] || 0, ["S","M","T","W","T","F","S"][dd.getDay()]]); max = Math.max(max, byDay[k] || 0); }
    days.forEach(function (x) { html += "<div><i><b style=\"height:" + Math.round(100 * x[1] / max) + "%\"></b></i>" + x[2] + "</div>"; });
    $("week").innerHTML = html;
    // den
    $("name").value = S.name; $("keyState").textContent = S.keyOk ? "Unlocked on this phone." : "No key entered. Everything that matters works without one.";
    $("buyKey").hidden = !BUY || S.keyOk; if (BUY) $("buyKey").href = BUY;
    $("swatches").innerHTML = COLOURS.map(function (c) { var locked = !c.free && !S.keyOk; return '<button class="sw' + (S.colour === c.id ? " on" : "") + (locked ? " lock" : "") + '" data-c="' + c.id + '" style="background:radial-gradient(circle at 35% 35%,' + c.belly + ',' + c.body + ' 70%)" aria-label="' + c.id + '"></button>'; }).join("");
    $("swatches").querySelectorAll(".sw").forEach(function (b) { b.addEventListener("click", function () { var c = COLOURS.find(function (x) { return x.id === b.dataset.c; }); if (!c.free && !S.keyOk) { toast("That colour needs the Ember key"); return; } S.colour = c.id; save(); renderAll(); }); });
    document.querySelectorAll("#questLens .chip").forEach(function (c) { c.classList.toggle("on", +c.dataset.q === S.quest); });
    document.querySelectorAll("#soundLens .chip").forEach(function (c) { c.classList.toggle("on", +c.dataset.s === S.sound); });
  }
  document.querySelectorAll("#questLens .chip").forEach(function (c) { c.addEventListener("click", function () { S.quest = +c.dataset.q; save(); renderAll(); }); });
  document.querySelectorAll("#soundLens .chip").forEach(function (c) { c.addEventListener("click", function () { S.sound = +c.dataset.s; save(); renderAll(); }); });
  $("saveDen").addEventListener("click", function () { S.name = $("name").value.trim().slice(0, 18); save(); renderAll(); toast("Saved"); });
  async function sha256(s) { var b = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(s)); return Array.from(new Uint8Array(b)).map(function (x) { return x.toString(16).padStart(2, "0"); }).join(""); }
  $("keySave").addEventListener("click", function () {
    var k = $("key").value.trim().toUpperCase(); if (!k) return;
    if (!window.crypto || !crypto.subtle) { toast("This browser cannot check keys"); return; }
    sha256(k).then(function (h) { if (KEY_HASHES.indexOf(h) >= 0) { S.keyOk = true; save(); $("key").value = ""; renderAll(); toast("Unlocked"); } else toast("That key is not right"); });
  });
  $("exportBtn").addEventListener("click", function () { var blob = new Blob([JSON.stringify(S)], { type: "application/json" }); var a = document.createElement("a"); a.href = URL.createObjectURL(blob); a.download = "ember-" + today() + ".json"; document.body.appendChild(a); a.click(); a.remove(); });
  $("importBtn").addEventListener("click", function () { $("importFile").click(); });
  $("importFile").addEventListener("change", function () { var f = this.files[0]; if (!f) return; var r = new FileReader(); r.onload = function () { try { var j = JSON.parse(r.result); if (!j || !("sessions" in j)) throw 0; S = j; var b = blank(); for (var k in b) if (S[k] === undefined) S[k] = b[k]; save(); renderAll(); toast("Imported"); } catch (e) { toast("That file isn't an Ember export"); } }; r.readAsText(f); this.value = ""; });
  $("wipe").addEventListener("click", function () { if (!confirm("Delete everything Ember has stored on this phone?")) return; S = blank(); try { localStorage.removeItem(KEY); } catch (e) {} renderAll(); show("focus"); toast("Deleted"); });

  if ("serviceWorker" in navigator && location.protocol === "https:") navigator.serviceWorker.register("sw.js").catch(function () {});
  // test hook: lets an automated check shorten a session without waiting
  window.__ember = { finish: finish, start: start, state: function () { return S; }, setMinutes: function (m) { minutes = m; renderClock(); } };
  renderClock(); renderAll();
})();
