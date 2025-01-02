import logging

from fastapi import APIRouter, Depends
from sqlmodel import Session, select

from .database import database as db
from .schema import ChatMessageSchema

logger = logging.getLogger("uvicorn.error")

router = APIRouter(prefix="/messages", tags=["message"])


@router.get("/{message_id}")
async def get_message(
    message_id: str, session: Session = Depends(db.get_session)
) -> db.ChatMessage:
    """Get single message in chat"""
    message = session.exec(
        select(db.ChatMessage).where(db.ChatMessage.id == message_id)
    ).one()
    return message


@router.patch("/{message_id}")
async def update_message(
    message_id: str, content: str, session: Session = Depends(db.get_session)
) -> ChatMessageSchema:
    """Update message in chat"""
    message = session.exec(
        select(db.ChatMessage).where(db.ChatMessage.id == message_id)
    ).one()
    message.content = content
    session.add(message)
    session.commit()
    return ChatMessageSchema(content=content)


@router.delete("/{message_id}")
async def delete_message(message_id: str, session: Session = Depends(db.get_session)):
    """Get single message in chat"""
    message = session.exec(
        select(db.ChatMessage).where(db.ChatMessage.id == message_id)
    ).one()
    session.delete(message)
    session.commit()
    return
