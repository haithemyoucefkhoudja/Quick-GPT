
from PyQt6.QtWidgets import QWidget, QLineEdit, QComboBox, QSpinBox, QVBoxLayout, QLabel
from ui.base_elements.CustomButton import CustomButton


class LLMSettings(QWidget):
    def __init__(self, parent=None, bot=None, Font=None):
        super().__init__(parent)
        self.bot = bot
        """
        Initializes the SettingsDialog object.
            Args:
                parent: The parent widget (default: None).
        """
        self.setFont(Font)
        self.engines_combobox = QComboBox()
        self.load_engines()
        self.engines_combobox.setCurrentText(bot.active_engine.get('name'))
        self.base_url = QLineEdit()
        self.base_url.setText(bot.active_engine.get("base_url"))
        self.models_combobox = QComboBox()
        self.engines_combobox.currentIndexChanged.connect(self.swtich_Engine)
        self.load_comboBox()
        self.models_combobox.currentIndexChanged.connect(self.changeModel)
        self.models_combobox.setCurrentText(bot.active_model.get("model_name"))
        self.tokens_limit_spinbox = QSpinBox()
        self.tokens_limit_spinbox.setRange(0, 32000)
        self.tokens_limit_spinbox.setValue(bot.max_request_tokens)
        self.max_response_spinbox = QSpinBox()
        self.max_response_spinbox.setRange(0, 32000)
        self.max_response_spinbox.setValue(bot.max_response_tokens)
        self.temperature_spinbox = QSpinBox()
        self.temperature_spinbox.setRange(0, 10)
        self.temperature_spinbox.setValue(int(bot.temperature * 10))
        save_button = CustomButton(" ",
                                   buttons={
                                       "default": {"icon": "", "function": self.save_parameters},
                                   },
                                   )
        save_button.setContentsMargins(0, 0, 10, 0)
        save_button.setText("Save")
        layout = QVBoxLayout()

        layout.addWidget(QLabel("Engines:"))
        layout.addWidget(self.engines_combobox)

        layout.addWidget(QLabel("base_url:"))
        layout.addWidget(self.base_url)

        layout.addWidget(QLabel("Model:"))
        layout.addWidget(self.models_combobox)

        layout.addWidget(QLabel("Max Request:"))
        layout.addWidget(self.tokens_limit_spinbox)

        layout.addWidget(QLabel("Max Response Limit:"))
        layout.addWidget(self.max_response_spinbox)

        layout.addWidget(QLabel("Temperature:"))
        layout.addWidget(self.temperature_spinbox)

        layout.addWidget(save_button)

        self.setLayout(layout)

    def swtich_Engine(self):
        """
        switch the current llm engine
        """
        self.bot.load_engine_parameters(self.engines_combobox.currentText())
        base_url = self.bot.active_engine.get("base_url")
        self.base_url.setText(base_url)
        self.tokens_limit_spinbox.setValue(self.bot.max_request_tokens)
        self.models_combobox.clear()
        self.load_comboBox()
        self.models_combobox.setCurrentText(self.bot.active_model.get("model_name"))
        self.changeModel()
        self.max_response_spinbox.setValue(self.bot.max_response_tokens)
        self.temperature_spinbox.setValue(int(self.bot.temperature * 10))


    def save_parameters(self):
        """
            Saves the selected settings and updates the bot's parameters.
        """
        for item in self.bot.models:
            if self.models_combobox.currentText() == item.get("model_name"):
                self.bot.model = item

        self.bot.active_model = self.bot.models[self.models_combobox.currentIndex()]
        self.bot.temperature = int(self.temperature_spinbox.text()) / 10
        self.bot.max_request_tokens = int(self.tokens_limit_spinbox.text())
        self.bot.max_response_tokens = int(self.max_response_spinbox.text())
        self.bot.save_engine_parameters(self.engines_combobox.currentIndex())

    def load_comboBox(self):
        for item in self.bot.models:
            self.models_combobox.addItem(item.get("model_name"))

    def changeModel(self):
        self.bot.active_model = self.bot.models[self.models_combobox.currentIndex()]


    def load_engines(self):
        for item in self.bot.engines:
            self.engines_combobox.addItem(item.get('name'))
        pass
