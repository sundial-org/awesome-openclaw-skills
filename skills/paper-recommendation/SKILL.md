# Paper Recommendation Skill

> 自动发现、深度阅读、生成简报 - 你的AI论文研究助手

A Clawdbot skill for AI research paper discovery, review, and recommendation.

## Overview

This skill provides automated paper fetching, sub-agent review, and recommendation generation for AI research papers. It follows a complete workflow from arXiv paper discovery to detailed briefing generation.

## Features

- **Automatic Paper Discovery**: Fetch latest papers from arXiv by category and keywords
- **Parallel Review**: Use sub-agents to read and review multiple papers simultaneously
- **Structured Output**: Generate detailed briefings with consistent format
- **Daily Automation**: Cron job support for daily paper research

## Scripts

### 1. fetch_papers.py

Fetches latest papers from arXiv and optionally downloads PDFs.

**Usage:**
```bash
# Fetch papers only
python3 scripts/fetch_papers.py --json

# Fetch and download PDFs
python3 scripts/fetch_papers.py --download --json
```

**Output:**
```json
{
  "papers": [...],
  "total": 15,
  "fetched_at": "2026-01-29T17:00:00Z",
  "papers_dir": "/home/ubuntu/jarvis-research/papers",
  "pdfs_downloaded": ["/path/to/paper.pdf"]
}
```

### 2. review_papers.py

Generates sub-agent tasks for parallel paper review.

**Usage:**
```bash
# With papers from fetch_papers.py
python3 scripts/fetch_papers.py --json | python3 scripts/review_papers.py --json

# Or directly
python3 scripts/review_papers.py --papers '<json-string>' --json
```

**Output:**
```json
{
  "papers": [...],
  "subagent_tasks": [
    {
      "paper_id": "2601.19082",
      "task": "请完整阅读这篇论文并给出评分...",
      "label": "review-2601.19082"
    },
    ...
  ],
  "count": 5,
  "instructions": "使用 sessions_spawn 开子代理..."
}
```

### 3. read_pdf.py

Reads PDF files and extracts text for analysis.

**Usage:**
```bash
# Extract text from PDF
python3 scripts/read_pdf.py ~/jarvis-research/papers/2601.19082.pdf

# Extract and output JSON
python3 scripts/read_pdf.py ~/jarvis-research/papers/2601.19082.pdf --json

# Extract specific sections (abstract, experiments, etc.)
python3 scripts/read_pdf.py ~/jarvis-research/papers/2601.19082.pdf --sections --json
```

**Output:**
```json
{
  "success": true,
  "pdf_path": "/home/ubuntu/jarvis-research/papers/2601.19082.pdf",
  "text_length": 15000,
  "text": "Full PDF text...",
  "sections": {
    "abstract": "Abstract text...",
    "methodology": "Methodology text...",
    "experiments": "Experiments text...",
    "results": "Results text...",
    "conclusion": "Conclusion text..."
  },
  "extracted_at": "2026-01-29T17:00:00Z"
}
```

**Note:** Uses `pdftotext` (Poppler) for PDF text extraction.

---

## Jarvis's Workflow (Agent Actions)

When you ask Jarvis to research papers, Jarvis should:

### Step 1: Call fetch_papers.py
```bash
python3 scripts/fetch_papers.py --download --json
```

### Step 2: Review the papers
Examine the paper list and decide which to review.

### Step 3: Generate sub-agent tasks
```bash
python3 scripts/review_papers.py --papers '<papers-json>' --json
```

### Step 4: Spawn sub-agents for paper review
For each paper, spawn a sub-agent to read and review:

```bash
# Example: Spawn one sub-agent per paper
clawdbot sessions spawn \
  --task "请完整阅读这篇论文并给出评分：..." \
  --label "review-2601.19082"
```

**Sub-agent task requirements:**
- Read the full paper via arXiv HTML page
- Extract: institutions, full abstract, contributions, conclusions, experiments
- Score: 1-5
- Recommend: yes/no
- Reply with JSON format

### Step 5: Collect reviews and decide
- Collect all sub-agent results
- Analyze scores and recommendations
- Jarvis makes final decision (score >= 4 && recommended == yes)

### Step 6: Generate detailed briefing
Create a comprehensive briefing following the **Standard Briefing Format** (see below).

### Step 7: Deliver
Send the briefing via Telegram or other channels.

---

## 📋 Standard Briefing Format (Required)

All briefings MUST follow this exact format. **No exceptions.**

### Mandatory Structure

```markdown
# 📚 论文简报 - TOPIC | YYYY年MM月DD日

---

## 📄 PAPER_TITLE

**标题:** Full paper title (英文原标题)  
**作者:** Author1, Author2, Author3... (所有作者，用逗号分隔)  
**机构:** Institution1; Institution2; Institution3... (真实机构名，不是作者名)  
**arXiv:** https://arxiv.org/abs/xxxx.xxxxx  
**PDF:** https://arxiv.org/pdf/xxxx.xxxxx.pdf  
**发布日期:** YYYY-MM-DD | **分类:** cs.XX (arXiv 分类)

### 摘要
Chinese translation of the abstract (full paragraph, ~200-400 characters). 必须是完整的中文翻译，不能是摘要片段。

### 核心贡献
1. Contribution 1 (一句话概括核心贡献)
2. Contribution 2
3. Contribution 3 (2-4个贡献点)

### 主要结论
1. Conclusion 1 (一句话概括主要结论)
2. Conclusion 2 (2-4个结论点)

### 实验结果
• Experiment setup 1 (实验设置)
• Experiment setup 2
• Key finding 1 (关键发现)
• Key finding 2 (3-5个要点)

### Jarvis 笔记
- **评分:** ⭐⭐⭐⭐ (X/5)
- **推荐度:** ⭐⭐⭐⭐⭐
- **适合研究方向:** Field1, Field2 (1-2个研究方向)
- **重要性:** One sentence summary (一句话说明为什么重要)

---

## 📊 统计
- 论文总数: N
- 平均评分: ⭐⭐⭐⭐ (X/5)
- 推荐指数: ⭐⭐⭐⭐⭐

---
*Generated by Jarvis | YYYY-MM-DD HH:MM | TOPIC*
```

---

## ⏰ Daily Workflow (Cron Job)

自动执行时间: **每天 10:00 AM**

### Add Cron Job (Clawdbot)

```bash
# 添加每日完整论文调研任务
clawdbot cron add \
  --name "daily-paper-research" \
  --description "每日完整论文调研：获取→阅读→简报→发送" \
  --cron "0 10 * * *" \
  --system-event "请执行完整论文调研工作流：运行 python3 /home/ubuntu/skills/jarvis-research/scripts/daily_workflow.py。这会获取具身智能论文、下载 PDF、生成简报并发送到我的 Telegram。完成后告诉我结果。" \
  --deliver \
  --channel telegram \
  --to 8077045709
```

### Check Status

```bash
# 列出所有 cron 任务
clawdbot cron list

# 查看任务详情
clawdbot cron status
```

### What It Does

**每天 10:00 AM 自动执行完整工作流：**

1. **获取论文** - 从 arXiv 获取具身智能相关论文（前 6 篇）
2. **下载 PDF** - 下载所有论文的 PDF 文件
3. **生成简报** - 按标准格式生成论文简报
4. **发送 Telegram** - 发送摘要到用户 Telegram

### Workflow Script

```bash
# 手动执行完整工作流
python3 /home/ubuntu/skills/jarvis-research/scripts/daily_workflow.py
```

### Output Files

- **简报:** `~/jarvis-research/papers/briefing-embodied-{YYYY-MM-DD}.md`
- **PDF 文件:** `~/jarvis-research/papers/{paper-id}.pdf`
- **Telegram:** 摘要自动发送到用户

### Notes

- Cron 触发 Agent 执行 `daily_workflow.py`
- 脚本自动完成：获取 → 下载 → 生成 → 发送
- Agent 收到结果后可以继续深入分析（可选）

### Topics

默认主题: **具身智能 (Embodied Intelligence)**

关键词配置在 `scripts/fetch_papers.py`:
```python
KEYWORDS = [
    'embodied', 'embodiment', 'embodied intelligence', 'embodied AI',
    'robotics', 'robot', 'manipulation', 'grasping',
    'vision-language-action', 'VLA', 'VLN',
    'reinforcement learning', 'sim2real', 'domain randomization',
    'sensorimotor', 'perception', 'motor control', 'action',
    'physical intelligence', 'embodied navigation'
]
```

### Field Definitions & Rules

| Field | Description | Required | Rules |
|-------|-------------|----------|-------|
| `标题` | Full paper title | ✅ | 英文原标题，不要翻译 |
| `作者` | All authors | ✅ | 用逗号分隔，所有作者 |
| `机构` | Real institutions | ✅ | **必须是真正的机构名**，从 arXiv HTML 页面提取，**绝对不能是作者名** |
| `arXiv` | arXiv abstract URL | ✅ | `https://arxiv.org/abs/<id>` |
| `PDF` | Direct PDF URL | ✅ | `https://arxiv.org/pdf/<id>.pdf` |
| `发布日期` | Publication date | ✅ | `YYYY-MM-DD` 格式 |
| `分类` | arXiv category | ✅ | e.g., `cs.RO`, `cs.AI` |
| `摘要` | Chinese translation | ✅ | **完整翻译**，不是片段，~200-400字符 |
| `核心贡献` | Core contributions | ✅ | 2-4 个 bullet points，一句话 each |
| `主要结论` | Main conclusions | ✅ | 2-4 个 bullet points，一句话 each |
| `实验结果` | Experimental results | ✅ | **必须有**，3-5 个要点，包含设置和关键发现 |
| `Jarvis 笔记` | Jarvis assessment | ✅ | 评分、推荐度、研究方向、重要性 |

### Critical Rules ⚠️

1. **机构 must be real institutions** - Fetch from arXiv HTML page (`/abs/<id>`), NOT author names
2. **摘要 must be Chinese** - Full translation from English abstract, not fragments
3. **实验结果 required** - Must include experimental setup AND key findings
4. **One paper per section** - Each paper gets its own `## 📄` section
5. **All fields required** - Never skip any field
6. **No placeholders** - Replace all example text with actual content

### How to Get Information

**For institutions and authors:**
```bash
# Fetch arXiv HTML page (recommended)
curl https://arxiv.org/abs/<paper-id>

# Or use web_fetch tool
web_fetch --url https://arxiv.org/abs/<paper-id> --extractMode text
```

**For full abstract and content:**
```bash
# Fetch HTML full text
curl https://arxiv.org/html/<paper-id>
```

**For PDF (if available):**
```bash
# Download and extract text
pdftotext <paper-id>.pdf -
```

---

## Example Agent Prompt

When you want Jarvis to research papers:

```
请执行论文调研任务：
1. 调用 fetch_papers.py 获取今天的多智能体相关论文（带 PDF 下载）
2. 查看论文列表，决定哪些值得深入阅读
3. 调用 review_papers.py 生成子代理任务
4. 使用 sessions_spawn 为每篇论文开一个子代理，要求：
   - 完整阅读论文（arXiv HTML 页面）
   - 提取机构、中文摘要、核心贡献、主要结论、实验结果
   - 给出 1-5 评分和推荐
   - 回复 JSON 格式
5. 收集所有子代理结果，分析评分，选出 3-5 篇推荐论文
6. 为每篇生成详细简报（必须包含：标题、作者、机构、中文摘要、核心贡献、主要结论、实验结果、Jarvis笔记）
7. 发送到我的 Telegram
```

## Configuration

**Papers Directory:** `~/jarvis-research/papers/`

**Categories Monitored:**
- cs.AI (Artificial Intelligence)
- cs.LG (Machine Learning)
- cs.MA (Multi-Agent Systems)

**Keywords:**
multi-agent, agent, collaboration, coordination, task planning, llm, reasoning, autonomous, swarm, collective, reinforcement, hierarchical, distributed, emergent

**Sub-agent Model:**
- Default: inherits from main agent
- Can override via `agents.defaults.subagents.model` or `sessions_spawn.model`

## Notes

- Skills are **tools** - Jarvis uses them as needed
- Jarvis makes all **decisions** (which papers to review, which to recommend)
- Sub-agents do **parallel** paper reading (faster than sequential)
- Skills output **structured data** - Jarvis interprets and acts on it
- The briefing is Jarvis's **creative work** - not automated
- **Always follow the Standard Briefing Format** - Never deviate

## Files

```
~/skills/paper-recommendation/
├── SKILL.md              # This file (FULL DOCUMENTATION)
└── scripts/
    ├── fetch_papers.py   # Paper fetching + PDF download
    ├── review_papers.py  # Sub-agent task generation
    └── read_pdf.py       # PDF text extraction
```

**PDF Reading:**
- Uses `pdftotext` (Poppler) for text extraction
- Can extract full text or specific sections (abstract, experiments, etc.)
- Useful for sub-agents to read downloaded PDFs

---

*Paper Recommendation Skill - AI Research Assistant*
