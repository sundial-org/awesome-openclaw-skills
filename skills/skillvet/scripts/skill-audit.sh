#!/usr/bin/env bash
# skill-audit.sh — Security scanner for ClawdHub skills
# Usage: skill-audit.sh <skill-directory>
# Returns: 0 = clean, 1 = warnings only, 2 = critical findings

set -uo pipefail

SKILL_DIR="${1:?Usage: skill-audit.sh <skill-directory>}"
SKILL_NAME="$(basename "$SKILL_DIR")"

if [ ! -d "$SKILL_DIR" ]; then
  echo "❌ Directory not found: $SKILL_DIR"
  exit 2
fi

RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
NC='\033[0m'

CRITICAL=0
WARNINGS=0
FINDINGS=""

add_finding() {
  local severity="$1" file="$2" line="$3" desc="$4"
  if [ "$severity" = "CRITICAL" ]; then
    FINDINGS+="${RED}🔴 CRITICAL${NC} [$file:$line] $desc\n"
    CRITICAL=$((CRITICAL + 1))
  else
    FINDINGS+="${YELLOW}🟡 WARNING${NC}  [$file:$line] $desc\n"
    WARNINGS=$((WARNINGS + 1))
  fi
}

echo "🔍 Auditing skill: $SKILL_NAME"
echo "   Path: $SKILL_DIR"
echo "---"

# Collect all text files (skip binaries, images, etc.)
FILES=$(find "$SKILL_DIR" -type f \( -name "*.md" -o -name "*.js" -o -name "*.ts" -o -name "*.py" -o -name "*.sh" -o -name "*.bash" -o -name "*.json" -o -name "*.yaml" -o -name "*.yml" -o -name "*.toml" -o -name "*.txt" -o -name "*.env*" -o -name "Dockerfile*" -o -name "Makefile" \) 2>/dev/null || true)

if [ -z "$FILES" ]; then
  echo "⚠️  No scannable files found"
  exit 0
fi

FILE_COUNT=$(echo "$FILES" | wc -l)
echo "   Scanning $FILE_COUNT files..."
echo ""

# --- CRITICAL CHECKS ---

# 1. Known exfiltration endpoints
while IFS=: read -r file line content; do
  rel_file="${file#$SKILL_DIR/}"
  if echo "$content" | grep -qiE '(webhook\.site|ngrok\.io|pipedream|requestbin|burpcollaborator|interact\.sh|oastify)'; then
    add_finding "CRITICAL" "$rel_file" "$line" "Known exfiltration endpoint: $(echo "$content" | grep -oiE '(webhook\.site|ngrok\.io|pipedream|requestbin|burpcollaborator|interact\.sh|oastify)[^ "]*')"
  fi
done < <(grep -rnE 'https?://' "$SKILL_DIR" --include='*.js' --include='*.ts' --include='*.py' --include='*.sh' 2>/dev/null || true)

# 2. Environment variable harvesting
while IFS=: read -r file line content; do
  rel_file="${file#$SKILL_DIR/}"
  add_finding "CRITICAL" "$rel_file" "$line" "Bulk env harvesting: ${content:0:120}"
done < <(grep -rnE '(\$\{!.*@\}|printenv\s*$|printenv\s*\||env\s*\|)' "$SKILL_DIR" --include='*.js' --include='*.ts' --include='*.py' --include='*.sh' 2>/dev/null || true)

# 3. Foreign credential access
OWN_KEYS=""
if [ -f "$SKILL_DIR/SKILL.md" ]; then
  OWN_KEYS=$(grep -oE '[A-Z][A-Z_]*_API_KEY|[A-Z][A-Z_]*_TOKEN|[A-Z][A-Z_]*_SECRET|[A-Z][A-Z_]*_KEY' "$SKILL_DIR/SKILL.md" 2>/dev/null | sort -u | tr '\n' '|' | sed 's/|$//')
fi
if [ -z "$OWN_KEYS" ]; then
  OWN_KEYS=$(grep -roE '[A-Z][A-Z_]*_KEY' "$SKILL_DIR"/*.md 2>/dev/null | grep -oE '[A-Z][A-Z_]*_KEY' | sort -u | tr '\n' '|' | sed 's/|$//')
fi

FOREIGN_KEYS="ANTHROPIC_API_KEY|OPENAI_API_KEY|OPENROUTER_API_KEY|TELEGRAM.*BOT_TOKEN|CLAUDE.*TOKEN|ELEVENLABS.*KEY|AGENTMAIL_API_KEY|FIRECRAWL_API_KEY|BROWSER_USE_API_KEY|MEM0_API_KEY|SERPAPI_KEY|GOOGLE_API_KEY"
while IFS=: read -r file line content; do
  rel_file="${file#$SKILL_DIR/}"
  [[ "$rel_file" == *.md ]] && continue
  matched_key=$(echo "$content" | grep -oE '[A-Z][A-Z_]*_API_KEY|[A-Z][A-Z_]*_KEY|[A-Z][A-Z_]*_TOKEN|[A-Z][A-Z_]*_SECRET' | head -1)
  if [ -n "$OWN_KEYS" ] && [ -n "$matched_key" ] && echo "$matched_key" | grep -qE "^($OWN_KEYS)$"; then
    continue
  fi
  add_finding "CRITICAL" "$rel_file" "$line" "Accesses foreign credentials: ${content:0:120}"
done < <(grep -rnE "($FOREIGN_KEYS)" "$SKILL_DIR" --include='*.js' --include='*.ts' --include='*.py' --include='*.sh' 2>/dev/null || true)

# 4. Obfuscation patterns
while IFS=: read -r file line content; do
  rel_file="${file#$SKILL_DIR/}"
  add_finding "CRITICAL" "$rel_file" "$line" "Code obfuscation detected: ${content:0:120}"
done < <(grep -rnE '(eval\s*\(|new\s+Function\s*\(|atob\s*\(|btoa\s*\(|Buffer\.from\s*\(.*(base64|hex)|exec\s*\(.*base64|\\x[0-9a-f]{2}\\x[0-9a-f]{2}\\x)' "$SKILL_DIR" --include='*.js' --include='*.ts' --include='*.py' --include='*.sh' 2>/dev/null || true)

# 5. Path traversal / sensitive file access
while IFS=: read -r file line content; do
  rel_file="${file#$SKILL_DIR/}"
  add_finding "CRITICAL" "$rel_file" "$line" "Path traversal / sensitive file access: ${content:0:120}"
done < <(grep -rnE '(\.\./\.\./|/etc/passwd|/etc/shadow|~\/\.bashrc|~\/\.ssh|~\/\.aws|~\/\.clawdbot|~\/\.config|\/home\/[a-z])' "$SKILL_DIR" --include='*.js' --include='*.ts' --include='*.py' --include='*.sh' 2>/dev/null || true)

# 6. Data exfiltration via curl/wget
while IFS=: read -r file line content; do
  rel_file="${file#$SKILL_DIR/}"
  add_finding "CRITICAL" "$rel_file" "$line" "Data exfiltration pattern: ${content:0:120}"
done < <(grep -rnE '(curl\s+.*(-d|--data|--data-raw)\s|wget\s+.*--post|curl\s+.*\$\(|curl.*\|\s*bash)' "$SKILL_DIR" --include='*.js' --include='*.ts' --include='*.py' --include='*.sh' 2>/dev/null || true)

# 7. Reverse/bind shells
while IFS=: read -r file line content; do
  rel_file="${file#$SKILL_DIR/}"
  add_finding "CRITICAL" "$rel_file" "$line" "Possible reverse/bind shell: ${content:0:120}"
done < <(grep -rnE '(\/dev\/tcp\/|mkfifo|nc\s+-[elp]|ncat\s|bash\s+-i|python.*socket.*connect|socat\s)' "$SKILL_DIR" --include='*.js' --include='*.ts' --include='*.py' --include='*.sh' 2>/dev/null || true)

# 8. .env file theft
while IFS=: read -r file line content; do
  rel_file="${file#$SKILL_DIR/}"
  [[ "$rel_file" == *.md ]] && continue
  add_finding "CRITICAL" "$rel_file" "$line" ".env file access: ${content:0:120}"
done < <(grep -rnE '(dotenv|load_dotenv|\.env\.local|open\(.*\.env|read.*\.env|config\s*\(\s*\))' "$SKILL_DIR" --include='*.js' --include='*.ts' --include='*.py' --include='*.sh' 2>/dev/null | grep -vE '(\.env\.example|\.env\.sample|#.*\.env)' || true)

# 9. Prompt injection in markdown
while IFS=: read -r file line content; do
  rel_file="${file#$SKILL_DIR/}"
  if echo "$content" | grep -qiE '(example|never|attack|malicious|don.t|warning|avoid|block|detect|prevent|security)'; then
    continue
  fi
  add_finding "CRITICAL" "$rel_file" "$line" "Prompt injection attempt: ${content:0:120}"
done < <(grep -rniE '(ignore (previous|prior|above|all) (instructions|rules|prompts)|disregard (your|all|previous)|forget (your|all|previous)|you are now|new persona|override (system|safety)|jailbreak|do not follow|pretend you|act as if you have no restrictions|reveal your (system|instructions|prompt))' "$SKILL_DIR" --include='*.md' --include='*.txt' --include='*.yaml' --include='*.yml' --include='*.json' 2>/dev/null || true)

# 10. LLM tool exploitation
while IFS=: read -r file line content; do
  rel_file="${file#$SKILL_DIR/}"
  add_finding "CRITICAL" "$rel_file" "$line" "LLM tool exploitation: ${content:0:120}"
done < <(grep -rniE '(send (this|the|all|my) (data|info|key|token|secret|config|env|password|credential)|exec.*curl.*api[_-]?key|write.*(api[_-]?key|token|secret|password).*to|post.*(credential|secret|token|key).*to|email.*(key|token|secret|credential)|forward.*(key|token|secret))' "$SKILL_DIR" --include='*.md' --include='*.txt' 2>/dev/null || true)

# 11. Agent config tampering
while IFS=: read -r file line content; do
  rel_file="${file#$SKILL_DIR/}"
  add_finding "CRITICAL" "$rel_file" "$line" "Agent config tampering: ${content:0:120}"
done < <(grep -rniE '(write|edit|modify|overwrite|replace|append).*(AGENTS\.md|SOUL\.md|IDENTITY\.md|USER\.md|HEARTBEAT\.md|MEMORY\.md|BOOTSTRAP\.md|clawdbot\.json|\.bashrc|\.profile)' "$SKILL_DIR" 2>/dev/null || true)

# 12. Unicode obfuscation
while IFS= read -r file; do
  rel_file="${file#$SKILL_DIR/}"
  if grep -Pq '[\x{200B}\x{200C}\x{200D}\x{200E}\x{200F}\x{202A}\x{202B}\x{202C}\x{202D}\x{202E}\x{2060}\x{FEFF}]' "$file" 2>/dev/null; then
    add_finding "CRITICAL" "$rel_file" "?" "Unicode obfuscation — hidden zero-width or directional chars detected"
  fi
done < <(find "$SKILL_DIR" -type f \( -name "*.md" -o -name "*.js" -o -name "*.ts" -o -name "*.py" -o -name "*.sh" \) 2>/dev/null || true)

# 13. Suspicious setup commands
if [ -f "$SKILL_DIR/SKILL.md" ]; then
  while IFS=: read -r file line content; do
    rel_file="${file#$SKILL_DIR/}"
    add_finding "CRITICAL" "$rel_file" "$line" "Suspicious setup command (exfil disguised as setup): ${content:0:120}"
  done < <(grep -nE '(curl|wget|nc |ncat)\s+.*(--data|--post|-d\s|>\s*/dev/tcp|\|.*bash)' "$SKILL_DIR/SKILL.md" 2>/dev/null || true)
fi

# 14. Social engineering
while IFS=: read -r file line content; do
  rel_file="${file#$SKILL_DIR/}"
  add_finding "CRITICAL" "$rel_file" "$line" "Social engineering — instructs user to download/run external binary: ${content:0:120}"
done < <(grep -rniE '(download.*\.(exe|zip|dmg|pkg|msi|deb|rpm|appimage|sh|bat|cmd|ps1)|extract.*passw|run.*executable|execute.*command.*terminal|install.*from.*(glot\.io|pastebin|hastebin|ghostbin|paste\.|privatebin|dpaste|controlc|rentry)|run.*(before|first).*using|\.zip.*password)' "$SKILL_DIR" --include='*.md' --include='*.txt' 2>/dev/null || true)

# 15. Shipped .env files
while IFS= read -r file; do
  rel_file="${file#$SKILL_DIR/}"
  if [[ "$rel_file" != *.example ]] && [[ "$rel_file" != *.sample ]]; then
    add_finding "CRITICAL" "$rel_file" "-" "Actual .env file shipped with skill — may contain or harvest credentials"
  fi
done < <(find "$SKILL_DIR" -name ".env" -o -name ".env.local" -o -name ".env.production" 2>/dev/null || true)

# --- WARNING CHECKS ---

# Subprocess execution
while IFS=: read -r file line content; do
  rel_file="${file#$SKILL_DIR/}"
  add_finding "WARNING" "$rel_file" "$line" "Subprocess execution: ${content:0:120}"
done < <(grep -rnE '(child_process|exec\(|execSync|spawn\(|subprocess\.|os\.system|os\.popen|Popen)' "$SKILL_DIR" --include='*.js' --include='*.ts' --include='*.py' 2>/dev/null || true)

# Network requests
while IFS=: read -r file line content; do
  rel_file="${file#$SKILL_DIR/}"
  add_finding "WARNING" "$rel_file" "$line" "Network request: ${content:0:120}"
done < <(grep -rnE '(require\(.*(axios|node-fetch|got|request)\)|import.*(axios|fetch|requests|httpx|urllib)|XMLHttpRequest|\.fetch\s*\()' "$SKILL_DIR" --include='*.js' --include='*.ts' --include='*.py' 2>/dev/null || true)

# Minified/bundled files
while IFS= read -r file; do
  rel_file="${file#$SKILL_DIR/}"
  line_len=$(head -1 "$file" 2>/dev/null | wc -c)
  if [ "$line_len" -gt 500 ]; then
    add_finding "WARNING" "$rel_file" "1" "Minified/bundled file (first line: ${line_len} chars) — cannot audit"
  fi
done < <(find "$SKILL_DIR" -name "*.js" -o -name "*.ts" 2>/dev/null || true)

# Filesystem write operations
while IFS=: read -r file line content; do
  rel_file="${file#$SKILL_DIR/}"
  add_finding "WARNING" "$rel_file" "$line" "File write operation: ${content:0:120}"
done < <(grep -rnE '(writeFileSync|writeFile\(|open\(.*[\"'"'"']w|\.write\(|fs\.append|>> )' "$SKILL_DIR" --include='*.js' --include='*.ts' --include='*.py' --include='*.sh' 2>/dev/null || true)

# Unknown external tool requirements
while IFS=: read -r file line content; do
  rel_file="${file#$SKILL_DIR/}"
  if echo "$content" | grep -qiE '(npm|pip|brew|apt|cargo|go install|gem install|docker|node|python|jq|curl|git|ffmpeg|ollama|playwright|gog|gemini)'; then
    continue
  fi
  add_finding "WARNING" "$rel_file" "$line" "Requires unknown external tool: ${content:0:120}"
done < <(grep -rniE '(requires?|must install|prerequisite|install.*first|download.*before).*\b[a-z][a-z0-9_-]+cli\b' "$SKILL_DIR" --include='*.md' 2>/dev/null || true)

# --- RESULTS ---
echo ""
if [ $CRITICAL -eq 0 ] && [ $WARNINGS -eq 0 ]; then
  printf "${GREEN}✅ CLEAN${NC} — No issues found in %s\n" "$SKILL_NAME"
  exit 0
fi

printf "%b" "$FINDINGS"
echo "---"
printf "Summary: ${RED}%d critical${NC}, ${YELLOW}%d warnings${NC}\n" "$CRITICAL" "$WARNINGS"

if [ $CRITICAL -gt 0 ]; then
  printf "\n${RED}⛔ BLOCKED — Critical issues found. Do NOT use this skill without manual review.${NC}\n"
  exit 2
else
  printf "\n${YELLOW}⚠️  CAUTION — Warnings found. Review before using.${NC}\n"
  exit 1
fi
