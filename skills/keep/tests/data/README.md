# Test Data

This directory contains public domain texts for testing keep functionality.

---

## Files

### ancrenewisse.pdf
- **Title:** Ancrene Wisse (Ancrene Riwle)
- **Date:** c. 1200s (13th century)
- **Language:** Middle English
- **Status:** Public domain
- **Description:** A monastic guide for anchoresses, one of the earliest works in English prose

---

### impermanence_verse.txt
- **Title:** 無常偈 (Impermanence Verse / Closing Verse)
- **Date:** Traditional Zen liturgy (exact origin uncertain)
- **Language:** Japanese (Kanji/Kana), with romanization and multiple English translations
- **Source:** Soto Zen liturgy
- **Status:** Traditional teaching, freely shared
- **Description:** Four-line verse chanted at the end of Zen practice sessions. "Great is the matter of birth and death / Life slips quickly by / Time waits for no one / Wake up! Wake up!" Includes character-by-character breakdown, cultural context, and linguistic notes.

---

### mn61.html
- **Title:** Ambalaṭṭhikārāhulovāda Sutta (MN 61) - The Exhortation to Rāhula at Mango Stone
- **Date:** Original: ~5th century BCE; Translation: contemporary
- **Language:** English translation from Pali
- **Translator:** Thanissaro Bhikkhu
- **Source:** https://www.dhammatalks.org/suttas/MN/MN61.html
- **Format:** Raw HTML (complete with markup, navigation, footnotes)
- **License:** Freely distributed for educational use
- **Description:** Buddha's teaching to his son Rāhula on reflection before, during, and after bodily, verbal, and mental actions. The triple-check pattern: reflect before acting/speaking, check while doing, review after. Mirror metaphor for self-reflection. Includes water dipper teaching on truthfulness and notes on contemplative practice. **Format note:** Kept as raw HTML to test document processing and summarization on markup-heavy content.

---

### mn62_translation-en-sujato.json
- **Title:** Mahārāhulovāda Sutta (MN 62) - The Longer Advice to Rāhula
- **Date:** Original: ~5th century BCE; Translation: modern
- **Language:** English translation from Pali
- **Translator:** Bhikkhu Sujato
- **Source:** SuttaCentral
- **License:** Creative Commons CC0 1.0 Universal (SuttaCentral translations)
- **Description:** Buddha's teaching to his son Rāhula on the five aggregates and mindfulness of breathing

---

### fortytwo_chapters.txt
- **Title:** 佛說四十二章經 (Sutra of Forty-Two Chapters)
- **Date:** Eastern Han Dynasty (25-220 CE)
- **Language:** Classical Chinese
- **Source:** Project Gutenberg (#23585)
- **Status:** Public domain
- **Description:** One of the earliest Buddhist texts to reach China, traditionally attributed to translation by Kāśyapa Mātaṅga and Dharmarakṣa

---

### mn62_translation-en-sujato.json
- **Title:** Mahārāhulovāda Sutta (MN 62) - The Longer Advice to Rāhula
- **Date:** Original: ~5th century BCE; Translation: modern
- **Language:** English translation from Pali
- **Translator:** Bhikkhu Sujato
- **Source:** SuttaCentral
- **License:** Creative Commons CC0 1.0 Universal (SuttaCentral translations)
- **Description:** Buddha's teaching to his son Rāhula on the five aggregates and mindfulness of breathing

---

### mumford_sticks_and_stones.txt
- **Title:** Sticks and Stones: A Study of American Architecture and Civilization
- **Author:** Lewis Mumford (1895-1990)
- **Date:** 1924
- **Language:** English
- **Source:** Internet Archive (sticksstones0000lewi)
- **Status:** Public domain (published before 1929)
- **Description:** Mumford's first major work on architecture, examining American building traditions from medieval influences through industrialization. Includes chapters on "The Medieval Tradition," "The Renaissance in New England," "The Age of Rationalism," and more.

**Note:** This is OCR text from archive.org. Quality is good but may contain occasional scanning artifacts.

**Content overview:**
- Chapter 1: The Medieval Tradition (New England villages, common lands, meeting-house architecture)
- Chapter 2: [continues through 8 chapters on American architectural history]
- Explores relationship between architecture and social/cultural development
- Foundational text in American architectural criticism

---

### true_person_no_rank.md
- **Title:** 無位真人 (The True Person of No Rank)
- **Date:** Original: 9th century CE; Commentary layers: 9th-20th centuries
- **Language:** Chinese (verified original text) with English translation and commentary
- **Source:** Record of Linji (臨濟錄, Línjì Lù); Book of Serenity (從容錄) Case 38
- **Primary sources:** DILA Buddhist Dictionary, multiple scholarly translations
- **Status:** Core teaching in public domain; compiled with verification notes
- **Description:** Linji Yixuan's famous teaching: "Within this mass of red flesh, there is a true person of no rank, constantly coming and going through the gates of your face." Multi-layered document exploring the original teaching, koan tradition, Dōgen's commentary, modern interpretations, and linguistic analysis. Includes Chinese text (verified), translations, and commentary relationships. Intentionally leaves some questions open for investigation.

**Verification status:** Chinese text and basic structure verified (2026-01-31). Modern teacher quotes compiled from teaching notes and may be paraphrased. See document header for details.

---

## Usage for Testing

These texts provide diverse test cases for keep:

1. **Different languages:** English, Chinese (Classical and modern romanization), Japanese, Middle English, Pali (via translation)
2. **Different formats:** PDF, plain text, JSON, Markdown, HTML (with markup)
3. **Different domains:** Buddhist teachings, Zen liturgy, architectural criticism, medieval devotional prose
4. **Different writing styles:** Ancient scripture, koan commentary, scholarly analysis, liturgical verse, teaching notes
5. **Different lengths:** Four-line verses to full books
6. **Different structures:** Linear narratives, multi-layered commentaries, character-by-character analysis, mirror patterns, web documents with navigation
7. **Multilingual content:** Japanese-English parallel texts, Chinese with romanization, cross-linguistic terminology
8. **Processing challenges:** OCR artifacts (Mumford), HTML markup (MN 61), PDF extraction (Ancrene Wisse), structured data (JSON)

---

## Adding More Test Data

When adding public domain texts:

1. Verify public domain status (pre-1929 for US, or explicit license)
2. Include source URL (Project Gutenberg, archive.org, etc.)
3. Add metadata to this README
4. Prefer clean text formats (txt, json) over scanned PDFs when available

---

## Lewis Mumford Works

**In Public Domain (pre-1929):**
- "The Story of Utopias" (1922) — ✅ Available on archive.org
- "Sticks and Stones" (1924) — ✅ Included in this dataset
- "The Golden Day" (1926) — ✅ Available on archive.org

**Still Under Copyright:**
- "Technics and Civilization" (1934)
- "The Culture of Cities" (1938)
- "The City in History" (1961) ⚠️ Not freely licensed

Other early Mumford works can be found at:
- https://archive.org (search: creator:"Lewis Mumford" AND date:[1900 TO 1928])
- Project Gutenberg (limited selection)

---

## License

Each text retains its original license status (public domain or Creative Commons as noted above). This README and dataset organization is released under CC0 1.0.
