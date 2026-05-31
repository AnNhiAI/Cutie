#!/usr/bin/env python3
"""
Directly patch package.json with the required changes.
"""
import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
PACKAGE_JSON = PROJECT_ROOT / "original" / "extensions" / "copilot" / "package.json"

def main():
    print(f"Reading {PACKAGE_JSON}...")
    with open(PACKAGE_JSON, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    # Apply changes
    print("Applying changes...")
    data["name"] = "cutie-chat"
    data["displayName"] = "AnNhiAI CutieChat"
    data["description"] = "CutieChat is a community fork of GitHub Copilot Chat."
    data["publisher"] = "AnNhiAI"
    data["engines"]["vscode"] = "^1.95.0"
    
    print("Writing modified package.json...")
    with open(PACKAGE_JSON, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")
    
    print("✓ Successfully patched package.json")
    print(f"  - name: {data['name']}")
    print(f"  - displayName: {data['displayName']}")
    print(f"  - publisher: {data['publisher']}")
    print(f"  - vscode: {data['engines']['vscode']}")

if __name__ == "__main__":
    main()
