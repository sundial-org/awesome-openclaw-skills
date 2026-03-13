# Web Search Pro

> Agent-first web search and retrieval stack with a no-key baseline, explainable routing, visible federated-search gains, and built-in `extract`, `crawl`, `map`, and `research` flows.

[![ClawHub](https://img.shields.io/badge/ClawHub-web--search--pro-blue)](https://www.clawhub.com/Zjianru/web-search-pro)
[![GitHub](https://img.shields.io/badge/GitHub-web--search--pro-black)](https://github.com/Zjianru/web-search-pro)
[![License](https://img.shields.io/badge/license-MIT--0-green)](https://github.com/Zjianru/web-search-pro/blob/main/LICENSE)

## Why it stands out

- Real `no-key` baseline for live web search and safe fetch
- Explainable routing with `confidence`, `topSignals`, and visible `routingSummary`
- Federated search reports concrete value such as recovered results and corroborated results
- Search can grow into `extract`, `crawl`, `map`, and `research` without switching skills

## Good fits

- Current web search and news search
- Docs lookup and code lookup
- Company research and competitor discovery
- Multi-step agent workflows that need both search and evidence collection

## Quick start

```bash
git clone https://github.com/Zjianru/web-search-pro.git
cd web-search-pro
node scripts/search.mjs --query "latest OpenAI Responses API docs"
node scripts/search.mjs --query "OpenAI pricing news" --type news
```

Then try:

```bash
node scripts/extract.mjs --url https://platform.openai.com/docs
node scripts/research.mjs --query "Compare web-search-pro vs web-search-plus"
```

## Links

- ClawHub: <https://www.clawhub.com/Zjianru/web-search-pro>
- GitHub: <https://github.com/Zjianru/web-search-pro>
