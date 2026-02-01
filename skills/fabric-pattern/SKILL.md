## Description
Integration for the Fabric AI framework (https://github.com/danielmiessler/Fabric). This skill manages text processing by reading local pattern files directly, while utilizing the Fabric CLI for specific web, YouTube, and search retrieval tasks.

## Rules

### 1. Pattern Application (Text Processing)
**Constraint:** Do NOT use `fabric -p "pattern"` to process text.
Instead, you must manually apply the pattern using the following logic:
1.  **Identify Pattern:** Determine the correct pattern name. If unsure, read `~/.config/fabric/patterns/pattern_explanations.md` to find the best fit.
2.  **Read Instruction:** Read the content of the system prompt file located at:
    `~/.config/fabric/patterns/"pattern_name"/system.md`
3.  **Apply:** Use the content of that `system.md` file as your strict instruction/persona to process the user's text.

### 2. Fabric CLI Usage (Retrieval & Tools)
Only use the `fabric` command line tool for the following specific retrieval or maintenance tasks:

* **YouTube/Video:** Use `fabric -y "URL"`
    * *Default behavior:* Returns the transcript.
    * *Supported flags:*
        * `--playlist` (Prefer playlist over video)
        * `--transcript` (Default)
        * `--transcript-with-timestamps`
        * `--comments`
        * `--metadata`
        * `--yt-dlp-args="..."` (e.g., `--cookies-from-browser brave`)
        * `--spotify="..."` (For Spotify podcast/episode metadata)
* **Web Scraping:** Use `fabric -u "URL"` to fetch page contents as Markdown.
* **Context Search:** Use `fabric -q "question"` to search using Jina AI.
* **Updates:** Use `fabric -U` to update the local patterns folder.

### 3. Integrations
* **Obsidian:** If the user asks to save, read, or interact with their Obsidian vault in relation to Fabric content (e.g., "save this summary to my vault"), utilize the `obsidian-cli` skill.

## Examples

**User:** "Summarize this website using the extract_wisdom pattern: https://example.com"
**Action:**
1. Run `fabric -u "https://example.com"` to get the raw text.
2. Read `~/.config/fabric/patterns/extract_wisdom/system.md`.
3. Process the raw text using the instructions found in `system.md`.

**User:** "Use fabric to get the transcript with timestamps for this video."
**Action:**
Run `fabric -y "VIDEO_URL" --transcript-with-timestamps`

**User:** "I need to use fabric to analyze this text but I don't know which pattern to use."
**Action:**
1. Read `~/.config/fabric/patterns/pattern_explanations.md`.
2. Select the most relevant pattern.
3. Read that pattern's `system.md` and apply it to the text.
