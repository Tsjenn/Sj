#!/usr/bin/env python3
"""SKYLINE itch.io cover (630x500).

Built from a real in-game frame (marketing/skyline/shot-raw-cover.png, captured
at exactly 2x the cover size) with the title locked up over a dark scrim, so
the store page shows the game as it actually looks.
"""

import os

from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "marketing", "skyline")
SRC = os.path.join(OUT, "shot-raw-cover.png")
W, H = 630, 500


def font(sz):
    for p in ("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",):
        if os.path.exists(p):
            return ImageFont.truetype(p, sz)
    return ImageFont.load_default()


def main():
    base = Image.open(SRC).convert("RGB").resize((W, H), Image.LANCZOS)

    # darken the top third so the title stays legible over the skyline
    scrim = Image.new("L", (W, H), 0)
    sd = ImageDraw.Draw(scrim)
    for y in range(H):
        a = 205 if y < 120 else max(0, int(205 * (1 - (y - 120) / 90.0)))
        sd.line([(0, y), (W, y)], fill=a)
    base = Image.composite(Image.new("RGB", (W, H), (26, 18, 48)), base, scrim)

    d = ImageDraw.Draw(base)

    def centered(y, txt, f, fill, stroke=(26, 18, 48), sw=3):
        bb = d.textbbox((0, 0), txt, font=f)
        x = (W - (bb[2] - bb[0])) / 2 - bb[0]
        d.text((x, y), txt, font=f, fill=fill, stroke_width=sw, stroke_fill=stroke)

    centered(28, "SKYLINE", font(84), (255, 226, 174))
    centered(126, "Swing · Flow · Deliver the light", font(21), (240, 228, 250), (26, 18, 48), 2)

    # badge so the "online" hook survives being shrunk to a store thumbnail
    tag = "RACE THE WORLD WITH FLIGHT CODES"
    f2 = font(15)
    bb = d.textbbox((0, 0), tag, font=f2)
    tw, th = bb[2] - bb[0], bb[3] - bb[1]
    bx0 = (W - tw) / 2 - 14
    by0 = H - th - 34
    d.rounded_rectangle([bx0, by0, bx0 + tw + 28, by0 + th + 18], radius=999,
                        fill=(255, 126, 90))
    d.text((bx0 + 14 - bb[0], by0 + 9 - bb[1]), tag, font=f2, fill=(255, 255, 255))

    p = os.path.join(OUT, "cover-630x500.png")
    base.save(p)
    print("wrote", p)


if __name__ == "__main__":
    main()
