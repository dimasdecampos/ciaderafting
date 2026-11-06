/* Cia. de Rafting — interações do site */
(function () {
  "use strict";

  var WHATSAPP = "5512997031363";
  var $ = function (s, c) { return (c || document).querySelector(s); };
  var $$ = function (s, c) { return Array.prototype.slice.call((c || document).querySelectorAll(s)); };

  function waLink(text) {
    return "https://wa.me/" + WHATSAPP + "?text=" + encodeURIComponent(text);
  }
  function openLink(url) {
    var w = null;
    try { w = window.open(url, "_blank", "noopener"); } catch (e) { w = null; }
    if (!w) {
      var a = document.createElement("a");
      a.href = url; a.target = "_blank"; a.rel = "noopener";
      document.body.appendChild(a); a.click(); a.remove();
    }
  }

  /* Header muda ao rolar + barra fixa no mobile */
  var header = $(".header");
  var mobileBar = $(".mobile-bar");
  function onScroll() {
    var y = window.scrollY;
    if (header) header.classList.toggle("is-scrolled", y > 40);
    if (mobileBar) mobileBar.classList.toggle("is-visible", y > 500);
  }
  window.addEventListener("scroll", onScroll, { passive: true });
  onScroll();

  /* Menu mobile */
  var drawer = $("#drawer");
  function setDrawer(open) {
    if (!drawer) return;
    drawer.classList.toggle("is-open", open);
    drawer.setAttribute("aria-hidden", String(!open));
    document.body.classList.toggle("no-scroll", open);
    $$("[data-drawer-open]").forEach(function (b) { b.setAttribute("aria-expanded", String(open)); });
    if (open) { var f = $("button, a", drawer); if (f) f.focus(); }
  }
  $$("[data-drawer-open]").forEach(function (b) { b.addEventListener("click", function () { setDrawer(true); }); });
  $$("[data-drawer-close]").forEach(function (b) { b.addEventListener("click", function () { setDrawer(false); }); });
  document.addEventListener("keydown", function (e) { if (e.key === "Escape") { setDrawer(false); closeLightbox(); } });

  /* Animação de entrada */
  var reveals = $$(".reveal");
  if ("IntersectionObserver" in window) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (en.isIntersecting) { en.target.classList.add("is-in"); io.unobserve(en.target); }
      });
    }, { threshold: 0.12, rootMargin: "0px 0px -40px 0px" });
    reveals.forEach(function (el) { io.observe(el); });
  } else {
    reveals.forEach(function (el) { el.classList.add("is-in"); });
  }

  /* Contadores */
  var counters = $$("[data-count]");
  if ("IntersectionObserver" in window && counters.length) {
    var co = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (!en.isIntersecting) return;
        var el = en.target, end = parseInt(el.getAttribute("data-count"), 10), start = parseInt(el.getAttribute("data-from") || "0", 10);
        var t0 = null, dur = 1600;
        function tick(t) {
          if (!t0) t0 = t;
          var p = Math.min((t - t0) / dur, 1), e = 1 - Math.pow(1 - p, 3);
          el.textContent = Math.round(start + (end - start) * e) + (el.getAttribute("data-suffix") || "");
          if (p < 1) requestAnimationFrame(tick);
        }
        requestAnimationFrame(tick);
        co.unobserve(el);
      });
    }, { threshold: 0.6 });
    counters.forEach(function (el) { co.observe(el); });
  }

  /* Filtro de atividades */
  $$("[data-filter-group]").forEach(function (group) {
    var target = $(group.getAttribute("data-filter-group"));
    $$(".chip", group).forEach(function (chip) {
      chip.addEventListener("click", function () {
        $$(".chip", group).forEach(function (c) { c.setAttribute("aria-pressed", "false"); });
        chip.setAttribute("aria-pressed", "true");
        var f = chip.getAttribute("data-filter");
        $$("[data-cat]", target).forEach(function (card) {
          card.classList.toggle("is-hidden", f !== "all" && card.getAttribute("data-cat") !== f);
        });
      });
    });
  });

  /* Seletor de pessoas */
  $$(".stepper").forEach(function (st) {
    var out = $("output", st), input = $("input", st);
    var min = 1, max = 60;
    $$("button", st).forEach(function (b) {
      b.addEventListener("click", function () {
        var v = parseInt(input.value, 10) + parseInt(b.getAttribute("data-step"), 10);
        v = Math.max(min, Math.min(max, v));
        input.value = v; out.textContent = v;
      });
    });
  });

  /* Data mínima = hoje */
  var today = new Date(); today.setMinutes(today.getMinutes() - today.getTimezoneOffset());
  $$('input[type="date"]').forEach(function (d) { d.min = today.toISOString().slice(0, 10); });

  function fmtDate(v) {
    if (!v) return "a combinar";
    var p = v.split("-"); return p[2] + "/" + p[1] + "/" + p[0];
  }

  /* Agenda ao vivo: vagas por data, botes e grupos (home)
     Hoje a ocupação é simulada em demoBooked(). Para ligar na agenda real,
     basta trocar o miolo de loadMonth() por um fetch que devolva
     { "2026-11-14": [6, 3, 0, 0, 2], ... } = lugares já ocupados em cada bote/grupo. */
  var vagas = (function () {
    var root = $("[data-vagas]");
    if (!root) return null;

    var ACTS = {
      r4: { full: "Rafting 4 horas · Brazadão", unit: "Bote", units: 5, seats: 6, staff: "instrutor", days: [0, 6], boat: true },
      r6: { full: "Rafting 6 horas · Núcleo Santa Virgínia", unit: "Bote", units: 5, seats: 6, staff: "instrutor", days: [0, 6], boat: true },
      tr: { full: "Trilha", unit: "Grupo", units: 3, seats: 10, staff: "guia", days: [0, 2, 3, 4, 5, 6] },
      cu: { full: "Curso de Rafting", unit: "Turma", units: 1, seats: 12, staff: "instrutor", course: true }
    };
    var HOL = { "2026-11-15": "Proclamação da República", "2026-11-20": "Consciência Negra", "2026-12-25": "Natal",
      "2027-01-01": "Ano Novo", "2027-02-08": "Carnaval", "2027-02-09": "Carnaval", "2027-03-26": "Sexta-feira Santa",
      "2027-04-21": "Tiradentes", "2027-05-01": "Dia do Trabalho" };
    var MES = ["janeiro", "fevereiro", "março", "abril", "maio", "junho", "julho", "agosto", "setembro", "outubro", "novembro", "dezembro"];
    var DIA = ["domingo", "segunda", "terça", "quarta", "quinta", "sexta", "sábado"];
    var DIA3 = ["Dom", "Seg", "Ter", "Qua", "Qui", "Sex", "Sáb"];
    var MAX_MESES = 5;

    var now = new Date(), hoje = new Date(now.getFullYear(), now.getMonth(), now.getDate());
    function pad(n) { return (n < 10 ? "0" : "") + n; }
    function iso(d) { return d.getFullYear() + "-" + pad(d.getMonth() + 1) + "-" + pad(d.getDate()); }
    function parse(s) { var p = s.split("-"); return new Date(+p[0], p[1] - 1, +p[2]); }
    function pl(n, s, p) { return n + " " + (n === 1 ? s : p); }
    function cap1(s) { return s.charAt(0).toUpperCase() + s.slice(1); }
    function longDate(d) { return cap1(DIA[d.getDay()]) + ", " + d.getDate() + " de " + MES[d.getMonth()]; }
    function shortDate(d) { return pad(d.getDate()) + "/" + pad(d.getMonth() + 1); }

    var st = { act: "r6", trail: 0, n: 4, y: hoje.getFullYear(), m: hoje.getMonth(), sel: null, soon: [] };
    function A() { return ACTS[st.act]; }
    function key() { return st.act === "tr" ? "tr" + st.trail : st.act; }
    function cap() { return A().units * A().seats; }
    function unitName(i) { return A().units === 1 ? A().unit : A().unit + " " + (i + 1); }
    function freeOf(b) { var f = 0, s = A().seats; b.forEach(function (x) { f += s - x; }); return f; }

    function operates(d) {
      var a = A();
      if (a.course) return d.getDay() === 6 && d.getDate() >= 8 && d.getDate() <= 14;
      return a.days.indexOf(d.getDay()) > -1 || !!HOL[iso(d)];
    }

    /* --- ocupação simulada (determinística por data) --- */
    function hash(s) { var h = 2166136261; for (var i = 0; i < s.length; i++) { h ^= s.charCodeAt(i); h = Math.imul(h, 16777619); } return h >>> 0; }
    function rng(seed) {
      return function () {
        seed = seed + 0x6D2B79F5 | 0;
        var t = Math.imul(seed ^ seed >>> 15, 1 | seed);
        t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t;
        return ((t ^ t >>> 14) >>> 0) / 4294967296;
      };
    }
    function demoBooked(k, day, ahead) {
      var a = A(), r = rng(hash(k + day)), out = [];
      var load = Math.max(.12, .82 - ahead / 110) + (HOL[day] ? .2 : 0);
      if (r() < .07) load = 2; // data esgotada
      for (var i = 0; i < a.units; i++) {
        var x = r();
        out.push(x < load * .45 ? a.seats : x < load ? 1 + Math.floor(r() * (a.seats - 1)) : 0);
      }
      return out;
    }

    var cache = {};
    function loadMonth(y, m) {
      var k = key(), ck = k + ":" + y + "-" + m;
      if (!cache[ck]) cache[ck] = new Promise(function (ok) {
        // PRODUÇÃO: fetch("/api/vagas?atividade=" + k + "&mes=" + y + "-" + pad(m + 1)).then(r => r.json()).then(ok)
        var out = {}, dim = new Date(y, m + 1, 0).getDate();
        for (var d = 1; d <= dim; d++) {
          var dt = new Date(y, m, d);
          if (dt <= hoje || !operates(dt)) continue; // a partir de amanhã
          out[iso(dt)] = demoBooked(k, iso(dt), Math.round((dt - hoje) / 864e5));
        }
        ok(out);
      });
      return cache[ck];
    }

    /* Distribui o grupo: enquanto não cabe inteiro em um bote, ocupa o mais vazio;
       o resto vai no bote onde sobra menos espaço (libera botes vazios para outros grupos). */
    function allocate(b, n) {
      var s = A().seats, mine = b.map(function () { return 0; }), left = n;
      function free(i) { return s - b[i] - mine[i]; }
      while (left > 0) {
        var best = -1, most = -1;
        for (var i = 0; i < b.length; i++) {
          if (mine[i] || free(i) <= 0) continue;
          if (free(i) >= left && (best < 0 || free(i) < free(best))) best = i;
          if (most < 0 || free(i) > free(most)) most = i;
        }
        if (best > -1) { mine[best] = left; left = 0; }
        else if (most > -1) { mine[most] = free(most); left -= mine[most]; }
        else break;
      }
      return { mine: mine, left: left };
    }
    function status(b) { var f = freeOf(b); return f < st.n ? "full" : f - st.n < A().seats ? "few" : "ok"; }

    var el = {
      acts: $$("[data-act]", root), trail: $("[data-vg-trail]", root), n: $("[data-vg-n]", root),
      minus: $('[data-vg-step="-1"]', root), plus: $('[data-vg-step="1"]', root), info: $("[data-vg-info]", root),
      fleet: $("[data-vg-fleet]", root), sum: $("[data-vg-sum]", root), title: $("[data-vg-title]", root),
      prev: $("[data-vg-prev]", root), next: $("[data-vg-next]", root), grid: $("[data-vg-grid]", root),
      soon: $("[data-vg-soon]", root), soonT: $("[data-vg-soon-t]", root)
    };

    function renderControls() {
      var a = A();
      if (st.n > cap()) st.n = cap();
      el.acts.forEach(function (b) { b.setAttribute("aria-pressed", String(b.getAttribute("data-act") === st.act)); });
      el.trail.hidden = st.act !== "tr";
      el.n.textContent = st.n;
      el.minus.disabled = st.n <= 1;
      el.plus.disabled = st.n >= cap();
      var u = Math.ceil(st.n / a.seats), txt;
      if (a.boat) txt = "= no mínimo <b>" + pl(u, "bote", "botes") + "</b><br>cada bote leva " + a.seats + " pessoas + 1 instrutor";
      else if (a.course) txt = "turma única de <b>" + a.seats + " alunos</b><br>2 dias com instrutores IRF";
      else txt = "= no mínimo <b>" + pl(u, "grupo", "grupos") + "</b><br>até " + a.seats + " pessoas + 1 guia por grupo";
      if (st.n >= cap()) txt += '<br><a href="' + waLink("Olá, Cia. de Rafting! Tenho um grupo com mais de " + cap() + " pessoas para " + a.full + ".") + '" target="_blank" rel="noopener">Grupo maior? Fechamos data exclusiva →</a>';
      el.info.innerHTML = txt;
    }

    function findSoon() {
      var jobs = [];
      for (var i = 0; i <= MAX_MESES; i++) { var d = new Date(hoje.getFullYear(), hoje.getMonth() + i, 1); jobs.push(loadMonth(d.getFullYear(), d.getMonth())); }
      return Promise.all(jobs).then(function (maps) {
        var list = [];
        maps.forEach(function (mp) { Object.keys(mp).sort().forEach(function (k) { if (list.length < 6 && freeOf(mp[k]) >= st.n) list.push(k); }); });
        return list;
      });
    }

    function renderSoon(list) {
      st.soon = list;
      el.soonT.textContent = A().boat ? "Próximos fins de semana com vaga para " + pl(st.n, "pessoa", "pessoas") : "Próximas datas com vaga para " + pl(st.n, "pessoa", "pessoas");
      el.soon.innerHTML = list.length ? list.map(function (k) {
        var d = parse(k);
        return '<button type="button" class="vg-chip" data-go="' + k + '"' + (k === st.sel ? ' aria-pressed="true"' : "") + "><small>" + DIA3[d.getDay()] + "</small>" + shortDate(d) + "</button>";
      }).join("") : '<span class="vg-empty">Sem datas para esse grupo nos próximos meses. Fale com a gente!</span>';
    }

    function pips(b, mine) {
      var s = A().seats;
      return '<span class="vg-pips">' + b.map(function (x, i) {
        return '<i style="--b:' + (x / s).toFixed(3) + ";--m:" + ((mine ? mine[i] : 0) / s).toFixed(3) + '"></i>';
      }).join("") + "</span>";
    }

    function renderCal() {
      var ym = st.y * 12 + st.m, base = hoje.getFullYear() * 12 + hoje.getMonth();
      el.title.textContent = cap1(MES[st.m]) + " " + st.y;
      el.prev.disabled = ym <= base;
      el.next.disabled = ym >= base + MAX_MESES;
      return loadMonth(st.y, st.m).then(function (mp) {
        var start = new Date(st.y, st.m, 1).getDay(), dim = new Date(st.y, st.m + 1, 0).getDate(), h = "";
        for (var i = 0; i < start; i++) h += '<span class="vg-day is-blank"></span>';
        for (var d = 1; d <= dim; d++) {
          var dt = new Date(st.y, st.m, d), k = iso(dt), b = mp[k], wk = dt.getDay() % 6 === 0 ? " is-wknd" : "";
          if (!b) { h += '<span class="vg-day is-off' + wk + '"><b>' + d + "</b></span>"; continue; }
          var s = status(b), f = freeOf(b), al = s === "full" ? null : allocate(b, st.n).mine;
          h += '<button type="button" class="vg-day is-' + s + wk + (HOL[k] ? " is-hol" : "") + (k === st.sel ? " is-sel" : "") + '" data-day="' + k + '"' +
            ' aria-label="' + longDate(dt) + (HOL[k] ? " (" + HOL[k] + ")" : "") + ": " + (f ? pl(f, "vaga livre", "vagas livres") : "esgotado") + '"' +
            (k === st.sel ? ' aria-pressed="true"' : ' aria-pressed="false"') + "><b>" + d + "</b>" + pips(b, al) +
            "<small>" + (f ? f + (f === 1 ? " vaga" : " vagas") : "esgotado") + "</small></button>";
        }
        el.grid.innerHTML = h;
      });
    }

    var SEATS = [[52, 22], [52, 42], [76, 22], [76, 42], [100, 22], [100, 42]];
    function unitHTML(i, booked, mine) {
      var a = A(), s = "", cls = "vg-unit" + (mine ? " is-mine" : "") + (booked >= a.seats ? " is-full" : "");
      function seat(k) { return k < booked ? "booked" : k < booked + mine ? "mine" : "free"; }
      function delay(k) { return seat(k) === "mine" ? ' style="animation-delay:' + (k - booked) * 70 + 'ms"' : ""; }
      if (a.boat) {
        s = '<svg class="vg-boat" viewBox="0 0 136 64" aria-hidden="true"><rect class="vg-tube" x="2" y="2" width="132" height="60" rx="30"/>' +
          '<rect class="vg-floor" x="14" y="13" width="108" height="38" rx="19"/><path class="vg-thwart" d="M64 15v34M88 15v34"/>' +
          '<circle class="vg-p vg-p--guide" cx="28" cy="32" r="8"/>';
        SEATS.forEach(function (p, k) { s += '<circle class="vg-p vg-p--' + seat(k) + '" cx="' + p[0] + '" cy="' + p[1] + '" r="7"' + delay(k) + "/>"; });
        s += "</svg>";
      } else {
        s = '<span class="vg-pod" style="--cols:' + Math.ceil(a.seats / 2) + '"><i class="vg-p vg-p--guide"></i>';
        for (var k = 0; k < a.seats; k++) s += '<i class="vg-p vg-p--' + seat(k) + '"' + delay(k) + "></i>";
        s += "</span>";
      }
      var tag = mine ? "<em>" + (mine === 1 ? "1 de vocês" : mine + " de vocês") + "</em>" : booked >= a.seats ? "lotado" : (a.seats - booked) + (a.seats - booked === 1 ? " livre" : " livres");
      return '<div class="' + cls + '" style="--i:' + i + '">' + s + '<span class="vg-unit__tag"><b>' + unitName(i) + "</b> " + tag + "</span></div>";
    }

    function waMsg(d, al, b) {
      var a = A(), used = [];
      al.mine.forEach(function (x, i) { if (x) used.push(unitName(i) + " (" + x + ")"); });
      return "Olá, Cia. de Rafting! Vi as vagas no site e quero reservar:\n" +
        "• Atividade: " + (st.act === "tr" ? $("select", el.trail).value : a.full) + "\n" +
        "• Data: " + DIA[d.getDay()] + ", " + shortDate(d) + "/" + d.getFullYear() + "\n" +
        "• Pessoas: " + st.n + "\n" +
        "• " + (a.boat ? "Botes" : a.unit) + ": " + used.join(", ");
    }

    function suggestion(mp) {
      var sel = parse(st.sel), alt = null;
      Object.keys(mp).filter(function (k) { return freeOf(mp[k]) >= st.n; }).concat(st.soon).forEach(function (k) {
        if (k !== st.sel && (!alt || Math.abs(parse(k) - sel) < Math.abs(parse(alt) - sel))) alt = k;
      });
      return alt ? '<button type="button" class="vg-chip vg-chip--alt" data-go="' + alt + '"><small>Tente</small>' + longDate(parse(alt)) + "</button>" : "";
    }

    function renderDetail() {
      var a = A();
      el.fleet.classList.toggle("vg-river--land", !a.boat);
      if (!st.sel) {
        el.fleet.innerHTML = "";
        el.sum.innerHTML = '<p class="vg-sum__status is-full">Sem datas para ' + pl(st.n, "pessoa", "pessoas") + " nos próximos meses.</p>";
        return;
      }
      var d = parse(st.sel);
      loadMonth(d.getFullYear(), d.getMonth()).then(function (mp) {
        var b = mp[st.sel], head = '<div class="vg-sum__date">' + longDate(d) + (HOL[st.sel] ? ' <span class="vg-badge">' + HOL[st.sel] + "</span>" : "") + "</div>";
        if (!b) {
          el.fleet.innerHTML = "";
          el.sum.innerHTML = head + '<p class="vg-sum__status is-full">Não há saída nesta data.</p><p class="vg-sum__plan">' +
            (a.boat ? "O rafting sai aos sábados, domingos e feriados." : a.course ? "A turma do curso começa no 2º sábado de cada mês." : "As trilhas saem de terça a domingo.") + "</p>" + suggestion(mp);
          return;
        }
        var al = allocate(b, st.n), fits = al.left === 0, free = freeOf(b);
        el.fleet.innerHTML = b.map(function (x, i) { return unitHTML(i, x, fits ? al.mine[i] : 0); }).join("");
        if (!fits) {
          el.sum.innerHTML = head + '<p class="vg-sum__status is-full">Faltam ' + pl(st.n - free, "vaga", "vagas") + " nesta data</p>" +
            '<p class="vg-sum__plan">' + (free ? "Restam só " + pl(free, "lugar", "lugares") + "." : "Data esgotada.") + " Escolha outra data ou diminua o grupo.</p>" + suggestion(mp);
          return;
        }
        var used = [], solo = 0;
        al.mine.forEach(function (x, i) { if (x) { used.push(unitName(i) + " <b>(" + x + ")</b>"); if (x === a.seats) solo++; } });
        var plan = a.course ? "Vocês ocupam " + pl(st.n, "vaga", "vagas") + " da turma." :
          used.length === 1 ? "Vocês ficam juntos: " + used[0] + "." + (solo ? " " + a.unit + " só de vocês." : "") :
          "Seu grupo vai em " + pl(used.length, a.unit.toLowerCase(), a.unit.toLowerCase() + "s") + ": " + used.join(" + ") + "." +
          (solo ? " " + (solo === 1 ? "1 " + a.unit.toLowerCase() + " só de vocês" : solo + " " + a.unit.toLowerCase() + "s só de vocês") + "." : "");
        el.sum.innerHTML = head + '<p class="vg-sum__status is-' + status(b) + '">' + (status(b) === "few" ? "Cabe! Últimas vagas" : "Cabe todo mundo!") +
          " <span>" + pl(free - st.n, "vaga sobra", "vagas sobram") + " depois de vocês</span></p>" +
          '<p class="vg-sum__plan">' + plan + "</p>" +
          '<a class="btn btn--whats btn--block" href="' + waLink(waMsg(d, al, b)) + '" target="_blank" rel="noopener"><svg class="icon icon--fill" aria-hidden="true"><use href="#i-whatsapp"/></svg> Reservar ' + shortDate(d) + " no WhatsApp</a>";
      });
    }

    function refresh() {
      renderControls();
      return findSoon().then(function (list) {
        if (!st.sel && list[0]) { var d = parse(list[0]); st.sel = list[0]; st.y = d.getFullYear(); st.m = d.getMonth(); }
        renderSoon(list);
        return renderCal();
      }).then(renderDetail);
    }
    function select(k) {
      var d = parse(k);
      st.sel = k;
      if (d.getFullYear() !== st.y || d.getMonth() !== st.m) { st.y = d.getFullYear(); st.m = d.getMonth(); renderCal(); }
      else $$(".vg-day", el.grid).forEach(function (b) { var on = b.getAttribute("data-day") === k; b.classList.toggle("is-sel", on); if (b.hasAttribute("data-day")) b.setAttribute("aria-pressed", String(on)); });
      $$(".vg-chip[data-go]", el.soon).forEach(function (c) { c.setAttribute("aria-pressed", String(c.getAttribute("data-go") === k)); });
      renderDetail();
    }

    el.acts.forEach(function (b) {
      b.addEventListener("click", function () { if (st.act === b.getAttribute("data-act")) return; st.act = b.getAttribute("data-act"); st.sel = null; refresh(); });
    });
    $("select", el.trail).addEventListener("change", function (e) { st.trail = e.target.selectedIndex; st.sel = null; refresh(); });
    [el.minus, el.plus].forEach(function (b) {
      b.addEventListener("click", function () { st.n = Math.max(1, Math.min(cap(), st.n + +b.getAttribute("data-vg-step"))); refresh(); });
    });
    el.prev.addEventListener("click", function () { st.m--; if (st.m < 0) { st.m = 11; st.y--; } renderCal(); });
    el.next.addEventListener("click", function () { st.m++; if (st.m > 11) { st.m = 0; st.y++; } renderCal(); });
    root.addEventListener("click", function (e) {
      var t = e.target.closest("[data-day], [data-go]");
      if (!t) return;
      select(t.getAttribute("data-day") || t.getAttribute("data-go"));
      if (window.innerWidth < 960) el.fleet.scrollIntoView({ behavior: "smooth", block: "center" });
    });

    refresh();

    return {
      /* Usado pela barra de reserva do topo: preenche e rola até a agenda */
      set: function (o) {
        var t = o.atividade || "";
        st.act = /^Rafting 4/.test(t) ? "r4" : /^Rafting 6/.test(t) ? "r6" : /^Trilha/.test(t) ? "tr" : /^Curso/.test(t) ? "cu" : st.act;
        if (st.act === "tr") { var sel = $("select", el.trail); for (var i = 0; i < sel.options.length; i++) if (sel.options[i].text === t) { sel.selectedIndex = i; st.trail = i; } }
        st.n = Math.max(1, Math.min(cap(), parseInt(o.pessoas, 10) || st.n));
        st.sel = null;
        if (o.data && parse(o.data) >= hoje) { var d = parse(o.data); st.sel = o.data; st.y = d.getFullYear(); st.m = d.getMonth(); }
        refresh();
        var sec = $("#vagas");
        if (sec) sec.scrollIntoView({ behavior: "smooth", block: "start" });
      }
    };
  })();

  /* Barra de reserva (home) */
  var booking = $("#booking");
  if (booking) {
    booking.addEventListener("submit", function (e) {
      e.preventDefault();
      if (vagas) {
        vagas.set({ atividade: booking.elements.atividade.value, data: booking.elements.data.value, pessoas: booking.elements.pessoas.value });
        return;
      }
      var act = booking.elements.atividade.value;
      var msg = "Olá, Cia. de Rafting! Quero verificar disponibilidade:\n" +
        "• Atividade: " + act + "\n" +
        "• Data: " + fmtDate(booking.elements.data.value) + "\n" +
        "• Pessoas: " + booking.elements.pessoas.value;
      openLink(waLink(msg));
    });
  }

  /* Formulário de contato */
  var form = $("#contact-form");
  if (form) {
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      if (!form.reportValidity()) return;
      var el = form.elements;
      var msg = "Olá, Cia. de Rafting! Meu nome é " + el.nome.value + ".\n" +
        "• Atividade: " + el.atividade.value + "\n" +
        "• Data desejada: " + fmtDate(el.data.value) + "\n" +
        "• Pessoas: " + el.pessoas.value + "\n" +
        (el.telefone.value ? "• Telefone: " + el.telefone.value + "\n" : "") +
        (el.mensagem.value ? "\n" + el.mensagem.value : "");
      openLink(waLink(msg));
    });
  }

  /* Links de WhatsApp com mensagem pronta: data-wa="texto" */
  $$("[data-wa]").forEach(function (a) {
    a.href = waLink(a.getAttribute("data-wa"));
    a.target = "_blank"; a.rel = "noopener";
  });

  /* Lightbox */
  var lb, lbImg, lbCount, lbItems = [], lbIndex = 0;
  function buildLightbox() {
    lb = document.createElement("div");
    lb.className = "lightbox"; lb.setAttribute("role", "dialog"); lb.setAttribute("aria-modal", "true"); lb.setAttribute("aria-label", "Galeria de fotos");
    lb.innerHTML =
      '<button class="lb-close" aria-label="Fechar"><svg class="icon"><use href="#i-x"/></svg></button>' +
      '<button class="lb-prev" aria-label="Foto anterior"><svg class="icon"><use href="#i-chevron-left"/></svg></button>' +
      '<img alt="">' +
      '<button class="lb-next" aria-label="Próxima foto"><svg class="icon"><use href="#i-chevron-right"/></svg></button>' +
      '<div class="lb-count"></div>';
    document.body.appendChild(lb);
    lbImg = $("img", lb); lbCount = $(".lb-count", lb);
    $(".lb-close", lb).addEventListener("click", closeLightbox);
    $(".lb-prev", lb).addEventListener("click", function () { showLb(lbIndex - 1); });
    $(".lb-next", lb).addEventListener("click", function () { showLb(lbIndex + 1); });
    lb.addEventListener("click", function (e) { if (e.target === lb) closeLightbox(); });
    document.addEventListener("keydown", function (e) {
      if (!lb.classList.contains("is-open")) return;
      if (e.key === "ArrowLeft") showLb(lbIndex - 1);
      if (e.key === "ArrowRight") showLb(lbIndex + 1);
    });
    var sx = 0;
    lb.addEventListener("touchstart", function (e) { sx = e.touches[0].clientX; }, { passive: true });
    lb.addEventListener("touchend", function (e) { var dx = e.changedTouches[0].clientX - sx; if (Math.abs(dx) > 50) showLb(lbIndex + (dx < 0 ? 1 : -1)); });
  }
  function showLb(i) {
    lbIndex = (i + lbItems.length) % lbItems.length;
    var a = lbItems[lbIndex];
    lbImg.src = a.getAttribute("href");
    lbImg.alt = ($("img", a) || {}).alt || "";
    lbCount.textContent = (lbIndex + 1) + " / " + lbItems.length;
  }
  function closeLightbox() {
    if (lb && lb.classList.contains("is-open")) { lb.classList.remove("is-open"); document.body.classList.remove("no-scroll"); }
  }
  $$("[data-lightbox]").forEach(function (group) {
    var items = $$("a", group);
    items.forEach(function (a, i) {
      a.addEventListener("click", function (e) {
        e.preventDefault();
        if (!lb) buildLightbox();
        lbItems = items; showLb(i);
        lb.classList.add("is-open"); document.body.classList.add("no-scroll");
        $(".lb-close", lb).focus();
      });
    });
  });

  /* Carrossel horizontal */
  $$("[data-rail]").forEach(function (nav) {
    var rail = $(nav.getAttribute("data-rail"));
    $$("button", nav).forEach(function (b) {
      b.addEventListener("click", function () {
        rail.scrollBy({ left: parseInt(b.getAttribute("data-dir"), 10) * rail.clientWidth * 0.8, behavior: "smooth" });
      });
    });
  });


  /* Slideshow do topo da home */
  (function () {
    var hero = $(".hero"), box = $("#hero-slides");
    if (!hero || !box) return;
    var slides = $$(".hero__slide", box), bars = $$(".hero__bars button", hero), pauseBtn = $('[data-hero="pause"]', hero);
    var INTERVAL = 6000, cur = 0, timer = null, paused = false;
    var reduce = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    hero.style.setProperty("--hero-interval", INTERVAL + "ms");

    function go(i) {
      var prev = cur;
      cur = (i + slides.length) % slides.length;
      if (cur !== prev) {
        /* a foto antiga fica por baixo até a nova terminar de aparecer */
        slides.forEach(function (s) { s.classList.remove("is-prev"); });
        slides[prev].classList.add("is-prev");
        setTimeout(function () { slides[prev].classList.remove("is-prev"); }, 1400);
      }
      slides.forEach(function (s, k) { s.classList.toggle("is-active", k === cur); s.setAttribute("aria-hidden", String(k !== cur)); });
      syncVideos();
      bars.forEach(function (b, k) {
        b.setAttribute("aria-selected", String(k === cur));
        /* reinicia a barra de progresso */
        var fill = b.firstElementChild; fill.style.animation = "none"; void fill.offsetWidth; fill.style.animation = "";
      });
      schedule();
    }
    function duration() { return parseInt(slides[cur].getAttribute("data-duration"), 10) || INTERVAL; }
    function schedule() {
      clearTimeout(timer);
      hero.style.setProperty("--hero-interval", duration() + "ms");
      if (!paused) timer = setTimeout(function () { go(cur + 1); }, duration());
    }

    /* vídeo: só toca no slide ativo; reinicia ao voltar para ele */
    var videos = $$("video", box);
    function syncVideos() {
      videos.forEach(function (v) {
        var active = v.closest(".hero__slide") === slides[cur];
        if (!v.classList.contains("is-ready")) return;
        if (active && !paused && !document.hidden) {
          try { v.currentTime = 0; } catch (e) {}
          var pr = v.play(); if (pr && pr.catch) pr.catch(function () {});
        } else { v.pause(); }
      });
    }
    function setPaused(p) {
      paused = p; hero.classList.toggle("is-paused", p);
      pauseBtn.setAttribute("aria-pressed", String(p));
      pauseBtn.setAttribute("aria-label", p ? "Retomar apresentação" : "Pausar apresentação");
      if (p) { clearTimeout(timer); videos.forEach(function (v) { v.pause(); }); } else go(cur);
    }
    $('[data-hero="prev"]', hero).addEventListener("click", function () { go(cur - 1); });
    $('[data-hero="next"]', hero).addEventListener("click", function () { go(cur + 1); });
    pauseBtn.addEventListener("click", function () { setPaused(!paused); });
    bars.forEach(function (b, k) { b.addEventListener("click", function () { go(k); }); });

    /* arrastar no celular */
    var sx = 0;
    hero.addEventListener("touchstart", function (e) { sx = e.touches[0].clientX; }, { passive: true });
    hero.addEventListener("touchend", function (e) {
      var dx = e.changedTouches[0].clientX - sx;
      if (Math.abs(dx) > 60) go(cur + (dx < 0 ? 1 : -1));
    });
    /* pausa quando a aba fica oculta */
    document.addEventListener("visibilitychange", function () {
      if (document.hidden) { clearTimeout(timer); videos.forEach(function (v) { v.pause(); }); }
      else { schedule(); syncVideos(); }
    });

    /* Carregamento leve: capa primeiro; fotos e vídeo só depois que a página carregou */
    function afterLoad() {
      $$("img[data-src]", box).forEach(function (im) {
        if (im.dataset.srcset) im.srcset = im.dataset.srcset;
        im.src = im.dataset.src;
        im.removeAttribute("data-src"); im.removeAttribute("data-srcset");
      });
      var c = navigator.connection || {};
      var slow = c.saveData || /(^|-)2g$/.test(c.effectiveType || "");
      if (reduce || slow) return;  /* fica só a capa */
      var small = window.matchMedia("(max-width: 760px)").matches || c.effectiveType === "3g";
      videos.forEach(function (v) {
        v.addEventListener("canplaythrough", function ready() {
          v.removeEventListener("canplaythrough", ready);
          v.classList.add("is-ready");
          /* se o vídeo é o slide atual, recomeça o tempo para ele tocar inteiro */
          if (v.closest(".hero__slide") === slides[cur] && !paused) go(cur); else syncVideos();
        });
        v.preload = "auto";
        v.src = small ? v.dataset.srcMobile : v.dataset.srcDesktop;
        v.load();
      });
    }
    function whenIdle(fn) { if ("requestIdleCallback" in window) requestIdleCallback(fn, { timeout: 1500 }); else setTimeout(fn, 200); }
    if (document.readyState === "complete") whenIdle(afterLoad);
    else window.addEventListener("load", function () { whenIdle(afterLoad); });

    slides.forEach(function (s, k) { s.setAttribute("aria-hidden", String(k !== 0)); });
    if (reduce) setPaused(true); else schedule();
  })();


  /* Logo: remos ao rolar e montagem no rodapé (a entrada é feita no CSS) */
  (function () {
    var reduce = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    if (reduce) return;
    var headLogo = $(".header__logo"), mark = $("[data-logo-parallax]"), ticking = false;
    function update() {
      ticking = false;
      var y = window.scrollY, vh = window.innerHeight;
      if (headLogo) headLogo.style.setProperty("--row", Math.sin(y / 110).toFixed(3));
      if (mark) {
        var top = mark.getBoundingClientRect().top;
        var p = Math.max(0, Math.min(1, (vh - top - 20) / Math.min(vh * 0.35, 300)));
        mark.style.setProperty("--p", p.toFixed(3));
      }
    }
    window.addEventListener("scroll", function () { if (!ticking) { ticking = true; requestAnimationFrame(update); } }, { passive: true });
    window.addEventListener("resize", update);
    update();
  })();

  /* Mascote: fala um pouco quando aparece na tela, ao passar o mouse e ao tocar */
  (function () {
    var list = $$(".mt");
    if (!list.length || window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;
    function talk(el, ms) {
      el.classList.add("is-talking");
      clearTimeout(el._mt);
      el._mt = setTimeout(function () { el.classList.remove("is-talking"); }, ms || 3200);
    }
    list.forEach(function (el) {
      el.addEventListener("mouseenter", function () { talk(el, 2200); });
      el.addEventListener("click", function () { talk(el, 2200); });
    });
    if ("IntersectionObserver" in window) {
      var io = new IntersectionObserver(function (entries) {
        entries.forEach(function (e) { if (e.isIntersecting) talk(e.target); });
      }, { threshold: 0.6 });
      list.forEach(function (el) { io.observe(el); });
    }
  })();

  /* Ano no rodapé */
  $$("[data-year]").forEach(function (el) { el.textContent = new Date().getFullYear(); });
})();
