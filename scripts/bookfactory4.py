#!/usr/bin/env python3
"""Status tool for 'A Story for Every Night' (365-tale anthology).

  python3 scripts/bookfactory4.py status
  (build: EPUB assembly lands once month 1 is complete)
"""

import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BF = os.path.join(ROOT, "bookfactory4")
STORIES = os.path.join(BF, "stories")

MONTHS = ["January", "February", "March", "April", "May", "June", "July",
          "August", "September", "October", "November", "December"]


def status():
    plan = json.load(open(os.path.join(BF, "plan.json")))
    files = sorted(f for f in os.listdir(STORIES) if f.endswith(".md"))
    total_target = sum(m["stories"] for m in plan["months"])
    words = 0
    per_month = {}
    problems = []
    for f in files:
        m = re.match(r"(\d\d)-(\d\d)-", f)
        if not m:
            problems.append("bad filename: " + f)
            continue
        per_month[int(m.group(1))] = per_month.get(int(m.group(1)), 0) + 1
        txt = open(os.path.join(STORIES, f)).read()
        w = len(txt.split())
        words += w
        if not 370 <= w <= 455:
            problems.append("%s: %d words (target 380-450)" % (f, w))
    print("%s — %d/%d stories (~%dk words of ~150k)"
          % (plan["title"], len(files), total_target, words // 1000))
    for mi, mo in enumerate(plan["months"], 1):
        have = per_month.get(mi, 0)
        if have:
            print("  %s: %d/%d" % (MONTHS[mi - 1], have, mo["stories"]))
    nxt = None
    for mi, mo in enumerate(plan["months"], 1):
        have = per_month.get(mi, 0)
        if have < mo["stories"]:
            nxt = (MONTHS[mi - 1], have + 1, mo["theme"])
            break
    if nxt:
        print("NEXT: %s %d — theme: %s" % nxt)
    else:
        print("COMPLETE — all 365 stories written.")
    for p in problems:
        print("  ⚠", p)
    return not problems


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "status":
        ok = status()
        sys.exit(0 if ok else 1)
    status()
