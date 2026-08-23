#!/usr/bin/env python3
"""Print-ready paperback interior and wrap cover for AI WITHOUT THE HYPE.

    python3 scripts/print_book.py art      # greyscale diagrams -> bookfactory7/art_print/
    python3 scripts/print_book.py html     # build dist/print/interior.html
    python3 scripts/print_book.py pdf      # render the interior PDF, report page count
    python3 scripts/print_book.py cover N  # wrap cover for an N-page interior
    python3 scripts/print_book.py all      # everything, in order

Trim 7 x 10 in. Margins are symmetric at 0.875in so KDP's gutter requirement is
met on both recto and verso without mirrored page boxes (Chromium's print engine
does not honour @page :left / :right margins reliably).
"""

import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BF = os.path.join(ROOT, "bookfactory7")
CH = os.path.join(BF, "chapters")
ARTP = os.path.join(BF, "art_print")
OUT = os.path.join(ROOT, "dist", "print")

TRIM_W, TRIM_H = 7.0, 10.0
MARGIN_SIDE = 0.875
MARGIN_TOP, MARGIN_BOT = 0.75, 0.85
DPI = 300
BLEED = 0.125
SPINE_PER_PAGE = 0.002252          # white paper, black ink

sys.path.insert(0, os.path.join(ROOT, "scripts"))

CHROME = ["/opt/pw-browsers/chromium-1194/chrome-linux/chrome",
          "/opt/pw-browsers/chromium_headless_shell-1194/chrome-linux/headless_shell"]


def build_art():
    """Re-render every diagram in a print-safe greyscale palette."""
    import ai_art
    ai_art.PAPER = (255, 255, 255)
    ai_art.NAVY = (26, 26, 26)
    ai_art.INK = (26, 26, 26)
    ai_art.CYAN = (122, 122, 122)
    ai_art.AMBER = (64, 64, 64)
    ai_art.SLATE = (135, 135, 135)
    ai_art.LIGHT = (232, 232, 232)
    ai_art.WHITE = (255, 255, 255)
    os.makedirs(ARTP, exist_ok=True)
    plan = json.load(open(os.path.join(BF, "plan.json")))
    n = 0
    for part in plan["parts"]:
        for ch in part["chapters"]:
            spec = ch["art"]
            im, d = ai_art.canvas(spec["title"])
            ai_art.TYPES[spec["type"]](d, spec["labels"])
            im.convert("L").save(os.path.join(ARTP, ch["id"] + ".png"), optimize=True)
            n += 1
    print("greyscale diagrams: %d -> %s" % (n, ARTP))


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def inline(s):
    s = esc(s)
    s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"\*(.+?)\*", r"<em>\1</em>", s)
    return s


def md_to_html(md):
    out, para, bullets, rows, nums, pre = [], [], [], [], [], []

    def fp():
        if para:
            out.append("<p>%s</p>" % inline(" ".join(para)))
            del para[:]

    def fb():
        if bullets:
            out.append("<ul>%s</ul>" % "".join("<li>%s</li>" % inline(b) for b in bullets))
            del bullets[:]

    def fn():
        if nums:
            out.append("<ol>%s</ol>" % "".join("<li>%s</li>" % inline(b) for b in nums))
            del nums[:]

    def fpre():
        if pre:
            out.append("<pre>%s</pre>" % esc("\n".join(pre)))
            del pre[:]

    def ft():
        if rows:
            body = []
            for i, r in enumerate(rows):
                tag = "th" if i == 0 else "td"
                body.append("<tr>%s</tr>" % "".join(
                    "<%s>%s</%s>" % (tag, inline(c), tag) for c in r))
            out.append("<table>%s</table>" % "".join(body))
            del rows[:]

    def flush_all():
        fp(); fb(); ft(); fn(); fpre()

    for line in md.splitlines():
        raw = line.rstrip()
        if raw.startswith("    ") and raw.strip():
            fp(); fb(); ft(); fn()
            pre.append(raw[4:])
            continue
        fpre()
        stripped = raw.strip()
        if raw.startswith("# "):
            flush_all(); out.append("<h1>%s</h1>" % inline(raw[2:]))
        elif raw.startswith("## "):
            flush_all(); out.append("<h2>%s</h2>" % inline(raw[3:]))
        elif raw.startswith("### "):
            flush_all(); out.append("<h3>%s</h3>" % inline(raw[4:]))
        elif raw.startswith("|"):
            fp(); fb(); fn()
            cells = [c.strip() for c in raw.strip("|").split("|")]
            if not all(re.fullmatch(r":?-+:?", c) for c in cells):
                rows.append(cells)
        elif re.match(r"\d+\. ", stripped):
            fp(); ft(); fb(); nums.append(re.sub(r"^\d+\. ", "", stripped))
        elif stripped.startswith("- "):
            fp(); ft(); fn(); bullets.append(stripped[2:])
        elif not stripped:
            flush_all()
        else:
            fb(); ft(); fn(); para.append(stripped)
    flush_all()
    return "\n".join(out)


CSS = """
@page { size: %(w)sin %(h)sin; margin: %(mt)sin %(ms)sin %(mb)sin %(ms)sin; }
html { font-size: 11.2pt; }
body { font-family: "DejaVu Serif", Georgia, serif; line-height: 1.44;
       color: #000; margin: 0; text-align: justify; hyphens: auto;
       -webkit-hyphens: auto; orphans: 2; widows: 2; }
h1 { font-family: "DejaVu Sans", Helvetica, sans-serif; font-size: 20pt;
     line-height: 1.2; margin: 0 0 1.6em; page-break-before: always;
     page-break-after: avoid; padding-top: 1.1in; text-align: left; }
h2 { font-family: "DejaVu Sans", Helvetica, sans-serif; font-size: 12.4pt;
     margin: 1.9em 0 0.55em; page-break-after: avoid; text-align: left; }
h3 { font-family: "DejaVu Sans", Helvetica, sans-serif; font-size: 11.2pt;
     margin: 1.5em 0 0.4em; page-break-after: avoid; text-align: left; }
p { margin: 0 0 0.62em; }
ul, ol { margin: 0 0 0.8em 1.25em; padding: 0; }
li { margin-bottom: 0.3em; }
pre { font-family: "DejaVu Sans Mono", monospace; font-size: 8.6pt;
      line-height: 1.35; white-space: pre-wrap; background: #f2f2f2;
      border-left: 3pt solid #999; padding: 0.5em 0.7em; margin: 0 0 0.9em;
      page-break-inside: avoid; text-align: left; }
table { border-collapse: collapse; width: 100%%; margin: 0 0 1em;
        font-size: 8.9pt; page-break-inside: avoid; text-align: left; }
th, td { border: 0.5pt solid #888; padding: 0.28em 0.4em; vertical-align: top;
         text-align: left; hyphens: auto; }
th { background: #ececec; font-family: "DejaVu Sans", Helvetica, sans-serif;
     font-size: 8.4pt; }
figure { margin: 1.1em 0; page-break-inside: avoid; text-align: center; }
figure img { max-width: 100%%; max-height: 6.2in; }
.tp { page-break-before: always; text-align: center; padding-top: 2.6in; }
.tp .t { font-family: "DejaVu Sans", Helvetica, sans-serif; font-size: 34pt;
         font-weight: bold; letter-spacing: 0.04em; margin-bottom: 0.35em; }
.tp .s { font-size: 12.5pt; font-style: italic; margin: 0 0.4in 2.4in;
         line-height: 1.45; }
.tp .a { font-family: "DejaVu Sans", Helvetica, sans-serif; font-size: 14pt; }
.fm { page-break-before: always; padding-top: 0.9in; text-align: left; }
.fm h2 { margin-top: 0; }
.fm p { font-size: 10pt; }
.part { page-break-before: always; text-align: center; padding-top: 3.1in; }
.part .k { font-family: "DejaVu Sans", Helvetica, sans-serif; font-size: 10pt;
           letter-spacing: 0.34em; margin-bottom: 0.9em; }
.part .n { font-family: "DejaVu Sans", Helvetica, sans-serif; font-size: 25pt;
           font-weight: bold; line-height: 1.25; margin: 0 0.5in; }
.toc { page-break-before: always; padding-top: 0.9in; text-align: left; }
.toc h2 { margin-top: 0; }
.toc .pt { font-family: "DejaVu Sans", Helvetica, sans-serif; font-weight: bold;
           font-size: 10pt; margin: 1.1em 0 0.35em; }
.toc .ce { font-size: 9.6pt; margin: 0 0 0.16em 0.9em; }
""" % {"w": TRIM_W, "h": TRIM_H, "ms": MARGIN_SIDE, "mt": MARGIN_TOP, "mb": MARGIN_BOT}

ROMAN = ["I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X"]

FRONT_MATTER = (
    '<div class="fm"><h2>About this book</h2>'
    '<p>This book is general information for working professionals. It is not '
    'legal, tax, accounting, medical, regulatory or investment advice. Rules '
    'differ between countries and professions and they change; check your own '
    'position with someone qualified to advise on it.</p>'
    '<p>The products and services described here change frequently. Capabilities '
    'are described in general terms for that reason, and no vendor has endorsed '
    'or reviewed this book.</p>'
    '<p>This book contains no invented statistics, studies, surveys or case '
    'studies, and makes no promise about anyone&#8217;s income, savings or '
    'employment. Every diagram in it is original.</p>'
    '<h2>About the author</h2>'
    '<p>Tang Shiuan Jenn is a qualified chartered accountant who works with AI '
    'systems every day &#8212; drafting, analysing, building, and, just as often, '
    'deciding not to use them. This book grew out of that practice: the questions '
    'colleagues actually ask, the mistakes worth warning people about, and the '
    'working methods that survived contact with real deadlines and real '
    'professional duties.</p></div>')


def build_html():
    plan = json.load(open(os.path.join(BF, "plan.json")))
    os.makedirs(OUT, exist_ok=True)
    parts = []

    parts.append('<div class="tp"><div class="t">%s</div>'
                 '<div class="s">%s</div><div class="a">%s</div></div>'
                 % (esc(plan["title"]), esc(plan["subtitle"]), esc(plan["author"])))
    parts.append(FRONT_MATTER)

    toc = ['<div class="toc"><h2>Contents</h2>']
    for part in plan["parts"]:
        toc.append('<div class="pt">Part %s &#183; %s</div>'
                   % (ROMAN[part["n"] - 1], esc(part["title"])))
        for ch in part["chapters"]:
            toc.append('<div class="ce">%s&#160;&#160;%s</div>'
                       % (ch["id"][2:].lstrip("0"), esc(ch["title"])))
    toc.append("</div>")
    parts.append("".join(toc))

    for part in plan["parts"]:
        parts.append('<div class="part"><div class="k">PART %s</div>'
                     '<div class="n">%s</div></div>'
                     % (ROMAN[part["n"] - 1], esc(part["title"])))
        for ch in part["chapters"]:
            body = md_to_html(open(os.path.join(CH, ch["id"] + ".md")).read())
            art = os.path.join(ARTP, ch["id"] + ".png")
            if os.path.exists(art):
                body = body.replace(
                    "</h1>", "</h1><figure><img src=\"file://%s\"/></figure>" % art, 1)
            parts.append(body)

    html = ("<!doctype html><html><head><meta charset='utf-8'>"
            "<title>%s</title><style>%s</style></head><body>%s</body></html>"
            % (esc(plan["title"]), CSS, "".join(parts)))
    path = os.path.join(OUT, "interior.html")
    open(path, "w").write(html)
    print("interior html -> %s (%.1f MB)" % (path, len(html) / 1e6))
    return path


def build_pdf():
    from playwright.sync_api import sync_playwright
    src = os.path.join(OUT, "interior.html")
    pdf = os.path.join(OUT, "AI-Without-The-Hype-INTERIOR.pdf")
    foot = ('<div style="width:100%;font-family:Georgia,serif;font-size:8pt;'
            'text-align:center;color:#000;"><span class="pageNumber"></span></div>')
    exe = next((c for c in CHROME if os.path.exists(c)), None)
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path=exe)
        pg = b.new_page()
        pg.goto("file://" + src, wait_until="load", timeout=300000)
        pg.pdf(path=pdf, width="%sin" % TRIM_W, height="%sin" % TRIM_H,
               print_background=True, display_header_footer=True,
               header_template="<div></div>", footer_template=foot,
               margin={"top": "%sin" % MARGIN_TOP, "bottom": "%sin" % MARGIN_BOT,
                       "left": "%sin" % MARGIN_SIDE, "right": "%sin" % MARGIN_SIDE})
        b.close()
    from pypdf import PdfReader
    n = len(PdfReader(pdf).pages)
    print("interior pdf -> %s" % pdf)
    print("PAGES: %d" % n)
    if n > 828:
        print("!! over KDP's 828-page limit for black ink on white paper")
    return n


BLURB = [
    ("Everyone is using AI.", 62, "w", True),
    ("Almost nobody is using it well.", 62, "w", True),
    ("", 26, "b", False),
    ("This book contains no invented statistics, no", 40, "b", False),
    ("fabricated case studies, no borrowed vendor", 40, "b", False),
    ("figures, and no promises about your income.", 40, "b", False),
    ("Every claim in it is one a careful reader could", 40, "b", False),
    ("check.", 40, "b", False),
    ("", 30, "b", False),
    ("Written by a chartered accountant for working", 40, "b", False),
    ("professionals, it teaches the skill from the", 40, "b", False),
    ("ground up: how the machine actually works, the", 40, "b", False),
    ("craft of prompting, how to make output reliable,", 40, "b", False),
    ("sixteen industry playbooks, a 90-day adoption", 40, "b", False),
    ("plan, and an honest chapter on when not to use", 40, "b", False),
    ("AI at all.", 40, "b", False),
    ("", 34, "b", False),
    ("68 chapters. A diagram in every chapter.", 40, "c", True),
]


def build_cover(pages):
    """Full wrap: back + spine + front, 0.125in bleed all round."""
    from PIL import Image, ImageDraw
    import ai_art

    spine = pages * SPINE_PER_PAGE
    W_in = TRIM_W * 2 + spine + BLEED * 2
    H_in = TRIM_H + BLEED * 2
    W, H = int(round(W_in * DPI)), int(round(H_in * DPI))

    DEEP, MID = (9, 18, 32), (19, 36, 60)
    AMBER, CYAN, WHITE = ai_art.AMBER, ai_art.CYAN, (255, 255, 255)
    BODY = (208, 220, 232)
    im = Image.new("RGB", (W, H), DEEP)
    d = ImageDraw.Draw(im)
    for y in range(H):
        t = y / H
        d.line([(0, y), (W, y)],
               fill=(int(DEEP[0] + (MID[0] - DEEP[0]) * t),
                     int(DEEP[1] + (MID[1] - DEEP[1]) * t),
                     int(DEEP[2] + (MID[2] - DEEP[2]) * t)))

    f = ai_art.font
    back_x0 = int(round(BLEED * DPI))
    spine_x0 = int(round((BLEED + TRIM_W) * DPI))
    spine_w = int(round(spine * DPI))
    front_x0 = int(round((BLEED + TRIM_W + spine) * DPI))
    front_w = int(round(TRIM_W * DPI))
    cx = front_x0 + front_w // 2

    import random
    rnd = random.Random(5)
    trace = (34, 58, 88)
    for _ in range(20):
        x = rnd.randint(front_x0 + 80, front_x0 + front_w - 320)
        y = rnd.randint(170, 700)
        L = rnd.choice([110, 170, 230])
        d.line([(x, y), (x + L, y)], fill=trace, width=4)
        d.line([(x + L, y), (x + L, y + L // 2)], fill=trace, width=4)
        d.ellipse([x + L - 8, y + L // 2 - 8, x + L + 8, y + L // 2 + 8],
                  fill=CYAN if rnd.random() < 0.3 else trace)

    def centred(text, y, size, fill, bold=True):
        sz = size
        ft = f(sz, bold)
        while d.textlength(text, font=ft) > front_w - 200 and sz > 20:
            sz -= 4
            ft = f(sz, bold)
        d.text((cx - d.textlength(text, font=ft) / 2, y), text, font=ft, fill=fill)
        return sz

    y = 700
    y += centred("AI", y, 470, AMBER) + 30
    for wd in ("WITHOUT", "THE HYPE"):
        y += centred(wd, y, 215, WHITE) + 26
    y += 70
    d.line([(cx - 330, y), (cx + 330, y)], fill=AMBER, width=6)
    y += 80
    y += centred("The Professional's Complete Guide to", y, 60, (198, 214, 228), False) + 20
    y += centred("Artificial Intelligence at Work", y, 72, WHITE) + 20
    y += 62
    y += centred("PROMPTING  ·  VERIFICATION  ·  AGENTS", y, 42, CYAN) + 18
    y += centred("16 INDUSTRY PLAYBOOKS  ·  68 DIAGRAMS", y, 42, CYAN) + 18

    fy = H - int(0.95 * DPI)
    d.rectangle([front_x0, fy, front_x0 + front_w, H], fill=(12, 24, 40))
    d.rectangle([front_x0, fy, front_x0 + front_w, fy + 8], fill=AMBER)
    centred("TANG SHIUAN JENN", fy + 66, 82, WHITE)
    centred("Chartered Accountant", fy + 170, 40, (170, 192, 210), False)

    # spine: reads top-to-bottom; title and author sized so they cannot collide
    if spine_w > 90:
        sp = Image.new("RGB", (int(TRIM_H * DPI), spine_w), (12, 24, 40))
        sd = ImageDraw.Draw(sp)
        sd.rectangle([0, 0, sp.width, 7], fill=AMBER)
        sd.rectangle([0, sp.height - 7, sp.width, sp.height], fill=AMBER)
        pad = 240
        t1, t2 = "AI WITHOUT THE HYPE", "TANG SHIUAN JENN"
        sz2 = max(16, int(spine_w * 0.26))
        f2 = f(sz2, False)
        w2 = sd.textlength(t2, font=f2)
        avail = sp.width - pad * 2 - w2 - 300
        sz1 = int(spine_w * 0.44)
        f1 = f(sz1, True)
        while sd.textlength(t1, font=f1) > avail and sz1 > 20:
            sz1 -= 4
            f1 = f(sz1, True)
        sd.text((pad, sp.height / 2 - sz1 * 0.70), t1, font=f1, fill=WHITE)
        sd.text((sp.width - pad - w2, sp.height / 2 - sz2 * 0.70), t2,
                font=f2, fill=(198, 214, 228))
        im.paste(sp.rotate(270, expand=True), (spine_x0, int(BLEED * DPI)))

    # back panel
    bx = back_x0 + 170
    bw = front_w - 340
    d.rectangle([back_x0 + 120, 330, back_x0 + front_w - 120, 336], fill=AMBER)
    cols = {"w": WHITE, "b": BODY, "c": CYAN}
    yy = 430
    for text, sz, key, bold in BLURB:
        if text:
            ft = f(sz, bold)
            while d.textlength(text, font=ft) > bw and sz > 18:
                sz -= 2
                ft = f(sz, bold)
            d.text((bx, yy), text, font=ft, fill=cols[key])
        yy += int(sz * 1.55)

    # KDP prints a barcode over the lower back cover. Nothing is drawn there;
    # the area is left clear so no artwork is lost underneath it.

    os.makedirs(OUT, exist_ok=True)
    jpg = os.path.join(OUT, "AI-Without-The-Hype-WRAP-cover.jpg")
    pdfp = os.path.join(OUT, "AI-Without-The-Hype-WRAP-cover.pdf")
    im.save(jpg, "JPEG", quality=95)
    im.save(pdfp, "PDF", resolution=float(DPI))
    print("wrap cover -> %s" % pdfp)
    print("  interior pages : %d" % pages)
    print("  spine width    : %.4f in" % spine)
    print("  full size      : %.4f x %.4f in (incl. %sin bleed)" % (W_in, H_in, BLEED))
    print("  pixels         : %d x %d at %d dpi" % (W, H, DPI))


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "all"
    if cmd == "art":
        build_art()
    elif cmd == "html":
        build_html()
    elif cmd == "pdf":
        build_pdf()
    elif cmd == "cover":
        build_cover(int(sys.argv[2]))
    else:
        build_art()
        build_html()
        build_cover(build_pdf())
