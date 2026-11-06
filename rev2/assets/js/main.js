(function () {
  "use strict";
  var $ = function (s, c) { return (c || document).querySelector(s); };
  var $$ = function (s, c) { return Array.prototype.slice.call((c || document).querySelectorAll(s)); };
  var reduce = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var mobile = window.matchMedia("(max-width: 1080px)");

  $$("[data-year]").forEach(function (el) { el.textContent = new Date().getFullYear(); });

  /* ---------- Menu ---------- */
  var bar = $(".menubar"), menu = $("#menu"), btn = $(".menu-btn");
  function closeGroups(except) {
    $$(".menu__group.is-open").forEach(function (g) {
      if (g !== except) { g.classList.remove("is-open"); $(".menu__link", g).setAttribute("aria-expanded", "false"); }
    });
  }
  function setMenu(open) {
    if (bar) document.documentElement.style.setProperty("--menu-top", bar.getBoundingClientRect().bottom + "px");
    menu.classList.toggle("is-open", open);
    btn.setAttribute("aria-expanded", open);
    btn.setAttribute("aria-label", open ? "Fechar menu" : "Abrir menu");
    document.body.classList.toggle("menu-open", open);
  }
  if (btn) btn.addEventListener("click", function () { setMenu(!menu.classList.contains("is-open")); });
  $$(".menu__group > .menu__link").forEach(function (b) {
    b.addEventListener("click", function () {
      var g = b.parentNode, open = !g.classList.contains("is-open");
      closeGroups(g);
      g.classList.toggle("is-open", open);
      b.setAttribute("aria-expanded", open);
    });
  });
  // no celular, abre já o grupo da página atual
  $$(".menu__sub [aria-current]").forEach(function (a) {
    var g = a.closest(".menu__group");
    if (g && mobile.matches) { g.classList.add("is-open"); $(".menu__link", g).setAttribute("aria-expanded", "true"); }
  });
  document.addEventListener("click", function (e) { if (!mobile.matches && !e.target.closest(".menu__group")) closeGroups(); });
  document.addEventListener("keydown", function (e) {
    if (e.key !== "Escape") return;
    closeGroups();
    if (menu.classList.contains("is-open")) { setMenu(false); btn.focus(); }
  });
  mobile.addEventListener && mobile.addEventListener("change", function () { setMenu(false); closeGroups(); });

  /* ---------- Sombra no menu ao rolar + remos do logo + logo do rodapé ---------- */
  var logo = $(".menubar__logo"), mark = $("[data-logo-parallax]"), ticking = false;
  function onScroll() {
    ticking = false;
    var y = window.scrollY, vh = window.innerHeight;
    if (bar) bar.classList.toggle("is-stuck", bar.getBoundingClientRect().top <= 0 && y > 10);
    if (reduce) return;
    if (logo) logo.style.setProperty("--row", Math.sin(y / 110).toFixed(3));
    if (mark) {
      var top = mark.getBoundingClientRect().top;
      mark.style.setProperty("--p", Math.max(0, Math.min(1, (vh - top - 20) / Math.min(vh * .35, 300))).toFixed(3));
    }
  }
  window.addEventListener("scroll", function () { if (!ticking) { ticking = true; requestAnimationFrame(onScroll); } }, { passive: true });
  window.addEventListener("resize", onScroll);
  onScroll();

  /* ---------- Entrada suave ---------- */
  var rev = $$(".reveal");
  if ("IntersectionObserver" in window && !reduce) {
    var io = new IntersectionObserver(function (es) {
      es.forEach(function (e) { if (e.isIntersecting) { e.target.classList.add("is-in"); io.unobserve(e.target); } });
    }, { rootMargin: "0px 0px -8% 0px" });
    rev.forEach(function (el) { io.observe(el); });
  } else rev.forEach(function (el) { el.classList.add("is-in"); });

  /* ---------- Vídeo da home (só depois da página carregar) ---------- */
  var v = $(".hero video");
  if (v && !reduce) {
    var conn = navigator.connection || {};
    if (!conn.saveData) {
      window.addEventListener("load", function () {
        var src = window.innerWidth < 760 ? v.dataset.sm : v.dataset.lg;
        v.src = src;
        v.addEventListener("canplay", function () { v.classList.add("is-ready"); v.play().catch(function () {}); }, { once: true });
      });
    }
  }

  /* ---------- Galerias (carrossel com contador) ---------- */
  $$(".gallery").forEach(function (g) {
    var track = $(".gallery__track", g), count = $(".gallery__count", g), n = track.children.length;
    function idx() { return Math.round(track.scrollLeft / track.clientWidth); }
    function go(i) { track.scrollTo({ left: ((i + n) % n) * track.clientWidth, behavior: reduce ? "auto" : "smooth" }); }
    function upd() { count.textContent = (idx() + 1) + "/" + n; }
    $(".gallery__nav--prev", g).addEventListener("click", function () { go(idx() - 1); });
    $(".gallery__nav--next", g).addEventListener("click", function () { go(idx() + 1); });
    track.addEventListener("scroll", function () { requestAnimationFrame(upd); }, { passive: true });
    track.addEventListener("keydown", function (e) {
      if (e.key === "ArrowLeft") { e.preventDefault(); go(idx() - 1); }
      if (e.key === "ArrowRight") { e.preventDefault(); go(idx() + 1); }
    });
    upd();
    if (!reduce) {
      var t = setInterval(function () { go(idx() + 1); }, 5000);
      ["pointerdown", "focusin", "wheel"].forEach(function (ev) { g.addEventListener(ev, function () { clearInterval(t); }, { passive: true }); });
    }
  });

  /* ---------- Formulário de contato: monta a mensagem e abre o WhatsApp ou o e-mail ---------- */
  var form = $("#contato-form");
  if (form) {
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      if (!form.reportValidity()) return;
      var d = new FormData(form), via = e.submitter && e.submitter.value;
      var txt = "Olá, Cia. de Rafting!\n\n" + d.get("mensagem") + "\n\n" +
        "Nome: " + d.get("nome") + "\nE-mail: " + d.get("email") +
        (d.get("telefone") ? "\nTelefone: " + d.get("telefone") : "") +
        (d.get("endereco") ? "\nEndereço: " + d.get("endereco") : "");
      var assunto = d.get("assunto") || "Contato pelo site";
      if (via === "email") {
        location.href = "mailto:" + form.dataset.email + "?subject=" + encodeURIComponent(assunto) + "&body=" + encodeURIComponent(txt);
      } else {
        window.open("https://wa.me/" + form.dataset.whatsapp + "?text=" + encodeURIComponent("*" + assunto + "*\n" + txt), "_blank", "noopener");
      }
    });
  }
})();
