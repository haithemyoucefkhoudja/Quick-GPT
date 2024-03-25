import os
import zmq

class ZMQCommunicator:
    """
    Base class for setting up ZeroMQ communication. Provides common methods
    for sending and receiving messages. Users should inherit and implement
    their specific communication logic.
    """

    def __init__(self, context=None, socket_type=zmq.REP):
        """
        Initializes the ZMQCommunicator object.

        Args:
            context (zmq.Context, optional): A ZeroMQ context. If not provided,
                                             a new one will be created.
            socket_type (int, optional): The ZeroMQ socket type.
                                         Defaults to zmq.REQ (Request).
        """
        self.context = context or zmq.Context()
        self.socket = self.context.socket(socket_type)
    def connect(self, endpoint):
        """Connects to a ZeroMQ endpoint."""
        self.socket.connect(endpoint)

    def receive_message(self):
        """Receives a message and returns it as a string."""
        return self.socket.recv_string()

    def bind(self, endpoint):
        """Binds to a ZeroMQ endpoint."""
        self.socket.bind(endpoint)

    def send_message(self, message):
        """Sends a message (assumes string format)."""
        self.socket.send_string(message)


    def close(self):
        """Closes the ZeroMQ socket and context."""
        self.socket.close()
        self.context.term()

from dotenv import load_dotenv
from langchain.agents.agent_types import AgentType
from langchain_experimental.agents.agent_toolkits import create_csv_agent
from langchain_openai import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.agents import create_vectorstore_agent
load_dotenv()
            
api_key = os.getenv('API_KEY')
class MyCustomScript(ZMQCommunicator):
    def __init__(self):
        super().__init__()
        self.bind("tcp://*:5555")

    def run(self):
        try:
            csvFile = self.receive_message()
            agent = create_csv_agent(
                ChatOpenAI(api_key=api_key,
                           base_url="https://api.groq.com/openai/v1",
                           temperature=0,
                           model="mixtral-8x7b-32768",
                           ),
                csvFile,
                verbose=True,
                agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
            )
            # CallBack
            self.send_message('FILE RECIEVED')
            while True:
                    message = self.receive_message()
                    if message == '<END-SIGNAL>':
                        self.send_message('Cycle is Broken')    
                        break
                    response = agent.invoke({"input": message})
                    self.send_message(response)
            self.close()

        except Exception as e:
            self.send_message(str(e))


if __name__ == "__main__":
    custom_script = MyCustomScript()
    custom_script.run()