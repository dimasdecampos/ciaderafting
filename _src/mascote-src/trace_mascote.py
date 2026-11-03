"""Vetoriza o mascote novo (tamanduá no bote, mascote-novo-orig.png) em camadas animáveis.
Fundo do arquivo = branco; traço do desenho ~ (21,22,26)."""
import os, numpy as np, potrace
from PIL import Image, ImageFilter
from collections import deque

HERE = os.path.dirname(os.path.abspath(__file__))
a = np.asarray(Image.open(os.path.join(HERE, "mascote-novo-orig.png")).convert("RGB")).astype(float)
H, W = a.shape[:2]
ssum = a.sum(-1)


def to_img(m):
    return Image.fromarray((m * 255).astype("uint8"))


def grow(m, r):
    return np.asarray(to_img(m).filter(ImageFilter.MaxFilter(2 * r + 1))) > 127 if r else m


def shrink(m, r):
    return np.asarray(to_img(m).filter(ImageFilter.MinFilter(2 * r + 1))) > 127 if r else m


def components(mask):
    out = np.zeros(mask.shape, int)
    n = 0
    ys, xs = np.nonzero(mask)
    for y0, x0 in zip(ys, xs):
        if out[y0, x0]:
            continue
        n += 1
        q = deque([(y0, x0)])
        out[y0, x0] = n
        while q:
            y, x = q.popleft()
            for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                ny, nx = y + dy, x + dx
                if 0 <= ny < H and 0 <= nx < W and mask[ny, nx] and not out[ny, nx]:
                    out[ny, nx] = n
                    q.append((ny, nx))
    return out, n


# --- fundo: branco neutro ligado às bordas (o creme do corpo é amarelado) ---
spread = a.max(-1) - a.min(-1)
cand = (ssum > 738) & (spread < 14)
lab_bg, _ = components(cand)
border_ids = set(np.unique(np.concatenate([lab_bg[0], lab_bg[-1], lab_bg[:, 0], lab_bg[:, -1]]))) - {0}
bg = np.isin(lab_bg, list(border_ids))
# vãos brancos fechados grandes (ex.: entre o braço e o corpo) também são fundo
inner, ni = components(cand & ~bg)
sizes = np.bincount(inner.ravel())
cy = np.bincount(inner.ravel(), weights=np.mgrid[0:H, 0:W][0].ravel()) / np.maximum(sizes, 1)
hole_ids = [k for k in range(1, ni + 1) if sizes[k] > 6000 or (sizes[k] > 800 and 400 < cy[k] < 0.72 * H)]
holes = np.isin(inner, hole_ids)
print("vaos tratados como fundo:", len(hole_ids))
bg = bg | holes
sil = shrink(grow(~bg, 2), 2)

PAL = {
    "ink": (21, 22, 26), "red": (254, 18, 2), "redD": (205, 12, 10), "redL": (245, 88, 82),
    "cream": (254, 241, 207), "creamD": (238, 208, 172), "yellow": (253, 230, 8), "yellowD": (240, 172, 20),
    "blue": (44, 153, 251), "blueL": (110, 190, 245), "cyan": (180, 238, 242), "white": (252, 252, 252),
    "grey": (170, 176, 186), "greyD": (95, 98, 106), "splashD": (22, 104, 178),
}
names = list(PAL)
pal = np.array([PAL[n] for n in names], float)
lab = np.zeros((H, W), int)
for y in range(0, H, 128):  # em blocos para economizar memória
    blk = a[y:y + 128]
    lab[y:y + 128] = ((blk[..., None, :] - pal[None, None]) ** 2).sum(-1).argmin(-1)
lab = np.where(sil, lab, -1)
M = {n: lab == i for i, n in enumerate(names)}
# pixels claros colados no fundo são só serrilhado da borda: viram traço
edge = grow(bg, 3)
for c in ("white", "cyan", "blueL", "blue", "creamD"):
    M[c] &= ~edge
yy, xx = np.mgrid[0:H, 0:W]

# --- remo: do pegador (mão de cima) até a pá ---
yel = M["yellow"] | M["yellowD"]
comp, n = components(yel)
info = []
for k in range(1, n + 1):
    ys, xs = np.nonzero(comp == k)
    if len(xs) > 20:
        info.append((k, len(xs), xs.mean(), ys.mean()))
blade_k = max((t for t in info if t[3] > H * 0.75), key=lambda t: t[1])
grip_k = max((t for t in info if t[3] < H * 0.45 and t[2] > W * 0.6), key=lambda t: t[1])
G = np.array([grip_k[2], grip_k[3]])
B = np.array([blade_k[2], blade_k[3]])
dvec = (B - G) / np.linalg.norm(B - G)
L = np.linalg.norm(B - G)
dline = np.abs((xx - G[0]) * dvec[1] - (yy - G[1]) * dvec[0])
along = (xx - G[0]) * dvec[0] + (yy - G[1]) * dvec[1]
corridor = (dline < 48) & (along > -40) & (along < L + 90)

paddle_col = (yel | M["grey"] | M["greyD"]) & corridor
pc, pn = components(paddle_col)
paddle = np.zeros_like(sil)
for k in range(1, pn + 1):
    m = pc == k
    if m.sum() > 30:
        paddle |= m
paddle = shrink(grow(paddle, 2), 2)
hands = (M["cream"] | M["creamD"]) & (dline < 90) & (along > -80) & (along < L * 0.55)
paddle_ink = M["ink"] & grow(paddle, 5) & ~grow(hands, 2)
paddle_all = paddle | paddle_ink

# --- respingos (azuis/brancos na parte de baixo) ---
redall = M["red"] | M["redD"] | M["redL"]
water = (M["blue"] | M["blueL"] | M["cyan"] | M["white"]) & (yy > H * 0.55)
# respingos de verdade: longe das mãos/corpo e com tamanho mínimo
water &= ~grow(M["cream"] | M["creamD"], 8)
wc, wn = components(water)
wsz = np.bincount(wc.ravel())
water = np.isin(wc, [k for k in range(1, wn + 1) if wsz[k] > 150])
splash = water

# --- bote: silhueta vermelha fechada por baixo do remo ---
boat = shrink(grow(redall, 16), 16) & sil & ~(M["ink"] & ~grow(paddle_all, 4))
base = sil & ~grow(paddle_all & ~boat, 2) & ~shrink(water, 2)

S = 0.5
BLUR = 1.7


def pt(p):
    x, y = (p.x, p.y) if hasattr(p, "x") else p
    return f"{x * S:.1f} {y * S:.1f}"


def path_d(mask, turd=40, blur=BLUR, g=0):
    m = to_img(mask).filter(ImageFilter.GaussianBlur(blur)).point(lambda v: 255 if v > 127 else 0)
    if g > 0:
        m = m.filter(ImageFilter.MaxFilter(2 * g + 1))
    bm = potrace.Bitmap(~(np.asarray(m) > 127))
    out = []
    for c in bm.trace(turdsize=turd, turnpolicy=potrace.POTRACE_TURNPOLICY_MINORITY, alphamax=1.2, opticurve=True, opttolerance=0.4):
        seg = ["M" + pt(c.start_point)]
        for sg in c.segments:
            if sg.is_corner:
                seg.append("L" + pt(sg.c) + "L" + pt(sg.end_point))
            else:
                seg.append("C" + pt(sg.c1) + " " + pt(sg.c2) + " " + pt(sg.end_point))
        out.append("".join(seg) + "Z")
    return "".join(out)


def hexc(nm):
    return "#%02x%02x%02x" % PAL[nm]


def p(mask, nm, turd=40, g=2, blur=BLUR):
    d_ = path_d(mask, turd, blur, g)
    return f'<path fill="{hexc(nm)}" fill-rule="evenodd" d="{d_}"/>' if d_ else ""


rest = ~paddle_all & ~splash
COLORS = ["red", "redD", "redL", "cream", "creamD", "yellow", "yellowD", "blue", "blueL", "cyan", "white", "grey", "greyD"]
body_under = p(base, "ink", g=0, blur=2.2) + p(boat, "red", g=0)
body_over = "".join(p(M[c] & rest, c, turd=25 if c in ("white", "cyan") else 40) for c in COLORS)
hand_ink = M["ink"] & grow(hands, 4) & corridor & ~paddle_all & ~grow(paddle, 7)
body_over += p(hand_ink, "ink", turd=15, g=0, blur=1.2)
paddle_layers = p(paddle_ink | grow(paddle, 2), "ink", turd=15, g=0, blur=1.5) + "".join(
    p(M[c] & paddle, c, turd=15) for c in ["grey", "greyD", "yellow", "yellowD"])

splash_l = splash & (xx < W * 0.3)
splash_r = splash & (xx > W * 0.72)
splash_b = splash & ~splash_l & ~splash_r


def splash_layers(m):
    col = m & ~M["ink"]
    return p(col, "splashD", turd=8, g=3, blur=1.4) + "".join(p(M[c] & m, c, turd=8) for c in ["blue", "blueL", "cyan", "white"])


PIV = G * S
VB_W, VB_H = W * S, H * S
WAVE = "M0 0 " + " ".join("q 40 -12 80 0 t 80 0" for _ in range(10)) + " V60 H0Z"
svg = f"""<svg class="masc-svg" viewBox="-10 -10 {VB_W + 20:.0f} {VB_H + 40:.0f}" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Mascote Tamanduá-de-colete remando no bote">
<g class="masc-wave masc-wave--back"><path fill="#9fd6e2" fill-opacity=".9" transform="translate(-40 {VB_H * 0.86:.0f})" d="{WAVE}"/></g>
<g class="masc-rig">
<g class="masc-splash masc-splash--l">{splash_layers(splash_l)}</g>
<g class="masc-splash masc-splash--r">{splash_layers(splash_r)}</g>
<g class="masc-body">{body_under}</g>
<g class="masc-paddle" style="transform-origin:{PIV[0]:.1f}px {PIV[1]:.1f}px">{paddle_layers}</g>
<g class="masc-body-front">{body_over}</g>
<g class="masc-splash masc-splash--b">{splash_layers(splash_b)}</g>
</g>
</svg>"""
open(os.path.join(HERE, "mascote-remando.svg"), "w", encoding="utf-8").write(svg)

inner = svg.split('<g class="masc-rig">', 1)[1].rsplit("</g>", 1)[0]
open(os.path.join(HERE, "mascote-bote.svg"), "w", encoding="utf-8").write(
    f'<svg viewBox="-10 -10 {VB_W + 20:.0f} {VB_H + 20:.0f}" xmlns="http://www.w3.org/2000/svg">{inner}</svg>')
STYLE = open(os.path.join(HERE, "mascote-anim.css"), encoding="utf-8").read()
open(os.path.join(HERE, "mascote-remando-avulso.svg"), "w", encoding="utf-8").write(svg.replace(">", "><style>" + STYLE + "</style>", 1))
print("ok", len(svg), "pegador", G.round(), "pa", B.round(), "remo px", int(paddle.sum()), "respingos px", int(splash.sum()))
