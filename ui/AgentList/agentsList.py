from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QPixmap, QPainter, QBitmap, QFont
from PyQt6.QtWidgets import QLabel, QWidget, QVBoxLayout, QHBoxLayout, QScrollArea
from Config import _configInstance
from ui.base_elements.CustomButton import CustomButton


class RoundedImage(QLabel):
    def __init__(self):
        super().__init__()
        self.__initVal()
        self.__initUi()

    def __initVal(self):
        self.__pixmap = ''
        self.__mask = ''

    def __initUi(self):
        self.setObjectName('AgentLabel')
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


class ImageListWidget(QWidget):
    def __init__(self, parent=None, bot=None):
        super().__init__(parent)
        self.bot = bot
        self._layout = QHBoxLayout()
        self._left_side = QHBoxLayout()
        self._right_side = QHBoxLayout()
        self.setLayout(self._layout)
        self.setFixedHeight(70)
        scroll_area = QScrollArea(self)
        scroll_area.setStyleSheet(scroll_area.styleSheet() + """
        background-color: rgb(57, 62, 70);
        """)
        widget = QWidget()  # Create a container widget
        widget.setFixedHeight(65)

        widget.setStyleSheet("background-color: rgb(57, 62, 70);")
        widget.setLayout(self._right_side)
        add_button = CustomButton('agentButton',
                                  button_width=32,
                                  button_height=32,
                                  buttons={
                                      "default": {"icon": 'static_files/icons/add.png',
                                                  "function": self.add_empty_item},
                                  },
                                  )
        self._left_side.addWidget(add_button)
        for i in range(1, 30):
            self.addImage("C:\\Users\\haithem-yk\\Desktop\\csv\\Accountant.png")

        scroll_area.setWidget(widget)
        scroll_area.setObjectName("AgentsScroll")
        self.setObjectName("AgentsList")
        self._layout.addLayout(self._left_side)
        self._layout.addWidget(scroll_area)
        self._layout.addStretch(0)

    def add_empty_item(self):
        self.addImage("C:\\Users\\haithem-yk\\Desktop\\csv\\Accountant.png")
        pass

    def addImage(self, filename):
        self_font = QFont(_configInstance.Font, _configInstance.Flash_Card_Font_Size)
        self_font.setLetterSpacing(QFont.SpacingType.AbsoluteSpacing, 0.5)
        self_font.setWeight(900)

        #_botlabel = QLabel('Unkonwn') if self.AgentConfig else QLabel('Unkonwn')
        _botlabel = QLabel('Unkonwn')
        _botlabel.setStyleSheet("color:white;")
        _botlabel.setFont(self_font)
        image = RoundedImage()
        image.setImage(filename)
        image.setFixedSize(QSize(32, 32))  # Example image size
        info_layout = QVBoxLayout()
        info_layout.addStretch(0)
        info_layout.addWidget(image, alignment=Qt.AlignmentFlag.AlignHCenter)
        info_layout.addWidget(_botlabel, alignment=Qt.AlignmentFlag.AlignHCenter)
        self._right_side.addLayout(info_layout, 1)


