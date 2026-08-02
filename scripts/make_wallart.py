#!/usr/bin/env python3
"""Generate the 'Wildhaven Nursery Wall Art' printable set for Etsy.

13 designs (10 critter portraits + 3 nursery quotes), each rendered in two
standard frame ratios at 300 dpi:
  4:5  -> 2400x3000  (prints 4x5, 8x10, 16x20)
  2:3  -> 2400x3600  (prints 4x6, 8x12, 12x18)

  dist/Wildhaven-Wall-Art-Set.zip      the sellable set (26 JPGs + guide)
  marketing/wallart/preview.jpg        Etsy listing collage

Run:  python3 scripts/make_wallart.py
"""

import os
import random
import zipfile

from PIL import Image, ImageDraw, ImageFont

from make_book import critter, star_shape, CRITTERS

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTDIR = os.path.join(ROOT, "marketing", "wallart")
TMP = os.path.join(ROOT, "book", "wallart")

RATIOS = {"8x10": (2400, 3000), "8x12": (2400, 3600)}

F_NAME = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
F_BODY = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

PALETTES = {
    "flufftail": (238, 246, 232), "pebblit": (240, 240, 242),
    "aquaphin": (230, 242, 248), "emberling": (250, 238, 228),
    "mossback": (236, 242, 232), "bubbletide": (232, 246, 246),
    "zephyrix": (250, 246, 228), "cinderpup": (248, 234, 230),
    "glimmerwing": (242, 236, 248), "nocturnix": (231, 234, 244),
}

TAGLINES = {
    "flufftail": "the meadow hopper", "pebblit": "the boulder dreamer",
    "aquaphin": "the pond dancer", "emberling": "the little lantern",
    "mossback": "the gentle giant", "bubbletide": "the bubble blower",
    "zephyrix": "the wind racer", "cinderpup": "the spark chaser",
    "glimmerwing": "the star painter", "nocturnix": "the night guardian",
}


def portrait(species, W, H):
    img = Image.new("RGB", (W, H), PALETTES[species])
    d = ImageDraw.Draw(img)
    random.seed(hash(species) % 9999)
    # soft backdrop disc + scattered stars
    cx, cy = W // 2, int(H * 0.42)
    r = int(W * 0.34)
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(255, 253, 246))
    for _ in range(10):
        x, y = random.randint(120, W - 120), random.randint(120, int(H * 0.7))
        star_shape(d, x, y, random.choice([22, 30, 40]), (232, 210, 150))
    b, a, f = CRITTERS[species]
    critter(d, cx, cy + int(r * 0.10), W / 300, b, a, f)
    fn = ImageFont.truetype(F_NAME, int(W * 0.085))
    ft = ImageFont.truetype(F_BODY, int(W * 0.038))
    d.text((cx, int(H * 0.80)), species.capitalize(), font=fn, fill=(72, 76, 90), anchor="mm")
    d.text((cx, int(H * 0.865)), "— " + TAGLINES[species] + " —", font=ft, fill=(140, 144, 158), anchor="mm")
    return img


QUOTES = [
    ("goodnight-dreamer", (231, 234, 244), ["Goodnight,", "little dreamer"], "moon"),
    ("wild-wonderful", (238, 246, 232), ["You are wild", "and wonderful"], "flufftail"),
    ("catch-the-light", (250, 238, 228), ["Catch", "the light"], "star"),
]


def quote_print(key, bg, lines, motif, W, H):
    img = Image.new("RGB", (W, H), bg)
    d = ImageDraw.Draw(img)
    random.seed(hash(key) % 9999)
    for _ in range(8):
        x, y = random.randint(120, W - 120), random.randint(120, H - 200)
        star_shape(d, x, y, random.choice([20, 26, 34]), (232, 210, 150))
    cy = int(H * 0.32)
    if motif == "moon":
        r = int(W * 0.2)
        d.ellipse([W // 2 - r, cy - r, W // 2 + r, cy + r], fill=(255, 240, 200))
        d.ellipse([W // 2 - r + 24, cy - r + 24, W // 2 + r - 24, cy + r - 24], fill=(255, 246, 218))
    elif motif == "star":
        star_shape(d, W // 2, cy, int(W * 0.19), (250, 214, 120))
    else:
        b, a, f = CRITTERS[motif]
        critter(d, W // 2, cy + 40, W / 340, b, a, f)
    fn = ImageFont.truetype(F_NAME, int(W * 0.1))
    y = int(H * 0.62)
    for line in lines:
        d.text((W // 2, y), line, font=fn, fill=(72, 76, 90), anchor="mm")
        y += int(W * 0.13)
    return img


GUIDE = """WILDHAVEN NURSERY WALL ART — Thank you for your purchase!

WHAT'S INCLUDED
13 designs x 2 sizes = 26 high-resolution JPG files (300 dpi):
  * 8x10 folder  - prints perfectly at 4x5", 8x10", 16x20"
  * 8x12 folder  - prints perfectly at 4x6", 8x12", 12x18"

HOW TO PRINT
* At home: any color printer, "photo" or "best" quality, on cardstock
  or matte photo paper.
* Print shop / online: upload the JPG to any print service and choose
  your size. The files are sharp up to large poster sizes.

LICENSE - PERSONAL USE
Print as many copies as you like for your own home or as gifts.
Do not resell, redistribute, or re-upload the files or prints.

From the world of "Goodnight, Wildhaven" - the bedtime storybook.
"""


def main():
    os.makedirs(OUTDIR, exist_ok=True)
    os.makedirs(TMP, exist_ok=True)
    files = []
    for ratio, (W, H) in RATIOS.items():
        for sp in CRITTERS.keys():
            img = portrait(sp, W, H)
            path = os.path.join(TMP, "%s-%s.jpg" % (sp, ratio))
            img.save(path, quality=92, dpi=(300, 300))
            files.append((path, "%s/%s.jpg" % (ratio, sp.capitalize())))
        for key, bg, lines, motif in QUOTES:
            img = quote_print(key, bg, lines, motif, W, H)
            path = os.path.join(TMP, "%s-%s.jpg" % (key, ratio))
            img.save(path, quality=92, dpi=(300, 300))
            files.append((path, "%s/%s.jpg" % (ratio, key)))
        print("rendered ratio", ratio)

    zpath = os.path.join(ROOT, "dist", "Wildhaven-Wall-Art-Set.zip")
    with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as z:
        for src, arc in files:
            z.write(src, "Wildhaven-Wall-Art/" + arc)
        z.writestr("Wildhaven-Wall-Art/READ-ME-FIRST.txt", GUIDE)
    print("zip:", zpath, os.path.getsize(zpath) // 1024 // 1024, "MB")

    # Etsy listing collage: 6 designs in a 3x2 grid (2000x1600)
    thumbs = ["flufftail", "nocturnix", "aquaphin"]
    coll = Image.new("RGB", (2000, 1600), (244, 240, 234))
    for i, sp in enumerate(thumbs):
        t = portrait(sp, 2400, 3000).resize((600, 750), Image.LANCZOS)
        coll.paste(t, (70 + i * 640, 60))
    for i, (key, bg, lines, motif) in enumerate(QUOTES):
        t = quote_print(key, bg, lines, motif, 2400, 3000).resize((600, 750), Image.LANCZOS)
        coll.paste(t, (70 + i * 640, 830))
    coll.save(os.path.join(OUTDIR, "preview.jpg"), quality=90)
    print("preview:", os.path.join(OUTDIR, "preview.jpg"))


if __name__ == "__main__":
    main()
