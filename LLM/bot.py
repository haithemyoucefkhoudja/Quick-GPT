import json
import os
from typing import Dict

import openai
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

        client = openai.OpenAI(api_key=self.api_key,
                               base_url=self.active_engine.get('base_url'),
                               )
        # input = self.fill_template(template, **kwargs)
        result = ''
        try:
            tokens: int = self.num_tokens_from_messages([
                {"role": "system", "content": "you are helpful assistant"},
                {"role": "user", "content": template},
            ])
            if tokens > self.max_request_tokens:
                progress_callback.emit(f'\ntokens={tokens} > max_request_tokens={self.max_request_tokens}')
                return ''

            stream = client.chat.completions.create(
                model=self.active_model.get("model_name"),
                messages=[
                    {"role": "system", "content": "you are helpful assistant"},
                    {"role": "user", "content": template},
                ],
                stream=True,
                max_tokens=self.max_response_tokens,
                stop=['</s>']
            )

            # fake_stream = ["Speaks ", "a ", "given ", "text ", "using ", "pyttsx3 ", "and ", "simulates " "audio " ,"streaming", '.']
            for chunk in stream:
                """"
                stream each token to the UI
                """
                progress_callback.emit(chunk.choices[0].delta.content or "")
                # progress_callback.emit(chunk)
                result += chunk.choices[0].delta.content or ''
            # result = ''.join(stream)
            progress_callback.emit(f'\ntokens={tokens}')
            # return ''.join(fake_stream)
            return result
        except Exception as e:
            raise e

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
