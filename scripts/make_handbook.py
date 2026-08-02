#!/usr/bin/env python3
"""Typeset 'The AI Side Hustle' handbook as a KDP-ready 6x9in PDF,
and draw its 1800x2700 (6x9 @ 300dpi) front cover.

  dist/The-AI-Side-Hustle-Interior.pdf   (manuscript, 6x9in)
  marketing/handbook/cover-front-1800x2700.png

Run:  python3 scripts/make_handbook.py
"""

import os
import sys

from reportlab.lib.pagesizes import inch
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.platypus import (BaseDocTemplate, PageTemplate, Frame,
                                Paragraph, Spacer, PageBreak)

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from handbook_content import TITLE, SUBTITLE, AUTHOR, DISCLAIMER, CHAPTERS, CLOSING

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAGE_W, PAGE_H = 6 * inch, 9 * inch
MARGIN = 0.8 * inch

ACCENT = "#B4652F"
INK = "#26282B"

S_TITLE = ParagraphStyle("t", fontName="Helvetica-Bold", fontSize=30, leading=36,
                         alignment=TA_CENTER, textColor=INK)
S_SUB = ParagraphStyle("s", fontName="Helvetica", fontSize=13, leading=19,
                       alignment=TA_CENTER, textColor="#555B63")
S_AUTHOR = ParagraphStyle("a", fontName="Helvetica-Bold", fontSize=15,
                          alignment=TA_CENTER, textColor=ACCENT)
S_CH_NUM = ParagraphStyle("cn", fontName="Helvetica-Bold", fontSize=13,
                          textColor=ACCENT, spaceBefore=0)
S_CH_TITLE = ParagraphStyle("ct", fontName="Helvetica-Bold", fontSize=22,
                            leading=27, textColor=INK, spaceAfter=18)
S_H2 = ParagraphStyle("h2", fontName="Helvetica-Bold", fontSize=12.5,
                      leading=16, textColor=ACCENT, spaceBefore=14, spaceAfter=6)
S_BODY = ParagraphStyle("b", fontName="Times-Roman", fontSize=11, leading=16.5,
                        alignment=TA_JUSTIFY, spaceAfter=9, textColor=INK)
S_BULLET = ParagraphStyle("bl", parent=S_BODY, leftIndent=16, bulletIndent=4,
                          spaceAfter=6)
S_TOC = ParagraphStyle("toc", fontName="Times-Roman", fontSize=12.5, leading=24,
                       textColor=INK)
S_SMALL = ParagraphStyle("sm", fontName="Times-Italic", fontSize=9.5, leading=14,
                         alignment=TA_JUSTIFY, textColor="#666C74")


def on_page(canvas, doc):
    canvas.saveState()
    if doc.page > 2:  # no folio on title/copyright pages
        canvas.setFont("Helvetica", 8.5)
        canvas.setFillColor("#8A9098")
        canvas.drawCentredString(PAGE_W / 2, 0.45 * inch, str(doc.page))
    canvas.restoreState()


def build():
    out = os.path.join(ROOT, "dist", "The-AI-Side-Hustle-Interior.pdf")
    doc = BaseDocTemplate(out, pagesize=(PAGE_W, PAGE_H),
                          leftMargin=MARGIN, rightMargin=MARGIN,
                          topMargin=MARGIN, bottomMargin=MARGIN,
                          title=TITLE, author=AUTHOR)
    frame = Frame(MARGIN, MARGIN, PAGE_W - 2 * MARGIN, PAGE_H - 2 * MARGIN, id="f")
    doc.addPageTemplates([PageTemplate(id="p", frames=[frame], onPage=on_page)])

    story = []
    # title page
    story.append(Spacer(1, 1.7 * inch))
    story.append(Paragraph(TITLE, S_TITLE))
    story.append(Spacer(1, 20))
    story.append(Paragraph(SUBTITLE.replace("\n", "<br/>"), S_SUB))
    story.append(Spacer(1, 2.2 * inch))
    story.append(Paragraph(AUTHOR, S_AUTHOR))
    story.append(PageBreak())

    # copyright / disclaimer
    story.append(Spacer(1, 5.8 * inch))
    story.append(Paragraph("Copyright © " + AUTHOR + ". All rights reserved.", S_SMALL))
    story.append(Paragraph(DISCLAIMER, S_SMALL))
    story.append(PageBreak())

    # contents
    story.append(Spacer(1, 0.4 * inch))
    story.append(Paragraph("Contents", S_CH_TITLE))
    for i, (title, _) in enumerate(CHAPTERS, 1):
        story.append(Paragraph(
            '<font color="%s"><b>%d</b></font>&nbsp;&nbsp;&nbsp;%s' % (ACCENT, i, title),
            S_TOC))
    story.append(PageBreak())

    # chapters
    for i, (title, paras) in enumerate(CHAPTERS, 1):
        story.append(Spacer(1, 0.5 * inch))
        story.append(Paragraph("CHAPTER %d" % i, S_CH_NUM))
        story.append(Paragraph(title, S_CH_TITLE))
        for p in paras:
            if p.startswith("## "):
                story.append(Paragraph(p[3:], S_H2))
            elif p.startswith("- "):
                story.append(Paragraph(p[2:], S_BULLET, bulletText="•"))
            else:
                story.append(Paragraph(p, S_BODY))
        story.append(PageBreak())

    # closing
    story.append(Spacer(1, 0.5 * inch))
    story.append(Paragraph("Before You Go", S_CH_TITLE))
    story.append(Paragraph(CLOSING, S_BODY))
    doc.build(story)
    print("interior:", out)


def cover():
    from PIL import Image, ImageDraw, ImageFont
    W, H = 1800, 2700
    img = Image.new("RGB", (W, H))
    d = ImageDraw.Draw(img)
    # deep navy -> teal gradient
    top, bot = (18, 28, 48), (42, 111, 106)
    for y in range(H):
        t = y / H
        d.line([(0, y), (W, y)],
               fill=tuple(int(top[i] + (bot[i] - top[i]) * t) for i in range(3)))
    # rising "income bars" motif with coin dots
    import random
    random.seed(4)
    bars = [(230, 0.30), (500, 0.42), (770, 0.38), (1040, 0.55), (1310, 0.70)]
    for x, hfrac in bars:
        bh = int(H * 0.32 * hfrac)
        d.rounded_rectangle([x, H - 620 - bh, x + 200, H - 620],
                            radius=28, fill=(255, 216, 112))
        d.ellipse([x + 55, H - 720 - bh, x + 145, H - 630 - bh], fill=(255, 240, 190))
    # spark / AI glyph
    cx, cy, r = W - 380, 1240, 130
    for ang in range(0, 360, 45):
        import math
        x2 = cx + math.cos(math.radians(ang)) * (r + 70)
        y2 = cy + math.sin(math.radians(ang)) * (r + 70)
        d.line([cx, cy, x2, y2], fill=(120, 210, 200), width=14)
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(120, 210, 200))
    d.ellipse([cx - r + 35, cy - r + 35, cx + r - 35, cy + r - 35], fill=(18, 28, 48))
    d.ellipse([cx - 32, cy - 32, cx + 32, cy + 32], fill=(255, 216, 112))

    fb = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 210)
    fm = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 62)
    fa = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 72)
    d.text((W // 2, 300), "THE AI", font=fb, fill=(255, 255, 255), anchor="mm")
    d.text((W // 2, 520), "SIDE HUSTLE", font=fb, fill=(255, 216, 112), anchor="mm")
    d.text((W // 2, 760),
           "A plain-English beginner's guide to creating", font=fm,
           fill=(210, 228, 226), anchor="mm")
    d.text((W // 2, 850),
           "and selling digital products with AI", font=fm,
           fill=(210, 228, 226), anchor="mm")
    d.text((W // 2, H - 260), AUTHOR.upper(), font=fa, fill=(255, 255, 255), anchor="mm")

    out_dir = os.path.join(ROOT, "marketing", "handbook")
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "cover-front-1800x2700.png")
    img.save(path)
    print("cover:", path)


if __name__ == "__main__":
    os.makedirs(os.path.join(ROOT, "dist"), exist_ok=True)
    build()
    cover()
