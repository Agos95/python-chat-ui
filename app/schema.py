from pydantic import BaseModel


class ChatMessageSchema(BaseModel):
    message: str
