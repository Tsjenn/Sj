# Why Google shows you the Amazon.in page, and how to point everyone at Amazon.com

## Why it happens

Amazon runs a separate storefront per country and Google indexes each
one as a separate page. Which one Google shows depends on the searcher:
their location, their language, and which storefront they have visited
before. Your own results show amazon.in because your Amazon account and
browsing history are on the Indian store (the "ast_author_mpb" link in
your message is an Author Central India link). A stranger in Singapore
searching the same title sees something different — usually amazon.com,
sometimes nothing yet, because the .com page for a new ASIN is not
always indexed for weeks.

Two facts settle where readers should go:

- **There is no Kindle store for Singapore or Malaysia.** Readers there
  buy from Amazon.com. So the link you share everywhere is
  https://www.amazon.com/dp/B0HG7RHNL4 — always.
- **A KDP ebook keeps the same ASIN in every store**, so the same ASIN
  works on .co.uk, .com.au, .ca, .de and .in when you need those.

## What has been done today

1. A landing page at https://tsjenn.github.io/Sj/ledger/ with the cover,
   the full description, the Amazon.com button first, the other stores
   below, and a plain note for Singapore and Malaysia readers. It
   carries schema.org Book data with an offer per store, which is what
   Google reads to show a book result with the right storefront.
2. It links to the .com page, which gives Google a reason to crawl and
   index that page.
3. It is in the site's sitemap.

## What you do (fifteen minutes)

1. **Author Central on Amazon.com**: author.amazon.com — claim the book,
   add the bio and photo. This is a different site from Author Central
   India, and it is the one US and Singapore readers see.
2. **Put the .com link everywhere**: LinkedIn profile "featured",
   TikTok bio, the Gumroad profile, email signature. Never the .in link.
3. **Optional, free, and worth it**: make a universal link at
   booklinker.com (free) — one link that sends each reader to their own
   country's store. Use it in social bios; use the plain .com link in
   emails to people you know are in Singapore, Malaysia or the US.
4. **Google Search Console**: add the site property if not already, and
   request indexing of /ledger/. Google then usually crawls within days.

## What will not help

Paying anyone to "rank your book on Google". A book page ranks on Google
when the book has reviews, sales and links pointing at it — the same
three things that make it rank inside Amazon.
