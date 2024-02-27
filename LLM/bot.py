import ast
import json
import os
import time
from typing import Dict
from langchain_openai import ChatOpenAI
import tiktoken
from PyQt6.QtCore import pyqtBoundSignal
from dotenv import load_dotenv
from Config import _configInstance


class Bot:
    """"
    to yield the stream to the front-end
    """
    """
    Config File
    """
    Config_file = _configInstance.get_path("Config.json")
    """
    List Of engines
    """
    engines: list[str] = []
    """
    Active Engine
    """
    active_engine: Dict = {
        "name": 'together',
        "base_url": 'https://api.together.xyz',
    }
    """
    Dictonary of commands
    """
    commands: Dict = {}
    """"
    to stop the stream
    """
    stop: bool = False

    temperature: float = 0.5
    """ 
    model_name: The name of the currently active large language model (LLM)
    start: Token marking the beginning of the LLM's generated text Exp: "<|im_start|>" 
    end: Token marking the end of the LLM's generated text Exp: "<|im_end|>"
    """
    active_model: Dict = {
        "model_name": '',
        "start": '',
        "end": ''
    }
    """"
    list of models
    """
    models: list[Dict] = []
    """"
    max request message size you can add tokenizer
    """
    max_request_tokens: int = 1000
    """
    max output length
    """
    max_response_tokens: int = 750
    """
    api_key 
    """
    api_key: str = ''

    def __init__(self):
        super().__init__()
        self.load_engine_parameters()

    @staticmethod
    def fill_template(template, **kwargs):
        """
        TODO: Maybe In the Future kind Hard

        Fills a template string with positional arguments using string formatting.

        Args:
            template (str): The template string with placeholders.
            **kwargs: Positional arguments to fill the placeholders.

        Returns:
            str: The formatted string with the placeholders filled in.
        """
        return template.format(**kwargs)

    @staticmethod
    def num_tokens_from_messages(messages, model="gpt-3.5-turbo-0613"):
        """Returns the number of tokens used by a list of messages."""
        try:
            encoding = tiktoken.encoding_for_model(model)
        except KeyError:
            encoding = tiktoken.get_encoding("cl100k_base")
        if model == "gpt-3.5-turbo-0613":  # note: future models may deviate from this
            num_tokens = 0
            for message in messages:
                num_tokens += 4  # every message follows <im_start>{role/name}\n{content}<im_end>\n
                for key, value in message.items():
                    num_tokens += len(encoding.encode(value))
                    if key == "name":  # if there's a name, the role is omitted
                        num_tokens += -1  # role is always required and always 1 token
            num_tokens += 2  # every reply is primed with <im_start>assistant
            return num_tokens
        else:
            raise NotImplementedError(f"""num_tokens_from_messages() is not presently implemented for model {model}.
          See https://github.com/openai/openai-python/blob/main/chatml.md for information on how messages are converted to tokens.""")

    def generate_response(self, template: str, progress_callback: pyqtBoundSignal) -> str:

        # input = self.fill_template(template, **kwargs)
        result = ''
        try:
            messages = [
                {"role": "system", "content": "you are helpful assistant"},
                {"role": "user", "content": template},
            ]
            tokens: int = self.num_tokens_from_messages(messages)
            if tokens > self.max_request_tokens:
                progress_callback.emit(f'\ntokens={tokens} > max_request_tokens={self.max_request_tokens}')
                return ''
            client: ChatOpenAI = ChatOpenAI(api_key=self.api_key,
                                            base_url=self.active_engine.get('base_url'),
                                            temperature=self.temperature,
                                            model=self.active_model.get("model_name"),
                                            max_tokens=self.max_response_tokens,
                                            )
            list_token = []
            with open(_configInstance.get_path('ui/Messanger/python exe.txt')) as file:
                List = file.read()
                my_list = ast.literal_eval(List)
                print(len(my_list))

            _index = 0
            for chunk in client.stream(template):
            #for content in my_list[2]:
                content = chunk.content
                """"
                stream each token to the UI
                """
                list_token.append(content)
                progress_callback.emit((content or "", _index))
                result += content or ''
                time.sleep(0.02)
                _index += 1

            progress_callback.emit((f'\ntokens={tokens}', _index))
            print(list_token)
            return result
        except Exception as e:
            progress_callback.emit(str(e))

    def load_engine_parameters(self):

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
            engines = config_data["engines"]
            self.engines = engines.keys()
            engine_data = config_data["engines"][self.active_engine.get('name')]
            update_data = {k: v for k, v in engine_data.items() if v is not None}
            self.__dict__.update(update_data)
        except FileNotFoundError:
            self.temperature = 0.7
            self.active_model = {
                "model_name": "zero-one-ai/Yi-34B-Chat",
                "start": "",
                "end": ""
            }
            self.max_request_tokens = 4096
            self.max_response_tokens = 750
            self.api_key = ""

    def save_commands(self):
        try:
            with open(self.Config_file, "r") as file:
                config_data = json.load(file)

            config_data["commands"] = self.commands
            with open(self.Config_file, "w") as file:
                json.dump(config_data, file, indent=4)

        except FileNotFoundError:
            pass

    def save_engine_parameters(self):
        try:
            with open(self.Config_file, "r") as file:
                config_data = json.load(file)
            config_data["engines"][self.active_engine.get('name')] = {
                "base_url": self.active_engine.get('base_url'),
                "temperature": self.temperature,
                "active_model": self.active_model,
                "max_request_tokens": self.max_request_tokens,
                "max_response_tokens": self.max_response_tokens,
                "models": self.models,
            }
            with open(self.Config_file, "w") as file:
                json.dump(config_data, file, indent=4)

        except FileNotFoundError:
            print(f"Error: '{self.Config_file}' not found.")
