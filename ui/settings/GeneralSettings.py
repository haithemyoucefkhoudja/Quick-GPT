from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QVBoxLayout, QWidget
from ui.settings.shortcutSettings import ShortcutCaptureWidget


class GeneralSettings(QWidget):
    def __init__(self, parent=None, Font: QFont = None, sender=None):
        super().__init__(parent)
        self.setFont(Font)
        layout = QVBoxLayout()
        self.shortcut_widget = ShortcutCaptureWidget(self, sender)
        layout.addWidget(self.shortcut_widget)
        layout.addStretch(1)
        self.setLayout(layout)

