# PR Review Agent

A Claude Code agent that analyzes PR diffs and generates structured review comments.

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Review a PR
python claude_review.py --pr https://github.com/owner/repo/pull/123

# Or review a diff file
python claude_review.py --diff path/to/diff.patch

# Save to file
python claude_review.py --pr URL --output review.md
```

## Usage

- `--pr URL`: GitHub PR URL to review
- `--diff FILE`: Path to diff/patch file
- `--output FILE`: Write review to file (default: stdout)
- `--json`: Output in JSON format
- `--token TOKEN`: GitHub personal access token

## Features

- Automatic PR diff fetching
- Structured Markdown output
- Risk identification
- Improvement suggestions
- Confidence scoring
- Statistics calculation

## Output Format

The agent generates a structured Markdown review with:

1. **Summary** - Brief overview of changes
2. **Statistics** - Lines added/removed, files changed
3. **Risk Assessment** - Risk level and confidence score
4. **Identified Risks** - Specific concerns found in the code
5. **Recommendations** - Actionable suggestions

## Testing

```bash
# Test with a real PR
python claude_review.py --pr https://github.com/python/cpython/pull/100000 --output test_review.md

# Test with diff file
curl -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/owner/repo/pulls/123/diff > test.patch

python claude_review.py --diff test.patch --output test_review.md
```

## Installation

1. Clone this repository
2. Install dependencies: `pip install -r requirements.txt`
3. Set GitHub token (optional): `export GITHUB_TOKEN=your_token`
4. Run: `python claude_review.py --pr PR_URL`

## License

MIT
