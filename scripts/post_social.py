#!/usr/bin/env python3
"""Post the next queued item from social/queue.json to X (Twitter).

Runs daily from .github/workflows/social.yml. Requires four repository
secrets (never stored in the repo): X_API_KEY, X_API_SECRET, X_ACCESS_TOKEN,
X_ACCESS_SECRET — created free at developer.x.com for the account being
posted to. Posting to your own account through the official API is the
ToS-compliant way to automate.

Behaviour:
- secrets missing        -> exit 0 with a notice (setup not done yet)
- queue exhausted        -> exit 0 with a notice (agents refill the queue)
- API rejects the post   -> exit 1 so the workflow run shows red
- success                -> advance the queue pointer (workflow commits it)
"""

import json
import os
import re
import sys

QUEUE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                     "social", "queue.json")


def tweet_len(text):
    """Length as X counts it: every URL becomes a 23-char t.co link."""
    return len(re.sub(r"https?://\S+", "x" * 23, text))


def main():
    keys = {k: os.environ.get(k, "").strip()
            for k in ("X_API_KEY", "X_API_SECRET", "X_ACCESS_TOKEN", "X_ACCESS_SECRET")}
    if not all(keys.values()):
        print("X API secrets not configured — skipping (add the four secrets "
              "in GitHub repo Settings > Secrets and variables > Actions).")
        return 0

    with open(QUEUE) as f:
        q = json.load(f)
    if q["next"] >= len(q["posts"]):
        print("Queue empty — nothing to post. The agents top it up via the "
              "message board; nothing to do today.")
        return 0

    text = q["posts"][q["next"]]
    if tweet_len(text) > 280:
        print("Post %d is %d chars (>280); skipping it." % (q["next"], tweet_len(text)))
        q["next"] += 1
        with open(QUEUE, "w") as f:
            json.dump(q, f, indent=1, ensure_ascii=False)
        return 0

    from requests_oauthlib import OAuth1Session
    session = OAuth1Session(keys["X_API_KEY"], keys["X_API_SECRET"],
                            keys["X_ACCESS_TOKEN"], keys["X_ACCESS_SECRET"])
    resp = None
    for endpoint in ("https://api.x.com/2/tweets", "https://api.twitter.com/2/tweets"):
        try:
            resp = session.post(endpoint, json={"text": text})
            break
        except Exception as e:            # DNS/connection issue: try the alias
            print("endpoint %s failed: %s" % (endpoint, e))
    if resp is None:
        print("Could not reach the X API at all.")
        return 1

    if resp.status_code in (200, 201):
        q["next"] += 1
        with open(QUEUE, "w") as f:
            json.dump(q, f, indent=1, ensure_ascii=False)
        print("Posted item %d: %s..." % (q["next"] - 1, text[:70].replace("\n", " ")))
        return 0

    if resp.status_code == 402:
        # X's API paywall: the free tier includes no posting credits. Exit
        # cleanly so the daily run doesn't spam failure emails — if credits
        # ever exist (paid or restored free tier), posting resumes untouched.
        print("X API says posting requires paid credits (402). Skipping — "
              "the queue is preserved and posting resumes automatically if "
              "credits become available.")
        return 0

    print("X API error %s: %s" % (resp.status_code, resp.text[:500]))
    return 1


if __name__ == "__main__":
    sys.exit(main())
