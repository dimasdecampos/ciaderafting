"""Gera as páginas da rev2 a partir do conteúdo editável em _conteudo/.

Uso (a partir da pasta rev2):  python _src/build.py
Dependências:                  pip install pillow pyyaml markdown

- _conteudo/site.yml            dados gerais (contatos, redes, rodapé)
- _conteudo/paginas/*.yml       uma página por arquivo: dados da aba + lista de blocos
O painel de edição (Pages CMS, ver /.pages.yml na raiz do repositório) altera esses arquivos;
uma automação do GitHub roda este script e publica o site.
"""
import os, re, sys, hashlib, html, unicodedata
from urllib.parse import quote

import yaml
import markdown
from PIL import Image, ImageOps

SRC = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(SRC)
CONT = os.path.join(ROOT, "_conteudo")
IMG = os.path.join(ROOT, "assets", "img")
AUTO = os.path.join(IMG, "auto")  # versões .webp geradas de fotos enviadas em jpg/png

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
    """Markdown (ou HTML simples) -> HTML de blocos."""
    if not s:
        return ""
    _md.reset()
    return _md.convert(str(s).strip())


def mdi(s):
    """Markdown de uma linha -> HTML sem o <p> externo."""
    out = md(s)
    if out.startswith("<p>") and out.endswith("</p>") and out.count("<p>") == 1:
        out = out[3:-4]
    return out


LOGO = open(os.path.join(SRC, "logo.svg"), encoding="utf-8").read()
LOGO_MENU = LOGO.replace('class="logo-svg"', 'class="logo-svg logo-anim"', 1)
LOGO_FOOTER = LOGO.replace(' role="img" aria-label="Cia. de Rafting"', ' aria-hidden="true" focusable="false"', 1)

ICONS = {
    "mail": '<rect x="2" y="4" width="20" height="16" rx="2"/><path d="m22 7-10 6L2 7"/>',
    "phone": '<path d="M22 16.9v3a2 2 0 0 1-2.2 2 19.8 19.8 0 0 1-8.6-3.1 19.5 19.5 0 0 1-6-6A19.8 19.8 0 0 1 2.1 4.2 2 2 0 0 1 4.1 2h3a2 2 0 0 1 2 1.7c.1.9.4 1.8.7 2.7a2 2 0 0 1-.5 2.1L8 9.8a16 16 0 0 0 6 6l1.3-1.3a2 2 0 0 1 2.1-.4c.9.3 1.8.6 2.7.7a2 2 0 0 1 1.7 2z"/>',
    "chevron": '<path d="m6 9 6 6 6-6"/>',
    "left": '<path d="m15 18-6-6 6-6"/>',
    "right": '<path d="m9 18 6-6-6-6"/>',
    "menu": '<path d="M4 7h16M4 12h16M4 17h16"/>',
    "x": '<path d="M18 6 6 18M6 6l12 12"/>',
    "arrow": '<path d="M5 12h14M12 5l7 7-7 7"/>',
    "file": '<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><path d="M14 2v6h6M9 13h6M9 17h6"/>',
    "shield": '<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/><path d="m9 12 2 2 4-4"/>',
    "instagram": '<rect x="2" y="2" width="20" height="20" rx="5"/><circle cx="12" cy="12" r="4"/><path d="M17.5 6.5h.01"/>',
    "facebook": '<path d="M18 2h-3a5 5 0 0 0-5 5v3H7v4h3v8h4v-8h3l1-4h-4V7a1 1 0 0 1 1-1h3z"/>',
}
WHATS = '<path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413Z"/>'
SPRITE = ('<svg width="0" height="0" style="position:absolute" aria-hidden="true">'
          + "".join(f'<symbol id="i-{k}" viewBox="0 0 24 24">{v}</symbol>' for k, v in ICONS.items())
          + f'<symbol id="i-whatsapp" viewBox="0 0 24 24">{WHATS}</symbol>'
          # pincelada: borda irregular nas listras, como no cabeçalho original
          + '<filter id="brush" x="-2%" y="-40%" width="104%" height="180%"><feTurbulence type="fractalNoise" baseFrequency=".035 .6" numOctaves="2" seed="7"/><feDisplacementMap in="SourceGraphic" scale="9"/></filter>'
          + '</svg>')


def icon(name, cls=""):
    if name not in ICONS and name != "whatsapp":
        return ""
    c = "icon" + (" icon--fill" if name == "whatsapp" else "") + (" " + cls if cls else "")
    return f'<svg class="{c}" aria-hidden="true"><use href="#i-{name}"/></svg>'


def wa(msg=None):
    return f"https://wa.me/{WA}?text={quote(msg or SITE.get('mensagem_padrao', ''))}"


# ---------------- imagens ----------------
_img_cache = {}


def safe_name(stem):
    """Nome de arquivo seguro para URL (sem espaços, acentos ou símbolos)."""
    s = unicodedata.normalize("NFKD", stem).encode("ascii", "ignore").decode()
    return re.sub(r"[^A-Za-z0-9_-]+", "-", s).strip("-") or "imagem"


def _convert(src, stem):
    """Fotos enviadas em jpg/png (ou com nome fora do padrão) viram .webp em assets/img/auto/."""
    stem = safe_name(stem)
    os.makedirs(AUTO, exist_ok=True)
    out = os.path.join(AUTO, stem + ".webp")
    out_sm = os.path.join(AUTO, stem + "-sm.webp")
    if not os.path.exists(out) or os.path.getmtime(out) < os.path.getmtime(src):
        im = ImageOps.exif_transpose(Image.open(src))
        im = im.convert("RGBA" if "A" in im.getbands() else "RGB")
        im.thumbnail((1800, 1800))
        im.save(out, "WEBP", quality=82)
        if im.width > 900:
            sm = im.copy(); sm.thumbnail((800, 800)); sm.save(out_sm, "WEBP", quality=80)
        elif os.path.exists(out_sm):
            os.remove(out_sm)
    return "assets/img/auto/" + stem


def resolve(ref):
    """Aceita '/rev2/assets/img/foto.jpg', 'foto.webp' ou só 'foto'. Devolve (base_url, w, h, sw) ou None."""
    ref = str(ref or "").strip()
    if not ref:
        return None
    if ref in _img_cache:
        return _img_cache[ref]
    name = os.path.basename(ref)
    stem, ext = os.path.splitext(name)
    base = None
    if ext.lower() == ".webp" and os.path.exists(os.path.join(IMG, name)):
        base = "assets/img/" + stem if safe_name(stem) == stem else _convert(os.path.join(IMG, name), stem)
    elif ext.lower() in (".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tif", ".tiff") and os.path.exists(os.path.join(IMG, name)):
        base = _convert(os.path.join(IMG, name), stem)
    elif not ext and os.path.exists(os.path.join(IMG, stem + ".webp")):
        base = "assets/img/" + stem
    if base is None:
        warn(f"imagem não encontrada: {ref}")
        _img_cache[ref] = None
        return None
    with Image.open(os.path.join(ROOT, base + ".webp")) as im:
        w, h = im.size
    sm = os.path.join(ROOT, base + "-sm.webp")
    sw = None
    if os.path.exists(sm):
        with Image.open(sm) as im:
            sw = im.size[0]
    _img_cache[ref] = (base, w, h, sw)
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


# ---------------- menu (mesma estrutura do site original) ----------------
MENU = [
    ("index", "Home", "index.html", None),
    ("cia", "A Cia. de Rafting", None, [
        ("Sobre nós", "sobre-nos.html"),
        ("Política de segurança", "politica-de-seguranca.html"),
        ("Nossa equipe", "nossa-equipe.html"),
        ("Mascote", "mascote.html"),
        ("Pq. Estadual da Serra do Mar", "pq-estadual-da-serra-do-mar.html"),
        ("São Luiz do Paraitinga", "sao-luiz-do-paraitinga.html"),
    ]),
    ("atividades", "Atividades", None, [
        ("Expedição de rafting 4 horas – Brazadão", "expedicao-de-rafting-4-horas-brazadao.html"),
        ("Expedição de rafting 6 horas – Núcleo", "expedicao-de-rafting-6-horas-nucleo.html"),
        ("Trilhas", "trilhas.html"),
    ]),
    ("educacao", "Educação & Treinamento", None, [
        ("Curso de rafting", "curso-de-rafting.html"),
    ]),
    ("contato", "Contato", "contato.html", None),
]


def active_key(page):
    for key, _l, href, sub in MENU:
        if href == page or (sub and any(h == page for _t, h in sub)):
            return key
    return ""


def menu_html(active, page):
    out = []
    cur = ' aria-current="page"'
    for key, label, href, sub in MENU:
        on = cur if key == active else ""
        if not sub:
            out.append(f'<li><a class="menu__link"{on} href="{href}">{label}</a></li>')
            continue
        items = "".join(f'<li><a href="{h}"{cur if h == page else ""}>{t}</a></li>' for t, h in sub)
        out.append(f'<li class="menu__group"><button class="menu__link"{on} aria-expanded="false">{label}{icon("chevron")}</button>'
                   f'<ul class="menu__sub">{items}</ul></li>')
    return "".join(out)


def header(page):
    active = active_key(page)
    return f'''<a class="skip" href="#conteudo">Pular para o conteúdo</a>
{SPRITE}
<header class="top">
  <div class="band">
    <div class="wrap band__in">
      <a class="band__mascot" href="index.html" aria-label="Cia. de Rafting — página inicial">
        <img src="assets/img/mascote-bote.webp" alt="" width="319" height="332">
      </a>
      <div class="band__contact">
        <a href="mailto:{esc(EMAIL)}">{icon("mail")}<span>{esc(EMAIL)}</span></a>
        <a href="{wa()}" target="_blank" rel="noopener">{icon("whatsapp")}<span>Fone/WhatsApp {esc(SITE["whatsapp_exibicao"])}</span></a>
      </div>
    </div>
  </div>
  <svg class="stripes" viewBox="0 0 1200 36" preserveAspectRatio="none" aria-hidden="true">
    <g filter="url(#brush)">
      <rect x="-20" y="2" width="1240" height="9" fill="var(--red)"/>
      <rect x="-20" y="11" width="1240" height="9" fill="var(--yellow)"/>
      <rect x="-20" y="21" width="1240" height="8" fill="var(--blue)"/>
    </g>
  </svg>
</header>
<nav class="menubar" aria-label="Principal">
  <div class="wrap menubar__in">
    <div class="menubar__social">
      <a href="{esc(SITE["facebook"])}" target="_blank" rel="noopener" aria-label="Facebook">{icon("facebook")}</a>
      <a href="{esc(SITE["instagram"])}" target="_blank" rel="noopener" aria-label="Instagram">{icon("instagram")}</a>
    </div>
    <a class="menubar__logo" href="index.html" aria-label="Cia. de Rafting — página inicial">{LOGO_MENU}</a>
    <ul class="menu" id="menu">{menu_html(active, page)}</ul>
    <div class="menubar__end">
      <a class="btn-wa" href="{wa(SITE.get("mensagem_reserva"))}" target="_blank" rel="noopener">{icon("whatsapp")}<span>WhatsApp</span></a>
      <button class="menu-btn" aria-controls="menu" aria-expanded="false" aria-label="Abrir menu">{icon("menu", "i-open")}{icon("x", "i-close")}</button>
    </div>
  </div>
</nav>
'''


def footer():
    return f'''
<footer class="foot">
  <svg class="stripes stripes--thin" viewBox="0 0 1200 20" preserveAspectRatio="none" aria-hidden="true">
    <g filter="url(#brush)"><rect x="-20" y="3" width="1240" height="5" fill="var(--red)"/><rect x="-20" y="8" width="1240" height="5" fill="var(--yellow)"/><rect x="-20" y="13" width="1240" height="5" fill="var(--blue)"/></g>
  </svg>
  <div class="wrap foot__in">
    <img class="foot__mascot" src="assets/img/mascote-fala.webp" alt="Mascote Tamanduá-de-colete" width="319" height="332" loading="lazy">
    <div class="foot__mid">
      <a class="foot__logo" href="index.html" aria-label="Cia. de Rafting — página inicial" data-logo-parallax>{LOGO_FOOTER}</a>
      <p class="foot__place">{esc(SITE["cidade"])}</p>
      <p class="foot__contacts">
        <a href="mailto:{esc(EMAIL)}">{esc(EMAIL)}</a>
        <a href="{wa()}" target="_blank" rel="noopener">{esc(SITE["whatsapp_exibicao"])}</a>
      </p>
    </div>
    <div class="foot__legal">
      <p>Copyright © Cia. de Rafting<br>{esc(SITE.get("ano_inicio", 1996))}–<span data-year>2026</span></p>
      <p>{esc(SITE.get("selo_iso", ""))}<br>{esc(SITE.get("cadastur", ""))}</p>
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
<meta name="theme-color" content="#1f4c9a">
<meta property="og:type" content="website">
<meta property="og:locale" content="pt_BR">
<meta property="og:site_name" content="Cia. de Rafting">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(desc)}">
{og_tag}<link rel="icon" type="image/png" href="assets/img/favicon.png">
<link rel="apple-touch-icon" href="assets/img/apple-touch-icon.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Barlow:wght@300;400;500;600;700&family=Chelsea+Market&display=swap" rel="stylesheet">
<link rel="stylesheet" href="assets/css/style.css?v={ver("assets/css/style.css")}">
<script>(function(){{var d=document.documentElement,n=4,v=1+Math.floor(Math.random()*n);try{{var l=+sessionStorage.getItem("lg-last")||0;if(v===l)v=v%n+1;sessionStorage.setItem("lg-last",v)}}catch(e){{}}d.setAttribute("data-lg",v)}})();</script>
</head>
<body>
'''


# ---------------- blocos de conteúdo ----------------
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
    cls = {"whatsapp": "btn btn--wa", "linha": "btn btn--line"}.get(estilo, "btn")
    before = icon(icone) if icone not in ("", "nenhum", "seta") else ""
    after = icon("arrow") if icone == "seta" else ""
    return f'<a class="{cls}" {link_attrs(link)}>{before}{esc(texto)}{after}</a>'


def b_cabecalho(b):
    sub = f'<p>{esc(b["subtitulo"])}</p>' if b.get("subtitulo") else ""
    return f'<div class="title reveal"><h1>{esc(b.get("titulo"))}</h1>{sub}</div>'


def b_texto(b):
    return f'<div class="md reveal">{md(b.get("texto"))}</div>'


def b_destaque(b):
    return f'<div class="lead reveal">{md(b.get("texto"))}</div>'


def b_titulo(b):
    ident = f' id="{esc(b["ancora"])}"' if b.get("ancora") else ""
    return f'<h2 class="reveal"{ident}>{esc(b.get("titulo"))}</h2>'


def b_fatos(b):
    cells = "".join(f'<div class="fact"><small>{esc(i.get("rotulo"))}</small><b>{mdi(i.get("valor"))}</b></div>' for i in items(b))
    return f'<div class="facts reveal">{cells}</div>'


def b_selos(b):
    return '<div class="badge-row reveal">' + "".join(f'<span class="badge">{icon("shield")} {esc(t)}</span>' for t in items(b)) + "</div>"


def b_caixa(b):
    cls = "box" + {"azul": " box--blue", "alerta": " box--alert"}.get(b.get("estilo"), "")
    titulo = f'<h3>{esc(b["titulo"])}</h3>' if b.get("titulo") else ""
    btn = ""
    if b.get("botao_texto"):
        btn = f'<a class="btn btn--line" {link_attrs(b.get("botao_link"))}>{icon("file")}{esc(b["botao_texto"])}</a>'
    inner = titulo + md(b.get("texto")) + btn
    if b.get("selo"):
        first, _, rest = str(b["selo"]).partition(" ")
        inner = (f'<div class="cert"><div class="cert__seal"><div><b>{esc(first)}</b>{esc(rest)}</div></div>'
                 f'<div>{inner}</div></div>')
    return f'<div class="{cls} reveal">{inner}</div>'


def b_botoes(b):
    btns = "".join(button(i.get("texto"), i.get("link"), i.get("estilo") or "azul", i.get("icone") or "", i.get("mensagem") or "") for i in items(b))
    return f'<div class="btns reveal">{btns}</div>'


def b_galeria(b):
    figs = []
    for i in items(b, "fotos"):
        tag = img(i.get("imagem"), i.get("alt"), "(max-width: 900px) 100vw, 860px")
        if tag:
            figs.append(f"<figure>{tag}</figure>")
    if not figs:
        return ""
    n = len(figs)
    return (f'<div class="gallery reveal" aria-roledescription="carrossel" aria-label="{esc(b.get("titulo") or "Galeria de fotos")}">'
            f'<div class="gallery__track" tabindex="0">{"".join(figs)}</div>'
            f'<button class="gallery__nav gallery__nav--prev" aria-label="Foto anterior">{icon("left")}</button>'
            f'<button class="gallery__nav gallery__nav--next" aria-label="Próxima foto">{icon("right")}</button>'
            f'<span class="gallery__count" aria-live="polite">1/{n}</span></div>')


def b_etiquetas(b):
    return '<ul class="tags reveal">' + "".join(f"<li>{esc(t)}</li>" for t in items(b)) + "</ul>"


def b_barras(b):
    rows = "".join(f'<div class="bar"><span>{esc(i.get("rotulo"))}</span><i style="--v:{int(i.get("valor") or 0)}%"></i><b>{int(i.get("valor") or 0)}%</b></div>' for i in items(b))
    return f'<div class="bars reveal">{rows}</div>'


def b_citacao(b):
    return f'<p class="quote reveal">{mdi(b.get("texto"))}</p>'


def b_missao(b):
    cards = "".join(f'<div class="reveal"><h2>{esc(i.get("titulo"))}</h2>{md(i.get("texto"))}</div>' for i in items(b))
    return f'<div class="mvv mt">{cards}</div>'


def b_ficha(b):
    rows = "".join(f'<div><dt>{esc(i.get("rotulo"))}</dt><dd>{mdi(i.get("valor"))}</dd></div>' for i in items(b))
    return f'<dl class="sheet reveal">{rows}</dl>'


def b_preco(b):
    rows = "".join(f'<div><small>{esc(i.get("rotulo"))}</small><b>{esc(i.get("valor"))}</b></div>' for i in items(b))
    return f'<div class="price reveal">{rows}</div>'


def b_trilha(b):
    hard = " lvl--hard" if b.get("pesada") else ""
    lvl = f'<span class="lvl{hard}">{esc(b["nivel"])}</span>' if b.get("nivel") else ""
    cells = "".join(f'<div class="fact"><small>{esc(i.get("rotulo"))}</small><b>{mdi(i.get("valor"))}</b></div>' for i in items(b, "fatos"))
    return (f'<article class="trail reveal"><div class="trail__head"><h2>{esc(b.get("nome"))}</h2>{lvl}</div>'
            f'<div class="trail__body"><div class="facts">{cells}</div>{md(b.get("detalhes"))}</div></article>')


def b_equipe(b):
    people = "".join(
        f'<figure class="member reveal"><div class="member__img">{img(p.get("foto"), p.get("nome"), "220px")}</div>'
        f'<figcaption>{esc(p.get("nome"))}</figcaption></figure>' for p in items(b, "pessoas"))
    return f'<div class="team">{people}</div>'


def b_cartoes(b):
    cards = "".join(
        f'<a class="card reveal" href="{esc(i.get("link"))}"><div class="card__img">{img(i.get("imagem"), i.get("alt"), "(max-width: 540px) 100vw, 25vw")}</div>'
        f'<div class="card__body"><b>{esc(i.get("titulo"))}</b><span>{esc(i.get("texto"))}</span><span class="card__go">Saiba mais {icon("arrow")}</span></div></a>'
        for i in items(b))
    return f'<div class="cards">{cards}</div>'


def b_formulario(b):
    hint = b.get("dica") or "A mensagem abre pronta no WhatsApp ou no seu e-mail — é só confirmar o envio."
    return f'''<form class="form reveal" id="contato-form" data-whatsapp="{esc(WA)}" data-email="{esc(EMAIL)}">
        <label>Nome *<input name="nome" required autocomplete="name"></label>
        <label>E-mail *<input name="email" type="email" required autocomplete="email"></label>
        <label>Telefone<input name="telefone" type="tel" autocomplete="tel"></label>
        <label>Endereço<input name="endereco" autocomplete="street-address"></label>
        <label class="full">Assunto<input name="assunto"></label>
        <label class="full">Mensagem *<textarea name="mensagem" required></textarea></label>
        <div class="full btns" style="justify-content:flex-start;margin-top:4px">
          <button class="btn btn--wa" type="submit" value="whatsapp">{icon("whatsapp")}Enviar pelo WhatsApp</button>
          <button class="btn btn--line" type="submit" value="email">{icon("mail")}Enviar por e-mail</button>
        </div>
        <p class="form__hint">{esc(hint)}</p>
      </form>'''


BLOCKS = {
    "cabecalho": b_cabecalho, "texto": b_texto, "destaque": b_destaque, "titulo": b_titulo, "fatos": b_fatos,
    "selos": b_selos, "caixa": b_caixa, "botoes": b_botoes, "galeria": b_galeria, "etiquetas": b_etiquetas,
    "barras": b_barras, "citacao": b_citacao, "missao": b_missao, "ficha": b_ficha, "preco": b_preco,
    "trilha": b_trilha, "equipe": b_equipe, "cartoes": b_cartoes, "formulario": b_formulario,
}


def render_blocks(blocks, slug):
    out = []
    for b in blocks:
        kind = (b or {}).get("tipo")
        fn = BLOCKS.get(kind)
        if not fn:
            warn(f"{slug}: bloco desconhecido '{kind}'")
            continue
        out.append(fn(b))
    return "\n".join(out)


def render_page(slug, data):
    blocks = [b for b in (data.get("blocos") or []) if b]
    kinds = {b.get("tipo") for b in blocks}
    lateral = data.get("lateral") or {}
    has_art = bool(lateral.get("imagem"))
    wide = has_art or bool(kinds & {"equipe", "cartoes", "formulario"})

    # títulos do início ficam acima de qualquer divisão em colunas
    top = []
    while blocks and blocks[0].get("tipo") == "cabecalho" and (has_art or "formulario" in kinds):
        top.append(blocks.pop(0))

    body = render_blocks(top, slug)
    if has_art:
        art = (f'<div class="split__art reveal">{img(lateral["imagem"], lateral.get("alt"), "300px")}</div>')
        left = lateral.get("posicao") == "esquerda"
        main = f'<div class="prose-col">{render_blocks(blocks, slug)}</div>'
        body += f'\n<div class="split{" split--left" if left else ""}">{art + main if left else main + art}</div>'
    elif blocks and blocks[0].get("tipo") == "formulario":
        body += (f'\n<div class="contact">{render_blocks(blocks[:1], slug)}'
                 f'<div class="addr">{render_blocks(blocks[1:], slug)}</div></div>')
    else:
        body += "\n" + render_blocks(blocks, slug)

    banner = ""
    if data.get("banner", {}) and data["banner"].get("imagem"):
        tag = img(data["banner"]["imagem"], data["banner"].get("alt"), "100vw", eager=True)
        banner = f'<div class="banner">{tag}</div>\n' if tag else ""

    hero = ""
    h = data.get("hero") or {}
    if h.get("imagem"):
        hero = (f'<section class="hero" aria-label="Rafting no Rio Paraibuna">{img(h["imagem"], h.get("alt"), "100vw", eager=True)}'
                '<video muted loop playsinline preload="none" poster="assets/video/rafting-hero-poster.webp" '
                'data-sm="assets/video/rafting-hero-480.mp4" data-lg="assets/video/rafting-hero-720.mp4" aria-hidden="true"></video></section>\n')

    art_cls = "article" + (" article--wide" if wide else "") + " prose"
    og = None
    for src in (data.get("banner"), data.get("hero")):
        r = resolve((src or {}).get("imagem"))
        if r:
            og = r[0]; break
    return (head(data.get("titulo_aba") or "Cia. de Rafting", data.get("descricao") or "", og)
            + header(slug + ".html") + '<main id="conteudo">\n' + banner + hero
            + f'<section class="page"><div class="{art_cls}">\n{body}\n</div></section>\n</main>\n'
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


build()
