# The Silicon Ledger — a cheap first Amazon Ads test

Written 19 September 2026. This is a two-week test with a hard cap, not
a campaign. Its job is to find out whether the book converts when a
reader who is looking for this subject sees it. The budget below is the
owner's to change.

## Before spending a cent — the order matters

1. **Reviews first, ads second.** An ebook with zero reviews converts
   badly no matter how good the ad is; readers use the review count as
   a proxy for "is this real". Run the review kit
   (REVIEW-REQUEST-KIT.md) for two weeks and start ads once the page
   shows three or more honest reviews. Ads on a zero-review page mostly
   buy clicks that bounce.
2. **Fix the page the ad lands on.** A+ Content (already made in
   marketing/aplus/) uploaded; the description as in the paste file;
   seven keyword slots filled; two categories that are actually reached
   (the paste file lists them); the "Look Inside" sample showing the
   first chapter, not the copyright page.
3. **Advertise on Amazon.com only.** That is where Singapore, Malaysia
   and the US buy Kindle books. Do not spread the budget across
   marketplaces.

## Where the ads console is

KDP Bookshelf → the book's "…" menu → "Promote and Advertise" → "Run an
ad campaign" → United States. Sponsored Products only. Ignore Sponsored
Brands and lockscreen ads for now.

## The three campaigns

| Campaign | Targeting | Daily budget | Starting bid | Runs |
|---|---|---|---|---|
| A — Auto | Automatic (Amazon picks) | US$3 | default, capped at US$0.45 | 14 days |
| B — Keywords | Manual, the phrase list below, phrase match | US$4 | US$0.40 | 14 days |
| C — Products | Manual, the three books below + the category "Semiconductors" | US$3 | US$0.45 | 14 days |

Total exposure: US$10 a day × 14 days = **US$140 maximum**, and Amazon
rarely spends the full daily budget on a new book. Expect US$60–100 to
actually go out. Bid figures are starting points, not predictions; the
guides for authors put typical Kindle non-fiction clicks in the tens of
cents, and the console will show the real number within three days.

Campaign settings that matter: campaign bidding strategy "Dynamic bids —
down only"; no placement multipliers; end date set, so nothing runs on
after you stop looking.

### Campaign B — keyword phrases (phrase match)

    semiconductor industry
    chip war
    nvidia
    nvidia book
    ai chips
    tsmc
    asml
    semiconductor book
    artificial intelligence business
    ai industry
    high bandwidth memory
    data center
    hyperscalers
    openai
    anthropic
    depreciation
    technology history book
    jensen huang

Eighteen phrases. Do not add more until the first fourteen days are
read; a long list on a small budget spreads the spend so thin that no
phrase reaches ten clicks, and ten clicks is the minimum to judge one.

### Campaign C — product targets (Amazon.com Kindle ASINs, checked 19 Sep 2026)

| Book | ASIN |
|---|---|
| Chip War — Chris Miller | B09RX4SD88 |
| The Thinking Machine — Stephen Witt | B0D1QFBGQD |
| The Nvidia Way — Tae Kim | B0DFV1HS1R |

Plus the category target "Kindle Store › Business & Money › Industries"
if the console offers it, and "Semiconductors" under Engineering. The
ad then appears on those books' pages under "Products related to this
item" — a reader who has just bought Chip War is the exact reader for
this book.

## Reading the results (day 7 and day 14)

From the console's campaign table:

- **Impressions under 1,000 after 7 days** → bids are too low for the
  auction. Raise each starting bid by US$0.10. Nothing else.
- **Clicks but CTR under 0.2%** → the cover or title is not stopping
  the scroll. That is a listing problem, not an ad problem.
- **Clicks and no orders after 30 clicks** → the page is not converting:
  reviews, description or price. Pause and fix before spending more.
- **ACOS** (ad spend ÷ sales): at a US$9.99 ebook the royalty is about
  US$7 (70% minus delivery), so ACOS under 70% is profitable, under 50%
  is good. Above 100% for a full 14 days means stop.
- Amazon's console lags one to three days on sales. Do not judge on
  day 2.

## What "cheap" means honestly

US$140 is cheap relative to what authors spend. It is expensive if the
page has no reviews, because then it buys nothing. The test is
designed so that the money is only spent once the page is ready, and
so that it stops itself.

## What is not on this list

Facebook and TikTok ads for a US$9.99 ebook (the cost of a click is
higher than the royalty), paid review services (against Amazon's rules
and grounds for removal), and "book promotion" sites that want money
for a newsletter blast without showing their list size.
