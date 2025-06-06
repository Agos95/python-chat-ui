from typing import Literal, TypedDict


class ChatMessageSchema(TypedDict):
    content: str
    role: Literal["human", "ai"]
