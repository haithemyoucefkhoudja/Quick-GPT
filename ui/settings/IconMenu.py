from PyQt6.QtWidgets import QHBoxLayout, QFrame
from ui.base_elements.CustomButton import CustomButton


class SettingsIconsMenu(QFrame):
    MENU_BUTTON: str = 'MenuButton'
    Height: int = 50
    IconsMenu_Object = 'IconsMenu'

    def __init__(self, parent=None, bot=None, signal=None):
        super().__init__(parent)
        if signal:
            self.signal = signal

        self.setObjectName(self.IconsMenu_Object)

        self.Bot_Button = CustomButton(self.MENU_BUTTON,
                     buttons={
                         "default": {"icon": 'static_files/icons/bot.png', "function": self.openBotSetting},
                     },
                     button_height=40)

        self.new_widget = None
        self.index = 0
        self.layout = QHBoxLayout()

        self.layout.addStretch()
        self.Command_Button = CustomButton(self.MENU_BUTTON,
                                     buttons={
                                         "default": {"icon": "static_files/icons/command-line.png", "function": self.openCommandSetting},
                                     },
                                     button_height=40
                                     )

        self.button_original_style = self.Bot_Button.styleSheet()
        self.Bot_Button.setStyleSheet("background-color:rgb(144, 238, 144)")
        self.layout.addWidget(self.Command_Button)
        self.layout.addWidget(self.Bot_Button)

        self.layout.addSpacing(20)
        self.setLayout(self.layout)

    def openCommandSetting(self):
        self.signal.emit(0)
        self.Bot_Button.setStyleSheet(self.button_original_style)  # Reset Bot_Button
        self.Command_Button.setStyleSheet("background-color:rgb(144, 238, 144)")

    def openBotSetting(self) -> None:
        self.signal.emit(1)
        self.Command_Button.setStyleSheet(self.button_original_style)  # Reset Command_Button
        self.Bot_Button.setStyleSheet("background-color:rgb(144, 238, 144)")
