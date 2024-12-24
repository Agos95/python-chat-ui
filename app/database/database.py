import json
import uuid
from datetime import datetime, timezone
from enum import StrEnum, auto

from sqlmodel import Field, Relationship, Session, SQLModel, create_engine

SQLITE_FILE = "database.db"
SQLITE_URL = f"sqlite:///{SQLITE_FILE}"


def utc_now():
    return datetime.now(timezone.utc)


class ChatMessageRole(StrEnum):
    AI = auto()
    HUMAN = auto()
    SYSTEM = auto()


class Base(SQLModel, table=False):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    create_time: datetime = Field(default_factory=utc_now, nullable=False)
    update_time: datetime = Field(
        default_factory=utc_now, nullable=False, sa_column_kwargs={"onupdate": utc_now}
    )


class Chat(Base, table=True):
    title: str | None = Field(None, nullable=True)
    history: list["ChatMessage"] = Relationship(
        back_populates="chat",
        cascade_delete=True,
        sa_relationship_kwargs={
            "lazy": "subquery",
            "order_by": "asc(ChatMessage.create_time)",
        },
    )


class ChatMessage(Base, table=True):
    chat_id: uuid.UUID = Field(
        nullable=False, foreign_key="chat.id", ondelete="CASCADE"
    )
    chat: Chat = Relationship(back_populates="history")
    role: ChatMessageRole = Field(nullable=False)
    content: str | None = Field(None)


engine = create_engine(SQLITE_URL, echo=True)


def init_db():
    SQLModel.metadata.create_all(engine)


def populate_db():
    with open("conversations.json", "r") as f:
        conversations = json.load(f)
    with Session(engine) as session:
        for i, conversation in enumerate(conversations):
            chat = Chat(title=f"Demo Chat {i+1}")
            chat.history = [
                ChatMessage(
                    chat_id=chat.id,
                    role=message["role"],
                    content=message["content"],
                )
                for message in conversation
            ]
            session.add(chat)
        session.commit()


if __name__ == "__main__":
    init_db()
    populate_db()
