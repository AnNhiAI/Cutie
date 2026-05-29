#!/usr/bin/env python3
"""Add missing --- a/ and +++ b/ headers to patch files."""

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
PATCHES_DIR = PROJECT_ROOT / "patches"

def fix_patch_file(patch_path: Path) -> bool:
    """Add or fix header in a patch file."""
    content = patch_path.read_text(encoding="utf-8")
    
    # Derive the target path from patch file location
    # patches/copilot/src/foo/bar.ts.patch -> original/extensions/copilot/src/foo/bar.ts
    rel_path = patch_path.relative_to(PATCHES_DIR)
    target_path = "original/extensions" / rel_path.with_suffix("")
    
    # Check if header exists and is correct
    correct_header_start = f"--- a/{target_path.as_posix()}\n+++ b/{target_path.as_posix()}\n"
    
    if content.startswith(correct_header_start):
        print(f"  ✓ {patch_path.name} (header OK)")
        return False
    
    # Remove old header if exists (lines starting with --- or +++)
    lines = content.splitlines(keepends=True)
    start_idx = 0
    
    # Skip old --- and +++ lines
    if lines and lines[0].startswith("--- "):
        start_idx = 1
        if len(lines) > 1 and lines[1].startswith("+++ "):
            start_idx = 2
    
    # Reconstruct content without old header
    body = "".join(lines[start_idx:])
    
    # Add correct header
    new_content = correct_header_start + body
    
    patch_path.write_text(new_content, encoding="utf-8")
    print(f"  ✓ {patch_path.name} (fixed header)")
    return True

def main():
    patches = sorted(PATCHES_DIR.rglob("*.patch"))
    
    if not patches:
        print("No patch files found.")
        return
    
    print(f"Fixing {len(patches)} patch file(s)...\n")
    
    fixed = 0
    for patch_path in patches:
        if fix_patch_file(patch_path):
            fixed += 1
    
    print(f"\nFixed {fixed} patch file(s).")

if __name__ == "__main__":
    main()
