# Spec ads — make a business its ad before it asks, with Seedance 2.5

Written 19 September 2026. The short you sent cannot be opened from this
environment (YouTube is blocked here), so the method below is the one
that title and every version of that video describe: make a short AI
video ad for a real local business without being asked, send it to
them, and let the ones who love it become the paying clients. It is the
oldest trick in advertising — the spec ad — with the cost of making one
collapsed to a few dollars of credits.

## The tool, and what it costs (checked 19 September 2026)

- **Seedance 2.5** is ByteDance's video model, released 7 August 2026.
  It makes 4–30 second clips at up to 1080p from text, up to fifty image,
  video and audio references, with synchronised audio, and it keeps a
  product consistent across shots — the feature that makes it usable
  for ads.
- **Where you use it:** Dreamina (dreamina.capcut.com) on the iPad —
  choose "AI Video", model "Seedance 2.5", ratio 9:16. Credits are
  bought inside Dreamina. The API route (about US$0.10 a second through
  OpenRouter or WaveSpeed) is for later, when there is volume.
- **Commercial use:** Dreamina's own guidance says paid-plan output can
  be used commercially; read the page linked in the sources before the
  first paid job. Do not use a business's logo or photos in a clip you
  publish; in a private spec you send *to them*, referencing their
  product is what the spec is for.

## The method, step by step

1. **Pick ten businesses that sell something you can film without a
   camera.** Cafés, bakeries, furniture, pilates, skincare, florists —
   visual products, small teams, an Instagram they run themselves and
   no video worth watching on it. Ten are picked in TARGETS.md.
2. **Write the ad first, in words.** One line of hook, three shots,
   one line of offer, one call to action. Fifteen seconds. The concept
   and the exact Seedance prompt for each business are in TARGETS.md;
   the prompt formula is in PROMPTS.md.
3. **Generate in Dreamina.** Three shots of five seconds each, or one
   fifteen-second clip. Use their own product photo from their public
   Instagram as an image reference so the croissant looks like *their*
   croissant. Two generations per shot; keep the better one.
4. **Send the clips here.** I finish the ad: captions in the safe zone,
   their name and offer on an end card, generated music, 1080×1920,
   under 15 MB. The script is scripts/spec_ad.py; on your side it is
   "upload three clips, get back one ad" in a few minutes.
5. **Send it privately, never post it.** Instagram DM or the contact
   form on their site, with the message in TARGETS.md. The ad is the
   message; the text is three lines.
6. **The offer when they reply:** three ads a month for their
   Instagram, delivered finished, at the Standard tier of the Fiverr
   video gig or a monthly fee — your call. Say plainly the video is
   AI-generated from their product; some will care, most will not.

## What to expect, honestly

Of ten businesses sent a finished ad, a few will reply and thank you,
one or two will ask what it costs, and the rest will say nothing. That
is a normal spec-ad hit rate and it is far better than a cold message,
because the work arrives already done. The first paying client usually
comes from the second batch of ten, after the first batch taught you
what these businesses respond to.

Ten ads cost roughly ten to twenty dollars of Dreamina credits and one
evening. That is the cheapest customer acquisition anything in this
repo has ever had.

## Rules

- Never claim a result ("this will double your sales"). The ad shows
  their product well; that is the claim.
- Say it is AI-made when asked, and before any paid work.
- Do not publish a spec ad anywhere public. It is theirs to post or bin.
- No fake reviews, no invented "as seen on", no prices you made up for
  their products — use the price from their own menu or say nothing.
- The owner's employer, title and city stay out of every message.
