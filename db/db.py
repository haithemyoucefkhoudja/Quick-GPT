from datetime import datetime
from sqlalchemy import create_engine, Integer, Column, DateTime, String, ForeignKey
from sqlalchemy.orm import sessionmaker, relationship, declarative_base

Base = declarative_base()

# Database configuration
DATABASE_URL = 'sqlite:///chat_database.db'  # Adjust if your file is named differently
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

# Models (Conversation and Message classes)
class Conversation(Base):
    __tablename__ = 'conversations'
    conversation_id = Column(Integer, primary_key=True, autoincrement=True)
    start_time = Column(DateTime, default=datetime.utcnow)
    messages = relationship("Message", back_populates="conversation")


class Message(Base):
    __tablename__ = 'messages'
    message_id = Column(Integer, primary_key=True, autoincrement=True)
    sender = Column(String(50), nullable=False)
    content = Column(String, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    conversation_id = Column(Integer, ForeignKey('conversations.conversation_id'))
    conversation = relationship("Conversation", back_populates="messages")


Base.metadata.create_all(engine)


def get_db_session():
    session = Session() # Call the sessionmaker
    return session  # Returning the class, not a session object


def create_conversation() -> Conversation:
    """Example function to add a new conversation"""
    with get_db_session() as session:
        new_conversation = Conversation()
        session.add(new_conversation)
        session.commit()
        return new_conversation
