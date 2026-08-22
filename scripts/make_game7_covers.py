#!/usr/bin/env python3
"""Cover images for Critter Drop (Playgama / portal listings).

- marketing/game7-cover-square.png    800x800
- marketing/game7-cover-portrait.png  1080x1920

Uses the game's real ball sprites (game7/img) and palette so the
listing shows exactly what the player gets.

    python3 scripts/make_game7_covers.py
"""

import os

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMG = os.path.join(ROOT, "game7", "img")
OUT = os.path.join(ROOT, "marketing")
FB = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

BG_TOP, BG_BOT = (251, 239, 217), (243, 217, 192)
INK, CORAL = (90, 76, 92), (224, 128, 106)

BALLS = [Image.open(os.path.join(IMG, "b%d.png" % i)).convert("RGBA")
         for i in range(10)]


def font(sz):
    return ImageFont.truetype(FB, sz)


def mixc(a, b, f):
    return tuple(int(a[i] + (b[i] - a[i]) * f) for i in range(3))


def ball(img, tier, cx_, cy_, d):
    """Paste tier ball with soft shadow, centered at (cx_, cy_), diameter d."""
    b = BALLS[tier].resize((d, d), Image.LANCZOS)
    sh = Image.new("RGBA", (d + 40, d + 40), (0, 0, 0, 0))
    ImageDraw.Draw(sh).ellipse([20 + 6, 20 + 10, 20 + d + 6, 20 + d + 10],
                               fill=(60, 40, 40, 70))
    sh = sh.filter(ImageFilter.GaussianBlur(7))
    img.alpha_composite(sh, (int(cx_ - d / 2 - 20), int(cy_ - d / 2 - 20)))
    img.alpha_composite(b, (int(cx_ - d / 2), int(cy_ - d / 2)))


def bg(img, w, h):
    d = ImageDraw.Draw(img)
    for y in range(h):
        d.line([(0, y), (w, y)], fill=mixc(BG_TOP, BG_BOT, y / h))
    # dashed danger line high up
    y0 = int(h * 0.145)
    x = 0
    while x < w:
        d.line([(x, y0), (x + 16, y0)], fill=INK + (60,), width=3)
        x += 30


def title(img, cx_, y, sz):
    d = ImageDraw.Draw(img)
    f = font(sz)
    for word, col in (("CRITTER", INK), ("DROP", CORAL)):
        d.text((cx_ + 4, y + 4), word, font=f, fill=(58, 44, 52, 70), anchor="ma")
        d.text((cx_, y), word, font=f, fill=col, anchor="ma",
               stroke_width=max(3, sz // 30), stroke_fill=(255, 247, 232))
        y += int(sz * 1.06)
    return y


def tagline(img, cx_, y, sz):
    ImageDraw.Draw(img).text((cx_, y), "MATCH TWO OF A KIND", font=font(sz),
                             fill=INK + (230,), anchor="ma")


def motion(img, x, y, s):
    d = ImageDraw.Draw(img)
    for i in range(3):
        yy = y + i * s * 0.55
        d.line([(x - s, yy), (x - s * 1.7, yy - s * 0.35)], fill=(255, 255, 255, 170), width=int(s * 0.16))
        d.line([(x + s, yy), (x + s * 1.7, yy - s * 0.35)], fill=(255, 255, 255, 170), width=int(s * 0.16))


def chain_strip(img, w, y, sw):
    x = (w - sw * 10) / 2
    for i in range(10):
        b = BALLS[i].resize((sw - 6, sw - 6), Image.LANCZOS)
        img.alpha_composite(b, (int(x + i * sw), int(y)))


def make(w, h, path):
    img = Image.new("RGBA", (w, h))
    bg(img, w, h)

    if h > w:                                    # portrait 1080x1920
        ty = title(img, w / 2, h * 0.05, int(w * 0.17))
        tagline(img, w / 2, ty + 24, int(w * 0.045))
        # heap: big pair meeting in the middle + supporters
        floor = h * 0.94
        ball(img, 6, w * 0.24, floor - 130, 260)
        ball(img, 7, w * 0.66, floor - 145, 290)
        ball(img, 9, w * 0.44, floor - 350, 330)   # the star: nocturnix
        ball(img, 4, w * 0.87, floor - 90, 180)
        ball(img, 5, w * 0.10, floor - 80, 170)
        ball(img, 2, w * 0.90, floor - 260, 130)
        # a small one falling in
        ball(img, 1, w * 0.24, h * 0.42, 150)
        motion(img, w * 0.24, h * 0.36, 34)
        chain_strip(img, w, h * 0.965, int(w / 13))
    else:                                        # square 800x800
        title(img, w / 2, h * 0.04, int(w * 0.15))
        floor = h * 0.96
        ball(img, 6, w * 0.26, floor - 105, 210)
        ball(img, 7, w * 0.68, floor - 115, 230)
        ball(img, 9, w * 0.47, floor - 275, 260)
        ball(img, 4, w * 0.90, floor - 75, 150)
        ball(img, 5, w * 0.07, floor - 70, 140)
        ball(img, 1, w * 0.85, h * 0.42, 110)
        motion(img, w * 0.85, h * 0.38, 26)

    img.convert("RGB").save(path, "PNG")
    print("wrote", path, Image.open(path).size)


def main():
    make(800, 800, os.path.join(OUT, "game7-cover-square.png"))
    make(1080, 1920, os.path.join(OUT, "game7-cover-portrait.png"))


if __name__ == "__main__":
    main()
