# Hướng dẫn Build Extension

## Thay đổi mới nhất (2026-05-31)
Script `rename_identifiers.py` đã được cập nhật để:
1. Rename chat participant display names: "GitHubCopilot" / "GitHub Copilot" → "Cutie"
2. **Rename view name từ "Chat" thành "Cutie"** để tránh nhầm lẫn với Copilot built-in trên sidebar

Điều này sẽ làm cho:
- Chat interface hiển thị "Cutie" thay vì "GitHub Copilot"
- Sidebar hiển thị view "Cutie" thay vì "Chat" (tránh conflict với Copilot built-in)

## Cách build extension

### 1. Chuẩn bị môi trường
Cần cài đặt:
- Node.js (đã có)
- Python 3.12+ (đã có)
- Visual Studio Build Tools (nếu build trên Windows)

### 2. Chạy scripts
```powershell
# Bước 1: Lấy code gốc
python scripts/get_original.py

# Bước 2: Apply patches (có thể bỏ qua nếu gặp lỗi quyền admin)
# python scripts/apply_patches.py --yes

# Bước 3: Patch package.json
python scripts/patch_package_json.py

# Bước 4: Rename identifiers (bao gồm chat participant names)
python scripts/rename_identifiers.py
```

### 3. Build extension
```powershell
cd original\extensions\copilot

# Cài dependencies (có thể mất nhiều thời gian)
npm install --omit=optional

# Compile
npm run compile

# Package thành VSIX
npx @vscode/vsce package --no-dependencies
```

### 4. Cài đặt
```powershell
# Gỡ extension cũ nếu có
code-insiders --uninstall-extension annhiai.cutie-chat

# Cài extension mới
code-insiders --install-extension cutie-chat-0.51.0.vsix

# Khởi động lại VS Code Insiders hoàn toàn
```

## Xác minh kết quả
Sau khi cài đặt và khởi động lại VS Code Insiders:
1. Mở chat panel
2. Kiểm tra xem tên hiển thị có phải là "Cutie" không (thay vì "GitHub Copilot")
3. Extension ID phải là `annhiai.cutie-chat`

## Lưu ý
- Nếu npm install gặp lỗi về sqlite3 hoặc Visual Studio, thử dùng `--omit=optional`
- Nếu compile lỗi thiếu esbuild, chạy `npm install` lại
- Phải khởi động lại VS Code hoàn toàn (tắt tất cả cửa sổ) để extension load đúng
