import json
import os
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
    engines: list[Dict] = []
    """
    Active Engine
    """
    active_engine: Dict = {}
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
        self.load_engine_parameters(None)

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
        try:
            # input = self.fill_template(template, **kwargs)
            result = ''

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
            """with open(_configInstance.get_path('ui/Messanger/python exe.txt')) as file:
                List = file.read()
                my_list = ast.literal_eval(List)
                print(len(my_list))"""

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
                _index += 1
            return result
        except FileNotFoundError as e:
            progress_callback.emit(('File Not Found Error:', -1))
            print('File Not Found Error:', e.args)
        except Exception as e:
            progress_callback.emit((str(e), -1))
            print('e:', str(e))

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

            }
            with open(self.Config_file, "w") as file:
                json.dump(config_data, file, indent=4)

        except FileNotFoundError:
            print(f"Error: '{self.Config_file}' not found.")
