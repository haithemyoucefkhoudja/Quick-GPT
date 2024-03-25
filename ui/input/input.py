from PyQt6.QtCore import Qt, pyqtSlot
from PyQt6.QtGui import QFont, QTextCursor
from PyQt6.QtWidgets import (
    QLabel,
    QWidget, QHBoxLayout, QProgressBar,
    QTextEdit, QCompleter
)
from queue import Queue
from Config import _configInstance
from ui.base_elements.CustomButton import CustomButton
from Settings_.settingsObject import settings
from ui.Transporter.Transporter import Sender
from LLM.bot import Bot
import re
from typing import Dict


def parse_config(config_text: str) -> Queue:
    """Parses the configuration text and extracts relevant information.

    Args:
        config_text: The configuration script text.

    Returns:
        A dictionary containing the extracted information.
    """

    result = Queue()

    for line in config_text.splitlines():
        line = line.strip()

        # Check for section headers
        current_section = line[1:-1]

        # Skip if no current section
        if not current_section:
            continue
        _SPECIAL_INDICATOR = current_section.split(' ', 1)[0]
        section = current_section[len(_SPECIAL_INDICATOR) + 1:]
        line_kv = {}
        line_kv[_SPECIAL_INDICATOR] = {}

        Pairs = re.findall(r"(.+?)='(.+?)'", section)
        if Pairs:
            for pair in Pairs:
                key, value = pair
                line_kv[_SPECIAL_INDICATOR][key.lstrip()] = value.lstrip()
        result.put(line_kv)

    return result


class TextEdit(QTextEdit):
    COMPLETER_OBJECT_NAME = 'CompleterPopUp'

    def __init__(self, parent=None, bot=None, sender=None, Font=None):
        super().__init__(parent)
        self.c: QCompleter | None = None
        self.sender: Sender = sender
        if self.sender:
            self.sender.connect_signal('command_signal', self.add_newWord)
            self.sender.connect_signal('shortcut_signal', self.append_text)
        self.bot: Bot = bot
        words = []
        self.init_GUI(Font)
        self.setCompleter(QCompleter(words, self), Font)

    def init_GUI(self, Font):
        self.document().documentLayout().documentSizeChanged.connect(self.resizeToFitContent)
        self.setAcceptRichText(False)  # don't Allow rich text formatting
        self.setFont(Font)
        self.setObjectName('TextEditor')
        self.setStyleSheet("""

                            QScrollBar {
                            background-color: transparent;
                            width: 10px;
                            }

                            QScrollBar::handle {
                                background-color: rgb(200, 200, 200);
                                border-radius: 4px;
                                min-height: 15px;
                            }

                            QScrollBar::handle:hover {
                                background-color: rgb(120, 120, 120);
                            }

                            QScrollBar::sub-page, QScrollBar::add-page {
                                background-color: rgb(80, 80, 80);
                            }

                            QScrollBar::sub-line, QScrollBar::add-line {
                                background-color: rgb(80, 80, 80);
                            }
                            """)
        self.setPlaceholderText("choose Agent...")

        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setWordWrapMode(self.wordWrapMode().WordWrap)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

    @pyqtSlot(str)
    def add_newWord(self, word):
        model = self.c.model()
        if self.bot.commands.get(word):
            self.bot.commands.pop(word)
            rows_to_remove = []
            for row in range(model.rowCount()):
                cell_text = model.index(row, 0).data()  # Check the appropriate column
                if cell_text == word:  # Modify the condition as needed
                    rows_to_remove.append(row)
            for row in reversed(sorted(rows_to_remove)):
                model.removeRow(row)

            return

        self.bot.commands[word] = ' '
        row = model.rowCount()
        model.insertRow(row)
        model.setData(model.index(row, 0), word)

    def setCompleter(self, completer, font):

        if self.c:
            self.c.disconnect(self)
        self.c = completer
        self.c.popup().setFont(font)
        if not self.c:
            return

        self.c.setWidget(self)
        self.c.setCompletionMode(QCompleter.CompletionMode.PopupCompletion)
        self.c.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.c.activated.connect(self.insertCompletion)

        self.c.popup().setStyleSheet("""
         background-color: rgb(26, 28, 31); 
    color: #fff; 
    border: none; 
    padding: 4px; 
}
QScrollBar {
    background-color: transparent;
    width: 5px;
}
QScrollBar::handle {
    background-color: rgb(238, 238, 238);
    border-radius: 4px;
    min-height: 20px;
}
  QScrollBar::sub-page,  QScrollBar::add-page {
    background-color: rgb(26, 28, 31);
}
QScrollBar::sub-line,  QScrollBar::add-line {
    background-color: rgb(26, 28, 31);
}
        """)
        self.c.popup().show()
        model = self.c.model()
        for item in self.bot.commands.keys():
            row = model.rowCount()
            model.insertRow(row)
            model.setData(model.index(row, 0), item)

    def textUnderCursor(self):
        tc = self.textCursor()
        tc.select(QTextCursor.SelectionType.WordUnderCursor)
        return tc.selectedText()

    def keyPressEvent(self, e):
        """"
        don't you ever try to understand this code because it's just C++ Code In python
        """
        if self.c and self.c.popup().isVisible():
            if e.key() in [Qt.Key.Key_Enter, Qt.Key.Key_Return, Qt.Key.Key_Escape,
                           Qt.Key.Key_Tab, Qt.Key.Key_Backtab]:
                e.ignore()
                return
        isShortcut = (e.modifiers() & Qt.KeyboardModifier.ControlModifier) and e.key() == Qt.Key.Key_E

        if not self.c or not isShortcut:
            super().keyPressEvent(e)

        ctrlOrShift = e.modifiers() & (Qt.KeyboardModifier.ControlModifier | Qt.KeyboardModifier.ShiftModifier)

        if (not self.c or (ctrlOrShift and len(e.text()) == 0) or e.key() == Qt.Key.Key_Backspace):
            return
        self.c.popup().hide()
        completionPrefix = self.textUnderCursor()
        if len(completionPrefix) < 1:
            return
        if completionPrefix != self.c.completionPrefix():
            self.c.setCompletionPrefix(completionPrefix)
            self.c.popup().setCurrentIndex(self.c.completionModel().index(0, 0))

        cr = self.cursorRect()
        cr.setWidth(self.c.popup().sizeHintForColumn(0) + self.c.popup().verticalScrollBar().sizeHint().width() + 20)

        self.c.complete(cr)

    def calculateFixedHeight(self, count):
        line_height = self.fontMetrics().lineSpacing()
        if count == 1:
            line_height += 10
        content_height = line_height * count
        return content_height + (2 * self.frameWidth())

    def resizeToFitContent(self):
        MaximumLines = 5
        MinimumLines = 1

        line_height = self.fontMetrics().lineSpacing()
        count = int((self.document().size().height()) / line_height)
        if count <= MaximumLines:
            self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
            self.setFixedHeight(self.calculateFixedHeight(MinimumLines))
        if MinimumLines < count <= MaximumLines:
            self.setFixedHeight(self.calculateFixedHeight(count))
        elif count > MaximumLines:
            self.setFixedHeight(self.calculateFixedHeight(MaximumLines))
            self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)

    @pyqtSlot(str)
    def append_text(self, text: str) -> None:
        """
        insert new text slot
        :param text:
        :return:
        """
        self.insertPlainText(text)
        self.scrollToBottom()

    def scrollToBottom(self) -> None:
        """ It's Just Scroll Down
        """
        Max: int = self.verticalScrollBar().maximum()

        self.verticalScrollBar().setValue(
            Max
        )

    def insertCompletion(self, completion) -> None:

        if self.c.widget() != self:
            return
        tc = self.textCursor()
        tc.movePosition(QTextCursor.MoveOperation.Left, QTextCursor.MoveMode.MoveAnchor, len(self.c.completionPrefix()))
        tc.movePosition(QTextCursor.MoveOperation.EndOfWord, QTextCursor.MoveMode.KeepAnchor)
        tc.insertText(completion)
        self.setTextCursor(tc)


class ExtendableInput:
    Inputs: Queue = Queue()
    def emptyQueue(self):
        while not self.Inputs.empty():
            self.Ex_Input.Inputs.get()


class AutoResizableTextEdit(QWidget):
    Ex_Input = ExtendableInput()
    KEY_V = "V"  # To start new Voice Record
    sendMessage = settings.value("send_message", "Ctrl+Return")  # to send the Message
    PromptButton = 'PromptButton'

    def __init__(self, parent=None, sender=None, bot=None):
        super().__init__(parent)
        # Set the font size and color of the editor text
        editor_font = QFont(_configInstance.Font, 12)
        editor_font.setLetterSpacing(QFont.SpacingType.AbsoluteSpacing, 0.4)
        editor_font.setWeight(700)
        self.sender: Sender = sender
        self.bot: Bot = bot
        if self.sendMessage == '':
            self.sendMessage = "Ctrl+Return"
        self.sender.connect_signal('isLoading_signal', self.LoadingState)
        self.sender.connect_signal('set_shortcut_signal', self.setShortcut)
        self.text_Editor = TextEdit(self, bot=bot, sender=sender, Font=editor_font)
        self.animation_label = QLabel()
        self.animation_label.setStyleSheet("color: white;")
        self.animation_label.setFixedWidth(42)
        self.animation_label.setFont(QFont(_configInstance.Font, 18))
        self.animation_label.setText("")

        self.progress_bar = QProgressBar()
        self.progress_bar.setOrientation(Qt.Orientation.Vertical)
        self.progress_bar.setFixedSize(10, 40)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setStyleSheet("""
                            QProgressBar {
                                background-color: rgb(80, 80, 80);
                                border-radius: 4px;
                            }
                            QProgressBar::chunk {
                                background-color: white;
                                border-radius: 4px;
                            }
                        """)
        self.send_button = CustomButton(self.PromptButton,
                                        buttons={
                                            "default": {"icon": "static_files/icons/paper-plane-white.png",
                                                        "function": self.sendData},
                                            "stop": {"icon": "static_files/icons/stop.png",
                                                     "function": self.stopStream}
                                        },
                                        button_height=40
                                        )
        self.send_button.setShortcut(self.sendMessage)
        self.send_button.setObjectName('PromptButton')
        self.voice_record_button = CustomButton(self.PromptButton,
                                                buttons={
                                                    "default": {"icon": "static_files/icons/microphone-white.png",
                                                                "function": self.recording_started},
                                                    "stop": {"icon": "static_files/icons/stop.png",
                                                             "function": self.recording_stopped}
                                                },
                                                button_height=40
                                                )

        self.voice_record_button.setShortcut(self.KEY_V)

        # Create recording thread and attach slots to its signals
        # TODO: Maybe i'll add voice messaging later it's just akward
        """

        self.recording_thread = RecordingThread()
        self.recording_thread.sig_started.connect(self.recording_started)
        self.recording_thread.sig_stopped.connect(self.recording_stopped)
        self.recording_thread.sig_intensity.connect(self.set_intensity)
        self.recording_thread.sig_error.connect(self.recording_error)
        self.recording_thread.sig_result.connect(self.append_text)
        self.voice_record_button.clicked.connect(self.recording_thread.start)
        """
        layout = QHBoxLayout()
        layout.addWidget(self.text_Editor)
        layout.addWidget(self.send_button)
        # layout.addWidget(self.voice_record_button)
        # layout.addWidget(self.progress_bar)
        layout.addWidget(self.animation_label)
        # Set the alignment of the QPushButton within its parent layout
        layout.setAlignment(self.send_button, Qt.AlignmentFlag.AlignBottom)
        layout.setAlignment(self.voice_record_button, Qt.AlignmentFlag.AlignBottom)
        layout.setAlignment(self.progress_bar, Qt.AlignmentFlag.AlignBottom)
        layout.setAlignment(self.animation_label, Qt.AlignmentFlag.AlignBottom)
        layout.setAlignment(self.text_Editor, Qt.AlignmentFlag.AlignBottom)

        self.setLayout(layout)

    def startSession(self, _scriptconfig: Dict) -> None:
        self.bot.session.terminate_Process()
        CMD: str = _scriptconfig.get('CMD')

        if not CMD:
            raise ValueError('No executable path is found')
        self.bot.session.startNewProcess(CMD.split(' '))

    def sendData(self):
        text = self.text_Editor.toPlainText()
        if text:

            agent = self.bot.commands.get(text)

            if agent:
                self.Ex_Input.emptyQueue()
                config = parse_config(agent)

                while not config.empty():
                    item: Dict = config.get()

                    if item.get('SCRIPT'):
                        _script_config: Dict = item['SCRIPT']
                        self.startSession(_script_config)
                    if item.get('AGENT'):
                        _profile_config: Dict = item['AGENT']
                        self.sender.send_signal('input_signal',
                                                _profile_config
                                                )
                    if item.get('INPUT'):
                        _Input_config: Dict = item['INPUT']
                        self.Ex_Input.Inputs.put(('INPUT', _Input_config))
                    if item.get('CYCLE'):
                        _Cycle_config: Dict = item['CYCLE']
                        self.Ex_Input.Inputs.put(('CYCLE', _Cycle_config))






                """"
                [START]
[SCRIPT PATH='C:\\Users\\haithem-yk\\Desktop\\Projects\\QuickGpt\\_scripts\\csv_script.py' INTERRUPTER_PATH='python' ]
[AGENT NAME='BOB Accountant' PROFILE='C:\\Users\\haithem-yk\\Desktop\\csv\\Accountant.png']
[INPUT TYPE='CSV FILE' SEPERATOR='\n']
[CYCLE ENDSEQ='<END-SIGNAL>']
[END]
                """

            if not self.Ex_Input.Inputs.empty():
                _type, seq = self.Ex_Input.Inputs.get()
                if _type == 'CYCLE':
                    if text == seq.get('ENDSEQ'):
                        self.sender.send_signal('input_signal',
                                                {"type": "text",
                                                 "content": text
                                                 }
                                                )
                        if self.Ex_Input.Inputs.empty():
                            self.text_Editor.setPlaceholderText('choose Agent...')
                            self.text_Editor.clear()
                            return
                        else:
                            self.sendData()
                            return

                    self.Ex_Input.Inputs.put((_type, seq))
                    self.text_Editor.setPlaceholderText('send Message...')
                    self.text_Editor.clear()

                if _type == 'INPUT':
                    Input = f'| {_type} |'
                    for key in seq:
                        Input += f' {key}:{seq[key]} |'
                    self.text_Editor.setPlaceholderText(Input)
                    self.text_Editor.clear()
                    return

            self.sender.send_signal('input_signal',
                                    {"type": "text",
                                     "content": text
                                     }
                                    )
            # self.Ex_Input._Args.clear()

            self.text_Editor.clear()
    def stopStream(self):
        pass
    @pyqtSlot(tuple)
    def setShortcut(self, shortcut: tuple) -> None:
        seq, _type = shortcut

        if _type == 'send_message':
            settings.setValue(_type, seq)
            self.sendMessage = seq
            self.send_button.setShortcut(self.sendMessage)

    @pyqtSlot(bool)
    def LoadingState(self, is_loading: bool) -> None:
        self.send_button.setup_button('')

    @pyqtSlot()
    def recording_started(self):
        """This slot is called when recording starts"""
        # TODO : Get rid of this clicked.... !
        self.voice_record_button.clicked.disconnect(self.recording_thread.start)
        self.voice_record_button.clicked.connect(self.recording_thread.stop)
        self.send_button.setDisabled(True)
        pass

    @pyqtSlot()
    def recording_stopped(self):
        """This slot is called when recording stops"""
        self.voice_record_button.clicked.disconnect(self.recording_thread.stop)
        self.voice_record_button.clicked.connect(self.recording_thread.start)
        self.send_button.setDisabled(False)
        pass

    @pyqtSlot(str)
    def recording_error(self, error):
        raise_error_message(error)

    @pyqtSlot(int)
    def set_intensity(self, intensity):
        self.progress_bar.setValue(intensity)
