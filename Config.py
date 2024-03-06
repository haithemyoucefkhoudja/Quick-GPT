import os
from PyQt6.QtCore import QFile, QTextStream


class Config:
    Base_Dir = os.path.dirname(__file__)
    Font: str = "consolas"
    Prompt_Font_Size: int = 12
    Flash_Card_Font_Size: int = 11
    Height: int = 780
    Width: int = 920

    def get_path(self, file_path: str):
        """Returns the directory of the main Python script."""
        full_path: str = os.path.join(self.Base_Dir,file_path)
        if not os.path.exists(full_path):
            raise FileNotFoundError
        return full_path
    @staticmethod
    def load_stylesheet(filename):
        style_file = QFile(filename)
        if style_file.open(QFile.OpenModeFlag.ReadOnly | QFile.OpenModeFlag.Text):
            stream = QTextStream(style_file)
            stylesheet = stream.readAll()
            style_file.close()
            return stylesheet
        else:
            return ''


_configInstance = Config()