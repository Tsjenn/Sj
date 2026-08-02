#!/usr/bin/env python3
"""Illustrate and assemble 'Goodnight, Wildhaven' — a children's bedtime book.

12 story pages + cover, flat-design illustrations drawn with PIL in the same
style as the Wildhaven album art. Output is a print-ready square PDF
(8.5 x 8.5 in at 300 dpi, KDP-compatible trim) plus page PNGs.

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
F_TEXT = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 96)
F_SMALL = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 64)

SKIES = {
    "day":    [(126, 200, 235), (200, 235, 250)],
    "sunset": [(90, 70, 120), (245, 170, 110)],
    "dusk":   [(40, 52, 92), (232, 168, 117)],
    "night":  [(12, 20, 44), (46, 62, 110)],
}


def sky(d, kind):
    top, bot = SKIES[kind]
    for y in range(S):
        t = y / S
        c = tuple(int(top[i] + (bot[i] - top[i]) * t) for i in range(3))
        d.line([(0, y), (S, y)], fill=c)


def stars(d, n=140, ymax=0.6):
    for _ in range(n):
        x, y = random.randint(0, S), random.randint(0, int(S * ymax))
        r = random.choice([2, 3, 3, 4, 6])
        d.ellipse([x - r, y - r, x + r, y + r], fill=(255, 252, 230))


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


def critter(d, cx, cy, u, body, accent, feature=None, eyes_closed=False):
    ink = (34, 34, 34)
    # tail features behind body
    if feature == "flame":
        d.polygon([(cx + 30 * u, cy + 20 * u), (cx + 78 * u, cy - 6 * u), (cx + 58 * u, cy + 44 * u)], fill=(255, 178, 74))
    d.ellipse([cx - 34 * u, cy - 8 * u, cx + 34 * u, cy + 56 * u], fill=body)      # body
    d.ellipse([cx - 26 * u, cy + 8 * u, cx + 26 * u, cy + 52 * u], fill=accent)    # belly
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
    d.ellipse([cx - 32 * u, cy - 52 * u, cx + 32 * u, cy + 8 * u], fill=body)      # head
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


def text_band(img, d, lines):
    """soft rounded panel with the story text at the bottom"""
    pad = 90
    lh = 132
    h = pad * 2 + lh * len(lines)
    y0 = S - h - 120
    panel = Image.new("RGBA", (S - 240, h), (255, 253, 245, 235))
    img.paste(panel, (120, y0), panel)
    d2 = ImageDraw.Draw(img)
    for i, line in enumerate(lines):
        d2.text((S // 2, y0 + pad + lh * i + lh // 2), line,
                font=F_TEXT, fill=(52, 58, 66), anchor="mm")


CRITTERS = {
    "flufftail": ((126, 200, 80), (232, 245, 208), "ears"),
    "pebblit": ((141, 141, 148), (201, 201, 207), "shell"),
    "aquaphin": ((74, 168, 216), (191, 230, 245), "fin"),
    "emberling": ((224, 112, 48), (255, 200, 74), "flame"),
    "mossback": ((93, 122, 69), (159, 181, 110), "shell"),
    "zephyrix": ((232, 200, 50), (255, 255, 255), "wings"),
    "glimmerwing": ((154, 106, 216), (230, 208, 255), "wings"),
    "nocturnix": ((58, 63, 107), (143, 208, 255), "wings"),
}


def page(name, sky_kind, build, lines):
    random.seed(hash(name) % 100000)
    img = Image.new("RGB", (S, S))
    d = ImageDraw.Draw(img)
    sky(d, sky_kind)
    build(img, d)
    if lines:
        text_band(img, d, lines)
    path = os.path.join(PAGES_DIR, name + ".png")
    img.save(path)
    print("page", name)
    return path


def main():
    os.makedirs(PAGES_DIR, exist_ok=True)
    os.makedirs(os.path.join(ROOT, "dist"), exist_ok=True)
    pages = []

    # ---- cover
    def cover(img, d):
        stars(d, 120, 0.5)
        moon(d, S * 0.78, S * 0.2, 150)
        hills(d, S * 0.62, 130, (44, 74, 66), 6, 3)
        hills(d, S * 0.74, 110, (58, 96, 74), 8, 5)
        hills(d, S * 0.86, 90, (84, 128, 78), 7, 9)
        for i in range(6):
            tree(d, 200 + i * 420, S * 0.72 + (i % 3) * 60, 1.4, dark=True)
        fence(d, S * 0.90, 0, S, 1.6)
        lamp(d, S * 0.2, S * 0.9, 2.0)
        b, a, f = CRITTERS["flufftail"]
        critter(d, S * 0.62, S * 0.84, 3.2, b, a, f, eyes_closed=True)
        b, a, f = CRITTERS["nocturnix"]
        critter(d, S * 0.82, S * 0.86, 2.4, b, a, f)
        d.text((S // 2 + 10, S * 0.13 + 10), "Goodnight,", font=F_TITLE, fill=(8, 12, 26), anchor="mm")
        d.text((S // 2, S * 0.13), "Goodnight,", font=F_TITLE, fill=(255, 250, 235), anchor="mm")
        d.text((S // 2 + 10, S * 0.235 + 10), "Wildhaven", font=F_TITLE, fill=(8, 12, 26), anchor="mm")
        d.text((S // 2, S * 0.235), "Wildhaven", font=F_TITLE, fill=(255, 216, 112), anchor="mm")
        d.text((S // 2, S * 0.31), "A bedtime story from the creature park", font=F_SMALL,
               fill=(210, 220, 240), anchor="mm")
    pages.append(page("00-cover", "night", cover, None))

    # ---- p1 sunset opening
    def p1(img, d):
        sun(d, S * 0.75, S * 0.35, 170)
        hills(d, S * 0.60, 120, (90, 120, 80), 6, 3)
        hills(d, S * 0.74, 100, (104, 148, 84), 8, 5)
        for i in range(5):
            tree(d, 260 + i * 500, S * 0.66 + (i % 2) * 80, 1.5)
        fence(d, S * 0.80, 0, S, 1.5)
        b, a, f = CRITTERS["flufftail"]
        critter(d, S * 0.3, S * 0.75, 2.6, b, a, f)
    pages.append(page("01-sunset", "sunset", p1, [
        "When the sun slips down behind the hill,",
        "and all the busy park grows still,",
        "the keeper walks from gate to den,",
        "to say goodnight to every friend."]))

    # ---- creature pages
    def creature_page(species, sky_kind, scenery, lines, closed=True, extra=None):
        def build(img, d):
            if sky_kind in ("dusk", "night"):
                stars(d, 90, 0.45)
                moon(d, S * 0.8, S * 0.18, 120)
            else:
                sun(d, S * 0.8, S * 0.2, 130)
            scenery(d)
            b, a, f = CRITTERS[species]
            critter(d, S * 0.5, S * 0.56, 4.2, b, a, f, eyes_closed=closed)
            if extra:
                extra(d)
        return page(species, sky_kind, build, lines)

    def meadow(d):
        hills(d, S * 0.55, 110, (104, 148, 84), 7, 4)
        for i in range(4):
            tree(d, 200 + i * 640, S * 0.5 + (i % 2) * 70, 1.4)
        for i in range(14):
            x, y = random.randint(80, S - 80), random.randint(int(S * 0.6), int(S * 0.68))
            d.ellipse([x - 14, y - 14, x + 14, y + 14],
                      fill=[(255, 255, 255), (255, 158, 192), (255, 226, 122)][i % 3])

    pages.append(creature_page("flufftail", "dusk", meadow, [
        "Flufftail hops one final lap,",
        "then curls up for a meadow nap.",
        '"Goodnight, Flufftail, soft and small,',
        'the comfiest bunny of them all."']))

    def rocks(d):
        hills(d, S * 0.55, 100, (120, 116, 108), 6, 7)
        for i in range(5):
            x = 260 + i * 480
            d.ellipse([x, S * 0.62, x + 260, S * 0.62 + 180], fill=(154, 147, 138))
    pages.append(creature_page("pebblit", "dusk", rocks, [
        "Pebblit yawns a stony yawn,",
        "been rolling boulders since the dawn.",
        '"Goodnight, Pebblit, sturdy friend,',
        'even mountains rest at day\'s end."']))

    def pond(d):
        hills(d, S * 0.52, 90, (84, 128, 78), 6, 2)
        d.ellipse([S * 0.12, S * 0.58, S * 0.88, S * 0.8], fill=(74, 148, 196))
        d.ellipse([S * 0.2, S * 0.62, S * 0.8, S * 0.78], fill=(96, 172, 218))
        for i in range(6):
            x = random.randint(int(S * 0.25), int(S * 0.75))
            y = random.randint(int(S * 0.63), int(S * 0.74))
            d.ellipse([x, y, x + 60, y + 22], fill=(120, 190, 230))
    pages.append(creature_page("aquaphin", "dusk", pond, [
        "Aquaphin makes one last splash,",
        "a silver ripple, then a dash.",
        '"Goodnight, Aquaphin, dive down deep,',
        'the pond will rock you fast asleep."']))

    def embers(d):
        hills(d, S * 0.55, 100, (110, 84, 70), 6, 8)
        for i in range(4):
            x = 400 + i * 520
            d.polygon([(x, S * 0.68), (x + 90, S * 0.52), (x + 180, S * 0.68)], fill=(255, 170, 90))
            d.polygon([(x + 40, S * 0.68), (x + 90, S * 0.58), (x + 140, S * 0.68)], fill=(255, 214, 120))
    pages.append(creature_page("emberling", "dusk", embers, [
        "Emberling glows warm and low,",
        "a tiny lantern's sleepy glow.",
        '"Goodnight, Emberling, dim your light,',
        'you\'ll shine again tomorrow night."']))

    def mosswood(d):
        hills(d, S * 0.52, 90, (64, 96, 64), 6, 6)
        for i in range(6):
            tree(d, 180 + i * 420, S * 0.5 + (i % 3) * 60, 1.7, dark=True)
    pages.append(creature_page("mossback", "dusk", mosswood, [
        "Mossback moves so slow, so deep,",
        "he's halfway into dreams already.",
        '"Goodnight, Mossback, mossy dome,',
        'wherever you are, you\'re always home."']))

    def breeze(d):
        hills(d, S * 0.62, 110, (104, 148, 84), 7, 4)
        for i in range(4):
            y = S * 0.3 + i * 140
            d.arc([S * 0.1 + i * 100, y, S * 0.5 + i * 100, y + 160], 200, 340,
                  fill=(255, 255, 255), width=16)
    pages.append(creature_page("zephyrix", "sunset", breeze, [
        "Zephyrix races one more breeze,",
        "then folds her wings beneath the trees.",
        '"Goodnight, Zephyrix, swift and free,',
        'the wind will hum your lullaby."']))

    def sparkle(d):
        hills(d, S * 0.58, 100, (74, 84, 120), 6, 5)
        for i in range(26):
            x, y = random.randint(100, S - 100), random.randint(int(S * 0.3), int(S * 0.62))
            r = random.choice([6, 8, 12])
            d.ellipse([x - r, y - r, x + r, y + r], fill=(230, 208, 255))
    pages.append(creature_page("glimmerwing", "night", sparkle, [
        "Glimmerwing sheds sparks of light,",
        "confetti for the coming night.",
        '"Goodnight, Glimmerwing, gleam and glow,',
        'you make the dark a wonder-show."']))

    def farhills(d):
        hills(d, S * 0.5, 130, (30, 44, 74), 6, 10)
        hills(d, S * 0.66, 110, (40, 58, 92), 8, 11)
        for i in range(5):
            tree(d, 300 + i * 460, S * 0.62 + (i % 2) * 70, 1.5, dark=True)
    pages.append(creature_page("nocturnix", "night", farhills, [
        "And on the farthest, darkest hill,",
        "Nocturnix watches, wise and still.",
        '"Goodnight, Nocturnix, count the stars,',
        'and guard the dreams that will be ours."'], closed=False))

    # ---- park at night
    def parknight(img, d):
        stars(d, 130, 0.5)
        moon(d, S * 0.2, S * 0.16, 140)
        hills(d, S * 0.6, 100, (44, 74, 66), 6, 3)
        hills(d, S * 0.74, 90, (58, 96, 74), 8, 5)
        fence(d, S * 0.84, 0, S, 1.6)
        lamp(d, S * 0.18, S * 0.84, 1.9)
        lamp(d, S * 0.5, S * 0.84, 1.9)
        lamp(d, S * 0.82, S * 0.84, 1.9)
    pages.append(page("10-park", "night", parknight, [
        "The lamps blink on, the gates are closed,",
        "the fountain sings, the park's in repose.",
        "Every habitat, snug and tight,",
        "hums with sleepy creature-light."]))

    # ---- final page
    def final(img, d):
        stars(d, 160, 0.55)
        moon(d, S * 0.5, S * 0.2, 170)
        hills(d, S * 0.66, 100, (44, 74, 66), 6, 3)
        hills(d, S * 0.8, 90, (58, 96, 74), 8, 5)
        xs = [0.16, 0.32, 0.48, 0.64, 0.8]
        names = ["flufftail", "aquaphin", "emberling", "glimmerwing", "nocturnix"]
        for x, nm in zip(xs, names):
            b, a, f = CRITTERS[nm]
            critter(d, S * x, S * 0.72, 1.9, b, a, f, eyes_closed=True)
    pages.append(page("11-goodnight", "night", final, [
        "So close your eyes, my sleepy friend,",
        "the day is done, the dreams begin.",
        "The stars will keep the park in sight —",
        "Goodnight, Wildhaven. Friends, goodnight."]))

    # ---- assemble PDF
    imgs = [Image.open(p).convert("RGB") for p in pages]
    pdf_path = os.path.join(ROOT, "dist", "Goodnight-Wildhaven-Book.pdf")
    imgs[0].save(pdf_path, save_all=True, append_images=imgs[1:],
                 resolution=300.0)
    print("PDF:", pdf_path, os.path.getsize(pdf_path) // 1024 // 1024, "MB,", len(imgs), "pages")


if __name__ == "__main__":
    main()
