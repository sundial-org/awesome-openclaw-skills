# zhipu-mcp-tools 示例

## 网页分析示例

```javascript
const ZhipuMCPTools = require('./index.js');
const zhipuTools = new ZhipuMCPTools();

// 分析网页
async function example() {
  const result = await zhipuTools.analyzeWebpage('https://example.com');
  console.log(result);
}

example();
```

## 视觉理解示例

```javascript
const ZhipuMCPTools = require('./index.js');
const zhipuTools = new ZhipuMCPTools();

// 分析图片
async function example() {
  const result = await zhipuTools.analyzeImage('/path/to/image.jpg');
  console.log(result);
}

example();
```

## 联网搜索示例

```javascript
const ZhipuMCPTools = require('./index.js');
const zhipuTools = new ZhipuMCPTools();

// 搜索
async function example() {
  const result = await zhipuTools.webSearch('人工智能发展趋势', 3);
  console.log(result);
}

example();
```

## 仓库分析示例

```javascript
const ZhipuMCPTools = require('./index.js');
const zhipuTools = new ZhipuMCPTools();

// 分析仓库
async function example() {
  const result = await zhipuTools.analyzeRepo('https://github.com/user/repo');
  console.log(result);
}

example();
```

## 文本生成示例

```javascript
const ZhipuMCPTools = require('./index.js');
const zhipuTools = new ZhipuMCPTools();

// 生成文本
async function example() {
  const result = await zhipuTools.generateText('写一篇关于气候变化的短文', 'glm-4');
  console.log(result);
}

example();
```