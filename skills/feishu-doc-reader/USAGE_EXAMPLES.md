# Feishu Doc Reader Usage Examples

## 获取完整文档Blocks结构

### 使用Shell脚本（推荐）
```bash
# 获取文档的完整blocks结构
./scripts/get_blocks.sh "docx_AbCdEfGhIjKlMnOpQrStUv"

# 输出到文件
./scripts/get_blocks.sh "docx_AbCdEfGhIjKlMnOpQrStUv" > document_blocks.json
```

### 使用Python脚本直接
```bash
# 获取完整文档信息（包括blocks）
python scripts/get_feishu_doc_blocks.py --doc-token "docx_AbCdEfGhIjKlMnOpQrStUv" --format full

# 仅获取纯文本内容
python scripts/get_feishu_doc_blocks.py --doc-token "docx_AbCdEfGhIjKlMnOpQrStUv" --format simple
```

## 文档Blocks结构说明

飞书文档的blocks结构包含以下主要类型：

### 文本块 (text)
```json
{
  "block_type": "text",
  "text": {
    "elements": [
      {
        "type": "text_run",
        "text_run": {
          "content": "这是普通文本"
        }
      }
    ]
  }
}
```

### 标题块 (heading1/2/3)
```json
{
  "block_type": "heading1",
  "heading1": {
    "elements": [
      {
        "type": "text_run", 
        "text_run": {
          "content": "一级标题"
        }
      }
    ]
  }
}
```

### 表格块 (table)
```json
{
  "block_type": "table",
  "table": {
    "rows": 2,
    "cols": 3,
    "cells": {
      "cell_1_1": {
        "blocks": ["block_id_1"]
      }
    }
  }
}
```

### 图片块 (image)
```json
{
  "block_type": "image",
  "image": {
    "token": "img_token_here",
    "width": 500,
    "height": 300
  }
}
```

## 集成到AI Agent工作流

### 在AI Agent中调用
```javascript
// 使用exec工具调用脚本
const result = await exec(`cd /path/to/feishu-doc-reader && ./scripts/get_blocks.sh "${docToken}"`);
const docData = JSON.parse(result.stdout);
```

### 处理文档内容
```javascript
// 提取文档标题
const title = docData.document.title;

// 遍历所有blocks
const blocks = docData.blocks;
for (const [blockId, block] of Object.entries(blocks)) {
  switch (block.block_type) {
    case 'text':
      // 处理文本块
      break;
    case 'heading1':
      // 处理一级标题
      break;
    case 'table':
      // 处理表格
      break;
    // ... 其他类型
  }
}
```

## 错误处理最佳实践

### 常见错误代码
- `99991663`: 应用没有权限访问该文档
- `99991664`: 文档不存在或已被删除  
- `99991668`: token过期，需要重新获取

### 重试策略
```bash
# 实现简单的重试逻辑
max_retries=3
retry_count=0

while [ $retry_count -lt $max_retries ]; do
  if ./scripts/get_blocks.sh "$doc_token"; then
    break
  else
    retry_count=$((retry_count + 1))
    sleep $((retry_count * 2))
  fi
done
```

## 性能优化建议

### Token缓存
- tenant_access_token有效期为2小时，建议缓存以减少API调用
- 脚本已内置token缓存机制

### 大文档处理
- 对于大型文档，考虑分批处理blocks
- 监控内存使用，避免OOM

### 速率限制
- 飞书API有调用频率限制
- 在批量处理时添加适当的延迟

## 安全注意事项

### 凭证管理
- 将`feishu_config.json`设置为600权限：`chmod 600 reference/feishu_config.json`
- 不要将凭证提交到版本控制系统

### 最小权限原则
- 只申请必要的API权限
- 定期审查应用权限

## 调试技巧

### 启用详细日志
```bash
# 设置环境变量启用调试日志
export FEISHU_DEBUG=true
./scripts/get_blocks.sh "docx_token"
```

### 手动测试API
```bash
# 获取tenant_access_token
curl -X POST https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal \
  -H "Content-Type: application/json" \
  -d '{"app_id":"your_app_id","app_secret":"your_app_secret"}'

# 使用token获取文档blocks
curl -H "Authorization: Bearer your_token" \
  https://open.feishu.cn/open-apis/docx/v1/documents/docx_token/blocks
```