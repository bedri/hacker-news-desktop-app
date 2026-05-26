# Hacker News Desktop Wrapper

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)

A modern, fast, and feature-rich desktop wrapper for Hacker News built with **PySide6 (Qt WebEngine)**. It integrates seamlessly into your desktop environment with system tray support, multi-profile isolation, and native shortcut controls.

---

## ✨ Features

- **System Tray Integration**: Close the application to minimize it to the tray, keeping it active in the background. Right-click the tray icon to quickly open new windows, clear cache, or quit.
- **Single Instance Lock**: Running the app launcher again will bring your existing window to focus instead of launching duplicate instances.
- **Multi-Profile Support**: Launch multiple isolated instances (e.g., for different accounts) by specifying a profile name via the command line. Each profile keeps its own cookies, cache, and window geometries.
- **Multi-Window Support**: Open multiple windows sharing the same session using `Ctrl + N` or the system tray menu.
- **Smart Link Handling**: Content and login links (Hacker News, GitHub, Google, Microsoft, etc.) open inside the app, while external article links are automatically redirected to your system's default web browser.
- **Desktop Launcher Installer**: Includes an installer script (`install.sh`) that sets up a local python virtual environment, installs dependencies, and creates a `.desktop` file to integrate the application into your system menu.
- **Modern UI Adjustments**: Features custom scrollbars that match the site theme and smooth scrolling.
- **Keyboard Shortcuts & Zoom Controls**: Responsive keyboard controls for navigation and font size adjustments.

---

## ⌨️ Keyboard Shortcuts

| Shortcut | Action |
| :--- | :--- |
| `Ctrl` + `R` / `F5` | Reload Page |
| `Alt` + `Left Arrow` | Go Back |
| `Alt` + `Right Arrow` | Go Forward |
| `Ctrl` + `N` | Open New Window (shared session) |
| `Ctrl` + `+` | Zoom In |
| `Ctrl` + `-` | Zoom Out |
| `Ctrl` + `0` | Reset Zoom |

---

## 🚀 Installation & Setup

### Automated Installation (Linux)

An installer script is provided to automate environment setup, dependency installation, and launcher registration:

```bash
chmod +x install.sh
./install.sh
```

This script will:
1. Create a Python virtual environment (`.venv`) inside the project folder.
2. Install all requirements (`PySide6`).
3. Copy the application icon to `~/.local/share/icons`.
4. Register a desktop entry (`hackernews.desktop`) in `~/.local/share/applications/` so you can launch the app from your application menu/dashboard.

---

## 🛠️ Manual Run

If you want to run the application manually without installing:

1. **Set up virtual environment & install PySide6**:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Launch the application**:
   ```bash
   python3 app.py
   ```

### Command Line Options

You can isolate accounts or settings by using a custom profile name:

```bash
python3 app.py --profile work
```

---

## 📁 Project Structure

* `app.py`: Core application code written in Python using PySide6.
* `hacker-news-app`: Startup bash script wrapper.
* `install.sh`: Linux desktop installer.
* `icon.png`: Application logo.
* `requirements.txt`: Python package dependencies.
* `.gitignore`: Configured to ignore local environments (`.venv`), Python cache (`__pycache__`), and OS-specific files.
* `LICENSE`: GNU General Public License v3.0.

---

## 📄 License

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE](file:///home/bedri/Projects/Hacker%20News%20Desktop%20App/LICENSE) file for details.
