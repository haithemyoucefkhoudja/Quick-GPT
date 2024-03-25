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
