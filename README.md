# wz-opensource

王子的开源仓库 —— Claude Code 技能（Skills）合集，让智能体获得领域专用的工作流能力。

## 项目简介

本仓库收集了一系列 Claude Code 技能定义（Skill），每个技能是一个独立、自包含的工作流模块。Claude Code 会将技能定义中的 `description` 与用户自然语言指令自动匹配，在对应场景下按规范流程执行任务。

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
- 按内容需要加入适合手机阅读的静态图表、数据卡片或流程示意，并保证样式被清洗后仍有文字降级
- 生成 HTML 文件并在浏览器中打开，Cmd+A / Cmd+C 即可粘贴到公众号编辑器

### macOS 缓存与日志安全清理（macos-cache-cleaner）

在 macOS 磁盘空间不足、缓存或日志堆积、Docker/Colima 占用增长时，安全扫描并清理可重建缓存、历史轮转日志和 Docker 无用数据。

**触发方式**：
- 对 Claude Code 说"清理磁盘"、"清理缓存"、"释放磁盘空间"

**功能特性**：
- 默认只扫描（dry-run），删除前要求用户明确确认
- 白名单式清理：只处理可重建开发缓存、明确的历史/轮转日志、Docker 可回收缓存
- 保护项目源码、用户文档、聊天附件、Postman 工作数据、运行中容器、使用中镜像和 Docker Volume
- 内置 Python 脚本 `scripts/cache_cleaner.py` 确定性执行，不手写宽泛的 `rm` / `find ... -delete`
- 附带 `unittest` 测试与 `evals/evals.json` 评估用例

## 仓库结构

```
skills/
  <skill-name>/
    SKILL.md              # 技能定义（frontmatter + 工作流）
    scripts/              # 可选：技能依赖的支撑脚本
    evals/evals.json      # 可选：评估提示词与预期输出
```

## 如何使用

### 1. 安装 Claude Code

参考 [Claude Code 官方文档](https://docs.anthropic.com/en/docs/claude-code) 安装并配置。

### 2. 安装技能

将本仓库中的技能拷贝到 Claude Code 的技能目录（个人技能目录 `~/.claude/skills/`，或项目技能目录 `.claude/skills/`）：

```bash
# 克隆仓库
git clone https://github.com/wz-org/wz-opensource.git

# 安装到个人技能目录
mkdir -p ~/.claude/skills
cp -r wz-opensource/skills/* ~/.claude/skills/
```

### 3. 使用技能

技能安装后，直接用自然语言描述需求即可触发对应技能。例如：

```
帮我把这个 README.md 转成微信公众号文章格式
```

或：

```
清理一下磁盘
```

Claude Code 会自动匹配到对应技能并按规范执行。

## 自定义技能

你可以参照现有技能的格式，在 `skills/<skill-name>/SKILL.md` 创建自己的技能定义：

```markdown
---
name: my-skill
description: 一句话描述什么时候触发该技能（用于技能发现与匹配）
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
- 技能定义文件名建议为 `SKILL.md`（`wechat-article-formatter` 目前仍为历史命名 `SKILLS.md`，可考虑重命名保持一致）
- 前置元数据需包含 `name`（与目录名一致）和 `description`（描述*何时*触发，而非仅说明功能）
- 支撑脚本放在 `scripts/`，通过 `{baseDir}/scripts/...` 引用，不硬编码绝对路径
- 评估用例放在 `evals/evals.json`，`expected_output` 描述可观察行为，而非精确文本

## 测试

唯一带可执行代码的技能是 macOS 缓存清理器。测试使用 Python `unittest`，通过 `CACHE_CLEANER_HOME` 环境变量隔离文件系统，不触碰真实主目录：

```bash
python3 skills/macos-cache-cleaner/scripts/test_cache_cleaner.py
```

## 许可

MIT License
