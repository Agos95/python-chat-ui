import asyncio
import string
import random
import logging

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlmodel import Session, select

from .schema import ChatMessageSchema
from .database import database as db

logger = logging.getLogger("uvicorn.error")

router = APIRouter(prefix="/chats", tags=["chat"])

LETTERS = list(string.ascii_letters + string.digits)


async def get_response(message: str, chat_id: str, session: Session):
    # here you would call your LLM to get the response
    response = ""
    await asyncio.sleep(2)
    for _ in range(random.randint(50, 100)):
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
async def get_chats(session: Session = Depends(db.get_session)) -> list[db.Chat]:
    """Get list of Chats."""
    chats = session.exec(select(db.Chat)).all()
    return chats


@router.get("/{chat_id}")
async def get_chat(chat_id: str, session: Session = Depends(db.get_session)) -> db.Chat:
    """Get single chat (without messages)"""
    chat = session.exec(select(db.Chat).where(db.Chat.id == chat_id)).one()
    return chat


@router.get("/{chat_id}/messages", tags=["chat", "message"])
async def get_chat_messages(
    chat_id: str, session: Session = Depends(db.get_session)
) -> list[db.ChatMessage]:
    """Get chat messages"""
    messages = session.exec(
        select(db.ChatMessage)
        .where(db.ChatMessage.chat_id == chat_id)
        .order_by(db.ChatMessage.create_time)
    ).all()
    return messages


@router.delete("/{chat_id}")
async def delete_chat(chat_id: str, session: Session = Depends(db.get_session)):
    """Delete chat"""
    chat = session.exec(select(db.Chat).where(db.Chat.id == chat_id)).one()
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
                message=message.message, chat_id=chat_id, session=session
            )
        ]
    )
    return response


@router.post("/{chat_id}/stream")
async def stream(
    chat_id: str, message: ChatMessageSchema, session: Session = Depends(db.get_session)
) -> StreamingResponse:
    """Post a message to chat and get the response as stream"""

    logger.info(f"Streaming chat {chat_id}")
    logger.info(f"Message: {message.message}")

    return StreamingResponse(
        get_response(message=message.message, chat_id=chat_id, session=session),
        media_type="text/event-stream",
    )
