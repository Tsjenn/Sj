#!/usr/bin/env python3
"""Cut a short, hook-plus-payoff version of each book clip.

    python3 scripts/book_shorts.py [ai|matcha|novel]

A cold TikTok audience decides in about two seconds. A 20-second clip
asks a lot of a viewer who does not know you; a ~10-second one that
opens on the hook and closes on the cover and the link gets a far
higher completion rate, and completion is what TikTok distributes on.

Takes the opening hook and the end card from the finished clip and
crossfades them, so no re-render is needed.

Output: dist/clips/book3d-<name>-short.mp4
"""

import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "dist", "clips")
HEAD = 4.6          # hook text, from the top
TAIL = 5.2          # cover + "On Kindle now" + the link
XF = 0.5


def dur(path):
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "csv=p=0", path], capture_output=True, text=True, check=True)
    return float(out.stdout.strip())


def build(name):
    src = os.path.join(OUT, "book3d-%s-live.mp4" % name)
    if not os.path.exists(src):
        raise SystemExit("missing %s" % src)
    total = dur(src)
    tail_start = max(HEAD, total - TAIL)
    out = os.path.join(OUT, "book3d-%s-short.mp4" % name)
    subprocess.run([
        "ffmpeg", "-y", "-loglevel", "error", "-i", src,
        "-filter_complex",
        "[0:v]trim=0:%.2f,setpts=PTS-STARTPTS,fps=30,settb=AVTB[a];"
        "[0:v]trim=%.2f:%.2f,setpts=PTS-STARTPTS,fps=30,settb=AVTB[b];"
        "[a][b]xfade=transition=fade:duration=%.2f:offset=%.2f,format=yuv420p[v];"
        "[0:a]atrim=0:%.2f,asetpts=PTS-STARTPTS,afade=t=out:st=%.2f:d=0.8[m]"
        % (HEAD, tail_start, total, XF, HEAD - XF,
           HEAD + TAIL - XF, HEAD + TAIL - XF - 0.8),
        "-map", "[v]", "-map", "[m]",
        "-c:v", "libx264", "-preset", "medium", "-crf", "20",
        "-c:a", "aac", "-b:a", "160k", out], check=True)
    print("%-7s -> %s  (%.1fs, %.1f MB)"
          % (name, os.path.basename(out), dur(out),
             os.path.getsize(out) / 1e6))


if __name__ == "__main__":
    for n in (sys.argv[1:] or ["ai", "matcha", "novel"]):
        build(n)
