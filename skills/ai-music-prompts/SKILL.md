---
name: ai-music-prompts
description: AI music prompt templates and best practices for generating music with AI tools like Suno, Udio, Mureka, and others. Use when user needs to create music prompts, song ideas, or wants guidance on writing effective prompts for AI music generation. Includes bilingual prompt templates for various genres, mood descriptors, instrumentation guidance, and lyric writing tips. Also provides techniques for crafting specific musical outcomes and examples of well-structured prompts in Chinese and English.
---

# AI Music Prompts / AI 音乐提示词
# AI 音乐提示词模板与最佳实践

Generate high-quality music prompts for AI music generation tools (Suno, Udio, Mureka, etc.) using proven templates and techniques.
生成高质量的音乐提示词，用于 AI 音乐生成工具（Suno、Udio、Mureka 等），使用经过验证的模板和技巧。

---

## Mureka V8 快速入门 / Mureka V8 Quick Start

### 为什么选择 Mureka V8 / Why Mureka V8

**Mureka V8** 是由 Skywork AI 开发的最先进 AI 音乐生成器，特别对**中文音乐生成**进行了优化：

- 🎵 **MusiCoT 技术**：使用思维链技术，生成的音乐结构更连贯、专业
- 🇨🇳 **中文支持优异**：人声真实度达 70%，特别适合普通话和粤语
- 🌐 **多语言支持**：支持 10+ 种语言，包括普通话、粤语、英语、日语、韩语等
- 🎤 **专业级人声**：情感表达丰富，发音清晰自然
- ⚡ **流式生成**：实时听生成过程，提升创作效率

### 中文提示词核心格式 / Chinese Prompt Core Format

针对 Mureka V8 优化的中文提示词格式：

```
[流派] with [人声类型], [情绪描述], [乐器细节], [速度/能量], [语言特点]

[Genre] with [vocal type], [mood], [instruments], [tempo], [language features]
```

### 5 个最实用的中文提示词模板 / 5 Essential Chinese Prompt Templates

#### 1. 华语流行情歌 / Mandopop Ballad
```
华语流行 with 温暖女声, 深情动人, 钢琴和弦乐, 中速 90-100 BPM, 普通话清晰发音 - 关于思念和爱情的感人情歌

Mandopop with warm female vocals, emotional and touching, piano and strings, mid-tempo 90-100 BPM, clear Mandarin pronunciation - A heartfelt love song about longing and romance
```

#### 2. 粤语经典抒情 / Cantonese Ballad
```
粤语流行 with 沧桑男声, 怀旧感伤, 木吉他, 慢速 75-85 BPM, 粤语标准发音 - 经典港式抒情歌，关于时光流逝

Cantonese pop with weathered male vocals, nostalgic and melancholic, acoustic guitar, slow 75-85 BPM, standard Cantonese pronunciation - Classic Hong Kong style ballad about the passage of time
```

#### 3. 国风古风 / Chinese Traditional
```
古风 with 空灵女声, 悠扬清幽, 古筝和笛子, 慢速 70-80 BPM, 中国风编曲 - 仙侠风格，清幽脱俗的意境

Chinese traditional with ethereal female vocals, melodious and serene, guzheng and bamboo flute, slow 70-80 BPM, Chinese style arrangement - Xianxia (fantasy) style with pure and transcendent atmosphere
```

#### 4. 中文摇滚 / Chinese Rock
```
中文摇滚 with 激昂男声, 充满力量, 电吉他和鼓, 快速 140-150 BPM, 普通话有力表达 - 关于自由和梦想的摇滚颂歌

Chinese rock with passionate male vocals, full of power, electric guitar and drums, fast 140-150 BPM, powerful Mandarin expression - Rock anthem about freedom and dreams
```

#### 5. 中文说唱 / Chinese Hip-Hop
```
中文说唱 with 自信 Flow, 都市风格, Trap 节奏和 808 贝斯, 中速 90-100 BPM, 普通话押韵 - 关于都市生活和奋斗

Chinese hip-hop with confident flow, urban style, Trap rhythm and 808 bass, mid-tempo 90-100 BPM, Mandarin rhyming - About urban life and struggle
```

### Mureka V8 中文优化要点 / Mureka V8 Chinese Optimization Tips

#### ✅ 情绪描述要具体 / Be Specific with Emotions
- ✅ 好的例子：深情、伤感、温馨、激昂、空灵、沧桑
- ❌ 避免模糊：好听、很好、不错

#### ✅ 人声特征要明确 / Define Vocal Characteristics
- ✅ 好的例子：温暖清澈、磁性低沉、空灵飘渺、高亢有力
- ❌ 避免简单：女声、男声

#### ✅ 乐器搭配要合理 / Match Instruments Appropriately
- 流行：钢琴、弦乐、吉他、鼓
- 古风：古筝、笛子、二胡、琵琶
- 摇滚：电吉他、贝斯、鼓
- 电子：合成器、808、鼓机

#### ✅ 语言特点要说明 / Specify Language Features
- 普通话：标准发音、清晰咬字
- 粤语：标准粤语、九声准确
- 方言：四川话、东北话等（如需要）

#### ✅ 提示词长度控制 / Keep Prompt Length in Check
- 最大长度：1024 字符
- 建议：200-500 字符为最佳范围

### 更多中文资源 / More Chinese Resources

查看以下章节获取更详细的中文音乐指导：
- **[Chinese Pop / 华语流行](#chinese-pop-华语流行)** - 华语流行音乐模板
- **[中文说唱 / Chinese Hip-Hop](#中文说唱-chinese-hip-hop)** - 中文说唱技巧
- **[古风国风 / Chinese Traditional](#古风-传统-chinese-traditional)** - 中国传统音乐
- **[中文歌词写作 / Chinese Lyrics](./references/lyrics.md#中文歌词写作-chinese-lyric-writing)** - 中文歌词写作技巧

---

## Quick Start / 快速入门

### Basic Prompt Structure / 基础提示词结构

Effective prompts follow this structure:
有效的提示词遵循以下结构：

```
[Genre] [Mood] [Tempo] [Key Instruments] [Vocal Style] - [Song Description]
[流派] [情绪] [速度] [关键乐器] [人声风格] - [歌曲描述]
```

Example / 示例：
```
Pop upbeat 120 BPM electric guitar drums female vocals - A catchy summer anthem about chasing dreams and overcoming obstacles
流行音乐 欢快 120 BPM 电吉他和鼓 女声 - 一首关于追逐梦想和克服障碍的朗朗上口的夏季颂歌
```

### Prompt Elements Explained / 提示词元素说明

| Element / 元素 | Description / 说明 | Examples / 示例 |
|----------------|-------------------|-----------------|
| **Genre / 流派** | Musical style / 音乐风格 | Pop, Rock, Jazz, Hip Hop, EDM, Folk, R&B, Classical |
| **Mood / 情绪** | Emotional tone / 情感基调 | Upbeat, Melancholic, Dark, Calm, Romantic, Intense |
| **Tempo / 速度** | Beats per minute / 每分钟节拍数 | 90 BPM, 120-128 BPM, Slow, Fast, Mid-tempo |
| **Instruments / 乐器** | Key instruments / 主要乐器 | Piano, guitar, drums, synthesizer, strings, saxophone |
| **Vocals / 人声** | Voice characteristics / 人声特征 | Male, female, harmonies, rap, falsetto, soulful |
| **Description / 描述** | Song concept / 歌曲概念 | Story, theme, narrative, emotion journey |

## Genre Templates / 流派模板

### Pop / 流行音乐

#### Bouncy Pop / 轻快流行 / 轻快流行
```
Pop upbeat 120-128 BPM synth bass catchy hooks bright female vocals - An infectious radio-ready pop song with feel-good vibes and singalong chorus

CN: 流行音乐 欢快 120-128 BPM 合成器贝斯 朗朗上口的旋律 明亮女声 - 一首具有感染力的电台就绪流行歌曲，感觉良好且有合唱部分
```

#### Sad Ballad / 悲伤抒情歌
```
Pop slow 70 BPM piano strings emotional female vocals - A heartbreaking ballad about lost love with soaring power ballad chorus

CN: 流行音乐 缓慢 70 BPM 钢琴和弦乐 情感丰富的女声 - 一首关于失去爱人的心碎抒情歌，有高亢的力量抒情副歌
```

#### Dance Pop / 舞曲流行
```
Pop EDM upbeat 128 BPM driving bass sawtooth synths energetic female vocals - High-energy dance pop with festival-ready drops and euphoric chorus

CN: 流行音乐 EDM 欢快 128 BPM 驱动性贝斯 锯齿合成器 充满活力的女声 - 高能量舞曲流行，适合音乐节的节奏和令人振奋的副歌
```

### Rock / 摇滚

#### Alternative Rock / 另类摇滚
```
Alternative rock mid-tempo 110 BPM distorted guitars dynamic male vocals - Gritty alt-rock with verses that build into explosive choruses

CN: 另类摇滚 中速 110 BPM 失真吉他 动态男声 - 粗砺的另类摇滚，主歌逐渐推进至爆炸性的副歌
```

#### Classic Rock / 经典摇滚
```
Classic rock 120 BPM electric guitar solos organ gritty male vocals - A vintage-inspired rock anthem with blistering guitar work and soulful swagger

CN: 经典摇滚 120 BPM 电吉他独奏 风琴 粗犷男声 - 一首复古风格的摇滚颂歌，有火辣的吉他演奏和灵魂般的自信
```

#### Soft Rock / 软摇滚
```
Rock acoustic ballad 80 BPM acoustic guitar gentle percussion soft male vocals - Intimate soft rock with heartfelt storytelling and melodic hooks

CN: 摇滚 原声抒情 80 BPM 原声吉他 轻柔打击乐 温柔男声 - 亲密的软摇滚，有真挚的叙事和旋律钩子
```

### Electronic / 电子音乐

#### House / 浩室音乐
```
House upbeat 124 BPM four-on-the-floor kick punchy bass filtered vocals - Deep house with warm analog synths and irresistible groove

CN: 浩室音乐 欢快 124 BPM 四拍踢鼓 有力贝斯 滤波人声 - 深度浩室音乐，有温暖的模拟合成器和无法抗拒的律动
```

#### Techno / 科技音乐
```
Techno dark 130 BPM repetitive percussive hypnotic arpeggiators - Driving techno with industrial textures and relentless energy

CN: 科技音乐 黑暗 130 BPM 重复打击乐 催眠琶音 - 驱动型科技音乐，有工业质感和无情能量
```

#### Lo-Fi / 低保真
```
Lo-Fi chill 85 BPM vinyl crackle mellow pianos dreamy - Relaxed lo-fi beats perfect for studying or late-night focus

CN: 低保真 轻松 85 BPM 唱片爆裂声 柔和钢琴 梦幻 - 放松的低保真节拍，适合学习或深夜专注
```

#### Dubstep / 回响低音
```
Dubstep aggressive 140 BPM wobble bass heavy drops - Intense dubstep with earth-shattering bass and dramatic build-ups

CN: 回响低音 激烈 140 BPM 摇摆贝斯 重型节奏 - 强烈的回响低音，有震撼人心的贝斯和戏剧性铺垫
```

### Hip Hop / Rap / 嘻哈/说唱

#### Trap / 陷阱音乐
```
Trap dark 140 BPM 808 bass hi-hat rolls aggressive rap flow - Hard-hitting trap with cinematic atmosphere and punchy delivery

CN: 陷阱音乐 黑暗 140 BPM 808贝斯 踩镲滚动 激烈说唱律动 - 重击型陷阱音乐，有电影氛围和有力的表达
```

#### Old School / 老派嘻哈
```
Hip-hop boom-bap 90 BPM sampled drums laid-back flow - Nostalgic 90s hip-hop with jazz samples and thoughtful lyricism

CN: 嘻哈 boom-bap 90 BPM 采样鼓 放松律动 - 怀旧的90年代嘻哈，有爵士采样和深思的歌词
```

#### Modern Rap / 现代说唱
```
Hip-hop modern 100 BPM minimal trap beats confident flow - Contemporary rap with sparse production and charismatic delivery

CN: 嘻哈 现代 100 BPM 极简陷阱节拍 自信律动 - 当代说唱，有简约制作和充满魅力的表达
```

#### 中文说唱 / Chinese Hip-Hop

##### Mureka V8 中文说唱优势 / Mureka V8 Chinese Rap Advantages

Mureka V8 对中文说唱有专门优化：
- ✅ **清晰的普通话发音**：咬字清晰，Flow 流畅
- ✅ **自然的节奏感**：理解中文节奏特点
- ✅ **丰富的情感表达**：传达歌词情绪
- ✅ **支持方言**：普通话、粤语、四川话等

##### 普通话说唱 / Mandarin Rap

**基础模板**：
```
中文说唱 [情绪] [速度] [节奏] [Flow 风格] - [主题描述]

Chinese hip-hop [mood] [tempo] [rhythm] [flow style] - [theme description]
```

**示例 Examples**：

1. **都市 Trap / Urban Trap**
```
中文说唱 自信 90-100 BPM Trap 节奏 808 贝斯 - 都市生活主题，自信 Flow，普通话押韵

Chinese hip-hop confident 90-100 BPM Trap rhythm 808 bass - Urban life theme, confident flow, Mandarin rhyming
```

2. **怀旧 Boom Bap / Nostalgic Boom Bap**
```
中文说唱 怀旧 85-95 BPM Boom Bap 节奏 采样鼓 - 90年代风格，怀旧主题，放松 Flow

Chinese hip-hop nostalgic 85-95 BPM Boom Bap rhythm sampled drums - 90s style, nostalgic theme, laid-back flow
```

3. **励志正能量 / Inspirational Positive**
```
中文说唱 充满力量 110-120 BPM 强节奏 激昂 Flow - 励志主题，追逐梦想，永不放弃

Chinese hip-hop empowering 110-120 BPM strong rhythm passionate flow - Inspirational theme, chasing dreams, never give up
```

4. **情感抒情 / Emotional Lyrical**
```
中文说唱 深情 80-90 BPM 柔和节奏 诉说 Flow - 情感主题，内心独白，真诚表达

Chinese hip-hop emotional 80-90 BPM soft rhythm storytelling flow - Emotional theme, inner monologue, sincere expression
```

##### 粤语说唱 / Cantonese Rap

**基础模板**：
```
粤语 Rap [情绪] [速度] [节奏] [Flow 风格] - [主题描述]

Cantonese rap [mood] [tempo] [rhythm] [flow style] - [theme description]
```

**示例 Examples**：

1. **港式 Trap / Hong Kong Trap**
```
粤语 Rap 激烈 140 BPM 快节奏 有力 Flow - 街头风格，粤语押韵，节奏感强

Cantonese rap intense 140 BPM fast rhythm powerful flow - Street style, Cantonese rhyming, strong rhythm
```

2. **粤语叙事 / Cantonese Storytelling**
```
粤语 Rap 沧桑 90-100 BPM 中速 节奏感 - 讲故事风格，香港街头，人生感悟

Cantonese rap weathered 90-100 BPM mid-tempo rhythmic - Storytelling style, Hong Kong streets, life reflections
```

##### 中文说唱 Flow 技巧 / Chinese Rap Flow Techniques

**1. 切分节奏 / Syncopated Rhythm**
```
提示词示例：
中文说唱 切分节奏 95 BPM - 节奏变化丰富，律动感强

Chinese hip-hop syncopated rhythm 95 BPM - Rich rhythm variations, strong groove
```

**2. 三连音 Flow / Triplet Flow**
```
提示词示例：
中文说唱 三连音 100 BPM 快速 Flow - 三连音技巧，快速连贯

Chinese hip-hop triplet flow 100 BPM fast flow - Triplet technique, fast and connected
```

**3. 旋律说唱 / Melodic Rap**
```
提示词示例：
中文说唱 旋律感 90 BPM 优美旋律 - 旋律说唱，歌唱感强

Chinese hip-hop melodic 90 BPM beautiful melody - Melodic rap, strong singing quality
```

##### 中文说唱押韵技巧 / Chinese Rhyming Techniques

**押韵方式 / Rhyme Schemes**：

1. **单押 / Single Rhyme**
```
示例：光 (guāng)、方 (fāng)、强 (qiáng)
提示词：中文说唱 单押 - 简单直接的押韵
```

2. **双押 / Double Rhyme**
```
示例：天空 (tiān kōng)、心中 (xīn zhōng)、风中 (fēng zhōng)
提示词：中文说唱 双押 - 两字押韵，更丰富
```

3. **多音节押韵 / Multi-syllable Rhyme**
```
示例：一直到天亮 (yī zhí dào tiān liàng)
      永远在心上 (yǒng yuǎn zài xīn shàng)
提示词：中文说唱 多音节押韵 - 复杂技巧，高级 Flow
```

4. **跳押 / Skip Rhyme**
```
示例：第一句末尾
      第三句末尾押韵
提示词：中文说唱 跳押 - 跨句押韵，技巧性强
```

##### 方言说唱 / Dialect Rap

**四川话 Rap / Sichuanese Rap**
```
四川话说唱 幽默 90 BPM - 川味幽默，风趣表达

Sichuanese rap humorous 90 BPM - Sichuan humor, witty expression
```

**东北话 Rap / Northeastern Dialect Rap**
```
东北话说唱 豪爽 100 BPM - 东北风格，直爽表达

Northeastern dialect rap bold 100 BPM - Northeastern style, straightforward expression
```

##### 中文说唱主题推荐 / Chinese Rap Theme Suggestions

| 主题 / Theme | 情绪 / Mood | 速度 / Tempo | 示例关键词 / Keywords |
|--------------|-------------|--------------|----------------------|
| **都市生活 / Urban Life** | 现实、观察 | 90-100 BPM | 都市、街头、奋斗、梦想 |
| **励志成长 / Inspirational Growth** | 积极、向上 | 110-120 BPM | 梦想、坚持、突破、成功 |
| **情感故事 / Emotional Stories** | 深情、真挚 | 80-90 BPM | 爱情、友情、亲情、回忆 |
| **社会观察 / Social Commentary** | 思考、批判 | 95-105 BPM | 社会、现实、反思、呼吁 |
| **怀旧回忆 / Nostalgic Memories** | 怀旧、感伤 | 85-95 BPM | 青春、过去、成长、变化 |
| **轻松快乐 / Lighthearted Fun** | 欢快、幽默 | 100-110 BPM | 快乐、幽默、轻松、派对 |

##### 中文说唱提示词检查清单 / Chinese Rap Prompt Checklist

在创建中文说唱提示词时，确保包含：

- [ ] **明确语言**：普通话、粤语或其他方言
- [ ] **Flow 风格**：自信、放松、激昂、旋律等
- [ ] **节奏类型**：Trap、Boom Bap、现代等
- [ ] **速度指示**：85-140 BPM，根据风格
- [ ] **主题描述**：都市、励志、情感等
- [ ] **押韵特点**：如需强调，可说明押韵方式
- [ ] **情绪氛围**：自信、怀旧、愤怒、欢快等

### Jazz / 爵士

#### Smooth Jazz / 平滑爵士
```
Smooth Jazz mellow 90 BPM saxophone Rhodes piano - Sophisticated smooth jazz with sultry melodies and relaxed grooves

CN: 平滑爵士 温和 90 BPM 萨克斯风 罗兹钢琴 - 精致的平滑爵士，有诱惑旋律和放松的律动
```

#### Bebop / 比波普
```
Jazz fast 170 BPM saxophone walking bass complex harmonies - Technical bebop with intricate improvisation and swing feel

CN: 爵士 快速 170 BPM 萨克斯风 行走贝斯 复杂和声 - 技术性比波普，有复杂即兴和摇摆感
```

#### Jazz Fusion / 爵士融合
```
Jazz fusion 120 BPM complex time signatures electric guitar synthesizer - Progressive fusion with virtuosic musicianship and adventurous compositions

CN: 爵士融合 120 BPM 复杂拍号 电吉他 合成器 - 前卫融合，有精湛演奏和冒险性作曲
```

### Classical / 古典

#### Orchestral / 管弦乐
```
Orchestral cinematic full orchestra sweeping strings brass fanfare - Epic orchestral piece with grandiose themes and dramatic dynamics

CN: 管弦乐 电影感 完整管弦乐团 壮阔弦乐 铜管号角 - 史诗管弦乐作品，有宏大主题和戏剧性动态
```

#### Piano Solo / 钢琴独奏
```
Classical piano solo expressive 80 BPM minor key - Intimate piano composition with emotional depth and classical elegance

CN: 古典 钢琴独奏 表现力丰富 80 BPM 小调 - 亲密的钢琴作品，有情感深度和古典优雅
```

#### String Quartet / 弦乐四重奏
```
Classical string quartet 90 BPM intricate harmonies - Sophisticated chamber music with rich textures and conversational interplay

CN: 古典 弦乐四重奏 90 BPM 错综和声 - 精致的室内乐，有丰富质感和对话性互动
```

### R&B / Soul / 节奏布鲁斯/灵魂乐

#### Contemporary R&B / 现代R&B
```
R&B smooth 95 BPM silky vocals lush harmonies - Modern R&B with sensual grooves and emotive delivery

CN: R&B 平滑 95 BPM 丝滑人声 丰富和声 - 现代R&B，有感性律动和情感表达
```

#### Soul / 灵魂乐
```
Soul 110 BPM brass section powerhouse vocals - Authentic soul music with gospel influences and passionate performance

CN: 灵魂乐 110 BPM 铜管乐部 强力人声 - 真实的灵魂音乐，有福音影响和激情演出
```

#### Neo-Soul / 新灵魂乐
```
Neo-soul laid-back 88 BPM jazz chords conscious lyrics - Intelligent neo-soul with sophisticated harmony and thoughtful storytelling

CN: 新灵魂乐 放松 88 BPM 爵士和弦 深刻歌词 - 聪明的新灵魂乐，有精致和声和深思叙事
```

### Country / 乡村音乐

#### Modern Country / 现代乡村
```
Country upbeat 120 BPM acoustic guitar banjo warm male vocals - Contemporary country with feel-good vibes and relatable storytelling

CN: 乡村音乐 欢快 120 BPM 原声吉他 班卓琴 温暖男声 - 当代乡村音乐，有感觉良好的氛围和可共鸣的叙事
```

#### Country Ballad / 乡村抒情歌
```
Country slow 75 BPM pedal steel guitar fiddle heartbreak - Traditional country ballad with classic themes and rich instrumentation

CN: 乡村音乐 缓慢 75 BPM 踏板钢吉他 小提琴 心碎 - 传统乡村抒情歌，有经典主题和丰富配器
```

#### Bluegrass / 蓝草音乐
```
Bluegrass 180 BPM banjo fiddle tight harmonies - Up-tempo bluegrass with virtuosic picking and authentic mountain sound

CN: 蓝草音乐 180 BPM 班卓琴 小提琴 紧密和声 - 快速蓝草音乐，有精湛拨奏和正宗山地声音
```

### Metal / 金属乐

#### Heavy Metal / 重金属
```
Heavy metal 140 BPM aggressive guitars pounding drums growled vocals - Intense metal with crushing riffs and powerful energy

CN: 重金属 140 BPM 激烈吉他 重击鼓 低吼人声 - 强烈金属音乐，有压倒性 riff 和强大能量
```

#### Metalcore / 金属核
```
Metalcore 150 BPM breakdowns clean/screamed vocals - Modern metalcore with dynamic shifts and emotional intensity

CN: 金属核 150 BPM 节奏变换 清唱/嘶吼 - 现代金属核，有动态变化和情感强度
```

#### Thrash Metal / 激流金属
```
Thrash metal 180 BPM rapid-fire riffs double-bass drums aggressive vocals - Ferocious thrash with lightning-speed playing

CN: 激流金属 180 BPM 急速 riff 双低音鼓 激烈人声 - 狂暴激流金属，有闪电般速度的演奏
```

### Folk / 民谣

#### Acoustic Folk / 原声民谣
```
Folk acoustic 80 BPM guitar harmonica storytelling - Traditional folk with simple arrangements and meaningful lyrics

CN: 民谣 原声 80 BPM 吉他 口琴 叙事 - 传统民谣，有简单编排和有意义歌词
```

#### Indie Folk / 独立民谣
```
Folk indie 95 BPM gentle guitar atmospheric textures - Contemporary indie folk with dreamy production and introspective themes

CN: 民谣 独立 95 BPM 温柔吉他 氛围质感 - 当代独立民谣，有梦幻制作和内省主题
```

### Reggae / 雷鬼

#### Reggae / 雷鬼
```
Reggae laid-back 75 BPM offbeat guitar bass-heavy groove - Authentic reggae with positive vibes and skanking rhythm

CN: 雷鬼 放松 75 BPM 反拍吉他 重贝斯律动 - 真实雷鬼，有积极氛围和 skanking 节奏
```

#### Dancehall / 舞厅雷鬼
```
Dancehall upbeat 100 BPM heavy bass trap influences - Modern dancehall with infectious energy and danceable beats

CN: 舞厅雷鬼 欢快 100 BPM 重贝斯 陷阱影响 - 现代舞厅雷鬼，有感染能量和可舞节拍
```

### Ambient / 氛围音乐

#### Ambient / 氛围
```
Ambient 60-80 BPM minimal drones atmospheric pads - Ethereal ambient music with slow evolution and meditative qualities

CN: 氛围音乐 60-80 BPM 极简长音 氛围垫音 - 空灵氛围音乐，有缓慢进化和冥想品质
```

#### Drone / 长音音乐
```
Drone slow 50 BPM sustained notes deep textures - Immersive drone music with layered frequencies and hypnotic repetition

CN: 长音音乐 缓慢 50 BPM 延续音符 深度质感 - 沉浸式长音音乐，有层叠频率和催眠重复
```

### World / Traditional / 世界/传统音乐

#### Latin Pop / 拉丁流行
```
Latin pop 100 BPM brass percussion syncopated rhythms - Energetic Latin pop with infectious dance beats and passionate vocals

CN: 拉丁流行 100 BPM 铜管 打乐 切分节奏 - 充满活力的拉丁流行，有感染舞曲节拍和激情人声
```

#### K-Pop / 韩国流行
```
K-Pop upbeat 120-130 BPM electronic elements catchy hooks idol vocals - Modern K-pop with dynamic production and energetic performances

CN: K-Pop 欢快 120-130 BPM 电子元素 朗朗上口的钩子 偶像人声 - 现代 K-Pop，有动态制作和充满活力的演出
```

#### Chinese Pop / 华语流行

##### Mureka V8 特别优化 / Mureka V8 Special Optimization

Mureka V8 对华语流行歌曲表现优异，**人声真实度达 70%**，特别适合普通话和粤语。

**关键优势**：
- ✅ MusiCoT 技术优化中文声调处理
- ✅ 自然流畅的旋律线
- ✅ 清晰准确的发音
- ✅ 丰富的情感表达

##### 普通话提示词模板 / Mandarin Prompt Templates

**基础模板**：
```
华语流行 [情绪] [速度] [乐器] [人声风格] - [歌曲描述]

Mandarin pop [mood] [tempo] [instruments] [vocal style] - [song description]
```

**示例 Examples**：

1. **深情情歌 / Emotional Ballad**
```
华语流行 深情 90-100 BPM 钢琴弦乐 温暖女声 - 关于思念和爱情的感人情歌，旋律优美动人

Mandarin pop emotional 90-100 BPM piano strings warm female vocals - A heartfelt love song about longing and romance with beautiful melodies
```

2. **青春励志 / Youthful Inspirational**
```
华语流行 充满希望 120-130 BPM 吉他鼓 清新人声 - 关于追逐梦想的励志歌曲，青春阳光

Mandarin pop hopeful 120-130 BPM guitar drums fresh vocals - Inspirational song about chasing dreams, youthful and sunny
```

3. **都市伤感 / Urban Melancholic**
```
华语流行 伤感 80-90 BPM 电子音色 沧桑男声 - 关于都市孤独和失落的伤感歌曲

Mandarin pop melancholic 80-90 BPM electronic textures weathered male vocals - Sad song about urban loneliness and loss
```

##### 粤语提示词模板 / Cantonese Prompt Templates

**基础模板**：
```
粤语流行 [情绪] [速度] [乐器] [人声风格] - [歌曲描述]

Cantonese pop [mood] [tempo] [instruments] [vocal style] - [song description]
```

**示例 Examples**：

1. **经典港式抒情 / Classic Hong Kong Ballad**
```
粤语流行 怀旧 75-85 BPM 钢琴木吉他 沧桑男声 - 经典港式抒情歌，关于时光流逝和人生感悟

Cantonese pop nostalgic 75-85 BPM piano acoustic guitar weathered male vocals - Classic Hong Kong style ballad about the passage of time and life reflections
```

2. **港式轻快 / Hong Kong Upbeat**
```
粤语流行 欢快 110-120 BPM 电子乐 活力女声 - 动感港式流行，都市节拍

Cantonese pop upbeat 110-120 BPM electronic energetic female vocals - Upbeat Hong Kong style pop with urban rhythm
```

##### 子流派指南 / Subgenre Guide

**Mandopop / 华语流行（现代）**
- 台湾风格：清新、自然、吉他主导（如：周杰伦、五月天）
- 大陆风格：电子化、强劲节拍（如：李荣浩、薛之谦）
- 马来风格：抒情、细腻、多语言（如：光良、品冠）

**Cantopop / 粤语流行**
- 经典抒情：深情、怀旧、港式韵味（如：张学友、陈奕迅）
- 现代流行：节奏明快、电子元素（如：邓紫棋、容祖儿）
- 粤语 R&B：流畅、现代感（如：方大同）

**台语歌 / Taiwanese Pop**
- 闽南语歌曲：乡土、情感丰富
- 台语摇滚：豪爽、直接、有力

##### 中文关键词库 / Chinese Keyword Library

**情绪关键词 / Mood Keywords**：
- 积极：欢快、温馨、励志、甜蜜、充满希望
- 消极：伤感、忧郁、孤独、痛苦、怀旧
- 中性：空灵、平静、淡雅、深沉

**人声关键词 / Vocal Keywords**：
- 女声：温暖清澈、空灵飘渺、高亢有力、甜美可爱
- 男声：温暖磁性、沧桑成熟、青春阳光、激昂澎湃

**乐器关键词 / Instrument Keywords**：
- 流行：钢琴、弦乐、吉他、鼓、电子合成
- 古风：古筝、笛子、二胡、琵琶、中国鼓
- 摇滚：电吉他、贝斯、鼓、键盘

#### J-Pop / 日本流行
```
J-Pop upbeat 120-140 BPM synthesizer catchy hooks high energy - Japanese pop with cheerful vibes and memorable melodies

CN: J-Pop 欢快 120-140 BPM 合成器 朗朗上口的钩子 高能量 - 日本流行，有欢快氛围和难忘旋律
```

#### African Traditional / 非洲传统
```
African traditional 100-120 BPM djembe percussion call and response - Authentic African rhythms with traditional instruments and communal energy

CN: 非洲传统 100-120 BPM 非洲鼓 打乐 呼应 - 真实非洲节奏，有传统乐器和社区能量
```

#### Indian Classical / 印度古典
```
Indian classical 80-100 BPM sitar tabla ragas - Traditional Indian music with complex rhythmic patterns and spiritual depth

CN: 印度古典 80-100 BPM 西塔鼓 塔布拉鼓 拉格 - 传统印度音乐，有复杂节奏模式和精神深度
```

## Mood & Atmosphere / 情绪与氛围

### Positive/Uplifting / 积极/振奋 / 积极/振奋

#### Joyful / 喜悦
- Joyful, euphoric, triumphant, radiant, blissful, exuberant
- 喜悦、狂喜、胜利、光辉、极乐、兴奋

#### Uplifting / 振奋
- Uplifting, inspiring, hopeful, optimistic, bright, sunny
- 振奋、鼓舞、充满希望、乐观、明亮、阳光

#### Celebratory / 庆祝
- Celebratory, jubilant, enthusiastic, vibrant, energetic
- 庆祝、狂欢、热情、充满活力、充满能量

### Melancholic/Sad / 忧郁/悲伤 / 忧郁/悲伤

#### Melancholic / 忧郁
- Melancholic, wistful, nostalgic, longing, somber
- 忧郁、渴望、怀旧、思念、阴郁

#### Heartbreaking / 心碎
- Heartbreaking, mournful, grief-stricken, sorrowful
- 心碎、哀悼、悲痛、悲伤

#### Reflective / 反思
- Bittersweet, melancholy, reflective, pensive
- 苦乐参半、忧郁、反思、沉思

### Dark/Mysterious / 黑暗/神秘 / 黑暗/神秘

#### Dark / 黑暗
- Dark, ominous, brooding, menacing, sinister
- 黑暗、不祥、阴沉、威胁、险恶

#### Mysterious / 神秘
- Mysterious, enigmatic, cryptic, shadowy, noir
- 神秘、谜一般、晦涩、阴影、黑色电影

#### Haunting / 挥之不去
- Haunting, eerie, spectral, otherworldly
- 挥之不去、怪异、幽灵、超脱尘世

### Intense/Dramatic / 强烈/戏剧性 / 强烈/戏剧性

#### Intense / 强烈
- Intense, dramatic, powerful, epic, monumental
- 强烈、戏剧性、强大、史诗、宏伟

#### Fierce / 凶猛
- Fierce, aggressive, relentless, driving
- 凶猛、激进、无情、驱动

#### Explosive / 爆发
- Explosive, thunderous, commanding, dominant
- 爆发、雷鸣、指挥、主导

### Calm/Peaceful / 平静/安宁 / 平静/安宁

#### Calm / 平静
- Calm, peaceful, serene, tranquil, meditative
- 平静、安宁、宁静、恬静、冥想

#### Soothing / 安慰
- Soothing, gentle, tender, warm, comforting
- 安慰、温柔、柔软、温暖、舒适

#### Ethereal / 空灵
- Ambient, ethereal, dreamy, airy, floaty
- 氛围、空灵、梦幻、轻盈、漂浮

### Romantic/Love / 浪漫/爱情 / 浪漫/爱情

#### Romantic / 浪漫
- Romantic, passionate, intimate, sensual, loving
- 浪漫、热情、亲密、感性、充满爱

#### Yearning / 渴望
- Yearning, devoted, tender, affectionate
- 渴望、奉献、温柔、深情

#### Sweet / 甜美
- Sweet, dreamy, affectionate, heartfelt
- 甜美、梦幻、深情、真心

### Other Moods / 其他情绪

#### Energetic / 充满活力
- Dynamic, driving, propulsive, pumping
- 动态、驱动、推进、澎湃

#### Mystical / 神秘莫测
- Mystical, magical, spiritual, transcendental
- 神秘莫测、魔法、精神、超脱

#### Playful / 俏皮
- Playful, whimsical, quirky, fun, lighthearted
- 俏皮、异想天开、古怪、有趣、轻松

## Instrumentation Guidance / 乐器指导

### Key Instruments by Genre / 各流派的关键乐器

| Genre / 流派 | Key Instruments / 关键乐器 |
|--------------|---------------------------|
| **Pop / 流行** | Synth bass, electric guitar, keyboards, drum machines, vocals / 合成器贝斯、电吉他、键盘、鼓机、人声 |
| **Rock / 摇滚** | Electric guitar, bass guitar, acoustic guitar, drum kit, vocals / 电吉他、贝斯吉他、原声吉他、鼓套件、人声 |
| **Electronic / 电子** | Synthesizers, drum machines, samplers, sequencers, pads / 合成器、鼓机、采样器、音序器、垫音 |
| **Hip Hop / 嘻哈** | 808 bass, drum machines, samplers, turntables / 808贝斯、鼓机、采样器、唱机 |
| **Jazz / 爵士** | Saxophone, trumpet, piano, upright bass, drums / 萨克斯、小号、钢琴、低音提琴、鼓 |
| **Classical / 古典** | Strings, brass, woodwinds, percussion, piano / 弦乐、铜管、木管、打击乐、钢琴 |
| **Country / 乡村** | Acoustic guitar, banjo, fiddle, pedal steel, mandolin / 原声吉他、班卓琴、小提琴、踏板钢吉他、曼陀林 |
| **Metal / 金属** | Distorted guitars, double-bass drums, aggressive vocals / 失真吉他、双低音鼓、激烈人声 |
| **Reggae / 雷鬼** | Bass guitar, rhythm guitar, organ, percussion, drums / 贝斯吉他、节奏吉他、风琴、打击乐、鼓 |
| **World / 世界** | Traditional instruments: sitar, koto, erhu, djembe, tabla, bagpipes / 传统乐器：西塔琴、古筝、二胡、非洲鼓、塔布拉鼓、风笛 |

### Production Techniques / 制作技巧

#### Vintage / 复古风格
- "vinyl crackle," "tape saturation," "warm analog," "lo-fi," "retro," "old-school"
- "唱片爆裂声"、"磁带饱和"、"温暖模拟"、"低保真"、"复古"、"老派"

#### Modern / 现代风格
- "crisp production," "polished," "radio-ready," "contemporary," "clean," "sleek"
- "清晰制作"、"精致"、"电台就绪"、"当代"、"干净"、"时尚"

#### Minimal / 极简风格
- "sparse arrangement," "stripped back," "simple," "understated," "ambient"
- "稀疏编排"、"简化"、"简单"、"低调"、"氛围"

#### Layered / 层叠风格
- "rich textures," "lush orchestration," "dense," "complex," "multi-layered"
- "丰富质感"、"华丽配器"、"密集"、"复杂"、"多层"

### Sound Design / 声音设计

#### Synthesizer Types / 合成器类型
- Analog / 模拟: "warm analog synth," "vintage Moog"
- Digital / 数字: "crisp digital synth," "FM synthesis"
- Hybrid / 混合: "modern hybrid synth," "wavetable"
- Granular / 颗粒: "granular synthesis," "textural pads"

#### Effects / 效果
- "reverb tail," "echo delay," "phaser," "flanger," "chorus"
- "spacey," "underwater," "metallic," "shimmering," "hazy"
- "混响尾音"、"回声延迟"、"移相"、"镶边"、"合唱"
- "空间感"、"水下"、"金属感"、"闪烁"、"朦胧"

## Vocal Specifications / 人声规格

### Vocal Styles / 人声风格

#### Male Voices / 男声
- Baritone: Rich, warm mid-range / 中音，温暖中音域
- Tenor: Bright, higher range / 亮音，较高音域
- Bass: Deep, low frequencies / 低音，低频率
- Falsetto: High, breathy / 高音，气声
- Growl: Aggressive, distorted / 低吼，失真
- Rap flow: Rhythmic delivery / 节奏性表达

#### Female Voices / 女声
- Soprano: High range, bright / 高音域，亮音
- Alto: Lower range, rich / 较低音域，丰富
- Mezzo-soprano: Middle range / 中音域
- Breathy: Soft, intimate / 柔和，亲密
- Powerful: Strong projection / 强投射
- Soulful: Emotional depth / 情感深度

#### Harmonies / 和声
- "2-part harmonies" / "二部和声"
- "3-part harmonies" / "三部和声"
- "stacked vocals" / "堆叠人声"
- "call and response" / "呼应"
- "background vocals" / "背景人声"
- "choir" / "合唱团"

#### Vocal Effects / 人声效果
- Reverb / 混响
- Delay / 延迟
- Chorus / 合唱效果
- Vocoder / 声码器
- Autotune (subtle) / 自动调音（微弱）

### Vocal Delivery / 人声表达

#### Intimate / 亲密
- Whisper-quiet, close-mic, breathy, personal
- 低语般，近距麦克风，气声，个人化

#### Powerful / 强力
- Belted, soaring, anthemic, commanding
- 爆发式，高亢，颂歌式，指挥式

#### Casual / 随意
- Conversational, laid-back, relaxed, natural
- 对话式，放松，轻松，自然

#### Aggressive / 激进
- Gritty, intense, passionate, forceful
- 粗砺，强烈，激情，有力

#### Emotional / 情感
- Vulnerable, tearful, anguished, joyful
- 脆弱，含泪，痛苦，喜悦

### Language Support / 语言支持

When working with different languages in AI music:
在 AI 音乐中使用不同语言时：

#### English / 英语
- Standard pronunciation, clear diction
- 标准发音，清晰吐字

#### Chinese / 中文
- Mandarin (Putonghua): Standard Chinese pronunciation
  - 普通话：标准中文发音
- Cantonese: Southern Chinese dialect
  - 粤语：南方汉语方言
- Regional accents: Beijing, Shanghai, Sichuan
  - 地方口音：北京、上海、四川

#### Japanese / 日语
- Standard Tokyo accent
- 标准东京口音

#### Korean / 韩语
- Standard Seoul pronunciation
- 标准首尔发音

#### Spanish / 西班牙语
- Latin American vs. European Spanish
- 拉美 vs. 欧洲西班牙语

#### Tips for Language Prompts / 语言提示词技巧
```
Female Mandarin vocals with clear pronunciation / 中文女声，发音清晰
Male rap in Spanish with confident delivery / 西班牙语男声说唱，自信表达
Bilingual lyrics with English and Chinese verses / 双语歌词，英文和中文主歌
```

## Lyric Writing Tips / 歌词写作技巧

### Structure Patterns / 结构模式

#### Verse-Chorus / 主歌-副歌
```
Verse → Pre-Chorus → Chorus → Verse → Chorus → Bridge → Chorus
主歌 → 预副歌 → 副歌 → 主歌 → 副歌 → 桥段 → 副歌
```

#### AABA / 古典结构
```
A section → A section → B section → A section (classic jazz/pop)
A段 → A段 → B段 → A段（经典爵士/流行）
```

#### Rap Flow / 说唱律动
```
16-bar verses, 8-bar hooks, layered ad-libs
16小节主歌，8小节钩子，层叠即兴
```

#### Progressive / 渐进结构
```
Intro → Build-up → Drop → Breakdown → Build-up → Drop → Outro
前奏 → 铺垫 → 节奏 → 间奏 → 铺垫 → 节奏 → 结尾
```

### Lyrical Themes / 歌词主题

#### Personal / 个人
- Relationships, growth, memories, dreams, struggles
- 人际关系、成长、记忆、梦想、挣扎

#### Universal / 普世
- Love, freedom, hope, time, nature, humanity
- 爱情、自由、希望、时间、自然、人性

#### Narrative / 叙事
- Stories, characters, adventures, journeys
- 故事、角色、冒险、旅程

#### Abstract / 抽象
- Feelings, concepts, philosophy, imagination
- 感受、概念、哲学、想象

### Writing Guidelines / 写作指南

#### 1. Be Specific / 具体化
- Instead of "I'm sad," describe the feeling with imagery
- 不要只说"我很伤心"，用意象描述这种感觉

#### 2. Show, Don't Tell / 展示而非讲述
- Use concrete details and sensory language
- 使用具体细节和感官语言

#### 3. Use Rhyme Schemes / 使用押韵模式
- AABB, ABAB, or free verse depending on genre
- AABB、ABAB 或自由诗，视流派而定

#### 4. Match the Mood / 匹配情绪
- Align lyrics with the musical emotion
- 歌词要与音乐情感一致

#### 5. Keep it Conversational / 保持对话感
- Write like people actually speak, not poetry
- 像实际说话那样写，而不是像写诗

### Lyric Writing Examples / 歌词写作示例

#### English Example / 英文示例
```
Verse:
Neon lights reflect in rainy streets tonight
I'm chasing shadows in the fading light
Every heartbeat echoes your name
Lost in this memory game

Chorus:
Don't let go of what we had
Even though it makes me sad
I'll hold on through the night
Until the morning light
```

#### Chinese Example / 中文示例
```
主歌：
霓虹灯光倒映在雨夜街头
我在渐暗的光线中追逐你的影子
每一次心跳都在呼喊你的名字
迷失在这场记忆的游戏中

副歌：
别放手，别遗忘我们的过去
虽然这让我心痛不已
我会彻夜坚持
直到晨光初现
```

### Bilingual Lyrics / 双语歌词

#### Mixed Language / 混合语言
```
English-Chinese fusion / 英中融合
Korean-English mix / 韩英混合
Spanish-English Spanglish / 西英混合
```

#### Translation Tips / 翻译技巧
- Focus on meaning, not literal translation
- 专注意义而非字面翻译
- Consider cultural nuances
- 考虑文化细微差别
- Adapt to rhythm and melody
- 适应节奏和旋律

## Advanced Techniques / 高级技巧

### Specific References / 具体参考

#### Artist Style References / 艺术家风格参考
```
"Inspired by [Artist]'s style from [Era] - [Specific elements to borrow]"
"受 [艺术家][年代] 风格启发 - [借鉴的具体元素]"

Examples / 示例：

- "In the style of 80s Prince - funky bass, falsetto vocals, Minneapolis sound"
  CN: "80年代Prince风格 - 放克贝斯，假声人声，明尼阿波利斯之声"
  
- "Channeling Radiohead - atmospheric guitars, innovative production, emotional depth"
  CN: "借鉴Radiohead - 氛围吉他，创新制作，情感深度"
  
- "Beatles-inspired - melodic bass lines, creative harmonies, classic songwriting"
  CN: "披头士风格 - 旋律性贝斯线，创意和声，经典创作"
  
- "Taylor Swift style - storytelling, catchy hooks, relatable lyrics"
  CN: "Taylor Swift 风格 - 叙事，朗朗上口的钩子，可共鸣的歌词"
  
- "Jay-Z flow - confident delivery, wordplay, sophisticated rhymes"
  CN: "Jay-Z 律动 - 自信表达，文字游戏，精致押韵"
```

#### Era References / 年代参考
```
1960s: Psychedelic rock, folk revival, soul explosion
1970s: Classic rock, disco, punk
1980s: Synth-pop, new wave, hair metal
1990s: Grunge, hip-hop golden era, boy bands
2000s: Pop-punk, R&B revival, indie explosion
2010s: EDM boom, trap rise, indie folk
2020s: Lo-fi revival, bedroom pop, genre fusion

CN:
1960年代：迷幻摇滚、民谣复兴、灵魂乐爆发
1970年代：经典摇滚、迪斯科、朋克
1980年代：合成器流行、新浪潮、长发金属
1990年代：垃圾摇滚、嘻哈黄金时代、男孩乐队
2000年代：流行朋克、R&B复兴、独立音乐爆发
2010年代：EDM繁荣、陷阱音乐崛起、独立民谣
2020年代：低保真复兴、卧室流行、流派融合
```

### Musical Elements / 音乐元素

#### Song Structure / 歌曲结构
```
[Song structure] [Key signature] [Time signature] [Specific chord progression]

Examples / 示例：

- "Verse-chorus-bridge format, C major, 4/4 time with I-V-vi-IV progression"
  CN: "主歌-副歌-桥段结构，C大调，4/4拍，I-V-vi-IV和弦进行"
  
- "Extended instrumental sections, E minor, 6/8 time for waltz feel"
  CN: "延伸器乐部分，E小调，6/8拍，华尔兹感觉"
  
- "Complex time signature changes, modal interchange, jazz chord extensions"
  CN: "复杂拍号变化，调式互换，爵士和弦扩展"
```

#### Chord Progressions / 和弦进行

#### Common Progressions / 常用进行
- **I-V-vi-IV (Pop standard) / 流行标准**
  - C Major: C - G - Am - F
  - CN: C大调：C - G - Am - F
  
- **ii-V-I (Jazz standard) / 爵士标准**
  - C Major: Dm7 - G7 - CMaj7
  - CN: C大调：Dm7 - G7 - CMaj7
  
- **i-VI-III-VII (Dark/Minor) / 黑暗/小调**
  - A Minor: Am - F - C - G
  - CN: A小调：Am - F - C - G
  
- **I-IV-V (Blues/Rock) / 布鲁斯/摇滚**
  - E Major: E - A - B7
  - CN: E大调：E - A - B7

#### Modal Suggestions / 调式建议
- **Major / 大调**: Bright, happy / 明亮，快乐
- **Minor / 小调**: Sad, serious / 悲伤，严肃
- **Dorian / 多里安**: Jazzy, hopeful / 爵士，充满希望
- **Mixolydian / 混合利底亚**: Bluesy, folk / 布鲁斯，民谣
- **Lydian / 利底亚**: Dreamy, fantasy / 梦幻，幻想

### Technical Specifications / 技术规格

#### Tempo / 速度
- Specify BPM range: "120-130 BPM"
- 指定 BPM 范围："120-130 BPM"
- Descriptive: "Slow," "Mid-tempo," "Fast," "Driving"
- 描述性："缓慢"、"中速"、"快速"、"驱动性"

#### Key / 调性
- "D minor" / "D小调"
- "C major" / "C大调"
- "E flat major" / "降E大调"

#### Time Signature / 拍号
- "4/4" - Common time / 常见拍号
- "3/4" - Waltz feel / 华尔兹感觉
- "6/8" - Folk feel / 民谣感觉
- "Complex time signatures" / "复杂拍号"

#### Length / 长度
- "2:30-3:00 duration" / "2:30-3:00时长"
- "Extended mix 5:00" / "扩展混音 5:00"
- "Short verse 1:00" / "短主歌 1:00"

## Platform-Specific Tips / 平台特定提示

### Suno / Suno AI Music

#### Best Practices / 最佳实践
```
- Keep prompts concise and descriptive
  - 保持提示词简洁且描述性强
  
- Use genre + mood + description format
  - 使用 流派 + 情绪 + 描述 格式
  
- Specify vocal style clearly
  - 清晰指定人声风格
  
- Suno v3 excels at: pop, rock, electronic genres
  - Suno v3 擅长：流行、摇滚、电子流派
```

#### Suno Prompt Examples / Suno 提示词示例
```
1. Pop song:
"Pop upbeat 125 BPM synth bass catchy hooks bright female vocals - Summer love song about meeting someone special at the beach"

CN: "流行音乐 欢快 125 BPM 合成器贝斯 朗朗上口的钩子 明亮女声 - 关于在海滩遇见特别的人的夏日情歌"

2. Rock anthem:
"Alternative rock mid-tempo 115 BPM distorted guitars powerful male vocals - Anthem about overcoming adversity and rising stronger"

CN: "另类摇滚 中速 115 BPM 失真吉他 强力男声 - 关于克服逆境变得更强大的颂歌"
```

### Udio / Udio AI Music

#### Best Practices / 最佳实践
```
- Udio handles complex musical arrangements well
  - Udio 能很好地处理复杂音乐编排
  
- Good for: jazz, classical, orchestral pieces
  - 适合：爵士、古典、管弦乐作品
  
- Use detailed instrumentation descriptions
  - 使用详细的乐器描述
  
- Specify production quality
  - 指定制作质量
```

#### Udio Prompt Examples / Udio 提示词示例
```
1. Jazz piece:
"Jazz fusion 125 BPM electric piano complex time signatures virtuosic improvisation - Progressive jazz fusion with intricate rhythms"

CN: "爵士融合 125 BPM 电钢琴 复杂拍号 精湛即兴 - 前卫爵士融合，有复杂节奏"

2. Orchestral:
"Orchestral cinematic full orchestra sweeping strings brass fanfare - Epic orchestral piece with dramatic crescendos"

CN: "管弦乐 电影感 完整管弦乐团 壮阔弦乐 铜管号角 - 史诗管弦乐，有戏剧性渐强"
```

### Mureka V8 / Mureka V8

#### New Features / 新特性

**V8 核心升级 / V8 Core Upgrades:**

```
- 🎯 Enhanced Multilingual Support (20+ Languages)
  - 增强多语言支持（20+ 种语言）
  - Native pronunciation for Chinese, Japanese, Korean, Spanish, French, German, Italian
  - 中文、日文、韩文、西班牙文、法文、德文、意大利文原生发音
  
- 🎤 Advanced Vocal Engine (V8 Voice)
  - 高级人声引擎（V8 Voice）
  - Improved breath control and natural phrasing
  - 改进气息控制和自然乐句表达
  - Better diction for complex lyrics
  - 复杂歌词的更佳发音
  
- 🎨 Genre Fusion System
  - 流派融合系统
  - Seamless blending of 3+ genres
  - 无缝融合 3+ 种流派
  - Intelligent cross-cultural integration
  - 智能跨文化融合
  
- 🎭 Mood Mapping 2.0
  - 情绪映射 2.0
  - Micro-emotion control (subtle emotional shifts)
  - 微表情控制（细微情感变化）
  - Emotional arc tracking throughout song
  - 整首歌的情感弧线跟踪
  
- 🎹 Production Quality Engine
  - 制作质量引擎
  - Studio-grade mixing and mastering
  - 录音室级混音和母带处理
  - Professional audio clarity and depth
  - 专业音频清晰度和深度
  
- 🌍 Cultural Intelligence
  - 文化智能
  - Context-aware musical traditions
  - 语境感知音乐传统
  - Respectful cultural fusion
  - 尊重的文化融合
  
- 📝 Lyric Enhancement
  - 歌词增强
  - Improved rhyme schemes
  - 改进的押韵模式
  - Better word-melody alignment
  - 更好的词-旋律对齐
  
- ⚡ Real-time Iteration
  - 实时迭代
  - Quick prompt refinement
  - 快速提示词优化
  - Version history for prompts
  - 提示词版本历史
```

#### Mureka V8 Prompt Structure / Mureka V8 提示词结构

**Standard Structure / 标准结构:**

```
[Language] [Genre] [Sub-Genre] [Mood] [Tempo] [Key] [Time Signature] [Instruments] [Vocal Style] [Production Style] [Cultural Context] - [Song Description]

示例 / Example:

EN: "Chinese Pop sentimental ballad 95 BPM C Major 4/4 piano strings erhu emotional female vocals lush production contemporary urban - Modern Chinese love ballad about longing and reunion with heartfelt lyrics, blending traditional erhu with modern orchestral arrangements"

CN: "中文 流行音乐 抒情歌 95 BPM C大调 4/4拍 钢琴 弦乐 二胡 情感女声 华丽制作 现代都市 - 现代中文爱情抒情歌，关于思念和重逢，有真挚歌词，融合传统二胡与现代管弦乐编排"
```

**Advanced Structure / 高级结构（V8 专属）:**

```
[Language] [Primary Genre] + [Secondary Genre] + [Tertiary Genre] [Mood Arc] [Tempo Range] [Key] [Instruments] [Vocal Style] [Production Tags] [Cultural Elements] [Technical Specs] - [Detailed Description]

示例 / Example:

EN: "Chinese Pop + Electronic + Ambient emotional-reflective-hopeful 88-95 BPM A Minor piano synthesizer guzheng ethereal female vocals cinematic spacious production Chinese pentatonic scale 5/4 time signature - An introspective Chinese electronic track exploring themes of personal growth and transformation, starting melancholic and gradually becoming hopeful, with layered textures and dynamic emotional arc"

CN: "中文 流行音乐 + 电子 + 氛围 情感-反思-充满希望 88-95 BPM A小调 钢琴 合成器 古筝 空灵女声 电影感 宽敞制作 中国五声音阶 5/4拍 - 一首内省的中文电子乐，探索个人成长和转变的主题，从忧郁开始逐渐变得充满希望，有层次质感和动态情感弧线"
```

#### Mureka V8 Best Practices / Mureka V8 最佳实践

**1. Language Specification / 语言明确指定**

```
✅ Good / 好:
"Mandarin vocals with standard Beijing accent and clear pronunciation"
"中文人声，标准北京口音，发音清晰"

✅ Bilingual / 双语:
"Mandarin-Chinese primary with English chorus sections, seamless transition between languages"
"以普通话为主，英文副歌部分，语言间无缝过渡"

✅ Dialect / 方言:
"Cantonese vocals with authentic Hong Kong pronunciation and local slang"
"粤语人声，正宗香港发音和本地俚语"

✅ Multi-Language / 多语言:
"Trilingual track: Japanese verse, Mandarin pre-chorus, English chorus"
"三语言歌曲：日文主歌，普通话预副歌，英文副歌"
```

**2. Cultural Context Application / 文化背景应用**

```
✅ Traditional Fusion / 传统融合:
"Chinese pentatonic scale with modern electronic production"
"中国五声音阶与现代电子制作"

✅ Regional Style / 地域风格:
"Shanghai jazz style with 1930s influence and contemporary arrangements"
"上海爵士风格，1930年代影响和现代编排"

✅ Cultural References / 文化引用:
"Japanese enka style ballad with Western orchestration, blending Showa-era aesthetics with modern production"
"日本演歌风格抒情歌，西方管弦乐编排，融合昭和时代美学与现代制作"

✅ Festival/Seasonal / 节日/季节:
"Chinese New Year celebration song with traditional instruments and modern upbeat production"
"春节庆祝歌曲，传统乐器与现代欢快制作"
```

**3. Mood Mapping 2.0 / 情绪映射 2.0**

```
✅ Single Emotion / 单一情绪:
"Melancholic and reflective throughout"
"整首歌忧郁且反思"

✅ Emotional Arc / 情感弧线:
"Melancholic verses → hopeful chorus → triumphant bridge"
"忧郁主歌 → 充满希望副歌 → 胜利桥段"

✅ Micro-Emotions / 微表情:
"Starts sad with subtle anxiety, gradually builds to determined, ends with peaceful resolution"
"开始悲伤带微妙焦虑，逐渐建立决心，以平静解决结束"

✅ Complex Emotion / 复杂情绪:
"Bittersweet nostalgia with underlying optimism, joyous but with tinge of longing"
"苦乐参半的怀旧，底色乐观，快乐但带有一丝渴望"
```

**4. Genre Fusion Mastery / 流派融合精通**

```
✅ Fusion Syntax / 融合语法:
"Pop dominant with jazz influence, rock energy in chorus, ambient textures"
"流行主导，爵士影响，副歌摇滚能量，氛围质感"

✅ Cross-Cultural Fusion / 跨文化融合:
"K-Pop meets Latin trap, Korean vocals with reggaeton rhythm"
"K-Pop 遇上拉丁陷阱，韩语人声配雷鬼顿节奏"

✅ Era Fusion / 时代融合:
"1970s disco vibes with 2020s production aesthetics, retro-futuristic"
"1970年代迪斯科氛围 + 2020年代制作美学，复古未来主义"

✅ Three-Way Fusion / 三重融合:
"Chinese folk + electronic + orchestral, traditional guzheng with modern synths and sweeping strings"
"中国民谣 + 电子 + 管弦乐，传统古筝配现代合成器和壮阔弦乐"
```

**5. Production Quality Tags / 制作质量标签**

```
✅ Quality Levels / 质量级别:
"Studio-grade production with professional mixing"
"录音室级制作，专业混音"

✅ Space/Ambience / 空间/氛围:
"Spacious reverb with intimate close-mic vocals"
"宽敞混响，亲密近距麦克风人声"

✅ Texture / 质感:
"Rich layered textures with crystalline clarity"
"丰富层叠质感，水晶般清晰"

✅ Dynamic / 动态:
"Dynamic production with quiet verses and explosive chorus"
"动态制作，安静主歌和爆炸性副歌"

✅ Vintage vs Modern / 复古 vs 现代:
"Warm analog warmth meets crisp digital precision"
"温暖模拟温暖遇上清晰数字精度"
```

**6. V8-Exclusive Features / V8 独有特性**

```
✅ Emotion Timeline / 情绪时间线:
"0:00-0:45: Melancholic introduction"
"0:45-1:30: Building hope and energy"
"1:30-2:15: Joyful chorus"
"2:15-3:00: Reflective bridge"
"3:00-3:45: triumphant resolution"

CN:
"0:00-0:45：忧郁开场"
"0:45-1:30：建立希望和能量"
"1:30-2:15：欢乐副歌"
"2:15-3:00：反思桥段"
"3:00-3:45：胜利解决"

✅ Instrument Roles / 乐器角色:
"Verse: Minimal piano and soft vocals"
"Pre-chorus: Bass and light percussion enter"
"Chorus: Full band with drums and backing vocals"
"Bridge: Orchestral swell with string section"

CN:
"主歌：极简钢琴和轻柔人声"
"预副歌：贝斯和轻打击乐进入"
"副歌：完整乐队，鼓和伴唱"
"桥段：管弦乐渐强，弦乐部"

✅ Voice Instructions / 人声指示:
"Verse: Intimate whisper with vulnerability"
"Chorus: Powerful belt with emotion"
"Bridge: Breathless, building to climax"

CN:
"主歌：亲密耳语，脆弱感"
"副歌：强力爆发，情感充沛"
"桥段：气喘吁吁，推向高潮"
```

#### Mureka V8 Advanced Examples / Mureka V8 高级示例

**Example 1 - Multi-Language Cultural Fusion / 多语言文化融合**

```
EN: 
"Japanese-Chinese bilingual J-Pop + Mandopop + Electronic upbeat 130 BPM G Major synthesizer koto piano idol female vocals glossy production Asian pop aesthetics - A bilingual collaboration track blending Japanese and Chinese pop styles, celebrating friendship and cultural exchange, with catchy hooks in both languages, bright synth melodies, and energy perfect for dancing"

CN:
"日中双语 K-Pop + 华语流行 + 电子 欢快 130 BPM G大调 合成器 琴 钢琴 偶像女声 光滑制作 亚洲流行美学 - 一首双语合作歌曲，融合日本和华语流行风格，庆祝友谊和文化交流，双语朗朗上口的钩子，明亮合成器旋律，适合跳舞的能量"
```

**Example 2 - Emotional Journey / 情感旅程**

```
EN:
"Chinese Rock + Ballad + Orchestral emotional-angry-determined-hopeful 85-120 BPM A Minor electric guitar strings erhu powerful female vocals dynamic production cinematic journey - A powerful Chinese rock ballad telling a story of personal struggle and eventual triumph, starting with anger at injustice, building through determination, and ending with hope and empowerment, featuring traditional erhu blending with electric guitar and orchestral strings"

CN:
"中文 摇滚 + 抒情歌 + 管弦乐 情感-愤怒-决心-充满希望 85-120 BPM A小调 电吉他 弦乐 二胡 强力女声 动态制作 电影感旅程 - 一首强有力的中文摇滚抒情歌，讲述个人挣扎和最终胜利的故事，从对不公的愤怒开始，经历决心的建立，以希望和赋能结束，传统二胡与电吉他和管弦乐弦乐融合"
```

**Example 3 - Ambient Ethereal / 氛围空灵**

```
EN:
"Korean Electronic + Ambient + Classical calm-peaceful-transcendental 70 BPM D Minor synthesizer gayageum strings ethereal female vocals spacious production meditative - A meditative Korean electronic ambient track combining electronic textures with traditional gayageum (Korean zither), creating a transcendent atmosphere perfect for mindfulness and reflection, with ethereal vocal layers and gradual evolution"

CN:
"韩语 电子 + 氛围 + 古典 平静-安宁-超脱 70 BPM D小调 合成器 伽倻琴 弦乐 空灵女声 宽敞制作 冥想 - 一首冥想韩语电子氛围乐，结合电子质感与传统伽倻琴（韩国筝），创造超脱氛围，适合正念和反思，有空灵人声层叠和渐进演变"
```

**Example 4 - Latin-Asian Fusion / 拉丁-亚洲融合**

```
EN:
"Spanish-Chinese bilingual Salsa + Mandopop + Jazz joyful-passionate-celebratory 120 BPM C Major brass piano erhu passionate bilingual male and female vocals party production cultural exchange - A fiery fusion track combining Latin salsa rhythms with Chinese melodies, bilingual lyrics in Spanish and Mandarin about celebrating life and cultural diversity, brass section meets traditional erhu, irresistible dance energy"

CN:
"西中双语 萨尔萨 + 华语流行 + 爵士 欢乐-激情-庆祝 120 BPM C大调 铜管 钢琴 二胡 激情双语男女声 派对制作 文化交流 - 一首火热的融合歌曲，结合拉丁萨尔萨节奏与中国旋律，西班牙语和普通话双语歌词关于庆祝生活和文化多样性，铜管乐部遇上传统二胡，无法抗拒的舞曲能量"
```

**Example 5 - Future Sound / 未来之声**

```
EN:
"English-Japanese-Korean trilingual Future Bass + Trap + K-Pop futuristic-cybernetic-intense 140 BPM F# Minor synthesizer heavy bass glitched vocals dystopian aesthetics - A cutting-edge future bass track with trilingual lyrics exploring themes of technology and humanity, heavy bass drops, glitchy vocal processing, cyberpunk aesthetics, and intense energy perfect for gaming and sci-fi contexts"

CN:
"英日韩三语言 Future Bass + 陷阱 + K-Pop 未来感-赛博-强烈 140 BPM 升F小调 合成器 重贝斯 故障人声 反乌托邦美学 - 一首前沿的 Future Bass 歌曲，三语言歌词探索技术和人性主题，重型贝斯节奏，故障人声处理，赛博朋克美学，强烈能量适合游戏和科幻场景"
```

**Example 6 - Traditional Evolution / 传统演进**

```
EN:
"Chinese Classical + Electronic + Cinematic reverent-majestic-evolving 80-110 BPM C Major guzheng pipa synthesizer orchestra no vocals epic production - An instrumental track showcasing the evolution of Chinese traditional music into the modern era, beginning with solo guzheng and pipa in classical style, gradually incorporating electronic elements and full orchestral arrangements, building to an epic cinematic climax"

CN:
"中文 古典 + 电子 + 电影感 敬畏-宏伟-演进 80-110 BPM C大调 古筝 琵琶 合成器 管弦乐 无人声 史诗制作 - 一首器乐曲，展示中国传统音乐向现代时代的演进，以独奏古筝和琵琶的古典风格开始，逐渐加入电子元素和完整管弦乐编排，构建至史诗电影感高潮"
```

**Example 7 - Hip Hop Global / 嘻哈全球**

```
EN:
"English-French-Arabic trilingual Hip-Hop + Reggaeton + Maqam confident-expressive-powerful 95 BPM A Minor 808 bass traditional percussion rap flow bilingual multilayered production global storytelling - A global hip-hop track with trilingual rapping in English, French, and Arabic, blending trap beats with Middle Eastern maqam scales and reggaeton rhythms, telling stories of cross-cultural identity and unity, confident delivery with multilayered vocal production"

CN:
"英法阿三语言 嘻哈 + 雷鬼顿 + 马卡姆 自信-表达-强力 95 BPM A小调 808贝斯 传统打击乐 说唱律动 双语多层制作 全球叙事 - 一首全球嘻哈歌曲，英法阿三语言说唱，融合陷阱节拍与中东马卡姆音阶和雷鬼顿节奏，讲述跨文化身份和团结的故事，自信表达和多层人声制作"
```

**Example 8 - Jazz Fusion Asia / 爵士融合亚洲**

```
EN:
"Chinese-Japanese bilingual Jazz Fusion + Ambient + Pentatonic contemplative-serene-joyous 100 BPM E Minor saxophone shakuhachi piano synthesisers subtle male vocals sophisticated production spiritual - A sophisticated jazz fusion track with bilingual male vocals, blending Western jazz with Chinese pentatonic and Japanese shakuhachi traditions, contemplative beginning building to joyful resolution, spiritual undertones throughout, intricate improvisation"

CN:
"中日双语 爵士融合 + 氛围 + 五声音阶 沉思-宁静-欢乐 100 BPM E小调 萨克斯 尺八 钢琴 合成器 微妙男声 精致制作 精神 - 一首精致的爵士融合歌曲，双语男声，融合西方爵士与中国五声音阶和日本尺八传统，沉思开始建立至欢乐解决，整曲贯穿精神底蕴，复杂即兴"
```

**Example 9 - Club Banger / 夜店劲曲**

```
EN:
"Korean-English bilingual EDM + House + K-Pop euphoric-intense-energetic 128 BPM C Major heavy kick synthesizer drops idol vocals festival production crowd energy - A high-energy club anthem blending EDM house beats with K-Pop energy, bilingual Korean-English lyrics about partying and living in the moment, massive synth drops, idol-style vocals, production optimized for festival crowds and dance floors"

CN:
"韩英双语 EDM + 浩室 + K-Pop 欣喜-强烈-充满能量 128 BPM C大调 重踢鼓 合成器 节奏 偶像人声 音乐节制作 人群能量 - 一首高能量夜店颂歌，融合EDM浩室节拍与K-Pop能量，韩英双语歌词关于派对和活在当下，巨大合成器节奏，偶像风格人声，为音乐节人群和舞池优化的制作"
```

**Example 10 - Storytelling Epic / 叙事史诗**

```
EN:
"Mandarin Chinese Folk + Rock + Cinematic epic-narrative-triumphant 75-120 BPM D Minor guitar banjo pipa orchestral swells powerful male vocals theatrical production hero's journey - An epic Chinese folk-rock ballad telling a complete hero's journey narrative across 5 minutes, starting with acoustic folk introduction, building through struggle and adversity, featuring traditional pipa solos, orchestral crescendos, and powerful vocals delivering a story of courage and victory in Mandarin Chinese"

CN:
"中文普通话 民谣 + 摇滚 + 电影感 史诗-叙事-胜利 75-120 BPM D小调 吉他 班卓琴 琵琶 管弦乐渐强 强力男声 剧场制作 英雄之旅 - 一首史诗中文民谣摇滚抒情歌，在5分钟内讲述完整的英雄之旅叙事，从原声民谣开场开始，经历挣扎和逆境，特色琵琶独奏，管弦乐高潮，强力人声用普通话讲述勇气和胜利的故事"
```

## Mureka V8 Advanced Mastery / Mureka V8 高级精通

### V8-Specific Prompt Techniques / V8 专属提示词技巧

#### 1. Emotion Granularity / 情绪细微度控制

V8 引入了**微情绪控制**，允许你在歌曲的不同部分指定精确的情绪变化：

```
[Language] [Genre] [Emotion Timeline] [Instrumentation] [Vocal Style] - [Description]

EN: "Chinese Pop emotional-structure: melancholic(0:00-0:45) → hesitant(0:45-1:15) → hopeful(1:15-2:00) → joyful(2:00-3:00) 95 BPM C Major piano strings erhu female vocals - Modern Chinese pop telling a story of emotional transformation from sadness to joy through personal growth"

CN: "中文 流行音乐 情绪结构：忧郁(0:00-0:45) → 犹豫(0:45-1:15) → 充满希望(1:15-2:00) → 欢乐(2:00-3:00) 95 BPM C大调 钢琴 弦乐 二胡 女声 - 现代中文流行，讲述通过个人成长从悲伤到欢乐的情感转变故事"
```

**情绪时间线格式 / Emotion Timeline Format:**
```
emotion_startTime-endTime → emotion_startTime-endTime
情绪开始时间-结束时间 → 情绪开始时间-结束时间

Examples / 示例：
- melancholic(0:00-0:30) → contemplative(0:30-1:00) → determined(1:00-2:00)
- 忧郁(0:00-0:30) → 沉思(0:30-1:00) → 决心(1:00-2:00)
- anxious(0:00-0:45) → peaceful(0:45-2:30) → transcendent(2:30-3:30)
- 焦虑(0:00-0:45) → 平静(0:45-2:30) → 超脱(2:30-3:30)
```

#### 2. Section-Specific Instrumentation / 分段乐器编排

V8 允许为歌曲的不同部分指定不同的乐器编排：

```
EN: "Chinese Electronic Progressive structure:
0:00-0:30: Intro - minimal piano solo
0:30-0:45: Pre-chorus - bass and light percussion enter
0:45-1:30: Chorus - full electronic arrangement with synths and drums
1:30-2:00: Verse - layered synthesis with guzheng textures
2:00-2:30: Bridge - orchestral swell with strings
2:30-3:30: Final Chorus - maximum density, all elements combined
100 BPM A Minor ethereal female vocals futuristic production - Progressive electronic track showcasing V8's section-specific instrumentation capabilities"

CN: "中文 电子 渐进结构：
0:00-0:30：前奏 - 极简钢琴独奏
0:30-0:45：预副歌 - 贝斯和轻打击乐进入
0:45-1:30：副歌 - 完整电子编排，合成器和鼓
1:30-2:00：主歌 - 层叠合成，古筝质感
2:00-2:30：桥段 - 管弦乐渐强，弦乐
2:30-3:30：最终副歌 - 最大密度，所有元素结合
100 BPM A小调 空灵女声 未来制作 - 渐进电子曲目，展示V8的分段乐器编排能力"
```

**常见结构标签 / Common Structure Tags:**
```
Intro - 开场 / 前奏
Verse - 主歌
Pre-chorus - 预副歌
Chorus - 副歌
Bridge - 桥段
Drop - 节奏
Breakdown - 间奏
Outro - 结尾
```

#### 3. Cross-Language Transitions / 跨语言过渡

V8 的高级多语言引擎支持语言间的无缝过渡：

```
EN: "Chinese-English seamless language transitions:
Verse: Mandarin Chinese
Pre-chorus: Mandarin Chinese
Chorus: English
Verse 2: English
Bridge: Mandarin Chinese
Final Chorus: Bilingual Mandarin + English
110 BPM G Major pop-rock bilingual female and male vocals cultural exchange - Bilingual pop-rock song about cultural understanding, with V8's advanced language transition engine creating natural flow between Mandarin and English"

CN: "中英无缝语言过渡：
主歌：普通话
预副歌：普通话
副歌：英文
主歌2：英文
桥段：普通话
最终副歌：双语普通话+英文
110 BPM G大调 流行摇滚 双语男女声 文化交流 - 双语流行摇滚歌曲，关于文化理解，使用V8的高级语言过渡引擎创造普通话和英文之间的自然流畅"
```

**语言过渡模式 / Language Transition Patterns:**
```
1. Verse-Chorus Language Switch / 主歌-副歌语言切换：
   Verse: Language A / 主歌：语言A
   Chorus: Language B / 副歌：语言B

2. Gradual Bilingual / 渐进双语：
   Start single language → gradually mix → fully bilingual
   单语言开始 → 逐渐混合 → 完全双语

3. Call-and-Response / 呼应：
   Line A: Language A / 句A：语言A
   Line B: Language B / 句B：语言B

4. Word-Level Fusion / 词级融合：
   Single phrases combining both languages
   单短语结合两种语言
```

#### 4. Cultural Fusion Depth / 文化融合深度

V8 的文化智能系统能够理解并融合不同文化的音乐传统：

```
EN: "Chinese-Latin fusion depth:
Primary foundation: Chinese pentatonic melodic system (宫商角徵羽)
Rhythmic foundation: Latin salsa and rumba patterns
Harmonic layer: Western contemporary chord voicings
Instrumentation blend: guzheng + congas + piano + tres guitar
Cultural fusion: 'Spring Festival meets Carnival' theme
125 BPM C Major bilingual Spanish-Chinese passionate vocals festive production - Deep cultural fusion celebrating Chinese New Year and Latin carnival simultaneously, V8 intelligently balances pentatonic melodies with clave rhythms"

CN: "中拉融合深度：
主要基础：中国五声音阶旋律系统（宫商角徵羽）
节奏基础：拉丁萨尔萨和伦巴模式
和声层：西方当代和弦编配
乐器融合：古筝 + 康加鼓 + 钢琴 + 特雷斯吉他
文化融合：'春节遇见狂欢节'主题
125 BPM C大调 双语西班牙-中文 激情人声 节日制作 - 深度文化融合，同时庆祝中国春节和拉丁狂欢节，V8智能平衡五声旋律与克拉维节奏"
```

**文化融合等级 / Cultural Fusion Levels:**

**Level 1: Superficial / 表层融合**
```
Simple instrument mixing / 简单乐器混合
EN: "Chinese instruments in Western song"
CN: "西方歌曲中的中国乐器"
```

**Level 2: Structural / 结构融合**
```
Combining musical systems / 结合音乐系统
EN: "Chinese pentatonic scale with Western harmony"
CN: "中国五声音阶配合西方和声"
```

**Level 3: Deep Cultural / 深层文化融合**
```
Understanding cultural contexts / 理解文化语境
EN: "Philosophical fusion of Taoist concepts and African polyrhythms"
CN: "道家概念与非洲多节奏的哲学融合"
```

**Level 4: Authentic Integration / 真正融合**
```
Cultural intelligence and respect / 文化智能和尊重
EN: "Respectful fusion understanding the spiritual origins of both traditions"
CN: "尊重的融合，理解两种传统的精神起源"
```

#### 5. V8 Voice Engineering / V8 人声工程

V8 的人声引擎提供了前所未有的控制力：

```
EN: "V8 Voice specifications:
Verse vocals: Intimate, breathy, close-mic, 90% dry signal
Pre-chorus build: Gradually add compression and reverb, 70% dry
Chorus: Powerful, belted, wide stereo image, 40% dry
Bridge: Falsetto with heavy reverb and delay, 20% dry
Ad-libs: whispered responses in verse background, layered in chorus
Vocal characteristics: Mandarin female, mezzo-soprano range, slight vibrato on long notes
95 BPM D Minor R&B ballad lush production - V8-optimized R&B ballad showcasing precise vocal engineering across sections"

CN: "V8 人声规格：
主歌人声：亲密、气声、近距麦克风、90%干信号
预副歌铺垫：逐渐添加压缩和混响、70%干信号
副歌：强力、爆发、宽立体声图像、40%干信号
桥段：假声配重度混响和延迟、20%干信号
即兴：主歌背景中的耳语回应、副歌中层叠
人声特征：中文女声、次女高音音域、长音符上有轻微颤音
95 BPM D小调 R&B抒情歌 华丽制作 - V8优化的R&B抒情歌，展示跨段的精确人声工程"
```

**V8 人声参数 / V8 Vocal Parameters:**

**Dry/Wet Balance / 干湿平衡:**
```
0% dry = fully wet (all effects) / 完全湿信号（全效果）
50% dry = balanced mix / 平衡混合
100% dry = no effects (natural) / 无效果（自然）

Verse examples / 主歌示例：
- "90% dry, intimate" / "90%干信号，亲密"
- "70% dry, subtle ambiance" / "70%干信号，微妙氛围"
- "50% dry, atmospheric" / "50%干信号，氛围感"

Chorus examples / 副歌示例：
- "30% dry, spacious" / "30%干信号，宽敞"
- "20% dry, epic reverb" / "20%干信号，史诗混响"
- "40% dry, moderate effects" / "40%干信号，适度效果"
```

**Vocal Dynamics / 人声动态:**
```
Intensity levels / 强度级别：
1. Whisper / 耳语 - barely audible, intimate
   几乎听不见，亲密

2. Soft / 轻柔 - quiet but clear, gentle
   安静但清晰，温柔

3. Conversational / 对话式 - natural speech level
   自然说话水平

4. Strong / 强力 - projected, confident
   投射，自信

5. Belted / 爆发 - powerful, passionate
   强力，激情

6. Screamed / 嘶吼 - extreme intensity (rare)
   极端强度（罕见）
```

### V8 Real-Time Iteration / V8 实时迭代

#### Prompt Version History / 提示词版本历史

V8 支持提示词版本管理，让你可以快速迭代和比较：

```
Version 1 / 版本1:
"Pop happy 120 BPM - Summer song"
CN: "流行 快乐 120 BPM - 夏季歌曲"

Version 2 / 版本2 (more specific / 更具体):
"Pop upbeat 125 BPM bright female vocals catchy - Summer anthem"
CN: "流行 欢快 125 BPM 明亮女声 朗朗上口 - 夏季颂歌"

Version 3 / 版本3 (added instruments / 添加乐器):
"Pop upbeat 125 BPM synth bass drums bright female vocals - Summer anthem with dance energy"
CN: "流行 欢快 125 BPM 合成器贝斯鼓 明亮女声 - 夏季颂歌，有舞曲能量"

Version 4 / 版本4 (V8 optimized / V8优化):
"Pop upbeat 125 BPM C Major synth bass punchy drums bright female vocals studio production emotional arc: joyful(0:00-1:00) → euphoric(1:00-3:00) - Summer anthem about beach days and endless nights with infectious energy and singalong chorus, V8 production quality maximum"
CN: "流行 欢快 125 BPM C大调 合成器贝斯 有力鼓 明亮女声 录音室制作 情绪弧线：欢乐(0:00-1:00) → 狂喜(1:00-3:00) - 夏季颂歌，关于海滩日和无限夜晚，有感染能量和合唱，V8制作质量最高"
```

**迭代策略 / Iteration Strategy:**

1. **Start Simple / 从简单开始**
   - Basic genre + mood + description / 基础流派 + 情绪 + 描述
   - Test the core idea / 测试核心理念

2. **Add Detail Incrementally / 逐步添加细节**
   - Add tempo / 添加速度
   - Add instruments / 添加乐器
   - Add vocal style / 添加人声风格

3. **Refine for V8 / 为V8优化**
   - Add emotional arc / 添加情绪弧线
   - Add section-specific details / 添加分段特定细节
   - Use V8-specific tags / 使用V8专属标签

4. **Compare Versions / 比较版本**
   - Listen to each version / 听每个版本
   - Identify improvements / 识别改进
   - Combine best elements / 结合最佳元素

### V8 Production Quality Engine / V8 制作质量引擎

V8 的制作质量引擎提供了录音室级别的音频质量：

```
Quality Tags / 质量标签:

【Production Quality Levels / 制作质量级别】

Level 1: Demo / 演示
- Basic mix / 基础混音
- Simple arrangement / 简单编排
Tag: "demo quality" / "演示质量"

Level 2: Home Studio / 家庭录音室
- Clean mix / 清晰混音
- Balanced frequencies / 平衡频率
Tag: "home studio production" / "家庭录音室制作"

Level 3: Professional / 专业
- Professional mixing / 专业混音
- Good clarity / 良好清晰度
Tag: "professional production" / "专业制作"

Level 4: Studio / 录音室
- Studio-grade mixing / 录音室级混音
- Professional mastering / 专业母带处理
Tag: "studio production" / "录音室制作"

Level 5: Commercial / 商业
- Radio-ready / 电台就绪
- Streaming-optimized / 流媒体优化
Tag: "radio-ready production" / "电台就绪制作"

Level 6: V8 Maximum / V8最高
- State-of-the-art AI mastering / 最先进AI母带处理
- Reference quality / 参考质量
Tag: "V8 maximum quality" / "V8最高质量"

【Usage Example / 使用示例】

EN: "Chinese Pop V8 maximum quality cinematic production orchestral layers professional mastering - Commercial-grade Chinese pop song with V8's highest production standards"

CN: "中文流行 V8最高质量 电影感制作 管弦乐层叠 专业母带处理 - 商业级中文流行歌曲，使用V8最高制作标准"
```

**Production Specific Tags / 制作特定标签:**

**Mix Characteristics / 混音特征:**
```
- "punchy mix" - 强劲有力的混音
- "warm analog" - 温暖模拟感
- "crisp digital" - 清晰数字感
- "spacious" - 宽敞空间感
- "intimate" - 亲密感
- "transparent" - 通透清晰
```

**Frequency Emphasis / 频率强调:**
```
- "bass-heavy" - 重低音强调
- "bright top end" - 明亮高频
- "mid-focused" - 中频集中
- "full spectrum" - 全频段平衡
```

**Spatial Effects / 空间效果:**
```
- "wide stereo" - 宽立体声
- "centered vocals" - 居中人声
- "3D imaging" - 3D立体图像
- "surround feel" - 环绕感
```

### V8 Cultural Intelligence Database / V8 文化智能数据库

V8 内置了丰富的文化音乐知识库：

```
【Traditional Music Systems / 传统音乐系统】

Chinese / 中文:
- Pentatonic scales / 五声音阶
- Erhu, guzheng, pipa, dizi / 二胡、古筝、琵琶、笛子
- Regional styles: Cantonese, Beijing, Shanghai / 地方风格：粤式、京式、沪式

Japanese / 日文:
- Japanese scales (Hirajoshi, etc.) / 日本音阶
- Koto, shakuhachi, shamisen / 琴、尺八、三味线
- Enka, J-Pop, anime music / 演歌、J-Pop、动漫音乐

Korean / 韩文:
- Pentatonic with unique ornamentation / 五声音阶配独特装饰音
- Gayageum, haegeum, janggu / 伽倻琴、奚琴、杖鼓
- K-Pop, trot, traditional court music / K-Pop、 Trot、传统宫廷音乐

Indian / 印地文:
- Raga systems / 拉格系统
- Sitar, tabla, sarod / 西塔鼓、塔布拉鼓、萨罗德
- Bollywood, classical / 宝莱坞、古典

African / 非洲:
- Polyrhythms / 多节奏
- Djembe, kora, mbira / 非洲鼓、科拉琴、拇指琴
- Afrobeat, highlife, soukous / 非洲节拍、Highlife、Soukous

Latin / 拉丁:
- Clave rhythms / 克拉维节奏
- Guitar, percussion, brass / 吉他、打击乐、铜管
- Salsa, reggaeton, tango / 萨尔萨、雷鬼顿、探戈

【Cultural Context Tags / 文化语境标签】

EN: "Chinese Lunar New Year festive traditional instruments modern arrangement - Celebratory track for Chinese New Year blending traditional instruments like erhu and guzheng with contemporary pop production"

CN: "中文春节庆祝 传统乐器 现代编排 - 春节庆祝曲目，融合二胡和古筝等传统乐器与当代流行制作"

EN: "Japanese autumn melancholy koto shakuhachi minimalist production - Reflective Japanese ambient piece inspired by autumn themes with traditional instruments"

CN: "日本秋季忧郁 琴 尺八 极简制作 - 受秋季主题启发的反思性日本氛围乐，使用传统乐器"

EN: "Korean traditional pansori contemporary fusion electric gayageum - Modern reinterpretation of Korean pansori storytelling tradition with electric instruments"

CN: "韩国传统盘索里 当代融合 电伽倻琴 - 韩国盘索里叙事传统的现代重新诠释，使用电子乐器"
```

### V8 Advanced Use Cases / V8 高级应用场景

#### 场景1: 电视剧原声 / TV Drama Soundtrack

```
EN: "Chinese Contemporary TV drama soundtrack
Episodes 1-3: Character introduction, hope, subtle optimism
Episodes 4-6: Conflict, tension, minor key
Episodes 7-9: Climax, dramatic orchestral, emotional peak
Episodes 10-12: Resolution, major key, peaceful ending
Vocal styles: Emotional female ballads, hopeful male vocals
Instrumentation: Piano, strings, traditional Chinese instruments
Production: V8 cinematic quality with seamless transitions between emotional states
Main theme: Love and destiny in modern China
110 BPM various keys orchestral pop-rock - Complete TV drama soundtrack with 4 emotional arcs"

CN: "中文当代电视剧原声
第1-3集：角色介绍、希望、微妙乐观
第4-6集：冲突、紧张、小调
第7-9集：高潮、戏剧性管弦乐、情感顶点
第10-12集：解决、大调、平静结局
人声风格：情感女声抒情歌、充满希望男声
乐器：钢琴、弦乐、中国传统乐器
制作：V8电影感质量，情绪状态间无缝过渡
主题：现代中国的爱情与命运
110 BPM 各种调性 管弦乐流行摇滚 - 完整电视剧原声，4个情感弧线"
```

#### 场景2: 游戏音乐 / Game Music

```
EN: "Japanese-style RPG game soundtrack
Battle theme: High energy, fast tempo, epic orchestral with electric guitar
Exploration theme: Peaceful, ambient, traditional Japanese instruments
Boss battle: Intense, heavy, dramatic with choir
Victory theme: Triumphant, major key, celebratory
Emotional cutscene: Piano, strings, emotional vocals
Language: Japanese and English bilingual
V8 features: Dynamic intensity changes, seamless loops, mood transitions
Production: Game-optimized with clear frequencies
Multiple tempos: 90-160 BPM depending on context
Orchestral + Rock fusion - Complete RPG soundtrack covering all game states"

CN: "日式RPG游戏原声
战斗主题：高能量、快节奏、史诗管弦乐配电吉他
探索主题：平静、氛围、日本传统乐器
Boss战：强烈、重型、戏剧性配合唱
胜利主题：胜利、大调、庆祝
情感过场：钢琴、弦乐、情感人声
语言：日英双语
V8特性：动态强度变化、无缝循环、情绪过渡
制作：游戏优化，频率清晰
多速度：90-160 BPM，根据上下文
管弦乐+摇滚融合 - 完整RPG原声，覆盖所有游戏状态"
```

#### 场景3: 品牌广告 / Brand Commercial

```
EN: "Global brand commercial music
Brand tone: Modern, innovative, global appeal
Target markets: China, Japan, Korea, Southeast Asia
Cultural fusion: Asian contemporary blend
Vocal approach: Bilingual with universal appeal
Structure: 30-second impact-driven
V8 features: Maximum production quality, cultural intelligence
Emotional arc: Curious → Inspired → Empowered → Action
Tempo: 120 BPM consistent
Language: Primarily English with Asian language elements
Pop + Electronic fusion with subtle traditional elements - Global commercial music blending contemporary pop with subtle Asian cultural elements for pan-Asian market appeal"

CN: "全球品牌广告音乐
品牌调性：现代、创新、全球吸引力
目标市场：中国、日本、韩国、东南亚
文化融合：亚洲当代融合
人声方式：双语，普遍吸引力
结构：30秒冲击驱动
V8特性：最高制作质量、文化智能
情绪弧线：好奇 → 受到启发 → 赋能 → 行动
速度：120 BPM一致
语言：主要英文配亚洲语言元素
流行+电子融合，微妙传统元素 - 全球商业音乐，融合当代流行与微妙亚洲文化元素，吸引泛亚市场"
```

#### 场景4: 儿童教育音乐 / Children's Educational Music

```
EN: "Chinese children's educational music series
Educational goals: Language learning, cultural values, creativity
Age group: 3-8 years old
Song themes:
- Numbers and counting (Chinese + English)
- Traditional festivals and customs
- Nature and animals
- Family and values
- Friendship and sharing
Vocal style: Clear, friendly, bilingual, easy to sing
Tempo: 100-120 BPM, child-friendly
Instruments: Bright, playful, combination of traditional and modern
Production: V8 clear vocals with child-friendly mixing
Language: Chinese-English bilingual, educational focus
Playful educational songs with simple melodies and bilingual lyrics - Children's music series teaching Chinese culture and language through fun, memorable songs"

CN: "中文儿童教育音乐系列
教育目标：语言学习、文化价值、创造力
年龄组：3-8岁
歌曲主题：
- 数字和计数（中文+英文）
- 传统节日和习俗
- 自然和动物
- 家庭和价值观
- 友谊和分享
人声风格：清晰、友好、双语、易于歌唱
速度：100-120 BPM，儿童友好
乐器：明亮、有趣、传统和现代结合
制作：V8清晰人声，儿童友好混音
语言：中英双语，教育重点
有趣教育歌曲，简单旋律和双语歌词 - 儿童音乐系列，通过有趣难忘的歌曲教授中文文化和语言"
```

#### 场景5: 冥想和正念 / Meditation and Mindfulness

```
EN: "Multilingual meditation music
Languages: Sanskrit mantras + Chinese ambient textures + English guidance
Meditation goals: Relaxation, focus, spiritual connection
V8 features:
- Extended ambient textures (20+ minutes)
- Subtle emotional transitions
- Layered vocal guidance
- Space for personal meditation
Instrumentation: Tibetan singing bowls, Chinese guzheng, synth pads
Vocal approach: Whispered guidance, mantra chanting, periods of silence
Production: V8 maximum quality with pristine clarity
Tempo: 60-70 BPM, very slow
Ambient spiritual meditation - Extended meditation track combining Sanskrit mantras with Chinese ambient elements and English guidance for transcendent experience"

CN: "多语言冥想音乐
语言：梵文咒语 + 中文氛围纹理 + 英文指导
冥想目标：放松、专注、精神连接
V8特性：
- 延伸氛围纹理（20+分钟）
- 微妙情绪过渡
- 层叠人声指导
- 个人冥想空间
乐器：西藏颂钵、中国古筝、合成器垫音
人声方式：耳语指导、咒语吟唱、静默时期
制作：V8最高质量，原始清晰
速度：60-70 BPM，非常慢
氛围精神冥想 - 延伸冥想曲目，结合梵文咒语与中文氛围元素和英文指导，创造超脱体验"
```

## Mureka V8 Quick Reference / Mureka V8 快速参考

### V8 核心特性速查 / V8 Core Features Quick Reference

```
🎯 Multilingual Support / 多语言支持
  - 20+ languages native / 20+语言原生
  - Seamless transitions / 无缝过渡
  - Cultural intelligence / 文化智能

🎤 Advanced Vocal Engine / 高级人声引擎
  - Micro-emotion control / 微表情控制
  - Section-specific vocals / 分段人声
  - Breath control / 气息控制
  - Dry/wet engineering / 干湿工程

🎨 Genre Fusion System / 流派融合系统
  - 3+ genre blending / 3+流派融合
  - Cross-cultural fusion / 跨文化融合
  - Intelligent integration / 智能集成

🎭 Mood Mapping 2.0 / 情绪映射 2.0
  - Emotional arcs / 情感弧线
  - Micro-emotions / 微表情
  - Timeline tracking / 时间线跟踪

🎹 Production Quality / 制作质量
  - Studio-grade mixing / 录音室级混音
  - Professional mastering / 专业母带处理
  - Reference quality / 参考质量

🌍 Cultural Intelligence / 文化智能
  - Traditional music systems / 传统音乐系统
  - Respectful fusion / 尊重的融合
  - Context-aware / 语境感知

📝 Lyric Enhancement / 歌词增强
  - Improved rhyme schemes / 改进的押韵模式
  - Better word-melody alignment / 更好的词-旋律对齐
  - Multilingual rhymes / 多语言押韵

⚡ Real-Time Iteration / 实时迭代
  - Prompt versioning / 提示词版本管理
  - Quick refinement / 快速优化
  - Comparison tools / 比较工具
```

### V8 提示词模板速查 / V8 Prompt Template Quick Reference

```
【基础模板 / Basic Template】

[Language] [Genre] [Mood] [Tempo] [Instruments] [Vocals] - [Description]

【高级模板 / Advanced Template】

[Language] [Primary Genre] + [Secondary Genre] + [Tertiary Genre]
[Emotion Timeline: emotion(time-time) → emotion(time-time)]
[Tempo Range] [Key] [Time Signature]
[Section-Specific: 0:00-0:30: A / 0:30-1:00: B]
[Instrumentation: instrument + instrument]
[Vocal Style: voice type + delivery style]
[Production: quality tags]
[Cultural Context: traditions/elements]
- [Detailed Description with theme and narrative]

【V8 最优模板 / V8 Optimal Template】

[Language] [Genre Fusion] [Emotional Arc] [Tempo] [Key] [Time Signature]
0:00-0:30: [Section] - [Instruments] - [Vocals] - [Emotion]
0:30-1:00: [Section] - [Instruments] - [Vocals] - [Emotion]
1:00-2:00: [Chorus] - [Instruments] - [Vocals] - [Emotion]
2:00-2:30: [Bridge] - [Instruments] - [Vocals] - [Emotion]
2:30-3:30: [Final Chorus] - [Instruments] - [Vocals] - [Emotion]
[Production: V8 maximum quality]
[Cultural Intelligence: elements and traditions]
- [Full narrative description with character, story, and themes]
```

### 常用 V8 标签速查 / Common V8 Tags Quick Reference

```
【语言标签 / Language Tags】
- Chinese Mandarin / 普通话
- Cantonese / 粤语
- Japanese / 日文
- Korean / 韩文
- Bilingual / 双语
- Trilingual / 三语言
- Native pronunciation / 原生发音

【质量标签 / Quality Tags】
- V8 maximum quality / V8最高质量
- Studio production / 录音室制作
- Radio-ready / 电台就绪
- Professional mixing / 专业混音
- Crisp digital / 清晰数字
- Warm analog / 温暖模拟

【情绪标签 / Emotion Tags】
- Melancholic / 忧郁
- Joyful / 喜悦
- Hopeful / 充满希望
- Intense / 强烈
- Peaceful / 平静
- Euphoric / 狂喜
- Reflective / 反思
- Powerful / 强力

【文化标签 / Cultural Tags】
- Chinese pentatonic / 中国五声
- Japanese koto / 日本琴
- Korean gayageum / 韩国伽倻琴
- Latin clave / 拉丁克拉维
- African polyrhythms / 非洲多节奏
- Cultural fusion / 文化融合

【制作标签 / Production Tags】
- Cinematic / 电影感
- Spacious / 宽敞
- Intimate / 亲密
- Punchy / 强劲
- Transparent / 通透
- Warm / 温暖
```

---

## Prompt Refinement / 提示词优化

## Prompt Refinement / 提示词优化

### Iterate and Improve / 迭代与改进

#### Step 1: Start with a Basic Prompt / 第一步：从基础提示词开始
```
Use genre + mood + description
使用 流派 + 情绪 + 描述

Example / 示例：
"Pop happy song about summer"
"流行 快乐 关于夏天的歌"
```

#### Step 2: Listen to the Output / 第二步：听输出结果
```
Identify what works and what doesn't
识别什么有效，什么无效
```

#### Step 3: Add Specificity / 第三步：增加具体性
```
Refine instrumentation, vocals, or production
优化乐器、人声或制作

Example / 示例：
"Pop upbeat 120 BPM catchy summer anthem with bright female vocals"
"流行 欢快 120 BPM 朗朗上口的夏季颂歌，有明亮女声"
```

#### Step 4: Experiment / 第四步：实验
```
Try different genres, moods, or combinations
尝试不同流派、情绪或组合

Example / 示例：
"Pop-EDM fusion summer anthem with electronic elements"
"流行-EDM 融合夏季颂歌，有电子元素"
```

#### Step 5: Combine Elements / 第五步：组合元素
```
Mix traits from different prompts for unique results
混合不同提示词的特征，获得独特结果

Example / 示例：
"Pop upbeat 125 BPM with tropical house influence, steel drums, reggaeton rhythm"
"流行 欢快 125 BPM 带热带浩室影响，钢鼓，雷鬼顿节奏"
```

### Common Adjustments / 常见调整

#### More Energy / 更多能量
- "More energy" / "更多能量"
- Add: "driving," "intense," "propulsive," "upbeat"
- 添加："驱动性"、"强烈"、"推进"、"欢快"

#### Softer Sound / 更柔和的声音
- "Softer sound" / "更柔和"
- Add: "gentle," "mellow," "warm," "soft"
- 添加："温柔"、"柔和"、"温暖"、"柔软"

#### More Complex / 更复杂
- "More complex" / "更复杂"
- Add: "layered," "intricate," "sophisticated," "rich"
- 添加："层叠"、"错综"、"精致"、"丰富"

#### Simpler / 更简单
- "Simpler" / "更简单"
- Add: "minimal," "stripped back," "direct," "clean"
- 添加："极简"、"简化"、"直接"、"干净"

#### Catchier / 更朗朗上口
- "Catchier" / "更朗朗上口"
- Add: "memorable hooks," "singalong," "anthemic," "sticky"
- 添加："难忘的钩子"、"合唱"、"颂歌式"、"粘性"

## Example Prompts / 提示词示例

### Complete Prompt Examples / 完整提示词示例

#### 1. Summer Pop Anthem / 夏季流行颂歌
```
Pop upbeat 126 BPM synth bass catchy hooks bright female vocals - An infectious radio-ready pop song about summer adventures and making memories under the sun with an irresistible singalong chorus

CN: 流行音乐 欢快 126 BPM 合成器贝斯 朗朗上口的钩子 明亮女声 - 一首具有感染力的电台就绪流行歌曲，关于夏日冒险和在阳光下创造回忆，有无法抗拒的合唱部分
```

#### 2. Emotional Ballad / 情感抒情歌
```
Piano ballad slow 72 BPM strings orchestral swell powerful female vocals - Heartbreak song about letting go and finding strength with dramatic chorus that builds to soaring crescendo

CN: 钢琴抒情歌 缓慢 72 BPM 弦乐 管弦乐渐强 强力女声 - 关于放手和寻找力量的心碎歌曲，戏剧性副歌逐渐推进至高亢的高潮
```

#### 3. Dark Techno / 黑暗科技音乐
```
Dark techno 132 BPM pounding kick hypnotic arpeggios industrial textures - Brooding techno for late-night warehouse atmosphere with relentless energy and minimal vocals

CN: 黑暗科技音乐 132 BPM 重击踢鼓 催眠琶音 工业质感 - 阴郁的科技音乐，适合深夜仓库氛围，有无情能量和极简人声
```

#### 4. Acoustic Folk Story / 原声民谣故事
```
Acoustic folk storytelling 85 BPM guitar harmonica gentle male vocals - Intimate folk song about small-town life and changing times with nostalgic warmth

CN: 原声民谣 叙事 85 BPM 吉他 口琴 温柔男声 - 亲密的民谣歌曲，关于小镇生活和时代变迁，有怀旧温暖
```

#### 5. Trap Banger / 陷阱音乐劲曲
```
Trap 140 BPM 808 bass hi-hat rolls aggressive rap flow cinematic atmosphere - Hard-hitting trap anthem about rising to the top with menacing energy and confident delivery

CN: 陷阱音乐 140 BPM 808贝斯 踩镲滚动 激烈说唱律动 电影氛围 - 重击型陷阱颂歌，关于登上巅峰，有威胁性能量和自信表达
```

#### 6. Chinese Traditional Fusion / 中国传统融合
```
中文 电子 氛围 100 BPM 二胡 古筝 合成器 梦幻女声 - 东西方音乐融合，结合传统中国乐器二胡和古筝与现代电子氛围，创造空灵梦幻的声音

Translation:
"Chinese Electronic ambient 100 BPM erhu guzheng synthesizer dreamy female vocals - East-West fusion combining traditional Chinese instruments erhu and guzheng with modern electronic atmosphere, creating ethereal dreamy sound"
```

#### 7. K-Pop Dance Track / K-Pop 舞曲
```
Korean upbeat 130 BPM electronic dance catchy hooks idol vocals high energy - Modern K-pop dance track with dynamic production and festival-ready drops

CN: 韩语 欢快 130 BPM 电子舞曲 朗朗上口的钩子 偶像人声 高能量 - 现代 K-Pop 舞曲，有动态制作和适合音乐节的节奏
```

#### 8. Jazz Fusion / 爵士融合
```
Jazz fusion 120 BPM complex time signatures electric guitar synthesizer - Progressive fusion with virtuosic musicianship and adventurous compositions

CN: 爵士融合 120 BPM 复杂拍号 电吉他 合成器 - 前卫融合，有精湛演奏和冒险性作曲
```

#### 9. Ambient Meditation / 氛围冥想
```
Ambient 60 BPM minimal drones atmospheric pads ethereal vocals - Meditative ambient music for relaxation and mindfulness

CN: 氛围音乐 60 BPM 极简长音 氛围垫音 空灵人声 - 冥想氛围音乐，用于放松和正念
```

#### 10. Reggae Summer Vibe / 雷鬼夏日氛围
```
Reggae upbeat 85 BPM steel drums offbeat guitar brass section - Tropical reggae with positive vibes perfect for beach parties

CN: 雷鬼 欢快 85 BPM 钢鼓 反拍吉他 铜管乐部 - 热带雷鬼，有积极氛围，适合海滩派对
```

### Bilingual Prompt Examples / 双语提示词示例

#### Bilingual Pop Song / 双语流行歌曲
```
"English-Chinese bilingual pop 110 BPM piano emotional male and female vocals - Love song with lyrics in both English and Chinese about cross-cultural romance"

CN: "英中双语流行 110 BPM 钢琴 情感 男女声 - 关于跨文化爱情的双语情歌，歌词包含英文和中文"
```

#### K-Pop Style / K-Pop 风格
```
"Korean-English K-Pop upbeat 130 BPM electronic catchy hooks idol vocals - Modern K-pop with bilingual lyrics mixing Korean and English"

CN: "韩英 K-Pop 欢快 130 BPM 电子 朗朗上口的钩子 偶像人声 - 现代 K-Pop，有混合韩文和英文的双语歌词"
```

#### Chinese Folk Electronic / 中文民谣电子
```
"中文 民谣 电子 95 BPM 二胡 合成器 梦幻 - 传统中文民谣与现代电子音乐的融合，创造独特的东西方声音"

Translation:
"Chinese folk electronic 95 BPM erhu synthesizer dreamy - Fusion of traditional Chinese folk and modern electronic music, creating unique East-West sound"
```

## Troubleshooting / 故障排除

### Common Issues / 常见问题

#### Issue 1: Results Too Generic / 结果太普通
```
Problem: The AI produces generic, forgettable music
问题：AI 生成普通、令人遗忘的音乐

Solutions:
解决方案：
- Add specific artist references / 添加具体的艺术家参考
- Include unique instrument combinations / 包含独特的乐器组合
- Specify detailed production techniques / 指定详细的制作技巧
- Use more descriptive adjectives / 使用更多描述性形容词

Example / 示例：
Instead of: "Sad song"
改为："Sad song"

Use: "Melancholic indie rock 85 BPM shoegaze guitars whispery vocals - Intimate song about late-night introspection"
使用："忧郁独立摇滚 85 BPM 自赏吉他 耳语人声 - 关于深夜内省的亲密歌曲"
```

#### Issue 2: Language Clarity Issues / 语言清晰度问题
```
Problem: Lyrics or vocals unclear in specific language
问题：特定语言中歌词或人声不清晰

Solutions:
解决方案：
- Specify language explicitly / 明确指定语言
- Add pronunciation notes / 添加发音说明
- Use simpler vocabulary / 使用更简单的词汇
- Test with shorter phrases / 用更短的短语测试

Example / 示例：
"Chinese Mandarin clear pronunciation standard Putonghua - Simple emotional love song with easy-to-understand lyrics"
CN: "中文 普通话 发音清晰 - 简单的情感情歌，歌词易于理解"
```

#### Issue 3: Genre Blending / 流派混合
```
Problem: Genre fusion sounds messy or confused
问题：流派融合听起来混乱或困惑

Solutions:
解决方案：
- Choose one dominant genre / 选择一个主导流派
- Add secondary genre as influence / 将次要流派作为影响添加
- Use "fusion" or "blend" terminology / 使用"融合"或"混合"术语
- Keep instrumentation consistent / 保持乐器一致

Example / 示例：
"Rock dominant with folk influence - Rock 110 BPM electric guitar acoustic guitar blend - Folk-rock fusion with rock energy and folk storytelling"
CN: "摇滚主导，民谣影响 - 摇滚 110 BPM 电吉他 原声吉他 混合 - 民谣摇滚融合，有摇滚能量和民谣叙事"
```

#### Issue 4: Vocals Not Matching Instrumentation / 人声不匹配乐器
```
Problem: Vocal style doesn't fit the music
问题：人声风格不适合音乐

Solutions:
解决方案：
- Match vocal energy to instrumental energy / 匹配人声能量与乐器能量
- Consider genre conventions / 考虑流派惯例
- Specify delivery style / 指定表达风格
- Try vocal effects / 尝试人声效果

Example / 示例：
Instead of: "Heavy metal with gentle vocals"
改为："Heavy metal with gentle vocals"

Use: "Heavy metal aggressive 140 BPM powerful gritty vocals - Intense metal with aggressive delivery matching the instrumental intensity"
使用："重金属 激烈 140 BPM 强力粗砺人声 - 强烈金属，有与乐器强度匹配的激进表达"
```

## Best Practices Summary / 最佳实践总结

### Do's / 要做的

1. **Be Specific / 要具体**
   - Include tempo, instruments, mood / 包含速度、乐器、情绪
   - Reference specific artists / 参考具体艺术家
   - Describe desired output / 描述期望的输出

2. **Use Platform Strengths / 利用平台优势**
   - Know what each platform excels at / 了解每个平台擅长什么
   - Tailor prompts accordingly / 相应地调整提示词
   - Learn from platform-specific examples / 从平台特定示例中学习

3. **Iterate and Refine / 迭代和优化**
   - Start simple, then add detail / 从简单开始，然后添加细节
   - Learn from what works / 学习什么有效
   - Don't be afraid to experiment / 不要害怕实验

4. **Consider Language / 考虑语言**
   - Specify language clearly / 明确指定语言
   - Be mindful of pronunciation / 注意发音
   - Use cultural context appropriately / 适当使用文化背景

5. **Balance Complexity / 平衡复杂性**
   - Enough detail for direction / 足够的细节用于指导
   - Not so much it confuses / 不要太多导致混乱
   - Find the sweet spot / 找到最佳平衡点

### Don'ts / 不要做的

1. **Don't Be Too Vague / 不要太模糊**
   - "Happy song" is not enough / "快乐的歌曲"是不够的
   - Need musical context / 需要音乐语境

2. **Don't Mix Too Many Genres / 不要混合太多流派**
   - One or two genres max / 最多一两个流派
   - More = confused output / 更多 = 困惑的输出

3. **Don't Ignore Platform Limits / 不要忽略平台限制**
   - Each platform has strengths/weaknesses / 每个平台都有优势和弱点
   - Work with, not against / 协作而非对抗

4. **Don't Skip Cultural Context / 不要跳过文化背景**
   - Especially for non-English / 特别是非英语
   - Specify style and era / 指定风格和年代

5. **Don't Expect Perfection First Try / 不要第一次就期望完美**
   - AI music generation is iterative / AI 音乐生成是迭代的
   - Refine and adjust / 优化和调整

## Mureka V8 Advanced Techniques / Mureka V8 高级技巧

### Prompt Iteration Strategy / 提示词迭代策略

**The 5-Step V8 Workflow / V8 五步工作流:**

```
Step 1: Foundation / 第一步：基础
Create a solid base prompt with core elements
创建核心元素的基础提示词

Example / 示例:
"Chinese Pop upbeat 120 BPM female vocals"
"中文 流行 欢快 120 BPM 女声"
```

```
Step 2: Refine / 第二步：优化
Add specific details for uniqueness
添加具体细节以获得独特性

Example / 示例:
"Chinese Mandopop upbeat 120-125 BPM C Major piano electric guitar emotional female vocals modern urban"
"中文 华语流行 欢快 120-125 BPM C大调 钢琴 电吉他 情感女声 现代都市"
```

```
Step 3: V8 Enhancement / 第三步：V8 增强
Add V8-specific features for quality
添加 V8 特有特性以提升质量

Example / 示例:
"Chinese Mandopop upbeat 120-125 BPM C Major piano electric guitar emotional-joyful-hopeful arc emotional female vocals studio-grade production modern urban - Track about overcoming challenges and finding hope"
"中文 华语流行 欢快 120-125 BPM C大调 钢琴 电吉他 情感-欢乐-充满希望弧线 情感女声 录音室级制作 现代都市 - 关于克服挑战和找到希望的歌曲"
```

```
Step 4: Fine-Tune / 第四步：微调
Adjust based on listening results
根据聆听结果调整

Example adjustments / 示例调整:
"Add more energy in chorus" → "High-energy chorus with layered vocals"
"副歌增加能量" → "高能量副歌，层叠人声"

"Softer verses" → "Intimate verses with gentle delivery"
"更柔和主歌" → "亲密主歌，温柔表达"
```

```
Step 5: Polish / 第五步：润色
Final tweaks for perfection
完美化的最终微调

Example / 示例:
"Chinese Mandopop upbeat 120-125 BPM C Major piano electric guitar emotional-joyful-hopeful arc emotional female vocals studio-grade production modern urban with crystal clarity and warm analog undertones - Inspiring track about overcoming challenges, with verses starting intimate and building to euphoric chorus celebration"
"中文 华语流行 欢快 120-125 BPM C大调 钢琴 电吉他 情感-欢乐-充满希望弧线 情感女声 录音室级制作 现代都市 水晶般清晰和温暖模拟底色 - 关于克服挑战的激励歌曲，主歌从亲密开始建立至欣悦副歌庆祝"
```

### Emotion Arc Design / 情感弧线设计

**Understanding Emotional Progression / 理解情感进程:**

```
Linear Progression / 线性进程:
Sad → Reflective → Hopeful → Joyful
悲伤 → 反思 → 充满希望 → 欢乐

CN: 悲伤 → 反思 → 充满希望 → 欢乐

应用场景: Personal growth songs, motivational tracks
应用场景：个人成长歌曲、激励性曲目
```

```
V-Shape Progression / V形进程:
Joyful → Melancholic → Joyful
欢乐 → 忧郁 → 欢乐

CN: 欢乐 → 忧郁 → 欢乐

应用场景: Party anthems with depth, celebration with meaning
应用场景：有深度的派对颂歌、有意义的庆祝
```

```
Inverted V / 倒V形:
Tense → Explosive → Calm
紧张 → 爆发 → 平静

CN: 紧张 → 爆发 → 平静

应用场景: Cinematic tracks, story-driven songs
应用场景：电影感曲目、故事驱动歌曲
```

```
Rolling Wave / 滚动波浪:
Emotional peaks and valleys throughout
整首情感起伏

CN: 整首情感起伏

应用场景: Long-form tracks, progressive genres
应用场景：长篇幅曲目、渐进式流派
```

### Genre Blending Matrix / 流派融合矩阵

**Effective Genre Combinations / 有效流派组合:**

```
East Meets West / 东西相遇:
Chinese folk + Electronic = Ethereal fusion
中国民谣 + 电子 = 空灵融合
K-Pop + Jazz = Sophisticated pop
K-Pop + 爵士 = 精致流行
Japanese rock + Classical = Cinematic rock
日本摇滚 + 古典 = 电影感摇滚

Latin + Asian = Fire fusion
拉丁 + 亚洲 = 火热融合
Salsa + Mandarin = Party bilingual
萨尔萨 + 普通话 = 派对双语
Reggaeton + K-Pop = Dance crossover
雷鬼顿 + K-Pop = 舞曲跨界
```

```
Era Blending / 时代融合:
1980s synth + Modern production = Retro-futurism
1980年代合成器 + 现代制作 = 复古未来主义
1970s disco + 2020s pop = Nostalgic fresh
1970年代迪斯科 + 2020年代流行 = 怀旧清新
Classical + Electronic = Genre evolution
古典 + 电子 = 流派演进

Jazz + Lo-Fi = Contemporary chill
爵士 + 低保真 = 当代轻松
Blues + Rock = Classic fusion
布鲁斯 + 摇滚 = 经典融合
```

```
Mood Contrasts / 情绪对比:
Sad lyrics + Upbeat music = Irony/hope
悲伤歌词 + 欢快音乐 = 讽刺/希望
Dark music + Hopeful vocals = Transformation
黑暗音乐 + 充满希望人声 = 转变
Angry verses + Celebratory chorus = Resolution
愤怒主歌 + 庆祝副歌 = 解决
```

### Cultural Fusion Guidelines / 文化融合指导

**Do's / 要做的:**

```
✅ Respect cultural authenticity
尊重文化真实性

"Authentic Japanese taiko drums with modern production"
"正宗日本太鼓与现代制作"

"Traditional Chinese pentatonic melodies preserved in electronic context"
"传统中国五声音阶旋律在电子语境中保持"
```

```
✅ Educate through fusion
通过融合教育

"Introducing erhu to Western audiences through accessible pop arrangement"
"通过易理解的流行编排向西方听众介绍二胡"
```

```
✅ Highlight collaboration spirit
突出合作精神

"Celebration of cross-cultural friendship and musical exchange"
"庆祝跨文化友谊和音乐交流"
```

**Don'ts / 不要做的:**

```
❌ Avoid stereotypical fusion
避免刻板印象融合

Instead of "generic Asian music with synths"
改为 "generic Asian music with synths"

Use: "Specific Guzheng melodies from Chinese classical tradition in electronic context"
使用："中国古典传统的具体古筝旋律在电子语境中"
```

```
❌ Don't tokenize culture
不要文化符号化

Instead of "exotic Eastern sounds"
改为 "exotic Eastern sounds"

Use: "Authentic shakuhachi flute with traditional Japanese phrasing"
使用："正宗尺八笛，传统日本乐句"
```

```
❌ Avoid superficial mixing
避免肤浅混合

Instead of just listing multiple cultures
改为：只是列出多种文化

Create meaningful fusion with purpose
创建有目的的有意义融合
```

### Vocal Technique Tags / 人声技巧标签

**V8 Voice Engine Tags / V8 人声引擎标签:**

```
🎤 Delivery Style / 表达风格:

"Intimate whisper" - Close-mic, vulnerable
"亲密耳语" - 近距麦克风，脆弱

"Powerful belt" - Full voice, projecting
"强力爆发" - 全音域，投射

"Breathy" - Soft, intimate
"气声" - 柔和，亲密

"Crisp" - Clear articulation
"清晰" - 清晰吐字

"Raw" - Unpolished, emotional
"原始" - 未修饰，情感

"Polished" - Professional, smooth
"精致" - 专业，流畅
```

```
🎭 Emotional Range / 情感范围:

"Vulnerable opening, building to strength"
"脆弱开场，建立至力量"

"Confident throughout with moments of tenderness"
"整首自信，有温柔时刻"

"Cool detachment in verses, passionate in chorus"
"主歌冷静超脱，副歌激情"

"Subtle emotion with restrained power"
"微妙情感，克制力量"
```

```
🌍 Language Specifics / 语言特定:

"Mandarin with clear Beijing accent and standard pronunciation"
"普通话，北京口音清晰，标准发音"

"Cantonese with authentic Hong Kong style and local expressions"
"粤语，正宗香港风格，本地表达"

"Japanese with standard Tokyo accent and polite/formal tone"
"日语，标准东京口音，礼貌/正式语气"

"Korean with Seoul accent, mixing formal and casual as appropriate"
"韩语，首尔口音，适当时混合正式和随意"

"Spanish with clear pronunciation, suitable for Latin American audience"
"西班牙语，发音清晰，适合拉美听众"
```

### Production Engineering / 制作工程

**V8 Production Tags / V8 制作标签:**

```
🎛️ Mixing Style / 混音风格:

"Wall of sound" - Dense, layered, powerful
"声音墙" - 密集，层叠，强力

"Spacious and open" - Airy, room for elements
"宽敞开阔" - 空气感，元素空间

"Intimate and close" - Upfront, personal
"亲密近距" - 前置，个人化

"Cinematic" - Wide, epic, movement
"电影感" - 宽广，史诗，动感

"Clean and precise" - Clarity, separation
"清晰精准" - 清晰度，分离度
```

```
🎵 Dynamic Structure / 动态结构:

"Quiet verses, explosive chorus"
"安静主歌，爆炸性副歌"

"Building energy throughout"
"整首建立能量"

"Intimate sections, big climaxes"
"亲密段落，大高潮"

"Subtle shifts, gradual evolution"
"微妙变化，渐进演变"
```

```
🔊 Frequency Focus / 频率焦点:

"Bass-heavy with punchy low end"
"重低音，有力低频"

"Crystal high frequencies with air"
"水晶般高频，空气感"

"Balanced across spectrum"
"全频段平衡"

"Mid-focused with warmth"
"中频焦点，温暖"
```

### Common Pitfalls & Solutions / 常见陷阱与解决方案

**Pitfall 1: Over-specification / 陷阱1：过度详细**

```
❌ Problem / 问题:
Too many constraints stifle creativity
太多限制抑制创造力

"Chinese Pop 120 BPM C Major 4/4 piano guitar drums bass strings synth female vocals emotional happy sad hopeful nostalgic modern retro production studio quality perfect mix"

✅ Solution / 解决方案:
Focus on key elements, let AI fill in gaps
聚焦关键元素，让 AI 填补空白

"Chinese Pop emotional 120 BPM piano electric guitar female vocals - Modern love ballad with nostalgic undertones"
"中文 流行 情感 120 BPM 钢琴 电吉他 女声 - 现代爱情抒情歌，怀旧底色"
```

**Pitfall 2: Cultural Insensitivity / 陷阱2：文化不敏感**

```
❌ Problem / 问题:
Stereotypical or superficial cultural references
刻板或肤浅的文化引用

"Asian-style music with exotic sounds"

✅ Solution / 解决方案:
Be specific, respectful, and educated
具体、尊重、有教育意义

"Traditional Chinese guzheng with authentic pentatonic melodies in contemporary arrangement"
"传统中国古筝，正宗五声音阶旋律，当代编排"
```

**Pitfall 3: Language Clarity Issues / 陷阱3：语言清晰度问题**

```
❌ Problem / 问题:
Poor pronunciation or awkward phrasing
发音差或乐句尴尬

✅ Solution / 解决方案:
Specify accent and pronunciation style
指定口音和发音风格

"Mandarin vocals with standard pronunciation and clear articulation, suitable for general Chinese audience"
"普通话人声，标准发音和清晰吐字，适合一般中文听众"
```

**Pitfall 4: Genre Confusion / 陷阱4：流派混乱**

```
❌ Problem / 问题:
Too many genres create muddy output
太多流派创造模糊输出

"Pop rock jazz classical electronic blues folk"

✅ Solution / 解决方案:
Choose primary genre, others as influence
选择主要流派，其他作为影响

"Pop dominant with rock energy and jazz harmonies in chord progressions"
"流行主导，摇滚能量，和弦进行中爵士和声"
```

**Pitfall 5: Emotion Mismatch / 陷阱5：情绪不匹配**

```
❌ Problem / 问题:
Lyrics don't match musical emotion
歌词与音乐情绪不匹配

"Happy upbeat music about heartbreak and depression"

✅ Solution / 解决方案:
Align all elements to same emotional direction
所有元素对齐相同情感方向

"Melancholic piano ballad about heartbreak with emotional vocals"
"忧郁钢琴抒情歌关于心碎，情感人声"

OR / 或

"Uplifting pop about overcoming heartbreak and finding new hope"
"振奋流行关于克服心碎和找到新希望"
```

### V8 Pro Tips / V8 专业技巧

**1. Use Version History / 使用版本历史**

```
Keep track of prompt iterations to refine over time
跟踪提示词迭代以随时间优化

v1: Basic pop song
v1: 基础流行歌曲

v2: Added emotion and vocals
v2: 添加情绪和人声

v3: Refined instrumentation and production
v3: 优化乐器和制作

v4: Final polished version
v4: 最终润色版本
```

**2. A/B Test Different Approaches / A/B 测试不同方法**

```
Test similar prompts with one element changed
测试相似提示词，改变一个元素

Prompt A: "Chinese Pop emotional 95 BPM"
提示词 A："中文 流行 情感 95 BPM"

Prompt B: "Chinese Rock ballad 95 BPM"
提示词 B："中文 摇滚 抒情 95 BPM"

Compare outputs to understand AI's strengths and weaknesses
比较输出以了解 AI 的优势和弱点
```

**3. Build Prompt Library / 建立提示词库**

```
Create reusable prompt templates for different needs
为不同需求创建可重用提示词模板

📁 Ballad Prompts / 抒情歌提示词
📁 Dance Prompts / 舞曲提示词
📁 Fusion Prompts / 融合提示词
📁 Language-Specific Prompts / 语言特定提示词
📁 Mood-Based Prompts / 基于情绪的提示词
```

**4. Leverage V8's Cultural Intelligence / 利用 V8 的文化智能**

```
V8 understands cultural context better than previous versions
V8 比以前版本更好地理解文化语境

Use this for authentic fusion
用此创建真实融合

"Traditional Chinese New Year celebration song with modern production, preserving cultural authenticity while appealing to contemporary audience"
"传统春节庆祝歌曲，现代制作，保持文化真实同时吸引当代听众"
```

**5. Experiment with Emotional Timelines / 实验情感时间线**

```
Map out the emotional journey before prompting
在提示词之前绘制情感旅程

0:00-0:30: Introduce theme (melancholic)
0:00-0:30：引入主题（忧郁）

0:30-1:00: Build tension
0:30-1:00：建立张力

1:00-1:30: Release (hopeful)
1:00-1:30：释放（充满希望）

1:30-2:00: Resolution (joyful)
1:30-2:00：解决（欢乐）

Then translate to prompt:
然后翻译为提示词：
"Emotional arc: melancholic introduction building to hopeful release and joyful resolution"
"情感弧线：忧郁开场建立至充满希望释放和欢乐解决"
```

**6. Use Reference Tracks Effectively / 有效使用参考曲目**

```
Instead of copying, extract principles
不复制，提取原则

Instead of: "Like Taylor Swift's 'Shake It Off'"
改为："Like Taylor Swift's 'Shake It Off'"

Use: "Upbeat pop with catchy hooks and confident female vocals, similar energy to Taylor Swift's uptempo tracks"
使用："欢快流行，朗朗上口的钩子和自信女声，类似 Taylor Swift 快速曲目的能量"
```

## Quick Reference Card / 快速参考卡

### V8 Prompt Template / V8 提示词模板
```
[Language] [Primary Genre] [+ Optional Secondary Genre] [Mood Arc] [Tempo] [Key] [Time Signature] [Instruments] [Vocal Style] [Production Style] [Cultural Context] - [Detailed Description]

[语言] [主要流派] [+ 可选次要流派] [情感弧线] [速度] [调性] [拍号] [乐器] [人声风格] [制作风格] [文化背景] - [详细描述]
```

### Genre Quick List / 流派快速列表
```
Pop, Rock, Electronic, Hip-Hop, Jazz, Classical, R&B, Country, Metal, Folk, Reggae, Ambient
流行、摇滚、电子、嘻哈、爵士、古典、R&B、乡村、金属、民谣、雷鬼、氛围
```

### Mood Quick List / 情绪快速列表
```
Positive: Joyful, Uplifting, Celebratory / 积极：喜悦、振奋、庆祝
Sad: Melancholic, Heartbreaking, Reflective / 悲伤：忧郁、心碎、反思
Dark: Ominous, Mysterious, Haunting / 黑暗：不祥、神秘、挥之不去
Intense: Dramatic, Fierce, Explosive / 强烈：戏剧性、凶猛、爆发
Calm: Peaceful, Soothing, Ethereal / 平静：安宁、安慰、空灵
Romantic: Passionate, Yearning, Sweet / 浪漫：热情、渴望、甜美
```

### Tempo Guide / 速度指南
```
Slow: 60-80 BPM / 慢速
Mid-slow: 80-100 BPM / 中慢
Mid: 100-120 BPM / 中速
Mid-fast: 120-140 BPM / 中快
Fast: 140+ BPM / 快速
```

## Mureka V8 Case Studies / Mureka V8 案例研究

### 案例1: 中国流行歌的国际化升级 / International Upgrade of Chinese Pop Song

**背景 / Background:**
一位中国歌手想要将一首传统中文抒情歌升级为国际化的亚洲流行歌曲，适合在 Spotify 和 Apple Music 上发布。

**原提示词 / Original Prompt:**
```
中文 情情歌 慢速 女声 - 关于思念的爱情歌
```

**V8 优化过程 / V8 Optimization Process:**

**版本 1 - 添加细节 / Add Details:**
```
中文 抒情歌 95 BPM 钢琴 弦乐 女声 - 关于异地恋的思念情歌
```

**版本 2 - 添加文化背景 / Add Cultural Context:**
```
中文 流行抒情歌 95 BPM C大调 钢琴 弦乐 现代都市感 情感女声 - 现代都市背景的异地恋情歌，融合传统情感表达与当代流行制作
```

**版本 3 - V8 优化 / V8 Optimized:**
```
中文 流行音乐 + 电子 + 氛围 情感-思念-希望 88-105 BPM C大调 4/4拍
情绪时间线：忧郁(0:00-0:45) → 焦虑思念(0:45-1:30) → 渴望(1:30-2:15) → 充满希望(2:15-3:00)
分段编排：
0:00-0:45：主歌 - 极简钢琴和轻柔女声，亲密感
0:45-1:30：预副歌 - 加入电子纹理和轻微节奏，建立张力
1:30-2:15：副歌 - 完整编排，钢琴+弦乐+电子氛围，情感爆发
2:15-3:00：桥段和结尾 - 管弦乐高潮，逐渐平静至充满希望
人声：中文女声，次女高音，主歌耳语式，副歌爆发式
制作：V8最高质量，录音室级混音和母带处理
文化元素：现代中文流行，隐含传统情感表达方式
- 一首现代中文异地恋情歌，讲述思念与坚持的故事，通过V8的情绪映射系统展现从忧郁到希望的情感旅程，适合亚洲流行音乐市场

V8 Features Used / 使用的V8特性：
- Emotion Timeline / 情绪时间线
- Section-Specific Instrumentation / 分段乐器编排
- V8 Maximum Quality / V8最高质量
- Cultural Intelligence / 文化智能
```

**成果 / Results:**
- 歌曲在流媒体平台获得了更好的制作质量
- 情感层次更加丰富，吸引更广泛的听众
- 保持了中文文化特色，同时具有国际吸引力

### 案例2: 多语言品牌主题曲 / Multilingual Brand Theme Song

**背景 / Background:**
一个亚洲科技品牌需要一首主题曲，要在多个市场（中国、日本、韩国、东南亚）使用，需要体现创新和全球化的品牌形象。

**V8 优化提示词 / V8 Optimized Prompt:**

```
多语言主题曲 中文-日文-韩文-英文 四语言
电子 + 流行 + 管弦乐 现代-创新-充满希望 128 BPM G大调 4/4拍

语言分布：
主歌1（0:00-0:30）：中文普通话，科技前沿的感觉
主歌2（0:30-1:00）：日文，精致和优雅
副歌（1:00-1:45）：四语言合唱，"Innovation for tomorrow"
主歌3（1:45-2:15）：韩文，活力和进取
桥段（2:15-2:45）：英文，连接和协作
最终副歌（2:45-3:30）：四语言混音，高潮和团结

情绪弧线：
好奇(0:00-0:30) → 激励(0:30-1:00) → 自信(1:00-1:45) → 充满活力(1:45-2:15)
→ 协作(2:15-2:45) → 庆祝和胜利(2:45-3:30)

乐器编排：
0:00-0:45：未来感合成器，轻巧节奏，科技氛围
0:45-1:45：完整电子编排，节奏强劲，现代感
1:45-2:15：加入传统亚洲乐器元素（古筝、琴）微妙纹理
2:15-3:30：完整管弦乐+电子，史诗感

人声：
主歌：各种语言的男女声，现代流行风格
副歌：四语言混音，和声层叠，力量感
桥段：英文说唱，快速节奏，能量爆发

制作：
V8最高质量，录音室级制作
商业级混音，适合电台和流媒体
频率平衡，适合各种播放设备

文化智能：
融合亚洲音乐传统（五声音阶微妙元素）与现代电子
尊重各语言文化特色
全球视野，亚洲根基

- 一首创新科技品牌的四语言主题曲，通过V8的高级多语言引擎和文化智能系统，创造统一而多元的音乐体验，展现品牌的创新精神和全球视野

V8 Features Used / 使用的V8特性：
- V8 Advanced Vocal Engine (multilingual) / V8高级人声引擎（多语言）
- Cultural Intelligence (Asia fusion) / 文化智能（亚洲融合）
- Genre Fusion (Electronic + Pop + Orchestral) / 流派融合（电子+流行+管弦乐）
- V8 Production Quality Engine / V8制作质量引擎
- Emotion Mapping 2.0 / 情绪映射2.0
```

**成果 / Results:**
- 一首歌在多个亚洲市场都能产生情感共鸣
- 品牌形象统一，同时尊重各市场文化差异
- 流媒体和广告表现优异

## Mureka V8 常见问题解答 / Mureka V8 FAQ

### Q1: V8和之前的Mureka版本有什么主要区别？
### Q1: What are the main differences between V8 and previous Mureka versions?

**A:** V8的三大核心升级 / **A:** V8's Three Core Upgrades:

1. **Multilingual Native Support / 多语言原生支持**
   - 之前版本：英语为主，其他语言为辅
   - V8：20+语言原生支持，发音自然

2. **Cultural Intelligence Engine / 文化智能引擎**
   - 之前版本：基于模板的文化元素
   - V8：真正的文化理解和融合能力

3. **Emotion Mapping 2.0 / 情绪映射2.0**
   - 之前版本：单一情绪标签
   - V8：情绪时间线和微表情控制

### Q2: 如何在V8中实现真正的文化融合？
### Q2: How to achieve authentic cultural fusion in V8?

**A:** 关键步骤 / **A:** Key Steps:

1. **理解文化根源 / Understand Cultural Roots**
   - 学习目标文化的历史和传统
   - 理解音乐的哲学和精神内涵

2. **使用V8文化智能 / Use V8 Cultural Intelligence**
   - 指定文化融合等级（Level 1-4）
   - 让V8处理复杂的文化元素

3. **尊重而非挪用 / Respect, Don't Appropriate**
   - 避免表面化的文化装饰
   - 与文化专家合作验证

4. **目标Level 3或4 / Aim for Level 3 or 4**
   - Level 3: Deep Cultural Understanding / 深层文化理解
   - Level 4: Authentic Integration / 真正融合

### Q3: V8的情绪时间线如何工作？
### Q3: How does V8's emotion timeline work?

**A:** 格式和用法 / **A:** Format and Usage:

```
格式 / Format:
[Emotion Timeline: emotion(time-time) → emotion(time-time)]

示例 / Example:
"情绪时间线：忧郁(0:00-0:45) → 焦虑(0:45-1:15) → 充满希望(1:15-2:00)"

工作原理 / How It Works:
- V8理解时间标记
- 自动调整音乐元素支持情绪变化
- 保持情绪间的自然过渡
```

### Q4: 如何优化V8的多语言人声？
### Q4: How to optimize V8's multilingual vocals?

**A:** V8人声工程最佳实践 / **A:** V8 Vocal Engineering Best Practices:

1. **明确语言分布 / Specify Language Distribution**
   - 哪些部分用什么语言
   - 过渡如何发生

2. **指定人声特征 / Specify Vocal Characteristics**
   - 声音类型、音域、表达风格
   - 分段变化（主歌vs副歌）

3. **使用V8干湿控制 / Use V8 Dry/Wet Control**
   - 主歌：较高干信号（70-90%）
   - 副歌：较低干信号（20-40%）

4. **文化发音准确性 / Cultural Pronunciation Accuracy**
   - 指定方言或口音
   - "标准普通话"、"正宗粤语"等

### Q5: V8最适合什么使用场景？
### Q5: What use cases is V8 best suited for?

**A:** V8优势场景 / **A:** V8 Advantage Scenarios:

```
✅ V8最擅长 / V8 Excels At:

1. 多语言音乐制作 / Multilingual Music Production
   - 跨国品牌主题曲
   - 亚洲流行音乐
   - 多语言合作歌曲

2. 文化融合音乐 / Cultural Fusion Music
   - 传统艺术复兴
   - 跨文化音乐项目
   - 全球化本地化音乐

3. 情感丰富的叙事音乐 / Emotionally Rich Narrative Music
   - 电影原声
   - 游戏音乐
   - 情感抒情歌

4. 高质量商业制作 / High-Quality Commercial Production
   - 流媒体发行音乐
   - 广告音乐
   - 品牌音乐

⚠️ V8可能过度 / V8 Might Be Overkill For:

简单演示demo / Simple demo songs
纯器乐作品 / Purely instrumental pieces
单语言标准流行歌 / Single-language standard pop songs
```

### Q6: 如何提高V8提示词的质量？
### Q6: How to improve V8 prompt quality?

**A:** V8提示词质量提升指南 / **A:** V8 Prompt Quality Improvement Guide:

```
Level 1: 基础 / Basic
[Language] [Genre] [Mood] - [Description]

Level 2: 详细 / Detailed
[Language] [Genre] [Mood] [Tempo] [Instruments] [Vocals] - [Description]

Level 3: V8标准 / V8 Standard
[Language] [Genre Fusion] [Emotion Timeline] [Tempo] [Instruments] [Vocals]
[Section-Specific Details] [Production Quality] - [Detailed Description]

Level 4: V8优化 / V8 Optimized
包含所有Level 3元素，加上：
- 完整的文化智能描述
- 精确的人声工程参数
- 详细的分段乐器编排
- 完整的情绪旅程设计
- V8独有特性的充分利用

目标：从Level 1逐步升级到Level 4
Goal: Progressively upgrade from Level 1 to Level 4
```

### Q7: V8支持哪些语言？
### Q7: What languages does V8 support?

**A:** V8多语言支持列表 / **A:** V8 Multilingual Support List:

```
亚洲语言 / Asian Languages:
- 普通话 (Mandarin Chinese)
- 粤语 (Cantonese)
- 日语 (Japanese)
- 韩语 (Korean)
- 泰语 (Thai)
- 越南语 (Vietnamese)
- 印尼语 (Indonesian)
- 马来语 (Malay)

欧洲语言 / European Languages:
- 英语 (English)
- 法语 (French)
- 德语 (German)
- 西班牙语 (Spanish)
- 意大利语 (Italian)
- 葡萄牙语 (Portuguese)

其他语言 / Other Languages:
- 阿拉伯语 (Arabic)
- 印地语 (Hindi)
- 其他20+语言 / 20+ other languages

注意：所有语言都支持原生发音 / Note: All languages support native pronunciation
```

### Q8: V8的实时迭代如何工作？
### Q8: How does V8's real-time iteration work?

**A:** 迭代工作流程 / **A:** Iteration Workflow:

```
1. 创建初始提示词 / Create Initial Prompt
   → 生成版本1 / Generate Version 1

2. 听取和分析 / Listen and Analyze
   → 识别问题/改进机会 / Identify issues/improvements

3. 创建版本2 / Create Version 2
   → 添加/修改元素 / Add/modify elements
   → 生成版本2 / Generate Version 2

4. 比较版本 / Compare Versions
   → V8显示版本差异 / V8 shows version differences
   → 选择最佳元素 / Select best elements

5. 继续迭代直到满意 / Continue iterating until satisfied

V8优势 / V8 Advantage:
- 版本历史自动保存
- 快速生成和比较
- 容易回滚到之前版本
```

### Q9: 如何避免文化不敏感的内容？
### Q9: How to avoid culturally insensitive content?

**A:** 文化尊重指南 / **A:** Cultural Respect Guidelines:

```
❌ 避免 / Avoid:
- 表面化的文化装饰
- 刻板印象
- 文化挪用（未经许可使用）
- 不准确的文化元素

✅ 做到 / Do:
- 学习目标文化
- 与文化专家合作
- 使用V8文化智能系统
- 尊重文化传统和精神
- 寻求文化顾问的反馈

V8帮助 / V8 Helps:
- 文化智能系统
- 文化融合等级指导
- 真正融合vs表面装饰的区别
```

### Q10: V8和其他AI音乐平台相比有什么优势？
### Q10: What are V8's advantages compared to other AI music platforms?

**A:** V8核心优势 / **A:** V8 Core Advantages:

```
🎯 vs Suno / 相比Suno:
V8优势：真正的多语言支持、文化智能、情绪时间线
Suno强项：流行、摇滚、电子音乐

🎯 vs Udio / 相比Udio:
V8优势：多语言、文化融合、情绪映射
Udio强项：爵士、古典、复杂编排

🎯 vs 其他平台 / 相比其他平台:
V8优势：完整的多语言文化音乐生态系统
V8特色：专为亚洲和全球化市场设计

选择建议 / Recommendation:
- 纯英语流行歌：Suno
- 爵士/古典：Udio
- 多语言/文化融合：V8（最强）
- 复杂叙事：V8
```

## Additional Resources / 其他资源

### Reference Documents / 参考文档
- [Genre-Specific Prompt Patterns](references/genre-patterns.md) - Detailed prompt structures for each major genre / 每个主要流派的详细提示词结构
- [Lyric Writing Techniques](references/lyrics.md) - Advanced lyrical composition strategies / 高级歌词创作策略
- [Production Reference Guide](references/production.md) - Mixing and production terminology for prompts / 混音和制作术语

### Recommended Reading / 推荐阅读
- AI music generation best practices / AI 音乐生成最佳实践
- Music theory for songwriters / 词曲作者的音乐理论
- Cross-cultural music fusion techniques / 跨文化音乐融合技巧

### Community Resources / 社区资源
- Mureka V8 documentation / Mureka V8 文档
- Suno and Udio community forums / Suno 和 Udio 社区论坛
- AI music creation communities / AI 音乐创作社区

---

**Note:** This skill supports both English and Chinese prompts. Feel free to use either language or combine both for bilingual music generation.
**注意：**此技能支持英文和中文提示词。可以自由使用任一语言或结合两者进行双语音乐生成。
