import json
import os
import time
from typing import Any

import openai
from PyQt6.QtCore import pyqtSignal, QThread

from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chat_models import ChatOpenAI
from langchain.chains import RetrievalQA
from langchain.document_loaders import PyPDFLoader
from langchain.memory import ConversationBufferMemory
from queue import Queue, Empty
from threading import Thread
from langchain.callbacks.base import BaseCallbackHandler
"""
in case you used function calling along with streaming you can append model chunks then test if there's valid params in json
"""


def extract_params_from_json_string(string):
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


# Defined a QueueCallback, which takes as a Queue object during initialization. Each new token is pushed to the queue.
class QueueCallback(BaseCallbackHandler):
    """Callback handler for streaming LLM responses to a queue."""

    def __init__(self, q):
        self.q = q

    def on_llm_new_token(self, token: str, **kwargs: Any) -> None:
        self.q.put(token)

    def on_llm_end(self, *args, **kwargs: Any) -> None:
        return self.q.empty()



class Bot(QThread):
    sig_response = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.stop = False

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

    def insert_data(self, conversation):
        conversation_text = "".join(conversation)
        # splitting the text into chunks
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        texts = text_splitter.split_text(conversation_text)
        persist_directory = 'db'
        embedding = OpenAIEmbeddings(openai_api_key=self.api_key)
        vectordb = Chroma.from_texts(texts=texts,
                                     embedding=embedding,
                                     persist_directory=persist_directory)
        vectordb.persist()

    def init_openai(self, ):
        openai.organization = self.organization_key
        openai.api_key = self.api_key

    # to prevent the user from redundant doc embedding we save file to docs
    def save_document_indicator(self, doc_name):
        indicator_file_path = f"Docs/{doc_name}_indicator"
        with open(indicator_file_path, "w"):
            pass

    def from_speech_to_text(self, filename):
        try:
            audio_file = open(f"{filename}", "rb")
            transcript = openai.Audio.transcribe("whisper-1", audio_file)
            return transcript.text
        except (openai.error.RateLimitError,
                openai.error.InvalidRequestError,
                openai.error.AuthenticationError,
                openai.error.APIError,
                openai.error.ServiceUnavailableError,
                openai.error.PermissionError,
                openai.error.APIConnectionError,
                openai.error.Timeout) as e:
            return str(e)

    def pdf_embedding(self, doc_path, doc_name):
        if os.path.exists(f"Docs/{doc_name}_indicator"):
            return
        self.save_document_indicator(doc_name)
        pdf_loader = PyPDFLoader(doc_path)
        documents = pdf_loader.load()
        # we split the data into chunks of 1,000 characters, with an overlap
        # of 200 characters between the chunks, which helps to give better results
        # and contain the context of the information between chunks
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        documents = text_splitter.split_documents(documents)
        embedding = OpenAIEmbeddings(openai_api_key=self.api_key)
        persist_directory = 'db'
        vectordb = Chroma.from_documents(documents=documents,
                                         embedding=embedding,
                                         persist_directory=persist_directory)
        vectordb.persist()

    def generate_response(self, question):
        embedding = OpenAIEmbeddings(openai_api_key=self.api_key)
        persist_directory = 'db'
        vectordb = Chroma(persist_directory=persist_directory,
                          embedding_function=embedding,
                          )

        retriever = vectordb.as_retriever(search_kwargs={"k": 2})

        # Create a Queue
        q = Queue()
        job_done = object()
        turbo_llm = ChatOpenAI(
                max_tokens=self.max_response_tokens,
                openai_api_key=self.api_key,
                temperature=self.temperature,
                model_name=self.model,
                streaming=True,
                callbacks=[QueueCallback(q)]
            )

        # create the chain to answer questions
        qa_chain = RetrievalQA.from_chain_type(llm=turbo_llm,
                                               chain_type="stuff",
                                               retriever=retriever,
                                               return_source_documents=True
                                               )

        def task():
            try:
                qa_chain(question)
            except Exception as e:
                self.sig_response.emit(str(e))
                return
            q.put(job_done)

        # Create a thread and start the function
        t = Thread(target=task)
        t.start()
        bot_content = ''
        # full example
        # Get each new token from the queue and emit it to gui, yield for our generator
        while True:
            try:
                next_token = q.get(True, timeout=1)
                time.sleep(0.1)
                if next_token is job_done or self.stop:
                    break
                bot_content += next_token
                self.sig_response.emit(next_token)
            except Empty:
                continue
        converasation = ["USER:" + question, "\nAI:" + bot_content]
        self.insert_data(converasation)

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
