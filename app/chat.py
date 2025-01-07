import asyncio
import logging
import random
import string
from typing import Annotated
from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlmodel import Session, select

from .database import database as db
from .schema import ChatMessageSchema, PaginationParameters

logger = logging.getLogger("uvicorn.error")

router = APIRouter(prefix="/chats", tags=["chat"])

LETTERS = list(string.ascii_letters + string.digits)


async def get_response(message: str, chat_id: str, session: Session):
    # here you would call your LLM to get the response
    response = ""
    await asyncio.sleep(2)
    for _ in range(random.randint(20, 100)):
        stream = "".join(random.choices(LETTERS, k=5))
        # logger.info(f"{response}")
        response += stream
        yield stream
        await asyncio.sleep(0.075)

    messages = [
        db.ChatMessage(chat_id=chat_id, role=db.ChatMessageRole.HUMAN, content=message),
        db.ChatMessage(chat_id=chat_id, role=db.ChatMessageRole.AI, content=response),
    ]
    logger.info("Addiding messages to db session")
    for m in messages:
        session.add(m)
    logger.info("Committing messages to db")
    session.commit()


@router.get("")
async def get_chats(
    pagination: Annotated[PaginationParameters, Query()],
    session: Session = Depends(db.get_session),
) -> list[db.Chat]:
    """Get list of Chats."""
    chats = session.exec(
        select(db.Chat)
        .order_by(db.Chat.create_time.desc())
        .offset(pagination.offset)
        .limit(pagination.limit)
    ).all()
    return chats


@router.post("")
async def create_chat(
    title: str | None = None, session: Session = Depends(db.get_session)
) -> db.Chat:
    """Get list of Chats."""
    chat = db.Chat(title=title)
    session.add(chat)
    session.commit()
    session.refresh(chat)
    return chat


@router.get("/{chat_id}")
async def get_chat(chat_id: str, session: Session = Depends(db.get_session)) -> db.Chat:
    """Get single chat (without messages)"""
    chat = session.exec(select(db.Chat).where(db.Chat.id == chat_id)).one()
    return chat


@router.delete("/{chat_id}")
def delete_chat(chat_id: str, session: Session = Depends(db.get_session)):
    """Delete chat"""
    chat = session.exec(select(db.Chat).where(db.Chat.id == chat_id))
    chat = chat.one()
    session.delete(chat)
    session.commit()
    return


@router.post("/{chat_id}")
async def chat(
    chat_id: str, message: ChatMessageSchema, session: Session = Depends(db.get_session)
) -> ChatMessageSchema:
    """Post a message to chat and get the response"""
    response = "".join(
        [
            chunk
            for chunk in get_response(
                message=message.content, chat_id=chat_id, session=session
            )
        ]
    )
    return ChatMessageSchema(content=response)


@router.post("/{chat_id}/stream")
async def stream(
    chat_id: str, message: ChatMessageSchema, session: Session = Depends(db.get_session)
) -> StreamingResponse:
    """Post a message to chat and get the response as stream"""

    logger.info(f"Streaming chat {chat_id}")
    logger.info(f"Message: {message.content}")

    return StreamingResponse(
        get_response(message=message.content, chat_id=chat_id, session=session),
        media_type="text/event-stream",
    )


@router.get("/{chat_id}/messages", tags=["message"])
async def get_messages(
    chat_id: str,
    pagination: Annotated[PaginationParameters, Query()],
    session: Session = Depends(db.get_session),
) -> list[db.ChatMessage]:
    """
    Get chat messages.
    Messages are returned from the newest to the oldest;
    in this way it is possible limit the history to the most recent N messages.
    """
    messages = session.exec(
        select(db.ChatMessage)
        .where(db.ChatMessage.chat_id == chat_id)
        .order_by(db.ChatMessage.create_time.desc())
        .offset(pagination.offset)
        .limit(pagination.limit)
    ).all()
    return messages
