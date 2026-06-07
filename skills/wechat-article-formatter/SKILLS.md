---
name: wechat-article-formatter
description: 将 HTML / Markdown 内容转成微信公众号富文本格式，一键复制即可带格式粘贴到公众号编辑器发布。
---

# 微信公众号文章格式化

将 HTML 或 Markdown 内容转换成微信公众号兼容的富文本格式，直接在浏览器中渲染后复制粘贴到公众号编辑器即可保留全部格式。

## 触发条件

- 用户说"生成公众号文章"、"微信排版"、"公众号格式"、"wechat article"
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

**不支持的（会被移除或降级）**
- flexbox / grid 布局 → 降级为块级布局
- 外部样式表 / `<style>` 标签 → 转为内联样式
- JavaScript → 完全移除
- CSS 动画 / 过渡 → 移除
- web fonts（如 Google Fonts）→ 改为系统字体栈

### 3. 保存并打开

1. 将生成的 HTML 保存到 `{cwd}/wechat-article-{timestamp}.html`
2. 用 `open` 命令在浏览器中打开该文件
3. 提示用户：在浏览器中 `Cmd+A` 全选，`Cmd+C` 复制，然后粘贴到公众号编辑器

### 4. 可选：本地图片处理

如果内容包含本地图片路径：
- 提醒用户公众号不支持本地图片，需先上传到公众号素材库
- 可用 Playwright 打开公众号后台 `https://mp.weixin.qq.com` 让用户手动上传

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

### 模式五：引导关注
末尾居中放置引导关注区域（卡片背景 + 加粗）

## 注意事项

1. **图片必须是公网 URL** - 本地图片无法显示，需先上传到公众号素材库获取 URL
2. **不要使用 emoji 作为主要视觉元素** - 部分 Android 设备显示不一致
3. **避免深色背景上的浅色文字** - 公众号编辑器可能丢失背景色
4. **代码块超过 30 行建议截图代替** - 手机端代码阅读体验差
5. **全文总宽度不超过 677px** - 超出会在手机端出现横向滚动条
6. **不要使用 `<table>`** - 手机端表格几乎不可读，用列表或卡片替代
7. **段落间留空行** - 在源码中段落之间加空行，方便公众号编辑器识别分段

## Markdown 转换

如果输入是 Markdown，先用 Python `markdown` 库转成 HTML，再套用本模板：

```python
import markdown
html_body = markdown.markdown(text, extensions=['fenced_code', 'tables', 'codehilite'])
```

## 输出文件

生成的 HTML 文件保存到当前工作目录：

```
{cwd}/wechat-article-{timestamp}.html
```

生成后用 `open` 命令在浏览器中打开，用户在浏览器中全选复制即可粘贴到公众号编辑器。