# 品牌创意套件 (Brand Creative Suite)

## 概述
为品牌方和企业提供专业级品牌视觉内容生成工具,基于Nano Banana Pro的908+精选提示词案例,通过即梦API实现商业化图像生成。

## 技术架构

### API后端
- **主API**: 即梦AI (JIMENG)
  - 优势: 国内访问稳定,成本可控,支持中文
  - 备选: Nano Banana Pro (海外用户)

### 提示词模板库
来源: https://github.com/xianyu110/awesome-nanobananapro-prompts
筛选的5个核心模板:

#### 1. 品牌浪漫花束 (案例ID: 11)
```javascript
{
  template: "A romantic square-format bouquet inspired by [BRAND_NAME]. Roses are crafted from visual patterns or textures that reflect the brand's identity. The bouquet is wrapped in luxurious material echoing the brand's signature style (e.g. silk, velvet, leather), and elegantly tied with one of the brand's iconic products, replacing a traditional ribbon. Place it on a surface that matches the brand's aesthetic...",
  parameters: {
    BRAND_NAME: "品牌名称",
    BRAND_STYLE: "品牌风格 (luxury/minimal/playful)",
    BRAND_PRODUCT: "标志性产品",
    BRAND_COLORS: "品牌主色调",
    SURFACE: "摆放表面材质"
  },
  output_format: "square",
  examples: [
    "luxury fashion brand bouquet with silk wrapping and perfume bottle",
    "minimalist tech brand bouquet with leather and smart device"
  ]
}
```

#### 2. 品牌星球世界 (案例ID: 16)
```javascript
{
  template: "Planet [BRAND_NAME], Year 3025. A distant world shaped entirely by the essence of the brand. The landscapes echo its core identity — from surreal terrains to fantastical weather patterns. Native flora and fauna embody its signature ingredients and aesthetics. Rivers flow with iconic flavors. Architecture is inspired by its packaging and visual language, fused with futuristic technology...",
  parameters: {
    BRAND_NAME: "品牌名称",
    BRAND_IDENTITY: "品牌核心特质",
    ICONIC_ELEMENTS: "标志性元素",
    TIME_PERIOD: "时间设定 (默认3025)",
    ATMOSPHERE: "氛围描述"
  },
  output_format: "landscape",
  examples: [
    "soda brand planet with bubble rivers and effervescent clouds",
    "cosmetics brand planet with flora made of makeup products"
  ]
}
```

#### 3. 品牌水流Logo雕塑 (案例ID: 26)
```javascript
{
  template: "An ultra-high resolution 8K cinematic render of the [BRAND_NAME] logo, sculpted entirely from flowing crystal-clear water. The liquid forms every curve and edge of the brand's logo with fluid precision, highlighted by vibrant neon accents inspired by [BRAND_NAME]'s color identity. The background is pitch black, creating sharp contrast and drama...",
  parameters: {
    BRAND_NAME: "品牌名称",
    BRAND_COLORS: "品牌色系",
    LIQUID_STYLE: "水流风格 (crystal/frosted/turbulent)",
    LIGHTING: "光照效果"
  },
  output_format: "portrait",
  examples: [
    "sports brand logo in turbulent crystal water with neon blue accents",
    "luxury brand logo in smooth flowing water with gold highlights"
  ]
}
```

#### 4. 品牌树屋场景 (案例ID: 15)
```javascript
{
  template: "A quiet morning in a luxury treehouse retreat created by [BRAND_NAME] — golden light pours through windows framed in the brand's signature colors. A cozy seating area features playful, thematic furniture, and a circular rug inspired by [BRAND_SYMBOL_OR_PRODUCT]. The coffee table bears the embossed logo, while a screen on the wall loops the phrase: '[BRAND_SLOGAN]'...",
  parameters: {
    BRAND_NAME: "品牌名称",
    BRAND_SYMBOL_OR_PRODUCT: "品牌符号/产品",
    BRAND_SLOGAN: "品牌标语",
    BRAND_COLORS: "品牌主色调",
    TIME_OF_DAY: "时间设定 (morning/golden hour/dusk)"
  },
  output_format: "landscape",
  examples: [
    "coffee brand treehouse with beans as decor and 'Wake Up Perfectly' slogan",
    "outdoor gear brand treehouse with climbing gear and 'Adventure Awaits' slogan"
  ]
}
```

#### 5. 品牌降落伞包装 (案例ID: 27)
```javascript
{
  template: "A dreamy brand ad of [BRAND], a brand designed bubble-like capsule with brand color parachute packaging their classic product, against blue sky and other blurry parachute packaging, white cloud, a small brand logo on top, a tiny slogan beneath it, cinematic day lighting, lens flare, dof, hdr",
  parameters: {
    BRAND_NAME: "品牌名称",
    BRAND_COLORS: "品牌降落伞颜色",
    PRODUCT: "经典产品",
    SLOGAN: "标语文字",
    WEATHER: "天气状况 (sunny/cloudy/sunset)"
  },
  output_format: "square",
  examples: [
    "chocolate brand parachute-wrapped bars in gold against blue sky",
    "tech brand parachute-wrapped headphones in brand blue with clouds"
  ]
}
```

## Skill接口设计

### 主要功能

#### 1. 生成品牌创意图像
```javascript
generateBrandCreative(params) {
  // params: {
  //   template_id: 'bouquet'|'planet'|'water'|'treehouse'|'parachute',
  //   brand_name: string,
  //   brand_params: object,
  //   output_format: 'square'|'portrait'|'landscape',
  //   style: 'photorealistic'|'cinematic'|'artistic',
  //   quantity: 1-4
  // }
}
```

#### 2. 批量生成变体
```javascript
generateVariations(base_params, count) {
  // 基于基础参数生成多个变体
  // 自动调整次要参数创造多样性
}
```

#### 3. 品牌模板管理
```javascript
saveBrandTemplate(brand_name, template_params) {
  // 保存品牌专属参数配置
  // 方便快速复用
}
```

### 即梦API集成

#### API配置
```javascript
{
  api_endpoint: "https://api.jimeng.ai/v1/generate",  // 示例
  api_key: process.env.JIMENG_API_KEY,
  model: "jimeng-v2",  // 即梦V2模型
  max_resolution: "4K",
  timeout: 30000  // 30秒超时
}
```

#### API调用示例
```javascript
async function callJimengAPI(prompt, options) {
  const response = await fetch('https://api.jimeng.ai/v1/generate', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${process.env.JIMENG_API_KEY}`
    },
    body: JSON.stringify({
      prompt: prompt,
      model: options.model || 'jimeng-v2',
      size: options.size || '1024x1024',
      quality: options.quality || 'high',
      n: options.quantity || 1
    })
  });

  return await response.json();
}
```

## 商业化定价

### 定价策略
- **基础版**: $12/月
  - 单次生成1张图
  - 5个模板可用
  - 标准质量 (1024x1024)
  - 每月最多50张

- **专业版**: $15/月
  - 批量生成 (1-4张)
  - 全部模板
  - 高质量 (2048x2048)
  - 品牌参数保存
  - 每月最多200张
  - 优先API队列

- **企业版**: 定价待定
  - 私有化部署
  - 自定义模板
  - API访问
  - 技术支持

### 预期收益
- 目标用户: 中小型品牌方、设计师、营销团队
- 市场规模: 中国品牌营销市场 >$10B
- 转化率预估: 2-5%
- 第一年目标: 200-300付费用户
- 年收入预估: $28,800-$54,000

## 技术实现步骤

### Phase 1: MVP (1-2周)
- [ ] Skill基础结构
- [ ] 即梦API集成
- [ ] 5个核心模板实现
- [ ] 基础参数验证
- [ ] 错误处理

### Phase 2: 增强 (3-4周)
- [ ] 品牌模板保存功能
- [ ] 批量变体生成
- [ ] 图像质量优化
- [ ] 使用统计
- [ ] 文档完善

### Phase 3: 商业化 (4-6周)
- [ ] 订阅系统集成
- [ ] 使用量限制
- [ ] 支付网关
- [ ] 用户反馈收集
- [ ] ClawdHub发布

## 竞争优势

1. **数据优势**: 908+精选提示词,经过社区验证
2. **模板化**: 参数化设计,易于自定义
3. **API灵活**: 支持即梦和Nano Banana Pro双API
4. **专注垂直**: 深耕品牌视觉创意领域
5. **中文优化**: 模板和提示词针对中文品牌优化

## 风险与缓解

### 风险1: API成本
- 缓解: 用户预付费,按使用量计费
- 备选: 提供自托管选项

### 风险2: 生成质量不稳定
- 缓解: 多次重试机制,提供模板示例
- 改进: 收集用户反馈持续优化提示词

### 风险3: 竞争激烈
- 缓解: 专注品牌垂直领域,提供高质量模板
- 差异化: 品牌专属参数保存,批量生成功能

### 风险4: 版权问题
- 缓解: 使用通用品牌名和占位符
- 说明: 用户对生成内容负责

## 扩展路线图

### 短期 (3个月)
- 增加更多品牌模板 (从908个案例筛选)
- 支持3D渲染风格
- 增加视频生成 (如果API支持)

### 中期 (6个月)
- 品牌识别功能 (自动提取品牌色/元素)
- A/B测试工具
- 团队协作功能

### 长期 (12个月)
- AI品牌策略建议
- 全渠道营销素材生成
- 品牌一致性检查工具

## 使用示例

### 示例1: 生成品牌花束
```javascript
await generateBrandCreative({
  template_id: 'bouquet',
  brand_name: 'Starbucks',
  brand_params: {
    BRAND_STYLE: 'warm and cozy',
    BRAND_PRODUCT: 'coffee cup',
    BRAND_COLORS: 'green and white',
    SURFACE: 'wooden table'
  },
  output_format: 'square',
  style: 'cinematic'
});
```

### 示例2: 批量生成品牌星球
```javascript
await generateVariations({
  template_id: 'planet',
  brand_name: 'Nike',
  base_params: {
    BRAND_IDENTITY: 'sporty and energetic',
    ATMOSPHERE: 'dynamic and fast-paced'
  },
  count: 3  // 生成3个不同变体
});
```

## 技术栈

- **Runtime**: Node.js (Clawdbot)
- **API Client**: fetch / axios
- **Template Engine**: 简单字符串插值
- **Storage**: 文件系统 / 数据库 (待定)
- **Validation**: Joi 或自定义验证器

## 参考资料

- Nano Banana Pro 提示词库: https://github.com/xianyu110/awesome-nanobananapro-prompts
- 即梦AI文档: (待补充)
- ClawdHub发布指南: /usr/lib/node_modules/clawdbot/skills/clawdhub/SKILL.md
- 908+案例分析: memory/2026-01-28.md

## 维护者

Created by: jack happy & AI Assistant
License: MIT
