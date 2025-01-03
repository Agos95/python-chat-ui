from app.database import database as db
from typing import Iterable

from pydantic import BaseModel, Field

from datetime import datetime


class ChatMessagePlaceholder(BaseModel):
    id: str = "placeholder_message"
    create_time: datetime = Field(default_factory=db.utc_now)
    update_time: datetime = Field(default_factory=db.utc_now)
    chat_id: str = "placeholder_chat"
    role: db.ChatMessageRole
    content: str | Iterable[str] = ""
