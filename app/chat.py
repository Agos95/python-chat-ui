import asyncio
import string
import random
import logging

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from .schema import ChatMessageSchema

logger = logging.getLogger("uvicorn.error")

router = APIRouter(prefix="/chats", tags=["chat"])

LETTERS = list(string.ascii_letters + string.digits)


@router.post("/{chat_id}/chat")
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
