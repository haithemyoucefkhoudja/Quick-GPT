import json
import openai
import tiktoken
from PyQt6.QtCore import pyqtSignal, QThread
from PDFService import Document

functions = [
    {
        "name": "get_pdf_pages",
        "description": "Get the pages using range first-last one page e.s 50-50 many pages  e.s 50-70",
        "parameters": {
            "type": "object",
            "properties": {
                "first_page": {
                    "type": "integer",
                    "description": "first page e.g. 50 means page 50 of pdf",
                },
                "last_page": {
                    "type": "integer",
                    "description": "last page e.g. 70 means page 70 of pdf"
                },
            },
            "required": ["first_page", "last_page"],
        },
    }
]


def extract_values_from_json_string(string):
    try:
        # Attempt to parse the JSON string into a Python dictionary
        data = json.loads(string)

        # Check if "first_page" and "last_page" keys exist in the dictionary
        if "first_page" in data and "last_page" in data:
            first_page_value = data["first_page"]
            last_page_value = data["last_page"]
            return first_page_value, last_page_value
        else:
            return None, None

    except json.JSONDecodeError:
        return None, None


class Bot(QThread):
    Document_List = []
    sig_response = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.stop = False
        self.function_call = 100
        self.text = None
        self.top_P = None
        self.temperature = None
        self.model = ""
        self.max_request_tokens = None
        self.max_response_tokens = None
        self.api_key = ""
        self.organization_key = ""
        self.load_parameters()
        self.init_openai()
        self.conversation = []

        self.document_list = []
        self.curr_document = None

    def init_openai(self, ):
        openai.organization = self.organization_key
        openai.api_key = self.api_key

    def add_document(self,document_name, pdf_path=''):
        doc = Document(document_name, pdf_path)
        self.document_list.append(doc)

    def get_document_names(self):
        return [doc.document_name for doc in self.document_list]

    def get_pdf_pages(self, first_page, last_page):
        page_list = self.curr_document.extract_pdf_pages(first_page - 1, last_page)
        number = first_page
        text = ""
        for page in page_list:
            text += f"\npage number {number}:\n" + page
            number += 1
        return text


    def handle_functions(self, function_call):
        print(function_call)
        pass

    def generate_response(self, message):
        user_input_tokens = 0
        try:
            if message != '':
                # calculate estimated tokens number because num_tokens_from_messages is not accurate
                estimated_list = [{"role": "user", "content": message}]
                user_input_tokens = self.num_tokens_from_messages(estimated_list, model=self.model) - 2
                # if user input tokens  + max response tokens = 750 >= token_limit
                # tell user text provided is too large for token_limit
                if user_input_tokens >= self.max_request_tokens - self.max_response_tokens - self.function_call:
                    return "text you provided is too large for max_request tokens"
                # add user list to conversation and test if self.conv_tokens + self.max_response_tokens >= self.tokens_limit
                self.conversation.extend(estimated_list)
                while self.num_tokens_from_messages(self.conversation) + self.max_response_tokens >= self.max_request_tokens - self.function_call:
                    del self.conversation[0]

            response = openai.ChatCompletion.create(
                model=self.model,
                messages=self.conversation,
                temperature=self.temperature,
                max_tokens=self.max_response_tokens,
                top_p=self.top_P,
                stream=True,  # this time, we set stream=True
                functions=functions,
                function_call="auto",
            )
            function_name = ""
            function_args = ""
            assistant_response = ""
            for chunk in response:
                if self.stop:
                    break
                else:
                    message = ""
                    if 'content' in chunk['choices'][0]['delta']:
                        message = chunk['choices'][0]['delta']['content']
                        if not message is None:
                            assistant_response += message
                    if 'function_call' in chunk['choices'][0]['delta']:
                        response_message = chunk['choices'][0]['delta']['function_call']
                        available_functions = {
                            "get_pdf_pages": self.get_pdf_pages,
                        }  # only one function in this example, but you can have multiple
                        if "name" in response_message:
                            function_name = response_message["name"]
                        fuction_to_call = available_functions[function_name]
                        if "arguments" in response_message:
                            function_args += response_message["arguments"]
                            # Extract values from the JSON string
                            first_page, last_page = extract_values_from_json_string(function_args)
                            if first_page is not None and last_page is not None:
                                function_args = ''
                                function_response = fuction_to_call(
                                    first_page=first_page,
                                    last_page=last_page,
                                    user_tokens=user_input_tokens
                                )
                                index = len(self.conversation) - 1
                                list = [{
                                    "role": "function",
                                    "name": "get_pdf_pages",
                                    "content": function_response,
                                }]
                                self.handle_pages(index, user_input_tokens, list)

                    self.msleep(100)
                    self.sig_response.emit(message)
            if assistant_response != '':
                if not self.stop:
                    self.conversation.append({"role": "assistant", "content": assistant_response})
                    self.sig_response.emit(f"\ntoken used = {self.num_tokens_from_messages(self.conversation)}")
                    self.sig_response.emit(f"\nmodel used: {self.model}")

        except openai.error.RateLimitError as e:

            self.sig_response.emit(f"An error occurred: {str(e)}")
        except openai.error.APIError as e:
            self.sig_response.emit(f"An error occurred: {str(e)}")
        except openai.error.ServiceUnavailableError as e:
            self.sig_response.emit(f"An error occurred: {str(e)}")
        except openai.error.PermissionError as e:
            self.sig_response.emit(f"An error occurred: {str(e)}")
        except openai.error.APIConnectionError as e:
            self.sig_response.emit(f"An error occurred: {str(e)}")
        except openai.error.Timeout as e:
            self.sig_response.emit(f"An error occurred: {str(e)}")
        except openai.error.AuthenticationError as e:
            self.sig_response.emit(f"An error occurred: {str(e)}")
        except openai.error.InvalidRequestError as e:
            self.sig_response.emit(f"An error occurred: {str(e)}")

    """def pages_search(self, user_question):
        # split into chunks
        text_splitter = CharacterTextSplitter(
            separator="\n",
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len
        )
        chunks = text_splitter.split_text(self.text)

        # create embeddings
        embeddings = OpenAIEmbeddings()
        knowledge_base = FAISS.from_texts(chunks, embeddings)

        docs = knowledge_base.similarity_search(user_question)

        llm = OpenAI()
        chain = load_qa_chain(llm, chain_type="stuff")
        with get_openai_callback() as cb:
            response = chain.run(input_documents=docs, question=user_question)
            print(cb)
            return response"""

    @classmethod
    def num_tokens_from_messages(cls, messages, model="gpt-3.5-turbo-0613"):
        """Return the number of tokens used by a list of messages."""
        try:
            encoding = tiktoken.encoding_for_model(model)
        except KeyError:
            print("Warning: model not found. Using cl100k_base encoding.")
            encoding = tiktoken.get_encoding("cl100k_base")
        if model in {
            "gpt-3.5-turbo-0613",
            "gpt-3.5-turbo-16k-0613",
            "gpt-4-0613",
            "gpt-4-32k-0613",
        }:
            tokens_per_message = 3
            tokens_per_name = 1
        elif "gpt-3.5-turbo" in model:
            return cls.num_tokens_from_messages(messages, model="gpt-3.5-turbo-0613")
        elif "gpt-4" in model:
            return cls.num_tokens_from_messages(messages, model="gpt-4-0613")
        else:
            raise NotImplementedError(
                f"""num_tokens_from_messages() is not implemented for model {model}. See https://github.com/openai/openai-python/blob/main/chatml.md for information on how messages are converted to tokens."""
            )
        num_tokens = 0
        for message in messages:
            num_tokens += tokens_per_message
            for key, value in message.items():
                num_tokens += len(encoding.encode(value))
                if key == "name":
                    num_tokens += tokens_per_name
        num_tokens += 3  # every reply is primed with <|start|>assistant<|message|>
        return num_tokens

    def from_speech_to_text(self, filename):
        try:
            audio_file = open(f"{filename}", "rb")
            transcript = openai.Audio.transcribe("whisper-1", audio_file)
            return transcript.text
        except openai.error.RateLimitError as e:
            return f"An error occurred: {str(e)}"
        except openai.error.APIError as e:
            return f"An error occurred: {str(e)}"
        except openai.error.ServiceUnavailableError as e:
            return f"An error occurred: {str(e)}"
        except openai.error.PermissionError as e:
            return f"An error occurred: {str(e)}"
        except openai.error.APIConnectionError as e:
            return f"An error occurred: {str(e)}"
        except openai.error.Timeout as e:
            return f"An error occurred: {str(e)}"
        except openai.error.AuthenticationError as e:
            return f"An error occurred: {str(e)}"
        except openai.error.InvalidRequestError as e:
            return f"An error occurred: {str(e)}"

    """def check_pattern(self, user_text):
        # Define the regular expression pattern
        pattern = r'p\[(\d{1,3})\]'
        # Find the match using the regular expression pattern
        match = re.search(pattern, user_text)
        if match:
            if self.curr_document is None or not os.path.exists(f"PDFTexts/{self.curr_document.document_name}-properties.txt"):
                return "you didn't upload any PDF file"
            else:
                # Extract the number from the match
                number = int(match.group(1))
                if number > self.curr_document.document_num_pages or int(number) <= 0:
                    return f"there's no page labeled {number} for the file"
                pages_list = self.curr_document.extract_pdf_pages(number - 1, number)
                return self.generate_response_document(user_text, pages_list, number)
        pattern = r'p\[(\d{1,3})-(\d{1,3})\]'
        match = re.search(pattern, user_text)
        if match:
            if self.curr_document is None or not os.path.exists(
                    f"PDFTexts/{self.curr_document.document_name}-properties.txt"):
                return "you didn't upload any PDF file"
            else:
                number1 = int(match.group(1))
                number2 = int(match.group(2))
                if number1 > self.curr_document.document_num_pages or int(number1) <= 0:
                    return f"there's no page labeled {number1} for the file"
                if number2 > self.curr_document.document_num_pages or int(number2) <= 0:
                    return f"there's no page labeled {number2} for the file"
                pages_list = self.curr_document.extract_pdf_pages(number1 - 1, number2)
                return self.generate_response_document(user_text, pages_list, number1)
        if user_text.startswith("/doc"):
            return self.generate_response_document(user_text, page_list=[], number=-1)
        return self.generate_response(user_text)"""

    def load_parameters(self):
        try:
            with open("OPENAI", "r") as file:
                data = json.load(file)
                self.api_key = str(data.get("api_key", self.api_key))
                self.organization_key = str(data.get("organization_key", self.organization_key))
                self.top_P = float(data.get("top_P", self.top_P))
                self.temperature = float(data.get("temperature", self.temperature))
                self.model = str(data.get("model", self.model))
                self.max_request_tokens = int(data.get("token_limit", self.max_request_tokens))
                self.max_response_tokens = int(data.get("max_response_tokens", self.max_response_tokens))
        except FileNotFoundError:
            self.top_P = 0.9
            self.temperature = 0.7
            self.model = "gpt-3.5-turbo"
            self.max_request_tokens = 4096
            self.max_response_tokens = 750
            self.api_key = ""
            self.organization_key = ""

    def save_parameters(self):
        data = {
            "api_key": self.api_key,
            "organization_key": self.organization_key,
            "top_P": self.top_P,
            "temperature": self.temperature,
            "model": self.model,
            "token_limit": self.max_request_tokens,
            "max_response_tokens": self.max_response_tokens
        }
        with open("OPENAI", "w") as file:
            json.dump(data, file)

    def handle_pages(self, index, user_input_tokens, list):
        pages_tokens = self.num_tokens_from_messages(list, model=self.model) - 2

        self.conversation.insert(index, list[0])
        if user_input_tokens + pages_tokens + self.max_response_tokens >= self.max_request_tokens - self.function_call:
            del self.conversation[index:]
            self.sig_response.emit(
                f"text or pages you provided is too large for max_request tokens {self.max_request_tokens} your tokens= {user_input_tokens + pages_tokens}")
            return
        while self.num_tokens_from_messages(self.conversation) + self.max_response_tokens >= self.max_request_tokens - self.function_call:
            del self.conversation[0]
        self.generate_response('')
