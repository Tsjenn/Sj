#!/usr/bin/env python3
"""AI for Finance Teams — The Working Pack (financepack/).

    python3 scripts/finance_pack.py build   # PDF + editable files + zip

Sources: financepack/meta.json and financepack/sections/*.md.
Outputs: dist/AI-For-Finance-Teams/ and dist/AI-For-Finance-Teams.zip.

The zip carries NO analytics and no tracking of any kind — it is a paid
download and the fleet rule is that paid downloads stay clean.
"""

import html
import json
import os
import re
import shutil
import subprocess
import sys
import zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PACK = os.path.join(ROOT, "financepack")
SECT = os.path.join(PACK, "sections")
DIST = os.path.join(ROOT, "dist")
OUT = os.path.join(DIST, "AI-For-Finance-Teams")
CHROME = "/opt/pw-browsers/chromium-1194/chrome-linux/chrome"


def meta():
    with open(os.path.join(PACK, "meta.json")) as f:
        return json.load(f)


# ---------------------------------------------------------------- markdown

def inline(s):
    s = html.escape(s)
    s = re.sub(r"`([^`]+)`", r"<code>\1</code>", s)
    s = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"(?<![*\w])\*([^*\n]+)\*(?!\*)", r"<em>\1</em>", s)
    return s


LABEL = re.compile(r"^\*{1,2}(P\d|Use when:|Paste this:|Check before)")


def md_to_html(text):
    """The markdown subset the sections are written in."""
    out, lines, i = [], text.split("\n"), 0
    while i < len(lines):
        ln = lines[i]

        if ln.startswith("```"):
            body = []
            i += 1
            while i < len(lines) and not lines[i].startswith("```"):
                body.append(html.escape(lines[i]))
                i += 1
            i += 1
            out.append("<pre class='paste'>%s</pre>" % "\n".join(body))
            continue

        if ln.startswith("|") and i + 1 < len(lines) and re.match(r"^\|[\s:|-]+\|$", lines[i + 1]):
            head = [c.strip() for c in ln.strip().strip("|").split("|")]
            i += 2
            rows = []
            while i < len(lines) and lines[i].startswith("|"):
                rows.append([c.strip() for c in lines[i].strip().strip("|").split("|")])
                i += 1
            t = ["<table><thead><tr>"]
            t += ["<th>%s</th>" % inline(c) for c in head]
            t.append("</tr></thead><tbody>")
            for r in rows:
                t.append("<tr>" + "".join("<td>%s</td>" % inline(c) for c in r) + "</tr>")
            t.append("</tbody></table>")
            out.append("".join(t))
            continue

        if ln.startswith("> "):
            body = []
            while i < len(lines) and (lines[i].startswith("> ") or lines[i].rstrip() == ">"):
                body.append(lines[i][2:] if len(lines[i]) > 2 else "")
                i += 1
            out.append("<blockquote>%s</blockquote>" % md_to_html("\n".join(body)))
            continue

        if re.match(r"^---+\s*$", ln):
            out.append("<hr>")
            i += 1
            continue

        m = re.match(r"^(#{2,4})\s+(.*)$", ln)
        if m:
            lvl = len(m.group(1))
            out.append("<h%d>%s</h%d>" % (lvl, inline(m.group(2)), lvl))
            i += 1
            continue

        if re.match(r"^\s*[-*]\s+", ln):
            items = []
            while i < len(lines) and re.match(r"^\s*[-*]\s+", lines[i]):
                items.append("<li>%s</li>" % inline(re.sub(r"^\s*[-*]\s+", "", lines[i])))
                i += 1
            out.append("<ul>%s</ul>" % "".join(items))
            continue

        if re.match(r"^\s*\d+[.)]\s+", ln):
            items = []
            while i < len(lines) and re.match(r"^\s*\d+[.)]\s+", lines[i]):
                items.append("<li>%s</li>" % inline(re.sub(r"^\s*\d+[.)]\s+", "", lines[i])))
                i += 1
            out.append("<ol>%s</ol>" % "".join(items))
            continue

        if ln.strip():
            para = []
            while i < len(lines) and lines[i].strip() and not re.match(
                    r"^(#{2,4}\s|\s*[-*]\s|\s*\d+[.)]\s|\||>\s|```|---+\s*$)", lines[i]):
                para.append(lines[i].strip())
                i += 1
                # Labelled lines ("**P1.2 — ...**", "*Use when:* ...") are their
                # own paragraph; without this they run together on one line.
                if i < len(lines) and LABEL.match(lines[i]):
                    break
            if para:
                joined = " ".join(para)
                cls = " class='label'" if LABEL.match(joined) else ""
                out.append("<p%s>%s</p>" % (cls, inline(joined)))
            else:
                i += 1
            continue
        i += 1
    return "\n".join(out)


CSS = """
@page { size: A4; margin: 20mm 18mm 18mm 18mm; }
* { box-sizing: border-box; }
body { font-family: Georgia,"Liberation Serif",serif; font-size: 10.5pt;
       line-height: 1.55; color: #1a1d21; margin: 0; }
h1 { font-family: Helvetica,Arial,sans-serif; font-size: 24pt; line-height: 1.15;
     margin: 0 0 4pt; letter-spacing: -.01em; page-break-before: always; }
h1:first-of-type { page-break-before: avoid; }
h2 { font-family: Helvetica,Arial,sans-serif; font-size: 13pt; margin: 20pt 0 6pt;
     color: #1E524E; page-break-after: avoid; }
h3 { font-family: Helvetica,Arial,sans-serif; font-size: 11pt; margin: 14pt 0 4pt;
     page-break-after: avoid; }
h4 { font-family: Helvetica,Arial,sans-serif; font-size: 10pt; margin: 12pt 0 3pt;
     page-break-after: avoid; }
p { margin: 0 0 8pt; }
p.label { margin-top: 14pt; page-break-after: avoid; }
ul,ol { margin: 0 0 8pt 0; padding-left: 18pt; }
li { margin-bottom: 3pt; }
code { font-family: "Liberation Mono",monospace; font-size: 9pt;
       background: #f2f4f5; padding: 0 2pt; border-radius: 2pt; }
pre.paste { font-family: "Liberation Mono",monospace; font-size: 8.6pt;
     line-height: 1.45; background: #f5f7f8; border: 1px solid #dfe4e7;
     border-left: 3px solid #2A6F6A; border-radius: 3pt; padding: 8pt 10pt;
     white-space: pre-wrap; word-wrap: break-word; margin: 0 0 9pt;
     page-break-inside: avoid; }
blockquote { border-left: 3px solid #cfd8dc; background: #fafbfb;
     margin: 0 0 9pt; padding: 8pt 12pt; page-break-inside: avoid; }
blockquote p:last-child { margin-bottom: 0; }
table { border-collapse: collapse; width: 100%; font-size: 8.8pt;
        margin: 0 0 10pt; page-break-inside: avoid; }
th,td { border: 1px solid #d5dade; padding: 4pt 6pt; text-align: left;
        vertical-align: top; }
th { background: #eef2f3; font-family: Helvetica,Arial,sans-serif;
     font-size: 8.4pt; }
hr { border: 0; border-top: 1px solid #dde2e5; margin: 14pt 0; }
.cover { page-break-after: always; text-align: center; padding-top: 62mm; }
.cover .kicker { font-family: Helvetica,Arial,sans-serif; font-size: 10pt;
     letter-spacing: .22em; color: #2A6F6A; text-transform: uppercase; }
.cover h1 { font-size: 34pt; margin: 14pt 0 0; page-break-before: avoid; }
.cover .sub { font-family: Helvetica,Arial,sans-serif; font-size: 15pt;
     color: #5a6570; margin-top: 6pt; }
.cover .rule { width: 70pt; height: 3pt; background: #2A6F6A; margin: 22pt auto; }
.cover .auth { font-family: Helvetica,Arial,sans-serif; font-size: 12pt;
     font-weight: bold; letter-spacing: .05em; }
.cover .cred { font-family: Helvetica,Arial,sans-serif; font-size: 9.5pt;
     color: #5a6570; margin-top: 3pt; }
.cover .note { font-size: 9pt; color: #5a6570; margin-top: 46mm;
     max-width: 108mm; margin-left: auto; margin-right: auto; }
.toc { page-break-after: always; }
.toc h2 { margin-top: 0; }
.toc ol { font-family: Helvetica,Arial,sans-serif; font-size: 11pt;
     padding-left: 16pt; }
.toc li { margin-bottom: 7pt; }
"""


def build_html(m):
    parts = [
        "<!doctype html><html><head><meta charset='utf-8'>",
        "<title>%s</title><style>%s</style></head><body>" % (html.escape(m["title"]), CSS),
        "<div class='cover'><div class='kicker'>A working pack</div>",
        "<h1>%s</h1>" % html.escape(m["title"]),
        "<div class='sub'>%s</div>" % html.escape(m["subtitle"]),
        "<div class='rule'></div>",
        "<div class='auth'>%s</div>" % html.escape(m["author"]),
        "<div class='cred'>%s</div>" % html.escape(m["author_line"]),
        "<p class='note'>No invented statistics. No fabricated case studies. "
        "No promises about your income. Everything in this pack is either an "
        "artefact you can use or a claim you can check.</p></div>",
        "<div class='toc'><h2>Contents</h2><ol>",
    ]
    parts += ["<li>%s</li>" % html.escape(s["title"]) for s in m["sections"]]
    parts.append("</ol></div>")
    for s in m["sections"]:
        path = os.path.join(SECT, s["file"])
        if not os.path.exists(path):
            raise SystemExit("missing section: %s" % s["file"])
        parts.append("<h1>%s</h1>" % html.escape(s["title"]))
        parts.append(md_to_html(open(path).read()))
    parts.append("</body></html>")
    return "\n".join(parts)


def build_pdf(src, dest):
    script = os.path.join(OUT, "_print.py")
    with open(script, "w") as f:
        f.write(
            "from playwright.sync_api import sync_playwright\n"
            "with sync_playwright() as p:\n"
            "    b = p.chromium.launch(executable_path=%r)\n"
            "    pg = b.new_page()\n"
            "    pg.goto('file://%s')\n"
            "    pg.pdf(path=%r, format='A4', print_background=True,\n"
            "           display_header_footer=True, header_template='<div></div>',\n"
            "           footer_template=\"<div style='width:100%%;font:8pt Helvetica;"
            "color:#8a939b;text-align:center;'><span class='pageNumber'></span></div>\")\n"
            "    b.close()\n" % (CHROME, src, dest))
    subprocess.run([sys.executable, script], check=True)
    os.remove(script)


SCORER_CSV = """Task,Frequency (1-5),Time now (1-5),Verifiability (1-5),Error is cheap (1-5),No sensitive data (1-5),Total,Verdict
"Replace these rows with your own tasks",,,,,,=SUM(B2:F2),
"Score each factor 1-5 using the definitions in 'Choosing What to Automate First'",,,,,,=SUM(B3:F3),
"A high total on time but a low score on verifiability is a trap - read the section",,,,,,=SUM(B4:F4),
"""

README = """AI FOR FINANCE TEAMS - THE WORKING PACK
Tang Shiuan Jenn, Chartered Accountant

WHAT IS IN THIS FOLDER

  AI-For-Finance-Teams.pdf      The full pack. Start here.
  editable/                     The same material as plain text, so you can
                                paste it into your own documents and edit it.
  editable/use-case-scorer.csv  Opens in Excel, Numbers or Sheets. Use it
                                with the section on choosing what to automate.

LICENCE

  Bought for you and your team. Use it inside your organisation, adapt the
  policy and the prompts, put them in your own templates and training. Do
  not resell it or publish it as your own.

WHAT IT DOES NOT CONTAIN

  No statistics about AI adoption, no productivity percentages, no case
  studies, and no promises about your income. Those things are standard in
  this market and almost none of them are checkable. Everything here is
  either an artefact you can use or a claim you can check.

NOT ADVICE

  Everything touching law, tax, professional standards or regulatory duty
  is general information. Rules differ between countries and professions
  and they change. Nothing here is legal advice, and adopting any of it is
  not a statement that you comply with anything. Have the policy read by
  whoever carries risk in your organisation before you use it.

NO TRACKING

  Nothing in this download phones home. There is no analytics, no beacon
  and no unique identifier in these files.
"""


def build():
    m = meta()
    if os.path.isdir(OUT):
        shutil.rmtree(OUT)
    os.makedirs(os.path.join(OUT, "editable"), exist_ok=True)

    src = os.path.join(OUT, "_pack.html")
    with open(src, "w") as f:
        f.write(build_html(m))

    pdf = os.path.join(OUT, "AI-For-Finance-Teams.pdf")
    build_pdf(src, pdf)
    os.remove(src)

    for s in m["sections"]:
        name = os.path.splitext(s["file"])[0] + ".md"
        shutil.copy(os.path.join(SECT, s["file"]), os.path.join(OUT, "editable", name))
    with open(os.path.join(OUT, "editable", "use-case-scorer.csv"), "w") as f:
        f.write(SCORER_CSV)
    with open(os.path.join(OUT, "README.txt"), "w") as f:
        f.write(README)

    zpath = os.path.join(DIST, "AI-For-Finance-Teams.zip")
    with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as z:
        for root, _, files in os.walk(OUT):
            for fn in sorted(files):
                p = os.path.join(root, fn)
                z.write(p, os.path.relpath(p, OUT))

    # the paid download must stay analytics-free
    with zipfile.ZipFile(zpath) as z:
        for n in z.namelist():
            if n.endswith((".txt", ".md", ".csv")):
                body = z.read(n).decode("utf-8", "replace").lower()
                for bad in ("cloudflareinsights", "beacon.min.js", "google-analytics", "gtag("):
                    if bad in body:
                        raise SystemExit("tracking found in paid download: %s" % n)

    print("pack   -> %s" % OUT)
    print("zip    -> %s (%.1f KB)" % (zpath, os.path.getsize(zpath) / 1024.0))
    print("pdf    -> %.1f KB" % (os.path.getsize(pdf) / 1024.0))


if __name__ == "__main__":
    build()
