#!/usr/bin/env python3
"""spec_ad.py — finish a 9:16 spec ad from generated clips.

    python3 scripts/spec_ad.py --name "Doña Bakehouse" --caption "Lamination you can hear." \
        --cta "Open 8am · @donabakehouse" --out dist/spec-ads/dona.mp4 clip1.mp4 clip2.mp4 clip3.mp4

Takes 1–4 clips (any size; Seedance 2.5 output from Dreamina), scales and
crops them to 1080×1920, joins them with short cross-fades, lays the
caption in TikTok's safe zone over the first clip, adds a three-second
end card with the business name and call to action, and mixes in a
generated, royalty-free score. No fonts or ffmpeg filters that a static
build lacks: text is rendered with Pillow and composited as PNG overlays.

Honest by construction: it never adds a claim, a price or a review — only
the words you pass in.
"""
import argparse, os, subprocess, sys, tempfile, math, wave, struct
from PIL import Image, ImageDraw, ImageFont, ImageFilter

sys.path.insert(0, os.path.dirname(__file__))
try:
    from book_clips import music  # the generated score from the book-clip pipeline
except Exception:
    music = None

W, H = 1080, 1920
SAFE_TOP, SAFE_BOTTOM = 260, 520          # TikTok/Reels interface zones

def ffmpeg():
    try:
        import imageio_ffmpeg; return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        return "ffmpeg"

def font(size, bold=False):
    for p in (["/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"] if bold else ["/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"]):
        if os.path.exists(p): return ImageFont.truetype(p, size)
    return ImageFont.load_default()

def wrap(d, text, f, maxw):
    lines, cur = [], ""
    for w in text.split():
        t = (cur + " " + w).strip()
        if d.textlength(t, font=f) > maxw and cur: lines.append(cur); cur = w
        else: cur = t
    if cur: lines.append(cur)
    return lines

def caption_png(text, path):
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    f = font(76, True); lines = wrap(d, text, f, W - 160)
    y = SAFE_TOP + 40
    for ln in lines:
        tw = d.textlength(ln, font=f); x = (W - tw) / 2
        for dx, dy in ((3, 3), (-3, 3), (3, -3), (-3, -3)): d.text((x + dx, y + dy), ln, font=f, fill=(0, 0, 0, 200))
        d.text((x, y), ln, font=f, fill=(255, 250, 240, 255)); y += 92
    im.save(path)

def endcard_png(name, cta, path):
    im = Image.new("RGB", (W, H), (18, 14, 16)); d = ImageDraw.Draw(im)
    glow = Image.new("RGB", (W, H), (18, 14, 16)); gd = ImageDraw.Draw(glow)
    gd.ellipse([W * 0.15, H * 0.35, W * 0.85, H * 0.75], fill=(70, 40, 30)); glow = glow.filter(ImageFilter.GaussianBlur(160))
    im = Image.blend(im, glow, 0.9); d = ImageDraw.Draw(im)
    f1 = font(96, True); lines = wrap(d, name, f1, W - 200); y = H * 0.40 - 50 * len(lines)
    for ln in lines: d.text(((W - d.textlength(ln, font=f1)) / 2, y), ln, font=f1, fill=(245, 236, 224)); y += 112
    f2 = font(48); y += 30
    for ln in wrap(d, cta, f2, W - 220): d.text(((W - d.textlength(ln, font=f2)) / 2, y), ln, font=f2, fill=(220, 180, 140)); y += 64
    im.save(path)

def probe_duration(ff, path):
    r = subprocess.run([ff, "-i", path], capture_output=True, text=True).stderr
    for l in r.splitlines():
        if "Duration" in l:
            h, m, s = l.split("Duration:")[1].split(",")[0].strip().split(":"); return int(h) * 3600 + int(m) * 60 + float(s)
    return 5.0

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("clips", nargs="+"); ap.add_argument("--name", required=True); ap.add_argument("--caption", required=True)
    ap.add_argument("--cta", default=""); ap.add_argument("--out", required=True); ap.add_argument("--end", type=float, default=3.0)
    ap.add_argument("--mood", default="calm"); ap.add_argument("--xfade", type=float, default=0.5)
    a = ap.parse_args(); ff = ffmpeg()
    os.makedirs(os.path.dirname(a.out) or ".", exist_ok=True)
    tmp = tempfile.mkdtemp()
    cap = os.path.join(tmp, "cap.png"); end = os.path.join(tmp, "end.png")
    caption_png(a.caption, cap); endcard_png(a.name, a.cta, end)
    durs = [probe_duration(ff, c) for c in a.clips]
    # end card as a video
    endv = os.path.join(tmp, "end.mp4")
    subprocess.run([ff, "-v", "error", "-y", "-loop", "1", "-i", end, "-t", str(a.end), "-r", "30", "-pix_fmt", "yuv420p", "-vf", f"scale={W}:{H}", endv], check=True)
    inputs = a.clips + [endv]; d_all = durs + [a.end]
    wavp = None
    if music:
        wavp = os.path.join(tmp, "score.wav")
    n = len(inputs)
    total = sum(d_all) - a.xfade * (n - 1)
    if wavp: music(a.mood, total + 0.5, wavp)
    args = [ff, "-v", "error", "-y"]
    for c in inputs: args += ["-i", c]
    if wavp: args += ["-i", wavp]
    fc = []
    for i in range(n):
        fc.append(f"[{i}:v]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},setsar=1,fps=30,settb=AVTB,format=yuv420p[v{i}]")
    prev = "v0"; offset = 0.0
    for i in range(1, n):
        offset += d_all[i - 1] - a.xfade
        fc.append(f"[{prev}][v{i}]xfade=transition=fade:duration={a.xfade}:offset={offset:.3f}[x{i}]"); prev = f"x{i}"
    fc.append(f"movie={cap}[cap];[{prev}][cap]overlay=0:0:enable='between(t,0.3,{max(1.0, durs[0] - 0.2):.2f})'[vo]")
    args += ["-filter_complex", ";".join(fc), "-map", "[vo]"]
    if wavp: args += ["-map", f"{n}:a", "-shortest"]
    args += ["-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p", "-movflags", "+faststart"]
    if wavp: args += ["-c:a", "aac", "-b:a", "128k"]
    args += [a.out]
    r = subprocess.run(args, capture_output=True, text=True)
    if r.returncode: sys.exit("ffmpeg failed:\n" + r.stderr[-2000:])
    print("wrote", a.out, "%.1fs" % total, "%.1f MB" % (os.path.getsize(a.out) / 1e6))

if __name__ == "__main__":
    main()
