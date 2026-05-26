#!/usr/bin/env python3
import sys
import os
import argparse
from PySide6.QtCore import QUrl, QSettings, Qt, QSize
from PySide6.QtGui import QIcon, QAction, QKeySequence, QDesktopServices
from PySide6.QtNetwork import QLocalServer, QLocalSocket
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QSystemTrayIcon,
    QMenu,
    QStyle,
    QMessageBox
)
from PySide6.QtWebEngineCore import (
    QWebEngineProfile,
    QWebEnginePage,
    QWebEngineScript,
    QWebEngineSettings
)
from PySide6.QtWebEngineWidgets import QWebEngineView

# Define a modern User Agent
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
TARGET_URL = "http://127.0.0.1:60010"
MAIN_DOMAIN = "127.0.0.1"

class CustomWebEnginePage(QWebEnginePage):
    def __init__(self, profile, parent=None):
        super().__init__(profile, parent)
        self.parent_window = parent

    def acceptNavigationRequest(self, url, _type, isMainFrame):
        # Open external links in user's default browser
        if _type == QWebEnginePage.NavigationType.NavigationTypeLinkClicked:
            host = url.host().lower()
            # Allow target domain, subdomains, and common auth/content CDNs
            allowed_suffixes = [
                MAIN_DOMAIN,
                "github.com", # Allow github logins
                "google.com", # Allow google logins
                "microsoft.com", # Allow microsoft logins
                "cloudflare.com",
                "fastly.net"
            ]
            
            is_allowed = False
            for suffix in allowed_suffixes:
                if host == suffix or host.endswith("." + suffix):
                    is_allowed = True
                    break
            
            if not is_allowed:
                QDesktopServices.openUrl(url)
                return False
        return True

class WrapperWindow(QMainWindow):
    def __init__(self, windows_list, shared_profile=None, profile_name="Hacker NewsProfile"):
        super().__init__()
        self.windows_list = windows_list
        self.profile_name = profile_name
        self.is_quitting = False
        
        # Load window settings
        self.settings = QSettings("Hacker NewsDesktop", f"AppName_{profile_name}")
        
        # Set Window Properties
        title = "Hacker News" if profile_name == "Hacker NewsProfile" else f"Hacker News ({profile_name.capitalize()})"
        self.setWindowTitle(title)
        self.setMinimumSize(800, 600)
        
        # Determine Icon Path
        self.app_dir = os.path.dirname(os.path.abspath(__file__))
        icon_path = os.path.join(self.app_dir, "icon.png")
        if os.path.exists(icon_path):
            self.app_icon = QIcon(icon_path)
        else:
            self.app_icon = QApplication.style().standardIcon(QStyle.StandardPixmap.SP_ComputerIcon)
        
        self.setWindowIcon(self.app_icon)
        
        # Setup WebEngine View
        self.web_view = QWebEngineView(self)
        self.setCentralWidget(self.web_view)
        
        # Configure Profile and User Agent
        if shared_profile:
            self.profile = shared_profile
        else:
            self.profile = QWebEngineProfile(profile_name, self)
            self.profile.setHttpUserAgent(USER_AGENT)
            self.profile.setPersistentCookiesPolicy(QWebEngineProfile.PersistentCookiesPolicy.ForcePersistentCookies)
            
            # Configure Client Hints if supported (Qt 6.8+)
            if hasattr(self.profile, "clientHints"):
                try:
                    hints = self.profile.clientHints()
                    hints.setPlatform("Windows")
                    hints.setPlatformVersion("15.0.0")
                    hints.setArch("x86")
                    hints.setBitness("64")
                    hints.setIsMobile(False)
                    hints.setIsWow64(False)
                    hints.setFullVersion("128.0.0.0")
                    hints.setFullVersionList({
                        "Google Chrome": "128.0.0.0",
                        "Chromium": "128.0.0.0",
                        "Not;A=Brand": "24.0.0.0"
                    })
                    hints.setAllClientHintsEnabled(True)
                except Exception as e:
                    print(f"Warning: Could not configure client hints: {e}")
        
        # Enable features
        web_settings = self.profile.settings()
        web_settings.setAttribute(QWebEngineSettings.WebAttribute.JavascriptEnabled, True)
        web_settings.setAttribute(QWebEngineSettings.WebAttribute.LocalStorageEnabled, True)
        web_settings.setAttribute(QWebEngineSettings.WebAttribute.ScrollAnimatorEnabled, True)
        web_settings.setAttribute(QWebEngineSettings.WebAttribute.FullScreenSupportEnabled, True)
        web_settings.setAttribute(QWebEngineSettings.WebAttribute.PluginsEnabled, True)
        web_settings.setAttribute(QWebEngineSettings.WebAttribute.FocusOnNavigationEnabled, True)
        
        # Set Custom Web Page
        self.web_page = CustomWebEnginePage(self.profile, self)
        self.web_view.setPage(self.web_page)
        
        # Handle Fullscreen Requests
        self.web_page.fullScreenRequested.connect(self.handle_fullscreen)
        
        # Inject Custom CSS (Dark Scrollbars and UI Tweaks)
        if not shared_profile:
            self.inject_styles()
        
        # Create Tray Icon
        self.setup_tray()
        
        # Setup Shortcuts
        self.setup_shortcuts()
        
        # Restore window geometry/state
        self.restore_window_state()
        
        # Load target site
        self.web_view.load(QUrl(TARGET_URL))

    def inject_styles(self):
        script = QWebEngineScript()
        script.setInjectionPoint(QWebEngineScript.InjectionPoint.DocumentReady)
        script.setWorldId(QWebEngineScript.ScriptWorldId.MainWorld)
        
        css = '''
        /* Modern Thin Scrollbars matching site colors */
        ::-webkit-scrollbar {
            width: 8px !important;
            height: 8px !important;
        }
        ::-webkit-scrollbar-track {
            background: #f4f4f5 !important;
        }
        ::-webkit-scrollbar-thumb {
            background: #d4d4d8 !important;
            border-radius: 4px !important;
        }
        ::-webkit-scrollbar-thumb:hover {
            background: #a1a1aa !important;
        }
        
        /* Smooth scrolling */
        html {
            scroll-behavior: smooth !important;
        }
        '''
        
        js_code = f"var style = document.createElement('style'); style.id = 'app-desktop-styles'; style.textContent = `{css}`; document.head.appendChild(style);"
        
        script.setSourceCode(js_code)
        self.profile.scripts().insert(script)

    def setup_shortcuts(self):
        # Reload: Ctrl+R / F5
        self.act_reload1 = QAction(self)
        self.act_reload1.setShortcut(QKeySequence("Ctrl+R"))
        self.act_reload1.triggered.connect(self.web_view.reload)
        self.addAction(self.act_reload1)
        
        self.act_reload2 = QAction(self)
        self.act_reload2.setShortcut(QKeySequence("F5"))
        self.act_reload2.triggered.connect(self.web_view.reload)
        self.addAction(self.act_reload2)
        
        # Zoom Controls
        self.act_zoom_in = QAction(self)
        self.act_zoom_in.setShortcut(QKeySequence("Ctrl++"))
        self.act_zoom_in.triggered.connect(self.zoom_in)
        self.addAction(self.act_zoom_in)
        
        self.act_zoom_out = QAction(self)
        self.act_zoom_out.setShortcut(QKeySequence("Ctrl+-"))
        self.act_zoom_out.triggered.connect(self.zoom_out)
        self.addAction(self.act_zoom_out)
        
        self.act_zoom_reset = QAction(self)
        self.act_zoom_reset.setShortcut(QKeySequence("Ctrl+0"))
        self.act_zoom_reset.triggered.connect(self.zoom_reset)
        self.addAction(self.act_zoom_reset)
        
        # Navigation
        self.act_back = QAction(self)
        self.act_back.setShortcut(QKeySequence("Alt+Left"))
        self.act_back.triggered.connect(self.web_view.back)
        self.addAction(self.act_back)
        
        self.act_forward = QAction(self)
        self.act_forward.setShortcut(QKeySequence("Alt+Right"))
        self.act_forward.triggered.connect(self.web_view.forward)
        self.addAction(self.act_forward)

        # New Window Shortcut: Ctrl+N
        self.act_new_win_shortcut = QAction(self)
        self.act_new_win_shortcut.setShortcut(QKeySequence("Ctrl+N"))
        self.act_new_win_shortcut.triggered.connect(self.open_new_window)
        self.addAction(self.act_new_win_shortcut)

    def zoom_in(self):
        self.web_view.setZoomFactor(self.web_view.zoomFactor() + 0.1)

    def zoom_out(self):
        self.web_view.setZoomFactor(max(0.2, self.web_view.zoomFactor() - 0.1))

    def zoom_reset(self):
        self.web_view.setZoomFactor(1.0)

    def open_new_window(self):
        new_win = WrapperWindow(self.windows_list, shared_profile=self.profile, profile_name=self.profile_name)
        self.windows_list.append(new_win)
        new_win.show()

    def reset_app(self):
        reply = QMessageBox.question(
            self,
            "Reset App Settings",
            "This will clear all cache, cookies, and settings, and log you out. Are you sure?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.profile.cookieStore().deleteAllCookies()
            self.profile.clearHttpCache()
            self.web_view.setZoomFactor(1.0)
            self.web_view.load(QUrl(TARGET_URL))
            QMessageBox.information(self, "Reset", "Application cache and cookies have been cleared. Please sign in again.")

    def handle_fullscreen(self, request):
        request.accept()
        if request.toggleOn():
            self.showFullScreen()
        else:
            self.showNormal()

    def setup_tray(self):
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(self.app_icon)
        tooltip = "Hacker News" if self.profile_name == "Hacker NewsProfile" else f"Hacker News ({self.profile_name.capitalize()})"
        self.tray_icon.setToolTip(tooltip)
        
        # Tray Menu
        self.tray_menu = QMenu()
        
        act_show = QAction("Show / Hide", self)
        act_show.triggered.connect(self.toggle_visibility)
        self.tray_menu.addAction(act_show)
        
        act_new_win = QAction("New Window", self)
        act_new_win.triggered.connect(self.open_new_window)
        self.tray_menu.addAction(act_new_win)
        
        act_reload = QAction("Reload Page", self)
        act_reload.triggered.connect(self.web_view.reload)
        self.tray_menu.addAction(act_reload)
        
        act_reset = QAction("Clear Cache & Cookies", self)
        act_reset.triggered.connect(self.reset_app)
        self.tray_menu.addAction(act_reset)
        
        self.tray_menu.addSeparator()
        
        act_quit = QAction("Quit", self)
        act_quit.triggered.connect(self.quit_app)
        self.tray_menu.addAction(act_quit)
        
        self.tray_icon.setContextMenu(self.tray_menu)
        self.tray_icon.activated.connect(self.tray_activated)
        self.tray_icon.show()

    def tray_activated(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            self.toggle_visibility()

    def toggle_visibility(self):
        if self.isVisible():
            if self.isMinimized():
                self.showNormal()
                self.raise_()
                self.activateWindow()
            else:
                self.hide()
        else:
            self.showNormal()
            self.raise_()
            self.activateWindow()

    def closeEvent(self, event):
        if self.is_quitting:
            self.settings.setValue("geometry", self.saveGeometry())
            self.settings.setValue("windowState", self.saveState())
            event.accept()
            return

        visible_count = sum(1 for w in self.windows_list if w.isVisible())
        
        if visible_count > 1:
            if self in self.windows_list:
                self.windows_list.remove(self)
            self.deleteLater()
            event.accept()
        else:
            event.ignore()
            self.hide()
            if not self.settings.value("tray_notice_shown", False):
                self.tray_icon.showMessage(
                    "Hacker News App",
                    "Hacker News is running in the background. Use the system tray icon to open or close it.",
                    QSystemTrayIcon.MessageIcon.Information,
                    5000
                )
                self.settings.setValue("tray_notice_shown", True)

    def quit_app(self):
        self.is_quitting = True
        for w in list(self.windows_list):
            w.is_quitting = True
            w.close()
        QApplication.quit()

    def restore_window_state(self):
        geometry = self.settings.value("geometry")
        state = self.settings.value("windowState")
        
        if geometry:
            self.restoreGeometry(geometry)
        else:
            self.resize(1024, 768)
            screen = QApplication.primaryScreen().geometry()
            size = self.geometry()
            self.move((screen.width() - size.width()) // 2, (screen.height() - size.height()) // 2)
            
        if state:
            self.restoreState(state)

def main():
    os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"
    
    parser = argparse.ArgumentParser(description="Hacker News Desktop Application")
    parser.add_argument("-p", "--profile", type=str, default="Hacker NewsProfile", help="Profile name for separating accounts")
    args, unknown = parser.parse_known_args()
    
    profile_name = args.profile
    
    app = QApplication(sys.argv)
    app.setApplicationName(f"AppName_{profile_name}")
    app.setOrganizationName("Hacker NewsDesktop")
    app.setDesktopFileName("hacker news")
    app.setQuitOnLastWindowClosed(False)
    
    socket_name = f"AppLock_{profile_name}"
    socket = QLocalSocket()
    socket.connectToServer(socket_name)
    if socket.waitForConnected(500):
        socket.write(b"show")
        socket.waitForBytesWritten(1000)
        return
        
    server = QLocalServer()
    server.removeServer(socket_name)
    server.listen(socket_name)
    
    windows = []
    
    def create_window():
        win = WrapperWindow(windows, profile_name=profile_name)
        windows.append(win)
        win.show()
        return win
        
    def handle_new_connection():
        client = server.nextPendingConnection()
        if client.waitForReadyRead(1000):
            data = client.readAll().data()
            if data == b"show":
                if windows:
                    first_win = windows[0]
                    first_win.showNormal()
                    first_win.raise_()
                    first_win.activateWindow()
                else:
                    create_window()
            client.close()
            
    server.newConnection.connect(handle_new_connection)
    create_window()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
