import pyttsx3
from PyQt6.QtCore import QRunnable, pyqtSignal, QObject
from Config import _configInstance
import simpleaudio as sa


class WorkerSignals(QObject):
    """
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

    """
    finished = pyqtSignal()


class Voiceoutput(QObject):
    engine = pyttsx3.init()

    def __init__(self, text: str = None):
        super().__init__()
        self.text = text
        _wave_obj = None
        _play_obj = None
        self.signals = WorkerSignals()

    def speechThread(self) -> None:
        """Speaks a given text using pyttsx3 and simulates audio streaming.
        """
        # 1. Initialize Text-to-Speech Engine

        # 2. Customize Voice Settings (Optional)
        # Example: Setting the rate
        rate = self.engine.getProperty('rate')
        self.engine.setProperty('rate', rate + 10.0)  # Slightly faster
        if not self.text:
            return
        self.engine.save_to_file(self.text, f'{_configInstance.Base_Dir}/output.wav')
        self.engine.runAndWait()
        self._wave_obj = sa.WaveObject.from_wave_file(f'{_configInstance.Base_Dir}/output.wav')
        self._play_obj = self._wave_obj.play()
        self._play_obj.wait_done()  # Wait for playback to finish
        self.engine.stop()
        self.signals.finished.emit()

    def run(self):
        self.speechThread()

    def stop(self):
        if self._play_obj:
            self._play_obj.stop()  # Best we can do to stop prematurely
            self._wave_obj = None


_voice_instance = Voiceoutput()
