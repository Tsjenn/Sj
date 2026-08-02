#!/usr/bin/env python3
"""Generate the Wildhaven Redbubble print-on-demand pack.

13 designs as 4500x4500 transparent-background PNGs (large enough for
Redbubble's full product range: apparel, stickers, mugs, cases, prints):
ten critter portraits and three quote designs.

  dist/Wildhaven-Redbubble-Pack.zip
  marketing/redbubble/preview.jpg

Run:  python3 scripts/make_redbubble.py
"""

import os
import zipfile

from PIL import Image, ImageDraw, ImageFont

from make_book import critter, star_shape, moon, CRITTERS

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TMP = os.path.join(ROOT, "book", "redbubble")
OUTDIR = os.path.join(ROOT, "marketing", "redbubble")
S = 4500

F_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

INK = (62, 66, 80)
GOLD = (240, 198, 110)


def critter_design(species, with_name=True):
    img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    u = 26 if with_name else 30
    cy = int(S * (0.44 if with_name else 0.5)) + 11 * u
    critter(d, S // 2, cy, u, *CRITTERS[species])
    if with_name:
        fn = ImageFont.truetype(F_BOLD, int(S * 0.09))
        d.text((S // 2, int(S * 0.88)), species.capitalize(), font=fn, fill=INK, anchor="mm",
                stroke_width=int(S * 0.008), stroke_fill=(255, 255, 255, 235))
    return img


def quote_design(lines, motif):
    img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    cy = int(S * 0.3)
    if motif == "moon":
        moon(d, S // 2, cy, int(S * 0.17))
    elif motif == "star":
        star_shape(d, S // 2, cy, int(S * 0.17), GOLD)
    else:
        critter(d, S // 2, cy + int(S * 0.02), 13, *CRITTERS[motif])
    fn = ImageFont.truetype(F_BOLD, int(S * 0.088))
    y = int(S * 0.6)
    for line in lines:
        d.text((S // 2, y), line, font=fn, fill=INK, anchor="mm",
               stroke_width=int(S * 0.008), stroke_fill=(255, 255, 255, 235))
        y += int(S * 0.115)
    return img


GUIDE = """WILDHAVEN REDBUBBLE PACK — upload guide

WHAT'S IN HERE
13 transparent PNG designs at 4500x4500 (300dpi class), ready for
Redbubble, TeePublic, and other print-on-demand sites.

HOW TO UPLOAD (per design, ~3 minutes)
1. redbubble.com -> Sell your art -> Upload new work
2. Upload the PNG. Redbubble spreads it across ~70 products
   (shirts, stickers, mugs, cases, notebooks, kids clothes...)
3. Drag/scale the art per product preview - defaults are usually fine.
   Enable ALL products. For dark shirts the transparent art works as-is.
4. Title / tags / description: see suggestions below.
5. Default markup ~20% is fine to start.
6. Mark "Is this artwork safe for all audiences?" -> Yes.

TITLES & TAGS (adjust freely)
- Critter portraits: "<Name> the Cute <thing> - Wildhaven Critters"
  tags: cute animal, kawaii, creature, cozy, kids, nursery, chibi,
        monster, adorable, wildhaven, gaming, cottagecore
- Goodnight design:  "Goodnight Little Dreamer - Cute Moon"
- Wild & wonderful:  "You Are Wild and Wonderful - Cute Critter"
- Catch the light:   "Catch the Light - Golden Star"

TIP: stickers are Redbubble's best sellers for art like this - Redbubble
adds the white die-cut border automatically around transparent designs.
"""


def main():
    os.makedirs(TMP, exist_ok=True)
    os.makedirs(OUTDIR, exist_ok=True)
    files = []
    for sp in CRITTERS.keys():
        img = critter_design(sp)
        p = os.path.join(TMP, sp + ".png")
        img.save(p)
        files.append((p, sp.capitalize() + ".png"))
        print("design:", sp)
    quotes = [
        ("goodnight-little-dreamer", ["Goodnight,", "little dreamer"], "moon"),
        ("wild-and-wonderful", ["You are wild", "and wonderful"], "flufftail"),
        ("catch-the-light", ["Catch", "the light"], "star"),
    ]
    for key, lines, motif in quotes:
        img = quote_design(lines, motif)
        p = os.path.join(TMP, key + ".png")
        img.save(p)
        files.append((p, key + ".png"))
        print("design:", key)

    zpath = os.path.join(ROOT, "dist", "Wildhaven-Redbubble-Pack.zip")
    with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as z:
        for src, arc in files:
            z.write(src, "Wildhaven-Redbubble/" + arc)
        z.writestr("Wildhaven-Redbubble/UPLOAD-GUIDE.txt", GUIDE)
    print("zip:", zpath, os.path.getsize(zpath) // 1024 // 1024, "MB")

    # preview sheet on light/dark split so transparency is visible
    sheet = Image.new("RGB", (6 * 380, 2 * 400), (240, 238, 234))
    d = ImageDraw.Draw(sheet)
    d.rectangle([0, 400, sheet.width, 800], fill=(46, 50, 60))
    picks = ["flufftail", "nocturnix", "cinderpup", "aquaphin", "glimmerwing", "mossback"]
    for i, sp in enumerate(picks):
        t = Image.open(os.path.join(TMP, sp + ".png")).resize((360, 360), Image.LANCZOS)
        sheet.paste(t, (10 + i * 380, 20), t)
        sheet.paste(t, (10 + i * 380, 420), t)
    sheet.save(os.path.join(OUTDIR, "preview.jpg"), quality=90)
    print("preview saved")


if __name__ == "__main__":
    main()
