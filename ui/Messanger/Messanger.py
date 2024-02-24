from PyQt6.QtCore import Qt, pyqtSlot, QThreadPool
from PyQt6.QtWidgets import QScrollArea, QVBoxLayout, QFrame, QSizePolicy
from Config import _configInstance
from LLM.bot import Bot
from ui.Messanger._MessageUI import MessageWrapper, Message
from ui.Messanger.Message import Role
from worker.worker import Worker


class Messanger(QScrollArea):
    Messages_List: [Message] = []

    def __init__(self, parent=None, sender=None, bot=None):
        super().__init__(parent)
        self.layout = QVBoxLayout()
        self.bot: Bot = bot
        self.scrollAreaWidgetContents: QFrame = QFrame()
        self.setup_ui()
        self.sender = sender
        self.threadpool: QThreadPool = QThreadPool()

        if self.sender:
            self.sender.connect_signal('input_signal', self.add_Message)

    def setup_ui(self):
        # Chat. Messanger
        self.setWidgetResizable(True)
        self.setObjectName("scrollArea")
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.verticalScrollBar().rangeChanged.connect(
            self.scrollToBottom
        )

        self.setFixedSize(int(_configInstance.Width * 0.9), int(_configInstance.Height * 0.7))
        # Body that holds the widgets.

        self.scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")

        # Box that holds the widgets.
        self.layout = QVBoxLayout(self.scrollAreaWidgetContents)
        self.layout.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        self.scrollAreaWidgetContents.setLayout(self.layout)
        self.setWidget(self.scrollAreaWidgetContents)
        self.layout.addStretch(1)
        self.layout.setSpacing(5)

    def scrollToBottom(self) -> None:
        """ It's Just Scroll Down
        """
        Max: int = self.verticalScrollBar().maximum()

        self.verticalScrollBar().setValue(
                Max
            )

    """def remove_current_fcs(self):
        # Remove all widgets from the QVBoxLayout
        while self.layout.count() > 0:
            widget = self.layout.takeAt(0).widget()
            if widget is not None:
                widget.deleteLater()"""

    """def chosen_file(self, index):
        self.remove_current_fcs()
        self.Index = index
        for data in self.Flash_Cards_List[self.Index]:
            self.layout.addWidget(MessageWrapper(message={'content':data}))"""

    @pyqtSlot(str)
    def add_Message(self, data: str) -> None:
        self.layout.addWidget(MessageWrapper(message={'content': data, 'Role': Role.User}))
        worker = Worker(fn=self.addBotMessage, **{'template': data})
        botWrapper = MessageWrapper(message={'content': '', 'Role': Role.Bot}, worker=worker)

        self.layout.addWidget(botWrapper)
        self.threadpool.start(worker)

    def addBotMessage(self, *args, **kwargs) -> str:
        result = self.bot.generate_response(**kwargs)
        return result

    def keyPressEvent(self, event) -> None:
        if event.key() == Qt.Key.Key_Down:
            # Scroll down when the down key is pressed
            self.verticalScrollBar().setValue(self.verticalScrollBar().value() + 10)
        elif event.key() == Qt.Key.Key_Up:
            # Scroll up when the up key is pressed
            self.verticalScrollBar().setValue(self.verticalScrollBar().value() - 10)
        else:
            super().keyPressEvent(event)