#!/usr/bin/env python3
"""Per-chapter mechanism diagrams for The Honest Sleep Book.

One clean editorial diagram per chapter — the visual version of the
book's "mechanism over miracle" rule. Light paper background (reads
well on e-ink and phones), warm ink, one gold accent.

  python3 scripts/sleepbook_art.py   -> book/sleep-art/ch01.png ... ch14.png
"""

import math
import os

from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "book", "sleep-art")
W, H = 1200, 780

PAPER = (250, 247, 240)
INK = (44, 46, 58)
GOLD = (206, 142, 66)
MUTE = (150, 148, 142)
SOFT = (226, 222, 212)

F = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FB = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
f_title = ImageFont.truetype(FB, 40)
f_lab = ImageFont.truetype(F, 28)
f_lab_b = ImageFont.truetype(FB, 28)
f_small = ImageFont.truetype(F, 23)


def canvas(title):
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    d.text((W // 2, 62), title, font=f_title, fill=INK, anchor="mm")
    d.line([W // 2 - 60, 100, W // 2 + 60, 100], fill=GOLD, width=4)
    return img, d


def arrow(d, x0, y0, x1, y1, col=INK, w=4):
    d.line([x0, y0, x1, y1], fill=col, width=w)
    a = math.atan2(y1 - y0, x1 - x0)
    for s in (-1, 1):
        d.line([x1, y1, x1 - 18 * math.cos(a + s * 0.45),
                y1 - 18 * math.sin(a + s * 0.45)], fill=col, width=w)


def curve(d, pts, col, w=5):
    d.line(pts, fill=col, width=w, joint="curve")


def ch01(d):
    # leverage, ranked: few tall bars then a long tail
    labels = ["wake\ntime", "light", "caffeine\ntiming", "bedroom", "sounds", "teas", "gadgets"]
    heights = [420, 340, 260, 180, 70, 45, 30]
    x = 130
    for lab, h in zip(labels, heights):
        col = GOLD if h > 150 else SOFT
        d.rectangle([x, 620 - h, x + 110, 620], fill=col, outline=INK, width=3)
        d.multiline_text((x + 55, 660), lab, font=f_small, fill=INK,
                         anchor="ma", align="center")
        x += 140
    d.text((W // 2, 165), "a handful of big levers — and a long tail that barely matters",
           font=f_lab, fill=MUTE, anchor="mm")


def ch02(d):
    # two systems over 24h: pressure ramp + clock wave
    d.line([120, 600, 1080, 600], fill=INK, width=3)
    for t, lab in [(120, "7am"), (600, "3pm"), (1080, "11pm")]:
        d.text((t, 630), lab, font=f_small, fill=MUTE, anchor="mm")
    pts = [(120 + i * 9.6, 600 - (i / 100) ** 1.15 * 330) for i in range(101)]
    curve(d, pts, GOLD, 6)
    pts2 = [(120 + i * 9.6, 400 - math.sin(i / 100 * math.pi * 1.6 - 0.8) * 120)
            for i in range(101)]
    curve(d, pts2, INK, 4)
    d.text((300, 250), "body clock (alerting)", font=f_lab, fill=INK, anchor="mm")
    d.text((880, 330), "sleep pressure", font=f_lab_b, fill=GOLD, anchor="mm")
    d.text((W // 2, 165), "good sleep = the two systems agreeing at bedtime",
           font=f_lab, fill=MUTE, anchor="mm")


def ch03(d):
    # anchored week vs scattered week
    days = "M T W T F S S".split()
    d.text((330, 210), "scattered wake times", font=f_lab, fill=INK, anchor="mm")
    d.text((870, 210), "anchored", font=f_lab_b, fill=GOLD, anchor="mm")
    import random
    random.seed(4)
    for i, day in enumerate(days):
        y = 270 + i * 55
        d.text((150, y), day, font=f_small, fill=MUTE, anchor="mm")
        x = 250 + random.randint(-60, 140)
        d.ellipse([x + 60, y - 13, x + 86, y + 13], fill=SOFT, outline=INK, width=3)
        d.text((760, y), day, font=f_small, fill=MUTE, anchor="mm")
        d.ellipse([850, y - 13, 876, y + 13], fill=GOLD, outline=INK, width=3)
    d.line([863, 250, 863, 640], fill=MUTE, width=2)
    d.text((W // 2, 705), "the clock can only set itself to a signal that repeats",
           font=f_lab, fill=MUTE, anchor="mm")


def ch04(d):
    # light dose: indoor vs cloudy vs clear (log-ish)
    bars = [("bright room", 90, SOFT), ("overcast sky", 300, GOLD), ("clear morning", 470, GOLD)]
    x = 210
    for lab, h, col in bars:
        d.rectangle([x, 600 - h, x + 200, 600], fill=col, outline=INK, width=3)
        d.text((x + 100, 640), lab, font=f_lab, fill=INK, anchor="mm")
        x += 290
    d.text((W // 2, 180), "your eyes and your body clock disagree about bright",
           font=f_lab, fill=MUTE, anchor="mm")
    d.text((310, 560), "a whisper", font=f_small, fill=MUTE, anchor="mm")


def ch05(d):
    # caffeine decay with cutoff
    d.line([120, 600, 1080, 600], fill=INK, width=3)
    pts = [(160 + i * 9, 240 + (1 - 0.5 ** (i / 45)) * 330) for i in range(100)]
    curve(d, pts, GOLD, 6)
    for x, lab in [(160, "2pm coffee"), (565, "8pm — half is left"), (970, "2am — a quarter")]:
        d.line([x, 600, x, 610], fill=INK, width=3)
        d.text((x, 640), lab, font=f_small, fill=INK, anchor="mm")
    d.text((W // 2, 175), "caffeine leaves in halves, not all at once",
           font=f_lab, fill=MUTE, anchor="mm")


def ch06(d):
    # bedroom, four words
    d.rounded_rectangle([330, 230, 870, 620], radius=26, outline=INK, width=5)
    d.rounded_rectangle([430, 380, 770, 540], radius=14, fill=SOFT, outline=INK, width=4)
    d.text((600, 460), "bed = sleep", font=f_lab_b, fill=INK, anchor="mm")
    for (x, y, lab) in [(330, 190, "cool"), (870, 190, "dark"),
                        (330, 665, "quiet"), (870, 665, "boring")]:
        d.text((x, y), lab, font=f_lab_b, fill=GOLD, anchor="mm")
    d.text((W // 2, 720), "four cheap words that beat every gadget",
           font=f_lab, fill=MUTE, anchor="mm")


def ch07(d):
    # trying spiral vs occupied narrator
    cx, cy = 350, 430
    pts = []
    for i in range(160):
        a = i / 14
        r = 12 + i * 1.05
        pts.append((cx + math.cos(a) * r, cy + math.sin(a) * r * 0.72))
    curve(d, pts, INK, 4)
    d.text((cx, 660), '"try to sleep" — arousal feeding itself',
           font=f_small, fill=INK, anchor="mm")
    pts2 = [(700 + i * 3.4, 300 + (i / 100) ** 1.6 * 280) for i in range(101)]
    curve(d, pts2, GOLD, 6)
    d.text((880, 660), "occupy the narrator — drift arrives sideways",
           font=f_small, fill=GOLD, anchor="mm")
    d.text((W // 2, 180), "sleep flees pursuit", font=f_lab, fill=MUTE, anchor="mm")


def ch08(d):
    # 3am flowchart
    def box(x, y, w2, lab, gold=False):
        d.rounded_rectangle([x - w2, y - 36, x + w2, y + 36], radius=12,
                            fill=(GOLD if gold else PAPER), outline=INK, width=4)
        d.multiline_text((x, y), lab, font=f_small,
                         fill=(PAPER if gold else INK), anchor="mm", align="center")
    box(600, 210, 150, "awake at 3am\n(no clock — ever)")
    arrow(d, 600, 246, 600, 300)
    box(600, 340, 150, "settle, drift?")
    arrow(d, 460, 340, 320, 340)
    box(210, 340, 105, "asleep —\nmost nights", gold=True)
    arrow(d, 600, 376, 600, 430)
    box(600, 470, 170, "waiting / churning\n(~20 min by feel)")
    arrow(d, 600, 506, 600, 560)
    box(600, 600, 190, "chair · dim lamp ·\nboring book")
    arrow(d, 790, 600, 940, 600)
    box(1030, 600, 100, "sleepy?\nback to bed", gold=True)
    arrow(d, 1030, 560, 1030, 380)
    arrow(d, 1030, 380, 755, 342)


def ch09(d):
    # jar with early withdrawal
    d.rounded_rectangle([460, 250, 740, 620], radius=20, outline=INK, width=5)
    d.rectangle([466, 430, 734, 614], fill=GOLD)
    for i in range(6):
        d.line([466, 430 + i * 30, 734, 430 + i * 30], fill=PAPER, width=2)
    d.text((600, 210), "sleep pressure, filling all day", font=f_lab, fill=INK, anchor="mm")
    arrow(d, 740, 470, 900, 400, GOLD, 6)
    d.text((950, 350), "a nap is\ntonight's sleep,\ntaken early", font=f_lab,
           fill=INK, anchor="mm", align="center")
    d.text((W // 2, 700), "short + early = first aid · long + late = tonight's insomnia",
           font=f_lab, fill=MUTE, anchor="mm")


def ch10(d):
    # measured vs guessed
    d.text((360, 230), "measured", font=f_lab_b, fill=GOLD, anchor="mm")
    d.text((840, 230), "guessed", font=f_lab_b, fill=MUTE, anchor="mm")
    for i, lab in enumerate(["asleep vs awake", "duration", "broken nights"]):
        y = 300 + i * 90
        d.rounded_rectangle([200, y - 30, 520, y + 30], radius=12, fill=GOLD)
        d.text((360, y), lab, font=f_lab, fill=PAPER, anchor="mm")
    for i, lab in enumerate(["deep sleep", "REM", "the score"]):
        y = 300 + i * 90
        d.rounded_rectangle([680, y - 30, 1000, y + 30], radius=12,
                            fill=SOFT, outline=MUTE, width=3)
        d.text((840, y), lab, font=f_lab, fill=INK, anchor="mm")
    d.text((W // 2, 660), "same confident font — very different evidence",
           font=f_lab, fill=MUTE, anchor="mm")


def ch11(d):
    # day timeline: what goes where
    d.line([130, 450, 1070, 450], fill=INK, width=4)
    stops = [(180, "morning\nexercise: any", GOLD), (430, "last caffeine\n(early pm)", INK),
             (680, "big dinner\nends 2-3h out", INK), (900, "hard workout?\ncool-down hour", INK),
             (1040, "bed", GOLD)]
    for x, lab, col in stops:
        d.ellipse([x - 12, 438, x + 12, 462], fill=col)
        d.multiline_text((x, 510), lab, font=f_small, fill=INK, anchor="ma", align="center")
    d.text((W // 2, 210), "timing beats abstinence, all day long",
           font=f_lab, fill=MUTE, anchor="mm")


def ch12(d):
    # the boundary line
    d.line([600, 200, 600, 640], fill=GOLD, width=6)
    d.text((350, 240), "habits territory", font=f_lab_b, fill=INK, anchor="mm")
    d.text((855, 240), "doctor territory", font=f_lab_b, fill=GOLD, anchor="mm")
    left = ["bad patches", "3am churning", "weekend drift", "screen habits"]
    right = ["snoring + gasping", "months, most nights", "restless legs", "dread + low days"]
    for i, lab in enumerate(left):
        d.text((350, 320 + i * 70), lab, font=f_lab, fill=MUTE, anchor="mm")
    for i, lab in enumerate(right):
        d.text((855, 320 + i * 70), lab, font=f_lab, fill=INK, anchor="mm")
    d.text((W // 2, 700), "crossing the line is the strong move",
           font=f_lab, fill=MUTE, anchor="mm")


def ch13(d):
    # 14-day calendar with dip
    for i in range(14):
        x = 150 + (i % 7) * 130
        y = 280 + (i // 7) * 170
        dip = i in (2, 3, 4)
        d.rounded_rectangle([x, y, x + 105, y + 130], radius=12,
                            fill=(SOFT if dip else PAPER), outline=INK, width=3)
        d.text((x + 52, y + 34), str(i + 1), font=f_lab_b,
               fill=(MUTE if dip else GOLD), anchor="mm")
        if dip:
            d.text((x + 52, y + 88), "the dip", font=f_small, fill=MUTE, anchor="mm")
    d.text((W // 2, 200), "one change a day — and days 3-5 honestly feel worse first",
           font=f_lab, fill=MUTE, anchor="mm")
    d.text((W // 2, 700), "success = better most nights, not perfect every night",
           font=f_lab, fill=INK, anchor="mm")


def ch14(d):
    # chain breaks, elastic returns
    x = 210
    for i in range(6):
        col = INK if i < 4 else SOFT
        d.ellipse([x, 300, x + 66, 366], outline=col, width=6)
        x += 56
    d.text((400, 430), "a streak: one miss and the chain is 'broken'",
           font=f_small, fill=INK, anchor="mm")
    pts = [(700 + i * 3.4, 330 + math.sin(i / 100 * math.pi * 2.2) *
            (60 * (1 - i / 130))) for i in range(101)]
    curve(d, pts, GOLD, 6)
    d.text((880, 430), "elastic: bends, then two nights back",
           font=f_small, fill=GOLD, anchor="mm")
    d.text((W // 2, 200), "the maintenance mindset", font=f_lab, fill=MUTE, anchor="mm")
    d.text((W // 2, 620), "you don't chase sleep — you make it welcome, and allow it",
           font=f_lab, fill=INK, anchor="mm")


TITLES = {
 "ch01": "Ranked by leverage", "ch02": "The two systems", "ch03": "The anchor",
 "ch04": "What counts as bright", "ch05": "The caffeine curve",
 "ch06": "The room, in four words", "ch07": "Why trying fails",
 "ch08": "The 3am playbook", "ch09": "The jar", "ch10": "Measured vs guessed",
 "ch11": "A well-timed day", "ch12": "The honest boundary",
 "ch13": "The 14-day reset", "ch14": "Bend, then return",
}
FUNCS = {"ch01": ch01, "ch02": ch02, "ch03": ch03, "ch04": ch04, "ch05": ch05,
         "ch06": ch06, "ch07": ch07, "ch08": ch08, "ch09": ch09, "ch10": ch10,
         "ch11": ch11, "ch12": ch12, "ch13": ch13, "ch14": ch14}


def main():
    os.makedirs(OUT, exist_ok=True)
    for slug, fn in FUNCS.items():
        img, d = canvas(TITLES[slug])
        fn(d)
        img.save(os.path.join(OUT, slug + ".png"), optimize=True)
        print("art:", slug)


if __name__ == "__main__":
    main()
