# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

A personal collection of Claude Code **skills** — self-contained, domain-specific workflows that Claude Code auto-discovers by matching a skill's `description` against the user's natural-language request. There is no build step, linting, or compiled code; the repo is Markdown skill definitions plus a small amount of Python.

## Repository Layout

```
skills/
  <skill-name>/
    SKILL.md              # skill definition (frontmatter + workflow instructions)
    scripts/              # optional supporting code invoked by the skill
    evals/evals.json      # optional evaluation prompts + expected outputs
```

Each skill is fully self-contained and independent. There are two skills today:

- **wechat-article-formatter** — converts Markdown/HTML into WeChat-public-account-safe rich text (inline styles, 677px max width, static charts).
- **macos-cache-cleaner** — safe scanner/cleaner for reproducible macOS caches, rotated logs, and Docker data. Backed by `scripts/cache_cleaner.py`.

## Skill Frontmatter

Every `SKILL.md` must start with YAML frontmatter. The two required fields are `name` (matches the directory name) and `description` (this is the trigger — Claude Code matches on it, so it must describe *when* the skill applies, not just what it does).

Optional fields used in this repo:

- `compatibility` — e.g. `macOS；需要 Python 3` (macos-cache-cleaner)
- `allowed-tools` — restricts which tools the skill may use (macos-cache-cleaner declares `Bash`, `Read`)
- `argument-hint` — hint for the slash-command argument syntax

The body of `SKILL.md` is a workflow: trigger conditions, step-by-step instructions, output artifacts, and any templates/code snippets. Output artifacts (e.g. generated HTML) belong in the user's working directory, **not** inside `skills/`.

## Naming Discrepancy (known issue)

Skill definition files are inconsistently named: `wechat-article-formatter` uses `SKILLS.md` (plural) while `macos-cache-cleaner` uses `SKILL.md` (singular, the canonical Claude Code convention). The README and `Skill Authoring Conventions` reference `SKILLS.md`. When adding or renaming skills, prefer `SKILL.md`; if you touch the wechat skill, consider renaming its file for consistency.

## The `{baseDir}` Placeholder

`SKILL.md` bodies reference `{baseDir}` (e.g. `{baseDir}/scripts/cache_cleaner.py`). This is resolved at runtime to the skill's own directory. When a skill needs to run its own script, reference it via `{baseDir}/scripts/...`, never a hardcoded absolute path.

## Running Tests

The only executable code with tests is the macOS cache cleaner. Tests use Python's `unittest` and isolate the filesystem via the `CACHE_CLEANER_HOME` env var (pointed at a temp dir), so they never touch the real home directory.

```bash
python3 skills/macos-cache-cleaner/scripts/test_cache_cleaner.py
```

The `cache_cleaner.py` script itself is invoked through the skill workflow, not directly by developers:

```bash
python3 skills/macos-cache-cleaner/scripts/cache_cleaner.py --mode scan
python3 skills/macos-cache-cleaner/scripts/cache_cleaner.py --mode clean --categories dev-caches --confirm DELETE-CACHE-ONLY
```

## Skill Evaluation (`evals/evals.json`)

`evals/evals.json` is a simple, hand-authored list (no runner harness in this repo). Each entry has `id`, `prompt`, `expected_output`, and `files`. `expected_output` describes the *observable behavior* the skill should produce, not exact text. When changing a skill's behavior, update its `evals.json` to match.

## IDE

This is an IntelliJ IDEA project (Python module). `.idea/` and `*.iml` are gitignored — do not commit them.
