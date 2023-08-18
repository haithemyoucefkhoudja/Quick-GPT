import math
import os
import struct
import sys
import time
import traceback
import wave
import webbrowser
import pyaudio as pa
import keyboard
from PyQt6 import QtWidgets
from PyQt6.QtCore import Qt, QTimer, QSize, QThread, pyqtSignal, pyqtSlot, QRunnable, QObject, QThreadPool
from PyQt6.QtGui import QIcon, QAction, QFont, QPixmap
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QMenu,
    QSystemTrayIcon,
    QTextEdit,
    QLabel,
    QVBoxLayout,
    QPushButton,
    QWidget, QHBoxLayout, QProgressBar, QMessageBox, QDialog, QLineEdit, QSpinBox, QComboBox,
    QFileDialog,
)
from largelanguagemodel import Bot


class WorkerSignals(QObject):
    '''
    Defines the signals available from a running worker thread.

    Supported signals are:

    finished
        No data

    error
        tuple (exctype, value, traceback.format_exc() )

    result
        object data returned from processing, anything

    progress
        int indicating % progress

    '''
    finished = pyqtSignal()
    error = pyqtSignal(tuple)
    result = pyqtSignal(object)
    progress = pyqtSignal(int)


class Worker(QRunnable):
    '''
    Worker thread

    Inherits from QRunnable to handler worker thread setup, signals and wrap-up.

    :param callback: The function callback to run on this worker thread. Supplied args and
                     kwargs will be passed through to the runner.
    :type callback: function
    :param args: Arguments to pass to the callback function
    :param kwargs: Keywords to pass to the callback function

    '''

    def __init__(self, fn, *args, **kwargs):
        super(Worker, self).__init__()

        # Store constructor arguments (re-used for processing)
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()

        # Add the callback to our kwargs
        self.kwargs['progress_callback'] = self.signals.progress

    @pyqtSlot()
    def run(self):
        '''
        Initialise the runner function with passed args, kwargs.
        '''
        # Retrieve args/kwargs here; and fire processing using them
        try:
            result = self.fn(*self.args)
        except:
            traceback.print_exc()
            exctype, value = sys.exc_info()[:2]
            self.signals.error.emit((exctype, value, traceback.format_exc()))
        else:
            self.signals.result.emit(result)  # Return the result of the processing
        finally:
            self.signals.finished.emit()  # Done


class RecordingThread(QThread):
    stopped = False
    sig_started = pyqtSignal()
    sig_stopped = pyqtSignal()
    sig_intensity = pyqtSignal(int)
    sig_error = pyqtSignal(str)
    sig_result = pyqtSignal(str)
    # Constants for audio settings
    FORMAT = pa.paInt16
    RATE = 44100
    CHUNK = 1024

    def __init__(self, ):
        super().__init__()

    def run(self) -> None:

        try:
            audio = pa.PyAudio()
            frames = []
            stream = audio.open(format=self.FORMAT, channels=1, rate=self.RATE, input=True,
                                frames_per_buffer=self.CHUNK)
        except OSError as e:
            # Handle the error when sound input is not accessible
            self.sig_error.emit(f"Error: Sound input is not accessible -{str(e)}", )
            return  # Or raise an exception, perform cleanup, etc.

        self.stopped = False
        self.sig_started.emit()

        while not self.stopped:
            data = stream.read(self.CHUNK)
            # Calculate voice intensity based on audio data
            rms = 0
            for i in range(0, len(data), 2):
                sample = struct.unpack("<h", data[i:i + 2])[0]
                rms += sample * sample
            rms = math.sqrt(rms / self.CHUNK)
            # Map intensity value to the range of the progress bar
            intensity = int((rms / 32768) * 100)
            self.sig_intensity.emit(intensity)  # Emit the intensity value
            frames.append(data)

        stream.close()

        self.sig_stopped.emit()
        filename = "UserVoiceMessages/" + str(time.time()) + ".wav"
        wf = wave.open(filename, 'wb')
        wf.setnchannels(1)
        wf.setsampwidth(audio.get_sample_size(pa.paInt16))
        wf.setframerate(44100)
        wf.writeframes(b''.join(frames))
        wf.close()
        self.sig_result.emit(bot.from_speech_to_text(filename))

    @pyqtSlot()
    def stop(self):
        self.stopped = True


class AutoResizableTextEdit(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        # Set the font size and color of the editor text
        global font
        editor_font = QFont(font, 12)
        editor_font.setLetterSpacing(QFont.SpacingType.AbsoluteSpacing, 1)
        self.text_editor = QTextEdit()
        self.text_editor.setAcceptRichText(False)  # don't Allow rich text formatting
        self.text_editor.setFont(editor_font)
        self.text_editor.setStyleSheet("""
                    QTextEdit {
                        color: white;
                        background-color: rgb(80, 80, 80);
                        border-radius: 10px;
                        padding: 5px;
                        }
                    QScrollBar {
                    background-color: transparent;
                    width: 10px;
                    }

                    QScrollBar::handle {
                        background-color: rgb(160, 160, 160);
                        border-radius: 4px;
                        min-height: 15px;
                    }

                    QScrollBar::handle:hover {
                        background-color: rgb(120, 120, 120);
                    }

                    QScrollBar::sub-page, QScrollBar::add-page {
                        background-color: rgb(80, 80, 80);
                    }

                    QScrollBar::sub-line, QScrollBar::add-line {
                        background-color: rgb(80, 80, 80);
                    }
                    """)
        self.text_editor.setPlaceholderText("Send Message...")
        self.text_editor.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.text_editor.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        max_characters_line = 50
        self.text_editor.setLineWrapColumnOrWidth(max_characters_line)  # Set the desired column width
        self.text_editor.setLineWrapMode(self.text_editor.LineWrapMode.FixedColumnWidth)
        self.text_editor.setWordWrapMode(self.text_editor.wordWrapMode().WordWrap)
        self.text_editor.setFixedHeight(self.calculateFixedHeight(1))
        self.text_editor.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.text_editor.document().documentLayout().documentSizeChanged.connect(self.resizeToFitContent)
        self.text_editor.textChanged.connect(self.resizeToFitContent)

        self.animation_label = QLabel()
        self.animation_label.setStyleSheet("color: white;")
        self.animation_label.setFixedWidth(42)
        self.animation_label.setFont(QFont(font, 18))
        self.animation_label.setText("")

        self.progress_bar = QProgressBar()
        self.progress_bar.setOrientation(Qt.Orientation.Vertical)
        self.progress_bar.setFixedSize(10, 40)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setStyleSheet("""
                            QProgressBar {
                                background-color: rgb(80, 80, 80);
                                border-radius: 4px;
                            }
                            QProgressBar::chunk {
                                background-color: white;
                                border-radius: 4px;
                            }
                        """)

        self.send_button = CustomButton(icon_path="icons/paper-plane-white.png")
        self.send_button.setShortcut("Ctrl+Return")

        self.voice_record_button = CustomButton(icon_path="icons/microphone-white.png")
        self.voice_record_button.setShortcut("V")

        # Create recording thread and attach slots to its signals
        self.recording_thread = RecordingThread()
        self.recording_thread.sig_started.connect(self.recording_started)
        self.recording_thread.sig_stopped.connect(self.recording_stopped)
        self.recording_thread.sig_intensity.connect(self.set_intensity)
        self.recording_thread.sig_error.connect(self.recording_error)
        self.recording_thread.sig_result.connect(self.append_text)

        self.voice_record_button.clicked.connect(self.recording_thread.start)
        layout = QHBoxLayout()

        layout.addWidget(self.text_editor)
        layout.addWidget(self.send_button)
        layout.addWidget(self.voice_record_button)
        layout.addWidget(self.progress_bar)
        layout.addWidget(self.animation_label)
        # Set the alignment of the QPushButton within its parent layout
        layout.setAlignment(self.send_button, Qt.AlignmentFlag.AlignBottom)
        layout.setAlignment(self.voice_record_button, Qt.AlignmentFlag.AlignBottom)
        layout.setAlignment(self.progress_bar, Qt.AlignmentFlag.AlignBottom)
        layout.setAlignment(self.animation_label, Qt.AlignmentFlag.AlignBottom)
        layout.setAlignment(self.text_editor, Qt.AlignmentFlag.AlignBottom)

        self.setLayout(layout)

    def resizeToFitContent(self):
        count = int((self.text_editor.document().size().height() - 8) / 20)
        if count <= 5:
            self.text_editor.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        if count == 1:
            self.text_editor.setFixedHeight(self.calculateFixedHeight(1))
        if 1 < count <= 5:
            self.text_editor.setFixedHeight(self.calculateFixedHeight(count))
        elif count > 5:
            self.text_editor.setFixedHeight(self.calculateFixedHeight(5))
            self.text_editor.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)

    def calculateFixedHeight(self, count):
        line_height = self.text_editor.fontMetrics().lineSpacing()
        if count == 1:
            line_height += 10
        content_height = line_height * count
        return content_height + (2 * self.text_editor.frameWidth())

    @pyqtSlot()
    def recording_started(self):
        """This slot is called when recording starts"""
        self.voice_record_button.clicked.disconnect(self.recording_thread.start)
        self.voice_record_button.clicked.connect(self.recording_thread.stop)
        self.send_button.setDisabled(True)
        self.voice_record_button.set_custom_Style("rgb(0, 195, 129)", "rgb(0, 195, 129)", "icons/microphone-white.png")
        pass

    @pyqtSlot()
    def recording_stopped(self):
        """This slot is called when recording stops"""
        self.voice_record_button.clicked.disconnect(self.recording_thread.stop)
        self.voice_record_button.clicked.connect(self.recording_thread.start)
        self.send_button.setDisabled(False)
        self.voice_record_button.set_custom_Style("rgb(80, 80, 80)", "rgb(0, 195, 129)", "icons/microphone-white.png")
        pass

    @pyqtSlot(str)
    def recording_error(self, error):
        raise_error_message(error)

    @pyqtSlot(int)
    def set_intensity(self, intensity):
        self.progress_bar.setValue(intensity)

    @pyqtSlot(str)
    def append_text(self, text):
        self.text_editor.insertPlainText(text)


class CustomButton(QPushButton):
    def __init__(self, icon_path="", color=" rgb(80, 80, 80)", hover_color=" rgb(0, 195, 129)"):
        super().__init__()
        self.color = color
        self.icon_path = icon_path
        self.set_custom_Style(color, hover_color, icon_path)
        self.setIconSize(QSize(32, 32))

    def set_custom_Style(self, color, hover_color, icon):
        self.setStyleSheet("""QPushButton {
        background-color: %s;
        width: 40px;
        height: 35px;
        border: none;
        border-radius: 10px;
        padding: 2px;
        }
        QPushButton:hover {
        background-color: %s;
    }
        """ % (color, hover_color))
        self.setIcon(QIcon(os.path.join(basedir, icon)))


class CustomTitleBar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAutoFillBackground(True)
        self.icon_path = "icons/window-icon.png"
        self.setStyleSheet("""
        background-color: rgb(60, 60, 60);
        color: white;
        """)
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        q_font = QFont(font, 12)
        title_label = QLabel()
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        picture = QPixmap(os.path.join(basedir, self.icon_path))
        title_label.setPixmap(picture)
        close_button = QPushButton("X")
        close_button.setShortcut("Esc")
        close_button.setFont(q_font)
        close_button.setFixedHeight(32)
        close_button.setFixedWidth(48)
        close_button.setStyleSheet("""
        QPushButton {
        color: white;
        border: none;
    }
    
    QPushButton:hover {
        background-color: red;
    }
        """)
        close_button.clicked.connect(parent.hide)
        layout.addWidget(title_label)
        # layout.addWidget(Icon_label)
        layout.addWidget(close_button)
        self.setLayout(layout)


class CustomQtextEdit(QTextEdit):
    def __init__(self, parent=None, message='', color="rgb(60, 60, 60)"):
        super().__init__(parent=parent,)
        self.insertPlainText(message)
        self.color = color
        self.initGui()

    def initGui(self):
        self.setReadOnly(True)
        self.setFixedWidth(475)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        max_characters_line = 55
        self.setLineWrapColumnOrWidth(max_characters_line)  # Set the desired column width
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self_font = QFont(font, 11)
        self_font.setLetterSpacing(QFont.SpacingType.AbsoluteSpacing, 1)

        self.setFont(self_font)
        self.setLineWrapColumnOrWidth(max_characters_line)  # Set the desired column width
        self.setLineWrapMode(self.LineWrapMode.FixedColumnWidth)
        self.setWordWrapMode(self.wordWrapMode().WordWrap)
        self.document().documentLayout().documentSizeChanged.connect(self.resizeToFitContent)
        self.setFixedHeight(int(self.document().size().height()))

        self.setStyleSheet("""
                    color: white;
                    background-color: %s;
                    border-radius: 5px;
                    padding: 5px;
                    
                    QScrollBar {
                    background-color: transparent;
                    width: 10px;
                    }

                    QScrollBar::handle {
                        background-color: rgb(160, 160, 160);
                        border-radius: 4px;
                        min-height: 15px;
                    }

                    QScrollBar::handle:hover {
                        background-color: rgb(120, 120, 120);
                    }

                    QScrollBar::sub-page, QScrollBar::add-page {
                        background-color: rgb(80, 80, 80);
                    }

                    QScrollBar::sub-line, QScrollBar::add-line {
                        background-color: rgb(80, 80, 80);
                    }
                                        """ % self.color)
        self.setCursor(Qt.CursorShape.IBeamCursor)

    def resizeToFitContent(self):
        height = int(self.document().size().height())
        self.setFixedHeight(height)

    @pyqtSlot(str)
    def append_text(self, bot_text):
        self.insertPlainText(bot_text)


class AnimationThread(QThread):
    finished = pyqtSignal()

    def __init__(self, label):
        super().__init__()
        self.label = label
        self.running = True

    def run(self):
        while self.running:
            self.label.setText(".")
            self.msleep(500)
            self.label.setText("..")
            self.msleep(500)
            self.label.setText("...")
            self.msleep(500)

    def stop(self):
        self.running = False
        self.msleep(1500)
        self.label.setText("")

    def resume(self):
        self.running = True
        self.start()


class BotThread(QThread):
    result_ready = pyqtSignal()

    def __init__(self, parent=None, user_text=""):
        super().__init__(parent)
        self.user_text = user_text

    def run(self):
        # Perform the time-consuming task
        # ...
        bot.generate_response(self.user_text)
        # Emit the result signal
        self.result_ready.emit()


class Messanger(QWidget):
    global basedir
    lineLength = 60

    def __init__(self, parent=None):
        super().__init__(parent)
        self.bot_label_queue = []
        self.scrollAreaWidgetContents = None
        self.scrollArea = None
        self.layout = None
        self.editor = AutoResizableTextEdit()
        self.animation_thread = AnimationThread(self.editor.animation_label)
        self.send_button = None
        self.text_editor = None
        self.user_text = ""
        self.bot_text = ""
        self.setup_ui()
        self.timer = QTimer()
        self.timer.setInterval(100)  # 100 milliseconds = 0.1 second
        self.timer.timeout.connect(self.start_bot_thread)
        self.timer.start()
        self.bot_thread = None

    def setup_ui(self):
        # Chat. ScrollArea
        self.scrollArea = QtWidgets.QScrollArea()
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setObjectName("scrollArea")
        self.scrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scrollArea.verticalScrollBar().rangeChanged.connect(
            self.scrollToBottom,
        )
        self.scrollArea.setFixedSize(500, 580)
        self.scrollArea.setStyleSheet("""
        scrollArea {
        border: 5px solid white;
        }
        QScrollBar {
                    background-color: transparent;
                    width: 10px;
                    }

                    QScrollBar::handle {
                        background-color: rgb(160, 160, 160);
                        border-radius: 4px;
                        min-height: 20px;
                    }
                
                    QScrollBar::handle:hover {
                        background-color: rgb(120, 120, 120);
                    }
                
                    QScrollBar::sub-page, QScrollBar::add-page {
                        background-color: rgb(60, 60, 60);
                    }
                
                    QScrollBar::sub-line, QScrollBar::add-line {
                        background-color: rgb(60, 60, 60);
                    }
        """)
        # Body that holds the widgets.
        self.scrollAreaWidgetContents = QWidget()
        self.scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")
        # Box that holds the widgets.
        self.layout = QVBoxLayout(self.scrollAreaWidgetContents)
        self.layout.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        self.scrollAreaWidgetContents.setLayout(self.layout)
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        self.layout.addStretch(-1)

        self.send_button = self.editor.send_button
        self.text_editor = self.editor.text_editor
        self.send_button.clicked.connect(self.send_message)
        self.editor.setContentsMargins(0, 20, 40, 0)
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.scrollArea)
        main_layout.addWidget(self.editor)
        self.setLayout(main_layout)

    def send_message(self):
        message = self.text_editor.toPlainText()
        if message:
            self.animation_thread.resume()
            # Start animation after adding the user label
            self.user_text = self.add_label(message)

    def stop_bot(self):
        bot.stop = True

    def add_label(self, message):
        label = CustomQtextEdit(message=message)
        label.setTextInteractionFlags(
                label.textInteractionFlags().TextSelectableByMouse |
                label.textInteractionFlags().TextBrowserInteraction |
                label.textInteractionFlags().TextSelectableByKeyboard)
        self.send_button.set_custom_Style(hover_color="rgb(255, 8, 76)", color="rgb(80, 80, 80)", icon="icons/stop.png")
        self.layout.addWidget(label)
        self.bot_label_queue.append(CustomQtextEdit(color="rgb(30, 30, 30)"))
        self.send_button.clicked.disconnect(self.send_message)
        self.send_button.clicked.connect(self.stop_bot)
        bot_label = self.bot_label_queue[len(self.bot_label_queue) - 1]
        bot_label.setTextInteractionFlags(bot_label.textInteractionFlags().NoTextInteraction)
        self.layout.addWidget(bot_label)
        bot.sig_response.connect(bot_label.append_text)
        self.text_editor.clear()
        return message

    def start_bot_thread(self):
        if (self.bot_thread is None or not self.bot_thread.isRunning()) and self.user_text != "":
            self.bot_thread = BotThread(self, user_text=self.user_text)
            self.bot_thread.result_ready.connect(self.bot_label)
            self.bot_thread.start()

    def bot_label(self):
        if self.user_text != "":
            self.timer.stop()
            self.send_button.set_custom_Style(hover_color="rgb(0, 195, 129)", color="rgb(80, 80, 80)", icon= "icons/paper-plane-white.png")
            self.send_button.clicked.disconnect(self.stop_bot)
            self.send_button.clicked.connect(self.send_message)
            bot.stop = False
            self.user_text = ""
            self.editor.text_editor.setText("")
            self.animation_thread.stop()
            bot_label = self.bot_label_queue[len(self.bot_label_queue) - 1]
            bot_label.setTextInteractionFlags(
                bot_label.textInteractionFlags().TextSelectableByMouse |
                bot_label.textInteractionFlags().TextBrowserInteraction |
                bot_label.textInteractionFlags().TextSelectableByKeyboard)

            bot.sig_response.disconnect(bot_label.append_text)
            self.timer.start()

    def scrollToBottom(self):
        # Additional params 'minVal' and 'maxVal' are declared because
        # rangeChanged signal sends them, but we set it to optional
        # because we may need to call it separately (if you need).
        self.scrollArea.verticalScrollBar().setValue(
            self.scrollArea.verticalScrollBar().maximum()
        )


class IconsMenu(QWidget):

    def __init__(self):
        super().__init__()
        self.new_widget = None
        self.index = 0
        self.layout = QHBoxLayout()
        label = QLabel()
        label.setFixedWidth(10)
        self.comboBox = QComboBox(self)
        self.setFixedHeight(42)
        self.comboBox.setFixedHeight(38)
        self.comboBox.setFixedWidth(210)
        self.comboBox.setFont(QFont(font, 10))
        self.setFixedWidth(510)
        self.populate_combo_box()

        self.animation_label = QLabel()
        self.animation_label.setStyleSheet("color: white;")
        self.animation_label.setFixedWidth(42)
        self.animation_label.setFont(QFont(font, 18))
        self.pdf_animation = AnimationThread(self.animation_label)
        self.threadpool = QThreadPool()
        self.add_new_pdf_button = CustomButton(icon_path="icons/plus-button.png")
        self.add_new_pdf_button.clicked.connect(self.open_navigation_bar)
        self.add_new_pdf_button.setStatusTip("Upload PDF File")
        self.add_new_pdf_button.setFixedWidth(42)
        self.layout.setContentsMargins(0, 0, 0, 0)

        telegram_link_button = CustomButton()
        telegram_link_button.set_custom_Style(hover_color="rgb(100,190,249)", color="rgb(80, 80, 80)",icon="icons/share.png")
        telegram_link_button.clicked.connect(lambda: webbrowser.open("https://t.me/+XKFgOwVjUVs4NDBk"))
        telegram_link_button.setFixedWidth(42)

        donate_link_button = CustomButton()
        donate_link_button.set_custom_Style(hover_color="rgb(255, 36, 0)", color="rgb(80, 80, 80)",
                                              icon="icons/heart.png")
        donate_link_button.clicked.connect(lambda: webbrowser.open("https://www.blockonomics.co/pay-url/aac9917abdc443b4"))
        donate_link_button.setFixedWidth(42)
        self.layout.addWidget(label)
        self.layout.addWidget(self.comboBox)
        self.layout.addWidget(self.add_new_pdf_button)
        self.layout.addWidget(self.animation_label)
        self.layout.addStretch()
        self.layout.addWidget(telegram_link_button)
        self.layout.addWidget(donate_link_button)
        self.layout.setAlignment(telegram_link_button, Qt.AlignmentFlag.AlignRight)
        self.layout.setAlignment(self.comboBox, Qt.AlignmentFlag.AlignLeft)
        self.layout.setAlignment(self.add_new_pdf_button, Qt.AlignmentFlag.AlignLeft)
        self.setLayout(self.layout)

    def start_animation_thread(self):
        self.pdf_animation.resume()

    def stop_animation_thread(self):
        self.pdf_animation.stop()

    def add_doc_name(self, doc_name):
        self.comboBox.addItem(doc_name)

    def open_navigation_bar(self):
        file_dialog = QFileDialog(self)
        file_dialog.setFileMode(QFileDialog.FileMode.ExistingFiles)
        file_dialog.setNameFilter("PDF Files (*.pdf)")
        if file_dialog.exec() == QFileDialog.DialogCode.Accepted:
            selected_files = file_dialog.selectedFiles()
            for file in selected_files:
                # ........................................
                self.start_animation_thread()
                pdf_name = os.path.basename(file.split("/")[-1].split(".pdf")[0])
                # Pass the function to execute
                worker = Worker(bot.pdf_embedding, file, pdf_name) # Any other args, kwargs are passed to the run function
                worker.signals.finished.connect(self.stop_animation_thread)
                worker.signals.result.connect(self.add_doc_name)
                self.threadpool.start(worker)

    def populate_combo_box(self):
        self.comboBox.setStyleSheet("""
        QComboBox {
    background-color: rgb(80, 80, 80);
    color: white;
    border: none;
    border-radius: 8px;
    padding: 1px 5px 1px 5px;
    min-width: 6em;
}

QComboBox::drop-down {
    subcontrol-origin: padding;
    subcontrol-position: top right;
    width: 15px;
    border-left-width: 0px;
    border-left-color: gray;
    border-left-style: solid;
    border-top-right-radius: 5px;
    border-bottom-right-radius: 5px;
}
QComboBox::down-arrow {
    image: url(./icons/combobox_down_arrow.png);
    height: 10px;
    width: 10px;
}
QListView{
    background-color: rgb(80, 80, 80);
    border: 5px;
    color: white;
    font-weight: bold;
    show-decoration-selected: 1;
}
QComboBox QAbstractItemView::item {
    height: 32px;
    width: 132px;
    border: none;
}

QComboBox QAbstractItemView::item:selected {
    border: 2px solid white;
    background: rgb(0, 195, 129);
}
        """)
        # Directory path where the files are located
        directory_path = os.path.join(basedir, "Docs")
        # Get a list of files ending with "-properties"
        file_names = [file for file in os.listdir(directory_path) if file.endswith("_indicator")]

        # Iterate over the files and add the PDF Files
        for file_name in file_names:
            document_name = file_name.split("_indicator")[0]
            self.comboBox.addItem(document_name)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setFixedSize(560, 762)
        self.setStyleSheet("""
        QWidget {
        background-color: rgb(60, 60, 60);
        }
        """)
        self.center()
        self.message_container = Messanger(self)
        main_layout = QVBoxLayout()
        iconsmenu = IconsMenu()
        main_layout.addWidget(iconsmenu)
        main_layout.setAlignment(iconsmenu, Qt.AlignmentFlag.AlignLeft)
        main_layout.addWidget(self.message_container)

        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        # Set the window flags to enable a borderless window
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        # Create a custom title bar widget and set it as the window title bar
        self.title_bar = CustomTitleBar(self)
        self.setMenuWidget(self.title_bar)
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

    def toggle_visibility(self):
        if self.isHidden():
            self.show()
        else:
            self.hide()


font = "Tahoma"
basedir = os.getcwd()
bot = Bot()

directories = ['UserVoiceMessages', 'Docs']
# Create the directories if they don't exist
for directory in directories:
    if not os.path.exists(directory):
        os.makedirs(directory)


def raise_error_message(message):
    error_box = QMessageBox()
    error_box.setFont(QFont(font, 11))
    error_box.window().setStyleSheet("""
    background-color: rgb(60, 60, 60)
    color: white;
    """)
    error_box.setStyleSheet("""
    background-color: rgb(60, 60, 60);
    color: white;
    """)
    error_box.setIcon(QMessageBox.Icon.Critical)
    error_box.setWindowTitle("Error")
    error_box.setText("An error occurred:")
    error_box.setInformativeText(message)
    error_box.exec()


class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        """
        Initializes the SettingsDialog object.
            Args:
                parent: The parent widget (default: None).
        """
        super().__init__(parent)
        self.setFixedSize(250, 450)
        self.setWindowTitle("Settings")
        self.setWindowIcon(QIcon(os.path.join(basedir, "icons/icon16.png")))
        self.setFont(QFont(font, 11))
        self.setStyleSheet("""
                 QLineEdit, QSpinBox {
            background-color: rgb(80, 80, 80);
            color: white;
            border: none;
            border-radius: 4px;
            padding: 5px;
        }
        QComboBox {
    background-color: rgb(80, 80, 80);
    color: white;
    border: none;
    border-radius: 5px;
    padding: 1px 18px 1px 3px;
    min-width: 6em;
}

QComboBox::drop-down {
    subcontrol-origin: padding;
    subcontrol-position: top right;
    width: 15px;
    border-left-width: 0px;
    border-left-color: gray;
    border-left-style: solid;
    border-top-right-radius: 5px;
    border-bottom-right-radius: 5px;
}
QComboBox::down-arrow {
    image: url(./icons/combobox_down_arrow.png);
    height: 10px;
    width: 10px;
}
QListView{
    background-color: rgb(80, 80, 80);
    color: white;
    font-weight: bold;
    show-decoration-selected: 1;
}
QComboBox QAbstractItemView::item {
    border: none;
}
QComboBox QAbstractItemView::item:selected {
    border: 2px solid white;
    background: rgb(0, 195, 129);
}
        QDialog {
            background-color: rgb(60, 60, 60);
            color: white;
            border: none;
        }
        QPushButton {
        color: white;
        }
        QLabel {
        color: white;
        }
        
        QSpinBox::up-button, QSpinBox::down-button {
        border: none;
        }
        
        """)
        self.apikey_edit = QLineEdit()
        self.apikey_edit.setText(bot.api_key)

        self.organizationkey_edit = QLineEdit()
        self.organizationkey_edit.setText(bot.organization_key)

        self.models_combobox = QComboBox()
        self.models_combobox.addItem("gpt-3.5-turbo")
        self.models_combobox.addItem("gpt-3.5-turbo-16k")
        self.models_combobox.addItem("gpt-4")
        self.models_combobox.addItem("gpt-4-32k")
        self.models_combobox.setCurrentText(bot.model)
        self.models_combobox.currentIndexChanged.connect(self.models_token_limit)
        self.tokens_limit_spinbox = QSpinBox()
        self.models_token_limit(self.models_combobox.currentIndex())
        self.tokens_limit_spinbox.setValue(bot.max_request_tokens)
        self.max_response_spinbox = QSpinBox()
        self.max_response_spinbox.setRange(0, 1000)
        self.max_response_spinbox.setValue(bot.max_response_tokens)
        self.temperature_spinbox = QSpinBox()
        self.temperature_spinbox.setRange(0, 10)
        self.temperature_spinbox.setValue(int(bot.temperature * 10))
        save_button = CustomButton()
        save_button.setText("Save")
        save_button.clicked.connect(self.save_parameters)

        layout = QVBoxLayout()
        layout.addWidget(QLabel("API KEY:"))
        layout.addWidget(self.apikey_edit)

        layout.addWidget(QLabel("ORGANIZATION KEY:"))
        layout.addWidget(self.organizationkey_edit)

        layout.addWidget(QLabel("Model:"))
        layout.addWidget(self.models_combobox)

        layout.addWidget(QLabel("Token Limit:"))
        layout.addWidget(self.tokens_limit_spinbox)

        layout.addWidget(QLabel("Max Response Limit:"))
        layout.addWidget(self.max_response_spinbox)

        layout.addWidget(QLabel("Temperature:"))
        layout.addWidget(self.temperature_spinbox)

        layout.addWidget(save_button)

        self.setLayout(layout)

    def save_parameters(self):
        """
                Saves the selected settings and updates the bot's parameters.
                """
        bot.model = self.models_combobox.currentText()
        bot.api_key = self.apikey_edit.text()
        bot.organization_key = self.organizationkey_edit.text()
        bot.temperature = int(self.temperature_spinbox.text()) / 10
        bot.max_request_tokens = int(self.tokens_limit_spinbox.text())
        bot.max_response_tokens = int(self.max_response_spinbox.text())
        bot.save_parameters()
        bot.init_openai()

    def models_token_limit(self, index):
        if index == 0:
            self.tokens_limit_spinbox.setRange(0, 4096)
        elif index == 1:
            self.tokens_limit_spinbox.setRange(0, 16384)
        elif index == 2:
            self.tokens_limit_spinbox.setRange(0, 8192)
        elif index == 3:
            self.tokens_limit_spinbox.setRange(0, 32768)


def check_shortcut():
    if keyboard.is_pressed("shift+r"):
        w.toggle_visibility()
    if keyboard.is_pressed("ctrl+t"):
        w.show()
        w.focusWidget()
        # get copied text
        clipboard = QApplication.clipboard()
        w.message_container.text_editor.insertPlainText(clipboard.text())


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)

    icon = QIcon(os.path.join(basedir, "icons/icon16.png"))
    app.setWindowIcon(icon)
    tray = QSystemTrayIcon()
    tray.setIcon(icon)
    tray.setVisible(True)

    menu = QMenu()
    quit = QAction("Quit")
    quit.triggered.connect(app.quit)
    # Add settings action
    settings = QAction("Settings")

    s = SettingsDialog()
    settings.triggered.connect(s.show)  # Replace `show_settings_dialog` with your own function
    menu.addAction(settings)
    menu.addAction(quit)
    tray.setContextMenu(menu)

    w = MainWindow()
    w.show()
    timer = QTimer()
    timer.timeout.connect(check_shortcut)
    timer.start(100)

    tray.activated.connect(w.activate)
    app.aboutToQuit.connect(w.save)

    sys.exit(app.exec())
