# Telegram Offline Voice 🎙️

**本地生成 Telegram 语音消息，无需 API Token。**

使用 Microsoft Edge-TTS 生成高质量中文语音，完全本地处理，零成本，无限制。

## 快速开始

```bash
# 安装依赖
pip install edge-tts
apt install ffmpeg

# 生成语音
edge-tts --voice zh-CN-XiaoxiaoNeural --rate=+5% --text "你好" --write-media raw.mp3
ffmpeg -y -i raw.mp3 -c:a libopus -b:a 48k -ac 1 -ar 48000 -application voip voice.ogg
```

## 特性

- 🔒 **完全本地** — 无需云服务 Token
- 🎯 **零成本** — Edge-TTS 免费无限制
- 🗣️ **高质量** — 微软神经网络语音
- 📱 **Telegram 原生** — 输出符合语音气泡标准

## 文档

详见 [SKILL.md](./SKILL.md) 获取完整技术规范。

## 致谢

由 **@sanwecn** 调优并维护。
