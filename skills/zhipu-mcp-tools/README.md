# zhipu-mcp-tools

使用智谱AI MCP服务器提供的多种AI能力，包括网页分析、视觉理解等功能。

## 概述

这个技能封装了智谱AI Comprehensive MCP服务器提供的多种AI功能，包括：

- 网页内容分析
- 图像视觉理解
- 联网搜索
- 代码仓库分析
- 文本生成

## 安装

1. 确保智谱AI MCP服务器正在运行（默认端口8000）
2. 配置好API密钥
3. 将此技能文件夹放置在Clawd的skills目录中
4. 运行 `npm install` 安装依赖

## 配置

确保智谱AI MCP服务器正在运行：

```bash
cd /home/admin/zhipu
./start_zhipu_comprehensive.sh
```

## 使用方法

### 在代码中使用

```javascript
const ZhipuMCPTools = require('clawd-skill-zhipu-mcp-tools');
const zhipuTools = new ZhipuMCPTools();

// 分析网页
const webpageResult = await zhipuTools.analyzeWebpage('https://example.com');

// 分析图片
const imageResult = await zhipuTools.analyzeImage('/path/to/image.jpg');

// 联网搜索
const searchResult = await zhipuTools.webSearch('搜索关键词', 5);

// 分析仓库
const repoResult = await zhipuTools.analyzeRepo('https://github.com/user/repo');

// 生成文本
const textResult = await zhipuTools.generateText('生成提示词', 'glm-4');
```

## API

### analyzeWebpage(url)
分析网页内容并返回摘要。

### analyzeImage(imagePath)
分析图片内容并返回描述。

### webSearch(query, maxResults = 5)
执行联网搜索。

### analyzeRepo(repoUrl)
分析代码仓库。

### generateText(prompt, model = 'glm-4')
生成文本。

## 依赖

- 智谱AI MCP服务器
- Node.js
- Axios

## 许可证

MIT