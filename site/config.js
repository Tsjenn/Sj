/* ============================================================
   STORE CONFIGURATION — this is the ONLY file you need to edit.

   1. Create a free account at https://gumroad.com
   2. Upload each zip from the /dist folder as a product
   3. Copy each product's short link (e.g. https://yourname.gumroad.com/l/budget)
   4. Paste the links below, replacing the SET-ME placeholders
   5. Optionally change the store name, email, and prices shown
   ============================================================ */

window.STORE = {
  name: "Clarity Templates",
  tagline: "Simple tools to organize your money, work, and goals.",
  supportEmail: "tangshiuanjenn@gmail.com",

  // Amazon Associates tag (e.g. "tangshiuan-20"). Once set, guide pages
  // automatically add it to Amazon product links and show the required
  // disclosure. SET-ME = affiliate links stay plain, nothing breaks.
  amazonTag: "SET-ME",

  // Displayed prices — set the SAME prices on Gumroad.
  // Gumroad accepts payments worldwide and handles VAT/sales tax for you.
  products: {
    budget: {
      price: "$9",
      link: "https://tangshiuan.gumroad.com/l/klwxce",
    },
    invoice: {
      price: "$12",
      link: "https://tangshiuan.gumroad.com/l/acroek",
    },
    planner: {
      price: "$7",
      link: "https://tangshiuan.gumroad.com/l/utqhxl",
    },
    bundle: {
      price: "$19",
      link: "https://tangshiuan.gumroad.com/l/brzfl",
    },
    game: {
      price: "$6",
      link: "https://tsjenn.itch.io/critter-isles",
    },
    park: {
      price: "$9",
      link: "https://tsjenn.itch.io/wildhaven",
    },
    arena: {
      price: "$9.99",
      link: "https://tsjenn.itch.io/wildhaven-arena",
    },
    racer: {
      price: "$9.99",
      link: "https://tsjenn.itch.io/neon-drift-racers-drift-boost-race-the-world",
    },
    sleep: {
      price: "$4.99",
      link: "https://tangshiuan.gumroad.com/l/ycrcl",
    },
    // Free lead magnet ($0+ on Gumroad) — every download collects a reader
    // email into the owner's Gumroad audience.
    starter: {
      price: "Free",
      link: "https://tangshiuan.gumroad.com/l/qubre",
      fallback: "downloads/Honest-Sleep-Starter.pdf",
    },
    skyline: {
      price: "$9.99",
      link: "https://tsjenn.itch.io/skyline",
    },
    music: {
      price: "$5+",
      link: "https://sjsjsj.bandcamp.com/album/sj",
    },
    book: {
      price: "$4.99",
      link: "https://www.amazon.com/dp/B0HCKYM617",
    },
    book2: {
      price: "$4.99",
      link: "https://www.amazon.com/dp/B0HCL3YCKJ",
    },
    huanjing: {
      price: "$3.99",
      link: "https://tangshiuan.gumroad.com/l/asvsdb",
    },
    // The three 2026 Kindle titles. Links are live; put YOUR Amazon list
    // price in each price field — SET-ME just hides the price, the link
    // still works.
    aibook: {
      price: "SET-ME",
      link: "https://www.amazon.com/dp/B0HG6VFYXP",
    },
    matcha: {
      price: "SET-ME",
      link: "https://www.amazon.com/dp/B0HG5ZY46K",
    },
    novel: {
      price: "SET-ME",
      link: "https://www.amazon.com/dp/B0HG6VGHDM",
    },
    // AI for Finance Teams — The Working Pack.
    // Upload dist/AI-For-Finance-Teams.zip to Gumroad, then paste the link
    // and YOUR chosen price here. Priced for firms, not individuals — this
    // is a team artefact, not a $9 template. The price is your decision.
    financepack: {
      price: "SET-ME",
      link: "SET-ME",
    },
  },
};
