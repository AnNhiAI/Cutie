#!/usr/bin/env python3
"""
get_original.py — Download and filter the VS Code Copilot original source.

Steps:
1. Clone the microsoft/vscode repo into the `original/` directory
   (prefers the GitHub CLI `gh`, falls back to `git`).
2. Use sparse checkout so only `extensions/copilot/` is kept on disk.
"""

import os
import subprocess
import shutil
import sys
from pathlib import Path

REPO_URL = "https://github.com/microsoft/vscode.git"
GH_REPO = "microsoft/vscode"

PROJECT_ROOT = Path(__file__).resolve().parent.parent
ORIGINAL_DIR = PROJECT_ROOT / "original"


def log(msg):
    """Print a status message and flush immediately so the user sees progress."""
    print(msg, flush=True)


def run(cmd, cwd=None):
    """Run a command, streaming stderr (for progress), and check the exit code."""
    log(f"  $ {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    if result.returncode != 0:
        log(f"  ERROR: command failed (exit code {result.returncode})")
        if result.stderr:
            log(result.stderr)
        sys.exit(1)
    return result


def on_rmtree_error(func, path, exc_info):
    """Handle permission-denied errors during rmtree (common on Windows with .git)."""
    os.chmod(path, 0o777, follow_symlinks=False)
    func(path)


def remove_dir(path):
    """Safely remove a directory tree, handling Windows permission issues."""
    if path.exists():
        log(f"Removing existing '{path}' …")
        shutil.rmtree(path, onerror=on_rmtree_error)


def check_dependencies():
    """Check that `gh` or `git` is available, and that `gh` is authenticated."""
    git = shutil.which("git")
    if not git:
        log("Error: `git` is not installed or not in PATH.")
        sys.exit(1)

    gh = shutil.which("gh")
    if gh:
        auth = subprocess.run([gh, "auth", "status"], capture_output=True, text=True)
        if auth.returncode != 0:
            log("Warning: `gh` is installed but not authenticated. Falling back to `git`.")
            gh = None

    return gh, git


def clone_with_sparse_checkout(gh, git):
    """Clone the repo and set up sparse checkout so only extensions/copilot/ is kept on disk."""
    remove_dir(ORIGINAL_DIR)

    if gh:
        log("Using GitHub CLI (`gh`).")
        run([gh, "repo", "clone", GH_REPO, str(ORIGINAL_DIR),
             "--", "--filter=blob:none", "--no-checkout"])
    else:
        log("Using `git` with HTTPS.")
        run([git, "clone", "--filter=blob:none", "--no-checkout",
             REPO_URL, str(ORIGINAL_DIR)])

    log("Configuring sparse checkout for `extensions/copilot/` only …")
    # Use --no-cone to avoid git checking out root-level files by default
    run(["git", "sparse-checkout", "init", "--no-cone"], cwd=ORIGINAL_DIR)
    run(["git", "sparse-checkout", "set", "/extensions/copilot/**"], cwd=ORIGINAL_DIR)
    run(["git", "checkout"], cwd=ORIGINAL_DIR)

    # Safety cleanup: remove any files/dirs outside .git and extensions/copilot/
    log("Cleaning up leftover files …")
    for item in ORIGINAL_DIR.iterdir():
        if item.name == ".git":
            continue
        if item.name == "extensions":
            # Remove everything inside extensions/ except copilot/
            for sub in item.iterdir():
                if sub.name != "copilot":
                    shutil.rmtree(sub, onerror=on_rmtree_error)
            continue
        # Remove any remaining root-level files or directories
        if item.is_dir():
            shutil.rmtree(item, onerror=on_rmtree_error)
        else:
            item.unlink()

    log(f"\nDone! Only `extensions/copilot/` remains in '{ORIGINAL_DIR}'.")


def main():
    gh, git = check_dependencies()
    clone_with_sparse_checkout(gh, git)


if __name__ == "__main__":
    main()
