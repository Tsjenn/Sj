/* Rehearsal — story server (Cloudflare Worker).
   Receives {name, wish, when, why, setting, witness, step}, asks Claude for a
   first-person "future memory", returns {title, paragraphs}. Keeps nothing.

   Environment variables (Cloudflare dashboard → Worker → Settings → Variables):
     ANTHROPIC_API_KEY   secret — the owner's key, never shipped to the browser
     ALLOWED_HASHES      comma-separated SHA-256 hex of valid unlock codes
     MODEL               optional, default claude-opus-5
     ALLOWED_ORIGIN      optional, default https://tsjenn.github.io
*/
const SYSTEM = `You write short first-person "future memories" for a focus app called Rehearsal.
The reader has written down one specific thing they want. Write the day it has already happened.

Rules:
- First person, present tense, 380–460 words, 6–8 short paragraphs.
- Ordinary and concrete: the light, a sound, what is in their hands, what someone says. No magic, no "universe", no "manifest", no "energy", no "vibration". No advice. No promises about the future. No exclamation marks.
- Include the place, the person who notices, and the reason it matters, using the reader's own words where you can.
- Near the end, the reader remembers the first small step they once took, in one plain sentence. Then a quiet final line.
- Give it a title of at most eight words, no quotation marks.

Return JSON only: {"title": "...", "paragraphs": ["...", "..."]}`;

async function sha256(s) {
  const b = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(s));
  return [...new Uint8Array(b)].map(x => x.toString(16).padStart(2, "0")).join("");
}

export default {
  async fetch(request, env) {
    const origin = env.ALLOWED_ORIGIN || "https://tsjenn.github.io";
    const cors = {
      "Access-Control-Allow-Origin": origin,
      "Access-Control-Allow-Methods": "POST, OPTIONS",
      "Access-Control-Allow-Headers": "Content-Type, X-Unlock",
      "Content-Type": "application/json"
    };
    if (request.method === "OPTIONS") return new Response(null, { headers: cors });
    if (request.method !== "POST") return new Response(JSON.stringify({ error: "POST only" }), { status: 405, headers: cors });

    const code = (request.headers.get("X-Unlock") || "").trim().toUpperCase();
    if (!code) return new Response(JSON.stringify({ error: "unlock code required" }), { status: 401, headers: cors });
    const allowed = (env.ALLOWED_HASHES || "").split(",").map(s => s.trim().toLowerCase()).filter(Boolean);
    if (!allowed.includes(await sha256(code))) {
      return new Response(JSON.stringify({ error: "that code is not valid" }), { status: 403, headers: cors });
    }

    let body;
    try { body = await request.json(); } catch { return new Response(JSON.stringify({ error: "bad json" }), { status: 400, headers: cors }); }
    const clean = k => String(body[k] || "").slice(0, 400).replace(/[\r\n]+/g, " ").trim();
    const p = { name: clean("name"), wish: clean("wish"), when: clean("when"), why: clean("why"),
                setting: clean("setting"), witness: clean("witness"), step: clean("step") };
    if (!p.wish) return new Response(JSON.stringify({ error: "wish is required" }), { status: 400, headers: cors });

    const user = `Name: ${p.name || "the reader"}
The thing, written as already true: ${p.wish}
When: ${p.when || "six months from now"}
Why it matters: ${p.why || "(not given)"}
Where the day happens: ${p.setting || "at home"}
Who notices: ${p.witness || "someone close"}
The first small step they once took: ${p.step || "(not given)"}
Today's date: ${new Date().toISOString().slice(0, 10)}`;

    const r = await fetch("https://api.anthropic.com/v1/messages", {
      method: "POST",
      headers: {
        "x-api-key": env.ANTHROPIC_API_KEY,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json"
      },
      body: JSON.stringify({
        model: env.MODEL || "claude-opus-5",
        max_tokens: 1200,
        system: SYSTEM,
        messages: [{ role: "user", content: user }]
      })
    });
    if (!r.ok) {
      return new Response(JSON.stringify({ error: "the writer is unavailable right now" }), { status: 502, headers: cors });
    }
    const j = await r.json();
    const text = (j.content || []).filter(c => c.type === "text").map(c => c.text).join("");
    let out;
    try {
      out = JSON.parse(text.slice(text.indexOf("{"), text.lastIndexOf("}") + 1));
    } catch {
      out = { title: "The day it happened", paragraphs: text.split(/\n\s*\n/).filter(Boolean) };
    }
    if (!Array.isArray(out.paragraphs) || !out.paragraphs.length) {
      return new Response(JSON.stringify({ error: "empty story" }), { status: 502, headers: cors });
    }
    return new Response(JSON.stringify({ title: String(out.title || "").slice(0, 80), paragraphs: out.paragraphs.map(String).slice(0, 10) }), { headers: cors });
  }
};
