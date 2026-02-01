#!/usr/bin/env node

function readStdin() {
  return new Promise((resolve, reject) => {
    let data = "";
    process.stdin.setEncoding("utf8");
    process.stdin.on("data", (chunk) => (data += chunk));
    process.stdin.on("end", () => resolve(data));
    process.stdin.on("error", reject);
  });
}

function pickEasterEggs(items) {
  const eggs = [];
  eggs.push("a tiny banana sticker hidden on a studio camera");
  eggs.push("a small lion plush sitting on a side table");

  const titles = items.map((i) => String(i.title || "")).join(" \n ").toLowerCase();

  if (/(regierung|parlament|wahl|koalition|kanzler|minister)/.test(titles)) {
    eggs.push("a subtle miniature parliament building silhouette as a desk ornament" );
  }

  if (/(eu|brüssel|nato|ukraine|russ|israel|gaza|usa|china)/.test(titles)) {
    eggs.push("a small globe with a few tiny glowing pins (no labels)" );
  }

  eggs.push("a coffee mug with a simple zebra-like pattern (no letters)" );

  return eggs.slice(0, 4);
}

function headlineSnippet(rawTitle) {
  return String(rawTitle || "")
    .replace(/\s+/g, " ")
    .trim()
    .replace(/[\u201c\u201d\u201e\u201f]/g, '"');
}

function splitTitle(rawTitle) {
  const title = headlineSnippet(rawTitle);
  const parts = title.split(":");
  if (parts.length < 2) return { lead: title, main: title };
  const lead = parts[0].trim();
  const main = parts.slice(1).join(":").trim();
  return { lead, main: main || lead };
}

function headlineFragment(rawTitle) {
  const { lead, main } = splitTitle(rawTitle);
  const full = `${lead} ${main}`.toLowerCase();
  const t = main.toLowerCase();

  const pick = (frag) => frag.toUpperCase();

  if (/(grönland|groenland|nuuk|kopenhagen)/.test(full)) return pick("GRÖNLAND");
  if (/(zoll|zölle|tarif)/.test(full)) return pick("ZÖLLE");
  if (/(nato)/.test(full)) return pick("NATO");
  if (/(kabul|anschlag|attentat)/.test(full)) return pick("KABUL");
  if (/(ukraine|ukrain|selenskyj)/.test(full)) return pick("UKRAINE");
  if (/(mercosur|abkommen|deal|freihandel)/.test(full)) return pick("EU-DEAL");
  if (/(china)/.test(full)) return pick("CHINA");
  if (/(iran)/.test(full)) return pick("IRAN");
  if (/(gaza|israel)/.test(full)) return pick("GAZA");

  const stop = new Set([
    "zu",
    "und",
    "der",
    "die",
    "das",
    "den",
    "dem",
    "des",
    "ein",
    "eine",
    "einer",
    "einem",
    "eines",
    "im",
    "in",
    "am",
    "an",
    "auf",
    "bei",
    "nach",
    "von",
    "mit",
    "für",
    "über",
    "gegen",
  ]);

  // Fallback: pick a short, noun-ish topic token from the main clause.
  const tokens = main
    .replace(/[“”„‟]/g, "")
    .replace(/[()]/g, " ")
    .replace(/[^\p{L}\p{N}\s-]/gu, "")
    .trim()
    .split(/\s+/)
    .filter(Boolean)
    .filter((w) => !stop.has(w.toLowerCase()));

  let first = tokens[0] || "NEWS";

  // Collapse things like "G-7-Treffen" → "G-7".
  const gMatch = first.match(/^(G-?\d+)/i);
  if (gMatch) first = gMatch[1];

  // Keep very short labels (e.g. EU) + next token.
  if (/^(EU|UNO|G-?\d+)$/i.test(first) && tokens[1]) {
    first = `${first} ${tokens[1]}`;
  }

  return pick(first || "NEWS");
}

function subtitleSnippet(rawTitle) {
  // 3–6 word “news-style” mini headline in German.
  // Prefer the main clause after ":" to avoid "X sagt: sagt Y"-style duplication.
  const { main } = splitTitle(rawTitle);
  const title = headlineSnippet(main)
    .replace(/[–—]/g, " ")
    .replace(/\s+/g, " ")
    .trim();

  const topic = headlineFragment(rawTitle);

  const rawWords = title
    .replace(/[:–—-]/g, " ")
    .replace(/[^\p{L}\p{N}\s-]/gu, "")
    .split(/\s+/)
    .filter(Boolean);

  const stop = new Set([
    "zu",
    "und",
    "der",
    "die",
    "das",
    "den",
    "dem",
    "des",
    "ein",
    "eine",
    "einer",
    "einem",
    "eines",
    "im",
    "in",
    "am",
    "an",
    // keep "auf" / "bei" in subtitles (they often carry meaning)
    "nach",
    "von",
    "mit",
    "für",
    "über",
    "gegen",
    "sollen",
    "soll",
    "wird",
    "werden",
    "ist",
    "sind",
    "war",
    "waren",
  ]);

  // Remove topic words if they appear in the subtitle.
  const topicWords = topic
    .toLowerCase()
    .replace(/[^\p{L}\p{N}\s-]/gu, "")
    .split(/\s+/)
    .filter(Boolean);

  const words = rawWords
    .map((w) => w.trim())
    .filter(Boolean)
    .filter((w) => !stop.has(w.toLowerCase()))
    .filter((w) => !topicWords.includes(w.toLowerCase()))
    .slice(0, 6);

  // Ensure at least 3 words.
  const finalWords = (words.length >= 3 ? words : rawWords.slice(0, 6)).slice(0, 6);

  return finalWords.join(" ");
}

function storyPanel(item) {
  const title = String(item.title || "");
  const t = title.toLowerCase();
  const fragment = headlineFragment(title);
  const subtitle = subtitleSnippet(title);

  // The goal: each story gets a distinct panel (iconography + short readable headline fragment).
  // Avoid repeating generic world maps unless the story truly needs it.

  const layout = `layout within the panel: TOP: big bold all-caps topic label \"${fragment}\". MIDDLE: a smaller 3–6 word mini-headline \"${subtitle}\". BOTTOM: exactly 1–2 simple icons (flat, high-contrast), no extra symbols, no charts, no maps.`;

  if (/(mercosur|freihandel|deal|abkommen)/.test(t) && /(eu|brüssel)/.test(t)) {
    return `a dedicated panel (${layout}) with exactly two icons: handshake icon + stamped document icon`;
  }

  if (/(grönland|groenland|nuuk|kopenhagen)/.test(t)) {
    return `a dedicated panel (${layout}) with exactly two icons: iceberg icon + patrol ship icon`;
  }

  if (/(zoll|zölle|tarif|drohung|drohungen|handel|sanktion)/.test(t)) {
    return `a dedicated panel (${layout}) with exactly two icons: shipping container icon + coin stack icon`;
  }

  if (/(nato)/.test(t)) {
    return `a dedicated panel (${layout}) with exactly two icons: cracked shield icon + radar sweep icon`;
  }

  if (/(ukraine|ukrain|selenskyj|gefangene|gefangener|mörder|morde|mord)/.test(t)) {
    return `a dedicated panel (${layout}) with exactly two icons: handcuffs icon + justice scale icon`;
  }

  if (/(kabul|anschlag|attentat|explosion|restaurant)/.test(t)) {
    return `a dedicated panel (${layout}) with exactly two icons: warning triangle icon + restaurant plate icon`;
  }

  if (/(wahl|parlament|regierung|koalition|minister|budget)/.test(t)) {
    return `a dedicated panel (${layout}) with exactly two icons: ballot box icon + parliament building icon`;
  }

  // More distinct iconography for frequent international story types.
  if (/(huawei|zte|netz|netzen|5g|telekom|mobilfunk)/.test(t)) {
    return `a dedicated panel (${layout}) with exactly two icons: antenna tower icon + forbidden sign icon`;
  }

  if (/(atomkraft|atomkraftwerk|akws|nuklear|reaktor)/.test(t)) {
    return `a dedicated panel (${layout}) with exactly two icons: radiation symbol icon + crosshair target icon`;
  }

  if (/(mexiko|usa)/.test(t) && /(liefert|ausliefert|ausliefer)/.test(t)) {
    return `a dedicated panel (${layout}) with exactly two icons: handcuffs icon + airplane icon`;
  }

  if (/(trump)/.test(t) && /(tech|bros|silicon|milliard)/.test(t)) {
    return `a dedicated panel (${layout}) with exactly two icons: suit tie icon + circuit board icon`;
  }

  if (/(eu|brüssel|usa|china|iran|gaza|israel|unganda|russ)/.test(t)) {
    return `a dedicated panel (${layout}) with exactly two icons: globe icon + location pin icon`;
  }

  return `a dedicated panel (${layout}) with exactly one icon: abstract breaking-news spotlight icon`;
}

function storyProps(items) {
  return items.slice(0, 6).map(storyPanel);
}

function main() {
  readStdin()
    .then((raw) => {
      const parsed = JSON.parse(raw);
      const items = Array.isArray(parsed?.items) ? parsed.items : [];
      const eggs = pickEasterEggs(items);
      const props = storyProps(items);

      const prompt = [
        "Cartoony illustration that matches the very distinct ORF ZiB studio look (NOT a generic newsroom).",
        "Camera framing: wide studio shot, anchor centered behind the desk, desk fills the lower half of frame.",
        "Color palette: dominant deep navy/midnight blue and cool cyan/blue lighting, with small crisp red accents. High-tech, clean, minimal.",
        "Set design cues (no logos):",
        "- a large CURVED wraparound video wall backdrop",
        "- the video wall prominently shows a panoramic Earth-from-space horizon band (blue glow) behind the anchor",
        "- vertical LED light columns/panels segmenting the backdrop",
        "- dark glossy reflective floor/riser with subtle blue light strips",
        "Desk design cues:",
        "- large oval/curved anchor desk with a glossy dark (glass-like) top",
        "- white/light-gray geometric base (faceted), with blue underglow",
        "- a thin horizontal red accent line near the desk edge",
        "Lighting: cool studio key light + blue ambient + subtle red rim accents.",
        "Style: 2D cartoon, crisp linework, soft shading, high detail, friendly and delightful.",
        "No logos, no watermarks.",
        "The studio's wraparound video wall MUST clearly reflect the specific news you pulled.",
        "Show 4–6 distinct panels/cards across the wall (one per headline). Each panel must be clean and readable:",
        "- TOP: big bold all-caps topic label (2–3 words)",
        "- MIDDLE: smaller 3–6 word mini-headline (news-style)",
        "- BOTTOM: exactly 1–2 simple icons (no maps, no busy collages)",
        ...props.map((p) => `- ${p}`),
        "Add 3–4 subtle Easter eggs to reward close inspection (no logos):",
        ...eggs.map((e) => `- ${e}`),
        "Avoid sports imagery.",
      ].join("\n");

      process.stdout.write(prompt + "\n");
    })
    .catch((err) => {
      process.stderr.write(String(err?.stack ?? err));
      process.stderr.write("\n");
      process.exitCode = 1;
    });
}

main();
