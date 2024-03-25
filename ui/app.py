import os

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QPixmap
from PyQt6.QtWidgets import QVBoxLayout, QMainWindow, QWidget, QApplication, QHBoxLayout, QFrame, QLabel, \
    QSystemTrayIcon
from Config import _configInstance
from ui.AgentList.agentsList import ImageListWidget
from ui.Messanger.Messanger import Messanger
from ui.Menu.Menu import IconsMenu
from ui.base_elements.CustomButton import CustomButton
from ui.input.input import AutoResizableTextEdit




class CustomTitleBar(QFrame):
    BUTTON_HEIGHT = 32
    BUTTON_WIDTH = 48
    CLOSE_BUTTON_NAME = 'CloseButton'
    CUSTOM_TITLE_BAR = 'CustomTitleBar'
    CLOSE_BUTTON_SHORTCUT = 'Esc'

    def __init__(self, parent=None, behavior_fn=None):
        super().__init__(parent)
        self.setAutoFillBackground(True)
        self.setObjectName(self.CUSTOM_TITLE_BAR)
        self.icon_path = "static_files/icons/QuickGPT.png"
        self.setFixedSize(_configInstance.Width, 32)
        layout = QHBoxLayout()
        title_label = QLabel()
        picture = QPixmap(_configInstance.get_path(self.icon_path))
        title_label.setPixmap(picture)
        close_button = CustomButton(self.CLOSE_BUTTON_NAME, self.BUTTON_HEIGHT, self.BUTTON_WIDTH,
                                    buttons={
                                        "default": {"icon": "", "function": behavior_fn},
                                    },
                                    )
        close_button.setObjectName(self.CLOSE_BUTTON_NAME)
        close_button.setFixedHeight(self.BUTTON_HEIGHT)
        close_button.setFixedWidth(self.BUTTON_WIDTH)
        close_button.setFont(QFont(_configInstance.Font, 12))
        close_button.setText('X')
        close_button.setShortcut(self.CLOSE_BUTTON_SHORTCUT)
        title_label = QLabel()
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        picture = QPixmap(_configInstance.get_path(self.icon_path))
        title_label.setPixmap(picture)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(title_label)
        layout.addWidget(close_button)
        self.setLayout(layout)

    def parent_close(self):
        QApplication.instance().quit()  # Close the entire application


class MainWindow(QMainWindow):
    def __init__(self, bot, sender):
        super().__init__()

        self.setFixedSize(_configInstance.Width, _configInstance.Height)
        self.center()
        main_layout = QVBoxLayout()
        # Connect the signal from Sender to the slot in Receiver
        message_container = Messanger(parent=self, sender=sender, bot=bot)
        # AgentsList = ImageListWidget(parent=self, bot=bot)
        input = AutoResizableTextEdit(sender=sender, bot=bot)
        icons_menu = IconsMenu(bot=bot,sender=sender)
        main_layout.addWidget(icons_menu)
        # main_layout.addWidget(AgentsList)
        main_layout.addWidget(message_container)
        main_layout.addWidget(input)
        central_widget = QWidget()
        central_widget.setObjectName('Central_Widget')
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        # Set the window flags to enable a borderless window
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        # Create a custom title bar widget and set it as the window title bar
        self.title_bar = CustomTitleBar(self, self.toggle_visibility)
        self.setMenuWidget(self.title_bar)
        main_layout.setSpacing(0)
        self.setStyleSheet(_configInstance.load_stylesheet(_configInstance.get_path('static_files/style.css')))
        self.oldPos = self.pos()

    def center(self):
        qr = self.frameGeometry()
        cp = self.screen().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def mousePressEvent(self, event):
        self.dragPos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event):
        self.move(self.pos() + event.globalPosition().toPoint() - self.dragPos)
        self.dragPos = event.globalPosition().toPoint()
        event.accept()

    def save(self):
        pass

    def clear_conv(self):
        pass

    def activate(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            self.show()
    def changePos(self) -> None:
        " change Pos and show Screen "

        self.show()

        screen_geometry = QApplication.primaryScreen().availableGeometry()

        # Calculate widget's bottom-right point
        widget_x = screen_geometry.width() - self.width()  # Align to right edge
        widget_y = screen_geometry.height() - self.height()  # Align to bottom

        # Move the widget
        self.move(widget_x, widget_y)


    def toggle_visibility(self):
        if self.isHidden():
            self.show()
        else:
            self.hide()
