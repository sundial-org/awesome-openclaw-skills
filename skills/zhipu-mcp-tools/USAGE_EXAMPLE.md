# zhipu-mcp-tools 使用示例

## 在Clawd中使用技能

### 1. 基本用法

```javascript
// 导入技能
const ZhipuMCPTools = require('clawd-skill-zhipu-mcp-tools');
const zhipuTools = new ZhipuMCPTools();

// 分析网页
const webpageResult = await zhipuTools.analyzeWebpage('https://example.com');
console.log(webpageResult);

// 分析图片
const imageResult = await zhipuTools.analyzeImage('/path/to/image.jpg');
console.log(imageResult);

// 联网搜索
const searchResult = await zhipuTools.webSearch('人工智能最新进展', 5);
console.log(searchResult);

// 分析仓库
const repoResult = await zhipuTools.analyzeRepo('https://github.com/user/repo');
console.log(repoResult);

// 生成文本
const textResult = await zhipuTools.generateText('写一段关于气候变化的描述', 'glm-4');
console.log(textResult);
```

### 2. 在Agent中集成

```javascript
// 在Agent中使用技能
class MyAgent {
  constructor() {
    this.zhipuTools = new (require('clawd-skill-zhipu-mcp-tools'))();
  }

  async handleRequest(request) {
    if (request.type === 'web-analyze') {
      return await this.zhipuTools.analyzeWebpage(request.url);
    } else if (request.type === 'image-analyze') {
      return await this.zhipuTools.analyzeImage(request.imagePath);
    } else if (request.type === 'search') {
      return await this.zhipuTools.webSearch(request.query, request.maxResults || 5);
    }
    // ... 其他处理
  }
}
```

### 3. 插件方式使用

```javascript
// 使用插件接口
const ZhipuMCPPlugin = require('clawd-skill-zhipu-mcp-tools/plugin.js');
const plugin = new ZhipuMCPPlugin(clawdInstance);

// 初始化插件
await plugin.initialize();

// 使用插件功能
const result = await plugin.analyzeWebpage('https://example.com');
```

## 注意事项

1. 确保智谱AI MCP服务器正在运行 (http://localhost:8000)
2. 确保已正确配置API密钥
3. 网络请求可能需要一定时间，请适当设置超时
4. 图片分析需要将图片转换为base64格式或提供可访问的URL

## 错误处理

```javascript
const result = await zhipuTools.analyzeWebpage('https://example.com');

if (result.success) {
  console.log('成功:', result.result);
} else {
  console.error('错误:', result.error);
}
```