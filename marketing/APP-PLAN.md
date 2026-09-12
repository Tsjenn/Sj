# App plan — "copy the most successful US app for Malaysia and Singapore"

Written 2026-09-12 after a research pass. This is the honest version.
Read it before spending money on developer accounts.

## 1. What actually tops the US charts, and why it cannot be copied

Top-grossing US App Store, early September 2026 (Peekly, AppCurrents,
Applyra estimates): ChatGPT, YouTube, TikTok, Snapchat, MONOPOLY GO!,
Audible, Hinge, Dropbox. The top ten take a median of roughly $30M a
month, and every one of the top 100 is free to download and monetised
by subscription or in-app purchase.

None of these is a product a solo builder can copy:

- ChatGPT / YouTube / TikTok / Snapchat / Hinge are platform or network
  businesses. Their value is the other users, not the code.
- MONOPOLY GO! is a licensed IP with a nine-figure marketing budget.
- Audible is Amazon's catalogue.

"Copy the top app" is therefore not a plan. What is copyable is the
pattern behind the indie breakouts underneath them.

## 2. The copyable pattern (the Cal AI archetype)

Cal AI: photograph food, get a calorie number. Built by teenagers,
15M+ downloads and $30M+ annual revenue in under two years, acquired by
MyFitnessPal in March 2026. Its mechanics, which are the thing to learn:

1. One job. One input. One number back in seconds.
2. A visible "score" that changes daily, so people return.
3. Weekly/annual subscription, free trial, paywall on first result.
4. Distribution by short video, not by app-store search.

Also worth learning from: it was pulled from the App Store in April 2026
over deceptive billing and suffered a 3.2M-user data breach. Copy the
mechanics, not the dark patterns.

## 3. Every obvious localisation is already taken

Checked 2026-09-12. This is the part that changes the decision.

| Localised idea | Who already ships it in MY/SG |
|---|---|
| Photo-calorie counter for hawker food | Welling, KiloKaki (SG, "85–90% on common meals"), Lifesum regional database, MyFitnessPal (now owns Cal AI) |
| Receipt-scan tax-relief tracker (LHDN categories) | MyTaxMate, ReceiptLah, MudahCukai, TaxBuddy, TaxSaver, FinPersona, ClaimLah — seven |
| Causeway / checkpoint traffic | JB SG Traffic Live, JB SG Checkpoints & Traffics, Interlink SG, SG Checkpoint, CausewayTraffic.sg, JAM-GO |
| Malaysian budgeting | RinggitWise, Money Manager, Wallet, plus MAE / CIMB / GXBank built-ins |
| Generic 183-day residency counter | Resident Live, Tax Resident Days Tracker, DayTally, Tax Residency Tracker, Domicile365 |

The window for "Cal AI for X in Malaysia" mostly closed during 2025.
Entering any of these as the fourth to eighth entrant, with no marketing
budget, is the weakest possible position.

## 4. Indie-app economics, stated plainly

- Honest median for a solo developer: under $1,000 a month.
- Realistic top-quartile solo result: $3,000–$15,000 a month after
  12–18 months, with tight niche positioning and subscriptions.
- Subscription apps take 18–24 months to compound to a full-time income.
- App-store search is a worse discovery channel than Amazon's; an app
  with no audience gets no installs.

Nobody can promise an app will be successful. Anyone who does is selling
something. What can be done is to pick the one gap where the odds are
not already stacked against us, and build it properly.

## 5. The gap that is still open: money that crosses the Causeway

Evidence:

- ~300,000 people cross the Johor–Singapore Causeway every day (reported
  as the world's busiest land border).
- The RTS Link opens around 1 January 2027 with ~40,000 riders a day
  expected at launch, rising towards 140,000. That is a wave of new
  commuters, new job offers, and new searches — a timing catalyst.
- The traffic side is crowded (table above). The *money* side is not.
  Nothing on either store models a cross-border pay packet: SGD salary in
  ringgit as the rate moves, what the commute actually costs a month, and
  where the commuter stands on Malaysia's 182-day and Singapore's 183-day
  residency tests at the same time. Generic day-counters exist for
  nomads; none handle a daily commuter who is in both countries on the
  same day, which is the whole problem.
- The owner's edge is real here: a chartered accountant who lives on
  this corridor, with a finance audience being built, and an existing
  tool (tools/jb-sg-pay/) that already answers the offer question.

So the app is **Causeway** — the commuter's money companion.

- **Today**: your Singapore pay in ringgit at today's rate, and how far
  it has moved since the day you signed. One number, changes daily.
- **Commute**: tap to log a crossing (mode, cost). Month total. RTS fare
  ready to slot in when it is gazetted.
- **Days**: mark each day MY / SG / both / away. Live counters against
  182 (Malaysia) and 183 (Singapore), days left in the year, and an
  honest explanation of what meeting both tests means (treaty
  tie-breaker, see a practitioner).
- **Offer**: the pay-check tool, one tap away.
- Everything stays on the device. The only network call is the exchange
  rate. Export and import as a file.

## 6. Why this fits "other countries" better than a clone would

The same product ships to any commuter border with a different data
file: Shenzhen–Hong Kong, Malmö–Copenhagen, Windsor–Detroit,
Luxembourg's three borders, Geneva–France, Basel. Each has its own pair
of residency tests, currencies and fares — and the same lack of a money
companion. That is a real expansion path. A cloned calorie app has none.

## 7. iOS and Android: how it actually ships, with costs

1. **Now, free**: it is a Progressive Web App at /causeway/. On iPhone:
   Share → Add to Home Screen. On Android: Chrome offers Install. It
   works offline and has an icon. No developer accounts needed.
2. **App Store**: Apple Developer Program, US$99 a year. The wrapper is
   Capacitor (app/causeway/). Without a Mac, Codemagic's free tier
   (500 macOS minutes a month) or Capawesome Cloud builds and uploads
   the .ipa; submission is then done from a browser.
3. **Google Play**: US$25 once. A personal account created after
   November 2023 must run a closed test with 12 testers opted in
   continuously for 14 days before it can go to production. Plan for
   three to four weeks.
4. App Store guideline 4.1 rejects copycats. This app is not a copy of
   anything, which is one more reason to build this rather than a clone.

## 8. What I will not do

- Promise it will be successful.
- Invent user counts, testimonials or income figures for the listing.
- Add a subscription price. Prices are the owner's decision; the app
  ships free with the paid tier left as a design decision.
- Use the words accountant, tax consultant or auditor anywhere public.

## 9. The decision the owner still has to make

INCOME-PLAN.txt argued for 0% of effort on new products until the first
sale. This app was built because the owner asked for it explicitly, and
because it is the demand-side asset in the exact niche the owner lives
in — closer to a lead magnet than a 21st SKU. If it does not earn
installs from the RTS launch wave by March 2027, stop and go back to the
plan.
