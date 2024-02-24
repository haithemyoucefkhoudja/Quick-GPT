from PyQt6 import QtWidgets
from PyQt6.QtCore import Qt, pyqtSlot, QThreadPool, QThread
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QVBoxLayout, QHBoxLayout, QFrame

from ui.Messanger.Message import Message
from ui.Voice.VoiceOutput import Voiceoutput
from ui.base_elements.CustomButton import CustomButton
from ui.base_elements.CustomQEditor import BaseEditor
from worker.worker import Worker
from Config import _configInstance


class MessageEditor(BaseEditor, Message):
    OBJECT_NAME: str = "MessageEditor"

    def __init__(self, parent=None, message: dict = None, worker=None):
        super().__init__(parent)
        if message:
            self.setmessage(message)
            self.insertPlainText(message.get('content'))
        self.worker: Worker = worker
        self.threadpool: QThreadPool = QThreadPool()

        self.init_GUI()

    def init_GUI(self) -> None:
        BaseEditor().init_GUI()
        self.setObjectName(self.OBJECT_NAME)
        self.setReadOnly(True)
        if self.worker:
            self.worker.signals.progress.connect(self.append_text)
            self.worker.signals.result.connect(self.setContent)
        self.setFixedWidth(int(_configInstance.Width * 0.83))

        self_font = QFont(_configInstance.Font, _configInstance.Flash_Card_Font_Size)
        self_font.setLetterSpacing(QFont.SpacingType.AbsoluteSpacing, 1)
        self.setFont(self_font)
        self.document().documentLayout().documentSizeChanged.connect(self.resizeToFitContent)
        self.setFixedHeight(int(self.document().size().height()) + 10)
        self.setCursor(Qt.CursorShape.IBeamCursor)

    def resizeToFitContent(self) -> None:
        height = int(self.document().size().height()) + 10
        self.setFixedHeight(height)

    @pyqtSlot(str)
    def append_text(self, bot_text) -> None:
        self.insertPlainText(bot_text)

    def save_message(self, content: str) -> None:
        self.setContent(content)


class MessageWrapper(QFrame):
    BUTTON_SIZE: int = 32
    BUTTON_OBJECT_NAME: str = 'MessageButton'
    OBJECT_NAME: str = 'MessageWrapper'

    def __init__(self, parent=None, message=None, worker=None):
        super().__init__(parent, )
        if message is None:
            message = {'content': ''}
        self.Editor: MessageEditor = MessageEditor(parent=self, message=message, worker=worker)
        self.Voice: CustomButton = CustomButton(self.BUTTON_OBJECT_NAME, self.BUTTON_SIZE,
                                                buttons={
                                                    "default": {"icon": "static_files/icons/voice.png",
                                                                "function": self.streamVoice},
                                                    "stop": {"icon": "static_files/icons/stop.png",
                                                             "function": self.stopStream},
                                                },
                                                )
        self.speech_thread = QThread()
        self.speech_worker = None
        self.init_GUI()

    def streamVoice(self) -> None:
        text_cursor = self.Editor.textCursor()
        selected_Text = text_cursor.selectedText()
        if selected_Text == '':
            return

        self.speech_worker = Voiceoutput(text=selected_Text)
        self.speech_worker.moveToThread(self.speech_thread)
        self.speech_worker.signals.finished.connect(self.speech_thread.quit)
        self.speech_worker.signals.finished.connect(self.speech_worker.deleteLater)
        self.speech_worker.signals.finished.connect(self.changetoStop)
        self.speech_thread.started.connect(self.speech_worker.run)
        self.speech_thread.start()
        self.Voice.setup_button('stop')

    def changetoStop(self):
        self.Voice.setup_button('default')
    
    def stopStream(self):
        self.speech_worker.stop()
        self.changetoStop()

    def init_GUI(self):
        self.setObjectName(self.OBJECT_NAME)
        buttons_layout = QHBoxLayout()

        buttons_layout.addWidget(self.Voice)
        buttons_layout.addStretch()
        wrapper_layout = QVBoxLayout()
        wrapper_layout.addWidget(self.Editor)
        wrapper_layout.addLayout(buttons_layout)
        self.setLayout(wrapper_layout)
        self.setSizePolicy(
            QtWidgets.QSizePolicy.Policy.Minimum,
            QtWidgets.QSizePolicy.Policy.Minimum
        )

        wrapper_layout.setSpacing(0)
