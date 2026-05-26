#!/usr/bin/env bash
set -e

PROJECT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
USER_ICONS_DIR="$HOME/.local/share/icons"
USER_APPS_DIR="$HOME/.local/share/applications"

echo "=== Hacker News Desktop App Installer ==="

# 1. Setup Icons
echo "Configuring application icons..."
mkdir -p "$USER_ICONS_DIR"

if [ -f "$PROJECT_DIR/icon.png" ]; then
    cp "$PROJECT_DIR/icon.png" "$USER_ICONS_DIR/hackernews-wrapper.png"
    echo "✔ Icon installed."
else
    echo "⚠️ Warning: icon.png not found."
fi

# 2. Setup Virtual Environment
echo "Setting up Python virtual environment..."
python3 -m venv "$PROJECT_DIR/.venv"
echo "✔ Virtual environment created."

# 3. Install Dependencies
echo "Installing Python dependencies (PySide6)..."
"$PROJECT_DIR/.venv/bin/pip" install --upgrade pip
"$PROJECT_DIR/.venv/bin/pip" install -r "$PROJECT_DIR/requirements.txt"
echo "✔ Dependencies installed."

# 4. Create Desktop Entry
echo "Registering application with system launcher..."
mkdir -p "$USER_APPS_DIR"

cat << EOF > "$USER_APPS_DIR/hackernews.desktop"
[Desktop Entry]
Name=Hacker News
Comment=Desktop Wrapper for Hacker News
Exec="$PROJECT_DIR/hacker-news-app"
Icon=hackernews-wrapper
Terminal=false
Type=Application
Categories=Network;WebBrowser;Qt;
StartupWMClass=AppName_Hacker NewsProfile
EOF

chmod +x "$USER_APPS_DIR/hackernews.desktop"
echo "✔ Desktop entry created."
echo "======================================"
echo "✔ Installation complete!"
echo "======================================"
