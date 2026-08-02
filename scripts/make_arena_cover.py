#!/usr/bin/env python3
"""Wildhaven Arena itch.io cover (630x500) — purple arena night, crowned
critter between crossed swords, bold title."""

import os

from PIL import Image, ImageDraw

import make_book as B

OUT = os.path.join(B.ROOT, "marketing", "arena")
W, H = 630, 500
S = 3          # supersample
W2, H2 = W * S, H * S

img = Image.new("RGB", (W2, H2))
d = ImageDraw.Draw(img)

# night-purple gradient sky
for y in range(H2):
    t = y / H2
    d.line([(0, y), (W2, y)], fill=(int(38 + 70 * t), int(18 + 34 * t), int(66 + 92 * t)))

# stars
import random
random.seed(7)
for _ in range(90):
    x, y = random.randint(0, W2), random.randint(0, int(H2 * 0.55))
    r = random.randint(2, 5)
    d.ellipse([x - r, y - r, x + r, y + r], fill=(255, 246, 214))

# arena ground — glowing ring
d.ellipse([W2*0.08, H2*0.62, W2*0.92, H2*1.10], fill=(58, 30, 92))
d.ellipse([W2*0.14, H2*0.68, W2*0.86, H2*1.04], outline=(255, 214, 92), width=10)

# three critters: champion center + two rivals
B.critter(d, W2*0.50, H2*0.72, W2/240, (247, 202, 136), (236, 148, 90), "fox")
B.critter(d, W2*0.24, H2*0.80, W2/340, (150, 214, 120), (96, 170, 80), None)
B.critter(d, W2*0.76, H2*0.80, W2/340, (130, 190, 240), (80, 140, 210), "fin")

# crown on champion
cx, cy = W2*0.50, H2*0.545
w = W2*0.055
d.polygon([(cx-w, cy), (cx-w*0.55, cy-H2*0.045), (cx-w*0.18, cy-H2*0.012),
           (cx, cy-H2*0.062), (cx+w*0.18, cy-H2*0.012), (cx+w*0.55, cy-H2*0.045),
           (cx+w, cy), (cx+w*0.8, cy+H2*0.028), (cx-w*0.8, cy+H2*0.028)],
          fill=(255, 214, 92))

img = img.resize((W, H), Image.LANCZOS)
d = ImageDraw.Draw(img)

# title
from PIL import ImageFont
def font(sz):
    for p in ("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",):
        if os.path.exists(p):
            return ImageFont.truetype(p, sz)
    return ImageFont.load_default()

def centered(y, txt, f, fill, stroke=None):
    bb = d.textbbox((0, 0), txt, font=f)
    x = (W - (bb[2] - bb[0])) / 2
    if stroke:
        d.text((x, y), txt, font=f, fill=fill, stroke_width=3, stroke_fill=stroke)
    else:
        d.text((x, y), txt, font=f, fill=fill)

centered(38, "WILDHAVEN", font(64), (255, 255, 255), (40, 18, 66))
centered(108, "ARENA", font(74), (255, 214, 92), (40, 18, 66))
centered(196, "Catch. Train. Duel the world.", font(24), (232, 222, 250))

os.makedirs(OUT, exist_ok=True)
img.save(os.path.join(OUT, "cover-630x500.png"))
print("wrote", os.path.join(OUT, "cover-630x500.png"))
