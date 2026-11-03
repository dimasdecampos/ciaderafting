"""Gera o mascote animável a partir da arte original (sem vetorizar), em 3 camadas PNG/WebP
transparentes com bordas suaves:
  corpo  — tudo, menos o remo (onde o remo cruzava é preenchido pelos vizinhos)
  remo   — o remo com o contorno
  maos   — os punhos por cima do remo (o cabo passa por baixo deles)
Também exporta o mascote inteiro recortado (fundo transparente) para a pasta da marca."""
import os, json, numpy as np
from PIL import Image, ImageFilter
from collections import deque

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
src = np.asarray(Image.open(os.path.join(HERE, "mascote-novo-orig.png")).convert("RGB")).astype(float)
H, W = src.shape[:2]
ssum = src.sum(-1)
spread = src.max(-1) - src.min(-1)


def to_img(m):
    return Image.fromarray((m * 255).astype("uint8"))


def grow(m, r):
    return np.asarray(to_img(m).filter(ImageFilter.MaxFilter(2 * r + 1))) > 127 if r else m


def shrink(m, r):
    return np.asarray(to_img(m).filter(ImageFilter.MinFilter(2 * r + 1))) > 127 if r else m


def components(mask):
    out = np.zeros(mask.shape, int)
    n = 0
    for y0, x0 in zip(*np.nonzero(mask)):
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


# ---------- fundo branco (inclui vãos fechados entre braço/corpo e perto do quadril) ----------
cand = (ssum > 738) & (spread < 14)
lab, n = components(cand)
sizes = np.bincount(lab.ravel())
border = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))) - {0}
cy = np.bincount(lab.ravel(), weights=np.mgrid[0:H, 0:W][0].ravel()) / np.maximum(sizes, 1)
bg_ids = [k for k in range(1, n + 1) if k in border or sizes[k] > 6000 or (sizes[k] > 800 and 400 < cy[k] < 0.72 * H)]
bg = np.isin(lab, bg_ids)

# ---------- alfa com bordas suaves: "desmistura" o branco do serrilhado ----------
fringe = grow(bg, 2) & ~bg
alpha = np.where(bg, 0.0, 1.0)
a_est = np.clip((255 - src.min(-1)) / 255.0, 0, 1)
alpha = np.where(fringe, a_est, alpha)
safe = np.maximum(alpha, 0.02)[..., None]
rgb = np.where(fringe[..., None], np.clip((src - (1 - alpha[..., None]) * 255) / safe, 0, 255), src)

# ---------- remo ----------
PAL = {"ink": (21, 22, 26), "red": (254, 18, 2), "redD": (205, 12, 10), "redL": (245, 88, 82),
       "cream": (254, 241, 207), "creamD": (238, 208, 172), "yellow": (253, 230, 8), "yellowD": (240, 172, 20),
       "blue": (44, 153, 251), "blueL": (110, 190, 245), "cyan": (180, 238, 242), "white": (252, 252, 252),
       "grey": (170, 176, 186), "greyD": (95, 98, 106)}
names = list(PAL)
pal = np.array([PAL[k] for k in names], float)
cls = np.zeros((H, W), int)
for y in range(0, H, 128):
    cls[y:y + 128] = ((src[y:y + 128, :, None, :] - pal[None, None]) ** 2).sum(-1).argmin(-1)
M = {k: (cls == i) & ~bg for i, k in enumerate(names)}
yy, xx = np.mgrid[0:H, 0:W]

yel = M["yellow"] | M["yellowD"]
comp, nc = components(yel)
info = []
for k in range(1, nc + 1):
    ys, xs = np.nonzero(comp == k)
    if len(xs) > 20:
        info.append((len(xs), xs.mean(), ys.mean()))
blade = max((t for t in info if t[2] > H * 0.75), key=lambda t: t[0])
grip = max((t for t in info if t[2] < H * 0.45 and t[1] > W * 0.6), key=lambda t: t[0])
G = np.array(grip[1:]); B = np.array(blade[1:])
d = (B - G) / np.linalg.norm(B - G); L = np.linalg.norm(B - G)
dline = np.abs((xx - G[0]) * d[1] - (yy - G[1]) * d[0])
along = (xx - G[0]) * d[0] + (yy - G[1]) * d[1]
corridor = (along > -40) & (along < L + 110) & (dline < np.where(along > L - 230, 95, 40))  # pá é mais larga que o cabo
corridor = corridor | ((along >= L - 230) & (along < L + 170) & (dline < 95))   # ponta da pá
shaft_light = (M["white"] | M["cyan"] | M["blueL"] | M["grey"]) & (along < L - 110) & (dline < 34)  # brilho do cabo
pc, pn = components((yel | M["grey"] | M["greyD"] | shaft_light) & corridor)
paddle = np.zeros((H, W), bool)
for k in range(1, pn + 1):
    m = pc == k
    if m.sum() > 30:
        paddle |= m
paddle = shrink(grow(paddle, 9), 9) & corridor & ~bg   # fecha brilhos e contornos internos do remo
hands = (M["cream"] | M["creamD"]) & (dline < 90) & (along > -80) & (along < L * 0.55)
# remo + seu contorno preto (o contorno é mais grosso que o serrilhado)
paddle_layer = grow(paddle | (grow(paddle, 11) & M["ink"]), 1) & ~bg & ~grow(hands, 1)
hands_layer = grow(hands, 5) & ~bg & ~paddle                # punhos + contorno por cima do remo

# ---------- corpo: preenche onde estava o remo com as cores vizinhas (sem puxar o preto) ----------
hole = grow(paddle_layer, 2) & ~grow(hands, 1)
body_rgb = rgb.copy(); body_a = alpha.copy()
known = ~hole
source = known & ~M["ink"]           # só cores (vermelho, água, fundo) alimentam o preenchimento
for _ in range(90):  # espalha cor e alfa dos vizinhos conhecidos para dentro do buraco
    if known.all():
        break
    acc = np.zeros_like(body_rgb); acca = np.zeros_like(body_a); cnt = np.zeros_like(body_a)
    for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        k2 = np.roll(np.roll(source, dy, 0), dx, 1)
        acc += np.roll(np.roll(body_rgb, dy, 0), dx, 1) * k2[..., None]
        acca += np.roll(np.roll(body_a, dy, 0), dx, 1) * k2
        cnt += k2
    new = ~known & (cnt > 0)
    body_rgb[new] = acc[new] / cnt[new][:, None]
    body_a[new] = acca[new] / cnt[new]
    known = known | new
    source = source | new


def save_layer(rgbarr, a, mask, name, out_w):
    a2 = np.where(mask, a, 0) if mask is not None else a
    im = Image.fromarray(np.dstack([np.clip(rgbarr, 0, 255), a2 * 255]).astype("uint8"), "RGBA")
    bbox_full = (0, 0, W, H)
    im = im.crop(bbox_full).resize((out_w, round(H * out_w / W)), Image.LANCZOS)
    im.save(os.path.join(ROOT, "assets", "img", name + ".webp"), quality=88, method=6)
    return im


OUT_W = 1000
save_layer(body_rgb, body_a, None, "mascote-camada-corpo", OUT_W)
save_layer(rgb, alpha, paddle_layer, "mascote-camada-remo", OUT_W)
save_layer(rgb, alpha, hands_layer, "mascote-camada-maos", OUT_W)
# mascote inteiro recortado, resolução total, para a marca
full = Image.fromarray(np.dstack([np.clip(rgb, 0, 255), alpha * 255]).astype("uint8"), "RGBA")
full.save(os.path.join(ROOT, "assets", "marca", "mascote-tamandua-bote.png"), optimize=True)
json.dump({"w": W, "h": H, "pivo_pct": [round(G[0] / W * 100, 2), round(G[1] / H * 100, 2)]},
          open(os.path.join(HERE, "camadas.json"), "w"))
print("pivo %", round(G[0] / W * 100, 2), round(G[1] / H * 100, 2))
