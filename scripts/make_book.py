#!/usr/bin/env python3
"""Illustrate and assemble 'Goodnight, Wildhaven' — 52-page edition.

Classic picture-book spreads: full-bleed illustration on the left page,
verse page on the right. Front matter, ten creature spreads, a dreams
section, and activity back matter. Print spec: 8.5 x 8.5 in at 300 dpi
(KDP square trim), 52 interior pages.

  dist/Goodnight-Wildhaven-Book.pdf
  book/pages/*.png

Run:  python3 scripts/make_book.py
"""

import os
import random

from PIL import Image, ImageDraw, ImageFont

S = 2550  # 8.5in * 300dpi, square
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAGES_DIR = os.path.join(ROOT, "book", "pages")

F_TITLE = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 210)
F_H = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 130)
F_TEXT = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 104)
F_SMALL = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 64)
F_NAME = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 72)

SKIES = {
    "day":    [(126, 200, 235), (200, 235, 250)],
    "sunset": [(90, 70, 120), (245, 170, 110)],
    "dusk":   [(40, 52, 92), (232, 168, 117)],
    "night":  [(12, 20, 44), (46, 62, 110)],
    "cream":  [(255, 250, 240), (250, 240, 224)],
    "lilac":  [(224, 214, 240), (244, 234, 248)],
}


def sky(d, kind):
    top, bot = SKIES[kind]
    for y in range(S):
        t = y / S
        c = tuple(int(top[i] + (bot[i] - top[i]) * t) for i in range(3))
        d.line([(0, y), (S, y)], fill=c)


def stars(d, n=140, ymax=0.6, big=False):
    for _ in range(n):
        x, y = random.randint(0, S), random.randint(0, int(S * ymax))
        r = random.choice([4, 6, 9] if big else [2, 3, 3, 4, 6])
        d.ellipse([x - r, y - r, x + r, y + r], fill=(255, 252, 230))


def star_shape(d, cx, cy, r, fill=(255, 226, 130)):
    import math
    pts = []
    for i in range(10):
        ang = math.pi / 2 + i * math.pi / 5
        rr = r if i % 2 == 0 else r * 0.45
        pts.append((cx + math.cos(ang) * rr, cy - math.sin(ang) * rr))
    d.polygon(pts, fill=fill)


def moon(d, cx, cy, r):
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(255, 240, 200))
    d.ellipse([cx - r + 18, cy - r + 18, cx + r - 18, cy + r - 18], fill=(255, 246, 218))


def sun(d, cx, cy, r):
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(255, 225, 130))


def hills(d, base_y, amp, color, n=7, seed=1):
    rnd = random.Random(seed)
    pts = [(0, S)]
    for i in range(n + 1):
        x = i * S / n
        y = base_y + (amp if i % 2 else -amp) * rnd.uniform(0.5, 1.0)
        pts.append((x, y))
    pts.append((S, S))
    d.polygon(pts, fill=color)


def tree(d, x, y, s, dark=False):
    trunk = (90, 66, 45)
    leaf = (40, 72, 48) if dark else (58, 104, 64)
    d.rectangle([x - 8 * s, y, x + 8 * s, y + 60 * s], fill=trunk)
    d.polygon([(x - 60 * s, y + 10 * s), (x + 60 * s, y + 10 * s), (x, y - 130 * s)], fill=leaf)


def fence(d, y, x0=0, x1=S, s=1.0):
    wood = (122, 84, 52)
    for fx in range(int(x0), int(x1), int(150 * s)):
        d.rectangle([fx, y - 60 * s, fx + 22 * s, y + 40 * s], fill=wood)
    d.rectangle([x0, y - 36 * s, x1, y - 16 * s], fill=(138, 98, 62))


def lamp(d, x, y, s=1.0, on=True):
    d.rectangle([x - 8 * s, y - 220 * s, x + 8 * s, y], fill=(58, 63, 69))
    glow = (255, 226, 130) if on else (200, 205, 210)
    if on:
        d.ellipse([x - 90 * s, y - 330 * s, x + 90 * s, y - 150 * s], fill=(255, 240, 170))
    d.ellipse([x - 44 * s, y - 280 * s, x + 44 * s, y - 192 * s], fill=glow)


def gate(d, cx, y, s=1.0):
    wood = (122, 84, 52)
    d.rectangle([cx - 320 * s, y - 460 * s, cx - 260 * s, y], fill=wood)
    d.rectangle([cx + 260 * s, y - 460 * s, cx + 320 * s, y], fill=wood)
    d.rectangle([cx - 360 * s, y - 540 * s, cx + 360 * s, y - 450 * s], fill=(180, 101, 47))


def fountain(d, cx, y, s=1.0):
    d.ellipse([cx - 340 * s, y - 90 * s, cx + 340 * s, y + 90 * s], fill=(185, 192, 201))
    d.ellipse([cx - 290 * s, y - 66 * s, cx + 290 * s, y + 60 * s], fill=(95, 180, 222))
    d.rectangle([cx - 34 * s, y - 300 * s, cx + 34 * s, y], fill=(185, 192, 201))
    d.polygon([(cx - 90 * s, y - 300 * s), (cx + 90 * s, y - 300 * s), (cx, y - 470 * s)],
              fill=(159, 212, 236))


def critter(d, cx, cy, u, body, accent, feature=None, eyes_closed=False):
    ink = (34, 34, 34)
    if feature == "flame":
        d.polygon([(cx + 30 * u, cy + 20 * u), (cx + 78 * u, cy - 6 * u), (cx + 58 * u, cy + 44 * u)], fill=(255, 178, 74))
    d.ellipse([cx - 34 * u, cy - 8 * u, cx + 34 * u, cy + 56 * u], fill=body)
    d.ellipse([cx - 26 * u, cy + 8 * u, cx + 26 * u, cy + 52 * u], fill=accent)
    if feature == "shell":
        d.pieslice([cx - 40 * u, cy - 20 * u, cx + 40 * u, cy + 52 * u], 180, 360, fill=accent)
    if feature in (None, "ears", "flame"):
        d.polygon([(cx - 22 * u, cy - 40 * u), (cx - 12 * u, cy - 78 * u), (cx - 2 * u, cy - 40 * u)], fill=body)
        d.polygon([(cx + 2 * u, cy - 40 * u), (cx + 12 * u, cy - 78 * u), (cx + 22 * u, cy - 40 * u)], fill=body)
    if feature == "wings":
        d.polygon([(cx - 34 * u, cy - 10 * u), (cx - 86 * u, cy - 44 * u), (cx - 40 * u, cy + 16 * u)], fill=accent)
        d.polygon([(cx + 34 * u, cy - 10 * u), (cx + 86 * u, cy - 44 * u), (cx + 40 * u, cy + 16 * u)], fill=accent)
    if feature == "fin":
        d.polygon([(cx - 10 * u, cy - 44 * u), (cx + 10 * u, cy - 44 * u), (cx, cy - 82 * u)], fill=accent)
    d.ellipse([cx - 32 * u, cy - 52 * u, cx + 32 * u, cy + 8 * u], fill=body)
    if eyes_closed:
        w = max(3, int(3 * u))
        d.arc([cx - 18 * u, cy - 32 * u, cx - 5 * u, cy - 20 * u], 0, 180, fill=ink, width=w)
        d.arc([cx + 5 * u, cy - 32 * u, cx + 18 * u, cy - 20 * u], 0, 180, fill=ink, width=w)
    else:
        d.ellipse([cx - 17 * u, cy - 32 * u, cx - 6 * u, cy - 19 * u], fill=ink)
        d.ellipse([cx + 6 * u, cy - 32 * u, cx + 17 * u, cy - 19 * u], fill=ink)
        d.ellipse([cx - 14 * u, cy - 29 * u, cx - 10 * u, cy - 25 * u], fill=(255, 255, 255))
        d.ellipse([cx + 9 * u, cy - 29 * u, cx + 13 * u, cy - 25 * u], fill=(255, 255, 255))
    d.arc([cx - 9 * u, cy - 18 * u, cx + 9 * u, cy - 6 * u], 20, 160, fill=ink, width=max(3, int(2 * u)))


CRITTERS = {
    "flufftail": ((126, 200, 80), (232, 245, 208), "ears"),
    "pebblit": ((141, 141, 148), (201, 201, 207), "shell"),
    "aquaphin": ((74, 168, 216), (191, 230, 245), "fin"),
    "emberling": ((224, 112, 48), (255, 200, 74), "flame"),
    "mossback": ((93, 122, 69), (159, 181, 110), "shell"),
    "bubbletide": ((111, 196, 201), (235, 250, 250), "fin"),
    "zephyrix": ((232, 200, 50), (255, 255, 255), "wings"),
    "cinderpup": ((184, 74, 58), (255, 166, 74), "flame"),
    "glimmerwing": ((154, 106, 216), (230, 208, 255), "wings"),
    "nocturnix": ((58, 63, 107), (143, 208, 255), "wings"),
}

_pages = []


def page(name, build):
    random.seed(hash(name) % 100000)
    img = Image.new("RGB", (S, S))
    d = ImageDraw.Draw(img)
    build(img, d)
    path = os.path.join(PAGES_DIR, "%02d-%s.png" % (len(_pages), name))
    img.save(path)
    _pages.append(path)


def verse_page(name, lines, species=None, bg="cream", closed=True):
    """right-hand page: verse centered on soft background + vignette"""
    def build(img, d):
        sky(d, bg)
        # decorative corner stars
        for (x, y) in [(260, 240), (S - 260, 300), (220, S - 300), (S - 240, S - 260)]:
            star_shape(d, x, y, 54, (240, 205, 120))
        y = S * 0.30 - (len(lines) - 4) * 70
        for line in lines:
            d.text((S // 2, y), line, font=F_TEXT, fill=(70, 74, 88), anchor="mm")
            y += 168
        if species:
            b, a, f = CRITTERS[species]
            critter(d, S // 2, S * 0.855, 2.4, b, a, f, eyes_closed=closed)
    page(name, build)


# ---------------------------------------------------------- scene builders
def scene_meadow(d):
    for i in range(4):
        tree(d, 300 + i * 640, S * 0.5 + (i % 2) * 70, 1.8)
    hills(d, S * 0.55, 110, (104, 148, 84), 7, 4)
    for i in range(16):
        x, y = random.randint(80, S - 80), random.randint(int(S * 0.6), int(S * 0.72))
        d.ellipse([x - 18, y - 18, x + 18, y + 18],
                  fill=[(255, 255, 255), (255, 158, 192), (255, 226, 122)][i % 3])


def scene_rocks(d):
    hills(d, S * 0.55, 100, (120, 116, 108), 6, 7)
    for i in range(5):
        x = 220 + i * 480
        d.ellipse([x, S * 0.6, x + 300, S * 0.6 + 220], fill=(154, 147, 138))


def scene_pond(d, bubbles=False):
    hills(d, S * 0.5, 90, (84, 128, 78), 6, 2)
    d.ellipse([S * 0.08, S * 0.55, S * 0.92, S * 0.85], fill=(74, 148, 196))
    d.ellipse([S * 0.16, S * 0.59, S * 0.84, S * 0.82], fill=(96, 172, 218))
    for i in range(7):
        x = random.randint(int(S * 0.22), int(S * 0.75))
        y = random.randint(int(S * 0.62), int(S * 0.78))
        d.ellipse([x, y, x + 70, y + 26], fill=(120, 190, 230))
    if bubbles:
        for i in range(9):
            x = random.randint(int(S * 0.3), int(S * 0.7))
            y = random.randint(int(S * 0.25), int(S * 0.55))
            r = random.choice([26, 40, 58])
            d.ellipse([x - r, y - r, x + r, y + r], outline=(235, 250, 250), width=10)


def scene_embers(d, sparks=False):
    hills(d, S * 0.55, 100, (110, 84, 70), 6, 8)
    for i in range(4):
        x = 340 + i * 540
        d.polygon([(x, S * 0.68), (x + 100, S * 0.5), (x + 200, S * 0.68)], fill=(255, 170, 90))
        d.polygon([(x + 45, S * 0.68), (x + 100, S * 0.57), (x + 155, S * 0.68)], fill=(255, 214, 120))
    if sparks:
        for i in range(14):
            x, y = random.randint(200, S - 200), random.randint(int(S * 0.3), int(S * 0.6))
            star_shape(d, x, y, random.choice([20, 30, 40]), (255, 196, 110))


def scene_mosswood(d):
    hills(d, S * 0.52, 90, (64, 96, 64), 6, 6)
    for i in range(6):
        tree(d, 200 + i * 420, S * 0.48 + (i % 3) * 70, 2.0, dark=True)


def scene_breeze(d):
    hills(d, S * 0.62, 110, (104, 148, 84), 7, 4)
    for i in range(4):
        y = S * 0.26 + i * 160
        d.arc([S * 0.08 + i * 110, y, S * 0.52 + i * 110, y + 180], 200, 340,
              fill=(255, 255, 255), width=20)


def scene_sparkle(d):
    hills(d, S * 0.58, 100, (74, 84, 120), 6, 5)
    for i in range(30):
        x, y = random.randint(100, S - 100), random.randint(int(S * 0.28), int(S * 0.62))
        star_shape(d, x, y, random.choice([16, 22, 34]), (230, 208, 255))


def scene_farhills(d):
    hills(d, S * 0.5, 130, (30, 44, 74), 6, 10)
    hills(d, S * 0.66, 110, (40, 58, 92), 8, 11)
    for i in range(5):
        tree(d, 260 + i * 480, S * 0.6 + (i % 2) * 80, 1.8, dark=True)


def creature_illustration(name, species, sky_kind, scenery, closed=True, u=5.2):
    def build(img, d):
        sky(d, sky_kind)
        if sky_kind in ("dusk", "night"):
            stars(d, 100, 0.45)
            moon(d, S * 0.82, S * 0.16, 130)
        else:
            sun(d, S * 0.82, S * 0.18, 140)
        scenery(d)
        b, a, f = CRITTERS[species]
        critter(d, S * 0.5, S * 0.58, u, b, a, f, eyes_closed=closed)
    page(name, build)


def dream_spread(species, sky_left, dream_draw, lines):
    """left: sleeping critter with dream bubble; right: 2-line verse"""
    def build(img, d):
        sky(d, sky_left)
        stars(d, 110, 0.5)
        moon(d, S * 0.16, S * 0.16, 120)
        hills(d, S * 0.72, 90, (44, 74, 66), 6, 3)
        b, a, f = CRITTERS[species]
        critter(d, S * 0.34, S * 0.78, 4.0, b, a, f, eyes_closed=True)
        # dream bubble
        d.ellipse([S * 0.42, S * 0.5, S * 0.5, S * 0.56], fill=(255, 253, 245))
        d.ellipse([S * 0.48, S * 0.42, S * 0.58, S * 0.5], fill=(255, 253, 245))
        d.ellipse([S * 0.5, S * 0.08, S * 0.95, S * 0.46], fill=(255, 253, 245))
        dream_draw(d, S * 0.725, S * 0.27)
    page("dream-" + species, build)
    verse_page("dreamv-" + species, lines, species=None, bg="lilac")


def main():
    global _pages
    _pages = []
    os.makedirs(PAGES_DIR, exist_ok=True)
    for f in os.listdir(PAGES_DIR):
        os.remove(os.path.join(PAGES_DIR, f))
    os.makedirs(os.path.join(ROOT, "dist"), exist_ok=True)

    # ============ FRONT MATTER (4 pages) ============
    def p_title(img, d):
        sky(d, "night")
        stars(d, 130, 0.6)
        moon(d, S * 0.5, S * 0.30, 190)
        hills(d, S * 0.72, 100, (44, 74, 66), 6, 3)
        fence(d, S * 0.9, 0, S, 1.6)
        d.text((S // 2, S * 0.55), "Goodnight,", font=F_TITLE, fill=(255, 250, 235), anchor="mm")
        d.text((S // 2, S * 0.645), "Wildhaven", font=F_TITLE, fill=(255, 216, 112), anchor="mm")
        d.text((S // 2, S * 0.73), "A Bedtime Story from the Creature Park",
               font=F_SMALL, fill=(214, 224, 244), anchor="mm")
        d.text((S // 2, S * 0.82), "S. J. Tang", font=F_NAME, fill=(255, 250, 235), anchor="mm")
    page("title", p_title)

    def p_copyright(img, d):
        sky(d, "cream")
        d.text((S // 2, S * 0.42), "For every little dreamer", font=F_TEXT, fill=(70, 74, 88), anchor="mm")
        d.text((S // 2, S * 0.49), 'who asks for "one more story, please."', font=F_TEXT, fill=(70, 74, 88), anchor="mm")
        d.text((S // 2, S * 0.88), "Copyright © S. J. Tang. All rights reserved.",
               font=F_SMALL, fill=(150, 150, 158), anchor="mm")
        d.text((S // 2, S * 0.92), "Story and illustrations created with the assistance of AI, directed by the author.",
               font=F_SMALL, fill=(150, 150, 158), anchor="mm")
    page("copyright", p_copyright)

    def p_belongs(img, d):
        sky(d, "lilac")
        star_shape(d, S * 0.5, S * 0.22, 130, (240, 205, 120))
        d.text((S // 2, S * 0.42), "This book belongs to", font=F_H, fill=(70, 74, 88), anchor="mm")
        d.line([S * 0.2, S * 0.56, S * 0.8, S * 0.56], fill=(150, 150, 170), width=8)
        b, a, f = CRITTERS["flufftail"]
        critter(d, S * 0.5, S * 0.76, 2.6, b, a, f)
    page("belongs", p_belongs)

    def p_welcome(img, d):
        sky(d, "sunset")
        sun(d, S * 0.7, S * 0.3, 170)
        hills(d, S * 0.58, 120, (90, 120, 80), 6, 3)
        hills(d, S * 0.72, 100, (104, 148, 84), 8, 5)
        gate(d, S * 0.5, S * 0.82, 1.4)
        fence(d, S * 0.82, 0, S * 0.28, 1.4)
        fence(d, S * 0.82, S * 0.72, S, 1.4)
        d.text((S // 2, S * 0.12), "Welcome to Wildhaven,", font=F_H, fill=(255, 250, 235), anchor="mm")
        d.text((S // 2, S * 0.19), "where the wild things sleep tight...", font=F_H, fill=(255, 250, 235), anchor="mm")
    page("welcome", p_welcome)

    # ============ OPENING SPREADS (4 pages) ============
    def p_sunset(img, d):
        sky(d, "sunset")
        sun(d, S * 0.75, S * 0.32, 180)
        hills(d, S * 0.58, 120, (90, 120, 80), 6, 3)
        hills(d, S * 0.72, 100, (104, 148, 84), 8, 5)
        for i in range(5):
            tree(d, 260 + i * 500, S * 0.64 + (i % 2) * 80, 1.7)
        fence(d, S * 0.8, 0, S, 1.5)
    page("sunset", p_sunset)
    verse_page("sunset-v", [
        "When the sun slips down",
        "behind the hill,",
        "and all the busy park",
        "grows still,",
        "the keeper walks",
        "from gate to den,",
        "to say goodnight",
        "to every friend."], species="flufftail", closed=False)

    def p_walk(img, d):
        sky(d, "dusk")
        stars(d, 70, 0.4)
        hills(d, S * 0.6, 100, (58, 96, 74), 7, 5)
        fence(d, S * 0.84, 0, S, 1.6)
        lamp(d, S * 0.25, S * 0.84, 2.0)
        lamp(d, S * 0.75, S * 0.84, 2.0)
        gate(d, S * 0.5, S * 0.84, 1.2)
    page("walk", p_walk)
    verse_page("walk-v", [
        "Down the path",
        "the keeper goes,",
        "past the gate",
        "where lamplight glows.",
        "Boots on gravel,",
        "soft and slow —",
        "time to tuck in",
        "friends below."], species=None)

    # ============ TEN CREATURE SPREADS (20 pages) ============
    creature_illustration("flufftail", "flufftail", "dusk", scene_meadow)
    verse_page("flufftail-v", [
        "Flufftail hops",
        "one final lap,",
        "then curls up for",
        "a meadow nap.",
        '"Goodnight, Flufftail,',
        'soft and small,',
        'the comfiest bunny',
        'of them all."'], species="flufftail")

    creature_illustration("pebblit", "pebblit", "dusk", scene_rocks)
    verse_page("pebblit-v", [
        "Pebblit yawns",
        "a stony yawn,",
        "been rolling boulders",
        "since the dawn.",
        '"Goodnight, Pebblit,',
        'sturdy friend,',
        'even mountains rest',
        'at day\'s end."'], species="pebblit")

    creature_illustration("aquaphin", "aquaphin", "dusk", scene_pond)
    verse_page("aquaphin-v", [
        "Aquaphin makes",
        "one last splash,",
        "a silver ripple,",
        "then a dash.",
        '"Goodnight, Aquaphin,',
        'dive down deep,',
        'the pond will rock you',
        'fast asleep."'], species="aquaphin")

    creature_illustration("bubbletide", "bubbletide", "dusk",
                          lambda d: scene_pond(d, bubbles=True))
    verse_page("bubbletide-v", [
        "Bubbletide blows",
        "one last bubble —",
        "pop! it lands",
        "without any trouble.",
        '"Goodnight, Bubbletide,',
        'drift and gleam,',
        'asleep upon',
        'the silver stream."'], species="bubbletide")

    creature_illustration("emberling", "emberling", "dusk", scene_embers)
    verse_page("emberling-v", [
        "Emberling glows",
        "warm and low,",
        "a tiny lantern's",
        "sleepy glow.",
        '"Goodnight, Emberling,',
        'dim your light,',
        'you\'ll shine again',
        'tomorrow night."'], species="emberling")

    creature_illustration("cinderpup", "cinderpup", "dusk",
                          lambda d: scene_embers(d, sparks=True))
    verse_page("cinderpup-v", [
        "Cinderpup has",
        "run all day,",
        "sparks of joy",
        "along the way.",
        '"Goodnight, Cinderpup,',
        'rest your feet,',
        'tomorrow\'s sparks will be',
        'twice as sweet."'], species="cinderpup")

    creature_illustration("mossback", "mossback", "dusk", scene_mosswood)
    verse_page("mossback-v", [
        "Mossback moves",
        "so slow, so deep,",
        "he's halfway into",
        "dreams already.",
        '"Goodnight, Mossback,',
        'mossy dome,',
        'wherever you are,',
        'you\'re always home."'], species="mossback")

    creature_illustration("zephyrix", "zephyrix", "sunset", scene_breeze)
    verse_page("zephyrix-v", [
        "Zephyrix races",
        "one more breeze,",
        "then folds her wings",
        "beneath the trees.",
        '"Goodnight, Zephyrix,',
        'swift and free,',
        'the wind will hum',
        'your lullaby."'], species="zephyrix")

    creature_illustration("glimmerwing", "glimmerwing", "night", scene_sparkle)
    verse_page("glimmerwing-v", [
        "Glimmerwing sheds",
        "sparks of light,",
        "confetti for",
        "the coming night.",
        '"Goodnight, Glimmerwing,',
        'gleam and glow,',
        'you make the dark',
        'a wonder-show."'], species="glimmerwing")

    creature_illustration("nocturnix", "nocturnix", "night", scene_farhills, closed=False)
    verse_page("nocturnix-v", [
        "And on the farthest,",
        "darkest hill,",
        "Nocturnix watches,",
        "wise and still.",
        '"Goodnight, Nocturnix,',
        'count the stars,',
        'and guard the dreams',
        'that will be ours."'], species="nocturnix", closed=False)

    # ============ PARK NIGHT SPREADS (6 pages) ============
    def p_fountain(img, d):
        sky(d, "night")
        stars(d, 120, 0.5)
        moon(d, S * 0.2, S * 0.16, 140)
        hills(d, S * 0.62, 100, (44, 74, 66), 6, 3)
        fountain(d, S * 0.5, S * 0.78, 1.6)
        lamp(d, S * 0.14, S * 0.84, 1.8)
        lamp(d, S * 0.86, S * 0.84, 1.8)
    page("fountain", p_fountain)
    verse_page("fountain-v", [
        "The lamps blink on,",
        "the gates are closed,",
        "the fountain sings,",
        "the park's in repose.",
        "Every habitat,",
        "snug and tight,",
        "hums with sleepy",
        "creature-light."], species=None)

    def p_stars(img, d):
        sky(d, "night")
        stars(d, 90, 0.9)
        for i, (x, y, r) in enumerate([(0.2, 0.24, 150), (0.42, 0.16, 120),
                                       (0.63, 0.28, 170), (0.8, 0.14, 110),
                                       (0.5, 0.48, 200)]):
            star_shape(d, S * x, S * y, r, (255, 226, 130))
        hills(d, S * 0.78, 90, (30, 44, 74), 6, 10)
    page("stars", p_stars)
    verse_page("stars-v", [
        "One star, two stars,",
        "three stars, four —",
        "five above",
        "the fountain's door.",
        "Every star's",
        "a tiny light",
        "keeping watch",
        "on us tonight."], species=None)

    def p_moon(img, d):
        sky(d, "night")
        stars(d, 130, 0.7)
        moon(d, S * 0.5, S * 0.4, 420)
        hills(d, S * 0.82, 80, (30, 44, 74), 6, 10)
    page("moon", p_moon)
    verse_page("moon-v", [
        "The moon leans down",
        "to hum a tune",
        "the hills have known",
        "since always-June.",
        "Hush now, hush now,",
        "close your eyes,",
        "the park is wrapped",
        "in lullabies."], species=None)

    # ============ DREAMS SECTION (12 pages) ============
    def p_dreams_intro(img, d):
        sky(d, "night")
        stars(d, 150, 0.6)
        moon(d, S * 0.78, S * 0.2, 150)
        hills(d, S * 0.74, 90, (44, 74, 66), 6, 3)
        names = ["flufftail", "emberling", "aquaphin"]
        for x, nm in zip([0.24, 0.5, 0.76], names):
            b, a, f = CRITTERS[nm]
            critter(d, S * x, S * 0.78, 2.4, b, a, f, eyes_closed=True)
    page("dreams", p_dreams_intro)
    verse_page("dreams-v", [
        "And what do",
        "sleeping critters dream,",
        "tucked beneath",
        "the moon's soft beam?",
        "Come and peek —",
        "but not a peep! —",
        "at dreams inside",
        "the park asleep."], species=None)

    dream_spread("flufftail", "night",
                 lambda d, x, y: [d.ellipse([x - 210 + i * 140, y - 40, x - 90 + i * 140, y + 80],
                                            fill=(255, 158, 192)) for i in range(3)],
                 ["Flufftail dreams of clover fields,", "",
                  "and all the somersaults they yield."])
    dream_spread("aquaphin", "night",
                 lambda d, x, y: d.polygon([(x - 180, y + 80), (x, y - 120), (x + 180, y + 80)],
                                           fill=(96, 172, 218)),
                 ["Aquaphin dreams of waterfalls,", "",
                  "of diving deep when morning calls."])
    dream_spread("emberling", "night",
                 lambda d, x, y: [star_shape(d, x - 140 + i * 140, y, 60, (255, 196, 110))
                                  for i in range(3)],
                 ["Emberling dreams of firefly nights,", "",
                  "of cocoa cups and friendly lights."])
    dream_spread("glimmerwing", "night",
                 lambda d, x, y: [star_shape(d, x - 160 + (i % 3) * 160, y - 80 + (i // 3) * 160,
                                             52, (154, 106, 216)) for i in range(6)],
                 ["Glimmerwing dreams in purple sparks,", "",
                  "of painting stars across the dark."])
    dream_spread("nocturnix", "night",
                 lambda d, x, y: moon(d, x, y, 130),
                 ["Nocturnix dreams with one eye bright —", "",
                  "somebody must guard the night."])

    # ============ FINALE (4 pages) ============
    def p_final(img, d):
        sky(d, "night")
        stars(d, 160, 0.55)
        moon(d, S * 0.5, S * 0.2, 170)
        hills(d, S * 0.66, 100, (44, 74, 66), 6, 3)
        hills(d, S * 0.8, 90, (58, 96, 74), 8, 5)
        xs = [0.13, 0.28, 0.43, 0.58, 0.73, 0.88]
        names = ["flufftail", "aquaphin", "emberling", "zephyrix", "glimmerwing", "nocturnix"]
        for x, nm in zip(xs, names):
            b, a, f = CRITTERS[nm]
            critter(d, S * x, S * 0.74, 1.9, b, a, f, eyes_closed=True)
        fence(d, S * 0.88, 0, S, 1.5)
    page("final", p_final)
    verse_page("final-v", [
        "So close your eyes,",
        "my sleepy friend,",
        "the day is done,",
        "the dreams begin.",
        "The stars will keep",
        "the park in sight —",
        "Goodnight, Wildhaven.",
        "Friends, goodnight."], species=None)

    def p_goodnight(img, d):
        sky(d, "night")
        stars(d, 200, 0.8, big=True)
        moon(d, S * 0.5, S * 0.42, 300)
        d.text((S // 2, S * 0.78), "Goodnight.", font=F_TITLE, fill=(255, 250, 235), anchor="mm")
    page("goodnight", p_goodnight)

    def p_gallery(img, d):
        sky(d, "cream")
        d.text((S // 2, S * 0.09), "The Friends of Wildhaven", font=F_H, fill=(70, 74, 88), anchor="mm")
        names = list(CRITTERS.keys())
        for i, nm in enumerate(names):
            col, row = i % 5, i // 5
            x = S * (0.14 + col * 0.18)
            y = S * (0.32 + row * 0.34)
            b, a, f = CRITTERS[nm]
            critter(d, x, y, 1.9, b, a, f)
            d.text((x, y + S * 0.09), nm.capitalize(), font=F_SMALL, fill=(70, 74, 88), anchor="mm")
    page("gallery", p_gallery)

    # ============ BACK MATTER (4 pages) ============
    def p_checklist(img, d):
        sky(d, "lilac")
        d.text((S // 2, S * 0.1), "My Goodnight List", font=F_H, fill=(70, 74, 88), anchor="mm")
        items = ["Brush my teeth", "Put on cozy pajamas", "Read one story (this one!)",
                 "A big goodnight hug", "Close my eyes and dream"]
        y = S * 0.26
        for it in items:
            d.rounded_rectangle([S * 0.14, y - 60, S * 0.14 + 120, y + 60], radius=20,
                                outline=(120, 124, 140), width=10)
            d.text((S * 0.22, y), it, font=F_TEXT, fill=(70, 74, 88), anchor="lm")
            y += S * 0.13
        b, a, f = CRITTERS["mossback"]
        critter(d, S * 0.8, S * 0.87, 2.0, b, a, f, eyes_closed=True)
    page("checklist", p_checklist)

    def p_draw(img, d):
        sky(d, "day")
        sun(d, S * 0.82, S * 0.14, 120)
        hills(d, S * 0.6, 90, (104, 148, 84), 7, 4)
        fence(d, S * 0.86, 0, S, 1.5)
        d.text((S // 2, S * 0.1), "Every park needs new friends.", font=F_H, fill=(70, 74, 88), anchor="mm")
        d.text((S // 2, S * 0.17), "Draw yours here!", font=F_H, fill=(70, 74, 88), anchor="mm")
        d.rounded_rectangle([S * 0.16, S * 0.26, S * 0.84, S * 0.78], radius=40,
                            outline=(120, 124, 140), width=12, fill=(255, 253, 245))
    page("draw", p_draw)

    def p_count(img, d):
        sky(d, "dusk")
        stars(d, 60, 0.3)
        hills(d, S * 0.6, 90, (58, 96, 74), 7, 5)
        d.text((S // 2, S * 0.09), "Can you count the Flufftails?", font=F_H, fill=(255, 250, 235), anchor="mm")
        b, a, f = CRITTERS["flufftail"]
        for i in range(7):
            x = S * (0.14 + (i % 4) * 0.24)
            y = S * (0.4 + (i // 4) * 0.3)
            critter(d, x, y, 1.8, b, a, f, eyes_closed=(i % 2 == 0))
    page("count", p_count)

    def p_about(img, d):
        sky(d, "night")
        stars(d, 120, 0.5)
        moon(d, S * 0.8, S * 0.14, 120)
        hills(d, S * 0.74, 90, (44, 74, 66), 6, 3)
        lines = [
            "Wildhaven is real (sort of)!",
            "",
            "The creatures in this book live in",
            "Wildhaven: Creature Park — a cozy game",
            "you can play together with a grown-up,",
            "and in Critter Isles, where it all began.",
            "",
            "Sweet dreams, keeper.",
        ]
        y = S * 0.16
        for line in lines:
            d.text((S // 2, y), line, font=F_TEXT, fill=(226, 232, 246), anchor="mm")
            y += 150
        names = ["flufftail", "cinderpup", "bubbletide"]
        for x, nm in zip([0.28, 0.5, 0.72], names):
            b, a, f = CRITTERS[nm]
            critter(d, S * x, S * 0.82, 2.2, b, a, f)
    page("about", p_about)

    # ============ assemble ============
    imgs = [Image.open(p).convert("RGB") for p in _pages]
    pdf_path = os.path.join(ROOT, "dist", "Goodnight-Wildhaven-Book.pdf")
    imgs[0].save(pdf_path, save_all=True, append_images=imgs[1:], resolution=300.0)
    print("PDF:", pdf_path, os.path.getsize(pdf_path) // 1024 // 1024, "MB,", len(imgs), "pages")


if __name__ == "__main__":
    main()
