from typing import Callable

from PyQt6 import QtWidgets
from PyQt6.QtCore import Qt, pyqtSlot, QThreadPool
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QVBoxLayout, QHBoxLayout, QFrame
from Config import Config
from LLM.bot import Bot
from ui.Messanger.Message import Message
from ui.base_elements.CustomQEditor import BaseEditor
from ui.base_elements.CustomButton import CustomButton
from worker.worker import Worker


class CommandEditor(BaseEditor, Message):
    OBJECT_NAME: str = "CommandEditor"

    def __init__(self, parent=None, worker=None):
        super().__init__(parent)
        self.worker: Worker = worker
        self.threadpool: QThreadPool = QThreadPool()
        self.init_GUI()

    def init_GUI(self) -> None:
        BaseEditor().init_GUI()
        self.setAcceptRichText(False)
        self.setObjectName(self.OBJECT_NAME)
        self.Allow_horizontalScroll(True)
        self.setReadOnly(True)
        """
        if self.worker:
            self.worker.signals.progress.connect(self.append_text)
            self.worker.signals.result.connect(self.setContent)"""
        self.setFixedWidth(int(Config.Width * 0.83))
        self.setStyleSheet("""
color: white;
border: None;
background-color: rgb(26, 28, 31);

        """)
        self_font = QFont(Config.Font, Config.Flash_Card_Font_Size)
        self_font.setLetterSpacing(QFont.SpacingType.AbsoluteSpacing, 1)
        self_font.setWeight(700)
        self.setFont(self_font)
        self.setCursor(Qt.CursorShape.IBeamCursor)
        self.setLineWidth(55)

    @pyqtSlot(str)
    def append_text(self, bot_text) -> None:
        self.insertPlainText(bot_text)

    def toggle_edit(self) -> None:
        self.setReadOnly(not self.isReadOnly())

    def save_message(self, content: str) -> None:
        self.setContent(content)


class CommandWrapper(QFrame):
    BUTTON_SIZE: int = 32
    BUTTON_OBJECT_NAME: str = 'CommandButton'
    OBJECT_NAME: str = 'CommandWrapper'

    def __init__(self, parent=None, worker=None, save_function: Callable = None):
        super().__init__(parent, )
        if save_function:
            self.save_function = save_function

        self.Editor: CommandEditor = CommandEditor(parent=self, worker=worker)
        self.Edit_Button = CustomButton(self.BUTTON_OBJECT_NAME,
                                        self.BUTTON_SIZE, self.BUTTON_SIZE,
                                        buttons={
                                            "default": {"icon": 'static_files/icons/edit.png',
                                                        "function": self.toogle_Editor},
                                            "done": {"icon": 'static_files/icons/done.png',
                                                     "function": self.save_Editor}
                                        }
                                        )

        self.init_GUI()

    def toogle_Editor(self):
        self.Edit_Button.setup_button('done')
        self.Editor.toggle_edit()

    def save_Editor(self):
        self.Edit_Button.setup_button('default')
        self.Editor.toggle_edit()
        self.save_function()

    def init_GUI(self):
        self.setObjectName(self.OBJECT_NAME)
        buttons_layout = QHBoxLayout()
        buttons_layout.addWidget(self.Edit_Button)
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

    def setText(self, text: str) -> None:
        self.Editor.setText(text)
