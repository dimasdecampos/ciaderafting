"""Boneco 2D articulado do Tamanduá-de-colete (estilo da arte nova, mascote-novo-orig.png).

Tudo é vetor. As coordenadas de referência são as da arte original (1479 x 1063 px):
a cabeça foi medida sobre ela, e o resto do corpo segue as mesmas proporções.

Cada pose é um dicionário de ângulos (graus; 0 = para a direita, 90 = para baixo).
render(pose) devolve um <svg> pronto para colocar na página.

Peças animáveis por CSS (classes):
  .mt-eyes .mt-lid   piscar
  .mt-mouth--*       bocas para falar (fechada, a, e, o)
  .mt-arm--near/far  braço inteiro gira no ombro (aceno)
  .mt-hand--*        mão gira no punho
"""
import math

INK = "#17181c"
CREAM = "#fef1cf"
CREAM_SH = "#f1dcb0"     # membros do lado de trás
CREAM_HL = "#fffaf0"
BLUE = "#1e9cf6"
BLUE_D = "#0d6fd0"
BLUE_L = "#9fdcff"
EAR_IN = "#f7c999"
MOUTH = "#5a1717"
TONGUE = "#f07d8c"
SW = 9          # traço principal
SW2 = 6         # traço de detalhe


# ---------------------------------------------------------------- geometria
def rot(p, a, c=(0, 0)):
    s, k = math.sin(math.radians(a)), math.cos(math.radians(a))
    x, y = p[0] - c[0], p[1] - c[1]
    return (c[0] + x * k - y * s, c[1] + x * s + y * k)


def add(a, b):
    return (a[0] + b[0], a[1] + b[1])


def polar(p, ang, L):
    return (p[0] + L * math.cos(math.radians(ang)), p[1] + L * math.sin(math.radians(ang)))


def f(v):
    return f"{v:.1f}".rstrip("0").rstrip(".")


def spline(pts, closed=True, t=1.0):
    """Catmull-Rom -> Bézier. Um ponto com 3º elemento 'c' vira canto (sem curva)."""
    P = [(p[0], p[1]) for p in pts]
    sharp = [len(p) > 2 and p[2] == "c" for p in pts]
    n = len(P)

    def tan(i):
        if sharp[i % n] or (not closed and (i == 0 or i == n - 1)):
            return (0.0, 0.0)
        a, b = P[(i - 1) % n], P[(i + 1) % n]
        return ((b[0] - a[0]) / 6 * t, (b[1] - a[1]) / 6 * t)

    d = [f"M{f(P[0][0])} {f(P[0][1])}"]
    segs = n if closed else n - 1
    for i in range(segs):
        a, b = P[i], P[(i + 1) % n]
        ta, tb = tan(i), tan(i + 1)
        c1 = (a[0] + ta[0], a[1] + ta[1])
        c2 = (b[0] - tb[0], b[1] - tb[1])
        d.append(f"C{f(c1[0])} {f(c1[1])} {f(c2[0])} {f(c2[1])} {f(b[0])} {f(b[1])}")
    if closed:
        d.append("Z")
    return "".join(d)


def sample(pts, per=8):
    """Pontos densos de uma Catmull-Rom aberta (para o eixo dos membros)."""
    out = []
    n = len(pts)
    for i in range(n - 1):
        p0 = pts[max(i - 1, 0)]; p1 = pts[i]; p2 = pts[i + 1]; p3 = pts[min(i + 2, n - 1)]
        for k in range(per):
            u = k / per
            u2, u3 = u * u, u * u * u
            out.append(tuple(0.5 * ((2 * p1[j]) + (-p0[j] + p2[j]) * u + (2 * p0[j] - 5 * p1[j] + 4 * p2[j] - p3[j]) * u2
                                    + (-p0[j] + 3 * p1[j] - 3 * p2[j] + p3[j]) * u3) for j in range(2)))
    out.append(tuple(pts[-1]))
    return out


def tube(axis, radii, cap0=True, cap1=True, per=6, t0=0.0, t1=1.0):
    """Contorno liso de um membro: eixo (pontos) + raio em cada ponto. Junta sem emenda."""
    dense = sample(axis, per)
    m = len(dense)
    rr = []
    for k in range(m):
        u = k / (m - 1) * (len(radii) - 1)
        i = min(int(u), len(radii) - 2)
        rr.append(radii[i] + (radii[i + 1] - radii[i]) * (u - i))
    lo, hi = int(round(t0 * (m - 1))), int(round(t1 * (m - 1)))
    dense, rr = dense[lo:hi + 1], rr[lo:hi + 1]
    m = len(dense)
    L, R = [], []
    for k in range(m):
        a = dense[max(k - 1, 0)]; b = dense[min(k + 1, m - 1)]
        dx, dy = b[0] - a[0], b[1] - a[1]
        l = math.hypot(dx, dy) or 1
        nx, ny = -dy / l, dx / l
        L.append((dense[k][0] + nx * rr[k], dense[k][1] + ny * rr[k]))
        R.append((dense[k][0] - nx * rr[k], dense[k][1] - ny * rr[k]))
    step = max(1, (m - 1) // 7)
    idx = list(range(0, m, step))
    if idx[-1] != m - 1:
        idx.append(m - 1)

    def cap(k, sign):
        a = dense[max(k - 1, 0)]; b = dense[min(k + 1, m - 1)]
        ang = math.degrees(math.atan2(b[1] - a[1], b[0] - a[0]))
        # da lateral +normal (L) para a -normal (R) no fim; o inverso no começo
        das = (60, 30, 0, -30, -60) if sign > 0 else (-120, -150, -180, -210, -240)
        return [polar(dense[k], ang + da, rr[k]) for da in das]

    pts = [L[k] for k in idx]
    pts += cap(m - 1, 1) if cap1 else []
    pts += [R[k] for k in reversed(idx)]
    pts += cap(0, -1) if cap0 else []
    return spline(pts)


def path(d, fill=CREAM, stroke=INK, sw=SW, extra=""):
    s = f'<path d="{d}" fill="{fill}"'
    if stroke:
        s += f' stroke="{stroke}" stroke-width="{f(sw)}" stroke-linejoin="round" stroke-linecap="round"'
    return s + extra + "/>"


def line(d, sw=SW2, color=INK, extra=""):
    return f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{f(sw)}" stroke-linecap="round" stroke-linejoin="round"{extra}/>'


def g(content, cls="", tr="", extra=""):
    a = f' class="{cls}"' if cls else ""
    a += f' transform="{tr}"' if tr else ""
    return f"<g{a}{extra}>{content}</g>"


# ---------------------------------------------------------------- cabeça (coordenadas da arte original)
NECK = (700, 300)   # pivô da cabeça

HEAD = [  # crânio + focinho; 0..16 recebem contorno, o resto é a base escondida no pescoço
    (604, 150), (600, 105), (622, 55), (672, 22), (740, 8), (805, 20), (848, 50), (872, 80),
    (930, 100), (1000, 124), (1070, 154), (1122, 185), (1152, 212), (1169, 243), (1164, 272),
    (1146, 291), (1118, 299), (1086, 292), (1045, 276), (995, 262), (948, 253), (905, 256),
    (874, 264), (838, 274), (800, 288), (768, 306), (740, 332),
    (690, 348), (630, 330), (598, 270), (592, 205)]
HEAD_STROKE_END = 26   # contorno vai do ponto 0 ao 26 (queixo)

NOSE_CLIP = [(1048, 140), (1030, 175), (1020, 220), (1024, 262), (1040, 300), (1220, 330), (1220, 120)]

BANDANA = [(603, 152, "c"), (597, 110), (612, 62), (652, 28), (712, 7), (772, 5), (818, 20), (847, 46, "c"),
           (812, 64), (770, 78), (728, 88), (697, 98), (686, 125), (684, 172), (691, 222), (704, 262),
           (713, 286, "c"), (694, 294), (671, 289, "c"), (652, 254), (641, 200), (643, 148, "c"), (624, 147)]
BANDANA_HL = [(622, 92), (648, 48), (700, 22), (760, 16)]
BANDANA_DK = [(652, 160), (650, 215), (664, 262), (680, 284)]


def head_parts(uid, hat="bandana"):
    hd = spline(HEAD)
    s = []
    s.append(path(hd, CREAM, None))
    s.append(f'<clipPath id="{uid}-hc"><path d="{hd}"/></clipPath>')
    # brilho no alto do focinho
    s.append(line(spline([(890, 104), (960, 124), (1030, 152)], closed=False), 14, CREAM_HL))
    # ponta preta do focinho + reflexo
    s.append(g(path(spline(NOSE_CLIP), INK, None) +
               line(spline([(1092, 175), (1130, 198), (1152, 232), (1150, 262)], closed=False), 7, "#74777f"),
               extra=f' clip-path="url(#{uid}-hc)"'))
    s.append(line(spline(HEAD[:HEAD_STROKE_END + 1], closed=False), SW))
    # orelha
    ear = [(688, 104), (712, 92), (738, 100), (746, 120), (736, 140), (712, 148), (692, 140)]
    s.append(path(spline(ear), CREAM, INK, SW2 + 1))
    s.append(path(spline([(694, 108), (712, 100), (720, 118), (712, 138), (696, 134)]), EAR_IN, None))
    s.append(line(spline([(728, 112), (716, 104), (704, 114), (708, 128), (722, 136)], closed=False), SW2))
    if hat == "bandana":
        s.append(path(spline(BANDANA), BLUE, INK, SW))
        s.append(line(spline(BANDANA_HL, closed=False), 9, BLUE_L, ' opacity=".9"'))
        s.append(line(spline(BANDANA_DK, closed=False), 10, BLUE_D, ' opacity=".8"'))
        s.append(line("M742 26 L768 44 L748 44 L782 64", 5, INK))      # dobras do pano
        s.append(line("M690 40 L716 56 L700 60", 5, INK))
    # tufos de pelo na testa
    s.append(line("M742 92 L752 112", 5))
    s.append(line("M790 98 L776 116", 5))
    return "".join(s)


def eyes(uid, brow="firme", look=(0, 0)):
    cx, cy = 823, 141
    s = []
    eye_d = f"M{cx} {cy - 52}" \
            f"C{cx + 26} {cy - 52} {cx + 39} {cy - 25} {cx + 38} {cy + 2}" \
            f"C{cx + 37} {cy + 32} {cx + 22} {cy + 52} {cx - 2} {cy + 51}" \
            f"C{cx - 26} {cy + 50} {cx - 37} {cy + 24} {cx - 36} {cy - 4}" \
            f"C{cx - 35} {cy - 32} {cx - 24} {cy - 52} {cx} {cy - 52}Z"
    s.append(f'<clipPath id="{uid}-ec"><path d="{eye_d}"/></clipPath>')
    s.append(path(eye_d, "#fff", None))
    px, py = 837 + look[0], 147 + look[1]
    s.append(g(f'<ellipse cx="{px}" cy="{py}" rx="23" ry="33" fill="{INK}"/>'
               f'<circle cx="{px - 9}" cy="{py + 2}" r="8.5" fill="#fff"/>'
               f'<circle cx="{px + 8}" cy="{py - 16}" r="4" fill="#fff"/>',
               extra=f' clip-path="url(#{uid}-ec)"'))
    # pálpebra (pisca): cobre o olho de cima para baixo
    s.append(g(path(f"M{cx - 50} {cy - 62}H{cx + 50}V{cy + 14}Q{cx} {cy + 30} {cx - 50} {cy + 14}Z", CREAM, None) +
               line(f"M{cx - 36} {cy + 10}Q{cx} {cy + 28} {cx + 38} {cy + 8}", SW2 + 1),
               "mt-lid", extra=f' clip-path="url(#{uid}-ec)"'))
    s.append(path(eye_d, "none", INK, SW2 + 1))
    if brow == "firme":      # cara da arte original: sobrancelha desce para o focinho
        b = [(778, 116), (796, 92), (826, 80), (852, 90), (870, 112), (876, 126), (862, 108), (836, 94), (806, 98)]
    elif brow == "alegre":   # sobrancelha arqueada, simpática
        b = [(782, 98), (800, 74), (828, 64), (854, 70), (872, 88), (874, 98), (854, 82), (828, 78), (802, 86)]
    else:                    # surpresa
        b = [(784, 84), (802, 58), (830, 48), (856, 56), (872, 76), (872, 86), (854, 68), (830, 62), (804, 72)]
    s.append(path(spline(b), INK, None))
    return g("".join(s), "mt-eyes")


def cheek():
    return line(spline([(794, 222), (840, 205), (896, 196)], closed=False), 15)


MOUTHS = {
    "fechada": lambda: line("M818 236 L834 230", SW2) + line(spline([(826, 246), (850, 258), (882, 261)], closed=False), SW2 + 1),
    "sorriso": lambda: line(spline([(816, 232), (838, 256), (870, 264), (898, 258)], closed=False), SW2 + 1)
               + line("M812 240 L824 226", SW2),
    "a": lambda: path(spline([(830, 252), (872, 262, "c"), (930, 254, "c"), (928, 286), (896, 312), (858, 304), (836, 280)]), MOUTH, INK, SW2 + 1)
         + path(spline([(852, 296), (880, 288), (908, 296), (890, 308), (862, 304)]), TONGUE, None),
    "e": lambda: path(spline([(830, 252), (872, 262, "c"), (930, 254, "c"), (924, 272), (890, 284), (852, 278)]), MOUTH, INK, SW2 + 1)
         + path(spline([(862, 274), (888, 270), (906, 276), (888, 281)]), TONGUE, None),
    "o": lambda: path(spline([(846, 258), (874, 262, "c"), (904, 260, "c"), (910, 284), (888, 300), (862, 294), (850, 276)]), MOUTH, INK, SW2 + 1),
}


def mouths(talk=True, rest="fechada"):
    s = [g(MOUTHS[rest](), f"mt-mouth mt-mouth--{rest}")]
    if talk:
        for k in ("a", "e", "o"):
            s.append(g(MOUTHS[k](), f"mt-mouth mt-mouth--{k}"))
    return "".join(s)


# ---------------------------------------------------------------- corpo
HIP = (612, 650)
TORSO = [(604, 150), (576, 170), (532, 203, "c"), (562, 206, "c"), (522, 238), (494, 268, "c"), (518, 265, "c"),
         (482, 312), (456, 390), (446, 470), (456, 556), (490, 636), (552, 692), (630, 706), (708, 690),
         (762, 632), (784, 548), (782, 456), (762, 372), (742, 330), (720, 290), (680, 230), (640, 170)]
VEST = [(470, 290), (560, 290), (640, 298), (696, 320), (716, 400), (724, 500), (716, 600), (700, 720, "c"),
        (400, 720, "c"), (400, 300)]
SHOULDER_N = (650, 400)
SHOULDER_F = (742, 352)
HIP_N = (650, 652)
HIP_F = (566, 640)
TAIL_BASE = (488, 604)


def torso_parts(uid):
    td = spline(TORSO)
    s = [path(td, CREAM, None),
         f'<clipPath id="{uid}-tc"><path d="{td}"/></clipPath>',
         g(path(spline(VEST), INK, None) +
           line(spline([(486, 340), (468, 440), (474, 540)], closed=False), 12, "#3a3c44", ' opacity=".9"'),
           extra=f' clip-path="url(#{uid}-tc)"'),
         path(td, "none", INK, SW)]
    return "".join(s)


# ---------------------------------------------------------------- mãos e pés (local: punho em 0,0, apontando +x)
def hand(kind, shade=False):
    c = CREAM_SH if shade else CREAM
    if kind == "punho":
        o = [(-6, -34), (24, -46), (62, -50), (92, -40), (108, -18), (112, 8), (104, 32), (82, 48), (44, 50), (8, 40), (-8, 14)]
        d = [line(spline([(110, -6), (90, -10), (74, -4)], closed=False)),
             line(spline([(106, 20), (88, 16), (74, 22)], closed=False)),
             line(spline([(28, -34), (58, -38), (82, -26), (86, -10)], closed=False))]
        return path(spline(o), c) + "".join(d)
    if kind == "aberta":   # palma aberta, dedos para +x
        o = [(-6, -30), (30, -40), (52, -62), (70, -86), (86, -82), (80, -56), (92, -46), (128, -58), (138, -46),
             (106, -24), (140, -20), (144, -6), (108, 0), (136, 14), (134, 28), (100, 20), (110, 42), (98, 52),
             (70, 36), (40, 44), (8, 36), (-8, 10)]
        return path(spline(o), c) + line(spline([(40, -20), (62, -10), (66, 10)], closed=False), SW2 - 1)
    if kind == "aponta":   # punho com indicador esticado
        o = [(-6, -34), (24, -46), (60, -50), (88, -44), (132, -50), (150, -42), (148, -28), (104, -20), (110, 8),
             (102, 32), (82, 48), (44, 50), (8, 40), (-8, 14)]
        d = [line(spline([(104, 12), (88, 8), (74, 14)], closed=False)),
             line(spline([(30, -32), (58, -34), (80, -24)], closed=False))]
        return path(spline(o), c) + "".join(d)
    if kind == "segura":   # punho fechado visto de lado, para segurar cabo (o cabo passa no x=60)
        o = [(-6, -36), (26, -48), (64, -52), (96, -42), (110, -16), (112, 12), (102, 38), (76, 52), (40, 52), (6, 40), (-8, 12)]
        d = [line(spline([(112, -2), (94, -6), (80, 0)], closed=False)),
             line(spline([(108, 24), (90, 20), (78, 26)], closed=False)),
             line(spline([(30, -36), (60, -40), (84, -30)], closed=False))]
        return path(spline(o), c) + "".join(d)
    raise ValueError(kind)


def foot(shade=False):
    c = CREAM_SH if shade else CREAM
    o = [(-34, -22), (0, -34), (44, -28), (86, -12), (118, 6), (124, 28), (104, 40), (40, 42), (-20, 38), (-42, 14)]
    d = [line("M98 38 L104 18", SW2 - 1), line("M74 41 L78 20", SW2 - 1)]
    return path(spline(o), c) + "".join(d)


def tail(base, ang, curl, uid, L=330):
    """Rabo preênsil: sai da base na direção ang, enrolando 'curl' graus; ponta preta."""
    pts, p, a = [base], base, ang
    seg = L / 5
    for k in range(5):
        a += curl / 5
        p = polar(p, a, seg)
        pts.append(p)
    radii = [42, 50, 52, 50, 40, 8]
    d_all = tube(pts, radii, cap0=False)
    d_tip = tube(pts, [r + 2 for r in radii], cap0=False, t0=0.58)
    tip_edge = sample(pts, 6)
    k0 = int(0.58 * (len(tip_edge) - 1))
    s = [path(d_all, CREAM, None),
         f'<clipPath id="{uid}-tl"><path d="{d_all}"/></clipPath>',
         g(path(d_tip, INK, None), extra=f' clip-path="url(#{uid}-tl)"'),
         path(d_all, "none", INK, SW)]
    return "".join(s)


# ---------------------------------------------------------------- acessórios
def paddle(grip, ang, L=520):
    """Remo: punho T em 'grip', cabo cinza, pá amarela no fim."""
    end = polar(grip, ang, L)
    sh = polar(grip, ang, L - 150)
    s = [line(f"M{f(grip[0])} {f(grip[1])}L{f(sh[0])} {f(sh[1])}", 30, INK),
         line(f"M{f(grip[0])} {f(grip[1])}L{f(sh[0])} {f(sh[1])}", 16, "#c9ced8"),
         line(f"M{f(grip[0])} {f(grip[1])}L{f(sh[0])} {f(sh[1])}", 5, "#f4f6fa", ' opacity=".9"')]
    blade = [polar(sh, ang + 90, 26), polar(polar(sh, ang, 40), ang + 90, 46), polar(end, ang + 90, 40), polar(polar(end, ang, 26), ang, 0),
             polar(end, ang - 90, 40), polar(polar(sh, ang, 40), ang - 90, 46), polar(sh, ang - 90, 26)]
    s.append(path(spline(blade), "#fde208", INK, SW))
    s.append(line(f"M{f(polar(sh, ang, 30)[0])} {f(polar(sh, ang, 30)[1])}L{f(polar(end, ang, -20)[0])} {f(polar(end, ang, -20)[1])}", 6, "#f0ac14"))
    t1, t2 = polar(grip, ang + 90, 36), polar(grip, ang - 90, 36)
    s.append(line(f"M{f(t1[0])} {f(t1[1])}L{f(t2[0])} {f(t2[1])}", 34, INK))
    s.append(line(f"M{f(t1[0])} {f(t1[1])}L{f(t2[0])} {f(t2[1])}", 20, "#fde208"))
    return "".join(s)


def stick(top, ang, L=640):
    bot = polar(top, ang, L)
    mid = polar(polar(top, ang, L * .5), ang + 90, 8)
    d = spline([top, mid, bot], closed=False)
    return line(d, 30, INK) + line(d, 17, "#9a6236") + line(spline([polar(top, ang, 40), polar(polar(top, ang, L * .45), ang + 90, 10)], closed=False), 4, "#c4864f")


def hiker_hat():
    """Chapéu de trilheiro verde (substitui a bandana)."""
    crown = [(612, 128, "c"), (614, 70), (650, 24), (716, 2), (786, 8), (832, 40), (846, 90, "c")]
    brim = [(556, 140), (600, 112), (700, 96), (800, 92), (880, 100), (918, 120), (880, 136), (780, 134), (680, 140), (590, 156)]
    s = [path(spline(crown, closed=True), "#4c9a3c", INK, SW),
         line(spline([(640, 50), (700, 22), (770, 22)], closed=False), 9, "#7cc565"),
         path(spline([(612, 104), (720, 92), (842, 84), (846, 108), (720, 116), (614, 126)]), "#8a5a2e", INK, SW2),
         path(spline(brim), "#3f8531", INK, SW)]
    return "".join(s)


def backpack(shade=False):
    pack = [(380, 330), (440, 300), (500, 312), (520, 380), (520, 560), (500, 620), (420, 630), (370, 600), (356, 460)]
    roll = [(398, 280), (480, 270), (500, 300), (480, 322), (398, 328), (380, 304)]
    s = [path(spline(pack), "#4c9a3c", INK, SW),
         path(spline([(372, 470), (430, 460), (470, 470), (470, 560), (430, 580), (376, 568)]), "#3f8531", INK, SW2),
         path(spline(roll), "#7cc565", INK, SW2 + 1),
         line("M440 274 L436 326", SW2 - 1), line("M412 470 L420 520", 5)]
    return "".join(s)


# ---------------------------------------------------------------- montagem
def limb_arm(sh, a1, a2, L1, L2, r, cls, hand_kind, hand_ang, flip, shade, uid, extra_front=""):
    el = polar(sh, a1, L1)
    wr = polar(el, a2, L2)
    d = tube([sh, el, wr], r)
    c = CREAM_SH if shade else CREAM
    hk = hand_ang if hand_ang is not None else a2
    sy = -1 if flip else 1
    hnd = g(g(g(hand(hand_kind, shade), "", "translate(-14 0)"), f"mt-hand mt-hand--{cls}", extra=' style="transform-origin:0 0"'),
            "", f"translate({f(wr[0])} {f(wr[1])}) rotate({f(hk)}) scale(1 {sy})")
    body = path(d, c, INK, SW)
    return g(body + extra_front + hnd, f"mt-arm mt-arm--{cls}", extra=f' style="transform-origin:{f(sh[0])}px {f(sh[1])}px"'), wr


def limb_leg(hp, a1, a2, L1, L2, r, foot_ang, shade, cls):
    kn = polar(hp, a1, L1)
    an = polar(kn, a2, L2)
    d = tube([hp, kn, an], r)
    c = CREAM_SH if shade else CREAM
    ft = g(foot(shade), "", f"translate({f(an[0])} {f(an[1])}) rotate({f(foot_ang)})")
    return g(path(d, c, INK, SW) + ft, f"mt-leg mt-leg--{cls}"), an


DEFAULT = dict(
    torso=0, head=0, brow="firme", look=(0, 0), mouth="fechada", talk=True, hat="bandana", flip=False,
    arm_n=(70, 20, "punho", None, False), arm_f=(8, 0, "punho", None, False), arm_f_front=False,
    leg_n=(95, 85, 0), leg_f=(100, 85, 0), tail=(200, 70), extras=None, legs=True,
)


def render(pose, uid="mt", label="Mascote Tamanduá-de-colete", view=None, cls="", underlay=None):
    if isinstance(pose, str):
        cls = (cls + " mt--" + pose).strip()
        pose = POSES[pose]
    P = dict(DEFAULT); P.update(pose)
    T = P["torso"]
    tr = lambda p: rot(p, T, HIP)
    sN, sF, hN, hF, tb, nk = tr(SHOULDER_N), tr(SHOULDER_F), tr(HIP_N), tr(HIP_F), tr(TAIL_BASE), tr(NECK)
    layers = {k: [] for k in ("back", "tail", "leg_f", "arm_f_back", "torso", "leg_n", "arm_f_front", "head", "arm_n", "front")}
    ex = P["extras"] or {}

    a = P["arm_f"]
    armf, wrf = limb_arm(sF, a[0], a[1], 150, 140, [50, 42, 34], "far", a[2], a[3], a[4], True, uid)
    layers["arm_f_front" if P["arm_f_front"] else "arm_f_back"].append(armf)
    a = P["arm_n"]
    armn, wrn = limb_arm(sN, a[0], a[1], 170, 150, [68, 54, 40], "near", a[2], a[3], a[4], False, uid)
    if P["legs"]:
        l = P["leg_f"]
        lf, _ = limb_leg(hF, l[0], l[1], 118, 100, [54, 44, 34], l[2], True, "far")
        layers["leg_f"].append(lf)
        l = P["leg_n"]
        ln, _ = limb_leg(hN, l[0], l[1], 125, 105, [64, 50, 38], l[2], False, "near")
        layers["leg_n"].append(ln)
    tl = P["tail"]
    layers["tail"].append(g(tail(tb, tl[0], tl[1], uid), "mt-tail", extra=f' style="transform-origin:{f(tb[0])}px {f(tb[1])}px"'))

    torso_svg = torso_parts(uid)
    if "backpack" in ex:
        layers["back"].append(g(backpack(), "", f"rotate({f(T)} {HIP[0]} {HIP[1]})"))
    layers["torso"].append(g(torso_svg, "mt-torso", f"rotate({f(T)} {HIP[0]} {HIP[1]})"))
    if "backpack" in ex:   # alça por cima do ombro
        layers["torso"].append(g(path(spline([(560, 300), (600, 296), (640, 380), (650, 520), (620, 520), (606, 390)]), "#3f8531", INK, SW2),
                                 "", f"rotate({f(T)} {HIP[0]} {HIP[1]})"))

    head_tr = f"translate({f(nk[0] - NECK[0])} {f(nk[1] - NECK[1])}) rotate({f(T + P['head'])} {NECK[0]} {NECK[1]})"
    hat = P["hat"]
    hsvg = head_parts(uid, hat) + cheek() + g(mouths(P["talk"], P["mouth"]), "mt-mouths") + eyes(uid, P["brow"], P["look"])
    if hat == "trilha":
        hsvg += hiker_hat()
    layers["head"].append(g(g(hsvg, "mt-head", extra=f' style="transform-origin:{NECK[0]}px {NECK[1]}px"'), "", head_tr))

    if "paddle" in ex:
        pa = ex["paddle"]
        layers["arm_f_back" if not P["arm_f_front"] else "arm_f_front"].insert(0, paddle(wrf if pa.get("grip") == "far" else pa["at"], pa["ang"], pa.get("L", 520)))
    if "stick" in ex:
        st = ex["stick"]
        top = polar(wrn, st["ang"], -st.get("above", 120))
        layers["arm_n"].insert(0, stick(top, st["ang"], st.get("L", 640)))
    layers["arm_n"].append(armn)
    for k, v in ex.items():
        if k.startswith("svg_"):
            layers[v[0]].append(v[1])

    order = ("back", "tail", "leg_f", "arm_f_back", "torso", "leg_n", "arm_f_front", "head", "arm_n", "front")
    inner = "".join("".join(layers[k]) for k in order)
    vb = view or P.get("view") or (60, -20, 1220, 1100)
    if underlay:
        inner = f'<image href="{underlay}" x="0" y="0" width="1479" height="1063" opacity=".4"/>' + inner
    if P["flip"]:
        inner = g(inner, "", f"translate({2 * vb[0] + vb[2]} 0) scale(-1 1)")
    return (f'<svg class="mt {cls}" viewBox="{" ".join(f(v) for v in vb)}" xmlns="http://www.w3.org/2000/svg" '
            f'role="img" aria-label="{label}">' + g(inner, "mt-rig", extra=f' style="transform-origin:{f(HIP[0])}px {f(HIP[1] + 300)}px"') + "</svg>")


# ---------------------------------------------------------------- poses
POSES = {
    # pose de referência: igual à arte (para conferir as proporções por cima do original)
    "ref": dict(arm_n=(52, 40, "punho", 20, False), arm_f=(4, 6, "punho", 0, False), arm_f_front=True, legs=False, tail=(205, 20)),
    # sobre.html: em pé, apontando para a frente e falando
    "fala": dict(view=(248, -60, 994, 1010), torso=-3, head=-9, brow="alegre", mouth="sorriso", look=(6, -4),
                 arm_n=(-4, -26, "aponta", -26, False), arm_f=(78, 30, "aberta", -20, True),
                 leg_n=(94, 86, 4), leg_f=(76, 104, -6), tail=(196, 60)),
    # trilhas.html: trilheiro com chapéu, mochila e cajado
    "trilha": dict(view=(246, -40, 1005, 1097), torso=-2, head=-3, brow="alegre", mouth="sorriso", hat="trilha",
                   arm_n=(62, 8, "segura", -92, False), arm_f=(96, 96, "punho", 96, True),
                   leg_n=(80, 100, 0), leg_f=(110, 82, -4), tail=(190, 70),
                   extras={"backpack": 1, "stick": {"ang": 96, "above": 150, "L": 620}}),
    # dica no canto da tela: acenando
    "acena": dict(view=(260, -40, 984, 986), torso=-3, head=-6, brow="alegre", mouth="sorriso", look=(-2, 0),
                  arm_n=(28, -48, "aberta", -84, True), arm_f=(82, 90, "punho", 90, True),
                  leg_n=(92, 88, 2), leg_f=(102, 84, -2), tail=(200, 60)),
}

if __name__ == "__main__":
    import os, sys
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), "rig-out")
    os.makedirs(out, exist_ok=True)
    for k, v in POSES.items():
        svg = render(v, uid="mt-" + k)
        open(os.path.join(out, k + ".svg"), "w", encoding="utf-8").write(svg.replace("<svg ", '<svg width="980" height="1080" ', 1))
    print("ok", list(POSES))
