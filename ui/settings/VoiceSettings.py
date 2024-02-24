from PyQt6.QtCore import Qt, QRect
from PyQt6.QtGui import QPainter, QColor, QPen, QBrush
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton  # ... or other controls


class MySwitch(QPushButton):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setCheckable(True)
        self.setMinimumWidth(66)
        self.setMinimumHeight(22)

    def paintEvent(self, event):
        label = "ON" if self.isChecked() else "OFF"
        bg_color = Qt.GlobalColor.white if self.isChecked() else Qt.GlobalColor.darkGray

        radius = 10
        width = 32
        center = self.rect().center()

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.translate(center)
        painter.setBrush(QColor(0,0,0))

        pen = QPen(Qt.GlobalColor.black)
        pen.setWidth(2)
        painter.setPen(pen)
        painter.drawRoundedRect(QRect(-width, -radius, 2*width, 2*radius), radius, radius)
        painter.setBrush(QBrush(bg_color))
        sw_rect = QRect(-radius, -radius, width + radius, 2*radius)
        if not self.isChecked():
            sw_rect.moveLeft(-width)
        painter.drawRoundedRect(sw_rect, radius, radius)
        painter.drawText(sw_rect, Qt.AlignmentFlag.AlignCenter, label)


class VoiceSettingsWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout()
        self.voice_label = QLabel("Voice:")
        self.voice_combobox = MySwitch(self)
        layout.addWidget(self.voice_label)
        layout.addWidget(self.voice_combobox)
        self.setLayout(layout)
