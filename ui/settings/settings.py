from PyQt6.QtCore import  pyqtSignal, pyqtSlot
from PyQt6.QtWidgets import QVBoxLayout, QStackedWidget, QHBoxLayout, QFrame
from LLM.bot import Bot
from ui.settings.GeneralSettings import GeneralSettings
from ui.settings.IconMenu import SettingsIconsMenu
from ui.settings.commandList import  CommandWidget
from ui.settings.llm import LLMSettings
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QDialog
from Config import _configInstance


class SettingDialog(QDialog):

    Widget_signal = pyqtSignal(int)

    def __init__(self, parent=None, bot=None, sender=None):
        super().__init__(parent)
        if bot:
            self.bot: Bot = bot
        if sender:
            self.sender = sender
        self.setStyleSheet(_configInstance.load_stylesheet(_configInstance.get_path('static_files/setting_style.css')))
        editor_font = QFont(_configInstance.Font, 12)
        editor_font.setLetterSpacing(QFont.SpacingType.AbsoluteSpacing, 1)
        self.setWindowTitle("Settings")
        self.setFont(editor_font)
        CommandSetting = CommandWidget(bot=bot, sender=sender,)

        self.Widget_signal.connect(self.swtichWidget)
        iconsMenu = SettingsIconsMenu(signal=self.Widget_signal)
        self.stacked_widget = QStackedWidget()
        generalSettings = GeneralSettings(self, Font=editor_font, sender=sender)
        layout = QVBoxLayout()
        layout.addWidget(iconsMenu)
        H_layout = QHBoxLayout()
        llmSettings = LLMSettings(bot=bot, Font=editor_font, parent=self)
        H_layout.addWidget(llmSettings)
        H_layout.addWidget(generalSettings)
        h_widget = QFrame()
        h_widget.setLayout(H_layout)
        self.stacked_widget.addWidget(CommandSetting)
        self.stacked_widget.addWidget(h_widget)
        self.stacked_widget.setCurrentIndex(1)
        layout.addWidget(self.stacked_widget)
        self.setLayout(layout)

    @pyqtSlot(int)
    def swtichWidget(self, index):
        self.stacked_widget.setCurrentIndex(index)
