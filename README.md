# wz-opensource

王子的开源仓库 —— Claude Code 技能（Skills）合集，让智能体获得领域专用的工作流能力。

## 项目简介

本仓库收集了一系列 Claude Code 技能定义文件（SKILLS.md），每个技能为一个独立的功能模块，可以无缝集成到 Claude Code 中，让 AI 编程助手自动识别场景并按规范流程执行任务。

## 当前技能

### 微信公众号文章格式化（wechat-article-formatter）

将 HTML 或 Markdown 内容一键转换为微信公众号兼容的富文本格式。

**触发方式**：
- 对 Claude Code 说"把这篇 Markdown 转成公众号文章"
- 提供 HTML/Markdown 文件路径，要求适配微信公众号发布

**功能特性**：
- 自动转换 Markdown / HTML 为内联样式富文本
- 适配公众号编辑器标准（最大宽度 677px、系统字体栈）
- 支持标题、代码块、引用、卡片、列表、图片等元素
- 生成 HTML 文件并在浏览器中打开，Cmd+A / Cmd+C 即可粘贴到公众号编辑器

## 如何使用

### 1. 安装 Claude Code

参考 [Claude Code 官方文档](https://docs.anthropic.com/en/docs/claude-code) 安装并配置。

### 2. 注册技能

将本仓库克隆到本地，然后在 Claude Code 中注册技能目录：

```bash
# 克隆仓库
git clone https://github.com/wz-org/wz-opensource.git

# 在 Claude Code 中注册技能
claude mcp add skills -- path/to/wz-opensource/skills
```

或者通过 Claude Code 的设置界面，将 `skills/` 目录添加为技能源。

### 3. 使用技能

技能注册后，直接用自然语言描述需求即可触发对应技能。例如：

```
帮我把这个 README.md 转成微信公众号文章格式
```

Claude Code 会自动匹配到 `wechat-article-formatter` 技能并按规范执行。

## 自定义技能

你可以参照现有技能的格式，在 `skills/<skill-name>/SKILLS.md` 创建自己的技能定义：

```markdown
---
name: my-skill
description: 一句话描述技能功能
---

# 技能名称

## 触发条件
- 用户说"xxx"时触发
- ...

## 工作流程
1. 步骤一
2. 步骤二
...
```

创建后在 Claude Code 中重新加载技能目录即可生效。

## 贡献

欢迎提交 PR 贡献新的技能或改进现有技能。技能目录约定：

- 每个技能放在 `skills/<skill-name>/` 目录下
- 技能定义文件名为 `SKILLS.md`
- 前置元数据需包含 `name`（与目录名一致）和 `description`

## 许可

MIT License
