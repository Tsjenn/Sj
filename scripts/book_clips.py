#!/usr/bin/env python3
"""Vertical promo clips for the books, for TikTok / Reels / Shorts.

    python3 scripts/book_clips.py [ai|matcha|novel]     (default: all)

Two end cards are produced for each book:
  book-<name>-coming.mp4   "Coming to Kindle"  — honest before you publish
  book-<name>-live.mp4     "On Kindle now"     — post this once it is live

Renders still cards with PIL, animates them with a slow ffmpeg zoom and
crossfades, and lays an originally-composed soundtrack underneath (no
third-party music, so there is nothing to get a video muted).

Output: dist/clips/book-<name>.mp4  — 1080x1920, ~22s, H.264 + AAC.

Every line of copy in CARDS below must be true of the actual book. No
sales figures, no rankings, no review quotes, no "bestseller".
"""

import os
import subprocess
import sys
import wave

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIST = os.path.join(ROOT, "dist")
OUT = os.path.join(DIST, "clips")
TMP = os.path.join(OUT, "_frames")
W, H = 1080, 1920
FPS = 30
SR = 44100

FONTS = {
    "bold": ["/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
             "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"],
    "reg": ["/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"],
    "serif": ["/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf",
              "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"],
}


def font(kind, size):
    for p in FONTS[kind]:
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


# ---------------------------------------------------------------- the copy

BOOKS = {
    "ai": {
        "cover": "AI-Without-The-Hype-cover.jpg",
        "title": "AI WITHOUT THE HYPE",
        "face": "bold",
        "bg": [(11, 22, 40), (24, 44, 74)],
        "accent": (224, 163, 62),
        "mood": "clean",
        "cards": [
            ("Everyone is using AI.\nAlmost nobody is\nusing it well.", 96),
            ("So I wrote the book\nI wanted to read.", 88),
            ("68 chapters.\nNo invented statistics.\nNo fake case studies.", 80),
            ("40 prompts you can\nactually paste.", 88),
            ("16 industry playbooks —\nfinance, audit, legal,\nhealthcare, manufacturing.", 72),
            ("And one whole chapter\non when NOT to use it.", 82),
        ],
    },
    "matcha": {
        "cover": "Matcha-cover.jpg",
        "title": "MATCHA",
        "face": "serif",
        "bg": [(22, 46, 34), (54, 92, 60)],
        "accent": (198, 214, 120),
        "mood": "calm",
        "cards": [
            ("One green powder.\nEight hundred years.", 100),
            ("Matcha is the only tea\nyou drink whole.", 88),
            ("The whole leaf,\nstone-ground,\nwhisked into water.", 84),
            ("That one fact explains\nthe colour, the price,\nand the price tag.", 76),
            ("History, craft, science —\nand 63 recipes.", 80),
        ],
    },
    "novel": {
        "cover": "AmahsDaughter-cover.jpg",
        "title": "THE AMAH'S DAUGHTER",
        "face": "serif",
        "bg": [(13, 24, 44), (36, 62, 100)],
        "accent": (201, 168, 76),
        "mood": "warm",
        "cards": [
            ("She raised her own\ndaughter —\nas the servant.", 92),
            ("Malacca, 1934.\nA girl arrives with a\nsecret she does not know.", 76),
            ("Then a war takes the\none person who knew\nthe truth.", 78),
            ("Seventy years of silence.", 86),
            ("2005: a biscuit tin\nof letters is finally\nopened.", 80),
        ],
    },
}


# ---------------------------------------------------------------- graphics

def gradient(c0, c1):
    im = Image.new("RGB", (W, H), c0)
    d = ImageDraw.Draw(im)
    for y in range(H):
        t = (y / H) ** 0.9
        d.line([(0, y), (W, y)], fill=tuple(
            int(c0[i] + (c1[i] - c0[i]) * t) for i in range(3)))
    return im


def vignette(im):
    m = Image.new("L", (W, H), 0)
    ImageDraw.Draw(m).ellipse([-W * 0.35, -H * 0.12, W * 1.35, H * 1.12], fill=170)
    m = m.filter(ImageFilter.GaussianBlur(180))
    return Image.composite(im, Image.new("RGB", (W, H), (0, 0, 0)), m)


def centred(d, lines, f, y, fill, lead=1.22):
    hs = []
    for ln in lines:
        b = d.textbbox((0, 0), ln or "X", font=f)
        hs.append(b[3] - b[1])
    step = max(hs) * lead
    y -= step * (len(lines) - 1) / 2
    for ln in lines:
        w = d.textlength(ln, font=f)
        d.text(((W - w) / 2, y), ln, font=f, fill=fill, anchor="lm")
        y += step


def text_card(spec, text, size):
    im = vignette(gradient(*spec["bg"]))
    d = ImageDraw.Draw(im)
    lines = text.split("\n")
    f = font(spec["face"], size)
    while max(d.textlength(l, font=f) for l in lines) > W - 150 and size > 34:
        size -= 4
        f = font(spec["face"], size)
    centred(d, lines, f, H * 0.46, (255, 255, 255))
    d.rectangle([W / 2 - 60, H * 0.72, W / 2 + 60, H * 0.72 + 7], fill=spec["accent"])
    return im


END_CARDS = {
    "coming": ("Coming to Kindle", "follow so you see it go up"),
    "live":   ("On Kindle now", "search the title on Amazon"),
}


def cover_card(spec, cover_path, label, sub):
    im = vignette(gradient(*spec["bg"]))
    d = ImageDraw.Draw(im)
    cov = Image.open(cover_path).convert("RGB")
    tw = int(W * 0.60)
    cov = cov.resize((tw, int(cov.height * tw / cov.width)), Image.LANCZOS)
    cx, cy = (W - cov.width) // 2, int(H * 0.30)
    sh = Image.new("L", (W, H), 0)
    ImageDraw.Draw(sh).rectangle([cx + 14, cy + 22, cx + cov.width + 14,
                                  cy + cov.height + 22], fill=150)
    im.paste(Image.new("RGB", (W, H), (0, 0, 0)), (0, 0),
             sh.filter(ImageFilter.GaussianBlur(30)))
    im.paste(cov, (cx, cy))
    d = ImageDraw.Draw(im)
    d.rectangle([cx - 2, cy - 2, cx + cov.width + 2, cy + cov.height + 2],
                outline=(255, 255, 255), width=3)
    f = font("bold", 62)
    w = d.textlength(label, font=f)
    y = cy + cov.height + 90
    d.text(((W - w) / 2, y), label, font=f, fill=spec["accent"], anchor="lm")
    f2 = font("reg", 40)
    w2 = d.textlength(sub, font=f2)
    d.text(((W - w2) / 2, y + 70), sub, font=f2, fill=(210, 218, 228), anchor="lm")
    return im


# ---------------------------------------------------------------- audio

MOODS = {
    # (bpm, chord roots in Hz, melody pool, pad gain, pluck gain)
    "clean": (92, [130.81, 174.61, 196.00, 146.83],
              [523.25, 587.33, 659.25, 783.99, 880.00], 0.055, 0.085),
    "calm":  (68, [146.83, 110.00, 164.81, 130.81],
              [440.00, 493.88, 587.33, 659.25, 880.00], 0.062, 0.070),
    "warm":  (76, [110.00, 146.83, 164.81, 130.81],
              [440.00, 523.25, 587.33, 698.46, 880.00], 0.060, 0.075),
}


def tone(freq, dur, gain, kind="sine", attack=0.02):
    n = int(SR * dur)
    t = np.arange(n) / SR
    if kind == "tri":
        x = 2 * np.abs(2 * ((freq * t) % 1) - 1) - 1
    else:
        x = np.sin(2 * np.pi * freq * t)
    env = np.ones(n)
    a = max(1, int(SR * attack))
    env[:a] = np.linspace(0, 1, a)
    env *= np.exp(-t * (2.6 if kind == "tri" else 0.85))
    return x * env * gain


def _add(buf, start, x):
    """Mix x into buf at start, clipped to the buffer."""
    end = min(len(buf), start + len(x))
    if end > start:
        buf[start:end] += x[:end - start]


def music(mood, secs, path):
    bpm, roots, pool, pad_g, plk_g = MOODS[mood]
    buf = np.zeros(int(SR * secs) + SR)
    beat = 60.0 / bpm
    bar = beat * 4
    i = 0
    while i * bar < secs:
        r = roots[i % len(roots)]
        s = int(i * bar * SR)
        for m in (1.0, 1.5, 2.0):          # root, fifth, octave pad
            _add(buf, s, tone(r * m, bar * 1.05, pad_g))
        for k in range(4):                  # sparse plucks
            if (i * 4 + k) % 3 == 0:
                f = pool[(i * 3 + k) % len(pool)]
                st = int((i * bar + k * beat) * SR)
                _add(buf, st, tone(f, beat * 1.6, plk_g, "tri", 0.005))
        i += 1
    buf = buf[:int(SR * secs)]
    fade = int(SR * 1.4)
    buf[-fade:] *= np.linspace(1, 0, fade)
    buf[:int(SR * 0.4)] *= np.linspace(0, 1, int(SR * 0.4))
    peak = float(np.max(np.abs(buf))) or 1.0
    pcm = (buf / peak * 0.62 * 32767).astype("<i2")
    with wave.open(path, "w") as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(SR)
        f.writeframes(pcm.tobytes())


# ---------------------------------------------------------------- assembly

def build(name, variant):
    spec = BOOKS[name]
    cover = os.path.join(DIST, spec["cover"])
    if not os.path.exists(cover):
        raise SystemExit("missing cover: %s" % cover)
    os.makedirs(TMP, exist_ok=True)

    stills, holds = [], []
    for i, (txt, sz) in enumerate(spec["cards"]):
        p = os.path.join(TMP, "%s-%02d.png" % (name, i))
        text_card(spec, txt, sz).save(p)
        stills.append(p)
        holds.append(3.1 if i == 0 else 2.8)
    label, sub = END_CARDS[variant]
    p = os.path.join(TMP, "%s-end-%s.png" % (name, variant))
    cover_card(spec, cover, label, sub).save(p)
    stills.append(p)
    holds.append(4.4)

    xf = 0.45
    total = sum(holds) - xf * (len(holds) - 1)
    wav = os.path.join(TMP, "%s-%s.wav" % (name, variant))
    music(spec["mood"], total, wav)

    # each still: slow zoom, then crossfade the chain together
    cmd = ["ffmpeg", "-y", "-loglevel", "error"]
    for p in stills:
        cmd += ["-loop", "1", "-t", "%.2f" % (max(holds) + 1), "-i", p]
    cmd += ["-i", wav]

    fc = []
    for i, hold in enumerate(holds):
        frames = int(hold * FPS)
        fc.append(
            "[%d:v]scale=%d:%d,zoompan=z='min(zoom+0.00045,1.10)':d=%d"
            ":x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=%dx%d:fps=%d,"
            "setsar=1[v%d]" % (i, int(W * 1.16), int(H * 1.16), frames, W, H, FPS, i))
    prev, elapsed = "[v0]", holds[0]
    for i in range(1, len(holds)):
        off = elapsed - xf
        lbl = "[x%d]" % i
        fc.append("%s[v%d]xfade=transition=fade:duration=%.2f:offset=%.2f%s"
                  % (prev, i, xf, off, lbl))
        prev = lbl
        elapsed = off + xf + holds[i] - xf + xf
        elapsed = off + holds[i]
    fc.append("%sformat=yuv420p[vout]" % prev)

    cmd += ["-filter_complex", ";".join(fc),
            "-map", "[vout]", "-map", "%d:a" % len(stills),
            "-c:v", "libx264", "-preset", "medium", "-crf", "20",
            "-r", str(FPS), "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-b:a", "160k", "-shortest",
            os.path.join(OUT, "book-%s-%s.mp4" % (name, variant))]
    subprocess.run(cmd, check=True)
    out = os.path.join(OUT, "book-%s-%s.mp4" % (name, variant))
    print("%-7s %-6s -> %s  (%.1f s, %.1f MB)"
          % (name, variant, os.path.basename(out), total,
             os.path.getsize(out) / 1e6))


def main():
    os.makedirs(OUT, exist_ok=True)
    which = sys.argv[1:] or list(BOOKS)
    for n in which:
        for v in ("coming", "live"):
            build(n, v)


if __name__ == "__main__":
    main()
