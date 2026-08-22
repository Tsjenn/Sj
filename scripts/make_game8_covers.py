#!/usr/bin/env python3
"""Cover images for Critter Beat (Playgama / portal listings).

- marketing/game8-cover-square.png    800x800
- marketing/game8-cover-portrait.png  1080x1920

Stage-dark look matching the game: lane glow, hit bar, the four lane
critters as falling tiles.

    python3 scripts/make_game8_covers.py
"""

import os

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMG = os.path.join(ROOT, "game8", "img")
OUT = os.path.join(ROOT, "marketing")
FB = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

TOP, BOT = (36, 31, 51), (58, 46, 78)
CREAM, ORANGE = (255, 244, 228), (255, 196, 107)
LCOL = [(162, 210, 134), (132, 192, 228), (244, 158, 104), (192, 160, 232)]
BALLS = [Image.open(os.path.join(IMG, "lane%d.png" % i)).convert("RGBA") for i in range(4)]


def font(sz):
    return ImageFont.truetype(FB, sz)


def mixc(a, b, f):
    return tuple(int(a[i] + (b[i] - a[i]) * f) for i in range(3))


def stage(img, w, h, hity):
    d = ImageDraw.Draw(img)
    for y in range(h):
        d.line([(0, y), (w, y)], fill=mixc(TOP, BOT, y / h))
    lw = w / 4
    for l in range(4):
        if l % 2 == 0:
            d.rectangle([l * lw, 0, (l + 1) * lw, h], fill=mixc(TOP, (255, 255, 255), 0.03) + (255,))
    # beat glow at the hit bar
    glow = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ImageDraw.Draw(glow).ellipse([w * 0.1, hity - w * 0.28, w * 0.9, hity + w * 0.28],
                                 fill=(255, 244, 228, 60))
    glow = glow.filter(ImageFilter.GaussianBlur(w * 0.08))
    img.alpha_composite(glow)
    d = ImageDraw.Draw(img)
    d.rectangle([0, hity - 22, w, hity + 22], fill=(255, 244, 228, 40))
    d.rectangle([0, hity - 2, w, hity + 2], fill=(255, 244, 228, 170))
    for l in range(4):
        d.rectangle([l * lw + 8, hity + 26, (l + 1) * lw - 8, hity + 32], fill=LCOL[l] + (150,))
    for s in range(40):
        d.point([(s * 727) % w, (s * 331) % int(h * 0.7)], fill=(255, 244, 228, 160))


def ball(img, lane, cx_, cy_, dia, glow=False):
    if glow:
        gl = Image.new("RGBA", img.size, (0, 0, 0, 0))
        ImageDraw.Draw(gl).ellipse([cx_ - dia * 0.7, cy_ - dia * 0.7, cx_ + dia * 0.7, cy_ + dia * 0.7],
                                   fill=LCOL[lane] + (110,))
        gl = gl.filter(ImageFilter.GaussianBlur(dia * 0.12))
        img.alpha_composite(gl)
    b = BALLS[lane].resize((dia, dia), Image.LANCZOS)
    img.alpha_composite(b, (int(cx_ - dia / 2), int(cy_ - dia / 2)))


def title(img, cx_, y, sz):
    d = ImageDraw.Draw(img)
    f = font(sz)
    for word, col in (("CRITTER", CREAM), ("BEAT", ORANGE)):
        d.text((cx_ + 4, y + 4), word, font=f, fill=(10, 8, 20, 160), anchor="ma")
        d.text((cx_, y), word, font=f, fill=col, anchor="ma")
        y += int(sz * 1.06)
    return y


def make(w, h, path):
    img = Image.new("RGBA", (w, h))
    hity = h * 0.78
    stage(img, w, h, hity)
    lw = w / 4

    if h > w:                                    # portrait
        ty = title(img, w / 2, h * 0.05, int(w * 0.17))
        ImageDraw.Draw(img).text((w / 2, ty + 24), "YOUR TAPS PLAY THE SONG",
                                 font=font(int(w * 0.042)), fill=CREAM + (220,), anchor="ma")
        ball(img, 0, lw * 0.5, h * 0.36, int(lw * 0.62))
        ball(img, 2, lw * 2.5, h * 0.38, int(lw * 0.62))
        ball(img, 3, lw * 3.5, h * 0.48, int(lw * 0.62))
        ball(img, 1, lw * 1.5, hity, int(lw * 0.72), glow=True)   # the one you're hitting
        # burst at the hit
        d = ImageDraw.Draw(img)
        for i in range(10):
            import math
            a = i / 10 * 6.28
            x1 = lw * 1.5 + math.cos(a) * lw * 0.45
            y1 = hity + math.sin(a) * lw * 0.45
            d.ellipse([x1 - 6, y1 - 6, x1 + 6, y1 + 6], fill=LCOL[1] + (200,))
    else:                                        # square
        title(img, w / 2, h * 0.04, int(w * 0.15))
        ball(img, 0, lw * 0.5, h * 0.44, int(lw * 0.6))
        ball(img, 3, lw * 3.5, h * 0.52, int(lw * 0.6))
        ball(img, 2, lw * 2.5, h * 0.40, int(lw * 0.6))
        ball(img, 1, lw * 1.5, hity, int(lw * 0.7), glow=True)

    img.convert("RGB").save(path, "PNG")
    print("wrote", path, Image.open(path).size)


def main():
    make(800, 800, os.path.join(OUT, "game8-cover-square.png"))
    make(1080, 1920, os.path.join(OUT, "game8-cover-portrait.png"))


if __name__ == "__main__":
    main()
