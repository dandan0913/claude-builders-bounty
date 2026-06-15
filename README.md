# Pre-Tool-Use Security Hook for Claude Code

A Python hook that intercepts dangerous bash commands before Claude Code executes them.

## Installation (2 commands)

```bash
# 1. Create hooks directory and copy hook
mkdir -p ~/.claude/hooks && cp pre_tool_use_hook.py ~/.claude/hooks/pre_tool_use_hook.py

# 2. Verify installation
python ~/.claude/hooks/pre_tool_use_hook.py --test
```

## How It Works

The hook automatically runs when Claude Code executes bash commands. It:

- **Blocks** dangerous patterns (`rm -rf`, `DROP TABLE`, `git push --force`, etc.)
- **Logs** every blocked attempt to `~/.claude/hooks/blocked.log`
- **Allows** safe commands to proceed normally
- **Shows** a clear message explaining why a command was blocked

## Blocked Patterns

| Pattern | Example |
|---------|---------|
| File destruction | `rm -rf`, `rm --recursive -f` |
| Database destruction | `DROP TABLE`, `TRUNCATE`, `DELETE FROM` (no WHERE) |
| Git destruction | `git push --force`, `git push -f` |
| Disk destruction | `mkfs` |
| Permission danger | `chmod 777`, `chmod -R 777` |

## Safe Patterns (Allowed)

- `rm -i` (interactive delete)
- `git push --force-with-lease` (safe force push)

## Testing

```bash
# Run full test suite
python pre_tool_use_hook.py --test

# Test a single command
python pre_tool_use_hook.py 'rm -rf /'
```
