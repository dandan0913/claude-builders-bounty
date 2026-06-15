# CHANGELOG Generator

A structured CHANGELOG generator from git history. Works via Claude Code skill or standalone scripts.

## Quick Start (3 Steps)

### 1. Install

```bash
# Clone or copy these files into your project
python generate_changelog.py --repo OWNER/REPO --output CHANGELOG.md
```

### 2. Generate

```bash
# API mode (no git required)
python generate_changelog.py --repo OWNER/REPO --output CHANGELOG.md

# Or git mode (local repo)
python generate_changelog.py --git-path ./my-project --since-tag v1.0.0

# Bash wrapper
./generate-changelog.sh --since-tag v1.0.0
```

### 3. Use in Claude Code

Just run `/generate-changelog` in Claude Code.

## Features

- Auto-categorizes: Added / Fixed / Changed / Removed / Performance / Security
- Parses conventional commits: `feat(scope): description`
- Supports GitHub API mode (no git required)
- Clean Markdown output with SHA references
