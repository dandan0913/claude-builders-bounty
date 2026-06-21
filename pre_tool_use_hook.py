#!/usr/bin/env python3
"""
pre_tool_use_hook.py - Claude Code pre-tool-use hook that blocks destructive bash commands.

Blocks these patterns:
- rm -rf, DROP TABLE, TRUNCATE, DELETE FROM (without WHERE)
- git push --force / -f (but NOT --force-with-lease)
- dd if=/dev/zero, chmod 777, mkfs, shred -u, sudo rm -rf

Installation:
  mkdir -p ~/.claude/hooks && cp pre_tool_use_hook.py ~/.claude/hooks/pre_tool_use_hook.py

Usage: Claude Code automatically detects and runs hooks from ~/.claude/hooks/
"""

import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

BLOCKED_PATTERNS = [
    (r'\brm\s+(-r\s+)?-f\b|\brm\s+-rf\b', 'Recursive forceful deletion — irreversible and dangerous. Use `rm -r` and confirm each directory.'),
    (r'\bDROP\s+TABLE\b', 'Drops entire database tables — irreversible data loss. Use `DELETE FROM ... WHERE ...` instead.'),
    (r'\bTRUNCATE\s+(TABLE\s+)?\w+', 'Truncates all data from a table — irreversible. Consider soft-delete or archival.'),
    (r'\bDELETE\s+FROM\b(?!.*\bWHERE\b)', 'Deletes ALL rows without WHERE clause. Add a WHERE filter to target specific rows.'),
    (r'\bgit\s+push\s+--force(?![\w-])', 'Force pushes can overwrite remote history. Use `git push --force-with-lease` to protect shared branches.'),
    (r'\bgit\s+push\s+-\s*f\b', 'Force pushes can overwrite remote history. Use `git push --force-with-lease` instead.'),
    (r'\bdd\s+if=/dev/zero\b', 'Overwrites disk with zeros — data destruction. Are you sure this is intentional?'),
    (r'\bchmod\s+777\b', 'Sets world-writable permissions — major security risk. Use restrictive permissions like 755 or 644.'),
    (r'\bchmod\s+o\+w\b', 'Makes files world-writable — security risk. Use restrictive permissions instead.'),
    (r'\bsudo\s+rm\s+-rf\b', 'Privileged recursive deletion — extremely dangerous. Never combine sudo with rm -rf.'),
    (r'\bmkfs\b', 'Formats a disk partition — destroys all data on it.'),
    (r'\bshred\s+-u\b', 'Securely deletes files irreversibly. Make sure this is intentional.'),
]

LOG_DIR = Path.home() / '.claude' / 'hooks'
LOG_FILE = LOG_DIR / 'blocked.log'


def log_blocked(command: str, reason: str, project_path: str):
    """Append a blocked attempt to the log file."""
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    entry = (
        f"[{timestamp}] BLOCKED: {command}\n"
        f"  Reason: {reason}\n"
        f"  Project: {project_path}\n\n"
    )
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(entry)


def get_project_path() -> str:
    """Try to determine the current project root."""
    cwd = Path.cwd()
    for parent in [cwd] + list(cwd.parents)[:5]:
        if (parent / '.git').exists():
            return str(parent)
        if (parent / 'package.json').exists():
            return str(parent)
    return str(cwd)


def check_command(command: str) -> tuple:
    """
    Check if a command matches any blocked pattern.
    Returns (is_blocked: bool, reason: str)
    """
    stripped = command.strip()
    for pattern, reason in BLOCKED_PATTERNS:
        if re.search(pattern, stripped, re.IGNORECASE):
            return True, reason
    return False, ""


def main():
    # Read hook input from stdin
    try:
        input_data = json.loads(sys.stdin.read())
    except (json.JSONDecodeError, EOFError):
        sys.exit(0)

    tool = input_data.get('tool', '')
    arguments = input_data.get('arguments', {})

    if tool in ('bash', 'script'):
        command = arguments.get('command', '')
        project_path = arguments.get('project_path', '') or get_project_path()

        is_blocked, reason = check_command(command)

        if is_blocked:
            log_blocked(command, reason, project_path)
            error_response = {
                'error': (
                    f'COMMAND BLOCKED: {reason}\n\n'
                    f'The command "{command}" has been blocked by the pre-tool-use security hook.\n\n'
                    f'Safe alternatives are listed above.\n'
                    f'Blocked attempts are logged to: {LOG_FILE}'
                ),
                'blocked': True,
            }
            print(json.dumps(error_response))
            sys.exit(1)

    sys.exit(0)


if __name__ == '__main__':
    main()
