# QVeris Skill for Claude Code

中文文档 | [English](README.md)

这是一个让 Claude Code 能够通过 QVeris API 动态搜索和执行工具的技能。

## 功能特性

- **工具发现**：通过描述您的需求来搜索 API
- **工具执行**：使用参数执行任何已发现的工具
- **广泛覆盖**：访问天气、股票、搜索、货币以及数千种其他 API

## 安装

### 前置要求

此技能需要 `uv`，一个快速的 Python 包管理工具。请先安装它：

**macOS 和 Linux:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows:**
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

更多安装方式，请查看 [uv 官方安装指南](https://docs.astral.sh/uv/getting-started/installation/)。

### 安装技能

1. 将此文件夹复制到您的 Claude Code 技能目录：
   ```bash
   cp -r qveris ~/.claude/skills/
   ```

2. 设置您的 API 密钥：
   ```bash
   export QVERIS_API_KEY="your-api-key-here"
   ```

   在 https://qveris.ai 获取您的 API 密钥

## 使用方法

安装完成后，当您询问以下问题时，Claude Code 将自动使用此技能：
- 天气数据
- 股票价格和市场分析
- 网络搜索
- 货币汇率
- 更多...

### 手动命令

```bash
# 搜索工具
uv run scripts/qveris_tool.py search "stock price data"

# 执行工具
uv run scripts/qveris_tool.py execute <tool_id> --search-id <id> --params '{"symbol": "AAPL"}'
```

## 作者

[@hqmank](https://x.com/hqmank)

## 许可证

MIT
