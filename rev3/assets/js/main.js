(function () {
  var $ = function (s, c) { return (c || document).querySelector(s); };
  var $$ = function (s, c) { return Array.prototype.slice.call((c || document).querySelectorAll(s)); };

  // Cabeçalho fica sólido ao rolar
  var top = $(".top");
  var onScroll = function () { top.classList.toggle("is-solid", window.scrollY > 40); };
  onScroll();
  window.addEventListener("scroll", onScroll, { passive: true });

  // Menu no celular
  var toggle = $(".menu-toggle");
  if (toggle) {
    toggle.addEventListener("click", function () {
      var open = document.body.classList.toggle("menu-open");
      toggle.setAttribute("aria-expanded", open);
    });
    $$(".nav a").forEach(function (a) { a.addEventListener("click", function () { document.body.classList.remove("menu-open"); }); });
  }

  // Revelação suave
  if ("IntersectionObserver" in window) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) { if (e.isIntersecting) { e.target.classList.add("is-in"); io.unobserve(e.target); } });
    }, { rootMargin: "0px 0px -8% 0px" });
    $$(".reveal").forEach(function (el) { io.observe(el); });
  } else {
    $$(".reveal").forEach(function (el) { el.classList.add("is-in"); });
  }

  // Galeria com ampliação
  var links = $$(".gallery a");
  if (links.length) {
    var lb = document.createElement("div");
    lb.className = "lightbox";
    lb.setAttribute("role", "dialog");
    lb.setAttribute("aria-label", "Foto ampliada");
    lb.innerHTML = '<img alt=""><button class="lb-close" type="button">Fechar</button><button class="lb-prev" type="button">Anterior</button><button class="lb-next" type="button">Próxima</button>';
    document.body.appendChild(lb);
    var img = $("img", lb), i = 0;
    var show = function (n) { i = (n + links.length) % links.length; img.src = links[i].href; img.alt = $("img", links[i]).alt; };
    var close = function () { lb.classList.remove("is-open"); };
    links.forEach(function (a, n) { a.addEventListener("click", function (e) { e.preventDefault(); show(n); lb.classList.add("is-open"); }); });
    $(".lb-close", lb).addEventListener("click", close);
    $(".lb-prev", lb).addEventListener("click", function () { show(i - 1); });
    $(".lb-next", lb).addEventListener("click", function () { show(i + 1); });
    lb.addEventListener("click", function (e) { if (e.target === lb) close(); });
    document.addEventListener("keydown", function (e) {
      if (!lb.classList.contains("is-open")) return;
      if (e.key === "Escape") close();
      if (e.key === "ArrowLeft") show(i - 1);
      if (e.key === "ArrowRight") show(i + 1);
    });
  }

  // Formulário de contato: abre a mensagem pronta no WhatsApp ou no e-mail
  var form = $("#contato-form");
  if (form) {
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      if (!form.reportValidity()) return;
      var d = new FormData(form), via = e.submitter && e.submitter.value;
      var assunto = "Contato pelo site — " + (d.get("interesse") || "Informações");
      var txt = "Nome: " + d.get("nome") +
        (d.get("telefone") ? "\nTelefone: " + d.get("telefone") : "") +
        (d.get("data") ? "\nData desejada: " + d.get("data") : "") +
        (d.get("pessoas") ? "\nPessoas: " + d.get("pessoas") : "") +
        "\n\n" + d.get("mensagem");
      if (via === "email") {
        location.href = "mailto:" + form.dataset.email + "?subject=" + encodeURIComponent(assunto) + "&body=" + encodeURIComponent(txt);
      } else {
        window.open("https://wa.me/" + form.dataset.whatsapp + "?text=" + encodeURIComponent("*" + assunto + "*\n" + txt), "_blank", "noopener");
      }
    });
  }
})();
