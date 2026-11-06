"""Gera as páginas da rev3 ("rafting gourmet").

Uso: dentro da pasta rev3, rode  python _src/build.py
Só gera as primeiras páginas do site; as demais apontam para a rev2.
"""
from pathlib import Path
from urllib.parse import quote

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
IMG = ROOT / "assets" / "img"

WHATS = "5512997031363"
WHATS_TXT = "(12) 99703-1363"
EMAIL = "contato@ciaderafting.com.br"


def wa(msg="Olá, Cia. de Rafting! Gostaria de fazer uma reserva."):
    return f"https://wa.me/{WHATS}?text={quote(msg)}"


def img(name, alt, cls="", sizes="100vw", eager=False):
    """<img> com versão leve (-sm) para telas menores."""
    w, h = Image.open(IMG / f"{name}.webp").size
    sm = IMG / f"{name}-sm.webp"
    srcset = ""
    if sm.exists():
        sw = Image.open(sm).size[0]
        srcset = f' srcset="assets/img/{name}-sm.webp {sw}w, assets/img/{name}.webp {w}w" sizes="{sizes}"'
    load = 'fetchpriority="high"' if eager else 'loading="lazy"'
    c = f' class="{cls}"' if cls else ""
    return f'<img{c} src="assets/img/{name}.webp"{srcset} alt="{alt}" width="{w}" height="{h}" {load} decoding="async">'


ARROW = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.2" aria-hidden="true"><path d="M4 12h16M14 6l6 6-6 6"/></svg>'
CHECK = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.2" aria-hidden="true"><path d="M4 12.5l5 5L20 6.5"/></svg>'
WA_ICON = '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M12 2a10 10 0 0 0-8.6 15.1L2 22l5-1.3A10 10 0 1 0 12 2Zm0 18.2a8.2 8.2 0 0 1-4.2-1.2l-.3-.2-3 .8.8-2.9-.2-.3A8.2 8.2 0 1 1 12 20.2Zm4.5-6.1c-.2-.1-1.5-.7-1.7-.8-.2-.1-.4-.1-.6.1l-.8 1c-.1.2-.3.2-.5.1a6.7 6.7 0 0 1-3.3-2.9c-.3-.4.3-.4.7-1.4.1-.2 0-.3 0-.4l-.8-1.8c-.2-.5-.4-.4-.6-.4h-.5a1 1 0 0 0-.7.3 3 3 0 0 0-.9 2.2 5.2 5.2 0 0 0 1.1 2.7 11.8 11.8 0 0 0 4.5 4c1.7.7 2.3.8 3.2.6.5-.1 1.5-.6 1.7-1.2.2-.6.2-1.1.2-1.2-.1-.1-.3-.2-.5-.3Z"/></svg>'
ORNAMENT = '<svg class="ornament" viewBox="0 0 64 14" fill="none" stroke="currentColor" stroke-width="1" aria-hidden="true"><path d="M0 7h22M42 7h22"/><path d="M26 7c2-4 4-4 6 0s4 4 6 0"/></svg>'

NAV = [
    ("index.html", "Início"),
    ("sobre-nos.html", "A Casa"),
    ("expedicao-de-rafting-4-horas-brazadao.html", "4 horas"),
    ("expedicao-de-rafting-6-horas-nucleo.html", "6 horas"),
    ("contato.html", "Contato"),
]


def page(file, title, desc, body):
    nav = "\n".join(
        f'<a href="{href}"{" aria-current=\"page\"" if href == file else ""}>{label}</a>' for href, label in NAV
    )
    html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<meta name="robots" content="noindex">
<meta name="theme-color" content="#0d1512">
<link rel="icon" type="image/png" href="assets/img/favicon.png">
<link rel="apple-touch-icon" href="assets/img/apple-touch-icon.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,300;0,400;0,500;1,300;1,400&family=Jost:wght@300;400;500&display=swap" rel="stylesheet">
<link rel="stylesheet" href="assets/css/style.css">
</head>
<body>
<a class="skip" href="#conteudo">Pular para o conteúdo</a>
<header class="top">
  <div class="wrap">
    <a class="brand" href="index.html" aria-label="Cia. de Rafting — início">
      <span class="brand__name">Cia. de <em>Rafting</em></span>
      <span class="brand__tag">Serra do Mar · desde 1996</span>
    </a>
    <button class="menu-toggle" type="button" aria-label="Abrir menu" aria-expanded="false"><span></span><span></span></button>
    <nav class="nav" aria-label="Principal">
{nav}
<a class="btn" href="{wa()}" target="_blank" rel="noopener">Reservar</a>
    </nav>
  </div>
</header>
<main id="conteudo">
{body}
</main>
<footer class="foot">
  <div class="wrap">
    <div class="foot__grid">
      <div>
        <img class="foot__logo" src="assets/img/logo-branco.webp" alt="Cia. de Rafting" width="900" height="394" loading="lazy">
        <p>Rafting, trilhas e educação ao ar livre na Mata Atlântica. Uma das cinco primeiras operadoras de rafting comercial do Brasil.</p>
      </div>
      <div>
        <h4>Experiências</h4>
        <ul>
          <li><a href="expedicao-de-rafting-4-horas-brazadao.html">Expedição 4 horas</a></li>
          <li><a href="expedicao-de-rafting-6-horas-nucleo.html">Expedição 6 horas</a></li>
          <li><a href="../rev2/trilhas.html">Trilhas</a></li>
          <li><a href="../rev2/curso-de-rafting.html">Curso de rafting</a></li>
        </ul>
      </div>
      <div>
        <h4>A Casa</h4>
        <ul>
          <li><a href="sobre-nos.html">Nossa história</a></li>
          <li><a href="../rev2/nossa-equipe.html">Equipe</a></li>
          <li><a href="../rev2/politica-de-seguranca.html">Política de segurança</a></li>
          <li><a href="../rev2/sao-luiz-do-paraitinga.html">São Luiz do Paraitinga</a></li>
        </ul>
      </div>
      <div>
        <h4>Reservas</h4>
        <ul>
          <li><a href="{wa()}" target="_blank" rel="noopener">WhatsApp {WHATS_TXT}</a></li>
          <li><a href="mailto:{EMAIL}">{EMAIL}</a></li>
          <li><a href="https://www.instagram.com/ciaderafting/" target="_blank" rel="noopener">Instagram</a> · <a href="https://www.facebook.com/Ciaderafting" target="_blank" rel="noopener">Facebook</a></li>
          <li>São Luiz do Paraitinga – SP</li>
        </ul>
      </div>
    </div>
    <div class="foot__base">
      <span>© Cia. de Rafting · desde 1996</span>
      <span>ISO 21.101 certificada · CADASTUR 26.028025.10.0001-1</span>
    </div>
  </div>
</footer>
<a class="concierge" href="{wa()}" target="_blank" rel="noopener" aria-label="Falar com a Cia. pelo WhatsApp">{WA_ICON}<span>Concierge</span></a>
<script src="assets/js/main.js" defer></script>
</body>
</html>
"""
    (ROOT / file).write_text(html, encoding="utf-8")
    print("ok", file)


def pagehead(image, alt, crumb, title, sub):
    return f"""<section class="pagehead">
  {img(image, alt, eager=True)}
  <div class="wrap">
    <div class="crumbs"><a href="index.html">Início</a> &nbsp;/&nbsp; {crumb}</div>
    <h1>{title}</h1>
    <p>{sub}</p>
  </div>
</section>"""


def cta(image, title, text, msg=None):
    return f"""<section class="cta">
  {img(image, "")}
  <div class="narrow reveal">
    <span class="eyebrow eyebrow--center">Reservas</span>
    <h2>{title}</h2>
    <p>{text}</p>
    <div class="hero__actions">
      <a class="btn" href="{wa(msg) if msg else wa()}" target="_blank" rel="noopener">Reservar pelo WhatsApp {ARROW}</a>
      <a class="btn btn--ghost" href="contato.html">Falar com a Cia.</a>
    </div>
  </div>
</section>"""


# ---------------------------------------------------------------- Início
def home():
    body = f"""<section class="hero">
  <div class="hero__media">
    <video autoplay muted loop playsinline poster="assets/video/rafting-hero-poster.webp">
      <source src="assets/video/rafting-hero-720.mp4" type="video/mp4" media="(min-width: 700px)">
      <source src="assets/video/rafting-hero-480.mp4" type="video/mp4">
    </video>
  </div>
  <div class="hero__body">
    <div class="wrap hero__foot">
      <div>
        <span class="eyebrow">Rio Paraibuna · Mata Atlântica</span>
        <h1>A Mata Atlântica, servida em <em>corredeiras.</em></h1>
        <p>Expedições de rafting conduzidas com o rigor de quem certificou a própria segurança — e o cuidado de quem recebe convidados em casa.</p>
        <div class="hero__actions">
          <a class="btn" href="#carta">Conhecer as expedições {ARROW}</a>
          <a class="btn btn--ghost" href="{wa()}" target="_blank" rel="noopener">Reservar</a>
        </div>
      </div>
      <span class="hero__scroll">Role</span>
    </div>
  </div>
</section>

<section class="section manifesto">
  <div class="narrow reveal">
    <span class="eyebrow eyebrow--center">A Casa</span>
    {ORNAMENT}
    <p class="lead">Há quase três décadas descemos o Rio Paraibuna com o mesmo princípio: <em>a aventura é o prato principal</em>, mas são os detalhes — a equipe certificada, o equipamento impecável, o lanche à beira de uma praia de água transparente — que fazem a experiência inesquecível.</p>
    <p class="signature">Cia. de Rafting · São Luiz do Paraitinga</p>
  </div>
</section>

<section class="section section--dark" id="carta">
  <div class="wrap">
    <div class="section-head reveal">
      <div>
        <span class="eyebrow">A carta</span>
        <h2>Duas expedições,<br><em>dois tempos de rio.</em></h2>
      </div>
      <p class="muted">Como num menu degustação, cada expedição tem seu ritmo: a de 4 horas é leve e luminosa; a de 6 horas é intensa e profunda, dentro da zona de amortecimento do Parque Estadual da Serra do Mar.</p>
    </div>
    <div class="carte">
      <article class="course reveal">
        <a class="course__img" href="expedicao-de-rafting-4-horas-brazadao.html">{img("rafting-comemoracao", "Grupo comemorando no bote", sizes="(max-width: 860px) 100vw, 50vw")}</a>
        <div class="course__body">
          <div class="course__meta"><span>N.º I · Brazadão</span><span>≈ 4 horas</span></div>
          <h3>Expedição <em>4 horas</em></h3>
          <p class="course__sub">Rio Paraibuna, Natividade da Serra</p>
          <ul class="steps">
            <li><span class="k">Recepção</span><span class="v">Complexo Manacá da Serra, km 59, até 8h</span></li>
            <li><span class="k">Descida</span><span class="v">Corredeiras entre a Floresta Atlântica</span></li>
            <li><span class="k">Pausa</span><span class="v">Lanche na Praia do Funilzão</span></li>
            <li><span class="k">Inclui</span><span class="v">Equipamento completo e seguro viagem</span></li>
          </ul>
          <a class="link" href="expedicao-de-rafting-4-horas-brazadao.html">Ver a expedição {ARROW}</a>
        </div>
      </article>
      <article class="course reveal">
        <a class="course__img" href="expedicao-de-rafting-6-horas-nucleo.html">{img("corredeira-cachoeira", "Bote descendo corredeira forte", sizes="(max-width: 860px) 100vw, 50vw")}</a>
        <div class="course__body">
          <div class="course__meta"><span>N.º II · Núcleo</span><span>≈ 6 horas</span></div>
          <h3>Expedição <em>6 horas</em></h3>
          <p class="course__sub">Núcleo Santa Virgínia · Classes II, III e IV</p>
          <ul class="steps">
            <li><span class="k">Recepção</span><span class="v">Hospedaria do Núcleo Santa Virgínia, até 8h30</span></li>
            <li><span class="k">Descida</span><span class="v">Corredeiras classe II a IV, mata intocada</span></li>
            <li><span class="k">Segurança</span><span class="v">SGS certificado ISO 21.101, caiaque e rádio VHF</span></li>
            <li><span class="k">Inclui</span><span class="v">Vestiários, banho e seguro viagem</span></li>
          </ul>
          <a class="link" href="expedicao-de-rafting-6-horas-nucleo.html">Ver a expedição {ARROW}</a>
        </div>
      </article>
    </div>
  </div>
</section>

<section class="section section--night section--tight">
  <div class="wrap">
    <div class="figures reveal">
      <div class="figure"><b>1996</b><span>Fundação</span></div>
      <div class="figure"><b>ISO</b><span>21.101 certificada</span></div>
      <div class="figure"><b>II–IV</b><span>Classes de corredeira</span></div>
      <div class="figure"><b>180 km</b><span>de São Paulo</span></div>
    </div>
  </div>
</section>

<section class="section">
  <div class="wrap split">
    <div class="split__media reveal">
      {img("rio-paraibuna-mata", "O Rio Paraibuna cercado pela Mata Atlântica", sizes="(max-width: 900px) 100vw, 50vw")}
      {img("bromelia", "Bromélia da Mata Atlântica", cls="inset", sizes="25vw")}
    </div>
    <div class="split__text reveal">
      <span class="eyebrow">O terroir</span>
      <h2>Um rio de águas transparentes, <em>numa floresta Patrimônio da Humanidade.</em></h2>
      <p>O Rio Paraibuna corre pela Mata Atlântica, considerada Patrimônio da Humanidade pela UNESCO. Descer suas corredeiras é conhecer de perto a diversidade de espécies vegetais e animais de uma das florestas mais importantes do mundo.</p>
      <p class="muted">A operação acontece entre São Luiz do Paraitinga — importante centro cultural e arquitetônico — e Natividade da Serra, no Vale do Paraíba.</p>
      <a class="link" href="sobre-nos.html">Nossa história {ARROW}</a>
    </div>
  </div>
</section>

<section class="section section--ivory">
  <div class="wrap split split--rev">
    <div class="split__media reveal">
      {img("equipamentos", "Equipamentos de rafting organizados", sizes="(max-width: 900px) 100vw, 50vw")}
    </div>
    <div class="split__text reveal">
      <span class="eyebrow">O serviço</span>
      <h2>Segurança tratada como <em>alta cozinha:</em> com método.</h2>
      <p>Nada é improvisado. Cada descida segue um Sistema de Gestão da Segurança certificado e é conduzida por uma equipe formada nas normas brasileiras e internacionais.</p>
      <ul class="creds">
        <li>{CHECK}<span>Certificação ABNT NBR ISO 21101 — Sistema de Gestão da Segurança</span></li>
        <li>{CHECK}<span>Condutores habilitados na ABNT NBR 15.370 e certificados pela IRF</span></li>
        <li>{CHECK}<span>Seguro saúde/viagem incluso em todas as expedições</span></li>
      </ul>
    </div>
  </div>
</section>

<section class="section section--tight">
  <div class="wrap">
    <div class="section-head reveal">
      <div>
        <span class="eyebrow">Também na casa</span>
        <h2>Para além <em>do bote.</em></h2>
      </div>
      <p class="muted">Caminhadas guiadas no Parque Estadual da Serra do Mar e um curso completo para quem quer aprender a conduzir no rio.</p>
    </div>
    <div class="more reveal">
      <a class="tile" href="../rev2/trilhas.html">{img("trilha-grupo", "Grupo caminhando na trilha", sizes="(max-width: 760px) 100vw, 50vw")}<div class="tile__body"><span class="eyebrow">Núcleo Santa Virgínia</span><h3>Trilhas</h3></div></a>
      <a class="tile" href="../rev2/curso-de-rafting.html">{img("curso-vira-bote", "Treino de virar o bote no curso", sizes="(max-width: 760px) 100vw, 50vw")}<div class="tile__body"><span class="eyebrow">48 horas/aula</span><h3>Curso de rafting</h3></div></a>
    </div>
  </div>
</section>

{cta("rio-paisagem", "Reserve seu lugar <em>no rio.</em>", "Conte a data e o tamanho do grupo — a Cia. cuida do resto.")}"""
    page("index.html", "Cia. de Rafting · Expedições de rafting na Serra do Mar",
         "Expedições de rafting no Rio Paraibuna, na Mata Atlântica. Desde 1996, com segurança certificada ISO 21.101.", body)


# ---------------------------------------------------------------- Sobre
def sobre():
    body = f"""{pagehead("grupo-rio", "Grupo com vários botes reunidos no rio", "A Casa", "Uma das primeiras casas do <em>rafting brasileiro.</em>", "Fundada em 1996, a Cia. de Rafting implantou as operações comerciais na Bacia do Rio Paraibuna.")}

<section class="section">
  <div class="wrap split">
    <div class="split__text reveal">
      <span class="eyebrow">História</span>
      <h2>Desde 1996, <em>no mesmo rio.</em></h2>
      <p>A Cia. de Rafting é uma das cinco primeiras operadoras de rafting comercial do Brasil, responsável pela implantação das operações na Bacia do Rio Paraibuna, no Vale do Paraíba — entre São Luiz do Paraitinga, importante centro cultural e arquitetônico, e Natividade da Serra, a 180 km de São Paulo.</p>
      <p class="muted">A equipe reúne formações técnicas, acadêmicas e de ensino médio, com certificação na IRF — International Rafting Federation — e nas Normas Brasileiras de Referência da ABNT. Todas as atividades seguem a legislação aplicável e as boas práticas consagradas no turismo de aventura.</p>
    </div>
    <div class="split__media reveal">
      {img("guias-rio", "Guias da Cia. de Rafting no rio", sizes="(max-width: 900px) 100vw, 50vw")}
      {img("tamandua-real", "Tamanduá na Mata Atlântica", cls="inset", sizes="25vw")}
    </div>
  </div>
</section>

<section class="section section--dark">
  <div class="wrap">
    <div class="section-head center reveal" style="grid-template-columns:1fr">
      <div>
        <span class="eyebrow eyebrow--center">Princípios</span>
        <h2>O que nos <em>conduz.</em></h2>
      </div>
    </div>
    <div class="pillars reveal">
      <div class="pillar"><span class="roman">I.</span><h3>Missão</h3><p>Conectar pessoas à natureza através de nossos serviços no mais alto grau de espírito de aventura.</p></div>
      <div class="pillar"><span class="roman">II.</span><h3>Visão</h3><p>As atividades de aventura ao ar livre estimulam mudanças fantásticas nas pessoas e no seu entorno. Por isso, é nosso dever criar os meios que possibilitem o acesso de todos a essas experiências.</p></div>
      <div class="pillar"><span class="roman">III.</span><h3>Valores</h3><p>Honestidade, legalidade, responsabilidade, planejamento e segurança.</p></div>
    </div>
  </div>
</section>

<section class="section">
  <div class="wrap">
    <div class="seal reveal">
      <div class="seal__badge"><div><span>ABNT NBR</span><b>ISO</b><b>21101</b></div></div>
      <div>
        <span class="eyebrow">Certificação</span>
        <h3>Sistema de Gestão da Segurança certificado</h3>
        <p class="muted">Certificado ABNT NBR ISO 21101:2014 para a atividade de rafting no Rio Paraibuna, na zona de amortecimento do Parque Estadual da Serra do Mar — Núcleo Santa Virgínia. Certificação voluntária, válida de 08/10/2025 a 08/10/2026.</p>
        <div class="hero__actions" style="margin-top:20px">
          <a class="btn btn--dark" href="../rev2/politica-de-seguranca.html">Política de segurança</a>
          <a class="link" href="../rev2/nossa-equipe.html">Conhecer a equipe {ARROW}</a>
        </div>
      </div>
    </div>
  </div>
</section>

{cta("rafting-grupo-remos", "Venha remar <em>conosco.</em>", "Duas expedições, um mesmo cuidado. Escolha o seu tempo de rio.")}"""
    page("sobre-nos.html", "A Casa · Sobre a Cia. de Rafting",
         "Fundada em 1996, a Cia. de Rafting é uma das cinco primeiras operadoras de rafting comercial do Brasil.", body)


# ---------------------------------------------------------------- Expedições
def sheet(rows, msg):
    dl = "".join(f"<div><dt>{k}</dt><dd>{v}</dd></div>" for k, v in rows)
    return f"""<aside class="sheet reveal">
      <span class="eyebrow">Ficha técnica</span>
      <h2>Em resumo</h2>
      <dl>{dl}</dl>
      <a class="btn" href="{wa(msg)}" target="_blank" rel="noopener">Reservar {ARROW}</a>
      <small>Atendimento pelo WhatsApp {WHATS_TXT}</small>
    </aside>"""


def ticks(items):
    return "".join(f"<li>{i}</li>" for i in items)


def exp4():
    msg = "Olá, Cia. de Rafting! Gostaria de reservar a Expedição de Rafting 4 horas (Brazadão)."
    fotos = [("rafting-onda", "Bote furando uma onda"), ("rafting-grupo-remos", "Grupo remando juntos"),
             ("peixes-rio", "Águas transparentes do Rio Paraibuna"), ("rafting-bote", "Bote descendo o rio"),
             ("grupo-pedras", "Grupo nas pedras do rio"), ("briefing-grupo", "Briefing de segurança com o grupo"),
             ("remos-amarelos", "Remos amarelos prontos para a descida"), ("rafting-remos", "Remos levantados no bote"),
             ("hero-corredeira", "Bote na corredeira")]
    gal = "".join(f'<a href="assets/img/{n}.webp">{img(n, a, sizes="(max-width: 700px) 50vw, 40vw")}</a>' for n, a in fotos)
    body = f"""{pagehead("rafting-comemoracao", "Grupo comemorando no bote", "Expedição 4 horas", "Brazadão, <em>4 horas de rio.</em>", "Rio Paraibuna, Natividade da Serra — corredeiras, Floresta Atlântica e uma pausa na Praia do Funilzão.")}

<section class="section">
  <div class="wrap dossier">
    {sheet([("Percurso", "Rio Paraibuna, Natividade da Serra"), ("Duração", "Aproximadamente 4 horas de rio"), ("Chegada", "Até 8h00, no km 59 da Rod. Oswaldo Cruz"), ("Condução", "Instrutores ABNT NBR 15.370"), ("Seguro", "Saúde/viagem incluso")], msg)}
    <div class="prose reveal">
      <span class="eyebrow">O roteiro</span>
      <h2>Uma manhã inteira <em>no ritmo do rio.</em></h2>
      <p class="lead">Além da aventura, a Floresta Atlântica: a descida combina corredeiras com trechos calmos para apreciar a paisagem.</p>
      <ol class="timeline">
        <li><div><b>Recepção no Manacá da Serra</b>Ponto de encontro no km 59 da Rodovia Oswaldo Cruz, com estacionamento, sanitários e refeições.</div></li>
        <li><div><b>Traslado à beira do rio</b>Transporte terceirizado adequado até o início da atividade, às margens do Rio Paraibuna.</div></li>
        <li><div><b>A descida</b>Corredeiras e remanso entre as belezas da Floresta Atlântica.</div></li>
        <li><div><b>Pausa na Praia do Funilzão</b>Lanche servido à beira das águas transparentes do Paraibuna.</div></li>
        <li><div><b>Retorno</b>Embarque de volta ao ponto de encontro para a troca de roupa.</div></li>
      </ol>
      <h3>Acesso</h3>
      <p class="muted">São Luiz do Paraitinga fica a 200 km de São Paulo. Siga pela Rodovia Ayrton Senna/Carvalho Pinto ou pela Dutra, sentido Rio de Janeiro, até Taubaté; depois pela Rodovia Oswaldo Cruz, sentido Litoral Norte (Ubatuba – saída 111), até o km 59, no complexo Manacá da Serra.</p>
    </div>
  </div>
</section>

<section class="section section--dark section--tight">
  <div class="wrap pair">
    <div class="reveal">
      <span class="eyebrow">Incluso</span>
      <h3>O que oferecemos</h3>
      <ul class="ticks">{ticks(["Bote inflável para 5 passageiros", "Capacete, colete salva-vidas e remo", "Jaqueta de frio", "Instrutores habilitados na ABNT NBR 15.370", "Seguro saúde/viagem", "Lanche na Praia do Funilzão"])}</ul>
    </div>
    <div class="reveal">
      <span class="eyebrow">Na bagagem</span>
      <h3>O que levar</h3>
      <ul class="ticks">{ticks(["Par extra de tênis", "Camiseta, short e toalha", "Repelente e protetor solar", "Máquina fotográfica", "Protetor para óculos, para evitar quedas"])}</ul>
    </div>
  </div>
</section>

<section class="section">
  <div class="wrap">
    <div class="section-head reveal">
      <div><span class="eyebrow">Galeria</span><h2>Do rio, <em>em imagens.</em></h2></div>
      <p class="muted">Toque numa foto para ampliar.</p>
    </div>
    <div class="gallery reveal">{gal}</div>
  </div>
</section>

{cta("rio-paisagem", "Sua manhã <em>no Paraibuna.</em>", "Também servimos a versão de 6 horas, mais intensa, no Núcleo Santa Virgínia.", msg)}"""
    page("expedicao-de-rafting-4-horas-brazadao.html", "Expedição de Rafting 4 horas · Brazadão · Cia. de Rafting",
         "Rafting de aproximadamente 4 horas no Rio Paraibuna, em Natividade da Serra, com parada na Praia do Funilzão.", body)


def exp6():
    msg = "Olá, Cia. de Rafting! Gostaria de reservar a Expedição de Rafting 6 horas (Núcleo)."
    body = f"""{pagehead("corredeira-cachoeira", "Bote descendo corredeira forte no Rio Paraibuna", "Expedição 6 horas", "Núcleo Santa Virgínia, <em>6 horas de mata intocada.</em>", "Classes II, III e IV na zona de amortecimento do Parque Estadual da Serra do Mar.")}

<section class="section">
  <div class="wrap dossier">
    {sheet([("Dificuldade", "Classes II, III e IV"), ("Percurso", "Rio Paraibuna — zona de amortecimento do PESM"), ("Duração", "Aproximadamente 6 horas"), ("Apresentação", "Até 8h30, na hospedaria do Núcleo Santa Virgínia"), ("Segurança", "SGS certificado ISO 21.101")], msg)}
    <div class="prose reveal">
      <span class="eyebrow">A expedição</span>
      <h2>Um dos melhores raftings <em>do país.</em></h2>
      <p class="lead">Descer o Rio Paraibuna conhecendo de perto a riqueza natural da Mata Atlântica, enfrentando suas corredeiras — numa das florestas mais importantes do mundo, Patrimônio da Humanidade pela UNESCO.</p>
      <p>Nesta expedição de 6 horas, o passageiro tem contato com um ambiente natural intocado. Toda a operação na Zona de Amortecimento do Núcleo Santa Virgínia passou por um processo de regulamentação técnica e de segurança, e o produto possui um Sistema de Gestão da Segurança (SGS) certificado conforme a norma ISO 21.101.</p>
      <ol class="timeline">
        <li><div><b>Recepção no Núcleo Santa Virgínia</b>Até as 8h30, na hospedaria, onde os guias passam as instruções.</div></li>
        <li><div><b>A descida</b>Corredeiras de classe II a IV, com caiaque de segurança e veículo de apoio com rádio VHF.</div></li>
        <li><div><b>Banho e troca de roupa</b>Banheiros e vestiários à disposição ao final do percurso.</div></li>
      </ol>
      <h3>Como chegar</h3>
      <p class="muted">O Núcleo Santa Virgínia fica a 33 km do centro de São Luiz do Paraitinga, no km 78 da Rodovia Oswaldo Cruz — de onde parte um acesso de 3 km de estrada de terra até a hospedaria. De São Paulo, siga pela Ayrton Senna/Carvalho Pinto ou pela Dutra até Taubaté, e depois pela Oswaldo Cruz, sentido Ubatuba, até a placa do Parque Estadual da Serra do Mar, à esquerda.</p>
    </div>
  </div>
</section>

<section class="section section--dark section--tight">
  <div class="wrap pair">
    <div class="reveal">
      <span class="eyebrow">Incluso</span>
      <h3>O que oferecemos</h3>
      <ul class="ticks">{ticks(["Botes para 5 a 6 passageiros", "Capacete, colete salva-vidas, remo e jaqueta de frio", "Instrutores habilitados na ABNT NBR 15.370", "Seguro saúde/viagem", "Veículo de apoio com rádio VHF e caiaque de segurança", "Banheiros e vestiários para banho"])}</ul>
    </div>
    <div class="reveal">
      <span class="eyebrow">Na bagagem</span>
      <h3>O que levar</h3>
      <ul class="ticks">{ticks(["Par extra de tênis, short e toalha", "Neoprene", "Repelente e protetor solar", "Máquina fotográfica", "Protetor para óculos", "Agasalho de lã ou nylon — a serração dentro do parque derruba a temperatura"])}</ul>
    </div>
  </div>
</section>

<section class="section section--tight">
  <div class="narrow">
    <div class="note reveal">
      <span class="eyebrow">Legislação</span>
      <h3>Informações ao participante</h3>
      <p class="muted">Em cumprimento à lei, disponibilizamos as informações mínimas e preliminares ao cliente, conforme a Norma ABNT NBR ISO 21103 — Comunicação aos Participantes.</p>
      <a class="link" href="mailto:{EMAIL}?subject={quote('Informações mínimas e preliminares ao cliente')}">Solicitar por e-mail {ARROW}</a>
    </div>
    <div class="note note--gold reveal">
      <span class="eyebrow">Programa social</span>
      <h3>Rafting gratuito</h3>
      <p class="muted">Em cumprimento ao TAU/FF/PESM – Santa Virgínia nº 18/2022, da Fundação Florestal, oferecemos vagas gratuitas nesta expedição — prioritariamente a moradores do entorno da unidade de conservação, escolas públicas, ONGs de cunho social, comunidades tradicionais, pessoas inscritas em programas sociais e outros em situação de vulnerabilidade socioeconômica.</p>
      <a class="link" href="contato.html">Entrar em contato {ARROW}</a>
    </div>
  </div>
</section>

{cta("hero-corredeira", "Seis horas <em>de Serra do Mar.</em>", "Prefere algo mais leve? A expedição de 4 horas no Brazadão é a entrada perfeita.", msg)}"""
    page("expedicao-de-rafting-6-horas-nucleo.html", "Expedição de Rafting 6 horas · Núcleo Santa Virgínia · Cia. de Rafting",
         "Rafting de 6 horas no Rio Paraibuna, classes II, III e IV, na zona de amortecimento do Parque Estadual da Serra do Mar.", body)


# ---------------------------------------------------------------- Contato
def contato():
    body = f"""{pagehead("rafting-remos", "Remos levantados no bote", "Contato", "Ao seu <em>dispor.</em>", "Para reservas, grupos, empresas e dúvidas — respondemos pelo WhatsApp e por e-mail.")}

<section class="section">
  <div class="wrap contact">
    <div class="reveal">
      <span class="eyebrow">Mensagem</span>
      <h2 style="font-size:clamp(2rem,3.4vw,2.9rem);font-weight:300;margin:18px 0 34px">Conte-nos sobre <em style="color:var(--gold)">o seu grupo.</em></h2>
      <form class="form" id="contato-form" data-whatsapp="{WHATS}" data-email="{EMAIL}">
        <div class="row">
          <div class="field"><label for="f-nome">Nome</label><input id="f-nome" name="nome" required autocomplete="name"></div>
          <div class="field"><label for="f-tel">Telefone</label><input id="f-tel" name="telefone" type="tel" autocomplete="tel"></div>
        </div>
        <div class="row">
          <div class="field"><label for="f-int">Interesse</label>
            <select id="f-int" name="interesse">
              <option>Expedição 4 horas</option><option>Expedição 6 horas</option><option>Trilhas</option><option>Curso de rafting</option><option>Grupos e empresas</option><option>Outros assuntos</option>
            </select></div>
          <div class="row" style="gap:20px">
            <div class="field"><label for="f-data">Data</label><input id="f-data" name="data" type="date"></div>
            <div class="field"><label for="f-pes">Pessoas</label><input id="f-pes" name="pessoas" type="number" min="1" inputmode="numeric"></div>
          </div>
        </div>
        <div class="field"><label for="f-msg">Mensagem</label><textarea id="f-msg" name="mensagem" required></textarea></div>
        <div class="form__actions">
          <button class="btn" type="submit" value="whatsapp">Enviar pelo WhatsApp {ARROW}</button>
          <button class="btn btn--dark" type="submit" value="email">Por e-mail</button>
        </div>
        <p class="form__hint">A mensagem abre pronta no WhatsApp ou no seu e-mail — é só confirmar o envio.</p>
      </form>
    </div>
    <div class="reveal">
      <div class="addr">
        <span class="eyebrow">Atendimento</span>
        <h3>Reservas</h3>
        <p><a href="{wa()}" target="_blank" rel="noopener">+55 {WHATS_TXT}</a><br><a href="mailto:{EMAIL}">{EMAIL}</a></p>
      </div>
      <div class="addr">
        <span class="eyebrow">Base operacional</span>
        <h3>Sítio Água</h3>
        <p class="muted">Rodovia Dr. Oswaldo Cruz, km 66,5<br>São Luiz do Paraitinga – SP · CEP 12.140-000</p>
      </div>
      <div class="addr">
        <span class="eyebrow">Escritório</span>
        <h3>Administrativo</h3>
        <p class="muted">Rua Cel. Domingues de Castro, 128, sala 02<br>São Luiz do Paraitinga – SP · CEP 12.140-000</p>
      </div>
      <div class="addr">
        <span class="eyebrow">Redes</span>
        <p style="margin-top:12px"><a href="https://www.instagram.com/ciaderafting/" target="_blank" rel="noopener">@ciaderafting</a> &nbsp;·&nbsp; <a href="https://www.facebook.com/Ciaderafting" target="_blank" rel="noopener">facebook.com/Ciaderafting</a></p>
      </div>
    </div>
  </div>
</section>"""
    page("contato.html", "Contato · Cia. de Rafting",
         "Fale com a Cia. de Rafting: WhatsApp (12) 99703-1363 e contato@ciaderafting.com.br. São Luiz do Paraitinga – SP.", body)


if __name__ == "__main__":
    home()
    sobre()
    exp4()
    exp6()
    contato()
