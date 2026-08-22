#!/usr/bin/env python3
"""Wildhaven critters, second generation.

Designer-toy inspired rebuild of the cast: chibi proportions (head is
most of the mass), huge glossy eyes with double highlights, soft cell
shading, thick rounded outlines, blush, and one signature quirk per
character. Rendered supersampled then downscaled so edges stay soft.

render(species, px) -> RGBA Image, transparent background.
"""

import math

from PIL import Image, ImageDraw, ImageFilter

INK = (48, 40, 46, 255)          # warm dark outline, not pure black
SS = 3                            # supersample factor


def _mix(c, other, t):
    return tuple(int(a + (b - a) * t) for a, b in zip(c[:3], other[:3])) + (255,)


def _dark(c, t=0.22):
    return _mix(c, (66, 44, 86), t)


def _light(c, t=0.35):
    return _mix(c, (255, 255, 255), t)


MODE = "color"   # "color" | "lineart" | "silhouette"


def _map_fill(fill):
    if fill is None or MODE == "color":
        return fill
    if MODE == "silhouette":
        return (30, 26, 32, 255) if (len(fill) < 4 or fill[3] > 120) else None
    # lineart: keep dark strokes (ink, pupils), turn every light fill white,
    # drop translucent overlays (blush, glow) entirely
    if len(fill) == 4 and fill[3] < 200:
        return None
    lum = 0.299 * fill[0] + 0.587 * fill[1] + 0.114 * fill[2]
    return fill if lum < 90 else (255, 255, 255, 255)


class Ctx:
    def __init__(self, px):
        self.S = px * SS
        self.img = Image.new("RGBA", (self.S, self.S), (0, 0, 0, 0))
        self.d = ImageDraw.Draw(self.img)
        self.u = self.S / 100.0   # all geometry in 0..100 units

    def E(self, x0, y0, x1, y1, fill, outline=None, ow=0):
        u = self.u
        fill = _map_fill(fill)
        if fill is None:
            return
        self.d.ellipse([x0 * u, y0 * u, x1 * u, y1 * u], fill=fill,
                       outline=outline, width=int(ow * u))

    def P(self, pts, fill, outline=None, ow=0):
        u = self.u
        fill = _map_fill(fill)
        if fill is None:
            return
        self.d.polygon([(x * u, y * u) for x, y in pts], fill=fill,
                       outline=outline, width=max(1, int(ow * u)))

    def A(self, x0, y0, x1, y1, a0, a1, fill, w):
        u = self.u
        fill = _map_fill(fill) or (30, 26, 32, 255)
        self.d.arc([x0 * u, y0 * u, x1 * u, y1 * u], a0, a1, fill=fill,
                   width=max(2, int(w * u)))

    def L(self, pts, fill, w):
        u = self.u
        fill = _map_fill(fill)
        if fill is None:
            return
        self.d.line([(x * u, y * u) for x, y in pts], fill=fill,
                    width=max(2, int(w * u)), joint="curve")

    def out(self, px):
        return self.img.resize((px, px), Image.LANCZOS)


OW = 1.6   # outline weight in units


def face(c, cx, cy, w, mood="smile", eyes_closed=False, eye_dx=0.0,
         iris=(66, 48, 54), fang=True, blush=(250, 150, 150, 90)):
    """The family face: huge low-set glossy eyes, tiny grin, one fang."""
    eyes_closed = eyes_closed or FORCE_CLOSED
    ew = w * 0.30                 # eye width relative to face width
    eh = ew * 1.18
    ey = cy + w * 0.05            # low on the face (neoteny)
    ex = w * 0.30
    if eyes_closed:
        aw = ew * 0.55
        for sx in (-1, 1):
            x = cx + sx * ex
            c.A(x - aw, ey - aw * 0.6, x + aw, ey + aw * 1.0, 180, 360,
                INK, OW * 0.9)
    else:
        for sx in (-1, 1):
            x = cx + sx * ex + eye_dx
            c.E(x - ew / 2, ey - eh / 2, x + ew / 2, ey + eh / 2, INK)
            c.E(x - ew * 0.36, ey - eh * 0.34, x + ew * 0.36, ey + eh * 0.42,
                iris + (255,))
            c.E(x - ew * 0.30, ey - eh * 0.05, x + ew * 0.24, ey + eh * 0.40,
                (30, 24, 30, 255))
            # double highlight: big upper-left + small lower-right
            c.E(x - ew * 0.30, ey - eh * 0.36, x + ew * 0.02, ey - eh * 0.04,
                (255, 255, 255, 245))
            c.E(x + ew * 0.10, ey + eh * 0.14, x + ew * 0.26, ey + eh * 0.30,
                (255, 255, 255, 200))
    # blush
    for sx in (-1, 1):
        c.E(cx + sx * w * 0.52 - w * 0.10, ey + w * 0.16,
            cx + sx * w * 0.52 + w * 0.10, ey + w * 0.28, blush)
    # mouth
    my = ey + w * 0.24
    if mood == "beak":
        c.P([(cx - w * 0.07, my - w * 0.03), (cx + w * 0.07, my - w * 0.03),
             (cx, my + w * 0.07)], INK)
        c.P([(cx - w * 0.055, my - w * 0.02), (cx + w * 0.055, my - w * 0.02),
             (cx, my + w * 0.055)], (255, 168, 74, 255))
    elif mood == "smile":
        c.A(cx - w * 0.10, my - w * 0.06, cx + w * 0.10, my + w * 0.08,
            15, 165, INK, OW * 0.8)
        if fang:
            c.P([(cx + w * 0.045, my + w * 0.055), (cx + w * 0.10, my + w * 0.055),
                 (cx + w * 0.072, my + w * 0.115)], (255, 255, 255, 255))
    elif mood == "open":
        c.E(cx - w * 0.085, my - w * 0.02, cx + w * 0.085, my + w * 0.11,
            (94, 48, 56, 255))
        c.E(cx - w * 0.05, my + w * 0.05, cx + w * 0.05, my + w * 0.11,
            (240, 130, 140, 255))
        if fang:
            c.P([(cx - w * 0.075, my - w * 0.012), (cx - w * 0.025, my - w * 0.012),
                 (cx - w * 0.05, my + w * 0.045)], (255, 255, 255, 255))


def shaded_ball(c, cx, cy, r, col, squash=1.0):
    """outlined ball with soft top-light / bottom-shade cell shading"""
    ry = r * squash
    c.E(cx - r, cy - ry, cx + r, cy + ry, INK)                       # outline
    k = OW
    c.E(cx - r + k, cy - ry + k, cx + r - k, cy + ry - k, col + (255,))
    c.E(cx - r * 0.72, cy + ry * 0.28, cx + r * 0.72, cy + ry * 0.92,
        _dark(col, 0.14))
    c.E(cx - r * 0.55, cy - ry * 0.78, cx + r * 0.2, cy - ry * 0.25,
        _light(col, 0.28))


FORCE_CLOSED = False


def render(species, px=900, eyes_closed=False, mode="color"):
    global FORCE_CLOSED, MODE
    FORCE_CLOSED = eyes_closed
    MODE = mode
    try:
        c = Ctx(px)
        DRAW[species](c)
    finally:
        FORCE_CLOSED = False
        MODE = "color"
    return c.out(px)


# ---------------------------------------------------------------- cast

def flufftail(c):
    body = (162, 210, 134)
    belly = (236, 248, 214)
    # signature: enormous fluffy tail — stacked soft lobes curling up
    lobes = [(76, 74, 12), (84, 58, 14), (86, 38, 13), (78, 22, 11)]
    for x, y, r in lobes:
        c.E(x - r - OW * 0.6, y - r - OW * 0.6, x + r + OW * 0.6, y + r + OW * 0.6, INK)
    for x, y, r in lobes:
        c.E(x - r, y - r, x + r, y + r, _light(body, 0.16))
    for x, y, r in lobes:
        c.E(x - r * 0.6, y - r * 0.7, x + r * 0.4, y + r * 0.1, _light(body, 0.4))
    # ears: proper triangles with inner color
    for sx in (-1, 1):
        c.P([(50 + sx * 22, 26), (50 + sx * 15, 2), (50 + sx * 4, 18)], INK)
        c.P([(50 + sx * 19, 24), (50 + sx * 14, 6), (50 + sx * 7, 18)], body + (255,))
        c.P([(50 + sx * 16, 21), (50 + sx * 13.5, 10), (50 + sx * 10, 18)],
            (250, 200, 210, 255))
    # head (dominant) + small body
    shaded_ball(c, 47, 74, 21, body, 0.9)
    c.E(47 - 12, 67, 47 + 12, 87, belly + (255,))
    shaded_ball(c, 50, 40, 30, body)
    face(c, 50, 40, 42)


def pebblit(c):
    body = (184, 180, 192)
    shell = (126, 124, 140)
    # head + body first
    shaded_ball(c, 50, 66, 24, body, 0.86)
    shaded_ball(c, 50, 42, 29, body)
    # signature: round pebble cap sitting on the head, with a crack + leaf
    c.E(27, 8, 73, 40, INK)
    c.E(29, 10, 71, 38, shell + (255,))
    c.E(34, 13, 58, 26, _light(shell, 0.25))
    c.L([(58, 14), (63, 20), (60, 26)], _dark(shell, 0.35), 0.9)
    c.L([(44, 6), (47, 1)], (98, 160, 80, 255), 1.2)
    c.E(45, -3, 53, 3, (128, 196, 104, 255))
    c.E(47, -1.5, 50, 1, (170, 220, 150, 255))
    face(c, 50, 46, 38, mood="open")


def aquaphin(c):
    body = (132, 192, 228)
    belly = (222, 244, 252)
    # signature: two-lobe dolphin fluke + water droplet
    for lx, ly in ((80, 74), (86, 82)):
        c.E(lx - 8 - OW * 0.6, ly - 6 - OW * 0.6, lx + 8 + OW * 0.6,
            ly + 6 + OW * 0.6, INK)
    for lx, ly in ((80, 74), (86, 82)):
        c.E(lx - 8, ly - 6, lx + 8, ly + 6, body + (255,))
        c.E(lx - 5, ly - 4, lx + 1, ly, _light(body, 0.25))
    shaded_ball(c, 48, 66, 24, body, 0.9)
    shaded_ball(c, 50, 40, 30, body)
    c.E(50 - 12, 60, 50 + 12, 80, belly + (255,))
    # fin
    c.P([(42, 12), (50, -2), (58, 12)], INK)
    c.P([(44, 11), (50, 1), (56, 11)], _dark(body, 0.1))
    face(c, 50, 40, 42)
    c.E(70, 18, 76, 26, (190, 232, 250, 230))
    c.E(71, 19, 73, 22, (255, 255, 255, 220))


def emberling(c):
    body = (244, 158, 104)
    # signature: a real teardrop flame for hair — round bulb, curling tip
    def flame(cx, base, w, h, col):
        bulb = []
        for i in range(15):
            a = math.pi * i / 14
            bulb.append((cx + math.cos(a) * w, base - math.sin(a) * w * 0.9))
        tip = [(cx - w, base - w * 0.9 * 0),  # left rim
               (cx - w * 0.55, base - h * 0.45),
               (cx - w * 0.1, base - h * 0.62),
               (cx + w * 0.28, base - h),      # curled apex, off-center
               (cx + w * 0.5, base - h * 0.55),
               (cx + w, base)]
        c.P(bulb + [(cx - w * 0.55, base - h * 0.45),
                    (cx - w * 0.1, base - h * 0.62),
                    (cx + w * 0.28, base - h),
                    (cx + w * 0.5, base - h * 0.55)], col)
    shaded_ball(c, 50, 66, 23, body, 0.88)
    c.E(50 - 12, 60, 50 + 12, 80, (255, 214, 150, 255))
    shaded_ball(c, 50, 42, 29, body)
    flame(50, 18, 9, 24, INK)
    flame(50, 17.5, 7.6, 21, (255, 150, 52, 255))
    flame(50, 16.5, 4.8, 13, (255, 214, 110, 255))
    flame(50, 15.5, 2.4, 7, (255, 246, 200, 255))
    face(c, 50, 42, 40, mood="open")


def mossback(c):
    body = (158, 184, 122)
    shell = (92, 116, 70)
    # head peeking over a garden-dome shell; feet nubs below
    for sx in (-1, 1):
        c.E(50 + sx * 22 - 7, 82, 50 + sx * 22 + 7, 94, INK)
        c.E(50 + sx * 22 - 5.6, 83.4, 50 + sx * 22 + 5.6, 92.6, body + (255,))
    shaded_ball(c, 50, 36, 26, body)
    face(c, 50, 36, 37)
    # shell dome in front of the lower head
    c.E(18, 50, 82, 94, INK)
    c.E(20, 52, 80, 92, shell + (255,))
    c.A(26, 58, 74, 100, 190, 350, _light(shell, 0.22), 1.4)
    c.E(30, 58, 52, 70, _light(shell, 0.16))
    # tiny mushroom growing on the shell
    c.P([(63, 62), (67, 62), (67, 56), (63, 56)], (240, 228, 200, 255))
    c.E(58, 50, 72, 59, INK)
    c.E(59, 51, 71, 58, (216, 90, 82, 255))
    c.E(62, 52.5, 65.5, 55.5, (255, 255, 255, 235))


def bubbletide(c):
    body = (166, 218, 218)
    # signature: floats inside its own bubble
    c.E(8, 8, 92, 92, (170, 226, 236, 70))
    c.A(8, 8, 92, 92, 0, 360, (200, 240, 246, 160), 0.8)
    c.E(20, 16, 40, 34, (255, 255, 255, 90))
    shaded_ball(c, 50, 64, 20, body, 0.9)
    shaded_ball(c, 50, 42, 26, body)
    c.E(50 - 10, 58, 50 + 10, 76, (232, 250, 250, 255))
    face(c, 50, 42, 36)


def zephyrix(c):
    body = (248, 220, 124)
    wing = (255, 246, 222)
    # signature: scalloped cloud wings, low and behind
    for sx in (-1, 1):
        x = 50 + sx * 33
        for dx, dy, r in ((0, 0, 12), (sx * 9, 7, 9), (-sx * 6, 9, 8)):
            c.E(x + dx - r - OW * 0.6, 44 + dy - r - OW * 0.6,
                x + dx + r + OW * 0.6, 44 + dy + r + OW * 0.6, INK)
        for dx, dy, r in ((0, 0, 12), (sx * 9, 7, 9), (-sx * 6, 9, 8)):
            c.E(x + dx - r, 44 + dy - r, x + dx + r, 44 + dy + r, wing + (255,))
        c.E(x - 8, 36, x + 4, 46, (255, 255, 255, 255))
    # feather crest
    c.P([(46, 14), (50, 2), (54, 14)], INK)
    c.P([(47.5, 13), (50, 5), (52.5, 13)], (255, 178, 74, 255))
    shaded_ball(c, 50, 62, 22, body, 0.9)
    c.E(50 - 10, 56, 50 + 10, 74, (255, 244, 208, 255))
    shaded_ball(c, 50, 40, 28, body)
    face(c, 50, 38, 40, mood="beak", fang=False)


def cinderpup(c):
    body = (224, 128, 106)
    # signature: ember-tipped pup ears + soot nose
    for sx in ((-1), (1)):
        c.P([(50 + sx * 24, 26), (50 + sx * 34, 2), (50 + sx * 8, 18)], INK)
        c.P([(50 + sx * 22, 25), (50 + sx * 31, 6), (50 + sx * 10, 18)], body + (255,))
        c.E(50 + sx * 31 - 4, 2, 50 + sx * 31 + 4, 10, (255, 178, 74, 255))
    shaded_ball(c, 50, 66, 23, body, 0.88)
    c.E(50 - 12, 60, 50 + 12, 80, (255, 196, 150, 255))
    shaded_ball(c, 50, 42, 29, body)
    face(c, 50, 42, 40, mood="open")


def glimmerwing(c):
    body = (192, 160, 232)
    wing = (226, 204, 255)
    # signature: two soft wing lobes per side, gold spot in the big one
    for sx in (-1, 1):
        for wx, wy, rx, ry in ((36, 34, 17, 14), (32, 56, 12, 10)):
            x = 50 + sx * wx
            c.E(x - rx - OW * 0.6, wy - ry - OW * 0.6, x + rx + OW * 0.6,
                wy + ry + OW * 0.6, INK)
            c.E(x - rx, wy - ry, x + rx, wy + ry, wing + (255,))
        x = 50 + sx * 36
        c.E(x - 6, 28, x + 6, 40, (250, 216, 130, 235))
        c.E(x - 3.4, 30.5, x + 0.6, 34.5, (255, 240, 200, 255))
    shaded_ball(c, 50, 64, 21, body, 0.9)
    shaded_ball(c, 50, 42, 27, body)
    # antennae
    for sx in (-1, 1):
        c.L([(50 + sx * 8, 18), (50 + sx * 14, 6)], INK, 1.1)
        c.E(50 + sx * 14 - 2.6, 3, 50 + sx * 14 + 2.6, 8.5, (250, 216, 130, 255))
    face(c, 50, 42, 38)


def nocturnix(c):
    body = (112, 118, 170)
    belly = (168, 210, 245)
    # signature: crescent-moon chest + sleepy owl tufts (wide, soft)
    for sx in (-1, 1):
        c.P([(50 + sx * 26, 28), (50 + sx * 31, 4), (50 + sx * 6, 16)], INK)
        c.P([(50 + sx * 23, 26), (50 + sx * 28, 8), (50 + sx * 10, 17)], body + (255,))
        c.P([(50 + sx * 21, 24), (50 + sx * 25, 12), (50 + sx * 14, 18)],
            _light(body, 0.22))
    shaded_ball(c, 50, 64, 24, body, 0.9)
    shaded_ball(c, 50, 40, 29, body)
    c.E(50 - 13, 56, 50 + 13, 80, belly + (255,))
    # crescent
    c.E(44, 62, 58, 76, (250, 216, 130, 255))
    c.E(48, 61, 61, 74, body + (255,))
    face(c, 50, 40, 42, eyes_closed=True)
    # tiny beak
    c.P([(47, 50), (53, 50), (50, 55)], (255, 178, 74, 255))


DRAW = {
    "flufftail": flufftail, "pebblit": pebblit, "aquaphin": aquaphin,
    "emberling": emberling, "mossback": mossback, "bubbletide": bubbletide,
    "zephyrix": zephyrix, "cinderpup": cinderpup, "glimmerwing": glimmerwing,
    "nocturnix": nocturnix,
}

if __name__ == "__main__":
    import sys
    sheet = Image.new("RGBA", (5 * 320, 2 * 320), (250, 246, 238, 255))
    for i, sp in enumerate(DRAW):
        im = render(sp, 300)
        sheet.paste(im, (10 + (i % 5) * 320, 10 + (i // 5) * 320), im)
    out = sys.argv[1] if len(sys.argv) > 1 else "/tmp/critters2-sheet.png"
    sheet.save(out)
    print("sheet:", out)
