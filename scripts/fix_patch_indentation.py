#!/usr/bin/env python3
"""Fix patch files that have extra leading spaces."""

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
PATCHES_DIR = PROJECT_ROOT / "patches"

def fix_patch_indentation(patch_path: Path) -> bool:
    """Remove extra leading space from patch lines."""
    lines = patch_path.read_text(encoding="utf-8").splitlines(keepends=True)
    
    fixed_lines = []
    changed = False
    
    for line in lines:
        # Skip header lines (---, +++, don't modify them)
        if line.startswith("--- ") or line.startswith("+++ "):
            fixed_lines.append(line)
            continue
        
        # Hunk headers should not have leading space
        if line.startswith(" @@"):
            fixed_lines.append(line[1:])  # Remove 1 leading space
            changed = True
            continue
        
        # Context/add/remove lines: should have exactly 1 space/+/- prefix
        # If line starts with 2 spaces, it's a context line with extra space
        if line.startswith("  "):
            fixed_lines.append(" " + line[2:])  # Keep 1 space, remove extra
            changed = True
        elif line.startswith(" -") or line.startswith(" +"):
            fixed_lines.append(line[1:])  # Remove extra leading space
            changed = True
        else:
            fixed_lines.append(line)
    
    if changed:
        patch_path.write_text("".join(fixed_lines), encoding="utf-8")
        print(f"  ✓ {patch_path.name} (fixed indentation)")
        return True
    else:
        print(f"  ✓ {patch_path.name} (indentation OK)")
        return False

def main():
    patches = sorted(PATCHES_DIR.rglob("*.patch"))
    
    if not patches:
        print("No patch files found.")
        return
    
    print(f"Fixing indentation in {len(patches)} patch file(s)...\n")
    
    fixed = 0
    for patch_path in patches:
        if fix_patch_indentation(patch_path):
            fixed += 1
    
    print(f"\nFixed {fixed} patch file(s).")

if __name__ == "__main__":
    main()
