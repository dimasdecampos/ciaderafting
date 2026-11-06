(function () {
  "use strict";
  var $ = function (s, c) { return (c || document).querySelector(s); };
  var all = function (s, c) { return Array.prototype.slice.call((c || document).querySelectorAll(s)); };
  var reduce = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var mobile = window.matchMedia("(max-width: 1120px)");

  all("[data-year]").forEach(function (el) { el.textContent = new Date().getFullYear(); });

  /* ---------- Menu: submenus ---------- */
  var hd = $("[data-hd]"), nav = $("#nav"), toggle = $(".hd__toggle"), overlay = $("[data-overlay]");
  function closeGroups(except) {
    all(".has-sub.is-open").forEach(function (g) {
      if (g !== except) { g.classList.remove("is-open"); $(".menu__link", g).setAttribute("aria-expanded", "false"); }
    });
  }
  all(".has-sub > .menu__link").forEach(function (b) {
    b.addEventListener("click", function () {
      var g = b.parentNode, open = !g.classList.contains("is-open");
      closeGroups(g);
      g.classList.toggle("is-open", open);
      b.setAttribute("aria-expanded", open);
    });
  });
  document.addEventListener("click", function (e) { if (!mobile.matches && !e.target.closest(".has-sub")) closeGroups(); });

  /* ---------- Menu: gaveta lateral (tablet e celular) ---------- */
  function setNav(open) {
    nav.classList.toggle("is-open", open);
    toggle.setAttribute("aria-expanded", open);
    document.body.classList.toggle("nav-open", open);
    if (open) {
      overlay.hidden = false;
      requestAnimationFrame(function () { overlay.classList.add("is-on"); });
      // abre já o grupo da página atual
      var cur = $(".has-sub.is-current", nav);
      if (cur && !cur.classList.contains("is-open")) $(".menu__link", cur).click();
      setTimeout(function () { var c = $(".nav__close"); if (c) c.focus(); }, 60);
    } else {
      overlay.classList.remove("is-on");
      setTimeout(function () { if (!nav.classList.contains("is-open")) overlay.hidden = true; }, 300);
    }
  }
  if (toggle) toggle.addEventListener("click", function () { setNav(true); });
  var closeBtn = $(".nav__close");
  if (closeBtn) closeBtn.addEventListener("click", function () { setNav(false); toggle.focus(); });
  if (overlay) overlay.addEventListener("click", function () { setNav(false); });
  document.addEventListener("keydown", function (e) {
    if (e.key !== "Escape") return;
    if (nav.classList.contains("is-open")) { setNav(false); toggle.focus(); }
    else closeGroups();
  });
  // mantém o foco dentro da gaveta aberta
  nav.addEventListener("keydown", function (e) {
    if (e.key !== "Tab" || !nav.classList.contains("is-open")) return;
    var f = all("a, button", nav).filter(function (el) { return el.offsetParent !== null; });
    if (!f.length) return;
    if (e.shiftKey && document.activeElement === f[0]) { e.preventDefault(); f[f.length - 1].focus(); }
    else if (!e.shiftKey && document.activeElement === f[f.length - 1]) { e.preventDefault(); f[0].focus(); }
  });
  nav.addEventListener("click", function (e) { if (e.target.closest("a[href^='#']")) setNav(false); });
  if (mobile.addEventListener) mobile.addEventListener("change", function () { setNav(false); closeGroups(); });

  /* ---------- Sombra no cabeçalho + remos do logo ---------- */
  var logo = $(".hd__logo"), ticking = false;
  function onScroll() {
    ticking = false;
    var y = window.scrollY;
    if (hd) hd.classList.toggle("is-stuck", y > 40);
    if (!reduce && logo) logo.style.setProperty("--row", Math.sin(y / 110).toFixed(3));
  }
  window.addEventListener("scroll", function () { if (!ticking) { ticking = true; requestAnimationFrame(onScroll); } }, { passive: true });
  onScroll();

  /* ---------- Entrada suave ---------- */
  var rev = all(".reveal");
  if ("IntersectionObserver" in window && !reduce) {
    var io = new IntersectionObserver(function (es) {
      es.forEach(function (e) { if (e.isIntersecting) { e.target.classList.add("is-in"); io.unobserve(e.target); } });
    }, { rootMargin: "0px 0px -6% 0px" });
    rev.forEach(function (el) { io.observe(el); });
  } else rev.forEach(function (el) { el.classList.add("is-in"); });

  /* ---------- Vídeo da home (só depois da página carregar) ---------- */
  var v = $(".hero video");
  if (v && !reduce && !(navigator.connection || {}).saveData) {
    window.addEventListener("load", function () {
      v.src = window.innerWidth < 760 ? v.dataset.sm : v.dataset.lg;
      v.addEventListener("canplay", function () { v.classList.add("is-ready"); v.play().catch(function () {}); }, { once: true });
    });
  }

  /* ---------- Galerias ---------- */
  all(".gallery").forEach(function (g) {
    var track = $(".gallery__track", g), count = $(".gallery__count", g), slides = all(".gallery__item", g), n = slides.length;
    function idx() {
      var x = track.scrollLeft, best = 0;
      slides.forEach(function (s, i) { if (Math.abs(s.offsetLeft - track.offsetLeft - x) < Math.abs(slides[best].offsetLeft - track.offsetLeft - x)) best = i; });
      // no fim da faixa, o último slide pode não chegar à esquerda
      if (x + track.clientWidth >= track.scrollWidth - 4) best = n - 1;
      return best;
    }
    function go(i) {
      i = (i + n) % n;
      track.scrollTo({ left: slides[i].offsetLeft - track.offsetLeft, behavior: reduce ? "auto" : "smooth" });
    }
    function upd() { count.textContent = (idx() + 1) + " / " + n; }
    all(".gallery__btn", g).forEach(function (b) {
      b.addEventListener("click", function () { go(idx() + (+b.dataset.dir)); });
    });
    track.addEventListener("scroll", function () { requestAnimationFrame(upd); }, { passive: true });
    track.addEventListener("keydown", function (e) {
      if (e.key === "ArrowLeft") { e.preventDefault(); go(idx() - 1); }
      if (e.key === "ArrowRight") { e.preventDefault(); go(idx() + 1); }
    });
    upd();
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
