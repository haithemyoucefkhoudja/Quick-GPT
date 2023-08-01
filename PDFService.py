import os
import threading

import PyPDF2
basedir = os.getcwd()
FileBaseDir = os.path.join(basedir, "PDFTexts\\")
"""
from PyPDF2 import PdfReader
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.chains.question_answering import load_qa_chain
from langchain.llms import OpenAI
from langchain.callbacks import get_openai_callback


def main():
    
    # extract the text
      pdf_reader = PdfReader(pdf)
      text = ""
      for page in pdf_reader.pages:
        text += page.extract_text()
        
      # split into chunks
      text_splitter = CharacterTextSplitter(
        separator="\n",
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len
      )
      chunks = text_splitter.split_text(text)
      
      # create embeddings
      embeddings = OpenAIEmbeddings()
      knowledge_base = FAISS.from_texts(chunks, embeddings)
      
        docs = knowledge_base.similarity_search(user_question)
        
        llm = OpenAI()
        chain = load_qa_chain(llm, chain_type="stuff")
        with get_openai_callback() as cb:
          response = chain.run(input_documents=docs, question=user_question)
          print(cb)
"""


class Document:

    def __init__(self, document_name, pdf_path):
        self.pdf_path = pdf_path
        self.document_name = document_name
        self.document_num_pages = 0
        self.init_pdf_file()
        self.pdf_reader = None
        self.start_initialize_pdf_reader_thread()

    def start_initialize_pdf_reader_thread(self):
        # Step 3: Create a Thread object and pass your function as the target.
        thread = threading.Thread(target=self.initialize_pdf_reader_thread,)
        # Step 4: Start the thread.
        thread.start()

    def initialize_pdf_reader_thread(self):
        if self.pdf_path != '':
            pdfFileObj = open(self.pdf_path, 'rb')
            self.pdf_reader = PyPDF2.PdfReader(pdfFileObj)

    def extract_pdf_pages(self, min_num, sup_num):
        if self.pdf_reader is None:
            raise ValueError("PDF reader not initialized. Call initialize_pdf_reader() first.")
        pages = []
        for page in self.pdf_reader.pages[min_num: sup_num]:
            pages.append(page.extract_text())
        return pages

    def init_pdf_file(self):
        try:
            document_properties_path = os.path.join(FileBaseDir, f"{self.document_name}-properties.txt")
            if os.path.exists(document_properties_path):
                self.load_document_properties()
            else:
                with open(self.pdf_path, 'rb') as pdf_file:
                    reader = PyPDF2.PdfReader(pdf_file)
                    # write document properties into txt file named txt_path-properties
                    self.document_num_pages = len(reader.pages)
                    self.save_document_properties()
        except Exception as e:
            return f"error occurred {e}"

    def save_document_properties(self):
        document_path = os.path.join(FileBaseDir, f"{self.document_name}-properties.txt")
        print(f"document properties path={document_path}")
        with open(document_path, 'w', encoding='utf-8', errors='ignore') as txt_file:
            txt_file.write(f"""document_pdf_path={self.pdf_path}
document_name={self.document_name}
document_number_pages={self.document_num_pages}
""")

    def load_document_properties(self):
        document_path = os.path.join(FileBaseDir, f"{self.document_name}-properties.txt")
        with open(document_path, 'r', encoding="utf-8") as txt_file:
            content = txt_file.read()
        properties = {}
        lines = content.split('\n')
        for line in lines:
            if line.strip() != "":
                key, value = line.split('=')
                properties[key.strip()] = value.strip()
        # Accessing the properties
        self.pdf_path = properties.get('document_pdf_path')
        if not os.path.exists(self.pdf_path):
            os.remove(document_path)
            self.pdf_path = ""
            return
        self.document_name = properties.get('document_name')
        self.document_num_pages = int(properties.get('document_number_pages'))
