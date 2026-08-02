#!/usr/bin/env python3
"""Illustrate and assemble 'Count with the Critters!' — Wildhaven book two.

A bright educational picture book: numbers 1-10 (each number = N critters
of one species), then colors, shapes, and play-along activity pages.
25 interior pages at 8.5x8.5in 300dpi (KDP square trim), plus covers.

  dist/Count-with-the-Critters-Book.pdf     paperback interior
  marketing/book2/cover-ebook-2550x2550.jpg Kindle/listing cover
  marketing/book2/cover-paperback-wrap.pdf  paperback wraparound (25pp spine)
  book/pages2/*.png

Run:  python3 scripts/make_book2.py   (then scripts/make_epub.py for the EPUB)
"""

import os
import random

from PIL import Image, ImageDraw, ImageFont

from make_book import (S, SKIES, sky, sun, moon, hills, tree, fence, lamp,
                       star_shape, critter, CRITTERS, F_TITLE, F_H, F_TEXT,
                       F_SMALL, F_NAME)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAGES_DIR = os.path.join(ROOT, "book", "pages2")
OUT2 = os.path.join(ROOT, "marketing", "book2")

F_NUM = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 560)
F_WORD = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 150)

_pages = []


def page(name, build):
    random.seed(hash(name) % 100000)
    img = Image.new("RGB", (S, S))
    d = ImageDraw.Draw(img)
    build(img, d)
    path = os.path.join(PAGES_DIR, "%02d-%s.png" % (len(_pages), name))
    img.save(path)
    _pages.append(path)


def text_band(img, lines, y_frac=0.86):
    pad, lh = 60, 128
    h = pad * 2 + lh * len(lines)
    y0 = int(S * y_frac) - h // 2
    panel = Image.new("RGBA", (S - 220, h), (255, 253, 245, 235))
    img.paste(panel, (110, y0), panel)
    d = ImageDraw.Draw(img)
    for i, line in enumerate(lines):
        d.text((S // 2, y0 + pad + lh * i + lh // 2), line,
               font=F_TEXT, fill=(52, 58, 66), anchor="mm")


# critter positions per count (fractions of page, in the scene area)
LAYOUTS = {
    1: [(0.5, 0.62)],
    2: [(0.36, 0.62), (0.64, 0.62)],
    3: [(0.28, 0.64), (0.5, 0.56), (0.72, 0.64)],
    4: [(0.3, 0.56), (0.7, 0.56), (0.3, 0.72), (0.7, 0.72)],
    5: [(0.26, 0.56), (0.5, 0.5), (0.74, 0.56), (0.36, 0.7), (0.64, 0.7)],
    6: [(0.28, 0.54), (0.5, 0.54), (0.72, 0.54), (0.28, 0.7), (0.5, 0.7), (0.72, 0.7)],
    7: [(0.24, 0.54), (0.44, 0.5), (0.64, 0.54), (0.84, 0.5),
        (0.32, 0.68), (0.54, 0.7), (0.76, 0.68)],
    8: [(0.22, 0.52), (0.42, 0.5), (0.62, 0.52), (0.82, 0.5),
        (0.26, 0.68), (0.46, 0.7), (0.66, 0.68), (0.86, 0.7)],
    9: [(0.22, 0.5), (0.42, 0.48), (0.62, 0.5), (0.82, 0.48),
        (0.26, 0.64), (0.5, 0.66), (0.74, 0.64), (0.36, 0.76), (0.62, 0.76)],
    10: [(0.16, 0.56), (0.32, 0.52), (0.48, 0.56), (0.64, 0.52), (0.8, 0.56),
         (0.2, 0.7), (0.36, 0.72), (0.52, 0.7), (0.68, 0.72), (0.84, 0.7)],
}

NUMBERS = [
    (1, "flufftail", "ONE", "day",
     ["ONE little Flufftail hops out to play —", "the very first friend of the day!"]),
    (2, "pebblit", "TWO", "day",
     ["TWO sleepy Pebblits sunbathe on stones,", "humming their pebbly morning tones."]),
    (3, "aquaphin", "THREE", "day",
     ["THREE splashy Aquaphins dive and spin,", "making the pond go ripple-and-grin."]),
    (4, "bubbletide", "FOUR", "day",
     ["FOUR bouncy Bubbletides blow bubbles that POP!", "One lands on a nose and won't come off!"]),
    (5, "emberling", "FIVE", "sunset",
     ["FIVE cozy Emberlings glow in a row,", "warming the evening with soft little glow."]),
    (6, "cinderpup", "SIX", "day",
     ["SIX zoomy Cinderpups race down the trail,", "sparks of joy from nose to tail!"]),
    (7, "mossback", "SEVEN", "day",
     ["SEVEN slow Mossbacks march in a line —", "the slowest parade, and they're doing just fine."]),
    (8, "zephyrix", "EIGHT", "day",
     ["EIGHT breezy Zephyrixes loop through the sky,", "playing tag with the clouds going by."]),
    (9, "glimmerwing", "NINE", "dusk",
     ["NINE shiny Glimmerwings sprinkle the night,", "dusting the park with sparkle-light."]),
    (10, None, "TEN", "sunset",
     ["TEN friends together — the whole crew!", "(Rare Nocturnix is counting with you!)"]),
]


def scene_base(d, sky_kind):
    sky(d, sky_kind)
    if sky_kind == "day":
        sun(d, S * 0.84, S * 0.14, 130)
    elif sky_kind == "sunset":
        sun(d, S * 0.8, S * 0.2, 150)
    else:
        moon(d, S * 0.84, S * 0.14, 120)
    hills(d, S * 0.5, 100, (104, 148, 84) if sky_kind == "day" else (74, 104, 84), 7, 4)
    for i in range(3):
        tree(d, 260 + i * 900, S * 0.44 + (i % 2) * 60, 1.6)


def number_page(n, species, word, sky_kind, rhyme):
    def build(img, d):
        scene_base(d, sky_kind)
        # big numeral, upper-left with soft disc behind
        d.ellipse([S * 0.05, S * 0.03, S * 0.4, S * 0.38], fill=(255, 253, 245))
        d.text((S * 0.225, S * 0.2), str(n), font=F_NUM, fill=(180, 101, 47), anchor="mm")
        d.text((S * 0.62, S * 0.12), word, font=F_WORD, fill=(255, 255, 255), anchor="mm")
        if species:
            b, a, f = CRITTERS[species]
            for (x, y) in LAYOUTS[n]:
                critter(d, S * x, S * y, 1.9 if n > 6 else 2.3, b, a, f)
        else:  # ten = one of each species
            for (x, y), nm in zip(LAYOUTS[10], CRITTERS.keys()):
                b, a, f = CRITTERS[nm]
                critter(d, S * x, S * y, 1.7, b, a, f)
        text_band(img, rhyme)
    page("num-%02d" % n, build)


def main():
    global _pages
    _pages = []
    os.makedirs(PAGES_DIR, exist_ok=True)
    for f in os.listdir(PAGES_DIR):
        os.remove(os.path.join(PAGES_DIR, f))
    os.makedirs(os.path.join(ROOT, "dist"), exist_ok=True)
    os.makedirs(OUT2, exist_ok=True)

    # ---- title
    def p_title(img, d):
        sky(d, "day")
        sun(d, S * 0.82, S * 0.16, 150)
        hills(d, S * 0.55, 110, (104, 148, 84), 7, 4)
        fence(d, S * 0.88, 0, S, 1.6)
        for (x, y), nm in zip([(0.2, 0.72), (0.4, 0.76), (0.6, 0.72), (0.8, 0.76)],
                              ["flufftail", "aquaphin", "cinderpup", "glimmerwing"]):
            b, a, f = CRITTERS[nm]
            critter(d, S * x, S * y, 2.2, b, a, f)
        d.text((S // 2 + 10, S * 0.14 + 10), "Count with", font=F_TITLE, fill=(40, 40, 48), anchor="mm")
        d.text((S // 2, S * 0.14), "Count with", font=F_TITLE, fill=(255, 255, 255), anchor="mm")
        d.text((S // 2 + 10, S * 0.25 + 10), "the Critters!", font=F_TITLE, fill=(40, 40, 48), anchor="mm")
        d.text((S // 2, S * 0.25), "the Critters!", font=F_TITLE, fill=(255, 216, 112), anchor="mm")
        d.text((S // 2, S * 0.34), "A Wildhaven Book of Numbers, Colors & Shapes",
               font=F_SMALL, fill=(255, 255, 255), anchor="mm")
        d.text((S // 2, S * 0.44), "S. J. Tang", font=F_NAME, fill=(255, 255, 255), anchor="mm")
    page("title", p_title)

    # ---- dedication / belongs
    def p_belongs(img, d):
        sky(d, "cream")
        star_shape(d, S * 0.5, S * 0.18, 120, (240, 205, 120))
        d.text((S // 2, S * 0.36), "This counting book belongs to", font=F_H, fill=(70, 74, 88), anchor="mm")
        d.line([S * 0.2, S * 0.48, S * 0.8, S * 0.48], fill=(150, 150, 170), width=8)
        d.text((S // 2, S * 0.6), "who is learning to count — hooray!", font=F_TEXT, fill=(70, 74, 88), anchor="mm")
        b, a, f = CRITTERS["flufftail"]
        critter(d, S * 0.5, S * 0.8, 2.6, b, a, f)
        d.text((S // 2, S * 0.95), "Copyright © S. J. Tang. Illustrations created with AI assistance, directed by the author.",
               font=F_SMALL, fill=(160, 160, 168), anchor="mm")
    page("belongs", p_belongs)

    # ---- intro
    def p_intro(img, d):
        scene_base(d, "day")
        fence(d, S * 0.86, 0, S, 1.5)
        b, a, f = CRITTERS["flufftail"]
        critter(d, S * 0.5, S * 0.62, 3.4, b, a, f)
        text_band(img, ["The gates are open! Come on in —",
                        "the Wildhaven counting games begin!",
                        "Point to each critter, count out loud..."])
    page("intro", p_intro)

    # ---- numbers 1-10
    for n, species, word, sk, rhyme in NUMBERS:
        number_page(n, species, word, sk, rhyme)

    # ---- recap
    def p_recap(img, d):
        scene_base(d, "sunset")
        for (x, y), nm in zip(LAYOUTS[10], CRITTERS.keys()):
            b, a, f = CRITTERS[nm]
            critter(d, S * x, S * y, 1.7, b, a, f)
        text_band(img, ["From ONE to TEN, you counted them all!",
                        "Now once more — can you count them", "with no help at all?"])
    page("recap", p_recap)

    # ---- colors (4 pages)
    COLOR_PAGES = [
        ("GREEN", (126, 200, 80), ["flufftail", "mossback"],
         ["GREEN is Flufftail, green is the tree,", "green as the meadow, wild and free!"]),
        ("BLUE", (74, 168, 216), ["aquaphin", "bubbletide"],
         ["BLUE is Aquaphin, blue is the pool,", "blue as a bubble, shiny and cool!"]),
        ("ORANGE", (224, 112, 48), ["emberling", "cinderpup"],
         ["ORANGE is Emberling's cozy glow,", "orange as sparks where Cinderpups go!"]),
        ("PURPLE", (154, 106, 216), ["glimmerwing", "nocturnix"],
         ["PURPLE is Glimmerwing, dusted with light,", "purple as dreams in the middle of night!"]),
    ]
    for word, color, species, rhyme in COLOR_PAGES:
        def build(img, d, word=word, color=color, species=species, rhyme=rhyme):
            sky(d, "cream")
            d.rounded_rectangle([S * 0.1, S * 0.06, S * 0.9, S * 0.24], radius=60, fill=color)
            d.text((S // 2, S * 0.15), word, font=F_WORD, fill=(255, 255, 255), anchor="mm")
            for x, nm in zip([0.34, 0.66], species):
                b, a, f = CRITTERS[nm]
                critter(d, S * x, S * 0.5, 2.8, b, a, f)
            text_band(img, rhyme, 0.82)
        page("color-" + word.lower(), build)

    # ---- shapes (3 pages)
    def p_shape_circle(img, d):
        sky(d, "day")
        sun(d, S * 0.5, S * 0.3, 240)
        b, a, f = CRITTERS["bubbletide"]
        critter(d, S * 0.5, S * 0.66, 2.6, b, a, f)
        for x, y, r in [(0.24, 0.42, 90), (0.76, 0.4, 70), (0.3, 0.62, 55), (0.72, 0.6, 80)]:
            d.ellipse([S * x - r, S * y - r, S * x + r, S * y + r],
                      outline=(120, 190, 230), width=16)
        text_band(img, ["A CIRCLE is round like the sun up high,", "round as the bubbles floating by!"])
    page("shape-circle", p_shape_circle)

    def p_shape_triangle(img, d):
        sky(d, "day")
        hills(d, S * 0.5, 110, (104, 148, 84), 7, 4)
        for i in range(4):
            tree(d, 340 + i * 620, S * 0.48 + (i % 2) * 60, 2.2)
        b, a, f = CRITTERS["flufftail"]
        critter(d, S * 0.5, S * 0.68, 2.8, b, a, f)
        text_band(img, ["A TRIANGLE has three pointy sides —", "like trees! Like ears! Like mountain rides!"])
    page("shape-triangle", p_shape_triangle)

    def p_shape_star(img, d):
        sky(d, "night")
        for i in range(30):
            x, y = random.randint(100, S - 100), random.randint(80, int(S * 0.45))
            d.ellipse([x - 4, y - 4, x + 4, y + 4], fill=(255, 252, 230))
        for x, y, r in [(0.25, 0.2, 110), (0.5, 0.32, 150), (0.75, 0.18, 90)]:
            star_shape(d, S * x, S * y, r)
        hills(d, S * 0.68, 90, (44, 74, 66), 6, 3)
        b, a, f = CRITTERS["nocturnix"]
        critter(d, S * 0.5, S * 0.72, 2.8, b, a, f)
        text_band(img, ["A STAR has points that twinkle bright —", "Nocturnix counts them every night!"])
    page("shape-star", p_shape_star)

    # ---- activities (2 pages)
    def p_act_flowers(img, d):
        scene_base(d, "day")
        random.seed(6)
        for i in range(7):
            x = S * (0.15 + (i % 4) * 0.23)
            y = S * (0.5 + (i // 4) * 0.16)
            d.rectangle([x - 8, y, x + 8, y + 100], fill=(78, 138, 58))
            d.ellipse([x - 55, y - 90, x + 55, y + 20],
                      fill=[(255, 158, 192), (255, 226, 122), (255, 255, 255)][i % 3])
        b, a, f = CRITTERS["flufftail"]
        critter(d, S * 0.84, S * 0.68, 2.2, b, a, f)
        text_band(img, ["Flufftail planted flowers — what a show!", "How many flowers? Count them slow!", "(Did you find all SEVEN? Well done!)"])
    page("act-flowers", p_act_flowers)

    def p_act_more(img, d):
        sky(d, "cream")
        d.text((S // 2, S * 0.08), "Which side has MORE?", font=F_H, fill=(70, 74, 88), anchor="mm")
        d.line([S * 0.5, S * 0.16, S * 0.5, S * 0.86], fill=(200, 200, 210), width=10)
        b, a, f = CRITTERS["pebblit"]
        for (x, y) in [(0.25, 0.35), (0.35, 0.5), (0.2, 0.62)]:
            critter(d, S * x, S * y, 2.0, b, a, f)
        b, a, f = CRITTERS["aquaphin"]
        for (x, y) in [(0.65, 0.3), (0.8, 0.36), (0.62, 0.5), (0.78, 0.56), (0.7, 0.68)]:
            critter(d, S * x, S * y, 2.0, b, a, f)
        text_band(img, ["THREE Pebblits or FIVE Aquaphins?", "Point to the side with more friends!"], 0.92)
    page("act-more", p_act_more)

    # ---- certificate + about
    def p_cert(img, d):
        sky(d, "lilac")
        d.rounded_rectangle([S * 0.08, S * 0.1, S * 0.92, S * 0.9], radius=60,
                            outline=(180, 101, 47), width=16, fill=(255, 253, 245))
        star_shape(d, S * 0.5, S * 0.24, 130, (240, 205, 120))
        d.text((S // 2, S * 0.4), "HOORAY!", font=F_H, fill=(180, 101, 47), anchor="mm")
        d.text((S // 2, S * 0.5), "can count from 1 to 10", font=F_TEXT, fill=(70, 74, 88), anchor="mm")
        d.line([S * 0.25, S * 0.46, S * 0.75, S * 0.46], fill=(150, 150, 170), width=6)
        d.text((S // 2, S * 0.58), "with all ten friends of Wildhaven!", font=F_TEXT, fill=(70, 74, 88), anchor="mm")
        for x, nm in zip([0.3, 0.5, 0.7], ["flufftail", "zephyrix", "cinderpup"]):
            b, a, f = CRITTERS[nm]
            critter(d, S * x, S * 0.76, 1.9, b, a, f)
    page("cert", p_cert)

    def p_about(img, d):
        sky(d, "night")
        for i in range(80):
            x, y = random.randint(0, S), random.randint(0, int(S * 0.5))
            d.ellipse([x - 3, y - 3, x + 3, y + 3], fill=(255, 252, 230))
        moon(d, S * 0.8, S * 0.14, 120)
        hills(d, S * 0.72, 90, (44, 74, 66), 6, 3)
        lines = ["Want more Wildhaven?", "",
                 "Read the bedtime story:", "Goodnight, Wildhaven", "",
                 "And play the cozy games", "with a grown-up:",
                 "Wildhaven: Creature Park & Critter Isles"]
        y = S * 0.14
        for line in lines:
            d.text((S // 2, y), line, font=F_TEXT, fill=(226, 232, 246), anchor="mm")
            y += 148
        for x, nm in zip([0.3, 0.5, 0.7], ["mossback", "bubbletide", "nocturnix"]):
            b, a, f = CRITTERS[nm]
            critter(d, S * x, S * 0.85, 2.0, b, a, f)
    page("about", p_about)

    # ---- assemble PDF
    imgs = [Image.open(p).convert("RGB") for p in _pages]
    pdf_path = os.path.join(ROOT, "dist", "Count-with-the-Critters-Book.pdf")
    imgs[0].save(pdf_path, save_all=True, append_images=imgs[1:], resolution=300.0)
    print("PDF:", pdf_path, os.path.getsize(pdf_path) // 1024 // 1024, "MB,", len(imgs), "pages")

    # ---- covers
    cover = imgs[0].copy()
    cover.save(os.path.join(OUT2, "cover-ebook-2550x2550.jpg"), quality=95, dpi=(300, 300))
    # wraparound: back blurb + spine + front
    DPI = 300
    TRIM, BLEED = S, int(0.125 * DPI)
    SPINE = int(len(imgs) * 0.002252 * DPI)
    W, H = 2 * (TRIM + BLEED) + SPINE, TRIM + 2 * BLEED
    wrap = Image.new("RGB", (W, H))
    dw = ImageDraw.Draw(wrap)
    top, bot = SKIES["day"]
    for y in range(H):
        t = y / H
        dw.line([(0, y), (W, y)],
                fill=tuple(int(top[i] + (bot[i] - top[i]) * t) for i in range(3)))
    back_w = TRIM + BLEED
    blurb = ["Can you count to TEN with the", "critters of Wildhaven?",
             "", "Hop with ONE Flufftail, splash with", "THREE Aquaphins, race SIX zoomy",
             "Cinderpups - then discover colors,", "shapes, and counting games!",
             "", "A bright learning adventure for", "ages 2-5, from the world of",
             "Goodnight, Wildhaven."]
    fb = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 72)
    y = int(H * 0.14)
    for line in blurb:
        dw.text((back_w // 2, y), line, font=fb, fill=(40, 52, 66), anchor="mm")
        y += 106
    b, a, f = CRITTERS["pebblit"]
    critter(dw, back_w * 0.3, H * 0.78, 2.2, b, a, f)
    dw.rectangle([back_w, 0, back_w + SPINE, H], fill=(180, 101, 47))
    wrap.paste(cover.resize((TRIM, TRIM)), (back_w + SPINE + BLEED, BLEED))
    wrap.save(os.path.join(OUT2, "cover-paperback-wrap.pdf"), resolution=300.0)
    wrap.save(os.path.join(OUT2, "cover-paperback-wrap.jpg"), quality=92, dpi=(300, 300))
    print("covers ->", OUT2, f"(wrap {W}x{H}, {len(imgs)}-page spine)")


if __name__ == "__main__":
    main()
