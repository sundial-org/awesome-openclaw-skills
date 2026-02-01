---
name: telegram-offline-voice
description: 本地生成 Telegram 语音消息，无需 API Token。
metadata: {"openclaw":{"emoji":"🎙️","os":["linux"],"requires":{"bins":["ffmpeg","edge-tts"]}}}
---

# telegram-offline-voice 🎙️

**本地生成，无需 Token** — 使用 Microsoft Edge-TTS 生成高质量中文语音，完全离线处理，无需申请任何 API Key。

## 特性

- 🔒 **完全本地**：无需 OpenAI / Google / Azure 等云服务 Token
- 🎯 **零成本**：Edge-TTS 免费使用，无调用限制
- 🗣️ **高质量声线**：默认使用微软晓晓 (zh-CN-XiaoxiaoNeural)
- 📱 **Telegram 原生支持**：输出格式符合语音气泡标准

## 安装依赖

```bash
# Edge-TTS
pip install edge-tts

# FFmpeg (Debian/Ubuntu)
apt install ffmpeg
```

## 使用方法

```bash
# 1. 生成原始音频
edge-tts --voice zh-CN-XiaoxiaoNeural --rate=+5% --text "你好，这是测试" --write-media raw.mp3

# 2. 转换为 Telegram 语音格式
ffmpeg -y -i raw.mp3 -c:a libopus -b:a 48k -ac 1 -ar 48000 -application voip voice.ogg
```

## 技术规范

### 文本格式清洗

生成语音前需清洗文本，避免朗读出标记符号：

| 需移除 | 示例 |
|--------|------|
| Markdown 标记 | `**加粗**`、`` `代码` ``、`# 标题` |
| URL 链接 | `https://example.com` |
| 特殊符号 | `---`、`***`、`>>>` |

**清洗示例：**
```bash
# 简单清洗（去除常见 Markdown）
TEXT=$(echo "$RAW_TEXT" | sed 's/\*\*//g; s/`//g; s/^#\+ //g')
```

### Telegram 语音气泡格式

Telegram 要求语音消息使用 **OGG Opus** 格式，否则会显示为文件而非语音气泡：

```bash
ffmpeg -i input.mp3 -c:a libopus -b:a 48k -ac 1 -ar 48000 -application voip output.ogg
```

**参数说明：**
| 参数 | 值 | 说明 |
|------|-----|------|
| `-c:a` | `libopus` | Telegram 要求的编码器 |
| `-b:a` | `48k` | 音频比特率 |
| `-ac` | `1` | 单声道（语音标准） |
| `-ar` | `48000` | 采样率 48kHz |
| `-application` | `voip` | 针对语音优化 |

## 可用声线

```bash
# 查看所有中文声线
edge-tts --list-voices | grep zh-CN
```

**推荐：**
- `zh-CN-XiaoxiaoNeural` — 女声，自然亲和（默认）
- `zh-CN-YunxiNeural` — 男声，沉稳专业
- `zh-CN-XiaoyiNeural` — 女声，活泼年轻

## 语速调节

```bash
# 加速 5%
edge-tts --rate=+5% --text "..." --write-media out.mp3

# 减速 10%
edge-tts --rate=-10% --text "..." --write-media out.mp3
```

## 致谢

由 **@sanwecn** 调优并维护。
