from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QListWidget,  QScrollArea, QHBoxLayout,  QListWidgetItem, QMenu,  QWidget

from Config import Config
from LLM.bot import Bot
from ui.Transporter.Transporter import Sender
from ui.settings.CommandEditor import CommandWrapper

Config = Config()

from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QLineEdit,  QVBoxLayout

from Config import Config
from ui.base_elements.CustomButton import CustomButton


class CommandList(QListWidget):
    def __init__(self, parent=None, bot=None, sender=None, Font=None):
        super().__init__(parent)
        self.sender: Sender = sender
        self.bot: Bot = bot
        self.setFont(Font)
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.setSelectionMode(QListWidget.SelectionMode.SingleSelection)
        self.setStyleSheet("color: rgb(240, 240, 240)")
        self.init_list()

    def init_list(self):
        for item in self.bot.commands.keys():
            new_item = QListWidgetItem(item)
            self.addItem(new_item)


class CommandWidget(QWidget):
    def __init__(self, parent=None, bot=None, sender=None):
        super().__init__(parent)
        if bot:
            self.bot: Bot = bot
        if sender:
            self.sender = sender
        editor_font = QFont(Config.Font, 11)
        editor_font.setLetterSpacing(QFont.SpacingType.AbsoluteSpacing, 1)
        self.setFont(editor_font)
        # Create our widgets
        self.command_list = CommandList(parent=self, Font=editor_font, bot=bot, sender=sender)
        self.command_list.customContextMenuRequested.connect(self.on_right_click)
        self.command_list.itemClicked.connect(self.edit_item)

        self.text_display = CommandWrapper(self, save_function=self.set_Command)

        # --- Main layout setup ---
        main_layout = QHBoxLayout()

        # --- Left side: Command list ---
        list_scroll = QScrollArea()
        self.command_list.setFixedHeight(list_scroll.height())
        self.command_list.setStyleSheet("border:none;")
        list_scroll.setWidget(self.command_list)
        list_scroll.setStyleSheet("""
                    background-color: rgb(57, 62, 70);
                    }
                    QScrollBar::sub-page,  QScrollBar::add-page {
    background-color: rgb(160, 160, 160);
}

QScrollBar::sub-line,  QScrollBar::add-line {
    background-color: rgb(160, 160, 160);
}
                """)

        main_layout.addWidget(list_scroll)

        # --- Right side: Text display  ---
        right_side_layout = QVBoxLayout()

        # Input and button
        command_input_layout = QHBoxLayout()

        add_button = CustomButton('MenuButton',
                                  button_width=40,
                                  buttons={
                                      "default": {"icon": 'static_files/icons/add.png',
                                                  "function": self.add_empty_item},
                                  },
                                  )

        self.commands_edit = QLineEdit()
        self.commands_edit.setFont(editor_font)
        self.commands_edit.setFixedHeight(42)
        self.commands_edit.setPlaceholderText('add command..')

        command_input_layout.addWidget(add_button)
        command_input_layout.addWidget(self.commands_edit)
        right_side_layout.addLayout(command_input_layout)

        # Text display area
        text_scroll = QScrollArea()
        text_scroll.setWidget(self.text_display)
        text_scroll.setWidgetResizable(True)

        text_scroll.setStyleSheet("""
                    background-color: rgb(57, 62, 70); 
                """)
        self.text_display.setVisible(False)

        right_side_layout.addWidget(text_scroll)
        main_layout.addLayout(right_side_layout)

        self.commands_edit.setStyleSheet("""
                    background-color: rgb(26, 28, 31); 
                    color: white;
                    border: none;
                    border-radius: 8px;
                    padding: 5px;
                """)

        self.setLayout(main_layout)

    def on_right_click(self, position):
        menu = QMenu()
        remove_action = menu.addAction("Remove")
        action = menu.exec(self.command_list.mapToGlobal(position))

        if action == remove_action:
            self.remove_item()

    def edit_item(self):
        current_item = self.command_list.currentItem()
        if current_item:
            self.text_display.setVisible(True)
            self.text_display.setText(self.bot.commands.get(current_item.text()))
        self.bot.save_commands()

    def remove_item(self):
        current_item = self.command_list.currentItem()
        if current_item:
            row = self.command_list.row(current_item)
            self.command_list.takeItem(row)
            self.sender.send_signal('command_signal', current_item.text())
        self.bot.save_commands()

    def set_Command(self):
        isReadOnly = self.text_display.Editor.isReadOnly()
        if isReadOnly:
            selected_Item = self.command_list.selectedItems()[0].text()
            self.bot.commands[selected_Item] = self.text_display.Editor.toPlainText()
        self.bot.save_commands()

    def add_empty_item(self):
        text = self.commands_edit.text()
        if text == '':
            return
        if self.bot.commands.get(text):
            return
        new_item = QListWidgetItem(text)  # Create empty item
        self.sender.send_signal('command_signal', text)
        self.command_list.addItem(new_item)
        self.commands_edit.clear()

