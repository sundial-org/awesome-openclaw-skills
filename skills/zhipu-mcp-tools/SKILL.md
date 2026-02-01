# zhipu-mcp-tools

使用智谱AI MCP服务器提供的多种AI能力，包括网页分析、视觉理解等功能。

## 功能

- **网页分析**: 通过智谱AI的web_reader工具分析网页内容
- **视觉理解**: 通过智谱AI的vision_analyzer工具进行图像分析
- **联网搜索**: 通过智谱AI的web_search工具进行网络搜索
- **仓库分析**: 通过智谱AI的repo_analyzer工具分析GitHub/GitLab仓库
- **文本生成**: 通过智谱AI的text_generator工具生成文本

## 使用方法

### 网页分析
```
分析网页 [URL]
```

### 视觉理解
```
分析图片 [图片路径或URL]
```

### 联网搜索
```
搜索 [搜索查询]
```

### 仓库分析
```
分析仓库 [仓库URL]
```

### 文本生成
```
生成 [生成请求]
```

## 依赖

- 智谱AI MCP服务器正在运行 (http://localhost:8000)
- Python requests 库