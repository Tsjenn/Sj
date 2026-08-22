#!/usr/bin/env python3
"""Cover images for Critter Tower (Playgama / portal listings).

Outputs (exact sizes the Playgama form demands):
- marketing/game6-cover-square.png    800x800
- marketing/game6-cover-portrait.png  1080x1920

Art is generated from the same sources as the game itself:
critters2.py sprites + the in-game palette, so the cover honestly
shows what the player gets.

    python3 scripts/make_game6_covers.py
"""

import os
import sys

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import critters2  # noqa: E402

OUT = os.path.join(ROOT, "marketing")
FB = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

SKY_TOP, SKY_BOT = (142, 208, 240), (253, 243, 224)
CREAM, ORANGE, INKA = (255, 244, 228), (255, 196, 107), (32, 26, 40)
BLOCKS = [("flufftail", (162, 210, 134)), ("aquaphin", (132, 192, 228)),
          ("glimmerwing", (192, 160, 232)), ("emberling", (244, 158, 104)),
          ("zephyrix", (248, 220, 124)), ("pebblit", (184, 180, 192))]


def font(sz):
    return ImageFont.truetype(FB, sz)


def mixc(a, b, f):
    return tuple(int(a[i] + (b[i] - a[i]) * f) for i in range(3))


def sky(d, w, h):
    for y in range(h):
        d.line([(0, y), (w, y)], fill=mixc(SKY_TOP, SKY_BOT, y / h))


def sun(img, cx, cy, r):
    glow = Image.new("RGBA", img.size, (0, 0, 0, 0))
    g = ImageDraw.Draw(glow)
    g.ellipse([cx - r * 2.1, cy - r * 2.1, cx + r * 2.1, cy + r * 2.1],
              fill=(255, 236, 170, 110))
    glow = glow.filter(ImageFilter.GaussianBlur(r * 0.6))
    img.alpha_composite(glow)
    d = ImageDraw.Draw(img)
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(255, 233, 168, 255))


def cloud(d, x, y, s, a=235):
    col = (255, 255, 255, a)
    d.ellipse([x - s, y - s * 0.6, x + s, y + s * 0.6], fill=col)
    d.ellipse([x - s * 1.8, y - s * 0.35, x - s * 0.4, y + s * 0.6], fill=col)
    d.ellipse([x + s * 0.4, y - s * 0.35, x + s * 1.8, y + s * 0.6], fill=col)


def hills(d, w, h):
    back = mixc(SKY_BOT, (0, 0, 0), 0.09)
    front = mixc(SKY_BOT, (0, 0, 0), 0.17)
    d.ellipse([-w * 0.35, h * 0.9, w * 0.75, h * 1.35], fill=back)
    d.ellipse([w * 0.35, h * 0.94, w * 1.45, h * 1.3], fill=front)


def block(img, cx_, cy_, w, h, col, r=None):
    """Rounded slab with the in-game gradient + highlight, soft shadow."""
    r = r or int(h * 0.24)
    pad = 30
    tile = Image.new("RGBA", (w + pad * 2, h + pad * 2), (0, 0, 0, 0))
    td = ImageDraw.Draw(tile)
    # shadow
    sh = Image.new("RGBA", tile.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle(
        [pad + 6, pad + 9, pad + w + 6, pad + h + 9], r, fill=(20, 16, 24, 90))
    sh = sh.filter(ImageFilter.GaussianBlur(6))
    tile.alpha_composite(sh)
    # gradient body under rounded mask
    body = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    bd = ImageDraw.Draw(body)
    top, bot = mixc(col, (255, 255, 255), 0.22), mixc(col, (0, 0, 0), 0.14)
    for y in range(h):
        f = y / h
        c = mixc(top, col, f / 0.45) if f < 0.45 else mixc(col, bot, (f - 0.45) / 0.55)
        bd.line([(0, y), (w, y)], fill=c)
    mask = Image.new("L", (w, h), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, w - 1, h - 1], r, fill=255)
    tile.paste(body, (pad, pad), mask)
    td.rounded_rectangle([pad, pad, pad + w, pad + h], r,
                         outline=(48, 40, 48, 80), width=3)
    td.rounded_rectangle([pad + 10, pad + 7, pad + w - 10, pad + int(h * 0.28)],
                         int(h * 0.12), fill=(255, 255, 255, 78))
    img.alpha_composite(tile, (int(cx_ - w / 2 - pad), int(cy_ - pad)))


def critter(img, species, px, cx_, bottom):
    spr = critters2.render(species, px)
    img.alpha_composite(spr, (int(cx_ - px / 2), int(bottom - px)))


def title(img, cx_, y, sz):
    d = ImageDraw.Draw(img)
    f = font(sz)
    for word, col in (("CRITTER", CREAM), ("TOWER", ORANGE)):
        d.text((cx_ + 5, y + 5), word, font=f, fill=(32, 26, 40, 90), anchor="ma")
        d.text((cx_, y), word, font=f, fill=col, anchor="ma",
               stroke_width=max(3, sz // 28), stroke_fill=(58, 48, 66))
        y += int(sz * 1.08)
    return y


def tagline(img, cx_, y, sz, txt="TAP. STACK. DON'T TOPPLE!"):
    d = ImageDraw.Draw(img)
    d.text((cx_, y), txt, font=font(sz), fill=(90, 76, 92), anchor="ma")


def tower(img, cx_, base_y, bw, bh, n, jitter):
    """n stacked blocks, slightly offset like a real run; critter on top."""
    y = base_y
    for i in range(n):
        name, col = BLOCKS[i % len(BLOCKS)]
        off = jitter[i % len(jitter)]
        block(img, cx_ + off, y - bh, bw - i * 6, bh, col)
        y -= bh - 4
    top_off = jitter[(n - 1) % len(jitter)]
    # after the loop y sits 4px below the top block's top edge
    return cx_ + top_off, y - 4


def make(w, h, path):
    img = Image.new("RGBA", (w, h))
    d = ImageDraw.Draw(img)
    sky(d, w, h)
    sun(img, w * 0.82, h * 0.10, w * 0.055)
    d = ImageDraw.Draw(img)
    cloud(d, w * 0.16, h * 0.07, w * 0.05)
    cloud(d, w * 0.62, h * 0.15, w * 0.04, 200)
    cloud(d, w * 0.30, h * 0.24, w * 0.035, 170)
    hills(d, w, h)

    if h > w:                                    # portrait 1080x1920
        ty = title(img, w / 2, h * 0.055, int(w * 0.165))
        tagline(img, w / 2, ty + 26, int(w * 0.042))
        bw, bh = int(w * 0.56), int(w * 0.115)
        topx, topy = tower(img, w / 2, int(h * 0.945), bw, bh, 6,
                           [0, 14, -10, 6, -14, 8])
        critter(img, "flufftail", int(w * 0.34), topx, topy + 12)
        # a second critter drops in from above, mid-swing
        fx = w * 0.78
        critter(img, "emberling", int(w * 0.22), fx, h * 0.47)
        d = ImageDraw.Draw(img)
        for i in range(3):
            yy = h * 0.48 + i * 26
            d.line([(fx - 26, yy), (fx - 46, yy - 14)], fill=(255, 255, 255, 130), width=6)
            d.line([(fx + 26, yy), (fx + 46, yy - 14)], fill=(255, 255, 255, 130), width=6)
    else:                                        # square 800x800
        title(img, w / 2, h * 0.045, int(w * 0.15))
        bw, bh = int(w * 0.48), int(w * 0.10)
        topx, topy = tower(img, w * 0.42, int(h * 0.99), bw, bh, 4,
                           [0, 12, -8, 6])
        critter(img, "flufftail", int(w * 0.26), topx, topy + 10)
        critter(img, "aquaphin", int(w * 0.19), w * 0.80, h * 0.66)

    img.convert("RGB").save(path, "PNG")
    print("wrote", path, Image.open(path).size)


def main():
    make(800, 800, os.path.join(OUT, "game6-cover-square.png"))
    make(1080, 1920, os.path.join(OUT, "game6-cover-portrait.png"))


if __name__ == "__main__":
    main()
