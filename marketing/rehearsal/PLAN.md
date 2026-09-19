# Rehearsal — what was built, and what the Stella story actually says

Written 19 September 2026, after the owner sent a video about Stella, a
manifesting app reported to reach $340,000 a month within two months.

## What the video leaves out

- The founder's own LinkedIn headline reads "4.5M+ followers". The app
  launched into an audience of four and a half million people who
  already bought her $888 course. The app is the checkout; the audience
  is the business.
- Every revenue figure comes from the founder's interviews (Starter
  Story, podcasts). None of it is audited, and the same interviews are
  used to sell the story of the app.
- Manifestation apps do not appear in any top-grossing chart; the
  category earns through creator audiences, not through the store.
- The technical claim is true and cheap: an app like this is a text
  generator, a text-to-speech voice, and a subscription screen. The
  hard part was never the code.

So the honest reading is: the same app, built by someone with no
audience, earns what the twenty products before it earned. That was
said before building, and the owner asked for it anyway, so it was
built — as the version that can be defended.

## What Rehearsal is (and how it differs from Stella)

- Same mechanic: the reader writes one thing they want, and gets a
  first-person, present-tense story of the day it has already happened,
  read aloud. Daily. Kept in a library.
- Different claim. Stella says visualising brings things about.
  Rehearsal says nothing of the kind. It pairs the vivid picture with
  one concrete step for the day, because the research on mental
  contrasting and implementation intentions (Oettingen, Gollwitzer)
  found that the pairing helps and the picture alone does not. The
  seven-day step tracker is the point of the app; the story is the
  hook that gets someone to it.
- No "universe", "energy", "vibration", "manifest" anywhere in the
  copy or the story engine.
- Free tier costs nothing to run: stories are assembled on the phone
  from what the reader wrote, with the phone's own voice. Works
  offline. No accounts, no server, no data leaves the device.
- Paid tier: stories written fresh by Claude through a small Cloudflare
  Worker (worker/rehearsal/), unlocked with a code sold on Gumroad. The
  Worker keeps nothing. Cost per story is a few US cents.

## Where it lives

- App: https://tsjenn.github.io/Sj/rehearsal/ (installable on iPhone and
  Android from the browser — same path as Causeway).
- Worker + deploy steps + unlock-code hashing: worker/rehearsal/README.md
- Store entry: site/config.js → products.rehearsal (price, Gumroad link,
  Worker URL — all SET-ME until the owner sets them).

## To earn anything from it, in order

1. Deploy the Worker (ten minutes) and put its URL in config.js. Until
   then the "Write it with AI" button is hidden and the app is simply
   free.
2. Create the Gumroad product "Rehearsal — AI-written stories, one-year
   code". Generate a code, hash it into the Worker, paste the Gumroad
   link and price into config.js.
3. Then the part no build can do: the same three channels as
   everything else — the TikTok pipeline already exists (a 3D phone
   mock-up of the app turning under light is a thirty-minute job with
   book_clips3d.py), the Etsy shop, the Fiverr studio. An app with no
   audience earns nothing, and this one is not different.

## What is not claimed

No user numbers, no testimonials, no promise about outcomes, no
"passive". The word passive does not describe any of this; it describes
the founder's four and a half million followers.
