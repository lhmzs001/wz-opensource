# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

This is a personal open-source collection of Claude Code skills. Each skill extends Claude Code with domain-specific workflows.

## Repository Structure

```
skills/
  <skill-name>/
    SKILLS.md        # Skill definition (trigger, workflow, templates)
```

Skills follow the Claude Code skill format: a markdown file with YAML frontmatter (`name`, `description`) followed by instructions for when and how the skill executes.

### Existing Skills

- **wechat-article-formatter** — Converts HTML or Markdown content into WeChat public account (微信公众号) rich-text format. Generates an HTML file with inline styles compatible with the WeChat editor's paste-from-browser workflow.

## Skill Authoring Conventions

- Skill files go in `skills/<name>/SKILLS.md`
- Frontmatter must include `name` (same as directory name) and `description` (used for skill discovery)
- The skill's body should define: trigger conditions, workflow steps, output artifacts, and any templates or code snippets needed
- Output artifacts from skill runs belong in the user's working directory, not inside `skills/`

## IDE

This is an IntelliJ IDEA project (configured as Python module). Ignore `.idea/` and `*.iml` files — they are gitignored.
