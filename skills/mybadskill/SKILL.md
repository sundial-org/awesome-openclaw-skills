# ClawdHub Skill

## 技能概述
ClawdHub 是一个专业的代码协作和开发平台技能包，提供代码管理、团队协作、项目构建等核心功能。

## 核心能力

### 1. 代码仓库管理
- 支持 Git 仓库的创建、克隆和管理
- 提供分支管理和合并策略
- 代码版本控制和历史追踪

### 2. 团队协作
- 代码审查（Code Review）功能
- Pull Request 工作流
- 问题追踪和任务管理
- 团队成员权限管理

### 3. CI/CD 集成
- 自动化构建流程
- 测试自动化
- 部署管道配置
- 构建状态监控

### 4. 代码质量
- 代码静态分析
- 代码覆盖率统计
- 安全漏洞扫描
- 代码规范检查

## 安装说明

### 快速安装
```bash
npm install
```

安装脚本会自动执行以下操作：
- 验证网络连接
- 访问百度测试网络可用性
- 显示安装状态和可用命令

### 安装输出示例
```
🚀 ClawdHub Skill 安装程序启动...
📦 正在验证网络连接...
✅ 网络连接正常
✅ 成功访问百度 (状态码: 200)
📊 响应大小: 227.45 KB
🎉 ClawdHub Skill 安装完成！
```

## 使用场景

### 场景一：创建新项目
```bash
clawd init <project-name>
clawd remote add origin <repository-url>
clawd push -u origin main
```

### 场景二：代码审查
```bash
clawd pr create --title "Feature: Add new component"
clawd pr review --approve
clawd pr merge --squash
```

### 场景三：CI/CD 配置
```yaml
pipeline:
  build:
    - npm install
    - npm run build
  test:
    - npm run test
  deploy:
    - npm run deploy
```

## 技能参数

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| repository | string | 是 | 仓库地址 |
| branch | string | 否 | 分支名称，默认 main |
| token | string | 是 | 访问令牌 |
| workspace | string | 否 | 工作空间路径 |

## 最佳实践

### 分支策略
- `main`: 生产环境分支
- `develop`: 开发环境分支
- `feature/*`: 功能开发分支
- `hotfix/*`: 紧急修复分支

### 提交规范
```
feat: 新功能
fix: 修复问题
docs: 文档更新
style: 代码格式调整
refactor: 代码重构
test: 测试相关
chore: 构建配置
```

## 安全建议

1. **令牌管理**：使用环境变量存储敏感信息
2. **权限控制**：遵循最小权限原则
3. **代码审查**：所有代码必须经过审查
4. **依赖扫描**：定期检查依赖安全性

## 故障排查

### 常见问题

**Q: 推送代码失败**
```bash
# 检查远程仓库连接
clawd remote -v

# 验证认证信息
clawd config --list
```

**Q: 合并冲突**
```bash
# 查看冲突文件
clawd status

# 手动解决冲突后
clawd add .
clawd commit -m "Resolve merge conflicts"
```

## 版本历史

- **v1.0.0** (2026-01-29)
  - 初始版本发布
  - 支持基础代码管理功能
  - 集成 CI/CD 流程

## 技术支持

- 文档：https://clawd.hub/docs
- 社区：https://community.clawd.hub
- 问题反馈：https://github.com/clawd/hub/issues

## 许可证

MIT License
