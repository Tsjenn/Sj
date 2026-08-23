#!/usr/bin/env python3
"""THE FOUR LAYERS factory (bookfactory8).

    python3 scripts/bookfactory8.py status   # progress + next chapter brief
    python3 scripts/bookfactory8.py build    # EPUB + cover into dist/

Chapters live in bookfactory8/chapters/<id>.md; the plan (8 parts, 77
chapters) in bookfactory8/plan.json; art in bookfactory8/art/<id>.png
(regenerate with scripts/layers_art.py).

Markdown subset: '# ' chapter title, '## ' section, '### ' recipe name,
'- ' bullets, '| a | b |' tables, blank-line paragraphs, *i* and **b**.
"""

import json
import os
import re
import sys
import zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BF = os.path.join(ROOT, "bookfactory8")
CHAPTERS = os.path.join(BF, "chapters")
ART = os.path.join(BF, "art")
DIST = os.path.join(ROOT, "dist")


def load_plan():
    with open(os.path.join(BF, "plan.json")) as f:
        return json.load(f)


def flat_chapters(plan):
    out = []
    for part in plan["parts"]:
        for ch in part["chapters"]:
            out.append((part, ch))
    return out


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def inline(s):
    s = esc(s)
    s = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", s)
    s = re.sub(r"\*(.+?)\*", r"<i>\1</i>", s)
    return s


def md_to_xhtml(md):
    out, para, bullets, rows, nums, quote = [], [], [], [], [], []

    def flush_para():
        if para:
            out.append("<p>%s</p>" % inline(" ".join(para)))
            del para[:]

    def flush_bullets():
        if bullets:
            out.append("<ul>%s</ul>" % "".join("<li>%s</li>" % inline(b) for b in bullets))
            del bullets[:]

    def flush_nums():
        if nums:
            out.append("<ol>%s</ol>" % "".join("<li>%s</li>" % inline(b) for b in nums))
            del nums[:]

    def flush_quote():
        if quote:
            out.append('<div class="callout">%s</div>'
                       % "".join("<p>%s</p>" % inline(q) for q in quote))
            del quote[:]

    def flush_table():
        if rows:
            body = []
            for i, r in enumerate(rows):
                tag = "th" if i == 0 else "td"
                body.append("<tr>%s</tr>" % "".join("<%s>%s</%s>" % (tag, inline(c), tag) for c in r))
            out.append("<table>%s</table>" % "".join(body))
            del rows[:]

    for line in md.splitlines():
        line = line.rstrip()
        if line.startswith("# "):
            flush_para(); flush_bullets(); flush_table(); flush_nums(); flush_quote()
            out.append("<h1>%s</h1>" % inline(line[2:]))
        elif line.startswith("## "):
            flush_para(); flush_bullets(); flush_table(); flush_nums(); flush_quote()
            out.append("<h2>%s</h2>" % inline(line[3:]))
        elif line.startswith("### "):
            flush_para(); flush_bullets(); flush_table(); flush_nums(); flush_quote()
            out.append("<h3>%s</h3>" % inline(line[4:]))
        elif line.startswith("|"):
            flush_para(); flush_bullets()
            cells = [c.strip() for c in line.strip("|").split("|")]
            if not all(re.fullmatch(r":?-+:?", c) for c in cells):
                rows.append(cells)
        elif re.match(r"\d+\. ", line):
            flush_para(); flush_table(); flush_bullets()
            nums.append(re.sub(r"^\d+\. ", "", line))
        elif line.startswith("> "):
            flush_para(); flush_bullets(); flush_table(); flush_nums(); flush_quote(); flush_nums()
            quote.append(line[2:])
        elif line.startswith("- "):
            flush_para(); flush_table(); flush_nums()
            bullets.append(line[2:])
        elif not line.strip():
            flush_para(); flush_bullets(); flush_table(); flush_nums(); flush_quote()
        else:
            flush_bullets(); flush_table(); flush_nums(); flush_quote()
            para.append(line.strip())
    flush_para(); flush_bullets(); flush_table(); flush_nums(); flush_quote()
    return "\n".join(out)


CSS = """
body { font-family: serif; line-height: 1.6; margin: 1em; }
h1 { font-size: 1.5em; line-height: 1.25; margin: 1.4em 0 0.8em; }
h2 { font-size: 1.15em; margin: 1.4em 0 0.4em; }
h3 { font-size: 1.05em; margin: 1.3em 0 0.35em; color: #0F2438; }
ol { margin: 0 0 0.9em 1.3em; }
div.callout { border-left: 4px solid #1FA8C7; background: #F1F6F9; padding: 0.6em 0.9em; margin: 0 0 1em; }
div.callout p { margin: 0 0 0.4em; font-size: 0.95em; }
p { margin: 0 0 0.85em; text-indent: 0; }
ul { margin: 0 0 0.9em 1.2em; }
li { margin-bottom: 0.35em; }
table { border-collapse: collapse; margin: 0 0 1em; width: 100%; }
th, td { border: 1px solid #C6D2DA; padding: 0.35em 0.5em; text-align: left; font-size: 0.92em; }
th { background: #E8EEF2; }
p.art { text-align: center; margin: 1em 0; }
p.art img { max-width: 100%; }
.tp { text-align: center; margin-top: 24%; }
.tp h1 { font-size: 2.1em; margin-bottom: 0.2em; letter-spacing: 0.12em; }
.tp .sub { font-size: 1.05em; font-style: italic; margin-bottom: 2.2em; }
.tp .auth { font-size: 1.1em; }
.part { text-align: center; margin-top: 34%; }
.part .k { font-size: 0.9em; letter-spacing: 0.3em; color: #1FA8C7; }
.part h1 { font-size: 1.7em; }
.small { font-size: 0.85em; color: #444; }
"""

XHTML = """<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops">
<head><title>%s</title><link rel="stylesheet" type="text/css" href="style.css"/></head>
<body>%s</body>
</html>"""

ROMAN = ["I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X"]


def word_count(md):
    return len(re.sub(r"[#*\-|]", "", md).split())


def build():
    plan = load_plan()
    chs = flat_chapters(plan)
    done = [(p, c) for p, c in chs
            if c["status"] == "done" and os.path.exists(os.path.join(CHAPTERS, c["id"] + ".md"))]
    complete = len(done) == len(chs)
    os.makedirs(DIST, exist_ok=True)

    cover_path = os.path.join(DIST, "The-Silicon-Ledger-cover.jpg")
    if not os.path.exists(cover_path):
        sys.path.insert(0, os.path.join(ROOT, "scripts"))
        import layers_art
        layers_art.make_cover(cover_path)

    suffix = "" if complete else "-PREVIEW-%dof%d" % (len(done), len(chs))
    epub_path = os.path.join(DIST, "The-Silicon-Ledger%s.epub" % suffix)

    uid = "urn:uuid:%08x-wwi7-4000-8000-%012x" % (abs(hash(plan["title"])) % 2**32,
                                                  abs(hash(plan["subtitle"])) % 2**48)
    files, art_files, toc, order = {}, {}, [], []

    tp = ('<div class="tp"><h1>%s</h1><p class="sub">%s</p><p class="auth">%s</p></div>'
          % (esc(plan["title"]), esc(plan["subtitle"]), esc(plan["author"])))
    files["titlepage.xhtml"] = XHTML % (esc(plan["title"]), tp)
    order.append("titlepage.xhtml")

    about = ("<h1>About the Author</h1>"
             "<p>Tang Shiuan Jenn is a qualified chartered accountant who works with "
             "AI systems every day &#8212; drafting, analysing, building, and, just as "
             "often, deciding not to use them. This book grew out of that practice: "
             "the questions colleagues actually ask, the mistakes worth warning "
             "people about, and the working methods that survived contact with real "
             "deadlines and real professional duties.</p>"
             "<h1>About this book</h1>"
             "<p>This book is general information for working professionals. It is "
             "not legal, tax, medical, financial, or regulatory advice, and it is not "
             "a substitute for your own judgement, your employer&#8217;s policies, or "
             "the rules of your professional body and regulator. Check anything that "
             "matters against your own jurisdiction and circumstances.</p>"
             "<p>AI products change quickly. Where a specific tool is named, the book "
             "describes what that kind of tool does rather than the details of any "
             "current version; confirm current capabilities, terms, and prices with "
             "the provider before you rely on them.</p>"
             "<p>No statistics, studies, surveys, or case studies have been invented "
             "for this book. Where a scenario is used to illustrate a point, it is "
             "described as an illustration and involves no real organisation.</p>"
             "<p>All diagrams are original artwork made for this book.</p>")

    seen_parts = set()
    for part, ch in done:
        if part["n"] not in seen_parts:
            seen_parts.add(part["n"])
            pname = "part%d.xhtml" % part["n"]
            files[pname] = XHTML % (esc(part["title"]),
                '<div class="part"><p class="k">PART %s</p><h1>%s</h1></div>'
                % (ROMAN[part["n"] - 1], esc(part["title"])))
            order.append(pname)
            toc.append('<li><a href="%s">Part %s — %s</a></li>'
                       % (pname, ROMAN[part["n"] - 1], esc(part["title"])))
        with open(os.path.join(CHAPTERS, ch["id"] + ".md")) as f:
            body = md_to_xhtml(f.read())
        art_src = os.path.join(ART, ch["id"] + ".png")
        if os.path.exists(art_src):
            art_name = "art-" + ch["id"] + ".png"
            art_files[art_name] = art_src
            h1_end = body.find("</h1>")
            if h1_end != -1:
                body = (body[:h1_end + 5]
                        + '<p class="art"><img src="%s" alt="%s — illustration"/></p>'
                        % (art_name, esc(ch["title"])) + body[h1_end + 5:])
        if ch.get("timeline"):
            h1_end = body.find("</h1>")
            if h1_end != -1:
                body = (body[:h1_end + 5]
                        + '<p class="small" style="text-align:center; letter-spacing:0.08em;">%s</p>'
                        % esc(ch["timeline"]) + body[h1_end + 5:])
        name = ch["id"] + ".xhtml"
        files[name] = XHTML % (esc(ch["title"]), body)
        order.append(name)
        toc.append('<li><a href="%s">%s</a></li>' % (name, esc(ch["title"])))

    files["about.xhtml"] = XHTML % ("About", about)
    order.append("about.xhtml")
    toc.append('<li><a href="about.xhtml">About this book</a></li>')

    files["nav.xhtml"] = XHTML % ("Contents",
        '<nav epub:type="toc" id="toc"><h1>Contents</h1><ol>'
        '<li><a href="titlepage.xhtml">Title</a></li>%s</ol></nav>' % "".join(toc))

    manifest = ['<item id="f%d" href="%s" media-type="application/xhtml+xml"/>' % (i, n)
                for i, n in enumerate(order)]
    spine = ['<itemref idref="f%d"/>' % i for i in range(len(order))]

    opf = """<?xml version="1.0" encoding="utf-8"?>
<package xmlns="http://www.idpf.org/2007/opf" version="3.0" unique-identifier="uid">
<metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
<dc:identifier id="uid">%s</dc:identifier>
<dc:title>%s</dc:title>
<dc:creator>%s</dc:creator>
<dc:language>en</dc:language>
<meta property="dcterms:modified">2026-08-23T00:00:00Z</meta>
<meta name="cover" content="cover-img"/>
</metadata>
<manifest>
<item id="nav" href="nav.xhtml" media-type="application/xhtml+xml" properties="nav"/>
<item id="css" href="style.css" media-type="text/css"/>
<item id="cover-img" href="cover.jpg" media-type="image/jpeg" properties="cover-image"/>
%s
%s
</manifest>
<spine>%s</spine>
</package>""" % (uid, esc(plan["title"] + ": " + plan["subtitle"]), esc(plan["author"]),
                 "\n".join(manifest),
                 "\n".join('<item id="a%d" href="%s" media-type="image/png"/>' % (i, n)
                           for i, n in enumerate(art_files)),
                 "".join(spine))

    with zipfile.ZipFile(epub_path, "w") as z:
        z.writestr("mimetype", "application/epub+zip", compress_type=zipfile.ZIP_STORED)
        z.writestr("META-INF/container.xml",
                   '<?xml version="1.0"?><container version="1.0" '
                   'xmlns="urn:oasis:names:tc:opendocument:xmlns:container">'
                   '<rootfiles><rootfile full-path="OEBPS/package.opf" '
                   'media-type="application/oebps-package+xml"/></rootfiles></container>')
        z.writestr("OEBPS/package.opf", opf)
        z.writestr("OEBPS/style.css", CSS)
        z.write(cover_path, "OEBPS/cover.jpg")
        for n, src in art_files.items():
            z.write(src, "OEBPS/" + n)
        for name, content in files.items():
            z.writestr("OEBPS/" + name, content)

    words = 0
    for _, ch in done:
        with open(os.path.join(CHAPTERS, ch["id"] + ".md")) as f:
            words += word_count(f.read())
    print("Built %s (%d/%d chapters, ~%d words, %d illustrations)"
          % (epub_path, len(done), len(chs), words, len(art_files)))
    if complete:
        print("COMPLETE — ready for KDP upload (EPUB + dist/The-Silicon-Ledger-cover.jpg).")
    return complete


def status():
    plan = load_plan()
    chs = flat_chapters(plan)
    done = [(p, c) for p, c in chs if c["status"] == "done"]
    words = 0
    for _, ch in done:
        p = os.path.join(CHAPTERS, ch["id"] + ".md")
        if os.path.exists(p):
            with open(p) as f:
                words += word_count(f.read())
    print("%s — %d/%d chapters (~%d words of target ~347k)"
          % (plan["title"], len(done), len(chs), words))
    todo = [(p, c) for p, c in chs if c["status"] != "done"]
    if todo:
        part, nxt = todo[0]
        print("\nNEXT: %s — %s (Part %s: %s)" % (nxt["id"], nxt["title"], ROMAN[part["n"] - 1], part["title"]))
        if "brief" in nxt:
            print("BRIEF:", nxt["brief"])
        if "recipes" in nxt:
            print("RECIPES:", "; ".join(nxt["recipes"]))
    else:
        print("\nAll chapters written. Run: python3 scripts/bookfactory8.py build")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "status"
    build() if cmd == "build" else status()
