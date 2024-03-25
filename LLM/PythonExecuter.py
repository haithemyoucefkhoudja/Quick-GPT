import subprocess
from PyQt6.QtCore import  pyqtSignal, QThread
import os
import signal

class PythonExecutor(QThread):
    output_received = pyqtSignal(str)
    error_received = pyqtSignal(str)
    finished = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.cmd = None
        self.PID = None

    def setCommand(self, cmd: list) -> None:
        self.cmd = cmd

    def run(self):
        if not self.cmd:
            return
        with subprocess.Popen(self.cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE) as process:
            self.PID = process.pid
            for line in iter(process.stdout.readline, b''):
                self.output_received.emit(line.decode('utf-8'))
            error = process.stderr.read().decode('utf-8')
            if error:
                self.error_received.emit(error)

        self.finished.emit()

    def Stop(self):
        if self.PID:
            os.kill(self.PID, signal.Signals.SIGILL)


