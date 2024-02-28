import re
from typing import Optional

from PyQt6 import QtWidgets
from PyQt6.Qsci import QsciScintilla
from PyQt6.QtCore import Qt, pyqtSlot, QThread
from PyQt6.QtGui import QFont, QColor, QPainter, QPixmap, QBitmap
from PyQt6.QtWidgets import QVBoxLayout, QHBoxLayout, QFrame, QLabel
from LLM.PythonExecuter import  PythonExecutor
from ui.Messanger.Message import Message, Role
from ui.Messanger.Syntax.CodeSyntax import PyCustomLexer
from ui.Voice.VoiceOutput import Voiceoutput
from ui.base_elements.CustomButton import CustomButton
from ui.base_elements.CustomQEditor import BaseEditor
from worker.worker import Worker
from Config import _configInstance


class MessageEditor(BaseEditor):
    OBJECT_NAME: str = "MessageEditor"

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_GUI()


    def init_GUI(self) -> None:
        BaseEditor().init_GUI()
        self.setObjectName(self.OBJECT_NAME)
        self.setReadOnly(True)
        self.setFixedWidth(int(_configInstance.Width * 0.83))
        self_font = QFont(_configInstance.Font, _configInstance.Flash_Card_Font_Size)
        self_font.setLetterSpacing(QFont.SpacingType.AbsoluteSpacing, 0.4)
        self_font.setWeight(700)
        self.setFont(self_font)
        self.document().documentLayout().documentSizeChanged.connect(self.resizeToFitContent)
        self.setFixedHeight(int(self.document().size().height()) + 10)
        self.setCursor(Qt.CursorShape.IBeamCursor)
        self.setTextInteractionFlags(
        self.textInteractionFlags().NoTextInteraction)
        """self.setTextInteractionFlags(
            self.textInteractionFlags().TextSelectableByMouse |
            self.textInteractionFlags().TextBrowserInteraction |
            self.textInteractionFlags().TextSelectableByKeyboard)"""
        self.font().setWeight(400)

    def resizeToFitContent(self) -> None:
        height = int(self.document().size().height()) + 10
        self.setFixedHeight(height)

    def insertPlainText(self, text):
        super().insertPlainText(text)
        print('text is reaching:', text)

    def setMd(self) -> None:
        self.setTextInteractionFlags(
            self.textInteractionFlags().TextSelectableByMouse |
            self.textInteractionFlags().TextBrowserInteraction |
            self.textInteractionFlags().TextSelectableByKeyboard)
        self.setMarkdown(self.toPlainText())


class CodeEditor(QsciScintilla):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.cords = [0, 0]
        self.init_GUI()

    def init_GUI(self) -> None:
        lexer = PyCustomLexer(self)
        self.setCaretForegroundColor(QColor('white'))
        self.setCaretWidth(3)
        self.setLexer(lexer)
        self.setMarginWidth(1, 0)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.setReadOnly(True)
        self.linesChanged.connect(self.resizeToFitContent)

    def resizeToFitContent(self) -> None:
        self.cords = [self.lines(), 0]
        height = int(self.lines() * 20)
        self.setFixedHeight(height)

    def insertPlainText(self, text: str) -> None:
        self.cords[1] += len(text)
        self.setCursorPosition(self.cords[0], self.cords[1])
        self.insert(text)


class CodeWrapper(QFrame):
    BUTTON_SIZE: int = 32
    BUTTON_OBJECT_NAME: str = 'MessageButton'
    OBJECT_NAME: str = 'CodeWrapper'

    def __init__(self, parent=None):
        super().__init__(parent, )
        self.Editor: CodeEditor = CodeEditor(parent=self)
        self.CodeResult: CodeEditor = CodeEditor(parent=self)
        self.Voice: CustomButton = CustomButton(self.BUTTON_OBJECT_NAME, self.BUTTON_SIZE,
                                                buttons={
                                                    "default": {"icon": "static_files/icons/voice.png",
                                                                "function": self.start_process},
                                                    "stop": {"icon": "static_files/icons/stop.png",
                                                                "function": self.stop_process}
                                                },
                                                )

        self.worker_thread = PythonExecutor()
        self.Edit: CustomButton = CustomButton(self.BUTTON_OBJECT_NAME, self.BUTTON_SIZE,
                                                buttons={
                                                    "default": {"icon": "static_files/icons/edit.png",
                                                                "function": self.setisRead},
                                                    "stop": {"icon": "static_files/icons/done.png",
                                                                "function": self.setisNotRead}
                                                },
                                                )

        self.init_GUI()

    def insertPlainText(self, text: str) -> None:
        self.Editor.insertPlainText(text)

    def setMd(self) -> None:
        pass

    def stop_process(self) -> None:

        self.worker_thread.Stop()
        self.Voice.setup_button('default')

    def setisRead(self) -> None:
        self.Editor.setReadOnly(False)
        self.Edit.setup_button('stop')

    def setisNotRead(self) -> None:
        self.Edit.setup_button('default')
        self.Editor.setReadOnly(True)

    def start_process(self):
        _code_block: str = self.Editor.text()
        self.CodeResult.clear()
        _code = ''
        if _code_block.startswith("python"):
            _code = _code_block.replace("python", "", 1)  # Replace only the first occurrence
        cmd = ["python", "-c", _code]
        self.Voice.setup_button('stop')
        self.worker_thread.setCommand(cmd)
        self.worker_thread.output_received.connect(self.display_output)
        self.worker_thread.error_received.connect(self.display_error)
        self.worker_thread.finished.connect(self.process_finished)
        self.worker_thread.start()

    @pyqtSlot(str)
    def display_output(self, output: str):
        self.CodeResult.insertPlainText(output)

    @pyqtSlot(str)
    def display_error(self, output: str):
        self.CodeResult.insertPlainText(output)

    @pyqtSlot()
    def process_finished(self):
        self.Voice.setup_button('default')

    def init_GUI(self):
        self.setObjectName(self.OBJECT_NAME)
        buttons_layout = QHBoxLayout()
        buttons_layout.addWidget(self.Voice)
        buttons_layout.addWidget(self.Edit)
        buttons_layout.addStretch()
        wrapper_layout = QVBoxLayout()
        wrapper_layout.addWidget(self.Editor)
        wrapper_layout.addWidget(self.CodeResult)
        wrapper_layout.addLayout(buttons_layout)
        self.setLayout(wrapper_layout)
        self.setSizePolicy(
            QtWidgets.QSizePolicy.Policy.MinimumExpanding,
            QtWidgets.QSizePolicy.Policy.MinimumExpanding
        )



class RoundedImage(QLabel):
    def __init__(self):
        super().__init__()
        self.__initVal()
        self.__initUi()

    def __initVal(self):
        self.__pixmap = ''
        self.__mask = ''

    def __initUi(self):
        pass

    def setImage(self, filename: str):
        # Load the image and set it as the pixmap for the label
        self.__pixmap = QPixmap(filename)
        self.__pixmap = self.__pixmap.scaled(self.__pixmap.width(), self.__pixmap.height(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        # Create a mask the same shape as the image
        self.__mask = QBitmap(self.__pixmap.size())

        # Create a QPainter to draw the mask
        self.__painter = QPainter(self.__mask)
        self.__painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.__painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        self.__painter.fillRect(self.__mask.rect(), Qt.GlobalColor.white)

        # Draw a black, rounded rectangle on the mask
        self.__painter.setPen(Qt.GlobalColor.black)
        self.__painter.setBrush(Qt.GlobalColor.black)
        self.__painter.drawRoundedRect(self.__pixmap.rect(), self.__pixmap.size().width(),
                                       self.__pixmap.size().height())
        self.__painter.end()

        # Apply the mask to the image
        self.__pixmap.setMask(self.__mask)
        self.setPixmap(self.__pixmap)
        self.setScaledContents(True)


class MessageWrapper(QFrame, Message):
    BUTTON_SIZE: int = 32
    BUTTON_OBJECT_NAME: str = 'MessageButton'
    OBJECT_NAME: str = 'MessageWrapper'

    def __init__(self, parent=None, message=None, worker=None):
        super().__init__(parent, )
        self.text_editors: [Optional[MessageEditor, CodeWrapper]] = []

        self.fences: list = []

        self.in_code_block = False

        if worker:
            self.worker: Worker = worker
            self.worker.signals.progress.connect(self.append_text)
            self.worker.signals.result.connect(self.save_message)
        self.Editor: MessageEditor = MessageEditor(parent=self)
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
        if message and message.get('content') == '':
            self.init_GUI()
        if message and message.get('content') != '':
            self.setmessage(message)
            self.init_GUI()
            self.add_text_editor()
            self.appendUserText(message.get('content'))
            self.save_message(message.get('content'))


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

    def appendUserText(self, text: str):
        editor_ = self.text_editors[len(self.text_editors) - 1]
        editor_.insertPlainText(text)

    def is_sequential(self, list_of_maps):
        """Checks if the 'index' values in a list of maps are sequential.

        Args:
          list_of_maps: A list of dictionaries, where each dictionary has an 'index' key.

        Returns:
          True if the 'index' values are sequential, False otherwise.
        """

        # Extract the 'index' values and sort them
        indices = [item['index'] for item in list_of_maps]
        # Check if the sorted indices are equal to a range starting from the first index
        return indices == list(range(indices[0], indices[-1] + 1))


    @pyqtSlot(tuple)
    def append_text(self, bot_token: tuple) -> None:
        _bot_text, _index, *_ = bot_token or ("", 0)  # Provide defaults
        print("bot_ token:", bot_token)
        pattern = r"`{1,3}"
        editor_ = self.text_editors[len(self.text_editors) - 1]
        pattern_found = True
        match = re.search(pattern, _bot_text)

        if match:
            _fences = match.group()
            if _fences == '```':
                self.fences.clear()
            self.fences.append({"match": _bot_text, "index": _index})

            _fences_List = self.fences
            if not self.is_sequential(_fences_List):
                self.fences.clear()
                pattern_found = False
            matches = [item["match"] for item in _fences_List]
            fences = ''.join(matches)
            parts = re.split('```', fences)
            if len(parts) != 2:
                pattern_found = False
            bot_text_right = parts[1] if len(parts) > 1 else ""
            bot_text_left = parts[0] if len(parts) > 1 else ""
            if pattern_found:
                if self.in_code_block:
                    editor_.insertPlainText(bot_text_left)
                    self.add_text_editor()
                    editor_ = self.text_editors[len(self.text_editors) - 1]
                    editor_.insertPlainText(bot_text_right + ' ')
                    self.in_code_block = False
                else:
                    editor_.insertPlainText(bot_text_left)
                    self.add_text_editor(True)
                    editor_ = self.text_editors[len(self.text_editors) - 1]
                    editor_.insertPlainText(bot_text_right)
                    self.in_code_block = True
                self.fences.clear()
            return
        editor_.insertPlainText(_bot_text)

    def add_text_editor(self, Code=False) -> None:
        if Code:
            code_editor = CodeWrapper(self)
            self.text_editors.append(code_editor)
            self.wrapper_layout.addWidget(code_editor)
            return
        text_editor = MessageEditor()
        self.text_editors.append(text_editor)
        self.wrapper_layout.addWidget(text_editor)

    @pyqtSlot(object)
    def save_message(self, content: str) -> None:
        for ele in self.text_editors:
            ele.setMd()

        self.setContent(content)

    def changetoStop(self):
        self.Voice.setup_button('default')
    
    def stopStream(self):
        self.speech_worker.stop()
        self.changetoStop()

    def init_GUI(self):
        self.setObjectName(self.OBJECT_NAME)

        __label = RoundedImage()
        __label.setMaximumSize(32, 32)
        if self.role == Role.User:

            path = _configInstance.get_path('static_files/icons/user.png')
        else:
            path = _configInstance.get_path('static_files/icons/bot.png')
        __label.setImage(path)

        info_layout = QHBoxLayout()
        info_layout.addWidget(__label, alignment=Qt.AlignmentFlag.AlignLeft)

        buttons_layout = QHBoxLayout()
        buttons_layout.addWidget(self.Voice)
        buttons_layout.addStretch()
        self.wrapper_layout = QVBoxLayout()
        self.wrapper_layout.addLayout(info_layout)
        self.add_text_editor()
        self.setLayout(self.wrapper_layout)
        self.setSizePolicy(
            QtWidgets.QSizePolicy.Policy.Minimum,
            QtWidgets.QSizePolicy.Policy.Minimum
        )
        self.wrapper_layout.setSpacing(0)
