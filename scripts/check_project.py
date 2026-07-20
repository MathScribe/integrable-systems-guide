#!/usr/bin/env python3
"""Run the complete local validation used before opening a radar PR."""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def run(label: str, command: list[str]) -> None:
    print(f"\n== {label} ==", flush=True)
    subprocess.run(command, cwd=ROOT, check=True)


def main() -> None:
    python = sys.executable
    run("paper registry identities", [python, "scripts/validate_radar.py"])
    run("frontier data and controlled tags", [python, "scripts/validate_frontier_data.py"])
    run("radar regression tests", [python, "scripts/test_radar.py"])
    run("generated page consistency", [python, "scripts/render_radar.py", "--check"])

    node = shutil.which("node")
    if node is None:
        raise SystemExit("node is required for docs/javascripts/radar.js syntax validation")
    run("JavaScript syntax", [node, "--check", "docs/javascripts/radar.js"])

    # Let MkDocs create a fixed ignored workspace directory. On some Windows
    # sandbox profiles, directories created by tempfile are not re-openable by
    # a child process even though ordinary workspace paths are writable.
    site_dir = ROOT / "site-check"
    if site_dir.exists():
        shutil.rmtree(site_dir)
    run(
        "strict MkDocs build",
        [python, "-m", "mkdocs", "build", "--strict", "--site-dir", str(site_dir)],
    )
    shutil.rmtree(site_dir)

    print("\nAll project checks passed.")


if __name__ == "__main__":
    main()
