---
name: macos-cache-cleaner
description: 当用户输入"清理磁盘"、"磁盘清理"、"清理缓存"、"释放磁盘空间"、"清一下磁盘"等指令时触发此 Skill。在 macOS 磁盘空间不足、系统数据过大、缓存或日志堆积、Docker/Colima 占用增长时，必须使用此 Skill 安全扫描并清理可重建缓存、明确的历史轮转日志、Docker 无用镜像、已停止容器和 BuildKit 可回收缓存。默认只扫描，删除前要求用户明确确认；保护项目源码、用户文档、聊天附件、Postman 工作数据、运行中容器、使用中镜像和 Docker Volume。
compatibility: macOS；需要 Python 3。Docker 清理需要 docker CLI，BuildKit 清理需要 docker buildx。
allowed-tools:
  - Bash
  - Read
argument-hint: "[扫描|清理] [开发缓存|历史日志|Docker]"
---

# macOS 缓存与日志安全清理

使用 `{baseDir}/scripts/cache_cleaner.py` 完成确定性扫描和清理。不要手写宽泛的 `rm`、`find ... -delete` 或 `docker system prune --volumes` 命令。

## 安全边界

只处理以下内容：

- 可重建开发缓存：`~/.cache`、`~/.npm`、Go 构建缓存、JetBrains 缓存、Playwright 缓存、pnpm store。
- 明确的历史或轮转日志：白名单日志目录内的 `.log.N`、`.log.DATE`、`.gz`、`.zip`、JetBrains thread dump 历史文件。
- Docker/Colima：BuildKit 可回收缓存、未被容器使用的镜像、已停止容器。

始终保护：

- 项目源码、Git 仓库以及 `Documents`、`Desktop`、图片、音乐和视频。
- 微信等聊天记录与附件。
- Postman Collection、环境变量、本地工作区等工作数据。
- Docker 正在运行的容器、被容器使用的镜像、所有 Docker Volume。
- 当前活跃日志、未知日志和数据库文件。
- DLP、EDR、杀毒、审计等企业安全组件数据；这类日志默认只报告，用户单独明确授权后才能按精确文件范围处理。

## 工作流

### 1. 默认扫描

运行：

```bash
python3 "{baseDir}/scripts/cache_cleaner.py" --mode scan
```

可按范围扫描：

```bash
python3 "{baseDir}/scripts/cache_cleaner.py" --mode scan --categories dev-caches user-logs
python3 "{baseDir}/scripts/cache_cleaner.py" --mode scan --categories docker
```

向用户展示：

- 候选类别、路径和预计占用；
- `docker system df` 与 `docker buildx du` 的可回收信息；
- 明确不会触碰的内容；
- 缓存重建的影响，例如首次构建或安装可能变慢并重新下载依赖。

扫描不等于授权。即使用户说“看看”“检查”“排个序”，也只能扫描。

### 2. 获取明确确认

只有用户在看到本次候选范围后明确说“确认清理”或逐项批准，才能执行。若路径不存在、范围变化明显或出现企业安全组件日志，暂停并重新确认。

不要把之前一次清理的授权沿用到新一轮扫描。

### 3. 执行白名单清理

用户确认后运行：

```bash
python3 "{baseDir}/scripts/cache_cleaner.py" \
  --mode clean \
  --categories dev-caches user-logs docker \
  --confirm DELETE-CACHE-ONLY
```

只传入用户批准的类别。脚本自身还会验证确认令牌和路径白名单。

### 4. 验证并报告

执行后必须核对并报告：

- 脚本输出的清理后目录占用；
- `docker system df` 和 `docker buildx du`；
- `df -h /System/Volumes/Data`；
- 实际删除类别、保留范围、无法处理项和重新下载风险。

不要仅凭删除命令成功就声称释放了多少空间；以清理前后磁盘和目录结果为准。稀疏虚拟磁盘可能延迟归还空间，需如实说明。

## Dry-run 定义

`--mode scan` 就是 dry-run：它只枚举候选和读取空间信息，不删除任何内容。需要机器可读报告时添加 `--json`。

## 企业安全组件例外

遇到 `/Library/Application Support/DLP*`、EDR、终端安全、审计客户端等目录时：

1. 只统计和列出日志文件，不自动纳入清理；
2. 提醒日志可能受公司合规、审计或留存策略约束；
3. 只有用户对精确目录或精确轮转文件明确授权后，才可另行处理；
4. 保留当前正在写入的日志，优先删除编号或日期明确的旧轮转日志。

## 输出格式

用简体中文简洁报告：

1. 扫描或清理是否完成；
2. 按空间从大到小列出候选或实际处理项；
3. 当前磁盘可用空间与使用率；
4. 未触碰的受保护内容；
5. 剩余风险或缓存重建影响。
