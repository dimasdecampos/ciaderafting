"""Gera as páginas da rev5 a partir de _conteudo/.

Uso (a partir da pasta rev5):  python _src/build.py
Dependências:                  pip install pillow pyyaml markdown

Sistema de páginas (pensado para virar WordPress depois — ver README.md):
- _conteudo/site.yml          dados gerais + menu
- _conteudo/paginas/*.yaml    uma página por arquivo:
    titulo_aba, descricao     -> título da aba / descrição do Google
    topo                      -> topo da página (título, subtítulo, foto)
    secoes                    -> lista de seções; cada seção tem fundo, título e blocos
"""
import os, re, sys, hashlib, html
from urllib.parse import quote

import yaml
import markdown
from PIL import Image

SRC = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(SRC)
CONT = os.path.join(ROOT, "_conteudo")
IMG = os.path.join(ROOT, "assets", "img")

SITE = yaml.safe_load(open(os.path.join(CONT, "site.yml"), encoding="utf-8"))
WA = SITE["whatsapp"]
EMAIL = SITE["email"]
warnings = []


def warn(msg):
    warnings.append(msg)
    print("AVISO:", msg)


esc = lambda s: html.escape(str(s if s is not None else ""), quote=True)
_md = markdown.Markdown(extensions=["nl2br", "sane_lists"])


def md(s):
    if not s:
        return ""
    _md.reset()
    return _md.convert(str(s).strip())


def mdi(s):
    out = md(s)
    if out.startswith("<p>") and out.endswith("</p>") and out.count("<p>") == 1:
        out = out[3:-4]
    return out


LOGO = open(os.path.join(SRC, "logo.svg"), encoding="utf-8").read()
LOGO_HD = LOGO.replace('class="logo-svg"', 'class="logo-svg logo-anim"', 1)
LOGO_PLAIN = LOGO.replace(' role="img" aria-label="Cia. de Rafting"', ' aria-hidden="true" focusable="false"', 1)

ICONS = {
    "mail": '<rect x="2" y="4" width="20" height="16" rx="2"/><path d="m22 7-10 6L2 7"/>',
    "pin": '<path d="M20 10c0 6-8 12-8 12s-8-6-8-12a8 8 0 0 1 16 0Z"/><circle cx="12" cy="10" r="3"/>',
    "chevron": '<path d="m6 9 6 6 6-6"/>',
    "left": '<path d="m15 18-6-6 6-6"/>',
    "right": '<path d="m9 18 6-6-6-6"/>',
    "menu": '<path d="M4 7h16M4 12h16M4 17h10"/>',
    "x": '<path d="M18 6 6 18M6 6l12 12"/>',
    "arrow": '<path d="M5 12h14M12 5l7 7-7 7"/>',
    "file": '<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><path d="M14 2v6h6M9 13h6M9 17h6"/>',
    "shield": '<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/><path d="m9 12 2 2 4-4"/>',
    "check": '<path d="M20 6 9 17l-5-5"/>',
    "clock": '<circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/>',
    "instagram": '<rect x="2" y="2" width="20" height="20" rx="5"/><circle cx="12" cy="12" r="4"/><path d="M17.5 6.5h.01"/>',
    "facebook": '<path d="M18 2h-3a5 5 0 0 0-5 5v3H7v4h3v8h4v-8h3l1-4h-4V7a1 1 0 0 1 1-1h3z"/>',
}
WHATS = '<path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413Z"/>'
SPRITE = ('<svg width="0" height="0" style="position:absolute" aria-hidden="true">'
          + "".join(f'<symbol id="i-{k}" viewBox="0 0 24 24">{v}</symbol>' for k, v in ICONS.items())
          + f'<symbol id="i-whatsapp" viewBox="0 0 24 24">{WHATS}</symbol>'
          + '<filter id="brush" x="-2%" y="-40%" width="104%" height="180%"><feTurbulence type="fractalNoise" baseFrequency=".035 .6" numOctaves="2" seed="7"/><feDisplacementMap in="SourceGraphic" scale="7"/></filter>'
          + '</svg>')

STRIPES = ('<svg class="stripes" viewBox="0 0 1200 16" preserveAspectRatio="none" aria-hidden="true"><g filter="url(#brush)">'
           '<rect x="-20" y="1" width="1240" height="5" fill="var(--red)"/><rect x="-20" y="6" width="1240" height="5" fill="var(--yellow)"/>'
           '<rect x="-20" y="11" width="1240" height="4" fill="var(--blue)"/></g></svg>')


def icon(name, cls=""):
    if name not in ICONS and name != "whatsapp":
        return ""
    c = "icon" + (" icon--fill" if name == "whatsapp" else "") + (" " + cls if cls else "")
    return f'<svg class="{c}" aria-hidden="true"><use href="#i-{name}"/></svg>'


def wa(msg=None):
    return f"https://wa.me/{WA}?text={quote(msg or SITE.get('mensagem_padrao', ''))}"


# ---------------- imagens ----------------
_img_cache = {}


def resolve(ref):
    """'foto.webp', 'foto' ou '/qualquer/caminho/foto.webp' -> (base, w, h, largura_sm) ou None."""
    ref = str(ref or "").strip()
    if not ref:
        return None
    if ref in _img_cache:
        return _img_cache[ref]
    stem = os.path.splitext(os.path.basename(ref))[0]
    path = os.path.join(IMG, stem + ".webp")
    if not os.path.exists(path):
        warn(f"imagem não encontrada: {ref}")
        _img_cache[ref] = None
        return None
    with Image.open(path) as im:
        w, h = im.size
    sw = None
    sm = os.path.join(IMG, stem + "-sm.webp")
    if os.path.exists(sm):
        with Image.open(sm) as im:
            sw = im.size[0]
    _img_cache[ref] = ("assets/img/" + stem, w, h, sw)
    return _img_cache[ref]


def img(ref, alt="", sizes="100vw", eager=False, cls=""):
    r = resolve(ref)
    if not r:
        return ""
    base, w, h, sw = r
    if sw:
        src = f'src="{base}-sm.webp" srcset="{base}-sm.webp {sw}w, {base}.webp {w}w" sizes="{sizes}"'
    else:
        src = f'src="{base}.webp"'
    load = 'fetchpriority="high"' if eager else 'loading="lazy"'
    c = f' class="{cls}"' if cls else ""
    return f'<img{c} {src} alt="{esc(alt)}" width="{w}" height="{h}" {load} decoding="async">'


# ---------------- menu ----------------
MENU = SITE.get("menu") or []


def trilha_de_pao(page):
    """Devolve [(texto, link)] do menu até a página atual (para o caminho no topo)."""
    for m in MENU:
        if m.get("link") == page:
            return [(m["texto"], None)]
        for s in m.get("itens") or []:
            if s.get("link") == page:
                return [(m["texto"], None), (s["texto"], None)]
    return []


def menu_html(page):
    out = []
    for n, m in enumerate(MENU):
        subs = m.get("itens") or []
        if not subs:
            cur = ' aria-current="page"' if m.get("link") == page else ""
            out.append(f'<li class="menu__item"><a class="menu__link"{cur} href="{esc(m.get("link"))}">{esc(m["texto"])}</a></li>')
            continue
        on = any(s.get("link") == page for s in subs)
        cur = ' aria-current="page"'
        items = "".join(
            f'<li><a href="{esc(s.get("link"))}"{cur if s.get("link") == page else ""}>{esc(s["texto"])}</a></li>'
            for s in subs)
        out.append(f'<li class="menu__item has-sub{" is-current" if on else ""}">'
                   f'<button class="menu__link" type="button" aria-expanded="false" aria-controls="sub-{n}">{esc(m["texto"])}{icon("chevron", "menu__chev")}</button>'
                   f'<div class="menu__panel" id="sub-{n}"><ul>{items}</ul></div></li>')
    return "".join(out)


def social_links(cls=""):
    return (f'<a class="{cls}" href="{esc(SITE["facebook"])}" target="_blank" rel="noopener" aria-label="Facebook">{icon("facebook")}</a>'
            f'<a class="{cls}" href="{esc(SITE["instagram"])}" target="_blank" rel="noopener" aria-label="Instagram">{icon("instagram")}</a>')


def header(page):
    return f'''<a class="skip" href="#conteudo">Pular para o conteúdo</a>
{SPRITE}
<div class="util">
  <div class="wrap util__in">
    <p class="util__place">{icon("pin")}<span>{esc(SITE["cidade"])}</span></p>
    <div class="util__links">
      <a href="mailto:{esc(EMAIL)}">{icon("mail")}<span>{esc(EMAIL)}</span></a>
      <a href="{wa()}" target="_blank" rel="noopener">{icon("whatsapp")}<span>{esc(SITE["whatsapp_exibicao"])}</span></a>
      <span class="util__social">{social_links()}</span>
    </div>
  </div>
</div>
<header class="hd" data-hd>
  <div class="wrap hd__in">
    <a class="hd__logo" href="index.html" aria-label="Cia. de Rafting — página inicial">{LOGO_HD}</a>
    <nav class="nav" id="nav" aria-label="Principal">
      <div class="nav__head">
        <span class="nav__title">Menu</span>
        <button class="nav__close" type="button" aria-label="Fechar menu">{icon("x")}</button>
      </div>
      <ul class="menu">{menu_html(page)}</ul>
      <div class="nav__foot">
        <a class="btn btn--wa btn--block" href="{wa(SITE.get("mensagem_reserva"))}" target="_blank" rel="noopener">{icon("whatsapp")}Reservar pelo WhatsApp</a>
        <a class="nav__contact" href="mailto:{esc(EMAIL)}">{icon("mail")}{esc(EMAIL)}</a>
        <a class="nav__contact" href="{wa()}" target="_blank" rel="noopener">{icon("whatsapp")}{esc(SITE["whatsapp_exibicao"])}</a>
        <div class="nav__social">{social_links("round")}</div>
      </div>
    </nav>
    <div class="hd__actions">
      <a class="btn btn--wa hd__cta" href="{wa(SITE.get("mensagem_reserva"))}" target="_blank" rel="noopener">{icon("whatsapp")}<span>Reservar</span></a>
      <button class="hd__toggle" type="button" aria-controls="nav" aria-expanded="false" aria-label="Abrir menu">{icon("menu")}<span>Menu</span></button>
    </div>
  </div>
  {STRIPES}
</header>
<div class="nav-overlay" data-overlay hidden></div>
'''


def cta_final():
    return f'''<section class="cta" aria-label="Fale conosco">
  <div class="wrap cta__in reveal">
    <img class="cta__mascot" src="assets/img/mascote-bote.webp" alt="" width="319" height="332" loading="lazy">
    <div class="cta__txt">
      <h2>Fale com a Cia. de Rafting</h2>
      <p>Para informações gerais e esclarecimento de dúvidas, entre em contato conosco.</p>
    </div>
    <div class="cta__btns">
      <a class="btn btn--wa" href="{wa(SITE.get("mensagem_reserva"))}" target="_blank" rel="noopener">{icon("whatsapp")}Reservar pelo WhatsApp</a>
      <a class="btn btn--line" href="contato.html">{icon("mail")}Outras formas de contato</a>
    </div>
  </div>
</section>
'''


def footer():
    cols = []
    for m in MENU:
        subs = m.get("itens") or []
        if subs:
            links = "".join(f'<li><a href="{esc(s.get("link"))}">{esc(s["texto"])}</a></li>' for s in subs)
            cols.append(f'<div class="ft__col"><h3>{esc(m["texto"])}</h3><ul>{links}</ul></div>')
    return f'''
<footer class="ft">
  {STRIPES}
  <div class="wrap ft__grid">
    <div class="ft__brand">
      <a class="ft__logo" href="index.html" aria-label="Cia. de Rafting — página inicial">{LOGO_PLAIN}</a>
      <p>{esc(SITE.get("slogan", ""))}</p>
      <div class="ft__social">{social_links("round")}</div>
    </div>
    {"".join(cols)}
    <div class="ft__col">
      <h3>Contato</h3>
      <ul class="ft__contact">
        <li>{icon("pin")}<span>{esc(SITE["cidade"])}</span></li>
        <li><a href="{wa()}" target="_blank" rel="noopener">{icon("whatsapp")}{esc(SITE["whatsapp_exibicao"])}</a></li>
        <li><a href="mailto:{esc(EMAIL)}">{icon("mail")}{esc(EMAIL)}</a></li>
      </ul>
    </div>
  </div>
  <div class="ft__bottom">
    <div class="wrap ft__bottom-in">
      <p>Copyright © Cia. de Rafting · {esc(SITE.get("ano_inicio", 1996))}–<span data-year>2026</span></p>
      <p class="ft__seals"><span>{icon("shield")}{esc(SITE.get("selo_iso", ""))}</span><span>{esc(SITE.get("cadastur", ""))}</span></p>
    </div>
  </div>
</footer>
<a class="wa-float" href="{wa(SITE.get("mensagem_site"))}" target="_blank" rel="noopener" aria-label="Falar no WhatsApp">{icon("whatsapp")}</a>
'''


def ver(rel):
    with open(os.path.join(ROOT, rel), "rb") as f:
        return hashlib.md5(f.read()).hexdigest()[:8]


def head(title, desc, og):
    og_tag = f'<meta property="og:image" content="{og}.webp">\n' if og else ""
    return f'''<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<meta name="theme-color" content="#ffffff">
<meta property="og:type" content="website">
<meta property="og:locale" content="pt_BR">
<meta property="og:site_name" content="Cia. de Rafting">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(desc)}">
{og_tag}<link rel="icon" type="image/png" href="assets/img/favicon.png">
<link rel="apple-touch-icon" href="assets/img/apple-touch-icon.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Archivo:wght@600;700;800&family=Barlow:wght@400;500;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="assets/css/style.css?v={ver("assets/css/style.css")}">
<script>(function(){{var d=document.documentElement,n=4,v=1+Math.floor(Math.random()*n);try{{var l=+sessionStorage.getItem("lg-last")||0;if(v===l)v=v%n+1;sessionStorage.setItem("lg-last",v)}}catch(e){{}}d.setAttribute("data-lg",v);d.classList.add("js")}})();</script>
</head>
<body>
'''


# ---------------- blocos ----------------
# Blocos "largos" ocupam a largura toda da seção (no WordPress: alinhamento "largo").
WIDE = {"cartoes", "equipe", "galeria", "numeros", "colunas", "trilhas", "ficha", "missao", "imagem"}


def items(b, key="itens"):
    return [i for i in (b.get(key) or []) if i]


def link_attrs(url):
    url = str(url or "")
    return f'href="{esc(url)}"' + (' target="_blank" rel="noopener"' if url.startswith("http") else "")


def button(texto, link, estilo="azul", icone="", mensagem=""):
    if estilo == "whatsapp" and not link:
        link = wa(mensagem or SITE.get("mensagem_reserva"))
    if not icone and estilo == "whatsapp":
        icone = "whatsapp"
    cls = {"whatsapp": "btn btn--wa", "linha": "btn btn--line", "claro": "btn btn--light"}.get(estilo, "btn")
    before = icon(icone) if icone not in ("", "nenhum", "seta") else ""
    after = icon("arrow", "btn__arrow") if icone == "seta" else ""
    return f'<a class="{cls}" {link_attrs(link)}>{before}{esc(texto)}{after}</a>'


def b_texto(b):
    return f'<div class="md">{md(b.get("texto"))}</div>'


def b_destaque(b):
    return f'<div class="lead">{md(b.get("texto"))}</div>'


def b_titulo(b):
    ident = f' id="{esc(b["ancora"])}"' if b.get("ancora") else ""
    return f'<h2 class="h-sec"{ident}>{esc(b.get("titulo"))}</h2>'


def b_sobretitulo(b):
    return f'<p class="eyebrow">{esc(b.get("texto"))}</p>'


def facts(lst):
    return "".join(f'<div class="fact"><dt>{esc(i.get("rotulo"))}</dt><dd>{mdi(i.get("valor"))}</dd></div>' for i in lst)


def b_fatos(b):
    return f'<dl class="facts">{facts(items(b))}</dl>'


def b_selos(b):
    return '<ul class="badges">' + "".join(f'<li>{icon("shield")}{esc(t)}</li>' for t in items(b)) + "</ul>"


def b_caixa(b):
    cls = "box" + {"azul": " box--blue", "alerta": " box--alert", "destaque": " box--feature"}.get(b.get("estilo"), "")
    titulo = f'<h3>{esc(b["titulo"])}</h3>' if b.get("titulo") else ""
    btn = ""
    if b.get("botao_texto"):
        btn = f'<a class="btn btn--line btn--sm" {link_attrs(b.get("botao_link"))}>{icon("file")}{esc(b["botao_texto"])}</a>'
    inner = titulo + md(b.get("texto")) + btn
    if b.get("selo"):
        first, _, rest = str(b["selo"]).partition(" ")
        inner = (f'<div class="seal" aria-hidden="true"><b>{esc(first)}</b><span>{esc(rest)}</span></div>'
                 f'<div class="box__txt">{inner}</div>')
        cls += " box--seal"
    return f'<div class="{cls}">{inner}</div>'


def b_botoes(b):
    btns = "".join(button(i.get("texto"), i.get("link"), i.get("estilo") or "azul", i.get("icone") or "", i.get("mensagem") or "") for i in items(b))
    return f'<div class="btns">{btns}</div>'


def b_galeria(b):
    figs = []
    for i in items(b, "fotos"):
        tag = img(i.get("imagem"), i.get("alt"), "(max-width: 700px) 85vw, 560px")
        if tag:
            figs.append(f'<figure class="gallery__item">{tag}</figure>')
    if not figs:
        return ""
    return (f'<div class="gallery" aria-roledescription="carrossel" aria-label="{esc(b.get("titulo") or "Galeria de fotos")}">'
            f'<div class="gallery__track" tabindex="0">{"".join(figs)}</div>'
            f'<div class="gallery__bar"><span class="gallery__count" aria-live="polite">1 / {len(figs)}</span>'
            f'<span class="gallery__nav"><button type="button" class="gallery__btn" data-dir="-1" aria-label="Foto anterior">{icon("left")}</button>'
            f'<button type="button" class="gallery__btn" data-dir="1" aria-label="Próxima foto">{icon("right")}</button></span></div></div>')


def b_etiquetas(b):
    return '<ul class="tags">' + "".join(f"<li>{esc(t)}</li>" for t in items(b)) + "</ul>"


def b_barras(b):
    rows = "".join(f'<div class="bar"><span>{esc(i.get("rotulo"))}</span><i style="--v:{int(i.get("valor") or 0)}%"></i><b>{int(i.get("valor") or 0)}%</b></div>' for i in items(b))
    return f'<div class="bars">{rows}</div>'


def b_citacao(b):
    return f'<blockquote class="quote"><p>{mdi(b.get("texto"))}</p></blockquote>'


def b_missao(b):
    cards = "".join(f'<div class="mvv__item"><span class="mvv__n">0{n + 1}</span><h3>{esc(i.get("titulo"))}</h3>{md(i.get("texto"))}</div>'
                    for n, i in enumerate(items(b)))
    return f'<div class="mvv">{cards}</div>'


def b_ficha(b):
    return f'<dl class="sheet">{facts(items(b))}</dl>'


def b_preco(b):
    rows = "".join(f'<div class="price__row"><small>{esc(i.get("rotulo"))}</small><b>{esc(i.get("valor"))}</b></div>' for i in items(b))
    return f'<div class="price">{rows}</div>'


def b_trilha(b):
    hard = " lvl--hard" if b.get("pesada") else ""
    lvl = f'<span class="lvl{hard}">{esc(b["nivel"])}</span>' if b.get("nivel") else ""
    return (f'<article class="trail"><header class="trail__head"><h3>{esc(b.get("nome"))}</h3>{lvl}</header>'
            f'<dl class="trail__facts">{facts(items(b, "fatos"))}</dl>'
            f'<details class="trail__more"><summary>Roteiro, ambiente e ponto de encontro{icon("chevron")}</summary>'
            f'<div class="md">{md(b.get("detalhes"))}</div></details></article>')


def b_equipe(b):
    people = "".join(
        f'<figure class="member"><div class="member__img">{img(p.get("foto"), p.get("nome"), "(max-width: 600px) 45vw, 220px")}</div>'
        f'<figcaption>{esc(p.get("nome"))}</figcaption></figure>' for p in items(b, "pessoas"))
    return f'<div class="team">{people}</div>'


def b_cartoes(b):
    largo = b.get("estilo") == "largo"
    sizes = "(max-width: 700px) 100vw, 50vw" if largo else "(max-width: 600px) 100vw, (max-width: 1100px) 50vw, 300px"
    cards = "".join(
        f'<a class="card" href="{esc(i.get("link"))}"><div class="card__img">{img(i.get("imagem"), i.get("alt"), sizes)}</div>'
        f'<div class="card__body"><h3>{esc(i.get("titulo"))}</h3><p>{esc(i.get("texto"))}</p>'
        f'<span class="card__go">Saiba mais{icon("arrow")}</span></div></a>'
        for i in items(b))
    return f'<div class="cards{" cards--2" if largo else ""}">{cards}</div>'


def b_numeros(b):
    cells = "".join(f'<div class="stat"><b>{esc(i.get("valor"))}</b><span>{esc(i.get("rotulo"))}</span></div>' for i in items(b))
    return f'<div class="stats">{cells}</div>'


def b_imagem(b):
    return f'<figure class="fig">{img(b.get("imagem"), b.get("alt"), "(max-width: 900px) 100vw, 560px")}</figure>'


def b_colunas(b):
    return (f'<div class="cols"><div class="cols__col">{render_blocks(b.get("esquerda") or [], "colunas")}</div>'
            f'<div class="cols__col">{render_blocks(b.get("direita") or [], "colunas")}</div></div>')


def b_formulario(b):
    hint = b.get("dica") or "A mensagem abre pronta no WhatsApp ou no seu e-mail — é só confirmar o envio."
    return f'''<form class="form" id="contato-form" data-whatsapp="{esc(WA)}" data-email="{esc(EMAIL)}">
        <h3 class="form__title">Envie uma mensagem</h3>
        <label>Nome *<input name="nome" required autocomplete="name"></label>
        <label>E-mail *<input name="email" type="email" required autocomplete="email"></label>
        <label>Telefone<input name="telefone" type="tel" autocomplete="tel"></label>
        <label>Endereço<input name="endereco" autocomplete="street-address"></label>
        <label class="full">Assunto<input name="assunto"></label>
        <label class="full">Mensagem *<textarea name="mensagem" required rows="5"></textarea></label>
        <div class="full btns">
          <button class="btn btn--wa" type="submit" value="whatsapp">{icon("whatsapp")}Enviar pelo WhatsApp</button>
          <button class="btn btn--line" type="submit" value="email">{icon("mail")}Enviar por e-mail</button>
        </div>
        <p class="form__hint full">{esc(hint)}</p>
      </form>'''


BLOCKS = {
    "texto": b_texto, "destaque": b_destaque, "titulo": b_titulo, "sobretitulo": b_sobretitulo, "fatos": b_fatos,
    "selos": b_selos, "caixa": b_caixa, "botoes": b_botoes, "galeria": b_galeria, "etiquetas": b_etiquetas,
    "barras": b_barras, "citacao": b_citacao, "missao": b_missao, "ficha": b_ficha, "preco": b_preco,
    "trilha": b_trilha, "equipe": b_equipe, "cartoes": b_cartoes, "formulario": b_formulario,
    "numeros": b_numeros, "imagem": b_imagem, "colunas": b_colunas,
}


def render_blocks(blocks, slug):
    """Renderiza uma lista de blocos. Caixas e trilhas seguidas viram uma grade."""
    out, i = [], 0
    blocks = [b for b in blocks if b]
    while i < len(blocks):
        kind = blocks[i].get("tipo")
        if kind in ("caixa", "trilha"):
            j = i
            while j < len(blocks) and blocks[j].get("tipo") == kind:
                j += 1
            inner = "".join(BLOCKS[kind](b) for b in blocks[i:j])
            if j - i > 1:
                cls = "trails alignwide" if kind == "trilha" else "boxes"
                out.append(f'<div class="{cls} reveal">{inner}</div>')
            else:
                out.append(f'<div class="reveal{" alignwide" if kind == "trilha" else ""}">{inner}</div>')
            i = j
            continue
        fn = BLOCKS.get(kind)
        if not fn:
            warn(f"{slug}: bloco desconhecido '{kind}'")
            i += 1
            continue
        html_ = fn(blocks[i])
        if html_:
            wide = " alignwide" if kind in WIDE else ""
            out.append(f'<div class="blk blk--{kind}{wide} reveal">{html_}</div>' if kind not in ("titulo", "sobretitulo") else html_)
        i += 1
    return "\n".join(out)


# ---------------- seções e topo ----------------
def secao(s, slug):
    fundo = s.get("fundo") or "branco"
    ident = f' id="{esc(s["ancora"])}"' if s.get("ancora") else ""
    blocks = [b for b in (s.get("blocos") or []) if b]
    wide = any(b.get("tipo") in WIDE or b.get("tipo") == "trilha" for b in blocks)
    head = ""
    if s.get("titulo") or s.get("sobretitulo"):
        eb = f'<p class="eyebrow">{esc(s["sobretitulo"])}</p>' if s.get("sobretitulo") else ""
        h = f'<h2>{esc(s["titulo"])}</h2>' if s.get("titulo") else ""
        head = f'<header class="sec__head{" sec__head--center" if wide and not s.get("lado") else ""} reveal">{eb}{h}</header>'
    lado = s.get("lado") or {}
    if lado.get("imagem"):
        art = f'<figure class="sec__art reveal">{img(lado["imagem"], lado.get("alt"), "(max-width: 800px) 60vw, 320px")}</figure>'
        body = f'<div class="sec__body">{head}{render_blocks(blocks, slug)}</div>'
        left = lado.get("posicao") == "esquerda"
        inner = f'<div class="sec__split{" sec__split--left" if left else ""}">{art + body if left else body + art}</div>'
    else:
        inner = f'{head}<div class="sec__body">{render_blocks(blocks, slug)}</div>'
    return f'<section class="sec sec--{esc(fundo)}"{ident}>\n<div class="wrap">{inner}</div>\n</section>'


def topo(t, page):
    eb = f'<p class="eyebrow">{esc(t["sobretitulo"])}</p>' if t.get("sobretitulo") else ""
    sub = f'<p class="topo__sub">{esc(t["subtitulo"])}</p>' if t.get("subtitulo") else ""
    btns = ""
    if t.get("botoes"):
        btns = b_botoes({"itens": t["botoes"]})
    if t.get("estilo") == "video":
        return (f'<section class="hero" aria-label="Rafting no Rio Paraibuna">'
                f'<div class="hero__media">{img(t.get("imagem"), t.get("alt"), "100vw", eager=True)}'
                '<video muted loop playsinline preload="none" poster="assets/video/rafting-hero-poster.webp" '
                'data-sm="assets/video/rafting-hero-480.mp4" data-lg="assets/video/rafting-hero-720.mp4" aria-hidden="true"></video></div>'
                f'<div class="wrap hero__in">{eb}<h1>{esc(t.get("titulo"))}</h1>{sub}{btns}</div></section>')
    crumbs = trilha_de_pao(page)
    nav = ""
    if crumbs and page != "index.html":
        parts = ['<li><a href="index.html">Home</a></li>'] + [f"<li>{esc(c)}</li>" for c, _l in crumbs[:-1]]
        nav = f'<nav class="crumbs" aria-label="Você está em"><ol>{"".join(parts)}</ol></nav>'
    foto = img(t.get("imagem"), t.get("alt"), "(max-width: 900px) 100vw, 50vw", eager=True)
    fig = f'<figure class="topo__img">{foto}</figure>' if foto else ""
    return (f'<section class="topo{"" if fig else " topo--sem-foto"}"><div class="wrap topo__in">'
            f'<div class="topo__txt">{nav}{eb}<h1>{esc(t.get("titulo"))}</h1>{sub}{btns}</div>{fig}</div></section>')


def render_page(slug, data):
    page = slug + ".html"
    t = data.get("topo") or {}
    secs = "\n".join(secao(s, slug) for s in (data.get("secoes") or []) if s)
    og = resolve(t.get("imagem"))
    return (head(data.get("titulo_aba") or "Cia. de Rafting", data.get("descricao") or "", og[0] if og else None)
            + header(page) + '<main id="conteudo">\n' + topo(t, page) + "\n" + secs + "\n"
            + (cta_final() if slug != "contato" else "") + "</main>\n"
            + footer() + f'<script src="assets/js/main.js?v={ver("assets/js/main.js")}" defer></script>\n</body>\n</html>\n')


def build():
    pages = os.path.join(CONT, "paginas")
    for f in sorted(os.listdir(pages)):
        if not f.endswith((".yml", ".yaml")):
            continue
        slug = os.path.splitext(f)[0]
        data = yaml.safe_load(open(os.path.join(pages, f), encoding="utf-8")) or {}
        open(os.path.join(ROOT, slug + ".html"), "w", encoding="utf-8", newline="\n").write(render_page(slug, data))
        print("ok", slug + ".html")
    if "--estrito" in sys.argv and warnings:
        sys.exit(1)


if __name__ == "__main__":
    build()
