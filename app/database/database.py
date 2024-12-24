from sqlmodel import Field, SQLModel, Relationship

import uuid
from datetime import datetime, timezone
from enum import StrEnum, auto


def utc_now():
    return datetime.now(timezone.utc)


class ChatMessageType(StrEnum):
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
            "order_by": "asc(ChatMEssage.create_time)",
        },
    )


class ChatMessage(Base, table=True):
    chat_id: uuid.UUID = Field(
        nullable=False, foreign_key="chat.id", ondelete="CASCADE"
    )
    chat: Chat = Relationship(back_populates="history")
    type: ChatMessageType = Field(nullable=False)
    content: str | None = Field(None)
