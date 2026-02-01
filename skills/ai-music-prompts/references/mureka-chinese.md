# Mureka V8 中文优化指南 / Mureka V8 Chinese Optimization Guide

专门针对 Mureka V8 AI 音乐生成器的中文音乐提示词优化技巧，包括普通话和粤语的最佳实践。
Specialized techniques for optimizing Chinese music prompts for Mureka V8 AI music generator, including best practices for Mandarin and Cantonese.

---

## 为什么 Mureka V8 擅长中文 / Why Mureka V8 Excels at Chinese

### MusiCoT 技术优势 / MusiCoT Technology Advantages

**MusiCoT**（Music Chain-of-Thought）是 Mureka 的核心技术，它模拟人类音乐创作过程：

1. **全局规划**：先规划歌曲结构、情绪弧线、编排
2. **局部填充**：基于结构蓝图生成详细音频

**对中文的优势**：
- ✅ 更好的声调处理：中文有四个声调（普通话）或九个声调（粤语）
- ✅ 更自然的旋律线：理解声调与旋律的关系
- ✅ 更准确的发音：70% 人声真实度，发音清晰自然
- ✅ 更好的情感表达：理解中文情感细微差别

### 中文语言支持 / Chinese Language Support

| 语言 / Language | 声调 / Tones | 特点 / Characteristics | 最佳场景 / Best For |
|-----------------|--------------|------------------------|---------------------|
| **普通话 / Mandarin** | 4 声 | 标准发音，应用广泛 | 流行、摇滚、民谣 |
| **粤语 / Cantonese** | 9 声 | 独特韵味，港式风格 | 抒情、经典、怀旧 |
| **闽南语 / Minnan** | 7 声 | 地方特色 | 闽南风、台语歌 |
| **四川话 / Sichuanese** | 变调 | 幽默风趣 | 民谣、地方特色 |

---

## 普通话提示词最佳实践 / Mandarin Prompt Best Practices

### 普通话发音特点 / Mandarin Pronunciation Characteristics

#### 声调与旋律 / Tones and Melody
```
普通话四声：
1. 阴平（¯）：高平调 - 适合长音、延续音
2. 阳平（´）：升调 - 适合上扬旋律
3. 上声（ˇ）：降升调 - 适合波浪型旋律
4. 去声（ˋ）：降调 - 适合下行旋律
```

**提示词建议**：
- 明确要求"标准普通话发音"
- 强调"清晰咬字"和"自然表达"
- 可以指定"央视播音腔"或"口语化表达"

### 普通话人声类型 / Mandarin Vocal Types

#### 女声类型 / Female Voice Types

**1. 温暖清澈 / Warm and Clear**
```
应用场景：抒情歌、民谣、校园歌曲
提示词示例：
- 温暖清澈女声，标准普通话
- 清新甜美，自然表达
- 像梁静茹、孙燕姿风格
```

**2. 空灵飘渺 / Ethereal and Dreamy**
```
应用场景：古风、仙侠、意境歌曲
提示词示例：
- 空灵女声，悠扬婉转
- 清幽脱俗，仙气飘飘
- 像王菲、霍尊风格
```

**3. 高亢有力 / Powerful and Strong**
```
应用场景：摇滚、励志、颂歌
提示词示例：
- 高亢女声，充满力量
- 激情澎湃，穿透力强
- 像邓紫棋、张靓颖风格
```

#### 男声类型 / Male Voice Types

**1. 温暖磁性 / Warm and Magnetic**
```
应用场景：情歌、抒情、流行
提示词示例：
- 温暖男声，磁性低沉
- 深情款款，诉说感强
- 像陈奕迅、周杰伦风格
```

**2. 沧桑成熟 / Weathered and Mature**
```
应用场景：怀旧、感悟、人生
提示词示例：
- 沧桑男声，历经岁月
- 成熟稳重，故事感强
- 像李宗盛、罗大佑风格
```

**3. 青春阳光 / Youthful and Sunny**
```
应用场景：校园、励志、轻快
提示词示例：
- 清新男声，青春阳光
- 活力充沛，朝气蓬勃
- 像许嵩、汪苏泷风格
```

### 普通话提示词模板 / Mandarin Prompt Templates

#### 流行情歌 / Pop Ballad Template
```
华语流行 [人声类型] [情绪] [速度] [乐器] [语言特点] - [歌曲描述]

示例 Examples:

华语流行 温暖女声 深情 90 BPM 钢琴弦乐 标准普通话 - 关于思念的情歌

Mandarin pop with warm female vocals, emotional, 90 BPM, piano and strings, standard Mandarin - A love song about longing
```

#### 校园民谣 / Campus Folk Template
```
校园民谣 清新人声 怀旧 80-90 BPM 木吉他 清晰普通话 - 青春回忆，校园时光

Campus folk with fresh vocals, nostalgic, 80-90 BPM, acoustic guitar, clear Mandarin - Youth memories, campus days
```

#### 励志歌曲 / Inspirational Song Template
```
华语流行 激昂人声 充满力量 120-130 BPM 强节奏 有力普通话 - 追逐梦想，永不放弃

Mandarin pop with passionate vocals, empowering, 120-130 BPM, strong rhythm, powerful Mandarin - Chasing dreams, never give up
```

---

## 粤语提示词特殊技巧 / Cantonese Prompt Special Techniques

### 粤语发音特点 / Cantonese Pronunciation Characteristics

#### 九声与旋律 / Nine Tones and Melody
```
粤语九声：
1. 阴平（1声）：高平 / 高长音
2. 阴上（2声）：高升 / 上升音
3. 阴去（3声）：高降 / 下降音
4. 阳平（4声）：低平 / 低长音
5. 阳上（5声）：低升 / 低上升
6. 阳去（6声）：低降 / 低下降
7. 阴入（7声）：高短 / 高短促
8. 中入（8声）：中短 / 中短促
9. 阳入（9声）：低短 / 低短促
```

**提示词建议**：
- 要求"标准粤语发音"或"港式粤语"
- 可以指定"广东话"或"香港粤语"
- 强调"九声准确"和"地道表达"

### 粤语人声类型 / Cantonese Vocal Types

#### 经典港式男声 / Classic Hong Kong Male Voice
```
特点：成熟、沧桑、故事感强
提示词示例：
- 沧桑男声，经典港式
- 历经岁月，情感深沉
- 像张学友、刘德华风格
```

#### 清新港式女声 / Fresh Hong Kong Female Voice
```
特点：清澈、甜美、港式韵味
提示词示例：
- 清新女声，港式甜美
- 自然表达，港味十足
- 像杨千嬅、容祖儿风格
```

#### 粤语 R&B 风格 / Cantonese R&B Style
```
特点：节奏感强、现代感、流畅
提示词示例：
- R&B 风格，流畅粤语
- 现代感强，节奏明快
- 像方大同、陈奕迅（粤语歌）风格
```

### 粤语提示词模板 / Cantonese Prompt Templates

#### 经典港式抒情 / Classic Hong Kong Ballad Template
```
粤语流行 [人声类型] [情绪] [速度] [乐器] [语言特点] - [歌曲描述]

示例 Examples:

粤语流行 沧桑男声 怀旧 80 BPM 钢琴吉他 标准粤语 - 经典港式抒情，关于时光流逝

Cantonese pop with weathered male vocals, nostalgic, 80 BPM, piano and guitar, standard Cantonese - Classic Hong Kong style ballad about the passage of time
```

#### 粤语流行快歌 / Cantonese Pop Upbeat Template
```
粤语流行 活力人声 欢快 120-130 BPM 电子乐 节奏感粤语 - 动感快歌，都市节奏

Cantonese pop with energetic vocals, upbeat, 120-130 BPM, electronic, rhythmic Cantonese - Upbeat fast song, urban rhythm
```

---

## 中文情绪词汇库 / Chinese Emotion Vocabulary

### 积极情绪 / Positive Emotions

| 情绪 / Emotion | 中文描述 / Chinese | 适用场景 / Use Case |
|----------------|-------------------|---------------------|
| **欢快 / Joyful** | 欢快、愉悦、开心 | 节日、庆典、快乐主题 |
| **温馨 / Warm** | 温馨、温暖、舒适 | 家人、友情、回忆 |
| **激昂 / Passionate** | 激昂、澎湃、热血 | 励志、奋斗、梦想 |
| **希望 / Hopeful** | 充满希望、光明、憧憬 | 未来、梦想、新生 |
| **甜蜜 / Sweet** | 甜蜜、浪漫、柔情 | 爱情、约会、幸福 |
| **轻松 / Relaxed** | 轻松、自在、悠闲 | 休闲、放松、度假 |
| **自信 / Confident** | 自信、坚定、果敢 | 成功、胜利、力量 |
| **感动 / Touched** | 感动、温暖、触动 | 感恩、友情、亲情 |

### 消极情绪 / Negative Emotions

| 情绪 / Emotion | 中文描述 / Chinese | 适用场景 / Use Case |
|----------------|-------------------|---------------------|
| **伤感 / Sad** | 伤感、悲伤、难过 | 失恋、失去、离别 |
| **忧郁 / Melancholic** | 忧郁、愁苦、惆怅 | 思念、遗憾、回忆 |
| **孤独 / Lonely** | 孤独、寂寞、孤单 | 独处、思念、漂泊 |
| **痛苦 / Painful** | 痛苦、煎熬、挣扎 | 困境、磨难、挫折 |
| **绝望 / Desperate** | 绝望、无助、崩溃 | 谷底、黑暗、绝望 |
| **愤怒 / Angry** | 愤怒、怒火、不平 | 不公、背叛、反抗 |
| **焦虑 / Anxious** | 焦虑、不安、紧张 | 压力、迷茫、困惑 |
| **怀旧 / Nostalgic** | 怀旧、怀念、回想 | 过去、青春、回忆 |

### 中性情绪 / Neutral Emotions

| 情绪 / Emotion | 中文描述 / Chinese | 适用场景 / Use Case |
|----------------|-------------------|---------------------|
| **平静 / Calm** | 平静、安宁、淡然 | 冥想、宁静、内观 |
| **空灵 / Ethereal** | 空灵、飘渺、出尘 | 古风、仙侠、意境 |
| **神秘 / Mysterious** | 神秘、莫测、幽深 | 悬疑、探索、未知 |
| **梦幻 / Dreamy** | 梦幻、迷离、虚幻 | 梦境、幻想、童话 |
| **深沉 / Deep** | 深沉、厚重、凝重 | 思考、哲学、人生 |
| **淡雅 / Elegant** | 淡雅、清雅、素雅 | 文艺、清新、雅致 |

---

## 中文乐器描述 / Chinese Instrument Descriptions

### 中国传统乐器 / Chinese Traditional Instruments

| 乐器 / Instrument | 中文 / Chinese | 特点 / Characteristics | 情绪 / Mood |
|------------------|----------------|------------------------|-------------|
| **古筝 / Guzheng** | 古筝 | 悠扬、清雅、流水般 | 空灵、悠扬、古典 |
| **笛子 / Dizi** | 笛子 | 清脆、悠远、穿透力 | 清幽、飘逸、自然 |
| **二胡 / Erhu** | 二胡 | 哀婉、深情、诉说感 | 伤感、怀旧、深情 |
| **琵琶 / Pipa** | 琵琶 | 清脆、力度丰富、颗粒感 | 古典、刚柔并济 |
| **扬琴 / Yangqin** | 扬琴 | 清脆、共鸣好、和声 | 明亮、欢快、和谐 |
| **箫 / Xiao** | 箫 | 低沉、幽深、空灵 | 沧桑、悠远、空灵 |
| **古琴 / Guqin** | 古琴 | 古朴、深沉、禅意 | 古朴、宁静、超脱 |
| **唢呐 / Suona** | 唢呐 | 高亢、嘹亮、喜庆 | 热烈、喜庆、豪迈 |
| **中国鼓 / Chinese Drum** | 中国鼓 | 震撼、有力、节奏感 | 宏大、磅礴、激昂 |

### 中西融合乐器 / East-West Fusion Instruments

| 组合 / Combination | 中文描述 / Chinese | 效果 / Effect |
|--------------------|-------------------|---------------|
| **钢琴 + 古筝** | 钢琴古筝合奏 | 东西交融，现代感 |
| **弦乐 + 笛子** | 弦乐配笛子 | 悠扬大气，影视感 |
| **电子 + 二胡** | 电子配二胡 | 现代国风，独特韵味 |
| **吉他 + 扬琴** | 吉他配扬琴 | 民谣融合，清新自然 |
| **鼓 + 中国鼓** | 中西鼓乐结合 | 层次丰富，震撼力强 |

---

## 中文音乐术语对照 / Chinese Music Terminology

### 流派术语 / Genre Terms

| 中文 / Chinese | 英文 / English | 说明 / Description |
|----------------|----------------|-------------------|
| 华语流行 | Mandopop | 华语流行音乐 |
| 粤语流行 | Cantopop | 粤语流行音乐 |
| 古风 | Gufeng / Chinese Traditional Style | 古代风格 |
| 国风 | Guofeng / National Style | 国家风格，现代国风 |
| 民谣 | Folk / Minyao | 民间歌谣 |
| 校园民谣 | Campus Folk | 校园风格民谣 |
| 摇滚 | Rock | 摇滚音乐 |
| 说唱 | Rap / Hip-Hop | 说唱音乐 |
| R&B | R&B | 节奏布鲁斯 |
| 电子 | Electronic | 电子音乐 |

### 人声术语 / Vocal Terms

| 中文 / Chinese | 英文 / English | 说明 / Description |
|----------------|----------------|-------------------|
| 温暖 | Warm | 温暖柔和 |
| 清澈 | Clear | 清晰明亮 |
| 磁性 | Magnetic | 有吸引力 |
| 沧桑 | Weathered | 历经岁月 |
| 空灵 | Ethereal | 空灵感 |
| 高亢 | High-pitched | 高音明亮 |
| 深情 | Emotional/Deep | 情感深厚 |
| 激昂 | Passionate | 激情澎湃 |
| 柔和 | Gentle | 温柔柔顺 |
| 有力 | Powerful | 有力量感 |

### 情绪术语 / Emotion Terms

| 中文 / Chinese | 英文 / English | 说明 / Description |
|----------------|----------------|-------------------|
| 欢快 | Upbeat/Joyful | 快乐愉悦 |
| 深情 | Emotional | 情感深厚 |
| 伤感 | Sad/Melancholic | 悲伤忧郁 |
| 怀旧 | Nostalgic | 怀念过去 |
| 激昂 | Passionate | 激情澎湃 |
| 空灵 | Ethereal | 空灵飘渺 |
| 温馨 | Warm/Cozy | 温暖舒适 |
| 沧桑 | Weathered | 饱经风霜 |

### 速度术语 / Tempo Terms

| 中文 / Chinese | BPM | 英文 / English | 适用 / Suitable For |
|----------------|-----|----------------|---------------------|
| 慢速 | 60-80 | Slow | 抒情、安静 |
| 中慢 | 80-100 | Mid-Slow | 流行、民谣 |
| 中速 | 100-120 | Mid-Tempo | 流行、轻快 |
| 中快 | 120-140 | Mid-Fast | 摇滚、舞曲 |
| 快速 | 140+ | Fast | 电子、说唱 |

---

## Mureka V8 中文提示词检查清单 / Mureka V8 Chinese Prompt Checklist

在使用 Mureka V8 生成中文音乐前，检查以下要点：

### ✅ 必须包含 / Must Include

- [ ] **明确流派**：华语流行、古风、摇滚等
- [ ] **具体情绪**：深情、欢快、伤感等
- [ ] **人声特征**：温暖、清澈、沧桑等
- [ ] **乐器搭配**：钢琴、古筝、吉他等
- [ ] **速度指示**：BPM 或慢速/中速/快速
- [ ] **语言特点**：标准普通话、粤语等

### ✅ 优化建议 / Optimization Tips

- [ ] **提示词长度**：200-500 字符为佳（最多 1024）
- [ ] **情绪具体化**：避免"好听""不错"等模糊词
- [ ] **人声明确化**：不要只写"女声""男声"
- [ ] **乐器合理性**：搭配符合流派特点
- [ ] **参考风格**：可以指定像某某歌手风格

### ✅ 避免错误 / Avoid These Mistakes

- [ ] ❌ 不要过于简单："华语流行，女声，好听"
- [ ] ❌ 不要自相矛盾："欢快伤感歌"
- [ ] ❌ 不要元素过多：超过 1024 字符
- [ ] ❌ 不要乐器冲突："古风配电吉他重金属"
- [ ] ❌ 不要情绪模糊："感觉不错" "很棒"

---

## 常见问题解答 / FAQ

### Q1: Mureka V8 生成中文歌曲有什么优势？

**A**: Mureka V8 使用 MusiCoT 技术，对中文的声调处理、旋律生成、人声合成都有专门优化，人声真实度达 70%，特别适合普通话和粤语。

### Q2: 如何让 Mureka V8 生成更像真人的中文人声？

**A**: 在提示词中明确描述人声特征，如"温暖清澈女声""沧桑男声"，并指定语言特点，如"标准普通话发音""清晰咬字"。

### Q3: 可以混合普通话和粤语吗？

**A**: 可以，但建议明确说明，如"主歌普通话，副歌粤语"或"双语混合，普通话为主"。

### Q4: 如何生成古风歌曲？

**A**: 使用"古风"或"国风"作为流派，搭配中国传统乐器（古筝、笛子、二胡），指定"空灵女声"或"悠扬男声"。

### Q5: 提示词最长可以是多少？

**A**: Mureka V8 限制提示词最长 1024 字符，建议使用 200-500 字符以获得最佳效果。

### Q6: 可以指定像某某歌手的风格吗？

**A**: 可以，在提示词中提及参考风格会有帮助，如"像陈奕迅风格""类似王菲的空灵唱腔"。

---

**相关资源 / Related Resources**：
- [中文歌词写作技巧](./lyrics.md#中文歌词写作-chinese-lyric-writing)
- [中国传统音乐](./chinese-traditional.md)
- [中文情绪词汇库](./moods-chinese.md)
- [Mureka V8 API 文档](https://platform.mureka.ai/docs/)
