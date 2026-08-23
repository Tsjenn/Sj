#!/usr/bin/env python3
"""Cinematic 3D promo clips for the books (TikTok / Reels / Shorts).

    python3 scripts/book_clips3d.py [ai|matcha|novel]      (default: all)

The book is a real lit 3D object in three.js — cover texture-mapped onto
a board, paper page block, key/rim lighting, soft shadows, drifting motes
— filmed by a camera that arcs from the spine round to face-on. Frames
are captured deterministically through Playwright, then muxed with an
originally-composed soundtrack.

Output: dist/clips/book3d-<name>-<coming|live>.mp4  (1080x1920, H.264+AAC)

Every claim in BOOKS below must be true of the actual book: no sales
figures, no rankings, no review quotes, no "bestseller".
"""

import base64
import json
import os
import shutil
import subprocess
import sys

from book_clips import BOOKS as COPY, END_CARDS, cover_card, music

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "clipsrc")
DIST = os.path.join(ROOT, "dist")
OUT = os.path.join(DIST, "clips")
TMP = os.path.join(OUT, "_3d")
CHROME = "/opt/pw-browsers/chromium-1194/chrome-linux/chrome"
W, H, FPS = 1080, 1920, 30

# Scene styling per book: background gradient, rim/accent colour, board colour.
# Amazon ASINs, filled in as the owner confirms each one. A book with no
# ASIN here simply gets no URL bar on its end card.
ASIN = {
    "ai":     "B0HG6VFYXP",
    "matcha": "B0HG5ZY46K",
    "novel":  "B0HG6VGHDM",
}


LOOK = {
    "ai":     {"bg": ["#1b3career", "#070d18"], "accent": "#e0a33e", "spine": "#0f2438"},
    "matcha": {"bg": ["#2f5c3a", "#08130c"],    "accent": "#c6d678", "spine": "#2b4f33"},
    "novel":  {"bg": ["#23456e", "#060b16"],    "accent": "#c9a84c", "spine": "#16294a"},
}
LOOK["ai"]["bg"][0] = "#1b3a5c"

# Beat timing: (text, font px, screen position, appears at, leaves at)
def beats_for(name):
    cards = COPY[name]["cards"]
    out, t = [], 1.15
    for text, size in cards:
        hold = 2.35 if len(text) < 60 else 2.75
        out.append({"text": text, "size": int(size * 0.80),
                    "top": 0.075, "in": round(t, 2), "out": round(t + hold, 2)})
        t += hold + 0.55
    return out, round(t + 0.9, 2)


def data_uri(path):
    ext = os.path.splitext(path)[1].lower()
    mime = "image/jpeg" if ext in (".jpg", ".jpeg") else "image/png"
    with open(path, "rb") as f:
        return "data:%s;base64,%s" % (mime, base64.b64encode(f.read()).decode())


def render_frames(name, cfg, nframes, outdir):
    from playwright.sync_api import sync_playwright
    os.makedirs(outdir, exist_ok=True)
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path=CHROME, args=[
            "--use-gl=swiftshader", "--enable-unsafe-swiftshader",
            "--disable-lcd-text", "--force-device-scale-factor=1"])
        pg = b.new_page(viewport={"width": W, "height": H})
        errs = []
        pg.on("pageerror", lambda e: errs.append(str(e)))
        pg.add_init_script("window.__CFG__ = %s;" % json.dumps(cfg))
        pg.goto("file://" + os.path.join(SRC, "scene.html"))
        pg.wait_for_function("window.__ready && window.__ready()", timeout=30000)
        if errs:
            raise SystemExit("scene errors: %s" % errs[:3])
        el = pg.query_selector("#wrap")
        for i in range(nframes):
            pg.evaluate("i => window.setFrame(i)", i)
            el.screenshot(path=os.path.join(outdir, "f%05d.png" % i))
        if errs:
            raise SystemExit("scene errors during capture: %s" % errs[:3])
        b.close()


def build(name):
    spec = COPY[name]
    cover = os.path.join(DIST, spec["cover"])
    if not os.path.exists(cover):
        raise SystemExit("missing cover: %s" % cover)

    beats, dur = beats_for(name)
    look = LOOK[name]
    cfg = {"cover": data_uri(cover), "bg": look["bg"], "accent": look["accent"],
           "spine": look["spine"], "beats": beats, "duration": dur}

    frames = os.path.join(TMP, name)
    body = os.path.join(TMP, "%s-body.mp4" % name)
    scene_mtime = os.path.getmtime(os.path.join(SRC, "scene.html"))
    if os.path.exists(body) and os.path.getmtime(body) > scene_mtime:
        print("%-7s reusing rendered body" % name)
    else:
        if os.path.isdir(frames):
            shutil.rmtree(frames)
        n = int(dur * FPS)
        print("%-7s rendering %d frames (%.1fs) ..." % (name, n, dur))
        render_frames(name, cfg, n, frames)
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(FPS),
                        "-i", os.path.join(frames, "f%05d.png"),
                        "-c:v", "libx264", "-preset", "medium", "-crf", "19",
                        "-pix_fmt", "yuv420p", body], check=True)
        shutil.rmtree(frames)

    for variant in ("coming", "live"):
        label, sub = END_CARDS[variant]
        card = os.path.join(TMP, "%s-end-%s.png" % (name, variant))
        asin = ASIN.get(name)
        url = "amazon.com/dp/%s" % asin if asin else None
        cover_card(spec, cover, label, sub, url).save(card)

        hold, xf = 4.0, 0.6
        total = dur + hold - xf
        wav = os.path.join(TMP, "%s-%s.wav" % (name, variant))
        music(spec["mood"], total, wav)

        out = os.path.join(OUT, "book3d-%s-%s.mp4" % (name, variant))
        subprocess.run([
            "ffmpeg", "-y", "-loglevel", "error",
            "-i", body,
            "-loop", "1", "-t", "%.2f" % hold, "-i", card,
            "-i", wav,
            "-filter_complex",
            "[0:v]fps=%d,settb=AVTB[b];"
            "[1:v]scale=%d:%d,zoompan=z='min(zoom+0.00040,1.07)':d=%d"
            ":x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=%dx%d:fps=%d,"
            "setsar=1,settb=AVTB[e];"
            "[b][e]xfade=transition=fade:duration=%.2f:offset=%.2f,format=yuv420p[v]"
            % (FPS, int(W * 1.12), int(H * 1.12), int(hold * FPS), W, H, FPS,
               xf, dur - xf),
            "-map", "[v]", "-map", "2:a",
            "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-r", str(FPS),
            "-c:a", "aac", "-b:a", "160k", "-shortest", out], check=True)
        print("  %-6s -> %s  (%.1fs, %.1f MB)"
              % (variant, os.path.basename(out), total,
                 os.path.getsize(out) / 1e6))


def main():
    os.makedirs(OUT, exist_ok=True)
    os.makedirs(TMP, exist_ok=True)
    for n in (sys.argv[1:] or list(COPY)):
        build(n)


if __name__ == "__main__":
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    main()
