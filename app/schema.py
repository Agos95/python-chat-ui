from pydantic import BaseModel


class ChatMessageSchema(BaseModel):
    content: str
