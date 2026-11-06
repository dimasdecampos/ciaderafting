import os, re, json, sys, hashlib
from PIL import Image

ROOT = sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAGES = os.path.join(os.path.dirname(os.path.abspath(__file__)), "pages")
IMG = os.path.join(ROOT, "assets", "img")
WA = "5512997031363"

LOGO_SVG = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "logo-src", "logo.svg"), encoding="utf-8").read()
MASCOTE_REMANDO = (
    '<div class="masc2" role="img" aria-label="Mascote Tamanduá-de-colete remando no bote"><div class="masc2__rig">'
    '<img class="masc2__body" src="assets/img/mascote-camada-corpo.webp" alt="" width="1000" height="719" loading="lazy" decoding="async">'
    '<img class="masc2__paddle" src="assets/img/mascote-camada-remo.webp" alt="" width="1000" height="719" loading="lazy" decoding="async">'
    '<img class="masc2__hands" src="assets/img/mascote-camada-maos.webp" alt="" width="1000" height="719" loading="lazy" decoding="async">'
    '</div></div>'
)
import importlib.util as _ilu
_spec = _ilu.spec_from_file_location("rig", os.path.join(os.path.dirname(os.path.abspath(__file__)), "mascote-src", "rig.py"))
RIG = _ilu.module_from_spec(_spec); _spec.loader.exec_module(RIG)
_MT_N = [0]

def mascote(pose, label="Mascote Tamanduá-de-colete"):
    """Boneco vetorial do mascote numa pose (ver _src/mascote-src/rig.py)."""
    _MT_N[0] += 1
    return RIG.render(pose, uid=f"mt{_MT_N[0]}", label=label)

LOGO_HEADER = LOGO_SVG.replace('class="logo-svg"', 'class="logo-svg logo-anim"', 1)
LOGO_FOOTER = LOGO_SVG.replace(' role="img" aria-label="Cia. de Rafting"', ' aria-hidden="true" focusable="false"', 1)

ICONS = {
 "clock": '<circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/>',
 "pin": '<path d="M20 10c0 6-8 12-8 12S4 16 4 10a8 8 0 0 1 16 0z"/><circle cx="12" cy="10" r="3"/>',
 "waves": '<path d="M2 6c.6.5 1.2 1 2.5 1C7 7 7 5 9.5 5c2.6 0 2.4 2 5 2 2.5 0 2.5-2 5-2 1.3 0 1.9.5 2.5 1M2 12c.6.5 1.2 1 2.5 1 2.5 0 2.5-2 5-2 2.6 0 2.4 2 5 2 2.5 0 2.5-2 5-2 1.3 0 1.9.5 2.5 1M2 18c.6.5 1.2 1 2.5 1 2.5 0 2.5-2 5-2 2.6 0 2.4 2 5 2 2.5 0 2.5-2 5-2 1.3 0 1.9.5 2.5 1"/>',
 "shield": '<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/><path d="m9 12 2 2 4-4"/>',
 "users": '<path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.87M16 3.13a4 4 0 0 1 0 7.75"/>',
 "check": '<path d="M20 6 9 17l-5-5"/>',
 "calendar": '<rect x="3" y="4" width="18" height="18" rx="2"/><path d="M16 2v4M8 2v4M3 10h18"/>',
 "arrow": '<path d="M5 12h14M12 5l7 7-7 7"/>',
 "arrow-up-right": '<path d="M7 17 17 7M7 7h10v10"/>',
 "chevron-down": '<path d="m6 9 6 6 6-6"/>',
 "chevron-left": '<path d="m15 18-6-6 6-6"/>',
 "chevron-right": '<path d="m9 18 6-6-6-6"/>',
 "x": '<path d="M18 6 6 18M6 6l12 12"/>',
 "menu": '<path d="M4 7h16M4 12h16M4 17h10"/>',
 "mail": '<rect x="2" y="4" width="20" height="16" rx="2"/><path d="m22 7-10 6L2 7"/>',
 "phone": '<path d="M22 16.9v3a2 2 0 0 1-2.2 2 19.8 19.8 0 0 1-8.6-3.1 19.5 19.5 0 0 1-6-6A19.8 19.8 0 0 1 2.1 4.2 2 2 0 0 1 4.1 2h3a2 2 0 0 1 2 1.7c.1.9.4 1.8.7 2.7a2 2 0 0 1-.5 2.1L8 9.8a16 16 0 0 0 6 6l1.3-1.3a2 2 0 0 1 2.1-.4c.9.3 1.8.6 2.7.7a2 2 0 0 1 1.7 2z"/>',
 "award": '<circle cx="12" cy="8" r="6"/><path d="M15.5 12.9 17 22l-5-3-5 3 1.5-9.1"/>',
 "leaf": '<path d="M11 20A7 7 0 0 1 9.8 6.1C15.5 5 17 4.5 19 2c1 2 2 4.2 2 8 0 5.5-4.8 10-10 10Z"/><path d="M2 21c0-3 1.9-5.4 5.2-6.1"/>',
 "mountain": '<path d="m8 3 4 8 5-5 5 15H2L8 3z"/>',
 "backpack": '<path d="M4 10a4 4 0 0 1 4-4h8a4 4 0 0 1 4 4v10a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2z"/><path d="M8 6V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2M8 21v-5a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v5"/>',
 "lifebuoy": '<circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="4"/><path d="m4.9 4.9 4.3 4.3M14.8 14.8l4.3 4.3M14.8 9.2l4.3-4.3M4.9 19.1l4.3-4.3"/>',
 "compass": '<circle cx="12" cy="12" r="10"/><path d="m16.2 7.8-2.1 6.3-6.3 2.1 2.1-6.3z"/>',
 "route": '<circle cx="6" cy="19" r="3"/><path d="M9 19h8.5a3.5 3.5 0 0 0 0-7h-11a3.5 3.5 0 0 1 0-7H15"/><circle cx="18" cy="5" r="3"/>',
 "sun": '<circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M6.3 17.7l-1.4 1.4M19.1 4.9l-1.4 1.4"/>',
 "camera": '<path d="M14.5 4h-5L7 7H4a2 2 0 0 0-2 2v9a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2V9a2 2 0 0 0-2-2h-3z"/><circle cx="12" cy="13" r="3"/>',
 "car": '<path d="M19 17h2v-5l-2-5H5L3 12v5h2"/><circle cx="7" cy="17" r="2"/><circle cx="17" cy="17" r="2"/><path d="M9 17h6"/>',
 "coffee": '<path d="M17 8h1a4 4 0 1 1 0 8h-1M3 8h14v9a4 4 0 0 1-4 4H7a4 4 0 0 1-4-4z"/><path d="M6 2v2M10 2v2M14 2v2"/>',
 "book": '<path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20V2H6.5A2.5 2.5 0 0 0 4 4.5v15z"/><path d="M4 19.5A2.5 2.5 0 0 0 6.5 22H20v-5"/>',
 "heart": '<path d="M19 14c1.5-1.5 3-3.2 3-5.5A5.5 5.5 0 0 0 16.5 3c-1.8 0-3 .5-4.5 2-1.5-1.5-2.7-2-4.5-2A5.5 5.5 0 0 0 2 8.5c0 2.3 1.5 4 3 5.5l7 7z"/>',
 "eye": '<path d="M2 12s3-7 10-7 10 7 10 7-3 7-10 7S2 12 2 12z"/><circle cx="12" cy="12" r="3"/>',
 "target": '<circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="6"/><circle cx="12" cy="12" r="2"/>',
 "info": '<circle cx="12" cy="12" r="10"/><path d="M12 16v-4M12 8h.01"/>',
 "file": '<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><path d="M14 2v6h6M9 13h6M9 17h6"/>',
 "gift": '<rect x="3" y="8" width="18" height="4" rx="1"/><path d="M12 8v13M19 12v7a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2v-7M7.5 8a2.5 2.5 0 0 1 0-5C10 3 12 8 12 8s2-5 4.5-5a2.5 2.5 0 0 1 0 5"/>',
 "radio": '<path d="M4.9 19.1a10 10 0 0 1 0-14.2M7.8 16.2a6 6 0 0 1 0-8.4M16.2 7.8a6 6 0 0 1 0 8.4M19.1 4.9a10 10 0 0 1 0 14.2"/><circle cx="12" cy="12" r="2"/>',
 "paddle": '<path d="m14.5 9.5-9 9"/><path d="M14 4.5c1.8-1.8 4.5-2 5.7-.7 1.3 1.2 1.1 3.9-.7 5.7-1.4 1.4-3.3 1.8-4.6 1.1-.7-1.3-.3-3.2 1.1-4.6z"/><path d="m3 21 2.5-2.5"/>',
 "home": '<path d="m3 10 9-7 9 7v10a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><path d="M9 22V12h6v10"/>',
 "credit": '<rect x="2" y="5" width="20" height="14" rx="2"/><path d="M2 10h20"/>',
 "glasses": '<circle cx="6" cy="15" r="4"/><circle cx="18" cy="15" r="4"/><path d="M10 15a2 2 0 0 1 4 0M2.5 13 5 7c.7-1.3 1.4-2 3-2M21.5 13 19 7c-.7-1.3-1.5-2-3-2"/>',
 "shirt": '<path d="M20.4 6.6 16 4a4 4 0 0 1-8 0L3.6 6.6a1 1 0 0 0-.5 1.2l1 3a1 1 0 0 0 1.2.6L7 11v9a1 1 0 0 0 1 1h8a1 1 0 0 0 1-1v-9l1.7.4a1 1 0 0 0 1.2-.6l1-3a1 1 0 0 0-.5-1.2z"/>',
 "instagram": '<rect x="2" y="2" width="20" height="20" rx="5"/><circle cx="12" cy="12" r="4"/><path d="M17.5 6.5h.01"/>',
 "facebook": '<path d="M18 2h-3a5 5 0 0 0-5 5v3H7v4h3v8h4v-8h3l1-4h-4V7a1 1 0 0 1 1-1h3z"/>',
}
WHATS_PATH = '<path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413Z"/>'

SPRITE = '<svg width="0" height="0" style="position:absolute" aria-hidden="true">' + "".join(
    f'<symbol id="i-{k}" viewBox="0 0 24 24">{v}</symbol>' for k, v in ICONS.items()
) + f'<symbol id="i-whatsapp" viewBox="0 0 24 24">{WHATS_PATH}</symbol></svg>'

_dims = {}
def dims(name):
    if name not in _dims:
        with Image.open(os.path.join(IMG, name + ".webp")) as im:
            _dims[name] = im.size
    return _dims[name]

def img(name, alt, sizes="100vw", extra=""):
    if "defer" in extra:
        lazy = 'decoding="async" data-defer'
    elif "preload" in extra:
        lazy = 'loading="eager" fetchpriority="low"'
    elif "eager" in extra:
        lazy = 'loading="eager" fetchpriority="high"'
    else:
        lazy = 'loading="lazy"'
    defer = "defer" in extra
    extra = extra.replace("defer", "").replace("preload", "").replace("eager", "").strip()
    w, h = dims(name)
    small = os.path.exists(os.path.join(IMG, name + "-sm.webp"))
    if small:
        sw, _ = dims(name + "-sm")
        src = f'src="assets/img/{name}-sm.webp" srcset="assets/img/{name}-sm.webp {sw}w, assets/img/{name}.webp {w}w" sizes="{sizes}"'
    else:
        src = f'src="assets/img/{name}.webp"'
    if defer:  # carrega só depois da página (via JS)
        src = src.replace('src="', 'data-src="', 1).replace(' srcset="', ' data-srcset="', 1)
        src = 'src="data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7" ' + src
        lazy = ""
    return f'<img {src} alt="{alt}" width="{w}" height="{h}" {lazy} decoding="async" {extra}>'.replace("  ", " ").replace(" >", ">")

def icon(name, cls=""):
    classes = "icon" + (" icon--fill" if name == "whatsapp" else "") + (" " + cls if cls else "")
    return f'<svg class="{classes}" aria-hidden="true"><use href="#i-{name}"/></svg>'

def _macro(s, name, fn):
    out, i, tag = [], 0, "@" + name + "("
    while True:
        j = s.find(tag, i)
        if j < 0:
            out.append(s[i:]); return "".join(out)
        out.append(s[i:j]); k = j + len(tag); depth = 1
        while depth:
            c = s[k]
            if c == "(": depth += 1
            elif c == ")": depth -= 1
            k += 1
        out.append(fn([a.strip() for a in s[j + len(tag):k - 1].split("|")])); i = k

def expand(s):
    s = s.replace("@@MASCOTE_REMANDO@@", MASCOTE_REMANDO)
    s = _macro(s, "g", lambda a: f'<a href="assets/img/{a[0]}.webp">' + img(a[0], a[1], "(max-width: 700px) 100vw, 25vw") + '</a>')
    s = _macro(s, "img", lambda a: img(a[0], a[1], a[2] if len(a) > 2 and a[2] else "100vw", a[3] if len(a) > 3 else ""))
    s = _macro(s, "mascote", lambda a: mascote(a[0], a[1] if len(a) > 1 else "Mascote Tamanduá-de-colete"))
    s = _macro(s, "icon", lambda a: icon(a[0], a[1] if len(a) > 1 else ""))
    return s

NAV = [
    ("index", "Início", "index.html"),
]

def header(active):
    def cur(k): return ' aria-current="page"' if k == active else ""
    return f'''
<a class="skip-link" href="#conteudo">Pular para o conteúdo</a>
{SPRITE}
<div class="topbar">
  <div class="container">
    <div class="topbar__badges">
      <span>@icon(shield) Segurança certificada ISO 21.101</span>
      <span>@icon(award) Desde 1996 no Rio Paraibuna</span>
      <span>@icon(pin) São Luiz do Paraitinga · SP</span>
    </div>
    <div class="topbar__links">
      <a href="mailto:contato@ciaderafting.com.br">contato@ciaderafting.com.br</a>
      <a href="tel:+5512997031363">(12) 99703-1363</a>
    </div>
  </div>
</div>
<header class="header">
  <div class="container">
    <a class="header__logo" href="index.html" aria-label="Cia. de Rafting — página inicial">
      {LOGO_HEADER}
    </a>
    <nav class="nav" aria-label="Principal">
      <div class="nav__item"><a class="nav__link" href="index.html"{cur("index")}>Início</a></div>
      <div class="nav__item">
        <button class="nav__link" aria-haspopup="true"{cur("atividades")}>Atividades @icon(chevron-down)</button>
        <div class="dropdown dropdown--mega">
          <a class="mega-card" href="rafting-4-horas.html">@img(rafting-comemoracao|Grupo comemorando no bote|180px)<span>Rafting 4 horas<small>Brazadão · Natividade da Serra</small></span></a>
          <a class="mega-card" href="rafting-6-horas.html">@img(corredeira-cachoeira|Bote em corredeira forte|180px)<span>Rafting 6 horas<small>Núcleo · Classe II a IV</small></span></a>
          <a class="mega-card" href="trilhas.html">@img(trilha-grupo|Grupo em trilha na mata|180px)<span>Trilhas<small>Núcleo Santa Virgínia</small></span></a>
          <a class="mega-card" href="curso-de-rafting.html">@img(curso-vira-bote|Treino de virar o bote|180px)<span>Curso de Rafting<small>Formação básica · 48h</small></span></a>
        </div>
      </div>
      <div class="nav__item">
        <button class="nav__link" aria-haspopup="true"{cur("sobre")}>A Cia. @icon(chevron-down)</button>
        <div class="dropdown">
          <a href="sobre.html">Sobre nós<small>História, missão e valores</small></a>
          <a href="sobre.html#seguranca">Política de segurança<small>ISO 21.101 certificada</small></a>
          <a href="sobre.html#equipe">Nossa equipe<small>Quem guia sua aventura</small></a>
          <a href="sobre.html#mascote">Mascote<small>O Tamanduá-de-colete</small></a>
        </div>
      </div>
      <div class="nav__item">
        <button class="nav__link" aria-haspopup="true"{cur("destino")}>Destino @icon(chevron-down)</button>
        <div class="dropdown">
          <a href="destino.html#serra-do-mar">Pq. Estadual da Serra do Mar<small>Núcleo Santa Virgínia</small></a>
          <a href="destino.html#sao-luiz">São Luiz do Paraitinga<small>Patrimônio histórico e cultura</small></a>
          <a href="destino.html#como-chegar">Como chegar<small>Rotas de SP, RJ e Campinas</small></a>
        </div>
      </div>
      <div class="nav__item"><a class="nav__link" href="contato.html"{cur("contato")}>Contato</a></div>
    </nav>
    <div class="header__cta">
      <a class="btn btn--sm" href="#" data-wa="Olá, Cia. de Rafting! Gostaria de fazer uma reserva.">Reservar @icon(arrow|icon--arrow)</a>
      <button class="menu-toggle" data-drawer-open aria-controls="drawer" aria-expanded="false" aria-label="Abrir menu">@icon(menu)</button>
    </div>
  </div>
</header>

<div class="drawer" id="drawer" aria-hidden="true">
  <div class="drawer__top">
    <img src="assets/img/logo-branco.webp" alt="Cia. de Rafting" width="900" height="394">
    <button class="menu-toggle" style="display:inline-flex" data-drawer-close aria-label="Fechar menu">@icon(x)</button>
  </div>
  <nav class="drawer__nav" aria-label="Menu mobile">
    <a href="index.html">Início</a>
    <details><summary>Atividades @icon(chevron-down)</summary>
      <a href="rafting-4-horas.html">Rafting 4 horas · Brazadão</a>
      <a href="rafting-6-horas.html">Rafting 6 horas · Núcleo</a>
      <a href="trilhas.html">Trilhas</a>
      <a href="curso-de-rafting.html">Curso de Rafting</a>
    </details>
    <details><summary>A Cia. @icon(chevron-down)</summary>
      <a href="sobre.html">Sobre nós</a>
      <a href="sobre.html#seguranca">Política de segurança</a>
      <a href="sobre.html#equipe">Nossa equipe</a>
      <a href="sobre.html#mascote">Mascote</a>
    </details>
    <details><summary>Destino @icon(chevron-down)</summary>
      <a href="destino.html#serra-do-mar">Pq. Estadual da Serra do Mar</a>
      <a href="destino.html#sao-luiz">São Luiz do Paraitinga</a>
      <a href="destino.html#como-chegar">Como chegar</a>
    </details>
    <a href="contato.html">Contato</a>
  </nav>
  <div class="drawer__foot">
    <a class="btn btn--whats btn--block" href="#" data-wa="Olá, Cia. de Rafting! Gostaria de fazer uma reserva.">@icon(whatsapp) Reservar pelo WhatsApp</a>
    <a class="btn btn--ghost btn--block" href="tel:+5512997031363">@icon(phone) (12) 99703-1363</a>
  </div>
</div>
'''

FOOTER = '''
<footer class="footer">
  <div class="container">
    <div class="footer__grid">
      <div class="footer__brand">
        <a class="footer__mark" href="index.html" aria-label="Cia. de Rafting — página inicial" data-logo-parallax>@@LOGO_FOOTER@@</a>
        <p>Conectando pessoas à natureza desde 1996. Rafting, trilhas e formação de guias na Mata Atlântica da Serra do Mar.</p>
        <div class="socials">
          <a href="https://www.instagram.com/ciaderafting/" target="_blank" rel="noopener" aria-label="Instagram">@icon(instagram)</a>
          <a href="https://www.facebook.com/Ciaderafting" target="_blank" rel="noopener" aria-label="Facebook">@icon(facebook)</a>
          <a href="#" data-wa="Olá, Cia. de Rafting!" aria-label="WhatsApp">@icon(whatsapp)</a>
        </div>
      </div>
      <div>
        <h4>Atividades</h4>
        <ul>
          <li><a href="rafting-4-horas.html">Rafting 4 horas · Brazadão</a></li>
          <li><a href="rafting-6-horas.html">Rafting 6 horas · Núcleo</a></li>
          <li><a href="trilhas.html">Trilhas</a></li>
          <li><a href="curso-de-rafting.html">Curso de Rafting</a></li>
        </ul>
      </div>
      <div>
        <h4>A Cia.</h4>
        <ul>
          <li><a href="sobre.html">Sobre nós</a></li>
          <li><a href="sobre.html#seguranca">Política de segurança</a></li>
          <li><a href="sobre.html#equipe">Nossa equipe</a></li>
          <li><a href="sobre.html#mascote">Mascote</a></li>
          <li><a href="destino.html">O destino</a></li>
        </ul>
      </div>
      <div>
        <h4>Fale com a gente</h4>
        <ul class="footer__contact">
          <li>@icon(phone)<a href="tel:+5512997031363">+55 (12) 99703-1363</a></li>
          <li>@icon(mail)<a href="mailto:contato@ciaderafting.com.br">contato@ciaderafting.com.br</a></li>
          <li>@icon(pin)<span>Base: Sítio Água · Rod. Dr. Oswaldo Cruz, km 66,5 · São Luiz do Paraitinga – SP</span></li>
        </ul>
      </div>
    </div>
    <div class="footer__bottom">
      <span>© 1996–<span data-year>2026</span> Cia. de Rafting. Todos os direitos reservados.</span>
      <div class="footer__seals"><span>ISO 21.101 certificada</span><span>CADASTUR 26.028025.10.0001-1</span></div>
    </div>
  </div>
</footer>

<a class="wa-float" href="#" data-wa="Olá, Cia. de Rafting! Vim pelo site e gostaria de mais informações." aria-label="Falar no WhatsApp">@icon(whatsapp)</a>
<div class="mobile-bar">
  <a class="btn btn--ghost" href="tel:+5512997031363">@icon(phone) Ligar</a>
  <a class="btn btn--whats" href="#" data-wa="Olá, Cia. de Rafting! Gostaria de fazer uma reserva.">@icon(whatsapp) Reservar</a>
</div>
<script src="assets/js/main.js?v=@@JSVER@@" defer></script>
'''

def ver(rel):
    with open(os.path.join(ROOT, rel), "rb") as f:
        return hashlib.md5(f.read()).hexdigest()[:8]

def head(meta):
    title = meta["title"]
    desc = meta["description"]
    og = meta.get("og", "hero-corredeira")
    ld = meta.get("jsonld", "")
    pre = f'<link rel="preload" as="image" href="{meta["preload"]}" fetchpriority="high">' + chr(10) if meta.get("preload") else ""
    return f'''<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<meta name="theme-color" content="#0c1f1a">
<meta property="og:type" content="website">
<meta property="og:locale" content="pt_BR">
<meta property="og:site_name" content="Cia. de Rafting">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:image" content="assets/img/{og}.webp">
<link rel="icon" type="image/png" href="assets/img/favicon.png">
<link rel="apple-touch-icon" href="assets/img/apple-touch-icon.png">
{pre}<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Anton&family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<link rel="stylesheet" href="assets/css/style.css?v={ver("assets/css/style.css")}">
<script>(function(){{var d=document.documentElement,n=4,v=1+Math.floor(Math.random()*n);try{{var l=+sessionStorage.getItem("lg-last")||0;if(v===l)v=v%n+1;sessionStorage.setItem("lg-last",v)}}catch(e){{}}d.setAttribute("data-lg",v)}})();</script>
{ld}
</head>
<body class="has-hero">
'''

def build():
    for f in sorted(os.listdir(PAGES)):
        raw = open(os.path.join(PAGES, f), encoding="utf-8").read()
        first, body = raw.split("\n", 1)
        meta = json.loads(first)
        html = head(meta) + header(meta.get("active", "")) + '\n<main id="conteudo">\n' + body + "\n</main>\n" + FOOTER.replace("@@LOGO_FOOTER@@", LOGO_FOOTER).replace("@@JSVER@@", ver("assets/js/main.js")) + "</body>\n</html>\n"
        html = expand(html)
        open(os.path.join(ROOT, f), "w", encoding="utf-8", newline="\n").write(html)
        print("ok", f, len(html))
    # favicons a partir do mascote
    m = Image.open(os.path.join(IMG, "mascote-bote.webp")).convert("RGBA")
    m = m.crop(m.getbbox())
    for size, name in ((64, "favicon.png"), (180, "apple-touch-icon.png")):
        c = Image.new("RGBA", (size, size), (255, 214, 10, 255) if size == 180 else (0, 0, 0, 0))
        t = m.copy(); t.thumbnail((int(size * .92), int(size * .92)))
        c.alpha_composite(t, ((size - t.width) // 2, (size - t.height) // 2))
        c.save(os.path.join(IMG, name))

build()
