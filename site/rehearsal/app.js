/* Rehearsal — a three-minute daily rehearsal, read aloud, and one step.
   Free stories are assembled on the device. AI-written stories go through the
   owner's Worker only when an unlock code is present. Nothing else leaves. */
(function () {
  "use strict";
  var KEY = "rehearsal.v1";
  var CFG = (window.STORE && window.STORE.products && window.STORE.products.rehearsal) || {};
  var WRITER = (CFG.writer && CFG.writer !== "SET-ME") ? CFG.writer : "";
  var BUY = (CFG.link && CFG.link !== "SET-ME") ? CFG.link : "";

  function blank() { return { profile: null, stories: [], steps: {}, settings: { rate: 0.95, voice: "" }, code: "" }; }
  function load() {
    try { var s = JSON.parse(localStorage.getItem(KEY) || "null"); if (!s) return blank();
      var b = blank(); for (var k in b) if (s[k] === undefined) s[k] = b[k]; return s; } catch (e) { return blank(); }
  }
  function save() { try { localStorage.setItem(KEY, JSON.stringify(S)); } catch (e) { toast("Could not save — storage is full or blocked"); } }
  var S = load();

  var $ = function (id) { return document.getElementById(id); };
  var pad = function (n) { return (n < 10 ? "0" : "") + n; };
  function ymd(d) { return d.getFullYear() + "-" + pad(d.getMonth() + 1) + "-" + pad(d.getDate()); }
  function today() { return ymd(new Date()); }
  var MONTHS = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"];
  function nice(s) { var p = s.split("-"); return +p[2] + " " + MONTHS[+p[1] - 1] + " " + p[0]; }
  var toastT; function toast(m) { var t = $("toast"); t.textContent = m; t.classList.add("on"); clearTimeout(toastT); toastT = setTimeout(function () { t.classList.remove("on"); }, 2400); }
  function esc(s) { return String(s).replace(/[&<>"]/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]; }); }

  /* ---------- seeded picking, so "today's" story is stable for the day ---------- */
  function rng(seed) { var x = 0; for (var i = 0; i < seed.length; i++) x = (x * 31 + seed.charCodeAt(i)) >>> 0; return function () { x = (x * 1664525 + 1013904223) >>> 0; return x / 4294967296; }; }
  function pick(r, arr) { return arr[Math.floor(r() * arr.length)]; }

  /* ---------- the on-device story engine ---------- */
  var SETTINGS = {
    kitchen: { where: "in my kitchen", routine: ["I rinse the cup, dry it, and put it back in the wrong place, the way I always do.", "The radio is on low and I am only half listening."], open: ["The kettle clicks off and the kitchen goes quiet again.", "Morning light lies across the counter in a long stripe.", "There is a bowl in the sink from last night and I do not mind it."], sense: ["The tiles are cool under my feet.", "The window is open a crack and the street is starting up outside.", "The coffee smells the way it only does in the first minute."] },
    train: { where: "on the train", routine: ["I have a book open and have read the same page twice, happily.", "The announcement names the next stop and nobody looks up."], open: ["The train pulls out and the platform slides away.", "I get a seat by the window, which almost never happens.", "The carriage is half full and everyone is somewhere else in their head."], sense: ["The glass is cool against my shoulder.", "Someone two rows up laughs at their phone.", "The doors chime at every stop, the same two notes."] },
    office: { where: "at work", routine: ["I open the laptop and the first email is nothing, which is a kind of gift.", "Someone has restocked the biscuits. Small mercies."], open: ["The office is still mostly empty when I get in.", "The lift doors open on my floor and the lights come up one bank at a time.", "My desk looks the same as it did last month, which is somehow the point."], sense: ["The air-conditioning hums the way it always has.", "A printer starts up somewhere down the corridor.", "My mug has a chip on the rim I have stopped noticing."] },
    cafe: { where: "at the café", routine: ["I have a notebook out and have written nothing in it, and that is fine.", "The couple by the window are arguing gently about a holiday."], open: ["The café has the corner table free, the one with the wobble.", "The barista nods at me before I order; I have been here that often.", "Rain has just stopped and the pavement outside is bright."], sense: ["The cup is too hot to hold properly for the first minute.", "There is music on low, something I half recognise.", "A chair scrapes and someone apologises to no one."] },
    sea: { where: "by the sea", routine: ["I walk to where the sand goes dark and wet and stop there.", "A dog runs past with something it should not have."], open: ["The tide is out and the sand is ridged and firm.", "It is early enough that the beach belongs to the dog walkers.", "The horizon is a flat clean line and the light has not decided what colour to be."], sense: ["Salt on my lips before I have even reached the water.", "The wind takes the ends of my hair and does what it likes with them.", "Gulls, and then the long hush of a wave settling."] },
    home: { where: "in our living room", routine: ["I fold the blanket and unfold it again to sit under it.", "The plant on the shelf has a new leaf, which I only notice now."], open: ["The living room is a mess of Sunday: cushions on the floor, a mug on the bookshelf.", "Evening, and the lamp on the side table is the only light on.", "The fan turns slowly and the curtains move with it."], sense: ["The sofa has the dip in it where I always sit.", "Someone has left the television on mute.", "The floor is warm where the afternoon sun was."] }
  };
  var WITNESS = {
    "my mother": { says: ["\"You look different,\" she says. \"Lighter.\"", "She does not say anything for a while, and then, \"I told your father you would.\"", "\"So,\" she says, and lets the word sit there, pleased."], name: "she" },
    "my partner": { says: ["\"Say it again,\" they say, \"I want to hear you say it like it's normal.\"", "They just look at me over the top of the cup and grin.", "\"We did it,\" they say, and the we is the part I hold on to."], name: "they" },
    "an old friend": { says: ["\"Remember when you said you'd never?\" they say. \"You said never.\"", "They shake their head slowly, the way they do when they are impressed and will not admit it.", "\"Okay,\" they say. \"Okay. Tell me everything.\""], name: "they" },
    "a colleague": { says: ["\"I heard,\" they say, quietly, so the room does not. \"Good.\"", "They put a coffee down beside me without being asked.", "\"About time,\" they say, which from them is a speech."], name: "they" },
    "a stranger": { says: ["Someone I do not know says \"congratulations\" to the person next to them, and I take it anyway.", "A stranger holds the door and I realise I am smiling at nothing.", "The woman opposite catches my eye and smiles like she knows, though she cannot."], name: "they" }
  };
  var MIDDLE = [
    "It is not the big moment I imagined. It is a Tuesday. That is what surprises me: how ordinary it feels to have it.",
    "I keep waiting for it to feel like a film, and it does not. It feels like a fact. I have it, and the day carries on.",
    "The strange thing is how little I think about it now. It has become the floor I stand on instead of the thing I reach for."
  ];
  var WHY_LEAD = ["The part that matters is not the thing itself. It is this:", "If I am honest, this is why I wanted it:", "What it was really for, all along:"];
  var STEP_LEAD = ["I remember the first thing I did, which was small enough to seem like nothing at the time:", "It started, if I trace it back, with one small step:", "There was a day I almost did not bother, and then I did the one small thing:"];
  var CLOSE = ["I put the phone face down and let the moment be as plain as it wants to be.", "The light moves a little. I stay where I am for one more minute.", "Nothing else happens. That is the whole of it, and it is enough.", "Someone says my name, and I answer, and the day goes on."];
  var BODY = ["My shoulders are down. I notice that. For a long time they lived somewhere up near my ears, and I did not know it until they stopped.", "I breathe out and it goes all the way to the bottom, the way it does when there is nothing waiting behind it.", "There is a looseness in my hands. I keep noticing my hands."];
  var TITLES = ["The Tuesday it was already true", "A plain morning, six months on", "What it felt like from the inside", "The day nobody made a fuss", "Holding it like an ordinary thing", "The quiet version of getting there"];

  function lower1(s) { if (!s) return s; if (/^(I |I'|I,)/.test(s)) return s; return s.charAt(0).toLowerCase() + s.slice(1); }
  function pick2(r, arr, not) { var c = arr.filter(function (x) { return x !== not; }); return pick(r, c.length ? c : arr); }
  function stripEnd(s) { return String(s || "").trim().replace(/[.!?]+$/, ""); }
  function firstPerson(wish) {
    var w = stripEnd(wish);
    if (!w) return "";
    return /^(i |i'|we |my |our )/i.test(w) ? w : "I have it: " + w;
  }
  function buildStory(p, seed) {
    var r = rng(seed);
    var st = SETTINGS[p.setting] || SETTINGS.kitchen;
    var wt = WITNESS[p.witness] || WITNESS["my mother"];
    var wish = firstPerson(p.wish);
    var paras = [], sense1 = pick(r, st.sense);
    paras.push(pick(r, st.open) + " " + sense1 + " It is " + (p.when || "six months from now") + ", and " + lower1(wish) + ".");
    paras.push(pick(r, st.routine) + " " + pick(r, MIDDLE));
    paras.push(pick(r, BODY));
    paras.push((p.witness || "my mother").replace(/^my /, "My ").replace(/^an /, "An ").replace(/^a /, "A ") + " is here, " + st.where + ". " + pick(r, wt.says));
    if (p.why) paras.push(pick(r, WHY_LEAD) + " " + lower1(stripEnd(p.why)) + ". I did not say that out loud at the time. I say it now, to myself, " + st.where + ".");
    if (p.step) paras.push(pick(r, STEP_LEAD) + " " + lower1(stripEnd(p.step)) + ". That was all. Everything after it was just the next small thing.");
    paras.push(pick2(r, st.sense, sense1) + " " + pick(r, CLOSE));
    return { title: pick(r, TITLES), paragraphs: paras, source: "device" };
  }

  /* ---------- state helpers ---------- */
  function todayStory() {
    var t = today();
    for (var i = S.stories.length - 1; i >= 0; i--) if (S.stories[i].date === t && !S.stories[i].archived) return S.stories[i];
    return null;
  }
  function addStory(st, variant) {
    var s = { id: Date.now() + Math.floor(Math.random() * 1000), date: today(), title: st.title, paragraphs: st.paragraphs, source: st.source, fav: false, variant: variant || 0 };
    // keep only the newest story per day as "current"; older ones stay in library
    S.stories.forEach(function (x) { if (x.date === s.date) x.archived = true; });
    S.stories.push(s); if (S.stories.length > 400) S.stories = S.stories.slice(-400);
    save(); return s;
  }
  function ensureToday() {
    if (!S.profile) return null;
    var cur = todayStory();
    if (cur) return cur;
    return addStory(buildStory(S.profile, today() + "|" + S.profile.wish), 0);
  }

  /* ---------- views ---------- */
  var view = "today";
  function show(v) {
    if (!S.profile) v = "start";
    view = v;
    document.querySelectorAll(".view").forEach(function (el) { el.classList.toggle("on", el.id === "v-" + v); });
    document.querySelectorAll(".tabs button").forEach(function (b) { b.classList.toggle("on", b.dataset.view === v); });
    document.querySelector(".tabs").style.display = S.profile ? "" : "none";
    window.scrollTo(0, 0); render();
  }
  document.querySelectorAll(".tabs button").forEach(function (b) { b.addEventListener("click", function () { stopSpeech(); show(b.dataset.view); }); });

  /* ---------- onboarding ---------- */
  function chipGroup(id) {
    var g = $(id);
    g.querySelectorAll(".chip").forEach(function (c) { c.addEventListener("click", function () { g.querySelectorAll(".chip").forEach(function (x) { x.classList.remove("on"); }); c.classList.add("on"); }); });
    return function () { var on = g.querySelector(".chip.on"); return on ? on.dataset.v : ""; };
  }
  var getWhen = chipGroup("o_when"), getSetting = chipGroup("o_setting"), getWitness = chipGroup("o_witness");
  var getRate = chipGroup("rateChips");
  $("rateChips").addEventListener("click", function () { S.settings.rate = parseFloat(getRate()) || 0.95; save(); });
  $("o_go").addEventListener("click", function () {
    var wish = $("o_wish").value.trim();
    if (wish.length < 8) { toast("Write the one thing first — a full sentence"); $("o_wish").focus(); return; }
    S.profile = { name: $("o_name").value.trim(), wish: wish, when: getWhen(), why: $("o_why").value.trim(),
                  setting: getSetting(), witness: getWitness(), step: $("o_step").value.trim() };
    save(); show("today");
  });

  /* ---------- today ---------- */
  var current = null;
  function renderToday() {
    current = ensureToday(); if (!current) return;
    $("topDate").textContent = nice(today());
    $("sTitle").textContent = current.title;
    $("sBody").innerHTML = current.paragraphs.map(function (p) { return "<p>" + esc(p) + "</p>"; }).join("");
    $("srcPill").textContent = current.source === "ai" ? "written by AI from your words" : "written on device";
    $("srcPill").className = "pill " + (current.source === "ai" ? "ai" : "free");
    $("fav").textContent = current.fav ? "♥ Kept" : "♡ Keep";
    var step = S.profile.step || "Write one step under Me";
    $("stepText").textContent = step;
    $("stepDone").checked = !!S.steps[today()];
    $("aiBtn").hidden = !WRITER; // hidden until the owner deploys the writer
    var wc = current.paragraphs.join(" ").split(/\s+/).length;
    $("pS").textContent = "about " + Math.max(1, Math.round(wc / 120)) + " min · read aloud by your phone";
    // streak
    var html = "", n = 0, d = new Date();
    for (var i = 6; i >= 0; i--) { var k = ymd(new Date(d.getFullYear(), d.getMonth(), d.getDate() - i)); var on = !!S.steps[k]; if (on) n++; html += "<i" + (on ? ' class="on"' : "") + "></i>"; }
    $("streak").innerHTML = html;
    $("streakCap").textContent = n === 0 ? "No steps ticked yet this week. The story is the easy half." : n + " of the last 7 days with the step done.";
  }
  $("stepDone").addEventListener("change", function () { if (this.checked) S.steps[today()] = true; else delete S.steps[today()]; save(); renderToday(); });
  $("fav").addEventListener("click", function () { if (!current) return; current.fav = !current.fav; save(); renderToday(); toast(current.fav ? "Kept" : "Removed from kept"); });
  $("another").addEventListener("click", function () {
    stopSpeech();
    var v = (current && current.variant + 1) || 1;
    addStory(buildStory(S.profile, today() + "|" + S.profile.wish + "|" + v + "|" + Math.random()), v);
    renderToday(); toast("A different version");
  });

  /* ---------- AI-written (paid) ---------- */
  $("aiBtn").addEventListener("click", function () {
    if (!WRITER) return;
    if (!S.code) { $("aiNote").hidden = false; $("aiNote").innerHTML = "<strong>Needs an unlock code</strong>Enter it under Me. The free version on this screen costs nothing and works offline."; return; }
    var b = $("aiBtn"); b.disabled = true; b.textContent = "Writing…"; stopSpeech();
    fetch(WRITER, { method: "POST", headers: { "Content-Type": "application/json", "X-Unlock": S.code },
      body: JSON.stringify({ name: S.profile.name, wish: S.profile.wish, when: S.profile.when, why: S.profile.why, setting: (SETTINGS[S.profile.setting] || {}).where || S.profile.setting, witness: S.profile.witness, step: S.profile.step }) })
    .then(function (r) { return r.json().then(function (j) { if (!r.ok) throw new Error(j.error || "failed"); return j; }); })
    .then(function (j) { addStory({ title: j.title || "The day it happened", paragraphs: j.paragraphs, source: "ai" }, 99); renderToday(); $("aiNote").hidden = true; toast("Written from your words"); })
    .catch(function (e) { $("aiNote").hidden = false; $("aiNote").innerHTML = "<strong>Could not write it</strong>" + esc(e.message) + ". The device-written version above still works."; })
    .finally(function () { b.disabled = false; b.textContent = "Write it with AI"; });
  });

  /* ---------- speech ---------- */
  var synth = window.speechSynthesis, speaking = false, queue = [], idx = 0;
  function voices() { return synth ? synth.getVoices().filter(function (v) { return /^en/i.test(v.lang); }) : []; }
  function fillVoices() {
    var sel = $("voice"), vs = voices(); if (!sel) return;
    sel.innerHTML = vs.length ? vs.map(function (v, i) { return '<option value="' + i + '"' + (v.name === S.settings.voice ? " selected" : "") + ">" + esc(v.name.replace(/\(.*?\)/g, "").trim()) + "</option>"; }).join("") : "<option>No voice available</option>";
    if (!S.settings.voice && vs.length) { var pref = vs.find(function (v) { return /Samantha|Siri|Karen|Moira|Daniel|Google UK English Female/i.test(v.name); }); if (pref) sel.value = String(vs.indexOf(pref)); }
  }
  if (synth) { fillVoices(); synth.onvoiceschanged = fillVoices; }
  $("voice").addEventListener("change", function () { var vs = voices(); var v = vs[+this.value]; if (v) { S.settings.voice = v.name; save(); } });
  function setPlayingUI(on) {
    speaking = on; $("icoPlay").hidden = on; $("icoPause").hidden = !on; $("pT").textContent = on ? "Reading" : "Listen"; $("pp").setAttribute("aria-label", on ? "Pause" : "Play");
    if (!on) document.querySelectorAll("#sBody p").forEach(function (p) { p.classList.remove("now"); });
  }
  function stopSpeech() { if (synth) synth.cancel(); queue = []; idx = 0; setPlayingUI(false); }
  function speakNext() {
    if (idx >= queue.length) { setPlayingUI(false); return; }
    var u = new SpeechSynthesisUtterance(queue[idx]);
    var vs = voices(), v = vs[+$("voice").value] || vs.find(function (x) { return x.name === S.settings.voice; });
    if (v) u.voice = v; u.rate = S.settings.rate || 0.95; u.pitch = 1;
    var paras = document.querySelectorAll("#sBody p");
    paras.forEach(function (p, i) { p.classList.toggle("now", i === idx); });
    u.onend = function () { idx++; speakNext(); };
    u.onerror = function () { idx++; speakNext(); };
    synth.speak(u);
  }
  $("pp").addEventListener("click", function () {
    if (!synth) { toast("This browser cannot read aloud — read it instead"); return; }
    if (speaking) { stopSpeech(); return; }
    var title = current ? current.title : "";
    queue = current.paragraphs.slice(); idx = 0; setPlayingUI(true);
    var t = new SpeechSynthesisUtterance(title); t.rate = S.settings.rate || 0.95; var vs = voices(), v = vs[+$("voice").value]; if (v) t.voice = v;
    t.onend = speakNext; t.onerror = speakNext; synth.speak(t);
  });
  document.addEventListener("visibilitychange", function () { if (document.hidden) stopSpeech(); });

  /* ---------- library ---------- */
  function rowHtml(s) {
    return '<div class="row"><div class="l"><div class="t">' + esc(s.title) + '</div><div class="s">' + nice(s.date) + (s.source === "ai" ? " · AI-written" : "") + '</div></div>' +
      '<div class="r"><button data-a="open" data-id="' + s.id + '" aria-label="Open">↗</button><button data-a="fav" data-id="' + s.id + '" class="' + (s.fav ? "on" : "") + '" aria-label="Keep">' + (s.fav ? "♥" : "♡") + '</button></div></div>';
  }
  function renderLibrary() {
    var favs = S.stories.filter(function (s) { return s.fav; }).reverse();
    var all = S.stories.slice().reverse();
    $("favList").innerHTML = favs.length ? favs.map(rowHtml).join("") : '<p class="empty">Tap ♡ Keep on a rehearsal you want to hear again.</p>';
    $("allList").innerHTML = all.length ? all.slice(0, 60).map(rowHtml).join("") : '<p class="empty">Nothing yet.</p>';
    document.querySelectorAll("#v-library button[data-a]").forEach(function (b) {
      b.addEventListener("click", function () {
        var s = S.stories.find(function (x) { return String(x.id) === b.dataset.id; }); if (!s) return;
        if (b.dataset.a === "fav") { s.fav = !s.fav; save(); renderLibrary(); }
        else { S.stories.forEach(function (x) { if (x.date === today()) x.archived = true; }); s.date = today(); s.archived = false; save(); stopSpeech(); show("today"); }
      });
    });
  }

  /* ---------- me ---------- */
  function renderMe() {
    var p = S.profile || {};
    $("m_wish").value = p.wish || ""; $("m_why").value = p.why || ""; $("m_step").value = p.step || ""; $("m_name").value = p.name || "";
    $("codeState").textContent = S.code ? "Unlocked on this phone." : (WRITER ? "No code entered. Free rehearsals keep working." : "AI-written rehearsals are not switched on yet.");
    $("buyLink").hidden = !BUY; if (BUY) $("buyLink").href = BUY;
    document.querySelectorAll("#rateChips .chip").forEach(function (c) { c.classList.toggle("on", parseFloat(c.dataset.v) === (S.settings.rate || 0.95)); });
  }
  $("m_save").addEventListener("click", function () {
    if (!S.profile) return;
    var changed = S.profile.wish !== $("m_wish").value.trim();
    S.profile.wish = $("m_wish").value.trim() || S.profile.wish; S.profile.why = $("m_why").value.trim(); S.profile.step = $("m_step").value.trim(); S.profile.name = $("m_name").value.trim();
    if (changed) S.stories.forEach(function (x) { if (x.date === today()) x.archived = true; });
    save(); toast("Saved"); if (changed) show("today");
  });
  $("m_restart").addEventListener("click", function () {
    if (!confirm("Start a new rehearsal? Your library stays; the wish, why and step are cleared.")) return;
    S.profile = null; save(); show("start");
  });
  $("codeSave").addEventListener("click", function () {
    var c = $("code").value.trim().toUpperCase(); if (!c) { S.code = ""; save(); renderMe(); return; }
    S.code = c; save(); $("code").value = ""; renderMe(); toast("Code saved — try Write it with AI");
  });
  $("exportBtn").addEventListener("click", function () {
    var blob = new Blob([JSON.stringify(S, null, 1)], { type: "application/json" }); var a = document.createElement("a");
    a.href = URL.createObjectURL(blob); a.download = "rehearsal-" + today() + ".json"; document.body.appendChild(a); a.click(); a.remove();
  });
  $("importBtn").addEventListener("click", function () { $("importFile").click(); });
  $("importFile").addEventListener("change", function () {
    var f = this.files[0]; if (!f) return; var r = new FileReader();
    r.onload = function () { try { var j = JSON.parse(r.result); if (!j || !("stories" in j)) throw 0; S = j; var b = blank(); for (var k in b) if (S[k] === undefined) S[k] = b[k]; save(); show("today"); toast("Imported"); } catch (e) { toast("That file isn't a Rehearsal export"); } };
    r.readAsText(f); this.value = "";
  });
  $("wipe").addEventListener("click", function () {
    if (!confirm("Delete everything Rehearsal has stored on this phone? This cannot be undone.")) return;
    S = blank(); try { localStorage.removeItem(KEY); } catch (e) {} show("start"); toast("Deleted");
  });

  /* ---------- render ---------- */
  function render() {
    if (view === "today") renderToday();
    if (view === "library") renderLibrary();
    if (view === "me") renderMe();
  }
  if ("serviceWorker" in navigator && location.protocol === "https:") navigator.serviceWorker.register("sw.js").catch(function () {});
  show(S.profile ? "today" : "start");
})();
