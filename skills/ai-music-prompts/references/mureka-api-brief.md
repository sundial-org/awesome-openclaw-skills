# Mureka V8 API 简要参考 / Mureka V8 API Brief Reference

> **注意 / Note**：本文档为 Mureka V8 API 的简要参考，供未来 API 集成使用。
> **This document is a brief reference for Mureka V8 API, intended for future API integration.**

---

## 官方资源 / Official Resources

- **API 平台 / API Platform**: https://platform.mureka.ai/
- **API 文档 / API Documentation**: https://platform.mureka.ai/docs/
- **Mureka V8 官网 / Official Website**: https://murekav8.com/
- **歌曲生成 API / Song Generation API**: https://platform.mureka.ai/docs/api/operations/post-v1-song-generate.html

---

## 核心 API 端点 / Core API Endpoints

### 1. 歌曲生成 / Song Generation

**端点 / Endpoint**: `POST /v1/song/generate`

**描述 / Description**: 根据提示词生成完整歌曲（包含人声）

**关键参数 / Key Parameters**:
- `gpt_description` (string): 歌曲描述/提示词，最多 1024 字符
- `lyrics` (string, optional): 歌词内容
- `refer_audio` (string, optional): 参考音频 URL
- `n` (integer, optional): 生成数量，默认 1

**提示词映射 / Prompt Mapping**:
```
提示词格式 / Prompt Format:
[流派] with [人声类型], [情绪描述], [乐器细节], [速度/能量], [语言特点]

对应参数 / Corresponding Parameter:
gpt_description: "Pop with warm female vocals, emotional, piano and strings, mid-tempo, clear Mandarin"
```

**Python 示例 / Python Example**:
```python
import requests

url = "https://platform.mureka.ai/v1/song/generate"
headers = {
    "Authorization": "Bearer YOUR_API_KEY",
    "Content-Type": "application/json"
}
data = {
    "gpt_description": "华语流行 with 温暖女声, 深情动人, 钢琴弦乐, 90-100 BPM, 普通话清晰发音 - 关于思念的情歌",
    "n": 1
}

response = requests.post(url, json=data, headers=headers)
task_id = response.json()["task_id"]
```

**JavaScript 示例 / JavaScript Example**:
```javascript
const url = "https://platform.mureka.ai/v1/song/generate";
const headers = {
  "Authorization": "Bearer YOUR_API_KEY",
  "Content-Type": "application/json"
};
const data = {
  gpt_description: "华语流行 with 温暖女声, 深情动人, 钢琴弦乐, 90-100 BPM, 普通话清晰发音 - 关于思念的情歌",
  n: 1
};

fetch(url, {
  method: "POST",
  headers: headers,
  body: JSON.stringify(data)
})
.then(response => response.json())
.then(data => console.log(data.task_id));
```

### 2. 纯音乐生成 / Instrumental Generation

**端点 / Endpoint**: `POST /v1/instrumental/generate`

**描述 / Description**: 生成纯音乐（无人声）

**关键参数 / Key Parameters**:
- `gpt_description` (string): 音乐描述/提示词，最多 1024 字符
- `refer_audio` (string, optional): 参考音频 URL
- `n` (integer, optional): 生成数量，默认 1

### 3. 歌词生成 / Lyrics Generation

**端点 / Endpoint**: `POST /v1/lyrics/generate`

**描述 / Description**: 生成歌词

**关键参数 / Key Parameters**:
- `gpt_description` (string): 歌词描述/提示词
- `topic` (string, optional): 歌词主题
- `language` (string, optional): 语言（如：zh、en）

### 4. 歌曲续写 / Song Extension

**端点 / Endpoint**: `POST /v1/song/extend`

**描述 / Description**: 续写/扩展现有歌曲

**关键参数 / Key Parameters**:
- `song_id` (string): 原歌曲 ID
- `extend_audio_duration` (integer): 续写时长（秒）

---

## 提示词参数映射 / Prompt Parameter Mapping

### 中文提示词结构 / Chinese Prompt Structure

| 元素 / Element | 参数 / Parameter | 示例 / Example | 说明 / Description |
|----------------|-----------------|----------------|-------------------|
| **流派 / Genre** | `gpt_description` | "华语流行"、"古风" | 音乐风格 |
| **人声 / Vocals** | `gpt_description` | "温暖女声"、"沧桑男声" | 人声类型和特征 |
| **情绪 / Mood** | `gpt_description` | "深情"、"欢快"、"怀旧" | 情感基调 |
| **乐器 / Instruments** | `gpt_description` | "钢琴弦乐"、"古筝笛子" | 主要乐器 |
| **速度 / Tempo** | `gpt_description` | "90-100 BPM"、"中速" | 速度或 BPM |
| **语言 / Language** | `gpt_description` | "普通话清晰发音"、"粤语标准发音" | 语言特点 |
| **描述 / Description** | `gpt_description` | "关于思念的情歌" | 歌曲主题或描述 |

### 完整示例 / Complete Example

```json
{
  "gpt_description": "华语流行 with 温暖女声, 深情动人, 钢琴和弦乐, 中速 90-100 BPM, 普通话清晰发音 - 关于思念和爱情的感人情歌，旋律优美动人"
}
```

---

## API 限制与最佳实践 / API Limits and Best Practices

### 限制 / Limits

1. **提示词长度 / Prompt Length**: 最多 1024 字符
   - 建议 / Recommended: 200-500 字符为最佳范围

2. **生成数量 / Generation Count**: 默认 1，最多取决于订阅计划

3. **速率限制 / Rate Limit**: 根据订阅计划而定

### 最佳实践 / Best Practices

1. **提示词优化 / Prompt Optimization**
   - ✅ 使用具体情绪描述（深情、欢快、激昂）
   - ✅ 明确人声特征（温暖清澈、磁性低沉）
   - ✅ 指定乐器搭配（钢琴、古筝、电吉他）
   - ✅ 说明语言特点（标准普通话、粤语标准发音）
   - ❌ 避免模糊描述（好听、不错、很棒）

2. **歌词使用 / Using Lyrics**
   - 可以在 `lyrics` 参数中提供自定义歌词
   - 歌词与提示词结合使用效果更佳
   - 中文歌词建议 100-300 字

3. **参考音频 / Reference Audio**
   - 上传参考音频可以更好地控制风格
   - 参考音频 URL 需要公开可访问
   - 支持风格匹配功能

4. **异步处理 / Async Processing**
   - 生成是异步的，需要轮询任务状态
   - 使用 `task_id` 查询生成进度
   - 支持流式输出（流式播放）

---

## 任务状态查询 / Task Status Query

**端点 / Endpoint**: `GET /v1/song/query/{task_id}`

**描述 / Description**: 查询任务状态和结果

**响应 / Response**:
```json
{
  "task_id": "string",
  "status": "pending | processing | completed | failed",
  "result": {
    "audio_url": "string",
    "duration": integer,
    "metadata": {...}
  }
}
```

---

## 错误代码 / Error Codes

| 代码 / Code | 说明 / Description | 解决方案 / Solution |
|-------------|-------------------|---------------------|
| `400` | 请求参数错误 / Bad Request | 检查提示词格式和参数 |
| `401` | 未授权 / Unauthorized | 检查 API 密钥 |
| `429` | 请求过多 / Too Many Requests | 降低请求频率 |
| `500` | 服务器错误 / Server Error | 稍后重试 |

---

## 订阅计划 / Subscription Plans

| 计划 / Plan | 每月歌曲数 / Songs per Month | 商用权 / Commercial Rights | 高级功能 / Advanced Features |
|------------|------------------------------|---------------------------|---------------------------|
| **Free / 免费版** | 有限 / Limited | 个人使用 / Personal Only | 基础功能 / Basic |
| **Basic / 基础版** | 400 首 / Songs | ✅ 是 / Yes | 优先生成 / Priority |
| **Pro / 专业版** | 1,600 首 / Songs | ✅ 是 / Yes | 全部功能 / All Features |

---

## 快速开始示例 / Quick Start Examples

### 示例 1：生成华语流行情歌 / Example 1: Generate Mandopop Ballad

```python
import requests

url = "https://platform.mureka.ai/v1/song/generate"
headers = {"Authorization": "Bearer YOUR_API_KEY"}
data = {
    "gpt_description": "华语流行 with 温暖女声, 深情动人, 钢琴和弦乐, 90-100 BPM, 普通话清晰发音 - 关于思念和爱情的感人情歌"
}

response = requests.post(url, json=data, headers=headers)
print(response.json())
```

### 示例 2：生成古风音乐 / Example 2: Generate Gufeng Music

```python
data = {
    "gpt_description": "古风 with 空灵女声, 悠扬清幽, 古筝和笛子, 70-80 BPM, 中国风编曲 - 仙侠风格，清幽脱俗的意境"
}

response = requests.post(url, json=data, headers=headers)
print(response.json())
```

### 示例 3：带歌词生成 / Example 3: Generate with Lyrics

```python
data = {
    "gpt_description": "华语流行 with 温暖女声, 深情, 钢琴, 90 BPM - 关于思念的情歌",
    "lyrics": """主歌：
窗外的月光洒在床边
想起你温柔的脸

副歌：
我多么想再见你一面
告诉你我对你的眷恋"""
}

response = requests.post(url, json=data, headers=headers)
print(response.json())
```

---

## 下一步 / Next Steps

1. **注册账号 / Sign Up**: 在 https://platform.mureka.ai/ 注册
2. **获取 API 密钥 / Get API Key**: 在控制台获取 API 密钥
3. **阅读文档 / Read Documentation**: 查看 https://platform.mureka.ai/docs/
4. **测试 API / Test API**: 使用示例代码测试端点
5. **集成应用 / Integrate**: 将 API 集成到你的应用中

---

**相关文档 / Related Documentation**:
- [Mureka V8 中文优化指南](./mureka-chinese.md)
- [Mureka V8 中文提示词示例](../examples/mureka-chinese-prompts.json)
- [Mureka API 官方文档](https://platform.mureka.ai/docs/)

**最后更新 / Last Updated**: 2026-01-29
**文档版本 / Document Version**: 1.0
