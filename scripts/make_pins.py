#!/usr/bin/env python3
"""Generate the Pinterest pin pack: branded 1000x1500 pins for every product.

Each pin: soft brand background, product image card, bold headline, CTA pill,
and site footer. Outputs to marketing/pins/.

Run:  python3 scripts/make_pins.py
(expects wall-art renders in book/wallart/ — run make_wallart.py first)
"""

import os

from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "marketing", "pins")
W, H = 1000, 1500

F_BIG = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 78)
F_MED = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 44)
F_SM = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 34)

SITE = "tsjenn.github.io/Sj"


def pin(name, bg, img_path, headline_lines, cta, cta_color=(180, 101, 47), text_color=(52, 58, 66)):
    canvas = Image.new("RGB", (W, H), bg)
    d = ImageDraw.Draw(canvas)
    # product image card
    src = Image.open(os.path.join(ROOT, img_path)).convert("RGB")
    card_w = W - 120
    ratio = min(card_w / src.width, (H * 0.52) / src.height)
    nw, nh = int(src.width * ratio), int(src.height * ratio)
    src = src.resize((nw, nh), Image.LANCZOS)
    cx = (W - nw) // 2
    cy = 90
    # soft shadow + white frame
    d.rounded_rectangle([cx - 14 + 10, cy - 14 + 12, cx + nw + 14 + 10, cy + nh + 14 + 12],
                        radius=24, fill=(0, 0, 0, 40) if canvas.mode == "RGBA" else
                        tuple(max(0, c - 28) for c in bg))
    d.rounded_rectangle([cx - 14, cy - 14, cx + nw + 14, cy + nh + 14],
                        radius=24, fill=(255, 255, 255))
    canvas.paste(src, (cx, cy))
    # headline
    y = cy + nh + 110
    for line in headline_lines:
        d.text((W // 2, y), line, font=F_BIG, fill=text_color, anchor="mm")
        y += 100
    # CTA pill
    tw = d.textlength(cta, font=F_MED)
    pw = tw + 90
    d.rounded_rectangle([(W - pw) / 2, y + 10, (W + pw) / 2, y + 100],
                        radius=45, fill=cta_color)
    d.text((W // 2, y + 55), cta, font=F_MED, fill=(255, 255, 255), anchor="mm")
    # footer
    d.rectangle([0, H - 80, W, H], fill=(52, 58, 66))
    d.text((W // 2, H - 40), SITE, font=F_SM, fill=(255, 216, 112), anchor="mm")
    canvas.save(os.path.join(OUT, name + ".png"))
    print("pin:", name)


def main():
    os.makedirs(OUT, exist_ok=True)
    pin("wallart-set", (238, 244, 238), "marketing/wallart/preview.jpg",
        ["13 Nursery Prints", "One Tiny Price"], "INSTANT DOWNLOAD ↓")
    pin("wallart-dreamer", (231, 234, 244), "book/wallart/goodnight-dreamer-8x10.jpg",
        ["Free Your Nursery", "Walls Tonight"], "PRINT AT HOME")
    pin("book-bedtime", (24, 34, 56), "marketing/book/cover-ebook-2550x2550.jpg",
        ["The Bedtime Story", "Kids Ask For Twice"], "READ IT TONIGHT",
        cta_color=(180, 101, 47), text_color=(255, 250, 235))
    pin("book-counting", (250, 246, 228), "marketing/book2/cover-ebook-2550x2550.jpg",
        ["Count to 10 with", "the Critters!"], "FOR AGES 2–5")
    pin("game-wildhaven", (222, 240, 236), "marketing/wildhaven/screenshot-1-park.png",
        ["Build Your Own", "Creature Park"], "PLAY FREE IN BROWSER ▶", (42, 111, 106))
    pin("game-critter", (222, 236, 246), "marketing/itch/cover-630x500.png",
        ["A Cozy Game You", "Can Play Right Now"], "NO INSTALL — TAP & PLAY", (42, 111, 106))
    print("done ->", OUT)


if __name__ == "__main__":
    main()
