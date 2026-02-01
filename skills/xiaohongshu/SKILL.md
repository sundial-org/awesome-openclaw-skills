# 小红书技能 (Xiaohongshu Skill)

小红书内容创作、发布与运营一体化技能。

## 环境

- Python venv: `/root/clawd/skills/xiaohongshu/venv`
- 激活: `source /root/clawd/skills/xiaohongshu/venv/bin/activate`
- social-auto-upload: `/root/clawd/skills/xiaohongshu/social-auto-upload`

## 功能模块

### 1. 内容创作 ✅
AI 根据主题撰写小红书风格内容。

### 2. 渲染卡片 ✅
将 Markdown 内容渲染成小红书风格的图片卡片（1080×1440px）。

```bash
cd /root/clawd/skills/xiaohongshu
./render <markdown文件> --style <样式> -o output/
```

可用样式: `purple`(默认), `xiaohongshu`, `mint`, `sunset`, `ocean`, `elegant`, `dark`

### 3. 发布笔记 ✅ (RPA方式)
使用 Playwright 自动化发布，模拟真实用户操作。

**首次使用需要登录获取 Cookie：**
```bash
cd /root/clawd/skills/xiaohongshu/social-auto-upload
../venv/bin/python -c "
import asyncio
from uploader.xiaohongshu_uploader.main import xiaohongshu_cookie_gen
asyncio.run(xiaohongshu_cookie_gen('cookies/xhs_account.json'))
"
```
会打开浏览器，扫码登录后 Cookie 自动保存。

**发布图文笔记：**
```python
from uploader.xiaohongshu_uploader.main import XiaoHongShuVideo
# 详见 examples/upload_video_to_xiaohongshu.py
```

### 4. 查看数据（开发中）
通过 RPA 方式获取笔记数据。

### 5. 学习他人笔记（开发中）
通过 RPA 方式浏览和分析热门笔记。

## 完整工作流

```
1. 主题构思 → 告诉我你想写什么
2. AI 撰写 → 生成小红书风格文案
3. 保存内容 → output/note.md
4. 渲染卡片 → 生成封面 + 内容图片
5. RPA 发布 → 自动上传到小红书
6. 数据跟踪 → 查看互动数据
7. 优化迭代 → 根据数据调整内容
```

## 目录结构

```
xiaohongshu/
├── SKILL.md           # 本文档
├── .env               # Cookie 配置（API方式，备用）
├── venv/              # Python 虚拟环境
├── assets/            # HTML 模板
├── scripts/           # 工具脚本
│   ├── render_xhs_v2.py  # 渲染脚本
│   └── xhs_tool.py       # API 工具（备用）
├── output/            # 输出目录
└── social-auto-upload/  # RPA 发布工具
    ├── cookies/       # 登录凭证
    ├── videos/        # 待发布内容
    └── uploader/      # 各平台上传模块
```

## 注意事项

- RPA 方式需要首次扫码登录
- 发布间隔建议 > 30 秒，避免风控
- 图片尺寸 1080×1440px（小红书推荐比例）
- 支持定时发布
