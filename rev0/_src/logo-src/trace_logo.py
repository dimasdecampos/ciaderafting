import os, sys, numpy as np, potrace
from PIL import Image, ImageFilter
from collections import deque
im = Image.open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "logo-orig.png")).convert("RGBA")
W, H = im.size
a = np.asarray(im).astype(int)
r, g, b, al = a[..., 0], a[..., 1], a[..., 2], a[..., 3]
on = al > 128
blue = on & (b > r + 40) & (b > 90)
red = on & (r > 150) & (g < 120) & (b < 120)
yellow = on & (r > 160) & (g > 140) & (b < 120)
dark = on & ~blue & ~red & ~yellow & (np.maximum(np.maximum(r, g), b) < 140)

def mean_hex(m):
    c = a[m][:, :3].mean(0).round().astype(int)
    return "#%02x%02x%02x" % tuple(c)

def dilate(m, px):
    return np.asarray(Image.fromarray((m * 255).astype("uint8")).filter(ImageFilter.MaxFilter(px * 2 + 1))) > 127

# camadas de baixo ganham uma sobra para não abrir frestas
blue_d = dilate(blue, 3) & on
yellow_d = dilate(yellow, 2) & on
S = 0.5  # escala final (viewBox ~1168x512)

def pt(p):
    x, y = (p.x, p.y) if hasattr(p, "x") else p
    return f"{x*S:.1f} {y*S:.1f}"

def curve_d(c):
    d = ["M" + pt(c.start_point)]
    for s in c.segments:
        if s.is_corner:
            d.append("L" + pt(s.c) + "L" + pt(s.end_point))
        else:
            d.append("C" + pt(s.c1) + " " + pt(s.c2) + " " + pt(s.end_point))
    return "".join(d) + "Z"

def trace(m, turd=30):
    bm = potrace.Bitmap(~m)
    return bm.trace(turdsize=turd, turnpolicy=potrace.POTRACE_TURNPOLICY_MINORITY, alphamax=1.0, opticurve=True, opttolerance=0.3)

# componentes conectados das letras (em meia resolução)
small = np.asarray(Image.fromarray((dark * 255).astype("uint8")).resize((W // 2, H // 2))) > 127
lab = np.zeros(small.shape, int); n = 0
hh, ww = small.shape
for y in range(hh):
    for x in range(ww):
        if small[y, x] and not lab[y, x]:
            n += 1; q = deque([(y, x)]); lab[y, x] = n
            while q:
                cy, cx = q.popleft()
                for dy, dx in ((1,0),(-1,0),(0,1),(0,-1)):
                    ny, nx = cy + dy, cx + dx
                    if 0 <= ny < hh and 0 <= nx < ww and small[ny, nx] and not lab[ny, nx]:
                        lab[ny, nx] = n; q.append((ny, nx))
sizes = np.bincount(lab.ravel())
def comp_of(c):
    pts = [c.start_point] + [s.end_point for s in c.segments]
    votes = []
    for p in pts:
        x, y = (p.x, p.y) if hasattr(p, "x") else p
        cx, cy = int(x // 2), int(y // 2)
        for rr in range(1, 8):
            win = lab[max(0, cy-rr):cy+rr+1, max(0, cx-rr):cx+rr+1]
            vals = win[win > 0]
            if vals.size:
                votes.append(int(np.bincount(vals).argmax())); break
    return int(np.bincount(votes).argmax()) if votes else 0

groups = {}
for c in trace(dark):
    k = comp_of(c)
    groups.setdefault(k, []).append(curve_d(c))
# ordena letras da esquerda p/ direita, linha de cima antes
def bbox(k):
    ys, xs = np.nonzero(lab == k); return xs.min(), ys.min(), xs.max(), ys.max()
items = []
for k, ds in groups.items():
    if k == 0: continue
    x0, y0, x1, y1 = bbox(k)
    row = 0 if (y0 + y1) / 2 < hh * 0.42 else 1
    items.append((row, x0, ds, (x0, y0, x1, y1)))
items.sort(key=lambda t: (t[0], t[1]))
print("letras/partes:", len(items), file=sys.stderr)

def layer(m, cls, color, turd=30):
    ds = "".join(curve_d(c) for c in trace(m, turd))
    return f'<path class="{cls}" fill="{color}" fill-rule="evenodd" d="{ds}"/>'

cols = {"blue": mean_hex(blue), "yellow": mean_hex(yellow), "red": mean_hex(red), "dark": mean_hex(dark)}
print(cols, file=sys.stderr)
letters = []
for i, (row, x0, ds, bb) in enumerate(items):
    ox, oy = (bb[0] + bb[2]) * 2 / 2 * S, (bb[1] + bb[3]) * 2 / 2 * S  # centro p/ transform-origin
    letters.append(f'<path class="lg-l" style="--i:{i};transform-origin:{ox:.0f}px {oy:.0f}px" d="{"".join(ds)}"/>')
svg = (f'<svg class="logo-svg" viewBox="0 0 {W*S:.0f} {H*S:.0f}" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Cia. de Rafting">'
       f'<g class="lg-paddles">'
       f'<g class="lg-p lg-p--blue">{layer(blue_d, "lg-blue", cols["blue"])}</g>'
       f'<g class="lg-p lg-p--yellow">{layer(yellow_d, "lg-yellow", cols["yellow"])}</g>'
       f'<g class="lg-p lg-p--red">{layer(red, "lg-red", cols["red"])}</g>'
       f'</g><g class="lg-text" fill="currentColor" fill-rule="evenodd">{"".join(letters)}</g></svg>')
open(sys.argv[1], "w", encoding="utf-8").write(svg)
print("bytes", len(svg), file=sys.stderr)
