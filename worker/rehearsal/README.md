# Rehearsal story server

The free tier of the app needs no server: stories are assembled on the
phone. This Worker exists only for the paid "AI-written" tier.

## Deploy (about ten minutes, once)

1. Cloudflare dashboard → Workers → Create → paste `index.js`, or run
   `npx wrangler deploy` from this folder.
2. Settings → Variables: add the secret `ANTHROPIC_API_KEY` (from
   console.anthropic.com). Add `ALLOWED_HASHES`.
3. Put the Worker URL into `site/config.js` under
   `products.rehearsal.writer`.

## Unlock codes

Make a code per buyer (or one code for the Gumroad product). Store only
the SHA-256 of each code in `ALLOWED_HASHES`, comma-separated:

    python3 -c "import hashlib,sys;print(hashlib.sha256(sys.argv[1].upper().encode()).hexdigest())" YOUR-CODE

Never commit a code. The same rule as the game DLC codes.

## Cost

Each AI-written story is one Claude call of roughly 500 input and 700
output tokens. At claude-opus-5 list prices that is a few US cents a
story; set `MODEL` to a smaller model in `wrangler.toml` if the price
of the unlock does not cover it. The Worker itself runs on Cloudflare's
free tier at this volume.

## What it never does

Stores a story, logs a wish, or identifies a user. There are no
accounts. The only thing checked is that the unlock code's hash is on
the list.
