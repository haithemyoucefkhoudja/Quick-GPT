import random
import string
import time
from enum import Enum

from typing import Optional


class Role(Enum):
    Bot = "Assistant"
    User = "User"


def generate_random_id() -> str:
    """Generates a random string-based ID."""

    # Customizable parameters
    id_length = 8
    characters = string.ascii_letters + string.digits

    # Generate ID
    random_id = ''.join(random.choice(characters) for _ in range(id_length))
    return random_id


class Message:
    """
    Represents a message with an ID, role, and content.
    """
    def __init__(self, role=None, content=None):

        """
        Initializes a new Message object.

        Args:
            id: The unique identifier of the message.
            role: The role of the message (e.g., "user", "assistant").
            content: The content of the message.
            createdAt: The time Message generated in
        """
        self.id: str = generate_random_id()
        self.createdAt: float = time.time()
        self.role:  Role = role
        self.content: Optional[str, None] = content

    @property
    def getMessageId(self) -> str:
        return self.id

    @property
    def getContent(self) -> str:
        return self.content

    def setContent(self, content: str) -> None:
        self.content = content

    def setmessage(self, message: dict)-> None:
        self.content = message.get('content')
        self.setRole(message.get('Role'))

    def setRole(self, Role) -> None:
        self.role = Role
