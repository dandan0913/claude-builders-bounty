---
name: changelog-generator
description: >
  Generate a structured CHANGELOG.md from git history. Use when the user wants to create
  a changelog from commits, parse conventional commit messages, categorize changes into
  Added/Fixed/Changed/Removed/Performance/Security sections, or needs a /generate-changelog
  command for Claude Code. Also works as a standalone bash script (generate-changelog.sh)
  or Python module (generate_changelog.py).
---

# CHANGELOG Generator Skill

## Overview

Automatically generates a structured CHANGELOG.md from git history by parsing conventional
commit messages and categorizing them into logical sections.

## Commands

### Claude Code Command

Run /generate-changelog in Claude Code to generate a changelog for the current repo.

### Bash Script

`ash
# Basic usage - auto-detects latest tag
./generate-changelog.sh

# Since a specific tag
./generate-changelog.sh --since-tag v1.0.0

# Custom output file
./generate-changelog.sh --output docs/CHANGELOG.md

# Quiet mode (file only, no stdout)
./generate-changelog.sh --quiet
`

### Python Module

`ash
python generate_changelog.py --since-tag v1.0.0 --output CHANGELOG.md
`

## How It Works

1. Fetches git commits (optionally since last tag)
2. Parses conventional commit format: 	ype(scope): description
3. Categorizes by type:
   - **Added**: feat, feature, new, add
   - **Fixed**: fix, bugfix, bug
   - **Changed**: refactor, chore, docs, style, build, ci, test
   - **Removed**: remove, delete, rm
   - **Performance**: perf
   - **Security**: security, vuln
4. Generates formatted Markdown with SHA references

## Supported Commit Formats

- eat(auth): add login page
- ix: resolve memory leak
- docs(readme): update installation steps
- chore(deps): bump dependencies

## Files

- generate_changelog.py - Main Python generator
- generate-changelog.sh - Bash wrapper script
