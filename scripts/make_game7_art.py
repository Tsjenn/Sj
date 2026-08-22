#!/usr/bin/env python3
"""Ball sprites for Critter Drop (game7) — the drop-and-merge game.

Each tier is a glossy bubble in the species color with the critter
inside, pre-rendered so the game just drawImage()s. Tier order goes
smallest -> largest: pebble to night-owl.

    python3 scripts/make_game7_art.py
"""

import os
import sys

from PIL import Image, ImageDraw, ImageFilter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import critters2  # noqa: E402

OUT = os.path.join(ROOT, "game7", "img")

# smallest -> largest (the merge chain)
CHAIN = [
    ("pebblit",     (184, 180, 192)),
    ("flufftail",   (162, 210, 134)),
    ("bubbletide",  (166, 218, 218)),
    ("aquaphin",    (132, 192, 228)),
    ("cinderpup",   (224, 128, 106)),
    ("emberling",   (244, 158, 104)),
    ("mossback",    (158, 184, 122)),
    ("zephyrix",    (248, 220, 124)),
    ("glimmerwing", (192, 160, 232)),
    ("nocturnix",   (112, 118, 170)),
]


def mixc(a, b, f):
    return tuple(int(a[i] + (b[i] - a[i]) * f) for i in range(3))


def ball(species, col, px):
    """Glossy bubble of diameter px with the critter inside."""
    ss = 2
    S = px * ss
    img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    # radial-ish body: light top-left to deep bottom-right
    top = mixc(col, (255, 255, 255), 0.35)
    bot = mixc(col, (30, 26, 46), 0.25)
    for y in range(S):
        f = y / S
        d.line([(0, y), (S, y)], fill=mixc(top, bot, f) + (255,))
    mask = Image.new("L", (S, S), 0)
    ImageDraw.Draw(mask).ellipse([0, 0, S - 1, S - 1], fill=255)
    img.putalpha(mask)
    # critter, clipped to the bubble, sitting low
    spr = critters2.render(species, int(S * 0.78))
    tmp = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    tmp.alpha_composite(spr, (int(S / 2 - spr.width / 2), int(S * 0.56 - spr.height / 2)))
    tmp.putalpha(Image.composite(tmp.split()[3], Image.new("L", (S, S), 0), mask))
    img.alpha_composite(tmp)
    # inner rim shadow + gloss
    rim = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    rd = ImageDraw.Draw(rim)
    rd.ellipse([0, 0, S - 1, S - 1], outline=(30, 26, 46, 110), width=max(3, S // 60))
    img.alpha_composite(rim)
    gloss = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    gd = ImageDraw.Draw(gloss)
    gd.ellipse([S * 0.16, S * 0.06, S * 0.62, S * 0.34], fill=(255, 255, 255, 95))
    gloss = gloss.filter(ImageFilter.GaussianBlur(S * 0.02))
    img.alpha_composite(gloss)
    return img.resize((px, px), Image.LANCZOS)


def main():
    os.makedirs(OUT, exist_ok=True)
    # export size scales with tier so big balls stay crisp
    for i, (name, col) in enumerate(CHAIN):
        px = 96 + i * 26          # 96 .. 330
        ball(name, col, px).save(os.path.join(OUT, "b%d.png" % i))
        print("tier", i, name, px)
    total = sum(os.path.getsize(os.path.join(OUT, f)) for f in os.listdir(OUT))
    print("total img bytes:", total // 1024, "KB")


if __name__ == "__main__":
    main()
