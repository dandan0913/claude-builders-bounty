#!/usr/bin/env python3
"""
pre_tool_use_hook.py - Claude Code pre-tool-use hook for blocking dangerous commands.

Installation:
  1. mkdir -p ~/.claude/hooks
  2. cp pre_tool_use_hook.py ~/.claude/hooks/pre_tool_use_hook.py
"""

import re
import os
import sys
from datetime import datetime, timezone

DANGEROUS_PATTERNS = [
    (r'\brm\s+-rf\b', 'rm -rf: Permanently deletes files/directories without recovery. Use `rm -i` instead.'),
    (r'\brm\s+--recursive\s+-f\b', 'rm --recursive -f: Permanently deletes files. Use `rm -i` instead.'),
    (r'\brm\s+-r\s+-f\b', 'rm -r -f: Permanently deletes files. Use `rm -i` instead.'),
    (r'\bDROP\s+TABLE\b', 'DROP TABLE: Permanently deletes a database table and all data. Ensure backups exist.'),
    (r'\bTRUNCATE\b', 'TRUNCATE: Removes all rows instantly without logging. Ensure this is intentional.'),
    (r'\bDELETE\s+FROM\b(?!.*\bWHERE\b)', 'DELETE FROM without WHERE: Deletes ALL rows. Always use a WHERE clause.'),
    (r'\bgit\s+push\s+--force\b', 'git push --force: Overwrites remote history. Use `git push --force-with-lease` instead.'),
    (r'\bgit\s+push\s+\-f\b', 'git push -f: Overwrites remote history. Use `git push --force-with-lease` instead.'),
    (r'\bmkfs\b', 'mkfs: Formats a disk partition, destroying all data. Ensure correct device is selected.'),
    (r'\bchmod\s+777\b', 'chmod 777: Gives full permissions to everyone. Use more restrictive permissions.'),
    (r'\bchmod\s+-R\s+777\b', 'chmod -R 777: Recursively giving full permissions is extremely dangerous.'),
]

SAFE_COMMANDS = [
    r'\brm\s+-i\b',
    r'\bgit\s+push\s+--force-with-lease\b',
]


def is_safe_command(command):
    for pattern in SAFE_COMMANDS:
        if re.search(pattern, command, re.IGNORECASE):
            return True
    return False


def check_command(command):
    cmd = command.strip()
    if not cmd or cmd.startswith('#'):
        return False, None
    if is_safe_command(cmd):
        return False, None
    for pattern, reason in DANGEROUS_PATTERNS:
        if re.search(pattern, cmd, re.IGNORECASE):
            return True, reason
    return False, None


def log_blocked_attempt(command, reason, project_path):
    log_dir = os.path.expanduser('~/.claude/hooks')
    log_file = os.path.join(log_dir, 'blocked.log')
    os.makedirs(log_dir, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')
    log_entry = (
        f"[{timestamp}] BLOCKED: {command}\n"
        f"  Reason: {reason}\n"
        f"  Project: {project_path}\n"
        f"  ---\n"
    )
    try:
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(log_entry)
    except IOError as e:
        print(f"Warning: Could not write to {log_file}: {e}", file=sys.stderr)


def get_project_path():
    for env_var in ['CLAUDE_CODE_PROJECT_PATH', 'PROJECT_PATH', 'PWD', 'HOME']:
        path = os.environ.get(env_var)
        if path and os.path.isdir(path):
            return path
    return os.getcwd()


def pre_tool_use_hook(tool, input_data):
    if tool != 'bash':
        return None
    if isinstance(input_data, dict):
        command = input_data.get('command', '')
    elif isinstance(input_data, str):
        command = input_data
    else:
        return None
    is_dangerous, reason = check_command(command)
    if is_dangerous:
        project_path = get_project_path()
        log_blocked_attempt(command, reason, project_path)
        return {
            'blocked': True,
            'original_command': command,
            'reason': reason,
            'message': (
                f"COMMAND BLOCKED: '{command}' has been blocked by the pre-tool-use security hook.\n"
                f"\nReason: {reason}\n"
                f"Logged to ~/.claude/hooks/blocked.log"
            )
        }
    return None


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Test the pre-tool-use hook')
    parser.add_argument('command', nargs='?', help='Command to test')
    parser.add_argument('--test', action='store_true', help='Run all test cases')
    args = parser.parse_args()

    if args.test:
        print("=== Running Test Suite ===\n")
        test_cases = [
            ('rm -rf /', True, 'Recursive force delete'),
            ('rm -rf ./temp', True, 'Recursive force delete dir'),
            ('DROP TABLE users', True, 'Database table drop'),
            ('SELECT * FROM users', False, 'Safe SELECT query'),
            ('DELETE FROM users WHERE id=1', False, 'Safe DELETE with WHERE'),
            ('DELETE FROM users', True, 'Unsafe DELETE without WHERE'),
            ('git push --force', True, 'Force push'),
            ('git push --force-with-lease', False, 'Safe force push with lease'),
            ('git push origin main', False, 'Normal push'),
            ('ls -la', False, 'Normal ls command'),
            ('echo hello', False, 'Normal echo command'),
            ('TRUNCATE TABLE sessions', True, 'Table truncate'),
            ('chmod 777 /etc', True, 'World-writable permissions'),
            ('cat file.txt', False, 'Normal cat command'),
            ('pip install requests', False, 'Normal pip install'),
        ]
        passed = 0
        failed = 0
        for cmd, should_block, desc in test_cases:
            is_dangerous, reason = check_command(cmd)
            blocked = is_dangerous
            status = "PASS" if blocked == should_block else "FAIL"
            result = "BLOCKED" if blocked else "ALLOWED"
            if blocked == should_block:
                passed += 1
            else:
                failed += 1
            print(f"{status} | {result:<8} | {desc}")
            print(f"       Command: {cmd}")
            if reason:
                print(f"       Reason: {reason[:80]}")
            print()
        print(f"Results: {passed}/{len(test_cases)} passed, {failed} failed")
    elif args.command:
        is_dangerous, reason = check_command(args.command)
        if is_dangerous:
            print(f"BLOCKED: {args.command}")
            print(f"Reason: {reason}")
        else:
            print(f"ALLOWED: {args.command}")
    else:
        print("Usage:")
        print("  python pre_tool_use_hook.py --test          # Run test suite")
        print("  python pre_tool_use_hook.py 'rm -rf /'       # Test a command")
