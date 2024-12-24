import asyncio
import string
import random
import logging

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlmodel import Session, select

from .schema import ChatMessageSchema
from .database.database import get_session, Chat, ChatMessage

logger = logging.getLogger("uvicorn.error")

router = APIRouter(prefix="/chats", tags=["chat"])

LETTERS = list(string.ascii_letters + string.digits)


@router.get("")
async def get_chats(session: Session = Depends(get_session)) -> list[Chat]:
    chats = session.exec(select(Chat)).all()
    return chats


@router.get("/{chat_id}")
async def get_chat(chat_id: str, session: Session = Depends(get_session)) -> Chat:
    chat = session.exec(select(Chat).where(Chat.id == chat_id)).one()
    return chat


@router.delete("/{chat_id}")
async def delete_chat(chat_id: str, session: Session = Depends(get_session)):
    chat = session.exec(select(Chat).where(Chat.id == chat_id)).one()
    session.delete(chat)
    session.commit()
    return


@router.post("/{chat_id}")
async def chat(chat_id: str, message: ChatMessageSchema) -> StreamingResponse:
    logger.info(f"Streaming chat {chat_id}")
    logger.info(f"Message: {message.message}")

    # msg = message.message
    # here you would call your LLM in a real example
    async def streaming():
        await asyncio.sleep(2)
        for _ in range(random.randint(50, 100)):
            response = "".join(random.choices(LETTERS, k=5))
            logger.info(f"{response}")
            yield response
            await asyncio.sleep(0.075)

    return StreamingResponse(streaming(), media_type="text/event-stream")
