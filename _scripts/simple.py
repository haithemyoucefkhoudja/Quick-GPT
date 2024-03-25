import os

from Communicator.zmqCommunicator import ZMQCommunicator
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
load_dotenv()

api_key = os.getenv('API_KEY')
client: ChatOpenAI = ChatOpenAI(api_key=api_key,
                                            base_url="https://api.groq.com/openai/v1",
                                            temperature=0.5,
                                            model="mixtral-8x7b-32768",
                                            max_tokens=1000,
                                            )

class MyCustomScript(ZMQCommunicator):
    def __init__(self):
        super().__init__()
        self.bind("tcp://*:5555")

    def run(self):
        while True:
            message = self.receive_message()
            _Res = client.invoke(input=message)
            self.send_message(_Res.content)


if __name__ == "__main__":
    custom_script = MyCustomScript()
    custom_script.run()
    