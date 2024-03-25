import json
import os
import subprocess
import tempfile
from queue import Queue
from typing import Dict, Optional

import zmq
from Communicator.zmqCommunicator import ZMQCommunicator
from PyQt6.QtCore import pyqtBoundSignal
from dotenv import load_dotenv
from Config import _configInstance
context = zmq.Context()


class Session(ZMQCommunicator):

    """"
    to yield the stream to the front-end
    """
    process: Optional[subprocess.Popen] = None
    Messages_Signals: Optional[Queue] = None
    IsBusy: bool = False
    output_file = Optional[tempfile.NamedTemporaryFile]
    Script: list = []

    def __init__(self):

        super().__init__(socket_type=zmq.REQ)
        self.connect("tcp://localhost:5555")
        self.Messages_Signals = Queue()
        # "C:\Users\haithem-yk\Desktop\New folder (4)\langchain-pdf-qa\src\pdf_qa.py"
        # C:\\Users\\haithem-yk\\Desktop\\Projects\\QuickGpt\\_scripts\\simple.py
        self.startNewProcess(['python', 'C:\\Users\\haithem-yk\\Desktop\\New folder (4)\\langchain-pdf-qa\\src\\pdf_qa.py'])

    def terminate_Process(self):
        if self.process:
            self.terminateSession()
            self.process.terminate()

    def startNewProcess(self, cmd: list) -> None:
        self.process = subprocess.Popen(cmd, stderr=subprocess.PIPE,text=True, close_fds=False)



    def startSession(self):
        self.IsBusy = True

    def terminateSession(self):

        self.IsBusy = False




class Bot:
    session = Session()
    """
    Config File
    """
    Config_file = _configInstance.get_path("Config.json")
    """
    List Of Agents
    """
    agents: list[Dict] = []
    """
    Active Agent
    """
    active_agent: Dict = {}
    """
    Dictonary of commands
    """
    commands: Dict = {}


    def __init__(self):
        super().__init__()
        self.load_engine_parameters(None)



    """
            with subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE) as process:

                self.process = process
                _index = 0
                for line in iter(process.stdout.readline, b''):
                    content = line.decode('utf-8')
                    if content:
                        self.session.Messages_Signals.put((content, _index))
                        _index += 1

                error = process.stderr.read().decode('utf-8')
                if error:
                    self.session.Messages_Signals.put((error, -1))
                self.session.terminateSession()"""

    def generate_response(self, Input: str, progress_callback: pyqtBoundSignal) -> str:
        try:
            if self.session.IsBusy:
                return ''
            if not self.session.process:
                return ''

            self.session.startSession()

            self.session.send_message(Input)
            message = self.session.receive_message()
            progress_callback.emit((message, 0))
            _index = 0
            self.session.terminateSession()

            return 'hello'
        except Exception as e:
            progress_callback.emit((str(e), -1))

    def load_engine_parameters(self, name):

        try:
            with open(self.Config_file, "r") as file:
                config_data = json.load(file)

            load_dotenv()
            """
            API_KEY: DON'T SHARE IT WITH ANYONE EVEN WITH YOUR MOM!!!!
            Python  WILL LOAD IT FROM THE .env file
            """
            self.api_key = os.getenv('API_KEY')
            self.commands = config_data["commands"]
            engines_data = config_data["engines"]['engines_data']
            self.engines = [engine for engine in engines_data]

            for engine in engines_data:
                if engine.get('name') == config_data["engines"]['active_engine']:
                    self.active_engine = engine
            for engine in engines_data:
                if engine.get('name') == name:
                    self.active_engine = engine

            update_data = {k: v for k, v in self.active_engine.items() if v is not None}
            self.__dict__.update(update_data)
        except FileNotFoundError:
            print(f"Error: '{self.Config_file}' not found.")


    def save_commands(self):
        try:
            with open(self.Config_file, "r") as file:
                config_data = json.load(file)

            config_data["commands"] = self.commands
            with open(self.Config_file, "w") as file:
                json.dump(config_data, file, indent=4)

        except FileNotFoundError:
            pass

    def save_engine_parameters(self, index: int):
        try:
            with open(self.Config_file, "r") as file:
                config_data = json.load(file)
            config_data['engines']['active_engine'] = self.active_engine.get('name')
            config_data['engines']['engines_data'][index] = {
                "name": self.active_agent.get('name'),
                "base_url": self.active_agent.get('base_url'),

            }
            with open(self.Config_file, "w") as file:
                json.dump(config_data, file, indent=4)

        except FileNotFoundError:
            print(f"Error: '{self.Config_file}' not found.")
