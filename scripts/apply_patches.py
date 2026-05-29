#!/usr/bin/env python3
"""
apply_patches.py — Apply Cutie patch files to the original VS Code Copilot source.

Usage:
    python scripts/apply_patches.py              # Apply all patches
    python scripts/apply_patches.py --check      # Dry-run: check which patches would apply
    python scripts/apply_patches.py --reverse    # Reverse (un-apply) all patches
    python scripts/apply_patches.py --verbose    # Show detailed per-patch output

The script discovers all `.patch` files under `patches/`, and for each one:

  patches/copilot/src/foo/bar.ts.patch
      ↓ (read the `---` line inside the patch, strip `a/` prefix)
  original/extensions/copilot/src/foo/bar.ts

Then uses the `patch` command to apply (or reverse) the patch.
"""

import argparse
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
PATCHES_DIR = PROJECT_ROOT / "patches"
ORIGINAL_DIR = PROJECT_ROOT / "original"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def log(msg: str) -> None:
    print(msg, flush=True)


def err(msg: str) -> None:
    print(msg, file=sys.stderr, flush=True)


def resolve_target(patch_path: Path) -> Path | None:
    """
    Given a patch file path like:
        patches/copilot/src/foo/bar.ts.patch

    Return the corresponding original file path by reading the `---`
    line from the patch, stripping the `a/` prefix:

        original/extensions/copilot/src/foo/bar.ts

    The returned path is relative to PROJECT_ROOT (the patch `---` paths
    already start with `original/`).

    Returns None if the patch file doesn't have a valid `---` header.
    """
    try:
        header = patch_path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return None

    # Parse the first `--- ` line (the old-file path)
    for line in header.splitlines():
        if line.startswith("--- "):
            # Strip "--- " prefix
            raw_path = line[4:].strip()
            # Strip timestamp if present (tab-separated)
            if "\t" in raw_path:
                raw_path = raw_path.split("\t")[0]
            # Strip `a/` prefix
            if raw_path.startswith("a/"):
                raw_path = raw_path[2:]
            # The path is relative to the project root (e.g. original/extensions/...)
            return PROJECT_ROOT / raw_path

    return None


def find_all_patches() -> list[Path]:
    """Return a sorted list of all `.patch` files under `patches/`."""
    return sorted(PATCHES_DIR.rglob("*.patch"))


def check_patch_available() -> bool:
    """Verify that the `patch` command is available."""
    try:
        result = subprocess.run(
            ["patch", "--version"],
            capture_output=True, text=True,
            shell=True,
        )
        return result.returncode == 0
    except FileNotFoundError:
        return False


# ---------------------------------------------------------------------------
# Apply / reverse logic
# ---------------------------------------------------------------------------

def apply_single_patch(
    patch_path: Path,
    *,
    reverse: bool = False,
    check: bool = False,
) -> bool:
    """
    Apply (or reverse) a single patch file using the `patch` command.

    Returns True on success, False on failure.
    """
    cmd = ["patch", "-p1", "--batch", "--forward"]

    if reverse:
        cmd.append("-R")
    if check:
        cmd.append("--dry-run")

    cmd.extend(["-i", str(patch_path)])

    try:
        result = subprocess.run(
            cmd,
            capture_output=True, text=True,
            cwd=str(PROJECT_ROOT),
            shell=True,
        )
    except FileNotFoundError:
        err("  ERROR: `patch` command is not available.")
        sys.exit(1)

    if result.returncode == 0:
        if not check:
            action = "Reversed" if reverse else "Applied"
            log(f"  ✓ {action}")
        return True
    else:
        if check:
            log(f"  ✗ Would fail")
        else:
            log(f"  ✗ Failed")
        if result.stdout:
            log(f"    {result.stdout.strip()}")
        if result.stderr:
            log(f"    {result.stderr.strip()}")
        return False


def apply_all_patches(
    *,
    reverse: bool = False,
    check: bool = False,
    verbose: bool = False,
) -> int:
    """
    Apply/reverse/check all patches. Returns the number of failures.
    """
    patches = find_all_patches()

    if not patches:
        log("No `.patch` files found under 'patches/'.")
        return 0

    action = "Checking" if check else ("Reversing" if reverse else "Applying")
    log(f"{action} {len(patches)} patch(es) ...\n")

    failures = 0
    skipped = 0
    succeeded = 0

    for patch_path in patches:
        stem = patch_path.stem
        log(f"  [{stem}]")

        target = resolve_target(patch_path)

        if target is None:
            skipped += 1
            if verbose:
                log(f"     skipped — could not parse `---` path from patch")
            log("")
            continue

        if not target.exists():
            log(f"     ⚠ Target not found: {target}")
            log(f"     Skipping — run `python scripts/get_original.py` first?")
            skipped += 1
            log("")
            continue

        if verbose:
            log(f"     patch : {patch_path}")
            log(f"     target: {target}")

        ok = apply_single_patch(
            patch_path,
            reverse=reverse, check=check,
        )
        if ok:
            succeeded += 1
        else:
            failures += 1
        log("")

    # Summary
    total = len(patches)
    log(f"── Summary ──────────────────────────────────")
    log(f"  Total patches : {total}")
    log(f"  Succeeded     : {succeeded}")
    log(f"  Skipped       : {skipped}")
    log(f"  Failed        : {failures}")
    log(f"─────────────────────────────────────────────")

    if failures > 0:
        if check:
            log("Use `python scripts/apply_patches.py` (without --check) to apply.")
        else:
            log("Fix the issues above and re-run.")

    return failures


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Apply Cutie patches to the original VS Code Copilot source.",
    )
    parser.add_argument(
        "--check", action="store_true",
        help="Dry-run: check if patches would apply cleanly without modifying files.",
    )
    parser.add_argument(
        "--reverse", action="store_true",
        help="Reverse (un-apply) all patches.",
    )
    parser.add_argument(
        "--verbose", action="store_true",
        help="Show detailed output for each patch.",
    )
    parser.add_argument(
        "-y", "--yes", action="store_true",
        help="Skip confirmation prompts (useful for non-interactive/CI use).",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    if not PATCHES_DIR.is_dir():
        err(f"Error: patches directory not found at '{PATCHES_DIR}'.")
        err("Make sure you're running this script from the project root.")
        sys.exit(1)

    if not ORIGINAL_DIR.is_dir():
        log("Warning: 'original/' directory not found.")
        log("Run `python scripts/get_original.py` first to download the VS Code Copilot source.")
        log("")
        proceed = args.yes
        if not proceed:
            answer = input("Continue anyway? (y/N): ").strip().lower()
            proceed = answer in ("y", "yes")
        if not proceed:
            log("Aborting.")
            sys.exit(1)

    if not check_patch_available():
        err("Error: `patch` command is required but not found in PATH.")
        err("Install Git for Windows (which includes patch) or the GNU patch utility.")
        sys.exit(1)

    failures = apply_all_patches(
        reverse=args.reverse,
        check=args.check,
        verbose=args.verbose,
    )

    if args.check and failures == 0:
        log("All patches can be applied cleanly ✓")

    sys.exit(1 if failures > 0 and not args.check else 0)


if __name__ == "__main__":
    main()
