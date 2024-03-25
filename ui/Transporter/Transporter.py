from PyQt6.QtCore import pyqtSignal, QObject, pyqtBoundSignal
from typing import Dict
from typing import Callable


class Sender(QObject):
    command_signal = pyqtSignal(str)
    input_signal = pyqtSignal(object)
    shortcut_signal = pyqtSignal(str)
    isLoading_signal = pyqtSignal(bool)
    set_shortcut_signal = pyqtSignal(tuple)
    signal_map: Dict[str, pyqtBoundSignal] = {}

    def __init__(self):
        super().__init__()
        self.signal_map = self.get_bound_signals()

    def get_bound_signals(self) -> Dict[str, pyqtBoundSignal]:
        signal_map = {}
        for name in dir(self):
            attr = getattr(self, name)

            if isinstance(attr, pyqtBoundSignal):
                signal_map[name] = attr
        return signal_map

    def send_signal(self, signal_name: str, data: object=None) -> None:
        """Dispatches the specified signal, optionally with data.

        Args:
            signal_name: The string identifier of the signal.
            data: The data to be emitted with the signal (optional).
        """

        if signal_name in self.signal_map:
            signal = self.signal_map[signal_name]
            signal.emit(data)
        else:
            # You might want to raise an exception or log an error here
            print(f"Signal not found: {signal_name}")

    def connect_signal(self, signal_name: str, target_function: Callable) -> None:
        """Connects a signal to a specified function.

        Args:
            signal_name: The string identifier of the signal.
            target_function: The function (or method) to connect to the signal.
        """
        if signal_name in self.signal_map:
            self.signal_map[signal_name].connect(target_function)
        else:
            # You might want to raise an exception or log an error here
            print(f"Signal not found: {signal_name}")
