from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QPixmap
from PyQt6.QtWidgets import QHBoxLayout, QFrame, QWidget, QLabel, QVBoxLayout

from ui.base_elements.CustomButton import CustomButton
from Config import _configInstance
from ui.settings.settings import SettingDialog


class DonationWidget(QWidget):
    def __init__(self, qr_code_path, message):
        super().__init__()

        self.setWindowTitle("Support App")
        self.setStyleSheet("background-color: rgb(57, 62, 70); color: white;")
        # Image section
        qr_code_label = QLabel()
        qr_code_pixmap = QPixmap(qr_code_path)
        qr_code_label.setPixmap(qr_code_pixmap.scaledToWidth(350, Qt.TransformationMode.SmoothTransformation))

        # Text section
        message_label = QLabel(message)
        message_label.setFont(QFont(_configInstance.Font, 12))
        message_label.setWordWrap(True)

        # Layout
        text_layout = QVBoxLayout()
        text_layout.addWidget(message_label, alignment=Qt.AlignmentFlag.AlignCenter)

        main_layout = QHBoxLayout()
        main_layout.addWidget(qr_code_label, alignment=Qt.AlignmentFlag.AlignCenter)
        main_layout.addLayout(text_layout)

        self.setLayout(main_layout)


class IconsMenu(QFrame):
    MENU_BUTTON: str = 'MenuButton'
    DONATE: str = 'DonateButton'
    Height: int = 50
    ComboBox: str = 'FileComboBox'
    IconsMenu_Object = 'IconsMenu'

    def __init__(self, parent=None, bot=None, sender=None):
        super().__init__(parent)

        self.setObjectName(self.IconsMenu_Object)
        # self.File_button = CustomButton(behavior_fn=self.open_navigation_bar, icon='ui/static_files/icons/plus-button.png',button_height=40)
        self.settings = SettingDialog(bot=bot, sender=sender)
        self.Settings_Button = CustomButton(self.MENU_BUTTON,
                     buttons={
                         "default": {"icon": 'static_files/icons/setting.png', "function": self.open_setting},
                     },
                     button_width=40)

        self.new_widget = None
        self.index = 0
        self.layout = QHBoxLayout()
        """self.comboBox = QComboBox(self)
        self.comboBox.currentIndexChanged.connect(self.on_combo_box_current_index_changed)
        self.comboBox.setObjectName(self.ComboBox)
        self.setFixedHeight(50)
        self.comboBox.setFixedHeight(self.Height - 10)
        self.comboBox.setFixedWidth(210)
        self.comboBox.setFont(QFont(Config.Font, 10))"""

        # self.File_button.setObjectName(self.MENU_BUTTON)

        # TODO: add some file logic

        self.layout.addStretch()
        qr_code_path = _configInstance.get_path("static_files/icons/Support.png")
        message = "Your donation makes a difference. Scan the QR code to contribute and make developer Happy (:"
        Donation = DonationWidget(qr_code_path, message)
        Donate_Button = CustomButton(self.DONATE,
                                     buttons={
                                         "default": {"icon": "static_files/icons/heart.png", "function": Donation.show},
                                     },
                                     button_width=40
                                     )
        self.layout.addWidget(Donate_Button)
        self.layout.addWidget(self.Settings_Button)

        self.layout.addSpacing(20)
        self.setLayout(self.layout)

    def add_doc_name(self, doc_name):
        self.comboBox.addItem(doc_name)

    def open_setting(self):
        self.settings.show()

    """def open_navigation_bar(self):
        file_dialog = QFileDialog(self)
        file_dialog.setFileMode(QFileDialog.FileMode.ExistingFiles)
        file_dialog.setNameFilter("Json Files (*.json)")
        if file_dialog.exec() == QFileDialog.DialogCode.Accepted:
            selected_files = file_dialog.selectedFiles()
            for file in selected_files:
                file_name = os.path.basename(file.split("/")[-1].split(".json")[0])
                with open(file, 'r', encoding='utf-8') as filee:
                    json_data = filee.read()
                    # Parse the JSON data
                    data = json.loads(json_data)
                    #self.Messanger.Increment()
                    #for Qa in data:
                     #   self.Messanger.add_label(Qa)
                self.comboBox.addItem(file_name)

    def on_combo_box_current_index_changed(self, index):
        pass
        # This function will be called when the current index changes.
        self.Messanger.chosen_file(index)"""
