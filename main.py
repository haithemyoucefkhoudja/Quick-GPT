import os

from PyQt6.QtGui import QIcon, QAction
from PyQt6.QtWidgets import QApplication, QSystemTrayIcon, QMenu
from Config import _configInstance
from exceptions.exception_handler import  UncaughtHook
from LLM.bot import Bot
from shortcutMonitor.shortcutMonitor import ShortcutMonitor

from ui.Transporter.Transporter import Sender

INTERVAL = 100  # Interval for checking keyboard shortcuts (milliseconds)

bot = Bot()
sender = Sender()

def handle_shortcut():
    """
    Monitors for the 'ctrl+c' keyboard shortcut. When detected twice in succession,
    triggers the sending of copied clipboard text.
    """
    # if w is not hidden it will break
    if w.isHidden():
        w.changePos()  # Second press; activate main window

    w.activateWindow()  # Attempts to give the window focus
    w.raise_()  # Raises the window to the top of the window stack

    clipboard = QApplication.clipboard()
    counter = 0
    # Send the shortcut signal to the Input Component
    sender.send_signal('shortcut_signal', clipboard.text())


if __name__ == '__main__':
    """
    Main entry point for the application.

    * Sets up a system tray icon and menu.
    * Launches the main application window.
    * Manages keyboard shortcut detection and response.
    """

    import sys
    from ui.app import MainWindow

    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    qt_exception_hook = UncaughtHook()
    # Load icon
    icon_path = _configInstance.get_path("static_files/icons/icon16.png")

    icon = QIcon(icon_path)
    app.setWindowIcon(icon)

    # System tray setup
    tray = QSystemTrayIcon()
    tray.setIcon(icon)
    tray.setVisible(True)

    # Tray menu setup
    menu = QMenu()
    quit = QAction("Quit")
    quit.triggered.connect(app.quit)

    menu.addAction(quit)
    tray.setContextMenu(menu)

    # Initialize main window and UI components
    w = MainWindow(bot=bot, sender=sender)
    w.show()

    # Timer for shortcut check
    shortcut_monitor = ShortcutMonitor(interval=INTERVAL, trigger_callback=handle_shortcut, sender=sender)

    tray.activated.connect(w.activate)
    app.aboutToQuit.connect(w.save)

    sys.exit(app.exec())

