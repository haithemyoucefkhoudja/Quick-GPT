import os.path
from typing import Dict

from PyQt6.QtCore import QSize
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QPushButton
from Config import Config

Config = Config()


class CustomButton(QPushButton):

    def __init__(self, object_name: str,
                 button_height: int = 40,
                 button_width: int = 35,
                 **kwargs):
        super().__init__()
        self.setObjectName(object_name)
        self.button_states: Dict[str, Dict] = kwargs.get('buttons')
        self.setFixedSize(button_width, button_height)
        self.setIconSize(QSize(int(button_width * 0.8), int(button_height * 0.8)))
        self.state = None
        self.setup_button('default')

    def switchFunction(self, function_name):
        pass

    def setup_button(self, state_name: str):
        if self.state:
            self.clicked.disconnect(self.state['function'])
        if state_name in self.button_states:
            self.state = self.button_states[state_name]

            if 'icon' in self.state:
                self.setIcon(QIcon(Config.get_path(self.state['icon'])))


            # Connect the button's clicked signal to the specified function


            self.clicked.connect(self.state['function'])

        else:
            raise ValueError

    """def on_button_click(self):
        if self.behavior_fn:
            if self.Switch_Icon:
                temp = self.Icon
                self.Icon = self.Switch_Icon
                self.Switch_Icon = temp
                self.setIcon(QIcon(self.Icon))
            self.behavior_fn()"""

    def setButtonColor(self, color):
        self.setStyleSheet('')
        pass
