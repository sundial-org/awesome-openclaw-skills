# Contributing to Feishu Doc Reader

感谢你对本项目的关注！欢迎提交 Issue 和 Pull Request。

## 开发环境设置

### 1. 克隆仓库

```bash
git clone https://github.com/your-username/feishu-doc-reader.git
cd feishu-doc-reader
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 配置飞书应用凭证

复制示例配置文件并填入你的飞书应用凭证：

```bash
cp reference/feishu_config_sample.json reference/feishu_config.json
chmod 600 reference/feishu_config.json
```

编辑 `reference/feishu_config.json`，填入你的 `app_id` 和 `app_secret`。

**注意**：`reference/feishu_config.json` 已被 `.gitignore` 忽略，不会被提交到版本控制。

## 代码规范

### Python 代码

- 遵循 PEP 8 代码风格
- 使用有意义的变量名和函数名
- 添加适当的注释和文档字符串
- 保持函数简短，单一职责

### Shell 脚本

- 在脚本开头使用 `set -e` 或 `set -euo pipefail`
- 添加使用说明和示例
- 验证必要的参数

### 提交信息

- 使用清晰、描述性的提交信息
- 遵循约定式提交（Conventional Commits）格式：
  - `feat: 添加新功能`
  - `fix: 修复问题`
  - `docs: 更新文档`
  - `refactor: 重构代码`
  - `test: 添加测试`

## 提交 Pull Request

1. Fork 本仓库
2. 创建你的特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交你的更改 (`git commit -m 'feat: 添加某个功能'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 打开一个 Pull Request

### PR 检查清单

- [ ] 代码通过了本地测试
- [ ] 更新了相关文档
- [ ] 没有引入敏感信息（如密钥、个人路径等）
- [ ] 代码风格符合项目规范

## 安全注意事项

- **永远不要**在代码中硬编码凭证
- **永远不要**提交 `reference/feishu_config.json` 文件
- 在日志中避免输出敏感信息
- 使用相对路径而非硬编码的绝对路径

## 报告问题

如果你发现了 bug 或有功能建议，请通过 GitHub Issues 提交，并包含：

- 问题的详细描述
- 重现步骤（如果是 bug）
- 预期行为和实际行为
- 你的运行环境（Python 版本、操作系统等）

## 许可证

通过贡献代码，你同意你的贡献将按照 MIT 许可证进行授权。
