import math
import os
import struct
import time
import wave
import pyaudio as pa

from PyQt6.QtCore import pyqtSlot,QThread, pyqtSignal


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
            raise e

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
        # self.sig_result.emit(bot.from_speech_to_text(filename))

    @pyqtSlot()
    def stop(self):
        self.stopped = True
