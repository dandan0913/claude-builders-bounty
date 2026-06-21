# README.md - Pre-Tool-Use Hook for Blocking Destructive Bash Commands

> Intercepts dangerous bash commands before Claude Code executes them.

## Installation (2 commands)

```bash
mkdir -p ~/.claude/hooks
curl -sL https://raw.githubusercontent.com/dandan0913/destructive-hooks/main/pre_tool_use_hook.py -o ~/.claude/hooks/pre_tool_use_hook.py
```

Or clone and copy manually:

```bash
git clone https://github.com/dandan0913/destructive-hooks.git
cp destructive-hooks/pre_tool_use_hook.py ~/.claude/hooks/pre_tool_use_hook.py
```

## How It Works

This Claude Code `pre_tool_use` hook scans every bash command before execution. If a command matches a known dangerous pattern, it is **blocked** and Claude Code receives a clear error message explaining why.

## Blocked Patterns

| Pattern | Why It's Dangerous |
|---------|-------------------|
| `rm -rf` | Recursive forceful deletion — irreversible |
| `DROP TABLE` | Drops entire database tables |
| `TRUNCATE` | Clears all data from a table |
| `DELETE FROM` without `WHERE` | Deletes ALL rows in a table |
| `git push --force` / `-f` | Overwrites remote history |
| `dd if=/dev/zero` | Overwrites disk with zeros |
| `chmod 777` / `chmod o+w` | World-writable permissions — security risk |
| `sudo rm -rf` | Privileged recursive deletion |
| `mkfs` | Formats disk partitions |
| `shred -u` | Irreversible secure deletion |

## Logging

Every blocked attempt is logged to `~/.claude/hooks/blocked.log` with:
- Timestamp (UTC)
- The attempted command
- The reason it was blocked
- The project path

## Configuration

To add new patterns, edit the `BLOCKED_PATTERNS` list in `pre_tool_use_hook.py`:

```python
BLOCKED_PATTERNS = [
    (r'\bpattern\b', 'Reason for blocking'),
    # Add more patterns here
]
```

## License

MIT
