# Cutie 🐰

**Cutie** is a user-focused fork of the [VS Code Copilot extension](https://github.com/microsoft/vscode/tree/main/extensions/copilot).

## Introduction

Cutie is built on top of the VS Code Copilot extension source code (which has been merged into the VS Code monorepo), with the goal of delivering a more user-friendly and customizable experience. The project uses **patch files** to apply changes on top of the original source.

- **Origin:** [microsoft/vscode/extensions/copilot](https://github.com/microsoft/vscode/tree/main/extensions/copilot)
- **Remote:** [AnNhiAI/Cutie](https://github.com/AnNhiAI/Cutie)

## Project Structure

```
cutie/
├── patches/          # Patch files (.patch) containing Cutie customizations
├── original/         # Original source from VS Code Copilot (cloned by get_original.py)
├── scripts/          # Scripts for working with patches
│   ├── get_original.py
│   └── apply_patches.py
├── .gitignore
├── .gitattributes
└── README.md
```

## How It Works

1. The **original source** from VS Code Copilot is downloaded into `original/` using `get_original.py`
2. **Cutie customizations** are packaged as `.patch` files under `patches/`
3. **`apply_patches.py`** applies those patches to the original source

## Scripts

### `scripts/get_original.py`

Downloads the latest VS Code Copilot source into the `original/` directory.

```bash
python scripts/get_original.py
```

This clones the [microsoft/vscode](https://github.com/microsoft/vscode) repository with sparse checkout,
keeping only the `extensions/copilot/` subtree on disk.

### `scripts/apply_patches.py`

Applies all `.patch` files from `patches/` to the corresponding files in `original/`.

```bash
python scripts/apply_patches.py              # Apply all patches
python scripts/apply_patches.py --check      # Dry-run: verify patches can be applied
python scripts/apply_patches.py --reverse    # Un-apply all patches
python scripts/apply_patches.py --verbose    # Show detailed per-patch output
python scripts/apply_patches.py --yes        # Skip prompts (CI/non-interactive use)
```

#### Options

| Flag              | Description                                         |
|-------------------|-----------------------------------------------------|
| `--check`         | Dry-run — check if patches apply without modifying  |
| `--reverse`       | Reverse (un-apply) all patches                      |
| `--verbose`       | Show patch and target paths for each patch          |
| `-y` / `--yes`    | Skip confirmation prompts (for CI/automation)       |

The script discovers all `.patch` files recursively under `patches/`, reads the target
path from each patch's `---` header line, and uses the `patch` command with `-p1` to
apply it. If a patch has already been applied, it is detected and skipped gracefully.

## Workflow

```bash
# 1. Download the original VS Code Copilot source
python scripts/get_original.py

# 2. Verify patches can be applied cleanly
python scripts/apply_patches.py --check

# 3. Apply all Cutie customizations
python scripts/apply_patches.py

# 4. (Optional) Revert patches and restore the original source
python scripts/apply_patches.py --reverse
```

## Requirements

- **Python 3.10+**
- **Git** (for `get_original.py`)
- **`patch` command** (included with Git for Windows / Git Bash, or GNU patch on Linux)
- Node.js >= 22.14.0
- npm >= 9.0.0
- VS Code

## License

### Original Code
The original VS Code Copilot extension code is licensed under the MIT License by Microsoft Corporation.
See the original license at: https://github.com/microsoft/vscode/blob/main/LICENSE.txt

### Modifications
All modifications, patches, and customizations made by An Nhi AI (Sao Tin) are licensed under the Apache License 2.0.

Copyright 2026 An Nhi AI - Sao Tin

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

## Credits

- **Original Extension:** [Microsoft VS Code Copilot](https://github.com/microsoft/vscode/tree/main/extensions/copilot)
- **Modifications by:** An Nhi AI - Sao Tin
- **Project:** CutieChat - A community fork of GitHub Copilot Chat
