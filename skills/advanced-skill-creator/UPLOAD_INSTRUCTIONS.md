# Advanced Skill Creator - 上传说明

## 技能概述

这是一个高级技能创建器，能够执行官方的5步研究流程来创建符合OpenClaw标准的技能。该技能确保在用户请求创建或修改OpenClaw/Moltbot/ClawDBot技能时遵循正确的方法论和官方标准。

## 功能特性

1. **官方5步研究流程**：
   - 查阅官方最新文档
   - 查询ClawHub/ClawdHub上的相关公开技能
   - 搜索最新的实践与示例
   - 方案融合与对比
   - 按照规定结构输出

2. **全面的分析能力**：
   - 触发精度分析（误触发率）
   - 可维护性/可读性评估
   - 加载速度/内存影响分析
   - 兼容性检查
   - 安全与错误隔离
   - 升级友好度评估
   - 依赖管理复杂度分析

3. **标准化输出**：
   - 严格遵循官方SKILL.md格式
   - 包含完整的YAML frontmatter
   - 提供详细的使用说明
   - 包含适当的元数据定义

## 安装说明

1. 将整个 `advanced-skill-creator` 目录放置到您的技能目录中
2. 确保 Python 3.7+ 已安装
3. 确保 bash 环境可用

## 使用方法

### 基础功能
```bash
# 运行技能处理器
python3 scripts/advanced_skill_processor.py "Create a weather skill"

# 处理其他类型的技能请求
python3 scripts/advanced_skill_processor.py "Create a notification skill"
```

### 触发条件
该技能会在用户提及以下关键词时自动触发：
- "写一个触发"
- "写skill"
- "claw skill"
- "openclaw skill"
- "moltbot skill"
- "创建技能"
- "写一个让它..."

## 配置要求

- Python 3.7+
- bash 环境
- 访问官方文档的网络连接

## 兼容性

此技能遵循 OpenClaw 官方标准：
- 符合 AgentSkills 规范
- 支持 YAML frontmatter (name, description, when, examples, metadata.openclaw.*)
- 遵循官方推荐的触发机制
- 支持多种工具调用规范

## 文件结构

```
advanced-skill-creator/
├── SKILL.md                      # 技能描述文件
├── scripts/
│   └── advanced_skill_processor.py # 主要处理脚本
├── README.md                     # 使用说明
└── UPLOAD_INSTRUCTIONS.md        # 上传说明（当前文件）
```

## 注意事项

- 此技能需要网络访问以查询官方文档和ClawHub
- 某些高级功能可能需要额外的API凭据
- 确保Python环境满足依赖要求
- 建议定期更新以获取最新的官方标准