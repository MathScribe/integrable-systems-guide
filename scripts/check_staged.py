#!/usr/bin/env python3
"""Check the Git index, so unstaged fixes cannot hide a broken staged record."""
from __future__ import annotations

import os
import subprocess
import sys
import tempfile
from pathlib import Path


def check_staged(root: Path) -> int:
    result = subprocess.run(['git', 'diff', '--cached', '--name-only', '-z'], cwd=root,
                            check=True, capture_output=True)
    paths = result.stdout.decode('utf-8').split('\0')
    if not any(path.startswith(('data/', 'docs/', 'scripts/')) for path in paths):
        print('No staged content or validation changes.')
        return 0
    # A workspace-local temporary tree is readable by child processes in Windows sandboxes.
    with tempfile.TemporaryDirectory(prefix='.staged-check-', dir=root) as directory:
        snapshot = Path(directory)
        subprocess.run(['git', 'checkout-index', '--all', '--force',
                        '--prefix=' + snapshot.as_posix() + '/'], cwd=root, check=True)
        env = os.environ.copy()
        env['PYTHONDONTWRITEBYTECODE'] = '1'
        return subprocess.run([sys.executable, str(snapshot / 'scripts/validate_content.py'),
                               '--root', str(snapshot)], cwd=snapshot, env=env).returncode


if __name__ == '__main__':
    raise SystemExit(check_staged(Path(__file__).resolve().parents[1]))
