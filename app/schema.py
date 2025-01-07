from pydantic import BaseModel, Field, field_validator


class ChatMessageSchema(BaseModel):
    content: str


class PaginationParameters(BaseModel):
    model_config = {"extra": "forbid"}

    offset: int | None = Field(None, ge=0)
    limit: int | None = Field(None, ge=0)

    @field_validator("offset", "limit", mode="after")
    @classmethod
    def validate_pagination(cls, value) -> int | None:
        if isinstance(value, int) and value < 1:
            value = None
        return value
