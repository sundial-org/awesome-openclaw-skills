---
name: crypto-gold-monitor
description: "加密货币与贵金属价格监控 / Crypto & Precious Metals Price Monitor - 监控BTC/ETH实时价格、黄金(XAU)/白银(XAG)走势，免费API无需Key"
---

# 加密货币与贵金属价格监控 / Crypto & Precious Metals Price Monitor

实时监控比特币、以太坊、黄金、白银价格走势，支持多币种对比和价格提醒。

Real-time monitoring of Bitcoin, Ethereum, Gold, and Silver prices with multi-currency comparison.

## 功能特性 / Features

- ₿ **比特币 / Bitcoin** - 实时价格 (USD/CNY)、24h涨跌
  - Real-time price (USD/CNY), 24h change

- Ξ **以太坊 / Ethereum** - 实时价格 (USD/CNY)、24h涨跌
  - Real-time price (USD/CNY), 24h change

- 🥇 **黄金 / Gold** - XAU/USD 实时价格 (USD/CNY)
  - Gold XAU/USD real-time price (USD/CNY)

- 🥈 **白银 / Silver** - XAG/USD 实时价格 (USD/CNY)
  - Silver XAG/USD real-time price (USD/CNY)

- 💱 **汇率显示 / Exchange Rate** - 实时USD/CNY汇率
  - Real-time USD/CNY exchange rate

- 📊 **价格对比 / Comparison** - 对比多个资产表现
  - Compare multiple asset performance

- 📈 **涨跌幅排行 / Rankings** - 24h涨跌幅排名
  - 24h change rate rankings

- 🔔 **价格提醒 / Alerts** - 设置价格阈值提醒
  - Set price threshold alerts

## 使用方法 / Usage

### 1. 查看所有价格 / View All Prices
```bash
crypto-monitor all
```

### 2. 查看加密货币 / View Crypto
```bash
# 查看比特币
crypto-monitor btc

# 查看以太坊
crypto-monitor eth

# 查看两者
crypto-monitor crypto
```

### 3. 查看贵金属 / View Precious Metals
```bash
# 查看黄金
crypto-monitor gold

# 查看白银
crypto-monitor silver

# 查看两者
crypto-monitor metals
```

### 4. 价格对比 / Price Comparison
```bash
crypto-monitor compare btc eth
```

### 5. 涨跌幅排行 / Rankings
```bash
crypto-monitor rankings
```

### 6. 设置价格提醒 / Set Price Alert
```bash
# 当比特币跌破90000美元时提醒
crypto-monitor alert btc below 90000

# 当以太坊涨破3500美元时提醒
crypto-monitor alert eth above 3500
```

### 7. 刷新频率 / Refresh Rate
```bash
# 刷新间隔30秒（默认60秒）
crypto-monitor all --interval 30
```

## 数据来源 / Data Sources

### 加密货币 / Crypto
- **CoinGecko API** (免费，无需API Key)
- 无请求限制 / No rate limits

### 贵金属 / Precious Metals
- **GoldAPI.io** (免费额度有限)
- 或使用备用数据源

## 注意事项 / Notes

⚠️ 价格数据可能有15-60秒延迟
⚠️ Price data may have 15-60 seconds delay

⚠️ 贵金属API可能有每日请求限制
⚠️ Precious Metals API may have daily request limits

⚠️ 投资有风险，数据仅供参考
⚠️ Investment involves risk, data for reference only

## 常见问题 / FAQ

**Q: 需要API Key吗？**
A: 不需要，CoinGecko免费API无需Key。

**Q: 黄金白银价格准确吗？**
A: 使用多个数据源交叉验证。

**Q: 可以监控其他币种吗？**
A: 可扩展支持更多加密货币。
