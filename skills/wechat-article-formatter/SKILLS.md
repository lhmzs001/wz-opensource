---
name: wechat-article-formatter
description: 将 HTML / Markdown 内容转成微信公众号富文本格式，并按内容需要加入适合手机阅读的静态图表、数据卡片或流程示意，一键复制即可带格式粘贴到公众号编辑器发布。
---

# 微信公众号文章格式化

将 HTML 或 Markdown 内容转换成微信公众号兼容的富文本格式，直接在浏览器中渲染后复制粘贴到公众号编辑器即可保留全部格式。

## 触发条件

- 用户说"生成公众号文章"、"微信排版"、"公众号格式"、"wechat article"、"微信公众号格式"
- 用户要求加入图表、数据可视化、流程图或信息图并适配微信公众号
- 用户提供内容要求适配微信公众号发布

## 工作流程

### 1. 获取内容

从用户输入中提取内容，支持两种来源：
- 用户直接提供 HTML 或 Markdown 文本
- 用户指定一个文件路径，读取该文件内容

### 2. 生成公众号兼容 HTML

将内容包裹到公众号优化的 HTML 模板中，核心规则：

**样式原则**
- 全部使用内联样式（`style=""`），不使用 class / id 选择器
- 正文字号 15-16px，标题 18-22px，注释 12-13px
- 行高 1.75-2.0，保证手机端阅读舒适
- 颜色使用 `#3f3f3f`（正文）、`#888888`（次要文字）、`#000000`（标题）
- 段间距 0.8-1em，段内紧凑
- 最大宽度 677px（公众号素材标准宽度）

**图表决策原则**
- 先识别文章中是否存在趋势、对比、比例、排名、流程、时间线或关键指标；存在时优先加入 1-3 个有明确作用的视觉元素。
- 图表服务于解释，不为装饰而添加；没有可靠数据时不得虚构数值，可改用“示意图”“流程图”或“概念卡片”，并明确标注为示意。
- 每个图表都要回答一个具体问题（例如“谁更高”“如何变化”“步骤是什么”），正文中用一句话引导读者看图，图后用一句话总结结论。
- 视觉节奏建议为“正文 → 图表/卡片 → 结论”，避免连续堆放多个图表或让图表打断叙事。

**支持的富文本元素**

| 元素 | 说明 |
|------|------|
| `<h1>`-`<h4>` | 标题，h1 最大 22px |
| `<p>` | 正文段落，两端对齐 |
| `<strong>` / `<b>` | 加粗 |
| `<em>` / `<i>` | 斜体 |
| `<span style="color:...">` | 彩色文字 |
| `<blockquote>` | 引用块，左侧灰色边框 |
| `<ul>` / `<ol>` | 无序/有序列表 |
| `<img>` | 图片（需公网 URL） |
| `<hr>` | 分隔线 |
| `<section>` | 卡片/高亮区域 |
| `<pre>` / `<code>` | 代码块（灰底等宽字体） |
| `<figure>` / 图表图片 | 静态 PNG/JPG/WebP 图表，配标题、来源和文字结论；复制前降级为 `<img>` + 说明文字 |

**不支持的（会被移除或降级）**
- flexbox / grid 布局 → 降级为块级布局
- 外部样式表 / `<style>` 标签 → 转为内联样式
- JavaScript → 完全移除
- CSS 动画 / 过渡 → 移除
- web fonts（如 Google Fonts）→ 改为系统字体栈
- JavaScript 图表库、`<canvas>`、交互式 SVG → 转为静态图片；保留关键数据和文字结论

### 3. 保存并打开

1. 将生成的 HTML 保存到 `{cwd}/wechat-article-{timestamp}.html`
2. 用 `open` 命令在浏览器中打开该文件
3. 提示用户：在浏览器中 `Cmd+A` 全选，`Cmd+C` 复制，然后粘贴到公众号编辑器

### 4. 可选：本地图片处理

如果内容包含本地图片路径：
- 提醒用户公众号不支持本地图片，需先上传到公众号素材库
- 可用 Playwright 打开公众号后台 `https://mp.weixin.qq.com` 让用户手动上传

### 5. 图表与视觉元素处理

根据内容选择最易读的图表，不追求复杂或“像数据大屏”的效果：

| 内容关系 | 优先图表 | 使用要点 |
|------|------|------|
| 类别对比、排名 | 横向条形图 | 类别名称完整显示，最多展示约 8 项，按数值排序 |
| 随时间变化 | 折线图 | 时间点不宜过密，突出起点、终点和转折点 |
| 构成比例 | 环形图或 100% 堆叠条 | 分类建议 2-5 项；必须直接标出百分比或数量 |
| 步骤、决策、因果 | 流程图/箭头卡片 | 用 3-7 步短句，移动端按纵向排列 |
| 时间安排、阶段演进 | 时间线 | 每个节点只保留日期、标题和一句说明 |
| 单一关键数字 | 数据卡片/大数字 | 只突出一个指标，补充口径、单位和时间范围 |
| 无精确数据的观点 | 概念示意图/对比卡片 | 不使用看似精确的比例、坐标轴或虚构来源 |

**图表生成与可读性要求**
- 图表必须预先渲染为静态图片（推荐 PNG；照片型素材可用 JPG/WebP），宽度不超过 677px，文字在手机屏幕上仍清晰可辨。
- 图中只保留必要的标题、单位、标签、图例和 1 个核心结论；避免 3D、阴影堆叠、过多颜色、密集网格线和长段落。
- 使用正文同一套色彩语义：主色 `#1e6fff`，正向/增长 `#16a085`，警示/下降 `#e74c3c`，中性灰 `#888888`；同一篇文章中保持含义一致，并兼顾色觉差异，不能只靠颜色传达信息。
- 图表下方必须有说明文字，至少包含“图表标题/结论”；涉及外部数据时同时写明数据来源、统计口径和时间范围。
- 每张图表前后保留适度留白；不要把多张图表拼成一张无法放大的长图，也不要让图表承担正文全部信息。
- 复制到公众号前检查图片是否能正常加载；本地生成的图表需要上传到公众号素材库并替换成公网 URL。

**图表 HTML 模式**

公众号中优先使用“图片 + 图注 + 结论”的静态结构，不嵌入交互代码：

```html
<section style="margin:1.2em 0;padding:14px 12px;background:#fafafa;border:1px solid #eeeeee;border-radius:8px;">
  <p style="margin:0 0 0.7em;font-size:16px;font-weight:600;color:#000;text-align:left;">图：过去 5 年用户增长趋势</p>
  <img src="https://..." alt="折线图显示用户数从 2020 年到 2024 年总体上升，2023 年增速放缓" style="display:block;width:100%;height:auto;margin:0 auto;border-radius:4px;">
  <p style="margin:0.6em 0 0;text-align:center;font-size:12px;color:#888888;line-height:1.6;">数据来源：内部统计；统计时间：2020-2024 年</p>
  <p style="margin:0.6em 0 0;font-size:14px;color:#3f3f3f;line-height:1.7;"><strong>读图结论：</strong>用户数持续增长，但 2023 年后增速明显放缓。</p>
</section>
```

若只有结构化数字而暂时无法生成图片，可使用纵向数据卡片或短列表降级；不要使用横向滚动表格。

## HTML 模板

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>公众号文章</title>
</head>
<body style="
  margin: 0;
  padding: 20px;
  background: #f5f5f5;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', 'Helvetica Neue', Helvetica, Arial, sans-serif;
  display: flex;
  justify-content: center;
">
<article style="
  max-width: 677px;
  width: 100%;
  background: #ffffff;
  padding: 40px 20px;
  box-sizing: border-box;
  color: #3f3f3f;
  font-size: 15px;
  line-height: 1.8;
  letter-spacing: 0.5px;
">
  <!-- 内容区域 -->
</article>
</body>
</html>
```

## 元素样式规范

### 标题

```html
<h1 style="font-size:22px;font-weight:700;color:#000;text-align:center;margin:1.2em 0 0.8em;line-height:1.4;">标题一</h1>
<h2 style="font-size:20px;font-weight:700;color:#000;margin:1em 0 0.6em;line-height:1.4;">标题二</h2>
<h3 style="font-size:18px;font-weight:600;color:#000;margin:0.8em 0 0.5em;line-height:1.4;">标题三</h3>
<h4 style="font-size:16px;font-weight:600;color:#000;margin:0.6em 0 0.4em;line-height:1.4;">标题四</h4>
```

### 段落

```html
<p style="margin:0 0 0.8em;text-align:justify;word-break:break-all;">正文内容</p>
```

### 引用块

```html
<blockquote style="
  margin:1em 0;
  padding:10px 16px;
  border-left:4px solid #1e6fff;
  background:#f6f8fa;
  color:#666;
  font-size:14px;
  line-height:1.6;
">引用内容</blockquote>
```

### 代码块

```html
<pre style="
  margin:1em 0;
  padding:16px;
  background:#282c34;
  color:#abb2bf;
  font-family:'SF Mono','Monaco','Menlo','Consolas',monospace;
  font-size:13px;
  line-height:1.6;
  border-radius:6px;
  overflow-x:auto;
  white-space:pre-wrap;
  word-break:break-all;
"><code>code here</code></pre>
```

### 行内代码

```html
<code style="
  background:#f0f0f0;
  color:#e74c3c;
  padding:2px 6px;
  border-radius:3px;
  font-family:'SF Mono','Monaco','Menlo','Consolas',monospace;
  font-size:0.9em;
">inline code</code>
```

### 卡片/高亮区域

```html
<section style="
  margin:1.2em 0;
  padding:16px 20px;
  background:#f0f7ff;
  border-radius:8px;
  border:1px solid #d0e3f7;
">
  <p style="margin:0;color:#1a5fb4;font-size:14px;">卡片内容</p>
</section>
```

### 列表

```html
<ul style="margin:0.8em 0;padding-left:1.5em;list-style:disc;">
  <li style="margin-bottom:0.4em;">列表项</li>
</ul>
<ol style="margin:0.8em 0;padding-left:1.5em;">
  <li style="margin-bottom:0.4em;">有序列表项</li>
</ol>
```

### 分隔线

```html
<hr style="margin:1.5em 0;border:none;border-top:1px solid #e8e8e8;">
```

### 图片

```html
<img src="https://..." alt="描述" style="display:block;max-width:100%;height:auto;margin:1em auto;border-radius:4px;">
```

### 图片说明

```html
<p style="margin:-0.5em 0 1em;text-align:center;font-size:12px;color:#999;">图片说明文字</p>
```

### 强调/高亮文字

```html
<span style="color:#1e6fff;font-weight:600;">蓝色强调</span>
<span style="background:linear-gradient(to top,#fff3cd 40%,transparent 40%);">黄色标记</span>
<span style="color:#e74c3c;">红色警告</span>
```

## 常见内容模式

### 模式一：技术文章
标题居中大号 + 分隔线 + 正文 + 代码块 + 引用块

### 模式二：产品介绍
h2 分段标题 + 卡片式特性介绍 + 强调色按钮文字

### 模式三：列表/清单
h2 标题 + 有序/无序列表 + 加粗关键词

### 模式四：图文混排
段落 + 居中图片 + 图片说明 + 续段

### 模式五：数据/观点可视化
问题或结论引入 + 单个核心图表 + “读图结论” + 数据来源/口径说明

### 模式六：引导关注
末尾居中放置引导关注区域（卡片背景 + 加粗）

## 注意事项

1. **图片必须是公网 URL** - 本地图片无法显示，需先上传到公众号素材库获取 URL
2. **不要使用 emoji 作为主要视觉元素** - 部分 Android 设备显示不一致
3. **避免深色背景上的浅色文字** - 公众号编辑器可能丢失背景色
4. **代码块超过 30 行建议截图代替** - 手机端代码阅读体验差
5. **全文总宽度不超过 677px** - 超出会在手机端出现横向滚动条
6. **不要使用 `<table>`** - 手机端表格几乎不可读，用列表或卡片替代
7. **段落间留空行** - 在源码中段落之间加空行，方便公众号编辑器识别分段
8. **图表优先静态化** - 不使用交互式图表、JavaScript、`canvas` 或依赖外部脚本的 SVG
9. **图表必须可追溯** - 有真实数据时标注来源、口径和时间；无数据时标注“示意图”，禁止编造精确数字
10. **图表要有文字替代** - `alt` 描述和图后结论应能让无法查看图片的读者理解核心信息
11. **控制视觉密度** - 一般每 800-1200 字安排一个核心视觉元素；只有在确实有多组数据或步骤时才增加

## Markdown 转换

如果输入是 Markdown，先用 Python `markdown` 库转成 HTML，再套用本模板：

```python
import markdown
html_body = markdown.markdown(text, extensions=['fenced_code', 'tables', 'codehilite'])
```

Markdown 表格不要原样保留为 HTML `<table>`：若数据适合比较或趋势表达，优先转成静态图表；否则降级为纵向列表或数据卡片。

## 输出文件

生成的 HTML 文件保存到当前工作目录：

```
{cwd}/wechat-article-{timestamp}.html
```

生成后用 `open` 命令在浏览器中打开，用户在浏览器中全选复制即可粘贴到公众号编辑器。
