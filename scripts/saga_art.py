#!/usr/bin/env python3
"""Original illustrations for The Amah's Daughter (bookfactory6).

    python3 scripts/saga_art.py         # renders bookfactory6/art/chNN.png
    python3 scripts/saga_art.py cover   # renders dist/AmahsDaughter-cover.jpg

Style: two-tone "woodblock" vignettes — cream paper, indigo ink, one rust
or gold accent — inside a thin frame with Peranakan tile corners. All art
is parametric PIL drawing; nothing is sourced from photographs.
"""

import json
import math
import os
import sys

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BF = os.path.join(ROOT, "bookfactory6")
OUT = os.path.join(BF, "art")

CREAM = (245, 238, 220)
INDIGO = (31, 58, 95)
INK = (34, 40, 58)
RUST = (166, 75, 42)
GOLD = (201, 168, 76)
JADE = (78, 124, 89)

W, H = 1200, 760


def canvas():
    im = Image.new("RGB", (W, H), CREAM)
    d = ImageDraw.Draw(im)
    # paper grain
    for y in range(0, H, 7):
        d.line([(0, y), (W, y)], fill=(240, 232, 212), width=1)
    return im, d


def frame(d):
    d.rectangle([26, 26, W - 26, H - 26], outline=INDIGO, width=4)
    d.rectangle([38, 38, W - 38, H - 38], outline=INDIGO, width=2)
    # Peranakan tile corners
    for cx, cy in [(26, 26), (W - 26, 26), (26, H - 26), (W - 26, H - 26)]:
        d.rectangle([cx - 22, cy - 22, cx + 22, cy + 22], fill=CREAM, outline=INDIGO, width=3)
        for a in range(8):
            ang = a * math.pi / 4
            d.line([(cx, cy), (cx + 15 * math.cos(ang), cy + 15 * math.sin(ang))],
                   fill=RUST if a % 2 else INDIGO, width=3)
        d.ellipse([cx - 5, cy - 5, cx + 5, cy + 5], fill=GOLD)


def peony(d, cx, cy, r, col=RUST):
    for i in range(10):
        a = i * math.pi / 5
        d.ellipse([cx + 0.62 * r * math.cos(a) - 0.42 * r, cy + 0.62 * r * math.sin(a) - 0.42 * r,
                   cx + 0.62 * r * math.cos(a) + 0.42 * r, cy + 0.62 * r * math.sin(a) + 0.42 * r],
                  outline=col, width=3)
    d.ellipse([cx - 0.3 * r, cy - 0.3 * r, cx + 0.3 * r, cy + 0.3 * r], fill=col)
    d.ellipse([cx - 0.12 * r, cy - 0.12 * r, cx + 0.12 * r, cy + 0.12 * r], fill=GOLD)


def leaf(d, x, y, ln, ang, col=JADE):
    x2, y2 = x + ln * math.cos(ang), y + ln * math.sin(ang)
    mx, my = (x + x2) / 2, (y + y2) / 2
    px, py = -math.sin(ang) * ln * 0.22, math.cos(ang) * ln * 0.22
    d.polygon([(x, y), (mx + px, my + py), (x2, y2), (mx - px, my - py)], outline=col, width=3)
    d.line([(x, y), (x2, y2)], fill=col, width=2)


def shophouse_row(d, base, x0, x1, h1, col=INDIGO):
    """A row of shophouse facades between x0..x1 sitting on line `base`."""
    x = x0
    n = 0
    while x < x1 - 60:
        w = 120 + (n * 37) % 60
        top = base - h1 - (n * 29) % 46
        # pitched roof
        d.polygon([(x, top), (x + w // 2, top - 34), (x + w, top)], outline=col, width=4)
        d.rectangle([x, top, x + w, base], outline=col, width=4)
        # shutters
        for i in range(2):
            sx = x + 18 + i * (w // 2)
            d.rectangle([sx, top + 16, sx + w // 2 - 34, top + 60], outline=col, width=3)
            d.line([(sx, top + 38), (sx + w // 2 - 34, top + 38)], fill=col, width=2)
        # door with five-foot way column
        d.rectangle([x + w // 2 - 16, base - 56, x + w // 2 + 16, base], outline=col, width=3)
        d.line([(x + 6, base), (x + 6, base - 50)], fill=col, width=3)
        x += w + 8
        n += 1
    d.line([(x0 - 12, base), (x1 + 12, base)], fill=col, width=5)


def lantern(d, cx, cy, r, col=RUST):
    d.ellipse([cx - r, cy - r * 0.8, cx + r, cy + r * 0.8], outline=col, width=4)
    for i in (-1, 0, 1):
        d.arc([cx - r + 8 * abs(i), cy - r * 0.8, cx + r - 8 * abs(i), cy + r * 0.8],
              0, 360, fill=col, width=2)
    d.rectangle([cx - r * 0.4, cy - r * 0.8 - 12, cx + r * 0.4, cy - r * 0.8], outline=col, width=3)
    d.rectangle([cx - r * 0.4, cy + r * 0.8, cx + r * 0.4, cy + r * 0.8 + 10], outline=col, width=3)
    for i in range(4):
        d.line([(cx - r * 0.25 + i * r * 0.17, cy + r * 0.8 + 10),
                (cx - r * 0.25 + i * r * 0.17, cy + r * 0.8 + 34)], fill=GOLD, width=2)
    d.line([(cx, cy - r * 0.8 - 30), (cx, cy - r * 0.8 - 12)], fill=INK, width=2)


def slipper_shape(d, cx, cy, scale=1.0, col=INDIGO, beads=True):
    """A kasut manek slipper seen from above, toe left: two joined circles."""
    s = scale
    tx, tr = cx - 105 * s, 62 * s   # toe circle
    hx, hr = cx + 95 * s, 42 * s    # heel circle
    # sole outline: toe arc, tangent lines, heel arc
    d.arc([tx - tr, cy - tr, tx + tr, cy + tr], 95, 265, fill=col, width=4)
    d.arc([hx - hr, cy - hr, hx + hr, cy + hr], 275, 85, fill=col, width=4)
    d.line([(tx - 6 * s, cy - tr), (hx + 4 * s, cy - hr)], fill=col, width=4)
    d.line([(tx - 6 * s, cy + tr), (hx + 4 * s, cy + hr)], fill=col, width=4)
    # vamp band across the toe
    d.arc([tx - tr * 0.6, cy - tr * 1.35, tx + tr * 1.9, cy + tr * 1.35], 118, 242, fill=col, width=4)
    if beads:
        for i in range(40):
            bx = tx - tr * 0.7 + (i * 53) % int(tr * 1.5)
            by = cy - tr * 0.62 + ((i * 37) % int(tr * 1.24))
            if (bx - tx) ** 2 + (by - cy) ** 2 < (tr * 0.82) ** 2:
                d.ellipse([bx - 4, by - 4, bx + 4, by + 4],
                          fill=[RUST, GOLD, JADE][i % 3])
    peony(d, tx, cy, 24 * s, RUST)


def rain(d, x0, x1, y0, y1, step=34, col=INDIGO):
    for x in range(x0, x1, step):
        for y in range(y0, y1, 46):
            d.line([(x + (y % 17), y), (x - 8 + (y % 17), y + 26)], fill=col, width=2)


def bird(d, cx, cy, s=1.0, col=INK):
    d.ellipse([cx - 26 * s, cy - 14 * s, cx + 26 * s, cy + 14 * s], outline=col, width=3)
    d.ellipse([cx + 16 * s, cy - 26 * s, cx + 40 * s, cy - 4 * s], outline=col, width=3)
    d.polygon([(cx + 40 * s, cy - 15 * s), (cx + 54 * s, cy - 12 * s), (cx + 40 * s, cy - 9 * s)],
              fill=RUST)
    d.line([(cx - 26 * s, cy), (cx - 48 * s, cy - 10 * s)], fill=col, width=3)
    d.ellipse([cx + 24 * s, cy - 20 * s, cx + 29 * s, cy - 15 * s], fill=col)


def cage(d, cx, cy, r, col=INDIGO, door_open=False):
    d.arc([cx - r, cy - r, cx + r, cy + r], 180, 360, fill=col, width=4)
    for i in range(7):
        x = cx - r + i * (2 * r / 6)
        d.line([(x, cy - math.sqrt(max(r * r - (x - cx) ** 2, 0))), (x, cy + r * 0.75)], fill=col, width=3)
    d.line([(cx - r, cy + r * 0.75), (cx + r, cy + r * 0.75)], fill=col, width=4)
    d.line([(cx, cy - r), (cx, cy - r - 34)], fill=col, width=3)
    if door_open:
        d.rectangle([cx + r * 0.25, cy - 10, cx + r * 0.8, cy + r * 0.72], fill=CREAM)
        d.line([(cx + r * 0.25, cy - 10), (cx + r * 0.95, cy - 46)], fill=col, width=3)


def envelope(d, cx, cy, w, h, col=INDIGO):
    d.rectangle([cx - w // 2, cy - h // 2, cx + w // 2, cy + h // 2], outline=col, width=3)
    d.line([(cx - w // 2, cy - h // 2), (cx, cy + 4)], fill=col, width=3)
    d.line([(cx + w // 2, cy - h // 2), (cx, cy + 4)], fill=col, width=3)


def script_lines(d, x0, x1, y, n, col=INK):
    for i in range(n):
        yy = y + i * 22
        d.line([(x0, yy), (x1 - (i * 43) % 90, yy)], fill=col, width=2)


def tin_box(d, cx, cy, s=1.0):
    w, h = 320 * s, 150 * s
    d.rectangle([cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2], outline=INDIGO, width=5)
    d.rectangle([cx - w / 2, cy - h / 2 - 26 * s, cx + w / 2, cy - h / 2], outline=INDIGO, width=4)
    d.rectangle([cx - w / 2 + 14, cy - h / 2 + 14, cx + w / 2 - 14, cy + h / 2 - 14], outline=GOLD, width=2)
    peony(d, cx, cy + 6 * s, 40 * s, RUST)
    leaf(d, cx - 60 * s, cy + 22 * s, 52 * s, 2.6, JADE)
    leaf(d, cx + 60 * s, cy + 22 * s, 52 * s, 0.5, JADE)


# ---------------- per-chapter compositions ----------------

def a_tin(d):
    tin_box(d, W // 2, 350, 1.25)
    thread = [(W // 2 - 240, 560)]
    for i in range(1, 40):
        thread.append((W // 2 - 240 + i * 12, 560 + 26 * math.sin(i / 3.2)))
    d.line(thread, fill=RUST, width=4)
    envelope(d, W // 2 - 250, 620, 150, 88)
    d.ellipse([W // 2 + 190, 590, W // 2 + 240, 640], outline=JADE, width=5)  # jade ring
    rain(d, 70, 300, 70, 210)
    rain(d, W - 300, W - 70, 70, 210)

def a_gate(d):
    shophouse_row(d, 600, 90, W - 90, 300)
    # two small figures with case
    for fx, s in [(430, 1.0), (505, 0.72)]:
        d.ellipse([fx - 14 * s, 452 - 90 * s, fx + 14 * s, 480 - 90 * s], outline=INK, width=3)
        d.polygon([(fx - 24 * s, 600), (fx + 24 * s, 600), (fx + 15 * s, 484 - 8 * s), (fx - 15 * s, 484 - 8 * s)], outline=INK, width=3)
    d.rectangle([545, 560, 620, 600], outline=RUST, width=4)  # rattan case
    d.line([(560, 560), (560, 600)], fill=RUST, width=2)
    d.line([(600, 560), (600, 600)], fill=RUST, width=2)

def a_kitchen(d):
    # mortar and pestle, kueh tiers, pandan
    d.ellipse([250, 430, 470, 560], outline=INDIGO, width=5)
    d.rectangle([250, 495, 470, 560], outline=INDIGO, width=5)
    d.line([(430, 300), (350, 470)], fill=RUST, width=10)
    for i in range(3):
        y = 560 - i * 64
        d.rectangle([620 + i * 26, y - 54, 940 - i * 26, y], outline=INDIGO, width=4)
    peony(d, 780, 400, 34, RUST)
    for i in range(4):
        leaf(d, 150 + i * 18, 620, 130, -1.35 + i * 0.16, JADE)

def a_letters_school(d):
    d.rectangle([300, 250, 900, 560], outline=INDIGO, width=5)  # slate
    script_lines(d, 340, 860, 300, 5, CREAM if INDIGO == INK else INK)
    for i in range(5):
        d.line([(340, 300 + i * 44), (860 - (i * 61) % 130, 300 + i * 44)], fill=GOLD, width=3)
    d.line([(250, 620), (950, 620)], fill=INDIGO, width=5)
    d.polygon([(905, 585), (955, 570), (960, 585)], fill=RUST)  # pen nib
    d.rectangle([760, 566, 905, 585], outline=RUST, width=3)

def a_birdcage(d):
    cage(d, W // 2, 330, 190)
    bird(d, W // 2 - 20, 330, 1.1)
    lantern(d, 220, 260, 60)
    lantern(d, W - 220, 260, 60)
    script_lines(d, 380, 820, 600, 3)

def a_monsoon(d):
    rain(d, 80, W - 80, 80, 420, step=26)
    shophouse_row(d, 620, 90, W - 90, 220)
    d.arc([80, 560, W - 80, 760], 180, 360, fill=INDIGO, width=4)  # flood water
    for x in range(140, W - 120, 90):
        d.arc([x, 596, x + 70, 640], 180, 360, fill=INDIGO, width=3)

def a_temple(d):
    # temple roof with upswept eaves
    d.polygon([(200, 330), (W - 200, 330), (W - 150, 380), (150, 380)], outline=RUST, width=5)
    d.arc([90, 220, 420, 400], 250, 355, fill=RUST, width=6)
    d.arc([W - 420, 220, W - 90, 400], 185, 290, fill=RUST, width=6)
    d.rectangle([260, 380, W - 260, 620], outline=INDIGO, width=5)
    for i in range(3):
        d.line([(340 + i * 180, 380), (340 + i * 180, 620)], fill=INDIGO, width=4)
    # joss smoke
    for i, x in enumerate([520, 600, 680]):
        pts = [(x, 610)]
        for t in range(1, 16):
            pts.append((x + 18 * math.sin(t / 2 + i), 610 - t * 14))
        d.line(pts, fill=INK, width=2)

def a_slipper(d):
    slipper_shape(d, W // 2, 380, 1.5)
    for i in range(30):
        d.ellipse([120 + i * 34 - 3, 620 - 3, 120 + i * 34 + 3, 620 + 3],
                  fill=[RUST, GOLD, JADE, INDIGO][i % 4])
    d.line([(140, 660), (W - 140, 660)], fill=INK, width=2)  # thread

def a_photo(d):
    d.rectangle([360, 160, 840, 620], outline=INDIGO, width=6)
    d.rectangle([390, 190, 810, 560], outline=INK, width=3)
    # groom figure
    d.ellipse([520 - 26, 250, 520 + 26, 302], outline=INK, width=3)
    d.rectangle([480, 302, 560, 470], outline=INK, width=3)
    # folded-out bride: fold line + blank
    d.polygon([(640, 190), (810, 190), (810, 560), (640, 560)], fill=CREAM)
    d.line([(640, 190), (640, 560)], fill=INDIGO, width=4)
    d.polygon([(640, 190), (700, 240), (640, 300)], outline=INDIGO, width=3)
    script_lines(d, 400, 700, 590, 1)

def a_wedding(d):
    lantern(d, 260, 240, 70)
    lantern(d, W - 260, 240, 70)
    lantern(d, W // 2, 200, 88)
    # double-happiness-ish knot (abstract)
    for dx in (-70, 70):
        d.rectangle([W // 2 + dx - 44, 380, W // 2 + dx + 44, 520], outline=RUST, width=5)
        d.line([(W // 2 + dx - 44, 430), (W // 2 + dx + 44, 430)], fill=RUST, width=4)
        d.line([(W // 2 + dx, 380), (W // 2 + dx, 520)], fill=RUST, width=4)
    slipper_shape(d, W // 2 - 170, 620, 0.62)
    slipper_shape(d, W // 2 + 220, 620, 0.62)

def a_teacups(d):
    for i, cx in enumerate([400, 800]):
        d.arc([cx - 90, 380, cx + 90, 520], 0, 180, fill=INDIGO, width=5)
        d.line([(cx - 90, 450), (cx + 90, 450)], fill=INDIGO, width=5)
        d.ellipse([cx - 100, 508, cx + 100, 540], outline=INDIGO, width=4)
        for t in range(3):
            pts = [(cx - 20 + t * 20, 440)]
            for k in range(1, 10):
                pts.append((cx - 20 + t * 20 + 10 * math.sin(k / 1.6 + t), 440 - k * 16))
            d.line(pts, fill=INK, width=2)
    d.line([(W // 2, 300), (W // 2, 620)], fill=RUST, width=3)  # the divide

def a_harbour(d):
    d.line([(80, 520), (W - 80, 520)], fill=INDIGO, width=4)
    for x in range(120, W - 100, 70):
        d.arc([x, 530, x + 56, 560], 180, 360, fill=INDIGO, width=3)
    # steamer
    d.polygon([(380, 520), (820, 520), (770, 430), (430, 430)], outline=INK, width=4)
    d.rectangle([540, 360, 660, 430], outline=INK, width=4)
    d.rectangle([580, 300, 620, 360], outline=RUST, width=4)
    pts = [(600, 290)]
    for t in range(1, 12):
        pts.append((600 + t * 16, 290 - t * 9 - 8 * math.sin(t)))
    d.line(pts, fill=INK, width=3)
    # crates
    for i in range(4):
        d.rectangle([120 + i * 56, 468, 168 + i * 56, 516], outline=RUST, width=3)

def a_blackout(d):
    shophouse_row(d, 560, 90, W - 90, 230)
    # crossed tape on windows
    for x in range(150, W - 150, 210):
        d.line([(x, 350), (x + 66, 410)], fill=RUST, width=4)
        d.line([(x + 66, 350), (x, 410)], fill=RUST, width=4)
    # searchlights
    d.polygon([(200, 560), (60, 90), (150, 90)], outline=INK, width=2)
    d.polygon([(W - 200, 560), (W - 60, 90), (W - 150, 90)], outline=INK, width=2)
    d.rectangle([420, 610, 780, 660], outline=INK, width=4)
    script_lines(d, 440, 760, 622, 2)

def a_redthread(d):
    # bundle: letter, lock of hair, tiny slipper, tied in red thread
    envelope(d, 420, 340, 240, 150)
    slipper_shape(d, 800, 360, 0.5)
    pts = []
    for t in range(120):
        a = t / 8
        pts.append((W // 2 + (250 - t * 1.6) * math.cos(a) * 0.35, 560 + 16 * math.sin(a)))
    d.line(pts, fill=RUST, width=4)
    d.arc([560, 260, 660, 360], 0, 300, fill=INK, width=4)  # lock of hair
    d.arc([580, 280, 680, 380], 20, 320, fill=INK, width=3)

def a_altar(d):
    d.rectangle([300, 300, 900, 340], outline=RUST, width=5)   # altar beam
    d.rectangle([340, 340, 860, 620], outline=RUST, width=5)
    d.line([(340, 480), (860, 480)], fill=RUST, width=4)
    # Guan Yin silhouette (abstract seated figure)
    d.ellipse([575, 360, 625, 410], outline=INDIGO, width=4)
    d.arc([540, 390, 660, 500], 180, 360, fill=INDIGO, width=4)
    d.line([(540, 445), (660, 445)], fill=INDIGO, width=4)
    for cx in (450, 750):
        d.line([(cx, 400), (cx, 445)], fill=INK, width=3)
        pts = [(cx, 396)]
        for t in range(1, 10):
            pts.append((cx + 10 * math.sin(t / 1.4), 396 - t * 13))
        d.line(pts, fill=INK, width=2)
    for i, cx in enumerate([520, 600, 680]):
        d.arc([cx - 26, 520, cx + 26, 552], 0, 180, fill=GOLD, width=4)
        d.line([(cx - 26, 536), (cx + 26, 536)], fill=GOLD, width=3)

def a_padang(d):
    # empty field, one fallen pen in foreground; queue as distant marks
    d.line([(90, 520), (W - 90, 520)], fill=INDIGO, width=4)
    for i in range(24):
        x = 150 + i * 40
        d.line([(x, 500), (x, 470 - (i % 3) * 6)], fill=INK, width=4)
        d.ellipse([x - 5, 456 - (i % 3) * 6, x + 5, 468 - (i % 3) * 6], outline=INK, width=3)
    d.rectangle([460, 600, 700, 622], outline=RUST, width=4)
    d.polygon([(700, 600), (750, 611), (700, 622)], fill=RUST)  # the fountain pen
    rain(d, 90, W - 90, 90, 300, step=48)

def a_lamplight(d):
    d.line([(W // 2, 120), (W // 2, 260)], fill=INK, width=3)
    d.arc([W // 2 - 110, 230, W // 2 + 110, 380], 200, 340, fill=GOLD, width=6)
    d.ellipse([W // 2 - 30, 280, W // 2 + 30, 350], outline=RUST, width=4)
    for i in range(3):
        envelope(d, 380 + i * 220, 560, 190, 116)
    script_lines(d, 300, 890, 650, 2)

def a_ration(d):
    # ration queue bowls and a sack
    for i in range(5):
        cx = 220 + i * 190
        d.arc([cx - 70, 420, cx + 70, 520], 0, 180, fill=INDIGO, width=5)
        d.line([(cx - 70, 470), (cx + 70, 470)], fill=INDIGO, width=5)
    d.polygon([(480, 620), (720, 620), (690, 500), (510, 500)], outline=RUST, width=4)
    d.line([(510, 540), (690, 540)], fill=RUST, width=3)
    for i in range(8):
        d.ellipse([530 + i * 18, 560 - 2, 536 + i * 18, 564], fill=INK)

def a_cradles(d):
    for i, cx in enumerate([380, 820]):
        d.arc([cx - 150, 360, cx + 150, 560], 0, 180, fill=INDIGO if i == 0 else RUST, width=5)
        d.line([(cx - 150, 460), (cx + 150, 460)], fill=INDIGO if i == 0 else RUST, width=5)
        d.arc([cx - 170, 520, cx + 170, 600], 180, 360, fill=INDIGO if i == 0 else RUST, width=4)
    d.line([(W // 2, 300), (W // 2, 620)], fill=INK, width=2)
    peony(d, W // 2, 250, 36, GOLD)

def a_exchange(d):
    # two pairs of hands passing a swaddled bundle (abstract)
    d.arc([260, 300, 620, 560], 300, 90, fill=INDIGO, width=5)
    d.arc([580, 300, 940, 560], 90, 240, fill=RUST, width=5)
    d.ellipse([520, 360, 680, 470], outline=INK, width=4)
    d.arc([540, 380, 660, 450], 200, 340, fill=INK, width=3)
    d.ellipse([575, 388, 600, 412], outline=INK, width=3)
    script_lines(d, 420, 780, 600, 2)

def a_amah(d):
    # black-and-white amah figure: white blouse, black trousers, plait
    d.ellipse([W // 2 - 34, 200, W // 2 + 34, 268], outline=INK, width=4)
    pts = [(W // 2 + 30, 250)]
    for t in range(1, 14):
        pts.append((W // 2 + 30 + 8 * math.sin(t / 1.3), 250 + t * 22))
    d.line(pts, fill=INK, width=4)  # plait
    d.polygon([(W // 2 - 80, 270), (W // 2 + 80, 270), (W // 2 + 96, 440), (W // 2 - 96, 440)],
              outline=INK, width=4)  # white blouse
    d.polygon([(W // 2 - 96, 440), (W // 2 + 96, 440), (W // 2 + 80, 640), (W // 2 - 80, 640)],
              fill=INDIGO)  # black trousers
    d.line([(W // 2 - 80, 350), (W // 2 - 150, 430)], fill=INK, width=4)
    d.line([(W // 2 + 80, 350), (W // 2 + 170, 400)], fill=INK, width=4)
    bird(d, W // 2 + 220, 380, 0.8)

def a_gramophone(d):
    d.polygon([(430, 560), (720, 560), (700, 480), (450, 480)], outline=INDIGO, width=4)
    d.ellipse([500, 500, 650, 545], outline=INDIGO, width=3)
    # horn
    pts = []
    for t in range(40):
        a = 3.6 - t / 16
        r = 30 + t * 5.4
        pts.append((640 + r * math.cos(a) * 0.5, 470 - t * 4.4))
    d.line(pts, fill=RUST, width=5)
    d.arc([690, 160, 950, 330], 300, 120, fill=RUST, width=5)
    for i in range(6):
        d.ellipse([230 - i, 420 - i * 26, 330 + i, 448 - i * 26], outline=INK, width=3)  # records

def a_tapioca(d):
    for i in range(3):
        x = 300 + i * 220
        pts = [(x, 560)]
        for t in range(1, 12):
            pts.append((x + 14 * math.sin(t / 1.5 + i), 560 - t * 30))
        d.line(pts, fill=JADE, width=4)
        for t in range(3, 12, 2):
            leaf(d, x + 14 * math.sin(t / 1.5 + i), 560 - t * 30, 66, -0.9 + (t % 4) * 0.5, JADE)
    d.polygon([(340, 620), (420, 590), (560, 596), (700, 588), (820, 620)], outline=RUST, width=4)  # roots

def a_twoflags(d):
    for i, x in enumerate([340, 760]):
        d.line([(x, 200), (x, 620)], fill=INK, width=5)
        wave = [(x, 220)]
        for t in range(1, 22):
            wave.append((x + t * 10, 220 + 10 * math.sin(t / 2 + i * 2)))
        wave += [(x + 210, 320), (x, 320)]
        d.polygon(wave, outline=RUST if i == 0 else INDIGO, width=4)
    d.line([(90, 620), (W - 90, 620)], fill=INDIGO, width=4)

def a_niche(d):
    d.rectangle([420, 220, 780, 600], outline=INDIGO, width=6)
    for y in range(250, 600, 44):
        for x in range(430, 770, 84):
            d.rectangle([x + (y // 44 % 2) * 40, y, x + 74 + (y // 44 % 2) * 40, y + 34], outline=INK, width=2)
    d.rectangle([510, 330, 690, 490], fill=CREAM, outline=RUST, width=5)
    tin_box(d, 600, 420, 0.42)

def a_rebuilding(d):
    shophouse_row(d, 600, 90, 640, 260)
    # scaffolding on right half
    for x in range(660, W - 100, 80):
        d.line([(x, 600), (x, 300)], fill=RUST, width=3)
    for y in range(320, 600, 70):
        d.line([(660, y), (W - 100, y)], fill=RUST, width=3)
    d.polygon([(700, 300), (W - 120, 300), (W - 160, 250), (740, 250)], outline=INDIGO, width=3)

def a_kueh(d):
    # tiered kueh tray
    for i in range(3):
        y = 560 - i * 90
        w = 340 - i * 70
        d.rectangle([W // 2 - w, y - 64, W // 2 + w, y], outline=INDIGO, width=4)
        for k in range(4 + (2 - i)):
            kx = W // 2 - w + 40 + k * (2 * w - 60) // (3 + (2 - i))
            d.rectangle([kx, y - 48, kx + 46, y - 14], outline=[RUST, JADE, GOLD][k % 3], width=3)
    d.line([(W // 2, 240), (W // 2, 290)], fill=INK, width=3)
    d.ellipse([W // 2 - 8, 232, W // 2 + 8, 248], outline=INK, width=3)

def a_deed(d):
    d.rectangle([380, 200, 820, 600], outline=INDIGO, width=5)
    script_lines(d, 420, 780, 250, 9)
    d.ellipse([700, 490, 780, 570], outline=RUST, width=4)
    d.ellipse([716, 506, 764, 554], outline=RUST, width=3)  # seal
    d.line([(380, 460), (820, 460)], fill=GOLD, width=3)
    slipper_shape(d, 260, 640, 0.36)

def a_shopfront(d):
    shophouse_row(d, 620, 340, 860, 320)
    # signboard
    d.rectangle([430, 330, 770, 390], outline=RUST, width=5)
    peony(d, 470, 360, 20, RUST)
    peony(d, 730, 360, 20, RUST)
    slipper_shape(d, 600, 520, 0.55)
    lantern(d, 380, 300, 44)
    lantern(d, 820, 300, 44)

def a_merdeka(d):
    d.line([(W // 2, 160), (W // 2, 640)], fill=INK, width=6)
    wave = [(W // 2, 180)]
    for t in range(1, 30):
        wave.append((W // 2 + t * 11, 180 + 12 * math.sin(t / 2.4)))
    wave += [(W // 2 + 320, 330), (W // 2, 330)]
    d.polygon(wave, outline=RUST, width=5)
    d.ellipse([W // 2 + 40, 210, W // 2 + 110, 280], outline=GOLD, width=4)
    for i in range(11):
        a = i * math.pi / 5.5
        d.line([(W // 2 + 75 + 28 * math.cos(a), 245 + 28 * math.sin(a)),
                (W // 2 + 75 + 42 * math.cos(a), 245 + 42 * math.sin(a))], fill=GOLD, width=3)
    # fireworks
    for cx, cy in [(260, 240), (300, 420), (200, 540)]:
        for i in range(10):
            a = i * math.pi / 5
            d.line([(cx + 14 * math.cos(a), cy + 14 * math.sin(a)),
                    (cx + 52 * math.cos(a), cy + 52 * math.sin(a))], fill=[RUST, GOLD][i % 2], width=3)

def a_tworooms(d):
    # two lit windows in night facade
    d.rectangle([200, 200, W - 200, 620], outline=INDIGO, width=5)
    d.line([(W // 2, 200), (W // 2, 620)], fill=INDIGO, width=4)
    for i, x in enumerate([330, 790]):
        d.rectangle([x, 300, x + 180, 470], outline=INDIGO, width=4)
        if i == 0:
            d.rectangle([x + 8, 308, x + 172, 462], fill=(252, 242, 200))
            d.line([(x + 90, 308), (x + 90, 462)], fill=INDIGO, width=3)
    tin_box(d, 420, 560, 0.3)

def a_watch(d):
    # pocket watch and letters spanning decades
    d.ellipse([440, 240, 760, 560], outline=INDIGO, width=6)
    d.ellipse([470, 270, 730, 530], outline=INDIGO, width=3)
    d.line([(600, 400), (600, 300)], fill=RUST, width=4)
    d.line([(600, 400), (680, 430)], fill=RUST, width=4)
    d.rectangle([580, 210, 620, 240], outline=INDIGO, width=4)
    for i in range(4):
        envelope(d, 240 + i * 240, 650, 120, 70)

def a_grave(d):
    # omega-shaped Bukit Cina grave, tea cup, frangipani
    d.arc([380, 260, 820, 620], 180, 360, fill=INDIGO, width=6)
    d.line([(380, 440), (330, 560)], fill=INDIGO, width=5)
    d.line([(820, 440), (870, 560)], fill=INDIGO, width=5)
    d.rectangle([540, 370, 660, 480], outline=INK, width=4)
    script_lines(d, 556, 646, 390, 4)
    d.arc([560, 520, 640, 570], 0, 180, fill=GOLD, width=4)
    d.line([(560, 545), (640, 545)], fill=GOLD, width=3)
    for i in range(5):
        a = i * math.pi * 2 / 5 - math.pi / 2
        d.ellipse([260 + 30 * math.cos(a) - 14, 300 + 30 * math.sin(a) - 14,
                   260 + 30 * math.cos(a) + 14, 300 + 30 * math.sin(a) + 14], outline=RUST, width=3)
    d.ellipse([252, 292, 268, 308], fill=GOLD)

def a_meeting(d):
    d.ellipse([300, 300, 900, 560], outline=INDIGO, width=5)  # table
    for i in range(8):
        a = i * math.pi / 4
        cx, cy = 600 + 340 * math.cos(a) * 0.95, 430 + 180 * math.sin(a) * 1.15
        d.ellipse([cx - 22, cy - 22, cx + 22, cy + 22], outline=INK, width=3)
    d.rectangle([540, 390, 660, 470], outline=RUST, width=4)  # documents at center
    script_lines(d, 552, 648, 404, 3)

def a_restoration(d):
    shophouse_row(d, 600, 200, 620, 300)
    # drawing board overlay
    d.rectangle([640, 240, W - 120, 560], outline=RUST, width=4)
    d.line([(640, 320), (W - 120, 320)], fill=RUST, width=2)
    d.line([(640, 420), (W - 120, 420)], fill=RUST, width=2)
    d.line([(760, 240), (760, 560)], fill=RUST, width=2)
    d.polygon([(660, 540), (700, 500), (708, 508), (668, 548)], fill=INDIGO)  # pencil
    cage(d, 300, 300, 90, door_open=True)
    bird(d, 470, 210, 0.8)

def a_epilogue(d):
    cage(d, W // 2, 340, 170, door_open=True)
    bird(d, W // 2 + 260, 240, 1.0)
    slipper_shape(d, W // 2 - 200, 600, 0.5)
    slipper_shape(d, W // 2 + 200, 600, 0.5)
    tin_box(d, W // 2, 590, 0.28)

ART = {
    "tin": a_tin, "gate": a_gate, "kitchen": a_kitchen, "letters_school": a_letters_school,
    "birdcage": a_birdcage, "monsoon": a_monsoon, "temple": a_temple, "slipper": a_slipper,
    "photo": a_photo, "wedding": a_wedding, "teacups": a_teacups, "harbour": a_harbour,
    "blackout": a_blackout, "redthread": a_redthread, "altar": a_altar, "padang": a_padang,
    "lamplight": a_lamplight, "ration": a_ration, "cradles": a_cradles, "exchange": a_exchange,
    "amah": a_amah, "gramophone": a_gramophone, "tapioca": a_tapioca, "twoflags": a_twoflags,
    "niche": a_niche, "rebuilding": a_rebuilding, "kueh": a_kueh, "deed": a_deed,
    "shopfront": a_shopfront, "merdeka": a_merdeka, "tworooms": a_tworooms, "watch": a_watch,
    "grave": a_grave, "meeting": a_meeting, "restoration": a_restoration, "epilogue": a_epilogue,
}


def font(size, bold=False):
    cands = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSerif%s.ttf" % ("-Bold" if bold else ""),
        "/usr/share/fonts/truetype/liberation/LiberationSerif-%s.ttf" % ("Bold" if bold else "Regular"),
    ]
    for c in cands:
        if os.path.exists(c):
            return ImageFont.truetype(c, size)
    return ImageFont.load_default()


def _title_font(size, bold=True):
    """Cover type: prefer Liberation Serif (Times-like) over DejaVu's slab."""
    cands = [
        "/usr/share/fonts/truetype/liberation/LiberationSerif-%s.ttf" % ("Bold" if bold else "Regular"),
        "/usr/share/fonts/truetype/dejavu/DejaVuSerif%s.ttf" % ("-Bold" if bold else ""),
    ]
    for c in cands:
        if os.path.exists(c):
            return ImageFont.truetype(c, size)
    return ImageFont.load_default()


def _tracked(d, text, font, cx, y, fill, track=0):
    """Draw text centred on cx with extra letter-spacing."""
    widths = [d.textlength(ch, font=font) for ch in text]
    total = sum(widths) + track * (len(text) - 1)
    x = cx - total / 2
    for ch, w in zip(text, widths):
        d.text((x, y), ch, font=font, fill=fill)
        x += w + track
    return total


def _lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


SOLE_PROFILE = [
    (0.00, 0.00), (0.04, 0.30), (0.10, 0.42), (0.18, 0.485), (0.28, 0.50),
    (0.40, 0.455), (0.52, 0.395), (0.62, 0.368), (0.72, 0.385),
    (0.82, 0.425), (0.90, 0.415), (0.96, 0.30), (1.00, 0.00),
]


def _sole_half(t):
    """Half-width of the slipper sole at depth t (0 = toe, 1 = heel)."""
    if t <= 0.0 or t >= 1.0:
        return 0.0
    for i in range(len(SOLE_PROFILE) - 1):
        t0, h0 = SOLE_PROFILE[i]
        t1, h1 = SOLE_PROFILE[i + 1]
        if t0 <= t <= t1:
            k = (t - t0) / (t1 - t0)
            k = k * k * (3 - 2 * k)              # smoothstep, so no facets
            return h0 + (h1 - h0) * k
    return 0.0


VAMP_T0, VAMP_T1 = 0.010, 0.455


def _vamp_back(u_rel):
    """Depth of the vamp's opening edge: a shallow arc, deepest at centre."""
    return VAMP_T1 + 0.085 * (1.0 - u_rel * u_rel)


def _bead_colour(u_rel, s):
    """Colour of one bead. u_rel is -1..1 across the panel, s is 0..1 deep.

    The pattern is the book's 'Malacca pattern': a peony head in rust and
    gold on a field of white beads, jade leaves below it, an indigo border.
    """
    au = abs(u_rel)
    if au > 0.985 or s > 0.975 or s < 0.02:
        return (24, 40, 68)                      # indigo border row
    if au > 0.90 or s > 0.94 or s < 0.055:
        return (198, 164, 74)                    # gold piping

    px, py = u_rel * 0.46, (s - 0.50) * 0.92
    r = math.hypot(px, py)
    if r < 0.052:
        return (234, 198, 98)                    # gold centre
    if r < 0.082:
        return (166, 75, 42)
    if r < 0.225:
        petal = math.cos(5 * math.atan2(py, px))
        if petal > 0.25:
            return (208, 106, 74)                # lit petal
        if petal > -0.35:
            return (162, 72, 40)                 # shadowed petal
        return (236, 226, 206)

    for sx in (-1, 1):
        lx, ly = px - sx * 0.30, py - 0.20
        ang = sx * 0.85
        rx = lx * math.cos(ang) - ly * math.sin(ang)
        ry = lx * math.sin(ang) + ly * math.cos(ang)
        if (rx / 0.055) ** 2 + (ry / 0.175) ** 2 < 1.0:
            return (78, 124, 89) if abs(rx) > 0.018 else (110, 156, 118)

    if s > 0.70 and au < 0.035:
        return (198, 164, 74)                    # tendril down the centre

    return (238, 229, 210)                       # white bead field


def _draw_slipper(im, cx, cy, length, width, angle=14.0):
    """One kasut manek seen from above: leather sole, beaded toe panel."""
    pad = 90
    TW, TH = int(width + pad * 2), int(length + pad * 2)
    tile = Image.new("RGBA", (TW, TH), (0, 0, 0, 0))
    d = ImageDraw.Draw(tile)
    tcx, y0 = TW / 2.0, float(pad)

    def pt(t, side):
        return (tcx + side * _sole_half(t) * width, y0 + t * length)

    outline = [pt(i / 200.0, 1) for i in range(201)]
    outline += [pt(1 - i / 200.0, -1) for i in range(201)]

    d.polygon(outline, fill=(44, 33, 27, 255))
    d.line(outline + [outline[0]], fill=(178, 144, 72, 255), width=5, joint="curve")
    inner = [(tcx + (x - tcx) * 0.87, y0 + (y - y0) * 0.965 + length * 0.016)
             for x, y in outline]
    d.line(inner + [inner[0]], fill=(116, 92, 50, 255), width=2, joint="curve")

    # the dark crescent where the foot goes in — the cue that says "shoe"
    ob = [(tcx + u * _sole_half(_vamp_back(u)) * width * 0.95,
           y0 + _vamp_back(u) * length)
          for u in [i / 40.0 * 2 - 1 for i in range(41)]]
    ob += [(tcx + u * _sole_half(_vamp_back(u)) * width * 0.95,
            y0 + (_vamp_back(u) + 0.055) * length)
           for u in [1 - i / 40.0 * 2 for i in range(41)]]
    d.polygon(ob, fill=(26, 18, 14, 255))

    # the beaded toe panel
    step = 11.0
    row = 0
    t = VAMP_T0
    while t < VAMP_T1 + 0.10:
        y = y0 + t * length
        half = _sole_half(t) * width * 0.955
        if half > step * 0.55:
            offset = (step / 2.0) if row % 2 else 0.0
            n = int(half * 2 / step) + 1
            for c in range(n):
                x = tcx - half + offset + c * step
                u_rel = (x - tcx) / half
                if abs(u_rel) > 1.0:
                    continue
                back = _vamp_back(u_rel)
                if t > back:
                    continue
                s = (t - VAMP_T0) / (back - VAMP_T0)
                col = _bead_colour(u_rel, s)
                if col is None:
                    continue
                r = 4.2
                d.ellipse([x - r, y - r, x + r, y + r], fill=col + (255,))
                d.ellipse([x - r * 0.7 - 0.8, y - r * 0.7 - 0.8,
                           x - r * 0.7 + 1.4, y - r * 0.7 + 1.4],
                          fill=_lerp(col, (255, 255, 255), 0.5) + (255,))
        t += step * 0.86 / length
        row += 1

    tile = tile.rotate(-angle, resample=Image.BICUBIC, expand=True)

    # soft ground shadow cast from the rotated silhouette
    sh = Image.new("L", im.size, 0)
    sh.paste(tile.split()[3], (int(cx - tile.width / 2) + 20,
                               int(cy - tile.height / 2) + 26))
    sh = sh.point(lambda v: int(v * 0.42))
    sh = sh.filter(ImageFilter.GaussianBlur(30))
    im.paste(Image.new("RGB", im.size, (6, 12, 24)), (0, 0), sh)

    im.paste(tile, (int(cx - tile.width / 2), int(cy - tile.height / 2)), tile)


def make_cover(path):
    CW, CH = 1600, 2560
    im = Image.new("RGB", (CW, CH), INDIGO)
    d = ImageDraw.Draw(im)

    # --- night sky: deep ink at the top, warmer indigo toward the horizon
    top, mid, bot = (11, 21, 40), (34, 62, 100), (17, 28, 50)
    horizon = 1700
    for y in range(CH):
        if y < horizon:
            col = _lerp(top, mid, (y / horizon) ** 0.85)
        else:
            col = _lerp(mid, bot, (y - horizon) / (CH - horizon))
        d.line([(0, y), (CW, y)], fill=col)

    # --- a scatter of faint stars, high and sparse
    for i in range(90):
        x, y = (i * 419) % CW, (i * 277) % 900
        s = 2 + (i % 3)
        d.ellipse([x, y, x + s, y + s], fill=(146, 164, 196))

    # --- warm lamp halo, composited through a soft mask so it has no edge
    gx, gy, gr = CW // 2, 1800, 980
    mask = Image.new("L", (CW, CH), 0)
    md = ImageDraw.Draw(mask)
    for i in range(gr, 0, -3):
        t = 1.0 - (i / gr)
        md.ellipse([gx - i, gy - i * 0.86, gx + i, gy + i * 0.86],
                   fill=int(255 * (t ** 2.4) * 0.62))
    mask = mask.filter(ImageFilter.GaussianBlur(40))
    im = Image.composite(Image.new("RGB", (CW, CH), (186, 118, 64)), im, mask)

    # --- the hero object
    _draw_slipper(im, CW // 2, 1772, 920, 352)

    d = ImageDraw.Draw(im)

    # --- title
    cx = CW // 2
    f_small = _title_font(76, bold=False)
    _tracked(d, "THE", f_small, cx, 440, (212, 198, 166), track=26)

    for i, word in enumerate(["AMAH\u2019S", "DAUGHTER"]):
        size = 238
        while size > 90:
            f_t = _title_font(size, bold=True)
            if d.textlength(word, font=f_t) + 6 * (len(word) - 1) <= CW - 300:
                break
            size -= 6
        _tracked(d, word, f_t, cx, 570 + i * 262, CREAM, track=6)

    # gold hairline + subtitle
    d.line([(cx - 250, 1152), (cx + 250, 1152)], fill=GOLD, width=3)
    sub = "A Novel of Secrets, Love, and War in Old Malaya"
    size = 60
    while size > 30:
        f_s = _title_font(size, bold=False)
        if d.textlength(sub, font=f_s) <= CW - 300:
            break
        size -= 2
    w = d.textlength(sub, font=f_s)
    d.text((cx - w / 2, 1200), sub, font=f_s, fill=(224, 210, 178))

    # --- author
    d.line([(cx - 330, 2300), (cx + 330, 2300)], fill=GOLD, width=3)
    f_a = _title_font(84, bold=True)
    _tracked(d, "TANG SHIUAN JENN", f_a, cx, 2340, CREAM, track=10)

    im.save(path, "JPEG", quality=94)
    print("cover ->", path)


def main():
    with open(os.path.join(BF, "plan.json")) as f:
        plan = json.load(f)
    os.makedirs(OUT, exist_ok=True)
    for part in plan["parts"]:
        for ch in part["chapters"]:
            fn = ART[ch["art"]]
            im, d = canvas()
            fn(d)
            frame(d)
            p = os.path.join(OUT, ch["id"] + ".png")
            im.save(p, optimize=True)
    print("rendered %d illustrations -> %s" % (
        sum(len(p["chapters"]) for p in plan["parts"]), OUT))


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "cover":
        os.makedirs(os.path.join(ROOT, "dist"), exist_ok=True)
        make_cover(os.path.join(ROOT, "dist", "AmahsDaughter-cover.jpg"))
    else:
        main()
