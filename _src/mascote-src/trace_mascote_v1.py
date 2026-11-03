"""Vetoriza o mascote (tamanduá no bote) em camadas animáveis, com contornos suavizados."""
import os, sys, numpy as np, potrace
from PIL import Image, ImageFilter
from collections import deque

HERE = os.path.dirname(os.path.abspath(__file__))
im = Image.open(os.path.join(HERE, "mascote-bote-orig.png")).convert("RGBA")
W, H = im.size
a = np.asarray(im).astype(float)
alpha = a[..., 3] > 110

PAL = {  # cores medidas no desenho original
    "red": (250, 30, 5), "cream": (250, 235, 192), "black": (14, 11, 14), "blue": (45, 140, 230),
    "yellow": (255, 249, 12), "grey": (175, 158, 168), "white": (244, 244, 250),
}
names = list(PAL)
pal = np.array([PAL[n] for n in names], float)
dist = ((a[..., None, :3] - pal[None, None]) ** 2).sum(-1)
lab = np.where(alpha, dist.argmin(-1), -1)
M = {n: lab == i for i, n in enumerate(names)}

def components(mask):
    out = np.zeros(mask.shape, int); n = 0
    for y, x in zip(*np.nonzero(mask)):
        if out[y, x]: continue
        n += 1; q = deque([(y, x)]); out[y, x] = n
        while q:
            cy, cx = q.popleft()
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    ny, nx = cy + dy, cx + dx
                    if 0 <= ny < H and 0 <= nx < W and mask[ny, nx] and not out[ny, nx]:
                        out[ny, nx] = n; q.append((ny, nx))
    return out, n

# --- remo: partes amarelas/cinzas ao longo da linha do cabo ---
P0, P1 = np.array([217.0, 128.0]), np.array([140.0, 252.0])
d = (P1 - P0) / np.linalg.norm(P1 - P0)
comp, n = components(M["yellow"] | M["grey"])
paddle = np.zeros_like(alpha)
for k in range(1, n + 1):
    ys, xs = np.nonzero(comp == k)
    c = np.array([xs.mean(), ys.mean()]); v = c - P0
    if abs(v[0] * d[1] - v[1] * d[0]) < 18 and -10 < v @ d < np.linalg.norm(P1 - P0) + 15:
        paddle |= comp == k

def grow(m, r):
    return np.asarray(Image.fromarray((m * 255).astype("uint8")).filter(ImageFilter.MaxFilter(2 * r + 1))) > 127
def shrink(m, r):
    return np.asarray(Image.fromarray((m * 255).astype("uint8")).filter(ImageFilter.MinFilter(2 * r + 1))) > 127

paddle_line = M["black"] & grow(paddle, 1) & ~grow(M["cream"], 0)  # contorno do remo
paddle_all = paddle | paddle_line

# --- bote: silhueta vermelha fechada (preenche onde o remo passava) ---
boat = shrink(grow(M["red"], 5), 5) & (alpha | grow(M["red"], 2))
# --- base preta: dá o traço de contorno e esconde frestas entre cores ---
base = alpha & ~grow(paddle_all & ~boat, 1)

UP = 4      # amplia antes de vetorizar
BLUR = 3.2  # suavização dos contornos
S = 2 / UP  # coordenadas finais em 2x (viewBox ~638x664)

def smooth(mask, g4=0, blur=None):
    m = Image.fromarray((mask * 255).astype("uint8")).resize((W * UP, H * UP), Image.LANCZOS)
    m = m.filter(ImageFilter.GaussianBlur(blur or BLUR)).point(lambda v: 255 if v > 127 else 0)
    if g4 > 0:
        m = m.filter(ImageFilter.MaxFilter(2 * g4 + 1))
    elif g4 < 0:
        m = m.filter(ImageFilter.MinFilter(2 * -g4 + 1))
    return np.asarray(m) > 127

def pt(p):
    x, y = (p.x, p.y) if hasattr(p, "x") else p
    return f"{x*S:.1f} {y*S:.1f}"

def path_d(mask, turd=60, g4=0, blur=None):
    bm = potrace.Bitmap(~smooth(mask, g4, blur))
    out = []
    for c in bm.trace(turdsize=turd, turnpolicy=potrace.POTRACE_TURNPOLICY_MINORITY, alphamax=1.3, opticurve=True, opttolerance=0.5):
        seg = ["M" + pt(c.start_point)]
        for s in c.segments:
            seg.append(("L" + pt(s.c) + "L" + pt(s.end_point)) if s.is_corner else ("C" + pt(s.c1) + " " + pt(s.c2) + " " + pt(s.end_point)))
        out.append("".join(seg) + "Z")
    return "".join(out)

def hexc(n): return "#%02x%02x%02x" % PAL[n]
def p(mask, color, cls="", turd=60, g4=0, blur=None):
    d_ = path_d(mask, turd, g4, blur)
    return f'<path{f" class={chr(34)}{cls}{chr(34)}" if cls else ""} fill="{color}" fill-rule="evenodd" d="{d_}"/>' if d_ else ""

rest = ~paddle_all
# Estilo logomarca: contorno externo grosso e uniforme, linhas internas
# de espessura constante (as cores encolhem igual e o preto aparece entre elas).
OUT, SEAM, FB = 7, -2, 5.0   # contorno externo, meia-linha interna, suavização das cores
INK = "#1d1a1c"
yy, xx = np.mgrid[0:H, 0:W]
dline = np.abs((xx - P0[0]) * d[1] - (yy - P0[1]) * d[0])
shaft = (M["grey"] | M["black"]) & (dline < 2.2) & ~grow(M["cream"], 0) & ~boat_free if False else None
shaft = paddle & M["grey"] & (dline < 4)
body_under = p(base, INK, g4=OUT, blur=6) + p(boat, hexc("red"), g4=SEAM, blur=FB)
body_over = "".join([
    p(M["cream"] & rest, hexc("cream"), g4=SEAM, blur=FB, turd=40),
    p(M["blue"] & rest, hexc("blue"), g4=SEAM, blur=FB, turd=40),
    p(M["yellow"] & rest & ~paddle, hexc("yellow"), g4=SEAM, blur=FB, turd=40),
    p(M["white"] & rest & (yy < 112), hexc("white"), g4=0, blur=2.5, turd=12),
])
blade = paddle & M["yellow"]
x0, y0 = P0 * 2; x1, y1 = (P0 + (P1 - P0) * 0.86) * 2
line = lambda w, c: f'<line x1="{x0:.1f}" y1="{y0:.1f}" x2="{x1:.1f}" y2="{y1:.1f}" stroke="{c}" stroke-width="{w}" stroke-linecap="round"/>'
paddle_layers = "".join([
    line(17, INK),
    p(grow(blade, 1), INK, turd=10, g4=OUT - 2, blur=4),
    line(8, hexc("grey")),
    p(blade, hexc("yellow"), turd=10, g4=SEAM, blur=4),
])
body_layers = body_under + body_over
top_layers = ""
open(os.path.join(HERE, "partes.txt"), "w").write(f"pivot do remo (viewBox): {((P0 + (P1 - P0) * 0.2) * 2).round(1).tolist()}\n")
svg_parts = {"body": body_layers, "paddle": paddle_layers, "top": top_layers}
import json
json.dump(svg_parts, open(os.path.join(HERE, "mascote-partes.json"), "w", encoding="utf-8"))
print({k: len(v) for k, v in svg_parts.items()}, "W,H", W, H)

PIV = P0 * 2 + np.array([-2.0, 6.0])
WAVE = "M0 0 " + " ".join(f"q 40 -14 80 0 t 80 0" for _ in range(9)) + " V60 H0Z"
svg = f"""<svg class="masc-svg" viewBox="0 120 640 440" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Mascote Tamanduá-de-colete remando no bote">
<g class="masc-wave masc-wave--back"><path fill="#9fd6e2" transform="translate(-20 468)" d="{WAVE}"/></g>
<g class="masc-rig">
<g class="masc-body">{body_under}</g>
<g class="masc-paddle" style="transform-origin:{PIV[0]:.1f}px {PIV[1]:.1f}px">{paddle_layers}</g>
<g class="masc-body-front">{body_over}</g>
</g>
<g class="masc-splash" fill="#ffffff" stroke="#2b7fa3" stroke-width="3">
<circle class="masc-drop" style="--d:0" cx="262" cy="500" r="7"/><circle class="masc-drop" style="--d:1" cx="240" cy="494" r="5"/><circle class="masc-drop" style="--d:2" cx="284" cy="492" r="4.5"/>
</g>
<g class="masc-wave masc-wave--front"><path fill="#5fb6cc" fill-opacity=".92" transform="translate(-60 492)" d="{WAVE}"/><path fill="none" stroke="#ffffff" stroke-width="4" stroke-linecap="round" stroke-opacity=".8" transform="translate(-60 492)" d="M0 0 {" ".join("q 40 -14 80 0 t 80 0" for _ in range(9))}"/></g>
</svg>"""
open(os.path.join(HERE, "mascote-remando.svg"), "w", encoding="utf-8").write(svg)
STYLE = open(os.path.join(HERE, "mascote-anim.css"), encoding="utf-8").read()
open(os.path.join(HERE, "mascote-remando-avulso.svg"), "w", encoding="utf-8").write(svg.replace(">", "><style>" + STYLE + "</style>", 1))
static = f"""<svg viewBox="0 120 640 420" xmlns="http://www.w3.org/2000/svg"><g>{body_under}</g><g>{paddle_layers}</g><g>{body_over}</g></svg>"""
open(os.path.join(HERE, "mascote-bote.svg"), "w", encoding="utf-8").write(static)
print("svg", len(svg), "pivo", PIV.round(1).tolist())
