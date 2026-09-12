/* Causeway — the commuter's money companion.
   Everything is stored in localStorage on this device. The only network
   request the app ever makes is for the day's exchange rate, and only
   when the user taps the button. */
(function () {
  "use strict";

  var KEY = "causeway.v1";
  var FX_URL = "https://api.frankfurter.app/latest?from=SGD&to=MYR";
  var MY_NEED = 182, SG_NEED = 183;

  /* ---------- state ---------- */
  function blank() {
    return { settings: {}, crossings: [], days: {}, recent: [] };
  }
  function load() {
    try {
      var raw = localStorage.getItem(KEY);
      if (!raw) return blank();
      var s = JSON.parse(raw);
      var b = blank();
      return { settings: s.settings || b.settings, crossings: s.crossings || [],
               days: s.days || {}, recent: s.recent || [] };
    } catch (e) { return blank(); }
  }
  function save() {
    try { localStorage.setItem(KEY, JSON.stringify(S)); } catch (e) { toast("Could not save — storage is full or blocked"); }
  }
  var S = load();

  /* ---------- helpers ---------- */
  var $ = function (id) { return document.getElementById(id); };
  var pad = function (n) { return (n < 10 ? "0" : "") + n; };
  function ymd(d) { return d.getFullYear() + "-" + pad(d.getMonth() + 1) + "-" + pad(d.getDate()); }
  function fromYmd(s) { var p = s.split("-"); return new Date(+p[0], +p[1] - 1, +p[2]); }
  function today() { return ymd(new Date()); }
  var MONTHS = ["January","February","March","April","May","June","July","August","September","October","November","December"];
  var fmt0 = new Intl.NumberFormat("en-MY", { maximumFractionDigits: 0 });
  var fmt2 = new Intl.NumberFormat("en-MY", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
  function rm(n, dp) { var f = dp === 2 ? fmt2 : fmt0; return (n < 0 ? "−RM" : "RM") + f.format(Math.abs(n)); }
  function niceDate(s) { var d = fromYmd(s); return d.getDate() + " " + MONTHS[d.getMonth()].slice(0, 3) + " " + d.getFullYear(); }
  function num(v) { var n = parseFloat(v); return isFinite(n) ? n : 0; }
  var toastT;
  function toast(msg) {
    var t = $("toast"); t.textContent = msg; t.classList.add("on");
    clearTimeout(toastT); toastT = setTimeout(function () { t.classList.remove("on"); }, 2200);
  }

  /* ---------- residency arithmetic ---------- */
  function countYear(year) {
    var my = 0, sg = 0, marked = 0;
    for (var k in S.days) {
      if (k.slice(0, 4) !== String(year)) continue;
      var v = S.days[k];
      if (v === "MY" || v === "BOTH") my++;
      if (v === "SG" || v === "BOTH") sg++;
      marked++;
    }
    return { my: my, sg: sg, marked: marked };
  }
  function daysInYear(y) { return ((y % 4 === 0 && y % 100 !== 0) || y % 400 === 0) ? 366 : 365; }
  function dayOfYear(d) {
    var start = new Date(d.getFullYear(), 0, 1);
    return Math.round((d - start) / 86400000) + 1;
  }
  // Unmarked days from today to 31 Dec, inclusive of today if today is unmarked.
  function remainingDays(year) {
    var now = new Date(), y = now.getFullYear();
    if (year < y) return 0;
    if (year > y) return daysInYear(year);
    var left = daysInYear(y) - dayOfYear(now) + 1;
    // subtract already-marked days from today onward
    for (var k in S.days) {
      if (k.slice(0, 4) !== String(y)) continue;
      if (k >= today()) left--;
    }
    return Math.max(0, left);
  }
  function testMsg(have, need, left, country) {
    if (have >= need) return { cls: "met", label: "MET", text: country + " counts you as present for " + have + " days this year." };
    var gap = need - have;
    if (gap > left) return { cls: "out", label: "NOT THIS YEAR", text: gap + " more needed, but only " + left + " unmarked days are left in the year. If earlier days are missing from the log, go back and mark them." };
    return { cls: "open", label: "OPEN", text: gap + " more days needed. " + left + " unmarked days remain." };
  }

  /* ---------- views ---------- */
  var view = "today";
  function show(v) {
    view = v;
    document.querySelectorAll(".view").forEach(function (el) { el.classList.toggle("on", el.id === "v-" + v); });
    document.querySelectorAll(".tabs button").forEach(function (b) { b.classList.toggle("on", b.dataset.view === v); });
    window.scrollTo(0, 0);
    render();
  }
  document.querySelectorAll(".tabs button").forEach(function (b) {
    b.addEventListener("click", function () { show(b.dataset.view); });
  });

  /* ---------- today ---------- */
  var cMonth = new Date(); cMonth.setDate(1);
  var dMonth = new Date(); dMonth.setDate(1);
  var dYear = new Date().getFullYear();

  function monthlyPayRm() {
    var st = S.settings;
    if (!st.salary || !st.rate) return null;
    return st.salary * st.rate;
  }
  function commuteTotal(y, m) {
    var t = 0, n = 0;
    S.crossings.forEach(function (c) {
      var d = fromYmd(c.date);
      if (d.getFullYear() === y && d.getMonth() === m) { t += c.cost; n++; }
    });
    return { total: t, n: n };
  }

  function renderToday() {
    var st = S.settings;
    var setup = !st.salary;
    $("setupCard").hidden = !setup;
    $("todayMain").hidden = setup;
    $("topDate").textContent = niceDate(today());
    if (setup) return;

    var pay = monthlyPayRm();
    if (pay === null) {
      $("payRm").textContent = "—";
      $("payCap").textContent = "Fetch or enter today's rate to see this in ringgit.";
    } else {
      $("payRm").textContent = rm(pay);
      $("payCap").textContent = "S$" + fmt0.format(st.salary) + " × " + st.rate.toFixed(4) + " — before tax, before the commute.";
    }
    $("rateVal").textContent = st.rate ? st.rate.toFixed(4) + " RM/S$" : "not set";
    $("rateCap").textContent = st.rateDate ? (st.rateSource === "manual" ? "entered by you, " : "ECB reference, ") + niceDate(st.rateDate) : "";

    if (st.signRate && st.rate && st.salary) {
      var d = st.salary * (st.rate - st.signRate);
      $("signDelta").textContent = (d >= 0 ? "+" : "") + rm(d) + " / month";
      $("signDelta").className = "v delta " + (d >= 0 ? "pos" : "neg");
      $("signCap").textContent = "signed at " + st.signRate.toFixed(3) + (st.signDate ? ", " + niceDate(st.signDate) : "");
    } else {
      $("signDelta").textContent = "—"; $("signDelta").className = "v delta";
      $("signCap").textContent = "set the signing rate under More";
    }

    var tv = S.days[today()];
    document.querySelectorAll("#todaySeg button").forEach(function (b) { b.classList.toggle("on", b.dataset.v === tv); });
    $("todayH").textContent = tv ? "Today is marked" : "Where did today count?";

    var now = new Date();
    var c = commuteTotal(now.getFullYear(), now.getMonth());
    $("tMonthCommute").textContent = rm(c.total, 2);
    var yc = countYear(now.getFullYear());
    $("tMy").textContent = yc.my; $("tSg").textContent = yc.sg;
  }

  $("saveSetup").addEventListener("click", function () {
    var sal = num($("s_salary").value);
    if (!(sal > 0)) { toast("Enter your monthly pay first"); return; }
    S.settings.salary = sal;
    var sr = num($("s_signRate").value);
    if (sr > 0) S.settings.signRate = sr;
    if ($("s_signDate").value) S.settings.signDate = $("s_signDate").value;
    save(); render();
    if (!S.settings.rate) fetchRate();
  });

  document.querySelectorAll("#todaySeg button").forEach(function (b) {
    b.addEventListener("click", function () {
      var t = today();
      if (S.days[t] === b.dataset.v) delete S.days[t]; else S.days[t] = b.dataset.v;
      save(); render();
    });
  });

  /* ---------- exchange rate ---------- */
  function applyRate(rate, date, source) {
    S.settings.rate = rate; S.settings.rateDate = date; S.settings.rateSource = source;
    if (!S.settings.signRate) { S.settings.signRate = rate; S.settings.signDate = S.settings.signDate || date; }
    save(); render();
  }
  function fetchRate() {
    var btn = $("refreshRate"); btn.disabled = true; btn.textContent = "Fetching…";
    var done = function () { btn.disabled = false; btn.textContent = "Fetch today's rate"; };
    if (!navigator.onLine) { done(); toast("Offline — enter a rate instead"); $("rateForm").hidden = false; return; }
    fetch(FX_URL, { cache: "no-store" }).then(function (r) {
      if (!r.ok) throw new Error("http " + r.status);
      return r.json();
    }).then(function (j) {
      var v = j && j.rates && j.rates.MYR;
      if (!(v > 0)) throw new Error("no rate");
      applyRate(v, j.date || today(), "ecb");
      toast("Rate updated: " + v.toFixed(4));
      done();
    }).catch(function () {
      done(); $("rateForm").hidden = false;
      toast("No rate service — enter today's rate");
    });
  }
  $("refreshRate").addEventListener("click", fetchRate);
  $("manualRate").addEventListener("click", function () {
    $("rateForm").hidden = !$("rateForm").hidden;
    if (!$("rateForm").hidden) { $("rateIn").value = S.settings.rate || ""; $("rateIn").focus(); }
  });
  $("rateSave").addEventListener("click", function () {
    var v = num($("rateIn").value);
    if (!(v > 1 && v < 10)) { toast("That doesn't look like RM per S$1"); return; }
    applyRate(v, today(), "manual"); $("rateForm").hidden = true;
  });

  /* ---------- commute ---------- */
  var MODE_LABEL = { bus: "Bus", rts: "RTS", car: "Car", bike: "Motorbike", train: "KTM", other: "Other" };
  function renderCommute() {
    var y = cMonth.getFullYear(), m = cMonth.getMonth();
    $("cMonthH").textContent = MONTHS[m] + " " + y;
    var c = commuteTotal(y, m);
    $("cTotal").textContent = rm(c.total, 2);
    $("cCount").textContent = c.n;
    $("cAvg").textContent = c.n ? rm(c.total / c.n, 2) : "—";
    var pay = monthlyPayRm();
    $("cShare").textContent = (pay && c.total) ? (100 * c.total / pay).toFixed(1) + "%" : "—";
    var list = S.crossings.filter(function (x) {
      var d = fromYmd(x.date); return d.getFullYear() === y && d.getMonth() === m;
    }).sort(function (a, b) { return a.date < b.date ? 1 : -1; });
    var el = $("cList");
    if (!list.length) { el.innerHTML = '<p class="empty">No crossings logged this month.</p>'; return; }
    el.innerHTML = list.map(function (x) {
      return '<div class="item"><div class="l">' + niceDate(x.date) +
        '<span class="small">' + (MODE_LABEL[x.mode] || "Other") + '</span></div>' +
        '<div class="r"><span class="v">' + rm(x.cost, 2) + '</span>' +
        '<button class="x" data-id="' + x.id + '" aria-label="Delete">✕</button></div></div>';
    }).join("");
    el.querySelectorAll(".x").forEach(function (b) {
      b.addEventListener("click", function () {
        S.crossings = S.crossings.filter(function (x) { return String(x.id) !== b.dataset.id; });
        save(); render(); toast("Removed");
      });
    });
  }
  $("cPrev").addEventListener("click", function () { cMonth.setMonth(cMonth.getMonth() - 1); render(); });
  $("cNext").addEventListener("click", function () { cMonth.setMonth(cMonth.getMonth() + 1); render(); });

  /* crossing sheet */
  var xMode = "bus";
  function openSheet() {
    $("x_date").value = today();
    $("x_cost").value = "";
    xMode = (S.recent[0] && S.recent[0].mode) || "bus";
    paintChips();
    var rw = $("recentWrap"), rc = $("recentChips");
    if (S.recent.length) {
      rw.hidden = false;
      rc.innerHTML = S.recent.map(function (r, i) {
        return '<button class="chip" data-i="' + i + '">' + (MODE_LABEL[r.mode] || "Other") + " · " + rm(r.cost, 2) + "</button>";
      }).join("");
      rc.querySelectorAll(".chip").forEach(function (b) {
        b.addEventListener("click", function () {
          var r = S.recent[+b.dataset.i]; xMode = r.mode; $("x_cost").value = r.cost; paintChips();
        });
      });
    } else rw.hidden = true;
    $("sheet").classList.add("on");
    setTimeout(function () { $("x_cost").focus(); }, 50);
  }
  function closeSheet() { $("sheet").classList.remove("on"); }
  function paintChips() {
    document.querySelectorAll("#modeChips .chip").forEach(function (b) { b.classList.toggle("on", b.dataset.m === xMode); });
  }
  document.querySelectorAll("#modeChips .chip").forEach(function (b) {
    b.addEventListener("click", function () { xMode = b.dataset.m; paintChips(); });
  });
  $("addCross").addEventListener("click", openSheet);
  $("quickCross").addEventListener("click", openSheet);
  $("x_cancel").addEventListener("click", closeSheet);
  $("sheet").addEventListener("click", function (e) { if (e.target === $("sheet")) closeSheet(); });
  $("x_save").addEventListener("click", function () {
    var cost = num($("x_cost").value), date = $("x_date").value || today();
    if (!(cost >= 0)) { toast("Enter what it cost"); return; }
    S.crossings.push({ id: Date.now(), date: date, mode: xMode, cost: cost });
    S.recent = [{ mode: xMode, cost: cost }].concat(S.recent.filter(function (r) {
      return !(r.mode === xMode && r.cost === cost);
    })).slice(0, 3);
    // a logged crossing implies presence in both countries that day, unless already marked
    if (!S.days[date]) S.days[date] = "BOTH";
    save(); closeSheet(); render(); toast("Crossing saved");
  });

  /* ---------- days ---------- */
  var CYCLE = [undefined, "BOTH", "MY", "SG", "AWAY"];
  function renderDays() {
    $("yH").textContent = String(dYear);
    var c = countYear(dYear), left = remainingDays(dYear);
    $("myN").textContent = c.my; $("sgN").textContent = c.sg;
    $("myBar").style.width = Math.min(100, 100 * c.my / MY_NEED) + "%";
    $("sgBar").style.width = Math.min(100, 100 * c.sg / SG_NEED) + "%";
    var m1 = testMsg(c.my, MY_NEED, left, "Malaysia"), m2 = testMsg(c.sg, SG_NEED, left, "Singapore");
    $("myMsg").innerHTML = '<span class="status ' + m1.cls + '">' + m1.label + "</span> " + m1.text;
    $("sgMsg").innerHTML = '<span class="status ' + m2.cls + '">' + m2.label + "</span> " + m2.text;
    var dn = $("dualNote");
    if (c.my >= MY_NEED && c.sg >= SG_NEED) {
      dn.innerHTML = '<div class="note"><strong>Both tests met</strong>Both countries can treat you as resident for ' + dYear +
        '. The treaty tie-breaker then decides — permanent home, then centre of vital interests. This needs a practitioner, not an app; take this log with you.</div>';
    } else if (c.marked === 0) {
      dn.innerHTML = '<div class="note calm"><strong>Nothing marked yet</strong>Mark today on the Today tab, or use "Fill month as a commuter" below and correct the exceptions.</div>';
    } else dn.innerHTML = "";

    // month grid
    var y = dMonth.getFullYear(), m = dMonth.getMonth();
    $("dMonthH").textContent = MONTHS[m] + " " + y;
    var first = new Date(y, m, 1), startDow = (first.getDay() + 6) % 7; // Monday first
    var n = new Date(y, m + 1, 0).getDate();
    var t = today();
    var html = ["M","T","W","T","F","S","S"].map(function (d) { return '<div class="dow">' + d + "</div>"; }).join("");
    for (var i = 0; i < startDow; i++) html += '<div class="cell pad"></div>';
    for (var d = 1; d <= n; d++) {
      var k = y + "-" + pad(m + 1) + "-" + pad(d);
      var v = S.days[k] || "";
      html += '<button class="cell ' + v + (k === t ? " today" : "") + (k > t ? " future" : "") +
        '" data-k="' + k + '" aria-label="' + niceDate(k) + (v ? ", " + v : "") + '">' + d + "</button>";
    }
    $("cal").innerHTML = html;
    $("cal").querySelectorAll(".cell[data-k]").forEach(function (b) {
      b.addEventListener("click", function () {
        var k = b.dataset.k, cur = S.days[k], i = CYCLE.indexOf(cur), nx = CYCLE[(i + 1) % CYCLE.length];
        if (nx === undefined) delete S.days[k]; else S.days[k] = nx;
        save(); render();
      });
    });
  }
  $("yPrev").addEventListener("click", function () { dYear--; dMonth = new Date(dYear, 0, 1); render(); });
  $("yNext").addEventListener("click", function () { dYear++; dMonth = new Date(dYear, 0, 1); render(); });
  $("dPrev").addEventListener("click", function () { dMonth.setMonth(dMonth.getMonth() - 1); dYear = dMonth.getFullYear(); render(); });
  $("dNext").addEventListener("click", function () { dMonth.setMonth(dMonth.getMonth() + 1); dYear = dMonth.getFullYear(); render(); });
  $("fillCommute").addEventListener("click", function () {
    var y = dMonth.getFullYear(), m = dMonth.getMonth(), n = new Date(y, m + 1, 0).getDate(), t = today(), c = 0;
    for (var d = 1; d <= n; d++) {
      var k = y + "-" + pad(m + 1) + "-" + pad(d);
      if (k > t) break;
      if (S.days[k]) continue;
      var dow = new Date(y, m, d).getDay();
      S.days[k] = (dow === 0 || dow === 6) ? "MY" : "BOTH"; c++;
    }
    save(); render(); toast(c ? c + " days filled — fix the exceptions" : "Nothing to fill");
  });
  $("clearMonth").addEventListener("click", function () {
    var y = dMonth.getFullYear(), m = dMonth.getMonth(), n = new Date(y, m + 1, 0).getDate();
    if (!confirm("Clear every marked day in " + MONTHS[m] + " " + y + "?")) return;
    for (var d = 1; d <= n; d++) delete S.days[y + "-" + pad(m + 1) + "-" + pad(d)];
    save(); render();
  });

  /* ---------- more ---------- */
  function renderMore() {
    var st = S.settings;
    $("m_salary").value = st.salary || "";
    $("m_signRate").value = st.signRate || "";
    $("m_signDate").value = st.signDate || "";
  }
  $("saveMore").addEventListener("click", function () {
    var sal = num($("m_salary").value); if (sal > 0) S.settings.salary = sal;
    var sr = num($("m_signRate").value); if (sr > 0) S.settings.signRate = sr;
    S.settings.signDate = $("m_signDate").value || S.settings.signDate;
    save(); render(); toast("Saved");
  });
  $("exportBtn").addEventListener("click", function () {
    var blob = new Blob([JSON.stringify(S, null, 1)], { type: "application/json" });
    var a = document.createElement("a");
    a.href = URL.createObjectURL(blob); a.download = "causeway-" + today() + ".json";
    document.body.appendChild(a); a.click(); a.remove();
    setTimeout(function () { URL.revokeObjectURL(a.href); }, 1000);
  });
  $("importBtn").addEventListener("click", function () { $("importFile").click(); });
  $("importFile").addEventListener("change", function () {
    var f = this.files[0]; if (!f) return;
    var r = new FileReader();
    r.onload = function () {
      try {
        var j = JSON.parse(r.result);
        if (!j || typeof j !== "object" || !("days" in j)) throw new Error();
        S = { settings: j.settings || {}, crossings: j.crossings || [], days: j.days || {}, recent: j.recent || [] };
        save(); render(); toast("Imported");
      } catch (e) { toast("That file isn't a Causeway export"); }
    };
    r.readAsText(f); this.value = "";
  });
  $("wipeBtn").addEventListener("click", function () {
    if (!confirm("Delete everything Causeway has stored on this phone? This cannot be undone.")) return;
    S = blank(); try { localStorage.removeItem(KEY); } catch (e) {}
    render(); show("today"); toast("Deleted");
  });

  /* ---------- install ---------- */
  var deferred = null;
  var standalone = window.matchMedia("(display-mode: standalone)").matches || navigator.standalone === true;
  if (!standalone) {
    $("installCard").classList.add("on");
    var ios = /iphone|ipad|ipod/i.test(navigator.userAgent) && !window.MSStream;
    if (ios) $("installHow").textContent = "On iPhone: tap Share, then “Add to Home Screen”. It opens like an app, works offline, and keeps your data on the device.";
  }
  window.addEventListener("beforeinstallprompt", function (e) {
    e.preventDefault(); deferred = e; $("installBtn").hidden = false;
  });
  $("installBtn").addEventListener("click", function () {
    if (!deferred) return; deferred.prompt(); deferred = null; $("installBtn").hidden = true;
  });
  if ("serviceWorker" in navigator && location.protocol === "https:") {
    navigator.serviceWorker.register("sw.js").catch(function () {});
  }

  /* ---------- render ---------- */
  function render() {
    renderToday();
    if (view === "commute") renderCommute();
    if (view === "days") renderDays();
    if (view === "more") renderMore();
  }
  render();
})();
