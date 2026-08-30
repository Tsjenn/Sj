#!/usr/bin/env python3
"""The 'Also by' page that goes in the back of every book.

One catalogue, generated from site/config.js so a book can never point at
a dead link or a title that was renamed. Each book skips itself.

    from alsoby import also_by_html
    html = also_by_html(skip="ledger")

Honest by construction: it lists only titles with a live store link, says
nothing about sales or rankings, and makes no claim about any book beyond
what it is.
"""

import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# key -> (title, one honest line about what it is)
CATALOGUE = [
    ("ledger", "The Silicon Ledger",
     "Who really owns artificial intelligence, and what the accounts say. "
     "A financial history of the AI and semiconductor industry, read from "
     "company filings. 77 chapters."),
    ("aibook", "AI Without the Hype",
     "The professional&#8217;s complete guide to artificial intelligence at "
     "work: prompting, verification, agents, and sixteen industry playbooks. "
     "68 chapters, and one on when not to use it at all."),
    ("novel", "The Amah&#8217;s Daughter",
     "A novel of secrets, love and war in old Malaya. Malacca, 1934: a girl "
     "arrives with a secret she does not know she is carrying."),
    ("matcha", "Matcha",
     "The whole story of the whisked leaf &#8212; history, craft, science, "
     "and sixty-three recipes."),
]


def _links():
    src = open(os.path.join(ROOT, "site", "config.js")).read()
    out = {}
    for key, _, _ in CATALOGUE:
        m = re.search(r"\b%s:\s*\{[^}]*?link:\s*\"([^\"]+)\"" % key, src, re.S)
        if m and "SET-ME" not in m.group(1):
            out[key] = m.group(1)
    return out


def also_by_html(skip=None):
    live = _links()
    rows = []
    for key, title, blurb in CATALOGUE:
        if key == skip or key not in live:
            continue
        rows.append(
            "<p style=\"margin:0 0 1.4em\">"
            "<strong>%s</strong><br/>%s<br/>"
            "<span style=\"font-size:0.9em\">%s</span></p>"
            % (title, blurb, live[key]))
    if not rows:
        return ""
    return ("<h1>Also by Tang Shiuan Jenn</h1>" + "".join(rows) +
            "<p style=\"font-size:0.9em\">If this book was useful, the most "
            "helpful thing you can do is leave an honest review. It is the "
            "only thing that helps other readers find it.</p>")


if __name__ == "__main__":
    for k, t, _ in CATALOGUE:
        print(k, "->", "live" if k in _links() else "no link yet")
