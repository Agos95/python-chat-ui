import asyncio
import json
import uuid
from datetime import datetime, timezone
from enum import StrEnum, auto

from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel import Field, Relationship, SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession

SQLITE_FILE = "database.db"
SQLITE_URL = f"sqlite+aiosqlite:///{SQLITE_FILE}"


def utc_now():
    return datetime.now(timezone.utc)


class ChatMessageRole(StrEnum):
    AI = auto()
    HUMAN = auto()
    SYSTEM = auto()


class Base(SQLModel, table=False):
    id: str = Field(default_factory=lambda: uuid.uuid4().hex, primary_key=True)
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
    chat_id: str = Field(nullable=False, foreign_key="chat.id", ondelete="CASCADE")
    chat: Chat = Relationship(back_populates="history")
    role: ChatMessageRole = Field(nullable=False)
    content: str | None = Field(None)


engine = create_async_engine(SQLITE_URL, echo=True)


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


async def get_session():
    async with AsyncSession(engine) as session:
        yield session


async def populate_db():
    with open("conversations.json", "r") as f:
        conversations = json.load(f)
    async with AsyncSession(engine) as session:
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
        await session.commit()


if __name__ == "__main__":
    asyncio.run(init_db())
    asyncio.run(populate_db())
