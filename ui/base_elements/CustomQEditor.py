from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QTextEdit
from Config import Config

Config = Config()





class BaseEditor(QTextEdit):

    """
       Abstract base class for different editor types.
       """

    """
        Maximum Characters allowed per line
    """
    Max_Characters_Line: int = 55

    """
        Unique identifier for the editor type
    """
    OBJECT_NAME: str = "Editor"
    """
    Message I don't know why I named it Like this
    """


    def __init__(self, parent=None):
        super().__init__(parent)




    def init_GUI(self) -> None:
        """
            method to init The Editor.
        """
        self.setTextInteractionFlags(
            self.textInteractionFlags().TextSelectableByMouse |
            self.textInteractionFlags().TextBrowserInteraction |
            self.textInteractionFlags().TextSelectableByKeyboard)

        self.setLineWrapColumnOrWidth(self.Max_Characters_Line)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setLineWrapMode(self.LineWrapMode.FixedColumnWidth)
        self.setWordWrapMode(self.wordWrapMode().WordWrap)
        pass

    def Allow_horizontalScroll(self, allowed):
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
