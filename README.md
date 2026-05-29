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
├── original/         # Original source from VS Code Copilot (git worktree/submodule)
├── scripts/          # Scripts for working with patches
├── .gitignore
├── .gitattributes
└── README.md
```

## How It Works

1. The **original source** from VS Code Copilot is kept in the `original/` directory
2. **Cutie customizations** are packaged as `.patch` files under `patches/`
3. **Scripts** in `scripts/` handle creating and applying patches

## Requirements

- Git
- Node.js >= 22.14.0
- npm >= 9.0.0
- VS Code

## License

This project is a fork of VS Code and follows the original project's license (MIT).
