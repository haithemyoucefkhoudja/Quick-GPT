from typing import Callable
import keyboard
from PyQt6.QtCore import QTimer, QObject, pyqtSlot
from ui.Transporter.Transporter import Sender
from Settings_.settingsObject import settings


class ShortcutMonitor(QObject):
    Shortcut = settings.value("show_hide", "ctrl+shift+v")

    def __init__(self, parent=None, interval=100, trigger_callback: Callable = None, sender=None):
        super().__init__(parent)
        if sender:
            self.sender: Sender = sender
            self.sender.connect_signal('set_shortcut_signal', self.set_Shortcut)

        self.interval = interval
        self.trigger_callback = trigger_callback
        self.timer = QTimer()
        self.timer.timeout.connect(self.check_shortcut)
        self.timer.start(self.interval)

    @pyqtSlot(tuple)
    def set_Shortcut(self, shortcut: tuple) -> None:
        seq, _type = shortcut
        if _type == 'show_hide':
            settings.setValue(_type, seq)
            self.Shortcut = seq

    def check_shortcut(self) -> None:
        if keyboard.is_pressed(self.Shortcut):
            if self.trigger_callback:
                self.trigger_callback()
