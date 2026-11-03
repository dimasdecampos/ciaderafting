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

  /* Barra de reserva (home) */
  var booking = $("#booking");
  if (booking) {
    booking.addEventListener("submit", function (e) {
      e.preventDefault();
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

  /* Ano no rodapé */
  $$("[data-year]").forEach(function (el) { el.textContent = new Date().getFullYear(); });
})();
