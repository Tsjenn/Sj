# Ember — a focus timer with a dragon

Built 19 September 2026 at the owner's request for "a fantasy app that
is useful". It copies the mechanic that made Forest one of the
best-selling paid apps ever — focus and something grows, leave and it
withers — with a dragon instead of a tree.

## What it is
- Choose 15, 25, 45 or 60 minutes. Light the ember. Stay in the app.
- Leave for more than ten seconds and the session fades: nothing feeds
  the dragon. That is the whole trick, and it is why this category works.
- Kept minutes grow the dragon: egg → hatchling (1 h) → drake (5 h) →
  wyrm (15 h) → elder (40 h). Only kept sessions count.
- A daily quest (25–150 minutes) with a streak; a hoard page with the
  week's bars and best day.
- Offline PWA, no account, no server, no analytics inside the app.

## Money
- Free. The "Ember key" unlocks three extra colours and, later, a second
  dragon. Sold as a code on Gumroad, same pattern as the game DLC.
- Set the price and link in site/config.js → products.ember.
- To make a key: choose a code, then

      python3 -c "import hashlib,sys;print(hashlib.sha256(sys.argv[1].upper().encode()).hexdigest())" YOUR-CODE

  and paste the hex into KEY_HASHES in site/ember/app.js. Never commit
  the code itself. The hash in the file today is a placeholder that
  matches nothing.

## Store path
Same as Causeway: Capacitor wrapper, Codemagic for the iOS build,
US$99 Apple, US$25 Google plus 12 testers for 14 days. See
app/causeway/README.md; copy the folder and change appId and webDir.

## Honest note
Forest sold because it launched in 2014 into an App Store that still
surfaced new apps and then rode word of mouth for a decade. A copy of
its mechanic in 2026, however charming, needs the same thing every
other product here needs: someone to see it. The TikTok pipeline can
make a 3D phone clip of the dragon in a morning; that is the next
step, not another feature.
