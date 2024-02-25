from Settings_.settingsObject import settings
from PyQt6.QtCore import pyqtSlot
from PyQt6.QtGui import QKeySequence
from PyQt6.QtWidgets import QKeySequenceEdit, QLineEdit, QWidget, QHBoxLayout,  QLabel, QVBoxLayout
from ui.Transporter.Transporter import Sender

class KeySequenceEdit(QKeySequenceEdit):
    def keyPressEvent(self, event):
        super(KeySequenceEdit, self).keyPressEvent(event)
        seq_string = self.keySequence().toString()
        if seq_string:
            last_seq = seq_string.split(",")[-1].strip()
            le = self.findChild(QLineEdit, "qt_keysequenceedit_lineedit")
            self.setKeySequence(QKeySequence(last_seq))
            le.setText(last_seq)
            self.editingFinished.emit()


class ShortcutCaptureWidget(QWidget):
    def __init__(self, parent=None,sender=None):
        super().__init__(parent)
        if sender:
            self.sender: Sender = sender

        self._keysequenceedit = KeySequenceEdit(editingFinished=self.on_editingFinished,)
        self._keysequenceedit.setKeySequence(QKeySequence(settings.value("show_hide", 'Ctrl+shift+v')))
        self._keysequenceedit.setStyleSheet(self.styleSheet() +
                                            """
                                            QLineEdit:focus { 
                                              border: 2px solid blue; 
                                            } 
                                            """
                                            )
        self._message_keysequenceedit = KeySequenceEdit(editingFinished=self.on_send_editingFinished)
        self._message_keysequenceedit.setKeySequence(
            QKeySequence(settings.value("send_message", 'Ctrl+Return')))
        self._message_keysequenceedit.setStyleSheet(self._keysequenceedit.styleSheet())  # Same styling
        layout = QVBoxLayout()
        hlay = QHBoxLayout()
        hlay.addWidget(self._keysequenceedit)
        hlay.addStretch(0)
        sendMessage_hlay = QHBoxLayout()
        sendMessage_hlay.addWidget(self._message_keysequenceedit)
        sendMessage_hlay.addStretch(0)
        shortcut_label = QLabel("Show/Hide the UI:")
        send_shortcut_label = QLabel("SendMessage:")
        layout.addWidget(shortcut_label)
        layout.addLayout(hlay)
        layout.addWidget(send_shortcut_label)
        layout.addLayout(sendMessage_hlay)
        self.setLayout(layout)

    @pyqtSlot()
    def on_editingFinished(self):
        sequence = self._keysequenceedit.keySequence()
        seq_string = sequence.toString()
        if seq_string == '':
            return
        self.sender.send_signal('set_shortcut_signal', (seq_string, 'show_hide'))

    @pyqtSlot()
    def on_send_editingFinished(self):
        sequence = self._message_keysequenceedit.keySequence()
        seq_string = sequence.toString()
        if seq_string == '':
            return
        self.sender.send_signal('set_shortcut_signal', (seq_string, 'send_message'))
